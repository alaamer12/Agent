#!/usr/bin/env node
/**
 * parity.mjs — compare two sweeps and say, in writing, what the redesign did and did not change.
 *
 * Part of the `accessible` skill's verification scripts. No npm dependencies; Node >= 22.
 *
 *   node parity.mjs --before sweep-before.json --after sweep-after.json [--out parity.md]
 *
 * It answers three separate questions, and they must stay separate because a pass on one
 * says nothing about the others:
 *
 *   render   did every route still mount a page?
 *   runtime  does any route produce console output the other side does not?
 *   values   are the figures a person reads off the screen the same numbers?
 *
 * Errors that only one side produces are the finding. Errors both sides produce are
 * pre-existing: they belong in the report as "found, not caused, not fixed" so nobody later
 * reads them as redesign damage — and so the person can decide whether to ticket them.
 *
 * This tool deliberately cannot tell you the redesign is *correct*. It can only show you it
 * is not obviously broken. The functional pass at the end is a human's, and the checklist it
 * prints is meant to be handed over, not worked through alone.
 */
import { readFileSync, writeFileSync } from 'node:fs';

const argv = process.argv.slice(2);
const flag = (n, d) => { const i = argv.indexOf(`--${n}`); return i === -1 ? d : argv[i + 1]; };
const beforePath = flag('before', null);
const afterPath = flag('after', null);
const outPath = flag('out', 'parity.md');
if (!beforePath || !afterPath) {
  console.error('usage: node parity.mjs --before sweep-before.json --after sweep-after.json [--out parity.md]');
  process.exit(2);
}
const B = JSON.parse(readFileSync(beforePath, 'utf8'));
const A = JSON.parse(readFileSync(afterPath, 'utf8'));

/** Collapse anything that varies between runs — origins, cache-busting hashes, line numbers. */
const norm = (s) => String(s)
  .replace(/https?:\/\/\S+/g, '')
  .replace(/\?v=[0-9a-z]+/g, '')
  .replace(/\.js:\d+:\d+/g, '.js')
  .replace(/chunk-[A-Z0-9]+/g, 'chunk')
  .replace(/\s+/g, ' ').trim().slice(0, 140);

const routes = [...new Set([...Object.keys(A.results), ...Object.keys(B.results)])];
const missing = { onlyAfter: routes.filter((r) => !(r in B.results)), onlyBefore: routes.filter((r) => !(r in A.results)) };

const newlyDead = routes.filter((r) => A.results[r] && B.results[r] && !A.results[r].rendered && B.results[r].rendered);
const newlyAlive = routes.filter((r) => A.results[r] && B.results[r] && A.results[r].rendered && !B.results[r].rendered);

const afterOnly = [], beforeOnly = [], shared = [];
for (const r of routes) {
  const a = A.results[r]?.errors || [];
  const b = B.results[r]?.errors || [];
  const an = new Set(a.map((e) => norm(e.text)));
  const bn = new Set(b.map((e) => norm(e.text)));
  const extra = [...an].filter((e) => !bn.has(e));
  const gone = [...bn].filter((e) => !an.has(e));
  const both = [...an].filter((e) => bn.has(e));
  if (extra.length) afterOnly.push({ route: r, errors: extra });
  if (gone.length) beforeOnly.push({ route: r, errors: gone });
  if (both.length) shared.push({ route: r, errors: both });
}

const valueRows = [];
for (const r of routes) {
  const a = A.results[r]?.values || {};
  const b = B.results[r]?.values || {};
  const keys = [...new Set([...Object.keys(a), ...Object.keys(b)])];
  if (!keys.length) continue;
  const diffs = keys.filter((k) => norm(a[k]) !== norm(b[k]));
  valueRows.push({ route: r, keys, diffs, allZero: [a, b].some((v) => Object.keys(v).length && !Object.values(v).some((x) => /[1-9]/.test(String(x)))) });
}
const valueDiffs = valueRows.filter((v) => v.diffs.length);

const L = [];
L.push('# Visual and runtime parity: before vs after');
L.push('');
L.push(`| | before | after |`);
L.push(`|---|---|---|`);
L.push(`| side | \`${B.side}\` | \`${A.side}\` |`);
L.push(`| base | ${B.base} | ${A.base} |`);
L.push(`| routes | ${Object.keys(B.results).length} | ${Object.keys(A.results).length} |`);
L.push(`| did not render | ${Object.values(B.results).filter((r) => !r.rendered).length} | ${Object.values(A.results).filter((r) => !r.rendered).length} |`);
L.push(`| console errors | ${Object.values(B.results).reduce((n, r) => n + (r.errors?.length || 0), 0)} | ${Object.values(A.results).reduce((n, r) => n + (r.errors?.length || 0), 0)} |`);
L.push('');
L.push(`- **routes only on the after side:** ${missing.onlyAfter.length ? missing.onlyAfter.map((r) => `\`${r}\``).join(', ') : 'none'}`);
L.push(`- **routes only on the before side:** ${missing.onlyBefore.length ? missing.onlyBefore.map((r) => `\`${r}\``).join(', ') : 'none'}`);
L.push(`- **rendered before, broken after:** ${newlyDead.length ? '**' + newlyDead.join(', ') + '**' : 'none'}`);
L.push(`- **broken before, fixed by the pass:** ${newlyAlive.length ? newlyAlive.join(', ') : 'none'}`);
L.push(`- **console errors unique to the after side:** ${afterOnly.length ? '**' + afterOnly.length + ' route(s)**' : 'none'}`);
L.push(`- **extracted figures that differ:** ${valueDiffs.length ? '**' + valueDiffs.length + ' route(s)**' : (valueRows.length ? 'none' : 'not measured — pass --values to sweep.mjs')}`);
L.push('');

if (afterOnly.length) {
  L.push('## Regressions to fix before this is delivered');
  L.push('');
  afterOnly.forEach((o) => { L.push(`- \`${o.route}\``); o.errors.forEach((e) => L.push(`  - ${e}`)); });
  L.push('');
}
if (valueDiffs.length) {
  L.push('## Figures that changed');
  L.push('');
  L.push('| route | figure | before | after |');
  L.push('|---|---|---|---|');
  valueDiffs.forEach((v) => v.diffs.forEach((k) => L.push(`| \`${v.route}\` | ${k} | ${JSON.stringify(B.results[v.route]?.values?.[k] ?? '—')} | ${JSON.stringify(A.results[v.route]?.values?.[k] ?? '—')} |`)));
  L.push('');
  L.push('A changed figure is not automatically a defect — a redesign legitimately adds units and');
  L.push('denominators. It is a thing to look at and either explain or fix.');
  L.push('');
}
if (shared.length) {
  L.push('## Present on both sides — found, not caused');
  L.push('');
  L.push('These occur on the pre-redesign build too. Report them as pre-existing so nobody');
  L.push('attributes them to this pass, and let the person decide whether to ticket them.');
  L.push('');
  shared.forEach((o) => { L.push(`- \`${o.route}\``); o.errors.forEach((e) => L.push(`  - ${e}`)); });
  L.push('');
}
if (beforeOnly.length) {
  L.push('## Removed by the pass');
  L.push('');
  beforeOnly.forEach((o) => { L.push(`- \`${o.route}\`: ${o.errors.join(' · ')}`); });
  L.push('');
}

L.push('## Hand this to a person');
L.push('');
L.push('Machine parity is not the same as "the product still works". Ask someone who uses it to');
L.push('check, on the redesigned build:');
L.push('');
L.push('1. The numbers on the main screens match what they expect from the database.');
const sample = routes.filter((r) => A.results[r]?.rendered).slice(0, 12);
L.push(`2. These routes still do their job end to end: ${sample.map((r) => '`' + r + '`').join(', ') || '(none captured)'}.`);
L.push('3. Every filter, sort, page-size control, row action and bulk action still fires — the');
L.push('   ones a redesign most often breaks are the ones that were wired to a component that');
L.push('   got swapped, because a swapped component can quietly drop a binding that still');
L.push('   compiles.');
L.push('4. Anything that writes: forms, saves, deletes, exports. Read-only parity proves nothing');
L.push('   about a mutation.');
L.push('5. The console is clean while *they* click around, which finds the paths a walk of');
L.push('   first-load states never touches.');
L.push('');
writeFileSync(outPath, L.join('\n') + '\n');

const bad = afterOnly.length + newlyDead.length + valueDiffs.length;
console.log(L.join('\n'));
console.log(`\n\x1b[1m${bad ? '\x1b[33m' + bad + ' item(s) need a look\x1b[0m' : '\x1b[32m✓ no parity difference detected between the two builds\x1b[0m'} — wrote ${outPath}`);
process.exit(bad ? 1 : 0);
