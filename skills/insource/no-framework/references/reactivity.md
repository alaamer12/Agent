# Reactivity & Memoization with `van.derive()`

## What it does

`van.derive()` creates a computed value that automatically re-runs only
when one of the `van.state()` values it reads inside its function
actually changes. No dependency array to maintain — VanJS tracks which
state values were read during the derive function's last run and
re-triggers based on that.

```jsx
const searchTerm = van.state("");
const products = van.state([...]);

const filteredProducts = van.derive(() => {
  console.log("Filtering executed"); // only logs when searchTerm or products change
  return products.val.filter(p =>
    p.name.toLowerCase().includes(searchTerm.val.toLowerCase())
  );
});
```

This replaces what `useMemo` does in React, but automatically — no
dependency array to get wrong or forget to update.

## Before / after: avoiding recomputation on every render

```jsx
// Bad — expensiveSort() runs every time this function is called,
// even if products.val hasn't changed since the last call.
const bad = () => expensiveSort(products.val);

// Good — sortedProducts only recomputes when products.val actually changes.
const sortedProducts = van.derive(() => expensiveSort(products.val));
```

Use `sortedProducts.val` wherever the sorted list is needed; VanJS
handles the caching.

## Chaining derives

Derived values can depend on other derived values — VanJS tracks the
dependency chain the same way:

```jsx
const cart = van.state([]);

const cartTotal = van.derive(() =>
  cart.val.reduce((sum, item) => sum + item.price, 0)
);

const cartTotalWithTax = van.derive(() => cartTotal.val * 1.08);
```

## When NOT to use `van.derive()`

- For values that don't actually depend on other reactive state — just
  use a plain constant or function.
- For side effects (logging, network calls, DOM manipulation outside the
  returned tree) — `van.derive()` is for computing a *value*, not for
  running effects. If a genuine side effect needs to run on state change
  (rare in NoF, since most rendering is declarative), handle it
  explicitly at the point of the state change (inside the action in
  `store.js`) rather than inside a derive.

## The habit to build

Any time a render function or component body does a nontrivial
computation directly from state (`.filter()`, `.sort()`, `.reduce()`, a
formatting pass over a list), that's a candidate for `van.derive()`.
Reach for it by default rather than inlining the computation — it costs
nothing when the computation is cheap and saves real work when it isn't.
