# Worked examples

Each example is complete enough to paste and read. Version notes are stated where the output
differs; anything labelled "identical in v3.4 and v4" needs no translation.

## 1. Card component on default tokens only

Identical in v3.4 and v4.

```html
<article class="max-w-md p-6 bg-white border border-slate-200 rounded-lg shadow-sm">
  <h2 class="text-2xl font-semibold text-slate-900">Design Token Card</h2>
  <p class="mt-2 text-sm text-slate-600">
    Every value here (max-w-md, p-6, border-slate-200, rounded-lg, shadow-sm, text-2xl, text-sm,
    text-slate-900, text-slate-600, mt-2) comes from the default theme. Zero custom tokens.
  </p>
  <button class="mt-4 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700">
    Action
  </button>
</article>
```

Audit a component like this by naming the token behind each value. A value you cannot name is
either an arbitrary leak or a token the theme is missing.

## 2. Full brand palette, both versions

v3.4 — `tailwind.config.js`:

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
      },
      spacing: {
        128: '32rem',
        144: '36rem',
      },
      fontSize: {
        'display-1': ['4.5rem', { lineHeight: '1.05', letterSpacing: '-0.02em' }],
      },
      screens: {
        '3xl': '120rem',
      },
    },
  },
}
```

v4.0+ — `@theme` in the entry CSS:

```css
@import "tailwindcss";

@theme {
  --color-brand-50: oklch(0.97 0.014 254);
  --color-brand-100: oklch(0.93 0.038 254);
  --color-brand-200: oklch(0.87 0.075 254);
  --color-brand-300: oklch(0.78 0.123 254);
  --color-brand-400: oklch(0.69 0.171 254);
  --color-brand-500: oklch(0.65 0.196 254);
  --color-brand-600: oklch(0.55 0.196 254);
  --color-brand-700: oklch(0.46 0.171 254);
  --color-brand-800: oklch(0.39 0.146 264);
  --color-brand-900: oklch(0.34 0.146 264);
  --color-brand-950: oklch(0.21 0.097 269);

  /* no spacing entries needed: p-128 and p-144 generate from --spacing */

  --text-display-1: 4.5rem;
  --text-display-1--line-height: 1.05;
  --text-display-1--letter-spacing: -0.02em;

  --breakpoint-3xl: 120rem;
}
```

Both emit `bg-brand-500`, `p-128`, `text-display-1`, `3xl:flex`. Two things to notice in the v4
column: the hue rotates slightly across the range (254 → 264 → 269) because constant chroma at low
lightness shifts perception, and the spacing block disappears entirely.

## 3. Layered opacity

Identical in v3.4 and v4.

```html
<div class="relative">
  <img src="/hero.jpg" class="absolute inset-0 h-full w-full object-cover" alt="">
  <div class="relative rounded-2xl border border-white/40 bg-white/70 p-8 backdrop-blur-md">
    <h2 class="text-2xl font-bold text-slate-900/90">Glass Panel</h2>
    <p class="mt-2 text-slate-700/80">
      Background at 70%, border at 40%, headline at 90%, body at 80%. Every layer composes
      through one utility per element.
    </p>
  </div>
</div>

<!-- arbitrary alpha where the design specifies an exact number -->
<button class="bg-blue-600/[71.37%] text-white/[0.95]">Precise alpha</button>

<!-- alpha owned by the theme at runtime (v4 syntax) -->
<div class="bg-cyan-400/(--my-glass-alpha)">Theme-driven</div>
```

Opacity is a modifier on the color token, never a separate utility. A design system that specifies
`rgba(255,255,255,0.7)` is still specifying the `white` token plus `70`.

## 4. Mobile-first responsive typography

Identical in v3.4 and v4.

```html
<h1 class="text-3xl font-bold tracking-tight text-slate-900
           sm:text-4xl
           md:text-5xl
           lg:text-6xl
           xl:text-7xl">
  Scales up with the viewport
</h1>

<!-- base is the phone design; each prefix overrides upward -->
<h1 class="text-xl sm:text-2xl md:text-3xl">Correct direction</h1>

<!-- explicit upper bound when the design really is phone-only -->
<h1 class="max-sm:text-xl sm:text-3xl">xl below 640px, 3xl from 640px up</h1>

<!-- leading overridden on a display size -->
<h2 class="text-5xl leading-[1.05] tracking-tight">Compact display</h2>

<!-- exact size and exact leading, one-off -->
<p class="text-[15.5px]/[1.4]">Body at 15.5px with 1.4 leading</p>
```

## 5. Reading a token from JavaScript

v3.4 — the resolved config object:

```js
import resolveConfig from 'tailwindcss/resolveConfig'
import tailwindConfig from './tailwind.config.js'

const fullConfig = resolveConfig(tailwindConfig)

fullConfig.theme.colors.red[500]   // 'rgb(239 68 68)'
fullConfig.theme.fontSize.xl       // ['1.25rem', { lineHeight: '1.75rem' }]
fullConfig.theme.screens.lg        // '1024px'
```

v4.0+ — the computed CSS variables:

```js
const styles = getComputedStyle(document.documentElement)

styles.getPropertyValue('--color-red-500').trim()          // 'oklch(0.637 0.237 25.331)'
styles.getPropertyValue('--text-xl').trim()                // '1.25rem'
styles.getPropertyValue('--text-xl--line-height').trim()   // '1.75rem'
styles.getPropertyValue('--breakpoint-lg').trim()          // '64rem'
```

`trim()` the result: the declaration's leading whitespace survives in the variable value. Read
tokens once and cache per theme change; do not query inside a render loop.

## 6. Token-driven dark mode (v4)

```css
@import "tailwindcss";
@custom-variant dark (&:where(.dark, .dark *));

@theme {
  --color-background: oklch(1 0 0);
  --color-foreground: oklch(0.15 0.02 270);
  --color-muted: oklch(0.96 0.005 250);
  --color-muted-foreground: oklch(0.55 0.02 270);
  --color-primary: oklch(0.65 0.196 254);
  --color-primary-foreground: oklch(0.98 0.005 254);
}

@layer base {
  .dark {
    --color-background: oklch(0.18 0.02 270);
    --color-foreground: oklch(0.95 0.01 270);
    --color-muted: oklch(0.25 0.015 270);
    --color-muted-foreground: oklch(0.7 0.02 270);
    --color-primary: oklch(0.75 0.18 254);
    --color-primary-foreground: oklch(0.15 0.04 254);
  }
}
```

```html
<body class="bg-background text-foreground">
  <main class="rounded-xl bg-muted p-6 text-muted-foreground">
    <button class="rounded-md bg-primary px-4 py-2 text-primary-foreground">Action</button>
  </main>
</body>
```

Roles flip; utilities stay. The same file works for a third or tenth theme by adding one more block
that reassigns the same variables, and `[data-theme="high-contrast"]` is a better selector than a
second set of utility names.

## 7. Spacing outside the default scale

v4 dynamic integer, preferred when the value is a multiple of the base unit:

```html
<!-- p-17 = calc(0.25rem * 17) = 4.25rem = 68px -->
<div class="p-17 gap-43 mt-150">No arbitrary syntax, no config entry</div>
```

Arbitrary value, both versions, when the unit is not the base unit:

```html
<div class="mt-[2.5vh] gap-[calc(1rem+2px)] p-[13px]">One-off geometry</div>
```

Runtime variable:

```html
<!-- v4 -->
<div class="p-(--my-padding) gap-(--my-gap)"></div>
<!-- v3 (and still valid in v4) -->
<div class="p-[var(--my-padding)] gap-[var(--my-gap)]"></div>
```

Decision order: scale token → extended token (if it repeats) → v4 dynamic integer → arbitrary value
→ runtime variable. Reaching for `p-[68px]` in v4 when `p-17` exists is the common slip; it hides
the value from every audit that greps the theme.

## 8. Restoring old visual defaults after an upgrade

Out of scope here: default border and ring behavior across versions is catalogued by the `migration`
module ([../../migration/method.md](../../migration/method.md)). From the token side the durable
answer is the same as everywhere else in this module — declare the color you want
(`border-gray-200`, `ring-blue-500`) instead of relying on an unnamed default.
