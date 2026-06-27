# 운영 대시보드
# 타입별 페이지 수, 16개 핵심 기업 인제스트 커버리지, 최근 활동을 출력.
# 사용: pwsh scripts\stats.ps1

. "$PSScriptRoot\_common.ps1"
$root = Get-WikiRoot

Write-Host "=== 위키 대시보드 ===" -ForegroundColor Cyan

# 타입별(=디렉토리별) 페이지 수
Write-Host "`n[디렉토리별 페이지 수]"
$totalPages = 0
foreach ($d in (Get-ContentDirs)) {
    $dir = Join-Path $root $d
    $n = 0
    if (Test-Path $dir) {
        $n = (Get-ChildItem $dir -Filter *.md -File | Where-Object { -not (Test-ReservedFile $_.Name) }).Count
    }
    $totalPages += $n
    "{0,-20} {1,4}" -f $d, $n | Write-Host
}
Write-Host ("{0,-20} {1,4}" -f '합계', $totalPages)

# 핵심 16개 기업 커버리지
$core = @('HD현대일렉트릭','KB금융지주','LG전자','SK하이닉스','대한광통신','레인보우로보틱스',
'미래에셋증권','삼성전기','삼성전자','신영증권','에스피지','주성엔지니어링','한국투자증권','한미반도체','현대오토에버','현대자동차')
Write-Host "`n[핵심 16개 기업 커버리지]"
$done = 0
foreach ($c in $core) {
    $hasCompany = Test-Path (Join-Path $root "companies\$c.md")
    $hasSource = (Get-ChildItem (Join-Path $root 'sources') -Filter *.md -File -ErrorAction SilentlyContinue | Where-Object { $_.BaseName -like "$c*" }).Count -gt 0
    $mark = if ($hasCompany -and $hasSource) { '✓'; $done++ } elseif ($hasCompany -or $hasSource) { '◐' } else { '·' }
    "  {0} {1}" -f $mark, $c | Write-Host
}
Write-Host "  → 완료 $done / 16"

# 최근 활동 (log.md 마지막 헤딩들)
$log = Join-Path $root 'log.md'
if (Test-Path $log) {
    Write-Host "`n[최근 활동 (log.md)]"
    Get-Content $log -Encoding UTF8 | Select-String '^## ' | Select-Object -Last 5 | ForEach-Object { Write-Host "  $($_.Line)" }
}
