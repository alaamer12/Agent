# Agent Instructions

Instructions for AI agents working in this repository. Follow them on every task, including work delegated to
subagents. This file is a rulebook: it states what you must do and what you must read. It does not describe
the system - the files it points to do that.

<!-- agents-md:sections 1-10. Delete a section only if the user agreed it does not apply; never leave it blank. -->

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

> Generated from sections 1-9. **When the rulebook changes, regenerate this block.** It is a projection, not a
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

## 11. Rulebook Maintenance

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
| A new reusable component area appears, or the units index moves | 4 |
| A design/prototype directory is added, or scope changes between current and future | 5 |
| A shell, tooling, or package-manager restriction changes | 6 |
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
