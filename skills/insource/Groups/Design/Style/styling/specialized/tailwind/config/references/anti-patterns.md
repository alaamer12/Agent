# config — anti-patterns

Every mistake this module's surface produces, with the symptom, the cause, and the fix. Grouped:
configuration surface AP-1 … AP-6, `@apply` scope AP-7 … AP-10, `@reference` AP-11 … AP-14, cascade
and variants AP-15 … AP-22, not-config AP-23 … AP-25. Syntax: `methods.md`. Correct shapes:
`examples.md`.

Upgrade-breaking-change catalogs, default-value shifts, removed config options, and markup-side
syntax flips are the `migration` module's (`../../migration/method.md`) and are not repeated here.
Runtime-built class names and `@source inline` expansion are the `dynamic-classes` module's
(`../../dynamic-classes/method.md`).

---

## Configuration surface

### AP-1: v3 `@tailwind` directives in a v4 stylesheet

**Symptom**: build error, or a file that emits nothing.

```css
/* WRONG */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**Cause**: the three directives were a v3 PostCSS-era mechanism.

**Fix** :

```css
/* RIGHT */
@import "tailwindcss";
```

Partial imports (`theme`, `preflight`, `utilities`) exist only for embedding one layer into a
third-party bundle. The rest of the v3 entry pipeline is catalogued in the `migration` module.

### AP-2: token outside a recognised namespace

**Symptom**: `var(--brand-blue)` works; `bg-brand-blue` never generates.

```css
/* WRONG */
@theme { --brand-blue: #1da1f2; }
```

**Cause**: utilities are generated from namespace prefixes (`--color-*`, `--font-*`, `--spacing-*`,
`--radius-*`, …). A token in no namespace is a plain custom property as far as the compiler cares.

**Fix** :

```css
/* RIGHT */
@theme { --color-brand-blue: #1da1f2; }   /* bg-brand-blue, text-brand-blue, border-brand-blue */
```

Namespace to family mapping: `methods.md` section 2.

### AP-3: `var()` chain inside a plain `@theme`

**Symptom**: the utility applies nothing, or resolves inconsistently between scopes.

```css
/* WRONG */
@theme { --font-sans: var(--font-inter); }
```

**Cause**: default `@theme` emits the utility referencing `var(--font-sans)`, which references
`var(--font-inter)`. Wherever the inner variable is undefined the chain resolves to nothing.

**Fix** :

```css
/* RIGHT */
@theme inline { --font-sans: var(--font-inter); }
```

`@theme inline` substitutes the reference at build time and embeds the resolved value. Use
`@theme static` instead when the token's only consumer is JS (`getComputedStyle`) and pruning would
drop it.

### AP-4: `@import "tailwindcss"` inside a scoped block

**Symptom**: enormous CSS output; the framework duplicated once per component.

```vue
<!-- WRONG -->
<style scoped>
@import "tailwindcss";
.btn { @apply px-4 py-2; }
</style>
```

**Cause**: an import emits. Every scoped block that imports ships its own reset, theme, and utility
set.

**Fix** :

```vue
<!-- RIGHT -->
<style scoped>
@reference "../app.css";   /* theme context, zero output */
.btn { @apply px-4 py-2; }
</style>
```

### AP-5: same token defined in `@theme` and in a loaded JS config

**Symptom**: the value differs per build; no error is raised.

```css
/* WRONG */
@config "../tailwind.config.js";   /* theme.extend.colors.brand */
@theme {
  --color-brand: oklch(0.65 0.18 252);
}
```

**Cause**: v4 does not guarantee a merge order between CSS-declared and JS-declared tokens for the
same key.

**Fix**: exactly one source per token. Migrate per token category and delete the JS entry in the
same commit. `@config` is a migration scaffold, not a permanent second source.

### AP-6: JS plugin doing what CSS now does

**Symptom**: a build-time JS dependency and a plugin file for one variant or one utility.

```js
/* Works. Unnecessary. */
plugin(({ addVariant }) => {
  addVariant("pointer-coarse", "@media (pointer: coarse) { & }");
});
```

**Fix** :

```css
@custom-variant pointer-coarse (@media (pointer: coarse));
@utility scrollbar-thin { scrollbar-width: thin; }
```

CSS-native forms are shorter, have no JS dependency, and integrate with the v4 compiler directly.
Keep `@plugin` for legacy plugins and for logic that genuinely needs JS config introspection.

## `@apply` scope

### AP-7: utility hiding — `@apply` everywhere a component belongs

**Symptom**: the stylesheet grows a mirror image of the component tree (`.btn`, `.card`, `.input`,
`.alert`, `.modal`); every component exists twice.

**Cause**: treating `@apply` as "the way to reuse utilities". It rebuilds the CSS framework the
utility approach opted out of, and loses in-context readability, JIT pruning, and the ability to
compose at the call site.

**Fix**: in React/Vue/Svelte/Solid, reuse through components with props:

```tsx
function Button({ children }) {
  return <button className="rounded px-4 py-2 bg-blue-500 text-white">{children}</button>;
}
```

Reserve `@apply` for plain HTML / MDX / CMS output and for third-party markup you do not own. If a
bundle shows a utility's declarations duplicated everywhere a custom class appears, that is this
mistake measured: check the production CSS, not the file count.

### AP-8: `@apply` for a single utility, or a single use

**Symptom**: `.huge-text { @apply text-4xl; }` used once.

**Cause**: premature abstraction. A CSS rule plus a name to remember is heavier than the utility it
hides.

**Fix** :

```diff
- <h1 class="huge-text">Welcome</h1>
+ <h1 class="text-4xl font-bold">Welcome</h1>
```

Delete the rule. Extract a class only once the same recipe genuinely repeats (three or more call
sites is the working threshold), and document its meaning next to the rule.

### AP-9: `@apply` rule outside `@layer`

**Symptom**: `class="btn px-2"` does not override `.btn`'s `px-4`; or the custom class beats
utilities inconsistently. Most often seen in per-component CSS files where the layer is simply
absent.

```css
/* WRONG */
.btn { @apply rounded px-4 py-2; }
```

**Cause**: unlayered CSS sorts AFTER the utilities layer. Same specificity, later source order, so
utilities lose.

**Fix** :

```css
/* RIGHT */
@layer components {
  .btn { @apply rounded px-4 py-2; }
}
```

Now markup utilities win, and the rule loses cleanly to `base` rules only where it should.

### AP-10: `@apply`-ing your own class name

**Symptom**: build error `The btn class does not exist.`

```css
/* WRONG */
.btn-primary { @apply btn bg-blue-500 text-white; }
```

**Cause**: `@apply` copies the declarations of Tailwind utilities. A class you authored is not a
utility, in any layer.

**Fix**: expand the shared declarations, or move the indirection to a tool that has one:

```css
.btn-primary { @apply inline-flex items-center rounded px-4 py-2 font-medium bg-blue-500 text-white; }
```

Sass mixin, PostCSS partial, or a component — in that order of preference inside a framework.

## `@reference`

### AP-11: scoped `@apply` with no `@reference`

**Symptom** :

```
Error: Cannot apply unknown utility class: bg-blue-500
```

inside a Vue SFC `<style scoped>`, a Svelte `<style>`, an Astro component, or a `*.module.css`.

```vue
<!-- WRONG -->
<style scoped>
.btn { @apply px-4 py-2 bg-blue-500; }
</style>
```

**Cause**: v4's token registry is file-scoped. A scoped block is compiled in isolation and never
sees the global theme or custom utilities.

**Fix** :

```vue
<!-- RIGHT -->
<style scoped>
@reference "../app.css";
.btn { @apply px-4 py-2 bg-blue-500; }
</style>
```

Use `@reference "tailwindcss"` when there is no custom theme. Same diagnosis, different version: in
v3 the error means the utility was never generated — the file was not in `content`, the class is
typo'd, or the token is missing from the JS theme. Do not add `@reference` there (AP-14).

### AP-12: `@reference` path that does not resolve

**Symptom**: `Cannot apply unknown utility class` persists even with `@reference` present.

**Cause**: the path points at something other than the entry CSS that declares the tokens. It
resolves relative to the file containing the directive.

**Fix**: trace it. `src/components/Card.vue` → `../app.css`; `src/components/ui/Card.vue` →
`../../app.css`. When relative paths are brittle, use the bundler alias:

```vue
<style scoped>
@reference "@/app.css";
</style>
```

provided `@` maps to `src` in the build config. Pointing at a file without `@theme` produces the same
error as pointing at nothing.

### AP-13: `@reference` after the `@apply` that needs it

**Symptom**: the error persists although `@reference` is in the block.

```vue
<style scoped>
.btn { @apply bg-blue-500; }
@reference "../app.css";
</style>
```

**Cause**: parse order matters; the registry is loaded when the directive is read.

**Fix**: `@reference` first, as the first non-whitespace line, before any `@apply` or `@variant`.
One call is enough; duplicating it adds nothing.

### AP-14: `@reference` where it does not belong

**Symptom**: PostCSS warns about an unknown at-rule, or a confusing no-op line in the entry file.

**Cause**: two misuses. (a) v3 has no `@reference` directive — its PostCSS pipeline already resolves
`@apply` against global tokens. (b) The global entry file does not need it: it already declares
`@import "tailwindcss"` and the local `@theme`, so a self-reference is dead code that readers
misinterpret.

**Fix**: delete the line in v3 files and in the entry stylesheet; keep it only in scoped blocks that
use `@apply` or `@variant`.

## Cascade and variants

### AP-15: CSS in the wrong `@layer`

**Symptom**: `.text-shadow-sm` loses to a helper declared after it, or `.btn` beats a utility the
call site added.

**Cause**: layer chosen by habit instead of intent.

**Fix** :

| Intent | Layer |
|---|---|
| Element-level default | base |
| Named multi-utility component class | components |
| Single-purpose helper that must behave like a utility | utilities |

A `.text-shadow-sm` helper belongs in `utilities` so `text-shadow-none` on the same element wins.

### AP-16: chaining variants by listing them, or inventing a variant name

**Symptom**: `@apply hover:bg-blue-500 active:bg-blue-700` expected to mean "hover AND active"; or
`The hover-focus variant does not exist`.

**Cause**: each variant in an `@apply` list is evaluated in isolation and produces its own rule; and
a compound name is not a variant unless it was registered.

**Fix** :

```css
.btn { @apply hover:active:bg-blue-700; }              /* intersection: chained form */
.btn { @apply hover:bg-blue-500 focus:bg-blue-500; }   /* union: two declarations */
@custom-variant hover-focus (&:hover, &:focus);        /* union as one name */
.btn { @apply hover-focus:bg-blue-500; }
```

### AP-17: `@apply group` to get parent-context variants

**Symptom**: children's `group-hover:*` stop working.

**Cause**: `group` and `peer` are marker classes, not utilities with declarations to copy. `@apply`
copies declarations only.

**Fix**: put the marker in markup:

```html
<div class="card group">...</div>
```

### AP-18: importance written for the other version inside `@apply`

**Symptom**: v4 build error `Did you mean font-bold! instead of font-bold !important?`; or v4
silently ignoring a leading bang; or Sass failing with `Invalid property name` on `!important`.

```css
/* WRONG in v4 */
.btn { @apply font-bold !important; }
/* WRONG in v3 */
.btn { @apply font-bold!; }
```

**Fix**: v4 attaches the bang to the utility (`@apply font-bold!`, per utility, so
`@apply rounded font-bold! bg-blue-500` forces only the weight). v3 uses the keyword
(`@apply font-bold !important;`), and in Sass v3 needs interpolation:

```scss
.btn { @apply font-bold #{!important}; }
```

v4 Sass takes the trailing bang and needs no interpolation. The full form table is
`methods.md` section 9; how the modifier is written on a class in markup, and that change between
versions, is the `migration` module's.

### AP-19: `@apply … !important` as a specificity escape hatch

**Symptom**: `!` added because "the styles do not apply".

**Cause**: the real problem is selector specificity, layer placement, or source order.

**Fix**: diagnose the cascade first — find the winning rule in DevTools, identify why it wins
(layer, specificity, order), then fix the layer or the selector. Reach for `!` only when no clean
cascade fix exists, and say in a comment why.

### AP-20: override plugin registered before the plugin it overrides

**Symptom**: a plugin's `.btn`/`.prose` styles beat your override.

**Cause**: plugins inject into the matching layer in registration order; earlier output is placed
earlier and loses.

**Fix**: register the override last —

```css
@plugin "./plugins/typography.js";
@plugin "./plugins/btn-override.js";
```

and the same ordering inside the `plugins` array of a config loaded through `@config`. `addUtilities`
lands in `utilities`, not before your rules.

### AP-21: `@layer` used as a nesting block

**Symptom**: rules written inside `@layer components { @apply rounded px-4; }` do nothing.

**Cause**: `@layer` is a sorting bucket, not a scope. Contents must be rules with selectors.

**Fix** :

```css
@layer components {
  .btn { @apply rounded px-4 py-2; }
}
```

### AP-22: the same component class defined in two stylesheets

**Symptom**: `.btn` renders differently depending on page or bundle order.

**Cause**: two `@layer components` blocks both define `.btn`; both land in the same layer, source
order decides, and source order differs between dev and prod.

**Fix**: one definition per class, in one file. Compose with imports (Sass modules, CSS imports) so
there is a single source of truth; if a variant is needed, name it (`.btn-primary`), do not redefine
the base.

## Not config bugs

### AP-23: stale dev server blamed on `@apply`

**Symptom**: `@apply` or `@layer` edits do not show up until restart.

**Cause**: entry-CSS edits HMR fine; JS config edits (`tailwind.config.js`, anything loaded through
`@config` or `@plugin`) generally do not.

**Fix**: restart the dev server after touching JS config. If a CSS-only edit still does not apply,
suspect content/source scope elsewhere — not `@apply`.

### AP-24: class name assembled at runtime

**Symptom**: `` bg-${color}-500 `` works under HMR and produces no CSS in production.

```tsx
return <span className={`bg-${color}-500`}>…</span>;
```

**Cause**: detection is plain-text tokenisation; an interpolated string is opaque to it.

**Fix**: prefer a literal lookup map — `{ red: "bg-red-500", blue: "bg-blue-500" }[color]` — and
safelist with `@source inline(...)` only when the name truly exists only at runtime. Grammar,
expansion forms, and the full dynamic-class strategy: the `dynamic-classes` module
(`../../dynamic-classes/method.md`).

### AP-25: expecting a removed v3 option to work through `@config`

**Symptom**: the option is accepted and silently has no effect.

**Cause**: `@config` merges what v4 still supports; options removed in v4 are ignored without
warning.

**Fix**: nothing here. Which options are gone, and what replaces each, is the `migration` module's
catalog (`../../migration/method.md`). To keep a utility from being used at all, scope content with
`@source not` and forbid the name in lint.
