---
name: pvc-architecture
description: Apply PVC (Page-View-Component) role-based UI construction architecture for web apps across any component framework. Use when designing, reviewing, refactoring, or scaffolding UI structure, pages, views, components, decorations, aligners, or UI elements. Works for React, Vue, Svelte, Solid, Angular, and similar. Triggers include PVC, Page View Component architecture, role-based UI, semantic UI composition, View vs Component distinction, project structure for UI, UI hierarchy rules, architectural classification of components, Vue PVC, React PVC, framework-agnostic UI architecture.
---

# PVC Architecture — Page, View, Component

Role-based UI construction model. Pages compose Views. Views compose purposeful Components + supporting Decorations/Aligners + nested Views. UI Elements are the primitive building blocks. Classification is by architectural role, not by framework component implementation.

**Framework-agnostic.** The same roles apply whether the unit is a React function component, Vue SFC, Svelte component, Solid component, Angular component, or any other declarative UI unit.

Full role definitions, examples, and rationale → `references/architecture-core.md`  
Rules, violations, checklist → `references/rules-and-violations.md`  
Folders, naming, co-location → `references/project-structure.md`  
Framework mapping → `examples/polyglot-ui-examples.md`

## Core Hierarchy

```
Application
└── Page                    # Route/screen composition boundary
    └── View                # Meaningful section of UI (composable)
        ├── Component       # Purposeful functional unit
        ├── Decoration     # Supporting context/explanation/emphasis
        │   └── Aligner     # Positional decoration (leading/trailing/top/bottom)
        └── UI Element      # Primitive construction block
```

Central principle: **Pages compose Views. Views compose purposeful UI. UI Elements provide the primitive construction blocks.**

## Five Diagnostic Questions

| Level | Question |
|-------|----------|
| **Page** | What screen are we constructing? |
| **View** | What meaningful section are we constructing? |
| **Component** | What purposeful functionality is the user interacting with? |
| **Decoration / Aligner** | What supports, explains, or surrounds that functionality? |
| **UI Element** | What primitive interface pieces construct it? |

## Critical Distinction

```
Framework component unit  ≠  Architectural Component
```

Role is determined by responsibility in the current composition, not by the host framework’s component construct. Same technical unit can play different roles in different compositions.

## Implementation Patterns (Principle-First)

Express PVC with the idioms of the target stack. Do **not** force one framework’s syntax. Concrete mapping → `examples/polyglot-ui-examples.md`.

### Structural pattern (framework-neutral)

```
Page
  → composes Views only (no primitives, no deep layout)

View
  → composes Decorations + Component(s) + optional nested Views
  → may co-locate small Decorations

Component
  → purposeful interaction surface
  → consumes behavior from hook / composable / store / service
  → builds from UI Elements + Aligners

UI Element
  → generic primitive (value, events, variants)
  → zero application domain knowledge
```

### Purpose API (not DOM API)

| Role        | Prefer                         | Avoid                                      |
|-------------|--------------------------------|--------------------------------------------|
| Component   | `value`, `onSearch`, `onClear` | `inputClassName`, `iconPosition`, `padding` |
| View        | `initialQuery`, `onSearch`     | internal arrangement of children           |
| UI Element  | `value`, `disabled`, `variant` | feature names (DeleteAccount, Checkout…)   |

Adapt binding style to the stack (props/callbacks, `v-model`, `bind:`, signals, `@Input`/`@Output`). The **contract** stays purpose-based.

### Behavior placement

Domain logic lives outside the pure composition layer (hooks, composables, stores, services). The Component consumes that boundary; PVC only constrains UI composition roles.

### When generating code

1. Detect or ask for the target framework.
2. Emit **one** idiomatic dialect for that stack (not parallel dumps).
3. Keep PVC role names and purpose APIs intact.
4. If the stack is unspecified, describe structure in neutral terms and offer to emit for a chosen framework.

## Project Structure (Adaptive)

Scale to project size. Feature ownership and UI role are orthogonal. Full trees, naming, co-location, import direction → `references/project-structure.md`.

```
src/
├── app/ (routes, pages, layouts)
├── features/<feature>/
│   ├── views/
│   ├── components/
│   ├── decorations/
│   └── hooks|composables|services|types
├── ui/elements/   # global primitives
└── shared/
```

Small Decorations may co-locate with their View. Aligners need no dedicated folder. Do not make the filesystem a bureaucratic copy of the conceptual diagram.

## How the Agent Should Apply This Skill

1. Classify every significant piece with the five diagnostic questions.
2. Load `references/rules-and-violations.md` when enforcing rules or listing violations; do not invent a second rules list.
3. Load `references/architecture-core.md` for role depth, Search/Modal examples, benefits, recursive composition.
4. Load `references/project-structure.md` when scaffolding folders or naming.
5. Load `examples/polyglot-ui-examples.md` for framework mapping or when the user asks for cross-stack comparison.
6. Prefer co-location for small compositions; extract only when purpose or reuse justifies it.
7. Keep Pages thin, Views purposeful, Components focused on user intent, UI Elements generic.
8. Preserve downward dependency: Page → View → Component → UI Element.
9. Emit one idiomatic dialect for the user’s framework; never assume React-only.

## Reference map

| File | Owns |
|------|------|
| `references/architecture-core.md` | Conceptual model, roles, principles, benefits, worked examples |
| `references/rules-and-violations.md` | Hard rules, violations, checklist, anti-patterns |
| `references/project-structure.md` | Folders, naming, co-location, import direction, realistic trees |
| `examples/polyglot-ui-examples.md` | Role→framework table, purpose contracts, emission rule |
