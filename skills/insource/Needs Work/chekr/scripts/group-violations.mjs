#!/usr/bin/env bun
/**
 * Parse violations.json and group by file / rule.
 *
 * Usage:
 *   bun .cursor/skills/chekr/scripts/group-violations.mjs
 *   bun .cursor/skills/chekr/scripts/group-violations.mjs --rule check_functions_duplication --prefix apps/web
 *   bun .cursor/skills/chekr/scripts/group-violations.mjs --report scratch/web-violations.json
 */
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const args = process.argv.slice(2);
function arg(name, fallback) {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
}

const reportPath = resolve(arg('--report', 'violations.json'));
const ruleFilter = arg('--rule', null);
const prefixFilter = arg('--prefix', null);

const data = JSON.parse(readFileSync(reportPath, 'utf8'));
const violations = data.violations ?? [];

const filtered = violations.filter((v) => {
  const rule = v.rule ?? v.check ?? '';
  if (ruleFilter && rule !== ruleFilter) return false;
  if (!prefixFilter) return true;
  const files = (v.locations ?? []).map((l) => l.file).filter(Boolean);
  const extra = v.files ?? [];
  return [...files, ...extra].some((f) => f.startsWith(prefixFilter));
});

const byRule = new Map();
const byFile = new Map();
const pairs = [];

for (const v of filtered) {
  const rule = v.rule ?? v.check ?? 'unknown';
  byRule.set(rule, (byRule.get(rule) ?? 0) + 1);

  const locs = v.locations ?? [];
  for (const l of locs) {
    if (!l.file) continue;
    if (prefixFilter && !l.file.startsWith(prefixFilter)) continue;
    byFile.set(l.file, (byFile.get(l.file) ?? 0) + 1);
  }

  if (locs.length >= 2) {
    const files = [...new Set(locs.map((l) => l.file).filter(Boolean))].sort();
    if (files.length >= 2) {
      pairs.push({ rule, files, message: (v.message ?? '').split('\n')[0] });
    }
  }
}

console.log(`Report: ${reportPath}`);
console.log(`passed: ${data.passed}`);
console.log(`filtered violations: ${filtered.length}`);
console.log('\nBy rule:');
for (const [r, c] of [...byRule.entries()].sort((a, b) => b[1] - a[1])) {
  console.log(`  ${c}\t${r}`);
}

console.log('\nBy file (top 30):');
for (const [f, c] of [...byFile.entries()].sort((a, b) => b[1] - a[1]).slice(0, 30)) {
  console.log(`  ${c}\t${f}`);
}

if (pairs.length) {
  console.log('\nDuplicate pairs (sample 20):');
  for (const p of pairs.slice(0, 20)) {
    console.log(`  [${p.rule}] ${p.files.join(' <-> ')}`);
    if (p.message) console.log(`    ${p.message}`);
  }
}
