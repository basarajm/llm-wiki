# 새 빈 위키 부트스트랩 — 엔진(재사용 파일)만 복사하고 콘텐츠/원본 데이터는 제외.
# 새 구조: <대상>\CLAUDE.md, README.md, .gitignore, .claude\, engine\, wiki\, source_documents\
# 사용: pwsh engine\scripts\new-wiki.ps1 -Target C:\path\to\new-wiki [-Force]

param(
    [Parameter(Mandatory=$true)][string]$Target,
    [switch]$Force
)

. "$PSScriptRoot\_common.ps1"
$proj = Get-ProjectRoot

if (Test-Path $Target) {
    if (-not $Force) { Write-Host "대상이 이미 존재합니다. -Force로 덮어쓰기. ($Target)" -ForegroundColor Red; exit 1 }
} else {
    New-Item -ItemType Directory -Path $Target -Force | Out-Null
}

# 루트 엔진 파일
foreach ($f in @('CLAUDE.md','README.md','.gitignore')) {
    $src = Join-Path $proj $f
    if (Test-Path $src) { Copy-Item $src (Join-Path $Target $f) -Force }
}
# 루트 엔진 폴더
foreach ($d in @('.claude','engine')) {
    $src = Join-Path $proj $d
    if (Test-Path $src) { Copy-Item $src (Join-Path $Target $d) -Recurse -Force }
}

# 빈 위키 콘텐츠(wiki\) — 디렉토리 + 빈 index.md 스켈레톤
$wiki = Join-Path $Target 'wiki'
foreach ($d in (Get-ContentDirs)) {
    $dir = Join-Path $wiki $d
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    Set-Content -Path (Join-Path $dir 'index.md') -Value @("# $d","","<!-- 비어 있음 -->") -Encoding UTF8
}
Set-Content -Path (Join-Path $wiki 'index.md') -Value @('# 위키 — 전체 인덱스','','<!-- build-index.ps1로 생성 -->') -Encoding UTF8
Set-Content -Path (Join-Path $wiki 'log.md') -Value @('# 위키 작업 이력','') -Encoding UTF8

# 원본 드롭 폴더(source_documents\)
New-Item -ItemType Directory -Path (Join-Path $Target 'source_documents\raw\assets') -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $Target 'source_documents\AnnualReport_Recent') -Force | Out-Null

Write-Host "새 빈 위키 생성 완료: $Target" -ForegroundColor Green
Write-Host "엔진만 복사되었고 콘텐츠·원본 데이터는 포함되지 않았습니다. INSTALL.md를 참고해 시작하세요." -ForegroundColor Cyan
