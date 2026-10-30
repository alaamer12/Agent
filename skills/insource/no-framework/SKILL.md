---
name: no-framework
updated: 2026-10-08
description: >
  Build Single Page Applications using NoF (No Frameworks) — Navigo (~4KB routing) plus a choice of small UI libraries (Preact by default, or VanJS / Nano JSX via `--ui`), no React/Vue/Angular runtime or mandated structure. Use whenever scaffolding a small-to-medium SPA that should stay framework-free. Requires verifying current library versions/API (chosen UI library, Navigo, @preact/signals or Nano Stores) before writing code — pinned versions, especially fast-moving ones like @preact/signals, can go stale; the `updated` field above is a staleness signal, not a guarantee. Any vanilla-JS-compatible library is fair game, including Tailwind/Sass (`--styler`) and Nano Stores for cross-library state; StyleX is excluded (tied to React). Covers scaffolding, state/signals/derive patterns, routing, components, rendering, debugging, and production paths (no-bundler htm, and Vite JSX). Not a fit for very large multi-page apps, large teams, or heavy animation needs — see "when to use".
---

# NoF: No Frameworks Architecture

## Core philosophy

Simplicity over complexity, performance by default, full control over the
codebase. If something can be done with less code while staying just as
clear, do it that way — don't reach for abstraction NoF doesn't need.

NoF is a small UI library, Navigo for routing, and a small set of
conventions:

- **A UI library** — **Preact** (~3–4KB, JSX/hooks, the default),
  **VanJS** (~1KB, fine-grained reactive UI via `van.state()`/
  `van.derive()`, no virtual DOM), or **Nano JSX** (~1KB, real-DOM,
  explicit `this.update()`). Pick with `--ui` — see
  `references/ui_libraries.md` for the full comparison and why Preact
  is the default.
- **Navigo** (~4KB) — clean client-side routing with the History API,
  identical underneath whichever UI library is chosen.

Nothing else is required. No build step is strictly necessary — Preact
and Nano JSX use `htm` tagged templates instead of JSX for this (see
`references/ui_libraries.md`), the same no-build-step default VanJS
always had — though Vite/TypeScript/real JSX are fine additions when
the project grows (`--bundler vite`) — see `references/tooling.md`.

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
  `signal()`/`computed()`/`useSignal()` for `@preact/signals`;
  `atom()`/`computed()` for Nano Stores; the `Navigo` constructor, `.on()`, `.resolve()`, `.navigate()` for
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
bash scripts/init-nof.sh <project-name>                           # Preact, CDN + htm (default)
bash scripts/init-nof.sh <project-name> --ui vanjs                 # VanJS instead of Preact
bash scripts/init-nof.sh <project-name> --ui nanojsx                # Nano JSX instead of Preact
bash scripts/init-nof.sh <project-name> --ui preact --state nanostores  # Preact + Nano Stores instead of Signals
bash scripts/init-nof.sh <project-name> --demo                      # with a worked cart/products example
bash scripts/init-nof.sh <project-name> --bundler vite               # Vite + npm packages + real JSX
bash scripts/init-nof.sh <project-name> --styler tailwind             # + Tailwind CSS (standalone CLI)
bash scripts/init-nof.sh <project-name> --styler sass                  # + Sass (standalone CLI)
bash scripts/init-nof.sh <project-name> --bundler vite --styler tailwind  # Tailwind via @tailwindcss/vite
bash scripts/init-nof.sh <project-name> --ui nanojsx --demo --bundler vite  # combine freely
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

`--ui vanjs|preact|nanojsx` picks the UI library — default `preact`.
This changes component syntax (JSX/htm for Preact and Nano JSX vs.
`van.tags()` for VanJS), the local-state mechanism (hooks vs.
`van.state()` vs. class fields + `this.update()`), and what
`js/store.js` uses for shared state. See `references/ui_libraries.md`
for the full comparison — it's the first reference to check before
writing any component code for a non-default `--ui` choice, the same
way step 0 is the first check before trusting a version number.
`--state native|nanostores` only applies to `--ui preact` (default
`native`, meaning `@preact/signals`) — pass `--state nanostores` to use
Nano Stores instead, when the store needs to be shared with a
non-Preact part of the same page. `--ui nanojsx` always uses Nano
Stores for `js/store.js` regardless of `--state` (Nano JSX has no
reactive store of its own); passing `--state` with `--ui vanjs` or
`--ui nanojsx` is a scaffolding error explaining why, not a silently
ignored flag.

`--styler tailwind` or `--styler sass` adds CSS tooling beyond the
plain-CSS default — see `references/tooling.md`'s Tailwind and Sass
sections for why each genuinely needs a compile step (neither can be a
CDN `<script>` tag the way VanJS/Navigo can) and what that step looks
like. `--css-tooling cli|vite-plugin` picks between a standalone watcher
process and folding compilation into Vite; it defaults sensibly off
`--bundler` (`cli` without Vite, `vite-plugin` with it) so it rarely
needs to be passed explicitly. **StyleX is not a supported `--styler`
value** — it's tied to React's component model, not vanilla-compatible,
see `references/tooling.md#not-every-css-adjacent-tool-is-vanilla-compatible`
for why. The version numbers these flags write into `package.json` are
subject to the same step-0 verification as `--bundler vite`.

### 2. Design global state first

Before building pages, decide what lives in `js/store.js` as global
state versus what's local to a component. `references/state_management.md`
covers the local vs. global vs. derived split and the immutability rule
in VanJS terms (`van.state()`/`van.derive()`); the same rule applies
verbatim to `@preact/signals` and Nano Stores (reassign, don't mutate,
for arrays/objects) — see `references/ui_libraries.md` for the
signals/Nano Stores equivalents of every pattern in that file when `--ui`
isn't `vanjs`. As the project grows, see `references/code_health.md` for
when and how to split a single `store.js` into domain-specific files.

### 3. Build components as pure functions, split base/ from components/

Components are functions that take props and return the UI library's
element tree — classes only where Nano JSX genuinely needs one for local
state (see `references/ui_libraries.md#nano-jsx`). `references/components.md`
and `examples/<ui>/components/product-card.js` cover the pattern; VanJS
components take positional args, Preact/Nano JSX components take a props
object — `examples/vanjs/`, `examples/preact/` and `examples/nanojsx/`
each have the full worked set, and `references/ui_libraries.md` explains
the differences.

Once a project has enough components that the same raw tag+class combo
starts getting reimplemented across more than one of them, split dumb
app-agnostic primitives (`Button`, `Image`) into `js/base/`, and build
business components (`LoginButton`, `HeroImage`, `ProductCard`) out of
those in `js/components/`. See
`references/components.md#base-vs-components` for the full pattern and
when to introduce it, and `examples/<ui>/base/` +
`examples/<ui>/components/login-button.js` /
`examples/<ui>/components/hero-image.js` for both pairings worked through
(`<ui>` = `preact`, `vanjs`, or `nanojsx`).

### 4. Wire up routing

Use Navigo with file-based pages under `pages/`, fetched and rendered on
navigation. See `references/routing.md` and `examples/<ui>/routing/router.js`
(identical across the three — Navigo doesn't care which UI library sits
on top of it).

### 5. Render consistently

Always render through the `renderToApp()` helper from `js/utils.js`
rather than calling the UI library's render function (`van.add()`,
Preact's `render()`, Nano JSX's `render()`) directly, so every page
mounts the same way. See `references/rendering.md` — written in VanJS
terms, but `js/utils.js` generated under `--ui preact`/`--ui nanojsx`
follows the identical shape with that library's render call swapped in.

### 6. Apply the derive/computed equivalent wherever there's a computed or heavy value

Filtering, sorting, totals, any derived value — wrap it in `van.derive()`
(VanJS), `computed()` (`@preact/signals` or Nano Stores), instead of
recomputing it inline in a render function. This is the single most
important performance habit in NoF regardless of `--ui`; see
`references/reactivity.md` for the VanJS version of why and the
before/after pattern, and `references/ui_libraries.md` for the
signals/Nano Stores `computed()` equivalents.

### 7. Before shipping, handle the URL-fallback config the local dev server hid

`live-server`/Vite's dev server transparently handle serving
`index.html` for unknown paths (Navigo's clean URLs need this), which
means it's easy to ship a project that's never actually been tested
against what a real static host does with a direct request to
`/products`. Don't skip `references/deployment.md`'s "URL fallback in
production" section — it's a five-minute host-config step, but skipping
it means real users hit a 404 on refresh or a shared link, not just a
theoretical edge case.

## Preact + Navigo is the default, not the only option

Preact and Navigo are this skill's recommended default because Preact
pairs a familiar JSX/hooks surface and a large ecosystem with — via
`@preact/signals` — fine-grained updates close to VanJS's own, and
Navigo is small and battle-tested regardless of which UI library sits
on top of it. VanJS and Nano JSX (`--ui vanjs`/`--ui nanojsx`) remain
full alternatives, not legacy options — see `references/ui_libraries.md`
for when each fits better. NoF's actual principle is broader than any
specific package, default or not: **any library that works as plain
vanilla JS (no required build step, no framework runtime underneath it)
is fair game within this architecture.** The commitment is to staying
framework-free, not to any particular set of packages.

This opens up real, useful options beyond the core two:

- **Any vanilla-JS-compatible UI/state/utility library** can slot in
  alongside or instead of VanJS if the project's needs call for it —
  a different small reactive library, a vanilla date/animation/utility
  library, etc. — as long as it doesn't drag in a framework runtime
  (React, Vue, Angular) as a dependency. Check compatibility and current
  version the same way as step 0 above before adding anything new.
- **CSS tooling beyond plain CSS** — Tailwind and Sass/SCSS (or Less by
  hand) are legitimate additions when a project's needs justify them:
  Tailwind for utility-first styling, Sass/Less for variables, nesting,
  or mixins beyond what plain CSS custom properties comfortably handle.
  All compile to plain CSS ahead of time or via a build step and don't
  pull in a framework runtime, so they fit NoF's philosophy cleanly —
  `scripts/init-nof.sh --styler tailwind|sass` scaffolds either directly
  (see `references/tooling.md` for the CLI-vs-Vite-plugin compile-step
  choice each one needs, since neither works as a bare CDN
  `<script>` tag). Reach for them the same way as Vite — an addition to
  bring in once the project's needs justify it, not a default scaffold
  choice for a small project where plain CSS is enough.
- **Be careful with tools that assume a framework underneath them.**
  Not everything that touches CSS-in-JS is vanilla-compatible in the
  same way — some tools (StyleX is a notable example) are built around
  and optimized for a specific framework's component model and require
  a build-time compiler tied to that ecosystem. This is why `--styler`
  doesn't offer StyleX as a value — it would generate a NoF project with
  a React-only compiler and nothing to run it against. Before adding a
  tool like this by hand, verify it actually runs standalone against
  plain DOM/VanJS output rather than assuming CSS-in-JS tooling in
  general is automatically framework-agnostic just because it's "just
  CSS" on the surface.
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
| Always assign a *new* value, never mutate in place (`cart.val = [...cart.val, x]` / `cart.value = [...]` / `cart.set([...])`) | Every one of VanJS/signals/Nano Stores triggers reactivity on assignment, not on mutation |
| Wrap any computed/heavy logic in the derive/computed equivalent (`van.derive()` / `computed()`) | Automatic memoization — only recomputes when a dependency actually changes |
| Render through `renderToApp()` | Keeps every page's mount/unmount behavior consistent |
| Keep components pure functions of their props (classes only where Nano JSX genuinely needs local state) | Reusability, testability, no hidden state surprises |
| Centralize global state in `store.js` | One place to reason about app-wide state instead of scattered local state calls |

Full detail and examples for each of these live in `references/`.

## Reference index

- `references/philosophy_and_stack.md` — the full case for NoF, the
  technology table, and fine-grained reactivity vs. virtual-DOM diffing.
- `references/ui_libraries.md` — the full VanJS/Preact/Nano JSX
  comparison, `htm` vs. JSX, `@preact/signals`, and Nano Stores — the
  first file to check before writing component code under a non-default
  `--ui`.
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
  TypeScript integration, dev server options, CSS tooling (Tailwind's
  CLI-vs-Vite-plugin build step, Sass's CLI-vs-Vite-built-in split, why
  StyleX is excluded from `--styler`), HTMX/hypermedia libraries, and
  the honest limitations list.
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

`examples/` has one self-contained directory per `--ui` choice —
`preact/` (the default), `vanjs/`, and `nanojsx/` — each a complete,
parallel worked example of the same small shop app, so the *only*
differences between them are the ones that actually matter between the
libraries (component syntax, local state, shared state, how a component
reads a store). Read the directory matching the `--ui` in use; diff two
of them to see exactly what changes between libraries. Every directory
has the same layout, mirroring a real NoF project's `js/`:

- `examples/<ui>/base/`
  - `button.js` — a minimal, app-agnostic reusable primitive.
  - `image.js` — the same pattern applied to `<img>`.
- `examples/<ui>/components/`
  - `counter.js` — the smallest complete component with local state and
    a derived value, kept deliberately native-tag-only to isolate the
    state pattern from the base/component split. This is where the
    libraries differ most: `van.state`/`van.derive` (VanJS),
    `useSignal`/`useComputed` (Preact), class field + `this.update()`
    (Nano JSX).
  - `login-button.js` — a business component built from
    `base/button.js` (the base -> component pairing in practice), with
    local loading state.
  - `hero-image.js` — a business component built from `base/image.js`.
  - `product-card.js` — a component composed from a base primitive,
    taking props and a callback.
  - `cart-badge.js` — how a component *reads* shared store state:
    pass the state in directly (VanJS), embed the signal (Preact), or
    subscribe/update/unsubscribe by hand (Nano JSX).
- `examples/<ui>/pages/`
  - `home-page.js` — a page composed from several components, rendered
    via `renderToApp()`.
- `examples/<ui>/stores/`
  - `store.js` — a small but complete global store with an action and
    derived values: `van.state` (VanJS), `@preact/signals` (Preact),
    Nano Stores (Nano JSX).
- `examples/<ui>/routing/`
  - `router.js` — Navigo route setup with file-based page loading
    (identical in all three).
- `examples/<ui>/utils/`
  - `utils.js` — the standard `renderToApp` helper set.
- `examples/preact/html.js`, `examples/nanojsx/html.js` — the one-time
  `htm.bind(h)` helper those two directories import `html` from (VanJS
  needs none). Matches what `scripts/init-nof.sh` generates as
  `js/html.js`.

The Preact and Nano JSX examples use `htm` tagged templates (the
no-bundler default), not JSX. Under `--bundler vite` the same code is
written as real JSX instead — see `references/ui_libraries.md`.

## Scripts

- `scripts/init-nof.sh` — scaffolds a new NoF project with the standard
  directory structure, `index.html`, `store.js`, `utils.js`, `router.js`,
  `js/base/` and `js/components/`. Defaults to a clean, minimal Hello
  World (one route, one trivial page, empty store, a single
  `base/Button` primitive) — the right starting point for a real
  project. Pass `--demo` to instead generate a fuller worked example
  (cart store with an action and derived total, `base/Button` plus a
  `LoginButton` business component built from it, `ProductCard`, two
  routes) for learning the patterns or as a reference — not meant to be
  built on directly. Pass `--ui vanjs|preact|nanojsx` to pick the UI
  library (default `preact`) — see `references/ui_libraries.md`; this
  also changes generated file extensions (`.jsx` under `--bundler vite`
  for Preact/Nano JSX, `.js` otherwise) and adds a `js/html.js` helper
  for Preact/Nano JSX without a bundler. Pass `--state native|nanostores`
  (only valid with `--ui preact`; default `native` = `@preact/signals`)
  to use Nano Stores for `js/store.js` instead. Pass `--bundler vite` to
  scaffold with Vite, npm packages, and real JSX instead of the default
  no-build-step CDN + `htm` setup. Pass `--styler tailwind` or `--styler
  sass` to add CSS tooling beyond plain CSS, and optionally
  `--css-tooling cli|vite-plugin` to override the default compile-step
  choice (see `references/tooling.md`). All flags
  combine freely. Usage:
  `bash scripts/init-nof.sh <name> [--ui vanjs|preact|nanojsx] [--state native|nanostores] [--demo] [--bundler vite] [--styler tailwind|sass] [--css-tooling cli|vite-plugin]`.
