---
description: 사업보고서 원본을 위키 페이지로 인제스트 (단일/배치/dry-run/re-ingest)
argument-hint: [파일명 | 폴더 | --dry-run 폴더]
---

`engine\OPERATIONS.md` > "1. Ingest"와 `CLAUDE.md` > "Ingest" 절차를 따라 인제스트를 수행하라.

대상: $ARGUMENTS
- 인자가 없으면 `source_documents\AnnualReport_Recent\`를 배치 대상으로 간주한다.
- `--dry-run`이 포함되면 처리 대상 파일과 생성/갱신 예상 페이지 목록만 출력하고 실제 생성은 하지 않는다.
- `re-ingest`가 포함되면 이미 처리된 파일도 강제 재처리한다.

절차 요약:
1. 시작 시 `engine\taxonomy.md`, `wiki\index.md`를 아직 안 읽었으면 읽는다.
2. 미처리 파일 판별: `wiki\sources\`에 `resource:`로 참조되지 않은 원본만 대상(`engine\scripts\list-pending.ps1` 활용 가능).
3. 버전 중복(`[기재정정]`·`첨부00760/00761`)은 대표본 우선 규칙으로 정리.
4. 파일별 end-to-end 처리(모두 `wiki\` 하위): sources → company/group/industry/segment/product/shareholder/executive/(금융)financial_product·rating → stub 노드화 → 양방향 링크.
5. 각 파일 완료 후 `[N/전체] 파일명 완료` 보고, 전체 완료 후 요약, `wiki\log.md` 기록.
