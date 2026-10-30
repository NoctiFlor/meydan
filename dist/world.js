(function(root,factory){
 const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 root.MeydanWorld=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';

 const WORLD_VERSION=1;
 const plaza={
  id:'sahil-meydani',version:WORLD_VERSION,
  bounds:{minX:-12,maxX:12,minZ:-4.7,maxZ:15.5},
  spawn:{x:0,z:3,facing:Math.PI},
  zones:[
   {id:'central',name:'Sahil Meydanı',bounds:{minX:-2,maxX:9,minZ:-4.7,maxZ:8},music:'plaza'},
   {id:'cafe',name:'Kafe Sokağı',bounds:{minX:-12,maxX:-2,minZ:-4.7,maxZ:2},music:'cafe'},
   {id:'promenade',name:'Sahil Yolu',bounds:{minX:-12,maxX:12,minZ:8,maxZ:15.5},music:'shore'},
  ],
  landmarks:[
   {id:'dance-stage',type:'stage',x:1.5,z:-1.5,radius:2.65,label:'MEYDAN BEAT'},
   {id:'fountain',type:'fountain',x:6,z:5,radius:1.3,label:'Meydan Çeşmesi'},
   {id:'cafe-front',type:'shop',x:-5.9,z:-5.1,radius:1.5,label:'Sahil Kafe'},
   {id:'fashion-front',type:'shop',x:-.1,z:-5.55,radius:1.5,label:'Moda Atölyesi'},
   {id:'club-front',type:'club',x:5.55,z:-5.1,radius:1.6,label:'Club Liman'},
  ],
  obstacles:[
   [-8.9,-3,-8,-5.05],[-2.85,2.65,-9,-5.55],[2.8,8.4,-8,-5.05],
   [-6.6,-4.4,-3.1,-1.1],[-8.1,-6.1,-4.3,-2.3],[-4.9,-2.9,-4.25,-2.25],
   [-2.98,-2.02,-5.1,-4.1],[2.2,3.2,-5,-4],[7.2,8.2,-2.9,-1.9],[4.7,7.3,3.7,6.3],
  ],
  activities:[
   {id:'stage-dance',kind:'dance',x:1.5,z:-1.5,radius:3,capacity:6},
   {id:'cafe-chat',kind:'chat',x:-5.5,z:-2.1,radius:2.2,capacity:4},
   {id:'fountain-photo',kind:'photo',x:6,z:5,radius:2.1,capacity:3},
   {id:'shore-sit',kind:'sit',x:3,z:10,radius:2.5,capacity:4},
  ],
  npcSpawns:[
   {id:'npc-stage-a',x:.1,z:-.7,role:'dancer',activity:'stage-dance'},
   {id:'npc-stage-b',x:2.8,z:-1.1,role:'dancer',activity:'stage-dance'},
   {id:'npc-cafe-a',x:-5.4,z:-1.2,role:'social',activity:'cafe-chat'},
   {id:'npc-cafe-b',x:-7,z:-2.1,role:'social',activity:'cafe-chat'},
   {id:'npc-fountain',x:4.3,z:5.5,role:'visitor',activity:'fountain-photo'},
   {id:'npc-shore-a',x:2.3,z:9.5,role:'visitor',activity:'shore-sit'},
   {id:'npc-shore-b',x:7.8,z:10.6,role:'visitor',activity:'shore-sit'},
   {id:'npc-roamer',x:-1,z:5,role:'roamer',activity:null},
  ],
  lod:{near:12,medium:24,far:42},
  budgets:{
   low:{pixelRatio:1,shadowMap:512,maxNpc:6,maxAnimatedNpc:3,maxPointLights:2,maxDrawCalls:180},
   medium:{pixelRatio:1.35,shadowMap:1024,maxNpc:10,maxAnimatedNpc:6,maxPointLights:4,maxDrawCalls:260},
   high:{pixelRatio:1.7,shadowMap:2048,maxNpc:16,maxAnimatedNpc:10,maxPointLights:6,maxDrawCalls:380},
  },
 };

 function inside(bounds,x,z){return x>=bounds.minX&&x<=bounds.maxX&&z>=bounds.minZ&&z<=bounds.maxZ}
 function findZone(world,x,z){return world.zones.find(zone=>inside(zone.bounds,x,z))||null}
 function distanceSq(a,b){const dx=a.x-b.x,dz=a.z-b.z;return dx*dx+dz*dz}
 function nearestActivity(world,position,kind){
  const choices=kind?world.activities.filter(item=>item.kind===kind):world.activities;
  return choices.reduce((best,item)=>!best||distanceSq(position,item)<distanceSq(position,best)?item:best,null);
 }
 function lodBand(world,position,target){
  const distance=Math.sqrt(distanceSq(position,target));
  return distance<=world.lod.near?'near':distance<=world.lod.medium?'medium':distance<=world.lod.far?'far':'hidden';
 }
 function budgetFor(world,quality){return world.budgets[quality]||world.budgets.medium}
 function blocked(world,x,z,padding){
  const p=padding||0;
  if(!inside(world.bounds,x,z))return true;
  return world.obstacles.some(o=>x>o[0]-p&&x<o[1]+p&&z>o[2]-p&&z<o[3]+p);
 }
 function validateWorld(world){
  const errors=[],ids=new Set();
  function unique(items,label){for(const item of items){if(!item.id)errors.push(label+' missing id');else if(ids.has(item.id))errors.push('duplicate id '+item.id);else ids.add(item.id)}}
  if(!world||typeof world!=='object')return ['world missing'];
  if(!world.bounds||world.bounds.minX>=world.bounds.maxX||world.bounds.minZ>=world.bounds.maxZ)errors.push('invalid bounds');
  for(const key of['zones','landmarks','activities','npcSpawns','obstacles'])if(!Array.isArray(world[key]))errors.push(key+' missing');
  if(errors.length)return errors;
  unique(world.zones,'zone');unique(world.landmarks,'landmark');unique(world.activities,'activity');unique(world.npcSpawns,'npc');
  for(const spawn of world.npcSpawns){
   if(!inside(world.bounds,spawn.x,spawn.z))errors.push('npc outside bounds '+spawn.id);
   if(spawn.activity&&!world.activities.some(item=>item.id===spawn.activity))errors.push('unknown activity '+spawn.activity);
  }
  for(const name of['low','medium','high'])if(!world.budgets||!world.budgets[name])errors.push('missing budget '+name);
  if(!world.lod||!(world.lod.near<world.lod.medium&&world.lod.medium<world.lod.far))errors.push('invalid lod bands');
  return errors;
 }

 return {WORLD_VERSION,plaza,inside,findZone,nearestActivity,lodBand,budgetFor,blocked,validateWorld};
});
