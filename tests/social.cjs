const assert = require('node:assert/strict');
require('../dist/social.js');
const {STATES, SocialWorld, seededRandom} = globalThis.MeydanSocial;

const a = seededRandom(42), b = seededRandom(42);
assert.deepEqual([a(), a(), a()], [b(), b(), b()]);

const definitions = [
  {id:'ada', name:'Ada', x:0, z:0},
  {id:'mert', name:'Mert', x:8, z:8}
];
const first = new SocialWorld(7, definitions);
const second = new SocialWorld(7, definitions);
for (let i = 0; i < 80; i++) {
  first.update(.1, {x:20, z:20});
  second.update(.1, {x:20, z:20});
}
assert.deepEqual(first.snapshot(), second.snapshot(), 'same seed and inputs must produce identical NPCs');
assert.ok(first.snapshot().some(n => n.x !== 0 || n.z !== 0), 'at least one NPC should wander');

const world = new SocialWorld(3, definitions);
assert.equal(world.interact({x:50, z:50}).type, 'none');
let greeting = world.interact({x:.4, z:.3}, 'ada');
assert.equal(greeting.type, 'dialogue');
assert.equal(greeting.outcome, 'greeting');
assert.equal(world.npcs[0].state, STATES.CHAT);
let busy = world.interact({x:.4, z:.3}, 'ada');
assert.equal(busy.outcome, 'busy');
world.update(.25, {x:.4, z:.3});
for (let i = 0; i < 12; i++) world.update(.25, {x:.4, z:.3});
assert.equal(world.npcs[0].state, STATES.IDLE);
assert.ok(world.npcs[0].cooldownUntil > world.time);

world.npcs[0].cooldownUntil = 0;
world.npcs[0].state = STATES.INVITE;
world.npcs[0].stateUntil = world.time + 3;
const dance = world.interact({x:0, z:0}, 'ada');
assert.equal(dance.type, 'activity');
assert.equal(dance.activity, 'dance');
assert.equal(world.npcs[0].state, STATES.DANCE);
for (let i = 0; i < 22; i++) world.update(.25, {x:20, z:20});
assert.equal(world.npcs[0].state, STATES.IDLE);
assert.ok(world.takeEvents().some(e => e.type === 'dialogue' && /turdu|Ritmi/.test(e.text)));

assert.throws(() => world.update(-1), /Geçersiz/);
console.log('PASS: deterministic NPC wander, proximity chat, cooldown, dance invitation and activity lifecycle.');
