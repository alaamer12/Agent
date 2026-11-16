# UI Libraries: VanJS, Preact, and Nano JSX

## Why three options, and why this isn't a contradiction of "no frameworks"

NoF's commitment is to staying framework-free, not to any one specific
package. A library earns a place here if it doesn't mandate a build
step, a routing convention, or a data-fetching convention — the person
using it still brings their own router (Navigo, unchanged across all
three), owns their own `store.js`, and decides their own project
structure. That's the real dividing line between a *library* and a
*framework* in NoF's sense: Angular/Next.js/Nuxt bundle in routing, data
loading, and a mandated CLI-scaffolded structure; Preact and Nano JSX
don't — they're rendering libraries you drop into whatever structure you
already have, the same role VanJS plays. Preact's own docs describe it
the same way: "Fast 3kB alternative to React with the same modern API" —
a library, not an app framework.

`scripts/init-nof.sh --ui vanjs|preact|nanojsx` picks which one a
scaffold uses. **Preact is the default.** VanJS and Nano JSX remain full
first-class options, not legacy fallbacks — pick whichever fits the
project and the person's familiarity.

## Quick comparison

| | VanJS | Preact (default) | Nano JSX |
|---|---|---|---|
| Size | ~1KB | ~3–4KB (+ hooks/signals if used) | ~1KB |
| Rendering model | No VDOM — state bound directly to DOM nodes | Virtual DOM (small, Preact's own) | No VDOM — real DOM, manual reconciliation |
| Component syntax | `van.tags` (`div(...)`, `button(...)`) | JSX (Vite) or `htm` tagged templates (no bundler) | JSX (Vite) or `htm` tagged templates (no bundler) |
| Component shape | Plain functions, positional args | Plain functions, props object (JSX/React convention) | Plain functions (stateless) or classes (stateful, `this.update()`) |
| Reactivity | `van.state()` / `van.derive()`, built in | `useState`/hooks (local) + `@preact/signals` (fine-grained, see below) | None built in — explicit `this.update()` after a change |
| Shared/global state | `van.state()` in `store.js` | `@preact/signals` (default) or Nano Stores | Nano Stores (no built-in alternative) |
| Ecosystem | Small, VanJS-specific | Large — most React libraries/patterns port over via familiarity, `preact/compat` for React-specific packages | Small, Nano JSX-specific |
| Best fit | Smallest possible footprint, zero VDOM, happy with `van.tags` syntax | Default choice — JSX familiarity, hooks, signals give VanJS-like fine-grained updates with a bigger ecosystem | Real-DOM purism without VanJS's state-binding model, explicit control over when re-renders happen |

## Preact (default)

### Why it's the default

Preact is a library, not a framework (see above), genuinely small, and
— paired with `@preact/signals` — gets NoF most of the way back to
VanJS's fine-grained, no-full-re-render update model while adding JSX,
hooks, and a much larger ecosystem than VanJS or Nano JSX have on their
own. `references/philosophy_and_stack.md` covers the VDOM-vs-fine-grained
tradeoff in more depth; the short version is that a plain Preact app
re-renders a component function on state change like React does, but
Preact *with signals* patches the specific DOM text/attribute a signal
feeds, skipping the component re-render + diff entirely for that update
— which is the same "update only what changed, no tree diff" property
VanJS has by design, achieved here as an opt-in optimization rather than
the only way the library works.

**Version note:** Preact 11 reached stable on 2026-09-30 and is what
`scripts/init-nof.sh` pins. `@preact/signals` declares
`preact >= 10.25.0 || >= 11.0.0-0` as its peer range, so it works with
either the 10.x or 11 line. Always confirm current versions against
npm's `latest` tag directly (step 0) — blog posts and docs banners
lag the registry.

### Pages are rendered via `h()`, not by calling them

`renderToApp(HomePage)` renders `h(HomePage)` — it does **not** call
`HomePage()` itself. That distinction matters the moment a page uses a
hook (`useState`, `useStore`, `useSignal`) at its top level: hooks only
work inside Preact's own render, and calling the function yourself runs
it outside one and crashes (`Cannot read properties of undefined
(reading '__H')`). Going through `h()` lets Preact own the render, so
pages and nested components behave identically. The same holds for
`--ui nanojsx` (and a class page can't be constructed without `h()` at
all).

### Component shape

Preact/JSX components take a single props object, not positional
arguments — the idiomatic convention for JSX-based libraries, and a real
difference from VanJS's `Button(label, onClick, extraProps)` style:

```jsx
// js/base/Button.jsx (--bundler vite)
export const Button = ({ label, onClick, ...extraProps }) => (
  <button class="btn" onClick={onClick} {...extraProps}>{label}</button>
);

// usage
<Button label="Add to cart" onClick={() => addToCart(product)} />
```

### No bundler? `htm` instead of JSX

**Preact does not require Vite (or any bundler).** A common assumption is
that a virtual DOM implies a build step — it doesn't. The VDOM is just a
runtime library, loaded from a CDN like any other. The only thing in a
typical Preact project that needs a compiler is **JSX syntax**, which
isn't valid JavaScript; `htm` below removes that last requirement.

JSX itself requires a compiler — it's not valid JavaScript a browser can
run directly. That would force a build step onto Preact as the *default*
UI choice, breaking NoF's no-build-step default. `htm` (Hyperscript
Tagged Markup) is the standard answer: JSX-like syntax using plain
JavaScript [tagged template
literals](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals#tagged_templates),
which the browser parses natively, with the identical runtime behavior
once bound to Preact's `h()`. `scripts/init-nof.sh` generates a small
`js/html.js` that does this binding once:

```js
// js/html.js (generated, bundler=none)
import { h, render } from "preact"; // CDN URL in the actual generated file
import htm from "htm";
export const html = htm.bind(h);
export { h, render };
```

Every other component file imports `html` from there instead of writing
JSX:

```js
// js/base/Button.js (--bundler none, the default)
import { html } from "../html.js";

export const Button = ({ label, onClick, ...extraProps }) => html`
  <button class="btn" onClick=${onClick} ...${extraProps}>${label}</button>
`;
```

Referencing another component inside an `htm` template uses `<${Component} .../>`
(a dynamic/component tag) rather than `<Component />` — `${}` is how
htm's tagged template binds any JS expression, including a component
reference, into the markup.

`--bundler vite` switches every `.js` file using this pattern to a real
`.jsx` file with actual JSX, handled by `@preact/preset-vite` — same
component code, different compiler, your choice of which one to use.

### Local state: hooks

Component-owned state (a form field, a loading flag) uses Preact's
`useState` the same way React does:

```jsx
import { useState } from "preact/hooks";

export const LoginButton = ({ onLogin }) => {
  const [isLoading, setIsLoading] = useState(false);
  // ...
};
```

### Shared/global state: `@preact/signals` (default) — or Nano Stores

`js/store.js` defaults to `@preact/signals`:

```js
import { signal, computed } from "@preact/signals";

export const count = signal(0);
export const increment = () => { count.value++; };
export const doubled = computed(() => count.value * 2);
```

A signal's `.value` can be reassigned directly (`count.value++` is
fine, unlike VanJS's state object) — but for arrays and objects, the
same reassign-don't-mutate rule as VanJS's `van.state()` still applies,
because signals compare by value to decide whether to notify:

```js
// Wrong — mutates in place, no update fires
cart.value.push(product);

// Right — new reference, triggers reactivity
cart.value = [...cart.value, product];
```

**Reading a signal directly in JSX/htm** (not `.value`) is the
optimized path — Preact's deep signals integration binds the specific
text node to the signal and skips re-rendering the component that reads
it entirely:

```jsx
<p>Cart total: ${cartTotal}</p>   {/* direct — optimized */}
<p>Cart total: ${cartTotal.value}</p>  {/* also correct, but causes a normal component re-render */}
```

Outside JSX/htm (inside a plain function, an event handler, a
`computed()`), always use `.value` explicitly.

**When to use `--state nanostores` instead:** Nano Stores is
UI-library-agnostic — the same store can be read by a Preact component
*and* a Nano JSX component *and* plain vanilla JS on the same page (a
genuinely useful NoF scenario: a page with more than one "island" using
different UI libraries sharing state). Signals can't be read outside
Preact's own integration the same way. Pick `--state nanostores` when
that cross-library sharing is an actual requirement, not by default —
signals are simpler and more idiomatically Preact otherwise. See "Nano
Stores" below for the API itself; with Preact, use
`@nanostores/preact`'s `useStore()` hook to subscribe:

```jsx
import { useStore } from "@nanostores/preact";
import { cartTotal } from "../store.js";

const ProductsPage = () => {
  const total = useStore(cartTotal); // re-renders this component on change
  return <p>Cart total: {total.toFixed(2)}</p>;
};
```

## VanJS

Unchanged from NoF's original design — see
`references/reactivity.md`, `references/state_management.md`,
`references/rendering.md`, and `references/components.md`, which are
all still written VanJS-first since it was (and remains) the library
those patterns were designed around. `--ui vanjs` scaffolds exactly what
those documents describe: `van.tags()` component syntax, positional-args
components, `van.state()`/`van.derive()` for all state (local and
global), `van.add()` via `renderToApp()`.

The honest tradeoff versus Preact: no JSX/htm familiarity to lean on, a
much smaller ecosystem, but the smallest footprint of the three and
reactivity that's fine-grained by construction rather than an opt-in
layered on top (there's no "plain VanJS" vs. "VanJS + something" split
the way Preact has plain hooks vs. signals).

## Nano JSX

### The model: real DOM, no built-in reactivity

Nano JSX creates and updates real DOM nodes directly — no virtual DOM at
all, even smaller than Preact. The tradeoff for that: it does not
observe state changes automatically. A component's author is
responsible for calling `this.update()` after any change that should
re-render — there's no `van.state()`-style reactive wrapper and no
hooks. This makes Nano JSX components either:

- **Plain functions**, for anything stateless (most `base/` and many
  `components/` files — identical in shape to Preact's: a props object
  in, JSX/htm out, no `this` involved at all), or
- **Classes extending `Component`**, when the component owns mutable
  local state that needs to trigger its own re-render:

```jsx
// --bundler vite
import { Component } from "nano-jsx";

export class LoginButton extends Component {
  isLoading = false;

  handleClick = async () => {
    this.isLoading = true;
    this.update(); // explicit — Nano JSX won't notice the field change on its own
    try {
      await this.props.onLogin();
    } finally {
      this.isLoading = false;
      this.update();
    }
  };

  render() {
    return (
      <Button label={this.isLoading ? "Logging in..." : "Log in"} onClick={this.handleClick} disabled={this.isLoading || undefined} />
    );
  }
}
```

### Gotcha: boolean attributes

Nano JSX serializes `disabled={false}` as the literal attribute
`disabled="false"` — and any present `disabled` attribute disables the
element. Pass `undefined` instead of `false` to omit it:
`disabled={this.isLoading || undefined}`. (Preact handles real booleans
correctly, so this only applies to `--ui nanojsx`.) This applies to
every boolean attribute (`checked`, `hidden`, `readonly`...), not just
`disabled`.

### No bundler? Same `htm` approach as Preact

Nano JSX's own docs list "No JSX build tools required — uses Tagged
Templates instead of JSX if you prefer" as a built-in feature, and its
`h()` function has the same `(type, props, ...children)` shape `htm`
expects — so the identical `js/html.js` pattern from the Preact section
applies, just bound to Nano JSX's `h` instead:

```js
// js/html.js (generated, UI=nanojsx, bundler=none)
import { h, render, Component } from "nano-jsx"; // CDN URL in the actual file
import htm from "htm";
export const html = htm.bind(h);
export { h, render };
```

### Shared/global state: always Nano Stores

Nano JSX has no reactive store of its own, so `js/store.js` always uses
[Nano Stores](#nano-stores) under `--ui nanojsx`, regardless of
`--state` (which only applies to `--ui preact` — passing it with
`--ui nanojsx` is a scaffolding error explaining this). Since Nano JSX
has no hooks either, a component reads a store value by subscribing
explicitly — `didMount()`/`didUnmount()` lifecycle methods plus
`this.update()` in the subscription callback:

```jsx
import { Component } from "nano-jsx";
import { cartTotal } from "../store.js";

export class ProductsPage extends Component {
  didMount() {
    this.unsubscribe = cartTotal.subscribe(() => this.update());
  }
  didUnmount() {
    this.unsubscribe?.(); // release the subscription, or the store keeps a dead component alive
  }
  render() {
    return <p>Cart total: ${cartTotal.get().toFixed(2)}</p>;
  }
}
```

This subscribe → update → unsubscribe cycle is the Nano JSX
equivalent of what Preact's `useStore()` hook or VanJS's built-in
reactivity does automatically — the connection is explicit here because
neither Nano JSX nor Nano Stores assumes the other exists.

## Nano Stores

A tiny (~1KB), UI-library-agnostic state library. `atom()` creates a
writable store, `computed()` derives one from others, both expose
`.get()`/`.set()`/`.subscribe()`:

```js
import { atom, computed } from "nanostores";

export const count = atom(0);
export const increment = () => count.set(count.get() + 1);
export const doubled = computed(count, (c) => c * 2);
```

Used two ways in NoF:

- **Required for `--ui nanojsx`'s `js/store.js`** (no alternative — see
  above).
- **Optional for `--ui preact`'s `js/store.js`** via `--state
  nanostores`, when a store genuinely needs to be shared outside
  Preact's own signal integration (see the Preact section above for
  when that's worth it).

Framework bindings subscribe a component to a store and trigger its
re-render on change: `@nanostores/preact`'s `useStore()` hook for
Preact; Nano JSX has no official binding package, so the
subscribe/`this.update()`/unsubscribe pattern shown above is the direct
equivalent, written by hand.

## Worked examples

`examples/vanjs/`, `examples/preact/`, and `examples/nanojsx/` are
parallel, self-contained implementations of the same small shop app
(base elements, business components, a page, a store, a router, the
render helpers). The fastest way to see what actually differs between
the libraries is to diff the same file across them — `components/counter.js`
for local state, `stores/store.js` for shared state, and
`components/cart-badge.js` for reading shared state from a component.

## Choosing between them for a given project

- Person has React/JSX experience, wants the biggest ecosystem, no
  strong opinion otherwise → **Preact** (the default — just scaffold
  it).
- Person explicitly wants the smallest possible footprint, is fine with
  `van.tags()` syntax, or this skill's existing non-UI-specific
  reference docs (reactivity/state/rendering/components) are the
  primary thing being followed closely → **VanJS**.
- Person wants real-DOM updates with no VDOM at all but isn't drawn to
  VanJS's state-binding model, or explicitly asks for Nano JSX /
  Nano Stores by name → **Nano JSX**.
- Ambiguous and nothing above applies → default to Preact; it's the
  broadest-fit choice and the one this skill's `--ui` flag defaults to
  for exactly that reason.
