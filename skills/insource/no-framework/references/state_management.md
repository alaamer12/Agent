# State Management

## Three kinds of state

- **Local state** — inside a component, via `van.state()`, when nothing
  outside that component needs to read or change it (an input's current
  value, whether a dropdown is open).
- **Global state** — centralized in `js/store.js`, when more than one
  component/page needs to read or change it (cart contents, logged-in
  user, app-wide filters).
- **Derived state** — computed from other state via `van.derive()`, never
  stored and manually kept in sync by hand. If a value can be computed
  from other state, it should be derived, not duplicated into its own
  `van.state()`.

## The one rule that matters: always assign a new value

VanJS reactivity triggers on assignment to `.val`, not on mutation of the
existing value. Mutating an array or object in place and expecting
reactive updates to fire is the single most common NoF bug.

```jsx
// Wrong — mutates in place, VanJS won't detect this as a change
cart.val.push(product);

// Right — assigns a new array, triggers reactivity
cart.val = [...cart.val, product];
```

The same applies to objects:

```jsx
// Wrong
user.val.name = "New Name";

// Right
user.val = { ...user.val, name: "New Name" };
```

This is a deliberate design choice, not a limitation to work around — it
keeps reactivity predictable and makes state changes easy to reason
about (every real change is a `.val =` assignment you can grep for).

## The `store.js` pattern

Centralize global state and the actions that touch it in one file, so
there's one place to look for "what can change the cart," not scattered
`cart.val = ...` calls across every component that happens to touch the
cart.

```jsx
// js/store.js
import van from "https://cdn.jsdelivr.net/npm/vanjs-core@1.6.0/src/van.min.js";

export const cart = van.state([]);

export const addToCart = (product) => {
  cart.val = [...cart.val, { ...product, cartId: Date.now() }];
};

export const removeFromCart = (cartId) => {
  cart.val = cart.val.filter(item => item.cartId !== cartId);
};

export const cartTotal = van.derive(() =>
  cart.val.reduce((sum, item) => sum + item.price, 0)
);
```

Components import what they need from `store.js` rather than owning
their own copy of shared state:

```jsx
import { cart, addToCart, cartTotal } from "../store.js";
```

## When to keep something local instead

Not everything belongs in the global store. A search input's current
text, a modal's open/closed flag, a form's in-progress values before
submit — these are usually local to the component that owns them, using
`van.state()` directly inside that component's function. Promote
something to the global store only when a second component actually
needs it; premature globalization just makes local UI state harder to
reason about for no benefit.
