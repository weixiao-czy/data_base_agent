"""
文献地图渲染：输出 Markdown 大纲 / 交互式 HTML 思维导图 / JSON

HTML 是自包含的（内联 CSS + JS，无外部依赖、无 CDN），
双击即可离线打开，支持折叠、缩放、拖拽、检索高亮与文献详情面板。
"""

import html
import json
from typing import Any, Dict, List

from .models import (
    KIND_ASPECT,
    KIND_PAPER,
    KIND_ROOT,
    KIND_TOPIC,
    LiteratureMap,
)


# ---------------------------------------------------------------- Markdown

def to_markdown(litmap: LiteratureMap) -> str:
    """输出便于贴进笔记/文档的层级大纲"""
    data = litmap.to_dict()
    d = data["stats"]
    lines = [
        f"# 文献地图：{data['topic']}",
        "",
        f"> 生成时间 {data['generated_at']}｜共 {d['total_papers']} 篇文献、"
        f"{d['total_topics']} 个检索方向",
        "",
        "阅读顺序建议：先看「综述与奠基」建立全局，再按「核心方法 → 数据集与评测」"
        "定位自己的技术路线，最后用「挑战与开放问题」找选题切入点。",
        "",
        "---",
        "",
    ]

    def walk(node: Dict[str, Any], level: int) -> None:
        if node["kind"] == KIND_ROOT:
            for c in node["children"]:
                walk(c, level)
            return

        indent = "  " * level
        if node["kind"] == KIND_ASPECT:
            lines.append(f"{indent}- **{node['label']}** （{node['total_paper_count']} 篇）")
            lines.append(f"{indent}  _{node['note']}_")
            for c in node["children"]:
                walk(c, level + 1)
        elif node["kind"] == KIND_TOPIC:
            lines.append(f"{indent}- {node['label']}")
            if node.get("query"):
                lines.append(f"{indent}  `{node['query']}`")
            for p in node["papers"]:
                lines.append(f"{indent}  - [{p['title']}]({p['url']})"
                             f" — {(p['authors'] or ['佚名'])[0]}"
                             f"{' 等' if len(p['authors']) > 1 else ''}"
                             f" ({p['year'] or 'n.d.'})")
            for c in node["children"]:
                walk(c, level + 1)

    walk(data["root"], 0)

    # 文献总表
    lines += ["", "---", "", "## 文献清单", ""]
    rows = ["| # | 标题 | 年份 | 来源 | 所属分支 |", "|---|---|---|---|---|"]
    for i, p in enumerate(litmap.root.all_papers(), 1):
        title = p["title"].replace("|", "\\|")
        link = f"[{title}]({p['url']})" if p.get("url") else title
        rows.append(
            f"| {i} | {link} | {p['year'] or '-'} | {p['source'] or '-'} | {p['_node']} |"
        )
    lines += rows
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------- HTML

_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  :root{
    --bg:#f7f8fa; --panel:#ffffff; --ink:#1f2937; --ink-2:#4b5563; --ink-3:#8b95a3;
    --line:#e3e7ee; --accent:#2f6fed;
  }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%}
  body{
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",
      "Hiragino Sans GB","Microsoft YaHei",sans-serif;
    background:var(--bg); color:var(--ink); overflow:hidden;
  }
  .app{display:flex;height:100vh}

  /* ---------- 画布 ---------- */
  .canvas-wrap{position:relative;flex:1;overflow:hidden;cursor:grab}
  .canvas-wrap.dragging{cursor:grabbing}
  svg{display:block;width:100%;height:100%}
  .node{cursor:pointer}
  .node rect{transition:filter .15s, stroke .15s}
  .node:hover rect{filter:brightness(.97)}
  .node.sel rect{stroke:var(--accent);stroke-width:2.2}
  .node text{pointer-events:none;user-select:none}
  .edge{fill:none;stroke:#cfd6e2;stroke-width:1.4}
  .badge-txt{font-size:10.5px;font-weight:600}

  /* ---------- 顶部栏 ---------- */
  .topbar{
    position:absolute;left:16px;top:14px;right:16px;display:flex;gap:10px;
    align-items:center;pointer-events:none;z-index:5;
  }
  .topbar > *{pointer-events:auto}
  .title-box{background:var(--panel);border:1px solid var(--line);border-radius:10px;
    padding:9px 14px;box-shadow:0 1px 3px rgba(16,24,40,.06);max-width:46%}
  .title-box h1{margin:0;font-size:14px;font-weight:650;white-space:nowrap;
    overflow:hidden;text-overflow:ellipsis}
  .title-box p{margin:2px 0 0;font-size:11.5px;color:var(--ink-3)}
  .search{flex:1;max-width:280px;margin-left:auto;position:relative}
  .search input{
    width:100%;padding:9px 12px 9px 32px;border:1px solid var(--line);border-radius:10px;
    background:var(--panel);font-size:12.5px;outline:none;color:var(--ink);
  }
  .search input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(47,111,237,.1)}
  .search .ico{position:absolute;left:11px;top:9px;color:var(--ink-3);font-size:13px}
  .btn{
    padding:9px 12px;border:1px solid var(--line);border-radius:10px;background:var(--panel);
    font-size:12.5px;color:var(--ink-2);cursor:pointer;white-space:nowrap;
  }
  .btn:hover{border-color:#c8d0dd;color:var(--ink)}

  /* ---------- 图例 ---------- */
  .legend{
    position:absolute;left:16px;bottom:14px;background:var(--panel);border:1px solid var(--line);
    border-radius:10px;padding:9px 12px;font-size:11.5px;color:var(--ink-2);
    display:flex;gap:14px;align-items:center;box-shadow:0 1px 3px rgba(16,24,40,.05)
  }
  .legend i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px;
    vertical-align:-1px}

  /* ---------- 侧栏 ---------- */
  .side{
    width:330px;flex:none;background:var(--panel);border-left:1px solid var(--line);
    display:flex;flex-direction:column;overflow:hidden;
  }
  .side.hide{display:none}
  .side-head{padding:16px 18px 12px;border-bottom:1px solid var(--line)}
  .chip{display:inline-block;font-size:10.5px;padding:2px 8px;border-radius:999px;
    background:#eef2f9;color:#3d5a99;margin-bottom:7px;font-weight:600}
  .side-head h2{margin:0;font-size:15px;line-height:1.4;font-weight:650}
  .side-head .note{margin:7px 0 0;font-size:12px;color:var(--ink-2);line-height:1.6}
  .side-head .q{margin:8px 0 0;font-size:11.5px;color:var(--ink-3);word-break:break-all}
  .side-head .q code{background:#f3f5f9;padding:2px 6px;border-radius:5px;font-size:11px}
  .side-body{overflow-y:auto;padding:6px 0 24px}
  .empty{padding:28px 18px;font-size:12.5px;color:var(--ink-3);line-height:1.8}
  .paper{padding:12px 18px;border-bottom:1px solid #f0f2f6}
  .paper:hover{background:#fafbfd}
  .paper a{color:#1a4eba;text-decoration:none;font-size:12.8px;font-weight:600;
    line-height:1.5;display:block}
  .paper a:hover{text-decoration:underline}
  .paper .meta{margin-top:5px;font-size:11px;color:var(--ink-3);line-height:1.6}
  .paper .abs{margin-top:6px;font-size:11.5px;color:var(--ink-2);line-height:1.65;
    display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
  .side-foot{padding:8px 18px;border-top:1px solid var(--line);font-size:11px;
    color:var(--ink-3);display:flex;justify-content:space-between}
  ::-webkit-scrollbar{width:9px;height:9px}
  ::-webkit-scrollbar-thumb{background:#d5dae3;border-radius:6px;border:2px solid var(--panel)}
  ::-webkit-scrollbar-thumb:hover{background:#c2c9d6}
</style>
</head>
<body>
<div class="app">
  <div class="canvas-wrap" id="wrap">
    <svg id="svg"><g id="viewport"><g id="edges"></g><g id="nodes"></g></g></svg>

    <div class="topbar">
      <div class="title-box">
        <h1>__TOPIC__</h1>
        <p id="stats"></p>
      </div>
      <div class="search">
        <span class="ico">⌕</span>
        <input id="q" type="text" placeholder="搜索节点或文献标题…">
      </div>
      <button class="btn" id="expand-all">全部展开</button>
      <button class="btn" id="collapse-all">收起到维度</button>
      <button class="btn" id="fit">适应窗口</button>
    </div>

    <div class="legend">
      <span><i style="background:#1f2937"></i>研究主题</span>
      <span><i style="background:#2f6fed"></i>研究维度</span>
      <span><i style="background:#ffffff;border:1px solid #cfd6e2"></i>检索方向</span>
      <span><i style="background:#eef2f9"></i>文献</span>
      <span style="color:#aeb6c2">点击节点展开 / 折叠</span>
    </div>
  </div>

  <aside class="side" id="side">
    <div class="side-head">
      <span class="chip" id="side-kind">提示</span>
      <h2 id="side-title">点击左侧节点查看详情</h2>
      <p class="note" id="side-note">这张地图按「研究维度 → 检索方向 → 文献」三层组织。建议先读综述维度建立全局认知。</p>
      <p class="q" id="side-query"></p>
    </div>
    <div class="side-body" id="side-body"></div>
    <div class="side-foot">
      <span id="side-count"></span>
      <span>__GEN__</span>
    </div>
  </aside>
</div>

<script>
const DATA = __DATA__;

const NODE_W = {root:272, aspect:176, topic:212, paper:268};
const NODE_H = {root:56, aspect:42, topic:42, paper:34};
const GAP_X  = 72, GAP_Y = 14;
const PAD    = 40;

const PALETTE = ['#2f6fed','#0ea5a4','#b45309','#7c3aed','#be3461','#0284c7','#4d7c0f'];

const COL_X = [PAD];
for (let d=0; d<4; d++){
  const w = [NODE_W.root, NODE_W.aspect, NODE_W.topic, NODE_W.paper][d];
  COL_X.push(COL_X[d] + w + GAP_X);
}

// ---------- 初始化状态 ----------
let idSeq = 0;
function prep(node, depth, parent, idx){
  node._id = 'n' + (idSeq++);
  node._depth = depth;
  node._parent = parent;
  node._idx = idx || 0;                          // 维度配色索引
  node._kids = node.children || [];
  node._expanded = depth === 0 || depth === 1;   // 默认展开到维度层
  node._papers = node.papers || [];
  node._paperOpen = false;
  node._total = node.total_paper_count || 0;
  (node.children || []).forEach((c, i) => prep(c, depth + 1, node, i));
}
prep(DATA.root, 0, null);

const allNodes = [];
(function collect(n){ allNodes.push(n); (n.children||[]).forEach(collect); })(DATA.root);

// ---------- 布局 ----------
let cursorY = 0;

function visibleKids(n){
  if (!n._expanded) return [];
  const kids = (n.children || []).slice();
  if (n._paperOpen){
    n._papers.forEach((p, i) => {
      kids.push({
        _id: n._id + '_p' + i, _isPaper: true, _depth: n._depth + 1,
        _parent: n, _papers: [], children: [], label: p.title,
        paper: p, _kids: [], _expanded: false, _total: 0
      });
    });
  }
  return kids;
}

function layout(n){
  n._x = COL_X[Math.min(n._depth, 3)];
  n._w = [NODE_W.root, NODE_W.aspect, NODE_W.topic, NODE_W.paper][Math.min(n._depth,3)];
  n._h = [NODE_H.root, NODE_H.aspect, NODE_H.topic, NODE_H.paper][Math.min(n._depth,3)];
  const kids = visibleKids(n);
  n._vis = kids;
  if (kids.length === 0){
    n._y = cursorY;
    cursorY += n._h + GAP_Y;
    return n._y + n._h / 2;
  }
  const centers = kids.map(k => layout(k));
  n._y = (centers[0] + centers[centers.length-1]) / 2 - n._h / 2;
  return n._y + n._h / 2;
}

// ---------- 绘制 ----------
const svg = document.getElementById('svg');
const viewport = document.getElementById('viewport');
const gEdges = document.getElementById('edges');
const gNodes = document.getElementById('nodes');
const NS = 'http://www.w3.org/2000/svg';

let selected = null;

function esc(s){
  return String(s == null ? '' : s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function truncate(s, n){
  s = String(s || '');
  return s.length > n ? s.slice(0, n) + '…' : s;
}

// 按像素宽度裁剪：中英文混排时按字符数截断会溢出节点框
function fitText(s, avail, fs){
  s = String(s || '');
  let w = 0, out = '';
  for (const ch of s){
    const cw = /[\u4e00-\u9fa5\uff00-\uffef]/.test(ch) ? fs : fs * 0.56;
    if (w + cw > avail) return out + '…';
    w += cw;
    out += ch;
  }
  return out;
}

function nodeStyle(n){
  if (n._isPaper) return {fill:'#f4f7fc', stroke:'#dde4f0', dash:'2 3', color:'#5a6b85', weight:'400'};
  switch (n._depth){
    case 0: return {fill:'#1f2937', stroke:'#1f2937', color:'#ffffff', weight:'650'};
    case 1: {
      const c = PALETTE[(n._idx||0) % PALETTE.length];
      return {fill:'#edf3ff', stroke:'#c9dbff', color:'#1c3d7a', weight:'650', accent:c};
    }
    case 2: return {fill:'#ffffff', stroke:'#d8dfea', color:'#2b3543', weight:'550'};
    default: return {fill:'#f4f7fc', stroke:'#dde4f0', color:'#5a6b85', weight:'400'};
  }
}

function draw(){
  cursorY = PAD;
  layout(DATA.root);

  gEdges.innerHTML = '';
  gNodes.innerHTML = '';

  // 连线
  (function drawEdges(n){
    n._vis.forEach(k => {
      const x1 = n._x + n._w, y1 = n._y + n._h/2;
      const x2 = k._x,         y2 = k._y + k._h/2;
      const mx = (x1 + x2) / 2;
      const p = document.createElementNS(NS, 'path');
      p.setAttribute('class', 'edge');
      p.setAttribute('d', `M${x1},${y1} C${mx},${y1} ${mx},${y2} ${x2},${y2}`);
      if (k._isPaper) p.setAttribute('stroke-dasharray', '3 3');
      gEdges.appendChild(p);
      drawEdges(k);
    });
  })(DATA.root);

  // 节点
  let maxX = 0, maxY = 0;
  (function drawNodes(n){
    const s = nodeStyle(n);
    const g = document.createElementNS(NS, 'g');
    g.setAttribute('class', 'node' + (selected === n._id ? ' sel' : ''));
    g.setAttribute('transform', `translate(${n._x},${n._y})`);
    g.dataset.id = n._id;

    const r = document.createElementNS(NS, 'rect');
    r.setAttribute('width', n._w); r.setAttribute('height', n._h);
    r.setAttribute('rx', n._isPaper ? 7 : 9);
    r.setAttribute('fill', s.fill); r.setAttribute('stroke', s.stroke);
    r.setAttribute('stroke-width', 1.2);
    if (s.dash) r.setAttribute('stroke-dasharray', s.dash);
    g.appendChild(r);

    if (n._depth === 1){
      const bar = document.createElementNS(NS, 'rect');
      bar.setAttribute('width', 3.5); bar.setAttribute('height', n._h - 16);
      bar.setAttribute('x', 0); bar.setAttribute('y', 8); bar.setAttribute('rx', 2);
      bar.setAttribute('fill', s.accent || '#2f6fed');
      g.appendChild(bar);
    }

    const label = document.createElementNS(NS, 'text');
    const fs = n._depth === 0 ? 13.5 : (n._isPaper ? 11 : 12.2);
    const startX = n._depth === 1 ? 14 : 12;
    const badgeN = n._isPaper ? 0 : (n._depth <= 2 ? n._total : 0);
    const rightPad = (badgeN > 0 ? 40 : 20);
    label.setAttribute('x', startX);
    label.setAttribute('y', n._h/2 + 4.5);
    label.setAttribute('fill', s.color);
    label.setAttribute('font-size', fs);
    label.setAttribute('font-weight', s.weight);
    label.textContent = fitText(n.label, n._w - startX - rightPad, fs);
    g.appendChild(label);

    // 文献数徽标
    if (badgeN > 0){
      const bw = 22, bh = 16;
      const bx = n._w - bw - 9, by = (n._h - bh)/2;
      const b = document.createElementNS(NS, 'rect');
      b.setAttribute('x', bx); b.setAttribute('y', by);
      b.setAttribute('width', bw); b.setAttribute('height', bh);
      b.setAttribute('rx', 8);
      b.setAttribute('fill', n._depth === 0 ? 'rgba(255,255,255,.18)' :
        (n._paperOpen ? '#2f6fed' : '#eef2f9'));
      g.appendChild(b);

      const t = document.createElementNS(NS, 'text');
      t.setAttribute('class', 'badge-txt');
      t.setAttribute('x', bx + bw/2); t.setAttribute('y', by + 11.5);
      t.setAttribute('text-anchor', 'middle');
      t.setAttribute('fill', n._depth === 0 ? '#fff' : (n._paperOpen ? '#fff' : '#5b6b86'));
      t.textContent = badgeN;
      g.appendChild(t);
    }

    // 折叠标记
    if (n._kids.length || n._papers.length){
      const chev = document.createElementNS(NS, 'text');
      const open = n._expanded || n._paperOpen;
      chev.setAttribute('x', n._w - (badgeN ? 36 : 16));
      chev.setAttribute('y', n._h/2 + 4);
      chev.setAttribute('font-size', 9);
      chev.setAttribute('fill', n._depth === 0 ? 'rgba(255,255,255,.6)' : '#9aa5b6');
      chev.textContent = (n._expanded || n._paperOpen) ? '▾' : '▸';
      g.appendChild(chev);
    }

    g.addEventListener('click', e => { e.stopPropagation(); onNodeClick(n); });
    gNodes.appendChild(g);

    maxX = Math.max(maxX, n._x + n._w);
    maxY = Math.max(maxY, n._y + n._h);
    n._vis.forEach(drawNodes);
  })(DATA.root);

  svg.setAttribute('data-w', maxX + PAD);
  svg.setAttribute('data-h', maxY + PAD);
}

// ---------- 交互 ----------
let scale = 1, tx = 0, ty = 0;

function applyTransform(){
  viewport.setAttribute('transform', `translate(${tx},${ty}) scale(${scale})`);
}

function fit(){
  const w = +svg.getAttribute('data-w'), h = +svg.getAttribute('data-h');
  const rect = svg.getBoundingClientRect();
  scale = Math.min(rect.width / w, rect.height / h, 1.05);
  scale = Math.max(scale, 0.25);
  tx = (rect.width - w * scale) / 2;
  ty = (rect.height - h * scale) / 2;
  applyTransform();
}

function onNodeClick(n){
  if (n._isPaper){ selected = n._id; draw(); showPaper(n.paper); return; }

  const hasKids = n._kids.length > 0;
  const hasPapers = n._papers.length > 0;

  // 第三层（检索方向）：点击展开/收起其文献
  if (n._depth >= 2 && hasPapers){
    n._paperOpen = !n._paperOpen;
    n._expanded = n._paperOpen;
  } else if (hasKids){
    n._expanded = !n._expanded;
  }
  selected = n._id;
  draw();
  showNode(n);
}

function showNode(n){
  document.getElementById('side-kind').textContent =
    ['研究主题','研究维度','检索方向'][n._depth] || '节点';
  document.getElementById('side-title').textContent = n.label;
  document.getElementById('side-note').textContent = n.note || '';
  const q = document.getElementById('side-query');
  q.innerHTML = n.query ? `检索式 <code>${esc(n.query)}</code>` : '';

  const papers = [];
  (function collect(x){
    (x._papers || []).forEach(p => papers.push(p));
    if (n._depth <= 1) (x.children || []).forEach(collect);
  })(n);

  document.getElementById('side-count').textContent = papers.length ? papers.length + ' 篇' : '';
  const body = document.getElementById('side-body');
  body.innerHTML = papers.length ? papers.map(paperHTML).join('')
    : `<div class="empty">这个节点暂无文献。<br>可以点击上级维度查看汇总，或换一个检索式重新展开。</div>`;
}

function showPaper(p){
  document.getElementById('side-kind').textContent = '文献';
  document.getElementById('side-title').textContent = p.title;
  document.getElementById('side-note').textContent =
    [p.authors && p.authors.join(', '), p.venue, p.year].filter(Boolean).join(' · ');
  document.getElementById('side-query').innerHTML = p.doi
    ? `DOI <code>${esc(p.doi)}</code>` : '';
  document.getElementById('side-count').textContent = '';
  document.getElementById('side-body').innerHTML =
    `<div class="paper">${paperHTML(p)}</div>`;
}

function paperHTML(p){
  const meta = [
    (p.authors || []).slice(0, 3).join(', ') +
      ((p.authors || []).length > 3 ? ' 等' : ''),
    p.venue, p.year, p.source
  ].filter(Boolean).join(' · ');
  return `<div class="paper">
    <a href="${esc(p.url)}" target="_blank" rel="noopener">${esc(p.title)}</a>
    <div class="meta">${esc(meta)}</div>
    ${p.abstract ? `<div class="abs">${esc(p.abstract)}</div>` : ''}
  </div>`;
}

// 拖拽
const wrap = document.getElementById('wrap');
let dragging = false, sx = 0, sy = 0, stx = 0, sty = 0;
wrap.addEventListener('mousedown', e => {
  if (e.target.closest('.topbar') || e.target.closest('.legend')) return;
  dragging = true; wrap.classList.add('dragging');
  sx = e.clientX; sy = e.clientY; stx = tx; sty = ty;
});
window.addEventListener('mousemove', e => {
  if (!dragging) return;
  tx = stx + (e.clientX - sx);
  ty = sty + (e.clientY - sy);
  applyTransform();
});
window.addEventListener('mouseup', () => { dragging = false; wrap.classList.remove('dragging'); });

// 缩放
wrap.addEventListener('wheel', e => {
  if (e.target.closest('.topbar') || e.target.closest('.legend')) return;
  e.preventDefault();
  const rect = svg.getBoundingClientRect();
  const mx = e.clientX - rect.left, my = e.clientY - rect.top;
  const k = e.deltaY < 0 ? 1.1 : 1 / 1.1;
  const ns = Math.min(Math.max(scale * k, 0.2), 2.6);
  tx = mx - (mx - tx) * (ns / scale);
  ty = my - (my - ty) * (ns / scale);
  scale = ns;
  applyTransform();
}, {passive: false});

// 按钮
document.getElementById('fit').onclick = fit;
document.getElementById('expand-all').onclick = () => {
  allNodes.forEach(n => { if (n._depth <= 2) { n._expanded = true; } });
  draw();
};
document.getElementById('collapse-all').onclick = () => {
  allNodes.forEach(n => { n._expanded = n._depth === 0; n._paperOpen = false; });
  draw(); fit();
};

// 搜索高亮
const qInput = document.getElementById('q');
qInput.addEventListener('input', () => {
  const kw = qInput.value.trim().toLowerCase();
  document.querySelectorAll('.node').forEach(g => {
    g.style.opacity = 1;
    if (!kw) return;
    const n = allNodes.find(x => x._id === g.dataset.id);
    if (!n) return;                       // 文献叶子节点不参与搜索高亮
    const hay = (n.label + ' ' + (n.query || '')).toLowerCase();
    const inPaper = n ? (n._papers||[]).some(p =>
      (p.title||'').toLowerCase().includes(kw)) : false;
    g.style.opacity = (hay.includes(kw) || inPaper) ? 1 : 0.16;
  });
});

// 启动
document.getElementById('stats').textContent =
  `${DATA.stats.total_papers} 篇文献 · ${DATA.stats.total_topics} 个检索方向`;
draw();
fit();
window.addEventListener('resize', () => { draw(); fit(); });
</script>
</body>
</html>
"""


def to_html(litmap: LiteratureMap) -> str:
    """生成自包含的交互式思维导图"""
    data = litmap.to_dict()
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return (
        _HTML_TEMPLATE
        .replace("__TITLE__", html.escape(f"文献地图 · {litmap.topic}"))
        .replace("__TOPIC__", html.escape(litmap.topic))
        .replace("__GEN__", html.escape(data["generated_at"]))
        .replace("__DATA__", payload)
    )


def to_json(litmap: LiteratureMap) -> str:
    return json.dumps(litmap.to_dict(), ensure_ascii=False, indent=2)
