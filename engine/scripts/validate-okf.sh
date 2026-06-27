#!/usr/bin/env bash
# OKF v0.1 적합성 검증 (bash 버전)
# 모든 콘텐츠 .md(index.md/log.md 제외)가 frontmatter + 비어있지 않은 type 을 갖는지 확인.
set -u
# 스크립트 위치: <프로젝트>/engine/scripts → 콘텐츠 루트는 <프로젝트>/wiki
ROOT="$(cd "$(dirname "$0")/../../wiki" && pwd)"
DIRS="companies groups industries shareholders value_chain segments products executives financial_products ratings sources outputs"

violations=0
count=0
for d in $DIRS; do
  [ -d "$ROOT/$d" ] || continue
  while IFS= read -r -d '' f; do
    base="$(basename "$f")"
    [ "$base" = "index.md" ] && continue
    [ "$base" = "log.md" ] && continue
    count=$((count+1))
    # 첫 줄이 --- 인지, type: 비어있지 않은지
    first="$(head -n1 "$f" | tr -d '\357\273\277\r')"
    if [ "$first" != "---" ]; then
      echo "[frontmatter 없음] ${f#$ROOT/}"; violations=$((violations+1)); continue
    fi
    tval="$(awk 'NR>1{if($0=="---")exit} /^type:[[:space:]]*/{sub(/^type:[[:space:]]*/,"");print;exit}' "$f")"
    if [ -z "$tval" ]; then
      echo "[type 누락/공백] ${f#$ROOT/}"; violations=$((violations+1))
    fi
  done < <(find "$ROOT/$d" -name '*.md' -print0)
done

echo "OKF 검증: 콘텐츠 페이지 ${count}개 점검"
if [ "$violations" -eq 0 ]; then
  echo "통과 — OKF v0.1 type 규칙 만족."; exit 0
else
  echo "위반 ${violations}건."; exit 1
fi
