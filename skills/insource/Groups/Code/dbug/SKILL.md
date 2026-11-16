---
name: dbug
version: 1.1.0
author: Amr
specialized: none
description: 'Debug any problem in any codebase, any language — bug, error, exception, crash, 500, timeout, wrong/missing/duplicate data, regression, "worked before", "works on my machine", flaky, prod-only, or a pasted stack trace — even if the user never says "debug". One loop everywhere: see the problem → understand it → form a falsifiable hypothesis → run the cheapest experiment that can refute it → narrow → repeat; negative results delete search-space, so narrowing IS getting closer. Opens the mind with duck debugging: say the full traceback out loud, hop by hop (what enters, what must leave, what actually left) — it exposes the problem before any tooling runs. Stances: root cause not symptom, fix the source of truth, minimal-but-complete across every layer, every bug is a chance to test, controlled observation, honest escalation. Domain playbooks (backend, database, frontend, production), investigation engine, escalation ladder, git forensics, instrumentation, regression-testing load on demand from references/.'
when_to_use: 'Something is broken, wrong, failing, unexpected, regressed, or hard to reproduce — the moment you feel the urge to "just change code until the error disappears" is the moment to load this skill.'
argument-hint: "[problem description | pasted error/traceback]"
---

# dbug — the one debugging loop

Debugging never changes with the stack. The method is always the same:

```
SEE the problem → UNDERSTAND it → form a HYPOTHESIS → NARROW with an
experiment → LOOP until fixed. Each refuted hypothesis deletes a region
of the search space — narrowing is what getting closer looks like.
```

This file holds the loop's spine, the rails and the stances; how to *see*
and every stage's depth live in `references/` — read only what the current
bug needs (routing table at the bottom). Never "guess → change code → run →
hope": that loop skips Understand and Hypothesis; if you catch yourself in
it, stop and re-enter at stage 1.

Three hard rails over the loop (empirically, where debug sessions die):

- **Make it fail first.** Establish ONE repeatable, red-capable command
  before any theorizing — a failing test, a curl script against the dev
  server, a CLI run diffed against a snapshot, a replayed captured
  payload: whichever the stack supports. Without it every "fact" about
  runtime behaviour is a guess. For flaky bugs the goal is not a clean
  repro but a *high enough reproduction rate to be debuggable* (≈1-in-2
  yes; 1-in-100 instrument to raise it first).
- **Look before you edit.** Time-to-first-edit distinguishes a thrashing
  session from a working one: editing seconds after reading the error is
  the signature of guessing; minutes of observation before the first
  edit is the signature of understanding. Runtime state gets OBSERVED,
  never inferred from reading code — code shows what *can* happen; only
  a run shows what *did*.
- **After three fixes that didn't take, the model is wrong, not the
  code.** Stop and ask for fix #4: re-classify from stage 1, question
  the architecture with the user, or take a fresh look — repeating the
  same loop harder is how hours vanish.

## The loop, stage by stage

Full prose for each stage — the class table and its first moves, the
question set, the evidence order, the fix rules, the close-out checklist:
[`references/loop-stages.md`](references/loop-stages.md).

1. **Understand & classify** — one sentence: expected vs actual, under what conditions.
2. **Ask** — only path-changing questions, maximum one round, then go.
3. **Gather evidence before touching anything** — "what touched it last?"
4. **Duck-debug, then hypothesize** — a falsifiable, discriminating causal claim.
5. **Find the first invalid state** — earliest divergence, not the crash site.
6. **Design the fix** — root cause, source of truth, minimal but complete.
7. **Apply, test, verify** — failing test first; a new symptom is a new iteration.

## Duck debugging — say the traceback out loud

The cheapest experiment in existence, and the mind-opener this skill
starts with: **narrate the whole chain of calls in plain words, out loud
(or typed), as if explaining the traceback to someone else** — from entry
to failure, one frame at a time. Speaking forces the implicit model
explicit; the sentence that stalls mid-way ("and here it should… um")
marks the bug's neighborhood. The technique predates the duck joke —
Hunt & Thomas described it in *The Pragmatic Programmer* (explaining
expected-vs-actual to a deliberately unresponsive listener), Agans
codified it as "Get a Fresh View" — and the measured benefit comes from
the **forced self-explanation**, not from the listener: as the agent,
produce the narration as visible text, never merely think it — a silent
pass is a weaker channel than an uttered one.

The protocol — explanation, not naming:

- State the expected result *before* explaining, so actual-vs-expected
  diverges out loud at each hop.
- **Say why each step follows from the previous** and trace how the
  value moves *between* frames — naming every function can masquerade
  as understanding it.
- Do not skip the parts you feel sure about; the unexamined "obvious"
  hop is where the bug most often hides.
- Two full unproductive passes → stop explaining. Verbalization serves
  step-by-step logic defects; a wrong *frame* of the problem needs a
  fresh view (break, another agent, the user), not pass three.

For a pasted traceback, segment the frames before reading them:

```
top frames     = the reporter — HOW the invalid state finally blew up.
                 Shows how, rarely why.
first app frame above the library/stdlib noise = where YOUR code handed
                 a bad state to the machinery. Start backward here.
bottom frames  = entry/boot/routing — confirm the path taken, move on.
```

A trace of ONLY library frames is itself a verdict: your code handed the
library invalid input — hunt it at that call boundary, not inside the
dependency. And the raising frame is the *surfacing* site, not the
*repair* site: the fix belongs at the offending caller or the input
boundary — wrapping the raise line in a try/catch hides evidence, it
resolves nothing.

Per hop, answer four things aloud: what enters here exactly (type, shape,
constraints)? what transformations and side effects (cache, writes,
calls)? what must leave? what assumption am I making about
environment/global/concurrency? The divergence between "what must be
true" and "what is true" *is* the bug's address. Async boundaries sever
the stack — there, correlation IDs replace call frames
(`references/pipeline-model.md`).

## Ways to see — pick the observation, not a favorite

The channel catalogue — traceback + duck-debug, browser DevTools and its
Initiator chain, dev-only state endpoints, debug-mode boot, logs, gated
loggers, scratch scripts, isolated harnesses, debugger and OS-level
channels — each with its discipline, plus the black-box-first channel
rules: [`references/observation-channels.md`](references/observation-channels.md).

## The stances — non-negotiable

1. **Understand before solving.** Classify first; vague blast-radius
   problems need questions before digging.
2. **No fix without root cause.** A patch that hides the symptom while the
   defect remains is not a fix; fix the source of truth, not only the
   broken instance.
3. **Minimal ≠ incomplete.** Touch the least you can — then verify you
   judged "least" across every layer; make the bug structurally impossible.
4. **Every bug is a chance to test.** Reproduce the *actual* failure as a
   test, watch it fail, fix, watch it pass, keep it. Skipping is a stated
   decision, never an oversight (`references/regression-testing.md`).
5. **Controlled observation only.** Debug output goes through a gated,
   scoped facility; ad-hoc scripts live in `.debugging/tmp/` with a
   lifecycle; nothing ungated ships.
6. **Escalate honestly.** Blocked by a permission, credential, or
   platform-only UI? Never fake it: hand the user (1) what you cannot do,
   (2) why, (3) where to go, (4) the exact prepared statement/command in
   `.debugging/tmp/` to copy-paste, (5) what output to report back — then
   verify their action and continue.

## Ask the user — the only four gates

1. Vague/blast-radius problem → history questions **before** digging
   (stage 2).
2. Intensive verification (e2e suites, browser-automation setup, staging
   reseeds) → propose cost, get yes.
3. Promoting a scratch script to a permanent instrument → offer;
   borderline = user decides.
4. Blocked externally → the 5-point escalation, then resume.

## Artifacts — debugging must leave capability, not cruft

```
.debugging/            (target repo root, created on first real need)
├── tmp/          · this session's scratch scripts — empty at session end
├── instruments/  · promoted, generalized, reusable verify tools
└── bugs/         · significant investigation records (templates: assets/)
tests/            · regression tests born from real bugs (project's layout)
```

Promotion/deletion rules and the bug-record template:
`references/instrumentation.md` + `references/artifact-lifecycle.md`.
If the project keeps a procedure library (e.g. a **how-to-do** skill),
fold the *class-of-problem procedure* you just learned into it — dbug
records incidents, procedures belong there.

## Routing — load only what the bug needs

| Situation | Read |
|---|---|
| A stage in full: classify table, questions, evidence order, fix rules, close-out | `references/loop-stages.md` |
| Which observation channel answers this question, and its discipline | `references/observation-channels.md` |
| Hypothesis discipline, evidence bar, meta-debugging when stuck | `references/hypothesis-and-evidence.md` |
| Pipeline roles, directions, lineage, invariants, trace anatomy | `references/pipeline-model.md` |
| Which experiment next, what each costs, reproduction hierarchy | `references/escalation-ladder.md` |
| "Worked before" — bisect, bookends, diff windows | `references/git-forensics.md` |
| Named class: wrong data, timeout, queue/webhook, authz, CI-only… | `references/problem-playbooks.md` |
| Server / service / worker / env / module-resolution | `references/backend.md` + `references/env-and-resolution.md` |
| Database state, schema drift, migrations, locks, plans | `references/database.md` + `references/database-verification.md` + `assets/test-migration.sql` |
| Browser / client / framework state-vs-render | `references/frontend.md` |
| Unreproducible, intermittent, prod-only, races, growth | `references/production.md` |
| Adding debug logging, scratch scripts, artifact lifecycle | `references/instrumentation.md` + `references/artifact-lifecycle.md` |
| Turning a confirmed failure into a permanent test | `references/regression-testing.md` |
| Concrete harness / inspector implementations | `examples/` |
