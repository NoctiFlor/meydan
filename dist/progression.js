// Versioned offline progression. Renderer-independent and exercised in Node.
(() => {
  const CURRENT_VERSION = 3;
  const DEFAULT_KEY = 'meydan.progression';
  const ALLOWED_QUALITIES = new Set(['low', 'medium', 'high', 'auto']);
  const ALLOWED_AVATARS = new Set(['classic', 'sport', 'night']);

  function defaults() {
    return {
      version: CURRENT_VERSION,
      profile: {created: false, name: 'Oyuncu', avatar: 'classic', level: 1, xp: 0, coins: 0},
      settings: {sound: true, quality: 'auto', cameraSensitivity: 1},
      scores: {},
      unlocks: ['song:meydan_demo'],
      stats: {plays: 0, totalScore: 0, bestCombo: 0},
      updatedAt: 0
    };
  }

  function finite(value, fallback, min = -Infinity, max = Infinity) {
    value = Number(value);
    return Number.isFinite(value) ? Math.min(max, Math.max(min, value)) : fallback;
  }

  function migrate(raw) {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return defaults();
    let data = raw;
    // Early prototypes stored score/settings directly without a version.
    if (!Number.isInteger(data.version)) {
      data = {
        version: 1,
        settings: data.settings,
        scores: data.scores || (Number.isFinite(data.highScore) ? {meydan_demo:{easy:{score:data.highScore}}} : {}),
        unlocks: data.unlocks,
        profile: data.profile
      };
    }
    if (data.version === 1) data = {...data, version: 2, stats: data.stats || {}};
    // Every v2 save came from a player who had already entered the old direct-to-plaza build.
    if (data.version === 2) data = {...data, version: 3, profile:{...data.profile, created:true, avatar:data.profile?.avatar || 'classic'}};
    return data.version === CURRENT_VERSION ? data : defaults();
  }

  function normalizeProfileName(value) {
    return String(value || '').replace(/[<>\u0000-\u001f\u007f]/g, '').trim().replace(/\s+/g, ' ').slice(0, 24);
  }

  function normalize(raw) {
    const base = defaults();
    const data = migrate(raw);
    const profile = data.profile && typeof data.profile === 'object' ? data.profile : {};
    const settings = data.settings && typeof data.settings === 'object' ? data.settings : {};
    const stats = data.stats && typeof data.stats === 'object' ? data.stats : {};
    const scores = {};
    if (data.scores && typeof data.scores === 'object' && !Array.isArray(data.scores)) {
      for (const [song, difficulties] of Object.entries(data.scores)) {
        if (!song || !difficulties || typeof difficulties !== 'object' || Array.isArray(difficulties)) continue;
        scores[song] = {};
        for (const [difficulty, entry] of Object.entries(difficulties)) {
          if (!entry || typeof entry !== 'object') continue;
          scores[song][difficulty] = {
            score: finite(entry.score, 0, 0),
            accuracy: finite(entry.accuracy, 0, 0, 1),
            combo: finite(entry.combo, 0, 0),
            grade: typeof entry.grade === 'string' ? entry.grade.slice(0, 3) : 'D',
            playedAt: finite(entry.playedAt, 0, 0)
          };
        }
      }
    }
    const quality = ALLOWED_QUALITIES.has(settings.quality) ? settings.quality : base.settings.quality;
    return {
      version: CURRENT_VERSION,
      profile: {
        created: profile.created === true,
        name: normalizeProfileName(profile.name) || base.profile.name,
        avatar: ALLOWED_AVATARS.has(profile.avatar) ? profile.avatar : base.profile.avatar,
        level: Math.floor(finite(profile.level, 1, 1, 999)),
        xp: Math.floor(finite(profile.xp, 0, 0)),
        coins: Math.floor(finite(profile.coins, 0, 0))
      },
      settings: {
        sound: settings.sound !== false,
        quality,
        cameraSensitivity: finite(settings.cameraSensitivity, 1, .35, 2.5)
      },
      scores,
      unlocks: [...new Set(Array.isArray(data.unlocks) ? data.unlocks.filter(x => typeof x === 'string' && x.length < 80) : base.unlocks)],
      stats: {
        plays: Math.floor(finite(stats.plays, 0, 0)),
        totalScore: Math.floor(finite(stats.totalScore, 0, 0)),
        bestCombo: Math.floor(finite(stats.bestCombo, 0, 0))
      },
      updatedAt: finite(data.updatedAt, 0, 0)
    };
  }

  class ProgressionStore {
    constructor(storage = globalThis.localStorage, key = DEFAULT_KEY, now = () => Date.now()) {
      this.storage = storage;
      this.key = key;
      this.now = now;
      this.data = defaults();
    }
    load() {
      let raw = null;
      try { raw = this.storage?.getItem(this.key); }
      catch { this.data = defaults(); return this.snapshot(); }
      if (!raw) { this.data = defaults(); return this.snapshot(); }
      try { this.data = normalize(JSON.parse(raw)); }
      catch {
        try { this.storage?.setItem(`${this.key}.corrupt`, raw.slice(0, 10000)); } catch {}
        this.data = defaults();
      }
      return this.snapshot();
    }
    save() {
      this.data = normalize({...this.data, updatedAt:this.now()});
      try { this.storage?.setItem(this.key, JSON.stringify(this.data)); return true; }
      catch { return false; }
    }
    snapshot() { return JSON.parse(JSON.stringify(this.data)); }
    reset() {
      this.data = defaults();
      try { this.storage?.removeItem(this.key); } catch {}
      return this.snapshot();
    }
    updateSettings(patch = {}) {
      this.data.settings = {...this.data.settings, ...patch};
      this.data = normalize(this.data);
      this.save();
      return {...this.data.settings};
    }
    updateProfile(patch = {}) {
      this.data.profile = {...this.data.profile, ...patch};
      this.data = normalize(this.data);
      this.save();
      return {...this.data.profile};
    }
    createProfile(name, avatar = 'classic') {
      const cleanName = normalizeProfileName(name);
      if (!cleanName) return {ok:false, reason:'invalid-name'};
      if (!ALLOWED_AVATARS.has(avatar)) return {ok:false, reason:'invalid-avatar'};
      this.data = defaults();
      this.data.profile = {...this.data.profile, created:true, name:cleanName, avatar};
      return {ok:this.save(), profile:{...this.data.profile}};
    }
    unlock(id) {
      if (typeof id !== 'string' || !id || id.length >= 80) return false;
      if (this.data.unlocks.includes(id)) return false;
      this.data.unlocks.push(id); this.save(); return true;
    }
    recordScore(song, difficulty, result = {}) {
      if (typeof song !== 'string' || !song || typeof difficulty !== 'string' || !difficulty) return false;
      const entry = {
        score: Math.floor(finite(result.score, 0, 0)),
        accuracy: finite(result.accuracy, 0, 0, 1),
        combo: Math.floor(finite(result.combo, 0, 0)),
        grade: typeof result.grade === 'string' ? result.grade.slice(0, 3) : 'D',
        playedAt: this.now()
      };
      const previous = this.data.scores[song]?.[difficulty];
      if (!this.data.scores[song]) this.data.scores[song] = {};
      if (!previous || entry.score > previous.score) this.data.scores[song][difficulty] = entry;
      this.data.stats.plays++;
      this.data.stats.totalScore += entry.score;
      this.data.stats.bestCombo = Math.max(this.data.stats.bestCombo, entry.combo);
      const xpGain = Math.max(1, Math.floor(entry.score / 1000));
      this.data.profile.xp += xpGain;
      this.data.profile.coins += Math.max(1, Math.floor(entry.score / 5000));
      this.data.profile.level = 1 + Math.floor(this.data.profile.xp / 100);
      this.save();
      return !previous || entry.score > previous.score;
    }
  }

  globalThis.MeydanProgression = {CURRENT_VERSION, ALLOWED_AVATARS, defaults, normalize, normalizeProfileName, ProgressionStore};
})();
