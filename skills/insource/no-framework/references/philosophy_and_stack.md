# Philosophy & Technology Stack

## Why NoF exists

NoF (No Frameworks) is a complete architecture for building SPAs using
only vanilla JavaScript tools — VanJS for UI and state, Navigo for
routing. It exists to prove that heavy frameworks (React, Vue, Angular)
aren't required to build modern, scalable, maintainable web applications
— for the right size of project.

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
| UI & Reactivity | VanJS | ~1KB | Fine-grained reactive UI |
| Routing | Navigo | ~4KB | Clean client-side routing |
| State management | VanJS (`van.state()` + `van.derive()`) | built-in | Global + local state with memoization |
| Utilities | Custom `utils.js` | <1KB | Rendering helpers |
| Styling | Plain CSS | – | Full control, no CSS-in-JS overhead |
| Language | JavaScript / TypeScript | – | Core development |

Total framework footprint is typically well under 10KB gzipped — smaller
than most single React component libraries, let alone React itself.

## Fine-grained reactivity vs. virtual-DOM diffing

React (and similar frameworks) re-render a component function on state
change, then diff the resulting virtual DOM tree against the previous one
to figure out what actually changed. This works, but it means every
re-render does diffing work even when only one small value changed —
which is why `useMemo`, `useCallback`, and `React.memo` exist: to opt
specific things *out* of that default re-render cost.

VanJS inverts this. `van.state()` values are directly wired to the exact
DOM nodes that read them — when a state value changes, only those nodes
update. There's no tree to diff, because there's no re-render pass at
all; the binding is direct. `van.derive()` gives you a memoized computed
value in the same spirit — it only recomputes when one of the state
values it reads actually changes, automatically, with no dependency
array to get wrong.

Practical upshot: you don't need `useMemo`, `useCallback`, or
`React.memo` in NoF. `van.derive()` covers the computed-value case, and
direct state-to-DOM binding covers the "don't re-render things that
didn't change" case that `React.memo` exists to solve.

## Performance characteristics (typical)

- Bundle size: usually under 10KB gzipped for the framework layer itself.
- Runtime: strong, due to fine-grained updates rather than diffing.
- Memory usage: low — no virtual DOM tree kept in memory.
- No re-render cascades — a state change only touches the DOM nodes that
  actually depend on it.
