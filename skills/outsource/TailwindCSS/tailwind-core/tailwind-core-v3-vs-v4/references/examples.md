# Side-by-Side v3 vs v4 Examples

Every example shows the v3 form and the v4 equivalent. Copy-paste-ready.
All snippets verified against official docs (see SOURCES.md at repo root).

## 1. Install + CSS Entry Point

### v3 : PostCSS + autoprefixer
```bash
npm install -D tailwindcss@^3.4 postcss autoprefixer
npx tailwindcss init -p
```
```js
// postcss.config.js
module.exports = {
  plugins: { tailwindcss: {}, autoprefixer: {} },
}
```
```css
/* src/app.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### v4 : single PostCSS plugin OR Vite plugin
```bash
npm install tailwindcss @tailwindcss/postcss
```
```js
// postcss.config.js
module.exports = {
  plugins: { '@tailwindcss/postcss': {} },
}
```
```css
/* src/app.css */
@import "tailwindcss";
```

### v4 : Vite (preferred for greenfield Vite/React/Vue projects)
```bash
npm install tailwindcss @tailwindcss/vite
```
```js
// vite.config.js
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
export default defineConfig({ plugins: [tailwindcss()] })
```
```css
/* src/app.css */
@import "tailwindcss";
```

## 2. Full Config Translation

### v3 : `tailwind.config.js`
```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js,ts,jsx,tsx,vue,svelte}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: { DEFAULT: '#1da1f2', dark: '#0d8ddf' },
      },
      spacing: { '128': '32rem' },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
}
```

### v4 : `src/app.css`
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

Notes :
- v4 auto-detects most content paths ; explicit `@source` is needed only when
  templates live outside the default discovery (e.g. a sibling package).
- v4 has NO equivalent for `theme.extend` vs `theme.replace` distinction.
  `@theme` always extends ; to fully replace a category, redefine every
  token in it OR use `@theme inline { ... }`.

## 3. Dark Mode

### v3
```js
// tailwind.config.js
module.exports = { darkMode: 'class' /* or 'media' or ['selector', '[data-theme="dark"]'] */ }
```
```html
<html class="dark"> ... </html>
```

### v4
```css
@import "tailwindcss";
@custom-variant dark (&:where(.dark, .dark *));
```
```html
<html class="dark"> ... </html>
```

Data-attribute variant in v4 :
```css
@custom-variant dark (&:where([data-theme="dark"], [data-theme="dark"] *));
```

## 4. Custom Plugin

### v3 : JS plugin file
```js
// plugins/scrollbar.js
const plugin = require('tailwindcss/plugin')
module.exports = plugin(function ({ addUtilities }) {
  addUtilities({
    '.scrollbar-thin': {
      'scrollbar-width': 'thin',
    },
    '.scrollbar-none': {
      'scrollbar-width': 'none',
      '&::-webkit-scrollbar': { display: 'none' },
    },
  })
})
```
```js
// tailwind.config.js
module.exports = { plugins: [require('./plugins/scrollbar')] }
```

### v4 : CSS-first via `@utility`
```css
@import "tailwindcss";

@utility scrollbar-thin {
  scrollbar-width: thin;
}

@utility scrollbar-none {
  scrollbar-width: none;
  &::-webkit-scrollbar { display: none; }
}
```

### v4 : keep legacy JS plugin via `@plugin`
```css
@import "tailwindcss";
@plugin "./plugins/scrollbar";
```

## 5. Safelist (Dynamic Class Names)

### v3
```js
module.exports = {
  safelist: [
    'bg-red-500', 'bg-green-500', 'bg-blue-500',
    { pattern: /bg-(red|green|blue)-(100|500|900)/ },
    { pattern: /text-(red|green|blue)-(100|500|900)/, variants: ['hover'] },
  ],
}
```

### v4
```css
@import "tailwindcss";

/* List form */
@source inline("bg-red-500 bg-green-500 bg-blue-500");

/* Brace expansion (equivalent of v3 pattern) */
@source inline("bg-{red,green,blue}-{100,500,900}");

/* With variants */
@source inline("{hover:,}text-{red,green,blue}-{100,500,900}");
```

## 6. Scoped Component Styles (Vue, Svelte, CSS Modules)

### v3 : worked out of the box
```vue
<style scoped>
.btn { @apply px-4 py-2 bg-blue-500 text-white rounded; }
</style>
```

### v4 : `@reference` REQUIRED
```vue
<style scoped>
@reference "../app.css";
.btn { @apply px-4 py-2 bg-blue-500 text-white rounded-sm; }
</style>
```

Without `@reference`, v4 errors : `Cannot apply unknown utility class : px-4`.
The path points to whatever stylesheet imports `tailwindcss`.

## 7. Disable Specific Utilities

### v3
```js
module.exports = {
  corePlugins: { float: false, container: false },
}
```

### v4
There is NO direct equivalent. Options :

```css
/* Option A : exclude a path from content scanning so its float utilities are never generated */
@source not "../src/legacy/**/*";
```

```css
/* Option B : redefine the utility to a no-op (use as a last resort) */
@utility float-left { float: unset; }
@utility float-right { float: unset; }
```

Neither option fully reproduces v3 behaviour. If disabling utilities is a
hard requirement, STAY on v3.4.

## 8. JS Theme Access at Runtime

### v3
```js
import resolveConfig from 'tailwindcss/resolveConfig'
import tailwindConfig from '../tailwind.config.js'
const fullConfig = resolveConfig(tailwindConfig)
const brandColor = fullConfig.theme.colors.brand.DEFAULT
```

### v4
```js
const brandColor = getComputedStyle(document.documentElement)
  .getPropertyValue('--color-brand')
  .trim()
```

This requires the user's browser to be present (no SSR access). For
build-time access in v4, parse the CSS directly or define brand tokens in a
shared JS module that both your stylesheet and runtime read from.

## 9. Custom Variant

### v3 : plugin with `addVariant()`
```js
const plugin = require('tailwindcss/plugin')
module.exports = plugin(function ({ addVariant }) {
  addVariant('supports-grid', '@supports (display: grid)')
})
```

### v4 : one-line `@custom-variant`
```css
@custom-variant supports-grid (@media (display: grid));
```

Both let you write `<div class="supports-grid:grid">`.

## 10. Restore v3 Defaults Inside v4

When upgrading a large app and visual parity matters more than clean v4
code, drop this shim into the stylesheet right after `@import "tailwindcss"`:

```css
@import "tailwindcss";

/* Restore v3 border-color default (gray-200) */
@layer base {
  *, ::after, ::before, ::backdrop, ::file-selector-button {
    border-color: var(--color-gray-200, currentColor);
  }
}

/* Restore v3 ring defaults (3px width, blue-500 colour) */
@theme {
  --default-ring-width: 3px;
  --default-ring-color: var(--color-blue-500);
}

/* Restore v3 button cursor */
@layer base {
  button:not(:disabled), [role="button"]:not(:disabled) { cursor: pointer; }
}

/* Restore v3 always-apply hover */
@custom-variant hover (&:hover);
```

NEVER ship this shim long-term. It defeats v4 design intent. Use it as a
temporary bridge while components are audited one at a time.

## 11. Important Modifier

### v3
```html
<button class="!flex hover:!bg-red-500">
```

### v4
```html
<button class="flex! hover:bg-red-500!">
```

## 12. CSS Variable Arbitrary Value

### v3
```html
<div class="bg-[--brand-color] text-[--brand-fg]">
```

### v4
```html
<div class="bg-(--brand-color) text-(--brand-fg)">
```

## 13. Standalone CLI

### v3
```bash
npx tailwindcss -i ./src/in.css -o ./dist/out.css --watch
```

### v4
```bash
npx @tailwindcss/cli -i ./src/in.css -o ./dist/out.css --watch
```

## 14. Variant Stacking Order

### v3 : right-to-left
```html
<!-- "first child of any direct child" : *: applies, then first: filters -->
<ul class="first:*:pt-0">
  <li> ... <p>This <p>'s first child gets pt-0</p></p> ... </li>
</ul>
```

### v4 : left-to-right
```html
<!-- Same intent : *: applies, then first: filters -->
<ul class="*:first:pt-0">
  <li> ... <p>This <p>'s first child gets pt-0</p></p> ... </li>
</ul>
```

The `npx @tailwindcss/upgrade` codemod rewrites this for common cases.
Manual review needed for bespoke chains involving `[&...]` arbitrary
variants combined with structural pseudo-classes.

## 15. Opt-in Legacy JS Config (partial migration)

When migrating a large v3 codebase incrementally :

```css
@import "tailwindcss";
@config "../tailwind.config.js";
```

This lets the v4 engine consume the existing v3 JS config. Migrate the JS
keys to `@theme` one category at a time. Remove `@config` when the JS file
is empty. NEVER define the same token in BOTH `@theme` AND the JS config :
behaviour is unspecified.
