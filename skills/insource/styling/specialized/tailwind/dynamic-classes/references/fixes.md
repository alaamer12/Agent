# fixes — the four ranked fixes, worked

Everything here implements a fix from `../method.md`; the ranking and the decision tree live there.
Framework shapes only differ in where the map is declared — the tokens must be complete literals in
a scanned file in every one of them.

## Fix 1 — static map per prop

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

### React + TypeScript

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

`keyof typeof` keeps the union derived from the map: add a colour, the prop accepts it; typo one, the
compiler rejects it. Typing the map explicitly (`Record<Status, string>`) buys the same exhaustiveness
check when the key union is declared separately — see `examples.md` §4.

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
  <button :class="`${colorVariants[props.color]} rounded-md px-4 py-2`">
    <slot />
  </button>
</template>
```

The interpolation is inside the component that owns the map — the lookup, not the name, is dynamic.
Svelte and server templates make the same shape explicit below.

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

### Server templates (Jinja, Handlebars, ERB)

```html
{% set variants = {
  'blue': 'bg-blue-600 hover:bg-blue-500 text-white',
  'red': 'bg-red-500 hover:bg-red-400 text-white',
} %}

<button class="{{ variants[color] }} rounded-md px-4 py-2">
  {{ label }}
</button>
```

The template file is scanned, so the dictionary **values** are literal tokens even though the key is
chosen at render time. The same holds for a shared constants module: a map of complete strings,
imported and indexed, is fine; a function that builds a name is not
(`anti-patterns.md` §10).

## Fix 2 — inline style for arbitrary values

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

### Tailwind structure + runtime value (the hybrid that stays in the system)

When one value drives several utilities, set it as a custom property once and reference it from
arbitrary values. The utilities are literal tokens; the value is runtime.

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

<CustomThemedBox tint="oklch(0.7 0.15 200)">…</CustomThemedBox>
<CustomThemedBox tint="#ff5733">…</CustomThemedBox>
```

`border-(--tint)` and `bg-(--tint)/5` exist in the source as complete tokens, so the scanner emits
their rules once; `tint` flows through the variable at runtime with no CSS regeneration per value.

The arbitrary-value variable syntax differs by major version — v3 brackets, v4 parentheses. The
breaking-change catalog for that conversion is the `migration` module's (`../../migration/method.md`);
adopt whichever the project's version uses and keep it consistent.

## Fix 3 — v3 `safelist` shapes

These shapes mix freely inside one `safelist` array. `content` must be set: v3 with no `content` scans
nothing and generates zero classes (path configuration: `../../config/method.md`).

### Literal strings — variants allowed here

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

### Pattern with variants — the only place variants may appear

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

A `pattern` is matched against base utility names, so `hover:` inside it can never match. Compound
entries in `variants` (`'lg:hover'`) are legal.

### Combining literals and patterns

```js
module.exports = {
  safelist: [
    'bg-red-500',
    { pattern: /text-(red|green|blue)-\d+/, variants: ['hover'] },
    { pattern: /m[xy]-\d+/ },
  ],
}
```

### Scoping

Each pattern multiplies: colours × shades × (1 + variants). A wide pattern such as `/bg-.*/` covers
roughly 30 colours × 11 shades and every requested variant. ALWAYS restrict the alternation to the
values the app can actually emit, and audit the list each release (`../method.md` verification,
item 4).

## Fix 4 — v4 `@source inline` forms

Grammar and expansion semantics: `../method.md` §Fix 4 (this module owns the grammar). These are the
shapes with their output.

```css
@import "tailwindcss";

/* one class */
@source inline("bg-red-500");

/* several classes, space-separated */
@source inline("bg-red-500 bg-blue-500 bg-green-500");

/* brace expansion → bg-red-500, bg-blue-500, bg-green-500 */
@source inline("bg-{red,blue,green}-500");

/* numeric range → p-0 … p-12 */
@source inline("p-{0..12}");

/* range with step → bg-red-100 … bg-red-900 */
@source inline("bg-red-{100..900..100}");

/* nested: literal 50, stepped range, literal 950 → all eleven shades */
@source inline("bg-red-{50,{100..900..100},950}");

/* variants; the trailing comma emits the bare class too */
@source inline("{hover:,focus:,}bg-red-500");

/* directions × scale, all breakpoint prefixes */
@source inline("{sm:,md:,lg:,xl:,}m{x,y,t,r,b,l,}-{0..16}");
```

Full design system, bounded to one directive — and the reason to narrow it:

```css
@import "tailwindcss";

@source inline(
  "{hover:,focus:,active:,}bg-{red,orange,amber,yellow,lime,green,emerald,teal,cyan,sky,blue,indigo,violet,purple,fuchsia,pink,rose,zinc,slate,stone}-{50,{100..900..100},950}"
);
```

That is every named colour at every shade with three interaction variants: hundreds of rules, most of
them unused. ALWAYS cut the colour list down to the palette the product ships.

Excluding a subset from an otherwise-wide directive:

```css
@source inline("bg-{red,blue,green}-{50,{100..900..100},950}");
@source not inline("bg-{red,blue,green}-{800,900,950}");
```

`@source not inline` subtracts even when the scanner found the class in source, so it also prunes
accidental utility use — do not use it to hide a mistake you should fix in the component.

Coexistence with path sources (paths are the `config` module's territory):

```css
@import "tailwindcss";
@source "../../packages/ui";
@source inline("bg-{red,blue,green}-{500,700}");
```

Directives belong in the stylesheet that imports Tailwind, not in a component file.

## Local guard and prod parity

Tripwire the interpolation before it reaches review (the repo-wide audit and report format are
`../../validator/method.md`'s job):

```bash
#!/usr/bin/env bash
# scripts/check-dynamic-classes.sh
set -euo pipefail

# a class attribute whose value interpolates a template literal — JSX, Vue, Svelte, template strings
if grep -rEn 'class(Name)?=[^>]*\$\{' src \
    --include="*.tsx" --include="*.jsx" --include="*.vue" --include="*.svelte" --include="*.js"; then
  echo "ERROR: dynamic class interpolation detected. Use a static map."
  exit 1
fi

# concatenation with a utility prefix ('bg-' + color + '-500')
if grep -rEn "(bg|text|border|ring|shadow)-[a-z]*' *\+" src \
    --include="*.tsx" --include="*.jsx" --include="*.js"; then
  echo "ERROR: class-name concatenation detected. Use a static map."
  exit 1
fi

echo "OK: no dynamic class interpolation found."
```

Run it in CI before `npm run build`; it catches the class of bug the dev server cannot show.

Reproduce the production condition on purpose:

```bash
# Vite / Astro
npm run build && npm run preview
# Next
npm run build && npm start
```

The dev server's HMR re-scan is what hid the failure; a built artifact has no such second chance. If
the class fails under preview, it fails in production.
