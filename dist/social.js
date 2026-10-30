// Deterministic offline social-NPC rules. Renderer-independent and Node-testable.
(() => {
  const STATES = Object.freeze({IDLE:'idle', WANDER:'wander', CHAT:'chat', INVITE:'dance-invite', DANCE:'dance'});

  function seededRandom(seed = 1) {
    let value = (Number(seed) >>> 0) || 1;
    return () => {
      value = (Math.imul(value, 1664525) + 1013904223) >>> 0;
      return value / 4294967296;
    };
  }

  function distance(a, b) { return Math.hypot((a.x || 0) - (b.x || 0), (a.z || 0) - (b.z || 0)); }
  function clamp(value, low, high) { return Math.max(low, Math.min(high, value)); }

  const DIALOGUE = Object.freeze({
    greeting:['Selam! Meydana yeni mi geldin?', 'Akşam ritmi birazdan başlıyor.', 'Sahne bugün çok güzel görünüyor.'],
    busy:['Birazdan konuşalım.', 'Şu an ritmi kaçırmak istemiyorum.'],
    invite:['Birlikte bir dans turu deneyelim mi?', 'Sahne boşaldı, dansa katılmak ister misin?'],
    afterDance:['Güzel turdu!', 'Ritmi yakaladın, tekrar görüşürüz.']
  });

  class SocialWorld {
    constructor(seed = 1, definitions = []) {
      this.random = seededRandom(seed);
      this.time = 0;
      this.events = [];
      this.npcs = definitions.map((entry, index) => this.createNpc(entry, index));
    }

    createNpc(entry, index) {
      const home = {x:Number(entry.x) || 0, z:Number(entry.z) || 0};
      return {
        id:String(entry.id || `npc-${index + 1}`),
        name:String(entry.name || `Meydanlı ${index + 1}`),
        personality:entry.personality || 'friendly',
        state:STATES.IDLE,
        x:home.x, z:home.z, home,
        target:{...home},
        stateUntil:1 + this.random() * 2,
        cooldownUntil:0,
        interacted:false
      };
    }

    emit(type, npc, extra = {}) {
      const event = {type, npcId:npc.id, npcName:npc.name, time:this.time, ...extra};
      this.events.push(event);
      return event;
    }

    choose(list) { return list[Math.floor(this.random() * list.length) % list.length]; }

    setState(npc, state, duration) {
      npc.state = state;
      npc.stateUntil = this.time + duration;
      this.emit('state', npc, {state});
    }

    chooseWanderTarget(npc) {
      const angle = this.random() * Math.PI * 2;
      const radius = 1 + this.random() * 2.5;
      npc.target = {x:npc.home.x + Math.cos(angle) * radius, z:npc.home.z + Math.sin(angle) * radius};
      this.setState(npc, STATES.WANDER, 2.5 + this.random() * 2.5);
    }

    update(dt, player = {x:999, z:999}) {
      if (!Number.isFinite(dt) || dt < 0) throw new Error('Geçersiz sosyal dünya süresi');
      dt = Math.min(dt, .25);
      this.time += dt;
      for (const npc of this.npcs) {
        if (npc.state === STATES.WANDER) {
          const dx = npc.target.x - npc.x, dz = npc.target.z - npc.z;
          const remaining = Math.hypot(dx, dz);
          if (remaining > .02) {
            const step = Math.min(remaining, dt * .7);
            npc.x += dx / remaining * step; npc.z += dz / remaining * step;
          }
        }
        if (this.time < npc.stateUntil) continue;
        if (npc.state === STATES.CHAT || npc.state === STATES.INVITE) {
          npc.cooldownUntil = this.time + 4;
          this.setState(npc, STATES.IDLE, 1.5 + this.random() * 2);
        } else if (npc.state === STATES.DANCE) {
          npc.cooldownUntil = this.time + 6;
          this.emit('dialogue', npc, {text:this.choose(DIALOGUE.afterDance)});
          this.setState(npc, STATES.IDLE, 2);
        } else if (npc.state === STATES.WANDER || npc.state === STATES.IDLE) {
          if (distance(npc, player) < 2.4 && this.time >= npc.cooldownUntil && this.random() < .22) {
            this.setState(npc, STATES.INVITE, 3);
            this.emit('dialogue', npc, {text:this.choose(DIALOGUE.invite)});
          } else if (this.random() < .62) this.chooseWanderTarget(npc);
          else this.setState(npc, STATES.IDLE, 1.5 + this.random() * 2.5);
        }
      }
    }

    nearest(player, radius = 2.4) {
      return this.npcs.reduce((best, npc) => {
        const d = distance(player, npc);
        return d <= radius && (!best || d < best.distance) ? {npc, distance:d} : best;
      }, null);
    }

    interact(player, npcId = null) {
      const selected = npcId ? this.npcs.find(n => n.id === npcId) : this.nearest(player)?.npc;
      if (!selected || distance(player, selected) > 2.4) return {type:'none', text:'Yakında konuşabileceğin biri yok.'};
      if (this.time < selected.cooldownUntil || selected.state === STATES.CHAT || selected.state === STATES.DANCE) {
        return this.emit('dialogue', selected, {text:this.choose(DIALOGUE.busy), outcome:'busy'});
      }
      selected.interacted = true;
      if (selected.state === STATES.INVITE) {
        this.setState(selected, STATES.DANCE, 5);
        return this.emit('activity', selected, {activity:'dance', text:'Birlikte dans turu başladı.'});
      }
      this.setState(selected, STATES.CHAT, 3);
      return this.emit('dialogue', selected, {text:this.choose(DIALOGUE.greeting), outcome:'greeting'});
    }

    takeEvents() { return this.events.splice(0); }
    snapshot() {
      return this.npcs.map(n => ({id:n.id, name:n.name, state:n.state, x:n.x, z:n.z,
        cooldown:clamp(n.cooldownUntil - this.time, 0, Infinity)}));
    }
  }

  globalThis.MeydanSocial = {STATES, SocialWorld, seededRandom};
})();
