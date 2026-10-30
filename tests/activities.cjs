const assert=require('node:assert/strict');
const A=require('../dist/activities.js');
const actor={id:'player',position:{x:-5.4,z:-2}};
let activity=A.createActivity('cafe-sit',{x:-5.5,z:-2.1});

assert.deepEqual(A.canStart(activity,{id:'far',position:{x:20,z:20}},0),{ok:false,reason:'too-far'});
assert.equal(A.start(activity,actor,0,[{id:'npc',position:{x:-5.2,z:-2.2}}]).ok,true);
assert.deepEqual(activity.participants,['player','npc']);
assert.equal(A.start(activity,actor,1).reason,'already-active');
assert.equal(A.update(activity,7,{player:actor.position,npc:{x:-5.2,z:-2.2}}).changed,false);
let done=A.update(activity,8,{player:actor.position,npc:{x:-5.2,z:-2.2}});
assert.equal(done.state,A.STATES.COMPLETED);assert.deepEqual(done.reward,{social:2,coins:1});
assert.equal(A.reset(activity,9).reason,'cooldown');
assert.equal(A.reset(activity,20).ok,true);

activity=A.createActivity('fountain-photo',{x:6,z:5});
assert.equal(A.start(activity,{id:'player',position:{x:6,z:5}},30).ok,true);
let cancelled=A.update(activity,31,{player:{x:9,z:9}});
assert.equal(cancelled.state,A.STATES.CANCELLED);assert.equal(activity.reason,'left-area');
assert.equal(activity.reward,null);

activity=A.createActivity('dance-invite',{x:1.5,z:-1.5});
const crowd=Array.from({length:6},(_,i)=>({id:'n'+i,position:{x:1.5,z:-1.5}}));
assert.equal(A.start(activity,{id:'player',position:{x:1.5,z:-1.5}},50,crowd).reason,'capacity');
assert.equal(A.start(activity,{id:'player',position:{x:1.5,z:-1.5}},50,crowd.slice(0,5)).ok,true);
assert.equal(A.cancel(activity,51,'player-exit').ok,true);
assert.equal(A.cancel(activity,52).reason,'not-active');

assert.deepEqual(A.applyReward({coins:4},{coins:3,xp:8}),{coins:7,xp:8});
console.log('PASS: activity proximity, capacity, start, cancel, completion, rewards and cooldowns.');
