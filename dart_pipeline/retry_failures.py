# -*- coding: utf-8 -*-
"""
retry_failures.py — 014(원문 미제공) 등으로 실패한 기업을 대체 접수번호로 복구.

전략:
  - 실패 기업(corp_code)별로 사업보고서(A001) 공시를 3개월 창으로 조회
    (DART 규정: corp_code 지정 시 검색기간 3개월 제한)
    · 원래 접수일 전후 3개월  → 같은 회계연도 보고서의 원본/타 버전
    · 1년 전 같은 시기 3개월  → 직전 회계연도 보고서
  - 후보 접수번호를 최신순으로 document.xml 다운로드 시도 → 첫 성공본 사용
  - 성공 시 progress.json 갱신 및 failures.json 에서 제거
"""

import datetime as dt
import io
import json
import os
import sys
import zipfile

import config
from dart_client import DartClient, DartError, DartDailyLimitError
import run as runner


def windows_around(rcept_dt):
    """rcept_dt(YYYYMMDD) 기준 3개월 창 2개(당해·전년) 생성."""
    try:
        d = dt.datetime.strptime(rcept_dt, "%Y%m%d").date()
    except ValueError:
        d = dt.date.today()
    out = []
    for years_back in (0, 1):
        center = dt.date(d.year - years_back, d.month, 1)
        bgn = center - dt.timedelta(days=45)
        end = center + dt.timedelta(days=45)
        out.append((bgn.strftime("%Y%m%d"), end.strftime("%Y%m%d")))
    return out


def candidate_rcepts(client, corp_code, rcept_dt, exclude):
    seen = {}
    for bgn, end in windows_around(rcept_dt):
        try:
            for x in client.list_disclosures(
                bgn, end, "A001", last_reprt_at="N", corp_code=corp_code
            ):
                if x["corp_code"] != corp_code:
                    continue
                if x["rcept_no"] in exclude:
                    continue
                seen[x["rcept_no"]] = x
        except DartError:
            continue
    return sorted(seen.values(), key=lambda x: x["rcept_no"], reverse=True)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-key", default=None, help="DART API 키(미지정 시 env DART_API_KEY 사용)")
    args = ap.parse_args()
    client = DartClient(config.require_api_key(args.api_key),
                        request_delay=config.REQUEST_DELAY)
    failures = runner.load_json(config.FAILURES_PATH, {})
    progress = runner.load_json(config.PROGRESS_PATH, {})
    targets = {t["rcept_no"]: t for t in runner.load_json(config.TARGETS_PATH, [])}

    fail_items = list(failures.items())
    print(f"[retry] 실패 {len(fail_items)}건 복구 시도", flush=True)
    recovered = still = 0

    for rn, fv in fail_items:
        t = targets.get(rn)
        if not t:
            continue
        try:
            cands = candidate_rcepts(client, t["corp_code"], t.get("rcept_dt", ""),
                                     exclude={rn})
        except DartDailyLimitError:
            print("[중단] 일일 한도 초과 — 종료. 내일 재실행.", flush=True)
            break

        success = False
        for cand in cands:
            try:
                raw = client.download_document(cand["rcept_no"])
            except DartError:
                continue
            except DartDailyLimitError:
                print("[중단] 일일 한도 초과 — 종료.", flush=True)
                runner.save_json(config.PROGRESS_PATH, progress)
                runner.save_json(config.FAILURES_PATH, failures)
                return
            # 다운로드 성공 → 변환·저장 (대체 접수번호 메타로)
            alt = dict(t)
            alt["rcept_no"] = cand["rcept_no"]
            alt["rcept_dt"] = cand.get("rcept_dt", t.get("rcept_dt", ""))
            alt["report_nm"] = cand.get("report_nm", t.get("report_nm", ""))
            try:
                rel = _save_from_zip(raw, alt)
            except Exception as e:  # noqa: BLE001
                continue
            progress[rn] = {"status": "done", "file": rel,
                            "corp_name": t["corp_name"], "via": cand["rcept_no"]}
            failures.pop(rn, None)
            recovered += 1
            success = True
            print(f"  복구 {t['stock_code']} {t['corp_name']} "
                  f"← {cand['rcept_no']} ({cand.get('report_nm','')[:20]})", flush=True)
            break
        if not success:
            still += 1
            print(f"  미복구 {t['stock_code']} {t['corp_name']} (대체본 없음)",
                  flush=True)

    runner.save_json(config.PROGRESS_PATH, progress)
    runner.save_json(config.FAILURES_PATH, failures)
    print(f"\n[retry] 복구 {recovered} / 잔여실패 {still}")


def _save_from_zip(raw_zip, t):
    z = zipfile.ZipFile(io.BytesIO(raw_zip))
    names = z.namelist()
    inner = runner.pick_main_xml(names, t["rcept_no"])
    xml = runner.decode_xml(z.read(inner))
    fy = runner.fiscal_year(t.get("report_nm"), t.get("rcept_dt"))
    meta = {
        "corp_name": t["corp_name"], "corp_code": t["corp_code"],
        "stock_code": t["stock_code"], "market": t["market"],
        "report_name": t.get("report_nm", ""), "fiscal_year": fy,
        "rcept_no": t["rcept_no"], "rcept_dt": t.get("rcept_dt", ""),
        "dart_url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={t['rcept_no']}",
        "source_file": inner, "downloaded_at": dt.date.today().isoformat(),
        "converter": "md_converter v1 (stdlib, retry)",
    }
    from md_converter import xml_to_markdown
    md = xml_to_markdown(xml, meta)
    out_dir = os.path.join(config.OUTPUT_DIR, t["market"])
    os.makedirs(out_dir, exist_ok=True)
    fname = f"{t['stock_code']}_{runner.safe_name(t['corp_name'])}_{fy}.md"
    out_path = os.path.join(out_dir, fname)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)
    return os.path.relpath(out_path, config.BASE_DIR)


if __name__ == "__main__":
    main()
