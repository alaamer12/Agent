---
name: dbug
version: 1.0.1
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

This file holds the loop, the stances, and how to *see*. Everything deeper
lives in `references/` — read only what the current bug needs (routing
table at the bottom). Never "guess → change code → run → hope": that loop
skips Understand and Hypothesis; if you catch yourself in it, stop and
re-enter at stage 1.

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

1. **Understand & classify.** Restate the problem in one sentence:
   *expected behaviour vs actual behaviour, under what conditions.* If you
   cannot write that sentence, you do not understand yet — that is the
   point of the stage. Classify; the class sets the path:

   | Class | Signal | First move |
   |---|---|---|
   | Concrete artifact mismatch | two sources of truth disagree (schema file vs live DB, spec vs code) | diff them directly — no questions needed |
   | Regression | "worked before / broke after a change" | git forensics → `references/git-forensics.md` |
   | Wrong/missing/duplicate data | values off, no crash | data-lineage trace → `references/pipeline-model.md` §lineage |
   | Failure at a point | error, trace, non-2xx, exception | duck-debug the trace (§below), then trace backward |
   | Performance/resource | slow, timeout, OOM, grows over time | `references/production.md` — measure first, not code |
   | Non-reproducible | intermittent / prod-only / "sometimes" | `references/production.md` — characterize before touching anything |
   | Blast radius: "half the system broke" | everything at once | stop — ask the user first (§gates), never self-serve |

   A bug can hold two classes (regression *and* prod-only) — take the
   cheap part of both paths.

2. **Ask — only path-changing questions** (skip for concrete-mismatch,
   evidence is in hand): was this working before, how do you know? working
   in Git, roughly how many commits ago, which branch? what changed just
   before — deploy, migration, dependency bump, config edit? anywhere it
   still works (staging, another machine, another account)? Maximum one
   round; then investigate with whatever came back.

3. **Gather evidence before touching anything.** Reading what exists is
   free: exact error text and traceback verbatim (the trace is read
   first, word-for-word, never skipped or paraphrased — it is the
   cheapest observation channel that exists), logs, recent commits and
   diffs, the files the error names, tests on the path, past bug records
   (`.debugging/bugs/`, project docs — someone may have met this before).
   The default first move is **"what touched it last?"** — working
   systems keep working until something acts on them, so correlate onset
   with deploys, migrations, dependency bumps, config/data/traffic
   changes and diff that window before theorizing anything else.
   Characterize: expected X / actual Y / repro rate (always | 1-in-M |
   once) / conditions (env, data, user, since when). New evidence gets
   created under control — see §Ways to see.

4. **Duck-debug, then hypothesize.** Say the problem out loud first
   (§Duck debugging below) — then convert it into a falsifiable causal
   claim, "because \<A\>, we see \<B\>", with a prediction that can
   *refute* it, and run the cheapest experiment that distinguishes your
   top two hypotheses. The prediction must **discriminate**: whichever
   way the result lands it should rule one group of hypotheses in and
   another out — an experiment that can only "confirm" tests nothing.
   Hypotheses are **cumulative**: a new one must absorb every satisfied
   prediction, exclude every refuted one, and explain *all* the
   observations including the noise — one unexplained fact demotes a
   root cause to a suspect. Change one variable at a time so the next
   run attributes honestly, and keep an **audit trail** as you go
   (hypothesis → prediction → test → result): refuted regions never get
   re-explored, and every mutation you made to the system stays
   undoable to its pre-test state. Loop discipline and the evidence bar
   (anecdote → code-reading → telemetry → captured first-invalid-state
   → minimal repro) live in `references/hypothesis-and-evidence.md`;
   which experiment costs what → `references/escalation-ladder.md`.

5. **Find the first invalid state.** The failure's location is almost
   never the defect's location. The target question: *where did actual
   state first diverge from expected?* — earliest point, not the crash
   site. Pipeline roles, directions (forward/backward/narrow/widen) and
   lineage tracing: `references/pipeline-model.md`.

6. **Design the fix: root cause, minimal, complete.** You have the cause
   when you can state the chain `symptom ← immediate failure ← local
   cause ← … ← root defect` and know that fixing the root removes the
   failure while anything below it would not. Three rules: fix the
   **source of truth** artifacts too (schema files, codegen inputs,
   configs, seeds — live-state-only repairs re-break on next recreate);
   **minimal ≠ incomplete** — scope what you touch, but check necessity
   across *every layer the invalid data/state passes through*; make the
   bug **structurally impossible** (constraint in the store, type in the
   model, guard at the entry, assertion at the boundary — whichever
   layers exist). One fix at a time.

7. **Apply, test, verify.** Testable bug → failing regression test first
   (red for the *right reason*), fix, green, keep it forever —
   `references/regression-testing.md`. Verification sized to risk,
   cheapest sufficient. New symptom from verification → new iteration at
   stage 1; this is the loop, not a failure.

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

Same loop, every stack; what changes is only how you look. In
cheapest-first order (ladder with costs: `references/escalation-ladder.md`):

| Way to see | Use for | Discipline |
|---|---|---|
| Error/traceback verbatim + duck-debug it | where and how it broke | capture word-for-word, never paraphrase |
| Browser console & DevTools (Sources, Network + **Initiator chain** = the network edition of a call stack, Watch/Call Stack/Scope panels, Request Blocking as ablation, storage) | client-side failures, what the UI received | arm the Network panel BEFORE reproducing — it records only while open; normalize repeats with empty-cache hard reload; prefer evaluating in page context over editing source → `references/frontend.md` |
| **Dev-only debug page/endpoint** returning JSON of live state (config, cache, pool stats, session, flags) — the Go `net/http/pprof` genre, self-describing index included | "what does the server actually BELIEVE right now?" | read its index first to discover what is observable instead of guessing names; some data is empty until the runtime opts in — **no data ≠ no problem**; gated to non-prod, no secrets, keep-or-delete deliberately → `references/instrumentation.md` |
| **Debug-mode app boot** — a registered entry point (flag, `debug`-style command, env switch, deep link) that skips human gates, opens a named page directly, freezes interact-to-change state, or seeds fixture data | sessions that burn tokens reproducing navigation instead of observing the bug | use only what the project's rulebook registers — an unlisted instrument does not exist; when gates dominate and none is registered, propose engineering a gated one, dead in production → `references/instrumentation.md` §Debugging engineering |
| Existing logs/metrics/traces | what happened over time | filter to failing request/correlation IDs only; aggregates (SLO, p99) characterize the symptom — per-request evidence locates the cause |
| Scoped gated logger — verbosity hot-switchable without restart where the platform offers it | is state correct *at this hop* | dev-only by construction, addressable per module; tag every temporary print with a unique token (`[DEBUG-a4f2]`) so cleanup is one grep → `references/instrumentation.md` |
| Scratch script in `.debugging/tmp/` (exit 0/1) | question the DB/env/service directly | deterministic verdict, redacted output, self-cleaning |
| Isolated harness — call the suspect function with controlled inputs | our code vs its callers vs its dependencies | → `references/backend.md`, `examples/isolated-harness-polyglot.md` |
| Debugger channels: breakpoints; **tracepoints** (breakpoint that logs and keeps running); conditional & hit-count breakpoints; **data breakpoints** (write-watch — answers "when did this change?"); race detectors; profilers | exact values at a point; reaching a rare loop iteration; mutation timing; resource causality | prefer the non-perturbing variants first — breakpoints and chatty logs shift timing and can make a timing bug vanish; a *broken* condition expression still breaks — never read that as confirmation → `references/escalation-ladder.md` |
| OS/tool-level structured reports: live-process stack dumps, serialized crash reports (stack+registers+disassembly as machine-readable JSON), time-travel/replay recordings, allocation tags | when app channels are blind to the truth | demand/parse them from users and CI artifacts too — structured external reports have localized bugs before any maintainer repro existed |

**Channel rules** (what separates a fast session from a thrashing one):
establish the **black-box symptom first** (reproduce and probe from
outside, as a user sees it), then go white-box for causes; **read the
same boundary from both sides** — caller's view AND callee's view, one
vantage point cannot discriminate two hypotheses; if no existing
channel shows what you suspect, **create one** (tag the subsystem's
allocations/so that existing tools see it separately); for performance
defects **measure before fixing** — attribute time to a hop, never
optimize a guess.

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

## Close-out checklist

- [ ] Regression test kept — or a stated reason it's not testable
- [ ] Source-of-truth artifacts fixed, not just runtime state
- [ ] Every layer the invalid data/state crossed is now guarded
- [ ] `.debugging/tmp/` triaged (promote/delete) — physically empty
- [ ] Bug record written when the path has lasting value
- [ ] Instrumentation gated-and-deliberate or removed
- [ ] Reusable procedure captured into the project's procedure system

## Routing — load only what the bug needs

| Situation | Read |
|---|---|
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
