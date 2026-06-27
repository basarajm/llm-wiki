#!/usr/bin/env python3
"""
build-viz.py — 위키의 엔티티/관계를 Cytoscape.js 그래프(viz.html)로 렌더링.
콘텐츠 디렉토리의 .md frontmatter(type/title)와 본문 내부링크([..](/dir/page))로
노드·엣지를 만든다. 외부 의존성 없음(표준 라이브러리만).

사용: python scripts/build-viz.py   →  위키 루트에 viz.html 생성
"""
import os, re, json, html

# 스크립트 위치: <프로젝트>\engine\scripts\build-viz.py → 콘텐츠 루트는 <프로젝트>\wiki
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'wiki')
CONTENT_DIRS = ['companies','groups','industries','shareholders','value_chain',
                'segments','products','executives','financial_products','ratings',
                'sources','outputs']
RESERVED = {'index.md','log.md'}
LINK_RE = re.compile(r'\]\((/[^)\s]+)\)')

def parse_front_matter(text):
    fm = {}
    if not text.startswith('---'):
        return fm
    lines = text.splitlines()
    for line in lines[1:]:
        if line.strip() == '---':
            break
        m = re.match(r'\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$', line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm

def main():
    nodes, edges, seen = [], [], set()
    for d in CONTENT_DIRS:
        dpath = os.path.join(ROOT, d)
        if not os.path.isdir(dpath):
            continue
        for fn in os.listdir(dpath):
            if not fn.endswith('.md') or fn in RESERVED:
                continue
            base = fn[:-3]
            node_id = f'/{d}/{base}'
            with open(os.path.join(dpath, fn), encoding='utf-8') as f:
                text = f.read()
            fm = parse_front_matter(text)
            label = fm.get('title', base)
            ntype = fm.get('type', d)
            nodes.append({'data': {'id': node_id, 'label': label, 'group': ntype}})
            seen.add(node_id)
            for m in LINK_RE.finditer(text):
                tgt = m.group(1)
                if tgt.endswith('.md'):
                    tgt = tgt[:-3]
                edges.append({'data': {'source': node_id, 'target': tgt}})
    # 존재하는 노드 사이의 엣지만 유지
    edges = [e for e in edges if e['data']['target'] in seen]
    elements = nodes + edges

    tpl = """<!DOCTYPE html><html><head><meta charset="utf-8">
<title>LLM Wiki Graph</title>
<script src="https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js"></script>
<style>html,body{margin:0;height:100%}#cy{width:100%;height:100vh}</style></head>
<body><div id="cy"></div><script>
var elements = __ELEMENTS__;
cytoscape({container:document.getElementById('cy'),elements:elements,
  style:[{selector:'node',style:{'label':'data(label)','font-size':9,'background-color':'#4477aa','color':'#222'}},
         {selector:'edge',style:{'width':1,'line-color':'#bbb','target-arrow-color':'#bbb','target-arrow-shape':'triangle','curve-style':'bezier'}}],
  layout:{name:'cose',animate:false}});
</script></body></html>"""
    out = tpl.replace('__ELEMENTS__', json.dumps(elements, ensure_ascii=False))
    out_path = os.path.join(ROOT, 'viz.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(out)
    print(f'viz.html 생성: {out_path}  (노드 {len(nodes)}, 엣지 {len(edges)})')

if __name__ == '__main__':
    main()
