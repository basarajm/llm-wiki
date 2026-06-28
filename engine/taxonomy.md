---
type: Taxonomy
title: 위키 주제 분류 체계
description: 이 위키에서 사용하는 모든 페이지 타입의 정의와 스키마
timestamp: 2026-06-27T00:00:00Z
---

이 파일은 위키의 **단일 주제 관리 파일**입니다.
Claude는 새 페이지 생성 전 반드시 이 파일을 참조하고,
새 타입이 필요하면 `## 신규 주제 후보` 섹션에 제안한 후 사용자 승인을 받습니다.
타입 추가·수정 시 `## 변경 이력`에 한 줄 기록합니다.

---

## 등록된 타입 목록

| 타입명 | 디렉토리 | 설명 |
|---|---|---|
| Company | `companies\` | 기업 메인 페이지 (상장·비상장·해외 거래상대방 stub 포함) |
| Market | `markets\` | 상장 시장 (KOSPI·KOSDAQ) — 상장기업 분류 및 구성종목 |
| Corporate Group | `groups\` | 기업집단·그룹 (계열사·지배구조) |
| Industry | `industries\` | 산업 분석 및 경쟁 구도 |
| Shareholder | `shareholders\` | 주요 주주 (기관·개인·외국인·상장기업) |
| Value Chain | `value_chain\` | 기업의 공급사·고객사 관계 |
| Business Segment | `segments\` | 기업 내 사업 부문 |
| Product | `products\` | 주요 상품 및 시장 점유율 |
| Executive | `executives\` | 경영진·이사회 구성원 |
| Financial Product | `financial_products\` | 금융사 상품 (예금·대출·신탁·보험·카드) |
| Credit Rating | `ratings\` | 신용평가 등급 이력 |
| Annual Report | `sources\` | 사업보고서 요약 |
| Analysis | `outputs\` | 쿼리 기반 분석 결과물 |

**경쟁사(Competitor)는 별도 타입을 두지 않습니다.** 경쟁사는 그 자체로 Company이므로
Company stub 페이지 + Industry/Product의 비교 섹션 + cross-link로 표현합니다(중복 방지).

---

## 타입별 스키마

### Company

상장 한국기업이 1차 대상이나, 그래프 연결을 위해 **해외·비상장 거래상대방**(예: 포스코, 한국전력공사,
사우디전력청, ASML 등)도 경량 **stub 페이지**로 생성할 수 있습니다. stub은 `## 사업 개요`와 `# Citations`만 채웁니다.

```yaml
---
type: Company
title: <기업명>
description: <한 문장 사업 요약>
ticker: "<종목코드>"          # 문자열, 앞자리 0 보존. 비상장·해외는 생략
market: KOSPI | KOSDAQ | Foreign | Private
market_page: /markets/<KOSPI|KOSDAQ>   # 상장사(KOSPI·KOSDAQ)만. 시장↔기업 양방향 링크
industry: <주요 산업>
group: /groups/<그룹명>       # 기업집단 소속 시
is_stub: false                # 거래상대방 경량 노드면 true
tags: [기업, <산업>, <시장>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
source_count: <연결된 사업보고서 수>
---
```

**필수 섹션:**
- `## 사업 개요`
- `## 재무 하이라이트` — 최근 3개년 매출·영업이익·순이익 표 (stub 제외)
- `## 사업 부문` — segments\ 링크 (stub 제외)
- `## 주요 주주` — shareholders\ 링크, 상장기업 주주는 companies\ 링크 병기 (stub 제외)
- `## 밸류체인` — value_chain\ 링크 (stub 제외)
- `## 경영진` — executives\ 링크 (stub 제외)
- `## 리스크` (stub 제외)
- `# Citations`

---

### Market

KOSPI(유가증권시장)·KOSDAQ(코스닥시장) 등 상장 시장 페이지입니다. 해당 시장에 상장된
기업(Company)을 분류·집계하는 노드로, Company의 `market_page` 와 양방향으로 연결됩니다.

```yaml
---
type: Market
title: <시장명>                # 예: KOSPI (유가증권시장)
description: <한 문장 시장 설명>
market_code: KOSPI | KOSDAQ
operator: 한국거래소(KRX)
tags: [시장, <market_code>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---
```

**필수 섹션:**
- `## 시장 개요` — 시장 성격, 상장요건 개요, 대표 지수
- `## 상장기업` — 위키에 페이지가 존재하는 해당 시장 상장기업 목록 (`/companies/` 링크).
  기업 수가 많으므로 산업·그룹별로 묶어도 됨. ingest로 신규 기업 추가 시 이 목록도 갱신.
- `# Citations`

---

### Corporate Group

```yaml
---
type: Corporate Group
title: <그룹명>
description: <한 문장 그룹 설명>
controlling_person: <동일인(총수)>      # 미확인 시 생략
member_companies: [/companies/A, /companies/B]
tags: [기업집단, <그룹명>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---
```

**필수 섹션:**
- `## 그룹 개요`
- `## 계열사` — companies\ 링크 목록, 핵심 계열사 표시
- `## 지배구조` — 지주회사·순환출자·주요 지분 관계
- `# Citations`

---

### Industry

```yaml
---
type: Industry
title: <산업명>
description: <한 문장 산업 설명>
tags: [산업, <세부분류>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---
```

**필수 섹션:**
- `## 시장 구조` — 규모, 성장률
- `## 주요 플레이어` — companies\ 링크
- `## 경쟁 구도` — 점유율·재무 비교표, 경쟁사 cross-link (해외 경쟁사는 stub Company 링크)
- `## 트렌드 및 이슈`
- `## 규제 환경`
- `# Citations`

---

### Shareholder

```yaml
---
type: Shareholder
title: <주주명>
description: <한 문장 주주 설명>
entity_type: 기관 | 개인 | 외국인 | 상장기업
company_page: /companies/<기업명>   # entity_type이 상장기업인 경우만
tags: [주주, <entity_type>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---
```

**필수 섹션:**
- `## 개요`
- `## 주요 보유 종목` — 보유 기업, 지분율 표 (companies\ 링크)
- `## 투자 성향` (기관·외국인의 경우)
- entity_type이 상장기업인 경우: `## 기업 정보 → [기업 페이지](/companies/기업명)`
- `# Citations`

---

### Value Chain

```yaml
---
type: Value Chain
title: <기업명> 밸류체인
description: <기업명>의 주요 공급사와 고객사 관계
company: /companies/<기업명>
tags: [밸류체인, <기업명>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---
```

**필수 섹션:**
- `## 주요 공급사` — 품목별 공급사, companies\ 링크 (상장·식별 가능 기업)
- `## 주요 고객사` — 고객 유형별, companies\ 링크 (상장·식별 가능 기업)
- `## 협상력 분석` — 공급사·고객사 집중도, 대체 가능성
- `# Citations`

---

### Business Segment

```yaml
---
type: Business Segment
title: <기업명> <부문명>
description: <기업명>의 <부문명> 사업 부문
company: /companies/<기업명>
revenue_share: <매출 비중 %>   # 최근 연도 기준
tags: [사업부문, <기업명>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---
```

**필수 섹션:**
- `## 사업 내용`
- `## 매출 및 수익성 추이` — 연도별 표
- `## 주요 제품·서비스` — products\ 링크
- `## 경쟁 현황`
- `## KPI`
- `# Citations`

---

### Product

```yaml
---
type: Product
title: <상품명>
description: <한 문장 상품 설명>
category: <제품 카테고리>
market_share: <글로벌 또는 국내 점유율 %>   # 최근 기준, 불명확하면 생략
tags: [상품, <카테고리>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---
```

**필수 섹션:**
- `## 제품 개요`
- `## 시장 점유율` — 주요 플레이어별 점유율 표
- `## 주요 고객사` — companies\ 링크
- `## 경쟁 제품`
- `## 시장 트렌드`
- `# Citations`

---

### Executive

```yaml
---
type: Executive
title: <임원명>
description: <한 문장 설명 — 소속·직책>
company: /companies/<기업명>
position: <직책>               # 대표이사, 사내이사, 사외이사 등
tags: [임원, <기업명>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---
```

**필수 섹션:**
- `## 개요` — 직책, 선임일, 임기
- `## 경력`
- `## 보수` — 보고연도 기준 (공시된 경우)
- `## 겸직` — 타 기업 겸직 시 companies\ 링크
- `# Citations`

---

### Financial Product

은행·증권·보험·카드 등 금융사의 주요 상품·서비스를 표현합니다.

```yaml
---
type: Financial Product
title: <상품/서비스명>
description: <한 문장 설명>
issuer: /companies/<발행·취급 기업명>
product_type: 예금 | 대출 | 신탁 | 보험 | 카드 | 증권 | 자산운용 | 기타
tags: [금융상품, <product_type>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---
```

**필수 섹션:**
- `## 상품 개요`
- `## 잔액·수익` — 연도별 잔액/수익 표 (공시된 경우)
- `## 고객 세그먼트`
- `# Citations`

---

### Credit Rating

```yaml
---
type: Credit Rating
title: <기업명> 신용등급
description: <기업명>의 신용평가 등급 이력
issuer: /companies/<기업명>
tags: [신용평가, <기업명>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---
```

**필수 섹션:**
- `## 등급 이력` — 평가기관·등급·평가일 표 (회사채/CP/ABS 등 구분)
- `## 평가 근거` — 등급 사유 요약 (공시된 경우)
- `# Citations`

---

### Annual Report

```yaml
---
type: Annual Report
title: <기업명> <연도> 사업보고서
description: <기업명>의 <연도>년도 사업보고서 요약
company: /companies/<기업명>
year: <연도>
filing_date: <YYYY-MM-DD>
tags: [사업보고서, <기업명>, <연도>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
resource: source_documents/AnnualReport_Recent/<원본파일명>
---
```

**필수 섹션:**
- `## 핵심 수치` — 매출, 영업이익, 순이익, 주요 KPI
- `## 주목할 변화` — 전년 대비 유의미한 변화
- `## 사업 부문별 요약`
- `## 가이던스 및 전망`
- `## 리스크 요인`
- `# Citations`

---

### Analysis

```yaml
---
type: Analysis
title: <분석 제목>
description: <한 문장 분석 요약>
query_date: <YYYY-MM-DD>
related: [/companies/기업명, /industries/산업명]   # 관련 페이지 목록
tags: [분석, <주제>]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---
```

**필수 섹션:**
- `## 요약`
- `## 분석 내용`
- `## 결론 및 시사점`
- `# Citations`

---

## 신규 주제 후보

*Claude가 ingest·query·lint 중 새 타입이 필요하다고 판단하면 아래에 추가합니다.*
*사용자 승인 후 위 섹션으로 이동합니다. (`/propose-type` 워크플로 참조)*

<!-- 현재 후보 없음 -->

---

## 변경 이력

- 2026-06-26: 초기 8개 타입 등록 (Korean Company, Industry, Shareholder, Value Chain, Business Segment, Product, Annual Report, Analysis).
- 2026-06-27: 타입 12개로 확장. `Korean Company`→`Company` 일반화(stub·group·market 필드 추가). 신규 타입 추가: Corporate Group, Executive, Financial Product, Credit Rating. 경쟁사 처리 원칙 명문화. Industry에 `## 경쟁 구도` 섹션 추가.
- 2026-06-28: 타입 13개로 확장. 신규 타입 **Market**(`markets\`) 추가 — KOSPI·KOSDAQ 시장 분류 페이지. Company 스키마에 `market_page` 양방향 링크 필드 추가.
