---
description: 위키 기반 질의응답 — index-first 검색 + 출처 인용 + outputs 저장
argument-hint: <질문>
---

`engine\OPERATIONS.md` > "4. Query"의 index-first 프로토콜로 다음 질문에 답하라.

질문: $ARGUMENTS

1. `wiki\index.md`로 관련 페이지를 선별하고 read 한다.
2. 답변의 모든 수치·주장에 출처 페이지를 인용한다 `[페이지](/dir/page)`.
3. 분석 가치가 있으면 `wiki\outputs\`에 type: Analysis로 저장하고 index·log를 갱신한다.
4. 근거가 부족하면 누락된 페이지·주제를 보고하고 ingest 또는 추가 조사를 제안한다.
