// Offline-testable private-room protocol rules. No sockets, accounts or public service.
(() => {
  const CODE_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  const EMOTE_WINDOW_MS = 4000;
  const EMOTE_LIMIT = 4;

  function seededRandom(seed = 1) {
    let value = (Number(seed) >>> 0) || 1;
    return () => ((value = (Math.imul(value, 1103515245) + 12345) >>> 0) / 4294967296);
  }

  function finite(value, fallback = 0) { return Number.isFinite(value) ? value : fallback; }
  function normalizeName(name) {
    return String(name || 'Oyuncu').replace(/[<>\u0000-\u001f]/g, '').trim().slice(0, 24) || 'Oyuncu';
  }
  function normalizeTransform(transform = {}) {
    return {
      x:finite(transform.x), y:finite(transform.y, .1), z:finite(transform.z),
      yaw:finite(transform.yaw), state:['idle','walk','run','dance'].includes(transform.state) ? transform.state : 'idle'
    };
  }
  function interpolateTransform(a, b, renderAt) {
    if (!a) return b ? {...b.transform} : null;
    if (!b || b.serverTime <= a.serverTime) return {...a.transform};
    const alpha = Math.max(0, Math.min(1, (renderAt - a.serverTime) / (b.serverTime - a.serverTime)));
    const angleDelta = Math.atan2(Math.sin(b.transform.yaw-a.transform.yaw), Math.cos(b.transform.yaw-a.transform.yaw));
    return {
      x:a.transform.x+(b.transform.x-a.transform.x)*alpha,
      y:a.transform.y+(b.transform.y-a.transform.y)*alpha,
      z:a.transform.z+(b.transform.z-a.transform.z)*alpha,
      yaw:a.transform.yaw+angleDelta*alpha,
      state:alpha < .5 ? a.transform.state : b.transform.state
    };
  }

  class SnapshotBuffer {
    constructor(limit = 8) { this.limit = limit; this.samples = []; }
    push(snapshot) {
      if (!snapshot || !Number.isInteger(snapshot.seq) || !Number.isFinite(snapshot.serverTime)) return false;
      const last = this.samples[this.samples.length-1];
      if (last && (snapshot.seq <= last.seq || snapshot.serverTime < last.serverTime)) return false;
      this.samples.push({seq:snapshot.seq, serverTime:snapshot.serverTime, transform:normalizeTransform(snapshot.transform)});
      if (this.samples.length > this.limit) this.samples.splice(0, this.samples.length-this.limit);
      return true;
    }
    sample(renderAt) {
      if (!this.samples.length) return null;
      let before=this.samples[0], after=null;
      for (const sample of this.samples) {
        if (sample.serverTime <= renderAt) before=sample;
        else { after=sample; break; }
      }
      return interpolateTransform(before, after, renderAt);
    }
  }

  class PrivateRoomService {
    constructor(seed = 1, options = {}) {
      this.random = seededRandom(seed); this.rooms = new Map(); this.clock = options.clock || (()=>Date.now());
      this.maxPlayers = options.maxPlayers || 8; this.tokenSerial = 0;
    }
    randomText(length) {
      let out=''; for(let i=0;i<length;i++) out+=CODE_ALPHABET[Math.floor(this.random()*CODE_ALPHABET.length)];
      return out;
    }
    uniqueCode() {
      for(let i=0;i<64;i++){const code=this.randomText(6);if(!this.rooms.has(code))return code;}
      throw new Error('Oda kodu üretilemedi');
    }
    issueToken(code, playerId) { return `${code}.${playerId}.${++this.tokenSerial}.${this.randomText(10)}`; }
    create(name) {
      const code=this.uniqueCode(); const room={code, createdAt:this.clock(), players:new Map(), events:[]};
      this.rooms.set(code,room); const joined=this.join(code,name); room.hostId=joined.player.id;
      return {room:{code,hostId:room.hostId},...joined};
    }
    join(rawCode,name) {
      const code=String(rawCode||'').trim().toUpperCase(), room=this.rooms.get(code);
      if(!room) throw new Error('Oda bulunamadı');
      if(room.players.size>=this.maxPlayers) throw new Error('Oda dolu');
      const id=`p${room.players.size+1}-${this.randomText(4)}`;
      const player={id,name:normalizeName(name),connected:true,lastSeq:-1,transform:normalizeTransform(),emoteTimes:[],buffer:new SnapshotBuffer()};
      player.reconnectToken=this.issueToken(code,id); room.players.set(id,player);
      room.events.push({type:'join',playerId:id,at:this.clock()});
      return {player:this.publicPlayer(player),reconnectToken:player.reconnectToken};
    }
    publicPlayer(player) { return {id:player.id,name:player.name,connected:player.connected,transform:{...player.transform}}; }
    roomState(code) {
      const room=this.rooms.get(code); if(!room) return null;
      return {code:room.code,hostId:room.hostId,players:[...room.players.values()].map(p=>this.publicPlayer(p))};
    }
    getPlayer(code,id) { const room=this.rooms.get(code); return room?.players.get(id); }
    submitTransform(code,id,packet) {
      const player=this.getPlayer(code,id); if(!player||!player.connected) return {ok:false,reason:'not-connected'};
      if(!Number.isInteger(packet?.seq)||packet.seq<=player.lastSeq) return {ok:false,reason:'stale-sequence'};
      if(packet.seq-player.lastSeq>120&&player.lastSeq>=0) return {ok:false,reason:'sequence-jump'};
      const transform=normalizeTransform(packet.transform), dx=transform.x-player.transform.x, dz=transform.z-player.transform.z;
      if(Math.hypot(dx,dz)>12) return {ok:false,reason:'transform-jump'};
      player.lastSeq=packet.seq; player.transform=transform;
      player.buffer.push({seq:packet.seq,serverTime:this.clock(),transform});
      return {ok:true,seq:packet.seq,transform:{...transform}};
    }
    emote(code,id,emote) {
      const player=this.getPlayer(code,id), now=this.clock();
      if(!player||!player.connected) return {ok:false,reason:'not-connected'};
      player.emoteTimes=player.emoteTimes.filter(t=>now-t<EMOTE_WINDOW_MS);
      if(player.emoteTimes.length>=EMOTE_LIMIT) return {ok:false,reason:'rate-limit',retryAfter:EMOTE_WINDOW_MS-(now-player.emoteTimes[0])};
      const safe=String(emote||'').toLowerCase(); if(!['wave','clap','heart','dance'].includes(safe)) return {ok:false,reason:'invalid-emote'};
      player.emoteTimes.push(now); return {ok:true,emote:safe,playerId:id,at:now};
    }
    disconnect(code,id) {
      const player=this.getPlayer(code,id); if(!player) return false;
      player.connected=false; return true;
    }
    reconnect(token) {
      const [code,id]=String(token||'').split('.'), player=this.getPlayer(code,id);
      if(!player||player.reconnectToken!==token) return {ok:false,reason:'invalid-token'};
      player.connected=true; player.reconnectToken=this.issueToken(code,id);
      return {ok:true,roomCode:code,player:this.publicPlayer(player),reconnectToken:player.reconnectToken};
    }
  }

  globalThis.MeydanNetwork={PrivateRoomService,SnapshotBuffer,interpolateTransform,normalizeTransform};
})();
