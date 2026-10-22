// Explicit opt-in for the NEXT operator. Not invoked by any static check.
import fs from 'node:fs';
import path from 'node:path';
import {bundle} from '@remotion/bundler';
import {renderStill,selectComposition} from '@remotion/renderer';
import {root,scenes,lesson} from './lesson.mjs';
const serveUrl=await bundle({entryPoint:path.join(root,'src/index.ts')});
const props={music:false,voice:false};
const composition=await selectComposition({serveUrl,id:'Tutorial',inputProps:props});
const output=path.join(root,'out/preview');fs.mkdirSync(output,{recursive:true});
for(const scene of scenes){
 let stepFrom=scene.from;
 for(let i=0;i<scene.steps.length;i++){
  const step=scene.steps[i];
  // Before/after the demonstrated click, plus end-state: useful for static visual QA.
  for(const seconds of [1,3.8,step.seconds-.5]){
   const frame=stepFrom+Math.floor(seconds*lesson.fps);
   await renderStill({serveUrl,composition,inputProps:props,frame,
    output:path.join(output,`${scene.id}-${i+1}-${frame}.png`)});
  }
  stepFrom+=step.seconds*lesson.fps;
 }
}
console.log(`Preview frames written to ${output}. Review before rendering the movie.`);
