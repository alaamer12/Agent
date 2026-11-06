# The Settled-Behavior Axiom

> A governing principle rather than a component rule: architecture serves one *decided* behaviour, never a hedge across several. Applies anywhere a Component, Rendition, or placement decision is being classified. Referenced by [`composition-shapes.md`](./composition-shapes.md) §5, [`placement.md`](./placement.md) §3, and [`../assets/templates/view-design-sheet.md`](../assets/templates/view-design-sheet.md).

## 1. The axiom

> **A feature's Components reflect one decided product behaviour, never a menu of behaviours it might turn out to have.**

Before any Component, wrapper, or placement decision can be classified, one prior question has to be answered honestly, because getting it wrong silently corrupts everything downstream:

> Is the behaviour this Component embodies actually *settled* — or is it being treated as settled while still secretly being asked "but what if we also wanted it the other way"?

If a feature's search is defined as firing on each keystroke, then "would it ever fire on a Go button instead" is not a live architectural fork to keep both paths open for. It is a different, not-yet-real feature. Building for it now means building for a feature that does not exist.

## 2. The failure mode

The error is always the same shape: **inventing a hypothetical consumer and treating it as though it had the same standing as an actual, current requirement.**

Concretely — keeping a base Component independently importable "because some View somewhere might want the undecorated version". That hypothetical has no requirement behind it. It converts an unmade product decision into an architectural commitment, and the commitment is the expensive part: two parallel implementations now exist, each accumulating its own fixes, while the real behaviour gets settled by trial and error in production rather than by decision beforehand.

A Component that exists "in case we go back to the other behaviour" is dead weight wearing the shape of flexibility.

## 3. The rule while classifying

When classifying a Component — whether it stands alone, whether a capability wrapper around it is optional or mandatory, whether it should be underscored — ask only what this feature's **actual, current, decided** behaviour is. Do not ask what behaviour the feature *might* have instead: that is a product question, not an architecture question, and answering it preemptively produces exactly the wrong classification.

If the product behaviour later genuinely changes, the architecture is rebuilt to match the new settled behaviour. It does not hedge in advance by keeping both shapes alive "just in case."

## 4. The same instinct, already governing two other rules

This is not a new invention — it is an existing discipline in this system made explicit, because it had been violated by omission rather than by contradiction:

- **The closed-family requirement** ([`placement.md`](./placement.md) §3) already refuses to let a *speculative future consumer* justify a placement decision today: Global-Local is a permanent judgment, not "two consumers now and an uncertain future." This axiom is that same refusal one layer earlier — applied to a Component's *behaviour* instead of its *consumer count*. A Component's behaviour must be as settled as its consumer family before either can be classified.
- **The branch/case vocabulary** ([`view-and-rendition.md`](./view-and-rendition.md) §4) already treats a View's Renditions as the actual, exhaustive, decided set of outcomes for one behaviour — never a placeholder for "whichever behaviour gets picked later."

## 5. When a behaviour arrives unsettled

Some gaps are not the architecture's to close. If a feature is handed to implementation without a decided answer to "does this fire on keystroke or on a Go button", no folder structure, naming convention, or placement rule fixes it — because the gap is not architectural. It is a **product decision that was never made**.

So when a Component cannot be classified — when it is unclear whether it should stand alone, be underscored, or be replaced entirely by a Specialised Component — the correct diagnosis is almost never "the architecture lacks a rule for this." It is **"the product decision this architecture is supposed to reflect hasn't been made yet."** The fix is to go get that decision, not to invent an architectural escape hatch that quietly defers it.

Practically: fill in [`../assets/templates/view-design-sheet.md`](../assets/templates/view-design-sheet.md) before scaffolding. If a row of that sheet cannot be answered, the unsettled thing is the product, and that row is the question to take back — not a fork to code around.
