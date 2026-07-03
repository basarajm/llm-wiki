---
type: Analysis
title: 위키 검진 리포트 2026-07-03
description: IG13 배치(SK가스·SFA반도체·SBS·SK리츠 등) 이후 동시편집 충돌 잔여 정리 및 위키 전반 기계 점검 결과
tags: [lint, 검진, 유지보수]
timestamp: 2026-07-03T12:09:00Z
---

# 위키 검진 리포트 2026-07-03

`engine\OPERATIONS.md` §2 절차에 따라 `engine\scripts\lint.ps1`, `engine\scripts\validate-okf.ps1`을 실행하고,
특히 IG13 배치(미커밋 작업분: SK가스·SFA반도체·SBS·SK리츠·SK디앤디·SK바이오사이언스·SK케미칼·피케이씨·SJG세종 등)로 인한
동시편집 충돌 잔여 문제(중복 섹션·깨진 링크)를 중점 점검했다.

## 범위

- 전체 위키: 콘텐츠 페이지 5,430개 (`validate-okf.ps1`, `lint.ps1` 전수 실행)
- 중점 점검: `git status` 기준 미커밋 변경분 126개 파일(IG13 배치 산출물) — groups/SK.md, markets/KOSPI.md,
  wiki/index.md, wiki/log.md, companies/SK가스·SK디앤디·SK바이오사이언스·SK리츠·SKC·SFA반도체·TY홀딩스·피케이씨 등,
  관련 executives/shareholders/ratings/segments/value_chain 신규 페이지 일체

## 오류 (Errors)

1. **[수정 완료] index.md 링크-파일명 불일치** — `wiki/index.md`의 신용등급 항목이
   `[SK리츠 신용등급](/ratings/SK리츠 신용등급)`로 되어 있었으나 실제 파일명은
   `wiki/ratings/SK리츠_신용등급.md`(언더스코어). `SK리츠.md` 본문 내 링크는 이미 올바른 언더스코어 형태였음 —
   index 재생성(build-index.ps1) 과정에서 제목 문자열을 그대로 슬러그화하며 발생한 것으로 추정.
   → **본 세션에서 언더스코어로 정정 완료.**

## 경고 (Warnings) — IG13 범위 밖, 기존 미해결 이슈

2. **`wiki/groups/SK.md`, `wiki/companies/SK.md` 깨진 링크 (5건)** — `/companies/SK실트론`,
   `/companies/SK이노베이션` 참조 페이지가 아직 미생성. SK그룹 계열사 표에 이름은 있으나 정식 company 페이지가
   없는 상태(IG8 이후 지속). IG13에서 새로 만든 문제가 아니라 이전부터 존재하던 미인제스트 간극이며,
   `member_companies` 프론트매터에는 두 종목이 이미 등재돼 있어 향후 ingest 시 자동으로 해소될 것으로 보임.
3. **전체 위키 기준 깨진 내부 링크 629건, type/timestamp 누락 4건(`outputs\ingest-tracker-*.md`)** —
   IG13과 무관한 위키 전반의 누적 이슈. 상세는 `lint.ps1` 원본 출력 참조. 별도 세션에서 전수 정리 권장.

## 제안 (Suggestions)

4. 정규식 기반 점검에서 `강문수(SFA반도체)` 등 **괄호가 포함된 파일명/링크**가 오탐(false positive)으로 잡힘 —
   실제로는 시알홀딩스 소속 동명이인 강문수와 SFA반도체 강문수를 올바르게 구분한 정상 케이스. lint 스크립트의
   링크 파싱 정규식이 괄호를 못 닫는 경우가 있어 향후 `lint.ps1` 정규식 보정 검토 제안.
5. IG13이 다룬 SK가스·SK디앤디·SK바이오사이언스·SK케미칼(stub)이 `wiki/groups/SK디스커버리.md`,
   `wiki/markets/KOSPI.md`에 정상적으로 양방향 반영되어 있음을 확인 — 별도 조치 불필요.
6. `wiki/groups/SK.md` — SK리츠 추가는 정상 반영(member_companies + 계열사 표). 중복 섹션·중복 항목 없음 확인.

## 점검 결과 요약

| 항목 | 결과 |
|---|---|
| IG13 관련 파일 중복 `## ` 섹션 헤딩 | 0건 (전수 확인) |
| IG13 관련 파일 중복 리스트 항목(`- [...]`) | 0건 |
| IG13 신규 링크 중 실제 깨진 링크 | 1건 (수정 완료) |
| IG13 범위 밖 기존 깨진 링크(참고) | 629건(전체), 5건(SK그룹 계열사 미인제스트) |
| log.md 중복 헤딩/충돌 마커 | 0건 |

## 결론

IG13 배치 자체에서 발생한 동시편집 충돌(중복 섹션, 신규 깨진 링크)은 `wiki/index.md`의
SK리츠 신용등급 링크 1건뿐이며 이번 세션에서 정정했다. 그 외 지적된 깨진 링크(SK실트론·SK이노베이션)는
IG13 이전부터 존재하던 미인제스트 간극으로, 향후 해당 종목 ingest 시 자연 해소될 사안이다.
전체 위키 기준의 629건 깨진 링크·고아 페이지 등은 이번 점검 범위를 벗어나며 별도 전수 lint 세션이 필요하다.

# Citations

- `engine\scripts\lint.ps1` 실행 결과 (2026-07-03)
- `engine\scripts\validate-okf.ps1` 실행 결과 (2026-07-03)
- [SK리츠](/companies/SK리츠), [SK리츠 신용등급](/ratings/SK리츠_신용등급)
- [SK그룹](/groups/SK)
- [KOSPI](/markets/KOSPI)
