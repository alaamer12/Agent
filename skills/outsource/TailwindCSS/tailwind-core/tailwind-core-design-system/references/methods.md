# Tailwind CSS Design System: Complete Token Reference

Verified against Tailwind CSS docs (2026-05-19).

## Default Spacing Scale

Single scale used by every spacing utility (`p-*`, `px-*`, `py-*`, `m-*`, `gap-*`, `space-x-*`, `space-y-*`, `top-*`, `inset-*`, `w-*`, `h-*`, `min-w-*`, `max-w-*`, `min-h-*`, `max-h-*`, `size-*`, `translate-*`, `scroll-m-*`, `scroll-p-*`).

| Token | rem | px |
|-------|-----|----|
| `0` | 0 | 0 |
| `px` | 1px | 1px (literal pixel) |
| `0.5` | 0.125rem | 2px |
| `1` | 0.25rem | 4px |
| `1.5` | 0.375rem | 6px |
| `2` | 0.5rem | 8px |
| `2.5` | 0.625rem | 10px |
| `3` | 0.75rem | 12px |
| `3.5` | 0.875rem | 14px |
| `4` | 1rem | 16px |
| `5` | 1.25rem | 20px |
| `6` | 1.5rem | 24px |
| `7` | 1.75rem | 28px |
| `8` | 2rem | 32px |
| `9` | 2.25rem | 36px |
| `10` | 2.5rem | 40px |
| `11` | 2.75rem | 44px |
| `12` | 3rem | 48px |
| `14` | 3.5rem | 56px |
| `16` | 4rem | 64px |
| `20` | 5rem | 80px |
| `24` | 6rem | 96px |
| `28` | 7rem | 112px |
| `32` | 8rem | 128px |
| `36` | 9rem | 144px |
| `40` | 10rem | 160px |
| `44` | 11rem | 176px |
| `48` | 12rem | 192px |
| `52` | 13rem | 208px |
| `56` | 14rem | 224px |
| `60` | 15rem | 240px |
| `64` | 16rem | 256px |
| `72` | 18rem | 288px |
| `80` | 20rem | 320px |
| `96` | 24rem | 384px |

### v4 dynamic spacing

In v4 the scale is generated from a single CSS variable `--spacing: 0.25rem`. Any positive integer `N` produces `calc(var(--spacing) * N)`. This means `p-17` (4.25rem / 68px), `gap-43` (10.75rem / 172px), `mt-150` (37.5rem / 600px) all work natively without arbitrary syntax. The named tokens above are still emitted for ergonomic intermediates (the half-steps like `0.5`, `1.5`, etc.) but the integer tokens are no longer hardcoded.

### v3 spacing definition

```js
// v3 default (excerpt from tailwindcss/src/public/colors.js equivalent)
theme.spacing = {
  px: '1px',
  0: '0px',
  0.5: '0.125rem',
  1: '0.25rem',
  // ... full 32-entry table above
}
```

## Default Color Palette

### Neutral families (gray-toned, 5 variants)

| Family | Hue character | Notes |
|--------|---------------|-------|
| `slate` | cool blue-gray | Default for shadcn/ui Zinc/Slate theme |
| `gray` | neutral cool | Most common Material-style gray |
| `zinc` | nearly neutral, slight cool | Default for shadcn/ui Zinc theme |
| `neutral` | true neutral | Color-temperature zero |
| `stone` | warm-tinted | Earthy, paired well with browns/oranges |

### Chromatic families (17 variants)

`red`, `orange`, `amber`, `yellow`, `lime`, `green`, `emerald`, `teal`, `cyan`, `sky`, `blue`, `indigo`, `violet`, `purple`, `fuchsia`, `pink`, `rose`.

### Shades per family

`50`, `100`, `200`, `300`, `400`, `500`, `600`, `700`, `800`, `900`, `950` (11 shades each).

### Format difference

| Version | Format | Example |
|---------|--------|---------|
| v3.4 | `rgb()`, `hsl()`, or hex | `red-500 = rgb(239 68 68) = #ef4444` |
| v4.0+ | `oklch()` (P3 wide-gamut) | `red-500 = oklch(0.637 0.237 25.331)` |

### Color-consuming utilities (every utility that accepts a color token + opacity modifier)

| Utility family | CSS property |
|----------------|--------------|
| `bg-{color}` | `background-color` |
| `text-{color}` | `color` |
| `placeholder-{color}` | `::placeholder color` |
| `border-{color}` | `border-color` |
| `divide-{color}` | child border-color (between siblings) |
| `outline-{color}` | `outline-color` |
| `ring-{color}` | `--tw-ring-color` (box-shadow ring) |
| `inset-ring-{color}` | inner ring color (v4 only) |
| `shadow-{color}` | `--tw-shadow-color` |
| `inset-shadow-{color}` | inset shadow color (v4 only) |
| `drop-shadow-{color}` | filter drop-shadow color |
| `accent-{color}` | `accent-color` (form controls) |
| `caret-{color}` | `caret-color` (text input) |
| `decoration-{color}` | `text-decoration-color` |
| `fill-{color}` | SVG `fill` |
| `stroke-{color}` | SVG `stroke` |

## Default Type Scale

| Token | font-size | paired line-height |
|-------|-----------|---------------------|
| `text-xs` | 0.75rem (12px) | 1rem (16px) |
| `text-sm` | 0.875rem (14px) | 1.25rem (20px) |
| `text-base` | 1rem (16px) | 1.5rem (24px) |
| `text-lg` | 1.125rem (18px) | 1.75rem (28px) |
| `text-xl` | 1.25rem (20px) | 1.75rem (28px) |
| `text-2xl` | 1.5rem (24px) | 2rem (32px) |
| `text-3xl` | 1.875rem (30px) | 2.25rem (36px) |
| `text-4xl` | 2.25rem (36px) | 2.5rem (40px) |
| `text-5xl` | 3rem (48px) | 1 (unitless) |
| `text-6xl` | 3.75rem (60px) | 1 |
| `text-7xl` | 4.5rem (72px) | 1 |
| `text-8xl` | 6rem (96px) | 1 |
| `text-9xl` | 8rem (128px) | 1 |

In v4, the paired line-height is set via the companion variable `--text-{name}--line-height`. To override the paired line-height inline : `text-2xl/[1.1]` or `text-2xl leading-tight`.

## Default Breakpoints

| Token | min-width | px equivalent | CSS |
|-------|-----------|----------------|-----|
| `sm` | 40rem | 640px | `@media (width >= 40rem)` |
| `md` | 48rem | 768px | `@media (width >= 48rem)` |
| `lg` | 64rem | 1024px | `@media (width >= 64rem)` |
| `xl` | 80rem | 1280px | `@media (width >= 80rem)` |
| `2xl` | 96rem | 1536px | `@media (width >= 96rem)` |

All mobile-first : `sm:flex` applies from 40rem **upward**, not "only on small screens". To target an upper bound, use `max-{breakpoint}:` (v3.4+) or `max-[Npx]:`.

## v4 Theme Variable Namespaces (complete list)

Source : https://tailwindcss.com/docs/theme.

| Namespace | Utilities generated | Default example |
|-----------|---------------------|------------------|
| `--color-*` | `bg-*`, `text-*`, `border-*`, `ring-*`, `fill-*`, `stroke-*`, `accent-*`, `caret-*`, `decoration-*`, `outline-*`, `shadow-*`, `inset-shadow-*`, `inset-ring-*` | `--color-red-500: oklch(0.637 0.237 25.331)` |
| `--font-*` | `font-sans`, `font-serif`, `font-mono`, plus any custom family | `--font-sans: ui-sans-serif, system-ui, sans-serif, ...` |
| `--text-*` | `text-xs` through `text-9xl` plus paired `--text-*--line-height` | `--text-base: 1rem` |
| `--font-weight-*` | `font-thin` (100) through `font-black` (900) | `--font-weight-bold: 700` |
| `--tracking-*` | `tracking-tighter` through `tracking-widest` | `--tracking-tight: -0.025em` |
| `--leading-*` | `leading-tight`, `leading-snug`, `leading-normal`, `leading-relaxed`, `leading-loose` | `--leading-tight: 1.25` |
| `--breakpoint-*` | Responsive variants `sm:` through any custom | `--breakpoint-sm: 40rem` |
| `--container-*` | Container-query variants `@xs:` through `@7xl:` + `max-w-md` sizing | `--container-md: 28rem` |
| `--spacing` | Single base unit ; multiplies into every spacing utility | `--spacing: 0.25rem` |
| `--radius-*` | `rounded-xs`, `rounded-sm`, ..., `rounded-4xl` | `--radius-lg: 0.5rem` |
| `--shadow-*` | `shadow-2xs`, `shadow-xs`, ..., `shadow-2xl` | `--shadow-md: 0 4px 6px -1px ...` |
| `--inset-shadow-*` | `inset-shadow-xs`, `inset-shadow-sm` (v4 only) | |
| `--drop-shadow-*` | `drop-shadow-xs`, ..., `drop-shadow-2xl` | |
| `--blur-*` | `blur-xs`, ..., `blur-3xl` | |
| `--perspective-*` | `perspective-near`, `perspective-distant` (v4 only) | `--perspective-distant: 1200px` |
| `--aspect-*` | `aspect-video`, `aspect-square`, plus custom | |
| `--ease-*` | `ease-linear`, `ease-in`, `ease-out`, `ease-in-out` | `--ease-out: cubic-bezier(0,0,0.2,1)` |
| `--animate-*` | `animate-spin`, `animate-bounce`, plus colocated `@keyframes` | |

## v3 Configuration Object Map

| `theme.*` key | v4 namespace equivalent |
|---------------|--------------------------|
| `theme.colors.{family}.{shade}` | `--color-{family}-{shade}` |
| `theme.spacing.{key}` | derived from `--spacing` (single unit) |
| `theme.fontSize.{key}` | `--text-{key}` plus `--text-{key}--line-height` |
| `theme.fontFamily.{key}` | `--font-{key}` |
| `theme.fontWeight.{key}` | `--font-weight-{key}` |
| `theme.letterSpacing.{key}` | `--tracking-{key}` |
| `theme.lineHeight.{key}` | `--leading-{key}` |
| `theme.screens.{key}` | `--breakpoint-{key}` |
| `theme.borderRadius.{key}` | `--radius-{key}` |
| `theme.boxShadow.{key}` | `--shadow-{key}` |
| `theme.aspectRatio.{key}` | `--aspect-{key}` |
| `theme.transitionTimingFunction.{key}` | `--ease-{key}` |
| `theme.animation.{key}` | `--animate-{key}` (with `@keyframes` colocated) |

## Opacity Modifier Reference

### Syntax

```
{color-utility}-{family}-{shade}/{opacity}
```

`{opacity}` accepts :
- Named step : `0`, `5`, `10`, `15`, ..., `95`, `100` (5% increments, both v3 and v4)
- Arbitrary percentage : `/[37.5%]`
- Arbitrary decimal : `/[0.85]`
- CSS variable (v4 parens) : `/(--my-alpha)`
- CSS variable (v3 brackets) : `/[var(--my-alpha)]`

### Implementation

| Version | Mechanism |
|---------|-----------|
| v3 | Generates `rgb(var(--tw-color) / N)` via separate color and alpha channels |
| v4 | Uses CSS `color-mix(in oklch, var(--color-red-500) N%, transparent)` |

## Removed in v4 (No Direct Equivalent)

| v3 mechanism | v4 status |
|--------------|-----------|
| `import resolveConfig from 'tailwindcss/resolveConfig'` | Removed ; use `getComputedStyle(...).getPropertyValue('--color-red-500')` |
| `theme('colors.red.500')` (dot-notation) | Deprecated ; use `theme(--color-red-500)` or `var(--color-red-500)` |
| `bg-opacity-50`, `text-opacity-50`, etc. | Removed ; use `/N` modifier instead |
| `bg-gradient-to-r` | Renamed `bg-linear-to-r` |
