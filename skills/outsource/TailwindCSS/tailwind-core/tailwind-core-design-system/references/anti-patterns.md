# Tailwind CSS Design System: Anti-Patterns

Real failure modes mined from the upgrade guide and the Tailwind issue tracker. Each pattern lists what fails, why, and the deterministic fix.

## AP-1: Dynamic Class String Concatenation

```jsx
// BROKEN
function Badge({ color }) {
  return <span className={`bg-${color}-500 text-white`}>{children}</span>
}
// Produces : <span class="bg-red-500 text-white"> ... but no CSS rule exists.
```

### Why this fails

Tailwind's content scanner reads source files as **plain-text tokens**. `bg-${color}-500` never appears as a literal token in the source ; only `bg-` and `-500` do, neither of which is a valid class on its own. The class lands in the DOM but the corresponding CSS rule was never generated, so it renders as no-style.

### Fix : static class map

```jsx
const COLOR_CLASSES = {
  red:    'bg-red-500',
  blue:   'bg-blue-500',
  green:  'bg-green-500',
  yellow: 'bg-yellow-500',
}

function Badge({ color, children }) {
  return <span className={`${COLOR_CLASSES[color]} text-white`}>{children}</span>
}
```

Now every literal class string (`bg-red-500`, `bg-blue-500`, etc.) appears in source and gets generated.

### v4 escape hatch : `@source inline()`

When a static map is infeasible (e.g. CMS-driven colors), use the safelist directive in your main CSS :

```css
@import "tailwindcss";
@source inline("{hover:,}bg-{red,blue,green,yellow}-{50,{100..900..100},950}");
```

Brace expansion produces every combination. The v3 equivalent is the deprecated `safelist: [...]` config option.

Source : https://github.com/tailwindlabs/tailwindcss/issues/18136 and https://tailwindcss.com/docs/detecting-classes-in-source-files.

## AP-2: Mixing oklch and rgb Without Realising

```css
/* v4 main.css */
@import "tailwindcss";

@theme {
  /* All v4 defaults are oklch */
  --color-brand-500: #3b82f6;    /* hex tolerated but breaks perceptual consistency */
  --color-brand-600: oklch(0.55 0.196 254);
}
```

### Why this fails

The default palette is oklch. When you mix one custom color in hex and the rest in oklch, the **opacity modifier** uses `color-mix(in oklch, ...)`, which converts the hex value into oklch on the fly. The conversion is mathematically correct but visually unexpected : the hex color produces different alpha-blended output than the oklch sibling.

### Fix : ALWAYS use oklch in v4

```css
@theme {
  --color-brand-500: oklch(0.65 0.196 254);
  --color-brand-600: oklch(0.55 0.196 254);
}
```

Use a conversion tool (e.g. https://oklch.com or `culori` JS library) when migrating brand colors from hex to oklch.

Source : https://tailwindcss.com/docs/colors and https://tailwindcss.com/blog/tailwindcss-v4.

## AP-3: `theme('colors.red.500')` Dot-Notation in v4 CSS

```css
/* v4 CSS using legacy dot-notation */
.my-button {
  background: theme('colors.red.500'); /* WARNING in v4 */
}
```

### Why this fails

In v4 the theme is a flat CSS-variable namespace, not a nested JS object. The dot-notation form is deprecated and slated for removal. It still works in v4.0 through v4.3 with a deprecation warning, but the build will not catch all edge cases (theme keys with hyphens, custom keys with dots).

### Fix : use CSS-variable path or `var()`

```css
.my-button {
  background: var(--color-red-500);
}

/* Or, for compile-time substitution (v4 syntax) : */
.my-button {
  background: theme(--color-red-500);
}
```

Source : https://tailwindcss.com/docs/upgrade-guide (section on the `theme()` function).

## AP-4: Using `bg-opacity-50` in v4

```html
<!-- v3 syntax that silently breaks in v4 -->
<div class="bg-blue-600 bg-opacity-50">Translucent panel</div>
```

### Why this fails

`bg-opacity-*`, `text-opacity-*`, `border-opacity-*`, `divide-opacity-*`, `ring-opacity-*`, and `placeholder-opacity-*` are **removed** in v4. The class lands in the DOM but generates no CSS rule. The element keeps its base color at full opacity.

### Fix : opacity modifier

```html
<div class="bg-blue-600/50">Translucent panel</div>
```

This works in both v3.4 and v4 ; the legacy `bg-opacity-*` form should be removed everywhere.

Source : https://tailwindcss.com/docs/upgrade-guide (Opacity utilities section).

## AP-5: `import resolveConfig from 'tailwindcss/resolveConfig'` in v4

```js
// v3 code that throws ModuleNotFoundError in v4
import resolveConfig from 'tailwindcss/resolveConfig'
import tailwindConfig from '../tailwind.config.js'

const colors = resolveConfig(tailwindConfig).theme.colors
```

### Why this fails

`resolveConfig` is removed in v4 because the source of truth has moved from a JS config object to CSS variables. There is no JS-importable theme object anymore.

### Fix : `getComputedStyle` on CSS variables

```js
const styles = getComputedStyle(document.documentElement)
const red500 = styles.getPropertyValue('--color-red-500').trim()
```

For server-side or build-time access (e.g. generating an OpenGraph image), parse the compiled CSS output for `--color-*: oklch(...)` declarations.

Source : https://tailwindcss.com/docs/upgrade-guide.

## AP-6: Mixing v3 and v4 Arbitrary CSS-Variable Syntax

```html
<!-- v3 brackets syntax used in v4 project (still works but inconsistent) -->
<div class="bg-[var(--brand)] text-[var(--brand-fg)]">

<!-- v4 parens syntax used in v3 project (DOES NOT WORK) -->
<div class="bg-(--brand) text-(--brand-fg)">
```

### Why this fails

v4 introduced `bg-(--var)` parens syntax as a shorthand for `bg-[var(--var)]`. The brackets form is preserved for backward compatibility, but the parens form is **v4-only** : in v3 it is interpreted as an unrelated arbitrary value and silently produces no rule.

### Fix : pick one syntax per project

| Version | Syntax |
|---------|--------|
| v3.4 only | `bg-[var(--brand)]` (brackets) |
| v4.0+ exclusive | `bg-(--brand)` (parens) |
| v4 but still using v3 markup | brackets form continues to work |

Codebase migration recommendation : migrate to parens after fully on v4.

Source : https://tailwindcss.com/docs/upgrade-guide (Arbitrary variables section).

## AP-7: Assuming `sm:` Means "Small Screens Only"

```html
<!-- Author thinks : "small screens : larger text" -->
<h1 class="sm:text-3xl">Headline</h1>
```

### Why this fails

`sm:` is mobile-first : it applies from 40rem (640px) **and up**. On phones below 640px the rule never matches, and the base style (none specified here, so browser default) wins.

### Fix : default style for mobile, override at breakpoint

```html
<!-- Default text-xl on phones, scales up at sm/md -->
<h1 class="text-xl sm:text-2xl md:text-3xl">Headline</h1>
```

To explicitly target phones only, use the `max-{breakpoint}:` variant :

```html
<h1 class="max-sm:text-xl sm:text-3xl">Phones get xl, sm+ gets 3xl</h1>
```

Source : https://tailwindcss.com/docs/responsive-design.

## AP-8: Forgetting the Border + Ring Default Change When Migrating to v4

```html
<!-- Worked in v3, looks invisible in v4 -->
<div class="border rounded-md p-4">
  <button class="ring focus:ring-blue-500">Submit</button>
</div>
```

### Why this fails

In v3, `border` (no color) defaulted to `gray-200`, and `ring` defaulted to 3px blue-500. In v4 both defaults changed : `border` defaults to `currentColor` (often invisible against a same-color background), and `ring` defaults to 1px `currentColor`.

### Fix : explicit colors OR a compatibility shim

Option A : explicit per-element (preferred for new code).

```html
<div class="border border-gray-200 rounded-md p-4">
  <button class="ring ring-blue-500 ring-3 focus:ring-blue-600">Submit</button>
</div>
```

Option B : restore v3 defaults via `@layer base` (preferred for large migrations).

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

Source : https://tailwindcss.com/docs/upgrade-guide (sections on default colors and ring width).

## AP-9: Shadow / Radius / Blur Scale Shift in v4

```html
<!-- v3 : shadow-sm = small shadow, shadow = default 1px -->
<div class="shadow-sm">v3 small shadow</div>

<!-- v4 : same class name, but shadow-sm is now what v3 called shadow-md -->
```

### Why this fails

v4 inserted a new `*-xs` step at the bottom of the `shadow-*`, `blur-*`, `rounded-*`, `drop-shadow-*`, and `backdrop-blur-*` scales. Every existing class shifted up by one : v3's `shadow-sm` is now v4's `shadow-xs` ; v3's `shadow` (no suffix) is now `shadow-sm` ; and so on.

### Fix : map every site

| v3 class | v4 equivalent |
|----------|---------------|
| `shadow-sm` | `shadow-xs` |
| `shadow` | `shadow-sm` |
| `shadow-md` | `shadow-md` (unchanged) |
| `blur-sm` | `blur-xs` |
| `blur` | `blur-sm` |
| `rounded-sm` | `rounded-xs` |
| `rounded` | `rounded-sm` |

The upgrade tool `npx @tailwindcss/upgrade` handles most cases. Manually inspect any handwritten utilities-stack classes.

Source : https://tailwindcss.com/docs/upgrade-guide (sections 5 and 6).

## AP-10: Defining Colors Outside the Default 11-Shade Pattern

```css
/* Awkward : custom palette with non-standard shades */
@theme {
  --color-brand-light: oklch(0.85 0.05 254);
  --color-brand: oklch(0.55 0.196 254);
  --color-brand-dark: oklch(0.25 0.146 264);
}
```

### Why this fails

This works, but breaks every contributor's expectation. Every shadcn/ui pattern, every JS library that derives complementary shades, and every developer reading the code assumes the 50-950 scale. Custom shade names (`-light`, `-dark`, `-strong`) force everyone to learn your private vocabulary.

### Fix : follow the 50-950 convention

```css
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
}
```

Now `bg-brand-50` through `bg-brand-950` mirror the default palette and slot directly into any shadcn-style token system.

Source : https://tailwindcss.com/docs/theme and https://ui.shadcn.com/docs/theming.
