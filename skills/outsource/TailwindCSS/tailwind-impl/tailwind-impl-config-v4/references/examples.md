# tailwind-impl-config-v4 : Examples

End-to-end v4 configuration examples.

## Minimal Setup

```css
/* src/app.css */
@import "tailwindcss";
```

Loaded once, the entire framework is active. No JS config. No PostCSS plugin chain. Done.

## Production-Grade `app.css`

```css
@import "tailwindcss";

/* Load legacy plugins from npm */
@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";

/* Design tokens */
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

/* Custom dark-mode trigger */
@custom-variant dark (&:where(.dark, .dark *));

/* Additional source paths */
@source "../packages/ui/src/**/*.{ts,tsx,vue,svelte}";

/* Safelist runtime-generated classes */
@source inline("bg-{red,blue,green}-{500,700}");

/* Custom utility */
@utility tab-* {
  tab-size: --value(integer);
}

/* Custom variant */
@custom-variant pointer-coarse (@media (pointer: coarse));

/* Base typography */
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

## Vite Integration

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

## PostCSS Integration

```js
// postcss.config.js
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
```

## Next.js (App Router)

```css
/* app/globals.css */
@import "tailwindcss";

@theme {
  --font-sans: var(--font-geist-sans);
}
```

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

## Astro

```ts
// astro.config.ts
import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  vite: { plugins: [tailwindcss()] },
});
```

## Scoped Stylesheet (Vue SFC)

```vue
<template>
  <button class="btn">Click me</button>
</template>

<style scoped>
@reference "../app.css";

.btn {
  @apply px-4 py-2 bg-blue-500 text-white rounded;
}
</style>
```

Without `@reference`, v4 throws "Cannot apply unknown utility class". The reference imports theme + custom utilities without duplicating CSS output.

## Scoped Stylesheet (Svelte)

```svelte
<button class="btn">Click me</button>

<style>
@reference "../app.css";

.btn {
  @apply px-4 py-2 bg-blue-500 text-white rounded;
}
</style>
```

## CSS Modules

```css
/* Button.module.css */
@reference "../app.css";

.btn {
  @apply px-4 py-2 bg-blue-500 text-white rounded;
}
```

## Custom Color Palette Replacing Defaults

```css
@import "tailwindcss";

@theme {
  --color-*: initial;                    /* drop all default colours */

  --color-primary-50: oklch(0.97 0.02 250);
  --color-primary-500: oklch(0.55 0.20 250);
  --color-primary-900: oklch(0.25 0.15 252);

  --color-neutral-50: oklch(0.98 0 0);
  --color-neutral-900: oklch(0.18 0 0);
}
```

## Custom Utility with Theme Lookup

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

Usage : `<pre class="tab-4">`, `<pre class="tab-github">`.

## Combined Functional Utility

```css
/* Matches text-lg, text-lg/6, text-[14px], text-[14px]/6 */
@utility text-* {
  font-size: --value(--text-*, [length]);
  line-height: --modifier(--leading-*, [length], [*]);
}
```

## Brace-Expansion Safelist Patterns

```css
@source inline("bg-{red,green,blue}-500");                      /* 3 classes */
@source inline("p-{1..12}");                                    /* 12 classes */
@source inline("opacity-{0..100..10}");                         /* 11 classes */
@source inline("{hover:,focus:,}bg-{red,blue}-{50,{100..900..100},950}");
```

## Loading v3 Config (Incremental Migration)

```css
@import "tailwindcss";
@config "../tailwind.config.js";

/* Override or augment specific tokens directly in CSS */
@theme {
  --color-brand-500: oklch(0.65 0.18 252);
}
```

## Disabling Automatic Content Detection

```css
@import "tailwindcss";
@source none;
@source "./components/**/*.tsx";    /* explicit allow-list only */
```

Used when working in a monorepo with strict isolation rules, or in storybook / sandbox environments.

## Verified Sources

- https://tailwindcss.com/docs/installation/using-vite
- https://tailwindcss.com/docs/installation/using-postcss
- https://tailwindcss.com/docs/installation/framework-guides/nextjs
- https://tailwindcss.com/docs/theme
- https://tailwindcss.com/docs/detecting-classes-in-source-files

Last verified : 2026-05-19.
