#!/usr/bin/env bash
# 새 빈 위키 부트스트랩 (bash 버전) — 엔진만 복사, 콘텐츠/원본 제외.
# 새 구조: <대상>/CLAUDE.md, README.md, .gitignore, .claude/, engine/, wiki/, source_documents/
# 사용: engine/scripts/new-wiki.sh /path/to/new-wiki
set -eu
PROJ="$(cd "$(dirname "$0")/../.." && pwd)"
TARGET="${1:-}"
if [ -z "$TARGET" ]; then echo "사용: new-wiki.sh <대상경로>"; exit 1; fi
mkdir -p "$TARGET"

ROOT_FILES="CLAUDE.md README.md .gitignore"
ROOT_DIRS=".claude engine"
CONTENT_DIRS="companies groups industries shareholders value_chain segments products executives financial_products ratings sources outputs"

for f in $ROOT_FILES; do [ -f "$PROJ/$f" ] && cp "$PROJ/$f" "$TARGET/$f"; done
for d in $ROOT_DIRS; do [ -d "$PROJ/$d" ] && cp -r "$PROJ/$d" "$TARGET/$d"; done

for d in $CONTENT_DIRS; do
  mkdir -p "$TARGET/wiki/$d"
  printf '# %s\n\n<!-- 비어 있음 -->\n' "$d" > "$TARGET/wiki/$d/index.md"
done
printf '# 위키 — 전체 인덱스\n\n<!-- build-index 로 생성 -->\n' > "$TARGET/wiki/index.md"
printf '# 위키 작업 이력\n\n' > "$TARGET/wiki/log.md"
mkdir -p "$TARGET/source_documents/raw/assets" "$TARGET/source_documents/AnnualReport_Recent"

echo "새 빈 위키 생성 완료: $TARGET"
echo "엔진만 복사됨. INSTALL.md 참고."
