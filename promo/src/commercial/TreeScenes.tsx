import React from "react";
import { interpolate } from "remotion";
import { Logo } from "../components/Logo";
import { C, Eyebrow, Rise, Texture, lerp, place } from "./design";
import demo from "./tree-demo.json";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const cue = demo.cues;
const paper = demo.selectedPaper;
const Cursor: React.FC<{ x: number; y: number; click?: number }> = ({ x, y, click = 0 }) => (
  <svg width={52} height={62} viewBox="-10 -10 52 62" style={{ ...place(x, y), pointerEvents: "none", overflow: "visible" }}>
    {click > 0 && <circle cx="3" cy="4" r={12 + click * 26} fill="none" stroke={C.orange} strokeWidth={3} opacity={1 - click} />}
    <path d="M0 0 L0 31 L8 23 L15 39 L22 35 L15 21 L28 21 Z" fill="#17231B" stroke="#FFF" strokeWidth={2.5} />
  </svg>
);
const button: React.CSSProperties = { border: "1px solid #DDE2D8", borderRadius: 9, padding: "9px 15px", fontSize: 20, background: "#FFF", whiteSpace: "nowrap" };

// Shared app shell deliberately preserves the history sidebar. The real GUI uses
// QStackedWidget: the map replaces the chat page, not a second chat-side pane.
const AppShell: React.FC<{ children: React.ReactNode; map?: boolean; returning?: boolean }> = ({ children, map, returning }) => (
  <div style={{ ...place(115, 295), width: 1690, height: 650, background: "#FFF", color: C.ink, border: "1px solid #D9DFD4", borderRadius: 22, overflow: "hidden", boxShadow: "0 30px 75px #101D252A" }}>
    <div style={{ height: 50, borderBottom: "1px solid #E4E9DE", display: "flex", alignItems: "center", padding: "0 23px", fontSize: 19, gap: 14 }}><Logo size={30} />文献检索需求翻译 Agent<span style={{ marginLeft: "auto", color: "#788170", fontSize: 17 }}>GUI 功能演示</span><span style={{ marginLeft: 24 }}>—　□　×</span></div>
    <div style={{ display: "flex", height: 600 }}>
      <div style={{ width: 210, flexShrink: 0, background: "#F1F3EC", padding: "26px 19px", borderRight: "1px solid #E4E9DE" }}>
        <div style={{ ...button, fontSize: 22, marginBottom: 28 }}>＋ 新对话</div><div style={{ color: "#798271", fontSize: 17, marginBottom: 15 }}>对话历史</div>
        <div style={{ padding: "15px 10px", background: "#DEE7D4", borderRadius: 10, fontSize: 20, lineHeight: 1.6 }}>大模型辅助<br />文献检索</div>
        <div style={{ fontSize: 19, color: "#7B8574", padding: "20px 10px" }}>研究笔记</div><div style={{ position: "absolute", bottom: 25, left: 29, fontSize: 19, color: "#65715E" }}>⚙ 设置</div>
      </div>
      <div style={{ flex: 1, minWidth: 0, position: "relative" }}>
        <div style={{ height: 57, display: "flex", alignItems: "center", gap: 12, padding: "0 22px", borderBottom: "1px solid #E3E7DF" }}><strong style={{ fontSize: 23 }}>{map ? "◈ 文献地图" : "研究对话"}</strong><span style={{ color: "#7C8575", fontSize: 18 }}>{map ? demo.topic : "需求翻译卡已生成"}</span><span style={{ flex: 1 }} />{map ? <><span style={button}>在浏览器打开</span><span style={{ ...button, background: returning ? C.lime : "#F2F5EC" }}>返回对话</span></> : <><span style={button}>导出结果</span><span style={button}>导出翻译卡</span></>}</div>
        {children}
      </div>
    </div>
  </div>
);

const PlanActions: React.FC<{ selected?: boolean; returned?: boolean }> = ({ selected, returned }) => <div style={{ padding: "24px 40px" }}>
  <div style={{ display: "flex", gap: 25, alignItems: "stretch" }}>
    <div style={{ width: 430, border: "1px solid #DFE4D8", borderRadius: 14, padding: "25px 28px", background: "#FAFBF7" }}><div style={{ fontSize: 30, fontWeight: 700, marginBottom: 20 }}>需求翻译卡</div><div style={{ fontSize: 21, color: "#6D7C62", marginBottom: 12 }}>研究问题</div><div style={{ fontSize: 24, lineHeight: 1.6 }}>大模型如何辅助文献检索？</div><div style={{ fontSize: 21, color: "#6D7C62", marginTop: 24 }}>关键词 / 查询建议</div><div style={{ fontSize: 22, marginTop: 12, lineHeight: 1.8 }}>LLM · 查询扩展 · 检索增强</div></div>
    <div style={{ flex: 1 }}><div style={{ fontSize: 25, lineHeight: "34px", marginBottom: 18 }}>{returned ? "看过地图，继续推进研究。" : "这个计划看起来如何？"}</div>
      {["确认，开始检索", "需要调整（请说明）", "重新生成", "跳过检索", "以树形图查看文献结构"].map((text, i) => <div key={text} style={{ height: 56, lineHeight: "28px", padding: "13px 20px", marginBottom: 10, border: `1px solid ${i === 4 ? "#9DB784" : "#DFE4D8"}`, borderRadius: 10, background: i === 4 && selected ? C.lime : "#FAFBF7", fontSize: 23, transform: i === 4 && selected ? "scale(.99)" : undefined }}><span style={{ color: "#7B8B6C", marginRight: 17 }}>{i + 1}</span>{text}{i === 4 && <span style={{ float: "right", color: "#6A844C", fontSize: 19 }}>发散检索 + 思维导图 ↗</span>}</div>)}
    </div>
  </div>
  <div style={{ marginTop: 22, border: "1px solid #DDE3D5", padding: "13px 20px", borderRadius: 10, color: "#7B8574", fontSize: 20 }}>{returned ? "继续输入，或点选下一步操作…" : "也可以直接输入你的补充想法…"}</div>
</div>;

function TreeGraph({ f, explore = false }: { f: number; explore?: boolean }) {
  const c = cue.explore;
  const collapsed = explore && f >= c.collapse && f < c.expand;
  const searching = explore && f >= c.search;
  const selected = explore && f >= c.select;
  const zoom = explore ? lerp(f, c.zoomStart, c.zoomEnd, 1, 1.24) : 1;
  const panX = explore ? lerp(f, c.zoomStart, c.zoomEnd, 0, -180) : 0;
  const panY = explore ? lerp(f, c.zoomStart, c.zoomEnd, 0, -20) : 0;
  const growth = (at: number) => explore ? 1 : lerp(f, at, at + 18);
  const edge = (x: number, y: number, x2: number, y2: number, color: string, p: number, key?: string) => <path key={key} d={`M${x} ${y} C${(x + x2) / 2} ${y}, ${(x + x2) / 2} ${y2}, ${x2} ${y2}`} fill="none" stroke={color} strokeWidth={2.4} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} opacity={p} />;
  const node = (x: number, y: number, w: number, label: string, color: string, p: number, kind: "aspect" | "topic" | "paper", highlighted = false) => <g opacity={p} transform={`translate(${x + 25 * (1 - p)},${y - 22})`}>
    <rect width={w} height={44} rx={9} fill={highlighted ? "#D6F78A" : kind === "aspect" ? color : kind === "paper" ? "#EEF2F9" : "#FFF"} stroke={highlighted ? "#608E35" : kind === "aspect" ? color : "#CFD6E2"} strokeWidth={highlighted ? 2.7 : 1.2} />
    <text x={14} y={28} fontSize={kind === "paper" ? 19 : 22} fill={kind === "aspect" && !highlighted ? "white" : "#1F2937"}>{label}</text>
    {kind === "aspect" && <text x={w - 25} y={28} fontSize={22} fill="white">{collapsed ? "+" : "−"}</text>}
  </g>;
  return <svg viewBox="0 0 1400 500" width="100%" height="100%" style={{ display: "block" }}>
    <g transform={`translate(${panX},${panY}) scale(${zoom})`}>
      {edge(260, 250, 335, 35, "#849576", growth(0), "seed-edge")}
      {node(335, 35, 230, "种子文献", "#597444", growth(0), "aspect")}
      {!collapsed && <>{edge(565, 35, 965, 35, "#A4B397", growth(8), "seed-paper-edge")}{node(965, 35, 390, "示例：研究起点与代表性工作", "#597444", growth(8), "paper")}</>}
      {demo.dimensions.map((d, i) => {
        const y = 100 + i * 65;
        const p = growth(cue.growth.aspects + i * cue.growth.aspectStep);
        const t = growth(cue.growth.topics + i * 5);
        const leaf = growth(cue.growth.papers + i * 5);
        const match = d.id === "method";
        return <g key={d.id} opacity={searching && !match ? .24 : 1}>
          {edge(260, 250, 335, y, d.color, p)}
          {node(335, y, 230, d.label, d.color, p, "aspect")}
          {!collapsed && <>{edge(565, y, 625, y, d.color, t)}{node(625, y, 260, d.topic, d.color, t, "topic", searching && match)}
            {edge(885, y, 965, y, d.color, leaf)}{node(965, y, 390, d.paper, d.color, leaf, "paper", searching && match)}
          </>}
        </g>;
      })}
      <g><rect x={15} y={216} width={245} height={68} rx={12} fill="#1F2937" /><text x={36} y={245} fontSize={23} fill="white">大模型辅助</text><text x={36} y={272} fontSize={23} fill="white">文献检索</text></g>
      {selected && <circle cx={954} cy={165} r={7} fill={C.orange} />}
    </g>
  </svg>;
}

const MapContent: React.FC<{ f: number; explore?: boolean }> = ({ f, explore = false }) => {
  const c = cue.explore;
  const searching = explore && f >= c.search;
  const detail = explore && f >= c.select;
  const zooming = explore && f >= c.zoomStart && f < c.search;
  return <>
    <div style={{ height: 55, display: "flex", alignItems: "center", gap: 12, padding: "0 20px", background: "#F7F8FA", borderBottom: "1px solid #E3E7EE" }}>
      <span style={{ ...button, minWidth: 335, color: searching ? C.ink : "#8B95A3", borderColor: searching ? "#88A966" : "#DDE2D8" }}>{searching ? "⌕ 查询扩展" : "⌕ 搜索节点或文献标题…"}</span>
      <span style={{ ...button, background: explore && f >= c.expand && f < c.zoomStart ? C.lime : "#FFF" }}>全部展开</span>
      <span style={{ ...button, background: explore && f >= c.collapse && f < c.expand ? C.lime : "#FFF" }}>收起到维度</span><span style={button}>适应窗口</span>
      <span style={{ marginLeft: "auto", color: "#73806C", fontSize: 17 }}>研究维度 → 检索方向 → 文献</span>
    </div>
    <div style={{ display: "flex", height: 447, background: "#F7F8FA", overflow: "hidden" }}>
      <div style={{ flex: 1, minWidth: 0, position: "relative", overflow: "hidden" }}><TreeGraph f={f} explore={explore} />
        {zooming && <div style={{ position: "absolute", bottom: 12, left: 20, borderRadius: 20, padding: "8px 17px", background: "#1F2937", color: "white", fontSize: 18 }}>滚轮缩放 · 拖拽平移</div>}
      </div>
      {detail && <div style={{ width: 340, flexShrink: 0, borderLeft: "1px solid #DDE3EA", padding: "18px 22px", background: "#FFF" }}>
        <div style={{ color: "#2F6FED", fontSize: 17, lineHeight: "24px", marginBottom: 10 }}>文献详情 / 示例</div><div style={{ fontSize: 22, lineHeight: 1.4, fontWeight: 600 }}>{paper.title}</div>
        <div style={{ fontSize: 17, lineHeight: "24px", color: "#7B8591", marginTop: 12 }}>研究维度：核心方法</div><div style={{ fontSize: 17, lineHeight: "24px", color: "#7B8591", marginTop: 6 }}>检索方向：查询扩展</div>
        <div style={{ marginTop: 14, fontSize: 19, lineHeight: 1.55 }}>{paper.abstract}</div>
      </div>}
    </div>
    <div style={{ height: 41, display: "flex", alignItems: "center", padding: "0 20px", gap: 17, fontSize: 17, color: "#6D7866", borderTop: "1px solid #DFE5DA" }}><span>{demo.notice}</span><span style={{ marginLeft: "auto" }}>点击节点展开 / 折叠</span></div>
  </>;
};

export function TreeEntry({ f }: { f: number }) {
  const c = cue.entry;
  const ready = f >= c.map;
  return <><Texture f={f} light /><div style={place(115, 142)}><Eyebrow dark>04 / LITERATURE MAP</Eyebrow><Rise f={f}><h1 style={{ fontSize: 62, margin: "18px 0" }}>点一下，让文献长成一张地图。</h1></Rise></div>
    <AppShell map={ready}>{ready ? <MapContent f={12} /> : <PlanActions selected={f >= c.click} />}</AppShell>
    {f >= c.loading && !ready && <div style={{ ...place(610, 510), width: 880, padding: "38px 44px", borderRadius: 20, background: "#15251E", color: C.paper, boxShadow: "0 25px 75px #101D2550" }}><div style={{ fontSize: 32 }}>正在构建文献树形图…</div><div style={{ fontSize: 24, color: "#C2D6B3", margin: "18px 0" }}>种子文献 → 多维发散 → 逐条检索</div><div style={{ fontSize: 19, color: "#9CB08D" }}>生成过程已压缩展示，实际耗时依网络与检索规模而定。</div></div>}
    {f >= 16 && f < c.loading && <Cursor x={interpolate(f, [16, 42], [1630, 1390], clamp)} y={interpolate(f, [16, 42], [915, 770], clamp)} click={f >= c.click ? lerp(f, c.click, c.loading) : 0} />}
    <div style={{ ...place(115, 982), fontSize: 24, color: "#5B7050" }}>在应用内展开，保持研究上下文。</div>
  </>;
}

export function TreeGrowth({ f }: { f: number }) {
  return <><Texture f={f} /><div style={place(115, 140)}><Eyebrow>FROM A TOPIC TO A RESEARCH LANDSCAPE</Eyebrow><Rise f={f}><h1 style={{ fontSize: 62, margin: "18px 0" }}>六大维度。<span style={{ color: C.lime }}>下一篇，知道往哪找。</span></h1></Rise></div>
    <AppShell map><MapContent f={f} /></AppShell>
    <Rise f={f} at={205} style={{ ...place(115, 980), fontSize: 24, color: "#C2D5B7" }}>先读综述建立全局，再沿方法、评测与挑战深入。<span style={{ marginLeft: 34, color: C.lime }}>分支检索 · 全图去重</span></Rise>
  </>;
}

export function TreeExplore({ f }: { f: number }) {
  const c = cue.explore;
  const returned = f >= c.chat;
  const cursorX = interpolate(f, [0, c.collapse, c.expand, c.zoomStart, c.search, c.select - 6, c.select + 8, c.return - 12, c.return], [1090, 958, 790, 1170, 517, 1500, 1250, 1740, 1740], clamp);
  const cursorY = interpolate(f, [0, c.collapse, c.expand, c.zoomStart, c.search, c.select - 6, c.select + 8, c.return - 12, c.return], [690, 430, 430, 580, 430, 622, 627, 375, 375], clamp);
  const lastClick = [c.collapse, c.expand, c.search, c.select, c.return].filter(at => f >= at && f < at + 12).at(-1);
  return <><Texture f={f} light /><div style={place(115, 142)}><Eyebrow dark>EXPLORE / FOCUS / RETURN</Eyebrow><Rise f={f}><h1 style={{ fontSize: 62, margin: "18px 0" }}>沿着分支，<span style={{ color: "#638D3D" }}>找到研究线索。</span></h1></Rise></div>
    <AppShell map={!returned} returning={f >= c.return}>{returned ? <PlanActions returned /> : <MapContent f={f} explore />}</AppShell>
    {!returned && <Cursor x={cursorX} y={cursorY} click={lastClick === undefined ? 0 : lerp(f, lastClick, lastClick + 12)} />}
    <div style={{ ...place(115, 982), fontSize: 24, color: "#526847" }}>{f < c.zoomStart ? "展开 / 折叠，让复杂信息各归其位。" : f < c.search ? "缩放与拖拽，聚焦你关心的方向。" : f < c.select ? "搜索关键词，高亮相关节点与文献。" : f < c.return ? "点击文献查看摘要，判断是否值得深入。" : "一键返回对话，继续调整或检索。"}</div>
  </>;
}
