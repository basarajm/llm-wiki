# 위키 검진 (기계 점검)
# - type/timestamp frontmatter 누락
# - 깨진 내부 링크
# - 고아 페이지 (인바운드 링크 0)
# - 양방향 링크 누락 (shareholder/group/executive → company 역링크)
# 결과를 콘솔에 출력. (의미 점검은 Claude가 별도 수행)

. "$PSScriptRoot\_common.ps1"
$root = Get-WikiRoot

$files = Get-ConceptFiles -Root $root
$missingType = @(); $missingTs = @(); $broken = @(); $orphans = @(); $biDir = @()

# 인바운드 링크 집계용
$inbound = @{}
foreach ($f in $files) {
    $rel = '/' + ($f.FullName.Substring($root.Length).TrimStart('\') -replace '\\','/')
    $rel = $rel -replace '\.md$',''
    $inbound[$rel] = 0
}

foreach ($f in $files) {
    $rel = $f.FullName.Substring($root.Length).TrimStart('\')
    $fm = Get-FrontMatter -Path $f.FullName
    if (-not $fm.ContainsKey('type') -or [string]::IsNullOrWhiteSpace($fm['type'])) { $missingType += $rel }
    if (-not $fm.ContainsKey('timestamp') -or [string]::IsNullOrWhiteSpace($fm['timestamp'])) { $missingTs += $rel }

    foreach ($lnk in (Get-InternalLinks -Path $f.FullName)) {
        $target = Resolve-LinkToFile -Link $lnk -Root $root
        if (-not (Test-Path $target)) {
            $broken += "$rel → $lnk"
        } else {
            $key = ($lnk -replace '\.md$','')
            if ($inbound.ContainsKey($key)) { $inbound[$key]++ }
        }
    }
}

# 고아: 인바운드 0 (sources/outputs는 제외 — 흔히 단방향)
foreach ($k in $inbound.Keys) {
    if ($inbound[$k] -eq 0 -and $k -notmatch '^/(sources|outputs)/') {
        $orphans += $k
    }
}

# 양방향 링크: shareholders/groups/executives 의 /companies/ 링크가 역방향에 있는지
foreach ($f in $files) {
    $rel = $f.FullName.Substring($root.Length).TrimStart('\')
    if ($rel -notmatch '^(shareholders|groups|executives)\\') { continue }
    $selfLink = '/' + ($rel -replace '\\','/' -replace '\.md$','')
    foreach ($lnk in (Get-InternalLinks -Path $f.FullName)) {
        if ($lnk -match '^/companies/') {
            $companyFile = Resolve-LinkToFile -Link $lnk -Root $root
            if (Test-Path $companyFile) {
                $cRaw = Get-Content -Path $companyFile -Raw -Encoding UTF8
                if ($cRaw -notmatch [regex]::Escape($selfLink)) {
                    $biDir += "$rel ↔ $lnk (역링크 없음)"
                }
            }
        }
    }
}

function Show-Section($title, $items, $color) {
    Write-Host ""
    Write-Host "== $title ($($items.Count)) ==" -ForegroundColor $color
    if ($items.Count -eq 0) { Write-Host "  (없음)" } else { $items | Select-Object -Unique | ForEach-Object { Write-Host "  $_" } }
}

Write-Host "위키 검진 — 콘텐츠 페이지 $($files.Count)개" -ForegroundColor Cyan
Show-Section "type 누락" $missingType Red
Show-Section "timestamp 누락" $missingTs Yellow
Show-Section "깨진 내부 링크" $broken Red
Show-Section "고아 페이지 (인바운드 0)" $orphans Yellow
Show-Section "양방향 링크 누락" $biDir Yellow

$total = $missingType.Count + $broken.Count
Write-Host ""
if ($total -eq 0) { Write-Host "심각 오류 없음." -ForegroundColor Green } else { Write-Host "오류 $total건 (type/링크). 정정 필요." -ForegroundColor Red }
