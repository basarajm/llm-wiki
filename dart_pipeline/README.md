# DART 사업보고서 → Markdown 다운로드 파이프라인

KOSPI·KOSDAQ 상장기업의 **가장 최근 사업보고서(연간)** 원문을 DART OpenAPI로 내려받아
LLM(Claude)이 읽기 좋은 **정제된 Markdown**으로 변환·저장하는 도구입니다.

- **외부 의존성 0** — Python 표준 라이브러리(`urllib`, `html.parser`)만 사용 (최신 Python에서도 빌드 문제 없음)
- **재개 가능** — 중단되어도 같은 명령으로 이어서 실행 (`_state/progress.json` 체크포인트)
- **표 정제** — DART 마크업의 `ROWSPAN/COLSPAN` 병합셀을 그리드로 전개해 GFM 표로 정확히 복원

---

## 폴더 구조

```
dart_pipeline/
├── config.py            # 설정 (API 키는 하드코딩 안 함 — 환경변수/CLI 주입)
├── dart_client.py       # DART OpenAPI 클라이언트 (list.json / document.xml)
├── md_converter.py      # XML/SGML 원문 → Markdown 변환기 (핵심)
├── build_targets.py     # 최신 사업보고서 대상목록 생성
├── run.py               # 다운로드 + 변환 + 저장 오케스트레이터
├── _state/              # 체크포인트·로그 (커밋 안 함)
│   ├── targets.json     # 대상 기업·접수번호 목록
│   ├── progress.json    # 처리 진행상황(재개용)
│   ├── failures.json    # 실패 목록
│   └── run.log          # 실행 로그
└── dart_md/             # ★ 변환 결과 (커밋 안 함)
    ├── KOSPI/  005930_삼성전자_2025.md ...
    └── KOSDAQ/ 000250_삼천당제약_2025.md ...
```

---

## 사용법

### 1. API 키 준비 (외부 입력 — 저장소에 키를 두지 않음)
DART OpenAPI 키를 발급(https://opendart.fss.or.kr/, 무료)한 뒤 아래 중 하나로 주입합니다.

```bash
# 방법 A) 환경변수
set DART_API_KEY=발급받은키          # Windows (cmd)
$env:DART_API_KEY="발급받은키"       # Windows (PowerShell)
export DART_API_KEY=발급받은키        # bash

# 방법 B) 실행 인자
python run.py --api-key 발급받은키
python build_targets.py --api-key 발급받은키
```
키가 없으면 스크립트가 안내 메시지와 함께 종료합니다. `config.py` 에는 키를 하드코딩하지 않습니다.

### 2. 대상목록 생성 (선택 — run.py 가 없으면 자동 생성)
```bash
python build_targets.py --months 24
```
최근 24개월 공시검색을 월 단위로 순회하여, KOSPI/KOSDAQ 기업별 **가장 최근 사업보고서 1건**만
추려 `_state/targets.json` 에 저장합니다. (비-12월 결산법인까지 포함하도록 24개월 권장)

### 3. 다운로드 + 변환 실행
```bash
python run.py                 # 전체 실행 / 중단 시 재개
python run.py --limit 5       # 앞 5건만 (테스트)
python run.py --markets KOSPI # 특정 시장만
python run.py --rebuild-targets   # 대상목록 먼저 재생성 후 실행
python run.py --no-resume     # 진행기록 무시하고 처음부터
```

실행 중/후 요약은 콘솔과 `_state/run.log` 에 출력됩니다. 실패 건은 `_state/failures.json`
에 기록되며, 같은 `python run.py` 로 재실행하면 미완료·실패 건만 다시 시도합니다.

---

## 변환 규칙 (md_converter.py)

| DART 원문 요소 | Markdown 변환 |
|---|---|
| `SECTION-1 / 2 / 3 / 4` 중첩 | 제목 레벨 `##` / `###` / `####` / `#####` |
| `TITLE ATOC="Y"` | 해당 레벨 제목 |
| `TITLE ATOC="N"` | `**굵은 글씨**` 캡션 |
| `TABLE` (`TR/TH/TD/TU/TE`) | GFM 표 (병합셀 그리드 전개) |
| `ROWSPAN` | 세로 병합 → 첫 칸 값 반복, 나머지 빈칸 |
| `COLSPAN` | 가로 병합 → 첫 칸 값, 이후 빈칸 |
| 1행·1열 캡션성 표 | 일반 텍스트 줄 (예: `(단위 : 천원)`) |
| `목 차` 표지·목차 | 제거 (노이즈) |
| `IMAGE/IMG` | `*(이미지: 캡션)*` 자리표시 |

각 파일 상단에는 기업명·종목코드·시장·접수번호·회계연도·DART 원문 URL 등의
**프론트매터**가 포함되어, 위키 인제스트 시 출처 추적이 가능합니다.

---

## 동작 메모

- **최신 사업보고서 판별**: `list.json` 의 `pblntf_detail_ty=A001`(사업보고서),
  `last_reprt_at=Y`(정정 포함 최종본)로 조회 후, 기업별 접수일이 가장 늦은 1건 선택.
- **본문 XML 선택**: ZIP 내 `{접수번호}.xml`(본문)을 우선 사용. `_00760` 등은 첨부(감사보고서 등).
- **API 한도**: 분당 제한(코드 020) 시 자동 대기·재시도, 일일 한도(코드 021) 도달 시
  진행상황 저장 후 종료 → 다음 날 재실행으로 재개.
- **인코딩**: 원문은 UTF-8 우선, 실패 시 CP949/EUC-KR 폴백.

---

## 위키 인제스트 연계 (선택)

변환된 MD는 `dart_md/<시장>/` 에 저장됩니다. 이를 위키 인제스트 대상으로 쓰려면
해당 파일을 `source_documents/raw/` 로 복사하거나, `/ingest` 시 경로를 직접 지정하세요.
프론트매터의 `dart_url`·`rcept_no` 로 원본 추적이 가능합니다.

---

## 로컬 아카이브 기반 인제스트 (DART API 키 없이, 2026-07-01 추가)

`dart_md/`는 `.gitignore` 대상이라 다른 PC에서는 비어 있고, 채우려면 DART API 키로
`run.py`를 다시 돌려야 합니다. 그런데 **DART API 없이도** 사업보고서 MD를 대량으로
확보한 경우(예: 별도 프로젝트에서 이미 변환한 아카이브), 다음 경로가 그 용도로
예약되어 있습니다.

- `source_documents/AnnualReport_MD/` — 사업보고서 아카이브(`.gitignore` 대상, 각 머신에
  로컬로 채워야 함). 파일명 규칙은 `<회사명>-사업보고서-<YYYY.MM>.md`
  (`source_documents/AnnualReport_Recent/`의 16개 샘플과 동일 포맷 — **프론트매터 없음**,
  종목코드·상장시장은 본문(예: "유가증권시장 상장"·"종목코드 011150)")에서 직접 추출).
- `dart_pipeline/local_archive_status.py` — 이 아카이브를 ground truth로 삼아
  done(위키에 Full로 존재)/pending을 계산하는 트래커. `ingest_status.py`(dart_md 기준)를
  대체하는 것이 아니라, 원본 확보 경로가 다를 때 쓰는 대안이다.
  ```bash
  python dart_pipeline/local_archive_status.py            # 현황 + wiki/outputs/ingest-tracker-local.md 갱신
  python dart_pipeline/local_archive_status.py --next 3   # 다음 3개사 JSON (배치 인제스트용)
  ```
