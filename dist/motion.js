// Renderer-independent character and camera motion helpers.
(() => {
  const TAU = Math.PI * 2;

  function clamp(value, low, high) {
    return Math.max(low, Math.min(high, value));
  }

  function smoothstep(low, high, value) {
    if (high <= low) return value >= high ? 1 : 0;
    const t = clamp((value - low) / (high - low), 0, 1);
    return t * t * (3 - 2 * t);
  }

  function shortestAngle(from, to) {
    return ((to - from + Math.PI) % TAU + TAU) % TAU - Math.PI;
  }

  function dampAngle(current, target, rate, dt) {
    if (![current, target, rate, dt].every(Number.isFinite)) return current;
    if (dt <= 0 || rate <= 0) return current;
    return current + shortestAngle(current, target) * (1 - Math.exp(-rate * dt));
  }

  function locomotionWeights(speed, options = {}) {
    const value = Math.max(0, Number.isFinite(speed) ? speed : 0);
    const moveFull = options.moveFull ?? 0.35;
    const runStart = options.runStart ?? 2.1;
    const runFull = options.runFull ?? 3.2;
    const moving = smoothstep(0, moveFull, value);
    const run = moving * smoothstep(runStart, runFull, value);
    return {idle:1-moving, walk:moving-run, run};
  }

  function cameraCollisionDistance(desiredDistance, hitDistance, options = {}) {
    const desired = Math.max(0, Number.isFinite(desiredDistance) ? desiredDistance : 0);
    const padding = Math.max(0, options.padding ?? 0.25);
    const minimum = clamp(options.minimum ?? 1.2, 0, desired);
    if (!Number.isFinite(hitDistance) || hitDistance <= 0 || hitDistance >= desired + padding)
      return desired;
    return clamp(hitDistance - padding, minimum, desired);
  }

  function hashSeed(seed) {
    const text = String(seed);
    let hash = 2166136261;
    for (let i = 0; i < text.length; i++) {
      hash ^= text.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return hash >>> 0;
  }

  function avatarProfile(seed) {
    let state = hashSeed(seed);
    const next = () => {
      state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
      return state / 4294967296;
    };
    return {
      scale:0.96 + next() * 0.08,
      animationOffset:next() * 12,
      paletteIndex:Math.floor(next() * 6)
    };
  }

  globalThis.MeydanMotion = {
    shortestAngle,
    dampAngle,
    locomotionWeights,
    cameraCollisionDistance,
    avatarProfile
  };
})();
