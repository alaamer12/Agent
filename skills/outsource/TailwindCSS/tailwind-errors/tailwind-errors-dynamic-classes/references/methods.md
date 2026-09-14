# Methods : Each Fix in Detail

## Method 1 : Static Map per Framework

### React

```jsx
const colorVariants = {
  blue: 'bg-blue-600 hover:bg-blue-500 text-white',
  red: 'bg-red-500 hover:bg-red-400 text-white',
  green: 'bg-emerald-600 hover:bg-emerald-500 text-white',
  zinc: 'bg-zinc-900 hover:bg-zinc-700 text-zinc-50',
}

function Button({ color = 'blue', children }) {
  return (
    <button className={`${colorVariants[color]} rounded-md px-4 py-2`}>
      {children}
    </button>
  )
}
```

TypeScript with literal-union :

```tsx
type Color = keyof typeof colorVariants

function Button({ color, children }: { color: Color; children: ReactNode }) {
  return (
    <button className={`${colorVariants[color]} rounded-md px-4 py-2`}>
      {children}
    </button>
  )
}
```

### Vue 3 (Composition API)

```vue
<script setup lang="ts">
const props = defineProps<{ color: 'blue' | 'red' | 'green' }>()

const colorVariants = {
  blue: 'bg-blue-600 hover:bg-blue-500 text-white',
  red: 'bg-red-500 hover:bg-red-400 text-white',
  green: 'bg-emerald-600 hover:bg-emerald-500 text-white',
} as const
</script>

<template>
  <button :class="`${colorVariants[color]} rounded-md px-4 py-2`">
    <slot />
  </button>
</template>
```

### Svelte

```svelte
<script lang="ts">
  export let color: 'blue' | 'red' | 'green' = 'blue'

  const variants = {
    blue: 'bg-blue-600 hover:bg-blue-500 text-white',
    red: 'bg-red-500 hover:bg-red-400 text-white',
    green: 'bg-emerald-600 hover:bg-emerald-500 text-white',
  }
</script>

<button class="{variants[color]} rounded-md px-4 py-2">
  <slot />
</button>
```

### Server templates (Jinja, Handlebars)

```html
{% set variants = {
  'blue': 'bg-blue-600 hover:bg-blue-500 text-white',
  'red': 'bg-red-500 hover:bg-red-400 text-white',
} %}

<button class="{{ variants[color] }} rounded-md px-4 py-2">
  {{ label }}
</button>
```

Tailwind scans the template file and sees every value as a literal
token inside the dictionary.

## Method 2 : Inline Style for Arbitrary Values

### React

```jsx
function ThemedCard({ accent, children }) {
  return (
    <div
      className="rounded-lg p-6 shadow-sm"
      style={{
        borderTopWidth: '4px',
        borderTopColor: accent,
        backgroundColor: `${accent}11`,
      }}
    >
      {children}
    </div>
  )
}
```

### Vue

```vue
<template>
  <div
    class="rounded-lg p-6 shadow-sm"
    :style="{
      borderTopWidth: '4px',
      borderTopColor: accent,
      backgroundColor: `${accent}11`,
    }"
  >
    <slot />
  </div>
</template>
```

### Custom properties via inline style (advanced)

When the value should drive multiple utilities (text, background, border
each via Tailwind), expose it as a CSS variable in inline style and
reference it from Tailwind arbitrary values :

```jsx
function ThemedSection({ accent, children }) {
  return (
    <section
      className="border-l-4 border-(--accent) bg-(--accent)/10 text-(--accent)"
      style={{ '--accent': accent }}
    >
      {children}
    </section>
  )
}
```

The classes `border-(--accent)`, `bg-(--accent)/10`,
`text-(--accent)` are LITERAL TOKENS in the source file (the scanner
sees them). They reference the CSS variable set by `style`, which
carries the runtime value. This pattern combines Tailwind structure
with truly dynamic colour.

NOTE : v3 uses `bg-[--accent]`, v4 uses `bg-(--accent)`. See
`tailwind-impl-migration-v3-v4` for the brackets-to-parens change.

## Method 3 : v3 safelist Detail

### Literal-string array

```js
module.exports = {
  content: ['./src/**/*.{html,js,ts,jsx,tsx}'],
  safelist: [
    'bg-red-500',
    'bg-blue-500',
    'bg-green-500',
    'text-3xl',
    'lg:text-4xl',
  ],
}
```

### Pattern object

```js
module.exports = {
  safelist: [
    {
      pattern: /bg-(red|green|blue|amber|purple)-(50|100|200|300|400|500|600|700|800|900)/,
    },
  ],
}
```

### Pattern with variants

```js
module.exports = {
  safelist: [
    {
      pattern: /bg-(red|green|blue)-(500|700|900)/,
      variants: ['hover', 'focus', 'md', 'lg', 'lg:hover'],
    },
  ],
}
```

### Combining literals and patterns

```js
module.exports = {
  safelist: [
    'bg-red-500',
    {
      pattern: /text-(red|green|blue)-\d+/,
      variants: ['hover'],
    },
    {
      pattern: /m[xy]-\d+/,
    },
  ],
}
```

### Bundle-size warning

A wide pattern like `/bg-.*/` emits every colour combination in the
default palette : roughly 30 colours × 11 shades × the variants array.
Always scope patterns to the colours actually used.

## Method 4 : v4 @source inline Detail

### Single class

```css
@import "tailwindcss";
@source inline("bg-red-500");
```

### Multiple classes (space-separated)

```css
@source inline("bg-red-500 bg-blue-500 bg-green-500");
```

### Brace expansion (Cartesian product)

```css
@source inline("bg-{red,blue,green}-500");
```

Generates `bg-red-500`, `bg-blue-500`, `bg-green-500`.

### Numeric range

```css
@source inline("p-{0..12}");
```

Generates `p-0`, `p-1`, ..., `p-12`.

### Numeric range with step

```css
@source inline("bg-red-{100..900..100}");
```

Generates `bg-red-100`, `bg-red-200`, ..., `bg-red-900`.

### Nested expansion (full shade palette)

```css
@source inline("bg-red-{50,{100..900..100},950}");
```

Generates all eleven shades : `bg-red-50`, `bg-red-100`, ...,
`bg-red-900`, `bg-red-950`.

### Multiplied with variants

```css
@source inline("{hover:,focus:,}bg-red-500");
```

The empty alternative (trailing comma in `{hover:,focus:,}`) emits the
bare class. So this generates `bg-red-500`, `hover:bg-red-500`,
`focus:bg-red-500`.

### Full design-system safelist

```css
@import "tailwindcss";

@source inline(
  "{hover:,focus:,active:,}bg-{red,orange,amber,yellow,lime,green,emerald,teal,cyan,sky,blue,indigo,violet,purple,fuchsia,pink,rose,zinc,slate,stone}-{50,{100..900..100},950}"
);
```

This single line covers every Tailwind colour at every shade with
hover, focus, and active variants. ALWAYS narrow this to the colours
actually in use ; the unbounded version produces hundreds of unused
rules.

### Exclusion with @source not

To safelist all shades EXCEPT the very dark ones :

```css
@source inline("bg-{red,blue,green}-{50,{100..900..100},950}");
@source not inline("bg-{red,blue,green}-{800,900,950}");
```

### Combining with regular @source

`@source inline` adds classes to the build. `@source "path"` adds a
scan path. Both can coexist :

```css
@import "tailwindcss";
@source "../../packages/ui";
@source inline("bg-{red,blue,green}-{500,700}");
```

## Method 5 : Hybrid Patterns (CSS Variable + Tailwind Arbitrary)

When the value is genuinely user-typed but you want the rest of the
class string Tailwind-managed :

```tsx
function CustomThemedBox({ tint, children }: { tint: string; children: ReactNode }) {
  return (
    <div
      style={{ '--tint': tint } as React.CSSProperties}
      className="rounded-lg border border-(--tint) bg-(--tint)/5 p-6"
    >
      {children}
    </div>
  )
}
```

Usage :

```tsx
<CustomThemedBox tint="oklch(0.7 0.15 200)">…</CustomThemedBox>
<CustomThemedBox tint="#ff5733">…</CustomThemedBox>
```

The classes `border-(--tint)` and `bg-(--tint)/5` are literal tokens
in the source. The scanner sees them. The `tint` value flows through
the CSS variable at runtime.

## Method 6 : Detecting the Problem in CI

Add a build-time grep that fails the pipeline when banned dynamic
patterns appear :

```bash
#!/usr/bin/env bash
# scripts/check-dynamic-classes.sh
set -euo pipefail

PATTERN='class(Name)?\s*=\s*[`"]\?[^`"]*\${[^}]*}'

if grep -rEn "$PATTERN" src --include="*.tsx" --include="*.jsx" --include="*.vue" --include="*.svelte"; then
  echo "ERROR : dynamic class interpolation detected. Use a static map."
  exit 1
fi

echo "OK : no dynamic class interpolation found."
```

Run in CI before `npm run build`. The check catches the bug before
production.

## Method 7 : Dev Parity With Production

To reproduce the production bug in dev, force the dev server to skip
HMR re-scanning :

```bash
# Vite : run build then preview
npm run build && npm run preview

# Next : production build
npm run build && npm start

# Astro : production
npm run build && npm run preview
```

If the dynamic class fails here, it will fail in real production.
ALWAYS test prod-built bundles before shipping changes that touch
prop-driven styling.
