# Frontend / client-side debugging

Use whenever the observable failure lives in the client — UI shows
wrong/empty/stale data, a click does nothing or the wrong thing, console
errors, requests that look wrong in the Network tab, state that diverges
from what the server sent, unexpected re-renders, or "works locally but
not in the browser". The browser itself is the debugging instrument.

## Network-first triage (do this before reading a single line of component code)

Open DevTools → Network, reproduce, find the call:

```
Did the request even fire?          no → handler wiring, form validation
                                     blocking submit, feature flag, stale bundle
What did it send?                   payload wrong at the wire → the client
                                     produced it wrong (or the input was)
Status + payload correct?           no  → the bug's not here: follow it into
                                     backend.md / database.md (right tool,
                                     right time — don't debug a server bug in JSX)
Response correct but UI wrong?      yes → client bug: state or render, next
```

This one check prevents the classic waste: hours in components on what was
a server response bug all along (and the reverse — "UI bug" that was the
app reading stale/cached or lagging-replica data,
[`database.md`](database.md)/[`production.md`](production.md)).

Panel mechanics that make the check real: the Network panel **records
only while it is open** — arm it before performing the reproducing
action, history from before is unrecoverable; normalize repeat
conditions with empty-cache hard reload (cache is the classic
confounder); read the **Initiator** column/tree as the network edition
of a call stack (it names what caused a request and jumps to the code
that scheduled it); and use **Request Blocking** as a designed ablation
experiment — remove one dependency deliberately and observe whether the
breakage is total or partial, an outcome with mutually exclusive
answers rather than passive inference.

## Console execution — isolate like a scientist

Evaluate the suspect directly in page context to separate **function vs
caller vs state vs render vs environment** (the console edition of the
isolated harness):

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
| What threw, when, with what values? | Console + Sources: exception breakpoints ("Pause on caught & uncaught"), call stack, scope pane — then duck-debug the frames ([`../SKILL.md`](../SKILL.md)) |
| Rare condition inside a hot path? | **conditional breakpoints** (right-click line → add condition) instead of spam logs — caveat: a condition that *fails to evaluate* still breaks (with a warning); never read that break as confirmation |
| Something changed the DOM behind my back? | Elements → break on subtree modifications / attribute changes / node removal — maps the visual glitch to the exact JS |
| XHR/fetch: which call, which response? | Network (filter, replay, copy-as-curl → feed the [`backend.md`](backend.md) harness) |
| Event fired at all? | Event listener breakpoints (DOM type) / `getEventListeners(el)` in Console |
| Where does this value live / persist? | Application: Local/Session/IndexedDB, cookies, service-worker cache |
| Why so slow / re-rendering forever? | Performance flame/track, framework devtools profiler |
| Memory climbing while using the SPA? | Memory snapshots ×2 with interaction between → detached DOM nodes, leaked listeners → [`production.md`](production.md) growth method |
| Minified bundle unreadable? | Source maps on (verify they exist first — a class of "works locally" bug) |

## Framework state vs render (any reactive framework)

Symptom "data is right server-side but wrong on screen" narrows to:

```
response → parse → store/dispatch → selector → props → component render → DOM
```

- **Store snapshot vs rendered output disagree** → render path (props
  mapping, conditional template, CSS) — component test or storybook-class
  isolation, cheap.
- **Store itself already wrong** → trace actions/reducers/mutations:
  instrument the dispatcher (log every action + payload), find the first
  wrong transition (first-invalid-state, client edition).
- **Component ignores correct state** → the reference-identity trap (seen
  in React/Vue/Svelte-shaped systems alike): mutation in place
  (`state.items.push(x)`) instead of new objects/arrays breaks
  shallow-compare change detection → no re-render. Also: fresh `{}`/`[]`
  literal props every parent render → *unwanted* re-renders
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
([`../assets/scoped-debugger-example.md`](../assets/scoped-debugger-example.md)
— the dev-only guard matters doubly here; client code *ships to prod*);
for throwaway observation prefer the console/DevTools over editing source
at all — zero diff, zero cleanup.

## Regression testing frontend bugs

Prefer, in cost order: pure-function unit test on the reducer/helper that
held the bug → component test with controlled props/store (jsdom or the
framework's test utils — example tools) → *then* propose e2e
(Playwright-class — illustrative). E2e infrastructure is gate #2 —
never stand it up unilaterally for one bug
([`regression-testing.md`](regression-testing.md)).

---
**Better next stop:** response proven wrong upstream →
[`backend.md`](backend.md) / [`database.md`](database.md) ·
only-in-production user reports, unreproducible → [`production.md`](production.md) ·
process → [`../SKILL.md`](../SKILL.md).
