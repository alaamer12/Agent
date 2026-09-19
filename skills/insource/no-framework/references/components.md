# Component Architecture

## Components are pure functions

A NoF component is a function that takes props (and optionally
callbacks) and returns a VanJS DOM element tree. No classes, no
lifecycle methods, no `this`.

```jsx
import van from "https://cdn.jsdelivr.net/npm/vanjs-core@1.6.0/src/van.min.js";
import { Button } from "../base/Button.js";

const { div, h3, span } = van.tags;

export const ProductCard = (product, onAdd) => {
  return div({ class: "product-card" },
    h3(product.name),
    span(`$${product.price}`),
    Button("Add to Cart", () => onAdd(product))
  );
};
```

Usage:

```jsx
products.map(p => ProductCard(p, addToCart))
```

## Why pure functions

- **Reusability** — a pure component behaves the same way anywhere it's
  called, with no hidden dependency on where it's mounted.
- **Testability** — call it with test props, assert on the returned DOM
  tree; no mounting/unmounting harness needed.
- **No surprise state** — if a component needs its own state, that state
  is declared explicitly with `van.state()` inside the function, visible
  right there rather than hidden in a class field or a lifecycle hook.

## Composing components

Build small components and compose them into larger ones, the same way
`ProductCard` above composes the `Button` primitive from `js/base/`.
Keep each component focused on one piece of UI; a component that's
assembling several unrelated concerns is usually a sign it should be
split. See "Base vs. components" below for the base/business-component
distinction this composition relies on.

## Naming and organization

- Name components in PascalCase (`ProductCard`, not `productCard` or
  `product-card`) to visually distinguish them from plain functions and
  values at a glance.
- One component per file under `js/components/`, file name matching the
  component name (`ProductCard.js` exports `ProductCard`).
- Accept callbacks as plain function props (`onAdd`, `onRemove`) rather
  than reaching into global store actions directly from inside a leaf
  component — this keeps the component reusable in contexts where the
  action should do something different (e.g. a "recently viewed" list
  using a `ProductCard` with a different `onAdd` handler than the main
  product grid).

## Local state inside a component

A component can hold its own `van.state()` for state nothing outside it
needs:

```jsx
const { div, button } = van.tags;

export const Counter = () => {
  const count = van.state(0);
  return div(
    button({ onclick: () => count.val-- }, "-"),
    () => count.val,
    button({ onclick: () => count.val++ }, "+")
  );
};
```

This is fine and expected — not everything needs to go through
`store.js`. See `state_management.md` for the local-vs-global line.

## Base vs. components

As a project grows past a handful of components, split `js/components/`
into two layers:

- **`js/base/`** — dumb, app-agnostic primitives. Thin wrappers around a
  native tag plus a default class and the props that tag naturally
  takes. No business meaning, no knowledge of the app's domain, no
  store imports. Genuinely small — usually under 10 lines. Examples:
  `Button`, `Image`, `Input`, `Card`.
- **`js/components/`** — business components, built *out of* `base/`
  primitives rather than out of native tags directly. These carry app
  meaning: they know about auth, products, carts, whatever the domain
  is, and they compose one or more `base/` elements to express it.

```jsx
// js/base/button.js — dumb, reusable anywhere, no app knowledge
export const Button = (label, onClick, extraProps = {}) =>
  button({ class: "btn", onclick: onClick, ...extraProps }, label);

// js/components/login-button.js — business meaning, built from base/
import { Button } from "../base/button.js";

export const LoginButton = (onLogin) => {
  const isLoading = van.state(false);
  const handleClick = async () => {
    isLoading.val = true;
    try { await onLogin(); } finally { isLoading.val = false; }
  };
  return Button(
    () => (isLoading.val ? "Logging in..." : "Log in"),
    handleClick,
    { disabled: () => isLoading.val }
  );
};
```

The same pattern applies to any base element: `Image` (`base/`) becomes
`HeroImage` (`components/`) by adding a headline overlay and container;
`Button` becomes `LoginButton` by adding auth-specific loading state.
See `examples/base/button.js` + `examples/components/login-button.js`
and `examples/base/image.js` + `examples/components/hero-image.js` for
both pairings worked through in full.

**When to introduce the split:** a small project is fine with just
`js/components/`. Reach for `js/base/` once you notice the same raw
tag+class combination (a styled button, a styled image) getting
reimplemented slightly differently inside two or more business
components — that duplication is the signal to extract the shared
primitive into `base/` and have both business components import it,
rather than introducing the folder upfront on a project that doesn't
need it yet.

**Rule of thumb for which folder a new component belongs in:** if it
imports from `store.js`, knows an app-specific noun (product, cart,
user, login), or would stop making sense in a completely different
app, it's a `components/` component. If it would drop into any project
unchanged, it's a `base/` element.
