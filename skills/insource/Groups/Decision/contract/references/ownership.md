# The ownership decision method

Principle sources (Amr's blog, 2026-11-12): *Responsibility Ownership in Software
Architecture* (https://alaamer12.github.io/amr-tech/blogs/responsibility-ownership/) and its
sister post *Layers in Software Architecture*
(https://alaamer12.github.io/amr-tech/blogs/layers-in-software-architecture/). The blog uses
**OOUs/OU**; this skill standardizes **OoU/AoU**, tightens "multiple designated layers" to
**all defined layers** (so "some of us" can never smuggle dual ownership back in), and bans
the blog's generic sample filename `retry.md` in favor of scenario names. Where blog and this
skill differ, this skill is the newer decision.

## What counts as a layer here

Contracts address **explicit layers** — distinct runtime parts of the system (frontend,
backend, database) with real request paths through them. A project's *implicit* layers
(primitives → UI → components → features → pages inside one runtime tier) are a code-
organization discipline, not contract units: don't put "Features" in the Layers index next to
"Backend". Extra explicit layers (cache, message queue, edge) do belong in the index when the
architecture genuinely has them, numbered onward from 2.

## The question is never "where does X live?" but "who is RESPONSIBLE for X?"

A layer "having" some code is not ownership. Ownership means: when the requirement changes,
this is the layer whose files must change, whose tests guard it, and whose contract it breaks.

## Walk the axes, per layer

For the responsibility in question, consider each defined layer against:

- **Maintainability** — where does a change arrive first when business rules shift?
- **User experience** — what does the person paying for actually feel (latency, instant feedback)?
- **Security** — what data exposure does each option imply? This axis can veto, others adjust.
- **Performance** — native/infra capabilities vs application-side flexibility.
- **Scalability** — can the owner scale the responsibility without touching others?
- **Flexibility** — how fast can the decision itself be revised later?
- **Development complexity** — what machinery does each option drag in (migrations, syncing, duplicated code)?

Not every axis participates in every decision. The Reason must name the two or three that
actually moved the needle, and honestly name the price paid on the axis given up. "Backend
because backend" is not a reason; that is the default pretending to be a decision.

## Worked walk: filtering (the canonical example)

| option | gains | pays |
|---|---|---|
| **Database (0)** | native filtering, minimal application-side code | scaling/adjusting with business rules gets hard; SQL-specific logic adds migration overhead |
| **Backend (1)** | central, balanced for security + maintainability, evolves freely | not the fastest path; the app-side does the work |
| **Frontend (2)** | best UX — load once, filter locally, no round trips | the dataset is now client-visible; wrong data here is a leak, not a bug |

There is no winner. The answer depends on the *specific* filtering responsibility: auth-sensitive
catalog search → Backend. Performance-critical browsing of an already-authorized dataset →
Frontend, as an explicit contract exception with a safety condition ("only when the dataset is
safe to expose"). Same word, different responsibility, different owner, separate files.

## Worked walk: retry (the runaway-attempts example)

Both frontend and backend *can* retry. If each independently retries three times, a single
user action can produce up to **nine** backend attempts — 3 × 3 multiplication of load,
duplicated work, and a retry UI lying about what is happening. This is the canonical damage
of unowned responsibility: not two places doing one job badly, but two owners each doing it
*correctly* and producing a system behavior nobody designed. The split is the lesson:
automatic retry of transient failures belongs to the layer that knows what failed (Backend),
the manual retry affordance belongs to the layer that owns the experience (Frontend), each
explicitly conditioned on the other's policy being exhausted — two contracts,
`automatic_retry.md` and `manual_retry.md`, each referencing the other. See
`examples/contract-set/` for both.

## Choosing OoU vs AoU

- **OoU** when one layer can hold the whole responsibility including its failures. Format
  validation that must exist in both places "for safety" is not AoU — it is usually two
  contracts (input acceptance vs display normalization) with different owners.
- **AoU** when the responsibility is genuinely a protocol every layer implements against a
  shared definition: e.g. *timestamp representation* (every layer stores/sends/displays to the
  same rule). AoU means the rule is stated once and every layer owns its adherence, not that
  nobody owns the rule.
- If you find yourself writing "mostly X, but sometimes Y" — stop. That is either one contract
  plus a narrower exception contract, or an AoU stated honestly. Dual ownership inside a single
  declaration is illegal by design.

## When ownership changes

Update the contract's Ownership **and** Reason (the new reason *is* the audit trail), then the
index summary if it describes the owner. If an existing contract still holds as the default
and the change is a scenario, it should be a new file with `References` to the old one — not a
rewrite of it. Contracts are micro-ADR-shaped: decisions age in place or gain exceptions, they
do not get quietly edited into different decisions.