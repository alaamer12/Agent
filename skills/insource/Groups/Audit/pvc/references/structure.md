# Structure — turning roles into a filesystem

> Where role-carrying code goes, and when a folder has earned its existence. Read [`roles.md`](./roles.md) first — this document assumes its roles and adds placement conventions only. Which pole a file belongs to is [`placement.md`](./placement.md); the canonical worked trees are [`../examples/worked-trees.md`](../examples/worked-trees.md).

## 1. Purpose

The roles form a construction model:

```
Page → View → (Component + Decoration/Aligner) → UI Element
```

This document translates that into a project layout. The goal is **not** folders that exist because the architecture contains a term. The goal is a structure that reflects how the UI is actually constructed, so a reader can answer, without opening files:

- Where does this Page live, and what Views construct it?
- What Component provides this View's main functionality, and what Decorations support it?
- Which pieces are primitives, and which are feature-specific?
- Where does behaviour and data belong?
- Which code is globally reusable and which is bespoke?

The folder structure must not become a bureaucratic copy of the conceptual diagram.

## 2. Two independent axes

Feature ownership and architectural role are different questions, and a project needs both:

```
                 PROJECT ORGANIZATION
                          │
           ┌──────────────┴──────────────┐
           ↓                             ↓
    DOMAIN OWNERSHIP              UI CONSTRUCTION ROLE
    what domain is this for?      what role does it play?
    search / profile / checkout   View / Component / Decoration / UI Element
```

Feature architecture answers *"what capability does this code belong to?"* and provides ownership and domain boundaries. This model answers *"what role does this piece play in constructing its View?"* and provides UI composition semantics. Neither replaces the other; the filesystem expresses both at once — feature first, role within it.

## 3. Vocabulary is yours to choose

Every layout here writes `src/features/<feature>/`, `ui/`, and `shared/` because those are common conventions, but **none of it is required vocabulary** — no rule in this system checks spelling ([`placement.md`](./placement.md) §3.1 owns the reasoning for tier names, and it applies identically to every folder mentioned anywhere). Pick one spelling per concept and keep it consistent; consistency is what makes the structure readable, not the specific words.

## 4. Layout per role

```
Page            one folder or file per screen; contains only composition of Views
View            one unit per meaningful section; its Renditions live with it (§6)
Component       its own unit under the feature's Component tier
Decoration      its own unit under the feature's Decoration tier (Aligners need no
                separate home — Aligner ⊂ Decoration)
UI Element      the global primitive layer only, never inside a feature
Behaviour/data  beside the UI tree, not inside it (primitives-and-imports.md §5)
```

What each level is *not* allowed to do is the actual rule:

- A **Page** does not construct primitives. It composes Views and stops.
- A **View** does not host another feature's Component.
- A **primitive** does not import a feature. If it knows what feature it serves, it is a Component and has been misplaced.
- A **Behaviour unit** (hook, composable, service, store action) is not a UI role at all; giving it a UI-role folder teaches readers the wrong lesson.

## 5. Flat files or nested subfolders — a choice, not a rule

Every tree in this system may be drawn at either granularity, and both are the same architecture:

```
FLAT (siblings in one folder)         NESTED (one folder per unit)

FundCardView/                         FundCardView/
├── FundCardView.tsx                  ├── FundCardView/FundCardView.tsx
├── FundCardListRendition.tsx         ├── FundCardListRendition/…
├── FundCardGridRendition.tsx         ├── FundCardGridRendition/…
└── _FundCard.tsx                     └── _FundCard/
                                          ├── _FundCard.tsx
                                          ├── _FundCard.types
                                          └── _FundCard.test
```

**Being a Rendition, a Global-Local Component, a Wrapper, or a Specialised Component is a statement about role and pole, never about how many folder levels sit between a file and its siblings.** No test in this system has a folder-depth term in it — the placement question in [`placement.md`](./placement.md) §3 asks whether the piece would survive deleting its family, which is answered identically in both drawings. The `_` convention is unaffected too: it prefixes the *name*, not the *path*, so `_FundCard/_FundCard.tsx` signals "shared-but-scoped, not an independent export" exactly as `_FundCard.tsx` does alone.

Which to prefer is ordinary engineering judgment, not an architectural call:

- `[flat]` reads better when a View's Renditions and its scoped-shared pieces are individually small and the whole set scans as one folder listing.
- `[nested]` earns its keep once an individual unit grows its own supporting files — types, tests, styles, docs — the same trigger an ordinary Component uses.
- An unlisted mix is legitimate: nested where one unit is heavy, flat beside it. Choose per directory, not per project.

Extension and file-name conventions (`.tsx`, `.vue`, `.razor`, `.svelte`, `.rs`) belong to the framework; see [`framework-adapters.md`](./framework-adapters.md).

## 6. Folder-creation rules

**Do not create a folder tree mirroring the roles inside every View:**

```
excessive:   SearchView/
             ├── decorations/SearchDescription/ CommonKeywords/
             ├── aligners/
             ├── components/
             └── elements/
```

Use the feature's own tiers (`views/`, `components/`, `decorations/`) and let locality decide the rest. The filesystem optimises for discoverability, ownership, locality, maintainability, and project size — in that order of usefulness, not as a formula.

**Co-location for small compositions** is often better than extraction:

```
SearchView/
├── SearchView.tsx
├── SearchDescription.tsx     ← a Decoration used by only this View: stays here
├── CommonKeywords.tsx
└── index
```

while Components genuinely reusable across the feature live at the feature tier. Small supporting pieces stay close to their View; purposeful reusable units become explicit Components. This prevents folder fragmentation.

**A View should not extract everything it renders.** `<h1>Search</h1>` and `<p>Search for users…</p>` do not need to become `SearchTitle`, `SearchSectionContainer`, `SearchWrapper`, `SearchContent`, `SearchLayout` unless those abstractions have a real reason to exist. Manufacturing named abstractions for bare grouping is exactly the Wrapper Component trap — [`composition-shapes.md`](./composition-shapes.md) §2. The architecture exists to make structure clearer, not to increase the number of files.

**"Everything is a component" is the failure state to avoid** — a flat `components/` folder holding `SearchPageComponent`, `SearchViewComponent`, `SearchTitleComponent` hides the semantics entirely. Naming that keeps role visible: [`naming.md`](./naming.md).

## 7. Scale — the same shape at every size

A minimal project is already enough to apply the model:

```
app or routes/     pages (one per screen)
features/<one>/    views · components · decorations · behaviour units
ui/                the primitive layer
```

Growing adds breadth, never new concepts: more features, a Decorations and layout tier in the primitive layer, a shared app-wide layer for Global fact sources and Renditions, and infrastructure beside it all. The UI hierarchy itself does not change as the application grows:

```
Routes → Pages → Views → Components/Decorations → UI Elements
```

Three layers describe the whole project, at any scale:

| Layer | Contents |
| --- | --- |
| Application composition | Routes → Pages |
| UI composition | Pages → Views → Components, Decorations, Aligners |
| Primitive construction | Components, Decorations → UI Elements (both tiers) |

## 8. The test the structure has to pass

Reading the code should reveal the composition. A View whose body names one Decoration, one Component, and one Decoration reads as exactly what it is: supporting information, primary functionality, supporting options. A Component whose body names a leading piece, a primitive, and a trailing action reads as a primary unit with two Aligners.

When the filesystem, the composition tree, and the conceptual structure all tell the same story, the structure is doing its job. When they disagree, the disagreement is the bug — and it is usually a naming problem ([`naming.md`](./naming.md)) or a pole problem ([`placement.md`](./placement.md)) rather than a layout problem.
