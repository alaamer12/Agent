# Reference : @apply, @layer, @reference Methods

Exhaustive reference for every form, accepted syntax, and ordering rule.

## @apply

### Syntax

```css
selector {
  @apply <utility-class> [<utility-class>...] [!];
}
```

Each `<utility-class>` is a Tailwind utility name as written in HTML.
Variants like `hover:bg-blue-600` are allowed. The directive copies
the declarations of every listed utility into the current rule, in
listed order.

### Accepted utility forms

| Form                      | Example                       | Allowed |
| ------------------------- | ----------------------------- | ------- |
| Plain utility             | `font-bold`                   | Yes |
| Responsive variant        | `md:text-lg`                  | Yes |
| State variant             | `hover:bg-blue-600`           | Yes |
| Group / peer variant      | `group-hover:opacity-100`     | Yes |
| Arbitrary value           | `text-[14px]`                 | Yes |
| Arbitrary property        | `[mask-type:luminance]`       | Yes (v4) |
| Negative                  | `-mt-4`                       | Yes |
| Custom utility (plugin)   | `prose`                       | Yes |
| Class from another @layer | `.btn`                        | NO  |

Cannot apply your own class names. Only Tailwind utilities are valid
arguments. To reuse a custom class, name it explicitly :

```css
.btn-primary { @apply btn bg-blue-500; }   /* NOT supported */
```

ALWAYS extract shared rules into a base class and use plain CSS for
composition :

```css
.btn { @apply rounded px-4 py-2; }
.btn-primary { @apply rounded px-4 py-2 bg-blue-500 text-white; }
```

### v3 important keyword

v3 honors a trailing `!important` keyword inside @apply :

```css
.btn { @apply font-bold !important; }
```

For Sass / SCSS, escape via interpolation :

```scss
.btn { @apply font-bold #{!important}; }
```

### v4 important modifier

v4 honors a trailing bang on each utility :

```css
.btn { @apply font-bold!; }
```

ALWAYS attach the bang to the specific utility you want to force, not
to the whole rule. Multiple utilities with mixed importance :

```css
.btn { @apply rounded font-bold! bg-blue-500; }
```

Here only `font-bold` is `!important` ; `rounded` and `bg-blue-500` are not.

### Where @apply may appear

| Location                          | v3      | v4      |
| --------------------------------- | ------- | ------- |
| Inside a regular CSS selector     | Yes     | Yes     |
| Inside `@layer base/components/utilities` | Yes | Yes |
| Inside a Vue / Svelte scoped style | Yes (with PostCSS) | Yes (with @reference) |
| Inside a CSS module               | Yes     | Yes (with @reference) |
| At the top level (no selector)    | NO      | NO      |
| Inside `@theme`                   | NO      | NO      |

### Variant ordering inside @apply

Variants in the list compose left-to-right, but ALWAYS evaluate each
in isolation. `@apply hover:bg-blue-500 active:bg-blue-700` produces
two separate variant rules ; it does NOT chain them.

To chain variants, use the chained utility :

```css
.btn { @apply hover:active:bg-blue-700; }
```

## @layer

### Syntax

```css
@layer base | components | utilities {
  /* rules */
}
```

The three valid names map directly onto Tailwind's cascade :

```
@tailwind base;        →  @layer base
@tailwind components;  →  @layer components
@tailwind utilities;   →  @layer utilities
```

In v4, the cascade is built from `@import "tailwindcss"` but the three
layer names still apply.

### Specificity ascends

```
base   <  components  <  utilities
```

A rule in `utilities` always wins over a rule in `components` ; a rule
in `components` always wins over a rule in `base`, REGARDLESS of selector
specificity.

This is the whole point of the layer system : it solves the "my custom
class is overridden by Tailwind utilities" problem by guaranteeing
Tailwind utilities sit in the last layer.

### Order within a layer

CSS source order wins. Later rule beats earlier rule with the same
specificity. ALWAYS rely on order within a layer ; NEVER on `!important`.

### What goes where

| Rule type                            | Layer        |
| ------------------------------------ | ------------ |
| `h1 { @apply text-4xl; }`            | base         |
| `body { background: white; }`        | base         |
| `.btn { @apply rounded px-4; }`      | components   |
| `.card { @apply shadow rounded-lg; }` | components  |
| `.text-shadow-sm { text-shadow: ...; }` | utilities |
| Custom utility from plugin           | utilities    |

### Rules outside @layer

CSS outside any `@layer` ends up AFTER the utilities layer. It wins
over Tailwind utilities by source order but loses to anything in
`@layer utilities` that comes later. ALWAYS wrap custom CSS in a
layer ; only put rules outside a layer when you DELIBERATELY want
to override utilities.

## @reference (v4 only)

### Syntax

```css
@reference "path-to-entry-css";
```

Or for the default theme only :

```css
@reference "tailwindcss";
```

The path is resolved relative to the file containing the `@reference`.
For Vue / Svelte components that live deep in `src/components/`, that
typically resolves to `"../../app.css"` or `"~/app.css"` depending on
the bundler.

### What it does

`@reference` loads tokens, custom utilities, and custom variants from
the referenced file into the current parse context, WITHOUT emitting
the global CSS again. The file is parsed for its `@theme`, `@utility`,
`@custom-variant`, `@plugin`, and `@source` directives ; nothing else
is duplicated.

This makes @apply and @variant resolvable inside scoped contexts that
otherwise have no global CSS visibility :

- Vue SFC `<style scoped>`
- Vue SFC `<style module>`
- Svelte component `<style>` (per-file scope)
- CSS modules (`*.module.css`)
- CSS-in-JS that processes per-file

### Where to put it

The first line of the scoped block. Multiple `@reference` calls are
allowed but unnecessary ; one suffices.

```vue
<style scoped>
@reference "../app.css";

.card { @apply rounded shadow; }
</style>
```

### When NOT to use @reference

NEVER add `@reference` to your global entry CSS. The global file
already declares `@import "tailwindcss"` and any local `@theme` ; a
self-reference is a no-op and may confuse readers.

NEVER use `@reference` in v3. The directive does not exist there ; v3
relies on PostCSS context to resolve @apply.

## Plugin interaction

Plugins that emit CSS via `addBase`, `addComponents`, `addUtilities`
land in the matching layer. Order within the layer follows plugin
registration order.

```js
plugins: [
  pluginA(),
  pluginB(),
  ({ addComponents }) => {
    addComponents({
      ".btn": { /* your custom .btn */ },
    })
  },
]
```

Your inline plugin runs after `pluginA` and `pluginB`, so its
`.btn` wins. To override a plugin class, ALWAYS register your override
plugin AFTER the source plugin.

## Build-time vs runtime

@apply, @layer, and @reference are all build-time directives. They are
fully resolved during PostCSS / Vite processing and produce static CSS.
None of them have runtime cost.

If your bundle shows utility declarations duplicated everywhere `.btn`
is mentioned, @apply has been used where component extraction would be
better. ALWAYS measure the emitted CSS in production builds before
deciding the layer is "fine".
