# -*- coding: utf-8 -*-
"""
md_converter.py — DART 사업보고서 원문(XML/SGML) → 정제된 Markdown 변환기.

설계 목표:
  - 외부 의존성 0 (Python 표준 라이브러리 html.parser 만 사용 → Python 3.14 등 최신 환경에서도 빌드 문제 없음)
  - DART 전자공시 dart4.xsd 마크업 구조를 트리로 파싱한 뒤 LLM이 읽기 좋은 Markdown으로 변환
  - SECTION-1/2/3/4 중첩 → Markdown 제목 레벨(##/###/####/#####)
  - TABLE(TR/TH/TD/TU/TE, ROWSPAN·COLSPAN 포함) → GFM 표 (그리드 전개로 병합셀 정합성 유지)
  - 표지(COVER)의 목차표 등 노이즈는 제거, 본문(BODY) 위주로 추출

공개 함수:
  xml_to_markdown(xml_text: str, meta: dict) -> str
"""

from html.parser import HTMLParser
import re

# 닫는 태그가 생략될 수 있는(void) 태그 — 트리 빌드 시 자식을 받지 않음
VOID_TAGS = {"br", "pgbrk", "img"}

# 트리 walk 시 자체 출력 없이 자식만 재귀하는 컨테이너 태그
CONTAINER_TAGS = {
    "document", "body", "library", "summary", "tbody", "thead", "table-group",
    "a", "span", "extraction",
}

# 표 셀로 취급하는 태그
CELL_TAGS = {"th", "td", "tu", "te"}


class Node:
    __slots__ = ("tag", "attrs", "children")

    def __init__(self, tag, attrs=None):
        self.tag = tag
        self.attrs = attrs or {}
        self.children = []  # Node 또는 str


class _TreeBuilder(HTMLParser):
    """html.parser 기반의 관대한(lenient) 트리 빌더.

    - 태그/속성명은 소문자로 정규화됨
    - 닫는 태그가 어긋나도 스택에서 일치하는 항목까지만 pop (없으면 무시)
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("__root__")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        node = Node(tag, dict(attrs))
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag):
        # 스택을 위에서부터 훑어 일치하는 태그를 찾으면 거기까지 pop
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return
        # 일치 항목 없으면 무시 (관대 처리)

    def handle_data(self, data):
        if data:
            self.stack[-1].children.append(data)


# ----------------------------------------------------------------------------
# 텍스트 유틸
# ----------------------------------------------------------------------------

_WS_RE = re.compile(r"[ \t\r\f\v ]+")
_MULTINL_RE = re.compile(r"\n{3,}")


def _collapse_ws(s):
    s = s.replace(" ", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _inline_text(node):
    """노드 하위의 모든 텍스트를 공백 정규화하여 한 줄로 수집."""
    if isinstance(node, str):
        return node
    parts = []
    for ch in node.children:
        if isinstance(ch, str):
            parts.append(ch)
        elif ch.tag in VOID_TAGS:
            if ch.tag == "br":
                parts.append(" ")
            elif ch.tag == "img":
                parts.append(" (이미지) ")
        else:
            parts.append(_inline_text(ch))
    return "".join(parts)


def _cell_text(node):
    txt = _collapse_ws(_inline_text(node))
    txt = txt.replace("|", "\\|")
    return txt


# ----------------------------------------------------------------------------
# 표 변환 (ROWSPAN/COLSPAN 그리드 전개)
# ----------------------------------------------------------------------------

def _iter_rows(table):
    """table 노드 하위의 모든 TR을 (헤더여부, [셀노드...]) 형태로 순서대로 yield."""
    def walk(n, in_thead):
        for ch in n.children:
            if isinstance(ch, str):
                continue
            if ch.tag == "thead":
                yield from walk(ch, True)
            elif ch.tag in ("tbody", "table-group", "colgroup"):
                if ch.tag == "colgroup":
                    continue
                yield from walk(ch, in_thead)
            elif ch.tag == "tr":
                cells = [c for c in ch.children
                         if not isinstance(c, str) and c.tag in CELL_TAGS]
                all_th = bool(cells) and all(c.tag == "th" for c in cells)
                yield (in_thead or all_th, cells)
            else:
                yield from walk(ch, in_thead)

    yield from walk(table, False)


def _to_int(v, default=1):
    try:
        return max(1, int(v))
    except (TypeError, ValueError):
        return default


def _build_grid(rows):
    """(is_header, cells) 목록 → (grid: list[list[str]], header_row_count: int)."""
    grid = []
    header_count = 0
    pending = {}  # col_index -> [remaining_rows, text]
    leading = True

    for is_header, cells in rows:
        out = []
        ci = 0
        c = 0
        while ci < len(cells) or any(p[0] > 0 for p in pending.values() if True):
            # 현재 컬럼에 활성 rowspan이 있으면 우선 채움
            p = pending.get(c)
            if p and p[0] > 0:
                out.append(p[1])
                p[0] -= 1
                if p[0] == 0:
                    del pending[c]
                c += 1
                continue
            if ci < len(cells):
                cell = cells[ci]
                ci += 1
                cs = _to_int(cell.attrs.get("colspan"))
                rs = _to_int(cell.attrs.get("rowspan"))
                text = _cell_text(cell)
                out.append(text)
                for k in range(1, cs):
                    out.append("")
                if rs > 1:
                    for k in range(cs):
                        # rowspan 연속 셀: 첫 컬럼은 값 반복(카테고리 라벨), 나머지는 빈칸
                        pending[c + k] = [rs - 1, text if k == 0 else ""]
                c += cs
            else:
                break
        grid.append(out)
        if is_header and leading:
            header_count += 1
        else:
            leading = False
    return grid, header_count


def _table_to_md(table):
    rows = list(_iter_rows(table))
    if not rows:
        return ""
    grid, header_count = _build_grid(rows)
    if not grid:
        return ""
    width = max(len(r) for r in grid)
    if width == 0:
        return ""
    for r in grid:
        r += [""] * (width - len(r))

    # 1열짜리 '표'는 단위·주석 캡션인 경우가 대부분 → 일반 텍스트 줄로 출력
    if width == 1:
        lines = [r[0].strip() for r in grid if r[0].strip()]
        return "\n\n".join(lines)

    # 헤더 구성
    if header_count >= 1:
        header_rows = grid[:header_count]
        body_rows = grid[header_count:]
        header = []
        for col in range(width):
            vals = [hr[col] for hr in header_rows if hr[col]]
            header.append(" ".join(dict.fromkeys(vals)))  # 중복 제거 후 결합
    else:
        header = grid[0]
        body_rows = grid[1:]

    # 빈 헤더 셀은 컬럼 번호로 채움
    header = [h if h.strip() else f"열{idx + 1}" for idx, h in enumerate(header)]

    # 전부 빈 셀인 본문 행 제거 (목차표 등의 잔여 빈 행 정리)
    body_rows = [r for r in body_rows if any(c.strip() for c in r)]

    lines = []
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * width) + " |")
    for r in body_rows:
        cells = [(c if c.strip() else " ") for c in r]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# 본문 walk → Markdown
# ----------------------------------------------------------------------------

def _section_level(tag):
    m = re.match(r"section-(\d)", tag)
    return int(m.group(1)) if m else None


def _emit(out, text):
    if text:
        out.append(text)


def _is_toc_title(node):
    eng = node.attrs.get("eng", "").lower()
    if "table of contents" in eng:
        return True
    txt = _collapse_ws(_inline_text(node)).replace(" ", "")
    return txt in ("목차", "목 차")


def _walk(node, sec_num, out):
    skip_next_table = False
    for ch in node.children:
        if isinstance(ch, str):
            t = _collapse_ws(ch)
            if t:
                _emit(out, t)
            continue
        tag = ch.tag
        lvl = _section_level(tag)
        if lvl is not None:
            _walk(ch, lvl, out)
        elif tag == "cover":
            # 표지(제목면 + 목차표) 제거
            continue
        elif tag == "title":
            if _is_toc_title(ch):
                skip_next_table = True
                continue
            text = _collapse_ws(_inline_text(ch))
            if not text:
                continue
            if ch.attrs.get("atoc", "").lower() == "y":
                hashes = "#" * min(sec_num + 1, 6)
                _emit(out, f"{hashes} {text}")
            else:
                _emit(out, f"**{text}**")
        elif tag in ("table",):
            if skip_next_table:
                skip_next_table = False
                continue
            md = _table_to_md(ch)
            _emit(out, md)
        elif tag == "table-group":
            _walk(ch, sec_num, out)
        elif tag == "p":
            text = _collapse_ws(_inline_text(ch))
            if text:
                _emit(out, text)
        elif tag == "image":
            cap = ""
            for c in ch.children:
                if not isinstance(c, str) and c.tag == "img-caption":
                    cap = _collapse_ws(_inline_text(c))
            _emit(out, f"*(이미지{': ' + cap if cap else ''})*")
        elif tag in VOID_TAGS:
            continue
        else:
            # 그 밖의 컨테이너/미지정 태그는 자식만 재귀
            _walk(ch, sec_num, out)


def _build_frontmatter(meta):
    keys = [
        "corp_name", "corp_code", "stock_code", "market", "report_name",
        "fiscal_year", "rcept_no", "rcept_dt", "dart_url", "source_file",
        "downloaded_at", "converter",
    ]
    lines = ["---"]
    for k in keys:
        v = meta.get(k, "")
        if v is None:
            v = ""
        v = str(v).replace("\n", " ").strip()
        lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


def xml_to_markdown(xml_text, meta):
    """DART 원문 XML 문자열 → Markdown 문자열.

    meta: 프론트매터에 기록할 메타데이터 dict
    """
    builder = _TreeBuilder()
    try:
        builder.feed(xml_text)
        builder.close()
        root = builder.root
        # BODY 노드 탐색
        body = _find(root, "body")
        target = body if body is not None else root
        out = []
        _walk(target, 0, out)
        body_md = "\n\n".join(out)
    except Exception as e:  # noqa: BLE001 — 어떤 입력에도 파이프라인이 죽지 않도록
        body_md = _fallback_strip(xml_text)
        meta = dict(meta)
        meta["converter"] = meta.get("converter", "") + f" (fallback:{type(e).__name__})"

    body_md = _MULTINL_RE.sub("\n\n", body_md).strip()

    title = f"{meta.get('corp_name', '')} 사업보고서"
    rn = meta.get("report_name", "")
    if rn:
        title = f"{meta.get('corp_name', '')} — {rn}"

    header = (
        _build_frontmatter(meta)
        + f"\n\n# {title}\n\n"
        + f"> DART 전자공시 원문(접수번호 {meta.get('rcept_no','')})을 자동 변환한 문서입니다. "
        + f"원문 보기: {meta.get('dart_url','')}\n"
    )
    return header + "\n" + body_md + "\n"


def _find(node, tag):
    for ch in node.children:
        if isinstance(ch, str):
            continue
        if ch.tag == tag:
            return ch
        found = _find(ch, tag)
        if found is not None:
            return found
    return None


_TAG_RE = re.compile(r"<[^>]+>")


def _fallback_strip(xml_text):
    """파싱 실패 시 최소한의 텍스트라도 보존하는 폴백."""
    txt = _TAG_RE.sub(" ", xml_text)
    txt = _collapse_ws(txt)
    return txt


if __name__ == "__main__":
    import sys
    import zipfile

    # 단독 테스트: python md_converter.py sample.zip [내부XML명]
    zpath = sys.argv[1]
    z = zipfile.ZipFile(zpath)
    names = z.namelist()
    inner = sys.argv[2] if len(sys.argv) > 2 else min(
        (n for n in names if "_" not in n.split(".")[0][14:]), default=names[0]
    )
    raw = z.read(inner)
    try:
        xml = raw.decode("utf-8")
    except UnicodeDecodeError:
        xml = raw.decode("cp949", "replace")
    md = xml_to_markdown(xml, {
        "corp_name": "TEST", "rcept_no": inner.split(".")[0], "converter": "v1",
    })
    sys.stdout.reconfigure(encoding="utf-8")
    print(md[:6000])
    print(f"\n\n... [총 {len(md):,}자]")
