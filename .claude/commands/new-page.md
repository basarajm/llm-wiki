---
description: 템플릿 기반 신규 페이지 생성
argument-hint: <타입> <제목>
---

`engine\OPERATIONS.md` > "8. New Page" 절차로 새 페이지를 생성하라.

대상: $ARGUMENTS

1. `engine\taxonomy.md`에서 해당 타입의 스키마를 확인하고 `engine\templates\<타입>.md`를 기반으로 한다.
2. frontmatter와 필수 섹션을 채운다(가능한 근거는 기존 페이지·소스에서 인용). 페이지는 `wiki\<디렉토리>\`에 생성.
3. 양방향 링크를 연결하고 `wiki\index.md`·`wiki\log.md`를 갱신한다.
4. 타입이 미등록이면 먼저 `/propose-type`로 제안한다.
