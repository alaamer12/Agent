# Composition shapes — when a grouping is not a Component

> One question with three answers: something is holding several Components together — is it a Component, a Wrapper Component, or a Specialised Component? Read [`roles.md`](./roles.md) §5 and [`view-and-rendition.md`](./view-and-rendition.md) §6 (forwarding) first. The gate on the underscore decision in §4 is [`settled-behavior.md`](./settled-behavior.md).

## 1. The question

Given a named unit containing other Components, decide what it actually is. Three answers, and picking the wrong one is what makes a codebase's structure lie:

```
real coordination among the children   → an ordinary Component
zero coordination, zero addition       → a Wrapper Component
zero coordination, exactly one added   → a Specialised Component
                              capability (composed from a reusable mechanism)
```

## 2. The trap this exists to catch

A set of genuinely independent Components sits adjacent in the markup — three unrelated action buttons — and gets bundled under one plural, purposeful-sounding name (`InlineActions`, `SearchControls`, `ProfileButtons`). That name implies a single functional responsibility, which by [`roles.md`](./roles.md) §5's own test would make it a Component.

But nothing about *grouping unrelated siblings* is a meaningful action. The buttons underneath are each independently purposeful; the thing holding them together does nothing on its own. A plural noun is not a responsibility.

## 3. The coordination test

> **Do the children coordinate, or are they merely adjacent?**

- **No coordination** — no shared state, no exclusivity, no ordering dependency, none of them disabling another: the grouping carries **no architectural role of its own**. It is not a Component, not a Decoration, not a new primitive needing a name. It is a **Wrapper Component**: bare structural markup whose only job is holding independently-purposeful Components next to each other.
- **Real coordination exists** — shared state, mutual exclusivity, a fixed order that matters, one member disabling another: the grouping has a genuine responsibility and by the Component test **is** an ordinary Component. This is simply the rule that a Component may contain other Components, shown with a real case instead of left implicit.

## 4. Wrapper Component is forwarding, not a new concept

[`view-and-rendition.md`](./view-and-rendition.md) §6 established that one unit calling through to another with fixed, known inputs — making no choice, consulting no fact — is **forwarding**, not a new relationship. A Wrapper Component does exactly that, fanned out to several targets at once:

```
FORWARDING        one wrapper, one target,   fixed props, no choice
WRAPPER COMPONENT one wrapper, several       fixed props, no choice
                  independent targets
                  → same relationship, same rule, different arity

children start coordinating (shared state, exclusivity, order) →
    the wrapper has gained a responsibility and become an ordinary Component
```

Nothing in a Wrapper branches, nothing consults a fact, and there is exactly one output for a given input — same as any forwarding wrapper. §6's existing rule already governs it: *if a wrapper exists it must be pure forwarding, with no fact-consulting and no selection added on top.* That rule was never written to apply to exactly one target; it applies to however many targets a wrapper hands props to, as long as none of them is chosen between.

**Placement** follows whichever pole its contents and context earn ([`placement.md`](./placement.md)) — being a Wrapper Component is a statement about *role* (it has none, beyond holding things together), never about where it lives.

The `_`-prefix used on wrapper files in the worked examples is the same signal it carries for Global-Local implementation: "not an independently addressable export". See [`naming.md`](./naming.md) §6.

## 5. Specialised Component

A different situation that surfaces reliably once a codebase matures: a Component that already does its one job correctly, and that same behaviour refined by **exactly one additional capability** — debouncing a search-as-you-type input, adding infinite scroll to a list, adding optimistic update to a submit action.

> **Definition.** A Specialised Component is an existing Component, **composed** — never copied — with exactly one additional capability, where that capability is itself a generic, purpose-agnostic mechanism reusable by any Component that wants it.

Three separate things, with three separate classifications:

```
CAPABILITY MECHANISM   GLOBAL. Purpose-agnostic, reused by any Component. Owns an
(the debounce itself)   effect internally, but produces NEITHER State nor Condition —
                        it is not consulted by a View to select a Rendition; it is a
                        mechanism a Component consumes to reshape when it acts.

BASE COMPONENT         Underscored only if no standalone consumer exists for this
(the undecorated one)   feature's settled behaviour ([settled-behavior.md] §3) —
                        otherwise keeps its plain name and stays independently
                        importable like any ordinary Component.

SPECIALISED COMPONENT  LOCAL. A one-off fusion of exactly one base Component with
                        one capability, meaning one specific thing ("this feature's
                        search input, debounced") with no reuse anywhere else.
```

**Why the fusion is Local and not Global-Local.** Global-Local ([`placement.md`](./placement.md) §2) describes one implementation shared by a *closed family of several siblings*. A Specialised Component is a single one-off pairing that happens exactly once — there is no family to be closed or open. One Component, one capability, one result.

**Composition, not a new mechanism.** A Specialised Component composing its base Component is governed by exactly the relationship in [`view-and-rendition.md`](./view-and-rendition.md) §7: neither side is a fact-producer at this layer, so composition has no forced direction. Copying the base Component's internals into the specialised version is the violation — it forks one responsibility into two that then drift.

**Recognition test.** The name should read as *"a specific Component that also ___"* — "the search input, debounced". If it instead reads as *"a generic thing that ___"* with no tie to one purpose, you are looking at the capability mechanism itself (Global, shared location), not a Specialised Component. If it reads as *"what this feature's search does"* with no added capability beyond the Component's own settled purpose, it is just an ordinary Component and there is nothing to specialise.

**Provenance.** This concept and its tests are adopted from an independently developed doctrine, *The Four-Tier UI Chain* (`base → adaptive → component → specialised`), which names this tier "specialised". The name is kept so the provenance stays traceable rather than inventing a parallel term for an already-solved problem. That doctrine's other two tiers map onto this system's UI Element role as two placement tiers — [`primitives-and-imports.md`](./primitives-and-imports.md) §2.

## 6. Deciding, in order

1. Does the unit consult a fact and select between outcomes? → it is a **View**, and this document does not apply ([`view-and-rendition.md`](./view-and-rendition.md) §3).
2. Does it contain other Components? If not, it is an ordinary Component or a Decoration per [`roles.md`](./roles.md).
3. Do those children coordinate with each other? → **Component** (§3).
4. Does the unit add exactly one reusable, purpose-agnostic capability on top of a base Component it composes rather than copies? → **Specialised Component** (§5).
5. Otherwise — bare grouping, one output, no addition → **Wrapper Component** (§4).
6. If the base Component is now unused standalone, is that a *settled* fact about the feature, or a guess? → [`settled-behavior.md`](./settled-behavior.md) gates the underscore, and the behaviour question has to be answered before any of this classification is honest.
