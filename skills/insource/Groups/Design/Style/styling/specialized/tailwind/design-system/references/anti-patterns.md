# Anti-patterns

Failure modes around theme tokens, each with what breaks, why, and the deterministic fix. Upgrade-time
breaking changes (renamed scales, changed defaults, removed config options and utilities, removed
build APIs) are catalogued once by the `migration` module
([../../migration/method.md](../../migration/method.md)); nothing below repeats that list.

## AP-1 — token name assembled at a call site

```jsx
// BROKEN
function Badge({ color }) {
  return <span className={`bg-${color}-500 text-white`}>{children}</span>
}
// renders class="bg-red-500 text-white" with no CSS rule behind it
```

Why: the content scanner reads source as plain text. `bg-${color}-500` never appears as a literal
token; only `bg-` and `-500` do, and neither is a valid class. The element gets the name, the build
never generated the rule, and it renders unstyled. Dev-server rescans mask this until a production
build.

Fix: a map of complete literal class strings.

```jsx
const COLOR_CLASSES = {
  red: 'bg-red-500',
  blue: 'bg-blue-500',
  green: 'bg-green-500',
  yellow: 'bg-yellow-500',
}

function Badge({ color, children }) {
  return <span className={`${COLOR_CLASSES[color]} text-white`}>{children}</span>
}
```

A token map is a lookup, and every value in it is searchable. When the set is genuinely open (a CMS
picks the color), that is a runtime-variable problem, not a string-building problem. The full fix
ladder and the generation/safelist grammar belong to the `dynamic-classes` module
([../../dynamic-classes/method.md](../../dynamic-classes/method.md)).

Sources: https://github.com/tailwindlabs/tailwindcss/issues/18136,
https://tailwindcss.com/docs/detecting-classes-in-source-files.

## AP-2 — mixing oklch with hex/rgb inside one palette

```css
/* v4 */
@theme {
  --color-brand-500: #3b82f6;                /* hex: parses, breaks perceptual consistency */
  --color-brand-600: oklch(0.55 0.196 254);  /* oklch sibling */
}
```

Why: the default palette is oklch, and v4's opacity modifier runs through
`color-mix(in oklch, ...)`. The hex value is converted on the fly — mathematically correct, visually
different. Two adjacent shades of the same family then disagree about both lightness step and
alpha-blended output, and the difference is larger on P3 displays than on the monitor where it was
approved.

Fix: one format per palette, and in v4 that format is oklch.

```css
@theme {
  --color-brand-500: oklch(0.65 0.196 254);
  --color-brand-600: oklch(0.55 0.196 254);
}
```

Convert existing brand hexes with a tool (oklch.com, the `culori` library) instead of dropping them
into `@theme` unchanged. Sources: https://tailwindcss.com/docs/colors,
https://tailwindcss.com/blog/tailwindcss-v4.

## AP-3 — legacy dotted `theme()` path in v4 CSS

```css
.my-button {
  background: theme('colors.red.500'); /* nested JS path */
}
```

Why: in v4 the theme is a flat CSS-variable namespace, not a nested JS object. The dotted form is
deprecation-warned and fragile: keys with hyphens and custom keys with dots do not resolve reliably,
so the build can pass while the value is wrong.

Fix: reference the variable.

```css
.my-button {
  background: var(--color-red-500);        /* resolves at runtime, theme-switchable */
  border-color: theme(--color-red-500);    /* substituted at build */
}
```

Prefer `var()` for anything a theme swap or `@theme inline` may reassign; use the compile-time form
only when you deliberately want the value frozen. Source: https://tailwindcss.com/docs/theme.

## AP-4 — separate opacity utility instead of the modifier

```html
<!-- BROKEN: split-channel form -->
<div class="bg-blue-600 bg-opacity-50">Translucent panel</div>

<!-- GOOD: modifier on the color token -->
<div class="bg-blue-600/50">Translucent panel</div>
```

Why: the modifier is the form the token system is written for. In v3 the split-channel form works only
beside the matching color utility and sets a second custom property; in v4 there is no split-channel
form at all (see the `migration` module). The modifier reads as one intent per element, applies to
`text-*`, `border-*`, `ring-*`, `fill-*`, `shadow-*`, `outline-*`, `decoration-*` alike, and keeps the
alpha step greppable.

Fix: always `/N` on the color utility itself. Source: https://tailwindcss.com/docs/colors.

## AP-5 — importing the JS config to read a token

```js
// build-time / Node: reading a JS theme object
const colors = resolveConfig(tailwindConfig).theme.colors
```

Why: on v4 there is no JS-importable theme at all; the source of truth moved to CSS variables, so
the import has nothing to resolve. On v3 it works but freezes a second copy of the theme in JS,
which drifts the moment someone edits the config in one place only.

Fix on v4 — read the computed variables:

```js
const styles = getComputedStyle(document.documentElement)
const red500 = styles.getPropertyValue('--color-red-500').trim()
```

Fix with no DOM (SSR, OG-image generation, chart theming in Node): parse the compiled CSS output for
`--color-*: oklch(...)` declarations once at build time, or import the token source of truth and
generate both CSS variables and the JS map from it. Never hand-maintain two token lists.

## AP-6 — two syntaxes for runtime CSS variables in one codebase

```html
<div class="bg-[var(--brand)]">brackets</div>
<div class="bg-(--brand)">parens</div>
```

Why: the parens shorthand is v4-only. In a v3 project it parses as an unrelated arbitrary value and
silently produces no rule, which looks like a missing token rather than a syntax error. The brackets
form resolves in both.

Fix: pick per project and enforce it.

| Project | Use |
|---|---|
| v3.4 | `bg-[var(--brand)]` |
| v4.0+, new code | `bg-(--brand)` |
| v4.0+, existing v3 markup | brackets keep working; migrate to parens once the project is fully v4 |

Source: https://tailwindcss.com/docs/adding-custom-styles#using-css-variables.

## AP-7 — custom shades named by tone instead of the 50-950 convention

```css
@theme {
  --color-brand-light: oklch(0.85 0.05 254);
  --color-brand: oklch(0.55 0.196 254);
  --color-brand-dark: oklch(0.25 0.146 264);
}
```

Why: it builds, and it costs everyone. Every shadcn-style token system, every tool that derives a
hover shade from `500`, and every developer reading the markup assumes the 11-step scale. Tone names
force a private vocabulary per family, so `bg-brand-dark` and `bg-accent-deep` are two spellings of
the same idea and nothing can be generated or audited across them.

Fix: follow the convention.

```css
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
}
```

Then `bg-brand-50` … `bg-brand-950` mirror the default palette and slot into any role-alias system.
A single-value brand color is fine as `--color-brand: ...`; a *family* is not fine as three adjectives.
Source: https://ui.shadcn.com/docs/theming.

## AP-8 — reading `sm:` as "small screens only"

```html
<h1 class="sm:text-3xl">Headline</h1>
```

Why: `sm:` is a minimum-width variant — from 40rem upward. On a phone below 640px the rule never
matches, so the element keeps the browser default size: the exact case the author meant to style is
the case that goes unstyled.

Fix: base styles are the mobile design, prefixes override upward.

```html
<h1 class="text-xl sm:text-2xl md:text-3xl">Headline</h1>

<!-- only when the intent really is an upper bound -->
<h1 class="max-sm:text-xl sm:text-3xl">xl below 640px, 3xl from there up</h1>
```

Source: https://tailwindcss.com/docs/responsive-design.

## AP-9 — raw value at the call site instead of a token

```html
<div class="p-[18px] bg-[#3b82f6] text-[15px] border-[1px] border-[#dbeafe]">Card</div>
```

Why: each arbitrary value is an undocumented token. It cannot be re-themed, cannot be audited by
reading `@theme` or `theme.extend`, and invites the next contributor to copy the literal — which is
how five slightly different blues end up in one product.

Fix, in order of preference:

```html
<!-- 1. the default scale -->
<div class="p-4 bg-blue-600 text-base border border-blue-200">...</div>

<!-- 2. a named token added to the theme, because the value repeats -->
<div class="p-card bg-brand-600 text-body border-brand-200">...</div>

<!-- 3. arbitrary, only when the value is genuinely one-off -->
<div class="p-[calc(100%-2rem)]">...</div>
```

One arbitrary value is a pragmatic exception. The same arbitrary value three times is a missing token;
add it to the theme and replace all three.
