// Offline-only cosmetic economy. No real-money purchases or network dependency.
(() => {
  const CATEGORIES = new Set(['outfit', 'accessory', 'emote', 'effect']);

  function normalizeCatalog(input) {
    if (!Array.isArray(input)) throw new Error('Katalog bir liste olmalı');
    const ids = new Set();
    return input.map((raw, index) => {
      if (!raw || typeof raw !== 'object') throw new Error(`Geçersiz katalog öğesi: ${index}`);
      const id = typeof raw.id === 'string' ? raw.id.trim() : '';
      const category = typeof raw.category === 'string' ? raw.category : '';
      const price = Number(raw.price);
      if (!id || id.length > 80 || ids.has(id)) throw new Error(`Geçersiz veya yinelenen öğe kimliği: ${id}`);
      if (!CATEGORIES.has(category)) throw new Error(`Geçersiz kategori: ${category}`);
      if (!Number.isSafeInteger(price) || price < 0) throw new Error(`Geçersiz fiyat: ${id}`);
      ids.add(id);
      return Object.freeze({
        id,
        category,
        price,
        name: typeof raw.name === 'string' && raw.name.trim() ? raw.name.trim().slice(0, 40) : id,
        asset: typeof raw.asset === 'string' ? raw.asset.slice(0, 160) : '',
        starter: raw.starter === true
      });
    });
  }

  function cleanIds(values, validIds) {
    return [...new Set(Array.isArray(values) ? values.filter(id => typeof id === 'string' && validIds.has(id)) : [])];
  }

  class CosmeticEconomy {
    constructor(catalog, saved = {}) {
      this.catalog = normalizeCatalog(catalog);
      this.byId = new Map(this.catalog.map(item => [item.id, item]));
      const starter = this.catalog.filter(item => item.starter).map(item => item.id);
      const balance = Number(saved.balance);
      this.balance = Number.isSafeInteger(balance) && balance >= 0 ? balance : 0;
      this.owned = new Set([...starter, ...cleanIds(saved.owned, this.byId)]);
      this.equipped = {};
      if (saved.equipped && typeof saved.equipped === 'object') {
        for (const [category, id] of Object.entries(saved.equipped)) {
          const item = this.byId.get(id);
          if (CATEGORIES.has(category) && item?.category === category && this.owned.has(id)) this.equipped[category] = id;
        }
      }
    }
    getCatalog(category = null) {
      return this.catalog.filter(item => !category || item.category === category).map(item => ({
        ...item,
        owned: this.owned.has(item.id),
        equipped: this.equipped[item.category] === item.id
      }));
    }
    grantCoins(amount) {
      amount = Number(amount);
      if (!Number.isSafeInteger(amount) || amount <= 0 || this.balance > Number.MAX_SAFE_INTEGER - amount)
        return {ok:false, reason:'invalid_amount', balance:this.balance};
      this.balance += amount;
      return {ok:true, balance:this.balance};
    }
    purchase(id) {
      const item = this.byId.get(id);
      if (!item) return {ok:false, reason:'not_found', balance:this.balance};
      if (this.owned.has(id)) return {ok:false, reason:'already_owned', balance:this.balance};
      if (this.balance < item.price) return {ok:false, reason:'insufficient_balance', balance:this.balance, required:item.price};
      this.balance -= item.price;
      this.owned.add(id);
      return {ok:true, item:{...item}, balance:this.balance};
    }
    equip(id) {
      const item = this.byId.get(id);
      if (!item) return {ok:false, reason:'not_found'};
      if (!this.owned.has(id)) return {ok:false, reason:'not_owned'};
      this.equipped[item.category] = id;
      return {ok:true, category:item.category, id};
    }
    unequip(category) {
      if (!CATEGORIES.has(category)) return false;
      const existed = Object.hasOwn(this.equipped, category);
      delete this.equipped[category];
      return existed;
    }
    serialize() {
      return {
        version: 1,
        balance: this.balance,
        owned: [...this.owned].sort(),
        equipped: {...this.equipped}
      };
    }
  }

  globalThis.MeydanEconomy = {CATEGORIES, normalizeCatalog, CosmeticEconomy};
})();
