#!/usr/bin/env node
/**
 * map.mjs — the origin ↔ current page map, generated.
 *
 * A rollout over many pages needs two answers fast: which file did this one used to be, and
 * is it done yet. Reading that off git history is slow and error-prone; keeping it by hand
 * means it goes stale within an afternoon, and a stale map is worse than none because it gets
 * trusted.
 *
 *   node map.mjs --src src/pages --snapshot ../app-origin/src/pages --out map.md \
 *        [--ext .vue,.jsx,.tsx] [--ledger design/verification] [--moves moves.json]
 *
 * `--moves` is a JSON object of `{ newPath: oldPath }` for files that were relocated. Without
 * it, a moved page is reported as "new — no ancestor", which reads as unverified work when it
 * is the same component under a different name. Keep it in step with whatever route-redirect
 * table the app has: one is the URL, the other is the file.
 *
 * The map is also where a reviewer's verdict becomes visible. Point --ledger at the directory
 * ledger.mjs writes to and every row carries its latest status, so "we checked it" and "here
 * is the record" are the same column.
 */
import { readdirSync, readFileSync, existsSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { loadProfile, compile } from '../profile.mjs';

const argv = process.argv.slice(2);
const flag = (n, d) => { const i = argv.indexOf(`--${n}`); return i === -1 ? d : argv[i + 1]; };

const SRC = path.resolve(flag('src', 'src'));
const SNAPSHOT = flag('snapshot', null);
const OUT = flag('out', 'map.md');
const LEDGER = flag('ledger', null);
const moves = flag('moves', null);
const MOVED_FROM = moves && existsSync(path.resolve(moves)) ? JSON.parse(readFileSync(moves, 'utf8')) : {};

/*
 * Stack-specific patterns come from a profile (assets/stack-profiles/), the same one
 * mode-audit.mjs reads — see references/stack-profiles.md for deriving one in a few greps.
 * Hardcoding a Tailwind colour list here meant a Sass or CSS-Modules project mapped every page
 * as "0 raw colours left, converted" while its markup was full of literals.
 */
const { profile, source: profileSource } = loadProfile(flag('profile', null));
const P = compile(profile);
const exts = (flag('ext', null) || P.exts.join(',')).split(',').map((e) => (e.startsWith('.') ? e : '.' + e));

/**
 * Utility-palette classes left in markup. Counted in the template only: a class string inside
 * a script block is usually frozen data or a computed, and a gate that counts those can never
 * be satisfied, which turns a real signal into noise.
 */
const PALETTE_SRC = profile.colour?.utilityClasses ?? null;
const RAW_COLOUR_SRC = profile.colour?.inlineLiterals ?? null;
const PREFIX_RX = P.localPrefixes.length ? new RegExp(`<((?:${P.localPrefixes.join('|')})[A-Z]\\w*)`, 'g') : null;

function* walk(dir) {
  if (!existsSync(dir)) return;
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) yield* walk(p);
    else if (exts.some((x) => p.endsWith(x))) yield p;
  }
}

/*
 * Keys are relative to --src, so a snapshot tree and a working tree line up on the same key.
 * Keying off the parent instead produces `pages/pages/x.vue` lookups that all miss, and every
 * page silently reports as new — a map that looks complete and proves nothing.
 */
const relOf = (p) => path.relative(SRC, p).split(path.sep).join('/');
const ancestorOf = (rel) => {
  if (!SNAPSHOT) return null;
  const cand = MOVED_FROM[rel] ?? rel;
  return existsSync(path.join(SNAPSHOT, cand)) ? cand : null;
};

/**
 * Ledger files record paths however the reviewer happened to type them — repo-relative,
 * src-relative, or with a leading dot. Try the spellings rather than silently reporting
 * "not reviewed" for work that was reviewed.
 */
const verdictFor = (rel) => {
  const bare = rel.replace(/^pages\//, '');
  for (const key of [rel, `src/${rel}`, `./src/${rel}`, `src/pages/${bare}`, `./src/pages/${bare}`]) {
    if (verdicts.has(key)) return verdicts.get(key);
  }
  // Last resort: match on the trailing path so a differently-rooted ledger still counts.
  for (const [k, v] of verdicts) if (k.endsWith('/' + rel) || rel.endsWith(k)) return v;
  return null;
};

/** Latest ledger verdict per file, so the map shows coverage rather than implying it. */
const verdicts = new Map();
if (LEDGER && existsSync(path.resolve(LEDGER))) {
  for (const f of readdirSync(path.resolve(LEDGER)).filter((x) => x.endsWith('.jsonl'))) {
    for (const line of readFileSync(path.join(path.resolve(LEDGER), f), 'utf8').split('\n')) {
      if (!line.trim()) continue;
      try { const r = JSON.parse(line); verdicts.set(r.file, r); } catch { /* a torn line is not a verdict */ }
    }
  }
}

const rows = [];
let counts = { done: 0, pending: 0, fresh: 0, failing: 0, dangling: 0, unmeasured: 0 };
for (const file of [...walk(SRC)].sort()) {
  const rel = relOf(file);
  const src = readFileSync(file, 'utf8');
  const sEnd = src.search(/<script|^\s*(?:export\s+default|import\s)/m);
  const markup = sEnd === -1 ? src : src.slice(0, sEnd);
  const body = sEnd === -1 ? '' : src.slice(sEnd);
  const palette = PALETTE_SRC ? (markup.match(new RegExp(PALETTE_SRC, 'g')) || []).length : null;
  const raw = RAW_COLOUR_SRC ? (markup.match(new RegExp(RAW_COLOUR_SRC, 'g')) || []).length : null;
  const leftover = palette === null && raw === null ? null : (palette ?? 0) + (raw ?? 0);

  /*
   * A component used in markup but never imported renders as an unknown element — a blank
   * hole on screen and no error anywhere in source, so a compile check waves it through.
   * Local components are imported by relative path; framework components are registered
   * globally, so only PascalCase names with a known local prefix are treated as suspicious.
   */
  const imported = new Set([...body.matchAll(/import\s+(?:\{([^}]*)\}|(\w+))\s+from/g)].flatMap((m) => (m[1] || m[2] || '').split(',').map((x) => x.trim().split(/\s+as\s+/).pop()).filter(Boolean)));
  const used = PREFIX_RX ? new Set([...markup.matchAll(new RegExp(PREFIX_RX.source, 'g'))].map((m) => m[1])) : new Set();
  const dangling = [...used].filter((c) => !imported.has(c));
  if (dangling.length) counts.dangling++;

  const anc = ancestorOf(rel);
  const v = verdictFor(rel);
  /*
   * `leftover === null` means the profile has no colour rule for this stack. That is reported
   * as unknown, never as "0 left, converted" — the whole failure mode of a hardcoded pattern is
   * that it matches nothing and therefore finds nothing wrong.
   */
  const state = !anc
    ? '🆕 new'
    : leftover === null ? '❔ colour rule not configured'
    : leftover > 0 ? `🟡 ${leftover} raw colour(s) left`
    : '✅ converted';
  if (state.startsWith('🆕')) counts.fresh++;
  else if (state.startsWith('🟡')) counts.pending++;
  else if (state.startsWith('❔')) counts.unmeasured++;
  else counts.done++;
  if (v && v.status !== 'pass') counts.failing++;
  rows.push(`| \`${rel}\` | ${anc ? `\`${anc}\`${MOVED_FROM[rel] ? ' _(moved)_' : ''}` : '—'} | ${state} | ${dangling.length ? `**✗ ${dangling.join(', ')} not imported**` : '—'} | ${v ? (v.status === 'pass' ? `✔ ${v.reviewer}` : `**✗ ${v.status}**`) : '— not reviewed'} |`);
}

const lines = [
  '# Page map — origin, state, review',
  '',
  `Generated by \`map.mjs\` with stack profile \`${profileSource}\`. Do not edit by hand; it is`,
  `rebuilt from the filesystem and the snapshot, and a hand-edited copy is the thing everyone`,
  `trusts and nobody checks.`,
  '',
  SNAPSHOT ? `Snapshot compared against: \`${SNAPSHOT}\`` : 'No snapshot given — every page reports as new. Pass `--snapshot` for a real rollout.',
  '',
  `| | |`,
  `|---|---|`,
  `| pages mapped | ${rows.length} |`,
  `| converted | ${counts.done} |`,
  `| raw colour remaining | ${counts.pending} |`,
  ...(counts.unmeasured ? [`| **colour rule not configured** | ${counts.unmeasured} — pass --profile; this is not a pass |`] : []),
  `| no ancestor | ${counts.fresh} |`,
  `| component used but never imported | ${counts.dangling} |`,
  `| latest verdict not a pass | ${counts.failing} |`,
  '',
  '| page | ancestor | state | wiring | review |',
  '|---|---|---|---|---|',
  ...rows,
  '',
  '`✔` in the review column means a reviewer recorded a pass against that exact path in the',
  'ledger — it is not a claim about intent. Run `ledger.mjs audit` before trusting it: a',
  'ledger full of copy-pasted verdicts will fill this column out happily.',
  '',
  'The wiring column catches the failure a compile check cannot see: a component used in',
  'markup and never imported renders as an unknown element, which is a blank hole on screen',
  'and nothing in source.',
];

writeFileSync(OUT, lines.join('\n') + '\n');
console.log(`${OUT} written — ${rows.length} pages · ${counts.done} converted · ${counts.pending} with raw colour left · ${counts.failing} not passing review`);
