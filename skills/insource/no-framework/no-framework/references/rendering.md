# Rendering Pattern

## Why a shared render helper

Every page should mount the same way — clear the app container, then add
the new component tree. Doing this ad hoc in each page's script invites
inconsistency (some pages forget to clear `#app`, some use `innerHTML =`
directly and lose event listeners set elsewhere). Centralize it once in
`js/utils.js` and always render through it.

## The utility set

```jsx
// js/utils.js
import van from "https://cdn.jsdelivr.net/npm/vanjs-core@1.6.0/src/van.min.js";

/**
 * Clean way to render any VanJS component to the main app container.
 */
export const renderToApp = (component) => {
  const app = document.getElementById('app');
  if (!app) {
    console.error("[NoF] #app element not found");
    return;
  }
  app.innerHTML = '';
  van.add(app, component());
};

/**
 * Render a component that takes props.
 */
export const renderToAppWithProps = (component, props = {}) => {
  const app = document.getElementById('app');
  if (!app) return;
  app.innerHTML = '';
  van.add(app, component(props));
};

/**
 * Navigate helper — combines routing with rendering intent.
 */
export const navigateTo = (path) => {
  window.router.navigate(path);
};
```

## Usage

```jsx
import { renderToApp } from "../js/utils.js";
import { ProductsPage } from "./ProductsPage.js";

renderToApp(ProductsPage);
```

With props:

```jsx
import { renderToAppWithProps } from "../js/utils.js";

renderToAppWithProps(ProductDetailPage, { productId: 42 });
```

## The rule

Never call `van.add()` directly against `#app` from inside a page or
component — always go through `renderToApp()` / `renderToAppWithProps()`.
This is what keeps every page's mount behavior identical, and it's the
one place to fix if the mounting strategy ever needs to change (adding a
transition, a loading state, error boundaries, etc.) — a single choke
point rather than hunting through every page file.
