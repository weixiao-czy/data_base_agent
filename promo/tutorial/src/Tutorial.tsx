import React from 'react';
import { AbsoluteFill, Audio, Composition, Sequence, interpolate, staticFile, useCurrentFrame } from 'remotion';
import { lesson, scenes, totalFrames, FPS } from './timeline';
import { Views } from './Views';
import { Text, color, clamp } from './vector';
export type TutorialProps={music:boolean;voice:boolean};
const Scene:React.FC<{scene:typeof scenes[number];index:number}>=({scene,index})=>{
 const frame=useCurrentFrame();
 const stepIndex=Math.max(0,scene.steps.findIndex(step=>frame>=step.at&&frame<step.at+step.frames));
 const step=scene.steps[stepIndex],f=frame-step.at;
 const enter=interpolate(frame,[0,18],[0,1],clamp), stepEnter=interpolate(f,[0,12],[0,1],clamp);
 const global=scene.from+frame;
 const time=(v:number)=>`${Math.floor(v/60)}:${String(Math.floor(v%60)).padStart(2,'0')}`;
 return <AbsoluteFill style={{background:color.bg}}><svg width="100%" height="100%" viewBox="0 0 1920 1080" style={{fontFamily:'"Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", "Noto Sans SC", Arial, sans-serif'}}>
  <defs><pattern id="dots" width="32" height="32" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#668663" opacity=".12"/></pattern><linearGradient id="wash"><stop stopColor="#DFEDC8"/><stop offset="1" stopColor="#F5F4EC"/></linearGradient></defs>
  <rect width="1920" height="1080" fill={color.bg}/><circle cx={1600+Math.sin(global/100)*35} cy="100" r="660" fill="url(#wash)" opacity=".45"/><rect width="1920" height="1080" fill="url(#dots)"/>
  <Text x={80} y={55} text={`文献检索 AGENT  /  零基础上手`} size={22} bold/>
  <Text x={1840} y={55} text={`${String(index+1).padStart(2,'0')} / ${scenes.length}  ·  ${time(global/FPS)} / ${time(totalFrames/FPS)}`} anchor="end" size={21} fill={color.gray}/>
  <Text x={80} y={117} text={scene.chapter} size={25} fill={color.blue}/><Text x={80} y={184} text={scene.title} width={1760} size={53} bold/>
  <g opacity={stepEnter} transform={`translate(0,${(1-stepEnter)*14})`}>
   <rect x="80" y="239" width="450" height="62" rx="15" fill={color.ink}/><Text x={105} y={280} text={`现在做第 ${stepIndex+1} 步 / 共 ${scene.steps.length} 步`} size={26} fill={color.green}/>
   <Text x={85} y={365} text={step.action} width={490} size={36} bold lineHeight={1.55}/>
   <Text x={85} y={580} text="做完后，确认这一点" size={23} fill={color.gray}/>
   <rect x="80" y="602" width="450" height="158" rx="18" fill="#EAF0E1"/><Text x={100} y={642} text={scene.goal} width={410} size={27} lineHeight={1.6}/>
   <Text x={85} y={817} text="跟不上时可以暂停视频。" width={445} size={23} fill={color.gray}/>
  </g>
  <g opacity={enter} transform={`translate(${600+(1-enter)*25},225)`}><Views scene={scene} focus={step.focus} f={f}/></g>
  <path d="M80 918H1840" stroke={color.line} strokeWidth="2"/>
  <Text x={105} y={965} text={step.voice} width={1710} size={31} lineHeight={1.45}/>
  <rect x="0" y="1074" width={1920*global/(totalFrames-1)} height="6" fill={color.orange}/>
  {scenes.slice(1).map(s=><rect key={s.id} x={1920*s.from/totalFrames} y="1073" width="2" height="7" fill={color.ink}/>)}
 </svg></AbsoluteFill>;
};
export const Tutorial:React.FC<TutorialProps>=({music,voice})=><AbsoluteFill>
 {music&&<Audio src={staticFile('music.wav')} volume={voice ? .22 : .65}/>}
 {voice&&<Audio src={staticFile('narration.wav')}/>}
 {scenes.map((scene,index)=><Sequence key={scene.id} from={scene.from} durationInFrames={scene.frames}><Scene scene={scene} index={index}/></Sequence>)}
</AbsoluteFill>;
export const Root:React.FC=()=> <Composition id="Tutorial" component={Tutorial} defaultProps={{music:true,voice:false}} fps={FPS} durationInFrames={totalFrames} width={lesson.width} height={lesson.height}/>;
