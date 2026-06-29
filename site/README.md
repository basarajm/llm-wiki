# 웹 위키 (Quartz)

`wiki/` 폴더(OKF 마크다운)를 **Quartz v4**로 빌드해 정적 사이트로 배포합니다.
읽기·전문검색·그래프뷰·백링크 제공.

- **라이브:** https://basarajm.github.io/llm-wiki/
- 콘텐츠 원본: 저장소 루트의 `wiki/` (이 폴더는 빌드 도구·설정만 보관)

## 로컬 미리보기

```bash
cd site
npm ci
npx quartz build -d ../wiki -o public --serve   # http://localhost:8080
```

## 빌드 + 배포 (수동, 현재 운영 방식)

GitHub Pages는 `gh-pages` 브랜치(정적 HTML)를 서빙합니다. 콘텐츠를 바꾼 뒤:

```bash
cd site
npx quartz build -d ../wiki -o public
cd public
touch .nojekyll                       # Jekyll 처리 방지
git add -A && git commit -m "deploy"
git push -f https://github.com/basarajm/llm-wiki.git gh-pages
```

(`site/public`은 자체 git 저장소로 초기화되어 있어 위 명령으로 바로 `gh-pages`에 푸시됩니다.)

## (선택) 자동 배포 — GitHub Actions

`main`에 푸시할 때 자동으로 빌드·배포하려면 아래 워크플로를 추가하세요.
※ 워크플로 파일 커밋에는 gh 토큰의 `workflow` 스코프가 필요합니다
(`gh auth refresh -h github.com -s workflow` 또는 GitHub 웹 편집기로 추가).
추가 후 저장소 **Settings → Pages → Source** 를 *GitHub Actions* 로 변경합니다.

`.github/workflows/deploy-pages.yml`:

```yaml
name: Deploy wiki to GitHub Pages
on:
  push:
    branches: [main]
    paths: ["wiki/**", "site/**", ".github/workflows/deploy-pages.yml"]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: false
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-node@v4
        with: { node-version: 22 }
      - working-directory: site
        run: npm ci
      - working-directory: site
        run: npx quartz build -d ../wiki -o public
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with: { path: site/public }
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

## 설정 메모 (`quartz.config.ts`)

- `markdownLinkResolution: "absolute"` — `/companies/삼성전자` 같은 번들 루트절대 링크 해석
- `baseUrl: "basarajm.github.io/llm-wiki"`, `locale: "ko-KR"`
- OG 이미지·Latex 비활성(3,000+ 페이지 빌드 속도·`$` 오·렌더 방지)

## 알려진 제약

- `ratings/` 인라인 링크: 원본이 `/ratings/기업명 신용등급`처럼 **URL에 공백**을 사용 →
  표준 마크다운에서 링크로 인식되지 않아 렌더 시 끊김(Obsidian에서는 동작).
  ratings 페이지 자체는 검색·직접 URL(`/ratings/기업명-신용등급`)로 접근 가능.
  완전 연결이 필요하면 ratings 파일명·링크에서 공백 제거(슬러그화) 패스 필요.
