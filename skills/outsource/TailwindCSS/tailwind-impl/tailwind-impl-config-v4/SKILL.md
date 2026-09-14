---
name: tailwind-impl-config-v4
description: >
  Use when setting up or editing a Tailwind CSS v4 configuration via the
  CSS-first model: writing the entry stylesheet, defining design tokens
  in @theme, scoping content detection with @source, adding custom
  utilities with @utility, declaring custom variants with @custom-variant,
  wiring legacy JS plugins via @plugin, or fixing the Vue/Svelte/CSS-modules
  @apply trap with @reference. Prevents the silent-token-drop trap
  (defining @theme tokens without correct namespace prefix yields nothing),
  the lost-overrides trap (forgetting --color-*: initial before custom
  palette leaves old defaults active), the scoped-style breakage
  (@apply in Vue <style scoped> fails without @reference), the safelist
  miss (forgetting @source inline brace expansion for dynamic class names),
  and the @theme inline confusion (resolves var refs at build vs runtime).
  Covers every v4 directive (@import, @theme, @theme inline, @theme static,
  @source, @source not, @source inline, @source none, @plugin, @utility
  with --value/--modifier/--alpha/--spacing helpers, @variant,
  @custom-variant, @reference, @config, @apply, @layer), every theme
  namespace, custom-utility patterns, and JS-config back-compat.
  Keywords: tailwind v4 config, CSS-first config, @import tailwindcss,
  @theme, --color-*, --spacing, --font-*, --breakpoint-*, theme namespace,
  @theme inline, @theme static, @source, @source not, @source inline,
  brace expansion safelist, @source none, @plugin, @utility, @utility tab-*,
  --value(), --modifier(), --alpha(), --spacing(), @variant,
  @custom-variant, @reference, @config, @apply, @layer base, @layer
  components, scoped style apply, vue svelte css modules, Cannot apply
  unknown utility class, dynamic class names not detected, how do I add
  custom color tailwind v4, how to load v3 plugin in v4, where is
  tailwind.config.js v4, theme variables css variables, oklch colors,
  modern css tailwind config.
license: MIT
compatibility: "Designed for Claude Code. Requires Tailwind CSS v4.0+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# Tailwind CSS v4 CSS-First Configuration

v4 moves the entire configuration surface from JavaScript into CSS.
Tokens are CSS variables in `@theme`. Custom utilities are CSS at-rules.
Plugins, variants, and content paths all declare in CSS. The JS config
file is opt-in only, via `@config "./tailwind.config.js"`, for migration.

Companion skills :

- `tailwind-impl-config-v3` : the v3 JS-config surface (tailwind.config.js)
- `tailwind-core-v3-vs-v4` : v3-to-v4 differences across the API
- `tailwind-impl-migration-v3-v4` : automated codemod + manual steps
- `tailwind-errors-v4-migration` : trap catalogue when an upgrade breaks

## Quick Reference : The Minimum v4 Setup

```css
/* src/app.css */
@import "tailwindcss";
```

That single line replaces every v3 setup step (no JS config, no PostCSS
plugin chain, no `@tailwind` directives, no `postcss-import`, no
`autoprefixer`). Add tokens, plugins, sources, and custom utilities
below as needed.

## Directive Index

| Directive | Purpose | One-line example |
|-----------|---------|------------------|
| `@import "tailwindcss"` | Load base, components, utilities | `@import "tailwindcss";` |
| `@import "tailwindcss/preflight"` | Just the reset | partial install |
| `@import "tailwindcss/utilities"` | Just the utilities | partial install |
| `@import "tailwindcss/theme"` | Just the default theme | partial install |
| `@theme { ... }` | Define design tokens as CSS variables | `@theme { --color-brand: oklch(0.72 0.11 178); }` |
| `@theme inline { ... }` | Resolve var refs at build, inline value | `@theme inline { --font-sans: var(--font-inter); }` |
| `@theme static { ... }` | Always emit CSS variables, even if unused | `@theme static { --color-x: red; }` |
| `@source "<glob>"` | Add a content-scan path | `@source "../packages/ui";` |
| `@source not "<glob>"` | Exclude a path | `@source not "../src/legacy";` |
| `@source inline("...")` | Safelist with brace expansion | `@source inline("bg-{red,blue}-500");` |
| `@source none` | Disable automatic detection entirely | `@source none;` |
| `@plugin "name"` | Load a legacy JS plugin | `@plugin "@tailwindcss/typography";` |
| `@utility name { ... }` | Define a custom utility | `@utility tab-4 { tab-size: 4; }` |
| `@variant name { ... }` | Apply a variant inside CSS | `.x { @variant dark { background: black; } }` |
| `@custom-variant name (...)` | Register a custom variant | `@custom-variant dark (&:where(.dark, .dark *));` |
| `@reference "<file>"` | Import theme into a scoped stylesheet | `@reference "../app.css";` |
| `@config "<path>"` | Load legacy v3 JS config | `@config "./tailwind.config.js";` |
| `@apply` | Inline utilities into a rule | `.btn { @apply px-4 py-2; }` |
| `@layer base/components/utilities` | Cascade-layer organisation | `@layer base { h1 { ... } }` |

NEVER use the v3 `@tailwind base/components/utilities` directives in v4.
They are removed. Single `@import "tailwindcss"` replaces all three.

## @import : Partial Loading

```css
/* Full install (default for most projects) */
@import "tailwindcss";

/* Just the preflight reset, no utilities */
@import "tailwindcss/preflight";

/* Just utilities, no preflight (rare, but possible) */
@import "tailwindcss/utilities";

/* Just the default theme variables */
@import "tailwindcss/theme";
```

ALWAYS use the full `@import "tailwindcss"` for application code. Partial
imports exist for embedding Tailwind inside a third-party context where
you control exactly which layers to ship.

## @theme : Design Tokens as CSS Variables

```css
@import "tailwindcss";

@theme {
  /* Custom color (creates bg-mint-500, text-mint-500, etc.) */
  --color-mint-500: oklch(0.72 0.11 178);

  /* Custom font (creates font-display) */
  --font-display: "Inter Variable", "Inter", system-ui, sans-serif;

  /* Custom breakpoint (creates 3xl: variant) */
  --breakpoint-3xl: 120rem;

  /* Custom spacing key */
  --spacing-128: 32rem;
}
```

A token named `--{namespace}-{key}` automatically generates utilities. The
namespace prefix determines which utility family. Every token also becomes
a CSS custom property accessible via `var(--color-mint-500)`.

### Theme Namespaces

The full namespace table (~20 namespaces, every utility-family pairing) lives in `references/methods.md`. The most-used namespaces are `--color-*`, `--font-*`, `--text-*`, `--spacing` / `--spacing-*`, `--breakpoint-*`, `--radius-*`, `--shadow-*`. Add a token in the matching namespace and the matching utility family appears automatically.

NEVER prefix a token with a namespace Tailwind does not recognise. A token
`--brand-blue: blue` will become `var(--brand-blue)` but generates NO
utility class. Use `--color-brand-blue` to get `bg-brand-blue`,
`text-brand-blue`, and the rest.

Source : https://tailwindcss.com/docs/theme

### @theme inline vs @theme static vs default

```css
@theme {
  /* Default : creates utility class that references var(--color-x) */
  --color-x: oklch(0.72 0.11 178);
}

@theme inline {
  /* Inline : resolves var refs at build, embeds the resolved value
     in the utility class. Use when a token references ANOTHER var. */
  --font-sans: var(--font-inter);
}

@theme static {
  /* Static : always emits the CSS variable in output, even when no
     utility uses it (default behaviour omits unused tokens). */
  --color-primary: var(--color-red-500);
}
```

ALWAYS use `@theme inline` when a token's value contains another
`var(...)` reference. The default behaviour produces a chain of
references that may resolve to nothing if the outer scope changes.
ALWAYS use `@theme static` for tokens consumed only from JavaScript
(via `getComputedStyle`) where pruning would hide them.

### Resetting a Namespace

```css
@theme {
  --color-*: initial;          /* drop all default colours */
  --color-brand: #1da1f2;
  /* --*: initial;             drops EVERY default token */
}
```

## @source : Content Detection

v4 auto-scans project files for class-name tokens. Defaults skip
`.gitignore`d files, `node_modules`, binaries, CSS files, and lockfiles.

```css
/* Add a sibling package */
@source "../packages/ui/src/**/*.{html,ts,tsx,vue,svelte}";

/* Add a node_modules path (default scanner ignores node_modules) */
@source "../node_modules/@my-org/ui-lib";

/* Exclude */
@source not "../src/legacy";
@source not "../tests/**/*.fixture.html";

/* Disable automatic scanning entirely (rare) */
@source none;
```

### Safelist via @source inline

```css
/* Static list */
@source inline("bg-red-500 bg-green-500 bg-blue-500");

/* Brace expansion */
@source inline("bg-{red,green,blue}-500");

/* Range expansion (start..end..step) */
@source inline("p-{1..12}");
@source inline("opacity-{0..100..10}");

/* With variants */
@source inline("{hover:,focus:,}bg-{red,blue}-{50,{100..900..100},950}");
```

ALWAYS use `@source inline` for dynamic class names built from runtime
data (`bg-${color}-500`). NEVER rely on the scanner to find these : the
scanner is plain-text tokenisation and cannot follow string interpolation.

Source : https://tailwindcss.com/docs/detecting-classes-in-source-files

## @plugin : Legacy JS Plugins

```css
@import "tailwindcss";

@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";
@plugin "@tailwindcss/aspect-ratio";

/* Local plugin file */
@plugin "./plugins/scrollbar.js";
```

The plugin file follows the v3 plugin API (CommonJS export of
`plugin(function({ addUtilities, addVariant, ... }))`). v4 evaluates the
plugin at build time and merges its utilities, variants, and base styles
into the v4 cascade.

For new code, ALWAYS prefer `@utility` and `@custom-variant` over JS
plugins. Use `@plugin` for back-compat or for plugins that need JS-side
config logic (like Typography's `theme()` introspection).

## @utility : Custom Utilities

### Simple form

```css
@utility content-auto {
  content-visibility: auto;
}

@utility scrollbar-thin {
  scrollbar-width: thin;
  &::-webkit-scrollbar {
    width: 6px;
  }
}
```

Each `@utility` block defines ONE class name. The class works with every
variant : `hover:content-auto`, `md:scrollbar-thin`, `dark:content-auto`.

### Parameterised utilities

```css
/* Generates tab-1, tab-2, tab-76, etc. */
@utility tab-* {
  tab-size: --value(integer);
}

/* Reads from a theme namespace */
@theme {
  --tab-size-github: 8;
  --tab-size-2: 2;
  --tab-size-4: 4;
}

@utility tab-* {
  tab-size: --value(--tab-size-*);
}
```

### Helper functions inside @utility

| Helper | Purpose |
|--------|---------|
| `--value(integer)` | Match `tab-2`, `tab-76` (plain integer arg) |
| `--value([integer])` | Match `tab-[1]` (arbitrary value) |
| `--value(--tab-size-*)` | Match `tab-github` (theme key) |
| `--value([length])` | Match `--value([5rem])` length values |
| `--value(integer, --default(4))` | With default for bare `tab` |
| `--modifier(--leading-*, [length])` | Read modifier (`text-lg/6` modifier is `6`) |
| `--alpha(var(--color-lime-300) / 50%)` | Compose alpha via `color-mix(in oklab, X 50%, transparent)` |
| `--spacing(4)` | `calc(var(--spacing) * 4)` |

```css
/* Combined : matches text-lg, text-lg/6, text-[14px], text-[14px]/6 */
@utility text-* {
  font-size: --value(--text-*, [length]);
  line-height: --modifier(--leading-*, [length], [*]);
}

/* Negative parameterised utility */
@utility -inset-* {
  inset: calc(--value([percentage], [length]) * -1);
}
```

Source : https://tailwindcss.com/docs/adding-custom-styles

## @variant : Apply a Variant Inside CSS

```css
.btn {
  background: white;
  color: black;

  @variant dark {
    background: black;
    color: white;
  }

  @variant hover, focus {
    background: gray;
  }
}
```

Useful when you want to apply variant scoping to plain CSS without
writing a Tailwind class. ALWAYS prefer utility classes for new code ;
`@variant` is for legacy CSS being migrated to v4 theme tokens.

## @custom-variant : Define a New Variant

```css
/* Block form */
@custom-variant theme-midnight {
  &:where([data-theme="midnight"] *) {
    @slot;
  }
}

/* Shorthand form */
@custom-variant theme-midnight (&:where([data-theme="midnight"] *));
@custom-variant pointer-coarse (@media (pointer: coarse));
@custom-variant high-contrast (@media (prefers-contrast: more));
@custom-variant dark (&:where(.dark, .dark *));
```

Then use like any built-in variant :
```html
<button class="bg-white theme-midnight:bg-black pointer-coarse:p-4"></button>
```

v3 needed a JS plugin with `addVariant()`. v4 makes this a one-liner.

## @reference : Scoped @apply (Vue/Svelte/CSS-modules trap)

```vue
<!-- Vue SFC with scoped style -->
<style scoped>
@reference "../app.css";

.btn {
  @apply px-4 py-2 bg-blue-500 text-white;
}
</style>
```

```svelte
<!-- Svelte component -->
<style>
@reference "../app.css";

.btn {
  @apply px-4 py-2 bg-blue-500 text-white;
}
</style>
```

Without `@reference`, v4 compiles each scoped block in isolation and
throws "Cannot apply unknown utility class". The `@reference` directive
imports the theme + custom utilities WITHOUT duplicating the CSS output.

Use `@reference "tailwindcss"` for projects with no custom theme :

```css
@reference "tailwindcss";

.btn {
  @apply px-4 py-2;
}
```

ALWAYS add `@reference` to every scoped `<style>` block in Vue, Svelte,
Astro, and CSS-module projects. NEVER use `@import "tailwindcss"` inside
a scoped block ; that duplicates the entire framework into every
component's CSS output.

Source : https://tailwindcss.com/docs/functions-and-directives

## @config : Legacy JS Config Back-Compat

```css
@import "tailwindcss";
@config "../tailwind.config.js";
```

Loads a v3-style `tailwind.config.js` and merges its `theme.extend`,
`plugins`, and content paths into v4. Removed v3 options
(`corePlugins`, `safelist`, `separator`, `resolveConfig`) are silently
ignored. Use this for incremental migration only.

NEVER define the same token in BOTH `@theme` AND the JS config's
`theme.extend`. Behaviour is unspecified ; the safer rule is
"migrate per token category, in one commit".

## @apply : Inline Utilities

```css
@layer components {
  .btn {
    @apply px-4 py-2 rounded-md bg-blue-500 text-white;
  }

  .card {
    @apply rounded-lg p-6 shadow-md;
  }
}
```

ALWAYS wrap `@apply` blocks in `@layer components` (or another layer) so
utility classes from the user's HTML can still override them. NEVER
declare apply rules at the top level ; they then sit in the same cascade
layer as utilities and lose to almost nothing.

`@apply` needs theme context. In scoped contexts (Vue, Svelte, CSS
modules) add `@reference` first ; see the section above.

## @layer : Cascade-Layer Organisation

```css
@import "tailwindcss";

@layer base {
  h1 { font-size: var(--text-3xl); font-weight: bold; }
  h2 { font-size: var(--text-2xl); }
}

@layer components {
  .card {
    background: var(--color-white);
    border-radius: var(--radius-lg);
    padding: --spacing(6);
  }
}

@layer utilities {
  .text-balance { text-wrap: balance; }
}
```

v4 uses native CSS `@layer` (cascade layers) instead of v3's synthetic
ordering. Layers cascade in declared order : `theme < base < components <
utilities`. Utilities ALWAYS win over components ; components win over
base.

## Complete v4 Stylesheet Example

See `references/examples.md` for a full annotated `app.css` that combines `@theme`, `@plugin`, `@source`, `@custom-variant`, `@utility`, and `@layer` into a production-grade configuration.

## Reference Files

- `references/methods.md` : every directive with full syntax, every theme
  namespace, every --value helper, browser baseline
- `references/examples.md` : minimal + full stylesheet, scoped styles
  setup, partial-import use cases, dynamic class safelist, framework
  integrations (Vite, PostCSS, Next.js, Astro)
- `references/anti-patterns.md` : silent token drop, missing @reference,
  hard-coded namespace, @apply outside @layer, JS config mixed with @theme

## Verified Sources

- https://tailwindcss.com/docs/functions-and-directives (every directive)
- https://tailwindcss.com/docs/theme (namespaces, inline, static)
- https://tailwindcss.com/docs/adding-custom-styles (@utility, @layer)
- https://tailwindcss.com/docs/detecting-classes-in-source-files (@source)
- https://tailwindcss.com/blog/tailwindcss-v4 (rationale + overview)
