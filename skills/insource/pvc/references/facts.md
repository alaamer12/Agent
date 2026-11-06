# Facts — State and Condition

> The two kinds of fact a View may consult, and the one asymmetric ownership rule between them. Read [`roles.md`](./roles.md) first. This document defines facts only — who consults them and what gets rendered is [`view-and-rendition.md`](./view-and-rendition.md); where implementation files go in general is [`placement.md`](./placement.md).

## 0. The rule that makes everything else work

> **A fact source returns a fact. It never returns UI markup.**

`useXxxState()` / `useXxxCondition()` in a hooks framework; a signal, a computed, a store selector, a resource, an injected service method in others — the shape is the same regardless (see [`framework-adapters.md`](./framework-adapters.md)):

```
fact source      → returns data only, never renders
View             → the only unit that both consults facts and selects what to render
Rendition        → markup only, receives data, consults nothing
```

Names ending in `State` or `Condition` that return markup are always a defect, with no exceptions — see [`naming.md`](./naming.md) §4. The reason is load-bearing rather than stylistic: a fact is an input to a decision, and rendering *is* the decision. Folding both into one unit destroys the only place the system can see what a section knows versus what it shows.

## 1. The boundary

> **State** is what *this View's own data cycle* is doing right now.
> **Condition** is what *the outside world* is imposing on this View right now.

They were long lumped together as "state". They are separated because they differ on every axis that decides where the code lives and who may touch it:

| | **State** | **Condition** |
| --- | --- | --- |
| Caused by | This View's own request or action | Something external: network, server, ops, permissions |
| Lifespan | Finite — expected to resolve on its own | Indefinite — resolves when the outside world changes |
| Who resolves it | The View itself, automatically | An external event: reconnect, deploy ends, role granted |
| Typical values | idle, loading, success, error, empty | offline, maintenance, unauthorized, killed, feature-off |
| Mutation by a consumer | Normal — this View drives it | Never — Conditions are read, not written |

## 2. The one question to ask

> **"If I fixed this by waiting, would it resolve on its own — or does something outside this View have to change first?"**

Resolves because this View's request finished → **State**. Resolves because something external changed → **Condition**.

A second check that reaches the same answer from a different angle:

> **"If I deleted every other View in the app, would this still happen?"**

Tied only to this View's own data → likely State. Would happen to others too → likely Condition — but note that this second question decides *scope*, not *cause*; §4 keeps them separate for a reason.

## 3. Decision checklist

Walk in order, stop at the first yes.

1. Did *this View* trigger it, by making a request or performing an action? → **State**.
2. Does resolving it require something outside this View's control (reconnect, ops ending maintenance, a role being granted)? → **Condition**.

Still unsure → default to **Condition**. Conditions are the ones that get miscast as State, because "the screen looks broken" in both cases. The cause decides, not the appearance.

## 4. Cause is not scope — two independent axes

Condition does not mean "global" and State does not mean "local". That assumption is false, and mixing the axes produces wrong placement:

```
                     LOCAL                       GLOBAL
                (one View/feature)          (every View at once)

CONDITION     camera permission denied,   offline, maintenance,
(external     one widget down, one        session expired,
 cause)       feature flag                kill-switch

STATE         search is loading,          app-shell bootstrap fetch
(internal     one form failed to submit   ("check auth on load") — rare,
 cause)                                   still owned by one thing
```

And a **third**, separate decision sits on top of both: does the implementation file get *shared* or stay bespoke to one place? Orthogonal to Cause and Scope both. A local Condition (camera permission) can be a reusable fact source serving camera, mic, and location; a global Condition (kill-switch) can be a one-off never reused. Scope decides *where it is consulted from*; reusability decides *where the file lives*.

## 5. The ownership asymmetry

Because facts are consulted by Views, and Views nest, a View reacting to a Condition may own a nested State fetch, and a View reacting to a State may consult a Condition. Both directions are real — but **they are not the same relationship**, and treating them as symmetric is the mistake worth naming precisely:

> A View reacting to a **Condition** may **create and own** a State, because resolving that Condition can legitimately require its own fetch.
> A View reacting to a **State** may **only read** a pre-existing Condition, because a Condition by definition exists independently of any single View's request — nothing can own what it didn't cause.

**The test that exposes it:** does the fact source *create* the thing, or does it merely *listen* to a thing that already existed before this View mounted and will exist after it unmounts?

```
creates the effect  → State      → may be owned by the calling View
listens to a thing  → Condition  → may only be read
```

Two illustrative cases (concrete code in five frameworks: [`../examples/polyglot-walkthrough.md`](../examples/polyglot-walkthrough.md)):

- **Condition owning a State — real composition.** A maintenance countdown exists only because a View already reacting to maintenance needs it to pick what to display. Nobody else needs that fetch; it is created and destroyed with that View. The countdown is a State, owned by the View; the maintenance signal is a Condition, listened to.
- **State reading a Condition — a dependency, not composition.** "Am I online" is true or false whether or not any particular View ever mounts. It was not created by one View and cannot be destroyed by one. Every View can ask and get the same answer, because every View is *reading*, none is *owning*.

**Why it exists at all.** State and Condition are both fact-*producers*: each is backed by a side effect that somebody caused. Asymmetry only ever arises between a producer and a consumer, because "who caused this" has an unequal answer by construction — and Condition, by definition (§1), precludes local causation, so a View can never occupy the creator position relative to one.

```
Condition → may own     → State       (legitimate composition)
State     → may only read → Condition  (a dependency)
```

This is a property of the **fact source**, never of the View's name. Renaming the consuming View changes nothing about which side creates and which side listens — if renaming *did* change the answer, naming and ownership would be secretly coupled, which would itself be the flaw. Contrast [`view-and-rendition.md`](./view-and-rendition.md) §7: Component and Rendition produce no facts and own no effects, so the pair is *symmetric* where this pair is not.

## 6. Where each fact source lives

```
State fact sources      → colocated with the View that owns the fetch
                          (or at that feature's tier — see placement.md §3.1)

Condition fact sources  → placement follows Scope and reusability, not Cause:
   global + reusable     → a shared conditions/ location, consulted from a View near the root
   local + reusable      → a shared conditions/ location, consulted per feature
   not reusable          → stays with its owner, whatever its scope
```

Rule of thumb: **non-reusable always lives with its owner** (feature tier for local, the app shell for global). **Reusable always moves to a shared location**, and scope is expressed purely by *which View consults it*, never by which folder the file sits in. The general placement model, including the middle pole this shares with everything else, is [`placement.md`](./placement.md).

## 7. The tells in the code

- Writing the same global Condition check inline in many different Views — that duplication *is* the signal it should be consulted once, by one View near the root.
- Placing a State fact source at the root is impossible without the root knowing one feature's internal fetch. That impossibility is the signal too.
- A View mutating a Condition it didn't cause (calling a setter for `isOnline` from inside a feature) is a defect. Conditions are read.
- A fact source named `State`/`Condition` that returns markup. No exceptions.

If a check feels awkward to place, that discomfort is diagnostic, not incidental.

## 8. Quick reference

| Situation | Answer | Why |
| --- | --- | --- |
| Search results loading | State | Caused by this View's fetch, resolves when it completes |
| Search returned zero results | State | Outcome of this View's own request |
| Search request failed (500) | State | Retry re-triggers the same request this View owns |
| Fetching a countdown for a View reacting to maintenance | State (nested) | Caused, scoped, and killed by that View — real ownership |
| Reading `online` from inside a loading View | Condition (read, not owned) | Existed before, will exist after |
| Device has no network | Condition | External, hits every View, resolves outside the app |
| Server in maintenance mode | Condition | External, ops-controlled |
| Camera permission denied | Condition (local) | External cause, one feature's scope |
| Session expired / unauthorized | Condition | External to this View's own logic |
| Feature flag off | Condition | Externally imposed, not tied to one request |
