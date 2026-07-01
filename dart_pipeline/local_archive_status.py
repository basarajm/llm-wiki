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
  - done/pending 목록 산출, 사람이 읽는 트래커(wiki/outputs/ingest-tracker-local.md) 출력
  - --next N 으로 다음 N개 회사를 JSON으로 산출(배치 작업용)

사용:
  python local_archive_status.py                    # 현황 출력 + 트래커 갱신
  python local_archive_status.py --next 3            # 다음 3개사 JSON 출력
  python local_archive_status.py --mark "회사A,회사B" # 수동 done 표시(트래커 재계산에는 영향 없음, 참고용)
"""

import argparse
import json
import os
import re

import config

WIKI = os.path.normpath(os.path.join(config.BASE_DIR, "..", "wiki"))
SRC_DIR = os.path.normpath(
    os.path.join(config.BASE_DIR, "..", "source_documents", "AnnualReport_MD")
)

NAME_RE = re.compile(r"^(.*?)-사업보고서-\d{4}\.\d{2}\.md$")


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
    """회사명 -> 'full' | 'stub'."""
    out = {}
    d = os.path.join(WIKI, "companies")
    if not os.path.isdir(d):
        return out
    for fn in os.listdir(d):
        if not fn.endswith(".md") or fn == "index.md":
            continue
        fm = read_frontmatter(os.path.join(d, fn))
        out[fn[:-3]] = "stub" if fm.get("is_stub", "").lower() == "true" else "full"
    return out


def compute():
    archive = list_archive()
    status = wiki_company_status()
    done, pending, stub_upgradeable = [], [], []
    for name, fn in archive.items():
        st = status.get(name)
        entry = {"name": name, "file": f"source_documents/AnnualReport_MD/{fn}"}
        if st == "full":
            done.append(entry)
        elif st == "stub":
            stub_upgradeable.append(entry)
            pending.append(entry)
        else:
            pending.append(entry)
    done.sort(key=lambda x: x["name"])
    pending.sort(key=lambda x: x["name"])
    stub_upgradeable.sort(key=lambda x: x["name"])
    return archive, done, pending, stub_upgradeable


def write_md_tracker(done, pending, stub_upgradeable):
    out_dir = os.path.join(WIKI, "outputs")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "ingest-tracker-local.md")
    lines = [
        "# 로컬 아카이브(AnnualReport_MD) 인제스트 트래커",
        "",
        f"- 아카이브 회사 수: **{len(done) + len(pending)}건** "
        "(source_documents/AnnualReport_MD/, 각 머신에 로컬 배치 필요·git 미포함)",
        f"- 완료(done, Full): **{len(done)}건**",
        f"- 대기(pending): **{len(pending)}건** (이 중 stub→Full 승급 대상 {len(stub_upgradeable)}건)",
        "",
        "> done 기준: wiki/companies/<회사>.md 가 존재하고 is_stub:false.",
        "> 이 파일은 `python dart_pipeline/local_archive_status.py` 로 재생성됩니다.",
        "> 다음 N개사 산출: `python dart_pipeline/local_archive_status.py --next N`",
        "",
        f"## ⏳ 대기 (상위 50건, 전체 {len(pending)}건)",
        "",
    ]
    for r in pending[:50]:
        lines.append(f"- {r['name']} — `{r['file']}`")
    lines.append("")
    open(path, "w", encoding="utf-8").write("\n".join(lines))
    return os.path.relpath(path, config.BASE_DIR)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--next", type=int, default=0, help="다음 N개사를 JSON으로 출력")
    args = ap.parse_args()

    archive, done, pending, stub_upgradeable = compute()

    if args.next:
        print(json.dumps(pending[: args.next], ensure_ascii=False, indent=1))
        return

    md = write_md_tracker(done, pending, stub_upgradeable)
    print(
        f"아카이브 {len(archive)} / 완료 {len(done)} / 대기 {len(pending)} "
        f"(stub 승급 대상 {len(stub_upgradeable)})"
    )
    print(f"트래커: {md}")


if __name__ == "__main__":
    main()
