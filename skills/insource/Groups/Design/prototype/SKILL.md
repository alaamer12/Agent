---
name: prototype
description: 'Build interactive design prototypes as small JS-rendered web projects. HTML pages are thin entries (meta/links/data-page; JS builds the UI); js/ and css/ split shared layers (_app.js, specs.js, theme tokens) from per-page modules; a zero-dep dev server routes each page a clean direct URL working on entry, refresh, and query. State model: PER-COMPONENT STATE TREES — every component exposes modes + sub-states as params (?open=…, ?loading=header|all, ?error=kind); init via the same render path clicks use, write back preserving unrelated params, invalid values fall to defaults, push/replace history. ?filled[=seed] swaps sparse placeholders for a FULL seeded-random dataset, reproducible by URL. Clean code, not chaos: ~300-line files preferred; respect the project''s package manager per lockfile. Keeps: honest states (no fake skeletons), never-lorem copy, frameless viewports, specs-generated gallery chips, opt-in dead-control audit. Triggers: prototype this app/idea, make this a prototype, design review links.'
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

Illustrative layout — the file *roles* are the contract; names follow the
prototype's actual subject (the starter happens to demo a funds/NAV app —
renaming its pages, data, and copy to your subject is part of scaffolding):

```text
prototype/
├── package.json          # scripts + (minimal, justified) dependencies
├── serve.mjs             # zero-dep dev server: clean-URL routing
├── index.html            # entry/landing — usually the gallery
├── pages/
│   └── <page>.html       # THIN entry: meta, links, body[data-page], scripts
├── js/
│   ├── _app.js           # shared bootstrap + CENTRAL state helper
│   ├── specs.js          # per-page state trees + gallery previews (pure data)
│   ├── <shared>.js       # feature modules: glyphs, charts, tables…
│   └── <page>.js         # page module: builds + owns its screen
├── css/
│   ├── theme.css         # tokens: colors, type, spacing — loaded first
│   ├── _app.css          # app-wide layout + shared components
│   └── <page>.css        # page-specific — loaded after app css
└── assets/               # fonts and system assets
```

1. **Minimal HTML pages.** Each page HTML holds only document metadata,
   stylesheet references, `<body data-page="…">`, a `<noscript>`, and the
   script tags that initialize it. **No screen markup in HTML** — the DOM,
   layout, and UI states are generated and controlled by the page's JS
   module. Example file names are illustrative; adapt names and load
   strategy per project, the principle is fixed.
2. **Shared vs page code.** `_`-prefixed files (`_app.js`, `_app.css`) are
   the application layer shared across pages (a convention identifying
   app-level files — name shared modules by role, the prefix isn't a
   mandate on all of them). Page modules own their DOM generation,
   interactions, rendering, and state behavior. Reusable functionality
   (charts, glyphs) gets its own module the moment it would otherwise be
   duplicated — prefer explicit imports/exports (ES modules) over accidental
   globals or script-load-order tricks.
3. **CSS layers, deliberate order:** `theme.css` (tokens) → `_app.css`
   (shared) → `<page>.css` (scoped, never leaking into other pages). No
   duplicated rules, no unnecessary specificity.
4. **`package.json` + dev server** (§Routing). Simplest suitable tooling —
   no framework, bundler, or dependency unless the project actually needs
   it; the starter's zero-dep server is the default.
5. **`index.html`** is the landing/gallery entry consistent with the
   project's navigation design — never a mandatory gate in front of other
   pages.

## Routing — clean, direct URLs

Every page answers a clean URL: `/funds` → Funds, `/dashboard` → Dashboard.
Direct entry, browser refresh, and query parameters must all work. Naming a
file `funds.html` does **not** make `/funds` work — wire routes/rewrites
(`/<name>` → `/pages/<name>.html`, query string preserved) in the dev
server (starter `serve.mjs` does exactly this). Cross-page links are real
`<a href="/funds">` navigation, not click-driven JS routing — except where
a flow genuinely lives inside one page's states.

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

## Workflow

1. **Understand** — what screens/flows/states, from the request and any
   reference material. One-line restatement back, not interrogation; ask
   only when *what the screen is or does* is genuinely ambiguous. Ground
   every label in real subject matter: plausible data, product vocabulary —
   **never Lorem ipsum or "Item 1 / Item 2"**.
2. **Pin viewports** — default desktop; frameless always (dimensions and
   affordance rules: [`references/viewport-frames.md`](references/viewport-frames.md)).
   The screens-vs-states test survives the redesign: if two "states" have
   different headers and different primary content structure, they are
   distinct **pages** — own page module + own URL — not one page with a
   `?tab=` router in disguise.
3. **Scaffold** — copy the structure from `assets/starter/` (verified
   working: thin pages, modules, CSS layers, clean-URL server, tested state
   helper); fill `package.json` scripts and routes for every page.
4. **Build pages** — thin HTML entry + page module owning DOM and
   interactions; extract shared code on first duplication; style through the
   CSS layers. **A prototype licenses fake data, not chaos code** — write it
   as if it will be maintained: small functions, clear names, pure helpers,
   IIFEs and structuring tricks welcome where they clarify; keep files
   **under ~300 lines as a strong preference**, splitting by responsibility
   (section renderer, data module, state wiring) when one outgrows that.
   (A CDN utility framework remains an option where it genuinely
   helps — not a default; own tokens live in `theme.css`.)
5. **Wire URL state** — §URL-driven state, through the central helper.
6. **Gallery** — 2+ screens ⇒ root `index.html` shows every screen live and
   every state as chips driving iframe URLs
   ([`references/gallery-index.md`](references/gallery-index.md), adapted
   to clean URLs here). Skip for a single screen.
7. **Verify, then deliver** — checklist below; save under
   `design/<project-slug>/` unless a path is named; use whatever
   file-presentation mechanism the environment actually offers (check,
   don't assume).

## Verification (before claiming done)

- The configured dev command starts cleanly (run it).
- Every page URL works **directly**, with a query string, and on refresh
  (`curl -o /dev/null -w "%{http_code}"` per route at minimum).
- HTML entries stay thin: meta/links/`data-page`/scripts only.
- Boundaries respected: no page-specific rule in `_app.css`; no chart/glyph
  logic outside its module.
- Each meaningful state: URL-only load renders it; the equivalent click
  writes the URL; composed params work; removing one preserves others;
  invalid values fall back without breaking render; back/forward restores
  state. `?filled` and `?filled=<seed>` render full datasets, and the same
  seed reproduces the same rows on refresh.
- **Force every gallery chip and look at the render** (browser or
  screenshot) — a state is verified when *seen*, not when coded. Feed
  hostile input too: an unknown param value, a 90-character name, a missing
  field — it must render as unknown, never crash and never fabricate a
  normal-looking row.
- Tests run through the project's package manager (`bun test` / `pnpm test`
  / `npm test` per lockfile); if the starter's state helper was modified:
  its tests still pass (defaults, validation, preservation, history
  policy — reuse them as the harness for project copies).
- Migration jobs: spot-check the design against what it modeled —
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
| Data fill | sparse realistic placeholders by default; `?filled[=seed]` renders a FULL seeded-random dataset (reproducible by URL) |
| Tooling commands | respect the project's package manager — detect from the lockfile (`bun.lockb`→bun, `pnpm-lock.yaml`→pnpm, `yarn.lock`→yarn, else npm); starter scripts are PM-agnostic |
| Component states | EVERY mode + sub-state of every interactive component queryable (`?open=loading&loading=header`) |
| Output location | `design/<slug>/` — the default; an explicit user path always wins |
| Placeholder content | realistic, subject-grounded — never Lorem |

## References & assets

Read the one whose trigger matches what you're about to write; nothing else
needs reading up front.

| File | Owns | Read when |
|---|---|---|
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
