---
name: how-to-do
description: Maintains a persistent .htd/ folder of generalized "how to do X in this codebase" procedures, so multi-step tasks are done the same correct way every time across sessions, agents, and models — instead of silently missing a step. ALWAYS check for a .htd/ folder at the repo root before starting ANY coding task, even if not mentioned, and consult it if present. Trigger this — don't wait to be asked — whenever the user says "add", "create", "change", "update", "refactor", "migrate", "wire up", or "integrate" something in a real codebase, including simple-sounding tasks like "add a table" (exactly what this exists for — never skip as too simple). Also trigger on any mention of "how-to-do", ".htd", or standardizing a workflow. After any nontrivial multi-file change in a repo with (or needing) .htd/, use this proactively to record a new procedure, patch an existing one, or confirm no update is needed — skipping this defeats the skill's purpose.
---

# how-to-do

A persistent record, local to each repo, of *how* to correctly perform
recurring classes of change — so the procedure survives across sessions,
across different agents, and across different models, instead of being
re-derived (and silently getting a step wrong) every time.

## Read this first

Read `references/workflow.md` in full before creating or editing anything
in `.htd/`. It covers the decision logic this skill depends on: how to
match a request to an existing procedure, when to create a new domain file
vs. a new task-ID vs. a patch, how optional steps work, and when (and when
not) to fold patches into base steps. That logic is the actual substance of
this skill — this file is just the entry point.

## The shape, briefly

```
.htd/
├── changing-table-schemas.md    (a "domain file")
├── auth-flow-changes.md
└── ...
```

Each domain file covers a *class* of related changes, not one task. Inside
it, individual tasks are addressable sections called **task-IDs** (e.g.
`[TBL-ADD]`), each with generalized steps, an optional-steps mechanism, and
an append-only log of **patches** — dated corrections discovered when the
documented steps turned out to be incomplete for a later request.

Templates for both are in `assets/`:
- `assets/domain-file-scaffold.md` — starting structure for a new domain file
- `assets/task-id-template.md` — structure for a new task-ID section
- `assets/task-patch-template.md` — structure for a patch entry

A worked example is in `examples/`:
- `examples/example-domain-file.md` — a fully filled-in domain file (a
  `[TBL-ADD]` task-ID plus a patch found on a later request), showing what
  "generalized" actually looks like in practice versus the raw template
  placeholders. Check this whenever it's unclear how specific or general a
  step's wording should be.

## Core loop on every task in a repo with `.htd/`

1. **Before starting**, check `.htd/` for a domain file and task-ID that
   match the request (see `references/workflow.md` → "Matching").
2. **If a match exists**, follow its documented steps — including
   evaluating each optional step's condition against the current request.
3. **Do the task.**
4. **After finishing, decide what to write** using the table below —
   exactly one outcome applies. Full reasoning for each case is in
   `references/workflow.md` → "The three-way decision".

## Deciding: new file, new task-ID, or patch?

| Situation after finishing the task | What to do |
|---|---|
| No existing domain file's subject matter covers this class of change | **Create a new domain file** (`assets/domain-file-scaffold.md`) with a first task-ID inside it, generalized past this one instance. |
| A domain file matched, but no task-ID inside it covers this specific kind of task | **Add a new task-ID** to that existing file (`assets/task-id-template.md`). Do not create a second domain file for the same subject. |
| A task-ID matched, and following it produced a correct, complete result | **Write nothing.** No `.htd` edit needed — the system worked as intended. |
| A task-ID matched, but its documented steps were incomplete or wrong for this request (a step had to be added, changed, or skipped that wasn't in the doc) | **Append a patch** under that task-ID (`assets/task-patch-template.md`). Never rewrite the numbered base steps directly, even to fix an obvious gap. |

If more than one row seems to apply, resolve in the order the table is
listed — e.g. a request always checks "does a domain file exist" before
"does a task-ID exist," and "does a task-ID exist" before deciding a patch
is needed.

## Non-negotiables (details in the reference)

- **Task-IDs are generalized**, not a record of one instance — write steps
  so the next differently-worded request in the same class of task can
  follow them.
- **Files affected is the only mandatory field per step.** Everything else
  about a step's structure is free-form — use whatever conveys the
  necessary understanding (a caveat, a nested list, a warning paragraph).
- **Patches are additive**, dated, and capture both the raw and interpolated
  query. They never silently overwrite base steps.
- **Promotion of a patch into base steps is a deliberate, flagged action**,
  not something an agent does automatically mid-task, even when several
  patches converge on the same gap.
- **`.htd/` lives once per repo**, at the repo root, not per-package in a
  monorepo.
- **One domain file per subject.** If a matching domain file already
  exists, add to it — never create a second file covering the same class
  of change just because the wording of the request differs.
