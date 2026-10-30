---
name: heir
description: 'Acknowledge the legacy of previous agents before rebuilding anything. At the start of a task, if the project has a `bequest/` directory, open its INDEX, decide whether any inherited asset fits THIS task, verify it before trusting it, then reuse, adapt or extend it in place. Use when starting work in a project that may already contain scripts, procedures, configs or patterns left by earlier sessions, or when the user says "we did this before", "reuse what exists", "check what is already there". Inherited assets are evaluated, not assumed: inputs, assumptions, dependencies and verification status are read from the asset card, and its tests are run before it is trusted — a partially verified asset is a lead, not a fact. Improvements update the asset and its card rather than forking a copy. heir never creates bequest assets itself; when the session produces reusable work it hands off to `bequeath` so the next agent inherits it too.'
when_to_use: At the beginning of a task in a project that has a `bequest/` directory, or whenever prior work might already solve part of the current problem.
argument-hint: "[what the current task is about, for matching against bequest/INDEX.md]"
---

# Heir

Another agent may have already paid for part of this task. Heir is the habit of **looking before rebuilding**, and
the discipline of **verifying before trusting** what you find.

It is the reading half of a pair: [`bequeath`](../bequeath/SKILL.md) writes verified assets into `bequest/`;
heir finds them at the start of the next task. The rules live with their owner — heir links, it does not restate.

## Step 1 — acknowledge, in one line

Check for the inheritance surface; do not turn this into a speech:

```bash
ls bequest/INDEX.md 2>/dev/null && head -40 bequest/INDEX.md
```

If there is no `bequest/`, say nothing further and proceed; that is a normal project. If there is one, hold one
sentence in mind: *"previous work may already cover part of this"* — and spend the next two minutes checking
before writing code.

The cost rule: **one index read**, not a directory crawl. A `bequest/` with fifty assets is still cheaper to
scan by its index rows than by opening folders.

## Step 2 — match only what the task needs

Read `INDEX.md` rows and match against the task:

| Match by | Example |
|---|---|
| the asset's "What it does" sentence | "flags rows above a latency threshold" vs a slow-export task |
| type | a `procedure` for an operational task, a `script` for an analysis |
| trigger words in "When to use it" | "flaky tests under CI load", "migration blocked on a lock" |
| the constraint assets | "X fails because Y" — these prevent known dead ends |

Ignore everything else without guilt. Reading all cards "to be thorough" is how context dies.

## Step 3 — evaluate, do not assume

Open the card of a matched asset and read four things before running it
([`references/00-evaluating-an-inherited-asset.md`](references/00-evaluating-an-inherited-asset.md)):

1. **Inputs** — does the task actually have that input, in that shape?
2. **Dependencies** — present in this environment, at a compatible version?
3. **Assumptions and limitations** — OS, data shape, scale, what it never supported.
4. **Verification status** — `verified (automated)` or `(manual)` you may trust after re-running its tests;
   `partially verified` is a lead, not a fact; `unverified` is a hypothesis with a filename.

Then check for **drift**: the card's date and versions versus the project now. An asset written for Python 3.9
that was never run on 3.12 is not wrong — it is untested here. Say which case applies.

Run what the card offers as evidence — its `tests/`, or its recorded verification steps when the asset is a
procedure, config or query with no test files. A check that passes today is stronger evidence than a card line
written a month ago; a check that fails is a finding to record before touching anything. An asset whose "proof"
is only that someone used it once is a lead, not a fact.

## Step 4 — reuse, adapt, extend, or supersede

| Situation | Action |
|---|---|
| Fits as-is and its tests pass | use it; cite it in the work (commit message, PR, or decision record) |
| Close, but parameters or one branch are missing | **extend in place**: add the flag/branch, update the card, update the index row if the "what it does" sentence changed |
| The approach is right but the environment or data changed materially | **adapt in place**: adjust, re-run the full case matrix, update the verification block with today's date |
| It cannot be made correct, or a genuinely different method is needed | create a new asset under `bequest/` and mark the old card `Superseded by <slug>` |
| The card's claim is wrong (it never worked, or no longer does) | fix the asset if cheap; otherwise mark it `unverified` with what you observed, and tell the user in the same turn |

**Respect the original work.** Do not rewrite an inherited asset into your preferred style; preserve what made
it useful, change only what the task requires, and leave the card describing what future agents will actually
find. A silent rewrite is indistinguishable from a bug for the next reader.

## Step 5 — record the inheritance

Provenance is what lets the next agent trust the chain:

- one line in the commit message / PR body: `reuse: bequest/find-slow-requests (extended --threshold-ms)`;
- in a decision record or incident document, cite the asset path alongside other evidence;
- if you changed the asset, its card's **Origin** line says what changed and why.

Two lines of provenance cost nothing and prevent the "did this come from somewhere?" archaeology later.

## Step 6 — continue the legacy

At the end of the session, if the work produced something reusable — a script, a procedure, a constraint worth
checking — **offer** [`bequeath`](../bequeath/SKILL.md). Do not create assets silently: bequeath's rule is
propose → user selects → generalize → test.

heir does not write assets, does not generalise them, and does not decide what is worth keeping. Those are
bequeath's, and duplicating them here would produce two half-rules that disagree.

## Anti-patterns

- **Rebuilding first, checking later.** The most expensive way to learn an asset existed.
- **Trusting the card's status without running anything.** Cards age; environments move.
- **Reading everything.** The index exists so you do not have to.
- **Forking instead of extending.** Two near-identical assets is how the directory stops being readable.
- **Editing an asset and not its card.** The next agent inherits a lie.
- **Treating `bequest/` as authority.** It is prior evidence, not a source of truth about the current project.
- **Announcing the habit.** "As heir, I will now check the bequest" is noise; do it and mention only what you found.

## The pair

```text
end of session            start of next task
bequeath  ---------->  bequest/  ---------->  heir
(propose, select,          INDEX.md +            (match, evaluate, verify,
 generalize, test,         cards + tests         reuse/adapt, cite)
 store)
```

Both may be active in one session: heir at the beginning, bequeath at the end. Neither replaces `flush`/`iwts`
(session state) or `adapt` (global skills) — see bequeath's boundary table.
