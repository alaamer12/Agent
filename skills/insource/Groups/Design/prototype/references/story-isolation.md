# Story Isolation — Rendering Single Components by URL

> **What this owns:** The universal Story Isolation contract in the `prototype` skill: how every interactive or visual component declared in a prototype carries a `data-story` (and `data-testid`), how `?story_id=` isolates one or more components on a neutral stage, how state query parameters compose with story isolation, and the built-in inspection toolbox (`sy_*`).

---

## 1. The Core Idea

In a `prototype` project, reviewers, developers, and visual test suites must be able to inspect **any single component in isolation**, directly by URL, without clicking through pages or mounting the entire application shell:

- **No `story_id` in URL:** The application renders normally.
- **`?story_id=navbar`:** Only the navbar renders, centered on a neutral staging background.
- **`?story_id=button&story_id=modal` (or `?story_id=button,modal`):** Both units render, stacked vertically on the stage.
- **`?story_id=` (empty):** Displays an index of all available stories on that page.
- **`?story_id=unknown`:** Renders a clean not-found notice with links to all registered stories.

The component stays inside the real application's code and styling sheets (`theme.css`, `_app.css`, `<page>.css`), so what renders in isolation is **pixel-identical to what ships in the live app**.

---

## 2. Every Component MUST Have a `data-story` ID

When authoring DOM inside page modules (`<page>.js`) or shared components:

```javascript
// Example: Mark every testable unit with data-story and data-testid
`<header class="topbar" data-story="topbar" data-testid="topbar">...</header>`
`<nav class="tabs" data-story="tabs" data-testid="tabs">...</nav>`
`<div class="filters" data-story="filters" data-testid="filters">...</div>`
`<table class="funds-table" data-story="funds-table" data-testid="funds-table">...</table>`
`<div class="sheet" data-story="bottom-sheet" data-testid="bottom-sheet">...</div>`
`<div class="modal" data-story="modal" data-testid="modal">...</div>`
```

### The ID Naming Discipline
1. **Lowercase and hyphenated**: `topbar`, `tabs`, `bottom-sheet`, `transaction-modal`, `filter-strip`.
2. **Never differentiate by case alone**.
3. **Never end in `-component`**: accept it if supplied in the URL (`?story_id=topbar-component`), but canonical IDs omit it.

---

## 3. The Resolution Algorithm

Before event listeners attach, the shared state bootstrap in `_app.js` runs the story resolution pass:

```javascript
export function normalizeStoryId(raw) {
  return String(raw || "")
    .trim()
    .replace(/^["'\s]+|["'\s]+$/g, "")
    .toLowerCase()
    .replace(/-component$/, "");
}

export function parseStoryIds(params) {
  const ids = [];
  const rawList = params.getAll("story_id");
  for (const item of rawList) {
    for (const piece of item.split(",")) {
      const id = normalizeStoryId(piece);
      if (id && !ids.includes(id)) ids.push(id);
    }
  }
  return ids;
}
```

### Key Rules
- **Case-insensitive & quote-tolerant**: `?story_id=TopBar`, `?story_id="topbar"`, and `?story_id=topbar-component` all resolve to `topbar`.
- **Repeated parameters and comma-separated lists are both valid**: `?story_id=a,b&story_id=c`.
- **Order is preserved; duplicates are dropped**: Renders in the exact sequence requested in the URL.
- **Partial matches degrade gracefully**: If `?story_id=topbar,missing` is given, `topbar` renders below a notice that `missing` was not found.
- **Guarded event wiring**: Every component's event setup must guard for the element's existence (`if (!el) return;`) so event wiring never crashes when non-target components are omitted from the stage.

---

## 4. Staging & Neutral Canvas

When `story_id` is present, the app shell is swapped for a dedicated stage (`#stage` with `data-testid="story-root"`):

```css
#stage {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: var(--space-4, 32px);
  align-items: center;
  justify-content: center;
  padding: 32px;
  background: repeating-conic-gradient(#e4eaf1 0 25%, #eef2f6 0 50%) 0 0/24px 24px;
}
#stage > * {
  max-width: 100%;
}
#stage .nav, #stage header {
  position: relative !important; /* neutralize fixed/sticky positioning in isolation */
  top: auto !important;
}
```

---

## 5. Capturing Component States (Story + Component State Composition)

Story isolation composes directly with the URL-state contract:
- `?story_id=bottom-sheet&open=loading&loading=header` → Renders **only the bottom sheet**, in its partial header-loading shimmer state!
- `?story_id=bottom-sheet&open=error&error=permission` → Renders **only the bottom sheet**, in its trading permission error state!
- `?story_id=funds-table&filled=42&sort=nav` → Renders **only the funds table**, stress-tested with the full seeded dataset sorted by NAV!

This allows visual regression tools (Playwright, Puppeteer) or reviewers to capture single components in precise interactive states with clean, small screenshots.

---

## 6. The Story Toolbox (`sy_*` URL Parameters)

All staging tool configurations live entirely in URL query parameters, bookmarkable and test-controllable. **These params are the contract; the interactive UI that writes them is the Dev Dock's Story tools tab** ([`prototype-dock.md`](prototype-dock.md)) — a page module never renders toolbox buttons itself. The `mountToolbox()` body-injected toolbar in `assets/starter/` predates the dock and remains a working fallback for its params.

| Parameter | Values | Purpose |
|---|---|---|
| `sy_bg` | `checker` (default), `light` (`#ffffff`), `dark` (`#14161a`), or any `#hex`/CSS color | Stage background for contrast & transparency checks |
| `sy_grid` | `1` (8px grid) or `<px>` (e.g. `16`) | SVG overlay grid (major lines every 5x) for alignment |
| `sy_outline` | `1` | Outlines all DOM elements on the stage to debug layout/margins |
| `sy_inspect` | `1` | Hover highlights element dimensions; click copies CSS selector |
| `sy_toolbar` | legacy: `open`, `hide` (or `0`), default `closed` | Former bottom-left floating toolbar toggle — superseded by the dock; `?dock=hide` removes all prototype chrome for clean capture |

Example: `http://localhost:5173/funds?story_id=topbar&sy_bg=dark&sy_grid=16`
