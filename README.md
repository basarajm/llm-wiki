# 한국 기업 리서치 위키 (LLM Wiki)

> 한국 상장기업 **사업보고서(DART)를 Claude가 읽어 OKF 마크다운 위키로 구조화**한 리서치 지식베이스.
> 기업·그룹·주주·산업·공급망을 교차링크로 연결해, 질문할수록 풍부해지는 영속적 지식 그래프를 만듭니다.

Claude(Code·데스크탑) 기반의 한국 상장기업 분석 위키 시스템.
사업보고서를 **OKF(Open Knowledge Format) v0.1** 마크다운 번들로 구조화하고,
Claude가 생성·확장·검진·질의·운영을 담당합니다. 별도 프로그램·런타임 불필요.

`Markdown` · `OKF v0.1` · `Claude Code / Desktop` · `Obsidian 호환` · `PowerShell/Python 보조 스크립트`

### 저장소 개요

| 항목 | 내용 |
|---|---|
| **무엇** | 한국 상장사 사업보고서 기반 리서치 위키 + 운영 엔진(패키지) |
| **형식** | OKF v0.1 (YAML frontmatter + 마크다운 본문, 페이지 링크 = 엔티티 관계) |
| **수록 범위** | 16개 상장사 · 위키 페이지 **212개** · 12개 페이지 타입 · 그래프 212노드/863엣지 |
| **수록 기업** | 삼성전자·SK하이닉스·삼성전기·한미반도체·주성엔지니어링·대한광통신·현대자동차·현대오토에버·LG전자·HD현대일렉트릭·레인보우로보틱스·에스피지·KB금융지주·미래에셋증권·한국투자증권·신영증권 |
| **운영 기능** | 인제스트 / 검진(lint) / 질의(query) / 비교 / 관계추론(connect) / 대시보드 — 슬래시 커맨드 8종 + 스크립트 10개 |
| **폴더 구조** | `wiki\`(콘텐츠) · `engine\`(시스템) · `source_documents\`(원본) |
| **사용 환경** | Claude Code(루트 폴더 열기) 또는 Claude 데스크탑 · Obsidian(`wiki\` Vault) |
| **데이터 출처** | 금융감독원 전자공시(DART) 사업보고서 (공개 자료) |

---

## 핵심 개념

원본 사업보고서(immutable) → Claude가 읽고 추출·교차참조 → **영속적이고 누적되는 위키**.
질문할 때마다 처음부터 재발견하는 RAG와 달리, 지식이 한 번 컴파일된 뒤 계속 최신으로 유지됩니다.
페이지 간 링크가 곧 엔티티 간 관계이며, 위키가 커질수록 연결이 풍부해집니다.

---

## 빠른 시작

1. **Claude Code**: 이 폴더를 열면 `CLAUDE.md`가 자동 로드됩니다.
2. 운영은 슬래시 커맨드로:

   ```
   /ingest AnnualReport_Recent\      # 최신 보고서 배치 인제스트
   /query 삼성전자와 SK하이닉스의 HBM 경쟁력 비교
   /compare 삼성전자 SK하이닉스 한미반도체
   /connect 삼성전자 한미반도체       # 공급망 관계 추적
   /lint                             # 위키 검진
   /wiki-status                      # 운영 대시보드
   ```
3. **Claude 데스크탑**에서는 `CLAUDE.md`+`engine\OPERATIONS.md`를 참조시키면 동일 워크플로가 동작합니다.

설치·배포·재타게팅은 [INSTALL.md](engine/INSTALL.md), 패키지 구조는 [PACKAGE.md](engine/PACKAGE.md) 참조.

---

## 페이지 타입 (12)

| 타입 | 디렉토리 | 타입 | 디렉토리 |
|---|---|---|---|
| Company | `companies\` | Executive | `executives\` |
| Corporate Group | `groups\` | Financial Product | `financial_products\` |
| Industry | `industries\` | Credit Rating | `ratings\` |
| Shareholder | `shareholders\` | Annual Report | `sources\` |
| Value Chain | `value_chain\` | Analysis | `outputs\` |
| Business Segment | `segments\` | | |
| Product | `products\` | | |

스키마 정의는 [taxonomy.md](engine/taxonomy.md).

---

## 운영 기능 (operations layer)

3중 레이어로 데스크탑·Code 모두에서 동작합니다. 상세는 [OPERATIONS.md](engine/OPERATIONS.md).

| 기능 | 커맨드 | 스크립트 |
|---|---|---|
| 인제스트 | `/ingest` (단일/배치/dry-run/re-ingest) | `engine\scripts\list-pending.ps1` |
| 검진 | `/lint` | `engine\scripts\lint.ps1`, `validate-okf.ps1` |
| 주제 관리 | `/propose-type` | — |
| 질의응답 | `/query` | — |
| 비교 분석 | `/compare` | — |
| 관계 추론 | `/connect` | `engine\scripts\build-viz.py` |
| 대시보드 | `/wiki-status` | `engine\scripts\stats.ps1` |
| 페이지 생성 | `/new-page` | — |
| 인덱스 동기화 | — | `engine\scripts\build-index.ps1` |

---

## 디렉토리 구조 (3분할)

역할별로 **위키 콘텐츠 / 시스템 / 원본**을 명확히 분리했습니다.

```
D:\.LLMWiki\
├── CLAUDE.md              Claude 운영 지침 (루트, 자동 로드)
├── README.md              안내 (이 파일)
├── .gitignore
├── .claude\commands\      슬래시 커맨드 8종
│
├── wiki\                  ◀ 위키 콘텐츠 (OKF 번들 — 크로스링크 /companies/… 의 기준)
│   ├── index.md / log.md  카탈로그 / 이력 (예약 파일)
│   ├── viz.html           그래프 뷰어
│   ├── companies\ groups\ industries\ shareholders\ value_chain\
│   ├── segments\ products\ executives\ financial_products\ ratings\
│   ├── sources\           사업보고서 요약
│   └── outputs\           분석 결과물
│
├── engine\                ◀ 시스템/운영 (재사용·배포 대상)
│   ├── taxonomy.md        타입·스키마 (단일 관리)
│   ├── OPERATIONS.md      운영 매뉴얼
│   ├── INSTALL.md / PACKAGE.md
│   ├── templates\         타입별 템플릿
│   └── scripts\           운영 스크립트 (ps1 / sh / py)
│
└── source_documents\      ◀ 원본 사업보고서 (읽기 전용)
    ├── AnnualReport_Recent\  최신 (1차 ingest 대상)
    ├── AnnualReport_MD\      아카이브 (다년·분기·반기)
    └── raw\                  신규 소스 드롭 (raw\assets\ 이미지)
```

> **Obsidian으로 볼 때**는 `wiki\` 폴더를 Vault로 지정하면 됩니다(크로스링크가 이 폴더 기준).

---

## OKF 표준

[Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) v0.1 준수.
모든 페이지는 YAML frontmatter + 마크다운 본문이며, 별도 도구 없이 git·텍스트 에디터로 관리 가능합니다.
`engine\scripts\validate-okf.ps1`로 적합성을 검증합니다.
