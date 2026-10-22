// Original deterministic instrumental bed. Run ONLY when preparing a future render.
// No network, samples, downloaded music, speech API, or secrets required.
import fs from 'node:fs';
import path from 'node:path';
import {root,duration} from './lesson.mjs';
const rate=44100, channels=2, samples=Math.round(duration*rate), bytes=samples*channels*2;
const output=path.join(root,'public/music.wav');
fs.mkdirSync(path.dirname(output),{recursive:true});
const header=Buffer.alloc(44);
header.write('RIFF');header.writeUInt32LE(36+bytes,4);header.write('WAVEfmt ',8);
header.writeUInt32LE(16,16);header.writeUInt16LE(1,20);header.writeUInt16LE(channels,22);
header.writeUInt32LE(rate,24);header.writeUInt32LE(rate*4,28);header.writeUInt16LE(4,32);header.writeUInt16LE(16,34);
header.write('data',36);header.writeUInt32LE(bytes,40);
const fd=fs.openSync(output,'w');fs.writeSync(fd,header);
const tau=Math.PI*2, bpm=104, beat=60/bpm;
const chords=[[48,55,59,64],[45,52,57,60],[41,48,52,57],[43,50,55,59]];
const hz=n=>440*Math.pow(2,(n-69)/12), sine=(n,t)=>Math.sin(tau*hz(n)*t);
const noise=n=>{const h=Math.sin(n*12.9898+78.233)*43758.5453;return (h-Math.floor(h))*2-1;};
try{
 for(let offset=0;offset<samples;offset+=rate){
  const count=Math.min(rate,samples-offset), chunk=Buffer.alloc(count*4);
  for(let j=0;j<count;j++){
   const n=offset+j,t=n/rate,b=t/beat,bar=Math.floor(b/4),chordIndex=Math.floor(bar/2)%4,chord=chords[chordIndex];
   const q=b%1,half=b*2%1,section=Math.floor(bar/8)%4;
   const envelope=Math.min(1,t/2,(duration-t)/4);
   const pulse=Math.sin(Math.PI*(b%8)/8)**.35;
   let pad=0;
   const crossfade=Math.min(1,(b%8)*beat/.4);
   for(let k=0;k<chord.length;k++){
    const note=chord[k],previous=chords[(chordIndex+3)%4][k];
    pad+=((sine(note+12,t)+.18*sine(note+24,t))*crossfade+(sine(previous+12,t)+.18*sine(previous+24,t))*(1-crossfade))*.018;
   }
   pad*=.65+.35*pulse;
   const bass=sine(chord[0]-12,q*beat)*Math.exp(-q*4)*Math.min(1,q*60)*Math.min(1,(1-q)*60)*.075;
   const arpeggio=chord[[0,2,1,3,2,1,3,2][Math.floor(b*2)%8]]+24;
   const pluck=(sine(arpeggio,t)+.22*sine(arpeggio+12,t))*Math.exp(-half*7)*Math.min(1,half*80)*.035;
   const kick=Math.sin(tau*(48*q*beat+9*(1-Math.exp(-q*beat*28))))*Math.exp(-q*beat*24)*.085;
   const hat=noise(n)*Math.exp(-half*beat*2*100)*.008;
   const backbeat=Math.floor(b)%4===1||Math.floor(b)%4===3?noise(n)*Math.exp(-q*beat*45)*.012:0;
   const drums=t<4||t>duration-5?0:kick+hat+backbeat;
   const centered=pad+bass+drums;
   for(let channel=0;channel<2;channel++){
    const pan=.7+(channel===0?1:-1)*.25*Math.sin(b/8);
    const value=(centered+pluck*pan*(section===2?.6:1))*envelope;
    chunk.writeInt16LE(Math.round(Math.max(-1,Math.min(1,value))*32767),(j*2+channel)*2);
   }
  }
  fs.writeSync(fd,chunk);
 }
}finally{fs.closeSync(fd);}
console.log(`Created original ${bpm} BPM instrumental: ${output} (${duration}s). Listen before final delivery.`);
