---
type: Analysis
title: Product·Financial Product 인제스트 누락 분석 및 재개 옵션
description: KOSPI 배치 인제스트(347/833) 동안 products·financial_products·ratings 타입이 거의 갱신되지 않은 원인과 보완 선택지
tags: [인제스트, 범위, products, financial_products, ratings, 재개옵션]
timestamp: 2026-06-29T00:00:00Z
---

# Product·Financial Product 인제스트 누락 분석

## 1. 현황 (2026-06-29 기준, KOSPI 347/833 완료 시점)

| 타입 | 페이지 수(index 제외) | 비고 |
|---|---|---|
| `companies/` | 666 | 루프 동안 폭증(신규 Full + stub) |
| `segments/` | 909 | 기업당 1~5개 정상 생성 |
| `products/` | 11 | **전부 초기 세션 산물** (DRAM·HBM·MLCC·NAND_Flash·OLED패널·TC본더·반도체패키지기판·정밀감속기·초고압변압기 등) |
| `financial_products/` | 12 | **전부 초기 세션 산물** (KB금융·미래에셋·신영 계열) |
| `ratings/` | 29 | 대부분 초기, 루프 중 소수만(예: 미래아이앤지) |

→ 루프 구간(배치 CH~DI, 약 80여 개사) 동안 **products·financial_products는 신규 0개**.

## 2. 원인

버그가 아니라 **오케스트레이션 범위 설정의 결과**다.

- 매 배치 서브에이전트에게 지정한 "Full depth" 작업 목록을 **5종으로 고정**: Company + Annual Report + Business Segment + Value Chain + Executive.
- CLAUDE.md 워크플로의 추가 타입 — `products/상품명`(주요 상품·점유율), 금융사용 `financial_products/상품명`·`ratings/기업명 신용등급` — 을 **배치 프롬프트에서 제외**.
- 사유: (a) 3개사 병렬 배치의 속도·토큰 비용 관리, (b) 점유율·주력상품 정보를 **Business Segment·Company 본문에 인라인 기록**(예: 오뚜기 분말카레 82.7%, 경동나비엔 보일러 1위, 삼화왕관 병마개)하여 정보 자체는 보존됨, (c) 루프 구간 대부분이 제조·지주사라 금융 타입 수요가 적었음(참저축은행·무림캐피탈 등 일부 금융성 회사는 체계적 미처리).

## 3. 재개 시 선택 옵션 (사용자 결정 대기)

다음 작업 재개 시 아래 중 하나를 선택한다.

- **옵션 A — 범위 확대(권장):** 앞으로의 배치부터 5종 → **7종**으로 확대.
  - 제조·유통사: `products/` 주요 상품·점유율 페이지 추가(점유율/주력제품이 뚜렷한 경우)
  - 금융사(증권·보험·은행·캐피탈·저축은행): `financial_products/` + `ratings/` 추가
  - 장점: 이후 분량은 taxonomy 완전 준수. 단점: 배치당 비용↑·속도↓.

- **옵션 B — 기존 347개사 소급 백필:** 별도 패스로 점유율/주력상품 뚜렷한 기업에 Product, 금융사에 financial_products·ratings 생성.
  - 장점: 과거분까지 일관. 단점: 추가 루프 필요·비용 큼.

- **옵션 C — 현행 유지:** 점유율 정보는 이미 segment/company 본문에 있으므로 Product 노드는 **핵심 기업만 선별** 생성, financial_products는 금융사 ingest 시에만.
  - 장점: 효율적. 단점: 노드 단위 비교/링크는 제한적.

- **옵션 D — 하이브리드:** 재개분은 옵션 A 적용 + 과거분은 대표 기업(점유율 1위·금융 주요사)만 선별 백필.

## 4. 권고

기본은 **옵션 A**(재개분 7종 확대). 과거분 백필(B)은 비용이 크므로 사용자 우선순위에 따라 선택. 결정되면 배치 서브에이전트 프롬프트 템플릿에 products/financial_products/ratings 항목을 추가해 적용한다.

# Citations

- 본 분석은 2026-06-29 위키 디렉토리 상태 점검 및 `dart_pipeline/ingest_status.py KOSPI`(347/833) 기준.
- 범위 기준: [CLAUDE.md] 워크플로(Ingest 단계 4: products·financial_products·ratings 포함).
