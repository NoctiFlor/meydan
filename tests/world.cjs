const assert=require('node:assert/strict');
const worldApi=require('../dist/world.js');
const {plaza,findZone,nearestActivity,lodBand,budgetFor,blocked,validateWorld}=worldApi;

assert.deepEqual(validateWorld(plaza),[]);
assert.equal(findZone(plaza,1.5,-1.5).id,'central');
assert.equal(findZone(plaza,-6,-2).id,'cafe');
assert.equal(findZone(plaza,0,10).id,'promenade');
assert.equal(findZone(plaza,40,40),null);
assert.equal(nearestActivity(plaza,{x:1,z:-1},'dance').id,'stage-dance');
assert.equal(nearestActivity(plaza,{x:6,z:5}).id,'fountain-photo');
assert.equal(lodBand(plaza,{x:0,z:0},{x:8,z:0}),'near');
assert.equal(lodBand(plaza,{x:0,z:0},{x:20,z:0}),'medium');
assert.equal(lodBand(plaza,{x:0,z:0},{x:36,z:0}),'far');
assert.equal(lodBand(plaza,{x:0,z:0},{x:50,z:0}),'hidden');
assert.equal(budgetFor(plaza,'low').maxNpc,6);
assert.equal(budgetFor(plaza,'unknown').maxNpc,10);
assert.equal(blocked(plaza,6,5,.25),true);
assert.equal(blocked(plaza,0,3,.25),false);
assert.equal(blocked(plaza,20,3,0),true);

const broken=JSON.parse(JSON.stringify(plaza));
broken.npcSpawns[0].activity='missing';
assert.ok(validateWorld(broken).includes('unknown activity missing'));

console.log('PASS: world schema, zones, landmarks, activities, NPC spawns, LOD, budgets and collision queries.');
