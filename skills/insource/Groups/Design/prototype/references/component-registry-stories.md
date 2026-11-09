# Component Registry & Multi-State Stories Gallery

> **What this owns:** The component-in-isolation catalog inside a `prototype` project: how every reusable UI component is cataloged with its full state matrix (`stories.registry.js`), rendered in an isolated stories gallery (`index.stories.html` or `/stories`), and verified for complete state coverage.
>
> This pairs with [`story-isolation.md`](story-isolation.md):
> - **In-page Story Isolation (`?story_id=`):** Isolates a component directly from its host page DOM and live data context.
> - **Stories Catalog / Gallery (`/stories`):** Displays the unified project-wide component registry, showcasing every component across all its declared interactive and visual states (Component × State matrix).

---

## 1. Core Principles

1. **State Matrix over Single Happy Path:** A screen screenshot only shows one state at a time. The stories gallery shows what a component looks like when it is **empty, loading, disabled, validating, errored, or overflowing**.
2. **Unified Architecture:** Uses the same tokens (`theme.css`), layout styles (`_app.css`), and central URL state helper (`_app.js`) as the prototype screens.
3. **Pure Data Registry:** Component definitions live in `js/stories.registry.js` as pure data (no embedded DOM or ad-hoc functions).
4. **URL-Driven Facets & Descriptors:** URL parameters drive search, state filtering, and global facets (`dir`, `theme`, `density`).

---

## 2. Directory Layout within a Prototype

When a prototype includes a full component gallery alongside whole-screen pages:

```text
prototype/
├── index.html              # Chooser: Two cards -> Whole Pages | Component Stories
├── index.pages.html        # Screen gallery (all prototype pages)
├── index.stories.html      # Stories catalog entry: search box, descriptors, component cards
├── pages/                  # Prototype screen entries (/funds, /dashboard)
├── stories/                # Optional standalone component pages
├── js/
│   ├── _app.js             # Bootstrap + single state helper + story isolation
│   ├── components/         # Shared component renderers
│   ├── stories.registry.js # Registry data (id, name, states, props, facets)
│   ├── stories.js          # Stories gallery shell: search, filter, render
│   └── specs.js            # Page specs and preview links
├── css/
│   ├── theme.css           # Design tokens (colors, typography, spacing)
│   ├── _app.css            # Base app styles
│   └── stories.css         # Stories gallery chrome
└── serve.mjs               # Zero-dependency router supporting /stories and pages
```

---

## 3. Registry Schema (`stories.registry.js`)

The registry defines each component as pure data:

```javascript
export const meta = {
  title: "Component Catalog",
  caption: "Full state coverage matrix across components",
  facets: {
    dir: ["rtl", "ltr"],
    theme: ["light", "dark", "system"],
    density: ["comfortable", "compact"]
  },
  defaults: {
    dir: "ltr",
    theme: "system",
    density: "comfortable"
  }
};

export const components = [
  {
    id: "button",
    name: "Primary Button",
    renderer: "button",
    caption: "Action trigger with support for loading and disabled states",
    states: [
      { key: "default", label: "Default" },
      { key: "loading", label: "Loading", note: "Shows spinner, disables interaction" },
      { key: "disabled", label: "Disabled", note: "Suppresses pointer events" }
    ],
    props: {
      default: { text: "Confirm Transfer", variant: "primary" },
      loading: { text: "Processing...", variant: "primary", loading: true },
      disabled: { text: "Confirm Transfer", variant: "primary", disabled: true }
    }
  }
];
```

### Validation Rules
- **`id`**: Unique, kebab-case, permanent (used in URLs and test IDs).
- **`states`**: At least one state required. A component with only one state is usually a bug in enumeration.
- **`props`**: Every declared state key must map to props or explicitly declare `{ via: "props" }`.

---

## 4. URL State & Descriptor Grammar

The stories search input accepts natural keywords or typed descriptors (`@key: value`), which synchronize directly with URL query parameters:

| Descriptor | URL Parameter | Function |
|---|---|---|
| `@state: disabled` | `?show-only=disabled` | Shows only components possessing that state, displaying that state card |
| `@state: loading, error` | `?show-only=loading,error` | Shows union of those states |
| `@id: button` | `?id=button` | Filters to that specific component across all its states |
| `@dir: rtl` | `?dir=rtl` | Switches directional facet |
| `@theme: dark` | `?theme=dark` | Switches theme facet |
| `@density: compact` | `?density=compact` | Switches layout density facet |
| *Free text query* | `?q=transfer` | Filters components by title, caption, or prop values |

---

## 5. Automated State Coverage & Verification

Run verification using `scripts/stories_check.mjs` (or inline audit):
1. **Unreachable states:** Any state listed in `states[]` that has no distinct visual props or render path is flagged.
2. **Duplicate cards:** Two cards rendering identical markup or styles are rejected.
3. **Facet verification:** All components must render cleanly across `rtl`/`ltr` and `dark`/`light`.
