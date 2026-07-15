import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { isFolderPath, resolveRelative } from "../util/path"
import { QuartzPluginData } from "../plugins/vfile"
import style from "./styles/recentNotes.scss"
import { classNames } from "../util/lang"

interface Options {
  title?: string
  limit: number
  filter: (f: QuartzPluginData) => boolean
}

const defaultOptions: Options = {
  limit: 6,
  filter: (f) => !isFolderPath(f.slug ?? "") && !(f.slug ?? "").startsWith("tags/"),
}

// Fisher-Yates — build-time only, reshuffled on every site build
function shuffle<T>(arr: T[]): T[] {
  const copy = [...arr]
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[copy[i], copy[j]] = [copy[j], copy[i]]
  }
  return copy
}

export default ((userOpts?: Partial<Options>) => {
  const RandomLinks: QuartzComponent = ({
    allFiles,
    fileData,
    displayClass,
  }: QuartzComponentProps) => {
    const opts = { ...defaultOptions, ...userOpts }
    const candidates = allFiles.filter(opts.filter)
    const pages = shuffle(candidates).slice(0, opts.limit)

    return (
      <div class={classNames(displayClass, "recent-notes", "random-links")}>
        <h3>{opts.title ?? "무작위 링크"}</h3>
        <ul class="recent-ul">
          {pages.map((page) => {
            const title = page.frontmatter?.title ?? page.slug
            const description = page.frontmatter?.description

            return (
              <li class="recent-li">
                <div class="section">
                  <div class="desc">
                    <h3>
                      <a href={resolveRelative(fileData.slug!, page.slug!)} class="internal">
                        {title}
                      </a>
                    </h3>
                  </div>
                  {description && <p class="meta">{description}</p>}
                </div>
              </li>
            )
          })}
        </ul>
      </div>
    )
  }

  RandomLinks.css = style
  return RandomLinks
}) satisfies QuartzComponentConstructor
