#!/usr/bin/env python3
"""
build-graph-image.py — 위키 엔티티/관계를 정적 PNG 그래프로 렌더링 (README·문서용).
viz.html(인터랙티브)과 달리 GitHub README에 바로 표시되는 이미지를 만든다.
타입별 색상, 연결도(degree) 기반 노드 크기, 허브 노드 한글 라벨 표시.

사용: python engine/scripts/build-graph-image.py   →  docs/graph.png 생성
필요: matplotlib, networkx, numpy (Windows 한글 폰트 Malgun Gothic 자동 사용)
"""
import os, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx

PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.join(PROJ, "wiki")
OUT_DIR = os.path.join(PROJ, "docs")
OUT = os.path.join(OUT_DIR, "graph.png")

CONTENT_DIRS = ['companies','groups','industries','shareholders','value_chain',
                'segments','products','executives','financial_products','ratings',
                'sources','outputs']
RESERVED = {'index.md','log.md'}
LINK_RE = re.compile(r'\]\((/[^)\s]+)\)')

# 타입 → 색상
TYPE_COLOR = {
    'Company':'#2e6fdb', 'Corporate Group':'#d62728', 'Industry':'#9467bd',
    'Shareholder':'#ff7f0e', 'Value Chain':'#17becf', 'Business Segment':'#1f9e4f',
    'Product':'#e377c2', 'Executive':'#8c564b', 'Financial Product':'#bcbd22',
    'Credit Rating':'#7f7f7f', 'Annual Report':'#aec7e8', 'Analysis':'#111111',
}
DEFAULT_COLOR = '#cccccc'

def parse_fm(text):
    fm = {}
    if not text.startswith('---'):
        return fm
    for line in text.splitlines()[1:]:
        if line.strip() == '---':
            break
        m = re.match(r'\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$', line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm

def main():
    G = nx.DiGraph()
    raw_edges = []
    for d in CONTENT_DIRS:
        dp = os.path.join(ROOT, d)
        if not os.path.isdir(dp):
            continue
        for fn in os.listdir(dp):
            if not fn.endswith('.md') or fn in RESERVED:
                continue
            base = fn[:-3]
            nid = f'/{d}/{base}'
            with open(os.path.join(dp, fn), encoding='utf-8') as f:
                text = f.read()
            fm = parse_fm(text)
            G.add_node(nid, label=fm.get('title', base), ntype=fm.get('type', d))
            for m in LINK_RE.finditer(text):
                tgt = m.group(1)
                if tgt.endswith('.md'):
                    tgt = tgt[:-3]
                raw_edges.append((nid, tgt))
    for s, t in raw_edges:
        if t in G:
            G.add_edge(s, t)

    # 폰트 (한글)
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False

    deg = dict(G.degree())
    pos = nx.spring_layout(G, k=0.55, iterations=120, seed=42)

    node_colors = [TYPE_COLOR.get(G.nodes[n]['ntype'], DEFAULT_COLOR) for n in G]
    node_sizes = [40 + 26 * deg.get(n, 0) for n in G]

    fig, ax = plt.subplots(figsize=(20, 14), dpi=150)
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#dddddd', width=0.5,
                           arrows=False, alpha=0.6)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                           node_size=node_sizes, linewidths=0.3, edgecolors='#ffffff')

    # 허브 노드(연결도 상위)만 라벨
    top = sorted(deg, key=lambda n: deg[n], reverse=True)[:18]
    labels = {n: G.nodes[n]['label'] for n in top}
    nx.draw_networkx_labels(G, pos, labels=labels, ax=ax, font_size=11,
                            font_family='Malgun Gothic', font_color='#111111')

    # 범례 (타입별)
    present = [t for t in TYPE_COLOR if any(G.nodes[n]['ntype'] == t for n in G)]
    handles = [Line2D([0], [0], marker='o', linestyle='', markersize=9,
                      markerfacecolor=TYPE_COLOR[t], markeredgecolor='white', label=t)
               for t in present]
    ax.legend(handles=handles, loc='lower left', fontsize=10, frameon=True,
              title='Page type', title_fontsize=11)

    ax.set_title(f'한국 기업 리서치 위키 — 지식 그래프  (노드 {G.number_of_nodes()} · 엣지 {G.number_of_edges()})',
                 fontsize=16, fontfamily='Malgun Gothic')
    ax.axis('off')
    plt.tight_layout()
    os.makedirs(OUT_DIR, exist_ok=True)
    fig.savefig(OUT, bbox_inches='tight', facecolor='white')
    print(f'graph.png 생성: {OUT}  (노드 {G.number_of_nodes()}, 엣지 {G.number_of_edges()})')

if __name__ == '__main__':
    main()
