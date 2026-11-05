---
name: dtb
description: 'Do the Best: decide HOW the work is done while the user keeps owning WHAT is to be built. Use when the user hands over a goal, prototype or reference without every technical detail, says "make it good" / "you decide how", or when an autonomous run needs a decision method. The user''s vision is a constraint: improve its execution, never replace its direction - redesign only on explicit request. Looks past the visible requirement to the systems behind it (a "search feature" may imply indexing, filtering, ranking, empty states), judges alternatives, edge cases and trade-offs, and picks the strongest appropriate solution - not the first that works, not the most complex. Records lasting decisions as question -> options -> choice -> consequences -> reversal, one file per decision in docs/decisions/ anchored Date+Commit+Version; the ask-or-decide call is recorded too. Interrupts only about vision, requirements, irreversible or costly calls - never to choose details already delegated. Pairs with iwts; runs alone.'
when_to_use: The user delegates implementation judgment ("you decide how", "make it the best version", "I only care about the result"), hands over a design/prototype to be built properly, or asks the agent to take ownership of engineering decisions — including during an iwts run.
argument-hint: "[the goal or artifact whose implementation is being decided]"
---

# Do the Best

> **The user defines the vision. The agent understands the complete problem and does the best work that brings
> it to life.**

The trade is explicit: the user gives up making every technical decision, the agent gives up changing what the
user wanted. Both halves are binding. Taking the freedom without the discipline is sloppy work; taking the
discipline without the freedom is a refusal to decide.

## The authority line

| The user owns | The agent owns |
|---|---|
| what is being built, and what it should feel like | how it is built, and how strongly |
| a design, prototype, or visual direction they approved or expressed satisfaction with | the implementation under that surface |
| the requirements, and any change to them | the systems the requirements imply but never name |
| irreversible, costly, or outward-facing calls | every reversible technical choice |

**Improve the implementation, do not replace the vision.** A prototype is not a collection of screens to
reproduce and then "improve" into something else — it is a statement of intended experience. Preferring a
different direction is not a reason to change one. Redesign happens on explicit request only
([`00`](references/00-the-authority-line.md)).

Silently redefining the requirement is the same failure in the other direction: building what was literally
typed, or what the agent finds convenient, instead of what the user meant
([`00`](references/00-the-authority-line.md)).

## The loop

```text
Requirement
  ↓  what is the complete problem, not the sentence
The systems behind it
  ↓  which of them are actually required for this to be genuinely good
Approaches for each
  ↓  trade-offs, edge cases, consequences, reversibility
The best appropriate solution   <- not the first that works, not the most complex
  ↓
Implement
  ↓
"What is the best way to do THIS?"   <- the question repeats on every decision, big or small
```

The visible feature is rarely the engineering problem. "I need search" is a screen plus an index plus matching,
filtering, ordering, empty and failure states, and a data route to feed it — and which of those matter is a
judgment about *this* product, not a checklist
([`01`](references/01-behind-the-visible-requirement.md)).

Choosing is where the value is: name the real alternatives, steelman the one you did not pick, accept a
trade-off out loud, and re-ask the question before settling. "Does it work?" is the floor, not the bar
([`02`](references/02-what-is-the-best-way.md)).

## When to decide, when to ask

The user delegated the *how*. Do not hand it back:

- **Decide and note it:** internal structure, data flow, library or module boundaries, algorithms, caching,
  error handling, which supporting system to build, how to name things, how to keep a change reversible.
- **Ask first:** the intended experience or design changes, a requirement is ambiguous in a way that shifts
  the outcome materially, the action is irreversible/destructive, costs money or commits externally, or needs
  authorization the agent does not have.
- **Decide then surface it, in one line:** anything that surprises the user when they look — a new dependency,
  a schema change, a system nobody asked for but the feature genuinely needs. Silence about a real decision is
  how an agent ends up having "replaced the vision" without meaning to.

Under **iwts** (nobody awake to correct you) the same line holds, with a lower interruption threshold and a
higher recording duty: the decision method is this skill's, the *ownership and stop conditions* are
[`iwts`](../iwts/SKILL.md)'s, and its records land in the run's folder
([`03`](references/03-running-under-iwts.md)).

## Records, not vibes

A decision worth recording is one a successor might re-decide: architectural, behavioral, or hard to reverse.
It then needs — in this order — **the question the work asked**, the context at the time, the real options with
why the losers lost, the choice, its consequences, and its reversal boundary. An answer without a question is
not a record; if you cannot phrase the question, it was an implementation detail and does not get a file.

Use [`../iwts/assets/decision-record-template.md`](../iwts/assets/decision-record-template.md) — one template,
shared, not copied; it owns what a record *says*. **Where it goes is the project's convention, not dtb's**
(dtb and iwts are thin operating modes; agents-md's Ambiguity section owns the recording convention): the
project's `AGENTS.md` decision-records rule wins; otherwise **one file per decision** at
`<docs>/decisions/<slug>.md` — never a combined `decisions.md`, which explodes with project age — each record
anchored **Date + Commit hash + App-Version** (version stated whenever it changed between decisions). The
ask-or-decide call itself — what was decided without asking, what was assumed instead of asking — is a
recordable decision. Never invent a new location mid-run
([`03`](references/03-running-under-iwts.md)).

## Anti-patterns

- Reproducing the visible screens and stopping there, because only the screens were named.
- The first working solution shipped as the final one, with no second look.
- Complexity added to look sophisticated — or simplicity insisted on when the problem genuinely needs the
  machinery. Both are ego, neither is judgment.
- "Improving" a design the user already approved into something they did not ask for.
- Presenting the user with a menu of implementation choices they delegated, dressed as diligence.
- A decision with no record, so the next reader inherits the answer and cannot see the trade-off.
- Endless optimization: best is bounded by the actual requirement, the evidence, and the deadline.

## References

| File | Owns | Read when |
|---|---|---|
| [`00-the-authority-line.md`](references/00-the-authority-line.md) | Vision vs implementation ownership, reading a prototype/design as requirements, the redesign exception, the seven ways an agent silently redefines a requirement | Any design, prototype, mockup or "make it like this" is in play |
| [`01-behind-the-visible-requirement.md`](references/01-behind-the-visible-requirement.md) | The complete-problem method, the relevance test for internal systems, and what "genuinely strong and professional" demands per shape of product | A one-line feature ask that clearly implies more than one component |
| [`02-what-is-the-best-way.md`](references/02-what-is-the-best-way.md) | Alternatives and trade-off ledgers, edge cases worth designing for, reversibility, best ≠ most complex, the re-ask loop, when to stop optimizing | Any decision with more than one plausible answer |
| [`03-running-under-iwts.md`](references/03-running-under-iwts.md) | The shared one-file-per-decision path (<docs>/decisions/ + states.md), what changes while unsupervised, escalation differences, how to report decisions back, standalone mode | dtb is invoked inside a delegated/iwts run |
| [`../iwts/SKILL.md`](../iwts/SKILL.md) | Who decides and when: autonomy, stop conditions, state and resume | The user has left the work to the agent unsupervised |

## Cases

Worked examples, one scenario per file — read the one closest to your situation:

| Case | Situation | The point |
|---|---|---|
| [`case-01-search-is-an-iceberg.md`](examples/case-01-search-is-an-iceberg.md) | "add search" to a small product | sizing the real system set, deciding which parts matter, and what stayed deliberately out |
| [`case-02-prototype-direction-preserved.md`](examples/case-02-prototype-direction-preserved.md) | a three-screen prototype the user liked | improving the implementation underneath without touching the visual direction |
| [`case-03-decision-under-iwts.md`](examples/case-03-decision-under-iwts.md) | an unsupervised run hits a hard architectural choice | deciding, recording question→options→choice→consequences→boundary, and reporting one line |

## Scope

dtb decides engineering quality inside a goal that exists. It is not: a comparison of candidate libraries or
products for the *user* to pick (that research-and-choose job belongs to a decision-page skill such as
`decide`/`judge` here), not a pre-coding checklist (`implement`), and not a mandate to expand scope — the
best implementation of an unrequested feature is still unrequested work.
