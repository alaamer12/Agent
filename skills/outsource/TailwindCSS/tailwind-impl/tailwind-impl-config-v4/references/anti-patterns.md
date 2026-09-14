# tailwind-impl-config-v4 : Anti-Patterns

Common v4 config mistakes with WHY they fail and the fix.

## AP-1 : Using `@tailwind base/components/utilities` in v4

**Symptom** : Build error or zero output.

```css
/* WRONG (v4) */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**Why** : v4 removed all three `@tailwind` directives. They were a v3 PostCSS-era mechanism.

**Fix** :

```css
/* RIGHT (v4) */
@import "tailwindcss";
```

Source : https://tailwindcss.com/blog/tailwindcss-v4

## AP-2 : Custom Token Without a Recognised Namespace

**Symptom** : Token works as a CSS variable (`var(--brand-blue)`) but no `bg-brand-blue` utility appears.

```css
/* WRONG */
@theme {
  --brand-blue: #1da1f2;
}
```

**Why** : Tailwind recognises namespace prefixes (`--color-*`, `--font-*`, `--spacing-*`, etc.). A token outside any namespace becomes a plain CSS variable but does not generate a utility class.

**Fix** :

```css
/* RIGHT */
@theme {
  --color-brand-blue: #1da1f2;
}
/* Generates : bg-brand-blue, text-brand-blue, border-brand-blue, ... */
```

## AP-3 : `@apply` in Vue SFC `<style scoped>` Without `@reference`

**Symptom** : Build fails with "Cannot apply unknown utility class".

```vue
<!-- WRONG -->
<style scoped>
.btn { @apply px-4 py-2 bg-blue-500; }
</style>
```

**Why** : v4 compiles each scoped block in isolation. The theme + custom utilities defined in `app.css` are NOT implicitly available.

**Fix** :

```vue
<!-- RIGHT -->
<style scoped>
@reference "../app.css";

.btn { @apply px-4 py-2 bg-blue-500; }
</style>
```

If the project has no custom theme : `@reference "tailwindcss";`.

Source : https://github.com/tailwindlabs/tailwindcss/issues/16346

## AP-4 : Dynamic Class Names Without `@source inline()`

**Symptom** : `bg-${color}-500` works in dev (HMR re-scans) but produces no CSS in production.

```tsx
/* WRONG */
function Tag({ color }: { color: "red" | "blue" }) {
  return <span className={`bg-${color}-500`}>...</span>;
}
```

**Why** : Tailwind scans source files as plain text. Template literals are opaque to the scanner.

**Fix 1 (preferred)** :

```tsx
const colorClass = { red: "bg-red-500", blue: "bg-blue-500" }[color];
return <span className={colorClass}>...</span>;
```

**Fix 2 (when value is truly runtime)** :

```css
/* app.css */
@source inline("bg-{red,blue,green}-{50,{100..900..100},950}");
```

Source : https://github.com/tailwindlabs/tailwindcss/issues/18136

## AP-5 : `@apply` Outside `@layer`

**Symptom** : Custom class wins over later-declared utility classes. Or loses to base styles inconsistently.

```css
/* WRONG */
.btn { @apply px-4 py-2 bg-blue-500; }
```

**Why** : Without a layer, the declaration sits in the default cascade layer, breaking the predictable `theme < base < components < utilities` ordering.

**Fix** :

```css
/* RIGHT */
@layer components {
  .btn { @apply px-4 py-2 bg-blue-500; }
}
```

User-authored utility classes can then override `.btn` styles.

## AP-6 : Mixing `@theme` and Loaded JS Config `theme.extend` for the Same Token

**Symptom** : Token value is unspecified ; behaviour differs per build.

```css
/* WRONG */
@config "../tailwind.config.js";   /* defines theme.extend.colors.brand */
@theme {
  --color-brand: oklch(0.65 0.18 252);   /* ALSO defines brand */
}
```

**Why** : v4 does not guarantee a merge order between CSS-defined and JS-config-defined tokens for the same key.

**Fix** : Migrate per token category. Define each token in EXACTLY one place. Use `@theme` going forward, drop the JS config when migration of that category is done.

## AP-7 : Using `corePlugins: false` to Disable a Built-in

**Symptom** : Option is silently ignored. The utility still generates.

```js
// tailwind.config.js loaded via @config
module.exports = { corePlugins: { float: false } };
```

**Why** : v4 removed `corePlugins` without replacement.

**Fix** : There is none. v4 does not support disabling specific built-in utility families. Use `@source not` to scope content scanning OR a stylelint rule to forbid specific class names.

Source : https://tailwindcss.com/docs/upgrade-guide

## AP-8 : Defining a Variant via JS Plugin Instead of `@custom-variant`

**Symptom** : Variant works but adds JS plugin overhead unnecessarily.

```js
/* OK but unnecessary */
plugin(({ addVariant }) => {
  addVariant("pointer-coarse", "@media (pointer: coarse) { & }");
});
```

**Fix** :

```css
@custom-variant pointer-coarse (@media (pointer: coarse));
```

CSS-native is shorter, has no build-time JS dependency, and integrates with the v4 compiler more directly.

## AP-9 : Token Reference Chains Without `@theme inline`

**Symptom** : Utility class references a chain `--font-sans -> var(--font-inter)` that resolves to nothing at certain scopes.

```css
/* WRONG */
@theme {
  --font-sans: var(--font-inter);
}
```

**Why** : Default `@theme` emits CSS variable references, not values. If `--font-inter` is not defined in the consuming scope, the reference resolves to nothing.

**Fix** :

```css
/* RIGHT */
@theme inline {
  --font-sans: var(--font-inter);
}
```

`@theme inline` resolves `var()` references at build time and embeds the resolved value in the utility class.

## AP-10 : Importing Tailwind Inside Every Scoped Block

**Symptom** : Massive CSS output, full framework duplicated per component.

```vue
<!-- WRONG -->
<style scoped>
@import "tailwindcss";              /* duplicates the entire framework */
.btn { @apply px-4 py-2; }
</style>
```

**Fix** :

```vue
<!-- RIGHT -->
<style scoped>
@reference "../app.css";            /* no output, only theme context */
.btn { @apply px-4 py-2; }
</style>
```

Source : https://tailwindcss.com/docs/functions-and-directives

## AP-11 : Forgetting to Wrap `@apply` in `@layer components` for Component Classes

Same as AP-5 ; called out separately because the most common variant of this is per-component CSS files where the developer omits the layer entirely.

## Verified Sources

- https://github.com/tailwindlabs/tailwindcss/issues/16346 (scoped @apply)
- https://github.com/tailwindlabs/tailwindcss/issues/18136 (dynamic class names)
- https://tailwindcss.com/docs/upgrade-guide
- https://tailwindcss.com/docs/functions-and-directives

Last verified : 2026-05-19.
