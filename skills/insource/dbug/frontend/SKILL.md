---
name: dbug-frontend
description: Debug browser/client-side problems — UI shows wrong/empty/stale data, a click does nothing or the wrong thing, console errors, requests that look wrong in the Network tab, state that diverges from what the server sent, unexpected re-renders, or "works locally but not in the browser" — use whenever the observable failure lives in the client. The browser itself is the debugging instrument: DevTools tour, console-execution isolation, network-first triage, state-vs-render split.
---

# dbug-frontend — client-side debugging

## Network-first triage (do this before reading a single line of component code)

Open DevTools → Network, reproduce, find the call:

```
Did the request even fire?          no → handler wiring, form validation
                                     blocking submit, feature flag, stale bundle
What did it send?                   payload wrong at the wire → the client
                                     produced it wrong (or the input was)
Status + payload correct?           no  → the bug's not here: follow it into
                                     ../backend/ / ../database/ (right tool,
                                     right time — don't debug a server bug in JSX)
Response correct but UI wrong?      yes → client bug: state or render, next
```

This one check prevents the classic waste: hours in components on what was
a server response bug all along (and the reverse — "UI bug" that was the
app reading stale/cached or lagging-replica data, `../database/`/`../production/`).

## Console execution — isolate like a scientist

Evaluate the suspect directly in page context to separate **function vs
caller vs state vs render vs environment**:

```js
// "Does this function actually return what I think it returns?"
somePureHelper(testInput)                      // works alone → caller/state issue
window.__DEBUG_TARGET__ = suspiciousFunction   // expose it, then call with controlled args

// state truth:
store.getState?.()                             // or the framework's devtools hook
localStorage; sessionStorage; document.cookie  // what does the client BELIEVE
```

If the function is right in the console but wrong in the app, the
pipeline's *input* to it (state, props, effect timing) is the suspect —
back to the hop model.

## DevTools, by question

| Question | Tool |
|---|---|
| What threw, when, with what values? | Console + Sources: exception breakpoints ("Pause on caught & uncaught"), call stack, scope pane |
| Rare condition inside a hot path? | **conditional breakpoints** (right-click line → add condition) instead of spam logs |
| Something changed the DOM behind my back? | Elements → break on subtree modifications / attribute changes / node removal — maps the visual glitch to the exact JS |
| XHR/fetch: which call, which response? | Network (filter, replay, copy-as-curl → feed `../backend/` harness) |
| Event fired at all? | Event listener breakpoints (DOM type) / `getEventListeners(el)` in Console |
| Where does this value live / persist? | Application: Local/Session/IndexedDB, cookies, service-worker cache |
| Why so slow / re-rendering forever? | Performance flame/track, React/Vue devtools profiler |
| Memory climbing while using the SPA? | Memory snapshots ×2 with interaction between → detached DOM nodes, leaked listeners → `../production/` growth method |
| Minified bundle unreadable? | Source maps on (verify they exist first — a class of "works locally" bug) |

## Framework state vs render (React-shaped, generalizes)

Symptom "data is right server-side but wrong on screen" narrows to:

```
response → parse → store/dispatch → selector → props → component render → DOM
```

- **Store snapshot vs rendered output disagree** → render path (props
  mapping, conditional JSX, CSS) — component test or Storybook-class
  isolation, cheap.
- **Store itself already wrong** → trace actions/reducers/mutations:
  instrument the dispatcher (log every action + payload), find the first
  wrong transition (first-invalid-state, client edition).
- **Component ignores correct state** → the reference-identity trap:
  mutation in place (`state.items.push(x)`) instead of new objects/arrays
  breaks shallow-compare change detection → no re-render. Also: fresh
  `{}`/`[]` literal props every parent render → *unwanted* re-renders
  (memo/identity fix).
- **Stale value in callback** → closure captured an old state/props value
  (dependency-array staleness) — a *state timing* bug, not a logic bug;
  log/inspect inside the callback to confirm which vintage it saw.

## "Works locally / fails deployed / fails for one user"

Environment-differential, client edition: stale cached bundle & service
worker (hard-reload test), browser/engine + version where it fails,
extension interference (incognito check), screen/locale/timezone
formatting assumptions, CORS/proxy/header stripping at the real origin,
minification behavior differences, feature flags/env vars injected at
build time not runtime.

## Instrumentation in client code

Same discipline as everywhere: gated scoped logger
([`../instrumentation/assets/scoped-debugger-example.md`](../instrumentation/assets/scoped-debugger-example.md)
— dev-only guard matters doubly here; client code *ships to prod*); for
throwaway observation prefer the console/DevTools over editing source at
all — zero diff, zero cleanup.

## Regression testing frontend bugs

Prefer, in cost order: pure-function unit test on the reducer/helper that
held the bug → component test with controlled props/store → *then* propose
e2e (Playwright-class). E2e infrastructure is the dbug gate-#2 ask —
never stand it up unilaterally for one bug.

---
**Better next stop:** response proven wrong upstream →
[`../backend/SKILL.md`](../backend/SKILL.md) / [`../database/SKILL.md`](../database/SKILL.md) ·
only-in-production user reports, unreproducible → [`../production/SKILL.md`](../production/SKILL.md) ·
process → [`../investigation/SKILL.md`](../investigation/SKILL.md).
