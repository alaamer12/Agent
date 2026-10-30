# The authority line — what the agent may change and what it may not

Two ownerships travel together and are constantly confused:

> **The user owns the vision and the requirements. The agent owns the implementation decisions.**

Deciding *how* is the delegation. Redeciding *what* is the breach. Everything in this file is one of those two
cases wearing a disguise.

## The two-question locator

For any decision in flight, before choosing:

1. **Would the user notice if this were different?** Visible — layout, flow, wording, behavior they can
   observe, what the feature *does* — is their territory. Invisible — how state is held, where work happens,
   which internal boundaries exist — is yours, and asking about it is the failure mode this skill exists to
   prevent.
2. **Is this a change to the requirement, or a change to its execution?** A requirement change is proposed,
   never applied. An execution change is made and, if surprising, reported in one line.

Boundary cases resolve on question 1, not on importance. A change can be technically huge and entirely yours
(replacing an O(n²) join with an indexed lookup); a change can be technically trivial and unmistakably theirs
(renaming the primary action from "Publish" to "Post", dropping a screen they drew, changing the empty state
from encouraging to apologetic).

```text
   "This is only a small change"        <- size is not the test
   "They would not mind"                <- not yours to assume
   "It is obviously better"             <- to you; visible = ask
```

## Reading a prototype or design as requirements

A prototype is not a picture of screens. It is a statement of **intended experience**, and most of what it
asserts is not the pixels — it is the existence of a flow, its order, its density, and its tone.

| The artifact shows | It therefore asserts | Yours to change? |
|---|---|---|
| a set of screens and the order between them | the journey exists with these stages | no |
| how many things appear at once, grouping, hierarchy | information density and what matters first | no |
| copy and labels, tone of empty/error text | the product's voice | no |
| color, type, spacing, radius | the visual direction, *if the user approved or praised it* | no |
| a control with no wired behavior (a sort dropdown, a filter chip) | the behavior is **wanted** — the drawing is a requirement, not a mock | no: implement it |
| no loading, error, or no-results state | nothing. Those are implied by the product working, and filling them in is your job while keeping their style | yes, in the existing style |
| which data appears where | the data model the user believes exists | propose only; they own the model's meaning |
| implementation hints (`div`s, one file, inline styles) | nothing about the real architecture | yes, entirely |

That last row is the most common misread in the other direction: a hand-built prototype's *weaknesses* are not
requirements. Reproducing its inline styles into a 4,000-line component "to match the prototype exactly"
honors the drawing and betrays the intent — the intent is the visual result, which survives any clean
implementation.

## The redesign exception

Change the visible direction only on an **explicit** request or explicit freedom ("tear it up and make it
yours", "you decide the design too"). Otherwise the correct move is one line of proposal, not a decision:

> "The implementation is done behind your design. Two things in the design itself fight the users' data — the
> three-level filter row collapses on narrow screens, and results have no sort affordance. Want me to propose
> variants, or leave the direction as is?"

Ask, then continue working on the internals. Do not stall the whole task waiting for an aesthetic answer, and
do not treat silence as consent. If the user has already *said* they like a direction, that statement is a
constraint with a date on it — revisit it only when new evidence appears (a usability finding, a real device
where it breaks), and name the evidence.

## The seven silent requirement changes

Each of these is a real failure with a fix. "Silent" is the sin, not the change.

1. **Literalism** — building exactly the sentence typed, and delivering something that does not work in the
   product. *"I need search"* with a `LIKE '%q%'` over a growing table is literalism: technically delivered,
   functionally absent. Fix: restate the ask as the outcome the user wants, and build what makes that outcome
   true every time ([`01`](01-behind-the-visible-requirement.md)).
2. **Convenience substitution** — choosing the weak approach because the strong one is more work tonight.
   Fix: if the strong one is genuinely better and the cost is your time, the cost is not a reason; if the cost
   is the user's (schedule, complexity, ownership), it is exactly a reason — say which.
3. **Preference-driven redesign** — replacing approved design because the agent's taste differs. Fix: the
   exception above.
4. **Improvement-shaped scope creep** — adding a system nobody needs and presenting it as quality. Fix: the
   relevance test in [`01`](01-behind-the-visible-requirement.md); park the rest as a finding.
5. **The "temporary" deviation that ships** — bypassing the design contract for a day, then leaving it. Fix:
   every deviation gets a decision record with a reversal boundary; a deviation with no record is invisible at
   handover.
6. **Optimization that changes semantics** — caching, batching, lazy-loading, or debounce that quietly alters
   what the user sees when. Fix: state the visible difference before adopting it. A 300 ms stale result may be
   free; a stale *balance* is not.
7. **Stack substitution** — swapping a framework, storage, or library the project chose because another is
   better in general. Fix: the project's incumbent choice is a constraint. Changing it is a user decision, and
   a *separate* one from the task at hand.

## Same visible contract, stronger internals

The shape of a correct dtb change: the surface the user sees is untouched, everything under it improves.

```text
  user-visible contract  (unchanged):  screen, control, copy, behavior, timing they can perceive
  ─────────────────────────────────────────────────────────────────────────────
  internal boundaries    (yours):      where data is fetched, indexed, cached, validated, retried
                                       how state is owned, which module computes what, error taxonomy
```

A small sketch of the discipline that keeps them separate — a boundary the UI talks to, so the machinery
underneath stays the agent's decision and cannot leak into the design:

```ts
// UI depends only on this contract; the strategy behind it is the agent's to change.
interface SearchResults { query(q: string, f: Filters): Page<Item> }
```

The same holds in any stack — a controller in [Rails], a hook in [React]/[Vue]/[Svelte], a use-case class in
[Java]/[Kotlin]/[C#], a function returning a table in [SQL] behind [Postgres] or [SQLite], a route in
[Express]/[FastAPI]/[Gin]. What matters is that there **is** a seam: with one, an internal improvement is free
and invisible; without one, it becomes a redesign and lands in the user's territory.

## Reporting, so nothing was decided silently

One line per decision that could surprise, at the moment it is made — not in a footnote later:

> "Search now reads from a local index instead of scanning the table; results look identical, first paint went
> from 1.9 s to 40 ms, and the index rebuilds on write. Reversal is the one adapter in `search_source.py`."

Three parts: what changed under the surface, what did **not** change visibly, and how to undo it. Under an
autonomous run this becomes a record file instead of chat ([`03`](03-running-under-iwts.md)).
