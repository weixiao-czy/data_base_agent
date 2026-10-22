// Original score: "A Clearer Question". 120 BPM / D major, no samples or downloads.
// Electric-piano chords, bell motif, stereo arpeggio, warm bass, layered drums.
// The picture and score share film.json so edits cannot silently drift apart.
import { mkdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
import { film, music, isPeak, isBridge, accents, motifStarts } from './audio-plan.mjs';
const SR = 48000, DUR = film.duration, N = SR * DUR, beat = 60 / film.bpm;
const L = new Float32Array(N), R = new Float32Array(N);
const wetL = new Float32Array(N), wetR = new Float32Array(N);
const hz = m => 440 * 2 ** ((m - 69) / 12);
const noise = i => { let x = (i + 1) | 0; x = Math.imul(x ^ (x >>> 16), 0x45d9f3b); x = Math.imul(x ^ (x >>> 16), 0x45d9f3b); return ((x ^ (x >>> 16)) >>> 0) / 2147483648 - 1; };
function event(start, duration, pan, gain, fn, send = 0) {
  const first = Math.round(start * SR), count = Math.round(duration * SR);
  const gl = Math.cos((pan + 1) * Math.PI / 4), gr = Math.sin((pan + 1) * Math.PI / 4);
  for (let k = 0; k < count && first + k < N; k++) {
    const i = first + k; if (i < 0) continue;
    const t = k / SR, release = Math.min(1, (count - k) / (SR * .035));
    const v = fn(t, i) * gain * release;
    L[i] += v * gl; R[i] += v * gr;
    wetL[i] += v * gl * send; wetR[i] += v * gr * send;
  }
}
function piano(start, note, gain = .13, pan = 0, duration = 2.8) {
  const freq = hz(note);
  event(start, duration, pan, gain, t => {
    const attack = 1 - Math.exp(-t * 160);
    return attack * (Math.sin(2 * Math.PI * freq * t) * Math.exp(-t * 2.1) + .28 * Math.sin(2 * Math.PI * freq * 2 * t) * Math.exp(-t * 3.5) + .08 * Math.sin(2 * Math.PI * freq * 3 * t) * Math.exp(-t * 7));
  }, .25);
}
// Dmaj9 / Aadd9 / Bm7 / Gmaj9, smooth shared upper voices.
const chords = [[50, 57, 61, 64, 69], [45, 57, 59, 61, 64], [47, 54, 57, 62, 66], [43, 54, 57, 59, 62]];
for (let start = 0, bar = 0; start < music.resolve; start += 4, bar++) {
  const chord = chords[bar % 4];
  chord.forEach((m, j) => piano(start + j * .018, m + 12, .105, (j - 2) * .21, 3.8));
  if (start >= 8 && start < music.outro - 4) chord.slice(1).forEach((m, j) => piano(start + 2.5 + j * .014, m + 12, .07, (2 - j) * .2, 1.5));
  chord.slice(1).forEach((m, j) => event(start, 4.35, (j - 1.5) * .4, .027, t => {
    const env = Math.min(1, t / .5) * Math.min(1, Math.max(0, (4.35 - t) / .8));
    return env * (Math.sin(2 * Math.PI * hz(m + 12) * t) + .3 * Math.sin(2 * Math.PI * hz(m + 12) * 1.002 * t));
  }, .45));
}
// An eight-note motif with rests, answered an octave lower in the bridge.
const motif = [78, 76, 73, 69, 71, 73, 76, 73];
const rhythm = [0, .75, 1.5, 2.5, 4, 4.75, 5.5, 6.5];
for (const start of motifStarts) {
  motif.forEach((note, j) => piano(start + rhythm[j] * beat, note - (start >= music.detail ? 12 : 0), isPeak(start) ? .19 : .15, Math.sin(j * 2) * .22, 2));
}
// Sparkling but quiet syncopated arpeggio, expanding in the central sections.
for (let step = 0; step < Math.ceil((music.outro - 8) / .25); step++) {
  const t = 8 + step * .25; if (t >= music.outro) break;
  if (t < music.build && step % 2) continue;
  const chord = chords[Math.floor(t / 4) % 4];
  const note = chord[1 + (step % 4)] + 24;
  piano(t + (step % 2 ? .014 : 0), note, isPeak(t) ? .075 : .046, step % 2 ? .6 : -.6, .8);
}
const kick = t => Math.sin(2 * Math.PI * (48 * t + 3.1 * (1 - Math.exp(-t * 32)))) * Math.exp(-t * 15) * (1 - Math.exp(-t * 700));
const snare = (t, i) => (noise(i) * .65 + Math.sin(2 * Math.PI * 185 * t) * .35) * Math.exp(-t * 24) * (1 - Math.exp(-t * 900));
const hat = (t, i) => (noise(i) - noise(i - 1)) * Math.exp(-t * 95) * (1 - Math.exp(-t * 1200));
for (let b = Math.round(music.introEnd / beat); b < music.outro / beat; b++) {
  const t = b * beat, drop = isPeak(t), bridge = isBridge(t);
  if (!bridge || b % 2 === 0) event(t, .45, 0, drop ? .48 : .37, kick);
  if (b % 2 === 1 && !bridge) event(t, .22, .08, .16, snare, .1);
  event(t + .25, .12, b % 2 ? -.35 : .35, drop ? .065 : .043, hat);
  if (drop) event(t + .375, .06, -.35, .025, hat);
  const rootNote = chords[Math.floor(t / 4) % 4][0] - 12;
  event(t + .03, .39, 0, .18, v => {
    const env = Math.min(1, v / .015) * Math.exp(-v * 5);
    return env * (Math.sin(2 * Math.PI * hz(rootNote) * v) + .23 * Math.sin(4 * Math.PI * hz(rootNote) * v));
  });
}
// Small UI accents and a soft filtered-noise sweep into each picture edit.
for (const scene of film.scenes.slice(1)) {
  const t = scene.from / film.fps;
  event(t - .55, .55, -.25, .055, (v, i) => {
    const smooth = (noise(i) + noise(i - 1) + noise(i - 2) + noise(i - 3)) / 4;
    return smooth * Math.sin(Math.PI * v / .55) * (v / .55);
  }, .2);
  piano(t, 86, .055, .35, 1.5);
}
for (const accent of accents) piano(accent.time, 81, .045, .1, .5);
// Resolve on Dmaj9; leave the end card enough time to breathe.
[50, 57, 61, 64, 69, 74].forEach((m, j) => piano(music.resolve + j * .035, m + (j < 2 ? 0 : 12), .13, (j - 2.5) * .16, 4));
// Stereo musical delay and short diffusion. Delay never feeds the dry drum bus.
for (let i = 0; i < N; i++) {
  const d = Math.round(SR * .375), d2 = Math.round(SR * .113);
  if (i >= d) { wetL[i] += wetR[i - d] * .32; wetR[i] += wetL[i - d] * .32; L[i] += wetR[i - d] * .56; R[i] += wetL[i - d] * .56; }
  if (i >= d2) { L[i] += wetR[i - d2] * .23; R[i] += wetL[i - d2] * .23; }
}
let peak = 0, squares = 0;
for (let i = 0; i < N; i++) {
  const t = i / SR;
  const fade = Math.min(1, t / .035, Math.max(0, (DUR - t) / 1.7));
  L[i] = Math.tanh(L[i] * 1.25) * fade; R[i] = Math.tanh(R[i] * 1.25) * fade;
  peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i]));
}
const norm = 10 ** (-1.2 / 20) / peak;
const buf = Buffer.alloc(44 + N * 4);
buf.write('RIFF', 0); buf.writeUInt32LE(36 + N * 4, 4); buf.write('WAVE', 8); buf.write('fmt ', 12);
buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22); buf.writeUInt32LE(SR, 24);
buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34); buf.write('data', 36); buf.writeUInt32LE(N * 4, 40);
for (let i = 0; i < N; i++) { const l = L[i] * norm, r = R[i] * norm; squares += (l * l + r * r) / 2; buf.writeInt16LE(Math.round(l * 32767), 44 + i * 4); buf.writeInt16LE(Math.round(r * 32767), 46 + i * 4); }
mkdirSync(path.join(root, 'src/audio'), { recursive: true });
writeFileSync(path.join(root, 'src/audio/track.wav'), buf);
console.log(`Original score: ${DUR}s, ${film.bpm} BPM, stereo ${SR}Hz; peak -1.2 dBFS; RMS ${(10 * Math.log10(squares / N)).toFixed(1)} dBFS`);
