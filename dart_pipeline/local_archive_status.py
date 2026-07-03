# -*- coding: utf-8 -*-
"""
local_archive_status.py — source_documents/AnnualReport_MD/ (로컬 사업보고서 아카이브)
기반 인제스트 진행상황 트래커.

기존 ingest_status.py는 dart_pipeline/dart_md/(DART API 재다운로드 필요)를 기준으로 하지만,
이 스크립트는 리포 표준 위치인 source_documents/AnnualReport_MD/ 에 이미 저장된 사업보고서
MD 파일(파일명 패턴: "<회사명>-사업보고서-<YYYY.MM>.md")을 기준(ground truth)으로 삼는다.
이 폴더는 .gitignore 대상이므로 각 머신에 파일을 직접 채워 넣어야 동작한다.

기능:
  - AnnualReport_MD/ 의 회사명 목록 산출(파일명에서 추출)
  - 각 회사가 위키에 이미 Full(is_stub:false)로 인제스트되었는지 판정
  - 원본 MD 파일 본문의 "상장 유형" 표(유가증권시장 상장/코스닥시장 상장 행)를 파싱하여
    시장 구분(KOSPI/KOSDAQ/기타)을 산출 — 위키 미등재 회사도 시장별 필터링 가능
  - done/pending 목록 산출, 사람이 읽는 트래커(wiki/outputs/ingest-tracker-local.md) 출력
  - --next N 으로 다음 N개 회사를 JSON으로 산출(배치 작업용)

사용:
  python local_archive_status.py                           # 현황 출력 + 트래커 갱신
  python local_archive_status.py --next 3                  # 다음 3개사 JSON 출력
  python local_archive_status.py --market KOSPI --next 6   # KOSPI 중 다음 6개사 JSON 출력
  python local_archive_status.py --market KOSDAQ --next 6  # KOSDAQ 중 다음 6개사 JSON 출력
"""

import argparse
import functools
import json
import os
import re

import config

WIKI = os.path.normpath(os.path.join(config.BASE_DIR, "..", "wiki"))

# 원본 사업보고서 폴더. 기본값은 리포 표준 위치(source_documents/AnnualReport_MD/)이며,
# 환경변수 ANNUALREPORT_MD_DIR 로 다른 로컬 경로(예: 원본 아카이브 폴더)를 직접 지정할 수 있다.
# (개인 경로를 코드에 하드코딩하지 않기 위해 환경변수로 주입 — README/OPERATIONS 참고)
_DEFAULT_SRC_DIR = os.path.normpath(
    os.path.join(config.BASE_DIR, "..", "source_documents", "AnnualReport_MD")
)
SRC_DIR = os.environ.get("ANNUALREPORT_MD_DIR", "").strip() or _DEFAULT_SRC_DIR

NAME_RE = re.compile(r"^(.*?)-사업보고서-\d{4}\.\d{2}\.md$")

# 원본 MD 본문의 "상장 유형" 표에서 시장 행을 찾는 패턴.
# 예: "| 유가증권시장 상장 | 2004.08.05 | 해당사항 없음 |"
#     "| 코스닥시장 상장 | 2007.02.21 | 해당사항 없음 |"
# 날짜 칸이 "해당사항 없음"이 아니면 그 시장에 실제 상장된 것으로 판단.
MARKET_ROW_RE = re.compile(
    r"(유가증권시장 상장|코스닥시장 상장)\s*\|\s*([^\|]*?)\s*\|\s*([^\|]*?)\s*\|"
)


def read_frontmatter(path):
    fm = {}
    try:
        txt = open(path, encoding="utf-8-sig").read()
    except OSError:
        return fm
    m = re.match(r"^---\s*\n(.*?)\n---", txt, re.S)
    if not m:
        return fm
    for line in m.group(1).splitlines():
        mm = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if mm:
            fm[mm.group(1)] = mm.group(2).strip()
    return fm


@functools.lru_cache(maxsize=None)
def detect_market_from_source(path):
    """원본 사업보고서 MD 본문에서 상장 유형 표를 읽어 KOSPI/KOSDAQ/Unknown 판정."""
    try:
        txt = open(path, encoding="utf-8", errors="ignore").read()
    except OSError:
        return "Unknown"
    # 회사 자체의 "주권상장 및 특례상장에 관한 사항" 표는 사업보고서 최상단(I.회사의 개요)에
    # 한 번만 등장한다. 본문 뒤쪽에는 대주주·비교기업 등 다른 법인의 상장 정보가 표 형태로
    # 재등장할 수 있으므로, "가장 먼저 매칭되고 날짜가 실제로 채워진(해당사항 없음이 아닌)"
    # 행을 채택한다 — 두 시장 라벨 중 어느 쪽이 문서에 먼저 나오는지로 판정.
    for m in MARKET_ROW_RE.finditer(txt):
        label, date_col, _ = m.groups()
        listed = bool(date_col) and "해당사항 없음" not in date_col
        if listed:
            return "KOSPI" if label == "유가증권시장 상장" else "KOSDAQ"
    return "Unknown"


def list_archive():
    """회사명 -> 원본 md 파일명(리포 상대경로 source_documents/AnnualReport_MD/<파일명>)."""
    out = {}
    if not os.path.isdir(SRC_DIR):
        return out
    for fn in sorted(os.listdir(SRC_DIR)):
        if not fn.endswith(".md"):
            continue
        m = NAME_RE.match(fn)
        name = m.group(1) if m else fn[:-3]
        out[name] = fn
    return out


def wiki_company_status():
    """회사명 -> {'status': 'full' | 'stub', 'market': 'KOSPI' | 'KOSDAQ' | ...}."""
    out = {}
    d = os.path.join(WIKI, "companies")
    if not os.path.isdir(d):
        return out
    for fn in os.listdir(d):
        if not fn.endswith(".md") or fn == "index.md":
            continue
        fm = read_frontmatter(os.path.join(d, fn))
        out[fn[:-3]] = {
            "status": "stub" if fm.get("is_stub", "").lower() == "true" else "full",
            "market": fm.get("market", "Unknown"),
        }
    return out


def resolve_market(wiki_entry, src_path):
    """위키 frontmatter의 market이 있으면 우선 사용, 없으면 원본 MD에서 판정."""
    wiki_market = wiki_entry.get("market") if wiki_entry else None
    if wiki_market and wiki_market not in ("Unknown", ""):
        return wiki_market
    return detect_market_from_source(src_path)


def compute(market_filter=None):
    """market_filter: None(all) | 'KOSPI' | 'KOSDAQ'"""
    archive = list_archive()
    status = wiki_company_status()
    done, pending, stub_upgradeable = [], [], []
    for name, fn in archive.items():
        st = status.get(name)
        src_path = os.path.join(SRC_DIR, fn)
        market = resolve_market(st, src_path)
        entry = {
            "name": name,
            "file": f"source_documents/AnnualReport_MD/{fn}",
            "market": market,
        }

        if market_filter and market != market_filter:
            continue

        if st and st["status"] == "full":
            done.append(entry)
        elif st and st["status"] == "stub":
            stub_upgradeable.append(entry)
            pending.append(entry)
        else:
            pending.append(entry)
    done.sort(key=lambda x: x["name"])
    pending.sort(key=lambda x: x["name"])
    stub_upgradeable.sort(key=lambda x: x["name"])
    return archive, done, pending, stub_upgradeable


def write_md_tracker(done, pending, stub_upgradeable, market_filter=None):
    out_dir = os.path.join(WIKI, "outputs")
    os.makedirs(out_dir, exist_ok=True)
    suffix = f"-{market_filter.lower()}" if market_filter else ""
    path = os.path.join(out_dir, f"ingest-tracker-local{suffix}.md")
    title_suffix = f" ({market_filter})" if market_filter else ""
    lines = [
        f"# 로컬 아카이브(AnnualReport_MD) 인제스트 트래커{title_suffix}",
        "",
        f"- 아카이브 회사 수: **{len(done) + len(pending)}건** "
        "(source_documents/AnnualReport_MD/, 각 머신에 로컬 배치 필요·git 미포함)",
        f"- 완료(done, Full): **{len(done)}건**",
        f"- 대기(pending): **{len(pending)}건** (이 중 stub→Full 승급 대상 {len(stub_upgradeable)}건)",
        "",
        "> done 기준: wiki/companies/<회사>.md 가 존재하고 is_stub:false.",
        "> market 판정: 위키 frontmatter 우선, 없으면 원본 MD의 '상장 유형' 표(유가증권시장/코스닥시장 상장)에서 추출.",
        "> 이 파일은 `python dart_pipeline/local_archive_status.py [--market KOSPI|KOSDAQ]` 로 재생성됩니다.",
        "> 다음 N개사 산출: `python dart_pipeline/local_archive_status.py [--market KOSPI|KOSDAQ] --next N`",
        "",
        f"## ⏳ 대기 (상위 50건, 전체 {len(pending)}건)",
        "",
    ]
    for r in pending[:50]:
        lines.append(f"- {r['name']} (`{r['market']}`) — `{r['file']}`")
    lines.append("")
    open(path, "w", encoding="utf-8").write("\n".join(lines))
    return os.path.relpath(path, config.BASE_DIR)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--next", type=int, default=0, help="다음 N개사를 JSON으로 출력")
    ap.add_argument(
        "--market", choices=["KOSPI", "KOSDAQ"], help="특정 시장만 필터링 (KOSPI|KOSDAQ)"
    )
    args = ap.parse_args()

    archive, done, pending, stub_upgradeable = compute(market_filter=args.market)

    if args.next:
        print(json.dumps(pending[: args.next], ensure_ascii=False, indent=1))
        return

    md = write_md_tracker(done, pending, stub_upgradeable, market_filter=args.market)
    market_suffix = f" ({args.market})" if args.market else ""
    print(
        f"아카이브{market_suffix} {len(done) + len(pending)} / 완료 {len(done)} / 대기 {len(pending)} "
        f"(stub 승급 대상 {len(stub_upgradeable)})"
    )
    print(f"트래커: {md}")


if __name__ == "__main__":
    main()
