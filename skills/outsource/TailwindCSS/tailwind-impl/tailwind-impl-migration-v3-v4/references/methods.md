# Methods : Migration Procedures

Per-area procedures. Each runs independently. Sequence matters only
when noted.

## Method 1 : Branch and Run the Upgrade Tool

```bash
# 1. clean working tree
git status
# verify no uncommitted changes

# 2. branch
git checkout -b chore/tailwind-v4

# 3. verify Node version
node --version
# must be >= 20.0.0

# 4. run tool
npx @tailwindcss/upgrade

# 5. inspect diff
git diff --stat
git diff > /tmp/tailwind-upgrade.diff
less /tmp/tailwind-upgrade.diff

# 6. install fresh
rm -rf node_modules package-lock.json
npm install

# 7. verify build
npm run build
```

The tool writes through three layers : `package.json`, configuration
files (`tailwind.config.js`, `postcss.config.js`, `vite.config.ts`),
and templates (`.html`, `.tsx`, `.vue`, `.svelte`).

## Method 2 : Manual Audit Before Upgrade

Run grep across the source tree :

```bash
# corePlugins usage
grep -rn "corePlugins" tailwind.config.js

# safelist
grep -rn "safelist" tailwind.config.js

# separator
grep -rn "separator" tailwind.config.js

# prefix
grep -rn "prefix:" tailwind.config.js

# resolveConfig in app code
grep -rn "tailwindcss/resolveConfig" src

# scoped @apply
grep -rln "@apply" src --include="*.vue" --include="*.svelte" --include="*.module.css"

# bg-opacity / text-opacity / etc.
grep -rn "bg-opacity-\|text-opacity-\|border-opacity-\|ring-opacity-\|placeholder-opacity-\|divide-opacity-" src

# dynamic opacity in templates
grep -rn 'bg-opacity-\${' src

# bare border / ring without colour
grep -rEn 'class="[^"]*\b(border|ring)\b[^-/]' src
```

Document each finding in a checklist. Resolve before running the tool.

## Method 3 : Convert tailwind.config.js to @theme

Source (`tailwind.config.js`) :

```js
module.exports = {
  content: ['./src/**/*.{html,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: { primary: '#5b21b6', accent: '#f59e0b' },
      },
      spacing: { '128': '32rem' },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
      borderRadius: { '4xl': '2rem' },
      screens: { '3xl': '1920px' },
    },
  },
  plugins: [require('@tailwindcss/typography')],
}
```

Target (`src/app.css`) :

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

Namespace mapping :

| v3 path | v4 CSS variable |
|---------|-----------------|
| `theme.extend.colors.<group>.<shade>` | `--color-<group>-<shade>` |
| `theme.extend.colors.<name>` | `--color-<name>` |
| `theme.extend.spacing.<key>` | `--spacing-<key>` |
| `theme.extend.fontFamily.<key>` | `--font-<key>` |
| `theme.extend.fontSize.<key>` | `--text-<key>` |
| `theme.extend.fontWeight.<key>` | `--font-weight-<key>` |
| `theme.extend.borderRadius.<key>` | `--radius-<key>` |
| `theme.extend.boxShadow.<key>` | `--shadow-<key>` |
| `theme.extend.screens.<key>` | `--breakpoint-<key>` |
| `theme.extend.animation.<key>` | `--animate-<key>` |
| `theme.extend.transitionTimingFunction.<key>` | `--ease-<key>` |

## Method 4 : Convert @tailwind Directives

v3 entry :

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

v4 entry :

```css
@import "tailwindcss";
```

If you imported partial layers in v3 :

```css
@tailwind base;
@tailwind components;
```

v4 equivalent :

```css
@import "tailwindcss/preflight";
@import "tailwindcss/utilities";
```

## Method 5 : Convert PostCSS Config

v3 (`postcss.config.js` or `.mjs`) :

```js
export default {
  plugins: {
    "postcss-import": {},
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

v4 :

```js
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
}
```

Delete `postcss-import` and `autoprefixer` from `devDependencies` ;
both are built into the Oxide engine.

## Method 6 : Convert Vite Setup

v3 used the PostCSS plugin transparently. v4 has a native Vite plugin :

```ts
// vite.config.ts
import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss()],
});
```

Delete `postcss.config.js` if Vite was its only consumer.

## Method 7 : Convert Safelist to @source inline

v3 :

```js
module.exports = {
  safelist: [
    'bg-red-500',
    'bg-blue-500',
    { pattern: /bg-(red|green|blue)-(100|500|900)/ },
  ],
}
```

v4 :

```css
@import "tailwindcss";

@source inline("bg-red-500 bg-blue-500");
@source inline("bg-{red,green,blue}-{100,500,900}");
```

Brace expansion replaces the regex pattern. Variants stack :

```css
@source inline("{hover:,focus:,}bg-red-{500,600,700}");
```

## Method 8 : Restore v3 Defaults via @layer base

For projects with extensive `border`, `ring`, `placeholder` usage
without explicit colours, restore v3 defaults globally rather than
rewriting every component :

```css
@import "tailwindcss";

@theme {
  --default-ring-width: 3px;
  --default-ring-color: var(--color-blue-500);
}

@layer base {
  *,
  ::after,
  ::before,
  ::backdrop,
  ::file-selector-button {
    border-color: var(--color-gray-200, currentColor);
  }
  input::placeholder,
  textarea::placeholder {
    color: var(--color-gray-400);
  }
  button:not(:disabled),
  [role="button"]:not(:disabled) {
    cursor: pointer;
  }
  dialog {
    margin: auto;
  }
}

@custom-variant hover (&:hover);
```

The `@custom-variant hover (&:hover);` line removes the `(hover: hover)`
gating so touch devices apply hover styles like in v3.

## Method 9 : Scoped @apply Fix (Vue / Svelte / CSS Modules)

For each scoped stylesheet using `@apply` :

```vue
<!-- before -->
<style>
  h1 { @apply text-2xl font-bold text-red-500; }
</style>

<!-- after -->
<style>
  @reference "../../app.css";
  h1 { @apply text-2xl font-bold text-red-500; }
</style>
```

The path is relative to the source file (the `.vue` / `.svelte` /
`.module.css`), NOT the project root.

Use `@reference "tailwindcss";` to import only the default theme,
without your project's `@theme` overrides :

```vue
<style>
  @reference "tailwindcss";
  h1 { @apply text-2xl font-bold; }
</style>
```

NEVER use bare `@import "../../app.css";` inside scoped styles ; it
duplicates the entire CSS bundle.

## Method 10 : Replace resolveConfig at Runtime

v3 :

```js
import resolveConfig from 'tailwindcss/resolveConfig'
import tailwindConfig from '../../tailwind.config.js'

const fullConfig = resolveConfig(tailwindConfig)
const red500 = fullConfig.theme.colors.red['500']
```

v4 :

```js
const styles = getComputedStyle(document.documentElement)
const red500 = styles.getPropertyValue('--color-red-500').trim()
```

For Node-side rendering where there is no DOM, read the CSS file
directly and parse the `:root { ... }` block with PostCSS, or expose
the values as a JSON file emitted by a build step.

## Method 11 : Dual-Version Monorepo Setup

Workspace layout :

```
monorepo/
  packages/
    ui-tokens/        # plain CSS variables, version-agnostic
      tokens.css
    ui-components/    # shared React/Vue components, utilities only
      src/
        button.tsx
  apps/
    app-v3/           # tailwindcss@^3
      tailwind.config.js
      src/
    app-v4/           # tailwindcss@^4
      src/app.css     # @import "tailwindcss"; @theme inline { ... }
```

`packages/ui-tokens/tokens.css` :

```css
:root {
  --color-brand-primary: #5b21b6;
  --color-brand-accent: #f59e0b;
  --spacing-128: 32rem;
}
```

`apps/app-v3/tailwind.config.js` reads tokens via `theme.extend.colors`
that references the CSS variable (`{ brand: { primary: 'var(--color-brand-primary)' } }`).

`apps/app-v4/src/app.css` :

```css
@import "tailwindcss";
@import "@my-org/ui-tokens/tokens.css";

@theme inline {
  --color-brand-primary: var(--color-brand-primary);
  --color-brand-accent: var(--color-brand-accent);
  --spacing-128: var(--spacing-128);
}
```

The same tokens reach both apps. Components in `ui-components` use
plain utility classes (`bg-brand-primary`) that resolve in both
versions.

## Method 12 : Visual Regression Workflow

Before merging the upgrade :

```bash
# pre-merge baseline
npx playwright test --project=visual --update-snapshots
git add tests/snapshots
git commit -m "chore: visual baseline pre v4 upgrade"

# merge upgrade
git merge chore/tailwind-v4

# post-merge diff
npx playwright test --project=visual
```

Each diff is either intentional (default-colour change) or a bug.
Inspect every file Playwright marks as different.
