# tailwind-impl-config-v4 : Methods Reference

Complete API surface for the v4 CSS-first configuration system.

## Every v4 Directive (full signature)

### `@import "tailwindcss"`

Loads the framework. Replaces the v3 trio `@tailwind base; @tailwind components; @tailwind utilities;`.

```css
@import "tailwindcss";                    /* full framework */
@import "tailwindcss/preflight";          /* just the CSS reset */
@import "tailwindcss/utilities";          /* utilities only */
@import "tailwindcss/theme";              /* default theme variables only */
```

### `@theme { ... }`

Define design tokens as CSS variables. Tokens in recognised namespaces auto-generate utility classes.

Variants : `@theme inline` (substitutes `var()` refs at build time), `@theme static` (always emits to output, even unused).

```css
@theme {
  --color-brand: oklch(0.65 0.18 252);
  --font-display: "Inter Variable", sans-serif;
  --breakpoint-3xl: 120rem;
  --spacing-128: 32rem;
}

@theme inline {
  --font-sans: var(--font-inter);
}

@theme static {
  --color-x: red;
}
```

Reset via `--namespace-*: initial;` or `--*: initial;` to drop defaults.

### `@source "<glob>"`

Add content-scan paths beyond the auto-detected ones. Supports `not`, `inline`, `none`.

```css
@source "../packages/ui/src/**/*.{vue,svelte,tsx}";
@source not "../legacy";
@source inline("bg-{red,blue}-{500,700}");
@source none;
```

### `@plugin "<name>"`

Load a v3-style JS plugin (CommonJS module exporting `plugin(...)`).

```css
@plugin "@tailwindcss/typography";
@plugin "./plugins/scrollbar.js";
```

### `@utility <name> { ... }`

Define a custom utility. Plain or parameterised (`name-*`).

```css
@utility content-auto { content-visibility: auto; }

@utility tab-* {
  tab-size: --value(integer);
}
```

### `@variant <name> { ... }`

Apply a variant inside a CSS rule (without writing a Tailwind class).

```css
.btn {
  @variant dark { background: black; }
  @variant hover, focus { background: gray; }
}
```

### `@custom-variant <name> (<selector>)`

Register a new variant. Shorthand or block form.

```css
@custom-variant dark (&:where(.dark, .dark *));
@custom-variant pointer-coarse (@media (pointer: coarse));

@custom-variant theme-midnight {
  &:where([data-theme="midnight"] *) { @slot; }
}
```

### `@reference "<file>"`

Import theme + custom utilities into a scoped stylesheet WITHOUT duplicating output. Required for `@apply` inside Vue SFC `<style scoped>`, Svelte component `<style>`, CSS modules.

```css
@reference "../app.css";
@reference "tailwindcss";       /* if no custom theme */
```

### `@config "<path>"`

Load a v3 `tailwind.config.js` for incremental migration. Removed v3 options (`corePlugins`, `safelist`, `separator`) are silently ignored.

```css
@config "../tailwind.config.js";
```

### `@apply <utilities>`

Inline utility declarations into a rule. Wrap in `@layer components` for cascade safety. Needs `@reference` in scoped stylesheets.

```css
@layer components {
  .btn { @apply px-4 py-2 rounded bg-blue-500; }
}
```

### `@layer base/components/utilities`

CSS-native cascade layer organisation. Order : `theme < base < components < utilities`.

```css
@layer base { h1 { font-size: var(--text-3xl); } }
@layer components { .card { @apply rounded-lg p-6; } }
@layer utilities { .text-balance { text-wrap: balance; } }
```

## Complete Theme Namespace Table

| Namespace | Powers utilities |
|-----------|------------------|
| `--color-*` | `bg-*`, `text-*`, `border-*`, `fill-*`, `stroke-*`, `outline-*`, `divide-*`, `ring-*`, `accent-*`, `caret-*`, `from-*`, `via-*`, `to-*` |
| `--font-*` | `font-sans`, `font-serif`, `font-mono`, custom families |
| `--text-*` | `text-xs` through `text-9xl` (font-size + paired line-height) |
| `--font-weight-*` | `font-bold`, `font-semibold`, `font-medium`, ... |
| `--tracking-*` | Letter spacing (`tracking-wide`) |
| `--leading-*` | Line height (`leading-tight`) |
| `--spacing` | Base unit ; powers EVERY `p-*`, `m-*`, `gap-*`, `w-*`, `h-*`, `inset-*` |
| `--spacing-*` | Named spacing keys (`p-128`, `gap-px`) |
| `--breakpoint-*` | Viewport breakpoints (`sm:`, `md:`, `3xl:`) |
| `--container-*` | Container-query sizes (`@sm:`, `@md:`, named) |
| `--radius-*` | `rounded-*` |
| `--shadow-*` | `shadow-*` |
| `--inset-shadow-*` | `inset-shadow-*` |
| `--drop-shadow-*` | `drop-shadow-*` |
| `--blur-*` | `blur-*` |
| `--perspective-*` | `perspective-*` |
| `--aspect-*` | `aspect-*` |
| `--animate-*` | `animate-*` |
| `--ease-*` | `ease-*` transition timing |
| `--tab-size-*` | `tab-*` (combined with custom utility) |

## `--value()` and Related Helpers Inside `@utility`

| Helper | Matches | Example use |
|--------|---------|-------------|
| `--value(integer)` | `tab-2`, `tab-76` (plain integer) | `tab-size: --value(integer)` |
| `--value([integer])` | `tab-[1]` (arbitrary integer) | `tab-size: --value([integer])` |
| `--value(--tab-size-*)` | `tab-github` (matches theme key) | `tab-size: --value(--tab-size-*)` |
| `--value([length])` | `--value([5rem])` | `--value([length])` |
| `--value(integer, --default(4))` | `tab` bare uses default 4 | `--value(integer, --default(4))` |
| `--modifier(--leading-*, [length])` | Reads modifier after `/` | `line-height: --modifier(--leading-*, [length], [*])` |
| `--alpha(<color> / <%>)` | Composes alpha via `color-mix` | `--alpha(var(--color-lime-300) / 50%)` |
| `--spacing(<n>)` | `calc(var(--spacing) * <n>)` | `padding: --spacing(4)` |

## v3 Options Removed in v4 (no replacement OR alternate)

| v3 option | v4 status |
|-----------|-----------|
| `corePlugins: { float: false }` | REMOVED. No replacement. |
| `safelist: [...]` | REMOVED. Use `@source inline(...)` with brace expansion. |
| `separator: '_'` | REMOVED. Always `:`. |
| `prefix: 'tw-'` | KEPT but flipped to `tw:flex` (was `tw-flex`). |
| `darkMode: 'class' | 'media' | ['class', '[data-theme=...]']` | Use `@custom-variant dark (...)` instead. |
| `important: true | '#app'` | KEPT. Append `!` at end of utility (`font-bold!`). |
| `content: [...]` | Replaced by `@source` directives + auto-detect. |
| `theme.extend` | Replaced by `@theme` (additive by default ; namespace reset via `--ns-*: initial`). |
| `plugins: [plugin(({...}) => {})]` | Replaced by `@utility`, `@custom-variant`, or `@plugin "./file.js"`. |
| `presets: [...]` | Replaced by importing other CSS files via `@import`. |

## Verified Sources

- https://tailwindcss.com/docs/functions-and-directives (all directives, full syntax)
- https://tailwindcss.com/docs/theme (namespaces, `@theme inline`, `@theme static`)
- https://tailwindcss.com/docs/adding-custom-styles (`@utility`, `@layer`, helpers)
- https://tailwindcss.com/docs/detecting-classes-in-source-files (`@source` family)
- https://tailwindcss.com/docs/upgrade-guide (removed options table)
- https://tailwindcss.com/blog/tailwindcss-v4 (overview)

Last verified : 2026-05-19.
