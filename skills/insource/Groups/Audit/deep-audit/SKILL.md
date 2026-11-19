---
name: deep-audit
version: 1.0.0
author: Amr
specialized: none
description: 'End-to-end self-consistency loop for a project whose artifacts disagree with themselves: fan out read-only census subagents over non-overlapping slices hunting a fixed defect taxonomy (boundary violations, contradictions, invented content, stale markers, terminology drift, duplicate homes), ask the owner the weight-bearing questions in blocking rounds, write the reconciliation plan, then execute it in dependency-ordered WAVES — one atomic commit per wave behind a verification gate, teammate-safe, deviations recorded — and finish with rulebook sync plus a completeness proof. One entry point; modes: census, plan, fix, verify. Use for "deep-audit", "find the contradictions", "reconcile the docs", "organize the waves of reconciling", or when scaffolds exist but content drifted. Discovery-only routes to crosscheck; proof-only to please-verify; orientation to exmaine — deep-audit REMEDIATES.'
when_to_use: The user wants a project's own corpus (docs, code, config, ledgers, prototypes) audited for internal inconsistency AND fixed in an organized, gated way. Also /deep-audit, "organize the waves of reconciling", or after a session that produced multiple agents' worth of drift.
argument-hint: "[census|plan|fix|verify] [scope] — bare invocation runs the full loop"
---

# deep-audit — find what disagrees, settle it, reconcile in waves

A corpus of artifacts written over time drifts: the same fact gets two homes with two values, a rule
gets asserted that nothing defines, a "pending" outlives its answer, terminology forks. deep-audit
turns that mess into a plan and executes the plan in gated waves, so nothing lands unverified and
nothing gets decided silently.

**One loop, five stages: census → synthesis → decision rounds → plan + approval → waves + sync.**
Every stage has a done-gate; the whole skill has a clean-empty exit — a corpus that is consistent
ships a report, not churn.

## Boundary with sibling skills

| The ask really is | Skill |
|---|---|
| Discover findings with blind orthogonal lenses, report only | `crosscheck` (deep-audit's census may dispatch through it when installed) |
| Prove whether work is complete/verified, fix nothing | `please-verify` |
| Orient an agent in an unfamiliar project | `exmaine` |
| Plan without auditing first | `planner` |
| Audit the corpus, settle owner decisions, reconcile with gates | **deep-audit** |

## Modes (one entry point)

| Mode | Does | Stops at |
|---|---|---|
| `census` | Fan out the read-only auditors, merge defect tables | The report. No edits, no plan. |
| `plan` | Census + decision rounds + written plan | Plan approval (ExitPlanMode). No edits. |
| `fix` | Execute an approved plan in waves | All waves + gates + sync committed. |
| `verify` | Re-run every gate + the falsified-string sweep | The completeness proof. No new edits. |
| bare | census → plan → approval → fix → verify, in one delegated run | Same as fix+verify, continuous. |

## Scale gating

- **Small corpus** (< ~30 files): skip the fan-out, sweep directly — agents cost more than they add.
- **Medium** (30–150): 2 census agents, slices by surface.
- **Large or multi-artifact** (docs + code + prototype + ledgers): 3 agents, slices by
  (1) tier/taxonomy boundaries, (2) one content domain deep-dive, (3) the surfaces the first two
  cannot see (ledgers, rulebook, ground-truth behavior). Never more than 3; merge overlaps yourself.

## Stage 1 — Census fan-out

Dispatch read-only subagents, each with a **non-overlapping slice** and the same contract
(brief template: [references/agent-briefs.md](references/agent-briefs.md)):

- Hunt the fixed defect classes ([references/defect-taxonomy.md](references/defect-taxonomy.md)) —
  every class with its signature and how to prove it.
- Cite file:line for every finding; no vibes.
- Output the inventory TABLE (location | class | destination | one-line reason) **inline** in the
  returned result — a read-only agent cannot write a file; briefs that demand one waste the run.
- List what is **FINE** so the plan never churns correct content.
- End every brief with the open-questions section: anything the agent could not decide from the
  corpus alone comes back as a QUESTION, never an assumption baked into a destination.

## Stage 2 — Synthesis

Merge the reports in the main agent, do not re-do them:

1. De-duplicate (two agents finding one defect = one row with two witnesses — that is consensus).
2. Count by class; order destinations by dependency (what must exist before something can move).
3. Separate **settled-from-corpus** (the answer is readable) from **owner-decisions** (it is not).
4. Draft the defect inventory the plan will carry. If census mode was asked, deliver and stop.

## Stage 3 — Decision rounds

Weight-bearing forks go to the owner before anything is written
([references/decision-rounds.md](references/decision-rounds.md)):

- Bundle the questions into rounds: **R1 blocking** (the plan cannot be authored without them),
  **R2 consequence** (executes after R1 exists), **R3 deferred** (log as open, do not ask now).
- Use the interactive ask tool when available, ≤4 questions per call; recommended option first,
  with its actual cost stated; each option carries what's at stake.
- Findings that need no owner (pure moves, stale corrections) are NOT questions — decide, record,
  proceed.

## Stage 4 — Plan + approval gate

Write the plan (template: [assets/plan-template.md](assets/plan-template.md)) through the harness
plan mode / plan file so it is reviewable. Requirements:

- **Context** section: why this surgery, what triggered it, intended outcome.
- **Decision log**: each owner answer as a row (question, answer, where it lands) — the plan's spine.
- **Phases = waves**, ordered by dependency, each with its exact deliverable paths and its gate.
- **Honest scope trims**: what is deliberately NOT touched and why (a deviation or deferral is
  stated, never silent).
- **Verification section**: the commands/adapter that prove the end state, including the
  falsified-string sweep ("what we killed must not survive").
- Exit the plan mode for approval; do not edit a single file before the owner approves.

## Stage 5 — Waves: execution discipline

The organizing unit is the **wave**: one dependency-level of the reconciliation, one atomic commit,
one gate. Full rules in [references/waves-and-gates.md](references/waves-and-gates.md); the
non-negotiables:

1. **Wave order by dependency, never by ease:** corrections → decisions recorded → area/structure
   creation → extraction batches → reconciliation sweep → new owning docs → lesson folding →
   rulebook/ledger sync → final verification.
2. **Gate every wave** with the project's verification adapter (a checker command, tests, lint —
   whatever the project defines; the skill does not hardcode one) before the next wave starts.
   Red gate = fix in the same wave, never queue a red state.
3. **One wave, one commit** — Conventional-Commits style, imperative mood, body records the WHY,
   the gate result, and any deviation from the plan with its reason. A deviation is legal only when
   it is written down.
4. **Teammate safety:** before each wave re-check the working tree; a dirty file you did not
   author belongs to another agent — re-read current state, keep edits additive, never revert or
   reformat their work, never stash.
5. **Ledger and rulebook sync in the last waves:** decisions that changed the corpus get recorded
   where the project records decisions; rulebook/index/description lines that describe moved or
   rewritten content are updated in the same wave (a half-described file is a half-moved file);
   duplicate homes collapse to one owner + pointers.
6. **Completeness proof at the end** (verify mode): orphan/link gates pass, defect inventory
   closed item-by-item or explicitly deferred, and the falsified-string sweep returns only
   deliberate history. "Nothing stale, right?" is answered by running the sweep, never by
   remembering what was touched.

## Clean-empty exit

If the census finds no defect classes (rare but possible), deliver the report with the stats, say
so plainly, and change nothing. A deep-audit whose output is "consistent, verified, no edits" is a
complete run — not a failed one.

## Resources

| File | Load when |
|---|---|
| [references/defect-taxonomy.md](references/defect-taxonomy.md) | Writing census briefs or classifying findings |
| [references/agent-briefs.md](references/agent-briefs.md) | Dispatching the subagents |
| [references/decision-rounds.md](references/decision-rounds.md) | Building the ask-tool rounds |
| [assets/plan-template.md](assets/plan-template.md) | Writing the plan file |
| [references/waves-and-gates.md](references/waves-and-gates.md) | Executing; before each wave |