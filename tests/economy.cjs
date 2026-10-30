const assert = require('node:assert/strict');
require('../dist/economy.js');
const {normalizeCatalog, CosmeticEconomy} = globalThis.MeydanEconomy;

const catalog = [
  {id:'outfit:starter', category:'outfit', price:0, name:'Meydan Başlangıç', starter:true},
  {id:'outfit:blue', category:'outfit', price:80, name:'Mavi Ceket', asset:'outfits/blue'},
  {id:'emote:wave', category:'emote', price:25, name:'Selam Ver'},
  {id:'effect:gold', category:'effect', price:120, name:'Altın Ritim'}
];

assert.throws(() => normalizeCatalog([{id:'x',category:'outfit',price:-1}]), /fiyat/);
assert.throws(() => normalizeCatalog([{id:'x',category:'outfit',price:0},{id:'x',category:'emote',price:2}]), /yinelenen/);
assert.throws(() => normalizeCatalog([{id:'x',category:'weapon',price:0}]), /kategori/);

let economy = new CosmeticEconomy(catalog, {balance:50});
assert.equal(economy.getCatalog().find(i => i.id === 'outfit:starter').owned, true);
assert.deepEqual(economy.purchase('missing'), {ok:false,reason:'not_found',balance:50});
assert.deepEqual(economy.purchase('outfit:starter'), {ok:false,reason:'already_owned',balance:50});
assert.deepEqual(economy.purchase('outfit:blue'), {ok:false,reason:'insufficient_balance',balance:50,required:80});
assert.deepEqual(economy.equip('outfit:blue'), {ok:false,reason:'not_owned'});

assert.deepEqual(economy.grantCoins(50), {ok:true,balance:100});
assert.equal(economy.grantCoins(-2).reason, 'invalid_amount');
let purchase = economy.purchase('outfit:blue');
assert.equal(purchase.ok, true);
assert.equal(economy.balance, 20);
assert.equal(economy.purchase('outfit:blue').reason, 'already_owned');
assert.deepEqual(economy.equip('outfit:blue'), {ok:true,category:'outfit',id:'outfit:blue'});
assert.equal(economy.unequip('outfit'), true);
assert.equal(economy.unequip('outfit'), false);

assert.equal(economy.grantCoins(25).ok, true);
assert.equal(economy.purchase('emote:wave').ok, true);
assert.equal(economy.equip('emote:wave').ok, true);
const saved = economy.serialize();
assert.equal(saved.version, 1);
assert.equal(saved.balance, 20);
assert.deepEqual(saved.equipped, {emote:'emote:wave'});

economy = new CosmeticEconomy(catalog, {
  balance: saved.balance,
  owned:[...saved.owned, 'unknown:item'],
  equipped:{...saved.equipped, outfit:'unknown:item', weapon:'outfit:blue'}
});
assert.deepEqual(economy.serialize(), saved);
assert.equal(economy.getCatalog('emote').length, 1);

console.log('PASS: catalog validation, offline coin grants, purchase/equip rules, duplicates, balance and serialization.');
