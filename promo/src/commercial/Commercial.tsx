import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { Logo } from "../components/Logo";
import film from "../film.json";

import { C, lerp, pop, place, mono, Eyebrow, Rise, Pill, Texture } from "./design";
import { TreeEntry, TreeGrowth, TreeExplore } from "./TreeScenes";

function Hook({ f }: { f: number }) {
  const tags = ["大模型", "研究方向？", "关键词？", "文献综述", "从哪里开始", "信息检索"];
  const positions = [[1090, 220], [1430, 340], [1040, 510], [1460, 690], [1090, 800], [1400, 100]];
  const collapse = lerp(f, 130, 176);
  return <>
    <Texture f={f} />
    <div style={place(115, 220)}>
      <Rise f={f}><Eyebrow>EVERY DISCOVERY STARTS WITH A QUESTION</Eyebrow></Rise>
      <Rise f={f} at={8}><h1 style={{ fontSize: 112, lineHeight: 1.27, margin: "40px 0 24px", letterSpacing: -5 }}>有了想法。<br /><span style={{ color: C.lime }}>然后，搜什么？</span></h1></Rise>
      <Rise f={f} at={35}><p style={{ fontSize: 31, color: "#B6C3B9" }}>让研究兴趣，找到清晰的起点。</p></Rise>
    </div>
    {tags.map((tag, i) => {
      const p = pop(f, 10 + i * 7);
      const x = positions[i][0] + (1350 - positions[i][0]) * collapse;
      const y = positions[i][1] + (480 - positions[i][1]) * collapse;
      return <div key={tag} style={{ ...place(x, y), padding: "26px 32px", background: i === 2 ? C.orange : "#243329", color: i === 2 ? C.ink : C.paper, border: "1px solid #B9D6AE33", borderRadius: 20, fontSize: 34, opacity: Math.min(1, p) * (1 - collapse), transform: `translateY(${(1 - p) * 110 + Math.sin(f / 26 + i) * 14}px) rotate(${(i % 2 ? 7 : -8) * (1 - collapse)}deg) scale(${1 - collapse * .65})` }}>{tag}</div>;
    })}
    <div style={{ ...place(1260, 410), opacity: collapse, transform: `scale(${.7 + collapse * .3})` }}><Logo size={200} color={C.lime} /></div>
    <div style={{ ...place(115, 904), ...mono, fontSize: 20, color: C.muted }}>LESS GUESSING. MORE DISCOVERY.</div>
  </>;
}

function Reveal({ f }: { f: number }) {
  return <>
    <Texture f={f} light />
    <div style={{ ...place(1240, 170), width: 540, height: 540, transform: `rotate(${f * .17 - 20}deg)` }}>
      {[0, 1, 2].map(i => <div key={i} style={{ position: "absolute", inset: i * 65, border: `${i === 1 ? 42 : 2}px solid ${i === 1 ? C.ink : "#738664"}`, borderRadius: i === 2 ? "50%" : "32%", transform: `rotate(${i * 30}deg)` }} />)}
      <div style={{ ...place(175, 175), transform: `rotate(${20 - f * .17}deg)` }}><Logo size={190} /></div>
    </div>
    <div style={place(115, 205)}>
      <Rise f={f}><Eyebrow dark>MEET YOUR RESEARCH COMPANION</Eyebrow></Rise>
      <Rise f={f} at={8}><h1 style={{ fontSize: 94, lineHeight: 1.28, margin: "35px 0 26px", letterSpacing: -4 }}>文献检索<br />需求翻译 Agent<span style={{ color: "#66923B" }}>。</span></h1></Rise>
      <Rise f={f} at={30}><p style={{ fontSize: 32, color: "#536257" }}>把「我想研究」变成「这样检索」。</p></Rise>
    </div>
    <div style={{ ...place(115, 790), display: "flex", gap: 22 }}>
      {["01  对话澄清", "02  生成计划", "03  检索与文献地图"].map((s, i) => <Rise key={s} f={f} at={45 + i * 15}><div style={{ borderTop: "2px solid #111916", padding: "26px 0", width: 420, fontSize: 30 }}>{s}<span style={{ float: "right" }}>↗</span></div></Rise>)}
    </div>
  </>;
}

const WindowBar = ({ label }: { label: string }) => <div style={{ height: 64, display: "flex", alignItems: "center", gap: 9, borderBottom: "1px solid #17241915", padding: "0 25px", background: "#F8F9F3" }}>
  {["#FF997E", "#E4D99A", "#B5CE97"].map(c => <span key={c} style={{ width: 12, height: 12, borderRadius: 12, background: c }} />)}
  <span style={{ marginLeft: 25, fontSize: 18, color: "#657265" }}>{label}</span>
  <span style={{ marginLeft: "auto", fontSize: 16, color: "#657265" }}>功能演示</span>
</div>;

function Conversation({ f }: { f: number }) {
  const messages = [
    { at: 15, user: true, text: "我想研究大模型辅助文献检索。" },
    { at: 65, user: false, text: "你更关注检索方法，还是使用体验？" },
    { at: 120, user: true, text: "检索方法。" },
    { at: 175, user: false, text: "先围绕查询扩展与检索增强，构建关键词。" },
  ];
  return <>
    <Texture f={f} light />
    <div style={place(115, 210)}>
      <Eyebrow dark>01 / CLARIFY</Eyebrow>
      <Rise f={f} at={5}><h1 style={{ fontSize: 86, lineHeight: 1.3, margin: "35px 0" }}>先厘清。<br />再向前。</h1></Rise>
      <Rise f={f} at={35}><p style={{ fontSize: 30, lineHeight: 1.8, color: "#536257" }}>先给假设，你来修正。<br />点选方向，也能自由补充。</p></Rise>
      <Rise f={f} at={60}><div style={{ display: "flex", alignItems: "baseline", gap: 16, marginTop: 35 }}><span style={{ fontSize: 110, fontWeight: 700, letterSpacing: -7 }}>10</span><span style={{ fontSize: 28 }}>轮以内 · 随时可跳过</span></div></Rise>
    </div>
    <div style={{ ...place(790, 172), width: 1010, height: 730, borderRadius: 24, overflow: "hidden", background: "#FFF", boxShadow: "0 45px 80px #14291C20", transform: `perspective(1800px) rotateY(${-3 + lerp(f, 0, 240) * 4}deg) translateY(${(1 - pop(f)) * 90}px)` }}>
      <WindowBar label="文献检索 Agent / 新的研究" />
      <div style={{ padding: "30px 34px" }}>
        {messages.map((m, i) => <Rise key={m.at} f={f} at={m.at} style={{ display: "flex", justifyContent: m.user ? "flex-end" : "flex-start", marginBottom: 24 }}>
          <div style={{ maxWidth: "91%", padding: "22px 27px", borderRadius: m.user ? "20px 20px 4px 20px" : "20px 20px 20px 4px", background: m.user ? C.ink : "#F0F3EB", color: m.user ? C.paper : C.ink, fontSize: 26, lineHeight: 1.55 }}>
            {!m.user && <div style={{ ...mono, fontSize: 15, color: "#63824E", marginBottom: 8 }}>AGENT / {i === 1 ? "理解意图" : "确认方向"}</div>}{m.text}
          </div>
        </Rise>)}
        {f >= 78 && f < 120 && <div style={{ position: "absolute", top: 355, left: 34, right: 34, padding: 20, background: "#FFF", display: "flex", gap: 12, borderRadius: 16, boxShadow: "0 10px 30px #14291C15" }}>
          {["A  检索方法", "B  使用体验", "其他…"].map((label, i) => <div key={label} style={{ padding: "15px 23px", fontSize: 23, borderRadius: 12, border: "1px solid #D9E1D2", background: i === 0 && f >= 103 ? C.lime : "#F3F5EF", transform: `scale(${i === 0 && f >= 103 && f < 110 ? .96 : 1})` }}>{label}{i === 0 && f >= 103 ? " ✓" : ""}</div>)}
        </div>}
      </div>
      <div style={{ position: "absolute", bottom: 24, left: 34, right: 34, border: "1px solid #D9E1D2", borderRadius: 14, padding: "17px 22px", fontSize: 22, color: "#7B8577", display: "flex", justifyContent: "space-between" }}><span>继续描述你的研究想法…</span><span>↑</span></div>
    </div>
  </>;
}

function Plan({ f }: { f: number }) {
  const rows = [
    ["研究问题", "大模型如何辅助文献检索？"],
    ["关键词组合", "LLM · query expansion · literature retrieval"],
    ["查询建议", '(LLM OR "large language model")\nAND ("query expansion" OR retrieval)'],
    ["不确定性标注", "是否纳入多模态模型？待确认。"],
  ];
  return <>
    <Texture f={f} />
    <div style={place(115, 210)}>
      <Eyebrow>02 / TRANSLATE</Eyebrow>
      <Rise f={f} at={5}><h1 style={{ fontSize: 86, lineHeight: 1.3, margin: "35px 0" }}>一个想法。<br /><span style={{ color: C.lime }}>一份检索计划。</span></h1></Rise>
      <Rise f={f} at={30}><p style={{ color: "#B6C3B9", fontSize: 30, lineHeight: 1.8 }}>关键词、检索式、待确认的问题。<br />下一步，清清楚楚。</p></Rise>
      <Rise f={f} at={130}><Pill filled>需求翻译卡 ↗</Pill></Rise>
    </div>
    {[2, 1].map(i => <div key={i} style={{ ...place(900 + i * 26, 170 + i * 23), width: 830, height: 712, border: "1px solid #A8C28E55", borderRadius: 22, background: "#25372A", transform: `rotate(${i * 3}deg)` }} />)}
    <div style={{ ...place(880, 150), width: 830, minHeight: 712, padding: "38px 42px", background: C.paper, color: C.ink, borderRadius: 22, boxShadow: "0 40px 90px #0005", transform: `perspective(1800px) rotateY(${lerp(f, 0, 260, -7, 1)}deg) rotateZ(${lerp(f, 0, 100, -3, 0)}deg) translateY(${(1 - pop(f)) * 130}px)` }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}><span style={{ fontSize: 38, fontWeight: 700 }}>需求翻译卡</span><span style={{ ...mono, fontSize: 17 }}>RESEARCH PLAN / 01</span></div>
      {rows.map(([label, text], i) => <Rise key={label} f={f} at={25 + i * 40}>
        <div style={{ padding: "23px 0", borderTop: "1px solid #CDD3C6" }}>
          <div style={{ color: "#61754F", fontSize: 20, marginBottom: 10 }}>{`0${i + 1}`} / {label}</div>
          <div style={{ whiteSpace: "pre-line", fontFamily: i === 2 ? "Consolas, monospace" : "inherit", fontSize: i === 2 ? 23 : 26, lineHeight: 1.6 }}>{text}</div>
        </div>
      </Rise>)}
      <div style={{ fontSize: 16, color: "#6A7667", marginTop: 5 }}>示例研究主题 · 计划可在检索前确认与调整</div>
    </div>
  </>;
}

function Network({ f }: { f: number }) {
  const nodes = [{ x: 1130, y: 260, label: "SciMaster", sub: "优先检索 · 需配置" }, { x: 1430, y: 510, label: "Crossref", sub: "公开学术接口" }, { x: 1110, y: 780, label: "arXiv", sub: "开放预印本" }];
  return <>
    <Texture f={f} />
    <div style={place(115, 210)}>
      <Eyebrow>03 / DISCOVER</Eyebrow>
      <Rise f={f} at={5}><h1 style={{ fontSize: 86, lineHeight: 1.3, margin: "35px 0" }}>让好问题，<br /><span style={{ color: C.lime }}>遇见真实文献。</span></h1></Rise>
      <Rise f={f} at={35}><p style={{ fontSize: 30, color: "#B6C3B9", lineHeight: 1.8 }}>从结构化计划出发。<br />连接公开学术数据源。</p></Rise>
      <Rise f={f} at={135}><div style={{ marginTop: 40, maxWidth: 650, borderLeft: `3px solid ${C.orange}`, paddingLeft: 23, fontSize: 25, lineHeight: 1.7 }}>SciMaster 不可用时<br /><span style={{ color: C.muted }}>自动切换至 Crossref / arXiv</span></div></Rise>
    </div>
    <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
      {nodes.map((n, i) => <g key={n.label} opacity={lerp(f, 15 + i * 25, 40 + i * 25)}>
        <path d={`M 960 540 Q 1000 ${n.y} ${n.x + 140} ${n.y}`} stroke="#D6F78A35" strokeWidth="2" fill="none" />
        <path d={`M 960 540 Q 1000 ${n.y} ${n.x + 140} ${n.y}`} stroke={i === 0 ? C.orange : C.lime} strokeWidth="4" fill="none" strokeDasharray="16 220" strokeDashoffset={-f * 5 - i * 70} />
      </g>)}
      {[0, 1, 2].map(i => <circle key={i} cx="960" cy="540" r={65 + ((f * 1.5 + i * 60) % 180)} fill="none" stroke="#D6F78A" opacity={.22 * (1 - ((f * 1.5 + i * 60) % 180) / 180)} />)}
    </svg>
    <div style={{ ...place(900, 480), background: C.lime, borderRadius: 28, padding: 20 }}><Logo size={80} /></div>
    {nodes.map((n, i) => <div key={n.label} style={{ ...place(n.x, n.y - 65), width: 310, padding: "27px 30px", border: "1px solid #D0F0BA55", borderRadius: 24, background: "#26372E", transform: `translateY(${(1 - pop(f, 20 + i * 25)) * 75 + Math.sin(f / 40 + i) * 8}px)`, opacity: pop(f, 20 + i * 25) }}><div style={{ fontSize: 37, fontWeight: 600 }}>{n.label}<span style={{ color: i ? C.lime : C.orange, float: "right" }}>↗</span></div><div style={{ fontSize: 21, color: "#B6C3B9", marginTop: 12 }}>{n.sub}</div></div>)}
  </>;
}

function Workspace({ f }: { f: number }) {
  const focus = lerp(f, 65, 105);
  const exported = pop(f, 165);
  return <>
    <Texture f={f} light />
    <div style={place(115, 140)}><Eyebrow dark>05 / KEEP MOVING</Eyebrow><Rise f={f}><h1 style={{ fontSize: 64, letterSpacing: -2, margin: "22px 0" }}>从领域地图，回到你的研究。</h1></Rise></div>
    <div style={{ ...place(220, 335), width: 1480, height: 590, background: "#FFF", borderRadius: 22, overflow: "hidden", boxShadow: "0 30px 80px #23371C22", transform: `perspective(2200px) rotateX(${lerp(f, 0, 160, 5, 0)}deg) scale(${1 + focus * .018})` }}>
      <WindowBar label="文献检索 Agent / 研究工作台" />
      <div style={{ display: "flex", height: 526 }}>
        <div style={{ width: 260, flexShrink: 0, background: "#EDF1E6", padding: "30px 26px" }}><Logo size={56} /><div style={{ fontSize: 23, fontWeight: 600, margin: "22px 0" }}>我的研究</div>{["大模型与文献检索", "新的研究对话", "历史记录"].map((t, i) => <div key={t} style={{ fontSize: 20, padding: "15px 11px", marginBottom: 8, borderRadius: 10, background: i ? "transparent" : "#DCE5D0", color: i ? "#6A7763" : C.ink }}>{t}</div>)}</div>
        <div style={{ padding: "30px 36px", flex: 1 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: 27, marginBottom: 25 }}><strong>检索结果</strong><span style={{ padding: "12px 22px", background: C.ink, color: C.paper, borderRadius: 10, fontSize: 21 }}>导出结果 ↗</span></div>
          <div style={{ padding: "25px 28px", border: `2px solid ${focus > .5 ? "#91B269" : "#E2E7DA"}`, borderRadius: 16, boxShadow: `0 8px 24px #91B269${Math.round(focus * 25).toString(16).padStart(2, "0")}` }}>
            <div style={{ ...mono, fontSize: 16, color: "#637457", marginBottom: 12 }}>示例结果 / 元数据与内容以实际检索为准</div>
            <div style={{ fontSize: 29, fontWeight: 600 }}>大模型辅助文献检索：方法与应用</div>
            <div style={{ fontSize: 21, color: "#65735F", marginTop: 14 }}>论文元数据　 /　 来源链接　 /　 DOI</div>
            <div style={{ fontSize: 24, marginTop: 23, lineHeight: 1.6 }}><span style={{ background: `linear-gradient(90deg, #D6F78A ${lerp(f, 100, 155) * 100}%, transparent 0)` }}>浏览摘要，判断研究方向是否相关。</span></div>
          </div>
          <div style={{ display: "flex", gap: 14, marginTop: 24 }}>{["摘要", "原文链接", "BibTeX", "本地导出"].map((t, i) => <Rise key={t} f={f} at={35 + i * 25}><Pill>{t}</Pill></Rise>)}</div>
        </div>
      </div>
    </div>
    <div style={{ ...place(1370, 855), padding: "22px 28px", color: C.paper, background: C.ink, borderRadius: 15, fontSize: 23, boxShadow: "0 18px 45px #14291C33", opacity: exported, transform: `translateY(${(1 - exported) * 40}px)` }}>✓ 线索已保存，继续探索</div>
    <Rise f={f} at={75} style={{ ...place(220, 972), fontSize: 24, color: "#526847" }}>地图自动保存：HTML 交互导图　 /　 Markdown 大纲　 /　 JSON 结构数据</Rise>
  </>;
}

function Brand({ f }: { f: number }) {
  const orbit = Math.min(f, 150);
  return <>
    <Texture f={f} />
    <div style={{ ...place(400, 120), width: 1120, height: 720, border: "1px solid #C6ED9720", borderRadius: "50%", transform: `rotate(${-18 + orbit * .05}deg)` }} />
    <Rise f={f} style={{ ...place(860, 155) }}><div style={{ width: 200, height: 170, display: "flex", justifyContent: "center", alignItems: "center" }}><Logo size={145} color={C.lime} /></div></Rise>
    <div style={{ position: "absolute", top: 350, left: 0, right: 0, textAlign: "center" }}>
      <Rise f={f} at={12}><h1 style={{ fontSize: 108, margin: 0, letterSpacing: -4 }}>把时间<span style={{ color: C.lime }}>还给研究。</span></h1></Rise>
      <Rise f={f} at={30}><p style={{ fontSize: 34, color: "#BAC9BC", marginTop: 27 }}>文献检索需求翻译 Agent</p></Rise>
      <Rise f={f} at={50}><div style={{ marginTop: 40 }}><span style={{ display: "inline-block", background: C.lime, color: C.ink, padding: "23px 42px", fontSize: 28, borderRadius: 50 }}>从你的下一个问题开始 ↗</span></div></Rise>
      <Rise f={f} at={65}><div style={{ ...mono, color: "#C6D3C6", fontSize: 25, marginTop: 36 }}>github.com/weixiao-czy/data_base_agent</div></Rise>
      <Rise f={f} at={75}><div style={{ fontSize: 20, color: "#92A48F", marginTop: 28 }}>开源项目 · 内嵌文献地图 · 桌面 GUI / 命令行</div></Rise>
    </div>
  </>;
}

const scenes: Record<string, React.FC<{ f: number }>> = { hook: Hook, reveal: Reveal, conversation: Conversation, plan: Plan, network: Network, treeEntry: TreeEntry, treeGrowth: TreeGrowth, treeExplore: TreeExplore, workspace: Workspace, brand: Brand };

export const CommercialScene: React.FC<{ id: string; duration: number; index: number }> = ({ id, duration, index }) => {
  const f = useCurrentFrame();
  const light = ["reveal", "conversation", "treeEntry", "treeExplore", "workspace"].includes(id);
  const Scene = scenes[id];
  // Directional wipe on the final half beat; the actual cut lands on the downbeat.
  const wipe = lerp(f, duration - 9, duration);
  return <AbsoluteFill style={{ background: light ? C.paper : C.ink, color: light ? C.ink : C.paper, overflow: "hidden", fontFamily: '"Microsoft YaHei", "PingFang SC", "Noto Sans SC", Arial, sans-serif' }}>
    <Scene f={f} />
    <div style={{ ...place(115, 64), display: "flex", alignItems: "center", gap: 12, color: light ? C.ink : C.paper }}><Logo size={36} color={light ? C.ink : C.lime} /><span style={{ ...mono, fontSize: 18 }}>DATA BASE AGENT</span></div>
    <div style={{ position: "absolute", right: 115, top: 76, ...mono, color: light ? "#6F7D65" : "#A6B79B", fontSize: 17 }}>{String(index + 1).padStart(2, "0")} / {String(film.scenes.length).padStart(2, "0")}</div>
    {id !== "brand" && <div style={{ position: "absolute", left: 0, bottom: 0, width: "100%", height: 1080 * wipe, background: index % 2 ? C.orange : C.lime, transform: `skewY(${-5 * (1 - wipe)}deg)`, transformOrigin: "bottom left" }} />}
  </AbsoluteFill>;
};

export const FilmOverlay: React.FC = () => {
  const f = useCurrentFrame();
  return <div style={{ position: "absolute", bottom: 0, left: 0, height: 4, width: `${100 * f / (film.duration * film.fps - 1)}%`, background: C.orange, opacity: .8 }} />;
};
