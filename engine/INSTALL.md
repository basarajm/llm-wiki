# 설치 및 배포 가이드

이 위키는 **별도 프로그램 없이** Claude(Code·데스크탑)와 텍스트 에디터/Obsidian만으로 운영됩니다.
OKF(Open Knowledge Format) v0.1 마크다운 번들이므로 git으로 버전 관리·배포할 수 있습니다.

폴더는 3분할되어 있습니다: `wiki\`(콘텐츠) · `engine\`(시스템) · `source_documents\`(원본).
루트에는 `CLAUDE.md`·`README.md`·`.gitignore`·`.claude\`만 둡니다.

---

## A. 이 위키를 그대로 사용 (콘텐츠 포함)

1. 디렉토리 전체를 원하는 위치에 복사합니다.
2. **Claude Code**: 해당 폴더(루트)를 열면 `CLAUDE.md`가 자동 로드됩니다. `.claude\commands\`의
   슬래시 커맨드(`/ingest`, `/lint`, `/query`, `/compare`, `/connect`, `/wiki-status` 등)를 사용합니다.
3. **Claude 데스크탑**: `CLAUDE.md`와 `engine\OPERATIONS.md`를 대화 초기에 첨부/참조시키면
   동일한 워크플로를 슬래시 커맨드 없이 수행합니다.
4. (선택) **Obsidian**: **`wiki\` 폴더**를 Vault로 지정(크로스링크 `/companies/…`가 이 폴더 기준).
   Dataview·Marp 플러그인 권장.

---

## B. 빈 엔진만 새 시스템에 배포 (데이터 분리형 클린 패키지)

콘텐츠·원본 데이터를 제외하고 **재사용 엔진**만 새 위치에 부트스트랩합니다.

```powershell
# Windows / PowerShell 7+
pwsh engine\scripts\new-wiki.ps1 -Target C:\path\to\new-wiki
```
```bash
# macOS / Linux
bash engine/scripts/new-wiki.sh /path/to/new-wiki
```

복사되는 엔진: 루트의 `CLAUDE.md`·`README.md`·`.gitignore`·`.claude\`, 그리고 `engine\` 전체
(`taxonomy.md`·`OPERATIONS.md`·`INSTALL.md`·`PACKAGE.md`·`templates\`·`scripts\`).
`wiki\`는 빈 콘텐츠 디렉토리로, `source_documents\`는 빈 드롭 폴더로 생성됩니다.
이후 원본 보고서를 `source_documents\`에 넣고 `/ingest`로 채웁니다.

자세한 엔진/인스턴스 구분은 `PACKAGE.md` 참조.

---

## C. 다른 도메인으로 재타게팅

이 패키지는 한국 사업보고서에 특화되어 있으나 구조는 도메인 불문입니다.
1. `engine\taxonomy.md`의 타입을 도메인에 맞게 교체(`/propose-type` 활용)
2. `CLAUDE.md`의 디렉토리 역할·ingest 절차 수정
3. `engine\templates\`를 새 타입에 맞게 교체
4. `engine\scripts\_common.ps1`의 `$ContentDirs`와 `stats.ps1`의 핵심 목록 갱신

---

## 요구 사항

- **필수**: Claude Code 또는 Claude 데스크탑. 그 외 런타임 불필요.
- **스크립트(선택)**: PowerShell 7+ (`pwsh`) 또는 bash. 검증·집계·index 재생성 자동화용.
  스크립트 없이도 Claude가 `engine\OPERATIONS.md` 절차로 동일 작업을 수행합니다.
- **그래프 뷰어(선택)**: Python 3 (`engine\scripts\build-viz.py`) → `wiki\viz.html` 생성(브라우저로 열람).

---

## 검증

```powershell
pwsh engine\scripts\validate-okf.ps1   # OKF type 규칙 적합성
pwsh engine\scripts\lint.ps1           # 링크·고아·양방향 점검
pwsh engine\scripts\stats.ps1          # 커버리지 대시보드
pwsh engine\scripts\build-index.ps1    # index.md 동기화
```
