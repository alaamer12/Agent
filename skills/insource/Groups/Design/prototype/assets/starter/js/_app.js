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
  for (const k of new Set(p.keys())) if (!Object.hasOwn(spec, k)) {
    const values = p.getAll(k);
    Object.defineProperty(foreign, k, { value: values.length === 1 ? values[0] : values, enumerable: true });
  }
  return { state, foreign };
}

/** toQuery(state, spec, foreign) → "?..." — defaults omitted (clean URLs), non-defaults kept, foreign preserved. */
export function toQuery(state, spec, foreign = {}) {
  const p = new URLSearchParams();
  for (const [key, def] of Object.entries(spec)) {
    const v = state[key];
    if (v !== null && v !== undefined && v !== "" && String(v) !== String(def.default)) p.set(key, v);
  }
  for (const [k, v] of Object.entries(foreign)) {
    for (const value of Array.isArray(v) ? v : [v]) p.append(k, value);
  }
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

/** Normalize story ID (lowercase, trim quotes and whitespace, strip trailing -component) */
export function normalizeStoryId(raw) {
  return String(raw || "")
    .trim()
    .replace(/^["'\s]+|["'\s]+$/g, "")
    .toLowerCase()
    .replace(/-component$/, "");
}

/** Parse story_id values supporting both repeated params and comma lists */
export function parseStoryIds(search) {
  const p = new URLSearchParams(search);
  const ids = [];
  for (const v of p.getAll("story_id")) {
    for (const x of v.split(",")) {
      const n = normalizeStoryId(x);
      if (n && !ids.includes(n)) ids.push(n);
    }
  }
  return ids;
}

/**
 * mountStory(container) — Story Isolation Stage & Toolbox.
 * If story_id is present in location.search, moves matching [data-story] elements
 * onto a centered #stage and mounts the floating toolbox (sy_*).
 */
export function mountStory(container) {
  if (typeof window === "undefined" || !location.search) return false;
  container ??= document.querySelector(".app");
  if (!container || container === document.body) return false;
  const p = new URLSearchParams(location.search);
  if (!p.has("story_id")) return false;

  const ids = parseStoryIds(location.search);
  const all = Array.from(container.querySelectorAll("[data-story]"));
  const stage = document.createElement("main");
  stage.id = "stage";
  stage.setAttribute("data-testid", "story-root");
  stage.setAttribute("data-stories", ids.join(","));

  const found = [], missing = [];
  ids.forEach(id => {
    const t = all.find(e => normalizeStoryId(e.dataset.story) === id);
    if (t) found.push(t); else missing.push(id);
  });

  if (!ids.length || missing.length) {
    const box = document.createElement("div");
    box.id = "story-index";
    const heading = document.createElement("h1");
    heading.textContent = ids.length ? "Story not found" : "Stories";
    const detail = document.createElement("p");
    detail.textContent = missing.length ? `Missing: ${missing.join(", ")}` : "Available stories on this page:";
    const list = document.createElement("ul");
    for (const element of all) {
      const item = document.createElement("li"), link = document.createElement("a");
      const url = new URL(location.href);
      url.searchParams.set("story_id", element.dataset.story);
      link.href = url.href;
      link.textContent = element.dataset.story;
      item.appendChild(link);
      list.appendChild(item);
    }
    if (!all.length) list.textContent = "No [data-story] elements found";
    box.append(heading, detail, list);
    stage.appendChild(box);
  }

  found.forEach(t => stage.appendChild(t));
  if (found.length) document.title = "Story: " + found.map(t => t.dataset.story).join(" + ");

  container.innerHTML = "";
  container.appendChild(stage);
  mountToolbox(stage, p);
  return true;
}

/** Story Toolbox: sy_bg, sy_grid, sy_outline, sy_inspect, sy_toolbar */
function mountToolbox(stage, p) {
  const S = { bg: p.get("sy_bg") || "checker", grid: p.get("sy_grid"), outline: p.get("sy_outline"), inspect: p.get("sy_inspect") };
  const on = v => v !== null && !/^(0|false|off|no)$/i.test(v);
  const PRE = { light: "#ffffff", dark: "#14161a" };

  function setP(k, v) {
    const u = new URL(location.href);
    if (v === null) u.searchParams.delete(k); else u.searchParams.set(k, v);
    history.replaceState(null, "", u);
  }

  const grid = document.createElement("div"); grid.id = "sy-grid"; stage.appendChild(grid);
  const hl = document.createElement("div"); hl.id = "sy-hl"; const lb = document.createElement("span"); hl.appendChild(lb); stage.appendChild(hl);

  const raw = p.get("sy_toolbar");
  const mode = window.DevDock || p.get("dock") === "hide" ? "hide"
    : raw === null ? "closed" : (/^(0|false|off|no|hide)$/i.test(raw) ? "hide" : raw.toLowerCase());

  if (mode !== "hide") {
    const bar = document.createElement("div"); bar.id = "sy-toolbar"; bar.setAttribute("role", "region"); bar.setAttribute("aria-label", "Story tools");
    const opts = ["checker", "light", "dark"];
    const cur = S.bg.replace(/^["'\s]+|["'\s]+$/g, "");
    if (!opts.includes(cur.toLowerCase())) opts.push(cur);

    bar.innerHTML = `<button id="sy-hd" aria-expanded="false" aria-controls="sy-pn"><span>Story tools</span><i>▾</i></button>
      <div id="sy-pn" hidden>
        <label>Background <select id="sy-bg">${opts.map(o => `<option value="${o}">${o}</option>`).join("")}</select></label>
        <label>Grid <input type="checkbox" id="sy-g"></label>
        <label>Outline <input type="checkbox" id="sy-o"></label>
        <label>Inspect <input type="checkbox" id="sy-i"></label>
        <button id="sy-x">Hide tools</button>
      </div>`;
    stage.appendChild(bar);

    const hd = bar.querySelector("#sy-hd"), pn = bar.querySelector("#sy-pn"), selEl = bar.querySelector("#sy-bg");
    const setOpen = o => { pn.hidden = !o; bar.classList.toggle("open", o); hd.setAttribute("aria-expanded", o); };
    hd.onclick = () => { const o = pn.hidden; setOpen(o); setP("sy_toolbar", o ? "open" : null); };
    setOpen(mode === "open");

    selEl.value = PRE[cur.toLowerCase()] ? cur.toLowerCase() : cur;
    selEl.onchange = e => { S.bg = e.target.value; setP("sy_bg", S.bg); apply(); };

    [["sy-g", "grid", "sy_grid"], ["sy-o", "outline", "sy_outline"], ["sy-i", "inspect", "sy_inspect"]].forEach(([id, prop, qk]) => {
      bar.querySelector("#" + id).onchange = e => {
        S[prop] = e.target.checked ? (prop === "grid" && on(S.grid) ? S.grid : "1") : null;
        setP(qk, S[prop]);
        apply();
      };
    });
    bar.querySelector("#sy-x").onclick = () => { bar.remove(); setP("sy_toolbar", "hide"); };
  }

  function sel(el) {
    let s = el.tagName.toLowerCase();
    if (el.id) s += "#" + el.id;
    if (el.classList.length) s += "." + Array.from(el.classList).slice(0, 2).join(".");
    return s;
  }

  stage.addEventListener("mousemove", e => {
    if (!on(S.inspect)) return;
    const t = e.target;
    if (t === stage || t === grid) { hl.style.display = "none"; return; }
    const r = t.getBoundingClientRect();
    hl.style.cssText = `display:block;left:${r.left}px;top:${r.top}px;width:${r.width}px;height:${r.height}px`;
    hl.classList.toggle("flip", r.top < 26);
    lb.textContent = `${sel(t)}  ${Math.round(r.width)}×${Math.round(r.height)}`;
  });
  stage.addEventListener("mouseleave", () => { hl.style.display = "none"; });
  stage.addEventListener("click", e => {
    if (!on(S.inspect)) return;
    e.preventDefault(); e.stopPropagation();
    const t = sel(e.target);
    try { navigator.clipboard.writeText(t); } catch {}
    lb.textContent = "copied: " + t;
  }, true);

  function apply() {
    const v = S.bg.replace(/^["'\s]+|["'\s]+$/g, ""), k = v.toLowerCase();
    const c = PRE[k] || (/^[0-9a-f]{3,8}$/i.test(v) ? "#" + v : v);
    stage.style.background = k === "checker" ? "" : (c || "");
    stage.dataset.syBg = PRE[k] ? k : (c ? "custom" : "checker");
    stage.style.colorScheme = k === "dark" ? "dark" : "light";
    const n = parseInt(S.grid, 10);
    grid.style.setProperty("--g", (n > 1 ? n : 8) + "px");
    grid.style.display = on(S.grid) ? "block" : "none";
    stage.toggleAttribute("data-sy-outline", on(S.outline));
    stage.classList.toggle("sy-inspect", on(S.inspect));
    if (!on(S.inspect)) hl.style.display = "none";
  }
  apply();
}

/**
 * mountAppsToolbar(apps) — Floating bottom-right multi-app switcher.
 * Apps list format: [{ name: "Funds", url: "/funds" }, { name: "Dashboard", url: "/dashboard" }, ...]
 * Hidden via ?apps_toolbar=hide (or 0/false/off).
 * Prevents injecting cross-app navigation buttons into authentic page content.
 */
export function mountAppsToolbar(apps = []) {
  if (typeof window === "undefined" || !apps.length) return;
  const p = new URLSearchParams(location.search);
  const existing = document.getElementById("apps-toolbar");
  if (existing) existing.remove();
  const raw = p.get("apps_toolbar");
  if (window.DevDock || p.get("dock") === "hide" || (raw !== null && /^(0|false|off|no|hide)$/i.test(raw))) return;

  const bar = document.createElement("div");
  bar.id = "apps-toolbar";
  bar.setAttribute("role", "region");
  bar.setAttribute("aria-label", "Switch applications");

  const currentPath = location.pathname;
  const currentApp = apps.find(a => a.url === currentPath) || apps[0];

  bar.innerHTML = `
    <div class="apps-menu" hidden>
      <div class="apps-menu-title">Switch App / Surface</div>
      ${apps.map(a => `<a class="apps-menu-item ${a.url === currentPath ? "active" : ""}" href="${a.url}">${a.name}</a>`).join("")}
      <a class="apps-menu-item gallery-link" href="/">All Apps (Gallery)</a>
    </div>
    <button class="apps-btn" aria-expanded="false" aria-label="Toggle application menu">
      <span class="apps-btn-dot"></span>
      <span class="apps-btn-label">${currentApp ? currentApp.name : "Apps"}</span>
      <i class="apps-btn-arrow">▴</i>
    </button>
  `;
  document.body.appendChild(bar);

  const btn = bar.querySelector(".apps-btn");
  const menu = bar.querySelector(".apps-menu");
  btn.onclick = e => {
    e.stopPropagation();
    const open = menu.hidden;
    menu.hidden = !open;
    btn.setAttribute("aria-expanded", String(open));
  };
  document.addEventListener("click", () => {
    if (!menu.hidden) {
      menu.hidden = true;
      btn.setAttribute("aria-expanded", "false");
    }
  });
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
  const title = document.title;

  function runRender() {
    document.title = title;
    render(curState);
    dispatchEvent(new Event("prototype:render"));
    mountStory();
  }

  function sync(changes, opts = {}) {
    curState = patch(curState, changes);
    const qs = toQuery(curState, spec, curForeign);
    const url = location.pathname + qs + location.hash;
    const mode = opts.replace ? "replace"
      : (opts.key ? historyMode(opts.key, spec) : "push");
    history[mode === "replace" ? "replaceState" : "pushState"]({}, "", url);
    runRender();
  }

  window.addEventListener("popstate", () => {
    const r = parse(location.search, spec);
    curState = r.state; curForeign = r.foreign;
    runRender();
  });

  runRender();
  return { sync, state: () => curState };
}
