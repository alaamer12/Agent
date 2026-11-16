---
name: no-framework
version: 1.1.0
author: Amr
specialized: navigo
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
  **VanJS** (~1KB, fine-grained reactive UI, no virtual DOM), or
  **Nano JSX** (~1KB, real-DOM, explicit `this.update()`). Pick with
  `--ui`; comparison and why Preact is default: `references/ui_libraries.md`.
- **Navigo** (~4KB) — clean client-side routing with the History API,
  identical underneath whichever UI library is chosen.

Nothing else is required. No build step is strictly necessary — Preact
and Nano JSX use `htm` tagged templates instead of JSX; Vite/TypeScript/
real JSX are fine additions when the project grows (`--bundler vite`).
The full case, and fine-grained reactivity vs virtual-DOM diffing:
`references/philosophy_and_stack.md`.

## When to use NoF (and when not to)

**Good fit:** personal projects and portfolios, startups/MVPs, internal
tools and dashboards, performance-sensitive apps, educational projects,
anywhere the person explicitly wants to avoid a framework or wants deep
understanding and control.

**Not a good fit:** very large multi-page enterprise apps (100+ pages),
teams larger than roughly 8–10 developers, projects needing heavy
animation libraries or a large third-party component ecosystem. If the
request clearly falls there, say so before scaffolding — NoF trades
ecosystem size for simplicity, and that trade only pays inside its
scope. If it's ambiguous, state the assumption or ask (see the
`questionnaire` skill if enabled); don't silently scaffold NoF for
something that will outgrow it.

## Workflow

0. **Verify current library versions and API before writing code.**
   Every version hardcoded here or in the scripts (`vanjs-core@1.6.0`,
   `navigo@8.11.1`, CDN-loaded) is a starting point, not a guarantee.
   Check npm for the current stable of each library in use; a minor/patch
   bump is usually compatible, a **major** is not — read the changelog
   before trusting the patterns in `references/`. If the API did change,
   adapt the pattern to the current library rather than generating code
   against the stale one; an outdated pattern fails at runtime. One
   check per project, at the start. Full discipline: `references/tooling.md`.
1. **Scaffold the project** — don't hand-build the skeleton:

   ```bash
   bash scripts/init-nof.sh <project-name>                       # Preact, CDN + htm (default)
   bash scripts/init-nof.sh <project-name> --ui vanjs|nanojsx    # other UI libraries
   bash scripts/init-nof.sh <project-name> --state nanostores    # with --ui preact
   bash scripts/init-nof.sh <project-name> --demo                # worked cart example (learning only)
   bash scripts/init-nof.sh <project-name> --bundler vite        # Vite + npm + real JSX
   bash scripts/init-nof.sh <project-name> --styler tailwind|sass
   ```

   Flags combine freely. The default scaffold is a genuinely minimal
   Hello World — the right base for a real project; `--demo` is for
   seeing the patterns worked, never the starting point of a real app.
   What each flag actually changes (file extensions, state mechanism,
   compile steps, why StyleX is absent): `references/scaffold-options.md`.
2. **Design global state first.** What lives in `js/store.js` versus
   component-local versus derived — `references/state_management.md`
   (VanJS terms; `ui_libraries.md` has the signals/Nano Stores
   equivalents). Growth: split a single store by domain per
   `references/code_health.md`.
3. **Components are pure functions of their props** (classes only where
   Nano JSX genuinely needs local state). Dumb primitives to `js/base/`,
   business components composed from them in `js/components/` —
   `references/components.md`, worked in `examples/<ui>/`.
4. **Wire up routing** — Navigo with file-based pages under `pages/`,
   fetched on navigation: `references/routing.md`.
5. **Render consistently** — always through `renderToApp()` from
   `js/utils.js`, never the library's render directly, so every page
   mounts the same way: `references/rendering.md`.
6. **Wrap every computed or heavy value** in `van.derive()` /
   `computed()` — the single most important performance habit in NoF
   regardless of `--ui`: `references/reactivity.md`.
7. **Before shipping, handle the URL fallback** — dev servers serve
   `index.html` for unknown paths; real static hosts 404 on refresh or a
   shared link. Don't skip `references/deployment.md`'s "URL fallback in
   production": a five-minute host-config step users will feel.

## Must-follow rules (the short version)

| Rule | Why |
|---|---|
| Always assign a *new* value, never mutate in place (`cart.val = [...cart.val, x]` / `cart.value = [...]` / `cart.set([...])`) | Every one of VanJS/signals/Nano Stores triggers reactivity on assignment, not on mutation |
| Wrap any computed/heavy logic in the derive/computed equivalent (`van.derive()` / `computed()`) | Automatic memoization — only recomputes when a dependency actually changes |
| Render through `renderToApp()` | Keeps every page's mount/unmount behavior consistent |
| Keep components pure functions of their props (classes only where Nano JSX genuinely needs local state) | Reusability, testability, no hidden state surprises |
| Centralize global state in `store.js` | One place to reason about app-wide state instead of scattered local state calls |

Full detail and examples for each of these live in `references/`.

## The stack principle

Preact + Navigo is the default, not the only option. NoF's actual
principle: **any library that works as plain vanilla JS (no required
build step, no framework runtime) is fair game.** The commitment is to
staying framework-free, not to particular packages. Tailwind and Sass
fit (they compile to plain CSS); StyleX does not (React-only compiler —
not offered by `--styler`); HTMX is vanilla-compatible but a *different
architecture* (server-rendered hypermedia), not a Navigo swap. Verify
any tool runs standalone before assuming compatibility — full policy
and the compatibility checks: `references/scaffold-options.md`.

## Reference index

| File | Load when |
|---|---|
| `philosophy_and_stack.md` | arguing the choice; fine-grained vs vDOM |
| `ui_libraries.md` | before component code under a non-default `--ui` |
| `scaffold-options.md` | choosing flags; what a scaffold actually changes |
| `project_structure.md` | what `init-nof.sh` creates and why |
| `state_management.md` | local/global/derived split, immutability |
| `components.md` | the `base/` vs `components/` pattern |
| `routing.md` | Navigo setup, file-based pages |
| `rendering.md` | `renderToApp` / `navigateTo` utilities |
| `reactivity.md` | derive/computed memoization, before/after |
| `tooling.md` | version verification, TypeScript, dev servers, CSS tooling |
| `debugging.md` | which layer a bug is in; mutate-vs-reassign; minified traces |
| `deployment.md` | URL fallback config, CDN pinning tradeoff, Vite build |
| `code_health.md` | growing pains; store/router rot |

## Examples & scripts

`examples/` holds one complete worked shop per `--ui` — `preact/`,
`vanjs/`, `nanojsx/` — identical layout mirroring a real NoF project's
`js/` (`base/`, `components/`, `pages/`, `stores/`, `routing/`,
`utils/`), so the only differences you read are the real library
differences. Preact and Nano JSX examples use `htm` tagged templates;
under `--bundler vite` the same code is real JSX
(`references/ui_libraries.md`).

`scripts/init-nof.sh` is the only script — usage above; full option
semantics in `references/scaffold-options.md`.
