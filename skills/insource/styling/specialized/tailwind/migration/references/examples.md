# examples — worked v3 → v4 rewrites

Every unique code shape from the three consolidated sources, deduplicated. Data tables live in
[`breaking-changes.md`](breaking-changes.md); mistakes and their detection live in
[`anti-patterns.md`](anti-patterns.md). The border/ring/hover shims are NOT restated here — they
live in [`../method.md`](../method.md) §6; §5 below carries only the additional restore rules §6
omits.

## 1. Install and entry point

v3 — PostCSS chain + the trio:

```bash
npm install -D tailwindcss@^3.4 postcss autoprefixer
npx tailwindcss init -p
```

```js
// postcss.config.js (v3)
export default {
  plugins: { 'postcss-import': {}, tailwindcss: {}, autoprefixer: {} },
}
```

```css
/* src/app.css (v3) */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

v4 — one PostCSS plugin, nothing else:

```bash
npm install tailwindcss @tailwindcss/postcss
```

```js
// postcss.config.js (v4)
export default {
  plugins: { '@tailwindcss/postcss': {} },
}
```

```css
/* src/app.css (v4) */
@import "tailwindcss";
```

v4 with Vite (preferred for greenfield Vite/React/Vue; delete `postcss.config.js` if Vite was its
only consumer):

```bash
npm install tailwindcss @tailwindcss/vite
```

```ts
// vite.config.ts
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({ plugins: [tailwindcss()] })
```

Standalone CLI:

```bash
npx tailwindcss -i ./src/in.css -o ./dist/out.css --watch       # v3
npx @tailwindcss/cli -i ./src/in.css -o ./dist/out.css --watch  # v4
```

## 2. Full config translation — `tailwind.config.js` → `@theme` stylesheet

### 2.1 Typical app (colors, spacing, fonts, dark mode, plugins, content)

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js,ts,jsx,tsx,vue,svelte}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: { brand: { DEFAULT: '#1da1f2', dark: '#0d8ddf' } },
      spacing: { '128': '32rem' },
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] },
    },
  },
  plugins: [require('@tailwindcss/typography'), require('@tailwindcss/forms')],
}
```

becomes:

```css
@import "tailwindcss";

@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";

@theme {
  --color-brand: #1da1f2;
  --color-brand-dark: #0d8ddf;
  --spacing-128: 32rem;
  --font-sans: Inter, system-ui, sans-serif;
}

@custom-variant dark (&:where(.dark, .dark *));

@source "../src/**/*.{html,js,ts,jsx,tsx,vue,svelte}";
```

Notes:

- v4 auto-detects most content paths; explicit `@source` is needed only for templates outside the
  default discovery (e.g. a sibling package).
- v4 has NO equivalent for the `theme.extend` vs `theme.replace` distinction — `@theme` always
  extends. Namespace-reset mechanics: `../config/method.md`.

### 2.2 Namespaces beyond colors (radius, breakpoints, DEFAULT-less groups)

```js
module.exports = {
  content: ['./src/**/*.{html,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: { brand: { primary: '#5b21b6', accent: '#f59e0b' } },
      spacing: { '128': '32rem' },
      fontFamily: { sans: ['Inter', 'ui-sans-serif', 'system-ui'] },
      borderRadius: { '4xl': '2rem' },
      screens: { '3xl': '1920px' },
    },
  },
  plugins: [require('@tailwindcss/typography')],
}
```

becomes:

```css
@import "tailwindcss";

@theme {
  --color-brand-primary: #5b21b6;
  --color-brand-accent: #f59e0b;
  --spacing-128: 32rem;
  --font-sans: "Inter", ui-sans-serif, system-ui;
  --radius-4xl: 2rem;
  --breakpoint-3xl: 1920px;
}

@plugin "@tailwindcss/typography";
```

The full v3-path → v3-variable namespace map is in [`breaking-changes.md`](breaking-changes.md) §9.

## 3. Per-trap code rewrites

### 3.1 Variant stacking flip

```html
<!-- v3: right-to-left -->
<ul class="py-4 first:*:pt-0 last:*:pb-0"><li>Item</li></ul>
<!-- v4: left-to-right -->
<ul class="py-4 *:first:pt-0 *:last:pb-0"><li>Item</li></ul>
```

Three-variant chain (manual review, codemod may miss it):

```html
<div class="group-hover:first:*:opacity-100">  <!-- v3 -->
<div class="group-hover:*:first:opacity-100">  <!-- v4 -->
```

Read each flipped result aloud before committing — "`*:first:pt-0` = for every direct child, when
first, padding-top zero". If the sentence doesn't match the intent, the order is wrong. Chains
combining arbitrary `[&…]` variants with structural pseudo-classes are never safe to trust
(breaking-changes §2.1; AP-10).

### 3.2 Opacity → slash modifier

```html
<!-- v3 -->
<div class="bg-black bg-opacity-50">Overlay</div>
<p class="text-zinc-900 text-opacity-70">Muted</p>
<div class="border border-blue-500 border-opacity-50"></div>
<input class="placeholder-zinc-400 placeholder-opacity-50">
<!-- v4 -->
<div class="bg-black/50">Overlay</div>
<p class="text-zinc-900/70">Muted</p>
<div class="border border-blue-500/50"></div>
<input class="placeholder-zinc-400/50">
```

### 3.3 Prefix flip

```js
// v3 — tailwind.config.js
export default { prefix: 'tw-' }
```

```css
/* v4 — entry CSS */
@import "tailwindcss" prefix(tw);
```

```html
<div class="tw-flex tw-bg-red-500 tw-hover:bg-red-600">   <!-- v3 -->
<div class="tw:flex tw:bg-red-500 tw:hover:bg-red-600">   <!-- v4 -->
```

Mechanical but total: every `tw-` occurrence, including template strings and test selectors — use
the codemod, then the AP-17 grep.

### 3.4 Important modifier flip

```html
<div class="!flex !bg-red-500">          <!-- v3 -->
<div class="flex! bg-red-500!">          <!-- v4 -->
```

```css
.btn { @apply font-bold !important; }    /* v3 */
.btn { @apply font-bold!; }              /* v4 */
```

```diff
- .btn { @apply font-bold #{!important}; }   /* v3 in Sass */
+ .btn { @apply font-bold!; }                /* v4 — same form, Sass out of the pipeline anyway */
```

### 3.5 Outline rename

```html
<input class="focus:outline-none border focus:border-blue-500">  <!-- v3 -->
<input class="focus:outline-hidden border focus:border-blue-500"> <!-- v4 -->
```

```html
<button class="focus:outline-hidden"></button> <!-- = v3 outline-none: invisible, kept for forced-colors mode -->
<button class="focus:outline-none"></button>   <!-- v4: outline genuinely removed — a11y trap, see AP-20 -->
```

### 3.6 Arbitrary values — var parentheses, underscore spaces

```html
<div class="bg-[--brand-color] text-[--brand-fg]">  <!-- v3 -->
<div class="bg-(--brand-color) text-(--brand-fg)">  <!-- v4 -->
<div class="text-[--accent]/80">  <!-- v3 -->
<div class="text-(--accent)/80">  <!-- v4: modifier composes on the paren form -->
```

```html
<div class="grid grid-cols-[max-content,auto,minmax(0,1fr)]">    <!-- v3 -->
<div class="grid grid-cols-[max-content_auto_minmax(0,1fr)]">    <!-- v4 -->
<div class="object-[center,top]">  <!-- v3 -->
<div class="object-[center_top]">  <!-- v4 -->
```

Top-level separators become underscores; commas inside real CSS functions (`minmax(0,1fr)`) stay.

### 3.7 Transform and transition reset

```html
<button class="scale-150 focus:transform-none">              <!-- v3 -->
<button class="scale-150 focus:scale-none">                  <!-- v4 -->
<button class="rotate-45 scale-150 focus:rotate-none focus:scale-none">  <!-- v4, multi-prop -->
```

```html
<button class="transition-[opacity,transform] hover:scale-150">  <!-- v3 -->
<button class="transition-[opacity,scale] hover:scale-150">      <!-- v4 -->
```

### 3.8 Scale renames (shadow / blur / rounded)

```diff
- <div class="shadow-sm">Subtle shadow</div>
+ <div class="shadow-xs">Subtle shadow</div>
- <div class="shadow">Standard shadow</div>
+ <div class="shadow-sm">Standard shadow</div>
- <img class="blur-sm">
+ <img class="blur-xs">
- <div class="rounded">
+ <div class="rounded-sm">
```

CSS values are identical — only names moved. Let the codemod do this; hand-editing invites
double-rename (AP-9).

### 3.9 Border — surgical fix (the explicit-color alternative to the §6 shim)

```diff
- <div class="border p-4">
+ <div class="border border-gray-200 p-4">
- <hr class="border-t">
+ <hr class="border-t border-gray-200">
```

Every border declares its color; v4 default shifts become impossible. Long-term right fix.

### 3.10 Ring — surgical fix

```html
<button class="focus:ring focus:ring-blue-500">Save</button>      <!-- v3: 3px blue -->
<button class="focus:ring-3 focus:ring-blue-500">Save</button>    <!-- v4: 3px again -->
<button class="focus:ring focus:ring-blue-500">Save</button>      <!-- v4: accept 1px refresh -->
```

ALWAYS pair `ring` with an explicit color in v4 — the color default flipped to `currentColor`.

### 3.11 Hover gating and touch fallback

```css
/* v3 emitted: always applies */
.hover\:underline:hover { text-decoration: underline; }
/* v4 emits: */
@media (hover: hover) {
  .hover\:underline:hover { text-decoration: underline; }
}
```

```html
<button class="bg-blue-500 hover:bg-blue-700">Tap me</button>                    <!-- v3 behavior -->
<button class="bg-blue-500 hover:bg-blue-700 active:bg-blue-800">Tap me</button> <!-- v4: pair with active: -->
```

Escape hatch `@custom-variant hover (&:hover);` — see [`../method.md`](../method.md) §6, last resort.

### 3.12 Gradients

```html
<div class="bg-gradient-to-r from-red-500 to-yellow-400"></div>  <!-- v3 -->
<div class="bg-linear-to-r from-red-500 to-yellow-400"></div>    <!-- v4 -->
<div class="bg-radial from-cyan-300 to-blue-700"></div>          <!-- new in v4 -->
<div class="bg-conic-180 from-zinc-300 via-zinc-50 to-zinc-300"></div>
```

### 3.13 Custom utilities — plugin / `@layer utilities` → `@utility`

v3 JS plugin:

```js
// plugins/scrollbar.js
const plugin = require('tailwindcss/plugin')
module.exports = plugin(function ({ addUtilities }) {
  addUtilities({
    '.scrollbar-thin': { 'scrollbar-width': 'thin' },
    '.scrollbar-none': { 'scrollbar-width': 'none', '&::-webkit-scrollbar': { display: 'none' } },
  })
})
```

v4 CSS-first equivalent:

```css
@utility scrollbar-thin {
  scrollbar-width: thin;
}
@utility scrollbar-none {
  scrollbar-width: none;
  &::-webkit-scrollbar { display: none; }
}
```

Or keep the legacy JS plugin and just load it: `@plugin "./plugins/scrollbar";`.

Static list → functional utility:

```css
/* v3 */
@layer utilities {
  .tab-1 { tab-size: 1; }
  .tab-2 { tab-size: 2; }
  .tab-4 { tab-size: 4; }
  .tab-8 { tab-size: 8; }
}

/* v4 — one declaration emits every used integer */
@utility tab-* {
  tab-size: --value(integer);
}

/* v3 */
@layer utilities {
  .skew-10deg { transform: skewY(-10deg); } }

/* v4 */
@utility skew-10deg {
  transform: skewY(-10deg);
}
```

Functional helper semantics (`--value`, `--modifier`, `--alpha`, `--spacing`):
`../config/method.md`.

### 3.14 Components layer → `@utility`

```css
/* v3 */
@layer components {
  .btn {
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
    background-color: #5b21b6;
    color: white;
  }
}

/* v4 — expressed as a utility so other utilities can override it */
@utility btn {
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  background-color: #5b21b6;
  color: white;
}
```

### 3.15 `theme.container` → `@utility container`

```js
// v3
module.exports = { theme: { container: { center: true, padding: '2rem' } } }
```

```css
/* v4 */
@utility container {
  margin-inline: auto;
  padding-inline: 2rem;
}
```

### 3.16 Custom variants — dark mode and friends

```js
// v3
module.exports = { darkMode: 'class' /* or 'media', or ['selector', '[data-theme="dark"]'] */ }
```

```css
/* v4 — class strategy */
@custom-variant dark (&:where(.dark, .dark *));
/* v4 — data-attribute strategy */
@custom-variant dark (&:where([data-theme="dark"], [data-theme="dark"] *));
```

```html
<html class="dark">  <!-- unchanged; markup stays the same in both strategies -->
```

Plugin `addVariant()` → one-liner:

```js
// v3
const plugin = require('tailwindcss/plugin')
module.exports = plugin(function ({ addVariant }) {
  addVariant('supports-grid', '@supports (display: grid)')
})
```

```css
/* v4 */
@custom-variant supports-grid (@supports (display: grid));
```

Both enable `class="supports-grid:grid"`.

### 3.17 `theme()` rewrite

```css
/* v3 */
.my-class { background-color: theme(colors.red.500); }
@media (min-width: theme(screens.xl)) {
  .hero { padding: theme(spacing.16); }
}

/* v4 */
.my-class { background-color: var(--color-red-500); }
@media (width >= theme(--breakpoint-xl)) {
  .hero { padding: theme(--spacing-16); }
}
```

### 3.18 Safelist → `@source inline`

```js
// v3
module.exports = {
  safelist: [
    'bg-red-500', 'bg-green-500', 'bg-blue-500',
    { pattern: /bg-(red|green|blue)-(100|500|900)/ },
    { pattern: /text-(red|green|blue)-(100|500|900)/, variants: ['hover'] },
  ],
}
```

```css
/* v4 */
@source inline("bg-red-500 bg-green-500 bg-blue-500");          /* list form */
@source inline("bg-{red,green,blue}-{100,500,900}");            /* brace expansion = v3 pattern */
@source inline("{hover:,}text-{red,green,blue}-{100,500,900}"); /* with variants */
@source inline("p-{1..12}");                                     /* range form */
@source inline("{hover:,focus:,}text-zinc-{500,700,900}/{50,70,100}"); /* stacked */
```

This directive's expansion grammar is owned by `../dynamic-classes/method.md`.

### 3.19 Replacing `corePlugins`

Per-utility disable:

```css
/* Option A: exclude the path that generates them */
@source not "../src/legacy/**/*";

/* Option B: no-op override (last resort) */
@utility float-left  { float: unset; }
@utility float-right { float: unset; }
```

Neither fully reproduces v3 behavior — if disabling utilities is non-negotiable, STAY on v3.4
(`method.md` §1). Enforcement alternatives when the goal is *forbidding usage*:

```js
// .eslintrc — illustrative ban on float/clear utilities
rules: {
  'tailwindcss/no-custom-classname': ['error', { whitelist: ['^(?!(float|clear)-).*$'] }],
}
```

```bash
! grep -rEn 'class="[^"]*\bfloat-' src    # CI gate
```

Preflight disable (`corePlugins: { preflight: false }` has no v4 option):

```css
@import "tailwindcss/theme.css";       /* skip @import "tailwindcss/preflight.css" */
@import "tailwindcss/utilities.css";

@layer base {
  /* your own reset here */
  *, ::before, ::after { box-sizing: border-box; }
}
```

(The `source(none)` call option on `@import "tailwindcss"` controls content *detection*, not
preflight — don't confuse the two.)

### 3.20 JS plugins → `@plugin`

```js
// v3
module.exports = { plugins: [require('@tailwindcss/typography'), require('@tailwindcss/forms')] }
```

```css
/* v4 */
@import "tailwindcss";
@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";
```

### 3.21 `resolveConfig` → CSS-variable reads

```js
// v3
import resolveConfig from 'tailwindcss/resolveConfig'
import tailwindConfig from '../tailwind.config.js'
const fullConfig = resolveConfig(tailwindConfig)
const brandColor = fullConfig.theme.colors.brand.DEFAULT
const red500 = fullConfig.theme.colors.red['500']
```

```js
// v4 — browser runtime
const brandColor = getComputedStyle(document.documentElement)
  .getPropertyValue('--color-brand').trim()

// v4 — wrap it once, use it everywhere
function tokenValue(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}
const md = tokenValue('--breakpoint-md')
```

No DOM (SSR, Node tooling, Storybook-headless): parse the entry CSS's `:root { … }` block with
PostCSS, or emit `tokens.json` from a build step, or keep tokens in a shared JS module that both
the stylesheet and the runtime read.

## 4. Scoped component styles — `@reference` setups

v3 worked out of the box; v4 compiles each scoped block in isolation and the theme is invisible
until referenced.

```vue
<!-- v3 -->
<style scoped>
.btn { @apply px-4 py-2 bg-blue-500 text-white rounded; }
</style>

<!-- v4 -->
<style scoped>
@reference "../app.css";
.btn { @apply px-4 py-2 bg-blue-500 text-white rounded-sm; }
</style>
```

Same rule for Svelte `<style>` and `*.module.css`. Without `@reference` the build errors
`Cannot apply unknown utility class: px-4`.

Path rules:

- The path points to the stylesheet that contains `@import "tailwindcss"` — relative to the
  `.vue`/`.svelte`/`.module.css` file, NOT the project root.
- `@reference "tailwindcss";` (bare specifier, if the engine resolves it) imports ONLY the default
  theme — none of your project's `@theme` overrides. Use when that's what you want.
- NEVER use bare `@import "../../app.css";` inside a scoped block — it duplicates the entire CSS
  bundle into every component.

## 5. Restore rules beyond the §6 shim

[`../method.md`](../method.md) §6 already covers border-color, ring width/color, and hover gating.
The remaining v3 defaults the sources restore — append these to the same stylesheet, same time-box
(one release cycle, then audit and delete):

```css
@layer base {
  /* v3 ::placeholder color (v4: current text at 50% opacity) */
  input::placeholder, textarea::placeholder { color: var(--color-gray-400); }

  /* v3 button cursor (v4: default) */
  button:not(:disabled), [role="button"]:not(:disabled) { cursor: pointer; }

  /* v3 dialog centering */
  dialog { margin: auto; }

  /* v3 hidden-attribute override (v4: display utilities win over [hidden]) */
  [hidden]:where(:not([hidden="until-found"])) { display: none !important; }
}
```

## 6. Staged migration — `@config` bridge

```css
@import "tailwindcss";
@config "../tailwind.config.js";

/* v4-native additions alongside the legacy config */
@theme {
  --color-brand: oklch(0.6 0.18 250);
}
```

The v4 engine consumes `theme`, `content`, `plugins` from the JS file; `corePlugins`, `safelist`,
and `separator` are ignored. Migrate one category at a time and delete its JS block in the same
commit (procedure in AP-13). NEVER define the same token category in BOTH `@theme` and the JS
config. Remove `@config` when the JS file is empty.

## 7. Codemod run + diff review walkthrough

```bash
# 1. clean working tree
git status                       # verify no uncommitted changes

# 2. branch so the diff stays reviewable
git checkout -b chore/tailwind-v4

# 3. Node check — the tool requires Node 20+
node --version                   # >= 20.0.0, else: nvm use 20

# 4. run the codemod
npx @tailwindcss/upgrade

# 5. read the diff — it touched package.json, config files, and templates
git diff --stat
git diff > /tmp/tailwind-upgrade.diff
less /tmp/tailwind-upgrade.diff

# 6. fresh install (dependency swap happened in package.json)
rm -rf node_modules package-lock.json
npm install

# 7. verify
npm run build
```

What to look for while reading the diff: scale renames (`shadow-sm`→`shadow-xs`), bang flips
(`!flex`→`flex!`), prefix flips (`tw-flex`→`tw:flex`), opacity pairs merged to slash form, variant
chains reordered. What is DEFINITELY NOT in the diff: everything in
[`breaking-changes.md`](breaking-changes.md) §10's "missed" table — dynamic class strings,
`@reference` lines, plugin code, comments containing class names, and every §3 default-behavior
visual regression. Run §9's audit script next, then §10's visual gate.

## 8. Dual-version monorepo (one library, v3 + v4 consumers)

```
monorepo/
  packages/
    ui-tokens/        # plain CSS variables, version-agnostic
      tokens.css
    ui-components/    # shared React/Vue components, utility strings only
      src/
        button.tsx
  apps/
    app-v3/           # tailwindcss@^3
      tailwind.config.js
      src/
    app-v4/           # tailwindcss@^4
      src/app.css
```

```css
/* packages/ui-tokens/tokens.css */
:root {
  --color-brand-primary: #5b21b6;
  --color-brand-accent: #f59e0b;
  --spacing-128: 32rem;
}
```

```js
// apps/app-v3/tailwind.config.js — read the same variables through the JS config
module.exports = {
  theme: { extend: { colors: { brand: { primary: 'var(--color-brand-primary)' } } } },
}
```

```css
/* apps/app-v4/src/app.css */
@import "tailwindcss";
@import "@my-org/ui-tokens/tokens.css";

@theme inline {
  --color-brand-primary: var(--color-brand-primary);
  --color-brand-accent: var(--color-brand-accent);
  --spacing-128: var(--spacing-128);
}
```

Components in `ui-components` emit plain utility strings (`bg-brand-primary`) that resolve in both
apps — no `@apply`, no custom directives (strategy: [`../method.md`](../method.md) §7).

## 9. Audit script for v3 leftovers

`scripts/audit-tailwind-v4.sh` — run after the codemod, before merging, regardless of codebase
size:

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "--- @tailwind trio leftovers ---"
grep -rEn '@tailwind (base|components|utilities)' src/ || true

echo "--- Leading-bang !class (v3 syntax) ---"
grep -rEn 'class(Name)?=["'\''`][^"'\''`]*![a-z]' src/ || true

echo "--- v3-style prefix tw- (should be tw:) ---"
grep -rEn '\btw-(flex|grid|block|hidden|p-|m-|w-|h-)' src/ || true

echo "--- *-opacity-* utilities (removed) ---"
grep -rEn '\b(bg|text|border|divide|ring|placeholder)-opacity-' src/ || true

echo "--- bare ring (default width changed to 1px; needs PCRE) ---"
grep -rPn '\bring\b(?!-)' src/ || true

echo "--- v3 arbitrary CSS var syntax [--var] ---"
grep -rEn '\[--[a-z]' src/ || true

echo "--- old outline-none (now means outline-style:none) ---"
grep -rEn '\boutline-none\b' src/ || true

echo "--- bare border without explicit colour ---"
grep -rEn 'class="[^"]*\bborder\b[^-/]' src/ || true

echo "--- stacked variant chains (2+ variants; verify order semantics) ---"
grep -rEn 'class="[^"]*\b[a-z-]+:[a-z-]+:' src/ || true

echo "--- resolveConfig call sites ---"
grep -rn 'tailwindcss/resolveConfig' src/ || true

echo "--- runtime-assembled class strings ---"
grep -rn 'class\s*=\s*[`"][^`"]*\${' src/ || true

echo "--- scoped @apply without @reference ---"
find src \( -name '*.vue' -o -name '*.svelte' -o -name '*.module.css' \) \
  | xargs grep -l '@apply' 2>/dev/null \
  | while read -r f; do grep -q '@reference' "$f" || echo "needs @reference: $f"; done

echo "--- removed config options in tailwind.config.js (if kept via @config) ---"
grep -En 'corePlugins|safelist|separator|prefix:' tailwind.config.js || true

echo "Audit complete."
```

`package.json` wiring so leftovers can't regress:

```json
{
  "scripts": {
    "audit:tailwind-v4": "bash scripts/audit-tailwind-v4.sh"
  }
}
```

Production-bundle spot check (previously-safelisted classes must survive tree-shaking):

```bash
npm run build
grep -c "bg-red-500\|bg-blue-500" dist/assets/*.css
```

## 10. Visual regression workflow

```bash
# pre-merge baseline (on the v3 commit)
npx playwright test --project=visual --update-snapshots
git add tests/snapshots
git commit -m "chore: visual baseline pre v4 upgrade"

# merge upgrade
git merge chore/tailwind-v4

# post-merge diff
npx playwright test --project=visual
```

Every diff is either intentional (a §3 default-color shift) or a bug — inspect each file Playwright
marks; NEVER blanket-accept. (Gates: [`../method.md`](../method.md) §8.)

## Sources

- https://tailwindcss.com/docs/upgrade-guide
- https://tailwindcss.com/docs/functions-and-directives
- https://tailwindcss.com/blog/tailwindcss-v4
- https://tailwindcss.com/docs/detecting-classes-in-source-files
- https://github.com/tailwindlabs/tailwindcss/issues/16346
