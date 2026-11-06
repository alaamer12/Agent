# View and Rendition — who consults facts, and what gets shown

> The two roles that turn facts into a screen: the View is the only unit allowed to consult a fact *and* render, and a Rendition is one of the outcomes it can pick. Read [`roles.md`](./roles.md) and [`facts.md`](./facts.md) first — this document assumes both and adds nothing to them. Worked trees: [`../examples/worked-trees.md`](../examples/worked-trees.md). Naming: [`naming.md`](./naming.md).

## 1. The gap this closes

Once fact sources are correctly restricted to returning data and never rendering ([`facts.md`](./facts.md) §0), something still has to *consult* them and decide what appears. If that "something" is allowed to borrow the `State`/`Condition` suffix, rendering responsibility sneaks back into a name reserved for a fact. Two roles are needed instead:

```
View       → the unit that consults facts and selects what to render
Rendition  → what gets rendered — one of several possible outcomes of a View
```

## 2. Definitions

### View

> **A View consults State and/or Condition facts and selects exactly one Rendition to return.**

A View is the only kind of unit in this system permitted to read a fact *and* produce markup in the same body. That is deliberate: it is the single seam where fact and render are allowed to meet. Every other unit is one or the other, never both.

A View remains a View in every sense established in [`roles.md`](./roles.md) §4 — it composes Components and Decorations, it never composes primitives directly across a tier ([`primitives-and-imports.md`](./primitives-and-imports.md) §3), and it may nest inside another View.

> **A View is always the parent of its Renditions — the set of cases it can present.**

This holds even when it currently has one case. A search section with no loading, error, or offline handling yet is not "a View without Renditions" — it is a View with exactly one, the default case, which needs no name or file because there is nothing to disambiguate it from. Add a second case and nothing about the role changes; only the count does.

A unit that can only ever produce one fixed output, with no facts to consult and no cases to choose between, was never a View — it is a Component or Decoration wearing the wrong name ([`roles.md`](./roles.md) §1).

This is also why a View can never be substituted for a Rendition: a Rendition is one case, a View owns the set and picks among them. Even a "simple" View is a grouper of one.

### Rendition

> **A Rendition is one specific, complete render a View can produce. It receives data only. It consults no fact. It is not independently addressable — it has no purpose outside the View that selects it.**

The performance metaphor the word comes from: the View is the piece being performed, each Rendition a particular performance of it given the state of the room. "The disabled Rendition of the search." "The loading Rendition."

A Rendition is *built* the same way any View content is built — from Component and Decoration. It simply cannot branch on a fact itself. If branching is needed, that branching belongs one level up, in the View.

**The relation runs both ways.** A Rendition is built from Components (the ordinary case). But two *sibling* Renditions of the same View can also converge on and share one Component underneath them — shared layout, shared logic, shared data-shaping. That shared Component is real, has its own placement question, and is what [`placement.md`](./placement.md) exists to answer.

## 3. The rule, as a table

```
fact source (State/Condition) → data only, never renders
XxxView                       → the ONLY unit that both consults facts and selects a Rendition
XxxRendition                  → markup only, no fact consulting — pure input → output
```

Self-check for any unit in the codebase:

| Consults a fact? | Returns markup? | What it must be |
| --- | --- | --- |
| Yes | Yes | **View** |
| Yes | No | **fact source** — State or Condition ([`facts.md`](./facts.md)) |
| No | Yes | **Rendition**, or a plain Component/Decoration if it carries no fact-driven branching at all |
| No | No | Outside this system — a utility |

There is no valid cell for "returns markup, named with a fact suffix." That combination is always a defect regardless of which fact prompted it. A checker enforces it mechanically: [`../scripts/check_pvc.py`](../scripts/check_pvc.py).

## 4. Vocabulary: "branch" or "case", never "state"

When describing what a View can show, say **branch** or **case** — never "state". Not pedantry: "this View has three states" is genuinely ambiguous here, because it could mean three `State` fact values or three Renditions, and those vary independently — one State value can map to several cases, and a case can be reached by a State, a Condition, or both.

```
"State"           → reserved for the fact returned by a State fact source
"Condition"       → reserved for the fact returned by a Condition fact source
"branch" / "case" → neutral word for one of a View's possible outcomes
```

"SearchView has four branches" is unambiguous. "SearchView has four states" is not, and the reader should never have to guess which of two concepts a review comment meant.

## 5. Nesting: View-in-View holds, Rendition-in-Rendition cannot

[`roles.md`](./roles.md) §5 established that Views nest freely. That remains true, and now means something more precise: a View's selected Rendition is free to host a *child View*, which consults its own facts and selects its own Renditions entirely independently. Ordinary composition — two groupers, one inside the other's chosen case.

A Rendition, by contrast, cannot contain another Rendition as a sibling it chooses between. The reason is conceptual before it is mechanical. Renditions are the different cases of *one* View's question ("what does this section look like right now?"). A case cannot contain another case from the set it belongs to: "loading" and "error" are both answers to the same question, and neither answer can contain the other as an alternative to itself without collapsing the difference between *being a member of a set* and *being the thing that enumerates the set*. That incoherence exists before any code is written, and it is not fixed by passing the choice in as a prop instead of a hook — the problem was never *how* the choice is made, it is that a case is being asked to also be the chooser.

The mechanical symptom follows from the conceptual one: a Rendition takes data and performs no consulting (§2), so it cannot decide "show A or B". The moment a function makes that choice it is consulting something to decide with, which means it has a fact, which means per §3 it is no longer a Rendition. It has become a View. So "nested Renditions" was never a pattern to police — it is a contradiction in terms twice over. Anything that looks like a Rendition selecting between Renditions is a View that hasn't been renamed yet.

```
✘  a markup-only-named unit that branches on an incoming flag        → it is a View; rename it
✔  the branching unit named as a View, outcomes left as real Renditions
```

**The rule in full:** Views nest inside Views, including inside another View's Rendition. Renditions may host a nested View. A Rendition may not host a nested Rendition-that-selects — anything attempting that has already become a View and should be named and treated as one.

## 6. Forwarding is not nesting

§5 forbids one specific thing: a Rendition *choosing* between sibling Renditions. It does not forbid a Rendition being built by *calling* another Rendition. Forwarding makes no choice and consults no fact — it hands fixed, known data to a shared implementation. Nesting-as-selection requires a decision; a decision requires a fact; a fact makes the decider a View. Forwarding requires nothing but a call. Only the first is what §5 rules out.

A global, parameterized Rendition is a reusable unit that happens to satisfy Rendition's definition (data in, markup out, no branching), so nothing prevents a feature-local Rendition from being a thin wrapper around it. A View may equally call the global version inline; the local wrapper exists purely for organisation — a stable, named, colocated call site, or a place to pin fixed values once.

> **Forwarding is optional, never mandatory.** The only rule is that *if* a wrapper exists it must be pure forwarding — no fact consulting, no selection added on top. That is what keeps it from becoming a §5 or [`facts.md`](./facts.md) §5 violation.

The identical reasoning extends to fact sources: a local fact source may wrap a generic shared one, and the ownership test still passes through correctly, because ownership is decided by *which layer actually issues the request or registers the listener* — unaffected by how many wrapper layers sit above it. Forwarding is one principle applying to Renditions, State sources, and Condition sources, not three separate rules.

## 7. Component and Rendition are symmetric

It is tempting to look for an asymmetry here mirroring [`facts.md`](./facts.md) §5. There isn't one, and the reason is precise.

The State/Condition asymmetry exists because the test applied to that pair — *who caused the underlying side effect* — has a structurally unequal answer, since Condition precludes local causation by definition. Component and Rendition are not fact-producers at all. Neither owns an effect, neither issues a request or registers a listener. A Rendition is data-in/markup-out by definition; a Component is the purposeful unit a View composes and does not hold fact sources itself (only a View does, §3). With no side effect on either side, there is nothing for a causation test to be unequal *about*.

```
ASYMMETRIC  State / Condition      one side may own an effect, the other may only read
SYMMETRIC   Component / Rendition  neither produces a fact; composition has no forced direction
```

So the relationship in §2 runs whichever way the code needs: Rendition built from Component, and Component shared across sibling Renditions. Neither direction is privileged, because privilege in this system is created only by causal ownership of a fact. What that implies for where shared, non-global implementation may live is [`placement.md`](./placement.md).

## 8. Folder placement

Renditions are colocated with their View, not extracted to a shared folder — they are not independently addressable (§2), so there is nothing to share. If a Rendition's *content* genuinely repeats across features under different text, the reusable part is a Component or Decoration consumed by several Renditions; the Renditions themselves still stay local to their View.

The tree shapes, the underscore convention, and when a View's folder should be flat versus nested: [`../examples/worked-trees.md`](../examples/worked-trees.md) and [`structure.md`](./structure.md) §5.
