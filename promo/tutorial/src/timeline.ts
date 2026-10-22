import lesson from './lesson.json';
export type LessonScene = typeof lesson.scenes[number];
export type LessonStep = LessonScene['steps'][number];
export const FPS = lesson.fps;
let cursor = 0;
export const scenes = lesson.scenes.map(scene => {
  const from = cursor;
  let local = 0;
  const steps = scene.steps.map(step => {
    const at = local;
    local += step.seconds * FPS;
    return { ...step, at, frames: step.seconds * FPS };
  });
  cursor += local;
  return { ...scene, from, frames: local, steps };
});
export const totalFrames = cursor;
export { lesson };
