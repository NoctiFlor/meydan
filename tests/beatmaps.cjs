const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

const root=path.join(__dirname,'..','dist','beatmaps');
const files=fs.readdirSync(root).filter(name=>name.endsWith('.json')).sort();
const directions=new Set(['left','up','down','right']);
const ids=new Set();

assert.ok(files.length>=3,'at least three offline beatmaps are required');
for(const file of files){
 const bm=JSON.parse(fs.readFileSync(path.join(root,file),'utf8'));
 assert.equal(bm.id,path.basename(file,'.json'),`${file}: id must match filename`);
 assert.ok(!ids.has(bm.id),`${file}: duplicate id`);ids.add(bm.id);
 assert.equal(typeof bm.title,'string',`${file}: title`);assert.ok(bm.title.trim().length>=3,`${file}: title length`);
 assert.match(bm.artist,/Özgün/,`${file}: source must be marked original`);
 assert.equal(bm.audio,null,`${file}: current tracks must use offline synthesis`);
 assert.ok(Number.isFinite(bm.bpm)&&bm.bpm>=70&&bm.bpm<=180,`${file}: bpm range`);
 assert.ok(Number.isFinite(bm.offsetMs),`${file}: offset`);
 for(const name of ['easy','hard']){
  const diff=bm.difficulties?.[name];assert.ok(diff,`${file}: ${name}`);
  assert.ok(Number.isInteger(diff.level)&&diff.level>=1,`${file}: ${name} level`);
  assert.ok(Number.isInteger(diff.baseLength)&&diff.baseLength>=2&&diff.baseLength<=6,`${file}: ${name} baseLength`);
  assert.ok(Array.isArray(diff.patterns)&&diff.patterns.length>=8,`${file}: ${name} rounds`);
  for(const pattern of diff.patterns){
   assert.ok(Array.isArray(pattern)&&pattern.length>=diff.baseLength,`${file}: ${name} pattern length`);
   assert.ok(pattern.every(direction=>directions.has(direction)),`${file}: invalid direction`);
  }
 }
 assert.ok(bm.difficulties.hard.level>bm.difficulties.easy.level,`${file}: hard level ordering`);
 assert.ok(bm.difficulties.hard.baseLength>bm.difficulties.easy.baseLength,`${file}: hard length ordering`);
 console.log(`PASS: ${file} (${bm.bpm} BPM)`);
}
console.log(`ALL ${files.length} OFFLINE BEATMAPS VALID`);
