---
type: Analysis
title: 위키 Lint 리포트 (2026-07-13)
description: engine/scripts/lint.ps1·validate-okf.ps1 기계 점검 + Claude 의미 점검 결과
tags: [lint, 품질검진, 유지보수]
timestamp: 2026-07-13T00:00:00Z
---

# 위키 Lint 리포트 (2026-07-13)

콘텐츠 페이지 **28,283개** 대상. `engine/scripts/validate-okf.ps1` + `engine/scripts/lint.ps1` 기계 점검 결과와 Claude의 표본 기반 원인 분석을 결합했다.

## 요약

| 항목 | 건수 | 심각도 |
|---|---:|---|
| type frontmatter 누락 | 4 | 제안 (예약 파일 성격) |
| timestamp frontmatter 누락 | 4 | 제안 (동일 파일) |
| 깨진 내부 링크 | 1,539 | **오류** — 단, ~575건(37%)은 실제로는 파일이 존재하나 마크다운 문법 오류 |
| 고아 페이지 (인바운드 0) | 2,421 | 경고 |
| 양방향 링크 누락 | 2,421건(스캔, 헤더 표기 2,840) | 경고 — 대부분 stub 경량 페이지 특성상 낮은 실질 영향 |

## 1. 오류 — 깨진 내부 링크 (1,539건)

### 1-A. 시스템적 원인 발견 (약 575건, 최우선 수정 권고)

원인: 동명이인 구분용 파일명 `이름(소속).md` 형식을 마크다운 링크 `[텍스트](/executives/이름(소속))`로 그대로 사용하면, 마크다운 파서가 URL 내부의 첫 `)`를 링크 종료로 해석해 URL이 잘림.

예시 (`companies/ALT_America.md`):
```
대표이사(CEO)는 [이상수](</executives/이상수(알트)>)(알트 대표이사 겸직).
```
→ 실제 대상 파일 `wiki/executives/이상수(알트).md`는 **존재함**. 링크만 깨졌다.

**해결책**: 괄호 포함 링크는 `<>`로 URL을 감싸거나(`[이상수](</executives/이상수(알트)>)`) 퍼센트 인코딩(`%28`/`%29`) 적용. 위키 전반에 반복되는 패턴이므로 스크립트 일괄 치환이 효율적 — 정규식 `\]\(([^)]*\([^)]*\)[^)]*)\)` 매칭 후 괄호 URL 인코딩 권장.

### 1-B. 퍼센트 인코딩/공백 문제 (약 72건)

파일명에 공백이 포함된 페이지(예: `Mayson Partners Pte. Ltd..md`)를 링크할 때 `%20` 인코딩과 실제 파일명 표기가 불일치하는 사례. 개별 확인 필요.

### 1-C. 실제 누락 페이지 (약 890건)

링크 문법은 정상이나 대상 페이지 자체가 생성되지 않은 경우 — 대부분 사업보고서 본문에 언급된 임원·주주가 별도 stub으로 노드화되지 않은 케이스(예: `companies/GS.md → /executives/허연수`, `companies/DB손해보험.md → /shareholders/김남호`). 배치 ingest 과정에서 "주요 언급이지만 5% 미만 지분/사외이사급이라 stub 생략" 판단이 누적된 결과로 추정. 우선순위: 최대주주·대표이사급 언급인데 링크만 있고 페이지가 없는 케이스부터 stub 생성 권장.

## 2. 경고 — 고아 페이지 (인바운드 링크 0, 2,421건)

유형별 분포:

| 타입 | 건수 |
|---|---:|
| ratings (신용등급) | 721 |
| companies | 689 |
| executives | 435 |
| shareholders | 168 |
| groups | 144 |
| segments | 114 |
| products | 95 |
| industries | 29 |
| value_chain | 23 |
| financial_products | 3 |

`ratings`(신용등급) 페이지가 최다 — 대개 기업 페이지의 "신용등급" 섹션에서 텍스트로만 언급되고 `/ratings/...` 링크가 누락된 것으로 추정(1-A의 괄호/공백 문제와도 일부 중첩 가능). `companies` 고아 689건은 규모 대비 위키 성장 속도가 빨라 상호 참조가 아직 따라잡지 못한 자연스러운 현상 — 신규 그룹/산업 페이지 생성 시 정리 권장.

## 3. 경고 — 양방향 링크 누락 (executives/shareholders/groups → companies 방향, 표본 2,421건)

| 소스 타입 | 건수 |
|---|---:|
| executives → companies | 1,343 |
| shareholders → companies | 929 |
| groups → companies | 149 |

CLAUDE.md 규칙(주주↔기업, 그룹↔기업, 임원↔기업 양방향)이 지켜지지 않은 사례. 다만 이 중 다수는 "회사 페이지 본문에 임원 이름이 텍스트로 언급되어 있으나 명시적 마크다운 링크가 없는" 경미한 케이스로, 사업 규모나 위험도에 미치는 영향은 낮음. 최대주주·대표이사급(예: `허은철.md ↔ /companies/녹십자홀딩스`, `조현범.md ↔ /companies/한국타이어앤테크놀로지`)부터 우선 보완 권장.

## 4. 제안 — frontmatter 누락 (4건)

`wiki/outputs/ingest-tracker-*.md` 4개 파일은 `dart_pipeline` 스크립트가 자동 생성하는 진행 상황 트래커로, OKF 콘텐츠 페이지가 아님. `wiki/index.md`·`wiki/log.md`처럼 예약 파일로 취급하거나, `validate-okf.ps1`의 스캔 대상에서 `outputs/ingest-tracker-*` 패턴을 제외하는 것을 권장.

## 5. Claude 의미 점검 (표본)

- **시장 분류 오류 발견**: `wiki/companies/한국기업평가.md`, `wiki/companies/하이비젼시스템.md`의 `market:` 필드가 `KOSPI`로 잘못 기재되어 있음 — 두 회사 모두 실제로는 KOSDAQ 상장사(KOSPI 로컬 아카이브 배치 중 발견, 2026-07-13). `market`/`market_page` 필드 KOSDAQ으로 정정 필요.
- **의도된 리다이렉트 확인**: `companies/엘에스일렉트릭.md`, `companies/HL만도.md`, `companies/케이씨씨.md`는 `is_stub: true` + 리다이렉트 안내문 형태로 정식 페이지(LS일렉트릭/에이치엘만도/KCC)를 가리키도록 의도적으로 설계됨 — lint의 "stub 승급 대상" 집계에서는 오탐(false positive)으로 잡힐 수 있으므로 별도 화이트리스트 처리 권장.
- **수치 모순**: 대규모 표본 검증 결과 뚜렷한 동일 수치 모순 사례는 발견되지 않았으나, 28,283페이지 전수 검증은 이번 lint 범위를 벗어남 — 향후 `/compare`·`/connect` 등 개별 쿼리 작업 중 발견되는 대로 lint 후속 항목에 축적 권장.

## 권장 조치 우선순위

1. **(최우선, 자동화 가능)** 괄호 포함 임원/기업명 링크의 마크다운 문법 수정 — 약 575건, 스크립트 일괄 처리 권장
2. 한국기업평가·하이비젼시스템 등 `market` 필드 오기재 건 정정 (KOSDAQ lint 시 추가 발견분 포함 지속 확인)
3. `ingest-tracker-*.md` 4건을 validate-okf 스캔 대상에서 제외
4. 최대주주·대표이사급 인물의 미생성 stub 페이지 우선 보완 (약 890건 중 상위 우선순위 선별)
5. 고아 `ratings` 페이지(721건) — 기업 페이지 신용등급 섹션 링크 보완

# Citations

- engine/scripts/validate-okf.ps1 실행 결과 (2026-07-13)
- engine/scripts/lint.ps1 실행 결과 (2026-07-13)
- wiki/companies/ALT_America.md, wiki/companies/GS.md 등 표본 확인
