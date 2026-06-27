# OKF v0.1 적합성 검증
# 모든 콘텐츠 .md(예약 파일 제외)가 유효한 frontmatter + 비어있지 않은 type 을 갖는지 확인.
# 종료 코드 0 = 통과, 1 = 위반 발견.

. "$PSScriptRoot\_common.ps1"
$root = Get-WikiRoot

$violations = @()
$count = 0
foreach ($f in Get-ConceptFiles -Root $root) {
    $count++
    $fm = Get-FrontMatter -Path $f.FullName
    $rel = $f.FullName.Substring($root.Length).TrimStart('\')
    if ($fm.Count -eq 0) {
        $violations += "[frontmatter 없음] $rel"
    } elseif (-not $fm.ContainsKey('type') -or [string]::IsNullOrWhiteSpace($fm['type'])) {
        $violations += "[type 누락/공백] $rel"
    }
}

Write-Host "OKF 검증: 콘텐츠 페이지 ${count}개 점검" -ForegroundColor Cyan
if ($violations.Count -eq 0) {
    Write-Host "통과 — 모든 페이지가 OKF v0.1 type 규칙을 만족합니다." -ForegroundColor Green
    exit 0
} else {
    Write-Host "위반 $($violations.Count)건:" -ForegroundColor Red
    $violations | ForEach-Object { Write-Host "  $_" }
    exit 1
}
