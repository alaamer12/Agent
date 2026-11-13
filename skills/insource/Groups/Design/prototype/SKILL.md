---
name: prototype
description: "Interactive JS-rendered design prototypes with URL-driven states and component stories. Supports single apps and multi-app suites. Features: clean-URL dev server, thin HTML with JS DOM generation, per-component state trees via query params (Unicode-safe, Arabic values included), ?filled seeded stress testing, in-page story isolation (?story_id=), multi-state component catalogs (/stories), a unified floating Dev Dock owning every prototype control (declared state pickers, story/component picker, stage tools, 10-font picker, theme switch, live palette token browser with adaptive brand accent, cross-app switching, viewport readout) so screens stay chrome-free, designed empty/loading/error surfaces, and zero-duplication guards enforcing tokens, component classes, and a shared ui.js builder catalog. Triggers: prototype this, make this a prototype, /prototype components, stories gallery, dev dock, dedupe prototype styles."
when_to_use: Build or extend interactive, URL-driven prototypes, audit existing mockups for dead controls, or generate multi-state component catalogs and story isolation links.
argument-hint: "[screen or app name] [topology or mode]"
---

# prototype — JS-rendered, modular, URL-driven design prototypes

A prototype project looks real and every one of its meaningful states is reproducible by **opening a URL** — `/funds?tab=transactions&status=pending` renders exactly that screen state, no clicks, forever, shareable. There is no backend: dynamic state is exposed through query parameters.

```
pages (thin HTML) ──► js modules ──► URL query state helper ──► live reproducible screen
components        ──► ?story_id=  ──► in-page isolation     ──► neutral inspection stage
registry          ──► /stories    ──► multi-state catalog   ──► component x state matrix
```

## Core Tenets

1. **Thin HTML Entries:** Pages have minimal markup (`data-page`, metadata, scripts). JS modules build and control DOM.
2. **Central State Helper:** `_app.js` owns state parsing, sync, history, and validation. Pages never touch `URLSearchParams` directly.
3. **Per-Component State Trees:** Every interactive mode and sub-state is queryable (`?open=loading&loading=header`).
4. **Data Fidelity (`?filled`):** Sparse defaults; `?filled` (or `?filled=<seed>`) renders full seeded-random datasets for stress testing.
5. **Component Story Isolation:** Every interactive component has `data-story="<id>"` and `data-testid="<id>"`. Inspectable in-page via `?story_id=<id>`.
6. **Component Stories Catalog:** Unified `/stories` or `index.stories.html` driven by `stories.registry.js` with `@state:` descriptor filters (`?show-only=disabled`).
7. **One Dock, Zero Page Chrome:** Every prototype-meta control — `?filled` toggle, story tools (`sy_*`), font picker (`?font=`), theme (`?theme=`), cross-app navigation — lives in the single `devdock.js` instance or the URL. A page's render template emits **no** meta-control UI; a prototype is a projection of the product, not a place to add product functionality ([`references/prototype-dock.md`](references/prototype-dock.md)).
8. **Single-Owner Patterns:** Any visual pattern used twice exists in exactly one place — token, component class, or `ui.js` builder. Extend `ui.js` first; never paste class strings. `scripts/guards.mjs` measures it ([`references/zero-duplication.md`](references/zero-duplication.md)).
9. **Every State a Surface, Every Width Honest:** empty, zero-result, loading, and error are *designed* screens (recognition + path + reassurance, builder-enforced), never white space; every region of every state carries full plausible product content — sparse means few real rows, never blank; each route holds at its pinned viewport extremes, checked in the dock's Viewport tab, and mobile is framed by presentation, never by the page or by "resize your window" ([`references/state-surfaces.md`](references/state-surfaces.md), [`references/viewport-frames.md`](references/viewport-frames.md)).

---

## Architecture Layouts

- **Topology A (Single-App):** `pages/`, `js/` (`_app.js`, `specs.js`, `<page>.js`), `css/` (`theme.css`, `_app.css`, `<page>.css`), and `serve.mjs`.
- **Topology B (Multi-App Suite):** `shared/` (`css/theme.css`, `js/_app_core.js`, `glyphs.js`) + `apps/<app>/` (`pages/`, `js/`, `css/`). Details in [`references/multi-app-scope.md`](references/multi-app-scope.md).
- **Component Stories Catalog:** Added alongside pages (`stories.registry.js`, `stories.js`, `index.stories.html`). Details in [`references/component-registry-stories.md`](references/component-registry-stories.md).

---

## References & Assets

Read the reference file matching what you are about to build:

| Reference | Scope | Read When |
|---|---|---|
| [`references/workflow.md`](references/workflow.md) | Pre-build questionnaire, step-by-step authoring workflow, and verification checklist | Before starting any prototype or audit |
| [`references/prototype-dock.md`](references/prototype-dock.md) | The unified Dev Dock: the chrome rule, URL wiring contract, font/theme pickers | Scaffolding any project — or the moment you would render a control about the prototype inside a page |
| [`references/zero-duplication.md`](references/zero-duplication.md) | Three-layer styling (tokens → component classes → utilities), the Palette Law, and the `ui.js` builder catalog | Before writing the first page module of a multi-page prototype; on any pattern's second use |
| [`references/state-surfaces.md`](references/state-surfaces.md) | Anatomy of empty/zero-result/loading/error/forbidden states + content fidelity: designed surfaces, never blank screens or placeholder text | Before writing any non-happy path; before declaring any page done |
| [`references/query-param-states.md`](references/query-param-states.md) | URL-state contract: state trees, sub-states, naming, sync/history, ?filled rules | Before writing any state or specs code |
| [`references/story-isolation.md`](references/story-isolation.md) | In-page story isolation (?story_id=), staging canvas, and toolbox (sy_*) | Building any component or page module |
| [`references/component-registry-stories.md`](references/component-registry-stories.md) | Component registry, multi-state catalog (/stories), ?show-only= descriptors | Building or reviewing component galleries |
| [`references/multi-app-scope.md`](references/multi-app-scope.md) | Multi-app suites, portals, responsive surface branching, floating app switcher | Setting up multi-app or multi-surface projects |
| [`references/libraries.md`](references/libraries.md) | CDN-first policy for icons, charts, dates, animation, and UI utilities | Scaffolding libraries and visual elements |
| [`references/gallery-index.md`](references/gallery-index.md) | Root index.html gallery anatomy, max 3 columns, live preview scaling | Any prototype with 2+ screens |
| [`references/viewport-frames.md`](references/viewport-frames.md) | Device viewports, frameless presentation, mobile vs. desktop dimensions | Sizing screens and viewports |
| [`references/dead-control-audit.md`](references/dead-control-audit.md) | Audit & wiring of static/dead clickable elements in existing mockups | Fixing dead controls in legacy files |
| [`references/feedback-heuristics.md`](references/feedback-heuristics.md) | Affordance mapping, interactive feedback, toasts, sheets, dialogs | Wiring interaction responses |
| [`scripts/stories_check.mjs`](scripts/stories_check.mjs) | Automated validator for component stories registry and state coverage | Verifying component catalogs |
| [`scripts/guards.mjs`](scripts/guards.mjs) | Duplication guards: `dupes`, `tokens`, `svg`, `onclick` — reporting or `--strict` | Before writing page two; before declaring any batch done |
| [`assets/starter/`](assets/starter/) | Working starter prototype project with testable state helpers | Starting a new single-app prototype |
| [`assets/dev-dock/`](assets/dev-dock/) | `devdock.js` — the unified prototype chrome, copy into the project and mount on every page | Any project with meta-controls (states, tools, fonts, theme, apps) |
| [`examples/dedupe-content-head.md`](examples/dedupe-content-head.md) | Worked before/after of a page head: glow + pasted toggle + 26-copy card | When the abstraction in zero-duplication.md needs a concrete shape |
| [`assets/stories-templates/`](assets/stories-templates/) | Ready templates for stories shell, registry, and component renderers | Scaffolding component story catalogs |
