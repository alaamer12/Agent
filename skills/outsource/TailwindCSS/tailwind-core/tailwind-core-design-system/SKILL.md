---
name: tailwind-core-design-system
description: >
  Use when designing or picking values for a Tailwind CSS project: choosing spacing units,
  color tokens, font sizes, breakpoints, or opacity. Use also when reading existing utility
  classes and needing to know whether a value comes from the default theme or a custom
  override. Prevents hardcoded colors, ad-hoc spacing arithmetic, mismatched type scales,
  and the common v3 to v4 color-format mistake (rgb/hsl vs oklch).
  Covers the default spacing scale (single base unit in v4, 32-step scale in v3), the
  default 22 color families (slate / gray / zinc / neutral / stone plus 17 chromatic
  families), the v4 oklch P3 wide-gamut color format vs the v3 rgb/hsl format, the
  text-xs through text-9xl type scale, the default breakpoint scale (sm 640, md 768,
  lg 1024, xl 1280, 2xl 1536), the v4 CSS-variable token model (--color-*, --spacing,
  --font-*, --text-*, --breakpoint-*, --radius-*, --shadow-*), the v3 tailwind.config.js
  theme object, and opacity modifier syntax (bg-red-500/50, text-white/[0.85],
  bg-cyan-400/(--my-alpha)).
  Keywords: design tokens, theme tokens, spacing scale, color palette, oklch, P3 colors,
  wide gamut, type scale, font size, line height, breakpoints, sm md lg xl 2xl, opacity
  modifier, alpha channel, CSS variables, custom properties, theme config, tailwind config,
  bg-red-500, text-white, p-4, m-8, gap-2, what spacing is p-4, what color is sky-500,
  default theme, brand colors, custom colors, design system, token, palette,
  why does p-17 work, dynamic spacing, oklch vs rgb, color format changed in v4.
license: MIT
compatibility: "Designed for Claude Code. Requires Tailwind CSS v3.4 or v4.0+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# Tailwind CSS Core: Design System

The design system is the **single source of truth** for every value Tailwind utilities produce. Spacing, colors, type, breakpoints, radii, shadows: all of them are tokens, and the markup expresses intent within that token system. Mastering the design system is the difference between writing fluent Tailwind and fighting it.

## Quick Reference

### Default tokens at a glance

| Domain : default scale : v4 namespace : v3 location |
|--|
| Spacing : `0`, `0.5`, `1`, `1.5`, `2`, `2.5`, `3`, `3.5`, `4`, `5`, `6`, `7`, `8`, `9`, `10`, `11`, `12`, `14`, `16`, `20`, `24`, `28`, `32`, `36`, `40`, `44`, `48`, `52`, `56`, `60`, `64`, `72`, `80`, `96` (in 0.25rem steps) : `--spacing` (single base unit, 0.25rem) : `theme.spacing.*` |
| Color : 22 families (5 grays + 17 chromatic), 11 shades each (50, 100, ..., 950) : `--color-{family}-{shade}` (oklch) : `theme.colors.*` (rgb/hsl/hex) |
| Type : `text-xs`, `text-sm`, `text-base`, `text-lg`, `text-xl`, `text-2xl` ... `text-9xl` : `--text-*` (+ `--text-*--line-height` pairing) : `theme.fontSize.*` |
| Breakpoints : `sm` 640, `md` 768, `lg` 1024, `xl` 1280, `2xl` 1536 (px) : `--breakpoint-*` : `theme.screens.*` |
| Opacity : 0, 5, 10, ..., 95, 100 (5% steps) plus arbitrary : modifier `/N` or `/[N%]` : modifier `/N` or `/[N%]` |

### Top-3 most-used token patterns

```html
<!-- Spacing token (works identically v3 + v4) -->
<div class="px-4 py-8 gap-6 mt-12">...</div>

<!-- Color token + opacity modifier (works identically v3 + v4) -->
<button class="bg-blue-600 text-white hover:bg-blue-700/90">...</button>

<!-- Breakpoint + type token (works identically v3 + v4, mobile-first) -->
<h1 class="text-2xl sm:text-3xl md:text-4xl lg:text-5xl">...</h1>
```

### Where the values live: v3 vs v4

| | v3.4 | v4.0+ |
|--|------|-------|
| Configuration surface | `tailwind.config.js` (JavaScript) | `@theme { ... }` in main CSS (CSS variables) |
| Auto-loaded | Yes (`tailwind.config.js` resolved by default) | **No** : not auto-loaded ; use `@config "./tailwind.config.js"` to opt-in legacy |
| Color format | `rgb()` / `hsl()` / hex | `oklch()` (P3 wide-gamut) |
| Spacing definition | 32 named entries in `theme.spacing` | Single `--spacing: 0.25rem` ; utilities desugar to `calc(var(--spacing) * N)` |
| Arbitrary integer spacing | Only via arbitrary syntax `p-[68px]` | **Native** : `p-17` generates `calc(var(--spacing) * 17)` automatically |
| Reading a token in JS | `import resolveConfig from 'tailwindcss/resolveConfig'` | `getComputedStyle(document.documentElement).getPropertyValue('--color-red-500')` |
| Theme function in CSS | `theme(colors.red.500)` | `theme(--color-red-500)` or `var(--color-red-500)` |

## Decision Trees

### Picking a spacing value

```
need padding/margin/gap?
├── matches default scale (0..96 in 0.25rem steps)?
│   └── ALWAYS use the scale token : `p-4`, `gap-6`, `mt-12`
├── needs exactly 1px?
│   └── ALWAYS use the `-px` variant : `p-px`, `mx-px`, `border-px`
├── v4 + integer outside scale (e.g. 17)?
│   └── ALWAYS use native dynamic : `p-17` (desugars to calc(--spacing * 17))
├── v3 + integer outside scale?
│   └── EITHER extend `theme.spacing` OR use arbitrary `p-[68px]`
├── value with units other than rem-multiples (e.g. `13px`, `2.5vh`, `calc(...)`)?
│   └── ALWAYS use arbitrary value : `p-[13px]`, `p-[calc(100%-2rem)]`
└── value from a runtime CSS variable?
    ├── v4 : `p-(--my-padding)` (parens syntax)
    └── v3 : `p-[var(--my-padding)]` (brackets syntax)
```

### Picking a color value

```
need a color?
├── matches default palette (slate/gray/zinc/neutral/stone + 17 chromatic, 11 shades)?
│   └── ALWAYS use the named token : `bg-blue-600`, `text-slate-900`, `border-red-500`
├── brand color or custom name?
│   ├── v4 : ALWAYS define `--color-brand-500: oklch(...)` in `@theme { ... }`
│   └── v3 : ALWAYS define `theme.extend.colors.brand[500]` in `tailwind.config.js`
├── needs transparency on a token color?
│   ├── named opacity step (5% increments) : ALWAYS use `/N` modifier (`bg-blue-600/50`)
│   └── arbitrary opacity : ALWAYS use `/[N%]` modifier (`bg-blue-600/[37.5%]`)
├── one-off color outside any palette?
│   └── ALWAYS use arbitrary : `bg-[#1da1f2]`, `text-[oklch(0.7_0.2_220)]`
└── color from a runtime CSS variable?
    ├── v4 : `bg-(--brand-bg)` (parens)
    └── v3 : `bg-[var(--brand-bg)]` (brackets)
```

### Picking a type token

```
need font size?
├── matches default scale (text-xs through text-9xl)?
│   └── ALWAYS use the named token : `text-base`, `text-2xl`, `text-7xl`
├── need custom size?
│   ├── v4 : ALWAYS define `--text-display: 4.5rem` and `--text-display--line-height: 1.05` in `@theme`
│   └── v3 : ALWAYS define `theme.extend.fontSize.display = ['4.5rem', { lineHeight: '1.05' }]`
└── need exact pixel size on the fly?
    └── arbitrary value : `text-[15px]`, `text-[14.5px]/[1.3]` (size/line-height)
```

### Picking a breakpoint

```
need responsive variant?
├── default scale fits (sm 640 / md 768 / lg 1024 / xl 1280 / 2xl 1536)?
│   └── ALWAYS use mobile-first prefix : `sm:`, `md:`, `lg:`, `xl:`, `2xl:`
├── need a custom breakpoint?
│   ├── v4 : ALWAYS define `--breakpoint-3xl: 120rem` in `@theme` (auto-generates `3xl:*`)
│   └── v3 : ALWAYS define `theme.extend.screens['3xl'] = '120rem'`
├── need an upper-bound (desktop-first override)?
│   └── ALWAYS use `max-{breakpoint}:` : `max-md:hidden` (since v3.4)
├── need an arbitrary pixel value?
│   └── arbitrary breakpoint : `min-[1440px]:flex`, `max-[640px]:hidden`
└── need a container-query (parent-width-aware) instead of viewport?
    └── ALWAYS mark `class="@container"` on parent, then `@sm:*`, `@md:*` on children
```

## Patterns

### Pattern 1: Defining tokens (v3 vs v4)

This is the highest-divergence area between v3 and v4. NEVER share one snippet ; use dual columns.

| v3.4 : `tailwind.config.js` | v4.0+ : `@theme` in main CSS |
|-----------------------------|-------------------------------|
| ```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eff6ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
      },
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },
      fontSize: {
        'display': ['4.5rem', { lineHeight: '1.05' }],
      },
      screens: {
        '3xl': '120rem',
      },
    },
  },
}
``` | ```css
@import "tailwindcss";

@theme {
  --color-brand-50: oklch(0.97 0.014 254);
  --color-brand-500: oklch(0.65 0.196 254);
  --color-brand-900: oklch(0.34 0.146 264);

  --spacing: 0.25rem;
  /* v4 generates p-128 automatically because of dynamic spacing */

  --text-display: 4.5rem;
  --text-display--line-height: 1.05;

  --breakpoint-3xl: 120rem;
}
``` |

Both generate the same utility class names (`bg-brand-500`, `p-128`, `text-display`, `3xl:flex`). The mechanism, the file location, and the value format all differ.

### Pattern 2: Using the opacity modifier

The opacity modifier `/N` is one of the most powerful and most misunderstood features. It works on **every** color-consuming utility.

```html
<!-- Named opacity step (5% increments from 0 to 100) -->
<div class="bg-blue-600/0">...</div>      <!-- fully transparent -->
<div class="bg-blue-600/10">...</div>     <!-- 10% opacity -->
<div class="bg-blue-600/50">...</div>     <!-- 50% opacity (the most common) -->
<div class="bg-blue-600/100">...</div>    <!-- fully opaque (same as no modifier) -->

<!-- Arbitrary opacity -->
<div class="bg-pink-500/[71.37%]">...</div>
<div class="text-white/[0.85]">...</div>    <!-- decimal fraction also valid -->

<!-- CSS variable opacity -->
<div class="bg-cyan-400/(--my-alpha)">...</div>   <!-- v4 parens syntax -->
<div class="bg-cyan-400/[var(--my-alpha)]">...</div> <!-- v3 brackets syntax -->

<!-- Works on every color utility, not just bg -->
<div class="text-slate-900/60 border-red-500/30 ring-blue-600/50 fill-emerald-500/80">
```

### Pattern 3: Inspecting a token at runtime

| v3.4 (JavaScript) | v4.0+ (CSS variables) |
|-------------------|------------------------|
| ```js
import resolveConfig from 'tailwindcss/resolveConfig'
import tailwindConfig from './tailwind.config.js'

const fullConfig = resolveConfig(tailwindConfig)
const red500 = fullConfig.theme.colors.red[500]
// => 'rgb(239 68 68)'
``` | ```js
// resolveConfig is REMOVED in v4 ; tokens are CSS variables.
const styles = getComputedStyle(document.documentElement)
const red500 = styles.getPropertyValue('--color-red-500').trim()
// => 'oklch(0.637 0.237 25.331)'
``` |

In v4, this is the **only** runtime API for token lookup. The build no longer emits a JS-importable config object.

### Pattern 4: oklch P3 wide-gamut colors (v4-only)

v4 defines every default color in the `oklch()` color space, which targets the **P3 wide-gamut** display profile. On standard sRGB monitors, oklch values fall back to the nearest sRGB equivalent ; on P3 monitors (most modern phones, MacBooks since 2016, most external monitors since 2020), the colors render with measurably higher saturation, especially in the orange/red/violet/cyan ranges.

Why this matters for skills authoring custom colors:

```css
@theme {
  /* GOOD : oklch produces consistent perceptual lightness across hues */
  --color-brand-500: oklch(0.65 0.196 254);
  --color-brand-600: oklch(0.55 0.196 254);  /* perceptually one step darker */

  /* TOLERATED : hex / rgb still parse fine in @theme, but lose P3 reach */
  --color-legacy: #3b82f6;

  /* TOLERATED : hsl maps cleanly but is not perceptually uniform */
  --color-alt: hsl(217 91% 60%);
}
```

ALWAYS prefer `oklch()` in v4 ; the entire default palette uses it, and mixing formats produces inconsistent perceived contrast.

### Pattern 5: Reset, override, or extend

| Goal | v3.4 | v4.0+ |
|------|------|-------|
| Add to defaults | `theme.extend.{namespace}` | `@theme { --{namespace}-newkey: ... }` |
| Replace entire namespace | `theme.{namespace}` (no `.extend`) | `@theme { --{namespace}-*: initial; --{namespace}-key1: ... }` |
| Wipe ALL defaults | Replace all `theme.*` keys manually | `@theme { --*: initial; --spacing: 0.25rem; ... }` |
| Reference another variable | Compute in JS | `@theme inline { --color-brand: var(--my-brand); }` |

The `@theme inline` modifier in v4 is the escape hatch for runtime-resolved tokens (e.g. swapping a CSS variable from JS or a `[data-theme]` attribute).

### Pattern 6: Type scale with line-height pairing

Default v4 line-heights are paired to font sizes (matching v3 `theme.fontSize` tuples). This means `text-base` automatically applies `line-height: 1.5` and `text-2xl` automatically applies `line-height: 2 / 1.5`.

```html
<!-- ALWAYS rely on the paired line-height for body text -->
<p class="text-base">Body copy gets the right leading automatically.</p>

<!-- Override paired line-height with a separate utility when needed -->
<p class="text-2xl leading-tight">Headline tightened from default.</p>

<!-- Set both inline via arbitrary value -->
<p class="text-[14.5px]/[1.3]">Custom size with custom leading.</p>
```

In v4 the paired leading is set via the companion variable `--text-{name}--line-height` (see Pattern 1).

### Pattern 7: Token-driven dark mode

The design system carries through to dark mode by **changing the variable values**, not by rewriting utilities. The recommended pattern in v4 :

```css
@import "tailwindcss";
@custom-variant dark (&:where(.dark, .dark *));

@theme {
  --color-background: oklch(1 0 0);
  --color-foreground: oklch(0.15 0.02 270);
}

@layer base {
  .dark {
    --color-background: oklch(0.18 0.02 270);
    --color-foreground: oklch(0.95 0.01 270);
  }
}
```

Now `bg-background` and `text-foreground` work in both modes without `dark:` variants on every element.

## Reference Links

- `references/methods.md` : complete token namespace reference (every `--*-*` and its `theme.*` equivalent), full default scales for spacing / color / type / breakpoints.
- `references/examples.md` : working code examples for v3 and v4 across spacing, colors, type, breakpoints, opacity, theme overrides.
- `references/anti-patterns.md` : real anti-patterns mined from GitHub issues and the upgrade guide (dynamic class strings, oklch vs rgb mismatch, theme() dot-notation in v4, wrong arbitrary syntax).

## Verified Sources

All content verified against the following SOURCES.md-approved URLs :

- https://tailwindcss.com/docs/colors (v4 color palette + oklch format + opacity modifier)
- https://tailwindcss.com/docs/theme (v4 theme variable namespaces and `@theme` syntax)
- https://tailwindcss.com/docs/padding (v4 spacing scale + dynamic integer utilities)
- https://v3.tailwindcss.com/docs/customizing-colors (v3 color palette + tailwind.config.js theme.colors format)
- https://v3.tailwindcss.com/docs/configuration (v3 theme object structure)
- https://tailwindcss.com/docs/upgrade-guide (v3 to v4 breaking changes including theme function + resolveConfig removal)
- https://tailwindcss.com/blog/tailwindcss-v4 (oklch + P3 wide-gamut introduction)

Last verified : 2026-05-19 (Tailwind CSS v4.x current).
