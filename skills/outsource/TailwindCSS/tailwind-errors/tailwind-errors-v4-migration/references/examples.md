# Reference : v3 to v4 Migration Examples

Before/after snippets, staged `@layer base` shims, and audit scripts.

---

## Example 1 : Variant stacking order flip

v3 :

```html
<ul class="py-4 first:*:pt-0 last:*:pb-0">
  <li>Item</li>
</ul>
```

v4 :

```html
<ul class="py-4 *:first:pt-0 *:last:pb-0">
  <li>Item</li>
</ul>
```

The codemod handles common patterns. Multi-token chains require manual
review :

v3 : `group-hover:first:*:opacity-100`
v4 : `group-hover:*:first:opacity-100`

ALWAYS read each result aloud : "for every direct child, when first,
on group hover, set opacity to 100".

---

## Example 2 : Default border-color recovery shim

`src/app.css` :

```css
@import "tailwindcss";

@layer base {
  *, ::after, ::before, ::backdrop {
    border-color: var(--color-gray-200, currentColor);
  }
}
```

This restores v3 default border color. TEMPORARY. Audit borders
afterwards and either remove the shim or convert to explicit
`border-gray-200` on every bordered element.

---

## Example 3 : Default border-color surgical fix

Instead of the shim, add explicit colors :

```diff
- <div class="border p-4">
+ <div class="border border-gray-200 p-4">
```

```diff
- <hr class="border-t">
+ <hr class="border-t border-gray-200">
```

This is the right long-term fix. Visual regressions become impossible
because every border declares its color.

---

## Example 4 : Default ring-width fix

v3 (3px) :

```html
<button class="focus:ring focus:ring-blue-500">Save</button>
```

v4 surgical fix (3px again) :

```html
<button class="focus:ring-3 focus:ring-blue-500">Save</button>
```

Or accept the v4 default (1px) :

```html
<button class="focus:ring focus:ring-blue-500">Save</button>
```

ALWAYS pair `ring` with an explicit color in v4 ; the default flipped
to `currentColor`.

---

## Example 5 : Shadow scale rename

```diff
- <div class="shadow-sm">Subtle shadow</div>
+ <div class="shadow-xs">Subtle shadow</div>

- <div class="shadow">Standard shadow</div>
+ <div class="shadow-sm">Standard shadow</div>
```

Same applies to `blur`, `drop-shadow`, `backdrop-blur`, `rounded` :

```diff
- <img class="blur-sm" />
+ <img class="blur-xs" />

- <div class="rounded">
+ <div class="rounded-sm">
```

---

## Example 6 : bg-opacity / text-opacity replacement

```diff
- <div class="bg-black bg-opacity-50">Overlay</div>
+ <div class="bg-black/50">Overlay</div>

- <p class="text-red-500 text-opacity-75">Warning</p>
+ <p class="text-red-500/75">Warning</p>
```

```diff
- <div class="border border-blue-500 border-opacity-50">
+ <div class="border border-blue-500/50">
```

---

## Example 7 : Prefix flip

v3 setup :

```js
// tailwind.config.js
export default { prefix: "tw-" }
```

```html
<div class="tw-flex tw-bg-red-500 tw-hover:bg-red-600">
```

v4 setup :

```css
/* app.css */
@import "tailwindcss" prefix(tw);
```

```html
<div class="tw:flex tw:bg-red-500 tw:hover:bg-red-600">
```

The `tw-` to `tw:` flip is mechanical, but every utility containing
the prefix must be rewritten. Use the codemod.

---

## Example 8 : Important modifier flip

```diff
- <div class="!flex !bg-red-500">
+ <div class="flex! bg-red-500!">
```

Inside @apply :

```diff
- .btn { @apply font-bold !important; }
+ .btn { @apply font-bold!; }
```

Sass also flipped :

```diff
- .btn { @apply font-bold #{!important}; }
+ .btn { @apply font-bold!; }
```

---

## Example 9 : outline-none rename

```diff
- <input class="focus:outline-none border focus:border-blue-500" />
+ <input class="focus:outline-hidden border focus:border-blue-500" />
```

The v4 `outline-none` now sets `outline-style: none`, which can break
accessibility in forced-colors mode. ALWAYS use `outline-hidden`
unless you genuinely want to remove the outline entirely.

---

## Example 10 : Arbitrary CSS variable syntax

```diff
- <div class="bg-[--brand-color]">
+ <div class="bg-(--brand-color)">

- <div class="text-[--accent]/80">
+ <div class="text-(--accent)/80">
```

Parentheses replaced square brackets because modern CSS made the old
syntax ambiguous.

---

## Example 11 : Underscore in arbitrary values

```diff
- <div class="grid-cols-[max-content,auto]">
+ <div class="grid-cols-[max-content_auto]">

- <div class="object-[center,top]">
+ <div class="object-[center_top]">
```

Use `_` for the space. Comma no longer becomes a space substitute.

---

## Example 12 : Individual transform property reset

```diff
- <button class="scale-150 focus:transform-none">
+ <button class="scale-150 focus:scale-none">

- <div class="rotate-45 hover:transform-none">
+ <div class="rotate-45 hover:rotate-none">
```

Transitions also changed :

```diff
- <button class="transition-[opacity,transform] hover:scale-150">
+ <button class="transition-[opacity,scale] hover:scale-150">
```

---

## Example 13 : @layer utilities to @utility

v3 :

```css
@layer utilities {
  .tab-1 { tab-size: 1; }
  .tab-2 { tab-size: 2; }
  .tab-4 { tab-size: 4; }
  .tab-8 { tab-size: 8; }
}
```

v4 (functional utility) :

```css
@utility tab-* {
  tab-size: --value(integer);
}
```

This emits the same four utilities (plus any integer used in HTML),
all from one declaration.

---

## Example 14 : Removed corePlugins option

v3 :

```js
// tailwind.config.js
export default {
  corePlugins: { preflight: false },
}
```

v4 : v4 has no global off-switch. To replace preflight :

```css
@import "tailwindcss" source(none) layer(theme, base, components, utilities);

@layer base {
  /* write your own reset here */
  *, ::before, ::after { box-sizing: border-box; }
}
```

OR simply do not import the base layer :

```css
@import "tailwindcss/theme.css";
@import "tailwindcss/utilities.css";
/* skip @import "tailwindcss/preflight.css"; */
```

---

## Example 15 : Removed safelist option

v3 :

```js
// tailwind.config.js
export default {
  safelist: [
    "bg-red-500",
    "bg-green-500",
    { pattern: /bg-(red|green|blue)-(100|500|900)/ },
  ],
}
```

v4 :

```css
@import "tailwindcss";

@source inline "{bg-red-500,bg-green-500}";
@source inline "{bg-(red|green|blue)-(100,500,900)}";
```

Brace expansion handles the pattern case via `(a|b|c)` alternation.

---

## Example 16 : theme() function syntax

```diff
  /* v3 */
- @media (width >= theme(screens.xl)) {
-   .hero { padding: theme(spacing.16); }
- }

  /* v4 */
+ @media (width >= theme(--breakpoint-xl)) {
+   .hero { padding: theme(--spacing-16); }
+ }
```

Dot notation gone ; use the CSS-variable name directly.

---

## Example 17 : Staged migration with @config bridge

```css
@import "tailwindcss";
@config "./tailwind.config.js";

/* v4-native additions */
@theme {
  --color-brand: oklch(0.6 0.18 250);
}
```

The v3 config is still read for `theme`, `content`, `plugins`. New v4
features (CSS-first `@theme`, `@source`, `@utility`) work alongside.

PLAN to remove the `@config` line within one release cycle. The
bridge is a migration crutch, not a permanent layout.

---

## Example 18 : Hover gating with active fallback

v3 (always fires) :

```html
<button class="bg-blue-500 hover:bg-blue-700">Tap me</button>
```

v4 (does not fire on touch) :

```html
<button class="bg-blue-500 hover:bg-blue-700 active:bg-blue-800">
  Tap me
</button>
```

ALWAYS add `active:` for touch UX after v4 upgrade.

---

## Example 19 : Audit script for v3 leftovers

`scripts/audit-tailwind-v4.sh` :

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "--- Leading-bang !class (v3 syntax) ---"
grep -rEn 'class(Name)?=["'\''`][^"'\''`]*![a-z]' src/ || true

echo "--- v3-style prefix tw- (should be tw:) ---"
grep -rEn '\btw-(flex|grid|block|hidden|p-|m-|w-|h-)' src/ || true

echo "--- *-opacity-* utilities (removed) ---"
grep -rEn '\b(bg|text|border|divide|ring|placeholder)-opacity-' src/ || true

echo "--- bare 'ring' (default width changed to 1px) ---"
grep -rEn '\bring\b(?!-)' src/ || true

echo "--- v3 arbitrary CSS var syntax [--var] ---"
grep -rEn '\[--[a-z]' src/ || true

echo "--- old outline-none (now means outline-style:none) ---"
grep -rEn '\boutline-none\b' src/ || true

echo "Audit complete."
```

Run after the codemod, before merging.

---

## Example 20 : Full migration checklist

```
[ ] Run npx @tailwindcss/upgrade
[ ] Review codemod diff manually
[ ] Add @layer base default-color shim (temporary)
[ ] Replace bare `ring` with `ring-3` or accept 1px default
[ ] Run audit script
[ ] Visual regression suite on representative pages
[ ] Fix variant stacking order semantics
[ ] Migrate @layer utilities to @utility
[ ] Migrate safelist to @source inline
[ ] Remove deprecated config options (corePlugins, safelist, separator)
[ ] Pair hover: with active:/focus: for touch users
[ ] Plan @config bridge removal
[ ] Confirm browser support matches v4 minimums
[ ] Merge
```
