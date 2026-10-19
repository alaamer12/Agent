---
name: dbug-investigation
description: The core reasoning engine of dbug — use for the actual investigation of any bug: classify the problem, decide what to ask the user, gather and rank evidence, map the pipeline, run the hypothesis loop, use Git forensics when it "worked before", locate the first invalid state, design a root-cause fix that is minimal but complete across layers, and escalate honestly when blocked. Load this from dbug/SKILL.md on essentially every debugging task; the domain skills (backend, database, frontend, production) supply the domain moves, this skill supplies the process.
---

# dbug-investigation — the core engine

One loop, seven stages. Visit each; skip none silently.

```
classify → (ask?) → evidence → cause? → fix design → apply+test → verify/capture
```

## 1. Understand & classify

Restate the problem in one sentence: **expected behaviour vs actual
behaviour, under what conditions.** If you cannot write that sentence, you
do not understand the problem yet — that is the whole point of this stage.

| Class | Signal | First move |
|---|---|---|
| **Concrete artifact mismatch** | two sources of truth in hand disagree (schema file vs live DB, spec vs code) | diff them directly — no questions needed |
| **Regression** | "worked before / broke after a change" | Git forensics → [`references/git-forensics.md`](references/git-forensics.md) |
| **Wrong/missing/duplicate data** | output values incorrect but no crash | data-lineage trace → `references/pipeline-model.md` §First invalid state |
| **Failure at a point** | error, stack trace, non-2xx, exception | dissect trace, trace backward from app frame |
| **Performance/resource** | slow, timeout, OOM, grows over time | `production/` (metrics first, not code) |
| **Non-reproducible** | intermittent / prod-only / "only sometimes" | `production/` — observability before anything else |
| **Blast radius: "half the system broke"** | everything at once | stop — go to §2, this class is never self-serve |

Pick the class; it sets the path. A bug can hold two classes (regression
*and* prod-only) — take both paths' cheap parts first.

## 2. Ask the user — only path-changing questions

Investigating a vague problem without context wastes turns you can't get
back. For Regression / blast-radius / "something big changed" classes, ask
**before** digging (skip for Concrete-mismatch class — evidence is already
in hand):

- Was this working before? How do you know / when did you last see it work?
- Was it working in Git? Roughly how many commits ago? Which branch?
- What changed just before it broke — deploy, migration, dependency bump,
  config edit, data change, a big refactor?
- Anywhere else it still works (staging, another machine, another account)?

Every question must be able to change what you do next. Maximum one round
of questions; start investigating with whatever came back.

## 3. Gather evidence before touching anything

Read what already exists — it's free: the exact error text and stack,
logs, recent commits/diffs (`git log`, `git diff HEAD~n`), the files the
error names, tests that cover the path, `.htd/` and `.debugging/bugs/`
(someone may have met this before). Characterize:

```
Expected: X.   Actual: Y.   Repro rate: always | sometimes (≈N in M) | once.
Conditions: which env, which data, which user, which time-of-day, since when.
```

Then decide what new evidence needs creating — temp scripts go to
`.debugging/tmp/`, debug logging through the scoped facility — both per
[`../instrumentation/SKILL.md`](../instrumentation/SKILL.md).

## 4. Map the pipeline and form hypotheses

Sketch the concrete execution/data path for *this* symptom —
[`references/pipeline-model.md`](references/pipeline-model.md) gives the
entry/intermediate/terminal roles and when to trace forward vs backward vs
narrow vs widen. The failure's location is almost never the defect's
location; the target is the **first invalid state** — the earliest point
where actual state diverges from expected.

Run the loop from [`references/hypothesis-and-evidence.md`](references/hypothesis-and-evidence.md):
falsifiable hypothesis → prediction → cheapest experiment that can *refute*
it (ladder + technique cost table in
[`references/escalation-ladder.md`](references/escalation-ladder.md)).
Never "guess → change code → run → hope". Negative results are progress:
they delete whole regions of the search space.

If the environment also loads a separate **Systematic Debugging** skill,
use its useful parts inside this loop — adapt, don't run a second ritual
blindly. The five questions this stage must always answer: what is
failing, why, what evidence supports it, what change addresses the actual
cause, how to verify the result.

When stuck, or before burning an hour: "If we have *this* problem, how do we
debug it?" — [`references/problem-playbooks.md`](references/problem-playbooks.md).

## 5. Design the fix: root cause, minimal, complete

You have the cause when you can state the chain:

```
symptom ← immediate failure ← local cause ← … ← root defect (code/config/data/env)
```

and you know fixing the root removes the failure while fixing anything
below it would not (counterfactual). Design against three rules:

1. **Fix the source of truth, not just the instance.** Live DB repaired by
   hand while the project's schema SQL still contains the bug = the bug
   returns on the next recreate/deploy. Every artifact that *defines* the
   wrong thing gets corrected (schema files, codegen inputs, configs,
   seed data, docs that mislead future agents).
2. **Minimal ≠ incomplete.** Touch only what's necessary — then check
   *necessity was judged across all layers*. Validation added to one route
   handler is bypassed by the other three callers, a background job, and
   the test mock that fakes the next layer.
   **Validate at every layer data passes through; make the bug
   structurally impossible** (constraint in the DB, type in the model,
   guard in the entry, assertion at the boundary — whichever layers exist).
   See `references/pipeline-model.md` §Invariants.
3. **One fix at a time**, change one variable, so the next test run
   attributes honestly.

If the bug is testable and infrastructure exists or is cheap: build the
**failing regression test first** → [`../regression-testing/SKILL.md`](../regression-testing/SKILL.md).

## 6. Apply, test, verify

Fix applied → regression test flips to passing → verification sized to the
risk, cheapest sufficient method:

- test suite already covering the area: run it (free).
- state-level change (schema, config): a small script asserting the new
  state is correct (`.debugging/tmp/`, promote later if reusable).
- behavior needs a browser/stack to observe: **that is intensive** — ask
  the user before standing up e2e tooling (dbug gate #2).

Verification reveals a new problem? New symptom — new iteration of this
file, starting at §1.

## 7. Escalate honestly when blocked

Limited credentials, platform-only UI (e.g. a cloud SQL editor), external
service mutation you cannot perform: never fake it. Hand the user:

1. **What** you cannot do, 2. **why** (the exact limitation), 3. **where**
   to go (console page, editor, command), 4. **what to run/enter** (exact
   statement, prepared in `.debugging/tmp/` so it's copy-paste), 5. **what
   to report back** (the output/error that tells you the step worked).

After the user acts: verify it worked from your side, then continue. The
verification exposing *another* problem loops to §1.

## Close-out checklist (before declaring the bug dead)

- [ ] Regression test kept (or documented why untestable)
- [ ] Source-of-truth artifacts fixed, not just runtime state
- [ ] Every layer the invalid data/state crosses is now guarded
- [ ] `.debugging/tmp/` triaged (promote/delete) → `../instrumentation/`
- [ ] Bug record written if the investigation is worth keeping
- [ ] Is the *class* of problem now a reusable procedure? → **how-to-do**
- [ ] Debug instrumentation removed or gated per `../instrumentation/`

---
**Domain moves live elsewhere:** request/service/env mechanics →
[`../backend/SKILL.md`](../backend/SKILL.md) · data/DB-state →
[`../database/SKILL.md`](../database/SKILL.md) · browser/client →
[`../frontend/SKILL.md`](../frontend/SKILL.md) · unreproducible/prod-only →
[`../production/SKILL.md`](../production/SKILL.md).
