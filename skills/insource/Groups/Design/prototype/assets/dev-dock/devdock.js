/* ============================================================================
 * devdock.js — the unified prototype chrome for the `prototype` skill.
 *
 * ONE instance per page. Every prototype-meta control — data-state toggles
 * (?filled), story inspection tools (sy_*), font picker, theme switch,
 * cross-app navigation — lives here or in the URL. A page's own render
 * template must never emit meta-control UI (no in-page "toggle state" links,
 * no per-page toolbars, no duplicated app switchers). See
 * the `prototype` skill's `references/prototype-dock.md` for the full rule and wiring contract.
 *
 * Wiring contract:
 *   - The dock talks to the project ONLY through query parameters. Controls
 *     write params with history.replaceState + a dispatched popstate event,
 *     so a project following the skill's state-helper contract (mountState
 *     listening on popstate) re-renders with no reload. A project that only
 *     reads params on load picks the change up on next navigation — both are
 *     correct; the URL stays the single source of truth either way.
 *   - On load the dock self-applies what it can without JS cooperation:
 *     ?font= sets --font on <html>, ?theme= sets data-theme on <html>.
 *     sy_* and filled remain the project's mechanism (mountStory / specs);
 *     the dock only provides their UI.
 *   - Project extension: window.DevDockInit = { apps, states, stories, frames,
 *     accent, edge } before this script loads, or after:
 *     DevDock.declare({ states: [{key,label,values}], stories: [{id,states}],
 *     frames: { mobile: 390 } }) from any page/specs module — declaring is the
 *     standard channel; registerTab({ id, label, icon, render }) stays for
 *     genuinely custom views. The dock accent is never hardcoded: it resolves
 *     explicit config > the page's brand token (--brand/--accent/--primary…) >
 *     meta theme-color > the most vivid color token > neutral slate.
 *   - ?dock=hide removes the dock entirely (screenshots, embedding, gallery).
 *
 * Self-contained: no dependencies, no build step, works over file:// and any
 * static server. Everything inside the panel below marked CUSTOMIZE is meant
 * to be adapted per project; keep the param names, not the code, stable.
 * ==========================================================================*/
(() => {
  if (window.DevDock) return;
  const params0 = new URLSearchParams(location.search);
  if (params0.get('dock') === 'hide') return;

  /* ===== CUSTOMIZE: general settings (window.DevDockInit overrides these) ===== */
  const CONFIG = Object.assign({
    edge: 'bottom',                 // top | bottom | left | right
    pos: 0.5,                       // 0..1 position along that edge
    accent: null,                   // brand color: explicit > detected from the page's own tokens > neutral slate — never hardcoded per project
    leaveDelay: 250,                // ms the pill waits before collapsing after the pointer leaves
    storageKey: 'devdock:proto:v1',
    shortcut: (e) => e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'd',
    apps: [],                       // [{ name, url, current? }] — cross-app switcher entries
    states: [],                     // [{ key, label?, values: ['pending', {v,l}], defaultLabel? }] — declared state controls
    stories: [],                    // [{ id, states?: [{ l, q: {param: value} }] }] — component/story inventory
    frames: {},                     // { mobile: 390, desktop: 1280 } — pinned viewport targets for the readout
  }, window.DevDockInit || {});

  /* ---------- URL helpers: the only channel between dock and project ---------- */
  const Q = {
    /* Unicode-safe by construction: URLSearchParams percent-encodes Arabic (and
       any non-ASCII) values automatically — never hand-concatenate raw text into a URL. */
    get: (k) => new URLSearchParams(location.search).get(k),
    has: (k) => new URLSearchParams(location.search).has(k),
    all: () => [...new URLSearchParams(location.search).entries()],
    write(changes) {                       // { key: value | null(delete) }
      const p = new URLSearchParams(location.search);
      for (const [k, v] of Object.entries(changes)) (v == null || v === false) ? p.delete(k) : p.set(k, String(v));
      const q = p.toString();
      history.replaceState(null, '', q ? '?' + q + location.hash : location.pathname + location.hash);
      dispatchEvent(new PopStateEvent('popstate'));  // mountState-style listeners re-render
    },
  };

  /* ===== CUSTOMIZE: icon set (24x24 stroke paths, use any names you like) ===== */
  const I = {
    logo: '<path d="M5 8l4 4-4 4M12 17h7"/>',
    box: '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3z"/><path d="M4 7.5l8 4.5 8-4.5M12 12v9"/>',
    layers: '<path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 13l9 5 9-5"/>',
    sliders: '<path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/>',
    gear: '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9L7 7M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/>',
    target: '<circle cx="12" cy="12" r="1"/><circle cx="12" cy="12" r="7"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>',
    x: '<path d="M6 6l12 12M18 6L6 18"/>',
    chev: '<path d="M9 6l6 6-6 6"/>',
    dot: '<circle cx="12" cy="12" r="4"/>',
    db: '<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/><path d="M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>',
    font: '<path d="M6 20l6-14 6 14M8.5 14h7"/>',
    moon: '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    grid: '<path d="M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z"/>',
    copy: '<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
  };
  const icon = (n, s = 16) => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${I[n] || I.dot}</svg>`;
  const h = (t, a, ...k) => {
    const e = document.createElement(t);
    for (const [n, v] of Object.entries(a || {})) {
      if (n === 'class') e.className = v;
      else if (n === 'html') e.innerHTML = v;
      else if (n.startsWith('on')) e[n] = v;
      else if (v != null && v !== false) e.setAttribute(n, v === true ? '' : v);
    }
    e.append(...k.flat().filter((x) => x != null && x !== false));
    return e;
  };
  const ico = (n, s) => h('span', { class: 'i', html: icon(n, s) });

  /* ---------- brand accent: adapt to the prototype's own palette ---------- */
  const isColorish = (v) => /^(#|rgba?\(|hsla?\(|oklch|oklab|lab\(|color\()/i.test((v || '').trim());
  const walkRules = (rules, out) => {
    for (const r of rules) { if (r.cssRules) walkRules(r.cssRules, out); if (r.style) for (const p of r.style) if (p.startsWith('--')) out.add(p); }
  };
  function colorTokens() {
    const names = new Set();
    for (const sheet of document.styleSheets) { try { walkRules(sheet.cssRules, names); } catch { /* cross-origin sheet */ } }
    const cs = getComputedStyle(document.documentElement);
    const out = [];
    for (const n of names) { const v = cs.getPropertyValue(n).trim(); if (isColorish(v)) out.push([n, v]); }
    return out.sort((a, b) => a[0].localeCompare(b[0]));
  }
  function vividness(v) {                     // 0..1 — saturation weighted toward mid lightness
    let r, g, b;
    const hex = /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.exec(v.trim());
    if (hex) { let s = hex[1]; if (s.length === 3) s = s.split('').map((c) => c + c).join('');
      [r, g, b] = [s.slice(0, 2), s.slice(2, 4), s.slice(4, 6)].map((x) => parseInt(x, 16) / 255); }
    else { const rgb = /^rgba?\(\s*(\d+)[\s,]+(\d+)[\s,]+(\d+)/i.exec(v.trim()); if (!rgb) return 0;
      [r, g, b] = [+rgb[1], +rgb[2], +rgb[3]].map((x) => x / 255); }
    const mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2;
    if (mx === mn || l <= 0 || l >= 1) return 0;
    const sat = (mx - mn) / (1 - Math.abs(2 * l - 1));
    return sat * (1 - Math.abs(l - 0.55));
  }
  const BRAND_CANDIDATES = ['--accent', '--brand', '--brand-color', '--color-brand', '--primary', '--color-primary', '--primary-color', '--c-accent', '--tone-brand'];
  function resolveAccent(explicit) {
    if (explicit) return explicit;
    const cs = getComputedStyle(document.documentElement);
    for (const n of BRAND_CANDIDATES) { const v = cs.getPropertyValue(n).trim(); if (isColorish(v)) return v; }
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta && isColorish(meta.content)) return meta.content.trim();
    let best = null, score = 0;
    for (const [, v] of colorTokens()) { const s = vividness(v); if (s > score) { score = s; best = v; } }
    return score > 0.2 && best ? best : '#64748b';   // nothing brand-like found → neutral slate, not a foreign green
  }
  const ACCENT = resolveAccent(CONFIG.accent);

  /* ---------- styles ---------- */
  const css = `
    :host { all: initial; }
    * { box-sizing: border-box; }
    [hidden] { display: none !important; }
    .dd {
      --ac: ${ACCENT}; --bg: #fff; --side: #f6f6f7; --tx: #1f2125; --mu: #6e737b; --ln: #e4e5e8; --hv: #efeff1;
      position: fixed; inset: 0; pointer-events: none; z-index: 2147483646;
      font: 13px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif; color: var(--tx);
    }
    @media (prefers-color-scheme: dark) { .dd { --bg: #111; --side: #161616; --tx: #e5e5e5; --mu: #8a8f98; --ln: #262626; --hv: #202020; } }
    .dd > * { pointer-events: auto; }

    /* ---- pill: one icon at rest, morphs into two buttons on hover ---- */
    .pill {
      position: fixed; display: flex; align-items: center; padding: 3px; border-radius: 99px;
      background: rgba(17,17,17,.92); backdrop-filter: blur(10px); color: #f5f5f5; border: 1px solid #3a3a3a;
      box-shadow: 0 4px 16px rgba(0,0,0,.35); touch-action: none; user-select: none; cursor: grab;
      transition: box-shadow .4s, border-color .4s;
    }
    .pill.ex { box-shadow: 0 10px 30px rgba(0,0,0,.45); border-color: #4b4b4b; }
    .pill.drag { cursor: grabbing; }
    [data-edge=bottom] .pill { bottom: calc(14px + env(safe-area-inset-bottom, 0px)); left: calc(var(--p) * 100%); translate: -50% 0; }
    [data-edge=top] .pill { top: calc(14px + env(safe-area-inset-top, 0px)); left: calc(var(--p) * 100%); translate: -50% 0; }
    [data-edge=left] .pill { left: calc(14px + env(safe-area-inset-left, 0px)); top: calc(var(--p) * 100%); translate: 0 -50%; flex-direction: column; }
    [data-edge=right] .pill { right: calc(14px + env(safe-area-inset-right, 0px)); top: calc(var(--p) * 100%); translate: 0 -50%; flex-direction: column; }

    /* the extra buttons live in a grid whose track animates 0fr -> 1fr (width, or height on side edges) */
    .xs {
      --d: .38s; --e: cubic-bezier(.4, 0, .2, 1);
      display: grid; grid-template-columns: 0fr;
      transition: grid-template-columns var(--d) var(--e), grid-template-rows var(--d) var(--e);
    }
    .ex .xs { --d: .5s; --e: cubic-bezier(.22, 1, .36, 1); grid-template-columns: 1fr; }
    [data-edge=left] .xs, [data-edge=right] .xs { grid-template-columns: 1fr; grid-template-rows: 0fr; }
    [data-edge=left] .ex .xs, [data-edge=right] .ex .xs { grid-template-rows: 1fr; }
    .xs-in { min-width: 0; min-height: 0; overflow: hidden; display: flex; align-items: center; }
    [data-edge=left] .xs-in, [data-edge=right] .xs-in { flex-direction: column; }

    /* children fade, scale and un-blur in, slightly after the pill starts growing */
    .xs-in > * { opacity: 0; transform: scale(.4); filter: blur(4px); transition: opacity .18s, transform .22s, filter .18s; }
    .ex .xs-in > * { opacity: 1; transform: none; filter: none; transition: opacity .3s .1s, transform .5s .08s cubic-bezier(.34, 1.56, .64, 1), filter .3s .08s; }
    .sep { flex: none; width: 1px; height: 10px; background: #8886; margin: 0 3px; }
    [data-edge=left] .sep, [data-edge=right] .sep { width: 10px; height: 1px; margin: 3px 0; }

    .b { all: unset; box-sizing: border-box; display: grid; place-items: center; flex: none; width: 30px; height: 30px; border-radius: 50%; cursor: pointer; opacity: .75; position: relative; color: inherit; }
    .b:hover, .b.on { opacity: 1; background: color-mix(in srgb, currentColor 12%, transparent); }
    .b.on { color: var(--ac); }
    .b:focus-visible { outline: 2px solid var(--ac); outline-offset: -2px; }
    .pill .b { width: 32px; height: 32px; }
    button, a[href], [role=tab], [role=switch], [tabindex]:not([tabindex="-1"]) { cursor: pointer; }
    .pill.drag, .pill.drag * { cursor: grabbing !important; }
    .logo { color: var(--ac); opacity: 1; }
    .i { display: grid; place-items: center; pointer-events: none; }
    .cnt { position: absolute; top: 0; right: -2px; min-width: 14px; height: 14px; padding: 0 3px; border-radius: 7px; background: #e5484d; color: #fff; font-size: 9px; font-weight: 700; display: grid; place-items: center; }

    /* ---- panel ---- */
    .panel {
      position: fixed; display: flex; background: var(--bg); border: 1px solid var(--ln); border-radius: 14px;
      box-shadow: 0 20px 50px rgba(0,0,0,.35); overflow: hidden;
      opacity: 0; visibility: hidden; transform: var(--from, none) scale(.96);
      transition: opacity .2s, transform .34s cubic-bezier(.22, 1, .36, 1), visibility 0s .34s;
    }
    .open .panel { opacity: 1; visibility: visible; transform: none; transition-delay: 0s; }
    [data-edge=bottom] .panel, [data-edge=top] .panel { left: 0; right: 0; margin-inline: auto; width: min(94vw, 1000px); height: min(var(--ph), calc(100vh - 90px)); }
    [data-edge=bottom] .panel { bottom: calc(60px + env(safe-area-inset-bottom, 0px)); --from: translateY(12px); transform-origin: 50% 100%; }
    [data-edge=top] .panel { top: calc(60px + env(safe-area-inset-top, 0px)); --from: translateY(-12px); transform-origin: 50% 0; }
    [data-edge=left] .panel, [data-edge=right] .panel { top: 0; bottom: 0; margin-block: auto; height: min(80vh, 720px); width: min(var(--pw), calc(100vw - 90px)); }
    [data-edge=left] .panel { left: 60px; --from: translateX(-12px); transform-origin: 0 50%; }
    [data-edge=right] .panel { right: 60px; --from: translateX(12px); transform-origin: 100% 50%; }
    .rz { position: absolute; z-index: 2; }
    .rz:hover { background: var(--ac); opacity: .4; }
    [data-edge=bottom] .rz { top: 0; left: 0; right: 0; height: 6px; cursor: ns-resize; }
    [data-edge=top] .rz { bottom: 0; left: 0; right: 0; height: 6px; cursor: ns-resize; }
    [data-edge=left] .rz { right: 0; top: 0; bottom: 0; width: 6px; cursor: ew-resize; }
    [data-edge=right] .rz { left: 0; top: 0; bottom: 0; width: 6px; cursor: ew-resize; }

    .side { flex: none; width: 48px; display: flex; flex-direction: column; align-items: center; padding: 8px 0; gap: 2px; background: var(--side); border-right: 1px solid var(--ln); }
    .side hr { width: 24px; margin: 6px 0; border: 0; border-top: 1px solid var(--ln); }
    .sp { flex: 1; }
    .t { all: unset; box-sizing: border-box; position: relative; display: grid; place-items: center; width: 34px; height: 34px; border-radius: 9px; color: var(--mu); cursor: pointer; }
    .t:hover { background: var(--hv); color: var(--tx); }
    .t[aria-selected=true] { background: var(--hv); color: var(--ac); }
    .t:focus-visible { outline: 2px solid var(--ac); }
    .t .cnt { top: 1px; right: 0; }

    .main { flex: 1; min-width: 0; display: flex; flex-direction: column; background-color: var(--bg);
      background-image: linear-gradient(color-mix(in srgb, var(--ln) 35%, transparent) 1px, transparent 1px), linear-gradient(90deg, color-mix(in srgb, var(--ln) 35%, transparent) 1px, transparent 1px); background-size: 24px 24px; }
    .hd { display: flex; align-items: center; gap: 10px; padding: 8px 10px 8px 16px; background: var(--bg); border-bottom: 1px solid var(--ln); }
    .hd b { font-size: 14px; }
    .hd .b { width: 30px; height: 30px; color: var(--mu); }
    .ct { flex: 1; overflow: auto; padding: 14px; display: flex; flex-direction: column; gap: 18px; }
    [dir=rtl] .side { border-right: 0; border-inline-start: 0; border-inline-end: 1px solid var(--ln); }

    /* ---- building blocks you can reuse in your own tabs ---- */
    .sec h3 { margin: 0 0 8px; font-size: 12px; font-weight: 600; color: var(--mu); }
    .box { background: var(--bg); border: 1px solid var(--ln); border-radius: 10px; overflow: hidden; }
    .box > :last-child { border-bottom: 0; }
    .row { display: flex; align-items: center; justify-content: space-between; gap: 12px; min-height: 36px; padding: 6px 12px; border-bottom: 1px solid var(--ln); }
    button.row { all: unset; box-sizing: border-box; width: 100%; display: flex; align-items: center; justify-content: space-between; gap: 12px; min-height: 36px; padding: 6px 12px; border-bottom: 1px solid var(--ln); cursor: pointer; }
    button.row:hover { background: var(--hv); }
    button.row:focus-visible { outline: 2px solid var(--ac); outline-offset: -2px; }
    button.row.on { color: var(--ac); }
    .row small { display: block; font-size: 11px; }
    .k { color: var(--mu); }
    .v { font: 12px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; text-align: right; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 65%; }
    .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; }
    .card { background: var(--bg); border: 1px solid var(--ln); border-radius: 10px; padding: 10px 12px; }
    .card .n { font-size: 20px; font-weight: 600; font-variant-numeric: tabular-nums; }
    .card .l { color: var(--mu); font-size: 12px; }
    .empty { padding: 24px; text-align: center; color: var(--mu); }
    .tks { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px; }
    .tk { all: unset; box-sizing: border-box; display: flex; align-items: center; gap: 8px; padding: 6px 8px; border: 1px solid var(--ln); border-radius: 8px; cursor: pointer; min-width: 0; }
    .tk:hover { background: var(--hv); }
    .tk:focus-visible { outline: 2px solid var(--ac); }
    .tk .swat { flex: none; width: 18px; height: 18px; border-radius: 5px; border: 1px solid rgba(0,0,0,.15); }
    .tk .nm { font: 11px ui-monospace, SFMono-Regular, Menlo, monospace; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--tx); }
    .tools { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
    .btn { all: unset; box-sizing: border-box; display: inline-flex; align-items: center; gap: 6px; height: 30px; padding: 0 12px; border: 1px solid var(--ln); border-radius: 8px; background: var(--bg); cursor: pointer; }
    .btn:hover { background: var(--hv); }
    .btn:focus-visible { outline: 2px solid var(--ac); }
    .btn.on { border-color: var(--ac); color: var(--ac); }
    .sw { width: 30px; height: 18px; border-radius: 9px; background: var(--ln); position: relative; transition: background .15s; flex: none; }
    .sw::after { content: ""; position: absolute; top: 2px; left: 2px; width: 14px; height: 14px; border-radius: 50%; background: #fff; transition: transform .15s; box-shadow: 0 1px 2px rgba(0,0,0,.3); }
    [aria-checked=true] .sw { background: var(--ac); }
    [aria-checked=true] .sw::after { transform: translateX(12px); }
    [dir=rtl] [aria-checked=true] .sw::after { transform: translateX(-12px); }
  `;

  /* ---------- markup ---------- */
  const host = document.createElement('div');
  host.id = 'dev-dock';
  const root = host.attachShadow({ mode: 'open' });
  root.innerHTML = `
    <style>${css}</style>
    <div class="dd" data-edge="bottom">
      <div class="pill" role="toolbar" aria-label="Dev Dock">
        <button class="b logo" type="button" data-a="toggle" aria-haspopup="dialog" aria-expanded="false" title="Toggle Dev Dock (Ctrl+Shift+D)">${icon('logo', 18)}</button>
        <div class="xs">
          <div class="xs-in">
            <i class="sep"></i>
            <button class="b" type="button" data-a="inspect" title="Pick an element">${icon('target')}</button>
          </div>
        </div>
      </div>
      <section class="panel" role="dialog" aria-label="Dev tools">
        <div class="rz"></div>
        <nav class="side" role="tablist" aria-orientation="vertical"></nav>
        <div class="main">
          <header class="hd"><b data-r="title"></b><span class="k" data-r="sub"></span><span class="sp"></span>
            <button class="b" type="button" data-a="close" title="Close (Esc)">${icon('x')}</button></header>
          <div class="ct" role="tabpanel"></div>
        </div>
      </section>
      <div class="hl"><span></span></div>
      <div class="toast" role="status"></div>
    </div>`;

  const $ = (s) => root.querySelector(s);
  const dd = $('.dd'), pill = $('.pill'), logo = $('.logo'), xs = $('.xs'), panel = $('.panel'), side = $('.side'), ct = $('.ct'), rz = $('.rz');
  const hl = $('.hl'), toastEl = $('.toast'), inspectBtn = $('[data-a=inspect]');

  /* ---------- state ---------- */
  const S = { edge: CONFIG.edge, pos: CONFIG.pos, ph: 440, pw: 640, tab: 'states' };
  try { Object.assign(S, JSON.parse(localStorage.getItem(CONFIG.storageKey) || '{}')); } catch {}
  if (!['top', 'bottom', 'left', 'right'].includes(S.edge)) S.edge = 'bottom';
  const save = () => { try { localStorage.setItem(CONFIG.storageKey, JSON.stringify(S)); } catch {} };
  const apply = () => {
    dd.dataset.edge = S.edge;
    dd.style.setProperty('--p', S.pos);
    dd.style.setProperty('--ph', S.ph + 'px');
    dd.style.setProperty('--pw', S.pw + 'px');
  };

  const custom = [];
  let isOpen = false, inspecting = false, timer = null, toastT = null;

  /* ---------- declared inventories (DevDockInit / DevDock.declare) + DOM discovery ---------- */
  const declared = { states: [...(CONFIG.states || [])], stories: [...(CONFIG.stories || [])] };
  const seenStories = new Set();
  const discoverStories = () => {
    document.querySelectorAll('[data-story]').forEach((e) =>
      (e.getAttribute('data-story') || '').split(/\s+/).forEach((s) => s && seenStories.add(s)));
  };
  const storyInventory = () => {
    discoverStories();
    const byId = new Map(declared.stories.map((s) => [s.id, s]));
    seenStories.forEach((id) => { if (!byId.has(id)) byId.set(id, { id }); });
    return [...byId.values()];
  };

  /* ---------- UI building blocks (reuse these in your tabs) ---------- */
  const sec = (t, ...k) => h('section', { class: 'sec' }, h('h3', 0, t), ...k);
  const box = (...k) => h('div', { class: 'box' }, ...k);
  const kv = (k, v) => h('div', { class: 'row' }, h('span', { class: 'k' }, k), h('span', { class: 'v', title: String(v) }, String(v)));
  const card = (l, v) => h('div', { class: 'card' }, h('div', { class: 'n' }, String(v)), h('div', { class: 'l' }, l));
  const empty = (t) => h('div', { class: 'empty' }, t);
  const btn = (label, fn, ic, on) => h('button', { class: 'btn' + (on ? ' on' : ''), type: 'button', onclick: fn }, ic && ico(ic, 14), label);
  const act = (label, desc, fn, on) => h('button', { class: 'row' + (on ? ' on' : ''), type: 'button', onclick: fn },
    h('span', 0, label, desc && h('small', { class: 'k' }, desc)), ico('chev', 14));
  const tog = (label, get, set, desc) => {
    const b = h('button', { class: 'row', type: 'button', role: 'switch', 'aria-checked': String(!!get()) },
      h('span', 0, label, desc && h('small', { class: 'k' }, desc)), h('span', { class: 'sw' }));
    b.onclick = () => { set(!get()); render(); };
    return b;
  };
  const seg = (label, options, current, pick) => sec(label, box(
    h('div', { class: 'tools', style: 'padding:10px 12px' },
      ...options.map(([v, l]) => btn(l, () => { pick(v); render(); }, null, current === v)))));

  /* ---------- element picker (pill's second button) ---------- */
  const sel = (t) => t.localName + (t.id ? '#' + CSS.escape(t.id) : '') + [...t.classList].slice(0, 2).map((c) => '.' + CSS.escape(c)).join('');
  const target = (e) => { const p = e.composedPath(); return p.includes(host) || !(p[0] instanceof Element) ? null : p[0]; };
  function toast(msg) { toastEl.textContent = msg; toastEl.classList.add('on'); clearTimeout(toastT); toastT = setTimeout(() => toastEl.classList.remove('on'), 2200); }
  function onMove(e) {
    const t = target(e);
    if (!t) { hl.style.display = 'none'; return; }
    const r = t.getBoundingClientRect();
    Object.assign(hl.style, { display: 'block', left: r.left + 'px', top: r.top + 'px', width: r.width + 'px', height: r.height + 'px' });
    hl.classList.toggle('in', r.top < 22);
    hl.firstChild.textContent = `${sel(t)}  ${Math.round(r.width)}×${Math.round(r.height)}`;
  }
  function onPick(e) {
    const t = target(e); if (!t) return;
    e.preventDefault(); e.stopPropagation();
    const s = sel(t);
    try { navigator.clipboard.writeText(s).catch(() => {}); } catch {}
    toast('Copied ' + s); console.log('[DevDock] picked', t);
    stopInspect();
  }
  function startInspect() {
    close(); inspecting = true; inspectBtn.classList.add('on'); sync();
    toast('Click an element to copy its selector · Esc to cancel');
    addEventListener('mousemove', onMove, true); addEventListener('click', onPick, true);
  }
  function stopInspect() {
    inspecting = false; inspectBtn.classList.remove('on'); hl.style.display = 'none'; sync();
    removeEventListener('mousemove', onMove, true); removeEventListener('click', onPick, true);
  }

  /* ===== CUSTOMIZE: prototype tabs =====
     The dock owns every meta-control; page templates own everything else.
     Tabs below only read/write query params — the project's state helper stays
     the single owner of URL mechanics (see references/prototype-dock.md).   */

  /* Fonts: applied live (--font on <html>) AND persisted to ?font= so every
     URL stays reproducible. RTL documents get the Arabic-capable set. */
  const FONTS_LATIN = ['Inter', 'Manrope', 'Sora', 'Space Grotesk', 'IBM Plex Sans', 'Public Sans', 'Figtree', 'Outfit', 'Source Sans 3', 'Spectral'];
  const FONTS_AR = ['Cairo', 'Tajawal', 'IBM Plex Sans Arabic', 'Almarai', 'Noto Kufi Arabic', 'Readex Pro', 'Rubik', 'El Messiri', 'Marhey', 'Alexandria'];
  const isRtl = () => document.documentElement.dir === 'rtl' || Q.get('fonts') === 'ar';
  const fontSet = () => (isRtl() ? FONTS_AR : FONTS_LATIN);
  const stack = (name) => `"${name}", ${isRtl() ? '"Segoe UI", Tahoma' : 'system-ui'}, sans-serif`;
  function applyFont(name) {
    if (!name) { document.documentElement.style.removeProperty('--font'); return; }
    if (![...FONTS_LATIN, ...FONTS_AR].includes(name)) return;   // only the curated set reaches the network
    if (!root.querySelector(`link[data-dd-font="${name}"]`) && !document.querySelector(`link[data-dd-font="${name}"]`)) {
      const l = h('link', { rel: 'stylesheet', href: `https://fonts.googleapis.com/css2?family=${encodeURIComponent(name)}:wght@400;500;600;700&display=swap` });
      l.dataset.ddFont = name;
      document.head.append(l);
    }
    document.documentElement.style.setProperty('--font', stack(name));
  }

  const tabs = [
    { id: 'states', label: 'States', icon: 'db', group: 0, sub: () => declared.states.length ? `${declared.states.length} control(s)` : (Q.get('filled') ? 'filled data' : 'sparse data'), render: () => [
      ...(declared.states.length ? declared.states.map((s) => seg(s.label || s.key,
        [['', s.defaultLabel || 'default'], ...(s.values || []).map((o) => (typeof o === 'string' ? [o, o] : [o.v, o.l]))],
        Q.get(s.key) || '', (v) => Q.write({ [s.key]: v || null })))
        : [sec('Declared state controls', empty('Pages declare their state trees to the dock — DevDock.declare({ states: [{ key, label, values }] }) — and the dock renders the pickers. A page template never renders its own state switches.'))]),
      ...(declared.states.some((s) => s.key === 'filled') ? [] : [sec('Data fidelity', box(
        tog('Filled (seeded) data', () => !!Q.get('filled'), (v) => Q.write({ filled: v ? '1' : null }), '?filled=1 · sparse by default')))]),
      sec('This URL', box(
        ...(Q.all().length ? Q.all().map(([k, v]) => h('div', { class: 'row' },
          h('span', { class: 'k' }, k), h('span', { class: 'v', title: v }, v),
          btn('clear', () => { Q.write({ [k]: null }); })))
          : [kv('(no params)', 'default state')]))),
      h('div', { class: 'tools' },
        btn('Copy URL', () => { try { navigator.clipboard.writeText(location.href).catch(() => {}); toast('URL copied'); } catch {} }, 'copy'),
        btn('Reset to default', () => { history.replaceState(null, '', location.pathname + location.hash); dispatchEvent(new PopStateEvent('popstate')); })),
    ] },

    { id: 'stories', label: 'Stories', icon: 'box', group: 0, sub: () => Q.get('story_id') || 'full page', render: () => {
      const list = storyInventory();
      const cur = Q.get('story_id');
      const entry = list.find((s) => s.id === cur);
      return [
        box(
          act('Full page', 'no isolation — every component in place', () => Q.write({ story_id: null }), !cur),
          ...list.map((s) => act(s.id, s.states && s.states.length ? `${s.states.length} story state(s)` : 'component', () => Q.write({ story_id: s.id }), cur === s.id))),
        ...(entry && entry.states && entry.states.length ? [sec(`States · ${entry.id}`, box(
          ...entry.states.map((st) => {
            const q = st.q || {};
            const on = cur === entry.id && Object.entries(q).every(([k, v]) => Q.get(k) === String(v));
            return act(st.l || Object.entries(q).map(([k, v]) => `${k}=${v}`).join(' '),
              Object.entries(q).map(([k, v]) => `${k}=${v}`).join(' · '),
              () => Q.write(Object.assign({ story_id: entry.id }, q)), on);
          }))) ] : []),
        ...(list.length ? [] : [empty('No [data-story] components found on this page and none declared — stories come from pages; declare the suite inventory with DevDockInit.stories if this page has none.')]),
      ];
    } },

    { id: 'fonts', label: 'Fonts', icon: 'font', group: 0, sub: () => Q.get('font') || 'project default', render: () => [
      seg(`Family${isRtl() ? ' (Arabic set — RTL)' : ' (Latin set)'}`,
        [['', 'Project default'], ...fontSet().map((f) => [f, f])],
        Q.get('font') || '',
        (v) => { Q.write({ font: v || null }); applyFont(v || Q.get('font')); }),
      sec('Note', empty('The pick sets --font on <html> live and writes ?font= so the choice survives sharing. theme.css owns the project default; ?fonts=ar switches an LTR page to the Arabic set.')),
    ] },

    { id: 'inspect', label: 'Story tools', icon: 'sliders', group: 0, sub: () => 'sy_* params', render: () => [
      seg('Stage background', [['', 'default'], ['light', 'light'], ['dark', 'dark'], ['checker', 'checker']],
        Q.get('sy_bg') || '', (v) => Q.write({ sy_bg: v || null })),
      seg('Grid overlay', [['', 'off'], ['8', '8px'], ['16', '16px']],
        Q.get('sy_grid') || '', (v) => Q.write({ sy_grid: v || null })),
      sec('Outlines', box(
        tog('Outline all elements', () => Q.get('sy_outline') === '1', (v) => Q.write({ sy_outline: v ? '1' : null })),
        tog('Hover dimensions', () => Q.get('sy_inspect') === '1', (v) => Q.write({ sy_inspect: v ? '1' : null })))),
      sec('Applies to', empty('Story tools act on ?story_id= isolation stages — start a story from the URL (?story_id=<id>) and these write its sy_* params. The stage mechanism lives in the project state helper, not here.')),
    ] },

    { id: 'apps', label: 'Apps', icon: 'layers', group: 1, sub: () => CONFIG.apps.length ? `${CONFIG.apps.length} app(s)` : 'not configured', render: () => [
      ...(CONFIG.apps.length ? [box(
        ...CONFIG.apps.map((a) => act(a.name, a.current ? 'current app' : a.url, () => { if (!a.current) location.href = a.url; }, !!a.current))),
      ] : [empty('Configure cross-app links: window.DevDockInit = { apps: [{ name, url, current }] } before devdock.js loads.')]),
      sec('Gallery', box(act('Open root gallery', '/index.html', () => { location.href = '/index.html'; }))),
    ] },

    { id: 'theme', label: 'Theme', icon: 'moon', group: 1, sub: () => Q.get('theme') || 'auto', render: () => {
      const toks = colorTokens();
      return [
        seg('data-theme', [['', 'auto (system)'], ['light', 'light'], ['dark', 'dark']],
          Q.get('theme') || '', (v) => {
            Q.write({ theme: v || null });
            v ? document.documentElement.dataset.theme = v : document.documentElement.removeAttribute('data-theme');
          }),
        sec(`Project palette — ${toks.length} color token(s)`, toks.length
          ? h('div', { class: 'tks' }, ...toks.map(([n, v]) =>
              h('button', { class: 'tk', type: 'button', title: `${n} · ${v} — click copies var(${n})`,
                onclick: () => { try { navigator.clipboard.writeText(`var(${n})`).catch(() => {}); } catch {} toast(`var(${n}) copied`); } },
                h('i', { class: 'swat', style: `background:${v}` }), h('span', { class: 'nm' }, n.replace(/^--/, '')))))
          : empty('No color custom properties resolve on <html> — the project must define its palette in theme.css BEFORE page work (zero-duplication: the Palette Law). The dock accent fell back to neutral slate.')),
        sec('Note', empty('Swatches follow the active theme. Every color in pages and components must come from this list — the dock accent itself adapts to the detected brand token, which is why it is never hardcoded either.')),
      ];
    } },

    { id: 'viewport', label: 'Viewport', icon: 'grid', group: 1, sub: () => `${innerWidth}×${innerHeight}`, live: true, render: () => [
      sec('Live', box(kv('Window', `${innerWidth} × ${innerHeight}px`), kv('devicePixelRatio', String(devicePixelRatio)))),
      ...(Object.keys(CONFIG.frames || {}).length ? [sec('Pinned targets', box(
        ...Object.entries(CONFIG.frames).map(([name, w]) => {
          const d = innerWidth - w;
          return kv(name, `${w}px · ${Math.abs(d) <= 24 ? 'match' : d < 0 ? `${-d}px narrower` : `+${d}px wider`}`);
        })))]
        : [sec('Pinned targets', empty('Declare the questionnaire answer once: DevDockInit.frames = { mobile: 390, desktop: 1280 } — the tab then reports drift live.'))]),
      sec('Framing', empty('Screens stay frameless. Device framing is presentation-layer: view mobile surfaces in a device-width gallery iframe or browser emulation — never a bezel inside the page DOM, and nobody is asked to resize their window.')),
    ] },

    { id: 'about', label: 'Dock', icon: 'gear', group: 9, sub: () => 'help', render: () => [
      sec('Keyboard', box(
        kv('Toggle dock', 'Ctrl+Shift+D'), kv('Close / cancel pick', 'Esc'), kv('Hide entirely', '?dock=hide (URL param)'))),
      sec('Persistence', box(
        kv('Dock position', 'localStorage (edge, pos, size, tab)'),
        kv('Prototype state', 'the URL — every control writes query params'))),
      sec('Extend', box(
        kv('Declare controls', 'DevDock.declare({ states, stories, frames })'),
        kv('Project tab', 'DevDock.registerTab({ id, label, icon, render })'),
        kv('Config', 'window.DevDockInit = { apps, states, stories, frames, accent }'))),
    ] },
  ];
  const allTabs = () => [...tabs.filter((t) => t.group < 2), ...custom, ...tabs.filter((t) => t.group > 8)];

  /* ---------- render ---------- */
  function render() {
    if (!isOpen) return;
    const list = allTabs(), cur = list.find((t) => t.id === S.tab) || list[0];
    let last;
    side.replaceChildren();
    for (const t of list) {
      if (last !== undefined && t.group !== last) side.append(t.group === 9 ? h('i', { class: 'sp' }) : h('hr'));
      last = t.group;
      const c = t.badge && t.badge();
      side.append(h('button', { class: 't', type: 'button', role: 'tab', 'aria-selected': String(t === cur), title: t.label, onclick: () => go(t.id) },
        ico(t.icon || 'dot', 18), c ? h('span', { class: 'cnt' }, c > 9 ? '9+' : c) : null));
    }
    $('[data-r=title]').textContent = cur.label;
    $('[data-r=sub]').textContent = cur.sub ? cur.sub() : '';
    const out = cur.render();
    ct.replaceChildren(...[].concat(out).filter(Boolean).map((x) => typeof x === 'string' ? document.createTextNode(x) : x));
  }
  function go(id) { S.tab = id; save(); ct.scrollTop = 0; isOpen ? render() : open(); }

  /* ---------- pill expand / collapse ---------- */
  let hov = false, foc = false, leaveT = null, lastType = 'mouse';
  function sync() {
    const ex = hov || foc || isOpen || inspecting;
    pill.classList.toggle('ex', ex);
    xs.inert = !ex;                       // hidden buttons can't be tabbed to or clicked
  }
  const enter = () => { clearTimeout(leaveT); hov = true; sync(); };
  const leave = (delay = CONFIG.leaveDelay) => { clearTimeout(leaveT); leaveT = setTimeout(() => { hov = false; sync(); }, delay); };
  pill.addEventListener('pointerenter', (e) => { if (e.pointerType !== 'touch') enter(); });
  pill.addEventListener('pointerleave', (e) => { if (e.pointerType !== 'touch') leave(); });
  pill.addEventListener('focusin', (e) => { foc = !!e.target.matches(':focus-visible'); sync(); });
  pill.addEventListener('focusout', () => { foc = false; sync(); });

  /* ---------- open / close ---------- */
  function open() {
    isOpen = true; dd.classList.add('open'); logo.setAttribute('aria-expanded', 'true'); sync(); render();
    clearInterval(timer);
    timer = setInterval(() => { const t = allTabs().find((x) => x.id === S.tab); if (t && t.live) render(); }, 1000);
  }
  function close(returnFocus) {
    isOpen = false; dd.classList.remove('open'); logo.setAttribute('aria-expanded', 'false');
    clearInterval(timer); sync(); if (returnFocus) logo.focus();
  }
  const toggle = () => (isOpen ? close() : open());

  pill.addEventListener('pointerdown', (e) => { lastType = e.pointerType; });
  pill.addEventListener('click', (e) => {
    const a = e.target.closest('[data-a]'); if (!a) return;
    const k = a.dataset.a;
    // on touch screens the first tap only expands the pill, the next tap acts
    if (lastType === 'touch' && k === 'toggle' && !pill.classList.contains('ex')) { enter(); leave(3500); return; }
    if (k === 'toggle') toggle();
    else if (k === 'inspect') inspecting ? stopInspect() : startInspect();
  });
  $('[data-a=close]').addEventListener('click', () => close(true));

  /* ---------- drag pill, snap to nearest edge ---------- */
  let drag = null;
  pill.addEventListener('pointerdown', (e) => {
    if (e.button !== 0) return;
    const r = pill.getBoundingClientRect();
    drag = { x: e.clientX, y: e.clientY, cx: r.left + r.width / 2, cy: r.top + r.height / 2, moved: false };
  });
  pill.addEventListener('pointermove', (e) => {
    if (!drag) return;
    const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (!drag.moved) {
      if (Math.hypot(dx, dy) < 6) return;
      drag.moved = true; close(); pill.setPointerCapture(e.pointerId); pill.classList.add('drag');
    }
    Object.assign(pill.style, { left: drag.cx + dx + 'px', top: drag.cy + dy + 'px', right: 'auto', bottom: 'auto', translate: '-50% -50%', transition: 'none' });
  });
  const endDrag = () => {
    if (!drag) return;
    const d = drag; drag = null;
    if (!d.moved) return;
    pill.classList.remove('drag');
    const b = pill.getBoundingClientRect(), cx = b.left + b.width / 2, cy = b.top + b.height / 2;
    const dist = { left: cx, right: innerWidth - cx, top: cy, bottom: innerHeight - cy };
    S.edge = Object.keys(dist).sort((a, c) => dist[a] - dist[c])[0];
    const horiz = S.edge === 'top' || S.edge === 'bottom';
    S.pos = Math.min(.92, Math.max(.08, horiz ? cx / innerWidth : cy / innerHeight));
    pill.style.cssText = ''; apply(); save();
    const a = pill.getBoundingClientRect();                 // FLIP: glide from drop point to the edge
    pill.style.transform = `translate(${b.left - a.left}px, ${b.top - a.top}px)`;
    pill.getBoundingClientRect();
    pill.style.transition = 'transform .35s cubic-bezier(.2,.9,.3,1), box-shadow .4s, border-color .4s';
    pill.style.transform = '';
    setTimeout(() => { pill.style.transition = ''; }, 400);
  };
  pill.addEventListener('pointerup', endDrag);
  pill.addEventListener('pointercancel', () => { drag = null; pill.classList.remove('drag'); pill.style.cssText = ''; });

  /* ---------- resize panel ---------- */
  rz.addEventListener('pointerdown', (e) => {
    e.preventDefault(); rz.setPointerCapture(e.pointerId);
    const h0 = panel.offsetHeight, w0 = panel.offsetWidth, x = e.clientX, y = e.clientY;
    rz.onpointermove = (m) => {
      const dx = m.clientX - x, dy = m.clientY - y;
      if (S.edge === 'bottom') S.ph = h0 - dy; else if (S.edge === 'top') S.ph = h0 + dy;
      else if (S.edge === 'left') S.pw = w0 + dx; else S.pw = w0 - dx;
      S.ph = Math.max(220, Math.min(innerHeight - 100, S.ph)); S.pw = Math.max(360, Math.min(innerWidth - 100, S.pw));
      apply();
    };
    rz.onpointerup = () => { rz.onpointermove = rz.onpointerup = null; save(); };
  });

  /* ---------- global listeners ---------- */
  document.addEventListener('pointerdown', (e) => { if (isOpen && !e.composedPath().includes(host)) close(); });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && inspecting) stopInspect();
    else if (e.key === 'Escape' && isOpen) close(true);
    else if (CONFIG.shortcut(e)) { e.preventDefault(); toggle(); }
  });
  for (const ev of ['resize', 'popstate', 'hashchange']) addEventListener(ev, () => isOpen && render());

  /* ---------- public API ---------- */
  window.DevDock = {
    open, close, toggle, refresh: render, go, toast, params: Q, applyFont, colorTokens,
    declare(patch) {
      if (Array.isArray(patch.states)) for (const s of patch.states) if (!declared.states.some((d) => d.key === s.key)) declared.states.push(s);
      if (Array.isArray(patch.stories)) for (const s of patch.stories) { const i = declared.stories.findIndex((d) => d.id === s.id); if (i > -1) declared.stories[i] = Object.assign(declared.stories[i], s); else declared.stories.push(s); }
      if (patch.frames) Object.assign(CONFIG.frames, patch.frames);
      render();
    },
    // your own tab: {id, label, icon?, sub?, render: () => Node | Node[] | string}
    registerTab(tab) { tab.group = 2; custom.push(tab); render(); return () => { custom.splice(custom.indexOf(tab), 1); render(); }; },
  };

  /* ---------- boot: self-apply persisted URL choices, then mount ---------- */
  applyFont(Q.get('font'));
  const th = Q.get('theme');
  if (th === 'light' || th === 'dark') document.documentElement.dataset.theme = th;
  (document.body || document.documentElement).append(host);
  apply(); sync(); render();
})();