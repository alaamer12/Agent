---
name: states
description: Classify any fact an app consults as a State or a Condition, decide who owns it, and settle whether a consumer may read it or must create it. Use when deciding loading vs offline, error vs permission-denied, empty vs feature-flag-off, or any "is this my own request or something external" question; when placing a fact source (hook, composable, signal, resource, store, injected service); when a background job, sync worker, or subscription needs an ownership decision; or when a fact is duplicated across consumers. Fact sources return data and never render — the UI roles that consume them belong to the /pvc skill.
argument-hint: "<the flag, loading value, subscription, or request being classified>"
---

# State and Condition — facts and who owns them

## Overview

Every app runs on facts: values consulted before deciding what to do next. Two kinds, kept apart because they differ on every axis that decides ownership, lifetime, mutability, and where the source lives:

> **State** — what *this consumer's own work* is doing right now.
> **Condition** — what *the outside world* is imposing on it right now.

Names used throughout: **fact source** = the unit that produces the value (a hook, composable, signal, resource, store selector, injected service, worker subscription). **Consumer** = whatever reads it to decide what happens next — a screen section, a component, a service method, a background job. Nothing here requires a UI framework.

## The boundary

| | **State** | **Condition** |
| --- | --- | --- |
| Caused by | The consumer's own request or action | Something external: network, server, ops, permissions |
| Lifespan | Finite — expected to resolve on its own | Indefinite — resolves when the outside world changes |
| Who resolves it | The consumer, automatically | An external event: reconnect, deploy ends, role granted |
| Typical values | idle, loading, success, error, empty | offline, maintenance, unauthorized, killed, feature-off |
| Mutation by a consumer | Normal — this consumer drives it | **Never** — Conditions are read, not written |
| Ownership | Can be created, scoped, and destroyed by one consumer | Owned by nothing local; exists independently |

## The two questions

1. > **"If I fixed this by waiting, would it resolve on its own — or does something outside this consumer have to change first?"**
   Resolves because the request finished → **State**. Resolves because something external changed → **Condition**.
2. > **"If I deleted every other consumer, would this still happen?"**
   This decides **scope**, not cause. Keep the axes separate ([`references/state-vs-condition.md`](references/state-vs-condition.md) §4).

If still unsure, default to Condition: they are the ones miscast as State, because "it looks broken" either way. Cause decides, never appearance.

## The ownership rule

> **Create-vs-listen.** Does the source *create* the thing, or does it merely *listen* to a thing that already existed before this consumer arrived and will exist after it leaves?

```
creates the effect   → State       → may be owned by the consumer that called it
listens to a thing   → Condition   → may only be read; nothing local can own it
```

This asymmetry is a property of the **source**, never of the consumer's name. Renaming the consumer changes nothing. Full reasoning and the cases where it matters (nested ownership, wrappers, cleanup): [`references/ownership.md`](references/ownership.md).

## Workflow

1. **Name the fact.** One value, one sentence: what does it assert?
2. **Classify it.** Run the two questions. Write down the cause, not the appearance. → [`references/state-vs-condition.md`](references/state-vs-condition.md)
3. **Separate the three axes.** Cause (mine vs external) ≠ scope (one consumer vs app-wide) ≠ reusability (generic source vs bespoke). All three must be answered independently. → [`references/state-vs-condition.md`](references/state-vs-condition.md) §4
4. **Decide ownership.** Apply create-vs-listen. Then decide the read/write surface: a Condition exposes read-only data; a State exposes whatever the owner needs to drive it. → [`references/ownership.md`](references/ownership.md)
5. **Decide lifetime and cleanup.** An owned State must be cancellable when its owner goes (abort, unsubscribe, dispose, drop). A Condition's subscription outlives any single consumer and must be released per consumer. → [`references/ownership.md`](references/ownership.md) §4
6. **Place the file.** Reusable → a shared location; non-reusable → with its owner. Where the *file* goes among the placement poles is the `/pvc` skill's `placement` model; this skill only decides ownership, which is settled before placement.
7. **Keep it non-visual.** A fact source returns data and never renders. If it renders, it has become something else — in a UI, that unit is a View, and `/pvc` owns that boundary.

## Symptom → answer

| You see | It means | Go to |
| --- | --- | --- |
| "loading" used for both a slow request and a dead network | cause conflated with appearance | [`state-vs-condition.md`](references/state-vs-condition.md) §1 |
| the same offline check written inline in many places | one global Condition, consulted once | [`state-vs-condition.md`](references/state-vs-condition.md) §6 |
| a feature calls a setter for `isOnline` | a Condition being written — a defect | [`ownership.md`](references/ownership.md) §3 |
| a fetch that exists only because this consumer needed it | a State, owned — cancel it on teardown | [`ownership.md`](references/ownership.md) §2, §4 |
| "it's global, so it must be shared" | scope ≠ reusability | [`state-vs-condition.md`](references/state-vs-condition.md) §4 |
| a fact source that renders markup | no longer a fact source | `/pvc` (View/Rendition boundary) |
| unsure whether the source goes in a feature folder or a shared one | ownership settled, placement next | `/pvc` (placement poles) |

## Resources

- `references/state-vs-condition.md` — the taxonomy, the checklist, cause-vs-scope, the tells, the quick reference
- `references/ownership.md` — create-vs-listen, the read-only rule, nested ownership, forwarding pass-through, cleanup
- `examples/fact-sources-polyglot.md` — State and Condition sources in React, Vue, Solid, Blazor, Dioxus, and a non-UI worker
- `examples/classification-drills.md` — misclassification cases with answers

Practice on a real shape: [`examples/classification-drills.md`](examples/classification-drills.md). Pair with `/pvc` when the consumer is a UI section — `/pvc` needs only the binary "does this unit read a fact source at all?", not this taxonomy, so the two skills stay independent.

**Update the lists above whenever a file here is added, removed, or moved.**
