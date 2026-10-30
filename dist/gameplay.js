// Shared, deterministic gameplay rules; also exercised without a renderer in Node.
(() => {
  function analogVector(x, y, radius, deadzone = 0.12) {
    const distance = Math.hypot(x, y);
    if (!Number.isFinite(distance) || radius <= 0 || distance <= radius * deadzone)
      return {x:0, y:0, strength:0, thumbX:0, thumbY:0};
    const strength = (Math.min(1, distance / radius) - deadzone) / (1 - deadzone);
    const thumbScale = Math.min(radius, distance) / distance;
    return {x:x/distance*strength, y:y/distance*strength, strength,
      thumbX:x*thumbScale, thumbY:y*thumbScale};
  }

  class SequenceDance {
    constructor(bpm, patterns, baseLength = 2, offset = 0) {
      if (!(bpm > 0 && Number.isFinite(bpm)) || !patterns.length || offset < 0)
        throw new Error('Geçersiz ritim düzeni');
      if (patterns.some(p => !Array.isArray(p) || !p.length || p.some(d => !Number.isInteger(d) || d < 0 || d > 3)))
        throw new Error('Geçersiz yön dizisi');
      this.beat = 60 / bpm;
      this.patterns = patterns.map(p => [...p]);
      this.baseLength = baseLength;
      this.offset = offset;
      this.window = Math.min(0.35, this.beat * 0.55);
      this.index = 0; this.level = 1; this.combo = 0; this.position = 0;
      this.closed = false; this.events = []; this.prepare();
    }
    get start() { return this.offset + this.index * 8 * this.beat; }
    get target() { return this.start + 6.5 * this.beat; }
    get duration() { return this.offset + this.patterns.length * 8 * this.beat; }
    get done() { return this.index >= this.patterns.length; }
    prepare() {
      this.position = 0; this.closed = false;
      const pattern = this.patterns[this.index] || [];
      this.directions = pattern.slice(0, Math.min(pattern.length, this.baseLength + this.level - 1));
    }
    resetSequence(reason = 'manual') {
      const from = this.position;
      this.position = 0;
      this.lastReset = {reason, from, index:this.index};
      return from;
    }
    resolve(kind) {
      if (this.closed || this.done) return;
      this.closed = true;
      if (kind === 'miss') { this.combo = 0; this.level = Math.max(1, this.level - 1); }
      else { this.combo++; if (this.combo % 2 === 0) this.level = Math.min(10, this.level + 1); }
      this.events.push({kind, index:this.index});
    }
    update(time) {
      // Consume every expired phrase after a slow frame, exactly once each.
      while (!this.done) {
        if (!this.closed && time > this.target + this.window) this.resolve('miss');
        if (time < this.start + 8 * this.beat) break;
        this.index++; this.prepare();
      }
    }
    press(direction, time) {
      this.update(time);
      if (this.done || this.closed || time < this.start) return 'inactive';
      // Any extra direction after a completed phrase is also a mistake: the
      // player must enter the whole visible sequence again before confirming.
      if (this.position === this.directions.length) { this.resetSequence('extra-direction'); return 'wrong'; }
      if (direction !== this.directions[this.position]) { this.resetSequence('wrong-direction'); return 'wrong'; }
      this.position++;
      return this.position === this.directions.length ? 'complete' : 'correct';
    }
    confirm(time) {
      this.update(time);
      if (this.done || this.closed || time < this.start) return 'inactive';
      if (this.position !== this.directions.length) return 'incomplete';
      const delta = Math.abs(time - this.target);
      const kind = delta > this.window ? 'miss' : delta <= Math.min(.12,this.window*.4) ? 'perfect' : delta <= this.window*.7 ? 'great' : 'good';
      this.resolve(kind);
      return kind;
    }
    takeResults() { return this.events.splice(0); }
  }
  globalThis.MeydanGameplay = {analogVector, SequenceDance};
})();
