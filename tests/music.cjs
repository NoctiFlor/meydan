const assert=require('node:assert/strict');
require('../dist/music.js');
const {profiles,LOOP_BEATS,profileFor,generateBeat,generateLoop}=globalThis.MeydanMusic;

assert.equal(LOOP_BEATS,8);
assert.deepEqual(Object.keys(profiles).sort(),['gece_isiklari','meydan_demo','sahil_ritmi']);
assert.equal(profileFor('unknown'),profiles.meydan_demo);

const signatures=new Set();
for(const [id,profile] of Object.entries(profiles)){
 assert.equal(profile.id,id);
 for(const plan of ['kick','snare','hat','bass','chords']) assert.equal(profile[plan].length,LOOP_BEATS,`${id}: ${plan}`);
 const loop=generateLoop(id);
 assert.equal(loop.length,8);assert.deepEqual(loop.map(row=>row.beat),[0,1,2,3,4,5,6,7]);
 const flat=loop.flatMap(row=>row.events);
 assert.ok(flat.some(event=>event.kind==='kick'),`${id}: kick`);
 assert.ok(flat.some(event=>event.kind==='snare'),`${id}: snare`);
 assert.ok(flat.some(event=>event.kind==='bass'),`${id}: bass`);
 assert.ok(flat.some(event=>event.kind==='chord'),`${id}: chord`);
 assert.ok(flat.every(event=>event.offsetBeats>=0&&event.offsetBeats<1),`${id}: beat offsets`);
 assert.ok(flat.filter(event=>event.midi&&!Array.isArray(event.midi)).every(event=>event.midi>=36&&event.midi<=72),`${id}: bass register`);
 assert.ok(flat.filter(event=>Array.isArray(event.midi)).every(event=>event.midi.length>=3&&event.midi.every(note=>note>=48&&note<=84)),`${id}: chord register`);
 signatures.add(JSON.stringify(loop));
 assert.deepEqual(generateLoop(id),loop,`${id}: deterministic`);
 assert.deepEqual(generateLoop(id,2).map(row=>row.beat),[16,17,18,19,20,21,22,23]);
 console.log(`PASS: ${id} procedural groove`);
}
assert.equal(signatures.size,3,'each song must have a distinct groove');
assert.throws(()=>generateBeat('meydan_demo',-1),/beatIndex/);
assert.throws(()=>generateBeat('meydan_demo',.5),/beatIndex/);
assert.throws(()=>generateLoop('meydan_demo',-1),/loopNumber/);
console.log('ALL ORIGINAL PROCEDURAL MUSIC PROFILES VALID');
