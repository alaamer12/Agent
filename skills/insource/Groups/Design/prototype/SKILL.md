---
name: prototype
description: 'Build interactive design prototypes as small JS-rendered web projects. Scales from single apps to multi-app system suites and multi-surface variations (e.g. desktop web, mobile viewports, operator/admin consoles) sharing a unified design system. HTML pages are thin entries (meta/links/data-page; JS builds the UI); js/ and css/ split shared layers (_app.js, specs.js, theme tokens) from per-page modules; a zero-dep dev server routes each page a clean direct URL working on entry, refresh, and query. State model: PER-COMPONENT STATE TREES — every component exposes modes + sub-states as params (?open=…, ?loading=header|all, ?error=kind); init via the same render path clicks use, write back preserving unrelated params, invalid values fall to defaults, push/replace history. ?filled[=seed] swaps sparse placeholders for a FULL seeded-random dataset, reproducible by URL. Clean code, not chaos: ~300-line files preferred; respect the project''s package manager per lockfile. Keeps: honest states (no fake skeletons), never-lorem copy, frameless viewports, specs-generated gallery chips, opt-in dead-control audit. Triggers: prototype this app/idea, make this a prototype, design review links.'
---

# prototype — JS-rendered, modular, URL-driven design prototypes

A prototype project looks real and every one of its meaningful states is
reproducible by **opening a URL** — `/funds?tab=transactions&status=pending`
renders exactly that screen state, no clicks, forever, shareable. There is
no backend and no real logic: dynamic-looking state is faked with
placeholder content *whose surface and triggers stay honest* and exposed
through query parameters. The architecture exists to serve that promise:
pages are thin, JS owns the DOM, shared code has one home, URLs route and
drive state.

**Two entry points.** Build/extend a prototype project — the default, the
workflow below. Or audit an **existing** HTML file whose controls look
clickable but do nothing — [`references/dead-control-audit.md`](references/dead-control-audit.md),
triggered by "this does nothing when clicked", "make this feel real",
"audit for dead clicks". Never run the audit on a prototype you just built.

When **migrating** an existing static mockup (e.g. a `design-mockup` set)
into this architecture: preserve its visual hierarchy, layout, typography,
spacing, colors, responsive behavior, interactions, and screen variations —
move markup generation into page JS modules, extract shared functionality,
split global vs page CSS, expose its meaningful states through params, and
treat "unnecessary rewrites that change the design or break working
behavior" as the failure mode this step exists to avoid.

## Architecture (the non-negotiables)

The architecture scales from a **Single App** to a **Multi-App System Suite** (e.g. admin dashboard + operator console + consumer web app, or multi-surface variations like mobile viewport vs desktop web) sharing a cohesive design system.

### Topology A: Single-App Layout (Default for standalone products)
```text
prototype/
├── package.json          # scripts + (minimal, justified) dependencies
├── serve.mjs             # zero-dep dev server: clean-URL routing (/ -> index.html, /<page>)
├── index.html            # entry/landing — usually the gallery
├── pages/
│   └── <page>.html       # THIN entry: meta, links, body[data-page], scripts
├── js/
│   ├── _app.js           # shared bootstrap + CENTRAL state helper
│   ├── specs.js          # per-page state trees + gallery previews (pure data)
│   ├── <shared>.js       # feature modules: CDN library wrappers, tables, charts init…
│   └── <page>.js         # page module: builds + owns its screen
├── css/
│   ├── theme.css         # tokens: colors, type, spacing — loaded first
│   ├── _app.css          # app-wide layout + shared components
│   └── <page>.css        # page-specific — loaded after app css
└── assets/               # fonts and system assets
```

### Topology B: Multi-App System Suite Layout (For suites & multi-role portals)
```text
prototype/
├── package.json          # scripts to run and test the complete suite
├── serve.mjs             # zero-dep multi-app clean routing (/<app>/<page>)
├── index.html            # Unified System Gallery (all apps, screens, state chips)
├── shared/               # Design System & Common Foundation
│   ├── css/
│   │   ├── theme.css     # Global brand tokens (palette, typography, radii)
│   │   └── _base.css     # Base resets, typography, shared utility classes
│   └── js/
│       ├── _app_core.js  # Pure state helper (mountState, parse, patch, toQuery)
│       ├── glyphs.js     # Fallback icons — only when CDN is banned; see references/libraries.md
│       └── utils.js      # Seeded PRNG for ?filled, formatting helpers
└── apps/
    ├── <app-1>/          # e.g., admin (desktop, wide tables, governance)
    │   ├── pages/
    │   │   └── <page>.html
    │   ├── js/
    │   │   ├── _app.js   # Imports _app_core.js, wraps admin shell & nav
    │   │   ├── specs.js  # Component state trees for this app's pages
    │   │   └── <page>.js # Page DOM builder
    │   └── css/
    │       ├── _app.css  # Admin shell layout + theme overrides
    │       └── <page>.css
    └── <app-2>/          # e.g., operator (high-density dark) or client surface (mobile/responsive)
        ├── pages/
        ├── js/
        └── css/
```

1. **Minimal HTML pages.** Each page HTML holds only document metadata,
   stylesheet references, `<body data-page="…">`, a `<noscript>`, and the
   script tags that initialize it. **No screen markup in HTML** — the DOM,
   layout, and UI states are generated and controlled by the page's JS
   module. Example file names are illustrative; adapt names and load
   strategy per project, the principle is fixed.
2. **Shared vs page code.** In single-app, `_`-prefixed files (`_app.js`, `_app.css`)
   are the application layer. In multi-app suites, `shared/` owns the common design
   system tokens, glyphs, and the core state engine; each app owns its specific
   shell, specs, and page modules. Reusable functionality gets its own module
   the moment it would otherwise be duplicated — prefer explicit ES module imports/exports.
3. **CSS layers, deliberate order:**
   - Single-app: `theme.css` (tokens) → `_app.css` (shared) → `<page>.css` (scoped).
   - Multi-app: `/shared/css/theme.css` (base tokens) → `/shared/css/_base.css` → `/apps/<app>/css/_app.css` (app shell & theme overrides) → `<page>.css`.
4. **`package.json` + dev server** (§Routing). Zero-dep local server routing direct
   clean URLs for both single and multi-app setups.
5. **`index.html`** is the landing/gallery entry. In a multi-app system, it acts
   as the **System Suite Gallery**, grouping screens by app and displaying
   each app's viewport aspect ratio and state chips.

## Routing — clean, direct URLs

Every page answers a clean URL:
- Single-app: `/funds` → Funds, `/dashboard` → Dashboard.
- Multi-app: `/admin/overview` → `apps/admin/pages/overview.html`, `/operator/queue` → `apps/operator/pages/queue.html`.
- Dual-realm & subdomains: support clean namespace paths (`/app/overview`, `/marketing/pricing`) and simulated subdomains via query parameter (`?subdomain=app|marketing|enterprise`).
Direct entry, browser refresh, and query parameters must all work. Wire routes/rewrites in the dev server (`serve.mjs`). Cross-page links are real `<a href="/admin/overview">` navigation, not click-driven JS routing — except where a flow genuinely lives inside one page's states.

**Cross-App Navigation Invariant**: Never put cross-app switcher buttons into the page's main content, header, or navigation bar (which must remain 100% authentic to that specific product). In multi-app prototypes, cross-app and variant switching is handled exclusively by a **floating button on the bottom right with an upward dropdown menu**, hideable via **`?apps_toolbar=hide`**. Read [`references/multi-app-scope.md`](references/multi-app-scope.md).

## URL-driven state — the core contract

**The unit is the component, not the screen.** Walk every interactive
component the design contains — bottom sheet, modal, dropdown, tab strip,
filter/sort/search set, wizard — and enumerate its **state tree**: the
modes it can be in (including *which variant* of its content shows) and
the sub-states inside each mode. Every meaningful node of that tree is
queryable:

```text
?open=plain|selection|loading|error          ← the sheet's modes
?loading=header|input-fields|all             ← sub-state while open=loading
?error=network|validation|permission         ← sub-state while open=error
?modal=transaction-details&transactionId=102 ← a component + its subject
```

A component whose internals have variants but exposes only an open/closed
flag has failed the contract. One cross-cutting param joins every page:

**`?filled` — data fidelity.** Default rendering carries *sparse*
placeholder data (a few rows, gaps, what an almost-empty product looks
like); `?filled` (optionally `?filled=<seed>` — any value picks that seed)
generates a FULL random dataset for stress-review: long tables, crowded
charts, wrapped names. The data must be *seeded* random, never unseeded —
an unseeded roll breaks the skill's first promise (the URL reproduces the
state exactly on refresh/share); `?filled=17` should look the same every
time it is opened.

Requirements on top of the tree:

1. **Initialize from the URL** on load — using the *same* render functions
   interactions use (one code path, so URL-triggered and click-triggered
   states are pixel-identical).
2. **Write back on interaction** — any current state is bookmarkable.
3. **Compose** — components coexist on one URL; updating one state
   **preserves unrelated** active params.
4. **Validate** — missing/invalid values fall to declared defaults; a
   hostile URL never fails to render.
5. **History** — push for discrete moves (sheet opens, tab switches);
   replace for continuous ones (search keystrokes); `popstate` re-applies
   so back/forward restore the expected UI.
6. **Centralize** — parsing, validation, reading, updating live in one
   shared state helper in `_app.js` (pure functions + thin DOM binding);
   state *trees* are declared as data in `specs.js`, one owner per page.
   No page ever touches `URLSearchParams`.

This is *complete control of meaningful states*, not a mandate to URL-ify
transient internals (hover, scroll offset, focus stay out). **Enumeration is
a hunt, not a recital**: the reference owns the derivation method — rotate
reviewer stances over each component, walk only the condition axes it
actually touches, admit a candidate only through the
evidence/reachability/distinctness/consequence filter (states whose recovery
doesn't differ merge), and fail closed on unknown values — the happy path is
never the fallback, and the gallery strip is the coverage matrix that proves
what was found. Param naming, collision namespacing, sub-state mechanics,
`?filled`, and the honest-state rules (shimmer only the region declared
loading; a state with no real trigger doesn't get a mockup) are owned by
[`references/query-param-states.md`](references/query-param-states.md) —
read it before writing state code.

## Story Isolation — Rendering Single Components by URL

**Every testable or interactive UI component MUST carry a `data-story="<id>"` attribute and a matching `data-testid="<id>"`**. Story isolation allows URL parameters to swap the entire page shell for one named component, or several, displayed alone on a neutral stage (`#stage`, `data-testid="story-root"`).

- **`?story_id=<id>`** renders only that component, centered on the stage.
- **Multiple components** can be requested via repeated params (`?story_id=topbar&story_id=modal`) or comma lists (`?story_id=topbar,modal`), stacked vertically in URL order.
- **`?story_id=`** (empty) lists all available stories on the page.
- **`?story_id=missing`** displays a helpful not-found box with the list of valid IDs.
- **State composition**: Story isolation composes with the component-state contract (`?story_id=bottom-sheet&open=loading&loading=header` renders *only the bottom sheet* in its partial header-shimmer state).
- **Resolution**: Normalization is case-insensitive, trims surrounding quotes (`"..."`, `'...'`), and strips any trailing `-component`.
- **Story Toolbox (`sy_*`)**: Staging tools are controlled via URL params: `sy_bg=checker|light|dark|<hex>`, `sy_grid=1|<px>`, `sy_outline=1`, `sy_inspect=1`, `sy_toolbar=open|hide`. Read [`references/story-isolation.md`](references/story-isolation.md).

## Workflow

1. **Pre-build questionnaire (Never-rush law)** — Ask every question below
   before writing a single file. Group them into one message; do not drip
   them one at a time. Skip a question only when the user's prompt already
   answers it unambiguously.

   **A. Screen inventory**
   - Which screens / pages should the prototype include? (If the user has not
     listed them, propose a complete set based on the product idea and ask
     for confirmation or additions before continuing.)
   - For each screen: what is its primary purpose and who is the persona?

   **B. Viewport & responsiveness**
   - Which viewport(s) are in scope?
     - Desktop only (default for dashboards / backoffice)
     - Mobile only (390 px, for native-app or PWA flows)
     - Tablet only (~768 px)
     - Multiple viewports — if so, should they share one responsive file or
       be separate surface variants (Topology B)?
   - If multiple viewports: does the product behave differently per surface
     (different nav patterns, density, layout) — or is it one responsive
     design scaling up?

   **C. App scope**
   - Is this a single standalone app, or a multi-role suite (e.g. admin +
     operator + consumer portals)? Read
     [`references/multi-app-scope.md`](references/multi-app-scope.md) for
     the full topology decision.

   **D. Libraries & dependencies**
   - Any restriction on external libraries or CDN? The default is **CDN
     libraries for everything** — icons, charts, date formatting, animation,
     grids, drag-and-drop, whatever the design needs. Hand-rolling any of
     these is not the default; it requires an explicit reason. See
     [`references/libraries.md`](references/libraries.md) for the catalog.
   - Are there specific libraries the product already uses, or that the
     user prefers (e.g. a particular icon set, a specific chart library)?

   **E. Design language**
   - Is there an existing design system, brand guide, or color palette to
     follow? If so, share it or describe its tokens.
   - Dark mode, light mode, or both?

   **F. Data & content**
   - What is the product's real vocabulary? (domain terms, entity names —
     never Lorem ipsum)
   - Any real data samples or schemas to seed placeholder content from?

   Once answers are in hand, state the architectural plan (topology,
   viewport list, screen list, library choices) in one concise paragraph and
   ask for a go/no-go before scaffolding.

   Ground every label in real subject matter — **never Lorem ipsum or
   "Item 1 / Item 2"**.
2. **Pin viewports & topologies** — Single-app uses Topology A; multi-app uses
   Topology B (`shared/` + `apps/<app>/`). Select viewports per app/surface:
   desktop (1280×800) for backoffice/dashboards, mobile (390×844) for native/PWA
   flows; frameless always ([`references/viewport-frames.md`](references/viewport-frames.md)).
   The screens-vs-states test: if two "states" have different headers and different
   primary content structure, they are distinct **pages** — own page module + own URL —
   not one page with a `?tab=` router in disguise.
3. **Scaffold** — copy from `assets/starter/` (or the multi-app layout in
   `multi-app-scope.md`); wire `package.json` scripts and route rewrites in `serve.mjs`.
4. **Derive states before building** — for every screen, walk each interactive
   component through its condition axes (data, provider, in-flight, viewer, time) and
   enumerate its **complete state tree**: default/sparse state, `?filled` state, loading
   sub-states, every error kind, empty, stale, partial, and permission variants. Write
   the full `specs.js` entries — including `filled: { default: null }` on every page
   spec and `?filled` gallery chips — **before** writing any screen DOM code.
   A `?filled` param without a seeded generator that produces a full realistic dataset
   (long tables, crowded charts, wrapped long names, adversarial rows) is not done.
   The same seeded generator must reproduce bit-for-bit identical output on every
   refresh and share.
5. **Build pages** — thin HTML entry + page module owning DOM and
   interactions; extract shared code to `shared/` on first duplication; style through
   the CSS layers. **A prototype licenses fake data, not chaos code** — write it
   as if it will be maintained: small functions, clear names, pure helpers,
   IIFEs and structuring tricks welcome where they clarify; keep files
   **under ~300 lines as a strong preference**, splitting by responsibility
   (section renderer, data module, state wiring) when one outgrows that.
   **Use real libraries for everything** — icons, charts, dates, animation,
   grids, drag-and-drop, any UI utility the design needs. Load them via CDN
   (`<script src="https://cdn.jsdelivr.net/...">` or importmap). Do not
   hand-roll what a library does better; a prototype that uses hand-drawn
   SVG icons or bespoke chart renderers looks immediately cheap. The rule
   inverts only when the user explicitly bans external dependencies — see
   [`references/libraries.md`](references/libraries.md). Own design tokens
   live in `theme.css` regardless of which libraries are loaded.
   Every screen must suppress its own scrollbar in the gallery preview context:
   the screen's `body` / scroll container must not display scrollbars inside
   the gallery iframe (`scrollbar-width: none; &::-webkit-scrollbar { display:none; }`
   on the scrolling element, or `overflow: hidden` when the content is not
   expected to scroll at preview scale).
6. **Wire URL state** — §URL-driven state, through the central helper.
7. **Gallery** — 2+ screens ⇒ root `index.html` shows every screen live and
   every state as chips driving iframe URLs
   ([`references/gallery-index.md`](references/gallery-index.md), adapted
   to clean URLs). In multi-app suites, group cards by application section with
   proper device aspect ratios. Skip for a single screen.

   **Gallery layout rules (non-negotiable):**
   - Use **at most 3 columns** for the screen grid (use `repeat(auto-fit, minmax(320px, 1fr))`
     with a `max-width` cap on the grid; never `minmax(240px, 1fr)` or narrower, which
     forces 4+ columns and crowds cards).
   - Each card must have enough breathing room — `gap` of at least 24px and card
     padding of at least 20px.
   - Every screen card's state strip must include a chip for **each state** derived in
     step 4, including the `Filled` chip (linked to `?filled=1`). The strip is the
     visible state coverage matrix — if a state isn't chippped, it wasn't built.

8. **Verify, then deliver** — mandatory checklist below (not a suggestion); save under
   `design/<project-slug>/` unless a path is named; use whatever
   file-presentation mechanism the environment actually offers (check,
   don't assume).

## Verification (mandatory — do not mark done until every item passes)

This is not a wishlist. Run every check; report any failure before delivering.

**Structural checks**
- The configured dev command starts cleanly (run it; show the terminal output).
- Every page URL works **directly**, with a query string, and on refresh
  (`curl -o /dev/null -w "%{http_code}"` per route at minimum).
- HTML entries stay thin: meta/links/`data-page`/scripts only.
- Boundaries respected: no page-specific rule in `_app.css`; no chart/glyph
  logic outside its module.

**State checks — test every state by URL, not by assumption**
- Open each screen's URL cold (no prior navigation). It renders without clicks.
- For every state chip in the gallery strip: click it, confirm the iframe URL
  updates, and **visually confirm the render changed** — a chip is verified when
  the state is *seen*, not when the code path exists.
- `?filled` and `?filled=<seed>`: opening either produces a **full** dataset —
  long tables, crowded content, wrapped long names. The same seed reproduces
  identical output on refresh and in a fresh browser tab. Bare `?filled` uses
  the project-default seed and also reproduces.
- Composed params work: set two independent component states simultaneously
  (`?tab=transactions&open=loading`); removing one preserves the other.
- Invalid/unknown param values fall back to declared defaults without breaking
  the render, throwing errors, or producing a blank page.
- Back/forward navigation restores the expected UI state.
- Feed hostile input: a 90-character name, a missing field, an unknown
  category value — it renders as unknown (em-dash, "Unknown", or the declared
  fallback), never crashes, never fabricates a normal-looking row.

**Gallery checks**
- The gallery has at most 3 columns; cards have visible breathing room (gap ≥ 24px).
- No scrollbar is visible inside any preview iframe (the scroll container inside
  the screen suppresses its scrollbar via `scrollbar-width: none` /
  `::-webkit-scrollbar { display:none }`).
- Every screen card's state strip has a chip for every state derived in step 4,
  including an `Empty` chip (default/sparse state) and a `Filled` chip
  (`?filled=1` or the project seed).
- The `Open Screen` link in each card carries the currently-selected state's
  query string, not just the base URL.

**Tests**
- Run the project's package manager test command (`bun test` / `pnpm test` /
  `npm test`); all pass. If the starter's state helper was modified, its tests
  still pass (defaults, validation, preservation, history policy).

**Migration jobs**
- Spot-check the design against what it modeled —
  *preserved* is the requirement, reinterpreted is the failure.

## Quick defaults reference

| Axis | Default when unstated |
|---|---|
| Rendering | DOM built by the page JS module; HTML = thin entry |
| Module style | ES modules, explicit imports/exports |
| CSS order & tokens | theme → _app → page; CSS custom properties |
| Server/tooling | zero-dependency local server with clean-URL routes |
| URLs | `/` gallery/landing; `/<page>` direct; states via query params |
| Viewport | desktop; frameless always |
| Screen vs state | distinct screen ⇒ own page+URL; component state ⇒ param |
| Data fill | sparse realistic placeholders by default; `?filled[=seed]` renders a FULL seeded-random dataset (reproducible by URL); **`filled: { default: null }` declared in every page spec; gallery carries a `Filled` chip** |
| `?filled` generator | seeded PRNG (never `Math.random()`); same seed = same rows always; includes adversarial rows (90-char names, missing fields, unknown categories) |
| Tooling commands | respect the project's package manager — detect from the lockfile (`bun.lockb`→bun, `pnpm-lock.yaml`→pnpm, `yarn.lock`→yarn, else npm); starter scripts are PM-agnostic |
| **Libraries** | **CDN by default for everything — icons (Lucide), charts (Chart.js), dates (Day.js), animation, grids, etc. Hand-rolling any of these requires an explicit user opt-out. See `references/libraries.md`.** |
| Component states | EVERY mode + sub-state of every interactive component queryable (`?open=loading&loading=header`); derived BEFORE screen DOM code is written |
| Output location | `design/<slug>/` — the default; an explicit user path always wins |
| Placeholder content | realistic, subject-grounded — never Lorem |
| Gallery columns | **max 3** (`repeat(auto-fit, minmax(320px, 1fr))`); never minmax < 300px which forces 4+ columns |
| Scrollbars in preview | suppressed on the screen's scroll container (`scrollbar-width:none; ::-webkit-scrollbar{display:none}`) — never visible inside gallery iframes |

## References & assets

Read the one whose trigger matches what you're about to write; nothing else
needs reading up front.

| File | Owns | Read when |
|---|---|---|
| [`references/multi-app-scope.md`](references/multi-app-scope.md) | Multi-app scope discovery, topology selection (single app, suite, multi-surface variations, dual-realm/subdomain branching ?subdomain=), shared design system contracts | Step 1, before any code or scaffolding |
| [`references/libraries.md`](references/libraries.md) | CDN-first library rule, catalog of recommended picks by category (icons, charts, dates, animation, grids…), loading patterns, fallback rules when deps are banned | Step 1 questionnaire (D) and step 5 (Build pages) |
| [`references/story-isolation.md`](references/story-isolation.md) | Story isolation: rendering one or more components by URL (?story_id=), data-story attributes, staging, toolbox (sy_*) | Building any component or page module |
| [`references/query-param-states.md`](references/query-param-states.md) | The URL-state contract: per-component state trees + sub-states, naming, central helper spec, sync/history/validation, honest-state rules | Before writing any state code |
| [`references/project-architecture.md`](references/project-architecture.md) | Thin-HTML page shape, module boundaries, CSS layering, server/routing options, package.json | Setting up or restructuring a project |
| [`references/viewport-frames.md`](references/viewport-frames.md) | Viewport dimensions, frameless rules, native affordances | Writing the page shell/renderer |
| [`references/gallery-index.md`](references/gallery-index.md) | Gallery anatomy, one-owner state table, iframe scaling, acceptance test | Any set of 2+ screens |
| [`references/dead-control-audit.md`](references/dead-control-audit.md) | Opt-in audit: detect platform → inventory → classify → wire → report | Only when asked to fix dead controls in an existing file |
| [`references/feedback-heuristics.md`](references/feedback-heuristics.md) | Affordance→component mapping, dropdown/toast patterns | During that audit |
| [`assets/starter/`](assets/starter/) | A verified working prototype project + `test.mjs` state-helper tests | Starting any new prototype |

**Update this table whenever a reference or asset is added, removed, or
renamed** — it is the only map of this skill, and a stale one is worse than
none.
