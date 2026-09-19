// examples/routing/router.js
// Navigo route table with file-based page loading (static HTML pages).
// For pages that need reactive components instead of static HTML, see
// references/routing.md for the renderToApp() variant.
//
// Loaded via a CDN URL, same as VanJS elsewhere in this skill — a bare
// `import Navigo from 'navigo'` specifier can't resolve in a browser
// without a bundler or import map, so this matches the no-bundler
// default. If the project already uses Vite (see references/tooling.md),
// swap this for the bare-specifier form instead.

import Navigo from 'https://cdn.jsdelivr.net/npm/navigo@8.11.1/+esm';

const router = new Navigo('/');

async function loadPage(page) {
  const html = await fetch(`pages/${page}.html`).then(r => r.text());
  document.getElementById('app').innerHTML = html;
}

router.on('/', () => loadPage('home'));
router.on('/products', () => loadPage('products'));
router.on('/cart', () => loadPage('cart'));
router.on('/about', () => loadPage('about'));

router.resolve();

// Expose for the navigateTo() helper in utils.js
window.router = router;

export default router;
