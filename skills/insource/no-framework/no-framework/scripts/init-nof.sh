#!/usr/bin/env bash
# scripts/init-nof.sh
#
# Scaffolds a new NoF (No Frameworks) project: VanJS + Navigo, standard
# directory layout, index.html, store.js, utils.js, router.js,
# js/base/ (app-agnostic primitives) and js/components/ (business
# components built from base/).
#
# Default: a clean, minimal Hello World — one route, one trivial
# page, an empty store, and a single base/Button.js primitive. The
# right starting point for an actual project.
#
# --demo: a fuller worked example (cart store with actions/derive, a
# base/Button.js primitive, a LoginButton business component built from
# it, a second route, product-card-style composition) — useful for
# learning the patterns or as a reference, not meant to be the base you
# build a real project on top of.
#
# --bundler vite: adds Vite instead of the default no-build-step CDN
# setup. Switches every library import from a CDN URL to a bare
# specifier (import van from "vanjs-core"), generates package.json,
# vite.config.js, and a .gitignore for node_modules/dist, and adjusts
# index.html and the README's run instructions accordingly. See
# references/tooling.md#switching-an-existing-cdn-based-project-to-npm-packages-via-vite
# for what this does and why it's opt-in rather than the default.
#
# Usage:
#   bash init-nof.sh <project-name>                       # clean Hello World (default)
#   bash init-nof.sh <project-name> --demo                 # fuller worked example
#   bash init-nof.sh <project-name> --bundler vite          # Vite + npm packages
#   bash init-nof.sh <project-name> --demo --bundler vite    # both

set -euo pipefail

PROJECT_NAME=""
DEMO=false
BUNDLER=""

args=("$@")
i=0
while [ $i -lt ${#args[@]} ]; do
  arg="${args[$i]}"
  case "$arg" in
    --demo)
      DEMO=true
      ;;
    --bundler)
      i=$((i + 1))
      if [ $i -ge ${#args[@]} ]; then
        echo "Error: --bundler requires a value (only 'vite' is supported)" >&2
        exit 1
      fi
      BUNDLER="${args[$i]}"
      if [ "$BUNDLER" != "vite" ]; then
        echo "Error: unsupported --bundler value '$BUNDLER' (only 'vite' is supported)" >&2
        exit 1
      fi
      ;;
    --*)
      echo "Error: unknown flag '$arg'" >&2
      exit 1
      ;;
    *)
      if [ -z "$PROJECT_NAME" ]; then
        PROJECT_NAME="$arg"
      fi
      ;;
  esac
  i=$((i + 1))
done

PROJECT_NAME="${PROJECT_NAME:-nof-app}"

# NOTE: the VanJS/Navigo versions pinned below were current as of this
# skill's last update. Per SKILL.md step 0, verify the actual current
# versions before running this in a real project and update these
# variables if newer ones are available and compatible.
VANJS_VERSION="1.6.0"
NAVIGO_VERSION="8.11.1"
VITE_VERSION="6.0.0"

if [ -e "$PROJECT_NAME" ]; then
  echo "Error: '$PROJECT_NAME' already exists. Choose a different name or remove it first." >&2
  exit 1
fi

if [ "$DEMO" = true ]; then
  echo "Scaffolding NoF project (with demo example): $PROJECT_NAME"
else
  echo "Scaffolding NoF project (clean Hello World): $PROJECT_NAME"
fi
if [ "$BUNDLER" = "vite" ]; then
  echo "  with Vite (npm packages instead of CDN imports)"
fi

mkdir -p "$PROJECT_NAME/js/base" "$PROJECT_NAME/js/components" "$PROJECT_NAME/pages" "$PROJECT_NAME/css"

# --- Import lines: CDN URL by default, bare specifier under --bundler vite --
# Every generated file that imports van or Navigo uses these variables
# instead of hardcoding either form, so the CDN vs. npm-package choice
# only has to be made once here.
if [ "$BUNDLER" = "vite" ]; then
  VAN_IMPORT="import van from \"vanjs-core\";"
  NAVIGO_IMPORT="import Navigo from \"navigo\";"
else
  VAN_IMPORT="import van from \"https://cdn.jsdelivr.net/npm/vanjs-core@${VANJS_VERSION}/src/van.min.js\";"
  NAVIGO_IMPORT="import Navigo from \"https://cdn.jsdelivr.net/npm/navigo@${NAVIGO_VERSION}/+esm\";"
fi

# --- index.html (same for both modes) -------------------------------------
cat > "$PROJECT_NAME/index.html" <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NoF App</title>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <div id="app"></div>
  <script type="module" src="js/router.js"></script>
</body>
</html>
EOF

# --- js/utils.js (same for both modes) -------------------------------------
cat > "$PROJECT_NAME/js/utils.js" <<EOF
// Rendering helpers. Always render through these, not van.add() directly.

${VAN_IMPORT}

export const renderToApp = (component) => {
  const app = document.getElementById('app');
  if (!app) {
    console.error("[NoF] #app element not found");
    return;
  }
  app.innerHTML = '';
  van.add(app, component());
};

export const renderToAppWithProps = (component, props = {}) => {
  const app = document.getElementById('app');
  if (!app) return;
  app.innerHTML = '';
  van.add(app, component(props));
};

export const navigateTo = (path) => {
  window.router.navigate(path);
};
EOF

# --- css/style.css (same for both modes) ------------------------------------
cat > "$PROJECT_NAME/css/style.css" <<'EOF'
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: system-ui, -apple-system, sans-serif;
  line-height: 1.5;
  color: #1a1a1a;
}

.page {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  background: #1a1a1a;
  color: white;
  cursor: pointer;
  font-size: 1rem;
}

.btn:hover {
  opacity: 0.85;
}

.product-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
}
EOF

if [ "$DEMO" = false ]; then

  # ==========================================================================
  # CLEAN HELLO WORLD (default)
  # ==========================================================================

  # --- js/store.js — empty, ready for real state -----------------------------
  cat > "$PROJECT_NAME/js/store.js" <<EOF
// Global state. Centralize shared state and its actions here.
// Rule: always assign a new value to .val — never mutate in place.
//
// Example:
//   export const count = van.state(0);
//   export const increment = () => { count.val = count.val + 1; };
//   export const doubled = van.derive(() => count.val * 2);

${VAN_IMPORT}
EOF

  # --- js/base/Button.js — dumb, app-agnostic primitive ------------------------
  cat > "$PROJECT_NAME/js/base/Button.js" <<EOF
// Dumb, app-agnostic primitive: a thin wrapper around the native
// <button>, no business meaning. Business components import and build
// on this rather than writing button(...) directly. See the
// no-framework skill's references/components.md#base-vs-components.

${VAN_IMPORT}

const { button } = van.tags;

export const Button = (label, onClick, extraProps = {}) => {
  return button({ class: "btn", onclick: onClick, ...extraProps }, label);
};
EOF

  # --- js/components/HomePage.js — minimal single component -------------------
  cat > "$PROJECT_NAME/js/components/HomePage.js" <<EOF
${VAN_IMPORT}
import { Button } from "../base/Button.js";

const { div, h1, p } = van.tags;

export const HomePage = () => {
  return div({ class: "page home-page" },
    h1("Hello, NoF"),
    p("Edit js/components/HomePage.js to get started."),
    Button("Get started", () => console.log("Edit js/base/Button.js and js/components/HomePage.js"))
  );
};
EOF

  # --- js/router.js — one route -----------------------------------------------
  cat > "$PROJECT_NAME/js/router.js" <<EOF
${NAVIGO_IMPORT}
import { renderToApp } from './utils.js';
import { HomePage } from './components/HomePage.js';

const router = new Navigo('/');

router.on('/', () => renderToApp(HomePage));

router.resolve();
window.router = router;

export default router;
EOF

else

  # ==========================================================================
  # --demo: fuller worked example (cart store, Button, two routes)
  # ==========================================================================

  # --- js/store.js — cart demo with action + derive ---------------------------
  cat > "$PROJECT_NAME/js/store.js" <<EOF
// Global state. Centralize shared state and its actions here.
// Rule: always assign a new value to .val — never mutate in place.
// This is demo content (--demo) — replace with your app's real state.

${VAN_IMPORT}

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
EOF

  # --- js/base/Button.js — dumb, app-agnostic primitive ------------------------
  cat > "$PROJECT_NAME/js/base/Button.js" <<EOF
// Dumb, app-agnostic primitive: a thin wrapper around the native
// <button>, no business meaning. Business components (LoginButton
// below, ProductCard) import and build on this rather than writing
// button(...) directly. See the no-framework skill's
// references/components.md#base-vs-components.

${VAN_IMPORT}

const { button } = van.tags;

export const Button = (label, onClick, extraProps = {}) => {
  return button({ class: "btn", onclick: onClick, ...extraProps }, label);
};
EOF

  # --- js/components/LoginButton.js — business component built from base/ -----
  cat > "$PROJECT_NAME/js/components/LoginButton.js" <<EOF
// Business component: knows about auth/loading state, built from the
// base/Button.js primitive rather than a native <button> directly.
// This is the base -> component pattern in practice — see
// js/base/Button.js and references/components.md#base-vs-components.

${VAN_IMPORT}
import { Button } from "../base/Button.js";

export const LoginButton = (onLogin) => {
  const isLoading = van.state(false);

  const handleClick = async () => {
    isLoading.val = true;
    try {
      await onLogin();
    } finally {
      isLoading.val = false;
    }
  };

  return Button(
    () => (isLoading.val ? "Logging in..." : "Log in"),
    handleClick,
    { disabled: () => isLoading.val }
  );
};
EOF

  # --- js/components/ProductCard.js --------------------------------------------
  cat > "$PROJECT_NAME/js/components/ProductCard.js" <<EOF
${VAN_IMPORT}
import { Button } from "../base/Button.js";

const { div, h3, span } = van.tags;

export const ProductCard = (product, onAdd) => {
  return div({ class: "product-card" },
    h3(product.name),
    span(\`\$\${product.price.toFixed(2)}\`),
    Button("Add to Cart", () => onAdd(product))
  );
};
EOF

  # --- js/components/HomePage.js -----------------------------------------------
  cat > "$PROJECT_NAME/js/components/HomePage.js" <<EOF
${VAN_IMPORT}
import { Button } from "../base/Button.js";
import { LoginButton } from "./LoginButton.js";
import { navigateTo } from "../utils.js";

const { div, h1, p } = van.tags;

export const HomePage = () => {
  return div({ class: "page home-page" },
    h1("Welcome to your NoF app"),
    p("This is demo content (--demo) — see js/components/ProductsPage.js and js/store.js for the cart example."),
    Button("Go to Products", () => navigateTo('/products')),
    LoginButton(async () => {
      // app-specific auth call goes here
    })
  );
};
EOF

  # --- js/components/ProductsPage.js -------------------------------------------
  cat > "$PROJECT_NAME/js/components/ProductsPage.js" <<EOF
${VAN_IMPORT}
import { ProductCard } from "./ProductCard.js";
import { addToCart, cartTotal } from "../store.js";

const { div, h1, p } = van.tags;

const demoProducts = [
  { id: 1, name: "Widget", price: 9.99 },
  { id: 2, name: "Gadget", price: 19.99 },
  { id: 3, name: "Gizmo", price: 14.5 },
];

export const ProductsPage = () => {
  return div({ class: "page products-page" },
    h1("Products"),
    p("Cart total: $", () => cartTotal.val.toFixed(2)),
    div({ class: "product-grid" },
      demoProducts.map(p => ProductCard(p, addToCart))
    )
  );
};
EOF

  # --- js/router.js — two routes ------------------------------------------------
  cat > "$PROJECT_NAME/js/router.js" <<EOF
${NAVIGO_IMPORT}
import { renderToApp } from './utils.js';
import { HomePage } from './components/HomePage.js';
import { ProductsPage } from './components/ProductsPage.js';

const router = new Navigo('/');

router.on('/', () => renderToApp(HomePage));
router.on('/products', () => renderToApp(ProductsPage));

router.resolve();
window.router = router;

export default router;
EOF

fi

# --- Vite-only files: package.json, vite.config.js, .gitignore -------------
if [ "$BUNDLER" = "vite" ]; then

  cat > "$PROJECT_NAME/package.json" <<EOF
{
  "name": "$(basename "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9._-]/-/g')",
  "private": true,
  "type": "module",
  "version": "0.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vanjs-core": "^${VANJS_VERSION}",
    "navigo": "^${NAVIGO_VERSION}"
  },
  "devDependencies": {
    "vite": "^${VITE_VERSION}"
  }
}
EOF

  # Vite's dev server and 'vite preview' both handle SPA fallback routing
  # (serving index.html for unknown paths) out of the box, so Navigo's
  # clean-URL mode works with zero extra config here — unlike the
  # no-bundler path, which needs live-server's --entry-file flag (see
  # references/tooling.md and the README generated below).
  cat > "$PROJECT_NAME/vite.config.js" <<'EOF'
import { defineConfig } from 'vite';

export default defineConfig({
  // Vite's dev server and preview both fall back to index.html for
  // unknown paths automatically, which is what Navigo's clean History
  // API routing (new Navigo('/')) needs — no extra config required.
});
EOF

  cat > "$PROJECT_NAME/.gitignore" <<'EOF'
node_modules/
dist/
EOF

fi

# --- README ---------------------------------------------------------------
if [ "$BUNDLER" = "vite" ]; then
  RUN_LOCALLY_SECTION="This project uses Vite and npm packages (vanjs-core, navigo) instead of
CDN imports — that's what \`--bundler vite\` changes versus the default
NoF setup. Install dependencies, then run the dev server:

\`\`\`bash
npm install
npm run dev
\`\`\`

Vite's dev server handles SPA fallback routing (serving \`index.html\` for
unknown paths) automatically, so Navigo's clean URLs (\`/products\`, etc.)
work with zero extra config — unlike the no-bundler/live-server setup,
which needs an explicit flag for the same behavior.

For a production build: \`npm run build\` (outputs to \`dist/\`), then
\`npm run preview\` to check it locally before deploying. See
\`references/deployment.md\` in the \`no-framework\` skill for the
production URL-fallback config your actual host still needs — Vite's
dev-server fallback doesn't automatically carry over to how a static
host serves the built \`dist/\` output."
  STRUCTURE_EXTRA="- \`package.json\` / \`vite.config.js\` — Vite project config and npm dependencies (vanjs-core, navigo)
- \`.gitignore\` — excludes \`node_modules/\` and \`dist/\`"
  ARCH_GUIDE_SUFFIX=", the CDN-to-npm import swap this scaffold already applied"
  TAGLINE_SUFFIX=" + Vite"
else
  RUN_LOCALLY_SECTION="Any static file server works, since there's no required build step. Use
\`--entry-file=index.html\` so refreshing or directly opening a route
other than \`/\` (e.g. \`/products\`) doesn't 404 — Navigo's clean URLs
need the server to fall back to \`index.html\` for unknown paths:

\`\`\`bash
npx live-server . --entry-file=index.html
\`\`\`

(Don't use live-server's \`--spa\` flag here — it rewrites paths to
hash-based URLs, which conflicts with Navigo's default clean-URL mode.)"
  STRUCTURE_EXTRA=""
  ARCH_GUIDE_SUFFIX=""
  TAGLINE_SUFFIX=""
fi

if [ "$DEMO" = true ]; then
  DEMO_NOTE="

This project was generated with **--demo**: it includes a worked cart/products
example (js/store.js, ProductCard, ProductsPage) and a base -> component
pairing (js/base/Button.js -> js/components/LoginButton.js) to illustrate
the patterns. Delete or replace the demo content once you've seen how it
fits together."
else
  DEMO_NOTE=""
fi

cat > "$PROJECT_NAME/README.md" <<EOF
# $PROJECT_NAME

Scaffolded with NoF (No Frameworks) — VanJS + Navigo${TAGLINE_SUFFIX}.
${DEMO_NOTE}

## Run locally

${RUN_LOCALLY_SECTION}

## Structure

- \`js/store.js\` — global state
- \`js/router.js\` — Navigo route table
- \`js/utils.js\` — rendering helpers (renderToApp, navigateTo)
- \`js/base/\` — dumb, app-agnostic UI primitives (e.g. Button) with no
  business meaning; built into components rather than used raw in pages
- \`js/components/\` — business components, generally built out of
  \`js/base/\` primitives
- \`pages/\` — for file-based static HTML pages, if used instead of/alongside component routing
- \`css/style.css\` — plain CSS
${STRUCTURE_EXTRA}

See the \`no-framework\` skill's \`references/\` for the full architecture
guide (state management, routing, reactivity, component patterns${ARCH_GUIDE_SUFFIX}).
EOF

echo "Done. Next steps:"
echo "  cd $PROJECT_NAME"
if [ "$BUNDLER" = "vite" ]; then
  echo "  npm install"
  echo "  npm run dev"
else
  echo "  npx live-server . --entry-file=index.html"
fi
