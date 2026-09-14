# Anti-Patterns : @apply, @layer, @reference

Every common mistake with these directives, the symptom, the cause, and the fix.

---

## AP-1 : Wrapping every utility set in @apply

**Symptom :** Your CSS file balloons with `.btn`, `.card`, `.input`,
`.alert`, `.modal` definitions ; every component lives twice (in CSS
and in the framework component).

**Cause :** Treating @apply as "the right way" to reuse utilities.
This rebuilds the CSS framework you opted out of.

**Fix :** In component frameworks (React, Vue, Svelte, Solid), reuse
via components, not class names :

```tsx
function Button({ children }) {
  return <button className="rounded px-4 py-2 bg-blue-500 text-white">{children}</button>
}
```

Reserve @apply for non-component contexts (plain HTML, MDX content,
third-party library overrides).

---

## AP-2 : Forgetting @reference in v4 scoped styles

**Symptom :** Build error :

```
Error: Cannot apply unknown utility class: bg-blue-500
```

inside a Vue SFC `<style scoped>`, Svelte component, or CSS module.

**Cause :** v4 token registry is file-scoped. Scoped style blocks are
parsed in isolation and never see the global tokens.

**Fix :** Add `@reference` as the first line of the scoped block :

```vue
<style scoped>
@reference "../app.css";

.card { @apply rounded shadow; }
</style>
```

The path resolves relative to the file containing the directive.

---

## AP-3 : Using v3 leading-bang syntax in v4

**Symptom :** v4 ignores the bang silently ; the utility applies but
without `!important`.

**Cause :** v3 wrote `!font-bold` (bang first). v4 changed to
`font-bold!` (bang last) because the leading bang clashed with CSS
selector syntax.

**Fix :**

```diff
- <button class="!font-bold">
+ <button class="font-bold!">
```

Same flip inside @apply :

```diff
- .btn { @apply font-bold !important; }
+ .btn { @apply font-bold!; }
```

---

## AP-4 : @apply rule outside @layer

**Symptom :** Your `.btn` rule looks right but Tailwind utilities
like `px-2` on the same element are silently overridden by `.btn`'s
`@apply px-4`.

**Cause :** Without `@layer components`, the rule lands AFTER Tailwind's
utility layer. Same specificity ; source order wins ; utilities lose.

**Fix :** Wrap in `@layer components` :

```diff
- .btn { @apply rounded px-4 py-2; }
+ @layer components {
+   .btn { @apply rounded px-4 py-2; }
+ }
```

Now `class="btn px-2"` correctly overrides to `px-2`.

---

## AP-5 : Apply-ing your own class name

**Symptom :** Build error :

```
The `btn` class does not exist.
```

**Cause :** @apply only accepts Tailwind utilities, NOT your custom
class names.

**Fix :** Expand the shared utilities explicitly :

```diff
  .btn-primary {
-   @apply btn bg-blue-500 text-white;
+   @apply rounded px-4 py-2 font-medium bg-blue-500 text-white;
  }
```

Or use a Sass mixin / PostCSS plugin for the indirection.

---

## AP-6 : Chaining variants by listing them separately

**Symptom :** You write `@apply hover:active:bg-blue-700` and expect
"apply when hover AND active", but get separate rules.

Wait : that line IS the chained variant. The mistake is to write
`@apply hover:bg-blue-500 active:bg-blue-700` thinking it composes.

**Cause :** Each variant in the list is independent. `hover:` and
`active:` produce two separate rules, not a chained one.

**Fix :** Use the chained syntax explicitly :

```css
.btn { @apply hover:active:bg-blue-700; }
```

---

## AP-7 : @apply for a single utility

**Symptom :** Custom class names like `.huge-text { @apply text-4xl; }`
that are used once.

**Cause :** Premature abstraction. The CSS rule + class name pair is
heavier than the utility class it replaces.

**Fix :** Use the utility directly :

```diff
- <h1 class="huge-text">Welcome</h1>
+ <h1 class="text-4xl">Welcome</h1>
```

Remove the CSS rule.

---

## AP-8 : @reference path wrong

**Symptom :** "Cannot apply unknown utility class" persists even after
adding `@reference`.

**Cause :** The path does not resolve to the global entry CSS that
declares your `@theme` tokens.

**Fix :** Trace the path. From `src/components/Card.vue` to
`src/app.css`, the path is `../app.css`. From `src/components/ui/Card.vue`,
it is `../../app.css`. ALWAYS test with an absolute alias if the
relative path is brittle :

```vue
<style scoped>
@reference "@/app.css";
</style>
```

assuming `@` is configured to map to `src` in `vite.config.ts`.

---

## AP-9 : Using @reference in v3

**Symptom :** PostCSS warns about unknown at-rule, or the build fails
parsing the directive.

**Cause :** `@reference` is a v4-only directive. v3 has no equivalent
because its PostCSS pipeline already provides global token visibility
inside scoped styles.

**Fix :** Remove the `@reference` line entirely in v3 projects.

---

## AP-10 : Putting CSS in the wrong @layer

**Symptom :** Your `.text-shadow-sm` utility loses to `.shadow-md`
that came after, or your `.btn` component class wins over a Tailwind
utility you tried to apply on the same element.

**Cause :** Wrong layer choice.

**Fix :** Match layer to intent :

| Intent                              | Layer        |
| ----------------------------------- | ------------ |
| Element-level default               | base         |
| Multi-utility named component class | components   |
| Single-purpose helper (utility-like) | utilities   |

A `.text-shadow-sm` helper belongs in `utilities`, not `components`,
so that adding `text-shadow-none` on the element wins.

---

## AP-11 : Expecting @apply to handle parent context

**Symptom :** You write `.card { @apply group; }` and the `group-hover`
variants in children stop working.

**Cause :** `group` and `peer` are class names that act as parent
context markers. @apply copies declarations, not class-name semantics.

**Fix :** Set `group` directly in the HTML / template :

```html
<div class="card group">...</div>
```

NEVER try to @apply `group`. It is not a utility, it is a marker class.

---

## AP-12 : Override plugin order wrong

**Symptom :** Your `.btn` styles in `addComponents` are overridden by
Tailwind defaults or another plugin.

**Cause :** Plugin order. Plugins registered earlier emit CSS earlier
in the same layer ; later plugins win.

**Fix :** Register the override plugin LAST in `plugins` :

```js
plugins: [
  typography,
  forms,
  myOverridePlugin,   // last
]
```

---

## AP-13 : `!important` keyword vs trailing bang mixup

**Symptom :** v4 build error :

```
Did you mean `font-bold!` instead of `font-bold !important`?
```

**Cause :** v4 removed the `!important` keyword in @apply. The
trailing bang `font-bold!` is the only accepted form.

**Fix :**

```diff
- .btn { @apply font-bold !important; }
+ .btn { @apply font-bold!; }
```

In v3 the inverse applies : trailing bang is invalid, use the keyword.

---

## AP-14 : Forgetting Sass interpolation for !important

**Symptom :** Sass build error : `Invalid property name` when using
`@apply font-bold !important` inside a `.scss` file.

**Cause :** Sass parses `!important` differently than vanilla CSS.

**Fix :** Wrap with interpolation :

```scss
.btn { @apply font-bold #{!important}; }
```

This is v3-specific ; v4 with Sass uses the trailing bang and does
NOT need the interpolation hack.

---

## AP-15 : @apply variant chains that do not exist

**Symptom :** Build error : `The hover-focus variant does not exist`.

**Cause :** You wrote `@apply hover-focus:bg-blue-500` thinking
"hover or focus" composes into one variant.

**Fix :** Use either-or with two declarations :

```css
.btn { @apply hover:bg-blue-500 focus:bg-blue-500; }
```

Or define a custom variant (v4) :

```css
@custom-variant hover-focus (&:hover, &:focus);
```

Then :

```css
.btn { @apply hover-focus:bg-blue-500; }
```

---

## AP-16 : Treating @layer as a CSS nesting block

**Symptom :** You write `@layer components { @apply ...; }` with no
selector, expecting the rules to land somewhere.

**Cause :** `@layer` is a sorting bucket, not a scope. Rules inside
need real selectors.

**Fix :**

```diff
  @layer components {
-   @apply rounded px-4 py-2;
+   .btn { @apply rounded px-4 py-2; }
  }
```

---

## AP-17 : @reference appearing AFTER @apply

**Symptom :** Build error persists even though `@reference` is in the
scoped block.

**Cause :** The directive must appear BEFORE any @apply that depends
on it. Parse order matters.

**Fix :**

```diff
  <style scoped>
- .btn { @apply bg-blue-500; }
- @reference "../app.css";
+ @reference "../app.css";
+ .btn { @apply bg-blue-500; }
  </style>
```

---

## AP-18 : Stale dev server after layer / @apply edits

**Symptom :** New @apply or @layer changes do not apply until restart.

**Cause :** HMR usually handles entry-CSS changes, but config-file edits
(v3 `tailwind.config.js`, v4 `@config`-loaded JS) require restart.

**Fix :** Restart `npm run dev` after editing JS config. CSS-only edits
should HMR reliably ; if not, suspect a content / source scope issue
elsewhere, NOT @apply.

---

## AP-19 : Two stylesheets defining the same component class

**Symptom :** `.btn` style varies depending on page load order.

**Cause :** Two `@layer components` blocks define `.btn` differently.
Both end up in the components layer ; source order decides which wins,
and source order can shift between dev and prod builds.

**Fix :** Define each component class in exactly ONE place. Use Sass
imports / CSS imports to keep one source of truth.

---

## AP-20 : Using @apply to "fix" a low-specificity bug

**Symptom :** Someone reaches for `@apply ... !important` because
"the styles do not apply". The real issue is selector specificity
or layer ordering.

**Cause :** Treating @apply as a specificity escape hatch.

**Fix :** Diagnose the cascade first :

1. Open DevTools, find the element.
2. Identify which rule wins and why (selector specificity, source order, layer).
3. Adjust the layer or selector to win cleanly.
4. ONLY then reach for `!important` if there is no clean cascade fix.
