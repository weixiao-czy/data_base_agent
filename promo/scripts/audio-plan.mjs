import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = file => JSON.parse(readFileSync(path.join(root, file), 'utf8').replace(/^\uFEFF/, ''));
export const film = read('src/film.json');
export const demo = read('src/commercial/tree-demo.json');
const scene = id => {
  const s = film.scenes.find(s => s.id === id);
  if (!s) throw new Error(`Missing audio section: ${id}`);
  return s.from / film.fps;
};
export const music = {
  introEnd: scene('reveal'),
  build: scene('plan'),
  firstPeak: scene('network'),
  bridge: scene('treeEntry'),
  mapPeak: scene('treeGrowth'),
  detail: scene('treeExplore'),
  workspace: scene('workspace'),
  outro: scene('brand'),
  resolve: film.duration - 4,
};
export const isPeak = t => (t >= music.firstPeak && t < music.bridge) || (t >= music.mapPeak && t < music.detail);
export const isBridge = t => (t >= music.bridge && t < music.mapPeak) || (t >= music.detail && t < music.detail + 2);
// Local frame cues are also consumed by TreeScenes; changing an interaction moves
// its sound here automatically. These are UI accents, never simulated speech.
const localEvents = [
  ['conversation', [103, 120, 175]],
  ['plan', [25, 65, 105, 145]],
  ['treeEntry', [demo.cues.entry.click, demo.cues.entry.map]],
  ['treeGrowth', [0, ...demo.dimensions.map((_, i) => demo.cues.growth.aspects + i * demo.cues.growth.aspectStep), demo.cues.growth.topics, demo.cues.growth.papers]],
  ['treeExplore', [demo.cues.explore.collapse, demo.cues.explore.expand, demo.cues.explore.search, demo.cues.explore.select, demo.cues.explore.return]],
  ['workspace', [165]],
];
export const accents = localEvents.flatMap(([id, frames]) => frames.map(frame => ({ scene: id, frame, time: scene(id) + frame / film.fps })));
export const motifStarts = [];
for (let t = music.introEnd; t + 4 < music.outro; t += 8) motifStarts.push(t);
