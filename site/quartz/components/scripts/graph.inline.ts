import type { ContentDetails } from "../../plugins/emitters/contentIndex"
import {
  SimulationNodeDatum,
  SimulationLinkDatum,
  Simulation,
  forceSimulation,
  forceManyBody,
  forceCenter,
  forceLink,
  forceCollide,
  forceRadial,
  zoomIdentity,
  select,
  drag,
  zoom,
} from "d3"
import { Text, Graphics, Application, Container, Circle } from "pixi.js"
import { Group as TweenGroup, Tween as Tweened } from "@tweenjs/tween.js"
import { registerEscapeHandler, removeAllChildren } from "./util"
import { FullSlug, SimpleSlug, getFullSlug, resolveRelative, simplifySlug } from "../../util/path"
import { D3Config } from "../Graph"

type GraphicsInfo = {
  color: string
  gfx: Graphics
  alpha: number
  active: boolean
}

type NodeData = {
  id: SimpleSlug
  text: string
  tags: string[]
} & SimulationNodeDatum

type SimpleLinkData = {
  source: SimpleSlug
  target: SimpleSlug
}

type LinkData = {
  source: NodeData
  target: NodeData
} & SimulationLinkDatum<NodeData>

type LinkRenderData = GraphicsInfo & {
  simulationData: LinkData
}

type NodeRenderData = GraphicsInfo & {
  simulationData: NodeData
  label: Text
}

const localStorageKey = "graph-visited"
function getVisited(): Set<SimpleSlug> {
  return new Set(JSON.parse(localStorage.getItem(localStorageKey) ?? "[]"))
}

function addToVisited(slug: SimpleSlug) {
  const visited = getVisited()
  visited.add(slug)
  localStorage.setItem(localStorageKey, JSON.stringify([...visited]))
}

type TweenNode = {
  update: (time: number) => void
  stop: () => void
}

// ─── 데이터/인덱스 빌드 (로컬·전역 그래프 공용) ──────────────────────────
function buildLinksAndIndices(
  data: Map<SimpleSlug, ContentDetails>,
  showTags: boolean,
  removeTags: string[],
) {
  const links: SimpleLinkData[] = []
  const validLinks = new Set(data.keys())

  for (const [source, details] of data.entries()) {
    const outgoing = details.links ?? []
    for (const dest of outgoing) {
      if (validLinks.has(dest)) {
        links.push({ source, target: dest })
      }
    }

    if (showTags) {
      const localTags = details.tags
        .filter((tag) => !removeTags.includes(tag))
        .map((tag) => simplifySlug(("tags/" + tag) as FullSlug))

      for (const tag of localTags) {
        links.push({ source, target: tag })
      }
    }
  }

  // 소스/타겟별로 미리 색인해두면 이웃 탐색 시 매번 전체 links 배열을 다시
  // 스캔하지 않아도 된다 (수만 페이지 규모에서 그래프가 멈추는 원인이었음)
  const outgoingIndex = new Map<SimpleSlug, SimpleSlug[]>()
  const incomingIndex = new Map<SimpleSlug, SimpleSlug[]>()
  for (const l of links) {
    if (!outgoingIndex.has(l.source)) outgoingIndex.set(l.source, [])
    outgoingIndex.get(l.source)!.push(l.target)
    if (!incomingIndex.has(l.target)) incomingIndex.set(l.target, [])
    incomingIndex.get(l.target)!.push(l.source)
  }

  return { links, outgoingIndex, incomingIndex }
}

// depth < 0("전체" 보기)이어도 사이트 전체를 무제한으로 펼치지 않는다 —
// start 노드에서부터 넓혀가되 maxNodes에 도달하면 그 자리에서 멈춘다.
function boundedNeighbourhood(
  start: SimpleSlug,
  depth: number,
  maxNodes: number,
  outgoingIndex: Map<SimpleSlug, SimpleSlug[]>,
  incomingIndex: Map<SimpleSlug, SimpleSlug[]>,
): Set<SimpleSlug> {
  const neighbourhood = new Set<SimpleSlug>()
  const wl: (SimpleSlug | "__SENTINEL")[] = [start, "__SENTINEL"]
  const unlimitedDepth = depth < 0
  let remainingDepth = depth
  while (wl.length > 0 && neighbourhood.size < maxNodes) {
    const cur = wl.shift()!
    if (cur === "__SENTINEL") {
      if (!unlimitedDepth) {
        remainingDepth--
        if (remainingDepth < 0) break
      }
      if (wl.length > 0) wl.push("__SENTINEL")
    } else if (!neighbourhood.has(cur)) {
      neighbourhood.add(cur)
      wl.push(...(outgoingIndex.get(cur) ?? []), ...(incomingIndex.get(cur) ?? []))
    }
  }
  return neighbourhood
}

const cssVars = [
  "--secondary",
  "--tertiary",
  "--gray",
  "--light",
  "--lightgray",
  "--dark",
  "--darkgray",
  "--bodyFont",
] as const
type ComputedStyleMap = Record<(typeof cssVars)[number], string>
function getComputedStyleMap(): ComputedStyleMap {
  return cssVars.reduce((acc, key) => {
    acc[key] = getComputedStyle(document.documentElement).getPropertyValue(key)
    return acc
  }, {} as ComputedStyleMap)
}

// ─── pixi/d3 렌더링 (로컬·전역 그래프 공용) ──────────────────────────────
// 주어진 노드/링크 스냅샷을 한 번 그린다. 로컬 그래프는 페이지당 한 번,
// 전역(확장형) 그래프는 확장/뒤로/초기화 때마다 이 함수를 다시 호출해 새로
// 그린다 — 같은 NodeData 객체를 재사용하는 쪽(nodeDataById)에서 x/y를
// 유지시켜 주므로 기존 노드는 제자리에 남고 새 노드만 그 주변에 나타난다.
async function paintScene(params: {
  host: HTMLElement
  width: number
  height: number
  nodes: NodeData[]
  links: LinkData[]
  d3cfg: D3Config
  computedStyleMap: ComputedStyleMap
  colorOf: (d: NodeData) => string
  onActivate: (id: SimpleSlug) => void
}): Promise<() => void> {
  const { host, width, height, nodes, links: graphLinks, d3cfg, computedStyleMap, colorOf, onActivate } =
    params
  const {
    drag: enableDrag,
    zoom: enableZoom,
    scale,
    repelForce,
    centerForce,
    linkDistance,
    fontSize,
    opacityScale,
    focusOnHover,
    enableRadial,
  } = d3cfg

  const simulation: Simulation<NodeData, LinkData> = forceSimulation<NodeData>(nodes)
    .force("charge", forceManyBody().strength(-100 * repelForce))
    .force("center", forceCenter().strength(centerForce))
    .force("link", forceLink(graphLinks).distance(linkDistance))
    .force("collide", forceCollide<NodeData>((n) => nodeRadius(n)).iterations(3))

  const radius = (Math.min(width, height) / 2) * 0.8
  if (enableRadial) simulation.force("radial", forceRadial(radius).strength(0.2))

  function nodeRadius(d: NodeData) {
    const numLinks = graphLinks.filter((l) => l.source.id === d.id || l.target.id === d.id).length
    return 2 + Math.sqrt(numLinks)
  }

  let hoveredNodeId: string | null = null
  const linkRenderData: LinkRenderData[] = []
  const nodeRenderData: NodeRenderData[] = []
  const tweens = new Map<string, TweenNode>()

  function updateHoverInfo(newHoveredId: string | null) {
    hoveredNodeId = newHoveredId

    if (newHoveredId === null) {
      for (const n of nodeRenderData) n.active = false
      for (const l of linkRenderData) l.active = false
    } else {
      const hoveredNeighbours = new Set<string>()
      for (const l of linkRenderData) {
        const linkData = l.simulationData
        if (linkData.source.id === newHoveredId || linkData.target.id === newHoveredId) {
          hoveredNeighbours.add(linkData.source.id)
          hoveredNeighbours.add(linkData.target.id)
        }
        l.active = linkData.source.id === newHoveredId || linkData.target.id === newHoveredId
      }
      for (const n of nodeRenderData) {
        n.active = hoveredNeighbours.has(n.simulationData.id)
      }
    }
  }

  function renderLinks() {
    tweens.get("link")?.stop()
    const tweenGroup = new TweenGroup()

    for (const l of linkRenderData) {
      let alpha = 1
      if (hoveredNodeId) alpha = l.active ? 1 : 0.2
      l.color = l.active ? computedStyleMap["--gray"] : computedStyleMap["--lightgray"]
      tweenGroup.add(new Tweened<LinkRenderData>(l).to({ alpha }, 200))
    }

    tweenGroup.getAll().forEach((tw) => tw.start())
    tweens.set("link", {
      update: tweenGroup.update.bind(tweenGroup),
      stop() {
        tweenGroup.getAll().forEach((tw) => tw.stop())
      },
    })
  }

  function renderLabels() {
    tweens.get("label")?.stop()
    const tweenGroup = new TweenGroup()

    const defaultScale = 1 / scale
    const activeScale = defaultScale * 1.1
    for (const n of nodeRenderData) {
      const nodeId = n.simulationData.id
      if (hoveredNodeId === nodeId) {
        tweenGroup.add(
          new Tweened<Text>(n.label).to({ alpha: 1, scale: { x: activeScale, y: activeScale } }, 100),
        )
      } else {
        tweenGroup.add(
          new Tweened<Text>(n.label).to(
            { alpha: n.label.alpha, scale: { x: defaultScale, y: defaultScale } },
            100,
          ),
        )
      }
    }

    tweenGroup.getAll().forEach((tw) => tw.start())
    tweens.set("label", {
      update: tweenGroup.update.bind(tweenGroup),
      stop() {
        tweenGroup.getAll().forEach((tw) => tw.stop())
      },
    })
  }

  function renderNodes() {
    tweens.get("hover")?.stop()
    const tweenGroup = new TweenGroup()
    for (const n of nodeRenderData) {
      let alpha = 1
      if (hoveredNodeId !== null && focusOnHover) alpha = n.active ? 1 : 0.2
      tweenGroup.add(new Tweened<Graphics>(n.gfx, tweenGroup).to({ alpha }, 200))
    }

    tweenGroup.getAll().forEach((tw) => tw.start())
    tweens.set("hover", {
      update: tweenGroup.update.bind(tweenGroup),
      stop() {
        tweenGroup.getAll().forEach((tw) => tw.stop())
      },
    })
  }

  function renderPixiFromD3() {
    renderNodes()
    renderLinks()
    renderLabels()
  }

  const app = new Application()
  await app.init({
    width,
    height,
    antialias: true,
    autoStart: false,
    autoDensity: true,
    backgroundAlpha: 0,
    preference: "webgpu",
    resolution: window.devicePixelRatio,
    eventMode: "static",
  })
  host.appendChild(app.canvas)

  const stage = app.stage
  stage.interactive = false

  const labelsContainer = new Container<Text>({ zIndex: 3, isRenderGroup: true })
  const nodesContainer = new Container<Graphics>({ zIndex: 2, isRenderGroup: true })
  const linkContainer = new Container<Graphics>({ zIndex: 1, isRenderGroup: true })
  stage.addChild(nodesContainer, labelsContainer, linkContainer)

  for (const n of nodes) {
    const nodeId = n.id

    const label = new Text({
      interactive: false,
      eventMode: "none",
      text: n.text,
      alpha: 0,
      anchor: { x: 0.5, y: 1.2 },
      style: {
        fontSize: fontSize * 15,
        fill: computedStyleMap["--dark"],
        fontFamily: computedStyleMap["--bodyFont"],
      },
      resolution: window.devicePixelRatio * 4,
    })
    label.scale.set(1 / scale)

    let oldLabelOpacity = 0
    const isTagNode = nodeId.startsWith("tags/")
    const gfx = new Graphics({
      interactive: true,
      label: nodeId,
      eventMode: "static",
      hitArea: new Circle(0, 0, nodeRadius(n)),
      cursor: "pointer",
    })
      .circle(0, 0, nodeRadius(n))
      .fill({ color: isTagNode ? computedStyleMap["--light"] : colorOf(n) })
      .on("pointerover", (e) => {
        updateHoverInfo(e.target.label)
        oldLabelOpacity = label.alpha
        if (!dragging) renderPixiFromD3()
      })
      .on("pointerleave", () => {
        updateHoverInfo(null)
        label.alpha = oldLabelOpacity
        if (!dragging) renderPixiFromD3()
      })

    if (isTagNode) {
      gfx.stroke({ width: 2, color: computedStyleMap["--tertiary"] })
    }

    nodesContainer.addChild(gfx)
    labelsContainer.addChild(label)

    nodeRenderData.push({
      simulationData: n,
      gfx,
      label,
      color: colorOf(n),
      alpha: 1,
      active: false,
    })
  }

  for (const l of graphLinks) {
    const gfx = new Graphics({ interactive: false, eventMode: "none" })
    linkContainer.addChild(gfx)
    linkRenderData.push({
      simulationData: l,
      gfx,
      color: computedStyleMap["--lightgray"],
      alpha: 1,
      active: false,
    })
  }

  let dragStartTime = 0
  let dragging = false
  let currentTransform = zoomIdentity

  if (enableDrag) {
    select<HTMLCanvasElement, NodeData | undefined>(app.canvas).call(
      drag<HTMLCanvasElement, NodeData | undefined>()
        .container(() => app.canvas)
        .subject(() => nodes.find((n) => n.id === hoveredNodeId))
        .on("start", function dragstarted(event) {
          if (!event.active) simulation.alphaTarget(1).restart()
          event.subject.fx = event.subject.x
          event.subject.fy = event.subject.y
          event.subject.__initialDragPos = {
            x: event.subject.x,
            y: event.subject.y,
            fx: event.subject.fx,
            fy: event.subject.fy,
          }
          dragStartTime = Date.now()
          dragging = true
        })
        .on("drag", function dragged(event) {
          const initPos = event.subject.__initialDragPos
          event.subject.fx = initPos.x + (event.x - initPos.x) / currentTransform.k
          event.subject.fy = initPos.y + (event.y - initPos.y) / currentTransform.k
        })
        .on("end", function dragended(event) {
          if (!event.active) simulation.alphaTarget(0)
          event.subject.fx = null
          event.subject.fy = null
          dragging = false

          // if the time between mousedown and mouseup is short, we consider it a click
          if (Date.now() - dragStartTime < 500) {
            onActivate(event.subject.id as SimpleSlug)
          }
        }),
    )
  } else {
    for (const node of nodeRenderData) {
      node.gfx.on("click", () => onActivate(node.simulationData.id))
    }
  }

  if (enableZoom) {
    select<HTMLCanvasElement, NodeData>(app.canvas).call(
      zoom<HTMLCanvasElement, NodeData>()
        .extent([
          [0, 0],
          [width, height],
        ])
        .scaleExtent([0.25, 4])
        .on("zoom", ({ transform }) => {
          currentTransform = transform
          stage.scale.set(transform.k, transform.k)
          stage.position.set(transform.x, transform.y)

          const scale = transform.k * opacityScale
          let scaleOpacity = Math.max((scale - 1) / 3.75, 0)
          const activeNodes = nodeRenderData.filter((n) => n.active).flatMap((n) => n.label)

          for (const label of labelsContainer.children) {
            if (!activeNodes.includes(label)) {
              label.alpha = scaleOpacity
            }
          }
        }),
    )
  }

  let stopAnimation = false
  function animate(time: number) {
    if (stopAnimation) return
    for (const n of nodeRenderData) {
      const { x, y } = n.simulationData
      // 0은 유효한 좌표다 — falsy 체크(!x)를 쓰면 중심(포스가 원점으로 당기는)
      // 노드처럼 좌표가 정확히 0이 되는 노드가 렌더링에서 통째로 빠진다.
      if (x === undefined || y === undefined) continue
      n.gfx.position.set(x + width / 2, y + height / 2)
      if (n.label) {
        n.label.position.set(x + width / 2, y + height / 2)
      }
    }

    for (const l of linkRenderData) {
      const linkData = l.simulationData
      l.gfx.clear()
      l.gfx.moveTo(linkData.source.x! + width / 2, linkData.source.y! + height / 2)
      l.gfx
        .lineTo(linkData.target.x! + width / 2, linkData.target.y! + height / 2)
        .stroke({ alpha: l.alpha, width: 1, color: l.color })
    }

    tweens.forEach((t) => t.update(time))
    app.renderer.render(stage)
    requestAnimationFrame(animate)
  }

  requestAnimationFrame(animate)
  return () => {
    stopAnimation = true
    tweens.forEach((t) => t.stop())
    app.destroy()
  }
}

// ─── 로컬(사이드바) 그래프 — 페이지 이동마다 새로 그리는 정적 뷰 ─────────
async function renderGraph(graph: HTMLElement, fullSlug: FullSlug) {
  const slug = simplifySlug(fullSlug)
  const visited = getVisited()
  removeAllChildren(graph)

  const cfg = JSON.parse(graph.dataset["cfg"]!) as D3Config
  const { removeTags, showTags, depth, maxNodes } = cfg

  const data: Map<SimpleSlug, ContentDetails> = new Map(
    Object.entries<ContentDetails>(await fetchData).map(([k, v]) => [simplifySlug(k as FullSlug), v]),
  )
  const { links, outgoingIndex, incomingIndex } = buildLinksAndIndices(data, showTags, removeTags)
  const neighbourhood = boundedNeighbourhood(slug, depth, maxNodes, outgoingIndex, incomingIndex)

  const nodes: NodeData[] = [...neighbourhood].map((url) => ({
    id: url,
    text: url.startsWith("tags/") ? "#" + url.substring(5) : (data.get(url)?.title ?? url),
    tags: data.get(url)?.tags ?? [],
  }))
  const nodeById = new Map(nodes.map((n) => [n.id, n]))
  const graphLinks: LinkData[] = links
    .filter((l) => neighbourhood.has(l.source) && neighbourhood.has(l.target))
    .map((l) => ({ source: nodeById.get(l.source)!, target: nodeById.get(l.target)! }))

  const width = graph.offsetWidth
  const height = Math.max(graph.offsetHeight, 250)
  const computedStyleMap = getComputedStyleMap()
  const colorOf = (d: NodeData) => {
    if (d.id === slug) return computedStyleMap["--secondary"]
    if (visited.has(d.id) || d.id.startsWith("tags/")) return computedStyleMap["--tertiary"]
    return computedStyleMap["--gray"]
  }

  return paintScene({
    host: graph,
    width,
    height,
    nodes,
    links: graphLinks,
    d3cfg: cfg,
    computedStyleMap,
    colorOf,
    onActivate: (id) => {
      const targ = resolveRelative(fullSlug, id)
      window.spaNavigate(new URL(targ, window.location.toString()))
    },
  })
}

// ─── 전역(확장형) 그래프 — 클릭으로 이웃을 계속 확장해가는 탐색형 뷰 ─────
// 예: 가온전선 페이지에서 열면 가온전선이 중심 노드가 되고, 연결된
// "초고압케이블" 노드를 클릭하면 기존 그래프는 그대로 둔 채 그 노드의
// 이웃만 추가로 확장된다. 이후 새로 나타난 노드를 또 클릭하면 계속
// 확장되고, "이전" 버튼으로 직전 상태로, "초기화" 버튼으로 처음(중심 노드
// 기준 N단계) 화면으로 되돌아간다.
async function renderExpandableGraph(
  canvasHost: HTMLElement,
  fullSlug: FullSlug,
  controls: {
    depthSelect: HTMLSelectElement
    backBtn: HTMLButtonElement
    clearBtn: HTMLButtonElement
  },
): Promise<() => void> {
  const centerId = simplifySlug(fullSlug)
  const visited = getVisited()
  const cfg = JSON.parse(canvasHost.dataset["cfg"]!) as D3Config
  const { removeTags, showTags, maxNodes } = cfg

  const data: Map<SimpleSlug, ContentDetails> = new Map(
    Object.entries<ContentDetails>(await fetchData).map(([k, v]) => [simplifySlug(k as FullSlug), v]),
  )
  const { links, outgoingIndex, incomingIndex } = buildLinksAndIndices(data, showTags, removeTags)

  // 재빌드를 거쳐도 기존 노드의 좌표(x,y)가 유지되도록 슬러그별로 NodeData를
  // 계속 재사용한다 — 그래야 확장할 때마다 기존 그래프가 흐트러지지 않는다.
  const nodeDataById = new Map<SimpleSlug, NodeData>()
  function getOrCreateNode(id: SimpleSlug): NodeData {
    let n = nodeDataById.get(id)
    if (!n) {
      n = {
        id,
        text: id.startsWith("tags/") ? "#" + id.substring(5) : (data.get(id)?.title ?? id),
        tags: data.get(id)?.tags ?? [],
      }
      nodeDataById.set(id, n)
    }
    return n
  }

  const currentDepth = () => Number(controls.depthSelect.value) || 1

  let initialIds = boundedNeighbourhood(centerId, currentDepth(), maxNodes, outgoingIndex, incomingIndex)
  let currentIds = new Set(initialIds)
  let history: Set<SimpleSlug>[] = []
  let disposeScene: (() => void) | null = null

  const width = canvasHost.offsetWidth
  const height = Math.max(canvasHost.offsetHeight, 250)
  const computedStyleMap = getComputedStyleMap()
  const colorOf = (d: NodeData) => {
    if (d.id === centerId) return computedStyleMap["--secondary"]
    if (visited.has(d.id) || d.id.startsWith("tags/")) return computedStyleMap["--tertiary"]
    return computedStyleMap["--gray"]
  }

  // 같은 노드를 짧은 간격으로 두 번 "클릭"하면(= 더블클릭) 확장 대신 이동한다.
  let lastActivateId: SimpleSlug | null = null
  let lastActivateTime = 0
  function onActivate(id: SimpleSlug) {
    const now = Date.now()
    const isDoubleActivate = id === lastActivateId && now - lastActivateTime < 450
    lastActivateId = id
    lastActivateTime = now

    if (isDoubleActivate) {
      const targ = resolveRelative(fullSlug, id)
      window.spaNavigate(new URL(targ, window.location.toString()))
      return
    }

    expand(id)
  }

  function updateButtons() {
    controls.backBtn.disabled = history.length === 0
  }

  async function rebuild() {
    disposeScene?.()
    removeAllChildren(canvasHost)

    const nodes = [...currentIds].map(getOrCreateNode)
    const graphLinks: LinkData[] = links
      .filter((l) => currentIds.has(l.source) && currentIds.has(l.target))
      .map((l) => ({ source: getOrCreateNode(l.source), target: getOrCreateNode(l.target) }))

    disposeScene = await paintScene({
      host: canvasHost,
      width,
      height,
      nodes,
      links: graphLinks,
      d3cfg: cfg,
      computedStyleMap,
      colorOf,
      onActivate,
    })
  }

  function expand(id: SimpleSlug) {
    const neighbours = [...(outgoingIndex.get(id) ?? []), ...(incomingIndex.get(id) ?? [])]
    const newIds = neighbours.filter((n) => !currentIds.has(n))
    if (newIds.length === 0) return

    const room = Math.max(0, maxNodes - currentIds.size)
    if (room === 0) return

    history.push(new Set(currentIds))
    currentIds = new Set([...currentIds, ...newIds.slice(0, room)])
    updateButtons()
    void rebuild()
  }

  function goBack() {
    if (history.length === 0) return
    currentIds = history.pop()!
    updateButtons()
    void rebuild()
  }

  function clear() {
    history = []
    currentIds = new Set(initialIds)
    updateButtons()
    void rebuild()
  }

  function onDepthChange() {
    initialIds = boundedNeighbourhood(centerId, currentDepth(), maxNodes, outgoingIndex, incomingIndex)
    history = []
    currentIds = new Set(initialIds)
    updateButtons()
    void rebuild()
  }

  controls.backBtn.addEventListener("click", goBack)
  controls.clearBtn.addEventListener("click", clear)
  controls.depthSelect.addEventListener("change", onDepthChange)
  updateButtons()
  await rebuild()

  return () => {
    disposeScene?.()
    controls.backBtn.removeEventListener("click", goBack)
    controls.clearBtn.removeEventListener("click", clear)
    controls.depthSelect.removeEventListener("change", onDepthChange)
  }
}

let localGraphCleanups: (() => void)[] = []
let globalGraphCleanups: (() => void)[] = []

function cleanupLocalGraphs() {
  for (const cleanup of localGraphCleanups) {
    cleanup()
  }
  localGraphCleanups = []
}

function cleanupGlobalGraphs() {
  for (const cleanup of globalGraphCleanups) {
    cleanup()
  }
  globalGraphCleanups = []
}

document.addEventListener("nav", async (e: CustomEventMap["nav"]) => {
  const slug = e.detail.url
  addToVisited(simplifySlug(slug))

  async function renderLocalGraph() {
    cleanupLocalGraphs()
    const localGraphContainers = document.getElementsByClassName("graph-container")
    for (const container of localGraphContainers) {
      localGraphCleanups.push(await renderGraph(container as HTMLElement, slug))
    }
  }

  await renderLocalGraph()
  const handleThemeChange = () => {
    void renderLocalGraph()
  }

  document.addEventListener("themechange", handleThemeChange)
  window.addCleanup(() => {
    document.removeEventListener("themechange", handleThemeChange)
  })

  const containers = [...document.getElementsByClassName("global-graph-outer")] as HTMLElement[]
  async function renderGlobalGraph() {
    const currentSlug = getFullSlug(window)
    for (const container of containers) {
      container.classList.add("active")
      const sidebar = container.closest(".sidebar") as HTMLElement
      if (sidebar) {
        sidebar.style.zIndex = "1"
      }

      const canvasHost = container.querySelector(".global-graph-canvas") as HTMLElement
      const depthSelect = container.querySelector(".graph-depth-select") as HTMLSelectElement
      const backBtn = container.querySelector(".graph-back-btn") as HTMLButtonElement
      const clearBtn = container.querySelector(".graph-clear-btn") as HTMLButtonElement
      registerEscapeHandler(container, hideGlobalGraph)
      if (canvasHost && depthSelect && backBtn && clearBtn) {
        globalGraphCleanups.push(
          await renderExpandableGraph(canvasHost, currentSlug, { depthSelect, backBtn, clearBtn }),
        )
      }
    }
  }

  function hideGlobalGraph() {
    cleanupGlobalGraphs()
    for (const container of containers) {
      container.classList.remove("active")
      const sidebar = container.closest(".sidebar") as HTMLElement
      if (sidebar) {
        sidebar.style.zIndex = ""
      }
    }
  }

  async function shortcutHandler(e: HTMLElementEventMap["keydown"]) {
    if (e.key === "g" && (e.ctrlKey || e.metaKey) && !e.shiftKey) {
      e.preventDefault()
      const anyGlobalGraphOpen = containers.some((container) =>
        container.classList.contains("active"),
      )
      anyGlobalGraphOpen ? hideGlobalGraph() : renderGlobalGraph()
    }
  }

  const containerIcons = document.getElementsByClassName("global-graph-icon")
  Array.from(containerIcons).forEach((icon) => {
    icon.addEventListener("click", renderGlobalGraph)
    window.addCleanup(() => icon.removeEventListener("click", renderGlobalGraph))
  })

  document.addEventListener("keydown", shortcutHandler)
  window.addCleanup(() => {
    document.removeEventListener("keydown", shortcutHandler)
    cleanupLocalGraphs()
    cleanupGlobalGraphs()
  })
})
