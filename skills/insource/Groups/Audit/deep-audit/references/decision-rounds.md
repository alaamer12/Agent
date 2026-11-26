# Decision rounds — asking the owner without drowning them

Census findings split into two kinds: **mechanical** (a move, a correction, a merge — the corpus
already decides) and **weight-bearing** (only the owner decides). Weight-bearing items become the
plan's decision log — and they are asked BEFORE the plan is written, never smuggled into it.

## Classify as weight-bearing when ANY holds

- Choosing changes product behavior, security posture, data shape, or identity of anything.
- The answer is irreversible or expensive to reverse (schema scale, currency identity, public
  naming, deletion of a feature concept).
- Two defect findings conflict and neither reading is clearly the living authority.
- The corpus contains a consensus NOBODY recorded (class 5) — consensus is not consent.

Everything else is the agent's to decide and record: formatting, pointer conversion, stale-marker
cleanup, moving content to its taxonomy home when the home exists.

## Round structure

- **R1 — blocking:** the questions the plan cannot be authored without (destinations depend on
  answers). ≤4 questions per tool call. If R1's answers spawn new blocking forks, run R1b —
  never guess forward.
- **R2 — consequence:** answers that shape execution details, asked after the destination
  structure is decided.
- **R3 — deferred:** everything else. Goes in the plan's open-questions list with what blocks it,
  lands in the project's ledger — NOT asked now.

## Question anatomy (every question carries all five)

1. **Title:** a few words naming the decision.
2. **Description:** what is being decided, why it matters, what it unblocks downstream — written so
   someone who skipped the whole census can answer correctly.
3. **Options:** 2–4, mutually exclusive, each with concrete pros/cons — the recommended one first
   labeled "(Recommended)".
4. **Why this recommendation:** one or two sentences tied to goals the owner already stated.
5. **Evidence pointers:** the contradicting file:lines quoted in the description, so the owner
   decides from the artifacts, not from the agent's summary of them.

## When options are not the right shape

Some answers are sentences, not choices (an exact scale factor, a charset rule, a policy clause).
Ask them open-ended in the same round. A wrong guess recorded as an option list is worse than an
open question — options imply the space is known.

## The answer's lifecycle

Owner answers arrive → recorded as dated decisions in the project's decision home (settled ledger
with kind: explicit/implicit and provisional flags while drafting) → the plan's decision log cites
them → the correction wave updates every artifact that disagreed with them → falsified prior beliefs
go into the project's verified-facts list so nobody re-learns them.

A revision of a previously recorded decision is labeled as a revision (numbered row, reason, date),
never a silent overwrite — history is how drift gets diagnosed later.

## Refusals and deferrals are answers too

If the owner says "keep it simple", "as we were", or skips a question: record what was NOT decided,
leave the structured `Pending (Drafting)` marker honest, and design around it. deep-audit never treats a
deferral as consent to invent.