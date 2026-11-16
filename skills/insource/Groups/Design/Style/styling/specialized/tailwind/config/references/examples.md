# config — examples: v4 setup and custom-CSS integration

Copy-paste shapes for the entry stylesheet, the theme/utility directives, and the `@apply` /
`@layer` / `@reference` integration surface. Rules and syntax: `methods.md`. Failures:
`anti-patterns.md`.

---

## 1. Minimal entry

```css
/* src/app.css */
@import "tailwindcss";
```

Imported once and the framework is active: reset, default theme variables, utilities. No JS config,
no PostCSS plugin chain.

## 2. Production-grade `app.css`

```css
@import "tailwindcss";

/* Legacy JS plugins from npm */
@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";

/* Design tokens — everything below consumes these */
@theme {
  --color-brand-50: oklch(0.97 0.02 250);
  --color-brand-500: oklch(0.65 0.18 252);
  --color-brand-900: oklch(0.30 0.10 254);

  --font-display: "Inter Variable", system-ui, sans-serif;

  --breakpoint-xs: 24rem;
  --breakpoint-3xl: 120rem;

  --spacing-128: 32rem;
  --radius-card: 1.25rem;
}

/* Class-based dark mode */
@custom-variant dark (&:where(.dark, .dark *));
@custom-variant pointer-coarse (@media (pointer: coarse));

/* Content from a sibling package */
@source "../packages/ui/src/**/*.{ts,tsx,vue,svelte}";

/* Names that exist only at runtime (grammar: the dynamic-classes module) */
@source inline("bg-brand-500 bg-brand-900");

/* Custom utility */
@utility tab-* {
  tab-size: --value(integer);
}

/* Element defaults */
@layer base {
  h1 { font-family: var(--font-display); font-size: var(--text-4xl); }
}

/* Component recipes */
@layer components {
  .card {
    @apply rounded-card bg-white p-6 shadow-md;
  }
}
```

Every token above is usable as a utility (`bg-brand-500`, `rounded-card`, `p-128`, `xs:`, `3xl:`) and
as a variable (`var(--color-brand-500)`). `@layer components` placement is what lets a call site
write `class="card p-4"` and win.

## 3. Custom palette replacing the defaults

```css
@import "tailwindcss";

@theme {
  --color-*: initial;                    /* drop every default colour */

  --color-primary-50: oklch(0.97 0.02 250);
  --color-primary-500: oklch(0.55 0.20 250);
  --color-primary-900: oklch(0.25 0.15 252);

  --color-neutral-50: oklch(0.98 0 0);
  --color-neutral-900: oklch(0.18 0 0);
}
```

Without the `initial` reset, the default colours keep generating and stay usable in markup, so a
"brand-only" palette is not enforced by anything.

## 4. Theme-valued token, inlined and static

```css
@theme {
  --font-inter: "Inter Variable", sans-serif;
}

@theme inline {
  --font-sans: var(--font-inter);        /* resolved at build, no dangling reference */
}

@theme static {
  --color-read-from-js: var(--color-primary-500);   /* survives pruning for getComputedStyle */
}
```

## 5. Custom utility reading a theme namespace

```css
@theme {
  --tab-size-2: 2;
  --tab-size-4: 4;
  --tab-size-github: 8;
}

@utility tab-* {
  tab-size: --value(--tab-size-*);
}
```

Usage: `<pre class="tab-4">`, `<pre class="tab-github">`. Swap the helper for `--value(integer)` to
take plain numbers instead of keys.

## 6. Combined functional utility

```css
/* matches text-lg, text-lg/6, text-[14px], text-[14px]/6 */
@utility text-* {
  font-size: --value(--text-*, [length]);
  line-height: --modifier(--leading-*, [length], [*]);
}
```

## 7. Content scope

```css
@source "../packages/ui/src/**/*.{html,ts,tsx,vue,svelte}";
@source "../node_modules/@my-org/ui-lib";         /* node_modules is skipped by default */
@source not "../src/legacy";
@source not "../tests/**/*.fixture.html";
```

Strict isolation for a monorepo, storybook, or sandbox:

```css
@import "tailwindcss";
@source none;
@source "./components/**/*.tsx";                  /* explicit allow-list only */
```

Class names produced from runtime data are a separate question — the `dynamic-classes` module owns
`@source inline` expansion and the interpolation fixes.

## 8. Button component recipe

```css
@layer components {
  .btn {
    @apply inline-flex items-center justify-center rounded
           px-4 py-2 font-medium transition;
  }

  .btn-primary {
    @apply inline-flex items-center justify-center rounded
           px-4 py-2 font-medium transition
           bg-blue-500 text-white hover:bg-blue-600;
  }

  .btn-secondary {
    @apply inline-flex items-center justify-center rounded
           px-4 py-2 font-medium transition
           bg-gray-200 text-gray-900 hover:bg-gray-300;
  }
}
```

`.btn-primary { @apply btn bg-blue-500; }` is NOT valid — `@apply` takes Tailwind utilities, not
your own class names (`The btn class does not exist`). Repeat the shared utilities, factor the rule
through a Sass mixin or PostCSS partial, or extract a component. Only reach for the indirection
after measuring that the duplication actually costs something.

## 9. Base layer element defaults

```css
@layer base {
  body { @apply bg-gray-50 text-gray-900 antialiased; }

  h1 { @apply text-4xl font-bold tracking-tight; }
  h2 { @apply text-3xl font-semibold; }
  h3 { @apply text-2xl font-semibold; }

  a { @apply text-blue-600 underline underline-offset-2; }
  a:hover { @apply text-blue-800; }
}
```

Base rules hit every matching element with no class. `base` is for "every `h1` looks like this"; an
exception gets a class override in markup, not a `:not(.no-style)` carve-out.

## 10. Single-purpose helper in the utilities layer

```css
@layer utilities {
  .text-shadow-sm   { text-shadow: 0 1px 2px rgb(0 0 0 / 0.1); }
  .text-shadow-md   { text-shadow: 0 2px 4px rgb(0 0 0 / 0.15); }
  .text-shadow-none { text-shadow: none; }
}
```

```html
<p class="text-shadow-sm">Subtle shadow</p>
```

In v4 the modern equivalent is `@utility text-shadow-sm { ... }`, which additionally makes the class
variant-able (`hover:text-shadow-md`). Both work; `@utility` is preferred for new code.

## 11. Third-party widget override

```css
@layer components {
  .react-select__control { @apply rounded border border-gray-300 px-2 py-1 shadow-sm; }
  .react-select__menu    { @apply rounded border border-gray-200 bg-white shadow-lg; }
  .DocSearch-Button      { @apply rounded border border-gray-200 bg-white px-3 py-1.5; }
}
```

The library owns the markup, so component extraction is impossible; `@apply` bridges your tokens into
their selectors. ALWAYS scope to known library class names; NEVER a broad selector such as
`* { @apply ... }`.

## 12. Arbitrary values, variants, group/peer

```css
@layer components {
  .ratio-12-5 { @apply aspect-[12/5]; }
  .h-banner   { @apply h-[42vh]; }

  .input {
    @apply w-full rounded border border-gray-300 px-3 py-2
           focus:border-blue-500 focus:ring-2 focus:ring-blue-500;
  }

  .menu-item      { @apply flex items-center gap-2 px-3 py-2; }
  .menu-item-icon { @apply text-gray-500 group-hover:text-blue-500; }
}
```

Arbitrary values and variants are written exactly as in HTML. `group-hover:*` still needs the
`group` marker in markup — `@apply group` copies nothing useful:

```html
<a class="menu-item group" href="/">
  <svg class="menu-item-icon">...</svg>
  <span>Home</span>
</a>
```

## 13. Importance inside `@apply`

v3 (keyword form; Sass needs interpolation):

```css
.print-only { @apply block !important; }
@media not print { .print-only { @apply hidden !important; } }
```

```scss
.btn { @apply font-bold #{!important}; }
```

v4 (trailing bang on the utility, no interpolation needed):

```css
.print-only { @apply block!; }
@media not print { .print-only { @apply hidden!; } }
.btn { @apply rounded font-bold! bg-blue-500; }   /* only font-bold forced */
```

Prefer layer order and specificity; `!` is for utility-overriding-utility only.

## 14. Vue SFC scoped `@apply` (v4)

```vue
<script setup lang="ts">
defineProps<{ title: string }>()
</script>

<template>
  <div class="card">
    <h3 class="card-title">{{ title }}</h3>
    <div class="card-body"><slot /></div>
  </div>
</template>

<style scoped>
@reference "../app.css";

.card       { @apply rounded-lg border border-gray-200 bg-white p-4 shadow-sm; }
.card-title { @apply mb-2 text-lg font-semibold; }
.card-body  { @apply text-sm text-gray-700; }
</style>
```

`@reference` is the first non-whitespace line and its path resolves relative to the SFC. Without it
the build fails with `Cannot apply unknown utility class`.

## 15. Svelte scoped `@apply` (v4)

```svelte
<script lang="ts">
  let { children, variant = "primary" } = $props()
</script>

<button class="btn btn-{variant}">
  {@render children()}
</button>

<style>
  @reference "../app.css";

  .btn          { @apply inline-flex items-center rounded px-4 py-2 font-medium; }
  .btn-primary  { @apply bg-blue-500 text-white hover:bg-blue-600; }
  .btn-secondary { @apply bg-gray-200 text-gray-900 hover:bg-gray-300; }
</style>
```

`btn-{variant}` is an interpolated name the scanner cannot see: the fix (a literal union, a mapping,
or a safelist) is the `dynamic-classes` module's call, not something the scoped block solves.

## 16. CSS modules (v4)

```css
/* src/components/Button.module.css */
@reference "../app.css";

.button   { @apply rounded bg-blue-500 px-4 py-2 text-white; }
.disabled { @apply cursor-not-allowed opacity-50; }
```

```tsx
import styles from "./Button.module.css";

export function Button({ disabled }: { disabled?: boolean }) {
  return (
    <button className={`${styles.button} ${disabled ? styles.disabled : ""}`}>
      Save
    </button>
  );
}
```

Same rule as an SFC block: the module is compiled in isolation, so it needs its own `@reference`.

## 17. `@theme` token consumed by `@apply`

```css
@import "tailwindcss";

@theme {
  --color-brand-500: oklch(0.6 0.18 250);
}

@layer components {
  .badge-brand {
    @apply rounded-full bg-brand-500 px-2 py-0.5 text-xs text-white;
  }
}
```

The token generates `bg-brand-500`, and the generated utility is then a legal `@apply` argument in
the same file. In a scoped block the same is true only after `@reference`.

## 18. Extract a component instead of `@apply`

`@apply` route:

```css
.btn-primary { @apply rounded bg-blue-500 px-4 py-2 text-white; }
```

```tsx
<button className="btn-primary">Save</button>
```

Preferred route in a component framework:

```tsx
function Button({
  children,
  variant = "primary",
}: {
  children: ReactNode;
  variant?: "primary" | "secondary";
}) {
  const base = "rounded px-4 py-2 font-medium";
  const variants = {
    primary: "bg-blue-500 text-white hover:bg-blue-600",
    secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300",
  } as const;

  return <button className={`${base} ${variants[variant]}`}>{children}</button>;
}
```

```tsx
<Button>Save</Button>
<Button variant="secondary">Cancel</Button>
```

The component keeps the utilities visible at the call site, type-checks variant names, composes with
a caller's `className`, and deletes the CSS file.

## 19. Single use — `@apply` is wrong

```css
/* WRONG: one rule, one consumer */
.welcome-heading { @apply text-4xl font-bold; }
```

```html
<h1 class="welcome-heading">Welcome</h1>
```

```html
<h1 class="text-4xl font-bold">Welcome</h1>
```

A one-use `@apply` trades two utility names for a CSS rule plus a name to remember. Extract only once
the class genuinely repeats (three or more call sites is the working threshold).

## 20. Plugin ordering with the layers

```css
/* app.css */
@import "tailwindcss";
@plugin "./plugins/typography.js";
@plugin "./plugins/btn-override.js";     /* registered last, so it wins */
```

```js
// plugins/btn-override.js — the v3 JS plugin API still loads under v4
import plugin from "tailwindcss/plugin";

export default plugin(({ addComponents }) => {
  addComponents({
    ".prose .btn": {
      "@apply bg-purple-500 text-white": {},
    },
  });
});
```

Both land in `@layer components`; registration order decides which `.btn` survives. To override a
plugin class, register the override AFTER the source plugin. The same rule applies inside the
`plugins` array of a config loaded through `@config`.

## 21. Legacy JS config while migrating

```css
@import "tailwindcss";
@config "../tailwind.config.js";

/* Augment in CSS — but never the same token the JS config already defines */
@theme {
  --color-brand-500: oklch(0.65 0.18 252);
}
```

One place per token. Categories still living in JS stay in JS until moved, and the move deletes the
JS entry in the same commit. Which v3 options `@config` ignores is documented in the `migration`
module.

## 22. Framework wiring

Vite:

```ts
// vite.config.ts
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [tailwindcss()],
});
```

```css
/* src/app.css */
@import "tailwindcss";
@source "../packages/**/*.{ts,tsx,vue}";
```

PostCSS:

```js
// postcss.config.js
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
```

Next.js (App Router) — the theme reads a font variable supplied by the layout:

```css
/* app/globals.css */
@import "tailwindcss";

@theme {
  --font-sans: var(--font-geist-sans);
}
```

`@theme inline` is the correct form once the font variable is defined elsewhere and the reference
must resolve at build; see `methods.md` section 4.

```ts
// app/layout.tsx
import "./globals.css";
import { GeistSans } from "geist/font/sans";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={GeistSans.className}>
      <body>{children}</body>
    </html>
  );
}
```

Astro:

```ts
// astro.config.ts
import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  vite: { plugins: [tailwindcss()] },
});
```
