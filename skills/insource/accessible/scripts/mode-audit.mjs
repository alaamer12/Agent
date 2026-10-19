#!/usr/bin/env node
/**
 * mode-audit.mjs — grade what was actually delivered, against what was asked for.
 *
 *   node mode-audit.mjs --requested ultra --before ../app-origin --after .
 *   node mode-audit.mjs --requested ultra --against <revision-before-the-pass>
 *
 * Why this exists: a pass can be labelled Ultra, tick every box in the checklist from memory,
 * and still be a Medium result — new palette, better spacing, every page exactly as it was
 * structurally. The person then has to notice, say it twice, and the work gets redone. That is
 * a grading failure, and grading is exactly the thing an agent is unreliable at when it is also
 * the author.
 *
 * So the grade comes out of the diff, not out of a recollection of intent. Every criterion
 * below is computed from files, and every one prints the evidence it used.
 *
 * What it cannot see: taste. It will not tell you the result is calm, legible, or good — that
 * is accessible-audit.mjs plus a screenshot you actually looked at. It answers one narrower
 * question: did the moves this mode is supposed to contain actually happen to the structure.
 */
import { readFileSync, readdirSync, existsSync, mkdtempSync, mkdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { execFileSync } from 'node:child_process';
import path from 'node:path';
import { loadProfile, compile } from './profile.mjs';

const argv = process.argv.slice(2);
const flag = (n, d) => { const i = argv.indexOf(`--${n}`); return i === -1 ? d : argv[i + 1]; };
const requested = (flag('requested', 'ultra') || '').toLowerCase();
if (!['lite', 'medium', 'ultra'].includes(requested)) {
  console.error('usage: mode-audit.mjs --requested lite|medium|ultra (--before <dir> --after <dir> | --against <revision>)');
  console.error('                 [--profile base|vue-tailwind|react-tailwind|plain-css|<path.json>] [--ia-note "..."]');
  console.error('\nNo --profile means the neutral base profile, which finds CSS custom properties and');
  console.error('hex literals and nothing else. On a utility-class or Sass stack that under-reads');
  console.error('the code, and every measure it cannot take is reported as NOT MEASURED rather than 0.');
  console.error('Derive a profile for the stack in a few greps: see references/stack-profiles.md.');
  process.exit(2);
}

/*
 * All stack-specific behaviour comes from the profile. The first version hardcoded a Tailwind
 * colour regex, a Vue script-block rule, and a view-file-only extension list — and that last
 * one meant it never read `router/index.ts`, where every route is declared, so a 16-route
 * re-architecture measured as "0 renamed". A grader blind to the thing it grades still prints
 * a number, and the number is wrong in whichever direction it is blind.
 */
const { profile, source: profileSource } = loadProfile(flag('profile', null));
const P = compile(profile);
const EXTS = P.exts;
const SKIP = P.skipDirs;
const SNAPSHOT_DIR = P.snapshotDirRx;
const EXCLUDE_RE = flag('exclude', null) ? new RegExp(flag('exclude'), 'i') : null;

function* walk(dir) {
  if (!existsSync(dir)) return;
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) {
      if (SKIP.has(e.name) || (SNAPSHOT_DIR && SNAPSHOT_DIR.test(e.name)) || (EXCLUDE_RE && EXCLUDE_RE.test(p))) continue;
      yield* walk(p);
    } else if (EXTS.some((x) => p.endsWith(x))) yield p;
  }
}

const rel = (d, p) => path.relative(d, p).split(path.sep).join('/');
const read = (p) => { try { return readFileSync(p, 'utf8'); } catch { return ''; } };

/* ── gather the two sides ───────────────────────────────────────────────────────────── */
let before = new Map(); // rel path -> text
let after = new Map();
let structural = { added: [], removed: [], renamed: [] };

if (flag('against', null)) {
  /*
   * Materialise the whole tree at that revision and compare tree to tree. Diffing only the
   * files a commit touched was tried first and is meaningless: the criteria describe the
   * product (does a token layer exist, is the palette a ramp), and a one-commit slice of it
   * reports "0 -> 0 token definitions" on a commit that rebuilt everything.
   */
  const root = execFileSync('git', ['rev-parse', '--show-toplevel'], { encoding: 'utf8' }).trim();
  const prefix = path.relative(root, path.resolve('.')).split(path.sep).join('/');
  const tmp = mkdtempSync(path.join(tmpdir(), 'mode-audit-'));
  const sub = (dir, rev) => {
    const target = path.join(tmp, dir);
    mkdirSync(target, { recursive: true });
    execFileSync('sh', ['-c', `git archive '${rev}'${prefix ? ` -- '${prefix}'` : ''} | tar -x -C '${target}'`], { cwd: root, stdio: ['ignore', 'ignore', 'ignore'] });
    return prefix ? path.join(target, prefix) : target;
  };
  const B = sub('before', flag('against'));
  const A = sub('after', 'HEAD');
  for (const f of walk(B)) before.set(rel(B, f), read(f));
  for (const f of walk(A)) after.set(rel(A, f), read(f));
  structural.added = [...after.keys()].filter((k) => !before.has(k) && ![...before.keys()].some((b2) => path.basename(b2) === path.basename(k)));
  structural.removed = [...before.keys()].filter((k) => !after.has(k));
  structural.renamed = [...before.keys()].filter((k) => !after.has(k)).map((k) => {
    const hit = [...after.keys()].find((a2) => path.basename(a2) === path.basename(k) && a2 !== k);
    return hit ? [k, hit] : null;
  }).filter(Boolean);
  process.on('exit', () => { try { rmSync(tmp, { recursive: true, force: true }); } catch { /* temp dir */ } });
} else {
  const B = path.resolve(flag('before', '') || '');
  const A = path.resolve(flag('after', '') || '');
  if (!B || !A || !existsSync(B) || !existsSync(A)) {
    console.error('need --before <dir> and --after <dir>, or --against <revision>.');
    console.error('\nA "before" that is your own earlier output is not a before. Point it at the');
    console.error('pre-redesign tree — a real checkout, not a copy of what you produced.');
    process.exit(2);
  }
  for (const f of walk(B)) before.set(rel(B, f), read(f));
  for (const f of walk(A)) after.set(rel(A, f), read(f));
  structural.added = [...after.keys()].filter((k) => !before.has(k) && ![...before.keys()].some((b2) => path.basename(b2) === path.basename(k)));
  structural.removed = [...before.keys()].filter((k) => !after.has(k));
  structural.renamed = [...before.keys()].filter((k) => !after.has(k)).map((k) => {
    const hit = [...after.keys()].find((a2) => path.basename(a2) === path.basename(k) && a2 !== k);
    return hit ? [k, hit] : null;
  }).filter(Boolean);
}

/* ── measures ───────────────────────────────────────────────────────────────────────── */
const all = (m) => [...m.values()].join('\n');
const b = all(before);
const a = all(after);

/*
 * Every measure comes from a stack profile, not from this file's assumptions about the
 * framework. The first version hardcoded a Tailwind colour regex and a Vue script-block rule,
 * so a Sass project with no utility classes scored "0 raw colours — clean" while its
 * stylesheets were full of them. A rule that cannot match anything reports a zero, and a zero
 * looks exactly like a pass.
 *
 * Derive a profile for the stack (references/stack-profiles.md), pass it with --profile, and
 * anything the profile has no rule for is reported NOT MEASURED rather than satisfied.
 */
const n = (v) => (v === null ? 'not measured' : v);
const unmeasured = [];

const colourB = P.colours(b);
const colourA = P.colours(a);
const tokB = P.tokens(b);
const tokA = P.tokens(a);

/*
 * Elevation means a named *scale* that something consumes, not a pile of box-shadow
 * declarations. Moving ad-hoc shadows into tokens makes the raw declaration count go DOWN, so
 * counting the word "shadow" reports a regression on work that is strictly better.
 */
const elevB = P.elevation(b);
const elevA = P.elevation(a);
const typoB = P.patternCount(b, 'typography');
const typoA = P.patternCount(a, 'typography');
const spacB = P.patternCount(b, 'spacing');
const spacA = P.patternCount(a, 'spacing');
for (const [label, ok] of [['raw colour', colourA.measured], ['token definitions', tokA !== null], ['elevation scale', elevA.measured], ['typography', typoA !== null], ['spacing', spacA !== null]]) {
  if (!ok) unmeasured.push(label);
}

const pageFiles = (m) => [...m.keys()].filter((k) => !k.includes('components/') && !k.endsWith('.css'));
const newPages = structural.added.filter((f) => !f.includes('components/') && !f.endsWith('.css'));
const newComponents = structural.added.filter((f) => f.includes('components/') || /primitive|token|theme/i.test(f));

/*
 * The route surface, from the profile's declaration pattern. "Did the information architecture
 * move" has to mean the URLs and their grouping changed — not that a file with "nav" in its name
 * was edited, which an early version accepted and which passed a pass that renamed nothing.
 * Redirect stubs are stripped first: `{ path: '/settings/markets', redirect: '/catalog/…' }`
 * keeps the retired spelling declared, so without this a 16-route re-architecture reads as
 * "0 renamed".
 */
const bR = P.routes(b);
const aR = P.routes(a);
const addedRoutes = [...aR.paths].filter((r) => !bR.paths.has(r));
const goneRoutes = [...bR.paths].filter((r) => !aR.paths.has(r));
// A rename shows up as one path gone and another added that shares its trailing segment.
const renamedRoutes = addedRoutes.filter((x) => goneRoutes.some((o) => path.posix.basename(x) === path.posix.basename(o) && x !== o));
const netNewRoutes = addedRoutes.filter((x) => !renamedRoutes.includes(x));

/**
 * A pass that leaves every route name and every group untouched has not done the structural
 * move, whatever else changed. `--ia-note` exists for the legitimate exception, and requires
 * the reason in writing — an empty note does not clear the bar.
 */
const iaNote = flag('ia-note', '');
const routesMeasured = bR.measured && aR.measured;
const taxonomyDerived = !routesMeasured
  ? false
  : (renamedRoutes.length > 0 || goneRoutes.length > 0 || netNewRoutes.length > 0
    || (iaNote.trim().length > 20 && `[exception accepted: ${iaNote.trim().slice(0, 90)}]`));

const criteria = [
  { mode: 'lite', label: 'Typography and spacing actually moved',
    pass: typoA !== null && spacA !== null && (typoA !== typoB || spacA !== spacB),
    evidence: `type declarations ${n(typoB)} -> ${n(typoA)}, spacing declarations ${n(spacB)} -> ${n(spacA)}` },
  { mode: 'lite', label: 'Hardcoded colour reduced or bounded by tokens',
    pass: colourA.measured && tokA !== null && (colourA.total < colourB.total || tokA > tokB),
    evidence: `raw colour usages ${n(colourB.total)} -> ${n(colourA.total)}${colourA.utility === null ? ' (no utility-class rule; inline literals only)' : ''}; token definitions ${n(tokB)} -> ${n(tokA)}` },
  { mode: 'medium', label: 'Content was redistributed, not restyled in place',
    pass: newComponents.length > 0,
    evidence: `${newComponents.length} new shared component file(s) added${P.localPrefixes.length ? `; local component prefixes: ${P.localPrefixes.join(', ')}` : ''}` },
  { mode: 'medium', label: 'A real token layer exists and is consumed',
    pass: tokA !== null && tokA > 0 && tokA > tokB,
    evidence: `${n(tokB)} -> ${n(tokA)} token declarations` },
  { mode: 'ultra', label: 'The palette was rebuilt, not adjusted',
    pass: tokA !== null && tokA >= Math.max(P.rampMin(), tokB * P.rampFactor()),
    evidence: `${n(tokB)} -> ${n(tokA)} token declarations (profile asks for >= ${P.rampMin()} and >= ${P.rampFactor()}x the starting count — a re-theme adds a ramp, not a hex)` },
  { mode: 'ultra', label: 'An elevation system was introduced',
    pass: elevA.measured && elevA.steps >= P.profile.elevation.minSteps && elevA.consumed > 0 && elevA.steps > elevB.steps,
    evidence: `named elevation steps ${n(elevB.steps)} -> ${n(elevA.steps)}, consumed ${n(elevB.consumed)} -> ${n(elevA.consumed)} times; radius scale ${n(elevB.radiusSteps)} -> ${n(elevA.radiusSteps)} steps` },
  { mode: 'ultra', label: 'The output is structurally different — pages added, split, moved or re-grouped',
    pass: newPages.length > 0 || structural.renamed.length > 0 || structural.removed.length > 0,
    evidence: `${newPages.length} new page file(s), ${structural.renamed.length} moved/renamed, ${structural.removed.length} removed` },
  { mode: 'ultra', label: 'The navigation taxonomy was re-derived — routes renamed, split or dissolved',
    pass: !!taxonomyDerived,
    evidence: routesMeasured
      ? `${bR.paths.size} -> ${aR.paths.size} declared paths · ${renamedRoutes.length} renamed, ${goneRoutes.length} retired, ${netNewRoutes.length} genuinely new. ${typeof taxonomyDerived === 'string' ? taxonomyDerived : ''}`
      : 'NOT MEASURED — the profile has no route-declaration rule for this stack, so this cannot pass on a zero. Add routes.declarationPattern to your profile.' },
];

const want = { lite: 0, medium: 1, ultra: 2 }[requested];
const needFor = { lite: 0, medium: 1, ultra: 2 };
const met = { lite: 0, medium: 0, ultra: 0 };
for (const c of criteria) if (c.pass) met[c.mode]++;

const total = { lite: 2, medium: 2, ultra: 4 };
const reached = met.lite === total.lite
  ? (met.medium >= total.medium ? (met.ultra === total.ultra ? 'ultra' : 'medium') : 'lite')
  : 'none';
const reachedRank = { none: -1, lite: 0, medium: 1, ultra: 2 }[reached];

const lines = [];
lines.push('# Mode audit');
lines.push('');
const srcNote = flag('against', null)
  ? `baseline: tree at \`${flag('against')}\` · current: working tree`
  : `baseline: \`${path.resolve(flag('before', ''))}\` · current: \`${path.resolve(flag('after', ''))}\``;
lines.push(srcNote);
lines.push(`stack profile: **${profileSource}**`);
lines.push('');
if (unmeasured.length) {
  lines.push(`> \x1b[33m${unmeasured.length} measure(s) could not be taken with this profile\x1b[0m — ${unmeasured.join(', ')}.`);
  lines.push('> Those criteria read as failed, not as zero. A rule that matches nothing on a stack');
  lines.push('> that simply uses a different mechanism is a missing profile entry, not a clean pass');
  lines.push('> or a broken one. Fix the profile before believing any verdict here.');
  lines.push('');
}
lines.push('');

/*
 * These criteria measure *change*, so the baseline has to be the state before the pass began.
 * Point it at a revision mid-rollout and the earlier work is not in the diff: the numbers come
 * back flat and the verdict comes back Lite for a pass that already did everything. Two trees
 * that are near-identical are the signature, so say so rather than printing a wrong grade.
 */
const shared = [...after.keys()].filter((k) => before.has(k) && before.get(k) === after.get(k)).length;
const totalFiles = Math.max(after.size, 1);
const sameness = shared / totalFiles;
if (before.size && sameness > 0.9) {
  lines.push(`> \x1b[31m**Baseline looks too narrow** — ${(sameness * 100).toFixed(0)}% of files are byte-identical between the two trees.`);
  lines.push('> The criteria below measure change, so this run would grade almost nothing as done.');
  lines.push('> Point the baseline at the state *before the pass started*, not at the last commit.');
  lines.push('');
  console.log(lines.join('\n'));
  process.exit(2);
}

lines.push(`Requested **${requested.toUpperCase()}**. Measured from the diff, delivered **${reached === 'none' ? 'not even Lite' : reached.toUpperCase()}**.`);
lines.push('');
lines.push('| mode | criterion | met | evidence |');
lines.push('|---|---|---|---|');
for (const c of criteria) lines.push(`| ${c.mode} | ${c.label} | ${c.pass ? '✔' : '**✗**'} | ${c.evidence} |`);
lines.push('');

const gaps = criteria.filter((c) => c.pass === false && needFor[c.mode] <= want);
if (gaps.length) {
  lines.push(`## ${requested} was asked for and these are missing`);
  lines.push('');
  gaps.forEach((g) => lines.push(`- **${g.label}** — ${g.evidence}`));
  lines.push('');
  lines.push('This is not a footnote to write at the end. Either do the move, or deliver the pass');
  lines.push(`under the mode it actually reached and say which one you skipped and why. Do not ship`);
  lines.push(`a ${reached}-grade result labelled ${requested} and let the person discover it — that`);
  lines.push('is the failure this file exists to prevent.');
} else {
  lines.push(`Every criterion for ${requested.toUpperCase()} is met by measurable change, not by assertion.`);
  lines.push('');
  lines.push('This still does not mean the result is *good*. Taste is not measurable here: run');
  lines.push('`accessible-audit.mjs`, look at the screenshot, and answer the mode checklist against');
  lines.push('what you saw.');
}

console.log(lines.join('\n'));
process.exit(gaps.length ? 1 : 0);
