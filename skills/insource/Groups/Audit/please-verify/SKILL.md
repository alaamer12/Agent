---
name: please-verify
description: 'Broad verification of a project or delivered body of work - not just the last step - answering one question: is the work actually complete and sufficiently verified? Starts from the user''s ask (conversation, IDEA.md, plan, AGENTS.md), never from the agent''s own summary, and sweeps requirements, completeness, bugs, rule violations, consistency, missing work, proof of work, integration and project-level correctness. The evidence ladder is the rule: files existing is not proof, ''it should work'' is not proof - a build log, a test run with output, a launched app with observed behavior are proof; unproven is UNVERIFIED, never PASS. Catches the classic failure: files delivered and called ''done'' without ever building or running them. Read-only: runs builds, tests and the app for evidence, then reports COMPLETE & VERIFIED / INCOMPLETE / UNVERIFIED / BROKEN with an evidence table, blockers and ordered next actions - it does not fix. Triggers: ''please verify'', ''is this actually done'', ''did we finish'', ''prove it works''.'
when_to_use: The user asks whether work is really complete, wants a broad project-level verification or a proof-of-work check, or a delivery claims to be finished and the claim needs testing against the original expectations. Also /please-verify.
argument-hint: "[the project path, or the scope to verify]"
---

# please-verify — is it actually done, and proven?

Verification is not reading the code and nodding. It is **comparing the delivered work against what the
user expected, and demanding evidence for every claim**. The question this skill answers is exactly one:

> Is the work actually complete and sufficiently verified?

It is deliberately broader than checking the most recent step. A project can have every file, every test
green, and still fail this question - because nobody ever built it, ran it, or watched the expected
behavior happen.

## What gets verified

| Area | The question inside the area |
|---|---|
| **Requirements** | Does every thing the user asked for exist, and do this project's own docs (IDEA.md, plan, AGENTS.md) agree? |
| **Implementation completeness** | Are there stubs, `TODO`s, unimplemented branches, placeholder values, dead routes, empty handlers? |
| **Bugs and issues** | Do builds, type checks, linters and tests actually pass - with output, not with claims? |
| **Violations** | Does the work break the project's own rules (AGENTS.md, stack conventions, license, privacy policy)? |
| **Consistency** | Do naming, patterns, configs and docs agree with each other, or does the same thing exist three ways? |
| **Missing work** | What does "done" require that nobody produced - tests, migrations, docs, config, assets, error paths? |
| **Proof of work** | For every claim, is there evidence from this delivery - command output, logs, reports, artifacts? |
| **Integration behavior** | Do the pieces actually connect and run end to end? Does the app start? Does the flow complete? |
| **Project-level correctness** | Does the result satisfy the definition of done the user had in mind - not a weaker one the code created? |

The full checklists per area: `references/03-sweep-areas.md`.

## Step 0 — establish the expectation baseline (never skip)

Without the expectation there is nothing to verify. Before looking at any code:

1. **Collect what the user asked for** - the conversation, IDEA.md, a plan/spec doc, AGENTS.md's obligations.
2. **Turn it into explicit, observable outcomes** - "a full working app" becomes a checklist: the app
   builds; it launches; screen X does Y; data survives a restart; the failing case shows the promised
   message. "It exists" is not an outcome.
3. **Record what is ambiguous or unstated** - verify the stated, list the unstated as open, never invent
   requirements to pass or fail against.
4. **Write down the definition of done** you will verify against, in chat, before sweeping - so the verdict
   is checkable and the user can correct the bar.

How to build the baseline, including broad requests and doc-vs-conversation conflicts:
`references/01-expectation-baseline.md`.

## The evidence ladder — the core rule

Every claim gets a level, and the verdict may not exceed the weakest deciding claim:

| Level | Meaning |
|---|---|
| **L0 — exists** | The file/function/route is there. Proof that something was typed, not that it works. |
| **L1 — compiles / type-checks** | The project's own build and type checks ran and passed, with output. |
| **L2 — tests pass** | The suite ran in this verification (or its genuine report is attached), with output. Green tests still only prove what the tests assert. |
| **L3 — runs / integrates** | The app or service was actually started and the integration path executed: boot logs, smoke request, end-to-end flow. |
| **L4 — observed expected behavior** | A human- or agent-observable outcome matched the baseline: the screen renders, the export opens, the error message appears. |

- **Code you read but never ran is L0-L1 at best.** Label the verdict accordingly, and say "static review
  only" when that is all that happened.
- **Missing proof is UNVERIFIED - not PASS and not FAIL.** "Could not run because <reason>" is the honest
  label, and it stays in the verdict.
- The most common false PASS is **green tests over an app that never starts**: L2 without L3 is not a
  working app.

The ladder in depth - what counts as evidence, how to capture it, what may be run safely:
`references/02-evidence-ladder.md`.

## The verdict

One of four, for the whole scope and, where the scope divides, per requirement group:

```
VERDICT: COMPLETE & VERIFIED | INCOMPLETE | UNVERIFIED | BROKEN
```

- **COMPLETE & VERIFIED** - every baseline item is delivered and has evidence at the level its nature
  requires (an API endpoint needs L3; a UI promise needs L4).
- **INCOMPLETE** - baseline items are missing or partial; name them.
- **UNVERIFIED** - the work may exist, but the evidence does not; this is the default when builds/tests/app
  were never actually run, and it is a legitimate, honest verdict.
- **BROKEN** - evidence exists and shows failure: build fails, app crashes, the promised behavior is absent.

Deliver it with an evidence table - requirement, artifact, proof level, status - plus blockers, missing
proofs, risks and ordered next actions. Format: `assets/templates/verification-report.md`. Verbose
narrative is not the deliverable; the table is.

## Rules of the audit

- **Verify the expectation, not the summary.** The agent's own description of what it did is a claim, not
  evidence. Confront each claim with an artifact.
- **Broad first, then the recent step.** Sweep the whole scope the user cares about; only then look at what
  changed last.
- **Never fabricate evidence.** No invented test output, no "should pass", no green check without a run.
  A label of UNVERIFIED is always better than a false PASS.
- **Read-only by default.** Running builds, tests and the app is part of verification; editing code to make
  something pass is not. If a fix is obvious, report it and hand off - this skill produces the verdict, not
  the repair.
- **Time-box the sweep** and say what was not reached: "verified A and B; C left unverified because X" is
  a valid, useful result.
- **Scope stays where the user put it.** The whole project means the whole project; "the exported CSV"
  means the exported CSV - do not turn either into an unbounded rewrite review.

## Boundaries

| Not this | Go instead |
|---|---|
| Verifying one recent change / PR before pushing | `verify` (the change-level skill) |
| Writing or repairing tests | `test` |
| Behavior stories and their coverage design | `stories` |
| Performance numbers | `benchmark` |
| Deciding between approaches | `thebest` |
| Documenting anti-patterns as a living catalog | `antipattern` |
| Independent multi-agent cross-checking of findings | `crosscheck` |
| Fixing what the audit finds | `implement`, the relevant skill, or the user's call |

## Files

| Need | Load |
|---|---|
| Building the expectation baseline from a broad or messy ask | `references/01-expectation-baseline.md` |
| The evidence ladder: what counts, how to capture it, safe execution | `references/02-evidence-ladder.md` |
| The ten sweep areas, with concrete checks per area | `references/03-sweep-areas.md` |
| The report format: verdict, evidence table, blockers, next actions | `assets/templates/verification-report.md` |
| A worked audit: "full working app" that was never built or run | `examples/full-app-never-ran.md` |
