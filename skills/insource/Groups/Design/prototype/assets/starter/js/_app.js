/**
 * _app.js — shared application layer: the central URL-state helper.
 * Pure functions are DOM-free and unit-testable (js/state.test.mjs imports this file in Node).
 * Component state SETS live in specs.js (single owner); this file owns the mechanics.
 */

/** Coerce/validate one raw value against a spec entry; fall back to default. */
function coerce(raw, def) {
  if (raw === null || raw === undefined) return def.default;
  if (def.values && !def.values.some(v => String(v) === String(raw))) return def.default;
  if (def.parse) { try { return def.parse(raw); } catch { return def.default; } }
  if (typeof def.default === "number") { const n = Number(raw); return Number.isNaN(n) ? def.default : n; }
  return raw;
}

/** parse(search, spec, foreignKeys?) → { state, foreign } — unknown params are preserved, never dropped. */
export function parse(search, spec) {
  const p = new URLSearchParams(search);
  const state = {};
  for (const key of Object.keys(spec)) state[key] = coerce(p.get(key), spec[key]);
  const foreign = {};
  for (const [k, v] of p.entries()) if (!(k in spec)) foreign[k] = v;
  return { state, foreign };
}

/** toQuery(state, spec, foreign) → "?..." — defaults omitted (clean URLs), non-defaults kept, foreign preserved. */
export function toQuery(state, spec, foreign = {}) {
  const p = new URLSearchParams();
  for (const [key, def] of Object.entries(spec)) {
    const v = state[key];
    if (v !== null && v !== undefined && v !== "" && String(v) !== String(def.default)) p.set(key, v);
  }
  for (const [k, v] of Object.entries(foreign)) p.set(k, v);
  const s = p.toString();
  return s ? "?" + s : "";
}

/** patch(state, changes) → new state object; unrelated keys survive. */
export function patch(state, changes) {
  return { ...state, ...changes };
}

/** History policy: continuous keys (declared push:"replace") replace, discrete ones push. */
export function historyMode(key, spec) {
  return spec[key] && spec[key].push === "replace" ? "replace" : "push";
}

/* Seeded randomness — ?filled must reproduce: same seed, same dataset. */
export function strHash(s) {
  let h = 2166136261;
  for (const c of String(s)) { h ^= c.codePointAt(0); h = Math.imul(h, 16777619); }
  return h >>> 0;
}
export function rng(seed) {                       // mulberry32
  let a = strHash(seed === true || seed === "" || seed === "1" ? "filled" : seed);
  return () => {
    a |= 0; a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

/**
 * mountState(spec, render) — the only wiring pages need.
 * render(state) is the single update path: URL bootstrap, clicks, and
 * popstate all go through it, so URL-triggered and interaction-triggered
 * states are pixel-identical by construction.
 */
export function mountState(spec, render) {
  const { state, foreign } = parse(location.search, spec);
  let curState = state, curForeign = foreign;

  function sync(changes, opts = {}) {
    curState = patch(curState, changes);
    const qs = toQuery(curState, spec, curForeign);
    const url = location.pathname + qs;
    const mode = opts.replace ? "replace"
      : (opts.key ? historyMode(opts.key, spec) : "push");
    history[mode === "replace" ? "replaceState" : "pushState"]({}, "", url);
    render(curState);
  }

  window.addEventListener("popstate", () => {
    const r = parse(location.search, spec);
    curState = r.state; curForeign = r.foreign;
    render(curState);
  });

  render(curState);
  return { sync, state: () => curState };
}
