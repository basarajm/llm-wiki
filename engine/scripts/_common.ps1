# 공통 헬퍼 — 다른 스크립트에서 dot-source 하여 사용
# 사용: . "$PSScriptRoot\_common.ps1"

$OutputEncoding = [System.Text.Encoding]::UTF8

# 프로젝트 루트 (engine\scripts\ 의 두 단계 상위)
function Get-ProjectRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
}

# 위키 콘텐츠(번들) 루트 = <프로젝트>\wiki
function Get-WikiRoot {
    return (Resolve-Path (Join-Path (Get-ProjectRoot) 'wiki')).Path
}

# 콘텐츠(개념) 디렉토리 — 각 .md가 OKF 개념이며 type frontmatter 필수
$script:ContentDirs = @(
    'companies','groups','industries','shareholders','value_chain',
    'segments','products','executives','financial_products','ratings',
    'sources','outputs'
)

function Get-ContentDirs { return $script:ContentDirs }

# 예약 파일 (frontmatter 없음)
function Test-ReservedFile([string]$Name) {
    return ($Name -ieq 'index.md' -or $Name -ieq 'log.md')
}

# 모든 콘텐츠 .md 파일 경로 반환 (index.md/log.md 제외)
function Get-ConceptFiles {
    param([string]$Root = (Get-WikiRoot))
    $files = @()
    foreach ($d in $script:ContentDirs) {
        $dir = Join-Path $Root $d
        if (Test-Path $dir) {
            $files += Get-ChildItem -Path $dir -Filter *.md -File -Recurse |
                Where-Object { -not (Test-ReservedFile $_.Name) }
        }
    }
    return $files
}

# frontmatter를 해시테이블로 파싱 (간단한 key: value, 첫 --- 블록)
function Get-FrontMatter {
    param([string]$Path)
    $raw = Get-Content -Path $Path -Raw -Encoding UTF8
    $fm = @{}
    if ($raw -notmatch '^﻿?---\r?\n') { return $fm }
    $lines = $raw -split "\r?\n"
    if ($lines[0].TrimStart([char]0xFEFF) -ne '---') { return $fm }
    for ($i = 1; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -eq '---') { break }
        if ($lines[$i] -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$') {
            $fm[$matches[1]] = $matches[2].Trim()
        }
    }
    return $fm
}

# 본문에서 내부 절대링크 추출: [텍스트](/dir/page) → '/dir/page'
function Get-InternalLinks {
    param([string]$Path)
    $raw = Get-Content -Path $Path -Raw -Encoding UTF8
    $links = @()
    foreach ($m in [regex]::Matches($raw, '\]\((/[^)\s]+)\)')) {
        $links += $m.Groups[1].Value
    }
    return $links
}

# '/companies/삼성전자' → 'companies\삼성전자.md' 풀패스
function Resolve-LinkToFile {
    param([string]$Link, [string]$Root = (Get-WikiRoot))
    $rel = $Link.TrimStart('/')
    if (-not $rel.EndsWith('.md')) { $rel = "$rel.md" }
    $rel = $rel -replace '/', '\'
    return (Join-Path $Root $rel)
}
