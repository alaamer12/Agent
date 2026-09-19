# Debugging, Profiling, and Optimization

This covers the NoF-specific side of "something's wrong" and "is it fast
enough" — not a general JavaScript debugging tutorial. For deployment-time
problems (a bug that only shows up in production, not locally), see
`references/deployment.md`.

## Triage: which layer is the bug actually in

NoF has three moving parts, and a bug usually lives in exactly one of
them. Narrow it down before digging:

- **Nothing renders at all** (blank page, no error) — check that
  `renderToApp()` is actually being called from the active route, and
  that `<div id="app">` exists in `index.html` with that exact id.
  `renderToApp()` and `renderToAppWithProps()` both log
  `"[NoF] #app element not found"` and return early if the id is
  missing or misspelled — check the console for that before assuming
  it's a state or routing bug.
- **The wrong page renders, or navigation does nothing** — a routing
  bug. Check the route path strings in `router.on(...)` match what's
  actually being navigated to, that `router.resolve()` is called once
  after all `router.on()` calls (not before), and that navigation goes
  through `navigateTo()` / `router.navigate()` rather than a plain `<a
  href>` without `data-navigo` intercepting it unexpectedly. See
  `references/routing.md`.
- **A page renders once but doesn't update when state changes** — a
  state bug, and specifically almost always the same one bug. See the
  next section — it's common enough to check first before looking
  anywhere else.
- **Everything works when clicking around, but breaks on refresh or a
  direct/bookmarked URL** — this isn't a code bug, it's a dev-server or
  hosting config gap. See "`live-server` needs `--entry-file`, not
  `--spa`" in `references/tooling.md` for local dev, and
  `references/deployment.md` for the same problem in production.

## The #1 NoF bug: mutating `.val` instead of reassigning

If a page renders once correctly but silently stops updating after
that, check every action that touches the relevant state for in-place
mutation before looking anywhere else:

```js
// Silently broken — VanJS never sees a change, UI goes stale
cart.val.push(product);

// Fixed — new reference assigned to .val
cart.val = [...cart.val, product];
```

This doesn't throw an error, which is what makes it the most common NoF
bug to lose time on. Full rule and object-mutation equivalent in
`references/state_management.md`; the smell-pattern writeup is in
`references/code_health.md`.

## Stepping through minified library code

VanJS and Navigo are loaded from CDN as minified builds
(`van.min.js`, and Navigo's jsdelivr `+esm` output is minified too — see
`references/tooling.md`). That means:

- A stack trace that bottoms out *inside* VanJS or Navigo will show
  mangled variable names and collapsed code, not readable source. This
  is expected, not a sign of a broken import.
- Put breakpoints and `console.log`s in your own code (component
  functions, store actions, route handlers) rather than trying to step
  into the library — that's almost always where the actual bug is
  anyway, since VanJS/Navigo themselves are small and well-tested.
- If a bug genuinely seems to be inside VanJS or Navigo's own logic
  (rare), temporarily swap the CDN URL for the library's unminified
  dev build to get readable stack traces for that one debugging
  session, then revert to the pinned minified URL — don't leave a
  project running against an unminified/unpinned build long-term.

## Profiling: what to actually check, not just "open the Performance tab"

The Performance tab is useful, but only if you know what you're
verifying. Two NoF-specific things worth actually checking rather than
assuming, since a false assumption here compounds as an app grows:

1. **A `van.derive()` isn't recomputing more often than its inputs
   change.** Temporarily add a `console.log` inside the derive function
   and watch how often it fires while interacting with the app. If it's
   firing on state changes it doesn't actually read, something's
   accidentally reading extra state during the derive's run (a common
   cause: calling a function that itself reads unrelated `.val`s inside
   the derive body). Remove the log once confirmed — see
   `references/reactivity.md` for the memoization model this is
   verifying.
2. **`renderToApp()`'s DOM-nodes-touched footprint on navigation.**
   `renderToApp()` clears `#app` (`innerHTML = ''`) and rebuilds the new
   page's whole tree on every route change — this is a full teardown
   and rebuild of the page-level content, not a diff. That's the right
   tradeoff for NoF's target scope (small-to-medium apps, infrequent
   full-page navigations) and is unrelated to VanJS's fine-grained
   reactivity *within* a mounted page. Record a Performance trace across
   a route change vs. across an in-page state update (e.g. typing in a
   search box wired to `van.derive()`) and confirm the state-update
   trace only touches a handful of DOM nodes while the route-change
   trace touches the whole `#app` subtree — that contrast is the actual
   fine-grained-reactivity claim from `references/philosophy_and_stack.md`,
   worth confirming on a real project rather than taking on faith.

## When a profiling/debugging need seems to require new tooling

If a specific pain point (e.g. wanting a component inspector, wanting
real source maps for the CDN build) seems to need pulling in something
beyond browser DevTools, check the "Any vanilla-compatible library, not
just VanJS/Navigo" section of `references/tooling.md` before assuming
it's out of reach — the same framework-free compatibility check applies
to dev tooling as it does to runtime libraries. Don't reach for Vite
solely to get source maps if the underlying bug can be found with a
`console.log` in your own code; do reach for it if the project's actual
debugging needs have grown past what that supports (see the honest
limitations list at the end of `references/tooling.md`).
