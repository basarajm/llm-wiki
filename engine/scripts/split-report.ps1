# 대용량 사업보고서 원문(.md)을 챕터(I~XII) 단위로 분할하여 캐시에 저장
# - source_documents\ 원본은 절대 수정하지 않음 (읽기만 함)
# - 분할 결과는 engine\cache\report-chapters\<원본파일명>\ 에 생성 (재생성 가능한 파생물, git 추적 제외)
# - Claude는 ingest 시 원본 전체를 Read하는 대신 필요한 챕터 파일만 Read하여 토큰을 절약
#
# 사용법:
#   .\split-report.ps1 -Path "source_documents\AnnualReport_Recent\LG전자-사업보고서-2025.12.md"
#   .\split-report.ps1 -Folder "source_documents\AnnualReport_Recent"   # 폴더 전체 일괄 분할
#   .\split-report.ps1 -Path <파일> -Force                              # 이미 분할된 것도 재생성
#
# 분할 규칙: 원본 어딘가에 `## <로마숫자>. <제목>` (예: `## I. 회사의 개요`) 형태의
# 최상위(H2) 챕터 헤더가 있다고 가정(DART 사업보고서 표준 구조). 못 찾으면 경고만 출력하고 스킵.

param(
    [string]$Path,
    [string]$Folder,
    [switch]$Force
)

. "$PSScriptRoot\_common.ps1"

function Get-SafeChapterName([string]$s) {
    $s = $s -replace '[\\/:*?"<>|]', ''
    $s = $s -replace '\s+', ''
    if ($s.Length -gt 40) { $s = $s.Substring(0, 40) }
    return $s
}

function Split-ReportFile {
    param([string]$SourcePath, [switch]$Force)

    $srcFull = (Resolve-Path -LiteralPath $SourcePath).Path
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($srcFull)
    $root = Get-ProjectRoot
    $cacheRoot = Join-Path $root 'engine\cache\report-chapters'
    $outDir = Join-Path $cacheRoot $baseName

    if ((Test-Path $outDir) -and -not $Force) {
        Write-Host "스킵(이미 분할됨): $baseName  (-Force로 재생성)"
        return
    }

    $raw = Get-Content -LiteralPath $srcFull -Raw -Encoding UTF8

    # H2 챕터 헤더: '## I. 회사의 개요' 형태. 로마숫자(ASCII I/V/X 조합, 유니코드 Ⅰ-Ⅻ 모두 허용)
    $pattern = '(?m)^##\s+([IVXivx]{1,6}|[Ⅰ-Ⅻ])\.\s*(.+?)\s*$'
    $chapterMatches = [regex]::Matches($raw, $pattern)

    if ($chapterMatches.Count -eq 0) {
        Write-Warning "챕터 헤더를 찾지 못함: $baseName — 표준 구조가 아니거나 손상된 원본일 수 있음 (예: 개행이 소실된 파일). 원본 확인 필요."
        return
    }

    New-Item -ItemType Directory -Path $outDir -Force | Out-Null

    $relSrc = $srcFull.Substring($root.Length).TrimStart('\')
    $manifest = New-Object System.Collections.Generic.List[string]
    $manifest.Add("# $baseName — 챕터 분할 매니페스트")
    $manifest.Add("")
    $manifest.Add("원본: ``$relSrc``")
    $manifest.Add("전체 문자수: $($raw.Length)")
    $manifest.Add("")
    $manifest.Add("| # | 챕터 | 파일 | 문자수 |")
    $manifest.Add("|---|---|---|---|")

    $firstStart = $chapterMatches[0].Index
    if ($firstStart -gt 0) {
        $pre = $raw.Substring(0, $firstStart)
        $preFile = '00_머리말.md'
        Set-Content -LiteralPath (Join-Path $outDir $preFile) -Value $pre -Encoding UTF8 -NoNewline
        $manifest.Add("| 00 | 머리말 (표지/목차/정정신고 등) | $preFile | $($pre.Length) |")
    }

    for ($i = 0; $i -lt $chapterMatches.Count; $i++) {
        $m = $chapterMatches[$i]
        $numeral = $m.Groups[1].Value
        $title = $m.Groups[2].Value
        $start = $m.Index
        $end = if ($i + 1 -lt $chapterMatches.Count) { $chapterMatches[$i + 1].Index } else { $raw.Length }
        $chunk = $raw.Substring($start, $end - $start)
        $idx = ($i + 1).ToString('00')
        $safeTitle = Get-SafeChapterName $title
        $fname = "${idx}_${numeral}_${safeTitle}.md"
        Set-Content -LiteralPath (Join-Path $outDir $fname) -Value $chunk -Encoding UTF8 -NoNewline
        $manifest.Add("| $idx | $numeral. $title | $fname | $($chunk.Length) |")
    }

    Set-Content -LiteralPath (Join-Path $outDir '_manifest.md') -Value ($manifest -join "`n") -Encoding UTF8
    Write-Host "분할 완료: $baseName -> engine\cache\report-chapters\$baseName\ ($($chapterMatches.Count)개 챕터)"
}

if ($Folder) {
    $target = if (Test-Path $Folder) { $Folder } else { Join-Path (Get-ProjectRoot) $Folder }
    Get-ChildItem -Path $target -Filter *.md -File | ForEach-Object {
        Split-ReportFile -SourcePath $_.FullName -Force:$Force
    }
} elseif ($Path) {
    Split-ReportFile -SourcePath $Path -Force:$Force
} else {
    Write-Error "-Path 또는 -Folder 인자가 필요합니다."
}
