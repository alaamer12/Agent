# Reference : @apply, @layer, @reference Examples

Copy-paste patterns for common @apply / @layer / @reference scenarios.

---

## Example 1 : Button component class (both versions)

`src/styles/components.css` :

```css
@layer components {
  .btn {
    @apply inline-flex items-center justify-center rounded
           px-4 py-2 font-medium transition;
  }

  .btn-primary {
    @apply btn bg-blue-500 text-white hover:bg-blue-600;
  }

  .btn-secondary {
    @apply btn bg-gray-200 text-gray-900 hover:bg-gray-300;
  }
}
```

NOTE : `.btn-primary { @apply btn ... }` is NOT supported. Repeat the
shared utilities :

```css
@layer components {
  .btn-primary {
    @apply inline-flex items-center justify-center rounded
           px-4 py-2 font-medium transition
           bg-blue-500 text-white hover:bg-blue-600;
  }
}
```

Or extract a Sass mixin / PostCSS @apply chain only after measuring
the duplication actually matters.

---

## Example 2 : Base layer for element defaults

```css
@layer base {
  body {
    @apply bg-gray-50 text-gray-900 antialiased;
  }

  h1 { @apply text-4xl font-bold tracking-tight; }
  h2 { @apply text-3xl font-semibold; }
  h3 { @apply text-2xl font-semibold; }

  a {
    @apply text-blue-600 underline underline-offset-2;
  }

  a:hover {
    @apply text-blue-800;
  }
}
```

Base layer rules apply to every matching element. ALWAYS use class
overrides for exceptions ; do NOT add `:not(.no-style)` workarounds.

---

## Example 3 : Custom utility in utilities layer

```css
@layer utilities {
  .text-shadow-sm {
    text-shadow: 0 1px 2px rgb(0 0 0 / 0.1);
  }
  .text-shadow-md {
    text-shadow: 0 2px 4px rgb(0 0 0 / 0.15);
  }
  .text-shadow-none {
    text-shadow: none;
  }
}
```

Usage :

```html
<p class="text-shadow-sm">Subtle shadow</p>
```

For v4 only, the modern equivalent is `@utility text-shadow-sm { ... }`
(see `tailwind-impl-config-v4`). Both work ; `@utility` is preferred
for new code.

---

## Example 4 : Third-party widget override

```css
@layer components {
  /* react-select */
  .react-select__control {
    @apply rounded border border-gray-300 px-2 py-1 shadow-sm;
  }
  .react-select__menu {
    @apply rounded border border-gray-200 bg-white shadow-lg;
  }

  /* Algolia DocSearch */
  .DocSearch-Button {
    @apply rounded border border-gray-200 bg-white px-3 py-1.5;
  }
}
```

The library owns the markup, so component extraction is impossible.
@apply bridges your tokens into their selectors. ALWAYS scope to
known library class names ; NEVER use broad selectors like `* { @apply ... }`.

---

## Example 5 : Vue SFC scoped @apply (v4)

`src/components/Card.vue` :

```vue
<script setup lang="ts">
defineProps<{ title: string }>()
</script>

<template>
  <div class="card">
    <h3 class="card-title">{{ title }}</h3>
    <div class="card-body"><slot /></div>
  </div>
</template>

<style scoped>
@reference "../app.css";

.card {
  @apply rounded-lg border border-gray-200 bg-white p-4 shadow-sm;
}
.card-title {
  @apply mb-2 text-lg font-semibold;
}
.card-body {
  @apply text-sm text-gray-700;
}
</style>
```

ALWAYS put `@reference` as the first non-whitespace line. The path
resolves relative to the SFC file.

---

## Example 6 : Svelte component scoped @apply (v4)

`src/lib/Button.svelte` :

```svelte
<script lang="ts">
  let { children, variant = "primary" } = $props()
</script>

<button class="btn btn-{variant}">
  {@render children()}
</button>

<style>
  @reference "../app.css";

  .btn {
    @apply inline-flex items-center rounded px-4 py-2 font-medium;
  }
  .btn-primary {
    @apply bg-blue-500 text-white hover:bg-blue-600;
  }
  .btn-secondary {
    @apply bg-gray-200 text-gray-900 hover:bg-gray-300;
  }
</style>
```

Class names like `btn-{variant}` are dynamic. ALSO declare them in
`@source inline` (see `tailwind-impl-config-v4`) so the JIT scanner
generates the underlying utilities.

---

## Example 7 : CSS modules (v4)

`src/components/Button.module.css` :

```css
@reference "../app.css";

.button {
  @apply rounded bg-blue-500 px-4 py-2 text-white;
}

.disabled {
  @apply cursor-not-allowed opacity-50;
}
```

`src/components/Button.tsx` :

```tsx
import styles from "./Button.module.css"

export function Button({ disabled }: { disabled?: boolean }) {
  return (
    <button className={`${styles.button} ${disabled ? styles.disabled : ""}`}>
      Save
    </button>
  )
}
```

The `@reference` directive applies the SAME way for CSS modules as
for SFC scoped blocks.

---

## Example 8 : Important modifier inside @apply

v3 :

```css
.print-only {
  @apply block !important;
}

@media not print {
  .print-only { @apply hidden !important; }
}
```

v4 :

```css
.print-only {
  @apply block!;
}

@media not print {
  .print-only { @apply hidden!; }
}
```

ALWAYS prefer specificity / order over `!important` when possible.
Reserve `!` for utility-overriding-utility cases.

---

## Example 9 : @apply with arbitrary values

```css
@layer components {
  .ratio-12-5 {
    @apply aspect-[12/5];
  }
  .h-banner {
    @apply h-[42vh];
  }
}
```

Arbitrary values work the same inside @apply as they do in HTML.

---

## Example 10 : @apply with variants

```css
@layer components {
  .input {
    @apply w-full rounded border border-gray-300 px-3 py-2
           focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500;
  }
}
```

Variants like `focus:border-blue-500` are written exactly as in HTML.

---

## Example 11 : @apply with group / peer

```css
@layer components {
  .menu-item {
    @apply flex items-center gap-2 px-3 py-2;
  }
  .menu-item-icon {
    @apply text-gray-500 group-hover:text-blue-500;
  }
}
```

Usage :

```html
<a class="menu-item group" href="/">
  <svg class="menu-item-icon">...</svg>
  <span>Home</span>
</a>
```

The `group-hover` variant looks up the nearest ancestor with class `group`.

---

## Example 12 : Replacing @apply with a component (preferred for frameworks)

Anti-pattern (`@apply` for everything) :

```css
.btn-primary { @apply rounded bg-blue-500 px-4 py-2 text-white; }
```

```tsx
<button className="btn-primary">Save</button>
```

Preferred (React component, no @apply) :

```tsx
function Button({ children, variant = "primary" }: { children: ReactNode, variant?: "primary" | "secondary" }) {
  const base = "rounded px-4 py-2 font-medium"
  const variants = {
    primary: "bg-blue-500 text-white hover:bg-blue-600",
    secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300",
  }
  return <button className={`${base} ${variants[variant]}`}>{children}</button>
}
```

```tsx
<Button>Save</Button>
<Button variant="secondary">Cancel</Button>
```

The component version :

- Keeps utility classes visible to anyone reading the JSX.
- Type-checks variant names at compile time.
- Composes with other utilities via the `className` prop.
- Eliminates the CSS file entirely.

---

## Example 13 : Plugin ordering with @layer

```js
// tailwind.config.js (v3)
import typography from "@tailwindcss/typography"
import myButtonOverride from "./plugins/btn-override"

export default {
  plugins: [
    typography,
    myButtonOverride,
  ],
}
```

`./plugins/btn-override.js` :

```js
import plugin from "tailwindcss/plugin"

export default plugin(({ addComponents }) => {
  addComponents({
    ".prose .btn": {
      "@apply bg-purple-500 text-white": {},
    },
  })
})
```

The override runs AFTER `typography`, so its `.prose .btn` wins. ALWAYS
register override plugins last.

---

## Example 14 : Mixing v4 global @theme tokens with @apply

`src/app.css` :

```css
@import "tailwindcss";

@theme {
  --color-brand-500: oklch(0.6 0.18 250);
}

@layer components {
  .badge-brand {
    @apply rounded-full bg-brand-500 px-2 py-0.5 text-xs text-white;
  }
}
```

The token `--color-brand-500` automatically generates `bg-brand-500`,
which is now usable inside @apply.

---

## Example 15 : When @apply is wrong : extracting a single use

Anti-pattern :

```css
.welcome-heading { @apply text-4xl font-bold; }
```

```html
<h1 class="welcome-heading">Welcome</h1>
```

Preferred :

```html
<h1 class="text-4xl font-bold">Welcome</h1>
```

A single-use @apply rule trades two utility class names in HTML for a
new CSS rule + a new class name to remember. ALWAYS skip the @apply
unless the class name is reused at least 3 times.
