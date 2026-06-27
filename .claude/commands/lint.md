---
description: 위키 건강 검진 — 모순·고아 페이지·깨진 링크·양방향 링크·OKF 적합성 점검
---

`engine\OPERATIONS.md` > "2. Lint" 절차로 위키를 검진하라.

1. 가능하면 `engine\scripts\lint.ps1`과 `engine\scripts\validate-okf.ps1`을 실행해 기계 점검 결과를 수집한다.
   (스크립트 실행이 불가하면 Claude가 직접 `wiki\` 디렉토리·frontmatter를 스캔해 동일 점검을 수행)
2. 의미 점검(Claude): 수치 모순, 링크 없는 기업·주주명, 구버전 미갱신을 점검한다.
3. 발견 사항을 심각도(오류/경고/제안)로 분류한다.
4. 결과를 `wiki\outputs\lint-report-<오늘날짜>.md`(type: Analysis)로 저장하고 `wiki\log.md`에 `**Lint**` 기록.
5. 사용자에게 핵심 발견과 권장 조치를 요약 보고한다.
