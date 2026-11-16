# config — methods: every directive, form, and ordering rule

Consolidated syntax reference for the v4 CSS-first configuration surface and for custom-CSS
integration (`@apply`, `@layer`, `@reference`). Worked cases: `examples.md`. Failure modes:
`anti-patterns.md`. Setup prose and the decision trees: `../method.md`.

Ownership: the v3→v4 breaking-change catalog, default-value shifts, removed config options, and the
markup-side syntax flips live in the `migration` module (`../../migration/method.md`). The
`@source inline` expansion grammar and every runtime-built class-name fix live in the
`dynamic-classes` module (`../../dynamic-classes/method.md`). Default token scales and values live
in the `design-system` module (`../../design-system/method.md`).

---

## 1. Entry directives

```css
@import "tailwindcss";                 /* theme + preflight + utilities */
@import "tailwindcss/theme";           /* default theme variables only */
@import "tailwindcss/preflight";       /* the CSS reset only */
@import "tailwindcss/utilities";       /* utilities only */
```

The full import is the only correct entry for application code. Partial imports exist to embed
Tailwind in a third-party context where exactly one layer must ship. The v3 `@tailwind` trio does not
exist in v4 and produces a build error or empty output.

## 2. `@theme` — design tokens

### Signature

```css
@theme { /* --{namespace}-{key}: value; */ }
@theme inline { ... }    /* var() refs resolved at build, value embedded in the utility */
@theme static { ... }    /* variables always emitted, even with no utility consumer */
```

A recognised namespace prefix generates the utility family for that namespace AND emits the CSS
variable. A token in no recognised namespace emits the variable only — no class is generated.

```css
@theme {
  --color-brand: oklch(0.65 0.18 252);
  --font-display: "Inter Variable", sans-serif;
  --breakpoint-3xl: 120rem;
  --spacing-128: 32rem;
}
```

### Form choice

| Situation | Form |
|---|---|
| Literal value (`oklch(...)`, `120rem`, a font stack) | `@theme` |
| Value is another custom property: `--font-sans: var(--font-inter)` | `@theme inline` |
| Token read from JS (`getComputedStyle`), a style-prop, or a non-CSS consumer | `@theme static` |
| Token must disappear when unused (bundle size) | default `@theme` — pruning is the default behaviour |

`@theme inline` substitutes the reference at build time; without it the emitted utility carries
`var(--font-sans)` → `var(--font-inter)`, and the chain resolves to nothing in any scope that does
not define the inner variable.

### Namespace reset

```css
@theme {
  --color-*: initial;    /* drop every default colour token */
  --font-*: initial;
  --*: initial;          /* drop every default token, every namespace */
  --color-primary: #1da1f2;
}
```

`@theme` is additive by default: without `initial`, custom tokens sit alongside the built-in ones and
both keep generating utilities.

### Theme namespaces

| Namespace | Powers |
|---|---|
| `--color-*` | `bg-*`, `text-*`, `border-*`, `fill-*`, `stroke-*`, `outline-*`, `divide-*`, `ring-*`, `accent-*`, `caret-*`, `from-*`, `via-*`, `to-*` |
| `--font-*` | `font-{family}` |
| `--text-*` | font-size utilities, with paired line-height |
| `--font-weight-*` | `font-{weight}` |
| `--tracking-*` | letter-spacing utilities |
| `--leading-*` | line-height utilities |
| `--spacing` | base unit for every `p-*`, `m-*`, `gap-*`, `w-*`, `h-*`, `inset-*` |
| `--spacing-*` | named spacing keys |
| `--breakpoint-*` | viewport variant prefixes (`sm:`, `md:`, `3xl:`) |
| `--container-*` | container-query variants and container sizes |
| `--radius-*` | `rounded-*` |
| `--shadow-*` | `shadow-*` |
| `--inset-shadow-*` | `inset-shadow-*` |
| `--drop-shadow-*` | `drop-shadow-*` |
| `--blur-*` | `blur-*` |
| `--perspective-*` | `perspective-*` |
| `--aspect-*` | `aspect-*` |
| `--animate-*` | `animate-*` |
| `--ease-*` | transition timing functions |
| `--tab-size-*` | `tab-*`, when paired with a custom `@utility` |

Values for these scales, and the authoritative namespace catalog (including the v3 `theme.*` key
mapping), are the `design-system` module's: `../../design-system/references/namespaces.md`. The table
above records only which utility family a namespace generates, which is config behaviour.

## 3. `@source` — content detection

```css
@source "../packages/ui/src/**/*.{vue,svelte,tsx}";  /* add a path */
@source "../node_modules/@my-org/ui-lib";            /* node_modules is skipped by default */
@source not "../legacy";                             /* exclude a path */
@source not "../tests/**/*.fixture.html";
@source none;                                        /* disable auto-detection entirely */
@source inline("...");                               /* safelist */
```

Default scanning skips `.gitignore`d files, `node_modules`, binaries, CSS files, and lockfiles.
`@source none` + explicit `@source` globs gives a strict-allow-list monorepo or sandbox build.

`@source inline(...)` forces generation of class names no source file spells out literally. The list
syntax, set/range expansion, and the strategy for interpolated names belong to the `dynamic-classes`
module.

## 4. `@plugin` — legacy JS plugins

```css
@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";
@plugin "./plugins/scrollbar.js";
```

The file exports the v3 JS plugin API (`plugin(function ({ addBase, addComponents, addUtilities,
addVariant }) { ... })`). v4 evaluates it at build time and merges its output into the matching
cascade layers (see section 10). New code uses `@utility` / `@custom-variant`; `@plugin` is for
back-compat and for plugins whose behaviour needs JS-side config reads.

## 5. `@utility` — custom utilities

### Plain form

```css
@utility content-auto { content-visibility: auto; }

@utility scrollbar-thin {
  scrollbar-width: thin;
  &::-webkit-scrollbar { width: 6px; }
}
```

One block defines one class name. The class composes with every variant: `hover:content-auto`,
`md:scrollbar-thin`, `dark:content-auto`.

### Parameterised form

```css
@utility tab-* { tab-size: --value(integer); }        /* tab-2, tab-76, tab-[1] */

@theme { --tab-size-github: 8; }
@utility tab-* { tab-size: --value(--tab-size-*); }   /* tab-github */

@utility -inset-* { inset: calc(--value([percentage], [length]) * -1); }
```

### Helper functions

| Helper | Matches | Use |
|---|---|---|
| `--value(integer)` | `tab-2`, `tab-76` | `tab-size: --value(integer)` |
| `--value([integer])` | `tab-[1]` — arbitrary value | `tab-size: --value([integer])` |
| `--value(--tab-size-*)` | `tab-github` — theme key | `tab-size: --value(--tab-size-*)` |
| `--value([length])` | `tab-[5rem]` | any length-typed property |
| `--value(integer, --default(4))` | bare `tab` falls back to 4 | default for the un-suffixed class |
| `--modifier(--leading-*, [length], [*])` | the part after `/` in `text-lg/6` | `line-height: --modifier(...)` |
| `--alpha(var(--color-lime-300) / 50%)` | alpha composition | emits `color-mix(in oklab, X 50%, transparent)` |
| `--spacing(4)` | a spacing multiple | `calc(var(--spacing) * 4)` |

Combined functional utility — one block handling theme key, arbitrary value, and modifier:

```css
@utility text-* {
  font-size: --value(--text-*, [length]);
  line-height: --modifier(--leading-*, [length], [*]);
}
/* matches text-lg, text-lg/6, text-[14px], text-[14px]/6 */
```

## 6. `@variant` — apply a variant to plain CSS

```css
.btn {
  background: white;
  color: black;

  @variant dark { background: black; color: white; }
  @variant hover, focus { background: gray; }
}
```

References variants that already exist (built-in or `@custom-variant`). A `@variant` selector inside
`@apply` is not the same thing — see section 9. Application code should use utility classes in
markup; `@variant` is for theme blocks, plugin-authored CSS, and legacy rules being moved onto tokens.

## 7. `@custom-variant` — register a variant

```css
/* shorthand */
@custom-variant dark (&:where(.dark, .dark *));
@custom-variant pointer-coarse (@media (pointer: coarse));
@custom-variant high-contrast (@media (prefers-contrast: more));
@custom-variant hover-focus (&:hover, &:focus);

/* block form — @slot marks where the styled content lands */
@custom-variant theme-midnight {
  &:where([data-theme="midnight"] *) { @slot; }
}
```

Usable immediately as `theme-midnight:bg-black`, `hover-focus:bg-blue-500`. Registering in CSS is
shorter than a JS `addVariant()` plugin, has no build-time JS dependency, and integrates directly
with the v4 compiler.

## 8. `@reference` — token visibility in scoped stylesheets (v4)

### Signature

```css
@reference "../app.css";      /* your entry file */
@reference "tailwindcss";     /* default theme only, no custom theme to point at */
```

Resolved relative to the file containing the directive: `src/components/Card.vue` → `../app.css`;
`src/components/ui/Card.vue` → `../../app.css`; or a bundler alias such as `@/app.css` when the alias
exists in the build config.

### What it loads

It parses the target file for `@theme`, `@utility`, `@custom-variant`, `@plugin`, and `@source` and
brings the results into the current parse context. Nothing is emitted: no duplicate reset, no
duplicate utilities. This is what makes `@apply` and `@variant` resolvable inside:

- Vue SFC `<style scoped>` and `<style module>`
- Svelte component `<style>`
- Astro component styles
- CSS modules (`*.module.css`)
- any per-file CSS pipeline that compiles a block in isolation

### Placement rules

First non-whitespace line of the scoped block, before any `@apply` that depends on it — parse order
matters. One call suffices; repeated calls are allowed but pointless. NEVER add it to the global
entry stylesheet (a self-reference is a no-op), and NEVER use it in v3, where the directive does not
exist and the PostCSS pipeline already provides global token visibility.

## 9. `@apply`

### Signature

```css
selector { @apply <utility> [<utility>...] [<utility>!]; }
```

The declarations of each listed utility are copied verbatim into the rule, in listed order.

### Accepted arguments

| Form | Example | Allowed |
|---|---|---|
| Plain utility | `font-bold` | Yes |
| Responsive variant | `md:text-lg` | Yes |
| State variant | `hover:bg-blue-600` | Yes |
| Group / peer variant | `group-hover:opacity-100` | Yes |
| Arbitrary value | `text-[14px]` | Yes |
| Arbitrary property | `[mask-type:luminance]` | Yes (v4) |
| Negative | `-mt-4` | Yes |
| Plugin / custom utility | `prose`, `tab-4` | Yes |
| Your own class name | `.btn` → `@apply btn` | NO |
| Marker class | `group`, `peer` | NO — a marker, not a utility |

`@apply` copies declarations, not class-name semantics. Applying `btn` fails
(`The btn class does not exist`), and applying `group` does not make children's `group-hover:*`
work. Shared recipes are re-declared, or moved into a component/mixin; `group` goes in markup.

### Placement

| Location | v3 | v4 |
|---|---|---|
| Inside a regular CSS selector | Yes | Yes |
| Inside `@layer base` / `components` / `utilities` | Yes | Yes |
| Inside a Vue/Svelte scoped style | Yes (PostCSS context) | Yes, with `@reference` |
| Inside a CSS module | Yes | Yes, with `@reference` |
| At the top level, no selector | NO | NO |
| Inside `@theme` | NO | NO |

### Variants inside an `@apply` list

Each listed variant is evaluated in isolation: `@apply hover:bg-blue-500 active:bg-blue-700`
produces two independent rules, not one intersection. For "hover AND active" write the chained form
`@apply hover:active:bg-blue-700`. For "hover OR focus" write two declarations, or register a
`@custom-variant hover-focus (&:hover, &:focus)` and apply it.

### Importance inside `@apply` — the single home for this table

| Version | Inside `@apply` |
|---|---|
| v3 | `@apply font-bold !important;` — trailing keyword; Sass/SCSS: `@apply font-bold #{!important};` |
| v4 | `@apply font-bold!;` — trailing bang attached to the utility |

In v4 the bang is per utility, so mixed importance works:

```css
.btn { @apply rounded font-bold! bg-blue-500; }   /* only font-bold is !important */
```

The two forms are not interchangeable: v4 removed the `!important` keyword inside `@apply` (the build
answers `Did you mean font-bold! instead of font-bold !important?`), and v3 does not parse the
trailing bang. In Sass, v3 needs the interpolation escape; v4 Sass uses the trailing bang and needs
nothing. How the modifier is spelled on a class in markup, and the change of that spelling between
versions, is the `migration` module's fact.

Reserve `!` for utility-overriding-utility. Reaching for it because "the styles do not apply" is a
cascade diagnosis skipped, not a fix (`anti-patterns.md` AP-12).

## 10. `@layer`

### Signature

```css
@layer base | components | utilities { /* rules with real selectors */ }
```

The three names map onto Tailwind's cascade. v4 emits native CSS cascade layers; v3 achieved the same
ordering synthetically. In both, the names are the same three buckets.

### Specificity ascends

```text
theme  <  base  <  components  <  utilities
```

A rule in a later layer beats a rule in an earlier one REGARDLESS of selector specificity. This is
the mechanism that keeps `class="btn px-2"` working: utilities are the last layer, so markup always
overrides a component recipe.

### Within one layer

Source order decides. Later wins at equal specificity. ALWAYS rely on order within a layer; NEVER on
`!important`. Two files defining the same `.btn` in `@layer components` produce a build-order
dependency that shifts between dev and prod.

### What goes where

| Rule | Layer |
|---|---|
| `body { @apply bg-gray-50 antialiased; }` | base |
| `h1 { @apply text-4xl font-bold; }` | base |
| `.btn { @apply rounded px-4 py-2; }` | components |
| `.card { @apply rounded-lg p-6 shadow-md; }` | components |
| third-party library selector override | components |
| `.text-shadow-sm { text-shadow: ...; }` | utilities |
| custom utility emitted by a plugin | utilities |

A single-purpose helper belongs in `utilities`, not `components`, so a later helper on the same
element wins.

### Rules outside every layer

Unlayered CSS is sorted AFTER the utilities layer. It beats Tailwind utilities by source order and
loses to anything later that is also unlayered. ALWAYS wrap custom CSS in a layer; stay unlayered only
when deliberately overriding utilities.

### `@layer` is not a nesting block

`@layer components { @apply rounded px-4; }` with no selector sorts nothing: the bucket takes rules,
and rules take selectors.

## 11. Plugin order and the layers

Final sort:

```text
1. @layer base         — custom base + preflight + plugin addBase()
2. @layer components   — custom components + plugin addComponents()
3. @layer utilities    — custom utilities + built-in utilities + plugin addUtilities()
```

Within a layer, plugin output follows registration order and later registrations win. A plugin's
`addUtilities()` lands in `utilities` — it does not get placed before yours. To override a plugin
class, register the override plugin AFTER the source plugin; verify the emitted order in DevTools
before touching selectors.

## 12. Build-time or runtime

`@theme`, `@source`, `@plugin`, `@utility`, `@variant`, `@custom-variant`, `@reference`, `@apply`,
and `@layer` are all resolved at build time and produce static CSS — no runtime cost. The exception
inside this module's surface is the emitted CSS variable itself: `@theme` tokens are real custom
properties, so they cascade and can be reassigned at runtime (theming), and `@theme static` exists
precisely because a JS consumer reads them after paint.

If the bundle repeats a utility's declarations everywhere a custom class appears, `@apply` replaced
a component. Measure emitted CSS in a production build before declaring the layer fine.

## 13. Directive availability by version

| Directive | v3 | v4 |
|---|---|---|
| `@apply` | Yes | Yes; importance form differs (section 9) |
| `@layer base/components/utilities` | Yes | Yes |
| `@reference` | Does not exist | REQUIRED in scoped blocks using `@apply`/`@variant` |
| `@theme`, `@utility`, `@custom-variant`, `@source`, `@plugin` | Do not exist | Yes |
| `@config` | n/a (JS config is the default) | opt-in back-compat loader |
| Scoped `@apply` resolution | PostCSS global context | file-scoped registry, needs `@reference` |
