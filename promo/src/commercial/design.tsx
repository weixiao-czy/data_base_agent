import React from "react";
import { AbsoluteFill, interpolate, spring } from "remotion";
import film from "../film.json";

// Pure, deterministic frame-driven motion, including particles and camera moves.
export const C = { ink: "#111916", paper: "#F3F2EB", lime: "#D6F78A", orange: "#FF855F", muted: "#9FAFA6" };
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
export const lerp = (f: number, a: number, b: number, x = 0, y = 1) => interpolate(f, [a, b], [x, y], clamp);
export const pop = (f: number, at = 0) => f < at ? 0 : spring({ frame: f - at, fps: film.fps, config: { damping: 22, stiffness: 130 } });
export const place = (left: number, top: number): React.CSSProperties => ({ position: "absolute", left, top });
export const mono: React.CSSProperties = { fontFamily: '"Cascadia Code", Consolas, monospace', letterSpacing: 2 };

export const Eyebrow: React.FC<{ children: React.ReactNode; dark?: boolean }> = ({ children, dark }) => (
  <div style={{ ...mono, fontSize: 21, color: dark ? "#536257" : C.lime, display: "flex", alignItems: "center", gap: 14 }}>
    <span style={{ width: 9, height: 9, borderRadius: 9, background: "currentColor" }} />{children}
  </div>
);
export const Rise: React.FC<{ f: number; at?: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ f, at = 0, children, style }) => {
  const p = pop(f, at);
  return <div style={{ opacity: Math.min(1, p), transform: `translateY(${(1 - p) * 65}px)`, ...style }}>{children}</div>;
};
export const Pill: React.FC<{ children: React.ReactNode; filled?: boolean }> = ({ children, filled }) => (
  <span style={{ display: "inline-block", padding: "13px 23px", borderRadius: 40, border: "1px solid #83938355", background: filled ? C.lime : "transparent", color: filled ? C.ink : "inherit", fontSize: 25 }}>{children}</span>
);
export const Texture: React.FC<{ f: number; light?: boolean }> = ({ f, light }) => (
  <AbsoluteFill style={{ overflow: "hidden", pointerEvents: "none" }}>
    <div style={{ ...place(700 + Math.sin(f / 140) * 100, -400), width: 1500, height: 1500, borderRadius: "50%", background: `radial-gradient(ellipse, ${light ? "#D6E6BC66" : "#426A3A66"} 0%, transparent 65%)` }} />
    <AbsoluteFill style={{ opacity: light ? .14 : .09, backgroundImage: `radial-gradient(${light ? C.ink : C.paper} 1px, transparent 1px)`, backgroundSize: "32px 32px" }} />
    {[0, 1, 2].map(i => <div key={i} style={{ ...place(1050 - i * 180, 140 - i * 140), width: 850 + i * 360, height: 850 + i * 360, border: `1px solid ${light ? "#34533C12" : "#D6F78A10"}`, borderRadius: "50%", transform: `translateY(${Math.sin(f / 70 + i) * 20}px)` }} />)}
  </AbsoluteFill>
);
