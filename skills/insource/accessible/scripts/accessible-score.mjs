#!/usr/bin/env node
/**
 * accessible-score.mjs — one composite score from accessible-audit.mjs output.
 *
 *   node accessible-score.mjs <file.html|report.json> [...] [--json] [--chrome path]
 *
 * Design rules, in order of importance:
 *
 * 1. GATES BEFORE POINTS. A contrast violation is not something you can earn your way
 *    out of with generous padding. Hard failures cap the grade regardless of how high
 *    the composite scores. A page cannot be "Excellent" while failing WCAG.
 *
 * 2. EVERY DIMENSION IS EXPLAINED. A bare number is vibes with decimals. Each dimension
 *    prints the specific terms that moved it, so a score can be argued with and fixed.
 *
 * 3. WEIGHTS ARE CALIBRATED, NOT INVENTED. Anchored to three human judgements on the
 *    SNDUK admin pass: a dark direction rated painful, and two light directions where
 *    the shorter one was preferred despite the taller one having slightly better tap
 *    targets. That is a small sample — see CAVEATS at the bottom of the output.
 *
 * 4. PALETTE COHERENCE, NOT COLOUR COUNT. Many shades in one temperature is a good
 *    ramp and is rewarded. Five unrelated saturated hues all claiming attention is a
 *    rainbow and is penalised. The metric never asks for fewer colours.
 *
 * 5. SURFACE-TYPE AWARE. A long page is not a long page if the height is a paginated
 *    data table. Length is scored against effective height, not raw.
 */

import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';

const argv = process.argv.slice(2);
const OPTS = new Set(['--chrome', '--exclude', '--out', '--baseline', '--width', '--height']);
const positional = argv.filter((a) => !a.startsWith('--') && !OPTS.has(argv[argv.indexOf(a) - 1]));
const flag = (n, f) => { const i = argv.indexOf(`--${n}`); return i === -1 ? f : argv[i + 1]; };
const asJson = argv.includes('--json');
if (!positional.length) { console.error('usage: node accessible-score.mjs <file.html|report.json> [...] [--json] [--chrome path]'); process.exit(2); }

const AUDIT = path.join(path.dirname(new URL(import.meta.url).pathname), 'accessible-audit.mjs');
const clamp = (n, lo = 0, hi = 100) => Math.max(lo, Math.min(hi, n));
const r1 = (n) => Math.round(n * 10) / 10;

/* ------------------------------------------------------------- load reports */

const reports = positional.map((src) => {
  if (src.endsWith('.json')) return { name: path.basename(src).replace(/\.json$/, ''), report: JSON.parse(readFileSync(src, 'utf8')) };
  const out = path.join(tmpdir(), `score-${Date.now()}-${Math.random().toString(36).slice(2)}.json`);
  const args = [AUDIT, path.resolve(src), '--out', out];
  const chrome = flag('chrome', null); if (chrome) args.push('--chrome', chrome);
  // Chrome (the browser) and chrome (the UI) are unrelated words that collided in this
  // file. Scope the audit's --exclude through, or a bold brand-hue rail is counted as a
  // working-surface contrast failure and the score means nothing.
  const excl = flag('exclude', null); if (excl) args.push('--exclude', excl);
  try { execFileSync('node', args, { stdio: 'pipe' }); }
  catch (e) { if (e.status === 2) { console.error(e.stderr?.toString() || e.message); process.exit(2); } }
  if (!existsSync(out)) { console.error(`could not audit ${src}`); process.exit(2); }
  return { name: path.basename(src).replace(/\.html$/, ''), report: JSON.parse(readFileSync(out, 'utf8')) };
});

/* ------------------------------------------------------------------ scoring */

function score(r) {
  const c = r.contrast, w = r.whitespace, f = r.focus, a = r.accents, t = r.type, h = r.hitTargets, cl = r.clipping, L = r.length, pa = r.palette || { score: 100, flags: [], competingHues: 0, rampSteps: 0 };
  const notes = [];
  const add = (s) => notes.push(s);

  /* ---- gates: hard failures that cap the grade ---- */
  const gates = [];
  if (c.floorCount > 0) gates.push(`${c.floorCount} text pairing(s) below WCAG AA`);
  if (c.halationCount > 0) gates.push(`${c.halationCount} saturated colour(s) on a near-black reading surface (halation)`);
  if (cl.count > 0 || cl.horizontalPageOverflow) gates.push('content clipped or page overflows horizontally');
  const caps = [];
  if (c.ceilingCount > 0) caps.push(`${c.ceilingCount} sustained-text pairing(s) above the comfort ceiling`);
  // Proportional, not absolute: two 15px checkboxes are a real defect but should not
  // gate a page out of the top band the way a contrast failure must. Only a systemic
  // target problem — many, or a high share of all controls — earns a cap.
  const targetShare = h.measured ? h.aaCount / h.measured : 0;
  // The share test needs a floor on the count too, or a 13-control page with two tiny
  // checkboxes trips a percentage threshold on a denominator of thirteen.
  if (h.aaCount > 5 || (h.aaCount > 3 && targetShare > 0.25)) caps.push(`${h.aaCount} control(s) (${Math.round(targetShare * 100)}% of controls) under the 24px target minimum`);
  if (L.flags.length > 0) caps.push(...L.flags);
  // Rainbow is a cap, not a gate: it costs readability, it does not make text illegible.
  if (pa.flags.length) caps.push(...pa.flags);

  /* ---- 1. legibility (0.22): can it be read at all ---- */
  let leg = 100;
  if (c.floorCount) { leg -= Math.min(60, c.floorCount * 22); add(`-${Math.min(60, c.floorCount * 22)} · ${c.floorCount} below AA`); }
  if (c.medianRatio != null) {
    if (c.medianRatio < 4.5) { leg -= 25; add('-25 · median contrast ' + c.medianRatio + ':1 is thin'); }
    else if (c.medianRatio > 15) { leg -= 10; add('-10 · median ' + c.medianRatio + ':1 past the useful range'); }
    else leg += 0;
  }
  if (t.min != null && t.min < 11) { leg -= (11 - t.min) * 6; add(`-${r1((11 - t.min) * 6)} · smallest text ${t.min}px`); }
  if (t.median != null && t.median < 13) { leg -= (13 - t.median) * 5; add(`-${r1((13 - t.median) * 5)} · median text ${t.median}px`); }
  const legibility = clamp(leg);

  /* ---- 2. visual comfort (0.24): can it be read for half an hour ---- */
  let com = 100;
  if (c.ceilingCount) { const d = Math.min(55, c.ceilingCount * 7); com -= d; add(`-${d} · ${c.ceilingCount} above the contrast ceiling`); }
  if (c.halationCount) { const d = Math.min(45, c.halationCount * 9); com -= d; add(`-${d} · ${c.halationCount} halation source(s)`); }
  // ink coverage: how much of the viewport is content. Airiness, measured.
  const inkScore = w.inkRatio <= 20 ? 100 : w.inkRatio <= 35 ? 100 - (w.inkRatio - 20) * 1.4
    : w.inkRatio <= 50 ? 79 - (w.inkRatio - 35) * 1.6 : Math.max(20, 55 - (w.inkRatio - 50) * 1.2);
  com = com * 0.55 + inkScore * 0.45;
  add(`ink ${w.inkRatio}% → ${Math.round(inkScore)}`);
  if (w.medianGapPx != null && w.medianGapPx > 0) { add(`block rhythm ${w.medianGapPx}px`); com = clamp(com + 4); }
  const accScore = a.coveragePct <= 8 ? 100 : Math.max(55, 100 - (a.coveragePct - 8) * 1.8);
  com = com * 0.85 + accScore * 0.15;
  add(`accent load ${a.coveragePct}% → ${Math.round(accScore)}`);
  const comfort = clamp(com);

  /* ---- 3. hierarchy (0.20): does the eye know where to start ---- */
  let hi = 100;
  const signScore = L.headingsPerScreen >= 4 ? 100 : L.headingsPerScreen >= 2.5 ? 60 + (L.headingsPerScreen - 2.5) * 26 : Math.max(20, L.headingsPerScreen * 24);
  hi = hi * 0.5 + signScore * 0.5; add(`signposts ${L.headingsPerScreen}/screen → ${Math.round(signScore)}`);
  // Spread is the weakest signal in the set: a large display numeral inflates it, a calm
  // page of equal cards deflates it. Capped contribution on purpose.
  const spreadScore = f.hierarchySpread >= 3 ? 100 : f.hierarchySpread >= 2 ? 85 : f.hierarchySpread >= 1.5 ? 70 : 58;
  hi = hi * 0.8 + spreadScore * 0.2; add(`focus spread ${f.hierarchySpread}x → ${spreadScore} (low-confidence term)`);
  const stepScore = t.distinctSteps >= 4 && t.distinctSteps <= 12 ? 100 : t.distinctSteps > 12 ? 82 : 65;
  hi = hi * 0.85 + stepScore * 0.15; add(`${t.distinctSteps} type steps → ${stepScore}`);
  const hierarchy = clamp(hi);

  /* ---- 4. length & navigation (0.24): is it a page or a scroll ---- */
  const eff = L.lengthIsData ? L.screens * 0.55 : L.screens;   // a paginated table earns slack
  let ln;
  if (eff <= 1.4) ln = 100;
  else if (eff <= 2.2) ln = 100 - (eff - 1.4) * 22;
  else if (eff <= 3.2) ln = 82 - (eff - 2.2) * 30;
  else ln = Math.max(15, 52 - (eff - 3.2) * 22);
  add(`${L.screens} screens${L.lengthIsData ? ' (table-driven, counted as ' + r1(eff) + ')' : ''} → ${Math.round(ln)}`);
  const wallScore = L.longestWallScreens <= 0.5 ? 100 : L.longestWallScreens <= 1 ? 100 - (L.longestWallScreens - 0.5) * 60
    : L.longestWallScreens <= 1.6 ? 70 - (L.longestWallScreens - 1) * 50 : Math.max(10, 40 - (L.longestWallScreens - 1.6) * 30);
  ln = ln * 0.55 + wallScore * 0.45; add(`longest unbroken run ${L.longestWallScreens} screens → ${Math.round(wallScore)}`);
  let nav = L.stickyNav ? 100 : 62; if (L.screens > 3 && !L.stickyNav) nav = 35;
  ln = ln * 0.8 + nav * 0.2; add(L.stickyNav ? 'sticky orientation present' : 'no sticky orientation');
  const actScore = L.screensToLastAction <= 1.5 ? 100 : Math.max(45, 100 - (L.screensToLastAction - 1.5) * 25);
  ln = ln * 0.9 + actScore * 0.1; add(`last control at ${L.screensToLastAction} screens → ${Math.round(actScore)}`);
  if (L.flags.length) { ln = clamp(ln - L.flags.length * 10); add(`-${L.flags.length * 10} · ${L.flags.length} length flag(s)`); }
  const length = clamp(ln);

  /* ---- 5. robustness (0.10) ---- */
  let ro = 100;
  if (cl.count) { ro -= Math.min(40, cl.count * 12); add(`-${Math.min(40, cl.count * 12)} · ${cl.count} clipped`); }
  if (cl.horizontalPageOverflow) { ro -= 25; add('-25 · horizontal page overflow'); }
  if (h.aaCount) { const d = Math.min(45, h.aaCount * 5); ro -= d; add(`-${d} · ${h.aaCount} control(s) <24px`); }
  if (h.comfortCount) { const d = Math.min(15, h.comfortCount * 0.4); ro -= d; add(`-${r1(d)} · ${h.comfortCount} control(s) <44px (advisory)`); }
  const robustness = clamp(ro);

  /* ---- 6. palette coherence (0.13): shades good, dispersion bad ---- */
  // Deliberately NOT a count-of-colours penalty. A deep tonal ramp of many shades at
  // one temperature scores well; five unrelated saturated hues competing for
  // attention scores badly, however few of them there are.
  const palette = clamp(pa.score);
  add(`${pa.competingHues} competing hue families, ${pa.rampSteps} ramp shades -> ${Math.round(palette)}`);

  const dims = { legibility, comfort, hierarchy, length, palette, robustness };
  const WEIGHTS = { legibility: 0.20, comfort: 0.20, hierarchy: 0.17, length: 0.20, palette: 0.13, robustness: 0.10 };
  let composite = Object.entries(dims).reduce((s, [k, v]) => s + v * WEIGHTS[k], 0);

  /* ---- gates dominate the composite ---- */
  let grade;
  const band = (v) => (v >= 90 ? 'Excellent' : v >= 78 ? 'Good' : v >= 65 ? 'Acceptable' : v >= 50 ? 'Poor' : 'Fail');
  const rank = ['Fail', 'Poor', 'Acceptable', 'Good', 'Excellent'];
  grade = band(composite);
  let capped = false;
  if (gates.length) {
    // A hard legibility/robustness failure cannot be averaged away.
    composite = Math.min(composite, 62);
    grade = 'Acceptable'; capped = true;
  }
  if (caps.length) {
    composite = Math.min(composite, 84);
    if (rank.indexOf(grade) > rank.indexOf('Good')) { grade = 'Good'; capped = true; }
  }
  if (gates.length) grade = rank[Math.min(rank.indexOf(grade), rank.indexOf('Acceptable') - (c.floorCount > 0 || c.halationCount > 0 ? 1 : 0))];

  return { composite: r1(composite), grade, dims, notes, gates, caps, capped, raw: r };
}

/* -------------------------------------------------------------------- print */

const WEIGHTS = { legibility: 'Legibility 20%', comfort: 'Comfort     20%', hierarchy: 'Hierarchy   17%', length: 'Length      20%', palette: 'Palette     13%', robustness: 'Robustness  10%' };
const scored = reports.map((x) => ({ ...x, ...score(x.report) })).sort((a, b) => b.composite - a.composite);

if (asJson) { console.log(JSON.stringify(scored.map(({ raw, ...s }) => s), null, 2)); process.exit(0); }

const W = 26;
console.log(`\n\x1b[1m  ranked\x1b[0m${' '.repeat(W - 8)}${Object.values(WEIGHTS).map((w) => w.split(' ')[0].padStart(11)).join('')}   score  grade`);
console.log('  ' + '─'.repeat(W + 77));
for (const s of scored) {
  const bar = (v) => (v >= 90 ? '\x1b[32m' : v >= 70 ? '\x1b[33m' : '\x1b[31m') + String(Math.round(v)).padStart(11) + '\x1b[0m';
  const g = s.grade === 'Excellent' ? '\x1b[32m' : s.grade === 'Good' ? '\x1b[36m' : s.grade === 'Acceptable' ? '\x1b[33m' : '\x1b[31m';
  console.log(`  ${s.name.padEnd(W)}${Object.keys(WEIGHTS).map((k) => bar(s.dims[k])).join('')}   ${String(s.composite).padStart(5)}  ${g}${s.grade}${s.capped ? ' (capped)' : ''}\x1b[0m`);
}

for (const s of scored) {
  console.log(`\n\x1b[1m  ${s.name}\x1b[0m — ${s.composite}/100 · ${s.grade}`);
  if (s.gates.length) console.log('    \x1b[31mGATE\x1b[0m  ' + s.gates.join('\n          '));
  if (s.caps.length) console.log('    \x1b[33mcap\x1b[0m   ' + s.caps.join('\n          '));
  console.log('    ' + s.notes.filter(Boolean).join('\n    '));
}

console.log(`
\x1b[1m  CAVEATS\x1b[0m
    · Weights are calibrated against three human judgements on one admin panel, not a
      broad corpus. Treat relative ranking between pages as the useful output; treat an
      absolute "74 vs 78" as noise.
    · "Focus spread" is the least trustworthy term — a big display numeral inflates it and
      a calm page of equal-weight cards deflates it. It is capped at 10% of one dimension.
    · Ink ratio measures the first viewport only, so a page that is airy at the top and
      jammed at the bottom will over-score on comfort.
    · A score can never settle name/content mismatch, whether the copy is any good, or
      whether the direction fits the brand. Those still need a person looking at it.
`);
