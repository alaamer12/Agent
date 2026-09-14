---
name: tailwind-impl-apply-directive
description: >
  Use when writing custom CSS that needs to share design tokens with
  Tailwind utilities via @apply, organizing component / base / utility
  CSS via @layer, or fixing the "Cannot apply unknown utility class"
  error in Vue, Svelte, or CSS-module scoped styles by adding
  @reference. Prevents the utility-extraction anti-pattern (wrapping
  every utility in @apply destroys utility-first benefits like JIT
  pruning, in-context readability, and consistent design tokens), the
  scoped-style trap in v4 (Vue SFC, Svelte SFC, and CSS modules
  evaluate @apply against an empty token registry without @reference,
  failing with "Cannot apply unknown utility class"), the layer-order
  trap (custom CSS outside @layer leaks above utilities and gets
  overridden), the important-modifier syntax flip between v3
  (leading bang, !font-bold) and v4 (trailing bang, font-bold!), and
  the @apply !important keyword vs modifier confusion. Covers @apply
  semantics (copies utility declarations into the current rule),
  @layer base / components / utilities (specificity ascends in that
  order, matches @tailwind ordering in v3 and @import "tailwindcss"
  cascade in v4), @reference "path" (v4 only, makes tokens visible
  in scoped contexts without duplicating CSS), the v3 vs v4 important
  syntax flip, plugin-vs-layer ordering, and when @apply is the right
  tool versus when component extraction (React / Vue / Svelte
  component) is the right tool instead.
  Keywords: tailwind @apply, @apply utility, apply directive,
  custom CSS tailwind, share tokens custom CSS, @layer base
  components utilities, layer order tailwind, tailwind 3
  @apply !important, tailwind 4 @apply font-bold!, important
  modifier tailwind, !font-bold v3, font-bold! v4, leading
  bang vs trailing bang, @reference tailwindcss, @reference
  app.css, Cannot apply unknown utility class, Cannot apply
  unknown utility, vue scoped style apply, svelte scoped
  style apply, css modules apply, scoped @apply broken v4,
  tailwind component extraction, when not to use @apply,
  @apply anti pattern, button class @apply, when to extract
  utilities, plugin order @layer, third-party library
  override tailwind, override third party styles, @apply
  inside scoped style, tailwind 3-4 directive differences.
license: MIT
compatibility: "Designed for Claude Code. Requires Tailwind CSS v3.4 or v4.0+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# @apply, @layer, @reference

`@apply` lets custom CSS reuse Tailwind utility declarations. `@layer`
sorts custom CSS into Tailwind's cascade. `@reference` (v4) makes
tokens visible inside scoped style blocks.

ALWAYS prefer component extraction (React, Vue, Svelte component)
over @apply when the consumer is a component framework. NEVER reach
for @apply just because a class name appears twice. See
`references/anti-patterns.md` AP-1 for the full philosophy.

Companion skills :

- `tailwind-impl-config-v3` : v3 JS-config and PostCSS pipeline
- `tailwind-impl-config-v4` : v4 CSS-first config and directives
- `tailwind-impl-build-vite` : Vite plugin wiring

## Quick Reference

### @apply (both versions)

```css
.btn-primary {
  @apply rounded-lg bg-blue-500 px-4 py-2 text-white;
}
```

ALWAYS use inside a regular CSS selector, NEVER at the top level. The
declarations are copied verbatim from the utility class into the rule.

### @layer (both versions)

```css
@layer base {
  h1 { @apply text-4xl font-bold; }
}

@layer components {
  .btn { @apply rounded bg-blue-500 px-4 py-2 text-white; }
}

@layer utilities {
  .text-shadow-sm { text-shadow: 0 1px 2px rgb(0 0 0 / 0.1); }
}
```

Order in the cascade : `base < components < utilities`. Anything in
`utilities` wins over `components` ; anything in `components` wins
over `base`.

### @reference (v4 only)

```vue
<style scoped>
@reference "../app.css";

.card { @apply rounded bg-white shadow; }
</style>
```

The first line MUST be `@reference` when the scoped block uses
`@apply` or `@variant`. Without it, v4 raises `Cannot apply unknown
utility class`.

### Important modifier syntax flip

| Version | In HTML class    | Inside @apply                       |
| ------- | ---------------- | ----------------------------------- |
| v3      | `!font-bold`     | `@apply font-bold !important;`      |
| v4      | `font-bold!`     | `@apply font-bold!;`                |

NEVER write `!font-bold` in v4. NEVER write `font-bold!` in v3.

## Decision Trees

### Should I use @apply or extract a component ?

```
Are you in a component framework (React, Vue, Svelte, Solid) ?
├── Yes : ALWAYS extract a component. Pass props for variants.
│        @apply is the wrong tool inside a framework that already
│        gives you component reuse with type-checked props.
└── No  : continue
Is the consumer plain HTML, MDX, or a CMS template ?
├── Yes : @apply is acceptable for shared class names (.btn, .card).
│        Document the class semantics next to the @apply rule.
└── No  : continue
Is this a third-party-library override
(react-select dropdown, Algolia DocSearch, embedded widget) ?
├── Yes : @apply is the right tool. The library owns the markup ;
│        you can only style it from outside.
└── No  : revisit. Most uses of @apply outside the above two cases
         are utility hiding, not utility reuse.
```

### Which @layer should this rule go in ?

```
What kind of CSS am I adding ?
├── Global element default (h1, p, body)        : @layer base
├── Named, multi-utility component class (.btn) : @layer components
├── Single-purpose helper class (.text-shadow)  : @layer utilities
└── None : Tailwind will sort it AFTER utilities. Almost always wrong.
```

### My @apply errors with "Cannot apply unknown utility class". Why ?

```
v3 or v4 ?
├── v3 : the utility is not generated.
│        - JIT did not see the class in any scanned file
│        - The class is typo'd or uses a custom token that is not
│          registered in tailwind.config.js theme
│        Fix : add the file to content, fix the typo, or extend the theme.
└── v4 : you are inside a scoped style block (Vue, Svelte, CSS module).
         Tokens are not visible there by default.
         Fix : add `@reference "../app.css";` as the FIRST line of the
         scoped block. The path points to your global entry CSS.
```

## Patterns

### Pattern : extracting a component class

```css
@layer components {
  .btn {
    @apply inline-flex items-center rounded px-4 py-2 font-medium;
  }
  .btn-primary {
    @apply btn bg-blue-500 text-white hover:bg-blue-600;
  }
}
```

ALWAYS put @apply rules inside `@layer components`. Without the layer,
the rule lands after Tailwind utilities, so `class="btn px-2"` cannot
override the layer's `px-4` without `!`.

### Pattern : overriding third-party widget CSS

```css
@layer components {
  .select2-dropdown {
    @apply rounded-b-lg shadow-md;
  }
  .ais-SearchBox-input {
    @apply rounded border border-gray-300 px-3 py-2;
  }
}
```

When the library renders markup you do not control, @apply is the
clean bridge between your design tokens and their selectors.

### Pattern : base layer for element defaults

```css
@layer base {
  body {
    @apply bg-gray-50 text-gray-900 antialiased;
  }
  h1 { @apply text-4xl font-bold tracking-tight; }
  h2 { @apply text-3xl font-semibold; }
}
```

Base layer rules apply to every matching element without needing a
class. ALWAYS use base for "every h1 should look like this" not
"this specific h1 should look like this".

### Pattern : v4 scoped @apply in Vue / Svelte

Vue SFC :

```vue
<script setup lang="ts">
import "./style.css"
</script>

<template>
  <button class="btn">Save</button>
</template>

<style scoped>
@reference "./style.css";

.btn {
  @apply rounded bg-blue-500 px-4 py-2 text-white;
}
</style>
```

Svelte component :

```svelte
<style>
  @reference "../app.css";

  h1 { @apply text-3xl font-bold; }
</style>
```

The `@reference` line is REQUIRED in v4 for scoped @apply. It loads
the token registry into the file's parse context WITHOUT emitting
the global CSS again.

### Pattern : !important modifier

v3 in HTML :

```html
<button class="!font-bold">Force bold</button>
```

v3 inside @apply :

```css
.btn { @apply font-bold !important; }
```

v4 in HTML :

```html
<button class="font-bold!">Force bold</button>
```

v4 inside @apply :

```css
.btn { @apply font-bold!; }
```

NEVER mix the syntaxes. The v3 leading-bang form does NOT parse in v4.

## Anti-Patterns (summary)

NEVER wrap every reused utility set in @apply. Component extraction
(React/Vue/Svelte component with props) is the right tool inside a
component framework.

NEVER put @apply rules outside `@layer`. They land after Tailwind's
utility layer and lose all override behavior.

NEVER omit `@reference` in v4 Vue / Svelte / CSS-modules scoped styles
that use @apply. The error is always "Cannot apply unknown utility class".

NEVER mix `!font-bold` (v3) and `font-bold!` (v4) syntax across versions.

NEVER use @apply for a single utility. `class="font-bold"` in the
template is already that.

See `references/anti-patterns.md` for the full catalog.

## Plugin Order and @layer Interaction

Tailwind sorts the final CSS as :

1. `@layer base` (your custom base + Tailwind preflight)
2. `@layer components` (your component classes + plugin component classes)
3. `@layer utilities` (your utility classes + Tailwind utilities + plugin utilities)

A custom utility class declared via `@layer utilities` competes with
Tailwind utilities at the same specificity. ALWAYS rely on order
within the layer (later wins) rather than `!important`.

Plugins that register utilities or components inject INTO these layers.
A `addUtilities({ ... })` call lands in `utilities`, NOT before yours.
ALWAYS verify final order in DevTools when a plugin override misbehaves.

## v3 vs v4 Differences

| Feature                  | v3                                       | v4                                       |
| ------------------------ | ---------------------------------------- | ---------------------------------------- |
| @apply syntax            | `@apply font-bold;`                      | `@apply font-bold;`                      |
| Important inside @apply  | `@apply font-bold !important;`           | `@apply font-bold!;`                     |
| Important in HTML        | `class="!font-bold"`                     | `class="font-bold!"`                     |
| @layer support           | `@layer base/components/utilities`       | `@layer base/components/utilities`       |
| @reference               | NOT supported (not needed)               | REQUIRED in scoped style blocks          |
| Scoped @apply works ?    | Yes, via PostCSS context                 | Only with `@reference`                   |

## Reference Links

- `references/methods.md` : every directive's exact syntax, accepted
  forms, order rules, layer semantics
- `references/examples.md` : full patterns for components, layered
  base styles, scoped @apply in Vue/Svelte/CSS modules
- `references/anti-patterns.md` : utility-hiding mistakes, scoped-style
  errors, layer mistakes, important syntax errors

## Sources

- v4 directives reference : https://tailwindcss.com/docs/functions-and-directives
- v3 directives reference : https://v3.tailwindcss.com/docs/functions-and-directives
- v4 scoped @apply trap : https://github.com/tailwindlabs/tailwindcss/issues/16346
- L-002 (project lesson) : v4 scoped style + @apply ALWAYS needs @reference
