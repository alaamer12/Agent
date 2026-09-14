# Examples : Before / After for Every Breaking Change

Each section pairs the v3 form with the v4 equivalent. Copy-paste
shape.

## Example 1 : Entry CSS

```css
/* v3 */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

```css
/* v4 */
@import "tailwindcss";
```

## Example 2 : PostCSS Config

```js
// v3 : postcss.config.mjs
export default {
  plugins: {
    "postcss-import": {},
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

```js
// v4 : postcss.config.mjs
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
```

## Example 3 : Opacity Modifiers

```html
<!-- v3 -->
<div class="bg-black bg-opacity-50">
<p class="text-zinc-900 text-opacity-70">
<input class="placeholder-zinc-400 placeholder-opacity-50">
```

```html
<!-- v4 -->
<div class="bg-black/50">
<p class="text-zinc-900/70">
<input class="placeholder-zinc-400/50">
```

## Example 4 : Flex Shrink / Grow

```html
<!-- v3 -->
<div class="flex-shrink-0 flex-grow"></div>
```

```html
<!-- v4 -->
<div class="shrink-0 grow"></div>
```

## Example 5 : Shadow Scale Shift

```html
<!-- v3 -->
<div class="shadow-sm"></div>  <!-- the smallest -->
<div class="shadow"></div>     <!-- the default -->
```

```html
<!-- v4 -->
<div class="shadow-xs"></div>  <!-- the smallest -->
<div class="shadow-sm"></div>  <!-- the default -->
```

Same shift applies to `blur`, `drop-shadow`, `backdrop-blur`, and
`rounded`.

## Example 6 : Outline Hidden vs Outline None

```html
<!-- v3 : remove outline -->
<button class="focus:outline-none"></button>
```

```html
<!-- v4 : outline-hidden = preserves accessibility (forced-colors mode) -->
<button class="focus:outline-hidden"></button>

<!-- v4 : outline-none = removes outline entirely (different intent) -->
<button class="focus:outline-none"></button>
```

The v4 `outline-none` removes the outline entirely. The v4
`outline-hidden` is the new equivalent of v3's `outline-none` (visually
none, but visible in forced-colors mode for accessibility).

## Example 7 : Ring Width and Colour

```html
<!-- v3 : ring = 3px blue-500 -->
<button class="focus:ring focus:ring-blue-500"></button>
```

```html
<!-- v4 : explicit 3px + colour -->
<button class="focus:ring-3 focus:ring-blue-500"></button>
```

Or preserve v3 defaults globally :

```css
@theme {
  --default-ring-width: 3px;
  --default-ring-color: var(--color-blue-500);
}
```

## Example 8 : Border Default Colour

```html
<!-- v3 : border = 1px solid gray-200 -->
<div class="border"></div>
```

```html
<!-- v4 : border = 1px solid currentColor -->
<div class="border border-gray-200"></div>
```

Or restore globally :

```css
@layer base {
  *,
  ::after,
  ::before {
    border-color: var(--color-gray-200, currentColor);
  }
}
```

## Example 9 : Gradient Naming

```html
<!-- v3 -->
<div class="bg-gradient-to-r from-red-500 to-yellow-400"></div>
```

```html
<!-- v4 -->
<div class="bg-linear-to-r from-red-500 to-yellow-400"></div>
```

New in v4 :

```html
<div class="bg-radial from-cyan-300 to-blue-700"></div>
<div class="bg-conic-180 from-zinc-300 via-zinc-50 to-zinc-300"></div>
```

## Example 10 : Important Modifier Position

```html
<!-- v3 -->
<div class="!flex !bg-red-500"></div>
```

```html
<!-- v4 -->
<div class="flex! bg-red-500! hover:bg-red-600!"></div>
```

## Example 11 : CSS Variable in Arbitrary Value

```html
<!-- v3 -->
<div class="bg-[--brand]"></div>
```

```html
<!-- v4 -->
<div class="bg-(--brand)"></div>
```

## Example 12 : Arbitrary Value with Commas

```html
<!-- v3 -->
<div class="grid grid-cols-[max-content,auto,minmax(0,1fr)]"></div>
```

```html
<!-- v4 -->
<div class="grid grid-cols-[max-content_auto_minmax(0,1fr)]"></div>
```

Spaces inside parens (the `minmax(0,1fr)` part) stay as commas ;
spaces between top-level grid tracks become underscores.

## Example 13 : Variant Stacking Order

```html
<!-- v3 : right-to-left -->
<ul class="py-4 first:*:pt-0 last:*:pb-0">
  <li>...</li>
</ul>
```

```html
<!-- v4 : left-to-right -->
<ul class="py-4 *:first:pt-0 *:last:pb-0">
  <li>...</li>
</ul>
```

## Example 14 : Hover Gating

```css
/* v3 implicit : always applies */
.hover\:underline:hover { text-decoration: underline; }
```

```css
/* v4 : @media (hover: hover) gate */
@media (hover: hover) {
  .hover\:underline:hover { text-decoration: underline; }
}
```

To restore v3 behaviour :

```css
@import "tailwindcss";
@custom-variant hover (&:hover);
```

## Example 15 : Transform Reset

```html
<!-- v3 -->
<button class="scale-150 focus:transform-none"></button>
```

```html
<!-- v4 : individual property reset -->
<button class="scale-150 focus:scale-none"></button>
```

## Example 16 : Transition with Transforms

```html
<!-- v3 -->
<button class="transition-[opacity,transform] hover:scale-150"></button>
```

```html
<!-- v4 -->
<button class="transition-[opacity,scale] hover:scale-150"></button>
```

## Example 17 : Prefix Syntax

```html
<!-- v3 -->
<div class="tw-flex tw-bg-red-500 tw-hover:tw-bg-red-600"></div>
```

```html
<!-- v4 -->
<div class="tw:flex tw:bg-red-500 tw:hover:bg-red-600"></div>
```

```css
/* v3 : tailwind.config.js */
module.exports = { prefix: 'tw-' }
```

```css
/* v4 : in CSS */
@import "tailwindcss" prefix(tw);
```

## Example 18 : @apply in Scoped Vue Style

```vue
<!-- v3 : works as-is -->
<template>
  <h1>Hello</h1>
</template>
<style scoped>
  h1 { @apply text-2xl font-bold text-red-500; }
</style>
```

```vue
<!-- v4 : @reference required -->
<template>
  <h1>Hello</h1>
</template>
<style scoped>
  @reference "../app.css";
  h1 { @apply text-2xl font-bold text-red-500; }
</style>
```

## Example 19 : theme() Function

```css
/* v3 */
.my-class {
  background-color: theme(colors.red.500);
}
@media (min-width: theme(screens.xl)) {
  /* ... */
}
```

```css
/* v4 */
.my-class {
  background-color: var(--color-red-500);
}
@media (width >= theme(--breakpoint-xl)) {
  /* ... */
}
```

## Example 20 : Custom Utility

```css
/* v3 */
@layer utilities {
  .tab-4 { tab-size: 4; }
  .skew-10deg { transform: skewY(-10deg); }
}
```

```css
/* v4 */
@utility tab-4 {
  tab-size: 4;
}
@utility skew-10deg {
  transform: skewY(-10deg);
}
```

## Example 21 : Custom Component

```css
/* v3 */
@layer components {
  .btn {
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
    background-color: #5b21b6;
    color: white;
  }
}
```

```css
/* v4 : equivalent expressed as utility (overridable) */
@utility btn {
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  background-color: #5b21b6;
  color: white;
}
```

## Example 22 : Safelist

```js
// v3 : tailwind.config.js
module.exports = {
  safelist: [
    'bg-red-500',
    'bg-blue-500',
    { pattern: /bg-(red|green|blue)-(100|500|900)/ },
  ],
}
```

```css
/* v4 : in CSS */
@source inline("bg-red-500 bg-blue-500");
@source inline("bg-{red,green,blue}-{100,500,900}");
```

## Example 23 : Loading JS Plugin

```js
// v3 : tailwind.config.js
module.exports = {
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
}
```

```css
/* v4 : in CSS */
@import "tailwindcss";
@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";
```

## Example 24 : Dark Mode Configuration

```js
// v3 : tailwind.config.js
module.exports = {
  darkMode: 'class',
}
```

```css
/* v4 : in CSS */
@import "tailwindcss";
@custom-variant dark (&:where(.dark, .dark *));
```

## Example 25 : Reading Theme at Runtime

```js
// v3
import resolveConfig from 'tailwindcss/resolveConfig'
import config from '../../tailwind.config.js'

const full = resolveConfig(config)
const red = full.theme.colors.red['500']
```

```js
// v4 : at runtime in browser
const red = getComputedStyle(document.documentElement)
  .getPropertyValue('--color-red-500')
  .trim()
```

## Example 26 : Container Customization

```js
// v3
module.exports = {
  theme: {
    container: {
      center: true,
      padding: '2rem',
    },
  },
}
```

```css
/* v4 */
@utility container {
  margin-inline: auto;
  padding-inline: 2rem;
}
```
