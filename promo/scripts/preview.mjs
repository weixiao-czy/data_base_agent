// Optional renderer QA. Do not run during a source-only delivery.
import { bundle } from '@remotion/bundler';
import { renderStill, selectComposition } from '@remotion/renderer';
import { mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { film, demo } from './audio-plan.mjs';
import './check-project.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = path.join(root, 'out', 'review-litmap');
mkdirSync(out, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.join(root, 'src/index.ts') });
const composition = await selectComposition({ serveUrl, id: 'Promo' });
const frames = new Set([0, composition.durationInFrames - 1]);
for (const s of film.scenes) {
  frames.add(s.from + Math.floor(s.duration * .65));
  frames.add(s.from + s.duration - 10);
}
for (const [id, cueSet] of [['treeEntry', demo.cues.entry], ['treeExplore', demo.cues.explore]]) {
  const s = film.scenes.find(s => s.id === id);
  for (const f of Object.values(cueSet)) { frames.add(s.from + f - 1); frames.add(s.from + f + 1); }
}
for (const frame of [...frames].sort((a, b) => a - b)) {
  await renderStill({ composition, serveUrl, frame, output: path.join(out, `${String(frame).padStart(4, '0')}.png`), scale: 2 / 3 });
  console.log(`Wrote frame ${frame} / ${composition.durationInFrames} (requires visual review)`);
}
