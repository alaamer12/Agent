# config — Tailwind v4 CSS-first setup, @apply, @layer, @reference

v4 puts the entire configuration surface in CSS: design tokens as variables in `@theme`, custom
utilities and variants as at-rules, content paths and legacy plugins declared in the stylesheet.
That same stylesheet is where hand-written CSS meets the utility layer — `@apply` copies utility
declarations into a rule, `@layer` places a rule inside Tailwind's cascade, `@reference` makes the
theme visible to a scoped block. One entry CSS file does both jobs: configure the framework and
integrate custom CSS.

## Who owns which fact

| Fact | Owner |
|---|---|
| v3→v4 breaking changes, default-value shifts, removed config options, syntax flips (variant stacking, important modifier, prefix), utility renames, hover gating | the `migration` module — `../migration/method.md` |
| The `@source inline` brace/range expansion grammar, and every fix for class names assembled at runtime | the `dynamic-classes` module — `../dynamic-classes/method.md` |
| The default token scales and their values | the `design-system` module — `../design-system/method.md` |

Rules below are the config/integration surface only. Where a rule touches an owned-elsewhere fact it
links out instead of restating it. Never fork the same fact into two modules.

## Entry setup

```css
/* src/app.css */
@import "tailwindcss";
```

That one line is the framework: base reset, theme variables, utilities. No JS config file, no
PostCSS plugin chain, no `@tailwind base/components/utilities` trio, no `postcss-import`, no
`autoprefixer`. NEVER write the v3 `@tailwind` directives in a v4 stylesheet — they are gone; the
single import replaces all three.

Partial loading exists for embedding Tailwind inside a third-party context where you choose which
layers to ship:

```css
@import "tailwindcss/theme";       /* default theme variables only */
@import "tailwindcss/preflight";   /* the reset only */
@import "tailwindcss/utilities";   /* utilities only */
```

ALWAYS use the full `@import "tailwindcss"` for application code. Partial imports are for library
and widget bundles, not a bundle-size trick; a partial import that omits `theme` or `utilities`
silently removes the utilities the markup expects.

## Directive index

| Directive | Purpose | One-line form |
|---|---|---|
| `@import "tailwindcss"` | Load base + theme + utilities | `@import "tailwindcss";` |
| `@theme { ... }` | Design tokens as CSS variables; generates the matching utility families | `@theme { --color-brand: oklch(0.65 0.18 252); }` |
| `@theme inline { ... }` | Resolve `var()` refs at build, embed the value in the utility | `@theme inline { --font-sans: var(--font-inter); }` |
| `@theme static { ... }` | Emit the variables even when no utility uses them | `@theme static { --color-x: red; }` |
| `@source "<glob>"` | Add a content-scan path | `@source "../packages/ui";` |
| `@source not "<glob>"` | Exclude a path | `@source not "../src/legacy";` |
| `@source inline("...")` | Safelist classes no file spells out literally | `@source inline("bg-red-500");` — grammar: the `dynamic-classes` module |
| `@source none` | Disable automatic detection | `@source none;` |
| `@plugin "<name>"` | Load a legacy JS plugin | `@plugin "@tailwindcss/typography";` |
| `@utility name { ... }` | Define one custom utility class | `@utility tab-4 { tab-size: 4; }` |
| `@variant name { ... }` | Apply an existing variant to plain CSS | `.btn { @variant dark { ... } }` |
| `@custom-variant name (...)` | Register a new variant | `@custom-variant dark (&:where(.dark, .dark *));` |
| `@reference "<file>"` | Import theme + utilities + variants into a scoped block, no output | `@reference "../app.css";` |
| `@config "<path>"` | Load a legacy JS config for migration | `@config "./tailwind.config.js";` |
| `@apply` | Inline utility declarations into a rule | `.btn { @apply px-4 py-2; }` |
| `@layer base/components/utilities` | Cascade-layer placement of custom CSS | `@layer base { h1 { ... } }` |

Full signatures, every accepted form, and the ordering rules: `references/methods.md`.

## @theme — tokens, variants of the block, namespace reset

```css
@theme {
  --color-mint-500: oklch(0.72 0.11 178);                 /* bg-mint-500, text-mint-500, ... */
  --font-display: "Inter Variable", "Inter", system-ui, sans-serif;  /* font-display */
  --breakpoint-3xl: 120rem;                               /* 3xl: variant */
  --spacing-128: 32rem;                                   /* p-128, w-128, ... */
}
```

A token written as `--{namespace}-{key}` generates the utility family that owns the namespace, and
stays readable as a CSS variable (`var(--color-mint-500)`). NEVER name a token outside a recognised
namespace: `--brand-blue: blue` emits `var(--brand-blue)` and generates NO class. Write
`--color-brand-blue` to get `bg-brand-blue`, `text-brand-blue`, `border-brand-blue`.

Three forms, decided by what the value contains and who consumes it:

| Form | Behaviour | Use when |
|---|---|---|
| `@theme` | Emits the variable; the utility references `var(--token)` | Plain literal values (default) |
| `@theme inline` | Substitutes `var()` refs at build; the utility carries the resolved value | The token's value is another `var(...)` |
| `@theme static` | Always emits the variable, even with no consumer | JS reads the token (`getComputedStyle`), pruning would hide it |

ALWAYS use `@theme inline` when a token references another variable — the default form emits a
reference chain that resolves to nothing when the outer scope does not define the inner variable.

Namespace reset — the defaults are additive until you clear them:

```css
@theme {
  --color-*: initial;        /* drop every default colour */
  --color-primary: #1da1f2;
  /* --*: initial;          drops every default token in every namespace */
}
```

Forbidding `--color-*` while adding brand colours is the difference between "custom palette" and
"custom palette plus 300 default colours still generated and still usable".

## @source — content detection

v4 scans project files for class-name tokens by itself. The defaults skip `.gitignore`d paths,
`node_modules`, binaries, CSS files, and lockfiles.

```css
@source "../packages/ui/src/**/*.{html,ts,tsx,vue,svelte}";  /* another package */
@source "../node_modules/@my-org/ui-lib";                    /* shipped UI library */
@source not "../src/legacy";                                 /* exclude */
@source not "../tests/**/*.fixture.html";
@source none;                                                /* explicit allow-list only */
```

`@source none` plus explicit `@source` globs is the monorepo/storybook isolation shape: nothing
escapes detection by accident.

Safelisting uses `@source inline("...")`. ALWAYS use it when a class name genuinely exists only at
runtime — the scanner is plain-text tokenisation and cannot follow interpolation. The expansion
grammar (lists, brace sets, ranges, variant prefixes) and the whole dynamic-class question belong
to the `dynamic-classes` module: `../dynamic-classes/method.md`.

## @plugin and @config — legacy JS surface

```css
@plugin "@tailwindcss/typography";
@plugin "./plugins/scrollbar.js";
```

The plugin file still follows the v3 JS plugin API (a CommonJS `plugin(function ({ addUtilities,
addComponents, addVariant }){})`); v4 evaluates it at build and merges its output into the cascade.
For new code ALWAYS prefer `@utility` and `@custom-variant`; keep `@plugin` for back-compat and for
plugins whose logic needs JS-side config reads.

```css
@import "tailwindcss";
@config "../tailwind.config.js";
```

`@config` merges the legacy file's theme extensions, plugins, and content paths into v4 and ignores
without warning the options v4 no longer supports — the list of what is gone is the `migration`
module's. Use it for incremental migration only. NEVER define the same token in BOTH `@theme` and
the loaded JS config: v4 does not guarantee a merge order, so the value differs per build. Migrate
per token category, in one commit, and delete the JS entry when that category is done.

## @utility — custom utilities

```css
@utility content-auto {
  content-visibility: auto;
}

@utility scrollbar-thin {
  scrollbar-width: thin;
  &::-webkit-scrollbar { width: 6px; }
}
```

One `@utility` block defines ONE class name, and it works with every variant for free:
`hover:content-auto`, `md:scrollbar-thin`, `dark:content-auto`. That is the whole reason to use
`@utility` over a hand-written class.

Parameterised utilities take the value from the class name:

```css
@theme {
  --tab-size-github: 8;
}

@utility tab-* {
  tab-size: --value(integer);          /* tab-2, tab-76 */
  /* tab-size: --value(--tab-size-*);  tab-github — reads the namespace */
}

@utility -inset-* {
  inset: calc(--value([percentage], [length]) * -1);
}
```

Helpers inside `@utility`: `--value(...)` (integer / arbitrary `[...]` / theme namespace, with
`--default()`), `--modifier(...)` for the part after `/`, `--alpha(... / 50%)` for `color-mix`,
`--spacing(4)` for `calc(var(--spacing) * 4)`. Full table and the combined `text-*` form:
`references/methods.md`.

## @variant and @custom-variant

`@custom-variant` registers a new variant; `@variant` applies an existing one inside CSS.

```css
@custom-variant dark (&:where(.dark, .dark *));
@custom-variant pointer-coarse (@media (pointer: coarse));
@custom-variant high-contrast (@media (prefers-contrast: more));

@custom-variant theme-midnight {                       /* block form */
  &:where([data-theme="midnight"] *) { @slot; }
}
```

Then use it like any built-in: `theme-midnight:bg-black`, `pointer-coarse:p-4`. Block form needs
`@slot` where the styled content goes; shorthand form is one line.

```css
.btn {
  background: white;
  @variant dark { background: black; color: white; }
  @variant hover, focus { background: gray; }
}
```

`@variant` is for scoping plain CSS — theme blocks, legacy CSS being brought onto v4 tokens. ALWAYS
prefer real utility classes in markup for new application code; a `@variant` rule is invisible to
the scanner and unsearchable from the call site.

## @apply — reuse, or extract a component

`@apply` copies the declarations of the listed utilities into the current rule, in listed order,
verbatim. Variants, arbitrary values, negatives, and plugin utilities are valid arguments; your own
class names are not.

```css
@layer components {
  .btn { @apply inline-flex items-center rounded px-4 py-2 font-medium; }
}
```

ALWAYS wrap `@apply` rules in `@layer` (usually `components`). At the top level the rule lands after
Tailwind's utilities, so `class="btn px-2"` cannot override `.btn`'s `px-4` without `!`. NEVER
`@apply` at the top level or inside `@theme`.

### Should I use @apply, or extract a component?

```text
In a component framework (React, Vue, Svelte, Solid)?
├── Yes: extract a component and pass props for variants.
│        @apply is the wrong tool where the platform already gives type-checked reuse.
└── No: continue.
Consumer is plain HTML, MDX, or a CMS template?
├── Yes: @apply is fine for a genuinely shared name (.btn, .card).
│        Document the class semantics next to the rule.
└── No: continue.
Third-party library override (select widget, search box, embedded iframe content)?
├── Yes: @apply is the right tool — the library owns the markup, you can only style it from outside.
└── No: revisit. Most remaining uses hide utilities rather than reuse them.
```

Reusable test: the class name earns a rule only when it repeats. ONE use is not extraction, it is a
second name to remember plus a CSS file to open (`references/anti-patterns.md` AP-8). What happens to
the markup after the decision — the counting of repeats, grouping a long class list, sorting
tooling, and `clsx`/`twMerge` — is the `utility-soup` module's (`../utility-soup/method.md`); this
module owns only the directive that writes the recipe.

### Which layer?

```text
Global element default (every h1, body, a)        -> @layer base
Named multi-utility component class (.btn, .card) -> @layer components
Single-purpose helper (.text-shadow-sm)           -> @layer utilities
No layer                                          -> lands after utilities; almost always wrong
```

### Importance inside @apply

In a v4 stylesheet the only accepted form is the bang attached to the individual utility:
`@apply font-bold!`. It is per utility, so one forced declaration inside a longer list is legal. The
legacy keyword form and the Sass spelling, in one table with the reasons, are
`references/methods.md` section 9; how the modifier is written on a class in markup is the
`migration` module's fact.

## @layer — cascade order

v4 uses native CSS cascade layers. Declared order ascends:

```text
theme  <  base  <  components  <  utilities
```

A rule in `utilities` beats `components` beats `base` REGARDLESS of selector specificity — that is
the point: Tailwind utilities sit in the last layer, so markup always wins over a component recipe.
Within one layer, source order wins; ALWAYS rely on order rather than `!important`.

CSS outside every `@layer` ends up AFTER the utilities layer: it overrides utilities by source order
and loses to later same-layer rules. Deliberate escape hatch, not a place to park component CSS.
Rules inside `@layer` need real selectors — `@layer` is a sorting bucket, not a nesting scope.

## @reference — scoped stylesheets (Vue, Svelte, CSS modules)

```vue
<style scoped>
@reference "../app.css";

.btn { @apply px-4 py-2 bg-blue-500 text-white; }
</style>
```

A scoped block is compiled in isolation: it cannot see the theme or the custom utilities, and
`@apply` fails with **`Cannot apply unknown utility class`**. `@reference` imports the referenced
file's `@theme`, `@utility`, `@custom-variant`, `@plugin`, and `@source` results into the current
parse context WITHOUT emitting the CSS again. It is required whenever a scoped block uses `@apply`
or `@variant`, and must be the FIRST line — parse order matters, a `@reference` after the `@apply`
does not help.

```css
@reference "tailwindcss";   /* no custom theme to point at */
```

Rules: ALWAYS `@reference` in every Vue `<style scoped>` / `<style module>`, Svelte `<style>`,
Astro, and `*.module.css` block that uses `@apply`. NEVER `@import "tailwindcss"` there — that
duplicates the whole framework into every component's output. NEVER add `@reference` to the global
entry CSS; a self-reference is a no-op that confuses readers. The path resolves relative to the
file containing the directive (`src/components/ui/Card.vue` → `../../app.css`), and `@reference`
does not exist in v3.

## Plugin order and the layers

Tailwind sorts the final CSS as:

```text
1. @layer base         — your base + preflight + plugin addBase()
2. @layer components   — your components + plugin addComponents()
3. @layer utilities    — your utilities + built-in utilities + plugin addUtilities()
```

Plugins inject INTO these layers, in registration order, and later wins inside the layer. So an
override plugin must be registered AFTER the plugin it overrides. A custom utility in
`@layer utilities` competes with built-in utilities at equal specificity — order decides. When a
plugin override misbehaves, verify the emitted order in DevTools before changing selectors.
`references/examples.md` example 20 shows the registration order.

## The v4 stylesheet, in order

```css
@import "tailwindcss";

@plugin "@tailwindcss/typography";        /* 1. legacy JS surface first */

@theme {                                   /* 2. tokens: everything below consumes them */
  --color-brand-500: oklch(0.65 0.18 252);
  --font-display: "Inter Variable", system-ui, sans-serif;
  --breakpoint-3xl: 120rem;
}

@custom-variant dark (&:where(.dark, .dark *));   /* 3. variants */

@source "../packages/ui/src/**/*.{ts,tsx,vue}";   /* 4. content scope */

@utility tab-* { tab-size: --value(integer); }    /* 5. custom utilities */

@layer base {                                     /* 6. element defaults */
  h1 { font-family: var(--font-display); font-size: var(--text-4xl); }
}

@layer components {                               /* 7. component recipes */
  .card { @apply rounded-lg bg-white p-6 shadow-md; }
}
```

Order is a dependency chain, not style: theme before anything that consumes it, variants before
`@apply` that uses them, sources and safelists beside the content they describe. Full annotated
`app.css`, framework wiring, and scoped-style setups: `references/examples.md`.

## Procedure

1. Write the entry file: `@import "tailwindcss";` and nothing else until it builds.
2. Add `@theme` tokens in the correct namespace; reset a namespace before replacing it.
3. Register variants with `@custom-variant`; wire legacy JS with `@plugin`, `@config` only while
   migrating.
4. Widen content scope with `@source` before debugging "class not generated"; safelist only genuine
   runtime names (see the `dynamic-classes` module).
5. Reach for `@utility`, then `@layer`, then `@apply` — in that order — and run the extraction
   decision tree before writing any `@apply` rule inside a component framework.
6. Add `@reference` as the first line of every scoped block that uses `@apply` or `@variant`.
7. Measure the emitted CSS in the production build. Declarations duplicated everywhere `.btn`
   appears means `@apply` is doing a component's job.

## Anti-pattern index

Full catalog — symptom, cause, fix — in `references/anti-patterns.md`, grouped as:

| Group | Entries |
|---|---|
| Configuration surface: `@tailwind` leftovers, namespace-less tokens, `var()` chains, `@import` in a scoped block, dual token sources, JS plugin doing CSS work | AP-1 … AP-6 |
| `@apply` scope: utility hiding instead of extraction, single-use rules, missing `@layer`, own class names | AP-7 … AP-10 |
| `@reference`: missing, unresolvable path, wrong position, wrong version | AP-11 … AP-14 |
| Cascade and variants: layer choice, variant chaining, marker classes, importance form, `!important` as an escape hatch, plugin order, `@layer` misuse, duplicate definitions | AP-15 … AP-22 |
| Not config bugs: dev-server staleness, runtime-built class names, removed v3 options | AP-23 … AP-25 |

## Resources

- `references/methods.md` — every directive signature, theme namespaces, `@utility` helpers, `@apply`
  accepted forms and placement, `@layer` semantics, `@reference` scope, plugin order, build-time cost
- `references/examples.md` — production `app.css`, bundler wiring, scoped Vue/Svelte/CSS-module
  setups, component recipes, extraction, plugin ordering
- `references/anti-patterns.md` — the catalog above with symptom, cause, fix

## Sources

- https://tailwindcss.com/docs/functions-and-directives
- https://v3.tailwindcss.com/docs/functions-and-directives
- https://tailwindcss.com/docs/theme
- https://tailwindcss.com/docs/adding-custom-styles
- https://tailwindcss.com/docs/detecting-classes-in-source-files
- https://tailwindcss.com/docs/installation/using-vite
- https://tailwindcss.com/docs/installation/using-postcss
- https://tailwindcss.com/docs/installation/framework-guides/nextjs
- https://tailwindcss.com/blog/tailwindcss-v4
- https://github.com/tailwindlabs/tailwindcss/issues/16346 — scoped `@apply` requires `@reference`
- https://github.com/tailwindlabs/tailwindcss/issues/18136 — runtime-built class names are invisible
  to the scanner (fix owned by the `dynamic-classes` module)
