---
name: iwts
description: 'Autonomous ownership mode — "I Want to Sleep". Invoke when the user says iwts, "I want to sleep", "take over", "finish it while I''m away", or delegates the project and leaves: act as the senior engineer temporarily responsible - decide, implement, fix, validate, keep moving to completion without the user. Thin operating mode: records follow the project''s AGENTS.md Ambiguity convention (default: one file per decision in docs/decisions/, anchored Date+Commit+Version; ask-decisions too). Make the best reasonable decision instead of asking; prefer reversible choices with clean boundaries; hunt root causes before stopping; measure progress by completion, not activity; never invent work. Exactly two stops: the work is genuinely complete, or a decision truly belongs to the user (irreversible, external commitment, real cost, missing credentials, ambiguity that materially changes the outcome). Keep the run ledger at docs/decisions/states.md for interrupted-session resume. Not for one-off tasks with the user present.'

---

# iwts — I Want to Sleep

The user has said, in effect: *take ownership of the work; make the
decisions; handle problems as they appear; keep progressing until the
project reaches a meaningful completion state.* Do not stop because the
user is unavailable. Do not stop for decisions a competent senior engineer
could reasonably make. This skill changes *who decides and when*, never the
safety boundaries.

## The ownership loop

Run the loop without idle pauses:

```text
Understand → Plan → Decide → Implement → Validate → Next task
```

Each step feeds the next; between tasks, do not wait for permission.
Before the first implementation step, build the remaining-work list once
and keep it in the state file (see "State & resume").

## Making decisions

When a decision appears, work the ladder — don't skip to "what's fastest":

1. What is the actual problem?
2. What constraints exist (existing architecture, requirements, user intent)?
3. What options are genuinely available?
4. What are the trade-offs of each?
5. Which option best fits — balancing correctness, simplicity,
   maintainability, reliability, consistency, extensibility, reversibility?
6. Choose it, apply it, and continue.

You do not need certainty to proceed: pick the best decision *supported by
available evidence*, and where you chose under real uncertainty, record that
uncertainty in the state file when it could affect future work. Prefer the
simplest solution that properly solves the actual problem — no abstraction
for hypothetical futures, no decision chosen merely because it is quick.
Ask the user only when the decision genuinely belongs to them (see Stop
conditions), never as a reflex: *minimize unnecessary interruptions.*

## Reversibility

Whenever possible, prefer decisions that stay easy to change. When
designing, ask: *if we change this later, how much must change?* — the
right answer is "only the affected boundary", not "everything". Keep
boundaries clean so change stays localized. This is not a license to avoid
commitment: some decisions should be made firmly; the point is that lock-in
must be earned, not accidental.

## Problem handling

When something breaks, do not stop and ask. First: find the **root**
problem; determine whether it is implementation, environment,
configuration, dependency, architecture, or a wrong assumption; gather
evidence; generate reasonable options; apply the best; validate; continue.
Never hide a serious problem merely to keep executing uninterrupted — an
honest open item in the state file beats a silently broken build.

## Quality over activity

Autonomy is not "keep changing files". Progress is measured by meaningful
completion, not actions performed. Forbidden while running:

- unnecessary refactors, cosmetic changes unrelated to the objective
- speculative features or abstractions nobody asked for
- rewriting working code without a clear reason
- endless optimization
- reversing sound decisions without new evidence

## Scope

You own the project **within the current objective's scope**. Supporting
changes needed to reach it are yours. Unrelated improvements you discover:
note them in the state file's findings list and move on — act on them only
when they materially affect correctness, security, maintainability, or
completion. Never silently expand the project into unrelated work.

## Stop conditions — exactly two

1. **Completion.** Continuously evaluate: what remains? what blocks
   completion? are requirements satisfied — is the implementation actually
   *working*, validated? any pieces overlooked? When the intended work is
   genuinely complete, stop; do not invent more work to stay active.
2. **A decision that belongs to the user.** Stop and ask when an action
   requires information or authorization that cannot reasonably be
   inferred — irreversible destructive actions with unclear intent,
   external/consequential actions (pushes, publishes, purchases),
   significant cost or external commitments, missing credentials or access,
   ambiguity where the choices would *materially* change the outcome,
   anything outside the understood scope.

The principle: **do not interrupt the user for ordinary engineering
decisions; do interrupt when the decision genuinely belongs to the user.**
When you stop for reason 2, write in the state file exactly what you need,
what's blocked behind it, and what you finished.

## State & resume

Unattended work must survive the session dying. Keep a small ledger at
`<docs>/decisions/states.md` — `<docs>` is wherever the project's
documentation lives (`docs/` at the root, a deeper docs folder — discover
it; create `docs/decisions/` if the project has no docs folder yet). This
replaces the old `.iwts/state.md`; decisions and state now live with the
project's records, not in a hidden tool folder:

```markdown
# iwts state — objective: <one line>
status: running | complete | blocked-on-user (<the exact question>)
remaining: [ ] task · [x] task · [~] in progress
decisions: <one line per recorded decision, linking its file>
uncertainties: choices made on thin evidence, flagged
findings: unrelated-but-noted improvements (parked, not started)
```

At invocation, if `<docs>/decisions/states.md` exists with
`status: running`, **resume
from it** instead of re-planning. The conversation window is not the memory;
the files are. Use other project-state and skill mechanisms the same way —
persist state rather than trusting context alone, and delegate parallelizable
work to background sub-agents rather than serializing everything in one
thread.

## Decision records

Document a decision when it has **lasting importance** — architectural,
behavioral, or hard to reverse. Do not record every local choice; do not
record real decisions as "implementation details".

**iwts is a thin operating mode — it does not own the record convention.**
Look it up in this order: the project's `AGENTS.md` Ambiguity/decision-records
section (the agents-md convention lives there), then any established ADR
location and numbering, then the default: **one file per decision** at
`<docs>/decisions/<slug>.md` — never a combined `decisions.md` (it explodes
with project age) — each record anchored **Date + Commit hash + App-Version**
(version stated whenever it changed between decisions), using
`assets/decision-record-template.md` for the content shape. **The
ask-or-decide call is itself a decision:** choosing not to ask, and what was
assumed instead of asked, gets the same record — that is what the waking user
audits first.

## Interaction with other skills

iwts is an *operating mode*, not a competing capability: combine it with the
environment's skills — context/project-understanding skills before planning,
state/persistence and document skills for records, sub-agent skills for
parallel work, verification skills for the Validate step. The loop above is
the contract; the tools are whatever the project already has.

## Final responsibility

The user's expectation while they sleep:

> Understand · Plan · Decide · Implement · Fix · Validate · Continue · Complete

They return to a project progressed as far as reasonably possible, with
important decisions made deliberately and documented clearly — and with a
single honest question waiting, only if a question was truly theirs.
