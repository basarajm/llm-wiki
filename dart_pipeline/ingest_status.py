# -*- coding: utf-8 -*-
"""
ingest_status.py — dart_md 사업보고서의 위키 인제스트 진행상황 트래커.

기능:
  - dart_md/<시장>/ 의 다운로드된 MD 보고서 목록 산출
  - 각 기업이 위키에 이미 인제스트되었는지 판정
    (wiki/companies/<기업명>.md 가 존재하고 is_stub:false 이면 done)
  - 명시적 트래커(_state/ingest_tracker.json) 와 병합하여 done/pending 목록 생성
  - 사람이 읽는 트래커(wiki/outputs/ingest-tracker-<시장>.md) 출력

사용:
  python ingest_status.py KOSPI          # 현황 출력 + 트래커 갱신
  python ingest_status.py KOSPI --mark "삼성전자,SK하이닉스"   # 수동 done 표시
"""

import argparse
import glob
import json
import os
import re

import config

WIKI = os.path.normpath(os.path.join(config.BASE_DIR, "..", "wiki"))
TRACKER_JSON = os.path.join(config.STATE_DIR, "ingest_tracker.json")


def read_frontmatter(path):
    fm = {}
    try:
        txt = open(path, encoding="utf-8").read()
    except OSError:
        return fm
    m = re.match(r"^---\s*\n(.*?)\n---", txt, re.S)
    block = m.group(1) if m else txt[:1500]
    for line in block.splitlines():
        mm = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if mm:
            fm[mm.group(1)] = mm.group(2).strip()
    return fm


def list_reports(market):
    out = []
    for f in sorted(glob.glob(os.path.join(config.OUTPUT_DIR, market, "*.md"))):
        fm = read_frontmatter(f)
        out.append({
            "file": os.path.relpath(f, config.BASE_DIR).replace("\\", "/"),
            "corp_name": fm.get("corp_name", ""),
            "stock_code": fm.get("stock_code", ""),
            "fiscal_year": fm.get("fiscal_year", ""),
            "rcept_no": fm.get("rcept_no", ""),
        })
    return out


def company_page_status(corp_name):
    """위키 기업 페이지 존재/충실도. 반환: 'full' | 'stub' | None"""
    p = os.path.join(WIKI, "companies", f"{corp_name}.md")
    if not os.path.exists(p):
        return None
    fm = read_frontmatter(p)
    return "stub" if fm.get("is_stub", "").lower() == "true" else "full"


def load_tracker():
    if os.path.exists(TRACKER_JSON):
        try:
            return json.load(open(TRACKER_JSON, encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"done": {}}  # file -> {corp_name, marked_at}


def save_tracker(tr):
    os.makedirs(config.STATE_DIR, exist_ok=True)
    json.dump(tr, open(TRACKER_JSON, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


def compute(market):
    reports = list_reports(market)
    tr = load_tracker()
    done, pending = [], []
    for r in reports:
        page = company_page_status(r["corp_name"])
        is_done = (r["file"] in tr["done"]) or (page == "full")
        r["page"] = page or "-"
        (done if is_done else pending).append(r)
    return reports, done, pending, tr


def write_md_tracker(market, done, pending):
    out_dir = os.path.join(WIKI, "outputs")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"ingest-tracker-{market}.md")
    lines = [
        f"# {market} 인제스트 트래커",
        "",
        f"- 대상 보고서: **{len(done) + len(pending)}건**",
        f"- 완료(done): **{len(done)}건**",
        f"- 대기(pending): **{len(pending)}건**",
        "",
        "> done 기준: 위키에 충실한(non-stub) 기업 페이지가 있거나 트래커에 done 기록됨.",
        "> 이 파일은 `python dart_pipeline/ingest_status.py " + market + "` 로 재생성됩니다.",
        "",
        "## ✅ 완료",
        "",
    ]
    for r in sorted(done, key=lambda x: x["stock_code"]):
        lines.append(f"- [{r['stock_code']}] {r['corp_name']} "
                     f"(FY{r['fiscal_year']}) — `{r['file']}`")
    lines += ["", "## ⏳ 대기", ""]
    for r in sorted(pending, key=lambda x: x["stock_code"]):
        lines.append(f"- [{r['stock_code']}] {r['corp_name']} "
                     f"(FY{r['fiscal_year']}) — `{r['file']}`")
    lines.append("")
    open(path, "w", encoding="utf-8").write("\n".join(lines))
    return os.path.relpath(path, config.BASE_DIR)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("market", choices=["KOSPI", "KOSDAQ"])
    ap.add_argument("--mark", default="", help="쉼표구분 기업명 → done 표시")
    args = ap.parse_args()

    reports, done, pending, tr = compute(args.market)

    if args.mark:
        names = {n.strip() for n in args.mark.split(",") if n.strip()}
        by_name = {r["corp_name"]: r for r in reports}
        for n in names:
            if n in by_name:
                tr["done"][by_name[n]["file"]] = {"corp_name": n}
        save_tracker(tr)
        reports, done, pending, tr = compute(args.market)

    md = write_md_tracker(args.market, done, pending)
    print(f"[{args.market}] 전체 {len(reports)} / 완료 {len(done)} / 대기 {len(pending)}")
    print(f"트래커: {md}")


if __name__ == "__main__":
    main()
