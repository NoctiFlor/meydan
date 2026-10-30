const assert = require('node:assert/strict');
require('../dist/motion.js');

const {
  shortestAngle,
  dampAngle,
  locomotionWeights,
  cameraCollisionDistance,
  avatarProfile
} = globalThis.MeydanMotion;

const close = (a, b, tolerance = 1e-8) =>
  assert.ok(Math.abs(a - b) <= tolerance, `${a} != ${b}`);

// Rotation always follows the shortest path, including across the -PI/PI seam.
assert.ok(shortestAngle(Math.PI - .05, -Math.PI + .05) > 0);
assert.ok(shortestAngle(-Math.PI + .05, Math.PI - .05) < 0);

function simulateAngle(fps) {
  let angle = Math.PI - .2;
  for (let i = 0; i < fps * 2; i++)
    angle = dampAngle(angle, -Math.PI + .4, 8, 1 / fps);
  return angle;
}

// Exponential damping produces the same result at common render rates.
const at30 = simulateAngle(30), at60 = simulateAngle(60), at120 = simulateAngle(120);
close(at30, at60, 1e-10);
close(at60, at120, 1e-10);
close(dampAngle(1, 2, 8, 0), 1);

for (const speed of [0, .1, .35, 1, 2.1, 2.65, 3.2, 5]) {
  const weights = locomotionWeights(speed);
  close(weights.idle + weights.walk + weights.run, 1);
  for (const value of Object.values(weights)) assert.ok(value >= 0 && value <= 1);
}
assert.deepEqual(locomotionWeights(0), {idle:1, walk:0, run:0});
assert.ok(locomotionWeights(1).walk > .99);
assert.ok(locomotionWeights(2.65).walk > 0 && locomotionWeights(2.65).run > 0);
assert.ok(locomotionWeights(4).run > .99);

close(cameraCollisionDistance(6, Infinity), 6);
close(cameraCollisionDistance(6, 4), 3.75);
close(cameraCollisionDistance(6, .5), 1.2);
close(cameraCollisionDistance(6, 7), 6);
close(cameraCollisionDistance(2, .2, {minimum:.8, padding:.1}), .8);

const ada = avatarProfile('ada'), adaAgain = avatarProfile('ada'), mert = avatarProfile('mert');
assert.deepEqual(ada, adaAgain);
assert.notDeepEqual(ada, mert);
for (const profile of [ada, mert]) {
  assert.ok(profile.scale >= .96 && profile.scale < 1.04);
  assert.ok(profile.animationOffset >= 0 && profile.animationOffset < 12);
  assert.ok(Number.isInteger(profile.paletteIndex) && profile.paletteIndex >= 0 && profile.paletteIndex < 6);
}

console.log('PASS: shortest-angle damping; FPS independence; locomotion blend; camera collision; deterministic avatar profile.');
