# index.md 재생성
# 각 콘텐츠 디렉토리의 페이지 frontmatter(title/description)에서 디렉토리별 index.md를 재생성하고,
# 루트 index.md를 카테고리별로 갱신한다. (OKF progressive-disclosure)
# 사용: pwsh scripts\build-index.ps1

. "$PSScriptRoot\_common.ps1"
$root = Get-WikiRoot

$dirLabels = [ordered]@{
    'companies'='기업'; 'groups'='기업집단'; 'industries'='산업'; 'shareholders'='주주';
    'value_chain'='밸류체인'; 'segments'='사업 부문'; 'products'='상품'; 'executives'='임원';
    'financial_products'='금융상품'; 'ratings'='신용평가'; 'sources'='사업보고서'; 'outputs'='분석 결과물'
}

$rootLines = @('# 한국 기업 리서치 위키 — 전체 인덱스','', "*build-index.ps1로 생성됨*",'')

foreach ($d in $dirLabels.Keys) {
    $dir = Join-Path $root $d
    if (-not (Test-Path $dir)) { continue }
    $pages = Get-ChildItem $dir -Filter *.md -File | Where-Object { -not (Test-ReservedFile $_.Name) } | Sort-Object Name

    # 디렉토리별 index.md
    $dirLines = @("# $($dirLabels[$d]) ($d\)","")
    $rootLines += "## $($dirLabels[$d]) ($d\)"
    if ($pages.Count -eq 0) {
        $dirLines += "<!-- 비어 있음 -->"
        $rootLines += "<!-- 페이지가 추가되면 여기에 기록됩니다 -->"
    }
    foreach ($p in $pages) {
        $fm = Get-FrontMatter -Path $p.FullName
        $title = if ($fm.ContainsKey('title')) { $fm['title'] } else { $p.BaseName }
        $desc = if ($fm.ContainsKey('description')) { $fm['description'] } else { '' }
        $link = "/$d/$($p.BaseName)"
        $line = "* [$title]($link)" + $(if ($desc) { " - $desc" } else { '' })
        $dirLines += $line
        $rootLines += $line
    }
    $dirLines += ''
    Set-Content -Path (Join-Path $dir 'index.md') -Value $dirLines -Encoding UTF8
    $rootLines += ''
}

Set-Content -Path (Join-Path $root 'index.md') -Value $rootLines -Encoding UTF8
Write-Host "index.md 재생성 완료 (루트 + 디렉토리별)." -ForegroundColor Green
