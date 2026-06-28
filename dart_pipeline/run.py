# -*- coding: utf-8 -*-
"""
run.py — 사업보고서 원문 다운로드 → Markdown 변환 → 저장 (체크포인트/재개 지원).

흐름:
  1) _state/targets.json 로드 (없으면 build_targets 실행 안내)
  2) 각 대상에 대해 document.xml ZIP 다운로드 → 본문 XML 선택 → Markdown 변환
  3) dart_md/<시장>/<종목코드>_<기업명>_<회계연도>.md 로 저장
  4) 진행상황을 _state/progress.json 에 기록하여 중단 시 재개 가능

사용 예:
  python run.py                      # 전체 실행/재개
  python run.py --limit 5            # 앞 5건만 (테스트)
  python run.py --markets KOSPI      # 특정 시장만
  python run.py --rebuild-targets    # 대상목록 먼저 재생성
"""

import argparse
import io
import json
import os
import re
import sys
import time
import zipfile
import datetime as dt

import config
from dart_client import DartClient, DartDailyLimitError, DartError
from md_converter import xml_to_markdown
import build_targets

_ILLEGAL = re.compile(r'[\\/:*?"<>|\r\n\t]+')
_FISCAL = re.compile(r"\((\d{4})[.\-/](\d{1,2})")


def safe_name(name):
    name = name.replace("주식회사", "").replace("㈜", "").strip()
    name = _ILLEGAL.sub("", name)
    name = re.sub(r"\s+", "_", name)
    return name[:60] or "noname"


def fiscal_year(report_nm, rcept_dt):
    m = _FISCAL.search(report_nm or "")
    if m:
        return m.group(1)
    return (rcept_dt or "")[:4]


def pick_main_xml(names, rcept_no):
    """ZIP 내 본문 사업보고서 XML 파일명 선택."""
    main = f"{rcept_no}.xml"
    if main in names:
        return main
    xmls = [n for n in names if n.lower().endswith(".xml")]
    if not xmls:
        return names[0] if names else None
    # 접수번호_xxxxx.xml(첨부) 보다 접수번호.xml(본문) 우선; 없으면 가장 큰 파일
    non_attach = [n for n in xmls if "_" not in os.path.splitext(n)[0]]
    return (non_attach or xmls)[0]


def decode_xml(raw):
    for enc in ("utf-8", "cp949", "euc-kr"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return default
    return default


def save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def process_one(client, t):
    """대상 1건 처리 → 저장 경로 반환. 실패 시 예외 발생."""
    rcept_no = t["rcept_no"]
    raw_zip = client.download_document(rcept_no)
    z = zipfile.ZipFile(io.BytesIO(raw_zip))
    names = z.namelist()
    inner = pick_main_xml(names, rcept_no)
    if not inner:
        raise DartError("ZIP 내 XML 없음")
    xml = decode_xml(z.read(inner))

    fy = fiscal_year(t.get("report_nm"), t.get("rcept_dt"))
    dart_url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}"
    meta = {
        "corp_name": t["corp_name"],
        "corp_code": t["corp_code"],
        "stock_code": t["stock_code"],
        "market": t["market"],
        "report_name": t.get("report_nm", ""),
        "fiscal_year": fy,
        "rcept_no": rcept_no,
        "rcept_dt": t.get("rcept_dt", ""),
        "dart_url": dart_url,
        "source_file": inner,
        "downloaded_at": dt.date.today().isoformat(),
        "converter": "md_converter v1 (stdlib)",
    }
    md = xml_to_markdown(xml, meta)

    out_dir = os.path.join(config.OUTPUT_DIR, t["market"])
    os.makedirs(out_dir, exist_ok=True)
    fname = f"{t['stock_code']}_{safe_name(t['corp_name'])}_{fy}.md"
    out_path = os.path.join(out_dir, fname)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)
    return os.path.relpath(out_path, config.BASE_DIR)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="처리 건수 제한(테스트)")
    ap.add_argument("--markets", default="", help="쉼표구분 시장 필터 (예: KOSPI,KOSDAQ)")
    ap.add_argument("--delay", type=float, default=config.REQUEST_DELAY)
    ap.add_argument("--rebuild-targets", action="store_true")
    ap.add_argument("--no-resume", action="store_true", help="진행기록 무시하고 처음부터")
    ap.add_argument("--api-key", default=None, help="DART API 키(미지정 시 env DART_API_KEY 사용)")
    args = ap.parse_args()

    api_key = config.require_api_key(args.api_key)

    if args.rebuild_targets or not os.path.exists(config.TARGETS_PATH):
        print("[run] 대상목록 생성 중...", flush=True)
        build_targets.build(config.LOOKBACK_MONTHS, api_key=api_key)

    targets = load_json(config.TARGETS_PATH, [])
    if not targets:
        print("[run] targets.json 이 비어있습니다. build_targets.py 를 먼저 실행하세요.",
              file=sys.stderr)
        sys.exit(1)

    if args.markets:
        want = {m.strip() for m in args.markets.split(",") if m.strip()}
        targets = [t for t in targets if t["market"] in want]

    progress = {} if args.no_resume else load_json(config.PROGRESS_PATH, {})
    failures = load_json(config.FAILURES_PATH, {})

    todo = [t for t in targets if progress.get(t["rcept_no"], {}).get("status") != "done"]
    if args.limit:
        todo = todo[: args.limit]

    total = len(todo)
    done_cnt = sum(1 for v in progress.values() if v.get("status") == "done")
    print(f"[run] 전체대상 {len(targets)} / 이미완료 {done_cnt} / 이번실행 {total}",
          flush=True)

    client = DartClient(api_key, request_delay=args.delay)
    ok = err = 0
    t_start = time.time()
    try:
        for i, t in enumerate(todo, 1):
            rn = t["rcept_no"]
            try:
                rel = process_one(client, t)
                progress[rn] = {"status": "done", "file": rel,
                                "corp_name": t["corp_name"]}
                failures.pop(rn, None)
                ok += 1
                if i % 10 == 0 or i == total:
                    elapsed = time.time() - t_start
                    rate = i / elapsed if elapsed else 0
                    eta = (total - i) / rate if rate else 0
                    print(f"  [{i}/{total}] OK {t['stock_code']} {t['corp_name']} "
                          f"| 성공 {ok} 실패 {err} | ETA {eta/60:.1f}분", flush=True)
            except DartDailyLimitError:
                print("[중단] 일일 한도 초과 — 진행상황 저장 후 종료. "
                      "내일 같은 명령으로 재개하세요.", flush=True)
                break
            except (DartError, zipfile.BadZipFile, Exception) as e:  # noqa: BLE001
                err += 1
                failures[rn] = {"corp_name": t["corp_name"],
                                "error": f"{type(e).__name__}: {e}"}
                progress[rn] = {"status": "failed", "corp_name": t["corp_name"]}
                print(f"  [{i}/{total}] 실패 {t['stock_code']} {t['corp_name']}: {e}",
                      flush=True)
            if i % 25 == 0:
                save_json(config.PROGRESS_PATH, progress)
                save_json(config.FAILURES_PATH, failures)
    finally:
        save_json(config.PROGRESS_PATH, progress)
        save_json(config.FAILURES_PATH, failures)

    print(f"\n[run] 완료: 성공 {ok} / 실패 {err} / 소요 "
          f"{(time.time()-t_start)/60:.1f}분")
    if failures:
        print(f"[run] 실패 {len(failures)}건 → {config.FAILURES_PATH}")


if __name__ == "__main__":
    main()
