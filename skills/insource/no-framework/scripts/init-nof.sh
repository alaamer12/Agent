#!/usr/bin/env bash
# scripts/init-nof.sh
#
# Scaffolds a new NoF (No Frameworks) project: a UI library + Navigo for
# routing, standard directory layout, index.html, store.js, utils.js,
# router.js, js/base/ (app-agnostic primitives) and js/components/
# (business components built from base/).
#
# --ui vanjs|preact|nanojsx: which UI/reactivity library to scaffold.
# Default: preact. All three are libraries, not frameworks, under NoF's
# definition — none of them mandate a build step, a routing convention,
# or a data-fetching convention; Navigo and the store.js pattern stay
# identical underneath whichever one is picked. See
# references/ui_libraries.md for the full comparison and why Preact
# (small, JSX, hooks, large ecosystem, and — paired with
# @preact/signals — fine-grained updates much like VanJS's own) is the
# default, with VanJS (truly zero-VDOM, smallest) and Nano JSX (real-DOM,
# explicit `this.update()`, pairs with Nano Stores for shared state) as
# the alternatives.
#
# --state native|nanostores: only meaningful with --ui preact. Default
# native uses @preact/signals (signal()/computed()) for js/store.js —
# Preact's own idiomatic, deeply-integrated reactive primitive. Pass
# --state nanostores to use Nano Stores (atom()/computed()) instead —
# useful when the same store needs to be shared with a non-Preact part
# of the app (another NoF "island" on the same page, a Nano JSX widget,
# etc.), since Nano Stores is UI-library-agnostic. VanJS always uses its
# own van.state()/van.derive() (already fine-grained, no reason to swap
# it); Nano JSX always uses Nano Stores for js/store.js, since Nano JSX
# has no reactive store primitive of its own (local, component-owned
# state still uses Nano JSX's own class-field + this.update() either
# way) — passing --state with --ui vanjs or --ui nanojsx is an error
# explaining this rather than silently ignored.
#
# --demo: a fuller worked example (a shared counter store with an
# action and a derived value, a base/Button.js primitive, a
# LoginButton-style business component built from it, a second route,
# card-style composition) — useful for learning the patterns or as a
# reference, not meant to be the base you build a real project on top
# of.
#
# --bundler vite: adds Vite instead of the default no-build-step CDN
# setup. Switches every library import from a CDN URL to a bare
# specifier, generates package.json, vite.config.js, and a .gitignore
# for node_modules/dist, and adjusts index.html and the README's run
# instructions accordingly. For --ui preact/nanojsx this also switches
# component files from --bundler-none's tagged-template (htm) syntax to
# real JSX (.jsx files) — see references/tooling.md and
# references/ui_libraries.md for why both are genuine no-framework
# options and what changes between them.
#
# --styler tailwind|sass: adds CSS tooling beyond plain CSS. Plain CSS
# (no flag) remains the default. StyleX is NOT a supported value here —
# see references/tooling.md#not-every-css-adjacent-tool-is-vanilla-compatible
# for why (it's tied to React's component model, not vanilla-compatible).
#
# --css-tooling cli|vite-plugin: only meaningful together with --styler.
# Tailwind and Sass both need *some* build step even in NoF (neither can
# just be a CDN <script> tag) — this picks which one:
#   - cli:         standalone watcher process (@tailwindcss/cli or the
#                  `sass` CLI), independent of any JS bundler. The only
#                  valid choice with --bundler none (the default), and
#                  chosen automatically then.
#   - vite-plugin: requires --bundler vite. Tailwind uses the
#                  @tailwindcss/vite plugin; Sass needs no plugin at all
#                  since Vite has Sass support built in once the `sass`
#                  package is installed — either way this folds CSS
#                  compilation into Vite's own dev server/build, no
#                  second watch process. Chosen automatically when
#                  --bundler vite and --css-tooling isn't given.
# Explicitly pass --css-tooling cli with --bundler vite if you want
# Tailwind/Sass compiled independently of Vite anyway (e.g. Vite is only
# there for the JS side and you want CSS decoupled from it).
#
# Usage:
#   bash init-nof.sh <project-name>                                    # Preact, CDN + htm (default)
#   bash init-nof.sh <project-name> --ui vanjs                          # VanJS instead of Preact
#   bash init-nof.sh <project-name> --ui nanojsx                        # Nano JSX instead of Preact
#   bash init-nof.sh <project-name> --ui preact --state nanostores       # Preact + Nano Stores instead of Signals
#   bash init-nof.sh <project-name> --demo                              # fuller worked example
#   bash init-nof.sh <project-name> --bundler vite                       # Vite + npm packages + real JSX
#   bash init-nof.sh <project-name> --styler tailwind                    # + Tailwind (standalone CLI)
#   bash init-nof.sh <project-name> --styler sass                        # + Sass (standalone CLI)
#   bash init-nof.sh <project-name> --bundler vite --styler tailwind      # Tailwind via @tailwindcss/vite
#   bash init-nof.sh <project-name> --ui nanojsx --demo --bundler vite --styler sass  # combine freely

set -euo pipefail

PROJECT_NAME=""
DEMO=false
BUNDLER=""
STYLER=""
CSS_TOOLING=""
UI=""
STATE=""

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
    --styler)
      i=$((i + 1))
      if [ $i -ge ${#args[@]} ]; then
        echo "Error: --styler requires a value (tailwind or sass)" >&2
        exit 1
      fi
      STYLER="${args[$i]}"
      if [ "$STYLER" != "tailwind" ] && [ "$STYLER" != "sass" ]; then
        echo "Error: unsupported --styler value '$STYLER' (supported: tailwind, sass — StyleX is intentionally not supported here, see references/tooling.md)" >&2
        exit 1
      fi
      ;;
    --css-tooling)
      i=$((i + 1))
      if [ $i -ge ${#args[@]} ]; then
        echo "Error: --css-tooling requires a value (cli or vite-plugin)" >&2
        exit 1
      fi
      CSS_TOOLING="${args[$i]}"
      if [ "$CSS_TOOLING" != "cli" ] && [ "$CSS_TOOLING" != "vite-plugin" ]; then
        echo "Error: unsupported --css-tooling value '$CSS_TOOLING' (supported: cli, vite-plugin)" >&2
        exit 1
      fi
      ;;
    --ui)
      i=$((i + 1))
      if [ $i -ge ${#args[@]} ]; then
        echo "Error: --ui requires a value (vanjs, preact, or nanojsx)" >&2
        exit 1
      fi
      UI="${args[$i]}"
      if [ "$UI" != "vanjs" ] && [ "$UI" != "preact" ] && [ "$UI" != "nanojsx" ]; then
        echo "Error: unsupported --ui value '$UI' (supported: vanjs, preact, nanojsx)" >&2
        exit 1
      fi
      ;;
    --state)
      i=$((i + 1))
      if [ $i -ge ${#args[@]} ]; then
        echo "Error: --state requires a value (native or nanostores)" >&2
        exit 1
      fi
      STATE="${args[$i]}"
      if [ "$STATE" != "native" ] && [ "$STATE" != "nanostores" ]; then
        echo "Error: unsupported --state value '$STATE' (supported: native, nanostores)" >&2
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
UI="${UI:-preact}"

# --- Resolve --state against --ui -------------------------------------------
# Only Preact has a real choice here (its own signal()/computed() vs.
# Nano Stores' atom()/computed()). VanJS's own van.state()/van.derive()
# is already fine-grained and UI-library-agnostic state doesn't buy
# anything there; Nano JSX has no store primitive of its own at all, so
# js/store.js always uses Nano Stores for it regardless of this flag —
# see references/ui_libraries.md for why in both cases.
if [ -n "$STATE" ] && [ "$UI" != "preact" ]; then
  echo "Error: --state only applies to --ui preact (--ui vanjs always uses van.state()/van.derive(); --ui nanojsx always uses Nano Stores for js/store.js since Nano JSX has no reactive store of its own — see references/ui_libraries.md)" >&2
  exit 1
fi
STATE="${STATE:-native}"

# --- Resolve --css-tooling against --styler/--bundler -----------------------
# vite-plugin only exists when Vite is actually present; cli is the only
# option without a JS bundler, and the automatic default whenever
# --css-tooling wasn't explicitly given.
if [ -n "$CSS_TOOLING" ] && [ -z "$STYLER" ]; then
  echo "Error: --css-tooling requires --styler to also be set" >&2
  exit 1
fi
if [ "$CSS_TOOLING" = "vite-plugin" ] && [ "$BUNDLER" != "vite" ]; then
  echo "Error: --css-tooling vite-plugin requires --bundler vite" >&2
  exit 1
fi
if [ -n "$STYLER" ] && [ -z "$CSS_TOOLING" ]; then
  if [ "$BUNDLER" = "vite" ]; then
    CSS_TOOLING="vite-plugin"
  else
    CSS_TOOLING="cli"
  fi
fi

# NOTE: the versions pinned below were verified together (real
# `npm install` + `vite build` + running the built bundle, for every
# --ui) as of this skill's last update (see the `updated` field in
# SKILL.md's frontmatter). Per SKILL.md step 0, verify the actual
# current versions before running this in a real project and update
# these variables if newer ones are available and compatible. Worth
# flagging explicitly here rather than just in references/tooling.md:
#   - Preact 11 reached stable on 2026-09-30 (npm `latest`).
#     @preact/signals (peer: preact >= 10.25 || >= 11.0.0-0) and
#     @preact/preset-vite work with it.
#   - @preact/signals ships frequent minor releases — more likely than
#     most pins here to be behind current by the time this runs.
#   - The no-bundler CDN URLs (jsdelivr `+esm`) could NOT be fetched
#     from the environment this skill was verified in, so that mode was
#     tested with the same code resolved from npm instead. Open a
#     no-bundler scaffold in a browser once and check the console.
VANJS_VERSION="1.6.0"
NAVIGO_VERSION="8.11.1"
VITE_VERSION="8.3.3"
TAILWIND_CLI_VERSION="4.1.0"
TAILWIND_VITE_VERSION="4.1.0"
SASS_VERSION="1.104.0"
PREACT_VERSION="11.0.0"
PREACT_PRESET_VITE_VERSION="2.10.6"
PREACT_SIGNALS_VERSION="2.11.3"
NANO_JSX_VERSION="0.2.1"
NANOSTORES_VERSION="1.5.5"
NANOSTORES_PREACT_VERSION="1.1.1"
HTM_VERSION="3.0.4"

if [ -e "$PROJECT_NAME" ]; then
  echo "Error: '$PROJECT_NAME' already exists. Choose a different name or remove it first." >&2
  exit 1
fi

if [ "$DEMO" = true ]; then
  echo "Scaffolding NoF project (with demo example): $PROJECT_NAME"
else
  echo "Scaffolding NoF project (clean Hello World): $PROJECT_NAME"
fi
echo "  UI library: $UI"
if [ "$UI" = "preact" ]; then
  echo "  state: $STATE ($([ "$STATE" = "native" ] && echo "@preact/signals" || echo "nanostores"))"
elif [ "$UI" = "nanojsx" ]; then
  echo "  state: nanostores (js/store.js only — local state stays Nano JSX's own class-field + this.update())"
fi
if [ "$BUNDLER" = "vite" ]; then
  echo "  with Vite (npm packages + real JSX instead of CDN imports)"
fi
if [ "$STYLER" = "tailwind" ]; then
  echo "  with Tailwind CSS (via $CSS_TOOLING)"
elif [ "$STYLER" = "sass" ]; then
  echo "  with Sass (via $CSS_TOOLING)"
fi

mkdir -p "$PROJECT_NAME/js/base" "$PROJECT_NAME/js/components" "$PROJECT_NAME/pages" "$PROJECT_NAME/css"

# --- COMPONENT_EXT: .jsx for real JSX (preact/nanojsx + vite), .js otherwise
# VanJS never uses JSX. Preact/Nano JSX use tagged templates (htm) in
# plain .js files without a bundler, and real JSX in .jsx files with
# Vite (@preact/preset-vite, or esbuild's jsxFactory for Nano JSX).
COMPONENT_EXT="js"
if { [ "$UI" = "preact" ] || [ "$UI" = "nanojsx" ]; } && [ "$BUNDLER" = "vite" ]; then
  COMPONENT_EXT="jsx"
fi

# --- CDN URLs (bundler=none) --------------------------------------------
PREACT_CDN="https://cdn.jsdelivr.net/npm/preact@${PREACT_VERSION}/+esm"
PREACT_HOOKS_CDN="https://cdn.jsdelivr.net/npm/preact@${PREACT_VERSION}/hooks/+esm"
PREACT_SIGNALS_CDN="https://cdn.jsdelivr.net/npm/@preact/signals@${PREACT_SIGNALS_VERSION}/+esm"
HTM_CDN="https://cdn.jsdelivr.net/npm/htm@${HTM_VERSION}/+esm"
NANO_JSX_CDN="https://cdn.jsdelivr.net/npm/nano-jsx@${NANO_JSX_VERSION}/+esm"
NANOSTORES_CDN="https://cdn.jsdelivr.net/npm/nanostores@${NANOSTORES_VERSION}/+esm"
NANOSTORES_PREACT_CDN="https://cdn.jsdelivr.net/npm/@nanostores/preact@${NANOSTORES_PREACT_VERSION}/+esm"

# --- Import lines: CDN URL by default, bare specifier under --bundler vite --
# Every generated file that imports a library uses these variables
# instead of hardcoding either form, so the CDN-vs-npm-package choice
# only has to be made once here.
if [ "$BUNDLER" = "vite" ]; then
  VAN_IMPORT="import van from \"vanjs-core\";"
  NAVIGO_IMPORT="import Navigo from \"navigo\";"
  PREACT_RENDER_IMPORT="import { render } from \"preact\";"
  PREACT_H_RENDER_IMPORT="import { h, render } from \"preact\";"
  PREACT_HOOKS_IMPORT="import { useState } from \"preact/hooks\";"
  PREACT_SIGNALS_IMPORT="import { signal, computed } from \"@preact/signals\";"
  NANO_JSX_IMPORT="import { h, render, Component } from \"nano-jsx\";"
  NANOSTORES_IMPORT="import { atom, computed as storeComputed } from \"nanostores\";"
  NANOSTORES_PREACT_IMPORT="import { useStore } from \"@nanostores/preact\";"
else
  VAN_IMPORT="import van from \"https://cdn.jsdelivr.net/npm/vanjs-core@${VANJS_VERSION}/src/van.min.js\";"
  NAVIGO_IMPORT="import Navigo from \"https://cdn.jsdelivr.net/npm/navigo@${NAVIGO_VERSION}/+esm\";"
  PREACT_RENDER_IMPORT="import { render } from \"${PREACT_CDN}\";"
  PREACT_H_RENDER_IMPORT="import { h, render } from \"${PREACT_CDN}\";"
  PREACT_HOOKS_IMPORT="import { useState } from \"${PREACT_HOOKS_CDN}\";"
  PREACT_SIGNALS_IMPORT="import { signal, computed } from \"${PREACT_SIGNALS_CDN}\";"
  NANO_JSX_IMPORT="import { h, render, Component } from \"${NANO_JSX_CDN}\";"
  NANOSTORES_IMPORT="import { atom, computed as storeComputed } from \"${NANOSTORES_CDN}\";"
  NANOSTORES_PREACT_IMPORT="import { useStore } from \"${NANOSTORES_PREACT_CDN}\";"
fi

# --- Resolve the stylesheet href --------------------------------------------
# Plain CSS and the CLI-built paths both link the compiled css/style.css.
# Under vite-plugin tooling, Vite transforms the source file itself on
# request (Tailwind via @tailwindcss/vite, Sass via its built-in support),
# so index.html links the source directly and there's no separate build
# artifact to generate or gitignore.
CSS_HREF="css/style.css"
if [ "$STYLER" = "tailwind" ] && [ "$CSS_TOOLING" = "vite-plugin" ]; then
  CSS_HREF="css/input.css"
elif [ "$STYLER" = "sass" ] && [ "$CSS_TOOLING" = "vite-plugin" ]; then
  CSS_HREF="css/style.scss"
fi

# --- Resolve the app entry script (differs per UI/bundler) -----------------
# VanJS always boots from js/router.js directly. Preact/Nano JSX under
# Vite boot from a .jsx entry too (router.js can stay plain .js — it
# contains no JSX itself, only imports/calls — so this only matters for
# the <script> tag, which is the same path either way).
ENTRY_SCRIPT="js/router.js"

# --- index.html (same across all combinations) ------------------------------
cat > "$PROJECT_NAME/index.html" <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NoF App</title>
  <link rel="stylesheet" href="${CSS_HREF}">
</head>
<body>
  <div id="app"></div>
  <script type="module" src="${ENTRY_SCRIPT}"></script>
</body>
</html>
EOF

# --- js/html.js — only for preact/nanojsx without a bundler ------------------
# A tiny shared module binding htm's tagged-template syntax to the UI
# library's h() once, so every other file imports `html` + `render`
# from here instead of repeating `htm.bind(h)` everywhere. Not needed
# under --bundler vite (real JSX there) or --ui vanjs (van.tags() is
# already its own template-free syntax).
if { [ "$UI" = "preact" ] || [ "$UI" = "nanojsx" ]; } && [ "$BUNDLER" != "vite" ]; then
  {
    if [ "$UI" = "preact" ]; then
      echo "$PREACT_H_RENDER_IMPORT"
    else
      echo "$NANO_JSX_IMPORT"
    fi
    echo "import htm from \"${HTM_CDN}\";"
    echo
    cat <<'INNER'
// Binds htm's tagged-template syntax to h() once, so component files
// write `html`...`` instead of JSX and don't each need their own
// `htm.bind(h)`. See references/ui_libraries.md for why htm is the
// no-bundler alternative to JSX rather than JSX itself requiring a
// compiler that would contradict NoF's no-build-step default.
export const html = htm.bind(h);
export { h, render };
INNER
  } > "$PROJECT_NAME/js/html.js"
fi

# --- js/utils.js — rendering helpers, branches on --ui -----------------------
# Always render through these, never call the UI library's render/add
# directly from inside a page or component — see
# references/rendering.md.
if [ "$UI" = "vanjs" ]; then
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
elif [ "$UI" = "preact" ]; then
  cat > "$PROJECT_NAME/js/utils.js" <<EOF
// Rendering helpers. Always render through these, not Preact's render()
// directly. The page is rendered via h(component, props) — NOT by
// calling component() yourself — so Preact owns the render and hooks
// (useState, useStore, useSignal...) work at the top level of a page.
// Calling a hook-using component directly crashes: hooks need Preact's
// render context.

${PREACT_H_RENDER_IMPORT}

export const renderToApp = (component) => {
  const app = document.getElementById('app');
  if (!app) {
    console.error("[NoF] #app element not found");
    return;
  }
  app.innerHTML = '';
  render(h(component), app);
};

export const renderToAppWithProps = (component, props = {}) => {
  const app = document.getElementById('app');
  if (!app) return;
  app.innerHTML = '';
  render(h(component, props), app);
};

export const navigateTo = (path) => {
  window.router.navigate(path);
};
EOF
else
  cat > "$PROJECT_NAME/js/utils.js" <<EOF
// Rendering helpers. Always render through these, not Nano JSX's
// render() directly. The page is rendered via h(component, props), not
// by calling component() yourself — that works for plain function
// components and class components alike (a class page needs h() to be
// constructed at all). See references/ui_libraries.md.

${NANO_JSX_IMPORT}

export const renderToApp = (component) => {
  const app = document.getElementById('app');
  if (!app) {
    console.error("[NoF] #app element not found");
    return;
  }
  app.innerHTML = '';
  render(h(component), app);
};

export const renderToAppWithProps = (component, props = {}) => {
  const app = document.getElementById('app');
  if (!app) return;
  app.innerHTML = '';
  render(h(component, props), app);
};

export const navigateTo = (path) => {
  window.router.navigate(path);
};
EOF
fi

# --- css/ (branches on --styler; plain CSS is the default) ------------------
if [ "$STYLER" = "tailwind" ]; then

  # css/input.css is the source Tailwind compiles from either way (CLI or
  # the Vite plugin). The generated js/base/ and js/components/ files use
  # plain class names (.btn, .page, .product-card) regardless of --styler
  # or --ui, so this @layer block gives Tailwind's utilities to those
  # existing classes via @apply rather than requiring a separate rewrite
  # of the components. Reach for utility classes directly in markup as
  # the project grows — this block is a starting point, not a pattern to
  # keep extending indefinitely.
  cat > "$PROJECT_NAME/css/input.css" <<'EOF'
@import "tailwindcss";

@layer components {
  .btn {
    @apply cursor-pointer rounded-md bg-neutral-900 px-4 py-2 text-white;
  }
  .btn:hover {
    @apply opacity-85;
  }
  .page {
    @apply mx-auto max-w-3xl px-6 py-8;
  }
  .product-card {
    @apply rounded-lg border border-neutral-200 p-4;
  }
}
EOF

elif [ "$STYLER" = "sass" ]; then

  cat > "$PROJECT_NAME/css/style.scss" <<'EOF'
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

  &:hover {
    opacity: 0.85;
  }
}

.product-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
}
EOF

else

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

fi

if [ "$DEMO" = false ]; then

  # ==========================================================================
  # CLEAN HELLO WORLD (default)
  # ==========================================================================

  if [ "$UI" = "vanjs" ]; then

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
    # ------------------------------------------------------------------------
    # UI = preact or nanojsx. Button.{js,jsx}/HomePage.{js,jsx}/router.js are
    # identical content between the two (only js/html.js's internal h/render
    # binding, generated earlier, actually differs) — the two UI libraries
    # only diverge where local component state or the store is involved,
    # neither of which the clean default scaffold needs yet.
    # ------------------------------------------------------------------------

    # --- js/store.js — empty, ready for real state -----------------------------
    if [ "$UI" = "preact" ] && [ "$STATE" = "native" ]; then
      cat > "$PROJECT_NAME/js/store.js" <<EOF
// Global state. Centralize shared state and its actions here.
// Rule: signals compare by value — for arrays/objects, always assign a
// *new* reference, never mutate in place (the same rule VanJS uses for
// van.state()).
//
// Example:
//   export const count = signal(0);
//   export const increment = () => { count.value++; };
//   export const doubled = computed(() => count.value * 2);
//
// See references/ui_libraries.md#preact-signals for why signals (not
// Nano Stores) are the default here, and how to read a signal's value
// directly in JSX/htm.

${PREACT_SIGNALS_IMPORT}
EOF
    else
      STORE_UI_NOTE="Nano Stores"
      [ "$UI" = "preact" ] && STORE_UI_NOTE="Nano Stores (--state nanostores)"
      cat > "$PROJECT_NAME/js/store.js" <<EOF
// Global state via ${STORE_UI_NOTE}. Centralize shared state and its
// actions here.
//
// Example:
//   export const count = atom(0);
//   export const increment = () => count.set(count.get() + 1);
//   export const doubled = storeComputed(count, c => c * 2);
//
// See references/ui_libraries.md#nano-stores for how components read
// and subscribe to a Nano Stores atom/computed value.

${NANOSTORES_IMPORT}
EOF
    fi

    # --- js/base/Button.{js,jsx} — dumb, app-agnostic primitive ------------------
    if [ "$BUNDLER" = "vite" ]; then
      cat > "$PROJECT_NAME/js/base/Button.jsx" <<'INNER'
// Dumb, app-agnostic primitive: a thin wrapper around the native
// <button>, no business meaning. Business components import and build
// on this rather than writing JSX for a raw <button> directly. See the
// no-framework skill's references/components.md#base-vs-components.
// Preact/Nano JSX components here take a single props object (not
// positional args the way VanJS's base/Button.js does) — the idiomatic
// convention for both.

export const Button = ({ label, onClick, ...extraProps }) => (
  <button class="btn" onClick={onClick} {...extraProps}>{label}</button>
);
INNER
    else
      {
        echo "import { html } from \"../html.js\";"
        echo
        cat <<'INNER'
// Dumb, app-agnostic primitive: a thin wrapper around the native
// <button>, no business meaning. Business components import and build
// on this rather than writing html`<button>` directly. See the
// no-framework skill's references/components.md#base-vs-components.
// Takes a single props object (not positional args the way VanJS's
// base/Button.js does) — the idiomatic convention for Preact/Nano JSX.

export const Button = ({ label, onClick, ...extraProps }) => html`
  <button class="btn" onClick=${onClick} ...${extraProps}>${label}</button>
`;
INNER
      } > "$PROJECT_NAME/js/base/Button.js"
    fi

    # --- js/components/HomePage.{js,jsx} — minimal single component -------------
    if [ "$BUNDLER" = "vite" ]; then
      cat > "$PROJECT_NAME/js/components/HomePage.jsx" <<'INNER'
import { Button } from "../base/Button.jsx";

export const HomePage = () => (
  <div class="page home-page">
    <h1>Hello, NoF</h1>
    <p>Edit js/components/HomePage.jsx to get started.</p>
    <Button
      label="Get started"
      onClick={() => console.log("Edit js/base/Button.jsx and js/components/HomePage.jsx")}
    />
  </div>
);
INNER
    else
      {
        echo "import { html } from \"../html.js\";"
        echo "import { Button } from \"../base/Button.js\";"
        echo
        cat <<'INNER'
export const HomePage = () => html`
  <div class="page home-page">
    <h1>Hello, NoF</h1>
    <p>Edit js/components/HomePage.js to get started.</p>
    <${Button}
      label="Get started"
      onClick=${() => console.log("Edit js/base/Button.js and js/components/HomePage.js")}
    />
  </div>
`;
INNER
      } > "$PROJECT_NAME/js/components/HomePage.js"
    fi

    # --- js/router.js — one route (identical for preact and nanojsx) ------------
    cat > "$PROJECT_NAME/js/router.js" <<EOF
${NAVIGO_IMPORT}
import { renderToApp } from './utils.js';
import { HomePage } from './components/HomePage.${COMPONENT_EXT}';

const router = new Navigo('/');

router.on('/', () => renderToApp(HomePage));

router.resolve();
window.router = router;

export default router;
EOF

  fi

else

  # ==========================================================================
  # --demo: fuller worked example (cart store, Button, two routes)
  # ==========================================================================

  if [ "$UI" = "vanjs" ]; then

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

  if [ "$UI" = "preact" ]; then

    # --- js/store.js — cart demo with action + derive ---------------------------
    if [ "$STATE" = "native" ]; then
      cat > "$PROJECT_NAME/js/store.js" <<EOF
// Global state via @preact/signals. Centralize shared state and its
// actions here. Rule: signals compare by value — for arrays/objects,
// always assign a *new* reference, never mutate in place.
// This is demo content (--demo) — replace with your app's real state.

${PREACT_SIGNALS_IMPORT}

export const cart = signal([]);

export const addToCart = (product) => {
  cart.value = [...cart.value, { ...product, cartId: Date.now() }];
};

export const removeFromCart = (cartId) => {
  cart.value = cart.value.filter(item => item.cartId !== cartId);
};

export const cartTotal = computed(() =>
  cart.value.reduce((sum, item) => sum + item.price, 0)
);
EOF
    else
      cat > "$PROJECT_NAME/js/store.js" <<EOF
// Global state via Nano Stores (--state nanostores). Centralize shared
// state and its actions here.
// This is demo content (--demo) — replace with your app's real state.

${NANOSTORES_IMPORT}

export const cart = atom([]);

export const addToCart = (product) => {
  cart.set([...cart.get(), { ...product, cartId: Date.now() }]);
};

export const removeFromCart = (cartId) => {
  cart.set(cart.get().filter(item => item.cartId !== cartId));
};

export const cartTotal = storeComputed(cart, (items) =>
  items.reduce((sum, item) => sum + item.price, 0)
);
EOF
    fi

    # --- js/base/Button.{js,jsx} -------------------------------------------------
    if [ "$BUNDLER" = "vite" ]; then
      cat > "$PROJECT_NAME/js/base/Button.jsx" <<'INNER'
// Dumb, app-agnostic primitive — see references/components.md#base-vs-components.
export const Button = ({ label, onClick, ...extraProps }) => (
  <button class="btn" onClick={onClick} {...extraProps}>{label}</button>
);
INNER
    else
      {
        echo "import { html } from \"../html.js\";"
        echo
        cat <<'INNER'
// Dumb, app-agnostic primitive — see references/components.md#base-vs-components.
export const Button = ({ label, onClick, ...extraProps }) => html`
  <button class="btn" onClick=${onClick} ...${extraProps}>${label}</button>
`;
INNER
      } > "$PROJECT_NAME/js/base/Button.js"
    fi

    # --- js/components/LoginButton.{js,jsx} — hooks-based local state -----------
    if [ "$BUNDLER" = "vite" ]; then
      cat > "$PROJECT_NAME/js/components/LoginButton.jsx" <<'INNER'
// Business component: local loading state via Preact's useState hook,
// built from base/Button.jsx rather than a raw <button>. Local,
// component-owned state like this stays a hook regardless of whether
// js/store.js (shared state) uses signals or Nano Stores — see
// references/ui_libraries.md#preact.
import { useState } from "preact/hooks";
import { Button } from "../base/Button.jsx";

export const LoginButton = ({ onLogin }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleClick = async () => {
    setIsLoading(true);
    try {
      await onLogin();
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button
      label={isLoading ? "Logging in..." : "Log in"}
      onClick={handleClick}
      disabled={isLoading}
    />
  );
};
INNER
    else
      {
        echo "import { html } from \"../html.js\";"
        echo "$PREACT_HOOKS_IMPORT"
        echo "import { Button } from \"../base/Button.js\";"
        echo
        cat <<'INNER'
// Business component: local loading state via Preact's useState hook,
// built from base/Button.js rather than a raw <button>. See
// references/ui_libraries.md#preact.
export const LoginButton = ({ onLogin }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleClick = async () => {
    setIsLoading(true);
    try {
      await onLogin();
    } finally {
      setIsLoading(false);
    }
  };

  return html`
    <${Button}
      label=${isLoading ? "Logging in..." : "Log in"}
      onClick=${handleClick}
      disabled=${isLoading}
    />
  `;
};
INNER
      } > "$PROJECT_NAME/js/components/LoginButton.js"
    fi

    # --- js/components/ProductCard.{js,jsx} --------------------------------------
    if [ "$BUNDLER" = "vite" ]; then
      cat > "$PROJECT_NAME/js/components/ProductCard.jsx" <<'INNER'
import { Button } from "../base/Button.jsx";

export const ProductCard = ({ product, onAdd }) => (
  <div class="product-card">
    <h3>{product.name}</h3>
    <span>{`$${product.price.toFixed(2)}`}</span>
    <Button label="Add to Cart" onClick={() => onAdd(product)} />
  </div>
);
INNER
    else
      {
        echo "import { html } from \"../html.js\";"
        echo "import { Button } from \"../base/Button.js\";"
        echo
        cat <<'INNER'
export const ProductCard = ({ product, onAdd }) => html`
  <div class="product-card">
    <h3>${product.name}</h3>
    <span>$${product.price.toFixed(2)}</span>
    <${Button} label="Add to Cart" onClick=${() => onAdd(product)} />
  </div>
`;
INNER
      } > "$PROJECT_NAME/js/components/ProductCard.js"
    fi

    # --- js/components/HomePage.{js,jsx} -----------------------------------------
    if [ "$BUNDLER" = "vite" ]; then
      cat > "$PROJECT_NAME/js/components/HomePage.jsx" <<'INNER'
import { LoginButton } from "./LoginButton.jsx";
import { navigateTo } from "../utils.js";

export const HomePage = () => (
  <div class="page home-page">
    <h1>Welcome to your NoF app</h1>
    <p>This is demo content (--demo) — see js/components/ProductsPage.jsx and js/store.js for the cart example.</p>
    <button class="btn" onClick={() => navigateTo('/products')}>Go to Products</button>
    <LoginButton onLogin={async () => { /* app-specific auth call goes here */ }} />
  </div>
);
INNER
    else
      {
        echo "import { html } from \"../html.js\";"
        echo "import { LoginButton } from \"./LoginButton.js\";"
        echo "import { navigateTo } from \"../utils.js\";"
        echo
        cat <<'INNER'
export const HomePage = () => html`
  <div class="page home-page">
    <h1>Welcome to your NoF app</h1>
    <p>This is demo content (--demo) — see js/components/ProductsPage.js and js/store.js for the cart example.</p>
    <button class="btn" onClick=${() => navigateTo('/products')}>Go to Products</button>
    <${LoginButton} onLogin=${async () => { /* app-specific auth call goes here */ }} />
  </div>
`;
INNER
      } > "$PROJECT_NAME/js/components/HomePage.js"
    fi

    # --- js/components/ProductsPage.{js,jsx} — reads shared cart state ----------
    if [ "$STATE" = "native" ]; then
      if [ "$BUNDLER" = "vite" ]; then
        cat > "$PROJECT_NAME/js/components/ProductsPage.jsx" <<'INNER'
// Signals can be read directly in JSX (cartTotal, not cartTotal.value)
// — Preact's deep signals integration binds the text node straight to
// the signal and skips a full component re-render. See
// references/ui_libraries.md#preact-signals.
import { ProductCard } from "./ProductCard.jsx";
import { addToCart, cartTotal } from "../store.js";

const demoProducts = [
  { id: 1, name: "Widget", price: 9.99 },
  { id: 2, name: "Gadget", price: 19.99 },
  { id: 3, name: "Gizmo", price: 14.5 },
];

export const ProductsPage = () => (
  <div class="page products-page">
    <h1>Products</h1>
    <p>Cart total: ${cartTotal}</p>
    <div class="product-grid">
      {demoProducts.map((p) => (
        <ProductCard key={p.id} product={p} onAdd={addToCart} />
      ))}
    </div>
  </div>
);
INNER
      else
        {
          echo "import { html } from \"../html.js\";"
          echo "import { ProductCard } from \"./ProductCard.js\";"
          echo "import { addToCart, cartTotal } from \"../store.js\";"
          echo
          cat <<'INNER'
const demoProducts = [
  { id: 1, name: "Widget", price: 9.99 },
  { id: 2, name: "Gadget", price: 19.99 },
  { id: 3, name: "Gizmo", price: 14.5 },
];

export const ProductsPage = () => html`
  <div class="page products-page">
    <h1>Products</h1>
    <p>Cart total: $${cartTotal}</p>
    <div class="product-grid">
      ${demoProducts.map((p) => html`<${ProductCard} key=${p.id} product=${p} onAdd=${addToCart} />`)}
    </div>
  </div>
`;
INNER
        } > "$PROJECT_NAME/js/components/ProductsPage.js"
      fi
    else
      # --state nanostores: components subscribe via @nanostores/preact's
      # useStore() hook rather than reading .value directly.
      if [ "$BUNDLER" = "vite" ]; then
        cat > "$PROJECT_NAME/js/components/ProductsPage.jsx" <<'INNER'
import { useStore } from "@nanostores/preact";
import { ProductCard } from "./ProductCard.jsx";
import { addToCart, cartTotal } from "../store.js";

const demoProducts = [
  { id: 1, name: "Widget", price: 9.99 },
  { id: 2, name: "Gadget", price: 19.99 },
  { id: 3, name: "Gizmo", price: 14.5 },
];

export const ProductsPage = () => {
  const total = useStore(cartTotal);
  return (
    <div class="page products-page">
      <h1>Products</h1>
      <p>Cart total: ${total.toFixed(2)}</p>
      <div class="product-grid">
        {demoProducts.map((p) => (
          <ProductCard key={p.id} product={p} onAdd={addToCart} />
        ))}
      </div>
    </div>
  );
};
INNER
      else
        {
          echo "import { html } from \"../html.js\";"
          echo "$NANOSTORES_PREACT_IMPORT"
          echo "import { ProductCard } from \"./ProductCard.js\";"
          echo "import { addToCart, cartTotal } from \"../store.js\";"
          echo
          cat <<'INNER'
const demoProducts = [
  { id: 1, name: "Widget", price: 9.99 },
  { id: 2, name: "Gadget", price: 19.99 },
  { id: 3, name: "Gizmo", price: 14.5 },
];

export const ProductsPage = () => {
  const total = useStore(cartTotal);
  return html`
    <div class="page products-page">
      <h1>Products</h1>
      <p>Cart total: $${total.toFixed(2)}</p>
      <div class="product-grid">
        ${demoProducts.map((p) => html`<${ProductCard} key=${p.id} product=${p} onAdd=${addToCart} />`)}
      </div>
    </div>
  `;
};
INNER
        } > "$PROJECT_NAME/js/components/ProductsPage.js"
      fi
    fi

    # --- js/router.js — two routes ------------------------------------------------
    cat > "$PROJECT_NAME/js/router.js" <<EOF
${NAVIGO_IMPORT}
import { renderToApp } from './utils.js';
import { HomePage } from './components/HomePage.${COMPONENT_EXT}';
import { ProductsPage } from './components/ProductsPage.${COMPONENT_EXT}';

const router = new Navigo('/');

router.on('/', () => renderToApp(HomePage));
router.on('/products', () => renderToApp(ProductsPage));

router.resolve();
window.router = router;

export default router;
EOF

  fi

  if [ "$UI" = "nanojsx" ]; then

    # --- js/store.js — cart demo via Nano Stores (always, no --state choice) ---
    cat > "$PROJECT_NAME/js/store.js" <<EOF
// Global state via Nano Stores — Nano JSX has no reactive store of its
// own, so js/store.js always uses Nano Stores here regardless of
// --state (see references/ui_libraries.md#nano-jsx).
// This is demo content (--demo) — replace with your app's real state.

${NANOSTORES_IMPORT}

export const cart = atom([]);

export const addToCart = (product) => {
  cart.set([...cart.get(), { ...product, cartId: Date.now() }]);
};

export const removeFromCart = (cartId) => {
  cart.set(cart.get().filter(item => item.cartId !== cartId));
};

export const cartTotal = storeComputed(cart, (items) =>
  items.reduce((sum, item) => sum + item.price, 0)
);
EOF

    # --- js/base/Button.{js,jsx} -------------------------------------------------
    if [ "$BUNDLER" = "vite" ]; then
      cat > "$PROJECT_NAME/js/base/Button.jsx" <<'INNER'
// Dumb, app-agnostic primitive — see references/components.md#base-vs-components.
export const Button = ({ label, onClick, ...extraProps }) => (
  <button class="btn" onClick={onClick} {...extraProps}>{label}</button>
);
INNER
    else
      {
        echo "import { html } from \"../html.js\";"
        echo
        cat <<'INNER'
// Dumb, app-agnostic primitive — see references/components.md#base-vs-components.
export const Button = ({ label, onClick, ...extraProps }) => html`
  <button class="btn" onClick=${onClick} ...${extraProps}>${label}</button>
`;
INNER
      } > "$PROJECT_NAME/js/base/Button.js"
    fi

    # --- js/components/LoginButton.{js,jsx} — class + this.update() -------------
    if [ "$BUNDLER" = "vite" ]; then
      cat > "$PROJECT_NAME/js/components/LoginButton.jsx" <<'INNER'
// Business component: Nano JSX doesn't track plain fields reactively —
// local loading state lives on `this` and every change is followed by
// an explicit this.update() to re-render. Built from base/Button.jsx
// rather than a raw <button>. Note `|| undefined` on disabled: Nano JSX
// renders disabled={false} as the literal attribute disabled="false",
// which browsers treat as disabled — undefined omits it. See
// references/ui_libraries.md#nano-jsx.
import { Component } from "nano-jsx";
import { Button } from "../base/Button.jsx";

export class LoginButton extends Component {
  isLoading = false;

  handleClick = async () => {
    this.isLoading = true;
    this.update();
    try {
      await this.props.onLogin();
    } finally {
      this.isLoading = false;
      this.update();
    }
  };

  render() {
    return (
      <Button
        label={this.isLoading ? "Logging in..." : "Log in"}
        onClick={this.handleClick}
        disabled={this.isLoading || undefined}
      />
    );
  }
}
INNER
    else
      {
        echo "import { html } from \"../html.js\";"
        echo "import { Component } from \"${NANO_JSX_CDN}\";"
        echo "import { Button } from \"../base/Button.js\";"
        echo
        cat <<'INNER'
// Business component: Nano JSX doesn't track plain fields reactively —
// local loading state lives on `this` and every change is followed by
// an explicit this.update() to re-render. Note `|| undefined` on
// disabled: Nano JSX renders disabled={false} as the literal attribute
// disabled="false", which browsers treat as disabled — undefined omits
// it. See references/ui_libraries.md#nano-jsx.
export class LoginButton extends Component {
  isLoading = false;

  handleClick = async () => {
    this.isLoading = true;
    this.update();
    try {
      await this.props.onLogin();
    } finally {
      this.isLoading = false;
      this.update();
    }
  };

  render() {
    return html`
      <${Button}
        label=${this.isLoading ? "Logging in..." : "Log in"}
        onClick=${this.handleClick}
        disabled=${this.isLoading || undefined}
      />
    `;
  }
}
INNER
      } > "$PROJECT_NAME/js/components/LoginButton.js"
    fi

    # --- js/components/ProductCard.{js,jsx} --------------------------------------
    if [ "$BUNDLER" = "vite" ]; then
      cat > "$PROJECT_NAME/js/components/ProductCard.jsx" <<'INNER'
import { Button } from "../base/Button.jsx";

export const ProductCard = ({ product, onAdd }) => (
  <div class="product-card">
    <h3>{product.name}</h3>
    <span>{`$${product.price.toFixed(2)}`}</span>
    <Button label="Add to Cart" onClick={() => onAdd(product)} />
  </div>
);
INNER
    else
      {
        echo "import { html } from \"../html.js\";"
        echo "import { Button } from \"../base/Button.js\";"
        echo
        cat <<'INNER'
export const ProductCard = ({ product, onAdd }) => html`
  <div class="product-card">
    <h3>${product.name}</h3>
    <span>$${product.price.toFixed(2)}</span>
    <${Button} label="Add to Cart" onClick=${() => onAdd(product)} />
  </div>
`;
INNER
      } > "$PROJECT_NAME/js/components/ProductCard.js"
    fi

    # --- js/components/HomePage.{js,jsx} -----------------------------------------
    if [ "$BUNDLER" = "vite" ]; then
      cat > "$PROJECT_NAME/js/components/HomePage.jsx" <<'INNER'
import { LoginButton } from "./LoginButton.jsx";
import { navigateTo } from "../utils.js";

export const HomePage = () => (
  <div class="page home-page">
    <h1>Welcome to your NoF app</h1>
    <p>This is demo content (--demo) — see js/components/ProductsPage.jsx and js/store.js for the cart example.</p>
    <button class="btn" onClick={() => navigateTo('/products')}>Go to Products</button>
    <LoginButton onLogin={async () => { /* app-specific auth call goes here */ }} />
  </div>
);
INNER
    else
      {
        echo "import { html } from \"../html.js\";"
        echo "import { LoginButton } from \"./LoginButton.js\";"
        echo "import { navigateTo } from \"../utils.js\";"
        echo
        cat <<'INNER'
export const HomePage = () => html`
  <div class="page home-page">
    <h1>Welcome to your NoF app</h1>
    <p>This is demo content (--demo) — see js/components/ProductsPage.js and js/store.js for the cart example.</p>
    <button class="btn" onClick=${() => navigateTo('/products')}>Go to Products</button>
    <${LoginButton} onLogin=${async () => { /* app-specific auth call goes here */ }} />
  </div>
`;
INNER
      } > "$PROJECT_NAME/js/components/HomePage.js"
    fi

    # --- js/components/ProductsPage.{js,jsx} — class subscribes to the store ----
    # Nano JSX has no hooks, so reading a Nano Stores value reactively
    # means subscribing in didMount, calling this.update() on each
    # notification, and unsubscribing in didUnmount — see
    # references/ui_libraries.md#nano-jsx.
    if [ "$BUNDLER" = "vite" ]; then
      cat > "$PROJECT_NAME/js/components/ProductsPage.jsx" <<'INNER'
import { Component } from "nano-jsx";
import { ProductCard } from "./ProductCard.jsx";
import { addToCart, cartTotal } from "../store.js";

const demoProducts = [
  { id: 1, name: "Widget", price: 9.99 },
  { id: 2, name: "Gadget", price: 19.99 },
  { id: 3, name: "Gizmo", price: 14.5 },
];

export class ProductsPage extends Component {
  didMount() {
    this.unsubscribe = cartTotal.subscribe(() => this.update());
  }

  didUnmount() {
    this.unsubscribe?.();
  }

  render() {
    return (
      <div class="page products-page">
        <h1>Products</h1>
        <p>Cart total: ${cartTotal.get().toFixed(2)}</p>
        <div class="product-grid">
          {demoProducts.map((p) => (
            <ProductCard key={p.id} product={p} onAdd={addToCart} />
          ))}
        </div>
      </div>
    );
  }
}
INNER
    else
      {
        echo "import { html } from \"../html.js\";"
        echo "import { Component } from \"${NANO_JSX_CDN}\";"
        echo "import { ProductCard } from \"./ProductCard.js\";"
        echo "import { addToCart, cartTotal } from \"../store.js\";"
        echo
        cat <<'INNER'
const demoProducts = [
  { id: 1, name: "Widget", price: 9.99 },
  { id: 2, name: "Gadget", price: 19.99 },
  { id: 3, name: "Gizmo", price: 14.5 },
];

export class ProductsPage extends Component {
  didMount() {
    this.unsubscribe = cartTotal.subscribe(() => this.update());
  }

  didUnmount() {
    this.unsubscribe?.();
  }

  render() {
    return html`
      <div class="page products-page">
        <h1>Products</h1>
        <p>Cart total: $${cartTotal.get().toFixed(2)}</p>
        <div class="product-grid">
          ${demoProducts.map((p) => html`<${ProductCard} key=${p.id} product=${p} onAdd=${addToCart} />`)}
        </div>
      </div>
    `;
  }
}
INNER
      } > "$PROJECT_NAME/js/components/ProductsPage.js"
    fi

    # --- js/router.js — two routes ------------------------------------------------
    cat > "$PROJECT_NAME/js/router.js" <<EOF
${NAVIGO_IMPORT}
import { renderToApp } from './utils.js';
import { HomePage } from './components/HomePage.${COMPONENT_EXT}';
import { ProductsPage } from './components/ProductsPage.${COMPONENT_EXT}';

const router = new Navigo('/');

router.on('/', () => renderToApp(HomePage));
router.on('/products', () => renderToApp(ProductsPage));

router.resolve();
window.router = router;

export default router;
EOF

  fi

fi

# --- npm tooling: package.json, vite.config.js, .gitignore -----------------
# Needed whenever Vite is present (--bundler vite), a CSS tool ships via
# npm (--styler tailwind/sass), or the chosen --ui needs an npm package
# even without Vite (Preact/Nano JSX's CDN mode still needs nothing
# installed — htm + the UI library load straight from jsdelivr — so only
# Vite/--styler trigger this for them; this only differs from the base
# NoF/VanJS behavior in which packages get listed).
if [ "$BUNDLER" = "vite" ] || [ -n "$STYLER" ]; then

  DEPENDENCIES=()
  DEV_DEPENDENCIES=()
  SCRIPTS=()

  if [ "$BUNDLER" = "vite" ]; then
    SCRIPTS+=("\"dev\": \"vite\"" "\"build\": \"vite build\"" "\"preview\": \"vite preview\"")
    DEPENDENCIES+=("\"navigo\": \"^${NAVIGO_VERSION}\"")
    DEV_DEPENDENCIES+=("\"vite\": \"^${VITE_VERSION}\"")

    if [ "$UI" = "vanjs" ]; then
      DEPENDENCIES+=("\"vanjs-core\": \"^${VANJS_VERSION}\"")
    elif [ "$UI" = "preact" ]; then
      DEPENDENCIES+=("\"preact\": \"^${PREACT_VERSION}\"")
      DEV_DEPENDENCIES+=("\"@preact/preset-vite\": \"^${PREACT_PRESET_VITE_VERSION}\"")
      if [ "$STATE" = "native" ]; then
        DEPENDENCIES+=("\"@preact/signals\": \"^${PREACT_SIGNALS_VERSION}\"")
      else
        DEPENDENCIES+=("\"nanostores\": \"^${NANOSTORES_VERSION}\"" "\"@nanostores/preact\": \"^${NANOSTORES_PREACT_VERSION}\"")
      fi
    else
      DEPENDENCIES+=("\"nano-jsx\": \"^${NANO_JSX_VERSION}\"" "\"nanostores\": \"^${NANOSTORES_VERSION}\"")
    fi
  fi

  if [ "$STYLER" = "tailwind" ]; then
    if [ "$CSS_TOOLING" = "cli" ]; then
      DEV_DEPENDENCIES+=("\"@tailwindcss/cli\": \"^${TAILWIND_CLI_VERSION}\"")
      SCRIPTS+=("\"dev:css\": \"tailwindcss -i ./css/input.css -o ./css/style.css --watch\"" "\"build:css\": \"tailwindcss -i ./css/input.css -o ./css/style.css --minify\"")
    else
      DEV_DEPENDENCIES+=("\"@tailwindcss/vite\": \"^${TAILWIND_VITE_VERSION}\"")
    fi
  elif [ "$STYLER" = "sass" ]; then
    DEV_DEPENDENCIES+=("\"sass\": \"^${SASS_VERSION}\"")
    if [ "$CSS_TOOLING" = "cli" ]; then
      SCRIPTS+=("\"dev:css\": \"sass css/style.scss css/style.css --watch\"" "\"build:css\": \"sass css/style.scss css/style.css --style=compressed\"")
    fi
  fi

  DEPS_JSON=$(IFS=,; echo "${DEPENDENCIES[*]-}")
  DEV_DEPS_JSON=$(IFS=,; echo "${DEV_DEPENDENCIES[*]-}")
  SCRIPTS_JSON=$(IFS=,; echo "${SCRIPTS[*]-}")

  cat > "$PROJECT_NAME/package.json" <<EOF
{
  "name": "$(basename "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9._-]/-/g')",
  "private": true,
  "type": "module",
  "version": "0.0.0",
  "scripts": { ${SCRIPTS_JSON} },
  "dependencies": { ${DEPS_JSON} },
  "devDependencies": { ${DEV_DEPS_JSON} }
}
EOF

  if [ "$BUNDLER" = "vite" ]; then
    # Build the plugins array and any extra defineConfig options based on
    # --ui and the Tailwind-vite-plugin case, rather than assuming only
    # Tailwind ever needs a plugin here.
    VITE_PLUGIN_IMPORTS=""
    VITE_PLUGINS_LIST=""
    VITE_EXTRA_CONFIG=""

    if [ "$UI" = "preact" ]; then
      VITE_PLUGIN_IMPORTS="import preact from '@preact/preset-vite';
"
      VITE_PLUGINS_LIST="preact()"
    elif [ "$UI" = "nanojsx" ]; then
      # No preset plugin for Nano JSX — esbuild must be told to compile
      # JSX to h() calls (its default is React.createElement, which
      # crashes at runtime with "React is not defined"), and jsxInject
      # auto-adds the matching import to every file so component files
      # don't each need it by hand (mirroring what @preact/preset-vite
      # does for Preact automatically).
      VITE_EXTRA_CONFIG="  esbuild: {
    jsx: 'transform',
    jsxFactory: 'h',
    jsxFragment: 'Fragment',
    jsxInject: \`import { h, Fragment } from 'nano-jsx'\`,
  },
"
    fi

    if [ "$STYLER" = "tailwind" ] && [ "$CSS_TOOLING" = "vite-plugin" ]; then
      VITE_PLUGIN_IMPORTS="${VITE_PLUGIN_IMPORTS}import tailwindcss from '@tailwindcss/vite';
"
      if [ -n "$VITE_PLUGINS_LIST" ]; then
        VITE_PLUGINS_LIST="${VITE_PLUGINS_LIST}, tailwindcss()"
      else
        VITE_PLUGINS_LIST="tailwindcss()"
      fi
    fi

    VITE_PLUGINS_LINE=""
    if [ -n "$VITE_PLUGINS_LIST" ]; then
      VITE_PLUGINS_LINE="  plugins: [${VITE_PLUGINS_LIST}],
"
    fi

    {
      printf '%s' "$VITE_PLUGIN_IMPORTS"
      echo "import { defineConfig } from 'vite';"
      echo
      echo "export default defineConfig({"
      printf '%s' "$VITE_PLUGINS_LINE"
      printf '%s' "$VITE_EXTRA_CONFIG"
      cat <<'INNER'
  // Vite's dev server and preview both fall back to index.html for
  // unknown paths automatically, which is what Navigo's clean History
  // API routing (new Navigo('/')) needs — no extra config required.
});
INNER
    } > "$PROJECT_NAME/vite.config.js"
  fi

  GITIGNORE_CONTENT="node_modules/"
  if [ "$BUNDLER" = "vite" ]; then
    GITIGNORE_CONTENT="${GITIGNORE_CONTENT}
dist/"
  fi
  if [ -n "$STYLER" ] && [ "$CSS_TOOLING" = "cli" ]; then
    GITIGNORE_CONTENT="${GITIGNORE_CONTENT}
css/style.css"
  fi
  printf '%s\n' "$GITIGNORE_CONTENT" > "$PROJECT_NAME/.gitignore"

fi

# --- README ---------------------------------------------------------------
NPM_INSTALL_NEEDED=false
if [ "$BUNDLER" = "vite" ] || [ -n "$STYLER" ]; then
  NPM_INSTALL_NEEDED=true
fi

UI_LABEL="VanJS"
[ "$UI" = "preact" ] && UI_LABEL="Preact"
[ "$UI" = "nanojsx" ] && UI_LABEL="Nano JSX"

STATE_LABEL=""
if [ "$UI" = "preact" ]; then
  STATE_LABEL=" + @preact/signals"
  [ "$STATE" = "nanostores" ] && STATE_LABEL=" + Nano Stores"
elif [ "$UI" = "nanojsx" ]; then
  STATE_LABEL=" + Nano Stores"
fi

CSS_RUN_NOTE=""
if [ -n "$STYLER" ] && [ "$CSS_TOOLING" = "cli" ]; then
  CSS_TOOL_LABEL="Tailwind"
  [ "$STYLER" = "sass" ] && CSS_TOOL_LABEL="Sass"
  CSS_RUN_NOTE="

$CSS_TOOL_LABEL compiles as its own watch process, independent of
whatever's serving index.html — run it alongside the dev server in a
second terminal:

\`\`\`bash
npm run dev:css
\`\`\`

(\`npm run build:css\` for a one-off minified build before deploying.)"
fi

if [ "$BUNDLER" = "vite" ]; then
  RUN_LOCALLY_SECTION="This project uses Vite and real JSX ($( [ "$UI" = "vanjs" ] && echo "well, VanJS's own tag syntax — no JSX here" || echo "$UI_LABEL components" )) with npm packages instead of CDN imports —
that's what \`--bundler vite\` changes versus the default NoF setup.
Install dependencies, then run the dev server:

\`\`\`bash
npm install
npm run dev
\`\`\`

Vite's dev server handles SPA fallback routing (serving \`index.html\` for
unknown paths) automatically, so Navigo's clean URLs (\`/products\`, etc.)
work with zero extra config — unlike the no-bundler/live-server setup,
which needs an explicit flag for the same behavior.${CSS_RUN_NOTE}

For a production build: \`npm run build\` (outputs to \`dist/\`), then
\`npm run preview\` to check it locally before deploying. See
\`references/deployment.md\` in the \`no-framework\` skill for the
production URL-fallback config your actual host still needs — Vite's
dev-server fallback doesn't automatically carry over to how a static
host serves the built \`dist/\` output."
  ARCH_GUIDE_SUFFIX=", the CDN-to-npm import swap this scaffold already applied"
  TAGLINE_SUFFIX=" + Vite"
else
  NPM_PREFIX=""
  if [ "$NPM_INSTALL_NEEDED" = true ]; then
    NPM_PREFIX="\`npm install\` first (needed for the CSS compiler — see below),
then "
  fi
  JSX_NOTE=""
  if [ "$UI" = "preact" ] || [ "$UI" = "nanojsx" ]; then
    JSX_NOTE=" Components are written with htm tagged templates (\`html\\\`...\\\`\`), not JSX — see js/html.js and references/ui_libraries.md for why that's the no-bundler equivalent to real JSX rather than requiring a compiler."
  fi
  RUN_LOCALLY_SECTION="${NPM_PREFIX}any static file server works for the app itself, since JS stays a
no-build-step CDN setup.${JSX_NOTE} Use \`--entry-file=index.html\` so
refreshing or directly opening a route other than \`/\` (e.g.
\`/products\`) doesn't 404 — Navigo's clean URLs need the server to
fall back to \`index.html\` for unknown paths:

\`\`\`bash
npx live-server . --entry-file=index.html
\`\`\`

(Don't use live-server's \`--spa\` flag here — it rewrites paths to
hash-based URLs, which conflicts with Navigo's default clean-URL mode.)${CSS_RUN_NOTE}"
  ARCH_GUIDE_SUFFIX=""
  TAGLINE_SUFFIX=""
fi

STRUCTURE_EXTRA=""
if [ "$BUNDLER" = "vite" ]; then
  STRUCTURE_EXTRA="- \`package.json\` / \`vite.config.js\` — Vite project config and npm dependencies ($UI_LABEL, Navigo)"
elif { [ "$UI" = "preact" ] || [ "$UI" = "nanojsx" ]; } && [ "$BUNDLER" != "vite" ]; then
  STRUCTURE_EXTRA="- \`js/html.js\` — binds htm's tagged-template syntax to $UI_LABEL's h() once, so other files import \`html\` from here instead of JSX"
fi
if [ "$NPM_INSTALL_NEEDED" = true ] && [ "$BUNDLER" != "vite" ]; then
  STRUCTURE_EXTRA="${STRUCTURE_EXTRA}
- \`package.json\` — npm dependencies for the CSS compiler only (the JS side stays CDN-based)"
fi
if [ "$NPM_INSTALL_NEEDED" = true ]; then
  GITIGNORE_NOTE="\`node_modules/\`"
  [ "$BUNDLER" = "vite" ] && GITIGNORE_NOTE="${GITIGNORE_NOTE}, \`dist/\`"
  [ -n "$STYLER" ] && [ "$CSS_TOOLING" = "cli" ] && GITIGNORE_NOTE="${GITIGNORE_NOTE}, \`css/style.css\` (build output)"
  STRUCTURE_EXTRA="${STRUCTURE_EXTRA}
- \`.gitignore\` — excludes ${GITIGNORE_NOTE}"
fi

if [ "$STYLER" = "tailwind" ]; then
  if [ "$CSS_TOOLING" = "cli" ]; then
    CSS_STRUCTURE_LINE="- \`css/input.css\` — Tailwind source (\`@import \"tailwindcss\"\`); compiled to \`css/style.css\` by \`npm run dev:css\`/\`build:css\` (the standalone \`@tailwindcss/cli\`)"
  else
    CSS_STRUCTURE_LINE="- \`css/input.css\` — Tailwind source (\`@import \"tailwindcss\"\`), compiled on the fly by the \`@tailwindcss/vite\` plugin — no separate build step"
  fi
elif [ "$STYLER" = "sass" ]; then
  if [ "$CSS_TOOLING" = "cli" ]; then
    CSS_STRUCTURE_LINE="- \`css/style.scss\` — Sass source; compiled to \`css/style.css\` by \`npm run dev:css\`/\`build:css\` (the standalone \`sass\` CLI)"
  else
    CSS_STRUCTURE_LINE="- \`css/style.scss\` — Sass source, compiled on the fly by Vite's built-in Sass support — no separate build step or plugin needed"
  fi
else
  CSS_STRUCTURE_LINE="- \`css/style.css\` — plain CSS"
fi

if [ "$DEMO" = true ]; then
  DEMO_NOTE="

This project was generated with **--demo**: it includes a worked cart/products
example (js/store.js, ProductCard, ProductsPage) and a base -> component
pairing (js/base/Button -> js/components/LoginButton) to illustrate
the patterns. Delete or replace the demo content once you've seen how it
fits together."
else
  DEMO_NOTE=""
fi

cat > "$PROJECT_NAME/README.md" <<EOF
# $PROJECT_NAME

Scaffolded with NoF (No Frameworks) — ${UI_LABEL}${STATE_LABEL} + Navigo${TAGLINE_SUFFIX}.
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
${CSS_STRUCTURE_LINE}
${STRUCTURE_EXTRA}

See the \`no-framework\` skill's \`references/\` for the full architecture
guide (state management, routing, reactivity, component patterns${ARCH_GUIDE_SUFFIX}),
and \`references/ui_libraries.md\` specifically for $UI_LABEL's patterns.
EOF

echo "Done. Next steps:"
echo "  cd $PROJECT_NAME"
if [ "$BUNDLER" = "vite" ]; then
  echo "  npm install"
  echo "  npm run dev"
  if [ -n "$STYLER" ] && [ "$CSS_TOOLING" = "cli" ]; then
    echo "  npm run dev:css   # in a second terminal — Tailwind/Sass CLI runs independently of Vite here"
  fi
else
  if [ "$NPM_INSTALL_NEEDED" = true ]; then
    echo "  npm install       # for the CSS compiler (@tailwindcss/cli or sass) — the JS side stays CDN-based"
  fi
  echo "  npx live-server . --entry-file=index.html"
  if [ -n "$STYLER" ] && [ "$CSS_TOOLING" = "cli" ]; then
    echo "  npm run dev:css   # in a second terminal"
  fi
fi
