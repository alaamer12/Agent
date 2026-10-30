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
  console.error('                 [--profile base|vue-tailwind|react-tailwind|plain-css|<path.json>] [--ia-note "..."] [--flow-note "..."]');
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

/*
 * The interaction layer. Every other criterion here measures a surface someone *reads*; this
 * one measures the surfaces someone *uses* — forms, dialogs, pickers, multi-step jobs. It
 * exists because a pass can rebuild the palette, split the pages, rename the routes, clear
 * every bar in this file, and leave the way a user creates a thing exactly as it was. That is
 * not a smaller Ultra; it is a different kind of work that this rubric could not previously see.
 *
 * The comparison is a signature of the controls, not of the file: repainting a dialog must not
 * count as redesigning it. Files are paired across the two trees *including renames*, because
 * counting a moved page as a new flow is precisely how a re-skin clears this bar.
 *
 * A nonzero count is not a pass on merit. Ninety repainted dialogs and one touched flow is a
 * zero in substance, and the numbers below are printed so that ratio is visible in the report
 * rather than hidden behind a tick.
 */
const ixMeasured = P.interaction.enabled;
if (!ixMeasured) unmeasured.push('interaction layer');
const sigOf = (t) => { const s = P.interaction.signature(t); return s === null ? null : s.join(' › '); };
const pairs = new Map();
for (const k of before.keys()) if (after.has(k)) pairs.set(k, k);
for (const [bk, ak] of structural.renamed) if (before.has(bk) && after.has(ak) && !pairs.has(bk) && !pairs.has(ak)) pairs.set(bk, ak);

const ix = { redesigned: [], restyled: [], untouched: [], added: [], retired: [] };
if (ixMeasured) {
  for (const [bk, ak] of pairs) {
    if (!P.interaction.isSurface(before.get(bk)) && !P.interaction.isSurface(after.get(ak))) continue;
    if (before.get(bk) === after.get(ak)) { ix.untouched.push(bk); continue; }
    (sigOf(before.get(bk)) !== sigOf(after.get(ak)) ? ix.redesigned : ix.restyled).push(bk);
  }
  for (const k of structural.added) if (P.interaction.isSurface(after.get(k))) ix.added.push(k);
  const renamedFrom = new Set(structural.renamed.map(([b]) => b));
  for (const k of structural.removed) if (!renamedFrom.has(k) && P.interaction.isSurface(before.get(k))) ix.retired.push(k);
}
const flowChanged = ix.redesigned.length + ix.added.length + ix.retired.length;
const ixTotal = flowChanged + ix.restyled.length + ix.untouched.length;
const leftAlone = ix.restyled.length + ix.untouched.length;

/*
 * The bar is not "some flow changed" — a run that touches 3 of 77 dialogs clears that and is
 * the exact pass this criterion was written to catch. The bar is *having looked*: the changed
 * surfaces plus a written account of the ones deliberately left as they were, because leaving
 * a sound flow alone is triage and leaving one unexamined is paint. `--flow-note` is that
 * account, and it is printed into the report rather than accepted silently.
 */
const flowNote = flag('flow-note', '');
const flowNoted = flowNote.trim().length > 20;
/*
 * A tiny population is almost always a profile mismatch, not a formless app: a stack profile whose
 * `exts` do not include the project's view extension scans almost nothing, and the criterion then
 * reports "1 writing surface, 0 changed" as if it had found neglect. It found blindness instead.
 * The failure direction is safe — it never turns a zero into a pass — but it must be legible.
 */
const ixSparse = ixMeasured && ixTotal > 0 && (ixTotal < 3 || ixTotal / Math.max(after.size, 1) < 0.02);
const ixCaution = ixSparse
    ? ` [only ${ixTotal} of ${after.size} scanned files matched the writing-surface pattern — check the profile's \`exts\` and \`interaction.surfacePattern\` against this stack before reading the counts above as a finding]`
    : '';
let flowAccounted = false;
let flowWhy = '';
if (!ixMeasured) {
  flowWhy = 'NOT MEASURED — the profile has no interaction rule for this stack, so this cannot pass on a zero. Add interaction.surfacePattern and interaction.controlPattern to your profile.';
} else if (ixTotal === 0) {
  flowAccounted = '[no writing surfaces declared anywhere in this tree — nothing to redesign]';
} else if (leftAlone === 0) {
  flowAccounted = true;
} else if (flowNoted) {
  flowAccounted = `[exception accounted for: ${flowChanged} of ${ixTotal} redesigned, and the ${leftAlone} left alone are named and justified — "${flowNote.trim().slice(0, 80)}"]`;
} else if (flowChanged === 0) {
  flowWhy = `not one flow was touched across ${ixTotal} writing surfaces, and no --flow-note explains why`;
} else {
  flowWhy = `${flowChanged} of ${ixTotal} touched — which is fine if the other ${leftAlone} were examined and judged sound, and is not fine if they were never looked at. Run again with --flow-note naming what was considered and left.`;
}

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
  { mode: 'ultra', label: 'The interaction layer went through the pass — flows, dialogs and forms redesigned, not repainted',
    pass: !!flowAccounted,
    evidence: ixMeasured
      ? `${ixTotal} writing surface(s): ${ix.redesigned.length} with control structure changed, ${ix.added.length} added, ${ix.retired.length} retired, ${ix.restyled.length} restyled only, ${ix.untouched.length} untouched.${typeof flowAccounted === 'string' ? ' ' + flowAccounted : ''}${flowWhy ? ' — ' + flowWhy : ''}${ixCaution}`
      : flowWhy },
];

const want = { lite: 0, medium: 1, ultra: 2 }[requested];
const needFor = { lite: 0, medium: 1, ultra: 2 };
const met = { lite: 0, medium: 0, ultra: 0 };
for (const c of criteria) if (c.pass) met[c.mode]++;

const total = { lite: 2, medium: 2, ultra: 5 };
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

/*
 * The ratio, spelled out rather than summarised. A tick on the interaction criterion only
 * proves *a* flow moved; what the person needs to see is how many did not, because ninety
 * repainted dialogs and one touched flow is the failure this criterion was added to catch and
 * a boolean cannot tell it apart from a real pass.
 */
if (ixMeasured && ixTotal) {
  const top = P.interaction.listTop;
  const show = (arr, label) => arr.length
    ? [`- **${label}** (${arr.length}): ${arr.slice(0, top).map((f) => '`' + f + '`').join(', ')}${arr.length > top ? ` — +${arr.length - top} more` : ''}`]
    : [];
  lines.push('## Writing surfaces');
  lines.push('');
  lines.push(`${ixTotal} file(s) declare a form, dialog or picker:`);
  lines.push('');
  lines.push(...show(ix.redesigned, 'control structure changed'));
  lines.push(...show(ix.added, 'new'));
  lines.push(...show(ix.retired, 'retired'));
  lines.push(...show(ix.restyled, 'repainted — same controls in the same order'));
  lines.push(...show(ix.untouched, 'byte-identical to the input'));
  lines.push('');
  const left = leftAlone;
  if (left) {
    lines.push(`**${left} of ${ixTotal} writing surfaces were not redesigned.** That is not automatically a`);
    lines.push('shortfall — most existing flows are already sound, and a pass that reworked every one of');
    lines.push('them would probably be churn. But the report has to name which flows were looked at and');
    lines.push('left alone, and why, in the same breath as the palette. If it cannot, they were not');
    lines.push('looked at, and the pass has not done what it claims on the axis people use.');
    lines.push('');
    lines.push('Once they *have* been looked at, record it: `--flow-note "which flows were examined and');
    lines.push('why the rest were left sound"`. The note prints into the report; it is not a waiver.');
    lines.push('');
  }
}

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
  lines.push('This still does not mean the result is *good*, and it does not mean the work was worth');
  lines.push('doing. Taste is not measurable here: run `accessible-audit.mjs`, look at the screenshot,');
  lines.push('and answer the mode checklist against what you saw. Then the report owes one sentence');
  lines.push('no script can produce: **what a user can get done better than before** — faster, with');
  lines.push('fewer errors, by someone who could not do it at all. If that sentence turns out to be a');
  lines.push('list of colours, radii and renamed headings, say that instead and call the pass what it');
  lines.push('is. A pass that only moved paint has no business being reported as Ultra.');
}

console.log(lines.join('\n'));
process.exit(gaps.length ? 1 : 0);
