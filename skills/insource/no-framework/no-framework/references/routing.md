# Routing with Navigo

## Setup

One Navigo instance per app, defined in `js/router.js`:

```jsx
import Navigo from "https://cdn.jsdelivr.net/npm/navigo@8.11.1/+esm";

const router = new Navigo('/');

router.on('/products', () => loadPage('products'));
router.on('/cart', () => loadPage('cart'));
router.on('/', () => loadPage('home'));

router.resolve();

export default router;
```

**Import this via a CDN URL, not a bare specifier.** `import Navigo from
'navigo'` looks identical to how you'd write it once a bundler is
involved, but in a plain browser (no Vite, no import map) a bare
specifier can't resolve at all — the page fails outright, not just
performs worse. Load it via CDN URL exactly the way VanJS is loaded
elsewhere in this skill (`references/tooling.md`), or add an import map
in `index.html` mapping `"navigo"` to that same CDN URL if you want the
bare-specifier syntax without a bundler. Once the project actually adds
Vite (see `references/tooling.md`), switch to the bare `import Navigo
from 'navigo'` form and let Vite resolve it from `node_modules` — don't
mix the two styles in one project.

## File-based page loading

Each route maps to a page file under `pages/`, fetched and injected on
navigation:

```jsx
async function loadPage(page) {
  const html = await fetch(`pages/${page}.html`).then(r => r.text());
  document.getElementById('app').innerHTML = html;
}
```

For pages that need to run VanJS component logic rather than just static
HTML, have the page's own script call `renderToApp()` with its top-level
component after the route fires, instead of injecting raw HTML:

```jsx
router.on('/products', async () => {
  const { ProductsPage } = await import('../pages/products.js');
  renderToApp(ProductsPage);
});
```

Either approach (raw HTML injection for simple static pages, component
rendering for dynamic ones) is valid within NoF — pick based on whether
the page needs reactive state.

## CDN scripts load once, not per navigation

In the standard NoF setup, `index.html` loads once and every route
change after that happens by `renderToApp()` swapping DOM content inside
`#app` — no page reload, no re-fetching `index.html`. Because ES modules
are cached by the browser per URL, a CDN import like the VanJS or Navigo
one above only executes once for the whole session, no matter how many
files `import` it or how many times the user navigates.

The one place this isn't automatic: if a project uses the file-based
raw-HTML-fragment loading shown above (`fetch('pages/x.html')`), and any
individual `pages/*.html` file also has its own `<script src="...">` tag
pulling in VanJS or Navigo again, that would re-fetch and re-evaluate the
library on every navigation to that page. Keep library imports in
`js/router.js`, `js/store.js`, or `js/utils.js` — not inside the
per-page HTML fragments themselves — so this doesn't creep in.

## Clean URLs

Navigo uses the History API for clean URLs (no `#/` hash routing) by
default when instantiated as `new Navigo('/')`. This requires the dev
server to serve `index.html` for unknown paths (a typical SPA fallback
config) — with `live-server`, that's `--entry-file=index.html`, not
`--spa` (which does hash-based rewriting and actively conflicts with
Navigo's clean-URL mode). See `references/tooling.md` for the full
explanation and the exact command, and `references/deployment.md` for
the equivalent config production hosting needs — the local dev-server
fix does not carry over to production on its own.

## Navigation from within components

Use the `navigateTo()` helper from `js/utils.js` rather than calling
`router.navigate()` directly from scattered components, so navigation
goes through one consistent entry point:

```jsx
import { navigateTo } from "../js/utils.js";

Button("View Cart", () => navigateTo('/cart'))
```
