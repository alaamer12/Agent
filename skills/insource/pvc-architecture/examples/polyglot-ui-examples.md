# PVC — Polyglot Implementation Notes

Architectural roles are framework-invariant. This file shows how the **same roles** map onto common component models. Prefer emitting **one** idiomatic dialect for the user's stack, not parallel copies of the same tree.

---

## Role → framework construct

| PVC role     | React              | Vue                | Svelte           | Solid              | Angular              |
|--------------|--------------------|--------------------|------------------|--------------------|----------------------|
| Page         | route component    | page / route SFC   | `+page` / route  | route component    | routed component     |
| View         | function component | SFC                | `.svelte`        | function component | component            |
| Component    | function component | SFC                | `.svelte`        | function component | component            |
| Decoration  | function component | SFC                | `.svelte`        | function component | component            |
| UI Element   | function component | SFC                | `.svelte`        | function component | component / directive|
| Behavior     | hooks              | composables        | stores / runes   | stores / signals   | services + signals   |

Same responsibility; different vehicle.

---

## Structural shape (any stack)

```
SearchPage                    # Page — composition only
├── SearchView                # View
│   ├── SearchDescription     # Decoration
│   ├── SearchInput           # Component
│   │   ├── SearchIcon        # Aligner (leading)
│   │   ├── Input             # UI Element
│   │   └── ClearButton       # Aligner (trailing)
│   └── CommonKeywords        # Decoration
└── SearchResultsView         # View
    └── SearchResult[]        # Component
```

Reproduce this tree with the host framework's component syntax. Do not change role names or nesting meaning.

---

## Purpose API contract (stack-agnostic)

**SearchInput (Component)**  
- Inputs: current query value  
- Outputs: value changes, search intent, clear intent  
- Must not expose: icon slot layout, input class names, padding

**Input (UI Element)**  
- Inputs: value, placeholder, disabled, variant  
- Outputs: value change  
- Must not know: search, checkout, profile

Map these contracts to the local binding style:

- React / Solid — props + callbacks  
- Vue — props + `v-model` / emits  
- Svelte — `export let` + events / `bind:`  
- Angular — `@Input` / `@Output`

---

## Behavior boundary

Domain logic (search request, validation, history) lives outside the pure composition layer:

- React → `useSearch`  
- Vue → `useSearch` composable  
- Svelte → store or helper  
- Solid → store / signal factory  
- Angular → injectable service  

The Component **consumes** that boundary; it does not become the domain layer.

---

## Emission rule for agents

When asked for code:

1. Identify the target framework (ask if unclear).  
2. Generate **one** idiomatic implementation of the PVC tree for that framework.  
3. Keep PVC role names and purpose APIs intact.  
4. Do not paste the same example four times in different syntaxes unless the user explicitly requests a cross-framework comparison.

Parallel multi-framework dumps belong in teaching material only, not in default project scaffolding.
