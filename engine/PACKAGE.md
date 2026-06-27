# 패키지 매니페스트 — 엔진 vs 인스턴스

이 위키는 **데이터 분리형**으로 설계되어, 재사용 가능한 **엔진**과 이 위키 고유의 **인스턴스 데이터**가
폴더 단위로 명확히 구분됩니다. 타 시스템 배포 시 엔진만 복사하면 빈 위키를 시작할 수 있습니다
(`engine\scripts\new-wiki.ps1`).

폴더 3분할: `wiki\`(콘텐츠=인스턴스) · `engine\`(시스템=엔진) · `source_documents\`(원본=인스턴스).

---

## 엔진 (배포 대상 — 도메인 공통 재사용)

| 경로 | 역할 |
|---|---|
| `CLAUDE.md` (루트) | Claude 운영 지침 (세션 규칙·워크플로) |
| `README.md` (루트) | 사용자 안내 |
| `.gitignore` (루트) | 배포 시 원본 데이터 제외 옵션 |
| `.claude\commands\` (루트) | Claude Code 슬래시 커맨드 |
| `engine\taxonomy.md` | 페이지 타입·스키마 정의 |
| `engine\OPERATIONS.md` | 운영 매뉴얼 (모든 기능 절차) |
| `engine\INSTALL.md` | 설치·배포 가이드 |
| `engine\PACKAGE.md` | (이 파일) 매니페스트 |
| `engine\templates\` | 타입별 페이지 템플릿 |
| `engine\scripts\` | 운영 보조 스크립트 (validate/lint/stats/build-index/new-wiki/build-viz) |

## 인스턴스 (이 위키의 데이터 — 배포 시 제외/선택)

| 경로 | 역할 |
|---|---|
| `source_documents\AnnualReport_Recent\`, `…\AnnualReport_MD\` | 원본 사업보고서 (대용량) |
| `source_documents\raw\` | 신규 소스 드롭 |
| `wiki\companies\`,`groups\`,`industries\`,`shareholders\`,`value_chain\`, `segments\`,`products\`,`executives\`,`financial_products\`,`ratings\`,`sources\`,`outputs\` | 생성된 위키 페이지 |
| `wiki\index.md`, `wiki\log.md`, `wiki\viz.html` | 인스턴스별 카탈로그·이력·그래프 |

---

## OKF 적합성 요약

- 모든 콘텐츠 `.md`(`wiki\` 하위)는 YAML frontmatter + 비어있지 않은 `type:`을 가짐 (OKF v0.1 필수).
  검증: `engine\scripts\validate-okf.ps1`
- `wiki\index.md`·`wiki\log.md`는 예약 파일(frontmatter 없음)
- 페이지 간 관계는 마크다운 내부 링크 `[..](/dir/page)`로 표현 (기준 루트 = `wiki\`)
- 인용은 `# Citations` 섹션

## 타입 (12)

Company · Corporate Group · Industry · Shareholder · Value Chain · Business Segment ·
Product · Executive · Financial Product · Credit Rating · Annual Report · Analysis

상세 스키마는 `engine\taxonomy.md` 참조.
