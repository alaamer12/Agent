# The Dev Dock — one home for every prototype control

Loaded when scaffolding any prototype project, and whenever tempted to render a control that
manipulates the *prototype* rather than doing the *product's* work.

## The rule

**A prototype is a projection of the product, not a place to add product functionality.** Every
meta-control — the `?filled` data toggle, story inspection tools, cross-app navigation, font and
theme pickers, viewport info, state shortcuts — lives in exactly one component,
`assets/dev-dock/devdock.js`, or in the URL. A page's render template emits **zero** meta-control
UI.

The failure this kills is measured, not hypothetical: in a generated 42-page prototype the
sparse-state toggle link — "↺ clear data", a `<a>` with `href="?"` — was pasted into **8 page
content templates**, inside the header block above each `<h1>`, complete with the full
`inline-flex items-center gap-1.5 px-4 py-2 rounded-full bg-slate-100 …` class soup repeated
verbatim 8 times. Eight edits to change the wording; it had already drifted (one copy lost its
suffix). That link is prototype chrome: it should never have existed inside a page at all.

Two corollaries:

- **The dock is mounted, never written.** Copy `devdock.js` into the project (`shared/js/` in
  multi-app, `js/` in single-app) and load it on every page. Do not re-implement its pill,
  panel, or tabs per page or per app.
- **No per-page toolbars.** The older pattern of body-injected chrome (`sy_toolbar` bottom-left,
  apps switcher bottom-right) is retired: those tools are dock tabs now. Their **URL params are
  unchanged** — `sy_*`, `apps_toolbar`, `filled` remain the contracts; only the UI moved.

## The wiring contract

The dock and the project never call each other's internals:

| concern | owner |
|---|---|
| what the controls look like, where the dock sits, keyboard toggle | `devdock.js` |
| what the params mean, parsing, re-render on change | the project's state helper (`_app.js` / `_app_core.js`) |
| the current state itself | **the URL** — single source of truth |

- Dock controls write query params via `history.replaceState` + a dispatched `popstate`, so a
  page using the standard `mountState` contract re-renders with no reload. If a project listens
  only on load, the change lands on next navigation — still correct; never let the dock mutate
  project DOM to fake reactivity (except `--font`/`data-theme`, which it owns, see below).
- Every value the dock shows is read back from `location.search` — after `popstate`/`hashchange`
  the open panel re-renders, so the URL stays authoritative even when the person edits it by hand.
- `?dock=hide` removes the dock for clean screenshots and gallery iframes. The gallery itself
  never mounts a dock inside screen previews.

## Tabs that ship in the template

| tab | writes | notes |
|---|---|---|
| **States** | `?filled=1` on/off; shows every current param; copy-URL; reset | per-page state trees go in project-registered tabs, never in page content |
| **Fonts** | `?font=<Family>`, plus `--font` on `<html>` live | ten curated options; RTL documents get the Arabic-capable set (Cairo, Tajawal, IBM Plex Sans Arabic, …); `?fonts=ar` forces it on an LTR page. Names are validated against the curated list before any network fetch. |
| **Story tools** | `sy_bg`, `sy_grid`, `sy_outline`, `sy_inspect` | UI only — the stage mechanism stays in the project's story isolation code |
| **Apps** | navigation to sibling apps | configure `window.DevDockInit = { apps: [{name, url, current}] }` before the script loads |
| **Theme** | `?theme=light|dark`, plus `data-theme` on `<html>` live | pairs with the `[data-theme]` token blocks required by `zero-duplication.md` |
| **Dock** (bottom) | — | shortcuts, persistence notes, extension API |

The font and theme tabs apply their values live because those are CSS-level side effects with no
project mechanism to delegate to; `devdock.js` self-applies them from the URL at boot, so a shared
`?font=Cairo&theme=dark` URL reproduces exactly. Everything else is param-writing only.

## Mounting

Script tag order in every page's thin HTML, after the app's own modules:

```html
<script type="module" src="/js/_app.js"></script>   <!-- or the page module -->
<script src="/shared/js/devdock.js"></script>
```

Plain `<script>` (not module) so it mounts regardless of module timing, last so `body` exists.
`window.DevDockInit` must be set before that tag. In multi-app suites one copy lives under
`shared/` and every app loads it with the same `DevDockInit.apps` list — one dock configuration,
N apps.

## Extending without duplicating

A page with a rich state tree (the `?open=loading&loading=header` kind) registers a tab instead
of rendering controls:

```js
DevDock.registerTab({
  id: 'users-states', label: 'Users states', icon: 'box',
  sub: () => new URLSearchParams(location.search).get('status') || 'default',
  render: () => /* rows/switches that call DevDock.params.write({ status: v || null }) */,
});
```

That is the entire sanctioned way to add prototype UI. If what you are about to render is a
control *about the prototype* — toggle, switcher, picker, debug ribbon — it is dock content, or
it is nothing (a bare URL param is a perfectly good interface). If it is part of the product's
own surface (a real filter, a real settings control), it belongs in the page — the test is
"would this control exist in the shipped product?"

## Persistence split

Dock ergonomics (edge, position, panel size, last tab) persist in `localStorage` — they are
preferences of the person at the machine. Prototype state (data, theme, font, story, tools)
persists in the URL — it is reproducible for anyone who opens the link. Never invert this: a
`filled` choice kept only in localStorage makes shared URLs lie about what they show.