#!/usr/bin/env node
/**
 * guards.mjs — duplication guards for prototype projects (the `prototype` skill).
 *
 * Usage:
 *   node scripts/guards.mjs <dupes|tokens|svg|onclick|all> <project-dir> [options]
 *
 * Options:
 *   --strict        exit 1 when any finding is reported (default: report-only, exit 0)
 *   --min-len N     class-string length considered a "pattern" (default 25)
 *   --top N         findings shown per check before "... and K more" (default 15)
 *   --selftest      run built-in fixtures and exit
 *
 * Findings are the `references/zero-duplication.md` rule expressed mechanically: any
 * visual pattern used twice must exist in exactly one place. Default mode reports the
 * baseline so a migration can drive numbers down; flip to --strict once clean.
 *
 * Zero dependencies; ESM; Node 18+. Output and exit codes follow the house style of
 * stories_check.mjs: 0 clean (or reporting), 1 findings under --strict, 2 usage error.
 *
 * Run status: --selftest passes; verified against assets/starter/ (see skill notes).
 */

import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative, sep, basename } from 'node:path';

const EXTS = new Set(['.html', '.htm', '.js', '.mjs', '.cjs', '.jsx', '.ts', '.css']);
const SKIP_DIRS = new Set(['node_modules', 'vendor', '.git', 'dist', 'build', 'coverage', '.next', '.cache', '__snapshots__']);
// files that legitimately DEFINE hexes and literals:
const TOKEN_FILE = /(^|[\\/])(theme|tokens|tailwind_config|_?variables?)[^\\/]*\.(css|js|mjs|cjs|ts)$/i;
const IS_TEST = /\.(test|spec)\.[cm]?[jt]sx?$/i;

/* ---------------------------------------------------------------- collectors */

export function collectFiles(root) {
  const out = [];
  const walk = (dir) => {
    for (const ent of readdirSync(dir, { withFileTypes: true })) {
      const p = join(dir, ent.name);
      if (ent.isDirectory()) { if (!SKIP_DIRS.has(ent.name)) walk(p); continue; }
      const dot = ent.name.lastIndexOf('.');
      if (dot < 0 || !EXTS.has(ent.name.slice(dot).toLowerCase())) continue;
      if (IS_TEST.test(ent.name)) continue;
      let text;
      try { text = readFileSync(p, 'utf8'); } catch { continue; }
      out.push({ file: p, rel: relative(root, p).split(sep).join('/'), text });
    }
  };
  walk(root);
  return out;
}

const norm = (s) => s.trim().replace(/\s+/g, ' ');
const clip = (s, n = 64) => (s.length > n ? s.slice(0, n - 1) + '…' : s);
const escRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

/* ------------------------------------------------------------------- checks */

/** Repeated class strings: same styling pasted N times = N edits. */
export function checkDupes(files, { minLen = 25 } = {}) {
  const found = [];
  const hits = new Map(); // normalized class string -> { total, files: Map<rel,count>, sample }
  const RE = /\bclass(?:Name)?\s*=\s*(["'])([^"'\n]{10,})\1/g;
  for (const { rel, text } of files) {
    let m;
    while ((m = RE.exec(text))) {
      const cls = norm(m[2]);
      if (cls.length < minLen) continue;
      if (!hits.has(cls)) hits.set(cls, { total: 0, files: new Map(), sample: rel });
      const h = hits.get(cls);
      h.total++;
      h.files.set(rel, (h.files.get(rel) || 0) + 1);
    }
  }
  for (const [cls, h] of [...hits].sort((a, b) => b[1].total - a[1].total)) {
    if (h.files.size < 2 && h.total < 3) continue;
    const where = [...h.files.keys()].slice(0, 4).join(', ') + (h.files.size > 4 ? ` +${h.files.size - 4} more` : '');
    found.push({
      category: 'duped-class-string',
      message: `${h.total} uses in ${h.files.size} file(s): "${clip(cls)}" (${where}) — extract one component class (zero-duplication: layer 2) or a ui.js builder, then retrofit every copy`,
    });
  }
  return found;
}

/** Hex colors and arbitrary values outside token files: the leak that bypasses the scale. */
export function checkTokens(files) {
  const found = [];
  const hex = new Map();     // color -> { total, files:Set }
  const arb = new Map();     // utility-[value] -> { total, files:Set }
  const HEX = /#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})\b/g;
  const ARB = /\b(?:[a-z-]+:)*[a-z]+(?:-\[[^\]\s'"]+\])+/g;
  for (const { rel, text } of files) {
    if (TOKEN_FILE.test(rel)) continue;
    let m;
    HEX.lastIndex = 0;
    while ((m = HEX.exec(text))) {
      const key = m[0].toLowerCase();
      if (!hex.has(key)) hex.set(key, { total: 0, files: new Set() });
      hex.get(key).total++; hex.get(key).files.add(rel);
    }
    ARB.lastIndex = 0;
    while ((m = ARB.exec(text))) {
      const key = m[0];
      if (!arb.has(key)) arb.set(key, { total: 0, files: new Set() });
      arb.get(key).total++; arb.get(key).files.add(rel);
    }
  }
  for (const [color, h] of [...hex].sort((a, b) => b[1].total - a[1].total)) {
    if (h.total < 2 && h.files.size < 2) continue;
    found.push({
      category: 'hex-outside-tokens',
      message: `${color} used ${h.total}× across ${h.files.size} file(s) — define a token in theme.css + tailwind config and reference it; a theme in use must be covered by the token set`,
    });
  }
  for (const [u, h] of [...arb].sort((a, b) => b[1].total - a[1].total)) {
    if (h.total < 3) continue;
    found.push({
      category: 'repeated-arbitrary-value',
      message: `"${clip(u, 40)}" used ${h.total}× — recurring values are tokens (scale steps) or components (visual patterns); decide which, move it`,
    });
  }
  return found;
}

/** Inline <svg> while a glyph/icon helper exists in the project. */
export function checkSvg(files) {
  const found = [];
  const hasIconHelper = files.some(({ rel, text }) =>
    !rel.endsWith('.css') && (/function\s+icon\s*\(/.test(text) || /\bicon\s*=\s*(?:function\b|\([^)]*\)\s*=>|(\w+\s*=>))/.test(text) || /\bexport\s+(const|function)\s+(icon|Icon)\b/.test(text)));
  if (!hasIconHelper) return found;
  for (const { rel, text } of files) {
    if (rel.endsWith('.css')) continue;
    if (/glyphs?|icons?\.js$/i.test(rel)) continue; // the map itself
    const n = (text.match(/<svg\b/gi) || []).length;
    if (n > 0) found.push({ category: 'inline-svg', message: `${n} inline <svg> in ${rel} — call the existing icon()/glyph helper instead` });
  }
  return found;
}

/** Inline handlers, with navigation ones called out as data-go candidates. */
export function checkOnclick(files) {
  const found = [];
  const RE = /\bon(click|change|input|submit|keydown)\s*=\s*(["'`])([\s\S]{0,200}?)\2/g;
  let total = 0, nav = 0; const examples = [];
  for (const { rel, text } of files) {
    let m;
    RE.lastIndex = 0;
    while ((m = RE.exec(text))) {
      total++;
      const body = m[3];
      const isNav = /location\.(href|search|assign|replace)|\.click\(|history\.|go\(/.test(body);
      if (isNav) nav++;
      if (examples.length < 5) examples.push(`${rel}: on${m[1]}=${clip(body, 48)}`);
    }
  }
  if (total > 0) {
    found.push({
      category: 'inline-handler',
      message: `${total} inline handler(s) (${nav} navigation) — bind one delegated data-go/data-toast owner in definePage/ui.js; zero-duplication: behaviour layer`,
    });
    for (const e of examples) found.push({ category: 'inline-handler-site', message: e });
  }
  return found;
}

const CHECKS = { dupes: checkDupes, tokens: checkTokens, svg: checkSvg, onclick: checkOnclick };

/* -------------------------------------------------------------------- report */

function report(name, findings, top) {
  console.log(`${name}: ${findings.length} finding(s)`);
  for (const f of findings.slice(0, top)) console.log(`  - ${f.category}: ${f.message}`);
  if (findings.length > top) console.log(`  ... and ${findings.length - top} more`);
  return findings;
}

/* ------------------------------------------------------------------ selftest */

function selftest() {
  const F = (rel, text) => ({ file: rel, rel, text });
  const cases = [
    ['dupes: repeated class string flagged', () => {
      const files = [
        F('a.js', 'x = `<div class="flex items-center gap-3 rounded-xl border p-4 shadow-sm">`'),
        F('b.js', 'x = `<div class="flex items-center gap-3 rounded-xl border p-4 shadow-sm">`'),
      ];
      return checkDupes(files).some((f) => f.category === 'duped-class-string');
    }],
    ['dupes: single short class not flagged', () => {
      const files = [F('a.js', 'x = `<div class="btn">`'), F('b.js', 'x = `<p class="btn">`')];
      return checkDupes(files).length === 0;
    }],
    ['tokens: hex outside token files flagged', () => {
      const files = [F('a.js', 'color:#008f5d'), F('b.js', 'x="#008f5d"')];
      return checkTokens(files).some((f) => f.category === 'hex-outside-tokens');
    }],
    ['tokens: theme.css exempt', () => {
      const files = [F('css/theme.css', '--brand: #008f5d; --brand2: #008f5d;')];
      return checkTokens(files).length === 0;
    }],
    ['tokens: repeated arbitrary value flagged', () => {
      const files = [F('a.js', 'class="text-[11px]"'), F('b.js', 'class="text-[11px]"'), F('c.js', 'class="text-[11px]"')];
      return checkTokens(files).some((f) => f.category === 'repeated-arbitrary-value');
    }],
    ['svg: only flagged when a helper exists', () => {
      const inline = [F('p.js', 'h = `<svg viewBox="0 0 1 1"></svg>`')];
      if (checkSvg(inline).length !== 0) return false;
      const withHelper = [...inline, F('glyphs.js', 'export function icon(n){return `<svg>${n}</svg>`}')];
      return checkSvg(withHelper).some((f) => f.category === 'inline-svg') &&
             !checkSvg(withHelper).some((f) => f.message.includes('glyphs.js')); // the map file itself stays clean
    }],
    ['onclick: navigation handler counted', () => {
      const files = [F('a.js', 'x = `<a onclick="location.search=\'?filled=1\'">go</a>`')];
      const r = checkOnclick(files);
      return r.some((f) => f.category === 'inline-handler' && /\(1 navigation\)/.test(f.message));
    }],
    ['clean project produces no findings', () => {
      const files = [F('theme.css', ':root { --a: #fff; }'), F('a.js', 'const x = 1;')];
      return [...checkDupes(files), ...checkTokens(files), ...checkSvg(files), ...checkOnclick(files)].length === 0;
    }],
  ];
  let fails = 0;
  for (const [name, fn] of cases) {
    let ok = false;
    try { ok = fn(); } catch { ok = false; }
    console.log(`  ${ok ? 'pass' : 'FAIL'}: ${name}`);
    if (!ok) fails++;
  }
  console.log(`selftest: ${cases.length - fails}/${cases.length} passed`);
  process.exit(fails ? 1 : 0);
}

/* ---------------------------------------------------------------------- main */

function main(argv) {
  const args = argv.slice(2);
  if (args.includes('--selftest')) selftest();
  const flags = new Set(args.filter((a) => a.startsWith('--') && !a.includes('=')));
  const opt = (name, dflt) => {
    const hit = args.find((a) => a.startsWith(`--${name}=`));
    return hit ? Number(hit.split('=')[1]) : dflt;
  };
  const positional = args.filter((a) => !a.startsWith('--'));
  const [cmd, dir] = positional;
  if (!cmd || !dir || !(cmd in CHECKS || cmd === 'all')) {
    console.error('usage: node guards.mjs <dupes|tokens|svg|onclick|all> <project-dir> [--strict] [--min-len N] [--top N] | --selftest');
    process.exit(2);
  }
  let st;
  try { st = statSync(dir); } catch { console.error(`cannot read directory: ${dir}`); process.exit(2); }
  if (!st.isDirectory()) { console.error(`not a directory: ${dir}`); process.exit(2); }

  const files = collectFiles(dir);
  const names = cmd === 'all' ? Object.keys(CHECKS) : [cmd];
  let findings = 0;
  for (const name of names) {
    const f = name === 'dupes' ? CHECKS[name](files, { minLen: opt('min-len', 25) }) : CHECKS[name](files);
    findings += report(`${name} (${basename(dir)})`, f, opt('top', 15)).length;
  }
  console.log(`guards: ${files.length} file(s) scanned, ${findings} finding(s) total${flags.has('--strict') && findings ? ' (--strict)' : ''}`);
  process.exit(flags.has('--strict') && findings > 0 ? 1 : 0);
}

main(process.argv);