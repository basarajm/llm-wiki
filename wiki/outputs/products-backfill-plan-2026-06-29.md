---
type: Analysis
title: Product·Financial Product 백필 실행 계획 (옵션 B / B1)
description: 직전 gap 분석에서 결정된 옵션 B 백필을 B1(커밋된 위키 본문 추출) 방식으로 실행하기 위한 방법론·범위·오케스트레이션·진행 로그
tags: [인제스트, 백필, products, financial_products, ratings, 옵션B, B1, 실행계획]
timestamp: 2026-06-29T00:00:00Z
---

# Product·Financial Product 백필 실행 계획

> 선행 분석: [Product·Financial Product 인제스트 누락 분석](/outputs/ingest-scope-products-gap-2026-06-29)

## 1. 결정 (2026-06-29)

- **범위:** 옵션 B — 기존에 인제스트된 full(비-stub) 기업에 누락된 `products`·`financial_products`·`ratings` 노드를 소급 백필.
- **원본 확보:** **B1** — 이 PC에는 KOSPI 대량 다운로드본(`dart_pipeline/dart_md/`, gitignore)이 없으므로, **이미 커밋된 위키 본문**(company·segment 페이지의 인라인 점유율·주력상품 정보)에서 노드를 추출한다.
- **원본 전문 보강:** 원본 파일이 있는 환경에서 전문(全文)을 검토해 내용을 추가하는 작업은 **후속 패스**로 분리한다(사용자 예정분). 본 패스에서 생성한 노드는 그 보강의 골격이 된다.

## 2. 대상

- full(비-stub) 기업: **353개** (stub 기업은 본문이 빈약하여 제외).
- 이미 `products`/`financial_products`가 있는 초기 16개사(삼성전자·SK하이닉스·삼성전기·미래에셋증권·신영증권·한국투자증권·KB금융 등)는 **신규 노드만 보완**(기존 노드 재생성 금지, 링크 보강).

## 3. 추출 규칙

**제조·유통사 → `products/`**
- 주력제품 또는 시장 점유율이 **뚜렷한 경우에만** 노드화(옵션 C 기준 계승). 지주회사는 통상 제외(자체 제품 없음).
- 기존 공유 노드(DRAM·HBM·MLCC·NAND_Flash·OLED패널·TC본더·반도체패키지기판·정밀감속기·초고압변압기·카메라모듈·협동로봇)는 **재생성하지 않고 링크**, 필요 시 `## 주요 고객사`·`## 시장 점유율`에 해당 기업 링크만 추가.
- 양방향: company `## 주요 제품·서비스` ↔ product `## 주요 고객사`/`## 시장 점유율`.

**금융사(증권·보험·은행·카드·캐피탈·저축은행·금융지주) → `financial_products/` + `ratings/`**
- 본문에 상품·잔액·신용등급 정보가 있으면 노드화. 정보가 stub 수준이면 생략.

**출처·품질**
- Citations는 위키 source/segment/company 페이지를 인용(B1). 점유율·수치가 본문에 명시되지 않으면 "추정" 또는 "미확인" 표기.
- 모든 노드는 `engine/templates/`의 해당 타입 템플릿과 `engine/taxonomy.md` 스키마를 준수.

## 4. 오케스트레이션

- Workflow 다중 에이전트, 동시 실행 **최대 14개**(16코어 기준 `min(16, 코어−2)`). 이전 배치(3개 동시) 대비 약 4.7배.
- **쓰기 충돌 방지:** 각 에이전트는 자신이 담당한 기업의 **신규 노드 파일만** 작성하고 매니페스트를 반환한다. 공유 product 중복 제거, `wiki/index.md`·`wiki/log.md` 갱신, company 페이지 역링크는 **오케스트레이터가 사후 일괄 처리**.
- 파일럿(소수 기업)으로 품질·병합·링크를 검증한 뒤 전량으로 확대.

## 5. 진행 로그

| 일자 | 단계 | 결과 |
|---|---|---|
| 2026-06-29 | 계획 수립 | 옵션 B / B1 확정, 대상 353개사 산정 |
| 2026-06-29 | 파일럿 실행 | 12개사, 신규 노드 17개 |
| 2026-06-29 | 확대 청크 | 69개사 처리, 신규 노드 48개 |

# Citations

- [Product·Financial Product 인제스트 누락 분석](/outputs/ingest-scope-products-gap-2026-06-29)
- [CLAUDE.md] 워크플로 Ingest 단계 4 (products·financial_products·ratings)
- [engine/taxonomy.md] Product·Financial Product·Credit Rating 스키마
