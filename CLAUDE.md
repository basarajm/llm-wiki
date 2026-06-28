# 한국 기업 리서치 위키 — Claude 운영 지침

이 디렉토리는 한국 상장기업 사업보고서 기반 리서치 위키입니다.
OKF(Open Knowledge Format) 표준을 따르는 마크다운 파일 컬렉션이며,
Claude(Code·데스크탑)가 위키의 생성·유지·갱신·검진·질의를 담당합니다.

## 폴더 구조 (3분할)

프로젝트는 역할별로 **3개의 상위 폴더**로 분리되어 있습니다.

| 상위 폴더 | 역할 |
|---|---|
| `wiki\` | **위키 콘텐츠 (OKF 번들)** — Claude가 생성·관리. 크로스링크 `/companies/...`의 기준 루트 |
| `engine\` | **시스템/운영** — taxonomy·매뉴얼·템플릿·스크립트 (재사용·배포 대상) |
| `source_documents\` | **원본 사업보고서** (읽기 전용) |

루트에는 `CLAUDE.md`(이 파일), `README.md`, `.gitignore`, `.claude\`(슬래시 커맨드)만 둡니다.

운영 기능의 상세 절차는 **`engine\OPERATIONS.md`(운영 매뉴얼)** 에 정리되어 있습니다.
Claude Code에서는 `.claude\commands\`의 슬래시 커맨드(`/ingest`, `/lint`, `/query` 등)로 호출하고,
데스크탑 등에서는 본 문서와 `engine\OPERATIONS.md`의 절차를 그대로 따르면 됩니다.

---

## 세션 시작 시 필수 확인

새 대화가 시작되면 **반드시 다음 순서로 파일을 읽으십시오**:

1. `engine\taxonomy.md` — 위키의 페이지 타입과 스키마 정의 (현재 12개 타입)
2. `wiki\index.md` — 현재 존재하는 모든 페이지 목록

이 두 파일을 읽기 전에는 어떤 페이지도 생성하거나 수정하지 마십시오.
운영 작업(ingest/lint/query 등)을 수행할 때는 `engine\OPERATIONS.md`도 참조하십시오.

---

## 디렉토리 역할 (상세)

**`source_documents\` — 원본 (읽기 전용, 절대 수정 금지)**

| 경로 | 역할 |
|---|---|
| `source_documents\AnnualReport_Recent\` | 최신 사업보고서 (1차 ingest 대상) |
| `source_documents\AnnualReport_MD\` | 사업보고서 아카이브 (다년·분기·반기 포함) |
| `source_documents\raw\` | 신규 소스 드롭 폴더 (향후 추가분), `raw\assets\` 이미지 |

**`wiki\` — 위키 콘텐츠**

| 경로 | 역할 |
|---|---|
| `wiki\index.md` / `wiki\log.md` | 전체 카탈로그 / 작업 이력 (예약 파일) |
| `wiki\companies\` | 기업별 메인 페이지 (상장·비상장·해외 거래상대방 stub 포함) |
| `wiki\markets\` | 상장 시장 페이지 (KOSPI·KOSDAQ) — 상장기업 분류·구성종목 |
| `wiki\groups\` | 기업집단·그룹 페이지 |
| `wiki\industries\` | 산업 분석 페이지 |
| `wiki\shareholders\` | 주요 주주 페이지 |
| `wiki\value_chain\` | 공급사·고객사 관계 페이지 |
| `wiki\segments\` | 기업별 사업 부문 페이지 |
| `wiki\products\` | 주요 상품 및 시장 점유율 페이지 |
| `wiki\executives\` | 경영진·이사회 페이지 |
| `wiki\financial_products\` | 금융사 상품 페이지 |
| `wiki\ratings\` | 신용평가 등급 이력 페이지 |
| `wiki\sources\` | 사업보고서별 요약 페이지 |
| `wiki\outputs\` | 쿼리 분석 결과물 (비교표, 투자 메모, lint 리포트 등) |

**`engine\` — 시스템/운영**

| 경로 | 역할 |
|---|---|
| `engine\taxonomy.md` | 페이지 타입·스키마 정의 |
| `engine\OPERATIONS.md` | 운영 매뉴얼 |
| `engine\INSTALL.md` / `engine\PACKAGE.md` | 설치·배포 / 패키지 매니페스트 |
| `engine\templates\` | 타입별 페이지 템플릿 |
| `engine\scripts\` | 운영 보조 스크립트 (validate-okf, lint, stats 등) |
| `.claude\commands\` | Claude Code 슬래시 커맨드 정의 (루트의 `.claude\`) |

> **원본 소스 위치 규칙:** ingest 대상은 기본적으로 `source_documents\AnnualReport_Recent\`에서 찾습니다.
> 과거·분기·반기 자료가 필요하면 `source_documents\AnnualReport_MD\`를 참조합니다. 신규 파일은
> `source_documents\raw\`에 둡니다. Claude는 `source_documents\` 원본을 절대 수정하지 않습니다.

---

## OKF 파일 형식 규칙

### 프론트매터 (모든 페이지 필수)

```yaml
---
type: <taxonomy.md에 등록된 타입명>
title: <페이지 제목>
description: <한 문장 요약>
tags: [태그1, 태그2]
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
---
```

`type`은 비어 있으면 안 되며 `engine\taxonomy.md`에 등록된 값이어야 합니다(OKF v0.1 필수 규칙).

### 예약 파일 형식

**wiki\index.md** — 프론트매터 없음. 디렉토리 내 파일 목록:
```
* [제목](경로) - 한 줄 설명
```

**wiki\log.md** — 프론트매터 없음. 시계열 이력:
```
## YYYY-MM-DD

**Ingest** / **Update** / **Creation** / **Query** / **Lint** / **Taxonomy** 액션 설명
```

### 크로스 링크

- **절대 경로(번들 기준) 권장**: `[삼성전자](/companies/삼성전자)`
  여기서 `/`는 `wiki\` 폴더(OKF 번들 루트)를 가리킵니다. 즉 `/companies/삼성전자` → `wiki\companies\삼성전자.md`.
- Obsidian 위키링크도 허용: `[[삼성전자]]` (Vault를 `wiki\` 폴더로 지정)
- 링크는 관계를 표현하므로 적극적으로 사용 (OKF에서 링크 = 엔티티 간 관계)

---

## 워크플로 개요

상세 절차·옵션은 `engine\OPERATIONS.md` 참조. 아래는 핵심 요약입니다.

### Ingest (소스 추가)

사용자 명령: `ingest [파일명]`, `[파일명] 분석해줘`, `ingest AnnualReport_Recent`(배치) 등.

#### 단일 파일 ingest

1. 대상 폴더(`source_documents\AnnualReport_Recent\` 우선)에서 파일 읽기
2. 핵심 내용 요약 후 사용자와 주목 포인트 논의 (배치 시 생략)
3. `wiki\sources\`에 요약 페이지 생성 (type: Annual Report). `resource:`에 원본 경로 기재
   (예: `source_documents/AnnualReport_Recent/<파일명>`)
4. 다음 페이지들 확인 후 업데이트 또는 신규 생성 (모두 `wiki\` 하위):
   - `companies\기업명.md` — 재무지표·변화 반영 (type: Company)
   - `groups\그룹명.md` — 기업집단 소속이면 계열사 목록 갱신 (type: Corporate Group)
   - `industries\산업명.md` — 산업 동향·경쟁 구도 업데이트
   - `shareholders\주주명.md` — 지분 구조
   - `value_chain\기업명_밸류체인.md` — 공급사·고객사
   - `segments\기업명_부문명.md` — 사업 부문별 실적
   - `products\상품명.md` — 주요 상품 및 점유율
   - `executives\임원명.md` — 핵심 경영진(대표이사 등)
   - 금융사: `financial_products\상품명.md`, `ratings\기업명 신용등급.md`
5. 식별 가능한 공급사·고객사·경쟁사는 `wiki\companies\`에 **stub 페이지**(`is_stub: true`)로 노드화
6. 새 타입이 필요하면 `engine\taxonomy.md`의 `## 신규 주제 후보`에 기록 (`/propose-type`)
7. `wiki\index.md` 업데이트(또는 `engine\scripts\build-index.ps1` 실행), `wiki\log.md`에 `**Ingest** 파일명` 기록

#### 폴더 전체 batch ingest

1. 대상 폴더 파일 목록 확인 — 이미 `wiki\sources\`에 `resource:`로 참조된 파일은 건너뜀
   (`engine\scripts\list-pending.ps1`로 미처리 목록 자동 산출 가능)
2. **버전 중복 정리**: `[기재정정]`·`첨부00760/00761` 등 동일 보고서 변형은 본문(00760 또는 정정본) 우선
3. 처리할 목록을 사용자에게 보고하고 확인 요청
4. 파일을 **하나씩 순서대로** 처리(개별 논의 생략), 각 완료 후 `[N/전체] 파일명 완료` 보고
5. 전체 완료 후 요약(처리 수·신규/갱신 페이지·신규 주제 후보) 보고
6. `wiki\log.md`에 배치 1건 기록: `**Batch Ingest** N개 파일 처리 완료 — ...`

**이미 처리된 파일 판별 기준:**
`wiki\sources\`에 해당 파일명을 `resource:` frontmatter로 참조하는 페이지가 존재하면 처리 완료로 간주.
재처리는 사용자가 `re-ingest [파일명]`을 명시할 때만.

---

### 양방향 링크 규칙 (중요)

연결성이 위키의 핵심 가치입니다. 다음 관계는 **반드시 양방향**으로 링크합니다.
(링크 경로는 모두 번들 기준 절대경로 `/dir/page`)

**주주 ↔ 기업** — 주주가 KOSPI/KOSDAQ 상장기업인 경우:
- Shareholder 페이지 frontmatter에 `company_page: /companies/기업명`
- Shareholder 페이지 본문에 `→ [기업 페이지](/companies/기업명)`
- Company `## 주요 주주`에 `/companies/` 링크 병기
  예: `- [삼성생명](/shareholders/삼성생명) — 8.5% | [기업 페이지](/companies/삼성생명)`

**시장 ↔ 기업** — 기업이 KOSPI/KOSDAQ 상장사인 경우:
- Company frontmatter `market: KOSPI|KOSDAQ` 및 `market_page: /markets/KOSPI|KOSDAQ`
- Market `## 상장기업`에 `/companies/기업명` 링크 (신규 기업 ingest 시 목록 갱신)

**그룹 ↔ 기업:**
- Company frontmatter `group: /groups/그룹명`
- Corporate Group `## 계열사`에 `/companies/기업명` 링크

**임원 ↔ 기업:**
- Executive frontmatter `company: /companies/기업명`
- Company `## 경영진`에 `/executives/임원명` 링크

**공급사·고객사 ↔ 기업:**
- Value Chain 페이지에서 식별 가능한 상대방은 `/companies/` 링크(필요 시 stub 생성)

---

### Query (질문 답변)

1. `wiki\index.md` 읽기 → 관련 페이지 파악 (index-first 검색)
2. 관련 페이지 읽기 → 답변 합성 (반드시 출처 페이지 인용)
3. 중요한 분석·비교·인사이트는 `wiki\outputs\`에 저장 (type: Analysis) 후 index·log 갱신
4. 누락된 정보·주제 발견 시 `engine\taxonomy.md` 신규 후보 섹션에 기록

관계 추론(`/connect`)·비교표(`/compare`) 등 상세는 `engine\OPERATIONS.md` 참조.

---

### Lint (위키 건강 검진)

사용자 명령: `lint` 또는 `/lint`. 기계적 점검은 `engine\scripts\lint.ps1`, 의미적 점검은 Claude가 수행.

점검 항목:
- `type:` frontmatter 누락 / 미등록 타입
- 깨진 내부 링크, 고아 페이지(인바운드 링크 0)
- 양방향 링크 누락 (주주·그룹·임원 ↔ 기업)
- 모순: 같은 수치가 페이지마다 다름
- 누락 링크: 텍스트로만 언급되고 링크 없는 기업·주주명
- 구버전 정보: 더 최신 보고서가 있는데 미갱신
- index.md 미등록 페이지
- taxonomy.md 신규 후보 보고

결과를 `wiki\outputs\lint-report-YYYY-MM-DD.md`로 저장하고 `wiki\log.md`에 기록.

---

### 신규 주제 타입 제안 (`/propose-type`)

Claude가 새 페이지 타입이 필요하다고 판단할 때:
1. **직접 생성하지 않음**
2. `engine\taxonomy.md`의 `## 신규 주제 후보`에 기록:
   `- **타입명**: 필요한 이유, 예상 frontmatter 필드, 예상 섹션`
3. 사용자에게 알리고 승인 요청
4. 승인 후: `taxonomy.md` 표 등록 → `wiki\` 하위 디렉토리 생성 → `engine\templates\` 추가 → `## 변경 이력` 기록 → index 반영

---

## 품질 기준

- 모든 수치에는 출처 페이지를 `# Citations` 섹션에 기록
- 불확실한 정보는 "추정" 또는 "미확인" 표시
- 페이지 업데이트 시 `timestamp` frontmatter 갱신
- 기업명은 공식 명칭 사용 (삼성전자㈜ → 삼성전자)
- 금액 단위: 원칙적으로 억 원 또는 조 원 사용
- 새 페이지는 `engine\templates\`의 해당 타입 템플릿을 기반으로 작성
