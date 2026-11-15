#!/usr/bin/env node
/**
 * identity.mjs — the mechanical half of "no logic changed".
 *
 * A visual pass is safe only if everything that decides behaviour survives untouched. Reading
 * the diff and feeling confident is not that check; this snapshots the behaviour surface per
 * file so a later run asserts equality instead of trusting an eye.
 *
 *   node identity.mjs snapshot src/pages --out identity.json [--profile vue]
 *   node identity.mjs diff     src/pages --baseline identity.json [--allow-imports]
 *
 * HARD — any change fails the file:
 *   scriptHash   the logic block, byte-identical (imports may be excluded, see below). If the
 *                logic block never changed, no handler body, computed, effect or call site can
 *                have. For this job that is a stronger guarantee than a typechecker.
 *   bindings     every two-way binding, event handler, conditional and disabled expression in
 *                the markup. Layout may move freely; wiring may not.
 *   emits        declared event names.
 *   callSites    API / data-layer call sites.
 *
 * ADVISORY — reported, never fails: element tag counts (swapping a control for a primitive is
 * the point of the pass), and style-block sizes.
 *
 * `--allow-imports` excludes import lines from the hash. Adding an import for a new shared
 * component is normal in a redesign; without this flag every converted file fails for a reason
 * that has nothing to do with behaviour. Removing an import that still has a live reference is
 * still caught, because the reference itself fails to resolve.
 *
 * The baseline must come from the ORIGINAL, not from your own earlier output. A baseline
 * regenerated after the pass starts freezes the redesign and reports zero failures while
 * comparing nothing — which happened here, and looked like success.
 */
import { readdirSync, readFileSync, existsSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import path from 'node:path';

const argv = process.argv.slice(2);
const flag = (n, d) => { const i = argv.indexOf(`--${n}`); return i === -1 ? d : argv[i + 1]; };
const has = (n) => argv.includes(`--${n}`);
const cmd = argv[0];
const ROOT = path.resolve(argv[1] || 'src');
const exts = flag('ext', '.vue,.jsx,.tsx,.svelte').split(',').map((e) => (e.startsWith('.') ? e : '.' + e));

const PROFILES = {
  vue: {
    script: (s) => (s.match(/<script[^>]*>([\s\S]*?)<\/script>/g) || []).join('\n'),
    bindings: (s) => [
      ...(s.match(/v-model(:[\w-]+)?="[^"]*"/g) || []),
      ...(s.match(/@[.\w-]+="[^"]*"/g) || []),
      ...(s.match(/v-on:[.\w-]+="[^"]*"/g) || []),
      ...(s.match(/v-if="[^"]*"/g) || []),
      ...(s.match(/v-else-if="[^"]*"/g) || []),
      ...(s.match(/v-show="[^"]*"/g) || []),
      ...(s.match(/:(?:disabled|loading|modelValue|options|items|rules)="[^"]*"/g) || []),
      ...(s.match(/ref="[^"]*"/g) || []),
    ],
    emits: (s) => [...s.matchAll(/defineEmits[^)]*\[([\s\S]*?)\]/g)].flatMap((m) => [...m[1].matchAll(/['"]([^'"]+)['"]/g)].map((x) => x[1])),
    calls: (s) => [...s.matchAll(/\b[\w$.]+\.[\w$]+\.(?:query|mutation|useQuery|useMutation|fetch|get|post|put|delete)\b/g)].map((m) => m[0]),
  },
  react: {
    script: (s) => s,
    bindings: (s) => [
      ...(s.match(/\bon[A-Z]\w*=\{[^}]*\}/g) || []),
      ...(s.match(/\bvalue=\{[^}]*\}/g) || []),
      ...(s.match(/\bchecked=\{[^}]*\}/g) || []),
      ...(s.match(/\{[^{}]*&&\s*<[\s\S]{0,120}?\}/g) || []),
      ...(s.match(/\bdisabled=\{[^}]*\}/g) || []),
      ...(s.match(/\buseRef(?:<[^>]*>)?\(/g) || []),
    ],
    emits: (s) => [...s.matchAll(/\bprops\.(\w+)\s*\(/g)].map((m) => m[1]),
    calls: (s) => [...s.matchAll(/\b(?:api|queryClient|fetch|axios|trpc)\b[\w$.()]*/g)].map((m) => m[0].slice(0, 60)),
  },
};

function detect(text, file) {
  if (file.endsWith('.vue') || /defineEmits|v-model=/.test(text)) return 'vue';
  return 'react';
}

function* walk(dir) {
  if (!existsSync(dir)) return;
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) yield* walk(p);
    else if (exts.some((x) => p.endsWith(x))) yield p;
  }
}

/*
 * The normalisation has to be recorded in the baseline and reused by the diff. Two runs that
 * hash under different rules disagree on every file that gained an import, which looks exactly
 * like a broken refactor and is really a misconfigured comparison.
 */
let STRIP_IMPORTS = has('allow-imports');

const stripImports = (text) => text.split('\n').filter((l) => !/^\s*import\s|^\s*}\s*from\s|^\s*export\s+\*\s+from/.test(l)).join('\n');

function fingerprint(file) {
  const text = readFileSync(file, 'utf8');
  const profile = PROFILES[detect(text, file)] ?? PROFILES.react;
  const script = profile.script(text) || text;
  const tags = {};
  for (const m of text.matchAll(/<([A-Za-z][\w.-]*)/g)) tags[m[1]] = (tags[m[1]] || 0) + 1;
  return {
    scriptHash: createHash('sha256').update(STRIP_IMPORTS ? stripImports(script) : script).digest('hex'),
    bindings: [...profile.bindings(text)].sort(),
    emits: [...new Set(profile.emits(text))].sort(),
    callSites: [...profile.calls(text)].sort(),
    tags,
    lines: text.split('\n').length,
  };
}

/*
 * Keys are relative to ROOT, not to its parent, so a baseline taken from one tree (the
 * pre-redesign checkout) lines up with a diff run over another (the working tree). Keying on
 * the parent directory silently produced zero overlapping files and a clean report.
 */
const rel = (f) => path.relative(ROOT, f).split(path.sep).join('/');

if (cmd === 'snapshot') {
  const out = flag('out', 'identity.json');
  const baseline = {};
  for (const f of walk(ROOT)) baseline[rel(f)] = fingerprint(f);
  writeFileSync(out, JSON.stringify({ at: new Date().toISOString(), root: ROOT, normalisation: { stripImports: STRIP_IMPORTS, exts }, files: baseline }, null, 2));
  console.log(`snapshotted ${Object.keys(baseline).length} files -> ${out}`);
  console.log(`  normalisation: imports ${STRIP_IMPORTS ? 'stripped from the hash' : 'included in the hash'}`);
  console.log('  Keep this from the ORIGINAL state. Regenerating it after the pass proves nothing.');
  process.exit(0);
}

if (cmd !== 'diff') {
  console.error('usage: identity.mjs snapshot <dir> --out baseline.json\n       identity.mjs diff <dir> --baseline baseline.json [--allow-imports]');
  process.exit(2);
}

const baselinePath = flag('baseline', null);
if (!baselinePath || !existsSync(baselinePath)) { console.error('pass --baseline <file> that exists'); process.exit(2); }
const parsed = JSON.parse(readFileSync(baselinePath, 'utf8'));
const base = parsed.files;
const wantStrip = !!parsed.normalisation?.stripImports;
/*
 * The baseline carries its own normalisation and the diff inherits it, so the common case is
 * just `diff --baseline x.json`. It only refuses when the caller *explicitly* asks for the
 * other rule — that is a misunderstanding worth stopping on, because hashing one side with
 * imports and the other without disagrees on every converted file.
 */
if (has('allow-imports') && !wantStrip) {
  console.error('\x1b[31mconflicting instruction\x1b[0m — you asked to strip imports, but this baseline was hashed with them KEPT.');
  console.error('  Re-snapshot with --allow-imports from the ORIGINAL tree, or drop the flag. Do not re-snapshot after the pass to make the count move.');
  process.exit(2);
}
STRIP_IMPORTS = wantStrip;

const multi = (a) => JSON.stringify([...a].sort());
let checked = 0; const failures = []; const notes = []; const vanished = [];

for (const [key, was] of Object.entries(base)) {
  const file = path.join(ROOT, key);
  if (!existsSync(file)) { vanished.push(key); continue; }
  const now = fingerprint(file);
  checked++;
  const bad = [];
  if (now.scriptHash !== was.scriptHash) {
    const t = readFileSync(file, 'utf8');
    const prof = PROFILES[detect(t, key)] ?? PROFILES.react;
    const onlyImports = !STRIP_IMPORTS
      && createHash('sha256').update(stripImports(prof.script(t) || t)).digest('hex') === was.scriptHash;
    bad.push(onlyImports
      ? 'logic block differs only by import lines — take the baseline with --allow-imports if that is the whole change'
      : 'logic block changed');
  }
  if (multi(now.bindings) !== multi(was.bindings)) {
    const gone = was.bindings.filter((b) => !now.bindings.includes(b));
    const added = now.bindings.filter((b) => !was.bindings.includes(b));
    bad.push(`bindings changed (−${gone.length} +${added.length})${gone.length ? ': ' + gone.slice(0, 3).join(' | ') : ''}`);
  }
  if (multi(now.emits) !== multi(was.emits)) bad.push(`emits changed: ${multi(was.emits)} -> ${multi(now.emits)}`);
  if (multi(now.callSites) !== multi(was.callSites)) bad.push(`call sites changed (−${was.callSites.filter((c) => !now.callSites.includes(c)).length} +${now.callSites.filter((c) => !was.callSites.includes(c)).length})`);
  const tagDelta = Object.entries(now.tags).filter(([t]) => was.tags[t] !== undefined && now.tags[t] !== was.tags[t]).length;
  if (bad.length) failures.push([key, bad]);
  else if (tagDelta) notes.push(`${key}: ${tagDelta} element count(s) differ — expected for a component swap`);
}

console.log(`${checked}/${Object.keys(base).length} files compared against the baseline`);
if (vanished.length) {
  console.log(`\n\x1b[31m${vanished.length} baselined file(s) no longer exist at that path:\x1b[0m`);
  vanished.forEach((v) => console.log('  ' + v));
  console.log('  A moved file looks identical to a deleted one. If it moved, update the move table');
  console.log('  and re-snapshot from the origin — do not quietly drop it from the baseline.');
}
if (notes.length) { console.log(`\nadvisory (${notes.length}):`); notes.slice(0, 12).forEach((n) => console.log('  · ' + n)); }
if (failures.length) {
  console.log(`\n\x1b[31m${failures.length} file(s) broke the behaviour surface:\x1b[0m`);
  failures.forEach(([f, why]) => console.log(`  ${f}\n    ${why.join('\n    ')}`));
  process.exit(1);
}
if (!checked) { console.log('\n\x1b[31mnothing was compared — this run proves nothing\x1b[0m'); process.exit(1); }
console.log('\n\x1b[32m✓ every file keeps its logic block, bindings, emits and call sites\x1b[0m');
process.exit(vanished.length ? 1 : 0);
