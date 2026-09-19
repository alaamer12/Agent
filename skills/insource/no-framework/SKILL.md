---
name: no-framework
description: >
  Build Single Page Applications using NoF (No Frameworks) — a lightweight architecture defaulting to VanJS (~1KB, fine-grained reactive UI) and Navigo (~4KB, client-side routing), no React/Vue/Angular. Use this whenever building or scaffolding a small-to-medium SPA that should stay framework-free. Requires verifying current library versions and API compatibility (VanJS, Navigo, and any other library used) before writing code, since pinned versions in this skill's own examples can go stale. Any library that works as plain vanilla JS without a framework runtime is fair game within this architecture, not just VanJS/Navigo — including CSS tooling like Less/Sass when a project's needs justify it. Covers project scaffolding, state/derive patterns, routing, component architecture, rendering conventions, debugging/profiling, and shipping to production (no-bundler and Vite build paths). Not the right fit for very large multi-page enterprise apps, large teams, or apps needing complex animation libraries — see the "when to use" section for the actual line.
---

# NoF: No Frameworks Architecture

## Core philosophy

Simplicity over complexity, performance by default, full control over the
codebase. If something can be done with less code while staying just as
clear, do it that way — don't reach for abstraction NoF doesn't need.

NoF is two small libraries plus a small set of conventions:

- **VanJS** (~1KB) — fine-grained reactive UI and state. `van.state()`
  for reactive values, `van.derive()` for memoized computed values, no
  virtual-DOM diffing.
- **Navigo** (~4KB) — clean client-side routing with the History API.

Nothing else is required. No build step is strictly necessary (a CDN
import works), though Vite/TypeScript are fine additions when the project
grows — see `references/tooling.md`.

## When to use NoF (and when not to)

**Good fit:** personal projects and portfolios, startups/MVPs, internal
tools and dashboards, performance-sensitive apps, educational projects,
anywhere the person explicitly wants to avoid a framework or wants deep
understanding/control of what's running.

**Not a good fit:** very large multi-page enterprise apps (100+ pages),
teams larger than roughly 8–10 developers, projects that need heavy
animation libraries or a large third-party component ecosystem. If the
request clearly falls here, say so before scaffolding — NoF trades
ecosystem size and tooling maturity for simplicity and control, and that
trade only pays off within its intended scope.

If it's ambiguous which side of that line the person is on, that's a
delivery-scope fork worth a one-line stated assumption or a quick check
(see the `questionnaire` skill if enabled) rather than silently
scaffolding NoF for something that's clearly going to outgrow it.

## Workflow

### 0. Verify current library versions and API before writing any code

**Do this before scaffolding or writing a single line that imports a
library.** Every hardcoded version in this skill's scripts and examples
(currently `vanjs-core@1.6.0` and `navigo@8.11.1`, both loaded via CDN
URL — see `references/tooling.md` for why a bare `import Navigo from
'navigo'` doesn't work without a bundler) is a starting point, not a
guarantee — library versions move, APIs get
breaking changes between majors, and this skill's own training-data
knowledge can be stale by the time it's used. Don't trust a version
number baked into a reference file or script as current; go verify:

- Search for the current latest stable version of VanJS (`vanjs-core` on
  npm) and Navigo (`navigo` on npm), and of any other library being
  pulled in (see the "any vanilla-compatible library" section below).
- Check whether anything changed in the API surface this skill relies on
  — `van.state()`, `van.derive()`, `van.tags`, `van.add()` for VanJS;
  the `Navigo` constructor, `.on()`, `.resolve()`, `.navigate()` for
  Navigo — between the version referenced in this skill's examples and
  the actual current version. A minor/patch bump is usually safe to
  assume compatible; a major version bump is not — check its changelog
  or release notes for breaking changes before relying on the patterns
  in `references/` and `examples/` as-is.
- Use whatever's actually current in the scaffolded project — update the
  CDN URL / `package.json` version used by `scripts/init-nof.sh` and any
  example file to match, rather than leaving the older pinned version in
  place once you know a newer one exists and is compatible.
- If a major-version API change did happen and the patterns in this
  skill's `references/` no longer match, adapt the pattern to the
  current API rather than silently generating code against the old one
  — an outdated pattern that no longer matches the installed library's
  actual API will fail at runtime, not just be stylistically stale.

This is a one-time check per session/project, not something to repeat on
every file — verify once at the start of scaffolding, then proceed
using what you found.

### 1. Scaffold the project

Run `scripts/init-nof.sh` to generate the standard NoF directory
structure (see `references/project_structure.md` for what it creates and
why). This is the fastest correct starting point — don't hand-build the
skeleton from scratch when the script does it consistently.

```bash
bash scripts/init-nof.sh <project-name>                       # clean Hello World (default)
bash scripts/init-nof.sh <project-name> --demo                 # with a worked cart/products example
bash scripts/init-nof.sh <project-name> --bundler vite          # Vite + npm packages instead of CDN imports
bash scripts/init-nof.sh <project-name> --demo --bundler vite    # both together
```

The default scaffold is a genuinely minimal Hello World: one route, one
trivial page, a `base/Button.js` primitive, an empty `store.js` ready
for real state. Use this for an actual project — don't leave demo-only
content (a fake product cart) sitting in a real app's starting point.

`--demo` instead generates a fuller worked example (a cart store with an
action and a derived total, `base/Button.js` plus a `LoginButton`
business component built from it, `ProductCard` composition, two
routes) — useful when the person wants to see the patterns in action or
as a learning reference, not as the base for a real project. If it's
unclear which one fits what the person actually asked for, default to
the clean scaffold — "build me a NoF app for X" should get a clean
starting point for X, not unrelated demo content they'd have to delete
first.

`--bundler vite` switches the scaffold from the no-build-step CDN
default to Vite + npm packages: every generated file imports `vanjs-core`
and `navigo` as bare specifiers instead of CDN URLs, and the script also
generates `package.json`, `vite.config.js`, and a `.gitignore`. Combine
freely with `--demo`. Use this when the person explicitly wants
TypeScript, bundling, or npm-managed dependencies from the start (see
`references/tooling.md`'s "Local dev server" section for when Vite is
actually worth adding) — don't default to it for a small project where
the plain CDN setup is a complete, valid answer on its own. The version
numbers `--bundler vite` writes into `package.json` are still subject to
step 0 above: verify current `vanjs-core`/`navigo`/`vite` versions before
treating what the script generates as final.

### 2. Design global state first

Before building pages, decide what lives in `js/store.js` as global
state versus what's local to a component. See
`references/state_management.md` for the local vs. global vs. derived
split and the immutability rule that makes VanJS reactivity work at all
(`references/state_management.md#the-one-rule-that-matters`). As the
project grows, see `references/code_health.md` for when and how to
split a single `store.js` into domain-specific files.

### 3. Build components as pure functions, split base/ from components/

Components are functions that take props and return VanJS DOM elements —
no classes, no lifecycle methods. See `references/components.md` and
`examples/components/product-card.js` for the pattern, and
`examples/base/button.js` for the simplest possible reusable primitive.

Once a project has enough components that the same raw tag+class combo
starts getting reimplemented across more than one of them, split dumb
app-agnostic primitives (`Button`, `Image`) into `js/base/`, and build
business components (`LoginButton`, `HeroImage`, `ProductCard`) out of
those in `js/components/`. See
`references/components.md#base-vs-components` for the full pattern and
when to introduce it, and `examples/base/` +
`examples/components/login-button.js` /
`examples/components/hero-image.js` for both pairings worked through.

### 4. Wire up routing

Use Navigo with file-based pages under `pages/`, fetched and rendered on
navigation. See `references/routing.md` and `examples/routing/router.js`.

### 5. Render consistently

Always render through the `renderToApp()` helper from `js/utils.js`
rather than ad hoc DOM manipulation, so every page mounts the same way.
See `references/rendering.md`.

### 6. Apply `van.derive()` wherever there's a computed or heavy value

Filtering, sorting, totals, any derived value — wrap it in `van.derive()`
instead of recomputing it inline in a render function. This is the
single most important performance habit in NoF; see
`references/reactivity.md` for why and for the before/after pattern.

### 7. Before shipping, handle the URL-fallback config the local dev server hid

`live-server`/Vite's dev server transparently handle serving
`index.html` for unknown paths (Navigo's clean URLs need this), which
means it's easy to ship a project that's never actually been tested
against what a real static host does with a direct request to
`/products`. Don't skip `references/deployment.md`'s "URL fallback in
production" section — it's a five-minute host-config step, but skipping
it means real users hit a 404 on refresh or a shared link, not just a
theoretical edge case.

## VanJS + Navigo is the default, not the only option

VanJS and Navigo are this skill's recommended default because they're
small, well-suited to the philosophy, and battle-tested together — but
NoF's actual principle is broader: **any library that works as plain
vanilla JS (no required build step, no framework runtime underneath it)
is fair game within this architecture.** The commitment is to staying
framework-free, not to these two specific packages.

This opens up real, useful options beyond the core two:

- **Any vanilla-JS-compatible UI/state/utility library** can slot in
  alongside or instead of VanJS if the project's needs call for it —
  a different small reactive library, a vanilla date/animation/utility
  library, etc. — as long as it doesn't drag in a framework runtime
  (React, Vue, Angular) as a dependency. Check compatibility and current
  version the same way as step 0 above before adding anything new.
- **CSS tooling beyond plain CSS** — Less or Sass/SCSS are legitimate
  additions when a project's stylesheet complexity justifies variables,
  nesting, or mixins beyond what plain CSS custom properties comfortably
  handle. Both compile to plain CSS ahead of time or via a lightweight
  build step and don't pull in any framework runtime, so they fit
  NoF's philosophy cleanly. Reach for them the same way as Vite in
  `references/tooling.md` — an addition to bring in once the project's
  needs justify it, not a default scaffold choice for a small project
  where plain CSS is enough.
- **Be careful with tools that assume a framework underneath them.**
  Not everything that touches CSS-in-JS is vanilla-compatible in the
  same way — some tools (StyleX is a notable example) are built around
  and optimized for a specific framework's component model and require
  a build-time compiler tied to that ecosystem. Before adding a tool
  like this, verify it actually runs standalone against plain
  DOM/VanJS output rather than assuming CSS-in-JS tooling in general is
  automatically framework-agnostic just because it's "just CSS" on the
  surface.
- **HTMX and similar hypermedia libraries are vanilla-compatible, but a
  different architecture, not just an alternative router.** HTMX itself
  passes the vanilla-JS bar cleanly (single dependency-free file, no
  build step) — but it's server-rendered/hypermedia-driven (the server
  returns HTML fragments, HTML attributes declare the swapping), versus
  VanJS/Navigo's client-rendered component-and-state model. It's a
  legitimate alternative architecture when the backend and the person's
  preferences fit it better, not a drop-in swap for Navigo — see
  `references/tooling.md` for when to suggest it instead of default NoF
  versus alongside it.

## Must-follow rules (the short version)

| Rule | Why |
|---|---|
| Always assign a *new* value to `.val` (`cart.val = [...cart.val, x]`), never mutate in place | VanJS reactivity is triggered by assignment, not by mutation |
| Wrap any computed/heavy logic in `van.derive()` | Automatic memoization — only recomputes when a dependency actually changes |
| Render through `renderToApp()` | Keeps every page's mount/unmount behavior consistent |
| Keep components pure functions of their props | Reusability, testability, no hidden state surprises |
| Centralize global state in `store.js` | One place to reason about app-wide state instead of scattered `van.state()` calls |

Full detail and examples for each of these live in `references/`.

## Reference index

- `references/philosophy_and_stack.md` — the full case for NoF, the
  technology table, and fine-grained reactivity vs. virtual-DOM diffing.
- `references/project_structure.md` — the standard directory layout and
  what belongs where.
- `references/state_management.md` — local/global/derived state, the
  immutability rule, and the `store.js` pattern.
- `references/components.md` — pure component architecture and props.
- `references/routing.md` — Navigo setup and file-based page loading.
- `references/rendering.md` — the `renderToApp` / `renderToAppWithProps`
  / `navigateTo` utility pattern.
- `references/reactivity.md` — `van.derive()` memoization, and the
  before/after performance example.
- `references/tooling.md` — version/API verification discipline,
  TypeScript integration, dev server options, CSS tooling (Less/Sass),
  HTMX/hypermedia libraries, and the honest limitations list.
- `references/debugging.md` — triaging which layer a bug is in,
  the mutate-vs-reassign bug specifically, reading stack traces through
  minified CDN builds, and what to actually check when profiling.
- `references/deployment.md` — shipping a NoF app: the no-bundler
  no-build-step path and its CDN-pinning tradeoff, the production
  URL-fallback config each static host needs (Netlify/Vercel/GitHub
  Pages/S3), and the Vite production build step.
- `references/code_health.md` — how the project structure should shift
  as code grows (with before/after examples), NoF-specific code smells,
  and which files (`store.js`, `router.js`) tend to rot first and how to
  spot it.

## Examples index

`examples/` mirrors the project layout — organized by folder, the same
way a real NoF project's `js/` directory is:

- `examples/base/`
  - `button.js` — a minimal, app-agnostic reusable primitive.
  - `image.js` — the same pattern applied to `<img>`.
- `examples/components/`
  - `counter.js` — the smallest complete VanJS component
    (state + derive + event handler), kept deliberately native-tag-only
    to isolate the state/derive pattern from the base/component split.
  - `login-button.js` — a business component built from
    `base/button.js` (the base -> component pairing in practice).
  - `hero-image.js` — a business component built from `base/image.js`.
  - `product-card.js` — a component composed from a base primitive,
    taking props and a callback.
- `examples/pages/`
  - `home-page.js` — a page composed from several components, rendered
    via `renderToApp()`.
- `examples/stores/`
  - `store.js` — a small but complete global store with an action and a
    derived total.
- `examples/routing/`
  - `router.js` — Navigo route setup with file-based page loading.
- `examples/utils/`
  - `utils.js` — the standard `renderToApp` helper set.

## Scripts

- `scripts/init-nof.sh` — scaffolds a new NoF project with the standard
  directory structure, `index.html`, `store.js`, `utils.js`, `router.js`,
  `js/base/` and `js/components/`. Defaults to a clean, minimal Hello
  World (one route, one trivial page, empty store, a single
  `base/Button.js` primitive) — the right starting point for a real
  project. Pass `--demo` to instead generate a fuller worked example
  (cart store with an action and derived total, `base/Button.js` plus a
  `LoginButton` business component built from it, `ProductCard`, two
  routes) for learning the patterns or as a reference — not meant to be
  built on directly. Pass `--bundler vite` to scaffold with Vite and npm
  packages (bare-specifier imports, `package.json`, `vite.config.js`,
  `.gitignore`) instead of the default no-build-step CDN setup;
  combinable with `--demo`. Usage:
  `bash scripts/init-nof.sh <name> [--demo] [--bundler vite]`.
