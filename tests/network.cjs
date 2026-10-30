const assert=require('node:assert/strict');
require('../dist/network.js');
const {PrivateRoomService,SnapshotBuffer,interpolateTransform}=globalThis.MeydanNetwork;

let now=1000; const service=new PrivateRoomService(44,{clock:()=>now,maxPlayers:2});
const created=service.create(' <Ada> ');
assert.match(created.room.code,/^[A-Z2-9]{6}$/);
assert.equal(created.player.name,'Ada');
const guest=service.join(created.room.code,'Mert');
assert.equal(service.roomState(created.room.code).players.length,2);
assert.throws(()=>service.join(created.room.code,'Dolu'),/dolu/);

let move=service.submitTransform(created.room.code,created.player.id,{seq:0,transform:{x:1,z:2,yaw:0,state:'walk'}});
assert.equal(move.ok,true);
assert.equal(service.submitTransform(created.room.code,created.player.id,{seq:0,transform:{x:2,z:2}}).reason,'stale-sequence');
assert.equal(service.submitTransform(created.room.code,created.player.id,{seq:200,transform:{x:2,z:2}}).reason,'sequence-jump');
assert.equal(service.submitTransform(created.room.code,created.player.id,{seq:1,transform:{x:99,z:99}}).reason,'transform-jump');
now+=100; assert.equal(service.submitTransform(created.room.code,created.player.id,{seq:1,transform:{x:3,z:2,yaw:Math.PI,state:'run'}}).ok,true);

const player=service.getPlayer(created.room.code,created.player.id);
const sampled=player.buffer.sample(1050);
assert.equal(sampled.x,2); assert.equal(sampled.z,2);
assert.ok(Math.abs(Math.abs(sampled.yaw)-Math.PI/2)<1e-9);
const direct=interpolateTransform({serverTime:0,transform:{x:0,y:0,z:0,yaw:3,state:'idle'}},{serverTime:10,transform:{x:10,y:0,z:0,yaw:-3,state:'walk'}},5);
assert.ok(Math.abs(direct.yaw-3)<.2,'yaw interpolation must follow shortest arc');

for(const emote of ['wave','clap','heart','dance']) assert.equal(service.emote(created.room.code,guest.player.id,emote).ok,true);
const limited=service.emote(created.room.code,guest.player.id,'wave');
assert.equal(limited.reason,'rate-limit'); assert.ok(limited.retryAfter>0);
now+=4001; assert.equal(service.emote(created.room.code,guest.player.id,'wave').ok,true);
assert.equal(service.emote(created.room.code,guest.player.id,'script-tag').reason,'invalid-emote');

const oldToken=guest.reconnectToken;
assert.equal(service.disconnect(created.room.code,guest.player.id),true);
assert.equal(service.submitTransform(created.room.code,guest.player.id,{seq:0,transform:{}}).reason,'not-connected');
const reconnected=service.reconnect(oldToken); assert.equal(reconnected.ok,true);
assert.notEqual(reconnected.reconnectToken,oldToken,'reconnect tokens rotate after use');
assert.equal(service.reconnect(oldToken).reason,'invalid-token');
assert.equal(service.reconnect('forged.token').reason,'invalid-token');

const buffer=new SnapshotBuffer(2);
assert.equal(buffer.push({seq:1,serverTime:1,transform:{x:1}}),true);
assert.equal(buffer.push({seq:1,serverTime:2,transform:{x:2}}),false);
assert.equal(buffer.push({seq:2,serverTime:2,transform:{x:2}}),true);
assert.equal(buffer.push({seq:3,serverTime:3,transform:{x:3}}),true);
assert.equal(buffer.samples.length,2);

console.log('PASS: private rooms, join limits, snapshots, transform validation, interpolation, emote limits and reconnect rotation.');
