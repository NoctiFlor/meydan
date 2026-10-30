const assert = require('node:assert/strict');
require('../dist/progression.js');
const {CURRENT_VERSION, ProgressionStore} = globalThis.MeydanProgression;

class MemoryStorage {
  constructor(seed = {}) { this.values = new Map(Object.entries(seed)); }
  getItem(key) { return this.values.has(key) ? this.values.get(key) : null; }
  setItem(key, value) { this.values.set(key, String(value)); }
  removeItem(key) { this.values.delete(key); }
}

let storage = new MemoryStorage({'save':'not-json'});
let store = new ProgressionStore(storage, 'save', () => 1234);
let data = store.load();
assert.equal(data.version, CURRENT_VERSION);
assert.equal(data.profile.level, 1);
assert.equal(data.profile.created, false);
assert.equal(storage.getItem('save.corrupt'), 'not-json');

storage = new MemoryStorage({'save':JSON.stringify({highScore:9000, settings:{sound:false, quality:'impossible'}})});
store = new ProgressionStore(storage, 'save', () => 2000);
data = store.load();
assert.equal(data.scores.meydan_demo.easy.score, 9000);
assert.equal(data.settings.sound, false);
assert.equal(data.settings.quality, 'auto');
assert.equal(data.version, CURRENT_VERSION);
assert.equal(data.profile.created, true, 'legacy saves remain continuable after the menu migration');
assert.equal(data.profile.avatar, 'classic');

assert.equal(store.recordScore('meydan_demo', 'easy', {score:12000, accuracy:.91, combo:14, grade:'A'}), true);
assert.equal(store.recordScore('meydan_demo', 'easy', {score:8000, accuracy:.99, combo:18, grade:'S'}), false);
data = store.snapshot();
assert.equal(data.scores.meydan_demo.easy.score, 12000);
assert.equal(data.stats.plays, 2);
assert.equal(data.stats.totalScore, 20000);
assert.equal(data.stats.bestCombo, 18);
assert.ok(data.profile.xp > 0 && data.profile.coins > 0);

assert.equal(store.unlock('cosmetic:blue_jacket'), true);
assert.equal(store.unlock('cosmetic:blue_jacket'), false);
assert.deepEqual(store.updateSettings({quality:'low', cameraSensitivity:99}), {sound:false, quality:'low', cameraSensitivity:2.5});
assert.equal(store.updateProfile({name:'  <Ada>   Deniz  ', avatar:'night'}).name, 'Ada Deniz');
assert.equal(store.snapshot().profile.avatar, 'night');
assert.equal(JSON.parse(storage.getItem('save')).updatedAt, 2000);

data = store.reset();
assert.equal(storage.getItem('save'), null);
assert.deepEqual(data.unlocks, ['song:meydan_demo']);
assert.equal(data.profile.created, false);

const created = store.createProfile('  Hilal  ', 'sport');
assert.equal(created.ok, true);
assert.deepEqual(created.profile, {created:true, name:'Hilal', avatar:'sport', level:1, xp:0, coins:0});
assert.equal(store.createProfile('   ', 'classic').reason, 'invalid-name');
assert.equal(store.createProfile('Bahri', 'unknown').reason, 'invalid-avatar');

const brokenStorage = {getItem(){throw new Error('denied')},setItem(){throw new Error('denied')},removeItem(){}};
store = new ProgressionStore(brokenStorage, 'save');
assert.equal(store.load().version, CURRENT_VERSION);
assert.equal(store.save(), false);

console.log('PASS: versioned saves, migration, corruption recovery, scores, unlocks, settings and storage failure.');
