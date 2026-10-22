// Static validation only: no browser launch, media generation, API calls, or rendering.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import ts from 'typescript';
import {root,lesson,scenes,cues,totalFrames,duration,readJSON} from './lesson.mjs';
const expectedViews=new Set(['roadmap','release','files','credentials','provider','settings','chat','errors','plan','tree','results','export','history','env','source','terminal']);
assert.equal(lesson.fps,30);assert.equal(lesson.width,1920);assert.equal(lesson.height,1080);
assert.match(lesson.sourceCommit,/^[a-f0-9]{40}$/);
assert.equal(new Set(scenes.map(s=>s.id)).size,scenes.length,'Duplicate scene IDs');
assert.equal(totalFrames,duration*lesson.fps);
// Use the actual SVG text-wrapping implementation, without invoking a React render.
const vector=fs.readFileSync(path.join(root,'src/vector.tsx'),'utf8');
const wrapSource=vector.slice(vector.indexOf('export function wrap'),vector.indexOf('export const Text')).replace('export function','function');
const wrap=vm.runInNewContext(ts.transpile(wrapSource)+'\nwrap');
let cursor=0,maxReadingRate=0;
for(const scene of scenes){
 assert.equal(scene.from,cursor,'Scene discontinuity');assert.ok(expectedViews.has(scene.view),`Unknown view ${scene.view}`);
 assert.ok(wrap(scene.title,1760,53).length<=1,`Title may wrap: ${scene.id}`);
 assert.ok(wrap(scene.goal,410,27).length<=3,`Goal overflow: ${scene.id}`);
 for(const step of scene.steps){
  assert.ok(Number.isInteger(step.seconds)&&step.seconds>=6,'Step must have a readable integral duration');
  for(const key of ['action','voice','focus'])assert.ok(step[key]?.length,`${scene.id} lacks ${key}`);
  assert.ok(wrap(step.action,440,36).length<=4,`Action overflow: ${scene.id}`);
  assert.ok(wrap(step.voice,1710,31).length<=2,`Caption overflow: ${scene.id}`);
  const spokenUnits=[...step.voice].reduce((n,c)=>n+(/[\x00-\x7f]/.test(c)?.25:/[，。；：、！？]/.test(c)?0:1),0);
  maxReadingRate=Math.max(maxReadingRate,spokenUnits/step.seconds);
  assert.ok(spokenUnits/step.seconds<=6,`Narration too dense: ${scene.id} / ${step.focus}`);
 }
 cursor+=scene.frames;
}
const exported=readJSON('narration-cues.json');
assert.deepEqual(exported,cues.map(c=>({id:c.id,start:c.from/lesson.fps,seconds:c.frames/lesson.fps,text:c.voice,scene:c.scene})),'Run npm run docs after editing lesson.json');
const srt=fs.readFileSync(path.join(root,'subtitles.srt'),'utf8');
assert.equal((srt.match(/ --> /g)||[]).length,cues.length);
const stamp=sec=>{const ms=Math.round(sec*1000);return `${String(Math.floor(ms/3600000)).padStart(2,'0')}:${String(Math.floor(ms/60000)%60).padStart(2,'0')}:${String(Math.floor(ms/1000)%60).padStart(2,'0')},${String(ms%1000).padStart(3,'0')}`;};
assert.equal(srt,cues.map(c=>`${c.id}\n${stamp(c.from/lesson.fps)} --> ${stamp((c.from+c.frames)/lesson.fps)}\n${c.voice}\n`).join('\n'),'Stale subtitle file');
const board=fs.readFileSync(path.join(root,'STORYBOARD.md'),'utf8');
const narration=fs.readFileSync(path.join(root,'NARRATION.md'),'utf8');
for(const cue of cues){assert.ok(board.includes(cue.voice));assert.ok(narration.includes(cue.voice));}
const order=id=>scenes.findIndex(s=>s.id===id);
assert.ok(order('tree_entry')<order('return')&&order('return')<order('search'),'Map must precede ordinary search');
assert.ok(order('search')<order('exports'));
const pkg=readJSON('package.json'),lock=readJSON('package-lock.json');
assert.equal(pkg.name,lock.name);assert.equal(pkg.name,lock.packages[''].name);
assert.deepEqual(pkg.dependencies,lock.packages[''].dependencies);
assert.deepEqual(pkg.devDependencies,lock.packages[''].devDependencies);
for(const file of ['src/index.ts','src/Tutorial.tsx','src/Views.tsx','src/vector.tsx','src/timeline.ts','scripts/gen-audio.mjs','scripts/preview.mjs','scripts/narrate.ps1','scripts/assemble_voice.py','README.md','RENDER_HANDOFF.md','QUICKSTART.md','FACT_CHECK.md'])assert.ok(fs.existsSync(path.join(root,file)),`Missing ${file}`);
for(const file of ['Tutorial.tsx','Views.tsx','vector.tsx']){
 const source=fs.readFileSync(path.join(root,'src',file),'utf8');
 assert.ok(!/Math\.random|Date\.now|<img\b|<Img\b|fetch\(/.test(source),`${file}: nondeterministic or external visual dependency`);
}
console.log(`PASS: ${scenes.length} scenes / ${cues.length} cues / ${duration}s / ${totalFrames} frames.`);
console.log(`PASS: timeline, subtitle alignment, text line budgets, source completeness, lock consistency. Peak estimated narration density ${maxReadingRate.toFixed(2)} units/s.`);
console.log('Static validation only. Fonts, actual speech timing, sound mix and final visual layout still require future media review.');
