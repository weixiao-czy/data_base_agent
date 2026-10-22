import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
export const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
export const readJSON=file=>JSON.parse(fs.readFileSync(path.join(root,file),'utf8').replace(/^\uFEFF/,''));
export const lesson=readJSON('src/lesson.json');
let frame=0,number=0;
export const cues=[];
export const scenes=lesson.scenes.map(scene=>{
 const from=frame;
 for(const step of scene.steps){const frames=step.seconds*lesson.fps;cues.push({...step,id:++number,scene:scene.id,chapter:scene.chapter,from:frame,frames});frame+=frames;}
 return {...scene,from,frames:frame-from};
});
export const totalFrames=frame;
export const duration=frame/lesson.fps;
export const time=sec=>`${String(Math.floor(sec/60)).padStart(2,'0')}:${String(Math.floor(sec%60)).padStart(2,'0')}`;
