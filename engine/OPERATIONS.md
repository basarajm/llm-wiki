# 운영 매뉴얼 (Operations Manual)

이 문서는 위키를 **구축·확장·검진·질의·운영**하기 위한 모든 기능의 상세 절차를 정리합니다.
기능은 3중 레이어로 제공되어 Claude 데스크탑·Code 어디서나 동작합니다.

| 레이어 | 형태 | 위치 | 용도 |
|---|---|---|---|
| L1 워크플로 명세 | 문서 절차 | `CLAUDE.md`, 본 문서 | 어디서나 따라 할 수 있는 표준 절차 |
| L2 슬래시 커맨드 | 마크다운 커맨드 | `.claude\commands\*.md` | Claude Code에서 1급 호출 |
| L3 스크립트 | PowerShell/Python | `engine\scripts\*` | 결정론적 기계 점검·집계 |

스크립트가 없는 환경(데스크탑)에서는 Claude가 L1 절차로 동일 작업을 수행합니다.

---

## 기능 목록

| 기능 | 슬래시 커맨드 | 백킹 스크립트 | 요약 |
|---|---|---|---|
| 소스 인제스트 | `/ingest` | `list-pending.ps1` | 사업보고서 → 위키 페이지 |
| 위키 검진 | `/lint` | `lint.ps1` | 모순·고아·링크·OKF 점검 |
| 주제 타입 관리 | `/propose-type` | — | 신규 타입 제안·등록 |
| 질의응답 | `/query` | — | index-first 검색 + 인용 + save-back |
| 비교 분석 | `/compare` | — | 다기업·다지표 비교표 |
| 관계 추론 | `/connect` | `build-viz.py` | 엔티티 간 링크 경로 추적 |
| 운영 대시보드 | `/wiki-status` | `stats.ps1` | 커버리지·페이지 수·최근 활동 |
| 페이지 생성 | `/new-page` | — | 템플릿 기반 신규 페이지 |
| 인덱스 재생성 | — | `build-index.ps1` | frontmatter→index.md 동기화 |
| OKF 검증 | — | `validate-okf.ps1` | type frontmatter 적합성 |

---

## 1. Ingest — 소스 인제스트

**모드**
- 단일: `ingest [파일명]` — 한 보고서를 처리하며 사용자와 주목 포인트 논의
- 배치: `ingest AnnualReport_Recent\` — 폴더 전체, 자동 처리
- 미리보기: `ingest --dry-run AnnualReport_Recent\` — 처리 대상·예상 페이지만 출력(실제 생성 X)
- 재처리: `re-ingest [파일명]` — 이미 처리된 파일 강제 재처리

**파일명 파서 규칙** (원본 파일명 → 메타데이터)

원본 명명: `<기업명>-<보고서종류>-<연월>[-첨부XXXXX].md`, 정정본은 `[기재정정]` 접두.

| 토큰 | 의미 | 예 |
|---|---|---|
| 기업명 | 첫 `-` 앞 | `삼성전자` |
| 보고서종류 | 사업보고서 / 반기보고서 / 분기보고서 | `사업보고서` |
| 연월 | `YYYY.MM` | `2025.12` → year=2025 |
| `[기재정정]` | 정정 공시 → 같은 기간 원본보다 우선 | |
| `첨부00760/00761` | 첨부 분리본 → 본문(00760) 우선, 필요 시 병합 참조 | |

**버전 중복 정리:** 같은 (기업, 연월)에 여러 변형이 있으면 `[기재정정]` > 본문 > 첨부 순으로 대표본 선택.

**미처리 판별:** `sources\`에 그 원본 파일명을 `resource:`로 참조하는 페이지가 있으면 처리 완료.
`engine\scripts\list-pending.ps1`이 미처리 목록을 출력. (스크립트 없으면 Claude가 `sources\` 스캔)

**처리 절차:** `CLAUDE.md` > Ingest 참조. 핵심은 sources 요약 → company/group/industry/segment/
product/shareholder/executive/(금융)financial_product·rating 갱신 → stub 노드화 → 양방향 링크 → index·log.

---

## 2. Lint — 위키 검진

`engine\scripts\lint.ps1` 실행(기계 점검) + Claude의 의미 점검을 결합.

**기계 점검 (스크립트):**
1. 비예약 `.md`에 `type:` frontmatter 존재·비어있지 않음 (OKF 필수)
2. 깨진 내부 링크 (`/dir/page` 대상 파일 부재)
3. 고아 페이지 (인바운드 링크 0개)
4. 양방향 링크 누락 (shareholder/group/executive의 company 참조가 역방향에 없음)
5. `timestamp` 누락
6. `index.md` 미등록 페이지

**의미 점검 (Claude):**
1. 수치 모순 (같은 지표가 페이지마다 다름 → 최신 보고서 기준 정정)
2. 텍스트로만 언급되고 링크 없는 기업·주주명 → 링크 추가 또는 stub 생성
3. 더 최신 보고서가 있는데 갱신 안 된 페이지

**결과:** `outputs\lint-report-YYYY-MM-DD.md`(type: Analysis)로 저장, `log.md`에 `**Lint**` 기록.
심각도(오류/경고/제안)로 분류해 보고.

---

## 3. Taxonomy 관리 — `/propose-type`

새 타입 필요 판단 시:
1. `taxonomy.md` `## 신규 주제 후보`에 `- **타입명**: 이유 / frontmatter 필드 / 섹션` 기록
2. 사용자에게 보고·승인 요청
3. 승인 시 등록 체크리스트:
   - [ ] `taxonomy.md` 등록 타입 표에 행 추가
   - [ ] `taxonomy.md` 타입별 스키마 섹션 추가
   - [ ] 디렉토리 생성 + `index.md` 스켈레톤
   - [ ] `templates\<타입>.md` 작성
   - [ ] `taxonomy.md` `## 변경 이력`에 기록
   - [ ] `CLAUDE.md` 디렉토리 표·Ingest 절차 반영(필요 시)

---

## 4. Query — 질의응답 (`/query`)

**index-first 검색 프로토콜:**
1. `index.md` 읽기 → 타입·태그·제목으로 후보 페이지 선별
2. 후보 페이지 read → 근거 수집
3. 답변 합성 — 모든 수치·주장에 출처 페이지 인용 `[페이지](/dir/page)`
4. **save-back**: 분석 가치가 있으면 `outputs\`에 Analysis로 저장 + index·log 갱신
5. 근거 부족 시: 누락 페이지·주제를 사용자에게 보고하고 ingest/추가 조사 제안

출력 포맷 옵션: 마크다운(기본) / 비교표 / Marp 슬라이드 / matplotlib 차트.

---

## 5. Compare — 비교 분석 (`/compare`)

예: `compare 삼성전자 SK하이닉스 한미반도체` 또는 `compare 증권3사 ROE`.
1. 대상 기업 페이지 read
2. 지표 정렬(매출·영업이익·영업이익률·시장점유율 등) → 비교표 생성
3. 차이의 원인을 사업 부문·밸류체인·산업 페이지 근거로 해석
4. `outputs\`에 Analysis로 저장.

---

## 6. Connect — 관계 추론 (`/connect`)

예: `connect 삼성전자 한미반도체`(공급망), `connect 삼성전자 --shareholders`(주주망).
1. 시작 엔티티 페이지에서 아웃바운드 링크 수집
2. 링크 그래프를 따라 목표까지 경로 탐색(공급사·고객사·주주·계열사·겸직 임원 등)
3. 경로상의 각 관계를 출처와 함께 서술
4. 시각화가 필요하면 `engine\scripts\build-viz.py`로 `viz.html` 생성(Cytoscape 그래프).

---

## 7. Wiki Status — 운영 대시보드 (`/wiki-status`)

`engine\scripts\stats.ps1` 실행:
- 타입별 페이지 수
- 16개 핵심 기업 인제스트 커버리지(완료/미완)
- 고아 페이지 수, 양방향 링크 누락 수
- 최근 `log.md` 활동 요약

스크립트 없으면 Claude가 디렉토리·index 스캔으로 동일 집계.

---

## 8. New Page — 페이지 생성 (`/new-page`)

`new-page <타입> <제목>`:
1. `templates\<타입>.md` 복사
2. frontmatter·필수 섹션 채움(가능한 근거는 기존 페이지·소스에서)
3. 양방향 링크 연결, index·log 갱신.

---

## 스크립트 사용법 (요약)

```powershell
# 미처리 원본 목록
pwsh engine\scripts\list-pending.ps1 -SourceDir AnnualReport_Recent

# OKF 적합성 검증 (모든 비예약 .md에 type 존재)
pwsh engine\scripts\validate-okf.ps1

# 위키 검진 (기계 점검)
pwsh engine\scripts\lint.ps1

# 대시보드
pwsh engine\scripts\stats.ps1

# index.md 재생성 (frontmatter 기반)
pwsh engine\scripts\build-index.ps1

# 새 빈 위키 부트스트랩 (엔진만 복사)
pwsh engine\scripts\new-wiki.ps1 -Target C:\path\to\new-wiki

# (선택) 그래프 뷰어 생성
python engine\scripts\build-viz.py
```

bash 환경에서는 `.sh`/`.py` 대응본을 사용합니다. 자세한 배포는 `INSTALL.md` 참조.
