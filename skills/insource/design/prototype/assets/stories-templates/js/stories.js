/**
 * stories.js — the component gallery shell.
 *
 * Owns: URL state, descriptor parsing, search filtering, section + card rendering, facet switches.
 * Never owns: component markup (that is the renderer's job) or component styles (that is the
 * component's CSS layer).
 *
 * STATE HELPER: this file uses a tiny local wrapper so the template runs standalone. In a real
 * prototype project, DELETE the wrapper and import the project's existing helper from js/_app.js —
 * one state helper per project is the rule. The wrapper's API mirrors it: read(key, fallback),
 * write(patch, {replace}), and it always preserves unrelated params.
 */

import { meta, components } from "./stories.registry.js";

/* ---------- state: delete this block and import the project's helper ---------- */
const params = new URLSearchParams(location.search);
const state = {
  read(key, fallback) {
    const v = params.get(key);
    return v === null || v === "" ? fallback : v;
  },
  write(patch, { replace = false } = {}) {
    for (const [k, v] of Object.entries(patch)) {
      if (v === null || v === undefined || v === "") params.delete(k);
      else params.set(k, String(v));
    }
    const qs = params.toString();
    const url = location.pathname + (qs ? "?" + qs : "");
    history[replace ? "replaceState" : "pushState"]({}, "", url);
  },
};
/* ----------------------------------------------------------------------------- */

const root = document.getElementById("stories-root");

/** `@facet: value` descriptors are filter commands; anything else is a text query. */
function parseInput(raw) {
  const text = (raw || "").trim();
  const m = /^@(\w[\w-]*)\s*:?\s*(.*)$/u.exec(text);
  if (!m) return { kind: "query", value: text };
  const facet = m[1].toLowerCase();
  const value = m[2].trim();
  if (facet === "state") return { kind: "states", value };
  if (facet === "id") return { kind: "id", value };
  if (facet === "name") return { kind: "query", value };
  if (meta.facets[facet]) return { kind: "facet", facet, value };
  return { kind: "unknown", value: "@" + facet };
}

function readUrl() {
  const showOnly = (state.read("show-only", "") || "")
    .split(",").map(s => s.trim().toLowerCase()).filter(Boolean);
  return {
    q: state.read("q", "").toLowerCase(),
    showOnly,
    id: state.read("id", ""),
    facets: Object.fromEntries(
      Object.entries(meta.facets).map(([name, allowed]) =>
        [name, allowed.includes(state.read(name, meta.defaults[name]))
          ? state.read(name, meta.defaults[name]) : meta.defaults[name]])),
  };
}

function supports(component, stateKey) {
  return component.states.some(s => s.key === stateKey);
}

function matchesQuery(component, q) {
  if (!q) return true;
  const haystack = [component.id, component.name, component.caption,
    ...component.states.flatMap(s => [s.key, s.label, s.note || ""])].join(" ").toLowerCase();
  return haystack.includes(q);
}

/** The card set to render for one component under the current view. */
function visibleStates(component, view) {
  const all = component.states.map(s => s.key);
  const scoped = view.showOnly.length ? all.filter(k => view.showOnly.includes(k)) : all;
  return scoped.map(key => component.states.find(s => s.key === key));
}

function el(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined) node.textContent = text;
  return node;
}

/* ---------- renderers -------------------------------------------------------- */

function renderHeader(view, shown, total) {
  const header = el("header", "stories__header");
  const controls = el("div", "stories__controls");
  for (const [facet, values] of Object.entries(meta.facets)) {
    const group = el("div", "stories__facet");
    group.dataset.facet = facet;
    for (const value of values) {
      const btn = el("button", "facet-btn" + (view.facets[facet] === value ? " is-active" : ""), value);
      btn.type = "button";
      btn.setAttribute("aria-pressed", String(view.facets[facet] === value));
      btn.addEventListener("click", () => {
        state.write({ [facet]: value });
        render();
      });
      group.append(btn);
    }
    controls.append(group);
  }

  const title = el("h1", "stories__title", meta.title);
  const caption = el("p", "stories__caption", meta.caption);
  const count = el("p", "stories__count", `${shown} / ${total}`);
  count.setAttribute("aria-live", "polite");

  const search = el("input", "stories__search");
  search.type = "search";
  search.id = "stories-search";
  search.placeholder = "ابحث أو اكتب ‎@state: disabled‎";
  search.setAttribute("aria-label", "بحث أو وصف الحالة");
  search.value = state.read("q", "");
  search.addEventListener("input", () => {
    const parsed = parseInput(search.value);
    if (parsed.kind === "query") state.write({ q: parsed.value, id: null }, { replace: true });
    else if (parsed.kind === "states") state.write({ "show-only": parsed.value.split(",").map(s => s.trim()).join(","), q: null }, { replace: true });
    else if (parsed.kind === "id") state.write({ id: parsed.value, q: null }, { replace: true });
    else if (parsed.kind === "facet") state.write({ [parsed.facet]: parsed.value, q: null }, { replace: true });
    else state.write({ q: parsed.value }, { replace: true });
    render();
  });

  header.append(controls, title, caption, el("label", "stories__search-label", "بحث"), search, count);
  return header;
}

function renderCard(component, stateDef, view) {
  const card = el("article", "story-card");
  card.dataset.component = component.id;
  card.dataset.state = stateDef.key;

  const badge = el("span", "story-card__state", stateDef.label);
  const url = new URL(location.href);
  url.search = "";
  url.searchParams.set("id", component.id);
  url.searchParams.set("show-only", stateDef.key);
  for (const [f, v] of Object.entries(view.facets)) if (v !== meta.defaults[f]) url.searchParams.set(f, v);
  const link = el("a", "story-card__permalink", "↗");
  link.href = url.pathname + "?" + url.searchParams.toString();
  link.title = "رابط هذه الحالة";

  card.append(el("div", "story-card__head", [badge, link]));
  const stage = el("div", "story-card__stage");
  stage.append(renderComponent(component, stateDef.key));
  card.append(stage);
  if (stateDef.note) card.append(el("p", "story-card__note", stateDef.note));
  return card;
}

/**
 * renderComponent — the seam. In a real project this resolves the renderer from
 * js/components/<renderer>.js (preferred) or from a story-local map, and calls it with
 * (propsForState, stateKey). It must return the SAME markup the pages produce.
 */
import { renderers } from "./stories.renderers.js";

function resolveRenderer(component) {
  const fn = renderers[component.renderer];
  if (!fn) return missingRenderer(component);
  return fn;
}

function missingRenderer(component) {
  const box = el("div", "story-card__missing");
  box.append(el("strong", null, "renderer غير موجود: " + component.renderer));
  box.append(el("span", null, "أضِفه في js/components/ أو صحّح الـ id في الـ registry"));
  return box;
}

function renderComponent(component, stateKey) {
  const props = (component.props && component.props[stateKey]) || {};
  try {
    return resolveRenderer(component)(props, stateKey);
  } catch (err) {
    const box = el("div", "story-card__error");
    box.append(el("strong", null, "فشل الرسم: " + component.id + " / " + stateKey));
    box.append(el("span", null, String(err && err.message ? err.message : err)));
    return box;   // one broken card never blanks the gallery
  }
}

function renderSection(component, view) {
  const states = visibleStates(component, view);
  if (!states.length) return null;
  const section = el("section", "story-group");
  section.dataset.id = component.id;
  const head = el("div", "story-group__head");
  head.append(el("h2", "story-group__name", component.name),
    el("code", "story-group__id", component.id));
  section.append(head);
  if (component.caption) section.append(el("p", "story-group__caption", component.caption));
  const grid = el("div", "story-group__grid");
  for (const s of states) grid.append(renderCard(component, s, view));
  section.append(grid);
  return section;
}

function render() {
  const view = readUrl();
  for (const [facet, value] of Object.entries(view.facets)) {
    document.documentElement.dataset[facet] = value;
    if (facet === "dir") document.documentElement.setAttribute("dir", value);
  }
  const pool = view.id ? components.filter(c => c.id === view.id) : components;
  const matched = pool.filter(c => matchesQuery(c, view.q));
  root.replaceChildren();
  let shown = 0;
  for (const component of matched) {
    const section = renderSection(component, view);
    if (section) { root.append(section); shown += 1; }
  }
  if (!shown) {
    const empty = el("p", "stories__empty");
    empty.append("لا نتائج مطابقة. ",
      el("code", null, view.showOnly.length ? "show-only=" + view.showOnly.join(",") : (view.q ? "q=" + view.q : "(empty)")),
      " — جرّب مسح البحث أو عرض كل الحالات.");
    root.append(empty);
  }
  root.prepend(renderHeader(view, shown, components.length));
  // the search input is rebuilt on every render; restore focus and caret for typing continuity
  if (document.activeElement && document.activeElement.id === "stories-search") {
    const next = root.querySelector("#stories-search");
    if (next) { next.focus(); next.setSelectionRange(next.value.length, next.value.length); }
  }
}

window.addEventListener("popstate", render);
render();
