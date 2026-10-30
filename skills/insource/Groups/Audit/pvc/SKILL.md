---
name: pvc
description: Role-based UI construction (Page → View → Component, plus Decoration, Aligner, UI Element, Rendition) — framework-agnostic architecture for building or auditing UI code in React, Vue, Solid, Svelte, Blazor, Dioxus or any component system. Use when designing a screen or feature folder, deciding what a piece of UI actually is, separating loading/error/offline handling, placing a shared Component, naming a unit, or when a codebase has become "everything is a component". Also use for `scripts/check_pvc.py` audits and `scripts/scaffold_feature.py` skeletons. Classifying a fact as a State or a Condition, and deciding who owns it, is the companion /states skill — invoke both for screen design; this skill needs only whether a unit reads a fact source.
argument-hint: "<feature or screen being designed, or a path to audit>"
---

# PVC — Page → View → Component

## Overview

Classify every piece of UI by the **architectural role it plays**, never by the construct the framework gives you. A component-framework unit is an implementation mechanism; a role is what that unit represents in a composition. The system's founding law:

> **A framework component is not automatically an architectural Component.**

Everything below follows from that. The doctrine is framework-neutral; syntax is mapped in [`references/framework-adapters.md`](references/framework-adapters.md).

## The roles

| Role | Answers | Rule |
| --- | --- | --- |
| **Page** | what sections make up this screen? | composes Views only, never primitives |
| **View** | what is this section about? | the only unit that consults facts **and** selects what renders |
| **Component** | what is the user doing here? | one purposeful function |
| **Decoration** | what explains or surrounds it? | supporting context: titles, hints, badges |
| **Aligner** | what leads or trails it? | a positional Decoration (Aligner ⊂ Decoration) |
| **UI Element** | what primitives construct it? | feature-blind building blocks, in two tiers |
| **Rendition** | what does this case display? | props in, markup out; never consults a fact |

## The load-bearing rules

1. A **fact source** — hook, composable, signal, resource, store selector, injected service — returns data and never renders. Which kind of fact it is and who owns it is the `/states` skill's question; PVC asks only the binary: *does this unit read a fact source at all?*
2. That binary is the entire View/Rendition seam: a View may read a fact **and** return markup; nothing else may do both.
3. A Rendition never selects between sibling Renditions. Anything that does has already become a View.
4. Component ↔ Rendition composition is **symmetric** — neither produces a fact, so neither owns an effect, so nothing forces a direction.
5. Placement is three poles — **Global**, **Global-Local**, **Local** — decided by *reason for existing*, not consumer count; feature tiers are locked by design intent (§3.1's separate test).
6. A grouping whose children don't coordinate is a **Wrapper Component** — it has no role of its own.
7. A Component composed with exactly one reusable capability is a **Specialised Component**; composed, never copied.
8. Primitives live in `ui/base` (framework named once) and `ui/adaptive` (its skin). Imports point downward and never skip a tier.
9. A feature's Components reflect **one decided product behavior**. Speculative hedging is a missing product decision, not an architectural fork.

## Workflow

Work top to bottom; each step links the reference that owns its detail.

1. **Settle the behavior.** Fill in [`assets/templates/view-design-sheet.md`](assets/templates/view-design-sheet.md). A row you cannot answer is a product question to take back — not a shape to code both versions of. → [`references/settled-behavior.md`](references/settled-behavior.md)
2. **Name the roles.** For each screen: which Views make it up, and inside each View what is the primary Component versus what merely explains it. → [`references/roles.md`](references/roles.md)
3. **Mark the fact seam.** For each unit answer one binary: does it read a fact source? That alone decides View vs Rendition vs Component. Classifying *which kind* of fact, and who owns it, is `/states` — call it, do not re-derive it here.
4. **Give the View its branches.** One View selects among Renditions; say "branch" or "case", never "state". Nest Views freely; never nest a choosing Rendition. → [`references/view-and-rendition.md`](references/view-and-rendition.md)
5. **Place every file.** Run the pole test: would it survive deleting its family of consumers? Then check whether it sits in a *locked feature tier* instead — a different test, same pole. → [`references/placement.md`](references/placement.md), trees in [`examples/worked-trees.md`](examples/worked-trees.md)
6. **Classify awkward groupings.** Coordination test → Component, Wrapper, or Specialised. → [`references/composition-shapes.md`](references/composition-shapes.md)
7. **Fix the primitive layer and import direction.** `ui/base` → `ui/adaptive` → Component; nothing reaches past a tier, nothing points upward. → [`references/primitives-and-imports.md`](references/primitives-and-imports.md)
8. **Name it.** Suffix per role; `_` prefix for scoped-shared and wrappers. No fact suffix may render. → [`references/naming.md`](references/naming.md)
9. **Layout.** Feature × role as two independent axes; flat or nested by judgment, not doctrine. → [`references/structure.md`](references/structure.md)
10. **Verify.** Run the auditor, then read the composition — filesystem, component tree, and conceptual structure must tell the same story.

## Symptom → rule

| You see | It means | Go to |
| --- | --- | --- |
| a file named `…State` / `…Condition` that renders markup | always a defect | [`naming.md`](references/naming.md) §4 |
| a "Rendition" reading a store, hook, or injected service | it is a View, unnamed | [`view-and-rendition.md`](references/view-and-rendition.md) §5 |
| "is this loading flag a State or a Condition?" | not this skill's question | `/states` |
| a fact source duplicated across consumers | ownership, not placement | `/states` |
| `SearchControls`, `ProfileButtons` wrapping unrelated buttons | Wrapper Component | [`composition-shapes.md`](references/composition-shapes.md) §3 |
| one file with two consumers, meaningless outside them | Global-Local (a) | [`placement.md`](references/placement.md) §3 |
| "only one consumer, so move it out of the tier" | tier-lock is a different test | [`placement.md`](references/placement.md) §3.1 |
| both an eager and a debounced version kept "in case" | unmade product decision | [`settled-behavior.md`](references/settled-behavior.md) §2 |
| `Button variant="delete-account"` | primitive learned a feature | [`primitives-and-imports.md`](references/primitives-and-imports.md) §1 |
| a Page rendering `<Input/>` | Page took a lower role | [`roles.md`](references/roles.md) §3 |
| unsure how this maps to Blazor/Vue/Dioxus | vocabulary bridge | [`framework-adapters.md`](references/framework-adapters.md) |
| classifying a real shape, need practice | 16 drill cases | [`examples/classification-cases.md`](examples/classification-cases.md) |

## Tools

```
python scripts/check_pvc.py src              # audit a tree (exit 1 on errors)
python scripts/check_pvc.py src --explain TIER_SKIP
python scripts/scaffold_feature.py --feature funds --framework vue --view FundCardView:list,grid
```

`check_pvc.py` is stdlib-only and reads `.tsx .jsx .ts .js .vue .svelte .razor .cs .rs`; it treats folder names as illustrative and gates path-based findings on real file existence. Self-test: `python scripts/check_pvc.py tests/fixtures/dirty/src` must report 11 errors, and `tests/fixtures/clean/src` must report `OK`.

## Resources

- `references/` — `roles`, `view-and-rendition`, `placement`, `composition-shapes`, `primitives-and-imports`, `settled-behavior`, `structure`, `naming`, `framework-adapters`
- `examples/` — `worked-trees` (the only place any worked tree lives), `polyglot-walkthrough` (React · Vue · Solid · Blazor · Dioxus), `classification-cases`
- `scripts/` — `check_pvc.py`, `scaffold_feature.py`
- `assets/templates/view-design-sheet.md` — fill before scaffolding

## Adjacent skill

`/states` owns facts: State vs Condition, cause/scope/reusability, create-vs-listen ownership, and how a fact source is written in each framework. This skill owns roles and placement, and needs exactly one input from there — the binary *"does this unit read a fact source?"* Neither skill requires the other to load; invoke both when designing a screen. `check_pvc.py` audits both surfaces, because the violations are structural and detectable; classification itself is a judgment and stays in `/states`.

Load one reference at a time, on the step that needs it. **Update the lists above whenever a file here is added, removed, or moved** — a stale map reintroduces exactly the drift this skill prevents in code.
