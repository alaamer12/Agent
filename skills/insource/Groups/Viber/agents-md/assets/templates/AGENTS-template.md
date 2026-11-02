# Agent Instructions

Instructions for AI agents working in this repository. Follow them on every task, including work delegated to
subagents. This file is a rulebook: it states what you must do and what you must read. It does not describe
the system - the files it points to do that.

<!-- agents-md:sections 1-15. Delete a section only if the user agreed it does not apply; never leave it blank. -->
<!-- Budgets: ~500 lines for the file, ~50 lines per section. A section past ~50 lines is a doc with a
pointer missing: move its detail to a file under docs/ (project convention), keep 2-4 obligation lines plus
"Read: <path>" here. agents_lint.py flags it. -->

---

## 1. Agent Instructions

Stable behavioral rules, independent of version, channel, or phase.

- <!-- e.g. Do not contradict the steering docs without verifying the codebase first. -->
- <!-- e.g. Ask before deleting files or rewriting history; a rebuild or a revert is cheaper than a lost artifact. -->
- <!-- e.g. Report which skill(s) you used for the task, so the claim is checkable. -->

---

## 2. Mandatory Context

**Read these at the start of every conversation, regardless of the task, and keep them in mind for every
decision.** Each index file is a router, not the answer - follow its links to the specific document that
answers your question instead of assuming the index was enough.

### 2.1 Active context

| Dimension | Active | Out of scope - do not read or apply |
|---|---|---|
| Version | <!-- e.g. V1 --> | <!-- e.g. v2/ - future features only --> |
| Channel | <!-- e.g. canary --> | <!-- e.g. stable-only rules where they differ --> |
| <!-- other: MVP / post-MVP, tenant, platform --> | <!-- active value --> | <!-- excluded value(s) --> |

Never mix documentation, requirements, or rules across dimensions. If a file belongs to an excluded context,
treat it as absent.

### 2.2 Files to read

| File | Purpose |
|---|---|
| <!-- path --> | <!-- one line: what decision this file governs --> |
| <!-- [COMMITMENTS.md](COMMITMENTS.md) --> | <!-- declared priorities and trade-offs - read before choosing an approach that trades dimensions; owned by commitments-md --> |
| <!-- path --> | <!-- ... --> |

Shared/base context reads apply in every active context:

| File | Purpose |
|---|---|
| <!-- path --> | <!-- ... --> |

---

## 3. Development Workflow

- **Branching:** <!-- which branch work lands on first; what may be committed directly where; naming -->
- **Versioning:** <!-- format e.g. MAJOR.MINOR.PATCH.TAG{n}; which file holds the base; what increments per rebuild; who may change the base -->
- **Promotion / change management:** <!-- how work moves dev -> test -> release; who approves; what "stable" means here -->
- **CI and release effects:** <!-- what a push to each branch produces -->
- **Commits:** <!-- project convention, or a pointer to it; never both -->

---

## 4. Units Reference

**Before any implementation or planning work:**

1. Read <!-- path e.g. docs/UNITS.md --> in full.
2. Check whether an existing unit already covers, or partially covers, what the task needs. Reuse or extend it
   rather than building a parallel component; if you must not, state the reason in the change.
3. If the task introduces a new reusable unit, update the same file with its entry **as part of this task**,
   not as a follow-up. <!-- who owns the update when a subagent made the unit: master or subagent -->

This file is the index of important components; it is generated and maintained by
<!-- skill or owner -->, not by hand-editing during unrelated work.

---

## 5. Design, Prototypes, and Visual References

| Location | Scope | Use for |
|---|---|---|
| <!-- path --> | <!-- active context --> | <!-- current spec for what is shipping --> |
| <!-- path --> | <!-- excluded / future --> | <!-- future-scope work only --> |

Before treating a mockup or prototype as current, confirm it belongs to the active context. Do not mix
future-scope visuals into in-scope work, and do not assume every file in a design directory is relevant.

---

## 6. Execution and Tool Usage

- **Shell:** <!-- which shell to prefer and why, e.g. "PowerShell hangs in this environment; use CMD" -->
- **Chaining:** <!-- one command at a time; no && / pipes unless unavoidable, and why -->
- **Complex commands:** <!-- write a script under <dir>, run it, delete it when finished -->
- **Package manager:** <!-- the one to use, e.g. bun/bunx; what not to touch and why (lockfiles) -->
- **Verification commands:** <!-- the repo's own build/test commands, or a pointer; note any the agent must not run unprompted -->

---

## 7. Environment and Secrets

- **Do not edit `.env` files directly.** <!-- permitted route instead -->
- **Strategy in use:** <!-- pick/combine as decided: type-safe schema / build-time generation / runtime secret store -->
  - <!-- type-safe validation: where the schema lives, what it protects against -->
  - <!-- build-time generation: central source file, generating script, per-app outputs; regenerate command -->
  - <!-- runtime secrets: provider (e.g. 1Password), retrieval mechanism, and what must never be persisted -->
- **In debug scripts:** <!-- read from process.env; never hardcode secrets or connection strings -->

---

## 8. Debugging

- **Reproduce first:** <!-- how to get the failing state locally -->
- **Escalation order:** <!-- e.g. query the data store directly -> call the service layer -> then the UI/routing -->
- **Data access during debugging:** <!-- permitted to inspect? permitted to modify? which environment (local/staging/production)? -->
- **Visual verification:** <!-- how to observe the app: build+run, screenshots, device logs, harness tools -->
- **Cleanup:** <!-- remove scratch/debug artifacts when finished -->
- **If the code looks correct, do not stop at one failed attempt.** <!-- project-specific persistence rule -->

---

## 9. Agent Execution and Startup

Before the first change in a session:

1. <!-- read the mandatory context in section 2 -->
2. <!-- confirm the active version/channel, and how to detect it (branch, config, flag) -->
3. <!-- the minimum verification command that proves the toolchain works, or state that it was skipped -->
4. <!-- units check for implementation tasks (section 4) -->

Then, during work: <!-- reporting duties, checkpoints, when to stop and ask -->

---

## 10. Main Agent and Subagents

### 10.1 The premise that shapes every rule below

A subagent cannot see this conversation and cannot ask follow-up questions. Anything not in its prompt is
unavailable to it. Assume the omission will be filled by a guess.

### 10.2 Main agent responsibilities

1. **Name by responsibility.** Assign each subagent a name that says what it does
   (<!-- e.g. pipeline-diff-reviewer -->); the name is used for the handle, the report file, and status
   reporting. Never a generic label.
2. **Give complete context up front.** Goal, exact files and paths already identified, decisions already made
   (naming, chosen approach, rejected options), and the precise output expected. Do not delegate the framing.
3. **List the documents it must read.** Name the specific files for that task, in the prompt, on top of the
   baseline block below. A subagent reading only the general list will miss the constraint that mattered.
4. **Propagate the duties.** Units check (section 4), execution and shell rules (section 6), environment rules
   (section 7), and the report obligation.
5. **Bound the work.** State what the subagent may decide alone, what it must return undecided, and what it
   must not touch (files, branches, shared state). When several subagents can write, assign disjoint paths or
   sequence them.
6. **Merge, do not re-do.** When fanning out, the orchestrator splits scoped subtasks and integrates results;
   it does not perform every leaf's work itself.
7. **Collect the reports.** Confirm each finished subagent wrote its report; reconcile contradictions between
   reports before acting on them.

### 10.3 Subagent duties

- Read the mandatory documents listed in your prompt in full, and follow them exactly.
- Perform only the scoped task; return anything outside it as a finding, not as a change.
- Do not create parallel components where an existing unit covers the need (section 4).
- Obey the shell, package-manager, and environment rules (sections 6-7); do not edit `.env` or rewrite history.
- Write your report (10.5) and return its summary alongside the deliverable.
- If the task is impossible as briefed, say so with the evidence rather than substituting a different goal.

### 10.4 Baseline block - paste at the top of every subagent prompt

> Generated from sections 1-9, 11-13. **When the rulebook changes, regenerate this block.** It is a projection, not a
> second source of truth.

```text
=== MANDATORY AGENT PREFERENCES (read and follow) ===

1. CONTEXT - active version <!-- --> ; active channel <!-- --> ; ignore <!-- excluded paths -->
   Read in full before deciding anything: <!-- paths, from section 2 -->
   Indexes are routers: follow the links to the doc that answers your question.
2. TASK-SPECIFIC DOCS - the master lists these below; read them and adhere exactly.
3. SKILLS - <!-- project rule for mandatory skill use, or "not required for read-only questions" -->
4. SHELL - <!-- section 6, compressed: which shell, chaining, scratch scripts and cleanup -->
5. TOOLING - <!-- section 6: the one package manager -->
6. ENV - <!-- section 7: the route to change env values, and the .env prohibition -->
7. DEBUG - <!-- section 8: permitted inspection/modification, escalation order, cleanup -->
8. UNITS - read <!-- units file --> before implementing; reuse/extend, and add an entry for any new unit
9. REPORT - write <!-- report path pattern --> when finished: goal, actions, files touched, decisions,
   verification. This is in addition to your returned result.
10. PRIVACY - <!-- section 11, compressed: private paths + the rule that outputs of hidden tools stay
   private; write only into those, never commit them -->
11. RESOURCEFUL - <!-- section 12, compressed: project-local deps/toolchains/envs; no global installs
   without asking -->
12. AUTHORITY - <!-- section 13, compressed: ask before system installs, external processes, existing-DB
   writes; if blocked, say what you cannot do and ask -->
13. GIT - <!-- section 16, compressed: allowed/never tiers, stash pattern if allowed, commit identity rule -->

TASK-SPECIFIC DOCS: <!-- master fills this -->
SCOPE: <!-- what you may change; what you must not -->
OUTPUT CONTRACT: <!-- the exact deliverable, in the exact form -->

=== END PREFERENCES - the task follows below ===
```

### 10.5 Reports

Each subagent writes <!-- e.g. .repertoire/agents/<name>.md --> containing: what it was asked to do, what it
did, files touched, decisions made and why, verification performed and its result, and anything left
undecided. <!-- If the same role can run twice: <name>-<yyyymmdd-HHmm>.md, or the rule that overwriting is fine. -->
Reports are the durable record; the returned text is not.

### 10.6 Fan-out notation, when the project uses it

`x->N1x->N2x->...` - `x` is the orchestrator; each number is the agent count at that depth; branching factor
is `count[n+1] / count[n]`. Execute: parse, split into one scoped subtask per leaf, launch depth 1 in parallel,
have each mid-depth agent spawn its children and merge before returning, root merges everything into one
response. Limits: max <!-- N --> depths and max <!-- N --> total workers; if a leaf fails, report the failure
in the merged result instead of silently re-doing its scope.

---

## 11. Privacy

**What stays hidden - and what hiding it hides along with it.** This section is the project's visibility
policy for agents: paths that must not be committed or quoted in artifacts that leave the repo, and the
duties that keep the declaration real.

- Private paths: <!-- e.g. the agent-skills folder, working-plan directories, `tools/pocketbase.exe` -->
- **Cascade:** hiding a producer hides its outputs. If the agent skills are private, the folders those
  skills write are private too - the `.iwts/` run record, generated reports, caches.
- **Hidden binaries:** the file stays out; the *need* stays in - record where to obtain/install it in
  <!-- setup doc path -->, not the binary itself.
- **Sync duty:** every private path must also appear in `.gitignore`. When this section is updated and a
  path is missing there - or was tracked before being declared private - **ask the user before clearing
  the cache** (`git rm --cached`, deleting local generated copies); an ignore rule hides the future, not
  the past. Never delete silently.
- <!-- If nothing is private, state it: "No privacy restrictions recorded; everything here is shareable as-is." -->

---

## 12. Resourceful

**Project-local first.** Anything that can be installed, pinned, or run per-project is: dependencies,
toolchains, interpreters, CLIs, environments. Global installs are exceptions, named here with their reason -
never a convenience default.

- Local environments are the rule, e.g. `[.venv]` for Python, a project install for JS tooling (never a
  global `-g` install for a project need), a per-project `[Cargo]`/`[Composer]`/`[Maven]` local store, a
  project-local toolchain for the JVM - the same idea in every language.
- Run project binaries through the project's own tooling (the venv, `node_modules/.bin`, the package
  manager's exec), so the version used is the version the project pinned.
- Global installs allowed as exceptions: <!-- e.g. none, or: the company CLI the team shares; why, and who needs it -->

---

## 13. Authority

**What agents may do in this environment, and what they must ask about first.** Every action below has one
of two settings: **ask per session** (the safe default) or **fixed** (pre-granted - record the grant here,
with its reason).

| Action | Setting |
|---|---|
| Install a binary or package outside the project (system-wide; a standalone tool such as <!-- e.g. pocketbase -->) | <!-- ask per session / fixed --> |
| Run external processes (emulators, service daemons, third-party CLIs) | <!-- ask per session / fixed --> |
| Write to an existing database outside scratch/local data | <!-- ask per session / fixed --> |
| Read or write credentials and secret stores | <!-- ask per session / fixed --> |
| Change machine-level configuration (shell profiles, global config, system services) | <!-- ask per session / fixed --> |

- Installing an external tool is not inherently forbidden: a project may genuinely need something it does
  not have (a missing binary, a package the platform lacks) - that install happens under this section's
  setting, not as a silent act and not as an automatic refusal.
- Project-local installs belong to section 12 (Resourceful): this project's dependencies, toolchains and
  environments install locally without asking, because they touch nothing outside the project.
- **When an authority limit blocks the requested work, say so and ask** - never improvise around it and
  never silently skip the blocked part. The `/honest` shape, in plain words: "Under the current authority I
  may not be able to do X, Y, Z. Shall I continue as is, or do you grant me authority for it?"

---

## 14. Skills

**Per-skill instructions, owned by the skills.** Each independent skill that matters to this project
records one row here: when it applies, and what an agent must read or do before using it - the
condition and the pointer, not the skill's whole manual.

| Skill | Use it when | Read or do first |
|---|---|---|
| <!-- plan --> | <!-- work spans more than one session --> | <!-- docs/plans/README.md - the plan format this repo follows --> |
| <!-- commit --> | <!-- before any commit --> | <!-- the message map in docs/commit-craft.md --> |

- A skill adds its row here when the project adopts it; the row is updated when the skill's usage in
  this project changes. Keep rows to one line.

---

## 15. Rulebook Maintenance

**This file is current or it is wrong.** Every session that changes a project rule updates this file in the
same change — not in a follow-up, not next sprint.

- **Last reviewed:** <!-- YYYY-MM-DD -->

### What must be written here, the moment it is decided

| The decision | Section to update |
|---|---|
| A new channel, version, or other conditional context is introduced (e.g. the project adds `canary` alongside `stable`) | 2 — add the dimension, its active value, and what is now excluded |
| A new mandatory document is created | 2 (or 4/5 as appropriate) — add its row and one-line purpose |
| A document is renamed, moved, merged, or split | the row that pointed at it — fix the path in the same change that moved the file |
| A document becomes obsolete or moves out of active scope | remove or fence it; do not leave a pointer that reads as current |
| Branching, versioning, or promotion policy changes | 3 |
| A git permission changes (allowed/ask/never tier, stash policy, commit author identity) | 16 — the tier line, **and regenerate the block's GIT clause in 10.4** |
| A new reusable component area appears, or the units index moves | 4 |
| A path becomes private (or stops being) | 11 — the entry **and the `.gitignore` line in the same change**; if the path was already tracked, ask the user before clearing the cache |
| A design/prototype directory is added, or scope changes between current and future | 5 |
| A shell, tooling, or package-manager restriction changes | 6 |
| A dependency/local-environment rule changes, or a global install becomes an allowed exception | 12 — the exception and the local-first rule stay in one place |
| An authority setting changes (ask-per-session vs fixed), or a grant is given/revoked | 13 — the setting, its reason, and its scope in the same change |
| A skill gains a project-specific usage note (read X first, run it this way), or stops needing one | 14 — one row, condition + pointer |
| The environment or secrets strategy changes (new schema layer, new provider, new generation step) | 7 |
| Debug permissions change (new environment, new inspection tool) | 8 |
| A startup step is added or removed | 9 |
| Delegation rules change (naming, reports, autonomy, fan-out limits) | 10 — **and regenerate the block in 10.4** |

### What does not belong here

Technical detail belongs in the documents this file points at. A rule change is "the envelope around the
agent": *what must be read, what may be done, by whom, in which scope*. If the sentence explains how something
works, it goes into a doc and this file gains a row.

### The drift this prevents

A rulebook that stops being updated is worse than none, because agents trust it. `stable`-only rules after
`canary` shipped, a pointer to a file renamed three months ago, a "current version is V1" line while V2 is in
development — each one is a wrong instruction that reads like an authoritative one.

Run the check after editing:

```bash
python scripts/agents_lint.py AGENTS.md      # sections, dead links, scope fence, block sync, review date
```

## 16. Version Control

<!-- The git-specific half of authority: what the agent may DO with git, and under whose name. The
     `commit` and `branch` skills detect conventions and ask the authorship question precisely
     because this section should answer it; keep it in sync with section 3's branch model. -->

- **Allowed:** read-only git always (`status`, `log`, `diff`, `show`); <!-- and: commit on which
  branches, following section 3; create branches? tag? -->
- **Ask first:** <!-- push / PR creation / merge into shared branches / delete branches / release
  tags - outward-facing git actions -->
- **Never without explicit user order:** history rewrites (`rebase`, amending pushed commits,
  `reset --hard`, `git clean`, force-push), and never `--no-verify` to pass a failing hook - fix
  the cause instead.
- **Stash policy:** <!-- allowed / forbidden. If allowed, the pattern: `git stash push -u -m
  "agent/<task-slug>"`; in a shared worktree apply the exact entry by message, never bare `pop`,
  and drop only entries this agent created. If forbidden, say what to use instead (a WIP commit
  on a scratch branch, a dedicated worktree). -->
- **Author identity:** commits keep <!-- the repository's configured human identity / an agent
  identity -->; agent involvement is <!-- disclosed with a `Co-authored-by:` trailer naming the
  tool - state the exact name and address / invisible by choice -->. Never edit `git config` to
  change authorship; the `commit`/`branch` skills defer to this line.
