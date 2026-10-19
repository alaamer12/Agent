#!/usr/bin/env node
/**
 * ledger.mjs — the record of who checked which page, and whether they actually looked.
 *
 * A mechanical diff proves the behaviour surface survived. It cannot prove the page still
 * answers the same questions — a column can persist with its data gone, a filter can move
 * somewhere unreachable. That needs a reader, and a reader needs to leave a record.
 *
 *   node ledger.mjs record --batch wave1 --reviewer agent-A \
 *        --file src/pages/currency.vue --status pass \
 *        --note "6 columns, search, create dialog, both row actions present"
 *
 *   node ledger.mjs audit            # is this ledger evidence, or is it theatre?
 *   node ledger.mjs summary          # coverage per page
 *   node ledger.mjs failures         # every non-pass, newest first
 *
 * Each reviewer writes its own file under the ledger directory. One shared file is a trap:
 * parallel appenders lose lines, which is the same failure mode as parallel edits to a token
 * layer.
 *
 * `audit` exists because a real rollout produced 81 review records and 34 of them were
 * copy-pasted — one reviewer emitted the identical sentence for eight unrelated files. A
 * verdict that could have been written without opening the file is not evidence, and a
 * ledger full of them is worse than no ledger because it looks like coverage.
 */
import { appendFileSync, mkdirSync, readFileSync, readdirSync, existsSync } from 'node:fs';
import path from 'node:path';

const argv = process.argv.slice(2);
const flag = (n, d) => { const i = argv.indexOf(`--${n}`); return i === -1 ? d : argv[i + 1]; };
const all = (n) => argv.reduce((a, v, i) => (v === `--${n}` && argv[i + 1] ? [...a, argv[i + 1]] : a), []);
const DIR = path.resolve(flag('dir', 'design/verification'));
const cmd = argv[0];

const filesIn = () => (existsSync(DIR) ? readdirSync(DIR) : [])
  .filter((f) => f.endsWith('.jsonl'))
  .flatMap((f) => readFileSync(path.join(DIR, f), 'utf8').split('\n').filter(Boolean).map((l) => {
    try { return { ...JSON.parse(l), _shard: f }; } catch { return null; }
  }).filter(Boolean));

if (cmd === 'record') {
  const reviewer = flag('reviewer', null);
  const batch = flag('batch', null);
  const status = flag('status', null);
  const note = flag('note', '');
  const files = all('file');
  if (!reviewer || !batch || !status || !files.length) {
    console.error('usage: ledger.mjs record --batch B1 --reviewer name --file <path> [--file <path>...] --status pass|fail|blocked --note "what you actually saw"');
    process.exit(2);
  }
  if (!['pass', 'fail', 'blocked'].includes(status)) { console.error('status must be pass | fail | blocked'); process.exit(2); }
  if (status === 'pass' && note.trim().split(/\s+/).length < 6) {
    console.error(`\x1b[31mrefusing a pass with a ${note.trim().split(/\s+/).length}-word note\x1b[0m
  A verdict that fits in a shrug is not evidence. Name what you checked against: the columns,
  the controls, the values, the thing that could have gone missing and did not.`);
    process.exit(3);
  }
  mkdirSync(DIR, { recursive: true });
  const shard = path.join(DIR, `${batch.replace(/[^\w.-]/g, '_')}.jsonl`);
  for (const f of files) {
    appendFileSync(shard, JSON.stringify({ file: f, status, reviewer, batch, at: new Date().toISOString(), note }) + '\n');
  }
  console.log(`recorded ${status} for ${files.length} file(s) -> ${path.relative(process.cwd(), shard)}`);
  process.exit(0);
}

const records = filesIn();
if (!records.length) {
  console.log(`no records under ${DIR}\n  Reviewers add them with: ledger.mjs record --batch ... --reviewer ... --file ... --status pass --note ...`);
  process.exit(0);
}

if (cmd === 'summary') {
  const byFile = new Map();
  for (const r of records) byFile.set(r.file, [...(byFile.get(r.file) || []), r]);
  const pass = [...byFile].filter(([, v]) => v.some((r) => r.status === 'pass'));
  const bad = [...byFile].filter(([, v]) => v.some((r) => r.status !== 'pass'));
  console.log(`${byFile.size} files with a verdict · ${pass.length} pass · ${bad.length} not passing`);
  bad.forEach(([f, v]) => console.log(`  ${v[v.length - 1].status.toUpperCase().padEnd(7)} ${f}`));
  process.exit(bad.length ? 1 : 0);
}

if (cmd === 'failures') {
  records.filter((r) => r.status !== 'pass').sort((a, b) => b.at.localeCompare(a.at))
    .forEach((r) => console.log(`${r.at}  ${r.status}  ${r.file}\n    ${r.note}`));
  process.exit(0);
}

/* ── audit: is the ledger trustworthy? ──────────────────────────────────────────────── */
const problems = [];

// 1. Verdicts that were copied.
const byNote = new Map();
for (const r of records) {
  const key = r.note.replace(/\s+/g, ' ').trim().toLowerCase();
  if (key.length < 30) continue;
  byNote.set(key, [...(byNote.get(key) || []), r]);
}
const reused = [...byNote].filter(([, v]) => new Set(v.map((r) => r.file)).size > 1);
if (reused.length) {
  problems.push(`${reused.reduce((n, [, v]) => n + v.length, 0)} of ${records.length} records share a note with a record about a different file (${reused.length} distinct sentences doing ${reused.reduce((n, [, v]) => n + v.length, 0)} jobs). A review that reads identically for several unrelated pages did not look at most of them.`);
  reused.sort((a, b) => b[1].length - a[1].length).slice(0, 5).forEach(([, v]) =>
    problems.push(`   x${new Set(v.map((r) => r.file)).size}: "${v[0].note.slice(0, 90)}…" — ${[...new Set(v.map((r) => r.file))].slice(0, 4).join(', ')}${new Set(v.map((r) => r.file)).size > 4 ? ', …' : ''}`));
}

// 2. Thin passes.
const thin = records.filter((r) => r.status === 'pass' && r.note.trim().split(/\s+/).length < 12);
if (thin.length) problems.push(`${thin.length} passing records have a note under twelve words — too short to name what was checked:\n   ${thin.slice(0, 5).map((r) => r.file).join('\n   ')}`);

// 3. Coverage holes.
const verdicts = new Set(records.map((r) => r.file));
const latest = new Map();
for (const r of records) latest.set(r.file, r);
const unresolved = [...latest].filter(([, r]) => r.status !== 'pass');
if (unresolved.length) problems.push(`${unresolved.length} files' most recent verdict is not a pass:\n   ${unresolved.slice(0, 8).map(([f, r]) => `${r.status}  ${f}`).join('\n   ')}`);

// 4. Shard collisions — two reviewers claiming the same batch id.
const batchReviewers = new Map();
for (const r of records) batchReviewers.set(r.batch, new Set([...(batchReviewers.get(r.batch) || []), r.reviewer]));
const crowded = [...batchReviewers].filter(([, s]) => s.size > 1);
if (crowded.length) problems.push(`batch ids shared by multiple reviewers (${crowded.map(([b, s]) => `${b}: ${[...s].join('/')}`).join('; ')}) — records are attributed, but a batch is supposed to be one lane`);

console.log(`ledger: ${records.length} records · ${verdicts.size} files · ${new Set(records.map((r) => r.batch)).size} batches\n`);
if (!problems.length) {
  console.log('\x1b[32m✓ every record is distinct, every file resolves to a pass, and no note is too thin to check\x1b[0m');
  process.exit(0);
}
console.log('\x1b[31mthe ledger is not yet evidence:\x1b[0m');
problems.forEach((p) => console.log('  • ' + p));
process.exit(1);
