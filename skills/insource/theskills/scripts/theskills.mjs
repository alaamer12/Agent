#!/usr/bin/env node
/*
 * theskills - pin agent skills as standing (auto-apply) behavior and persist
 * that into the agent's memory context: repo AGENTS.md + the scoped memory dir.
 *
 * Source of truth: <repoRoot>/.theskills/pins.json
 * Baseline sink (never hand-edited): the AGENTS.md managed block in the repo.
 * Secondary sinks, only when the harness has them: <memoryDir>/pinned-skills.md and its
 * MEMORY.md index line; a session-start hook is the user's own wiring, never written here.
 */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const BEGIN = '<!-- BEGIN THE SKILLS (managed by theskills; edit .theskills/pins.json, then run: node scripts/theskills.mjs sync) -->';
const END = '<!-- END THE SKILLS -->';
const MEM_FILE = 'pinned-skills.md';
const INDEX_LINE = `- [Pinned skills](${MEM_FILE}) — standing auto-apply skills; invoke them when the trigger matches, without being asked.`;
const VALUE_FLAGS = new Set(['when', 'note', 'trigger', 'root', 'memory']);
const BUILTIN = new Set([
  'skill-creator', 'agent-creator', 'hook-config', 'mcp-config', 'sdk',
  'security-scan', 'remember', 'loop', 'run', 'verify', 'deep-research',
  'find-skills', 'workflow-authoring',
]);

const today = () => new Date().toISOString().slice(0, 10);
const die = (msg) => { console.log('ERROR: ' + msg); process.exit(1); };

function parseArgs(argv) {
  const pos = [];
  const opts = {};
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    if (!t.startsWith('--')) { pos.push(t); continue; }
    let k = t.slice(2);
    let v;
    const eq = k.indexOf('=');
    if (eq > -1) { v = k.slice(eq + 1); k = k.slice(0, eq); }
    else if (VALUE_FLAGS.has(k) && argv[i + 1] !== undefined && !argv[i + 1].startsWith('--')) v = argv[++i];
    opts[k] = v === undefined ? true : v;
  }
  return { pos, opts };
}

function repoRoot(cwd = process.cwd()) {
  let d = path.resolve(cwd);
  for (;;) {
    if (fs.existsSync(path.join(d, '.theskills')) || fs.existsSync(path.join(d, '.git'))) return d;
    const up = path.dirname(d);
    if (up === d) return path.resolve(cwd);
    d = up;
  }
}

const slugOf = (dir) => path.resolve(dir).replace(/^([A-Za-z]:)?[\\/]/, '').replace(/[\\/:\s]+/g, '-');

/*
 * Layer policy: AGENTS.md is the baseline sink - every harness reads an instruction file, so the
 * block is always written there. Auto-memory (MEMORY.md + an entry file) and hooks are SECONDARY and
 * harness-specific: they are written only when the mechanism actually exists here, or the user points
 * at it with --memory. Absent layers are reported, never invented, and never counted as drift.
 */
function memoryDir(root, override) {
  if (override) return path.resolve(String(override));      // explicit: created on sync
  const proj = path.join(os.homedir(), '.qoder', 'projects', slugOf(root), 'memory');
  return fs.existsSync(proj) ? proj : null;
  // No auto-fallback to the user-global memory dir: that is every other project's context too, and a
  // pin made in one repo has no business landing there. Point --memory at it deliberately instead.
}

const pinsPath = (root) => path.join(root, '.theskills', 'pins.json');
const active = (state) => state.pins.filter((p) => p.status === 'active');

function readPins(root) {
  const p = pinsPath(root);
  if (!fs.existsSync(p)) return null;
  let j;
  try {
    j = JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch (e) {
    die(`pins.json is not valid JSON (${p}): ${e.message}`);
  }
  if (!Array.isArray(j.pins)) die(`pins.json has no "pins" array: ${p}`);
  return { version: j.version || 1, updated: j.updated || null, pins: j.pins };
}

function writePins(root, state) {
  const p = pinsPath(root);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  state.updated = today();
  fs.writeFileSync(p, JSON.stringify(state, null, 2) + '\n');
  return p;
}

function parseFrontmatter(file) {
  const text = fs.readFileSync(file, 'utf8');
  const m = /^---\r?\n([\s\S]*?)\r?\n---/.exec(text);
  const fm = { name: null, description: null };
  if (!m) return fm;
  const lines = m[1].split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const kv = /^(name|description):\s*(.*)$/.exec(lines[i]);
    if (!kv) continue;
    let val = kv[2].trim();
    if (/^[|>][-+]?\d*$/.test(val)) {        // YAML block scalar: fold the indented lines that follow
      const parts = [];
      while (i + 1 < lines.length && /^\s+\S/.test(lines[i + 1])) parts.push(lines[++i].trim());
      val = parts.join(' ');
    }
    fm[kv[1]] = val.replace(/^["']|["']$/g, '');
  }
  return fm;
}

function installedSkills(root) {
  const bases = [
    ['user', path.join(os.homedir(), '.qoder', 'skills')],
    ['user', path.join(os.homedir(), '.agents', 'skills')],
    ['project', path.join(root, '.qoder', 'skills')],
    ['project', path.join(root, '.agents', 'skills')],
  ];
  const found = new Map();
  for (const [scope, base] of bases) {
    let entries;
    try {
      entries = fs.readdirSync(base, { withFileTypes: true });
    } catch { continue; }
    for (const entry of entries) {
      if (!entry.isDirectory() && !entry.isSymbolicLink()) continue;
      const file = path.join(base, entry.name, 'SKILL.md');
      if (!fs.existsSync(file)) continue;
      const fm = parseFrontmatter(file);
      const name = fm.name || entry.name;
      if (!found.has(name)) {
        found.set(name, { name, dir: entry.name, scope, base, description: fm.description || '' });
      }
    }
  }
  return found;
}

function catalogOnly(root, installed) {
  let entries;
  try {
    entries = fs.readdirSync(root, { withFileTypes: true });
  } catch { return []; }
  return entries
    .filter((e) => e.isDirectory() && fs.existsSync(path.join(root, e.name, 'SKILL.md')))
    .map((e) => e.name)
    .filter((n) => !installed.has(n));
}

function resolveSkill(name, root, installed) {
  if (installed.has(name)) return { kind: 'installed', record: installed.get(name) };
  if (BUILTIN.has(name)) return { kind: 'builtin', record: { name, description: '(runtime built-in)' } };
  const dir = path.join(root, name);
  if (fs.existsSync(path.join(dir, 'SKILL.md'))) {
    const fm = parseFrontmatter(path.join(dir, 'SKILL.md'));
    return { kind: 'uninstalled', record: { name: fm.name || name, dir, description: fm.description || '' } };
  }
  return { kind: 'missing', record: { name } };
}

function blockText(state) {
  const act = active(state);
  const paused = state.pins.filter((p) => p.status === 'paused');
  const L = [BEGIN, '', '## Pinned skills (auto-apply)'];
  if (!act.length) {
    L.push('', 'None pinned. `node <theskills>/scripts/theskills.mjs pin <skill> --when "<trigger>"` then `sync`.');
  } else {
    L.push(
      '',
      'Standing behavior in this repo. For each request, check every `when` below BEFORE doing the',
      'work; when one matches, invoke that skill first, without being asked. Announce it in one',
      'clause ("running /name first - this writes code"), then proceed.',
      '',
      '| skill | when to auto-invoke | note |',
      '| --- | --- | --- |',
    );
    for (const p of act) L.push(`| \`${p.skill}\` | ${p.when} | ${p.note || '-'} |`);
    L.push(
      '',
      '- A request matching no `when` gets no pinned skill. Never stretch a trigger to make one fire.',
      '- Overlapping triggers: the more specific `when` wins; an explicit instruction from the user outranks both.',
      '- A pinned skill that cannot be loaded: say so once, continue without it, then run `status`.',
      '- Act on this table; do not restate it in replies.',
    );
  }
  if (paused.length) L.push('', `Paused (not auto-applied): ${paused.map((p) => '`' + p.skill + '`').join(', ')}`);
  L.push('', `Pins: ${act.length} active / ${state.pins.length} total · updated ${state.updated || today()} · source of truth: .theskills/pins.json`, END);
  return L.join('\n');
}

function memoryText(state) {
  const B = [
    '---',
    'name: pinned-skills',
    'description: Skills the user pinned as standing auto-apply behavior in this project - what to invoke without being asked',
    'metadata:',
    '  type: feedback',
    '---',
    '',
    'Invoke the named skill before the work whenever its trigger matches the current request, without waiting to be asked.',
    '',
    '**Why:** the user declared these skills fixed for every interaction; making them re-invoke by hand each turn is the failure mode they asked to remove.',
    '',
    '**How to apply:** read the `when` column as a predicate on the request. Match -> invoke that skill, announce in one clause, then do the task. No match -> normal behavior. Overlapping triggers -> the more specific `when` wins; an explicit user instruction outranks the table. Source of truth is `.theskills/pins.json` at the repo root, mirrored into `AGENTS.md`. If a pinned skill is missing at runtime, report it once and continue. Suspect a stale pin -> run `status`. A renamed skill (folder or frontmatter) means unpin the old name and pin the new one.',
    '',
    '## Pinned skills',
    '',
  ];
  const act = active(state);
  if (!act.length) B.push('_No active pins._');
  else {
    B.push('| skill | when to auto-invoke | note | added |', '| --- | --- | --- | --- |');
    for (const p of act) B.push(`| ${p.skill} | ${p.when} | ${p.note || '-'} | ${p.added} |`);
  }
  return B.join('\n') + '\n';
}

function currentBlock(text) {
  const s = text.indexOf(BEGIN);
  const e = text.indexOf(END);
  if (s === -1 || e === -1 || e < s) return null;
  return text.slice(s, e + END.length);
}

function applyBlock(file, block) {
  const existed = fs.existsSync(file);
  let text = existed ? fs.readFileSync(file, 'utf8') : '';
  const s = text.indexOf(BEGIN);
  const e = text.indexOf(END);
  if (s !== -1 && e !== -1 && e > s) {
    text = text.slice(0, s) + block + text.slice(e + END.length);
  } else if (s !== -1 || e !== -1) {
    die('AGENTS.md has a damaged managed block (lone ' + (s !== -1 ? 'BEGIN' : 'END') + ' marker) - remove the stray marker, then sync');
  } else {
    text = text.trimEnd() + (text.trim() ? '\n\n' : '') + block + '\n';
  }
  fs.writeFileSync(file, text);
  return { created: !existed };
}

function upsertMemoryIndex(file, line) {
  const text = fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : '# Memory Index\n';
  const lines = text.split(/\r?\n/);
  const idx = lines.findIndex((l) => l.includes('](' + MEM_FILE + ')'));
  if (idx >= 0) lines[idx] = line;
  else {
    let last = lines.length - 1;
    while (last >= 0 && !lines[last].trim()) last--;
    lines.splice(last + 1, 0, line);
  }
  fs.writeFileSync(file, lines.join('\n'));
}

function main() {
  const [cmdName, ...argv] = process.argv.slice(2);
  const { pos, opts } = parseArgs(argv);
  const root = opts.root ? path.resolve(String(opts.root)) : repoRoot();
  const mem = memoryDir(root, opts.memory || process.env.THESKILLS_MEMORY_DIR);
  const state = readPins(root);
  const installed = installedSkills(root);
  const needPins = () => {
    if (!state) die('no pins - run: init, or pin <skill> --when "<trigger>"');
    return state;
  };

  switch (cmdName) {
    case 'init': {
      if (state) { console.log(`OK: pins.json already exists (${state.pins.length} pins)`); return; }
      console.log('OK: created ' + writePins(root, { version: 1, pins: [] }));
      console.log('next: discover, then pin <skill> --when "<trigger>", then sync');
      return;
    }

    case 'discover': {
      const rows = [...installed.values()].sort((a, b) => a.name.localeCompare(b.name));
      if (!rows.length) console.log('No installed skills found in ~/.qoder/skills, ~/.agents/skills, ./.qoder/skills');
      for (const r of rows) {
        console.log(`${r.name}\t[${r.scope}]\t${(r.description || '').replace(/\s+/g, ' ').slice(0, 78)}`);
      }
      const only = catalogOnly(root, installed);
      if (only.length) {
        console.log(`\nIn this repo but NOT installed (${only.length}) - nothing can auto-invoke them until they are:`);
        console.log('  ' + only.slice(0, 40).join(', ') + (only.length > 40 ? ' ...' : ''));
      }
      console.log('\nRuntime built-ins (invocable with no install dir): ' + [...BUILTIN].join(', '));
      console.log('Pin by the names above: pin <name> --when "<trigger>"   (--force pins an uninstalled one)');
      return;
    }

    case 'list': {
      needPins();
      if (!state.pins.length) { console.log('No skills pinned yet.'); return; }
      console.log('skill\tstatus\twhen\tskill-state\tsource\tnote');
      for (const p of state.pins) {
        console.log(`${p.skill}\t${p.status}\t${p.when}\t${p.skill_state}\t${p.source || '-'}\t${p.note || ''}`);
      }
      console.log(`\n${active(state).length} active / ${state.pins.length} total · updated ${state.updated}`);
      return;
    }

    case 'pin': {
      if (!pos.length) die('pin needs a skill name: pin <skill> --when "<trigger>"');
      if (!opts.when) die('pin requires --when "<trigger>" - a fixed skill with no trigger would fire on every turn');
      const st = readPins(root) || { version: 1, pins: [] };
      const when = String(opts.when);
      const note = opts.note ? String(opts.note) : '';
      let touched = 0;
      for (const name of pos) {
        const r = resolveSkill(name, root, installed);
        if (r.kind === 'missing' && !opts.force) {
          const near = [...installed.keys()].filter((k) => k.startsWith(name.slice(0, 3)) || name.startsWith(k.slice(0, 3)));
          console.log(`SKIP: '${name}' is not installed and is not a built-in. Closest: ${near.join(', ') || 'none'} - install it, or --force to pin unverified`);
          continue;
        }
        if (r.kind === 'uninstalled' && !opts.force) {
          console.log(`SKIP: '${name}' has a folder here (${r.record.dir}) but is NOT installed, so nothing can auto-invoke it. Install it, or --force to pin anyway`);
          continue;
        }
        touched++;
        const existing = st.pins.find((p) => p.skill === name);
        if (existing) {
          Object.assign(existing, { when, note, status: 'active', skill_state: r.kind });
          console.log(`OK: updated pin '${name}' -> when: ${when}`);
        } else {
          st.pins.push({
            skill: name, when, note, status: 'active', added: today(), skill_state: r.kind,
            source: r.record.base || (r.kind === 'builtin' ? 'runtime' : 'declared'),
          });
          console.log(`OK: pinned '${name}' (${r.kind}) -> when: ${when}`);
        }
      }
      if (touched) {
        writePins(root, st);
        console.log('\nSinks NOT updated - run: sync');
      }
      return;
    }

    case 'unpin': {
      needPins();
      if (!pos.length && !opts.all) die('unpin needs a skill name or --all');
      const before = state.pins.length;
      state.pins = opts.all ? [] : state.pins.filter((p) => !pos.includes(p.skill));
      const gone = before - state.pins.length;
      if (!gone) { console.log('SKIP: none of those are pinned: ' + pos.join(', ')); return; }
      writePins(root, state);
      console.log(`OK: removed ${gone} pin(s). Run sync.`);
      return;
    }

    case 'pause': case 'resume': {
      needPins();
      if (!pos.length) die(`${cmdName} needs a skill name`);
      let n = 0;
      for (const p of state.pins) {
        if (pos.includes(p.skill)) { p.status = cmdName === 'pause' ? 'paused' : 'active'; n++; }
      }
      if (!n) die('none of those are pinned: ' + pos.join(', '));
      writePins(root, state);
      console.log(`OK: ${cmdName === 'pause' ? 'paused' : 'resumed'} ${n} pin(s). Run sync.`);
      return;
    }

    case 'when': {
      needPins();
      if (!pos.length || !opts.trigger) die('usage: when <skill> --trigger "<new trigger>"');
      const p = state.pins.find((x) => x.skill === pos[0]);
      if (!p) die('not pinned: ' + pos[0]);
      p.when = String(opts.trigger);
      writePins(root, state);
      console.log(`OK: '${p.skill}' when -> ${p.when}. Run sync.`);
      return;
    }

    case 'sync': {
      needPins();
      const agents = path.join(root, 'AGENTS.md');
      const a = applyBlock(agents, blockText(state));
      console.log(`OK: synced ${active(state).length} active pin(s)`);
      console.log(`  baseline   AGENTS.md ${a.created ? 'created' : 'updated'}   ${agents}`);
      if (mem) {
        fs.mkdirSync(mem, { recursive: true });
        const memFile = path.join(mem, MEM_FILE);
        const isNew = !fs.existsSync(memFile);
        fs.writeFileSync(memFile, memoryText(state));
        upsertMemoryIndex(path.join(mem, 'MEMORY.md'), INDEX_LINE);
        console.log(`  secondary  memory ${isNew ? 'created' : 'updated'}   ${memFile}`);
        console.log(`  secondary  index                          ${path.join(mem, 'MEMORY.md')}`);
      } else {
        console.log('  secondary  memory SKIPPED - no memory dir in this harness; the AGENTS.md block '
          + 'carries the pins. Point --memory <dir> at one, or wire a session-start hook, to add the layer.');
      }
      console.log('\nTakes effect in new sessions (or after /skills reload).');
      return;
    }

    case 'status': case 'audit': {
      if (!state) { console.log(`NO PINS: ${pinsPath(root)} missing. Nothing is auto-applied here.`); process.exitCode = 1; return; }
      const problems = [];
      const agentsFile = path.join(root, 'AGENTS.md');
      const atext = fs.existsSync(agentsFile) ? fs.readFileSync(agentsFile, 'utf8') : '';
      const block = currentBlock(atext);
      if (block === null) problems.push('AGENTS.md has no managed block - run sync');
      else if (block !== blockText(state)) problems.push('the AGENTS.md block is stale or was hand-edited - run sync');
      let memoryState = 'absent (not a drift)';
      if (mem) {
        const memFile = path.join(mem, MEM_FILE);
        const indexFile = path.join(mem, 'MEMORY.md');
        memoryState = fs.existsSync(memFile) ? 'present at ' + mem : 'MISSING';
        if (!fs.existsSync(memFile)) problems.push(`memory file missing: ${memFile} - run sync`);
        else if (fs.readFileSync(memFile, 'utf8') !== memoryText(state)) problems.push('memory file drifted from pins.json - run sync');
        if (!fs.existsSync(indexFile)) problems.push(`no MEMORY.md index at ${indexFile}`);
        else if (!fs.readFileSync(indexFile, 'utf8').includes('](' + MEM_FILE + ')')) problems.push('MEMORY.md has no pointer to ' + MEM_FILE + ' - run sync');
      }
      let changed = false;
      for (const p of state.pins) {
        const r = resolveSkill(p.skill, root, installed);
        if (r.kind === 'missing') problems.push(`'${p.skill}' resolves to nothing (not installed, not a built-in, no folder here)`);
        else if (r.kind === 'uninstalled' && p.status === 'active') {
          problems.push(`'${p.skill}' is active but only authored here (${r.record.dir}) - install it or \`pause\` it; nothing can auto-invoke it`);
        }
        if (cmdName === 'audit' && p.skill_state !== r.kind) { p.skill_state = r.kind; changed = true; }
      }
      if (cmdName === 'audit') {
        writePins(root, state);
        console.log(changed ? 'OK: refreshed skill_state in pins.json' : 'OK: pins.json skill_state already current');
      }
      console.log(`root    ${root}`);
      if (mem) console.log(`memory  ${mem}`);
      console.log(`pins ${state.pins.length} (${active(state).length} active) · AGENTS.md ${block ? 'block present' : 'NO BLOCK'} · memory ${memoryState}`);
      if (problems.length) {
        console.log('\nDRIFT / PROBLEMS:');
        for (const p of [...new Set(problems)]) console.log('  - ' + p);
        process.exitCode = 2;
      } else {
        console.log('\nCLEAN: every available layer agrees with the registry, and every active pin '
          + 'resolves to an invocable skill.');
      }
      return;
    }

    case 'bootstrap': {
      if (!state || !active(state).length) {
        console.log('No active pins in this repo - nothing is auto-applied.');
        console.log('Pin with: node <theskills>/scripts/theskills.mjs pin <skill> --when "<trigger>" && sync');
        return;
      }
      console.log(blockText(state).replace(BEGIN, '').replace(END, '').trim());
      console.log('\nApplies for the rest of this session and every later one. Do not re-run bootstrap per turn - check `when` against each request.');
      return;
    }

    default:
      console.log(`theskills - pin skills as standing auto-apply behavior

  node scripts/theskills.mjs <command>

  init                          create .theskills/pins.json
  discover                      what is installed / built-in / here-but-uninstalled
  list                          current pins
  pin <skill...> --when "..."   pin with a mandatory trigger  (--note "...", --force)
  unpin <skill...> | --all      remove pins
  pause|resume <skill>          keep the record, stop/start auto-applying
  when <skill> --trigger "..."  restate a trigger
  sync                          rewrite AGENTS.md block + memory file + index line
  status                        read-only drift check (exit 2 on drift)
  audit                         status + refresh skill_state into pins.json
  bootstrap                     print what applies right now

  overrides: --root <dir>, --memory <dir>  (env THESKILLS_MEMORY_DIR also works)`);
      if (cmdName) process.exitCode = 1;
  }
}

main();
