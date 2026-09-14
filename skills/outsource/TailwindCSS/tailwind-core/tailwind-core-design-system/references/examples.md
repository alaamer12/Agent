# Tailwind CSS Design System: Working Examples

Every example is verified against the approved sources in SOURCES.md (2026-05-19).

## Example 1: Card Component Using Default Tokens

Works identically in v3.4 and v4.0+.

```html
<article class="max-w-md p-6 bg-white border border-slate-200 rounded-lg shadow-sm">
  <h2 class="text-2xl font-semibold text-slate-900">Design Token Card</h2>
  <p class="mt-2 text-sm text-slate-600">
    Every value here (max-w-md, p-6, border-slate-200, rounded-lg, shadow-sm,
    text-2xl, text-sm, text-slate-900, text-slate-600, mt-2) comes from the
    default theme. Zero custom tokens needed.
  </p>
  <button class="mt-4 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700">
    Action
  </button>
</article>
```

## Example 2: Defining a Custom Brand Palette

### v3.4 (tailwind.config.js)

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#eff6ff',
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
        '128': '32rem',
        '144': '36rem',
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

### v4.0+ (CSS @theme)

```css
@import "tailwindcss";

@theme {
  --color-brand-50:  oklch(0.97 0.014 254);
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

  /* spacing-128 / spacing-144 not needed : v4 generates p-128 dynamically */

  --text-display-1: 4.5rem;
  --text-display-1--line-height: 1.05;
  --text-display-1--letter-spacing: -0.02em;

  --breakpoint-3xl: 120rem;
}
```

Both produce the same utility classes : `bg-brand-500`, `p-128`, `text-display-1`, `3xl:flex`.

## Example 3: Opacity Modifier in Practice

Works identically in v3.4 and v4.0+.

```html
<!-- Layered glass-morphism panel -->
<div class="relative">
  <img src="/hero.jpg" class="absolute inset-0 w-full h-full object-cover">
  <div class="relative p-8 bg-white/70 backdrop-blur-md border border-white/40 rounded-2xl">
    <h2 class="text-2xl font-bold text-slate-900/90">Glass Panel</h2>
    <p class="mt-2 text-slate-700/80">
      The white background at 70% opacity, border at 40%, headline at 90%, body at 80%.
      Every layer composes through a single utility per element.
    </p>
  </div>
</div>

<!-- Arbitrary opacity for precise design tokens -->
<button class="bg-blue-600/[71.37%] text-white/[0.95]">Precise alpha</button>

<!-- Runtime CSS variable for theme-driven opacity (v4 syntax) -->
<div class="bg-cyan-400/(--my-glass-alpha)">Theme-driven</div>
```

## Example 4: Mobile-First Responsive Typography

Works identically in v3.4 and v4.0+.

```html
<h1 class="
  text-3xl    /* base : 30px (mobile) */
  sm:text-4xl /* sm+ : 36px (>= 640px) */
  md:text-5xl /* md+ : 48px (>= 768px) */
  lg:text-6xl /* lg+ : 60px (>= 1024px) */
  xl:text-7xl /* xl+ : 72px (>= 1280px) */
  font-bold
  tracking-tight
  text-slate-900
">
  Scales fluidly across breakpoints
</h1>

<!-- Override paired line-height for a tight headline -->
<h2 class="text-5xl leading-[1.05] tracking-tight">Compact display</h2>

<!-- Custom arbitrary size + line-height -->
<p class="text-[15.5px]/[1.4]">Body copy at exactly 15.5px with 1.4 leading</p>
```

## Example 5: Reading a Token at Runtime

### v3.4 (resolveConfig in JS)

```js
import resolveConfig from 'tailwindcss/resolveConfig'
import tailwindConfig from './tailwind.config.js'

const fullConfig = resolveConfig(tailwindConfig)

console.log(fullConfig.theme.colors.red[500])
// 'rgb(239 68 68)'

console.log(fullConfig.theme.fontSize.xl)
// ['1.25rem', { lineHeight: '1.75rem' }]

console.log(fullConfig.theme.screens.lg)
// '1024px'
```

### v4.0+ (getComputedStyle on CSS variables)

```js
const root = document.documentElement
const styles = getComputedStyle(root)

const red500 = styles.getPropertyValue('--color-red-500').trim()
// 'oklch(0.637 0.237 25.331)'

const textXl  = styles.getPropertyValue('--text-xl').trim()
const textXlLh = styles.getPropertyValue('--text-xl--line-height').trim()
// '1.25rem' and '1.75rem'

const breakpointLg = styles.getPropertyValue('--breakpoint-lg').trim()
// '64rem'
```

## Example 6: Token-Driven Dark Mode (v4)

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
<!-- Now bg-background and text-foreground work in both modes automatically -->
<body class="bg-background text-foreground">
  <main class="bg-muted text-muted-foreground p-6 rounded-xl">
    <button class="bg-primary text-primary-foreground px-4 py-2 rounded-md">
      Action
    </button>
  </main>
</body>
```

## Example 7: Custom Spacing Outside the Default Scale

### v4.0+ dynamic integer (preferred)

```html
<!-- p-17 = calc(0.25rem * 17) = 4.25rem = 68px -->
<div class="p-17 gap-43 mt-150">Spacing without arbitrary syntax</div>
```

### Arbitrary value (both versions)

```html
<div class="p-[13px] mt-[2.5vh] gap-[calc(1rem+2px)]">One-off values</div>
```

### CSS variable spacing

```html
<!-- v4 parens syntax -->
<div class="p-(--my-padding) gap-(--my-gap)">From runtime variables</div>

<!-- v3 brackets syntax -->
<div class="p-[var(--my-padding)] gap-[var(--my-gap)]">From runtime variables</div>
```

## Example 8: Restoring v3 Border + Ring Defaults in v4

The two most-cited v4 visual regressions (default border `currentColor` instead of `gray-200` ; default ring 1px instead of 3px). Add this once :

```css
@import "tailwindcss";

@layer base {
  *, ::before, ::after {
    border-color: var(--color-gray-200, currentColor);
  }
}

@theme {
  --default-ring-width: 3px;
  --default-ring-color: var(--color-blue-500);
}
```

Existing markup that relies on the v3 defaults (e.g. `border` without an explicit color) renders correctly again, while new code can opt into the v4 defaults by overriding per-element.
