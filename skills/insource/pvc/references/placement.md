# Placement — the three poles

> Where an implementation file is allowed to live, decided by *reason for existing* rather than by how many imports point at it today. Read [`roles.md`](./roles.md) first, and [`view-and-rendition.md`](./view-and-rendition.md) §2–7 if the thing being placed is a Rendition or a Component shared between Renditions. Every tree the rules below describe: [`../examples/worked-trees.md`](../examples/worked-trees.md).

## 1. The gap that forced a third pole

The basic model gave any piece of implementation two placement answers:

```
GLOBAL → lives in a shared, app-wide location; purpose-agnostic; any feature may consume it
LOCAL  → lives with its one owner; one consumer, one call site
```

That binary held for a long time because most real sharing situations do resolve to one of the two. It broke on a concrete case: a Component consumed by **more than one** sibling, and therefore not Local by definition — but with **no reason to exist for anyone outside that specific sibling set**, and therefore not Global either. Forcing it into either pole was wrong both times:

- Filed **Local**, colocated inside one of its two consumers → the other consumer now reaches into a sibling's folder to import it, and the "single owner, single call site" premise quietly stops being true.
- Filed **Global**, promoted to the shared layer → it now sits beside genuinely purpose-agnostic primitives while itself being irreducibly specific to one family. Anyone browsing the shared layer for something reusable finds something that was never meant for them.

Neither placement was dishonest by accident. The model simply had no slot for what actually happened.

## 2. The three poles

```
GLOBAL        → any feature, anywhere, may consume it; purpose-agnostic;
                has a reason to exist independent of any specific consumer

GLOBAL-LOCAL  → consumed by more than one sibling, but ONLY siblings belonging to one
                closed, specific family; no reason to exist, and no other consumer,
                outside that family

LOCAL         → exactly one consumer, one call site, one owner
```

Global-Local sits between the other two not as a compromise or a "not sure yet" bucket, but as its own answer with its own test. It is not "Global with fewer consumers" and not "Local with more consumers" — **consumer count was never what decided any of the three**. What decides is whether the thing has a reason to exist *beyond the specific set of siblings that currently use it*.

## 3. The test

The same instinct [`facts.md`](./facts.md) §2 uses ("if I deleted every other View, would this still happen?"), applied to placement:

> **If every current sibling consumer were deleted, would this piece have any remaining consumer, or any reason to exist?**

- Yes — anything in the app could plausibly consume it → **Global**. Its purpose does not depend on which features happen to use it today.
- No — no consumer and no reason to exist would remain, *but* more than one sibling currently uses it → **Global-Local**. Its purpose is defined entirely by that family.
- There is one consumer, period, now and by design → **Local**.

Decided the same way ownership is decided anywhere in this system: by what the thing's reason for existing actually is — not by how many places reference it, and not by what it is named.

### The closed-family requirement

Global-Local requires the consumer family to be a **closed, enumerable set** — exactly these siblings and nothing else, *by design*. That is what distinguishes it from "Global, but I haven't found the third consumer yet." Having two consumers and an uncertain future makes something a Global candidate with insufficient evidence, not Global-Local. Global-Local is the deliberate, permanent judgment that this piece's *entire reason for existing* is to serve one named family, and that this stays true even when the family's members change internally.

## 3.1 A second, independent test: tier-locking

§3 asks about the actual current consumers of one specific file. That is correct for a file sitting inside one View's own folder — its consumers are literally the sibling files in that folder, countable and real.

It gives the wrong answer for an entire **feature-level tier** — a feature's own `components/`, `decorations/`, or fact-source folder. A tier is not one file with a fixed set of consumers; it is a **designated pool**, built to serve every View that feature will ever have, one today or ten next year. Applying a file-by-file consumer count to a tier produces unstable reclassification pressure: it keeps asking "does this file have a second consumer *yet*?" and answering Local every time, until the moment a second View appears — at which point nothing about the file changed, only the count did. That instability is the signal that consumer-counting was never the right test for a tier; the tier's membership was decided by **where it was deliberately placed**.

So a second test governs this case:

> **Was this folder deliberately created as the shared pool for one feature's Views, Components, Decorations, or fact sources — regardless of how many currently exist inside it?**

- Yes — it is a feature-level tier → **Global-Local, locked to that feature**, the moment anything is placed there. True for the first file ever placed in an otherwise-empty tier, and true even if that file has only one consumer. The lock comes from the tier's designated role, not from a tally.
- No — the file lives inside one View's own folder → §3's ordinary consumer test applies, scoped to that View.

```
INSIDE a View's own folder      → §3: count actual current consumers
AT a feature's own tier folder  → §3.1: is this folder the feature-wide pool?
```

The two are not in tension; they answer different questions at different placements. §3 asks "how many things consume this one file?" — right where consumers are few and countable. §3.1 asks "what pool was this folder designed to be?" — right where membership is a design decision rather than a running count.

**One feature's tier is never shared with a sibling feature's tier of the same name.** Two features each having a `components/` folder means they share a folder *name*, not a family: nothing in one may reach into the other's tier. Each lock is scoped to the single feature it sits inside — never to `features/` as a whole, and never to a sibling that happens to use the same convention. Same visual depth in the tree, or same folder name, is not evidence of a relationship. Only an actual import establishes one.

**And none of this is about literal folder names.** Every example here writes `features/<name>/` because it is a common convention, but §3.1 never checks for a folder spelled `features` — it asks whether a folder is *a feature's own tier*, which is a question about role, not spelling. A project is free to call the grouping `capabilities/`, `modules/`, `domains/`, `packages/`, and the feature `funds`, `fund-management`, or `wallet`; nothing about which folders are tier-locked changes. The same caveat applies to any shared or primitive folder name in these rules — `shared/`, `common/`, `app-wide/` are illustrative. Only actual importability by any feature makes something Global.

## 4. Why Global-Local surfaced where it did — and why it isn't limited to that case

Worth stating precisely, because *why* it was first noticed and *what* it applies to turned out to be two different things.

**Where it was noticed.** [`view-and-rendition.md`](./view-and-rendition.md) §7 establishes that Component and Rendition are symmetric — neither is a fact-producer, so composition between them has no forced direction. The first case that surfaced Global-Local (`_FundCard`, shared between two sibling Renditions) happened to involve that pair. That symmetry made the case easy to spot. It is not a precondition for the pole.

**What it applies to.** §3's test does not mention Views, Renditions, or any particular pair of roles. It is a general placement test, answerable for **any** two siblings that share an implementation, regardless of role and regardless of whether a View exists anywhere above them. A worked case with no View, no Rendition, and no fact in it at all — two ordinary Components sharing one sub-piece — is in [`../examples/worked-trees.md`](../examples/worked-trees.md) §2 specifically to demonstrate that.

```
Component/Rendition symmetry → a narrow fact about one named pair; made the first case
                                 obvious; it is not the rule that defines the pole

Global-Local (§3)            → a general test, asked per-relationship, of any two siblings
                                 sharing implementation with no purpose beyond each other
```

**The one documented exception.** On the asymmetric side ([`facts.md`](./facts.md) §5), the test genuinely does not apply. A State source's ownership is already pinned to exactly one caller by the causation rule itself — there is no scenario of "two siblings legitimately sharing ownership of one State fetch", because ownership there was never a placement question; it was answered by create-versus-listen before placement was ever asked. That is the single place in this system where Global-Local cannot arise, and the reason is specific to that pair, not a general "asymmetric roles never share" claim.

## 5. Folder rule

```
GLOBAL        → the app-wide layer: shared primitives, shared fact sources, shared
                renditions. No lock, no family, any feature may import.

GLOBAL-LOCAL  → two configurations, governed by two tests:

  (a) INSIDE one View's own folder — colocated at the nearest common ancestor of its
      closed family of actual consumers (§3). Never promoted further out, never
      buried inside one of its own siblings. Convention: prefix the file with `_`,
      because it sits directly beside the siblings it is scoped to and needs to
      stand apart from them visually.

  (b) AT a feature's own tier — its components/, decorations/, fact-source pool (§3.1).
      Everything placed there is locked to that one feature regardless of current
      count. No underscore needed: the tier folder already signals the lock.

LOCAL         → colocated with its single owner. Includes every file inside one View's
                folder that only that View's own Renditions consume (§3). Being in the
                same feature as other Views does not promote anything — only actual
                placement in the feature's tier folder does.
```

**Two tests, not one — the most common source of confusion.** Which test applies is decided entirely by **where the file is placed**, never by guessing at its future. Applying §3's consumer count to a whole tier gives an unstable, wrong answer; applying §3.1's tier test to a file sitting beside its two actual consumers inside one View folder over-promotes it for no reason — it is not a feature-wide pool, it is two Renditions sharing one file.

## 6. Quick reference

| Question | Answer | Pole |
| --- | --- | --- |
| Could any feature, anywhere, plausibly use this? | Yes | **Global** |
| Inside one View's folder, more than one consumer in that same folder, and zero would remain if that family were deleted? | Yes | **Global-Local (a)** — §3 |
| Placed in a feature's own tier, built to serve any View that feature has or will have? | Yes | **Global-Local (b)** — §3.1, regardless of count |
| Exactly one consumer by design, and not in a feature-wide tier? | Yes | **Local** |
| Is the thing being placed a fact source (State/Condition)? | Yes | Not this model — [`facts.md`](./facts.md) §5's asymmetric rule instead |

## 7. The complete model

```
                        PLACEMENT
                            │
              ┌─────────────┼─────────────┐
              ↓             ↓             ↓
           GLOBAL      GLOBAL-LOCAL      LOCAL
        (any feature,   ┌────┴────┐    (one owner,
         purpose-       ↓         ↓     one call
         agnostic)    (a) View  (b) Tier  site)
                      -scoped,  -scoped,
                      §3        §3.1
                      consumer  design-
                      count     intent
```

Placement was always the question *where does this belong, and who may consume it?* The two-value answer served every case that happened to be either app-wide-and-purpose-agnostic or single-owner-and-bespoke. The real case in §1 proved a third, stable answer exists — **shared, but only within a closed family that is itself the entire reason the shared piece exists** — and §3.1 showed that even that third answer has two configurations decided by two different tests. The one documented exception remains the State/Condition pair, where causation settles ownership before placement is asked.
