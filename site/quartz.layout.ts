import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"
import { QuartzComponentProps } from "./quartz/components/types"
import { isFolderPath } from "./quartz/util/path"

const isHome = (page: QuartzComponentProps) => page.fileData.slug === "index"

// 첫 화면(index)에만 노출할 탐색 위젯 — 나머지 위키 페이지에는 영향 없음
const homeAfterBody = [
  Component.ConditionalRender({
    component: Component.RecentNotes({
      title: "최근 업데이트된 위키",
      limit: 8,
      linkToMore: false,
      showTags: false,
      // OKF 프론트매터에 timestamp가 없는 예약 파일(log, ingest-tracker 등)은
      // 빌드 시점 파일시스템 mtime으로 폴백돼 항상 "최신"으로 보이므로 제외
      filter: (f) =>
        !isFolderPath(f.slug ?? "") &&
        !(f.slug ?? "").startsWith("tags/") &&
        typeof f.frontmatter?.timestamp === "string",
    }),
    condition: isHome,
  }),
  Component.ConditionalRender({
    component: Component.RandomLinks({
      title: "둘러보기: 무작위 페이지",
      limit: 6,
    }),
    condition: isHome,
  }),
]

// components shared across all pages
export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [],
  afterBody: homeAfterBody,
  footer: Component.Footer({
    links: {
      GitHub: "https://github.com/jackyzha0/quartz",
      "Discord Community": "https://discord.gg/cRFFHYye7t",
    },
  }),
}

// components for pages that display a single page (e.g. a single note)
export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.ConditionalRender({
      component: Component.Breadcrumbs(),
      condition: (page) => page.fileData.slug !== "index",
    }),
    Component.ArticleTitle(),
    // 첫 화면 전용 검색창 — 링크 목록을 열기 전에 바로 검색부터 할 수 있도록 상단에 노출
    Component.ConditionalRender({
      component: Component.Search(),
      condition: isHome,
    }),
    Component.ContentMeta(),
    Component.TagList(),
  ],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
        { Component: Component.ReaderMode() },
      ],
    }),
    Component.Explorer(),
  ],
  right: [
    Component.Graph(),
    Component.DesktopOnly(Component.TableOfContents()),
    Component.Backlinks(),
  ],
}

// components for pages that display lists of pages  (e.g. tags or folders)
export const defaultListPageLayout: PageLayout = {
  beforeBody: [Component.Breadcrumbs(), Component.ArticleTitle(), Component.ContentMeta()],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
      ],
    }),
    Component.Explorer(),
  ],
  right: [],
}
