# Project architecture — thin pages, owned modules, layered CSS, real routes

> **What this owns:** the concrete shape of the files and boundaries in
> §Architecture of SKILL.md — single-app vs multi-app suite layouts,
> the page-entry HTML template, page-module conventions, the shared-module
> split, CSS layer rules, and server/routing options. The URL-state
> semantics are [`query-param-states.md`](query-param-states.md)'s;
> multi-app discovery is [`multi-app-scope.md`](multi-app-scope.md)'s;
> viewport mechanics are [`viewport-frames.md`](viewport-frames.md)'s.
> The runnable truth is `assets/starter/` — read this with it open.

## Single-App vs Multi-App System Topologies

The skill scales cleanly from a focused standalone prototype to an enterprise multi-application ecosystem sharing a unified design system:

### 1. Single-App Topology (Default for standalone products)
```text
prototype/
├── package.json
├── serve.mjs             # Routes: / -> index.html, /<page> -> pages/<page>.html
├── index.html            # Screen gallery
├── pages/
│   └── <page>.html       # Thin entry
├── js/
│   ├── _app.js           # Central state helper + app bootstrap
│   ├── specs.js          # Component state specs + gallery previews
│   └── <page>.js         # Page DOM builder
└── css/
    ├── theme.css         # Tokens (colors, typography, spacing)
    ├── _app.css          # Shared primitives & app layout
    └── <page>.css        # Page-scoped styles
```

### 2. Multi-App System Suite Topology (For suites, admin/operator/consumer portals, or multi-surface hybrid apps)
```text
prototype/
├── package.json          # Runs and tests the complete suite
├── serve.mjs             # Routes: / -> index.html, /<app>/<page> -> apps/<app>/pages/<page>.html
├── index.html            # Multi-App System Gallery (all apps, screens, & chips)
├── shared/               # Unified Design System & Common Primitives
│   ├── css/
│   │   ├── theme.css     # Base system tokens (brand palette, typography, radii, z-index)
│   │   └── _base.css     # Base resets, typography, global utilities
│   └── js/
│       ├── _app_core.js  # Pure state helper (mountState, parse, patch, toQuery)
│       ├── glyphs.js     # Fallback SVG icons — only used when CDN is banned (see libraries.md)
│       └── utils.js      # Seeded PRNG for ?filled, formatting helpers
└── apps/
    ├── <app-1>/          # e.g., admin-dashboard
    │   ├── pages/
    │   │   └── <page>.html
    │   ├── js/
    │   │   ├── _app.js   # Imports _app_core.js, wraps admin shell & nav
    │   │   ├── specs.js  # Admin component state specs
    │   │   └── <page>.js # Admin page DOM builder
    │   └── css/
    │       ├── _app.css  # Admin shell layout + optional theme overrides
    │       └── <page>.css
    └── <app-2>/          # e.g., operator-console (e.g. high-density dark mode) or mobile
        ├── pages/
        ├── js/
        └── css/
```

Both topologies honor the same immutable laws: thin HTML pages, DOM owned by JS, URL-driven component state, and zero-dependency clean routing.

## The thin page entry

Everything between `<body>` and `</body>` in a page file is structural
decoration, not content:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Funds · NAV Intelligence (prototype)</title>
  <link rel="stylesheet" href="/css/theme.css">
  <link rel="stylesheet" href="/css/_app.css">
  <link rel="stylesheet" href="/css/funds.css">
</head>
<body data-page="funds">
  <noscript>This prototype requires JavaScript to render its interface.</noscript>
  <script type="module" src="/js/_app.js"></script>
  <script type="module" src="/js/funds.js"></script>
</body>
</html>
```

- `data-page` is the only "content" the HTML declares — the renderer, the
  state helper, and the gallery can all key off it.
- No layout divs, no nav, no "just the header in HTML for SEO" exceptions.
  The JS builds the DOM; that is what buys generation, modification, and
  UI-state control flexibility. A screen that "would be easier in HTML" is
  the exact case the architecture rejects.
- Root-level paths (`/css/…`, `/js/…`) assume the server routes from the
  project root — opening files via `file://` is not the target workflow;
  direct links to pages with query strings must work, which only a routed
  server guarantees.

## Page modules

`js/<page>.js` owns its screen end to end:

```js
import { mountState } from "./_app.js";        // the central state helper
import { sparkline } from "./charts.js";
import { icon } from "./glyphs.js";

const spec = { /* this page's state spec — see query-param-states.md */ };

function render(state) {
  document.body.querySelector(".app")?.remove();
  const app = buildShell(state);              // DOM generation lives here
  // ... tab bodies, rows built from placeholder data, charts via sparkline()
}

mountState(spec, render);                     // parse URL → render; clicks → patch+sync; popstate → render
```

Rules of ownership:

- DOM generation, event wiring, and page state behavior live **in the page
  module**. `render(state)` is the single update path — the URL bootstrap
  and every click run through it (one code path ⇒ pixel-identical states).
- A page never imports another page. Shared things move *out* to a feature
  module (`charts.js`, `glyphs.js`, `table.js`…), created at **first
  duplication**, not pre-emptively — a prototype is not a component library.
  Reusable chart logic duplicated across page files is the named failure
  this rule exists to kill.
- The underscore convention marks application-level shared files (`_app.js`,
  `_app.css`); other shared modules are plain feature names. Don't force
  every shared file to be `_`-prefixed — name by role.
- ES modules with explicit import/export; no globals except the ones
  `index.html`-style gallery embedding genuinely needs (keep those minimal
  and documented).

## CSS layers

Load order per page:
- **Single-App:** `theme.css` → `_app.css` → `<page>.css`.
- **Multi-App:** `/shared/css/theme.css` → `/shared/css/_base.css` → `/apps/<app>/css/_app.css` → `/apps/<app>/css/<page>.css`.

- `theme.css`: custom properties only — colors, type scale, spacing,
  radii, shadows, z-layers. Nothing with selectors beyond `:root` (and
  media-query variants of tokens). In multi-app suites, `shared/css/theme.css`
  defines the baseline brand tokens, while an app's `_app.css` or an
  app-specific theme sheet overrides tokens if that app has a distinct persona
  (e.g., operator console running high-density dark mode).
- `_app.css`: app-wide layout primitives and shared components (shell,
  header, buttons, cards, tables) — styles that genuinely belong to the
  application interface.
- `<page>.css`: page-scoped. Scope by the page root (`.page-funds …` — the
  class `mountState`/shell sets from `data-page`) so nothing leaks into
  other pages. No `!important` escalation, no redefining another layer's
  rule to "fix" order problems — fix the order or the ownership.

## Server & routing options

Requirements: serve statics, route `/<name>` → `pages/<name>.html`,
preserve query strings, `package.json` script to start it, and
direct-URL + refresh correctness. Simplest-suitable wins:

| Setup | When |
|---|---|
| **Starter `serve.mjs`** (zero deps, Node ≥ 18) | Default. Route map + statics + query-preserving rewrites in ~100 lines; `npm start` runs it. Automatically maps `/funds` → `pages/funds.html` (single app) or `/<app>/<page>` → `apps/<app>/pages/<page>.html` (multi-app). |
| Vite (dev server + build) | Only if the project genuinely needs HMR, TS, or a bundler — an added dependency must be justified, not assumed. |
| Any host with rewrite rules (Netlify/nginx/`_redirects`) | When deploying; mirror the starter's route table — `/funds /pages/funds.html 200` style. |

Anti-pattern to refuse: "the file is named funds.html so `/funds` works" —
it doesn't. Routing is configuration; make it explicit either way.

### package.json

```json
{
  "name": "<slug>-prototype",
  "private": true,
  "type": "module",
  "scripts": {
    "start": "node serve.mjs",
    "test": "node js/state.test.mjs"
  }
}
```

No dependencies unless justified. The `test` script matters: the state
helper's pure functions are copied per project and must stay verifiable.

## index.html & navigation

`index.html` is the entry per the project's navigation design — for 2+
screen sets it is the gallery (see gallery-index.md); for a single screen
it can simply redirect or be the screen itself. Pages cross-link with real
anchors (`<a href="/dashboard">`); the only JS-driven navigation is inside
one page's own states (tab/modal changes are `patch + sync`, not
route-changes). A page must never require visiting another page first.
