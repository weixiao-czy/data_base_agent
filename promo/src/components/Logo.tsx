import React from "react";

export const Logo: React.FC<{ size: number; color?: string }> = ({ size, color }) => {
  const c = color ?? "#141416";
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      style={{ display: "block" }}
    >
      <g stroke={c} strokeLinecap="round" strokeLinejoin="round">
        <path d="M36 40 C29 34 19 32 10 35 L10 72 C19 69 29 71 36 77" strokeWidth="5" />
        <path d="M36 40 C43 34 53 32 62 35 L62 72 C53 69 43 71 36 77" strokeWidth="5" />
        <path d="M36 40 L36 77" strokeWidth="5" />
        <circle cx="76" cy="32" r="14" strokeWidth="6" />
        <path d="M86 42 L94 50" strokeWidth="7" />
      </g>
    </svg>
  );
};
