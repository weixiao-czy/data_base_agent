import React from 'react';
import { interpolate } from 'remotion';
export const color = { ink:'#172B27', bg:'#F5F4EC', green:'#D7F58B', orange:'#FF966F', blue:'#376EF1', gray:'#64766C', line:'#DBE3D8' };
export const clamp = { extrapolateLeft:'clamp', extrapolateRight:'clamp' } as const;
export function wrap(text:string, width:number, size:number) {
  const result:string[]=[];
  for (const paragraph of text.replace(/\\n/g, '\n').split('\n')) {
    let row='', units=0;
    for (const char of paragraph) {
      const unit = /[\u0000-\u00ff]/.test(char) ? .57 : 1;
      if (units + unit > width / size && row) { result.push(row); row=''; units=0; }
      row += char; units += unit;
    }
    result.push(row);
  }
  return result;
}
export const Text:React.FC<{x:number;y:number;text:string;size?:number;width?:number;fill?:string;bold?:boolean;lineHeight?:number;anchor?:'start'|'middle'|'end';mono?:boolean}> = ({x,y,text,size=26,width=1000,fill=color.ink,bold=false,lineHeight=1.45,anchor='start',mono=false}) => <text x={x} y={y} fill={fill} fontSize={size} fontWeight={bold?700:400} textAnchor={anchor} fontFamily={mono?'Consolas, "Noto Sans Mono CJK SC", monospace':undefined}>{wrap(text,width,size).map((line,i)=><tspan key={i} x={x} dy={i?size*lineHeight:0}>{line}</tspan>)}</text>;
export const Cursor:React.FC<{x:number;y:number;f:number}> = ({x,y,f}) => {
  const travel=interpolate(f,[12,60],[1,0],clamp), clicked=f>=90&&f<106;
  return <g transform={`translate(${x+travel*70},${y+travel*40})`} opacity={f<12?0:1}>
    {clicked&&<circle r={12+(f-90)*1.5} fill="none" stroke={color.orange} strokeWidth={3} opacity={1-(f-90)/16}/>}
    <path d="M0 0 L0 27 L7 20 L14 34 L20 30 L13 18 L25 18 Z" fill={color.ink} stroke="white" strokeWidth={2}/>
  </g>;
};
export const Box:React.FC<{x:number;y:number;w:number;h:number;label?:string;size?:number;active?:boolean;f?:number;fill?:string;ink?:string;click?:boolean;radius?:number}> = ({x,y,w,h,label,size=24,active=false,f=0,fill='white',ink=color.ink,click=false,radius=12}) => <g>
  <rect x={x} y={y} width={w} height={h} rx={radius} fill={active&&f>=90?color.green:fill} stroke={active?color.orange:color.line} strokeWidth={active?3:1.5}/>
  {active&&<rect x={x-5} y={y-5} width={w+10} height={h+10} rx={radius+4} fill="none" stroke={color.orange} strokeWidth={1.5} opacity={.22+.12*Math.sin(f/12)}/>}
  {label&&<Text x={x+18} y={y+(h-size)/2+size*.8} text={label} size={size} width={w-35} fill={active&&f>=90?color.ink:ink}/>}
  {active&&click&&<Cursor x={x+w-25} y={y+h-12} f={f}/>}
</g>;
export const Frame:React.FC<{title:string;children:React.ReactNode}> = ({title,children}) => <>
  <rect width={1230} height={650} rx={22} fill="white" stroke={color.line} strokeWidth={2}/>
  <path d="M0 52H1230" stroke={color.line}/><circle cx={25} cy={26} r={6} fill={color.orange}/><circle cx={45} cy={26} r={6} fill="#E4CE82"/><circle cx={65} cy={26} r={6} fill="#96BD6A"/>
  <Text x={94} y={34} text={title} size={20} width={1000}/>{children}
</>;
export const AppBase:React.FC<{children:React.ReactNode;focus:string;f:number;status?:string}> = ({children,focus,f,status='研究对话'}) => <Frame title="文献检索需求翻译 Agent · 教学示意">
  <rect x={1} y={53} width={180} height={596} fill="#EEF2E8"/>
  <Box x={15} y={75} w={150} h={49} label="＋ 新对话" active={focus==='new'} click f={f} size={22}/>
  <Text x={22} y={170} text="对话历史" size={19} fill={color.gray}/>
  <Box x={15} y={195} w={150} h={98} fill="#DEE8CF"/><Text x={30} y={232} text="大模型辅助\n文献检索" width={140} size={21}/>
  <Box x={15} y={572} w={150} h={48} label="⚙ 设置" active={focus==='settings'} click f={f} size={22}/>
  <Text x={207} y={86} text={status} size={21} width={390}/>
  <Box x={617} y={66} w={114} h={37} label="最近地图" size={16} active={focus==='recent'} click f={f}/>
  <Box x={740} y={66} w={178} h={37} label="导入树形图文件" size={16} active={focus==='import'} click f={f}/>
  <Box x={927} y={66} w={125} h={37} label="导出结果" size={16} active={focus==='result'} click f={f}/>
  <Box x={1061} y={66} w={150} h={37} label="导出翻译卡" size={16} active={focus==='card'} click f={f}/>
  <path d="M181 116H1230" stroke={color.line}/>{children}
</Frame>;
