#!/usr/bin/env node
/**
 * stories_check.mjs — validate a component stories registry, cross-check state coverage against the
 * renderer implementations, and emit one URL per card so every state can be *seen* rather than assumed.
 *
 * Usage:
 *   node scripts/stories_check.mjs validate  js/stories.registry.js
 *   node scripts/stories_check.mjs coverage  js/stories.registry.js [--impl js/components]
 *   node scripts/stories_check.mjs urls      js/stories.registry.js [--base http://localhost:5173] [--out cards.txt]
 *   node scripts/stories_check.mjs --selftest
 *
 * Exit: 0 clean, 1 findings, 2 usage/import error. ASCII output.
 *
 * Finding categories:
 *   meta        gallery metadata and facet declarations
 *   schema      a component object that does not match the registry contract
 *   id          malformed or duplicated ids/state keys
 *   states      empty state list, unknown state key referenced elsewhere
 *   props       props keyed to an undeclared state, or a state with no props
 *   duplicate   two states whose props are identical — two cards, one picture
 *   impl        renderer file missing, or a state key never mentioned in it (heuristic)
 *   url         non-unique or malformed card URL
 */
import { pathToFileURL } from "node:url";
import { readFileSync, existsSync, writeFileSync, statSync } from "node:fs";
import path from "node:path";

const KEBAB = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const ALLOWED_COMPONENT_KEYS = ["id", "name", "renderer", "caption", "states", "props", "facets", "notes", "since", "owners"];

// ------------------------------------------------------------------ helpers

// ------------------------------------------------------------------ validate

export function validate(reg) {
  const f = [];
  const meta = reg.meta || {};
  if (!String(meta.title || "").trim()) f.push("meta: no gallery title");
  if (!String(meta.caption || "").trim()) f.push("meta: no gallery caption - state the model (renderer + descriptor) in one line");
  const facets = meta.facets || {};
  for (const [name, values] of Object.entries(facets)) {
    if (!KEBAB.test(name)) f.push(`meta: facet name ${name} is not kebab-case`);
    if (!Array.isArray(values) || !values.length) f.push(`meta: facet ${name} has no values`);
    else for (const v of values) if (!KEBAB.test(v)) f.push(`meta: facet ${name} value ${v} is not kebab-case`);
  }
  const defaults = meta.defaults || {};
  for (const name of Object.keys(facets)) {
    if (!(name in defaults)) f.push(`meta: facet ${name} has no declared default`);
    else if (!facets[name].includes(defaults[name])) f.push(`meta: default ${defaults[name]} for facet ${name} is not one of its values`);
  }
  for (const name of Object.keys(defaults)) if (!(name in facets)) f.push(`meta: defaults declares ${name} which is not a facet`);

  const list = reg.components || [];
  if (!list.length) f.push("schema: the registry has no components");
  const seen = new Set();
  for (const c of list) {
    const who = c && c.id ? c.id : "(unnamed)";
    if (!c || typeof c !== "object") { f.push("schema: a component entry is not an object"); continue; }
    for (const key of Object.keys(c)) if (!ALLOWED_COMPONENT_KEYS.includes(key)) f.push(`schema: ${who} has unknown field '${key}'`);
    if (!c.id || !KEBAB.test(c.id)) f.push(`id: ${who} - id must be kebab-case (it appears in URLs)`);
    if (seen.has(c.id)) f.push(`id: duplicate id '${c.id}' - URLs and reports become ambiguous`);
    seen.add(c.id);
    if (!String(c.name || "").trim()) f.push(`schema: ${who} has no display name`);
    if (!String(c.renderer || "").trim()) f.push(`schema: ${who} has no renderer key`);
    if (!String(c.caption || "").trim()) f.push(`schema: ${who} has no caption - one line saying what the component is for`);

    const states = Array.isArray(c.states) ? c.states : [];
    if (!states.length) f.push(`states: ${who} declares no states - a component with one state is a bug, not a story`);
    const keys = new Set();
    for (const s of states) {
      if (!s || !s.key) { f.push(`states: ${who} has a state without a key`); continue; }
      if (!KEBAB.test(s.key)) f.push(`id: ${who}.${s.key} - state key must be kebab-case (used in ?show-only=)`);
      if (keys.has(s.key)) f.push(`id: ${who} declares state '${s.key}' twice`);
      keys.add(s.key);
      if (!String(s.label || "").trim()) f.push(`states: ${who}.${s.key} has no label - the badge would be empty`);
      for (const k of Object.keys(s)) if (!["key", "label", "note", "via"].includes(k)) f.push(`states: ${who}.${s.key} has unknown field '${k}'`);
      if (s.via !== undefined && !["props", "branch"].includes(s.via)) f.push(`states: ${who}.${s.key} via='${s.via}' must be "props" or "branch"`);
    }
    const props = c.props || {};
    for (const key of Object.keys(props)) {
      if (!keys.has(key)) f.push(`props: ${who} has props for '${key}' which is not a declared state (typo, or a missing state)`);
    }
    for (const key of keys) {
      if (!(key in props)) f.push(`props: ${who}.${key} has no props - the card renders the renderer's defaults; declare them or write props: {}`);
    }
    // two states, one picture
    const byShape = new Map();
    for (const key of keys) {
      const shape = JSON.stringify(props[key] ?? null);
      if (shape === "null" || shape === "{}") continue;
      if (byShape.has(shape)) f.push(`duplicate: ${who}.${key} and ${who}.${byShape.get(shape)} have identical props - two cards showing one picture`);
      else byShape.set(shape, key);
    }
    // per-component facet overrides must use declared facets/values
    for (const [name, values] of Object.entries(c.facets || {})) {
      if (!(name in facets)) f.push(`meta: ${who} overrides facet ${name} which the gallery does not declare`);
      else for (const v of [].concat(values)) if (!facets[name].includes(v)) f.push(`meta: ${who} uses ${name}=${v} which is not a declared value`);
    }
  }
  return f;
}

// ------------------------------------------------------------------ coverage

export function coverage(reg, implDir) {
  const f = [];
  // --impl may point at a DIRECTORY of one-file-per-renderer (shared mode) or at a single BUNDLE
  // file (cloned mode, e.g. js/stories.renderers.js). Both are checked; the difference is where drift hides.
  const bundle = implDir && /\.[cm]?js$/i.test(implDir) && existsSync(implDir) && statSync(implDir).isFile()
    ? implDir : null;
  let bundleSrc = "";
  const notes = [];
  const propsDriven = [];
  if (bundle) {
    try { bundleSrc = readFileSync(bundle, "utf8"); }
    catch (err) { return { findings: [`impl: cannot read bundle ${bundle}: ${err.message}`], notes }; }
    notes.push(`checking a single bundle (${bundle}) - cloned renderers can drift from the pages silently`);
  }
  // whole-word match: "invalid" must not satisfy a declared "valid" state
  const mentions = (src, key) => new RegExp("\\b" + key.replace(/[.*+?^${}()|[\]\\/-]/g, "\\$&") + "\\b", "i").test(src);
  for (const c of reg.components || []) {
    if (!implDir) { f.push(`impl: no --impl given; cannot cross-check ${c.states.length} state(s) of ${c.id}`); break; }
    if (bundle) {
      for (const s of c.states || []) {
        if (s.via === "props") { propsDriven.push(`${c.id}.${s.key}`); continue; }
        if (!mentions(bundleSrc, s.key))
          f.push(`impl: ${c.id}.${s.key} is declared but never branched on in ${path.basename(bundle)} - implement the branch, or declare via: "props"`);
      }
      continue;
    }
    const file = path.join(implDir, `${c.renderer}.js`);
    if (!existsSync(file)) {
      f.push(`impl: ${c.id} -> renderer '${c.renderer}' not found at ${file} (shared renderer missing, or the story cloned it - see references/06)`);
      continue;
    }
    const src = readFileSync(file, "utf8");
    for (const s of c.states || []) {
      if (s.via === "props") { propsDriven.push(`${c.id}.${s.key}`); continue; }
      if (!mentions(src, s.key)) {
        f.push(`impl: ${c.id}.${s.key} is declared but never branched on in ${path.basename(file)} - implement it, or declare via: "props"`);
      }
    }
  }
  if (propsDriven.length) {
    notes.push(`${propsDriven.length} state(s) declared via: "props" (no renderer branch): ${propsDriven.slice(0, 6).join(", ")}${propsDriven.length > 6 ? " ..." : ""} - confirm their props actually differ, or they are duplicate cards`);
  }
  return { findings: f, notes };
}

// ------------------------------------------------------------------ urls

export function cardUrls(reg, base) {
  const defaults = (reg.meta && reg.meta.defaults) || {};
  const urls = [];
  for (const c of reg.components || []) {
    for (const s of c.states || []) {
      const q = new URLSearchParams({ id: c.id, "show-only": s.key });
      for (const [facet, value] of Object.entries(defaults)) if (value !== defaults[facet]) q.set(facet, value);
      urls.push({ component: c.id, state: s.key, url: `${base}/index.stories.html?${q}` });
    }
  }
  const seen = new Set();
  const findings = [];
  for (const u of urls) {
    if (seen.has(u.url)) findings.push(`url: duplicate card URL ${u.url}`);
    seen.add(u.url);
  }
  return { urls, findings };
}

// ------------------------------------------------------------------ fixtures

const BASE = () => ({
  meta: {
    title: "كتالوج", caption: "renderer + descriptor لكل حالة",
    facets: { dir: ["rtl", "ltr"], theme: ["light", "dark"] },
    defaults: { dir: "rtl", theme: "light" },
  },
  components: [
    {
      id: "toggle", name: "مفتاح", renderer: "toggle", caption: "قيمة منطقية",
      states: [{ key: "valid", label: "صحيح" }, { key: "disabled", label: "معطل" }],
      props: { valid: { on: true }, disabled: { on: false } },
    },
    {
      id: "numeric-field", name: "رقم", renderer: "numeric-field", caption: "حدود رقمية",
      states: [{ key: "valid", label: "صحيح" }, { key: "invalid", label: "خطأ" }],
      props: { valid: { value: 3 }, invalid: { value: 99, error: "فوق الحد" } },
    },
  ],
});

function mutate(fn) { const r = BASE(); fn(r); return r; }

const FIXTURES = [
  ["clean", BASE(), []],
  ["no caption in meta", mutate(r => { r.meta.caption = ""; }), ["meta"]],
  ["bad id case", mutate(r => { r.components[0].id = "Toggle_Mode"; }), ["id"]],
  ["duplicate id", mutate(r => { r.components[1].id = "toggle"; }), ["id"]],
  ["no states", mutate(r => { r.components[0].states = []; r.components[0].props = {}; }), ["states"]],
  ["state without label", mutate(r => { r.components[0].states[1].label = " "; }), ["states"]],
  ["props for undeclared state", mutate(r => { r.components[0].props.ghost = {}; }), ["props"]],
  ["state without props", mutate(r => { delete r.components[0].props.valid; }), ["props"]],
  ["identical props two states", mutate(r => { r.components[0].props.disabled = { on: true }; r.components[0].props.valid = { on: true }; }), ["duplicate"]],
  ["unknown field", mutate(r => { r.components[0].colour = "blue"; }), ["schema"]],
  ["facet default not in values", mutate(r => { r.meta.defaults.theme = "sepia"; }), ["meta"]],
  ["state key not kebab", mutate(r => { r.components[0].states[0].key = "IsValid"; }), ["id"]],
];

function selftest() {
  let fails = 0;
  for (const [name, reg, expect] of FIXTURES) {
    const findings = validate(reg);
    const joined = findings.join(" | ");
    const ok = expect.length ? expect.every(e => joined.includes(e)) : findings.length === 0;
    console.log(`${name.padEnd(32)} ${ok ? "PASS" : "FAIL"} ${ok ? "" : "expected " + JSON.stringify(expect) + " got [" + joined.slice(0, 160) + "]"}`);
    if (!ok) fails++;
  }
  // coverage + urls smoke: a real impl file on disk
  const reg = BASE();
  const urls = cardUrls(reg, "http://localhost:5173");
  const expectUrls = 4;
  const urlsOk = urls.urls.length === expectUrls && !urls.findings.length;
  console.log(`${"card urls".padEnd(32)} ${urlsOk ? "PASS" : "FAIL"} (${urls.urls.length}/${expectUrls})`);
  if (!urlsOk) fails++;
  const cov = coverage(reg, null).findings;
  const covOk = cov.some(c => c.startsWith("impl:"));
  console.log(`${"coverage without --impl".padEnd(32)} ${covOk ? "PASS" : "FAIL"}`);
  if (!covOk) fails++;
  console.log(`self-test: ${FIXTURES.length + 2 - fails}/${FIXTURES.length + 2} checks behaved`);
  return fails ? 1 : 0;
}

// ------------------------------------------------------------------ cli

async function main(argv) {
  const cmd = argv[0];
  if (!cmd || cmd === "--selftest" || cmd === "-t") return selftest();
  const file = argv[1];
  if (!file) { console.log("usage: stories_check.mjs <validate|coverage|urls> FILE [--impl DIR] [--base URL] [--out FILE]"); return 2; }
  let reg;
  try {
    const mod = await import(pathToFileURL(path.resolve(file)).href);
    reg = { meta: mod.meta, components: mod.components };
    if (!mod.components) { console.log("schema: the module exports no `components` array"); return 2; }
  } catch (err) {
    console.log(`error: cannot import ${file}: ${err.message}`);
    return 2;
  }
  const flag = name => { const i = argv.indexOf(name); return i >= 0 ? argv[i + 1] : null; };

  let findings = [];
  if (cmd === "validate") findings = validate(reg);
  else if (cmd === "coverage") {
    const cov = coverage(reg, flag("--impl"));
    findings = [...validate(reg), ...cov.findings];
    for (const n of cov.notes) console.log("  note: " + n);
  }
  else if (cmd === "urls") {
    const { urls, findings: uf } = cardUrls(reg, flag("--base") || "http://localhost:5173");
    findings = uf;
    const body = urls.map(u => `${u.url}\t${u.component}.${u.state}`).join("\n") + "\n";
    if (flag("--out")) { writeFileSync(flag("--out"), body); console.log(`wrote ${urls.length} card URL(s) to ${flag("--out")}`); }
    else process.stdout.write(body);
  } else { console.log(`unknown command ${cmd}`); return 2; }

  const count = (reg.components || []).reduce((n, c) => n + (c.states || []).length, 0);
  console.log(`${cmd}: ${(reg.components || []).length} component(s), ${count} card(s), ${findings.length} finding(s)`);
  for (const f of findings) console.log("  - " + f);
  return findings.length ? 1 : 0;
}

main(process.argv.slice(2)).then(code => process.exit(code)).catch(err => {
  console.log("error: " + err.message);
  process.exit(2);
});
