---
name: tailwind-impl-migration-v3-v4
description: >
  Use when migrating a project from Tailwind CSS v3.4 to v4.0+, deciding
  between the automated upgrade tool and manual conversion, planning a
  dual-version monorepo transition, auditing a codebase before the
  upgrade, or verifying behaviour after the upgrade. Prevents the five
  most damaging migration mistakes: assuming the automated tool covers
  100 percent (it does not handle runtime opacity classes built from
  strings, scoped @apply blocks, or visual regressions from default
  border-color changes), running the tool without first auditing
  corePlugins/safelist/separator usage (all three removed or relocated
  in v4), missing the shadow/blur/rounded scale shift (shadow-sm in v3
  is shadow-xs in v4, an entire visual layer jumps), ignoring the
  variant stacking-order flip (first:*:pt-0 becomes *:first:pt-0), and
  forgetting that @apply in Vue/Svelte/CSS-modules requires @reference
  in v4. Covers the npx @tailwindcss/upgrade tool (Node 20+, branch
  workflow, what it converts), the complete breaking-changes catalogue
  (renamed utilities, removed utilities, opacity syntax, prefix syntax,
  default ring/border/placeholder colours, space/divide selector
  rewrites, hover gating to (hover: hover), individual transform
  properties, theme() function deprecation, corePlugins removal,
  resolveConfig removal, Sass/Less/Stylus incompatibility), the dual-
  version strategy for monorepos with shared component libraries, the
  pre-migration audit checklist, the post-migration verification
  procedure including visual regression and scoped-style @apply scan.
  Keywords: tailwind v3 to v4, tailwind v4 upgrade, @tailwindcss/upgrade,
  npx tailwindcss upgrade, tailwind migration, tailwindcss v4 breaking
  changes, @tailwind to @import tailwindcss, bg-opacity removed,
  shadow-sm renamed, shadow-xs, blur-xs, rounded-xs, outline-hidden,
  ring-3, default border color currentColor, default ring width 1px,
  prefix tw-flex to tw:flex, variant stacking left to right, first:*
  to *:first, @apply scoped style @reference, hover (hover: hover)
  gating, transform-none replaced, theme() deprecated, corePlugins
  removed, safelist removed @source inline, resolveConfig removed, Sass
  incompatible v4, monorepo dual version tailwind, audit corePlugins,
  audit safelist, audit separator, my classes broke after upgrade,
  visual regression after tailwind v4, can I keep v3, gradient reset
  via-none, transition outline-color, dialog margin auto, button cursor
  pointer.
license: MIT
compatibility: "Designed for Claude Code. Tailwind CSS v3.4 source + v4.0+ target."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# Tailwind CSS v3 to v4 Migration

The path. Audit first, automate second, verify third. Skipping the
audit produces a build that compiles and renders wrong.

Companion skills :

- `tailwind-core-v3-vs-v4` : decision tree for staying vs upgrading
- `tailwind-errors-v4-migration` : trap catalogue after upgrade
- `tailwind-impl-config-v4` : v4 CSS-first config surface
- `tailwind-impl-config-v3` : v3 JS config surface (source state)

## Decision : Do You Even Migrate

| Constraint | Stay on v3.4 | Migrate to v4 |
|------------|--------------|---------------|
| Must support Safari < 16.4, Chrome < 111, Firefox < 128 | yes | no |
| Uses Sass / Less / Stylus around Tailwind | yes | no |
| Heavy reliance on `corePlugins: { x: false }` to disable utilities | stay or accept utility cannot be disabled in v4 | no |
| Uses `resolveConfig` in JS at runtime | yes | only if you rewrite to `getComputedStyle` |
| Greenfield project, modern browsers | no | yes |
| Want CSS-first config and faster builds | no | yes |

v3.4 still receives security patches. There is NO urgency to migrate
purely for the sake of being current.

## Quick Path : Automated Upgrade

```bash
git checkout -b chore/tailwind-v4
npx @tailwindcss/upgrade
```

Requires Node.js 20 or higher. The tool runs in three phases :

1. **Dependency updates** : removes `tailwindcss@^3`, `autoprefixer`,
   `postcss-import` ; installs `tailwindcss@^4`, `@tailwindcss/postcss`
   or `@tailwindcss/vite` based on detected build setup.
2. **Config conversion** : reads `tailwind.config.js`, converts
   `theme.extend.colors`, `fontFamily`, `spacing`, etc. into a CSS
   `@theme { ... }` block in the entry stylesheet. Leaves the JS file
   in place with a comment, or removes it (review diff).
3. **Template rewrites** : runs codemods across `.html`, `.tsx`,
   `.vue`, `.svelte` for the deterministic renames (`shadow` →
   `shadow-sm`, `flex-shrink-0` → `shrink-0`, `bg-opacity-50` →
   adjusted variants, etc.) and the variant-stacking-order flip.

ALWAYS review the diff. The tool does NOT cover :

- Dynamic class strings : `` `bg-opacity-${n}` `` is invisible.
- Scoped `@apply` blocks in `.vue` / `.svelte` / CSS-modules
  (requires manual `@reference` per file).
- Custom plugins that read `theme()` in patterns the codemod misses.
- Visual regressions from default `border-color`, `ring-color`,
  `ring-width`, `placeholder-color` changes.

## Pre-Migration Audit Checklist

ALWAYS complete BEFORE running the upgrade tool :

1. **corePlugins** : grep `tailwind.config.js` for `corePlugins`. Every
   disabled utility now exists in v4 with no way to disable. Plan to
   add a lint rule or scope-limit content scanning.
2. **safelist** : grep `tailwind.config.js` for `safelist`. Migrate to
   `@source inline("class-list")` in CSS post-upgrade.
3. **separator** : grep for `separator:` in config. v4 fixes the
   separator to `:`. Custom separators must be removed.
4. **prefix** : if you use `prefix: 'tw-'` in v3, plan to convert all
   `class="tw-flex"` to `class="tw:flex"`. The tool handles common
   cases ; verify dynamic class strings.
5. **resolveConfig** : grep `node_modules` (your own packages) for
   `tailwindcss/resolveConfig`. Every call site needs rewriting to
   `getComputedStyle(document.documentElement).getPropertyValue(...)`.
6. **Default border colour** : grep for `<X class="border"` (no
   colour). Each becomes `currentColor` in v4 ; pages may render
   borders in unexpected colours. Either add explicit `border-zinc-200`
   everywhere, or restore the v3 default via `@layer base`.
7. **Default ring** : grep for `class="ring"`. The new default is 1px
   `currentColor`. Decide between adding explicit `ring-3 ring-blue-500`
   or preserving v3 globally via `@theme { --default-ring-width: 3px;
   --default-ring-color: var(--color-blue-500); }`.
8. **Sass / Less / Stylus** : v4 does NOT work alongside CSS
   preprocessors. If your build runs `.scss` through Sass before
   PostCSS, plan to flatten to plain CSS first.
9. **Scoped `@apply`** : grep `.vue`, `.svelte`, CSS-module files for
   `@apply`. Each scoped stylesheet needs `@reference "../app.css";`
   prepended in v4.
10. **Dynamic opacity** : grep for `bg-opacity-`, `text-opacity-`, etc.
    in dynamic templates. The codemod converts literal class strings
    but cannot rewrite string concatenation.

## Manual Breaking Changes (After Tool Runs)

### Renamed utility scale shift

Every size scale shifted by one. v3 `shadow` (the default with no
suffix) is v4 `shadow-sm`. v3 `shadow-sm` (the small one) is v4
`shadow-xs`. Same shift for `blur`, `drop-shadow`, `backdrop-blur`,
`rounded`.

| v3 | v4 |
|----|----|
| `shadow-sm` | `shadow-xs` |
| `shadow` | `shadow-sm` |
| `blur-sm` | `blur-xs` |
| `blur` | `blur-sm` |
| `rounded-sm` | `rounded-xs` |
| `rounded` | `rounded-sm` |
| `drop-shadow-sm` | `drop-shadow-xs` |
| `drop-shadow` | `drop-shadow-sm` |
| `backdrop-blur-sm` | `backdrop-blur-xs` |
| `backdrop-blur` | `backdrop-blur-sm` |

### Renamed outline and ring

- `outline-none` becomes `outline-hidden` (the v4 `outline-none`
  removes outline entirely, a different intent).
- `ring` (v3 default 3px) becomes `ring-3` to preserve 3px.

### Removed deprecated utilities

| v3 | v4 |
|----|----|
| `bg-opacity-50` | `bg-black/50` modifier syntax |
| `text-opacity-*` | `text-{color}/{n}` |
| `border-opacity-*` | `border-{color}/{n}` |
| `divide-opacity-*` | `divide-{color}/{n}` |
| `ring-opacity-*` | `ring-{color}/{n}` |
| `placeholder-opacity-*` | `placeholder-{color}/{n}` |
| `flex-shrink-*` | `shrink-*` |
| `flex-grow-*` | `grow-*` |
| `overflow-ellipsis` | `text-ellipsis` |
| `decoration-slice` | `box-decoration-slice` |
| `decoration-clone` | `box-decoration-clone` |
| `bg-gradient-to-r` | `bg-linear-to-r` (also `bg-radial`, `bg-conic`) |

### Variant-stacking order flip

v3 evaluated right-to-left. v4 evaluates left-to-right :

```html
<!-- v3 -->
<ul class="first:*:pt-0 last:*:pb-0">

<!-- v4 -->
<ul class="*:first:pt-0 *:last:pb-0">
```

The upgrade tool catches common cases. Stacked custom variants need
manual inspection.

### Important modifier position

v3 placed `!` at the front (`!flex`). v4 places it at the end (`flex!`).

### Variables in arbitrary values

v3 used brackets. v4 uses parentheses :

```html
<!-- v3 -->
<div class="bg-[--brand]"></div>

<!-- v4 -->
<div class="bg-(--brand)"></div>
```

### Arbitrary commas become underscores

v3 grid template lists used commas. v4 uses underscores for spaces :

```html
<!-- v3 -->
<div class="grid-cols-[max-content,auto]"></div>

<!-- v4 -->
<div class="grid-cols-[max-content_auto]"></div>
```

### Prefix syntax flips

v3 prefixed utility names (`tw-flex`). v4 treats prefix as a variant
(`tw:flex`). Configure in CSS :

```css
@import "tailwindcss" prefix(tw);
```

### Default colour changes

| What | v3 default | v4 default |
|------|-----------|-----------|
| `border` colour | `gray-200` | `currentColor` |
| `ring` colour | `blue-500` | `currentColor` |
| `ring` width | `3px` | `1px` |
| `placeholder` colour | `gray-400` | `currentColor` at 50% opacity |

Restore v3 behaviour globally :

```css
@theme {
  --default-ring-width: 3px;
  --default-ring-color: var(--color-blue-500);
}

@layer base {
  *,
  ::after,
  ::before,
  ::backdrop,
  ::file-selector-button {
    border-color: var(--color-gray-200, currentColor);
  }
  input::placeholder,
  textarea::placeholder {
    color: var(--color-gray-400);
  }
  button:not(:disabled),
  [role="button"]:not(:disabled) {
    cursor: pointer;
  }
  dialog {
    margin: auto;
  }
}
```

### Hover gating

v4 wraps `hover:` in `@media (hover: hover)`. Mobile devices that
emulate hover via touch will NOT fire it. Restore v3 behaviour :

```css
@custom-variant hover (&:hover);
```

### theme() function deprecation

v3 used `theme(colors.red.500)`. v4 prefers CSS variables :

```css
/* v3 */
.x { background: theme(colors.red.500); }

/* v4 */
.x { background: var(--color-red-500); }
```

The legacy `theme(...)` still works in v4 with the new dash-prefixed
syntax `theme(--color-red-500)`, but plain `var(...)` is preferred.

### corePlugins, safelist, separator REMOVED

No JS-config replacement. Migrate :

- `corePlugins` : accept utilities cannot be disabled ; restrict via
  `@source not "path"` or a lint rule.
- `safelist` : `@source inline("class-list")` in CSS.
- `separator` : v4 fixes the separator to `:`.

### resolveConfig REMOVED

No JS API to read the resolved config. Use the DOM :

```js
const styles = getComputedStyle(document.documentElement);
const red = styles.getPropertyValue('--color-red-500');
```

## Dual-Version Strategy (Monorepo)

When a shared component library is consumed by multiple apps and you
cannot upgrade them all simultaneously :

1. Library exposes Tailwind classes as plain strings (no `@apply` in
   library source ; `@apply` semantics differ between v3 and v4).
2. Each app installs its own Tailwind version. v3 apps keep
   `tailwindcss@^3` + `postcss-import` + `autoprefixer`. v4 apps
   install `tailwindcss@^4` + `@tailwindcss/postcss`.
3. Library publishes a `tailwind-tokens` package : in v3 a JS config
   fragment for `theme.extend`, in v4 a CSS file with `@theme { ... }`.
4. Each app imports the appropriate variant.
5. Migrate one app at a time. ALWAYS keep the library at the lowest
   common denominator (utilities only ; no `@apply`, no custom
   directives).

## Post-Migration Verification

1. **Build succeeds** : `npm run build` exits 0. CSS bundle generated.
2. **Bundle inspection** : grep the output for selectors known to have
   changed (`shadow-xs`, `outline-hidden`, etc.).
3. **Visual regression** : screenshot the top 20 pages before the
   merge, again after, diff with a tool (Percy, Playwright, Chromatic).
   Default-colour shifts (border, ring, placeholder) WILL produce
   diffs ; review each.
4. **Scoped @apply scan** : grep `find . -name '*.vue' -o -name
   '*.svelte' -o -name '*.module.css' | xargs grep -l '@apply'`.
   Every match needs `@reference "../app.css";` at the top of the
   `<style>` block.
5. **Dynamic class smoke test** : navigate to pages that build class
   names from props (`bg-opacity-${n}`, etc.). These cases the codemod
   could not rewrite.
6. **Tailwind plugin compatibility** : check every entry in
   `tailwind.config.js`'s `plugins` array. Most v3 plugins still work
   in v4 (loaded via `@plugin "..."` in CSS), but anything that
   touches `corePlugins` or `safelist` config will silently no-op.

## References

- `references/methods.md` : per-area migration procedures with
  exact commands and shell snippets
- `references/examples.md` : before/after code for every breaking
  change in this catalogue
- `references/anti-patterns.md` : ten migration traps with symptom,
  cause, fix, verification

## Sources

- https://tailwindcss.com/docs/upgrade-guide
- https://tailwindcss.com/blog/tailwindcss-v4
- https://github.com/tailwindlabs/tailwindcss/blob/main/packages/%40tailwindcss-upgrade/README.md
