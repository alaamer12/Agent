# The primitive layer and import direction

> How the UI Element role is split into two placement tiers, and the direction imports are allowed to run. Read [`roles.md`](./roles.md) §7 first. Provenance of the two-tier split: [`composition-shapes.md`](./composition-shapes.md) §5.

## 1. Primitives stay generic

The global primitive layer is independent of business features. A primitive must not know which feature is using it:

```
good primitive   Button(disabled, loading, size, variant, type, on_press, children)
feature-specific DeleteAccountButton          → that is a Component and belongs in the feature
```

Purposeful Components then compose the primitive:

```
DeleteAccount → Button
SearchAction  → Button
FollowUser    → Button
```

This keeps the primitive layer stable while the application grows. It is the same primitive-and-purpose distinction as [`roles.md`](./roles.md) §7, stated as a dependency rule rather than as a classification.

## 2. Two tiers within one role

The primitive role is one architectural role but **two placement tiers**, adopted from *The Four-Tier UI Chain* (`base → adaptive → component → specialised`):

```
ui/base/       ← the ONLY place the framework or platform primitive is allowed to exist,
                 re-declared under this system's own name. A one-line re-export is a
                 complete, correct file here.

ui/adaptive/   ← base + this system's own skin: variants, tokens, states, generic
                 decorators. Still purpose-agnostic, still zero feature knowledge.
                 Built ONLY from ui/base/.
```

**Both tiers remain UI Element as a role.** A Component built from `adaptive/Button` is answering exactly the same question — *what primitive interface pieces construct it?* — as one built from a raw framework control. Styling richness does not change a thing's job in constructing a View's purpose. What the tiers add is placement granularity *inside* one role, the same way [`placement.md`](./placement.md) distinguishes Global-Local's two configurations without changing what Global-Local means.

Do not promote a primitive's tier into a new role, and do not demote a Component into the primitive layer because it is small.

## 3. The two laws

**Law 1 — the framework is named exactly once.** Each primitive appears in `ui/base/` as a re-export under this system's own name. That file is correct at one line: the point is a single named seam, not added behaviour. Do not invent props or logic to justify its existence.

**Law 2 — imports point downward and never skip.**

```
Page → View → Component → adaptive → base → framework
                                   ↑
                            Components consume THIS tier only
```

A Component imports from `adaptive`, never from `base` and never from the framework directly. Skipping a tier is the most common violation: it puts raw framework styling decisions inside feature code, which then cannot be changed centrally.

```
GOOD   SearchPage → SearchView → SearchInput → adaptive/Input
BAD    SearchPage → SearchView → SearchInput → framework Input  (skipped adaptive)
BAD    adaptive/Input → SearchInput                              (reversed direction)
```

The mechanical check for both directions is [`../scripts/check_pvc.py`](../scripts/check_pvc.py).

## 4. Downward dependency, in general

The same direction applies to the whole hierarchy, not only to primitives:

```
Application-specific → Purpose-specific → Primitive
```

A primitive must never import a feature's View, Component, or Decoration. A UI Element that imports `features/<something>/views/<SomeView>` has reversed the abstraction direction, and the reversal is what turns a reusable layer into a liability that cannot be changed without touching the feature that leaked into it.

Supporting layers may be consumed from the appropriate level: a View consumes Components, Decorations, and (through them) primitives; it does not reach past the Component tier to arrange primitives on the user's behalf ([`view-and-rendition.md`](./view-and-rendition.md) §2).

## 5. Beyond the markup tiers

The UI hierarchy is a **UI composition layer**, not a whole-application architecture. Behaviour, data, and services live beside it:

```
Component → behaviour unit → service / store / data access
```

Where a fact belongs — inside a View, at a feature tier, or in a shared location — is decided by cause, scope, and reusability, which are three independent axes: [`facts.md`](./facts.md) §4 and §6. Nothing in this document's downward-import rule constrains how a data layer is organised; the rest of the application is free to evolve independently as long as the UI layer keeps pointing down.
