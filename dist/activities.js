(function(root,factory){
 const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 root.MeydanActivities=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';

 const STATES=Object.freeze({IDLE:'idle',ACTIVE:'active',COMPLETED:'completed',CANCELLED:'cancelled'});
 const DEFINITIONS=Object.freeze({
  'cafe-sit':{kind:'sit',duration:8,radius:2.2,capacity:4,cooldown:12,reward:{social:2,coins:1}},
  'fountain-photo':{kind:'photo',duration:3,radius:2.1,capacity:3,cooldown:18,reward:{social:3,coins:2}},
  'shore-bench':{kind:'sit',duration:10,radius:2.5,capacity:4,cooldown:10,reward:{social:2,energy:1}},
  'dance-invite':{kind:'dance',duration:12,radius:3,capacity:6,cooldown:20,reward:{social:5,coins:3,xp:8}},
 });

 const distanceSq=(a,b)=>{const x=a.x-b.x,z=a.z-b.z;return x*x+z*z};
 function cloneReward(reward){return Object.assign({},reward)}
 function createActivity(id,location,definition){
  const base=definition||DEFINITIONS[id];
  if(!base)throw new Error('unknown activity '+id);
  return {id,location:{x:location.x,z:location.z},definition:base,state:STATES.IDLE,participants:[],startedAt:null,endedAt:null,cooldownUntil:0,reward:null,reason:null};
 }
 function canStart(activity,actor,now){
  if(!actor||!actor.id||!actor.position)return {ok:false,reason:'invalid-actor'};
  if(activity.state===STATES.ACTIVE)return {ok:false,reason:'already-active'};
  if(now<activity.cooldownUntil)return {ok:false,reason:'cooldown'};
  if(distanceSq(actor.position,activity.location)>activity.definition.radius**2)return {ok:false,reason:'too-far'};
  return {ok:true};
 }
 function start(activity,actor,now,nearby){
  const allowed=canStart(activity,actor,now);if(!allowed.ok)return allowed;
  const roster=[actor].concat((nearby||[]).filter(item=>item&&item.id&&item.id!==actor.id&&item.position&&distanceSq(item.position,activity.location)<=activity.definition.radius**2));
  const unique=[];for(const item of roster)if(!unique.some(other=>other.id===item.id))unique.push(item);
  if(unique.length>activity.definition.capacity)return {ok:false,reason:'capacity'};
  activity.state=STATES.ACTIVE;activity.participants=unique.map(item=>item.id);activity.startedAt=now;activity.endedAt=null;activity.reward=null;activity.reason=null;
  return {ok:true,state:activity.state,participants:activity.participants.slice()};
 }
 function cancel(activity,now,reason){
  if(activity.state!==STATES.ACTIVE)return {ok:false,reason:'not-active'};
  activity.state=STATES.CANCELLED;activity.endedAt=now;activity.reward=null;activity.reason=reason||'cancelled';activity.cooldownUntil=now+Math.min(2,activity.definition.cooldown);
  return {ok:true,state:activity.state,reason:activity.reason};
 }
 function update(activity,now,positions){
  if(activity.state!==STATES.ACTIVE)return {changed:false,state:activity.state};
  const lookup=positions||{};
  for(const id of activity.participants){
   const position=lookup[id];
   if(position&&distanceSq(position,activity.location)>activity.definition.radius**2)return Object.assign({changed:true},cancel(activity,now,'left-area'));
  }
  if(now-activity.startedAt<activity.definition.duration)return {changed:false,state:activity.state,remaining:activity.definition.duration-(now-activity.startedAt)};
  activity.state=STATES.COMPLETED;activity.endedAt=now;activity.cooldownUntil=now+activity.definition.cooldown;activity.reward=cloneReward(activity.definition.reward);activity.reason=null;
  return {changed:true,ok:true,state:activity.state,reward:cloneReward(activity.reward),participants:activity.participants.slice()};
 }
 function reset(activity,now){
  if(activity.state===STATES.ACTIVE)return {ok:false,reason:'active'};
  if(now<activity.cooldownUntil)return {ok:false,reason:'cooldown'};
  activity.state=STATES.IDLE;activity.participants=[];activity.startedAt=null;activity.endedAt=null;activity.reward=null;activity.reason=null;
  return {ok:true,state:activity.state};
 }
 function applyReward(wallet,reward){
  const next=Object.assign({},wallet||{});for(const [key,value] of Object.entries(reward||{}))next[key]=(Number(next[key])||0)+value;return next;
 }
 return {STATES,DEFINITIONS,createActivity,canStart,start,cancel,update,reset,applyReward};
});
