# Philosophy & Technology Stack

## Why NoF exists

NoF (No Frameworks) is a complete architecture for building SPAs using
only vanilla JavaScript tools — a small UI library (Preact by default,
or VanJS / Nano JSX — see `references/ui_libraries.md`) for UI and
state, Navigo for routing. It exists to prove that heavy frameworks
(React, Vue, Angular) aren't required to build modern, scalable,
maintainable web applications — for the right size of project.

Preact itself is, by its own description, "a fast 3kB alternative to
React with the same modern API" — a rendering library, not an app
framework. It doesn't mandate routing, data-fetching conventions, or a
CLI-scaffolded project structure the way Next.js/Angular/Nuxt do; NoF
still supplies all of that (Navigo, `store.js`, the file layout). That's
what keeps it inside NoF's definition of "library, not framework" even
though it uses JSX and, under the hood, a virtual DOM — see the next
section for why that doesn't give up fine-grained updates.

## Core values

- **Simplicity first** — less abstraction means easier understanding and
  debugging. Every layer added should earn its place.
- **Fine-grained reactivity** — update only what actually needs updating,
  not a virtual-DOM diff pass over a subtree.
- **Zero framework lock-in** — full ownership of the codebase; nothing
  hidden behind a framework's internals.
- **Performance by default** — no unnecessary re-renders, because there's
  no coarse re-render model to opt out of in the first place.
- **Progressive enhancement** — the structure scales as the app grows,
  without requiring a rewrite.

## Technology stack

| Layer | Technology | Size (approx) | Purpose |
|---|---|---|---|
| UI | **Preact** (default) / VanJS / Nano JSX — `--ui` | ~3–4KB / ~1KB / ~1KB | Component rendering — see `references/ui_libraries.md` |
| Routing | Navigo | ~4KB | Clean client-side routing, identical across all three UI choices |
| State management | `@preact/signals` (Preact default) / `van.state()`+`van.derive()` (VanJS) / Nano Stores (Nano JSX, and optional for Preact via `--state`) | ~1KB or built-in | Global + local state, with memoization via `computed()`/`van.derive()` |
| No-bundler component syntax | `htm` tagged templates (Preact/Nano JSX only — VanJS's `van.tags()` already needs no compiler) | <1KB | JSX-equivalent that runs without a build step |
| Utilities | Custom `utils.js` | <1KB | Rendering helpers |
| Styling | Plain CSS (Tailwind/Sass optional via `--styler`) | – | Full control, no required CSS-in-JS overhead |
| Language | JavaScript / TypeScript | – | Core development |

Total framework footprint is typically well under 10KB gzipped for any
of the three `--ui` choices — smaller than most single React component
libraries, let alone React itself.

## Fine-grained reactivity vs. virtual-DOM diffing

React (and similar frameworks) re-render a component function on state
change, then diff the resulting virtual DOM tree against the previous one
to figure out what actually changed. This works, but it means every
re-render does diffing work even when only one small value changed —
which is why `useMemo`, `useCallback`, and `React.memo` exist: to opt
specific things *out* of that default re-render cost.

**VanJS** inverts this from the ground up. `van.state()` values are
directly wired to the exact DOM nodes that read them — when a state
value changes, only those nodes update. There's no tree to diff, because
there's no re-render pass at all; the binding is direct. `van.derive()`
gives you a memoized computed value in the same spirit — it only
recomputes when one of the state values it reads actually changes,
automatically, with no dependency array to get wrong. VanJS never has a
"plain" mode that re-renders and diffs — this is the only way it works.

**Preact**, used plainly (`useState`, props, no signals), works the
React way: a state change re-renders the component function and Preact
diffs the result — small and fast, but still a diff pass. **This is
where `@preact/signals` matters, and why it's NoF's default for Preact's
shared state rather than an optional add-on**: Preact's signals
integration patches the renderer to detect a signal read directly in a
JSX child position and bind that specific text/attribute node to the
signal, skipping the component re-render and the diff entirely for that
update — the same "update only what changed" property VanJS has by
default, recovered here as Preact's own deeply-integrated opt-in rather
than Preact's only mode. `useState`-based local state still re-renders
+ diffs normally; that's a reasonable tradeoff for state that's cheap
and local (a form field, a toggle) versus state read in many places.

**Nano JSX** takes a third approach: no virtual DOM at all (even
smaller than Preact), but also no automatic reactivity of any kind —
updating the DOM in response to a change is the component author's
explicit job (`this.update()`), not something the library infers from
state mutation the way VanJS or signals do.

Practical upshot: you generally don't need `useMemo`, `useCallback`, or
`React.memo` in NoF regardless of `--ui`. VanJS's `van.derive()` and
direct state-to-DOM binding cover that ground by construction; Preact's
`computed()`/signals cover the same ground when state is read through
them; Nano JSX's explicit `this.update()` model sidesteps the question
differently — there's no hidden re-render to memoize around in the
first place.

## Performance characteristics (typical)

- Bundle size: usually under 10KB gzipped for the UI + routing layer
  itself, for any of the three `--ui` choices.
- Runtime: strong across all three — VanJS/Preact+signals avoid diffing
  for the updates that matter; Nano JSX avoids a virtual DOM layer
  entirely at the cost of manual update calls; plain Preact (hooks-only,
  no signals) still diffs, but a small tree.
- Memory usage: low for VanJS and Nano JSX (no virtual DOM tree kept in
  memory); Preact keeps a small VDOM tree, the cost of its JSX/hooks
  ergonomics and ecosystem size.
- No re-render cascades for VanJS, or for Preact state read through
  signals — a change only touches the DOM nodes that actually depend on
  it. Nano JSX avoids cascades by never having an automatic one to begin
  with.
