# 미처리 원본 목록
# source_documents\<SourceDir>의 원본 .md 중, wiki\sources\에 resource:로 참조되지 않은 파일을 출력.
# 사용: pwsh engine\scripts\list-pending.ps1 [-SourceDir AnnualReport_Recent]

param([string]$SourceDir = 'AnnualReport_Recent')

. "$PSScriptRoot\_common.ps1"
$root = Get-WikiRoot
$proj = Get-ProjectRoot

$srcPath = Join-Path $proj "source_documents\$SourceDir"
if (-not (Test-Path $srcPath)) { Write-Host "소스 폴더 없음: $srcPath" -ForegroundColor Red; exit 1 }

# 이미 처리된 원본 파일명 집합 (sources\의 resource: 값에서 파일명 추출)
$processed = @{}
$sourcesDir = Join-Path $root 'sources'
if (Test-Path $sourcesDir) {
    foreach ($s in Get-ChildItem $sourcesDir -Filter *.md -File) {
        if (Test-ReservedFile $s.Name) { continue }
        $fm = Get-FrontMatter -Path $s.FullName
        if ($fm.ContainsKey('resource')) {
            $name = Split-Path ($fm['resource'] -replace '/','\') -Leaf
            $processed[$name] = $true
        }
    }
}

$all = Get-ChildItem $srcPath -Filter *.md -File
$pending = $all | Where-Object { -not $processed.ContainsKey($_.Name) }

Write-Host "소스 폴더: $SourceDir — 전체 $($all.Count)개, 처리완료 $($processed.Count)개, 미처리 $($pending.Count)개" -ForegroundColor Cyan
$pending | ForEach-Object { Write-Host "  $($_.Name)" }
