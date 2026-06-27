---
description: 운영 대시보드 — 타입별 페이지 수·인제스트 커버리지·고아·최근 활동
---

`engine\OPERATIONS.md` > "7. Wiki Status" 절차로 대시보드를 출력하라.

1. 가능하면 `engine\scripts\stats.ps1`을 실행한다. 불가하면 `wiki\` 디렉토리·index.md를 스캔해 집계한다.
2. 보고 항목:
   - 타입별 페이지 수
   - 16개 핵심 기업 인제스트 커버리지(완료/미완)
   - 고아 페이지 수, 양방향 링크 누락 수
   - 최근 `wiki\log.md` 활동 요약
3. 다음으로 권장하는 작업(미처리 ingest, lint 필요 등)을 제안한다.
