# The loop, stage by stage

The seven stages of the dbug loop in full — what each stage produces and
what it must not skip, plus the close-out checklist that ends a run. The
rails and the stage spine stay in [`../SKILL.md`](../SKILL.md); open this
when you are inside a stage.

1. **Understand & classify.** Restate the problem in one sentence:
   *expected behaviour vs actual behaviour, under what conditions.* If you
   cannot write that sentence, you do not understand yet — that is the
   point of the stage. Classify; the class sets the path:

   | Class | Signal | First move |
   |---|---|---|
   | Concrete artifact mismatch | two sources of truth disagree (schema file vs live DB, spec vs code) | diff them directly — no questions needed |
   | Regression | "worked before / broke after a change" | git forensics → `git-forensics.md` |
   | Wrong/missing/duplicate data | values off, no crash | data-lineage trace → `pipeline-model.md` §lineage |
   | Failure at a point | error, trace, non-2xx, exception | duck-debug the trace (§Duck debugging, `../SKILL.md`), then trace backward |
   | Performance/resource | slow, timeout, OOM, grows over time | `production.md` — measure first, not code |
   | Non-reproducible | intermittent / prod-only / "sometimes" | `production.md` — characterize before touching anything |
   | Blast radius: "half the system broke" | everything at once | stop — ask the user first (§gates, `../SKILL.md`), never self-serve |

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
   created under control — see §Ways to see in `observation-channels.md`.

4. **Duck-debug, then hypothesize.** Say the problem out loud first
   (§Duck debugging, `../SKILL.md`) — then convert it into a falsifiable causal
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
   → minimal repro) live in `hypothesis-and-evidence.md`;
   which experiment costs what → `escalation-ladder.md`.

5. **Find the first invalid state.** The failure's location is almost
   never the defect's location. The target question: *where did actual
   state first diverge from expected?* — earliest point, not the crash
   site. Pipeline roles, directions (forward/backward/narrow/widen) and
   lineage tracing: `pipeline-model.md`.

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
   `regression-testing.md`. Verification sized to risk,
   cheapest sufficient. New symptom from verification → new iteration at
   stage 1; this is the loop, not a failure.

## Close-out checklist

- [ ] Regression test kept — or a stated reason it's not testable
- [ ] Source-of-truth artifacts fixed, not just runtime state
- [ ] Every layer the invalid data/state crossed is now guarded
- [ ] `.debugging/tmp/` triaged (promote/delete) — physically empty
- [ ] Bug record written when the path has lasting value
- [ ] Instrumentation gated-and-deliberate or removed
- [ ] Reusable procedure captured into the project's procedure system
