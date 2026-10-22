import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { film, demo, music, accents, motifStarts } from './audio-plan.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = file => readFileSync(path.join(root, file), 'utf8').replace(/^\uFEFF/, '');
const ids = new Set();
let end = 0;
for (const scene of film.scenes) {
  assert(!ids.has(scene.id), `Duplicate scene ${scene.id}`); ids.add(scene.id);
  assert.equal(scene.from, end, `${scene.id}: gap or overlap`);
  assert(Number.isInteger(scene.duration) && scene.duration > 0, `${scene.id}: invalid duration`);
  assert.equal(scene.from % (film.fps * 60 / film.bpm), 0, `${scene.id}: off beat`);
  assert.equal(scene.duration % (film.fps * 60 / film.bpm), 0, `${scene.id}: off beat ending`);
  end += scene.duration;
}
assert.equal(end, film.duration * film.fps);
assert.equal(film.scenes.at(-1).id, 'brand');
assert(film.scenes.at(-1).duration >= 6 * film.fps, 'CTA should remain readable');
const registered = read('src/commercial/Commercial.tsx').match(/const scenes:[^=]+=[\s\S]*?\{([^}]+)\}/)?.[1];
assert(registered, 'Cannot locate scene registry');
for (const id of ids) assert(new RegExp(`\\b${id}\\s*:`).test(registered), `Unregistered scene ${id}`);
assert.equal(demo.dimensions.length, 6);
assert.equal(new Set(demo.dimensions.map(d => d.id)).size, 6);
assert(demo.notice.includes('示例'));
for (const d of demo.dimensions) assert(d.paper.startsWith('示例：'), `Unlabelled fixture ${d.id}`);
assert.equal(demo.selectedPaper.title, demo.dimensions.find(d => d.id === 'method').paper);
for (const section of ['entry', 'explore']) {
  const scene = film.scenes.find(s => s.id === (section === 'entry' ? 'treeEntry' : 'treeExplore'));
  const values = Object.values(demo.cues[section]);
  for (let i = 0; i < values.length; i++) {
    assert(values[i] >= 0 && values[i] < scene.duration - 9, `${section}: cue under exit wipe`);
    if (i) assert(values[i] > values[i - 1], `${section}: out-of-order cues`);
  }
}
const growth = film.scenes.find(s => s.id === 'treeGrowth');
assert(demo.cues.growth.papers + (demo.dimensions.length - 1) * 5 + 18 <= demo.cues.growth.hold);
assert(demo.cues.growth.hold < growth.duration - 9);
for (const accent of accents) {
  const scene = film.scenes.find(s => s.id === accent.scene);
  assert(accent.frame >= 0 && accent.frame < scene.duration - 9, `Audio accent outside scene: ${accent.scene}`);
  assert(accent.time < music.outro);
}
assert(music.mapPeak > music.bridge && music.detail > music.mapPeak);
assert.equal(music.resolve + 4, film.duration);
assert(music.outro < music.resolve);
assert(motifStarts.at(-1) > music.workspace - 8, 'Melody stops before the new scenes');
const pkg = JSON.parse(read('package.json'));
const lock = JSON.parse(read('package-lock.json'));
assert.deepEqual(pkg.dependencies, lock.packages[''].dependencies, 'Package lock out of sync');
for (const name of readdirSync(path.join(root, 'scripts')).filter(n => n.endsWith('.mjs'))) {
  execFileSync(process.execPath, ['--check', path.join(root, 'scripts', name)], { stdio: 'pipe' });
}
console.log(`PASS: ${film.scenes.length} scenes, ${end} frames, ${film.duration}s; continuous beat-aligned timeline`);
console.log(`PASS: six dimensions, ordered map interactions, ${accents.length} synchronized audio accents, full-length music plan`);
console.log('PASS: script syntax and package lock; NO browser, frames, video or audio generated');
