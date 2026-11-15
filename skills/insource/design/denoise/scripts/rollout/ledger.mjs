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
 *        --note "6 columns, search, create dialog, both row actions present" \
 *        --cite src/pages/currency.vue:14 --cite src/router/index.ts:469
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
 *
 * Refusing short notes and flagging repeated ones narrowed it but did not close it: a
 * *plausible* sentence about a file is still writable without opening it, and no amount of
 * deduplication catches a well-phrased fabrication. So a `pass` now carries `--cite
 * <path>:<line>` — something you can only type if you had the file open at that line — and
 * `audit` re-reads the window around each citation and asks whether the note and the code
 * share a distinctive word. The line is checked on write (it must exist, and must not be
 * blank or comment-only) and again on audit (the note must actually say something about it).
 * Citations recorded against files that are later deleted or rewritten are reported as
 * uncheckable rather than as passing. Ledgers written before `--cite` still parse: their
 * passes are simply reported as having no citation recorded.
 */
import { appendFileSync, mkdirSync, readFileSync, readdirSync, existsSync } from 'node:fs';
import path from 'node:path';

const argv = process.argv.slice(2);
const flag = (n, d) => { const i = argv.indexOf(`--${n}`); return i === -1 ? d : argv[i + 1]; };
const all = (n) => argv.reduce((a, v, i) => (v === `--${n}` && argv[i + 1] ? [...a, argv[i + 1]] : a), []);
const DIR = path.resolve(flag('dir', 'design/verification'));
/** Where citation paths are resolved from — the app root, when the ledger lives elsewhere. */
const ROOT = path.resolve(flag('root', '.'));
const cmd = argv[0];

/* ── citations: a line of code the note can be checked against ───────────────────────── */

const lineCache = new Map();
const linesOf = (p) => {
  const fp = path.resolve(ROOT, p);
  if (!lineCache.has(fp)) {
    try { lineCache.set(fp, readFileSync(fp, 'utf8').split(/\r?\n/)); } catch { lineCache.set(fp, null); }
  }
  return lineCache.get(fp);
};

/** `src/x.vue:42`, `C:\repo\src\x.vue:42`, `42` alone is not a citation. */
const parseCite = (raw) => {
  const m = /^(.*?):(\d+)$/.exec(String(raw).trim());
  return m && m[1] ? { path: m[1].trim(), line: Number(m[2]) } : null;
};

const HASH_COMMENT_EXT = new Set(['.py', '.sh', '.bash', '.zsh', '.rb', '.yml', '.yaml', '.toml', '.conf', '.ini', '.env', '.tf', '.r']);
/** A line with nothing in it but a comment cannot evidence what the code does. */
const commentOnly = (p, text) => {
  const t = text.trim();
  if (/^(\/\/|\/\*|\*|<!--|-->|--|;;|%)/.test(t)) return true;
  if (t.startsWith('#') && HASH_COMMENT_EXT.has(path.extname(p).toLowerCase())) return true;
  return false;
};

/** Prose filler and language keywords: sharing one of these with the code proves nothing. */
const STOP = new Set(['this', 'that', 'with', 'from', 'have', 'has', 'was', 'were', 'been', 'they',
  'them', 'their', 'there', 'then', 'than', 'when', 'what', 'which', 'while', 'into', 'onto', 'upon',
  'about', 'after', 'before', 'over', 'under', 'again', 'here', 'also', 'only', 'very', 'more', 'most',
  'other', 'same', 'such', 'because', 'through', 'during', 'your', 'you', 'will', 'would', 'should',
  'could', 'does', 'doing', 'each', 'few', 'many', 'much', 'several', 'just', 'like', 'used', 'using',
  'return', 'function', 'const', 'true', 'false', 'null', 'undefined', 'import', 'export', 'default',
  'class', 'style', 'props', 'emits', 'reactive', 'computed', 'template', 'script', 'await', 'async',
  'void', 'string', 'number', 'boolean', 'object', 'array', 'item', 'items', 'value', 'values', 'type',
  'types', 'name', 'names', 'data']);

/**
 * The words a note and a line of code can share. camelCase and snake_case identifiers are
 * split into their parts, since the note says "create dialog" and the code says
 * `openCreateDialog`: exact-string comparison would call that a mismatch and drown the check
 * in false alarms. What survives is a set of real words of four letters or more.
 */
const lex = (s) => {
  const out = new Set();
  for (const t of String(s).replace(/([a-z0-9])([A-Z])/g, '$1 $2').replace(/([A-Z]+)([A-Z][a-z])/g, '$1 $2').split(/[^A-Za-z0-9]+/)) {
    const w = t.toLowerCase();
    if (w.length >= 4 && !STOP.has(w)) out.add(w);
  }
  return out;
};

/**
 * Does the note say something about the cited window, or merely sit next to a file path?
 * A detailed note should intersect the code in more than one place, because a single shared
 * word is cheap: admin-page vocabulary ("filter", "column", "dialog") matches most admin
 * pages by accident. So five or more checkable words in the note raises the bar to two
 * overlaps, and a short note is only held to one. An overlap is not proof of a careful
 * review — only that the note and the line it names are about the same thing.
 */
function corroborate(note, cite, span = 6) {
  const lines = linesOf(cite.path);
  if (!lines) return { state: 'gone', detail: `${cite.path} is not readable from --root ${ROOT}` };
  if (lines[cite.line - 1] === undefined) return { state: 'gone', detail: `${cite.path} now has ${lines.length} lines` };
  const window = lines.slice(Math.max(0, cite.line - 1 - span), cite.line + span).join(' ');
  const noteWords = lex(note);
  if (!noteWords.size) return { state: 'thin', detail: 'the note has no word of four letters or more that is not filler' };
  const windowWords = lex(window);
  const hits = [...noteWords].filter((w) => windowWords.has(w));
  const need = noteWords.size >= 5 ? 2 : 1;
  if (hits.length < need) {
    return { state: 'unmatched', detail: `the note shares ${hits.length} word${hits.length === 1 ? '' : 's'} with the ${span} lines around ${cite.path}:${cite.line}, which wanted ${need} — that line reads "${lines[cite.line - 1].trim().slice(0, 70)}" and talks about ${[...windowWords].slice(0, 8).join(', ') || 'nothing checkable'}` };
  }
  return { state: 'ok', detail: hits.join(', ') };
}


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
  const citeRaw = all('cite');
  if (!reviewer || !batch || !status || !files.length) {
    console.error('usage: ledger.mjs record --batch B1 --reviewer name --file <path> [--file <path>...] --status pass|fail|blocked --note "what you actually saw" [--cite <path>:<line> ...] [--root <app-root>]');
    process.exit(2);
  }
  if (!['pass', 'fail', 'blocked'].includes(status)) { console.error('status must be pass | fail | blocked'); process.exit(2); }
  if (status === 'pass' && note.trim().split(/\s+/).length < 6) {
    console.error(`\x1b[31mrefusing a pass with a ${note.trim().split(/\s+/).length}-word note\x1b[0m
  A verdict that fits in a shrug is not evidence. Name what you checked against: the columns,
  the controls, the values, the thing that could have gone missing and did not.`);
    process.exit(3);
  }
  const cites = [];
  for (const raw of citeRaw) {
    const c = parseCite(raw);
    if (!c) { console.error(`\x1b[31m--cite "${raw}" is not a citation\x1b[0m\n  The form is <path>:<line>, e.g. --cite src/pages/currency.vue:14`); process.exit(2); }
    const lines = linesOf(c.path);
    if (!lines) { console.error(`\x1b[31m--cite ${raw}: no such file\x1b[0m\n  Nothing at ${path.resolve(ROOT, c.path)}. Citation paths are resolved from --root (currently ${ROOT}); pass the path the way the repo spells it.`); process.exit(3); }
    const text = lines[c.line - 1];
    if (text === undefined) { console.error(`\x1b[31m--cite ${raw}: that line does not exist\x1b[0m\n  ${c.path} has ${lines.length} lines. A citation to a line past the end of the file is a citation to nothing.`); process.exit(3); }
    if (!text.trim()) { console.error(`\x1b[31m--cite ${raw}: that line is blank\x1b[0m\n  Move the citation onto a line with something in it — the column definition, the handler, the label.`); process.exit(3); }
    if (commentOnly(c.path, text)) { console.error(`\x1b[31m--cite ${raw}: that line is only a comment\x1b[0m\n  It reads "${text.trim().slice(0, 70)}". A comment says what someone intended; it does not say the code is there.`); process.exit(3); }
    const check = corroborate(note, c);
    if (status === 'pass' && check.state === 'unmatched') {
      console.error(`\x1b[33mwarning: --cite ${raw} shares no distinctive word with the note\x1b[0m\n  ${check.detail}\n  Recorded anyway; \`audit\` will report it. Either cite the line the note is about, or go and look again.`);
    }
    cites.push({ path: c.path, line: c.line, text: text.trim().slice(0, 200) });
  }
  if (status === 'pass' && !cites.length) {
    console.error(`\x1b[31mrefusing a pass with nothing cited\x1b[0m
  A sentence about a file can be written without opening it — that is exactly what happened to
  the last ledger, where the notes that survived deduplication were still unfalsifiable. Point
  the verdict at a line you had on screen:
      --cite ${files[0]}:<line>
  One citation per file you claim to have read. \`audit\` re-reads the window around it and
  checks that the note and the code share a distinctive word.`);
    process.exit(3);
  }
  if (files.length > 1 && cites.length && cites.length < files.length) {
    console.error(`  \x1b[33mnote\x1b[0m: ${files.length} files, ${cites.length} citation(s) — the same citations are being attached to every file in this record, and \`audit\` flags a citation used as evidence for more than one file. One record per file is the honest shape here.`);
  }
  mkdirSync(DIR, { recursive: true });
  const shard = path.join(DIR, `${batch.replace(/[^\w.-]/g, '_')}.jsonl`);
  for (const f of files) {
    appendFileSync(shard, JSON.stringify({ file: f, status, reviewer, batch, at: new Date().toISOString(), note, cites }) + '\n');
  }
  console.log(`recorded ${status} for ${files.length} file(s)${cites.length ? ` with ${cites.length} citation(s)` : ''} -> ${path.relative(process.cwd(), shard)}`);
  process.exit(0);
}

const records = filesIn();
if (!records.length) {
  console.log(`no records under ${DIR}\n  Reviewers add them with: ledger.mjs record --batch ... --reviewer ... --file ... --status pass --note ... --cite <path>:<line>`);
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
    .forEach((r) => console.log(`${r.at}  ${r.status}  ${r.file}\n    ${r.note}${(r.cites || []).length ? `\n    cites: ${r.cites.map((c) => `${c.path}:${c.line}`).join(', ')}` : ''}`));
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

/* ── 5. the citations: does the note survive being checked against the line it names? ── */
const citesOf = (r) => (Array.isArray(r.cites) ? r.cites : []);
const cited = records.filter((r) => citesOf(r).length);
const uncitedPass = records.filter((r) => r.status === 'pass' && !citesOf(r).length);
const unreadable = []; // cited line no longer there
const thinNotes = [];  // note is all filler, so nothing could match
const unsupported = []; // note and cited window share no distinctive word
for (const r of cited) {
  const results = citesOf(r).map((c) => ({ c, v: corroborate(r.note, c) }));
  results.forEach(({ c, v }) => {
    if (v.state === 'gone') unreadable.push(`${c.path}:${c.line} — ${v.detail}`);
    if (v.state === 'thin') thinNotes.push(`${r.file}: ${v.detail}`);
  });
  const checkable = results.filter(({ v }) => v.state !== 'gone');
  if (checkable.length && !checkable.some(({ v }) => v.state === 'ok')) {
    unsupported.push({ r, first: checkable.find(({ v }) => v.state === 'unmatched') || checkable[0] });
  }
}
if (uncitedPass.length) {
  problems.push(`${uncitedPass.length} of ${records.length} passing records have no citation recorded — nothing about them can be checked against the code, so they are claims rather than evidence.${cited.length ? ' Passes recorded under the new rule carry `--cite <path>:<line>`; these were not, and re-review is the only way to make them checkable.' : ' This ledger predates `--cite`: re-review what you still rely on with a citation, or keep these verdicts labelled as unverified.'}\n   ${uncitedPass.slice(0, 8).map((r) => r.file).join('\n   ')}`);
}
if (unsupported.length) {
  problems.push(`${unsupported.length} of ${cited.length} cited records name a line whose code shares no distinctive word with the note — the verdict and the citation are about different things:\n   ${unsupported.slice(0, 5).map(({ r, first }) => `${r.file} → ${first.c ? `${first.c.path}:${first.c.line}` : '(unreadable)'}\n      note: "${String(r.note).slice(0, 80)}"\n      ${first.v.detail}`).join('\n   ')}`);
}
if (unreadable.length) problems.push(`${unreadable.length} citation(s) cannot be re-checked — the file or the line is gone (it may have moved during the pass, which is worth saying out loud rather than leaving as a stale pointer):\n   ${unreadable.slice(0, 6).join('\n   ')}`);
if (thinNotes.length) problems.push(`${thinNotes.length} record(s) have a note made only of filler words, so no citation could ever corroborate it:\n   ${thinNotes.slice(0, 4).join('\n   ')}`);

// 6. Duplicate citations — a line pasted as evidence for several different files.
const byCite = new Map();
for (const r of cited) for (const c of citesOf(r)) {
  const key = `${c.path}:${c.line}`;
  byCite.set(key, { files: new Set([...(byCite.get(key)?.files || []), r.file]) });
}
const sharedCites = [...byCite].filter(([, v]) => v.files.size > 1);
if (sharedCites.length) {
  problems.push(`${sharedCites.length} citation(s) are offered as evidence for more than one file (${sharedCites.slice(0, 5).map(([k, v]) => `${k} → ${v.files.size} files`).join('; ')}). One line of code cannot show that two different pages still work; a citation copied between records is the same shortcut as a note copied between records.`);
}

const citedPasses = records.filter((r) => r.status === 'pass' && citesOf(r).length).length;
console.log(`ledger: ${records.length} records · ${verdicts.size} files · ${new Set(records.map((r) => r.batch)).size} batches · ${cited.length} records cited (${citedPasses} of them passes)${uncitedPass.length ? `, ${uncitedPass.length} passes with no citation recorded` : ''}\n`);
if (!problems.length) {
  console.log('\x1b[32m✓ every record is distinct, every file resolves to a pass, no note is too thin to check, and every citation says something about the line it points at\x1b[0m');
  process.exit(0);
}
console.log('\x1b[31mthe ledger is not yet evidence:\x1b[0m');
problems.forEach((p) => console.log('  • ' + p));
process.exit(1);
