# Code Health: Growth, Smells, and Refactoring in NoF

This is about the *dynamic* discipline on top of the static layout in
`project_structure.md` — when and how a NoF project's structure should
shift as it grows, what to watch for as specifically NoF-shaped rot, and
how to fix it once spotted. Structure decisions here are trigger-based:
don't pre-emptively adopt a "grown-up" structure on a small project —
start flat, shift when a concrete trigger below actually applies.

## 1. Structural shifts as the project grows

### Stage 0 → 1: flat `components/` splits into `base/` + `components/`

**Trigger:** the same raw tag+class combination (a styled button, a
styled image) is getting reimplemented slightly differently inside two
or more business components. See `components.md#base-vs-components`
for the full pattern.

**Before:**
```
js/components/
├── Button.js          # used raw by ProductCard, LoginForm, Modal —
│                       # each imports it slightly differently
├── ProductCard.js
├── LoginForm.js
└── Modal.js
```

**After:**
```
js/
├── base/
│   └── Button.js       # dumb, app-agnostic primitive
└── components/
    ├── LoginButton.js   # built from base/Button.js
    ├── ProductCard.js   # built from base/Button.js
    └── Modal.js
```

Update imports as part of this move (`./Button.js` becomes
`../base/Button.js` from inside `components/`) — mechanical, not a
redesign. This shift is orthogonal to and usually happens before the
feature-grouping shift below; a project can need `base/` well before it
has enough components to justify grouping by feature.

### Stage 1 → 2: flat `components/` becomes grouped by feature

**Trigger:** `components/` passes roughly 10-15 files, or you're
scrolling/searching to find the component you want rather than knowing
where it lives. This applies within `js/components/` — `js/base/`
usually stays flat much longer, since primitives are few by design.

**Before:**
```
js/
├── base/
│   ├── Button.js
│   └── Modal.js
└── components/
    ├── ProductCard.js
    ├── ProductGrid.js
    ├── CartSummary.js
    ├── CartItem.js
    ├── UserAvatar.js
    └── ...
```

**After:**
```
js/
├── base/
│   ├── Button.js
│   └── Modal.js
└── components/
    ├── cart/
    │   ├── CartSummary.js
    │   └── CartItem.js
    └── products/
        ├── ProductCard.js
        └── ProductGrid.js
```

Update the relative import paths as part of this move (`../base/Button.js`
becomes `../../base/Button.js` from inside `components/cart/`, etc.) —
this is a mechanical rename, not a redesign; component internals don't
change.

### Stage 2 → 3: single `store.js` splits by domain

**Trigger:** `store.js` covers more than roughly two unrelated domains
(e.g. cart state and user state and notification state all in one
file), or it's grown past roughly 150-200 lines.

**Before** (`js/store.js`, one file, multiple unrelated domains):
```js
import van from "https://cdn.jsdelivr.net/npm/vanjs-core@1.6.0/src/van.min.js";

export const cart = van.state([]);
export const addToCart = (product) => {
  cart.val = [...cart.val, product];
};
export const cartTotal = van.derive(() =>
  cart.val.reduce((sum, item) => sum + item.price, 0)
);

export const user = van.state(null);
export const login = (userData) => { user.val = userData; };
export const logout = () => { user.val = null; };

export const notifications = van.state([]);
export const pushNotification = (msg) => {
  notifications.val = [...notifications.val, msg];
};
```

**After** (split by domain, re-exported from a barrel file so existing
imports across the app don't need to change):

`js/stores/cart.js`:
```js
import van from "https://cdn.jsdelivr.net/npm/vanjs-core@1.6.0/src/van.min.js";

export const cart = van.state([]);
export const addToCart = (product) => {
  cart.val = [...cart.val, product];
};
export const cartTotal = van.derive(() =>
  cart.val.reduce((sum, item) => sum + item.price, 0)
);
```

`js/stores/user.js`:
```js
import van from "https://cdn.jsdelivr.net/npm/vanjs-core@1.6.0/src/van.min.js";

export const user = van.state(null);
export const login = (userData) => { user.val = userData; };
export const logout = () => { user.val = null; };
```

`js/stores/notifications.js`:
```js
import van from "https://cdn.jsdelivr.net/npm/vanjs-core@1.6.0/src/van.min.js";

export const notifications = van.state([]);
export const pushNotification = (msg) => {
  notifications.val = [...notifications.val, msg];
};
```

`js/store.js` (now a barrel file — this is what makes the split
non-breaking for the rest of the app):
```js
export * from './stores/cart.js';
export * from './stores/user.js';
export * from './stores/notifications.js';
```

Every existing `import { cart, addToCart } from '../store.js'` elsewhere
in the app keeps working unchanged, because the barrel file re-exports
everything from the same path. This is what makes the split safe to do
incrementally rather than needing a big-bang rewrite of every importer.

### Stage 3 → 4: route handlers move out of `router.js`

**Trigger:** a route's handler in `router.js` grows past a one-line
`renderToApp(SomePage)` call — conditional logic, param parsing, auth
guards living inline in the route table.

**Before** (`js/router.js`, logic growing inline):
```js
import Navigo from "https://cdn.jsdelivr.net/npm/navigo@8.11.1/+esm";
import { renderToApp } from './utils.js';
import { user } from './store.js';
import { ProductsPage } from './components/ProductsPage.js';
import { AccountPage } from './components/AccountPage.js';
import { LoginPage } from './components/LoginPage.js';

const router = new Navigo('/');

router.on('/account', () => {
  if (!user.val) {
    // auth guard logic inline in the route table
    renderToApp(LoginPage);
    return;
  }
  renderToApp(AccountPage);
});

router.on('/products/:id', ({ data }) => {
  // param parsing and validation inline
  const id = parseInt(data.id, 10);
  if (isNaN(id) || id < 1) {
    renderToApp(() => "Invalid product ID");
    return;
  }
  renderToAppWithProps(ProductsPage, { productId: id });
});

router.resolve();
window.router = router;
export default router;
```

**After** (route logic extracted into `js/routes/`, `router.js`
shrinks back down to just the table):

`js/routes/account.js`:
```js
import { renderToApp } from '../utils.js';
import { user } from '../store.js';
import { AccountPage } from '../components/AccountPage.js';
import { LoginPage } from '../components/LoginPage.js';

export const accountRoute = () => {
  renderToApp(user.val ? AccountPage : LoginPage);
};
```

`js/routes/products.js`:
```js
import { renderToApp, renderToAppWithProps } from '../utils.js';
import { ProductsPage } from '../components/ProductsPage.js';

export const productRoute = ({ data }) => {
  const id = parseInt(data.id, 10);
  if (isNaN(id) || id < 1) {
    renderToApp(() => "Invalid product ID");
    return;
  }
  renderToAppWithProps(ProductsPage, { productId: id });
};
```

`js/router.js` (back to a clean table):
```js
import Navigo from "https://cdn.jsdelivr.net/npm/navigo@8.11.1/+esm";
import { accountRoute } from './routes/account.js';
import { productRoute } from './routes/products.js';

const router = new Navigo('/');

router.on('/account', accountRoute);
router.on('/products/:id', productRoute);

router.resolve();
window.router = router;
export default router;
```

`router.js` is now legible at a glance — the route table — and each
route's actual logic lives in its own testable, focused file.

## 2. Code smells specific to NoF

These are the failure patterns particular to this architecture, not
generic smells restated. Each is worth recognizing on sight.

### Mutating `.val` in place instead of reassigning

This is the most important one — it doesn't throw an error, it just
silently fails to update the UI, which makes it a nasty one to debug.

```js
// BEFORE — smell: mutates in place, VanJS never sees a change,
// the UI silently goes stale even though the data "changed"
export const addToCart = (product) => {
  cart.val.push(product);
};

// AFTER — new reference assigned to .val, reactivity fires correctly
export const addToCart = (product) => {
  cart.val = [...cart.val, product];
};
```

Same pattern for objects (`user.val.name = x` vs.
`user.val = { ...user.val, name: x }`) — see `state_management.md` for
the full rule.

### `van.derive()` used for a side effect instead of a computed value

```js
// BEFORE — smell: derive is doing a side effect (network call,
// logging), not computing and returning a value
const _ = van.derive(() => {
  console.log("Cart changed:", cart.val);
  fetch('/api/analytics', { method: 'POST', body: JSON.stringify(cart.val) });
});

// AFTER — the actual computed value stays a derive; the side effect
// moves to where the state change actually happens (the action)
export const addToCart = (product) => {
  cart.val = [...cart.val, product];
  fetch('/api/analytics', { method: 'POST', body: JSON.stringify(cart.val) });
};

export const cartTotal = van.derive(() =>
  cart.val.reduce((sum, item) => sum + item.price, 0)
);
```

### Global state that only one component ever touches

```js
// BEFORE — smell: in store.js, but nothing outside ProductSearch.js
// ever reads or writes searchTerm
export const searchTerm = van.state("");

// AFTER — demoted to local state inside the one component that
// actually uses it
export const ProductSearch = () => {
  const searchTerm = van.state("");
  // ...
};
```
If a second component later genuinely needs it, promote it back to
`store.js` at that point — not before.

### A component reaching into `store.js` directly instead of taking a callback prop

Already called out in `components.md` — worth recognizing here as a
smell in an existing codebase, not just a rule for new code:

```js
// BEFORE — smell: ProductCard is now only usable with the global
// cart, can't be reused with a different "add" behavior
import { addToCart } from '../store.js';
import { Button } from '../base/Button.js';

export const ProductCard = (product) => {
  return div({ class: "product-card" },
    h3(product.name),
    Button("Add to Cart", () => addToCart(product))
  );
};

// AFTER — takes the action as a prop, reusable anywhere
import { Button } from '../base/Button.js';

export const ProductCard = (product, onAdd) => {
  return div({ class: "product-card" },
    h3(product.name),
    Button("Add to Cart", () => onAdd(product))
  );
};
// caller: ProductCard(product, addToCart)
```

### `renderToApp()` bypassed with direct `van.add()` calls

```js
// BEFORE — smell: bypasses the shared render helper, inconsistent
// mount behavior between this page and every other page
const app = document.getElementById('app');
van.add(app, ProductsPage());

// AFTER
renderToApp(ProductsPage);
```

## 3. Hotspots: which files rot first, and how to tell at a glance

In NoF, `store.js` and `router.js` are the two files everything else
touches, which makes them the ones most likely to accumulate unrelated
concerns over time if nothing pushes back on that.

**`store.js`** — healthy: short, each exported group of state+actions
serves one clear domain, reads top-to-bottom without needing to jump
around. Unhealthy: several unrelated domains mixed together, actions
that do more than reassign state (heavy business logic, side effects
baked in with no separation), growing past roughly 150-200 lines. See
the store-split shift above once this shows up.

**`router.js`** — healthy: each `router.on(...)` line is a one-liner
pointing at a page component or an extracted route handler; the whole
file is scannable as a table of contents for the app's routes.
Unhealthy: inline conditionals, param validation, or auth checks living
directly in the route table. See the route-extraction shift above.

Everything else in NoF (individual components, individual pages) tends
to stay naturally bounded because each one is a small pure function —
these two files are the ones worth periodically glancing at specifically
*because* nothing about the architecture inherently limits their growth
the way a component's single-responsibility shape does.
