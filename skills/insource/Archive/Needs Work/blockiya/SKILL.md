---
name: blockiya
description: Enforce and apply the Blockiya architectural pattern for UI construction across component frameworks. Use when designing, reviewing, refactoring, or implementing orchestrators, features, pages, views, or project structure that must follow Blockiya rules — zero visual concerns in orchestrators, derive-before-pass, intents-only-upward, stereotypes, adapters, Strict utilities, growth signals, UML notation, or recommended feature-slice layout. Works for React, Vue, Svelte, Solid, and similar. Triggers include blockiya, Blockiya pattern, orchestrator block, strict blockiya, blockiya-core, derive before pass, fire intents and stop, zero styling blockiya, Atomic stereotype, Compound stereotype, behavioral primitive, adapter wrapper, UML notation, Vue Blockiya, framework-agnostic Blockiya.
metadata:
  version: "2.2.0"
  type: architecture-pattern
  source: The Blockiya Pattern (v2.1) — polyglot adaptation
---

# Blockiya Pattern Skill (Polyglot)

Apply the Blockiya architectural pattern rigorously across component frameworks (React, Vue Composition API, Svelte, Solid, Angular signals, etc.).

A Blockiya is an **orchestrator**. It owns domain state, talks to data sources, derives props/data before passing them down, and translates user actions into intents that fire only upward. It never owns visual styling. It never reaches into a library's internals. It never decides what happens after it fires an intent — that is always the caller's concern.

Mental model: architect, not craftsman. The Blockiya decides the shape and assembles materials; everything else is someone else's concern.

## Core Invariants (framework-agnostic — never violate)

1. **Zero visual concerns** — No class bindings, style objects, CSS modules, utility classes, or framework-specific styling APIs inside any Blockiya. All visual output goes exclusively through primitives or adapters.
2. **Derive before you pass** — Raw API / domain shapes never reach presentational children. Always transform first (named pure deriver).
3. **Fire intents and stop** — After emitting an upward intent the Blockiya's responsibility ends. No confirmation dialogs, no navigation, no sibling refresh, no toast ownership inside the Blockiya.
4. **Data only through dedicated accessors** — Never call fetch / HTTP clients / RPC directly. Always via a queries / data-access layer (composables, hooks, stores, or equivalent).
5. **3–7 inputs in / 3–7 intents out** — Beyond this ceiling extract a child Blockiya.
6. **Know only the layer below** — A Blockiya may import primitives, behavioral primitives, adapters, utilities, and its own presentational children. It must not import other features' internals.

## Stereotypes (shared vocabulary)

| Stereotype | Role | When to use |
| --- | --- | --- |
| `<<Page>>` | Top-level route / screen | Router pages; owns post-intent decisions |
| `<<Feature>>` | Large workflow orchestrator | Multi-step wizards, complex flows |
| `<<Compound>>` | Multi-component Blockiya | Owns 2–5 child blocks |
| `<<Atomic>>` | Single-purpose leaf Blockiya | Focused responsibility |
| `<<Primitive>>` | Non-behavioral design-system unit | Visual tokens only |
| `<<Behavioral>>` | Interaction-owning design-system unit | Dropdown, Modal, Tooltip — interaction state stays internal |
| `<<Adapter>>` | Third-party library wrapper | Token + event + lifecycle translation only |
| `<<Utility>>` | Pattern-native structural helper | Conditional, list, intent, derivation helpers — no domain, no visuals |
| `<<Context>>` / Provide | Scoped state provider | Deep sharing inside one Blockiya tree |
| `<<Hook/Query>>` / Composable / Store | Data-fetching / mutation accessor | Lives in queries / data layer |

Stereotypes are growth signals. An Atomic that accumulates children wants to become Compound.

## Layer Stack

```
Page / Screen
  └── Blockiya                          ← owns domain state, derives, fires intents
        ├── Presentational children     ← receive derived data, fire intents up
        ├── Behavioral Primitives       ← own interaction state internally
        ├── Non-Behavioral Primitives   ← visual tokens only
        ├── Adapters                    ← third-party isolation
        └── Utilities (blockiya-core)   ← structural + intent + derivation helpers
```

## Strict Blockiya (recommended)

When Strict mode is requested or team convention:

- Every async handler **must** go through the intent utility of the target framework (`useIntent` / `useIntent` composable / equivalent).
- Every derivation **must** go through the derive utility.
- Conditional / list / composition rendering **must** use the structural helpers of the target framework.
- No manual loading/error pairs for async intents.
- No inline derivation objects or ad-hoc map/ternary rendering of domain lists.

See `references/blockiya-core-polyglot.md` for React + Vue implementations and contracts for other frameworks.

## Naming & Visibility

- Block names end with `Block` (or framework convention) → `BillingOverviewBlock`
- Adapter names end with `Adapter`
- Intent callbacks / emits end with `Intent` → `onSaveIntent`, `saveIntent`, `@save-intent`
- Visibility is contextual: Public (exported from feature), Private (under parent children), Internal (state/accessors)

## UML Notation (summary)

Full system in `references/uml-notation.md`. Use when producing or reviewing diagrams.

- Four-section shape: Header (stereotype + visibility), ▼ Inputs, ◆ Internal, ▲ Events/Intents
- Callback received as input is still ▼; the same callback when invoked is ▲
- Relationships: `*--` owns, `..>` uses, provide/consume for scoped state

## Rules & Violations

### Must do
- Own domain + transient UI state.
- Derive display shapes with pure named functions + derive utility.
- Fire typed intents upward and stop.
- Keep interaction state inside behavioral primitives.
- Place adapters in top-level adapters/.
- Keep presentational children private until reuse appears.

### Must never
- Own any visual styling inside a Blockiya.
- Call data APIs directly.
- Manage open/closed state for Dropdown/Modal (belongs inside the behavioral primitive).
- Navigate, confirm, toast, or refresh siblings after an intent.
- Pass raw server shapes to children.
- Import from another feature's private folders.
- Let an adapter own domain state.

## Imperative Primitives (exception)

Toasts and similar system-level UI have no declarative placement. Their API is a function/composable. Document them as imperative and keep ownership outside Blockiyas (usually Page or global host).

## Recommended Project Structure (adapt per framework)

Vertical feature slices are recommended, not forced.

```
src/
  shared/
    ui/
      primitives/
      behavioral/
    blockiya-core/          ← framework-specific utilities implementing the same contracts
  entities/
  features/
    <feature-name>/
      blockiyas/
        <Name>Block/
          index.*           ← the orchestrator (zero visual concerns)
          context.* / provide  ← optional scoped state
          children/         ← private presentational views
      routes/ or pages/
      queries/ or composables/ or stores/
  adapters/
  app/
```

Adapt file extensions and folder names to the framework (`.tsx`, `.vue`, `.svelte`, etc.). The architectural placement rules stay identical.

## Growth Signals

- Inputs / intents > 7 → split.
- Two domains inside one file → extract child Blockiya.
- Atomic starts owning children → promote to Compound.
- Private presentational child imported by two parents → promote.
- Adapter starts carrying domain decisions → move those decisions up.

## Coexistence with Framework Patterns

Blockiya is the "knows" side of Smart/Dumb, Container/Presentational, Feature/UI, Composable/Component, etc. It adds the extra discipline: zero visual concerns, derive-before-pass, intents-and-stop, input ceiling.

Inside children freely use controlled inputs, scoped provide/inject or context, prop grouping, etc.

## State Placement Decision

1. Only this unit needs it? → local reactive state.
2. Comes from / syncs with server? → data layer (queries / composables / stores).
3. Shared by multiple Blockiyas across the app? → global store outside features.
4. Otherwise → scoped provide / context belonging to the feature or parent Blockiya.

## When Reviewing or Generating Code

1. Identify every unit that owns domain state or data → candidate Blockiya.
2. Enforce zero visual concerns and intent-only upward flow.
3. Check input/intent counts; extract if over ceiling.
4. Verify all data access goes through the data layer.
5. Confirm behavioral primitives hide interaction state.
6. Confirm adapters perform only the three translations (token / event / lifecycle).
7. Prefer Strict utilities for the target framework.
8. Surface growth signals.
9. When drawing diagrams, use the UML notation.

## References (load on demand)

- Full methodology (framework-agnostic principles + original depth) → `references/methodology.md`
- **Polyglot utilities** (contracts + React / Vue implementations) → `references/blockiya-core-polyglot.md`
- Stereotypes, growth, project structure → `references/structure-and-stereotypes.md`
- Full UML notation + diagrams → `references/uml-notation.md`
- Focused role examples (React + Vue) → `references/example-user-profile-polyglot.md`
- Quick review checklist → `references/review-checklist.md`

## Assets (copyable templates — not loaded into context)

- `assets/templates/user-profile-react.tsx` — full React Blockiya template
- `assets/templates/user-profile-vue.vue` — full Vue Blockiya template

When the user needs a ready-to-copy file, read from assets/ and present or write it. Keep reference examples focused; do not paste full templates into chat unless requested.

Always load the relevant reference when the task requires deeper detail, code generation of utilities, diagram production, or a complete working example in a specific framework.
