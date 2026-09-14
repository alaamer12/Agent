---
name: tailwind-core-v3-vs-v4
description: >
  Use when picking a Tailwind CSS version for a new project, deciding whether
  to upgrade an existing v3 codebase to v4, or debugging visual regressions and
  build errors that appear right after a v3 to v4 bump. Prevents the silent
  visual breakages (border-color, ring-width, shadow scale rename) and the
  removed-option traps (corePlugins, safelist, separator) that bite every
  v3 to v4 migration. Covers the JIT vs Oxide engine model, JS config vs
  CSS-first @theme configuration, default behaviour shifts, removed APIs,
  browser baseline requirements, and the upgrade-or-stay decision tree.
  Keywords: tailwind v3, tailwind v4, tailwindcss v4, oxide engine, JIT,
  tailwind upgrade, tailwind migration, @theme, @tailwind directive removed,
  corePlugins removed, safelist removed, separator removed, ring-width changed,
  border-color changed, shadow-sm changed, should I upgrade tailwind,
  tailwind 4 vs 3, breaking changes tailwind, lightning css, @import tailwindcss
license: MIT
compatibility: "Designed for Claude Code. Requires Tailwind CSS v3.4 or v4.0+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# Tailwind CSS v3 vs v4

This skill is the version-comparison reference for Tailwind CSS. Every section
presents v3 and v4 side-by-side. Pair with companion skills:

- `tailwind-impl-migration-v3-v4` : step-by-step upgrade execution
- `tailwind-errors-v4-migration` : trap catalog when an upgrade breaks builds

## Quick Decision Tree

```
Do you control the browser baseline (Safari 16.4+, Chrome 111+, Firefox 128+)?
├── NO  → STAY on v3.4 (v4 requires @property and color-mix() support)
└── YES → Is the project new (greenfield)?
    ├── YES → USE v4 (CSS-first config, faster builds, native @import + autoprefix)
    └── NO  → Does the project use ANY of: corePlugins, safelist, separator,
              custom prefix with `tw-` pattern, JS resolveConfig at runtime,
              or Sass/Less/Stylus in the pipeline?
        ├── YES → STAY on v3.4 until alternatives are in place
        │        (corePlugins and separator have NO v4 replacement)
        └── NO  → UPGRADE with `npx @tailwindcss/upgrade` (requires Node 20+)
                  then expect visual diffs from border-color, ring-width, and
                  shadow/blur/radius scale renames.
```

## Engine Model

| Aspect | v3 (JIT) | v4 (Oxide) |
|--------|----------|------------|
| Implementation | JavaScript | Rust + Lightning CSS |
| Default since | v3.0 (Dec 2021) | v4.0 (Jan 22 2025) |
| Full build (official benchmark) | 378ms | 100ms |
| Incremental with CSS changes | 44ms | 5ms |
| Incremental without CSS changes | 35ms | 192µs |
| Marketing claim | n/a | over 3.5x full, over 8x incremental, over 100x no-CSS-change |
| `@import` bundling | requires `postcss-import` | built-in |
| Vendor prefixing | requires `autoprefixer` | built-in |
| Cascade layers | synthetic ordering | native `@layer` |
| Opacity composition | rgba mixing | `color-mix()` |
| RTL support | extra config | logical properties by default |

Source : https://tailwindcss.com/blog/tailwindcss-v4

### Browser Baseline (v4 only)

v4 ALWAYS requires Safari 16.4+, Chrome 111+, Firefox 128+ because Oxide
emits `@property` and `color-mix()`. NEVER ship v4 to a project that must
support older browsers. Stay on v3.4 instead.

## Configuration

| Topic | v3 | v4 |
|-------|----|----|
| Config file | `tailwind.config.js` (auto-detected) | None auto-detected ; legacy via `@config "./..."` |
| Tokens | JS object under `theme.extend` | CSS variables in `@theme { ... }` |
| Plugins | `plugins: [require('...')]` | `@plugin "..."` in CSS |
| Content scanning | `content: [...]` glob array | `@source "..."` directive (auto-detects by default) |
| Custom variants | `addVariant()` in plugin | `@custom-variant name (...)` in CSS |
| Dark mode | `darkMode: 'class' \| 'media' \| 'selector'` | `@custom-variant dark (&:where(.dark, .dark *))` |
| Prefix | `prefix: 'tw-'` → `tw-flex` | CSS-first prefix → `tw:flex` (variant-style) |
| Safelist | `safelist: [...]` array/regex | `@source inline("...")` with brace expansion |
| Disable utilities | `corePlugins: { float: false }` | REMOVED, no replacement |
| Custom separator | `separator: '_'` | REMOVED, no replacement |
| JS access to theme | `resolveConfig()` | REMOVED, use `getComputedStyle()` on CSS vars |

See `references/examples.md` for a complete v3 config rewritten as a v4 stylesheet.

## CSS Entry-Point

```css
/* v3 : three @tailwind directives required */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

```css
/* v4 : single @import replaces all three */
@import "tailwindcss";
```

The v3 `@tailwind` directives ALWAYS error in v4 with "Cannot apply unknown
utility class". This is the most common upgrade failure. Always replace ALL
three before first build.

## Default Behaviour Shifts (visual breakage)

These v4 changes affect EVERY existing v3 project on upgrade. Verified against
the official upgrade guide.

| Property | v3 default | v4 default | Restore-v3 shim |
|----------|------------|------------|-----------------|
| Border color | `gray-200` | `currentColor` | `@layer base { *, ::after, ::before, ::backdrop, ::file-selector-button { border-color: var(--color-gray-200, currentColor); } }` |
| Ring width | `3px` | `1px` | `@theme { --default-ring-width: 3px; }` |
| Ring color | `blue-500` | `currentColor` | `@theme { --default-ring-color: var(--color-blue-500); }` |
| Placeholder color | `gray-400` | current text at 50% opacity | Restore via `@layer base` selector override |
| Button cursor | `pointer` | `default` | `@layer base { button, [role="button"] { cursor: pointer; } }` |
| Hover variant | always applies | `@media (hover: hover)` gated | `@custom-variant hover (&:hover);` |
| `outline-none` | works | renamed to `outline-hidden` | Run upgrade tool to rename |

ALWAYS apply the shims OR refactor markup. NEVER ignore these on upgrade :
unstyled borders and 1px rings on cards/inputs are the most reported visual
regressions in v4 upgrade threads.

Source : https://tailwindcss.com/docs/upgrade-guide

## Scale Renames (size-shift by one step)

EVERY size-suffixed scale shifted down by one in v4 because a new `-xs` step
was inserted. Existing `shadow-sm` becomes visually smaller after upgrade.

| Scale | v3 smallest | v3 next | v4 smallest | v4 next |
|-------|-------------|---------|-------------|---------|
| `shadow-*` | `shadow-sm` | `shadow` | `shadow-xs` | `shadow-sm` |
| `drop-shadow-*` | `drop-shadow-sm` | `drop-shadow` | `drop-shadow-xs` | `drop-shadow-sm` |
| `blur-*` | `blur-sm` | `blur` | `blur-xs` | `blur-sm` |
| `backdrop-blur-*` | `backdrop-blur-sm` | `backdrop-blur` | `backdrop-blur-xs` | `backdrop-blur-sm` |
| `rounded-*` | `rounded-sm` | `rounded` | `rounded-xs` | `rounded-sm` |

ALWAYS run `npx @tailwindcss/upgrade` first ; it renames the call sites.
NEVER rely on visual parity after upgrade without checking each shadowed
card, input ring, and rounded badge.

## Removed Without Replacement

| Feature | v3 syntax | v4 status | Workaround |
|---------|-----------|-----------|------------|
| Disable specific utilities | `corePlugins: { float: false }` | REMOVED | Use `@source not "path/to/file"` to scope content scan, or post-process |
| Custom separator | `separator: '_'` | REMOVED | None ; refactor templates to use `:` |
| JS theme access at runtime | `import resolveConfig from 'tailwindcss/resolveConfig'` | REMOVED | `getComputedStyle(document.documentElement).getPropertyValue('--color-red-500')` |
| Sass / Less / Stylus in pipeline | worked in dev | NOT SUPPORTED | Tailwind v4 is the preprocessor ; remove the other pipeline |

If a v3 project depends on any of these, STAY on v3.4 until the dependency is
removed. Migrating then failing to compile is the most common v4 upgrade trap.

Source : https://tailwindcss.com/docs/upgrade-guide

## Variant Stacking Order (silent semantic change)

v3 reads variant chains right-to-left. v4 reads left-to-right.

```html
<!-- v3 : "first child of any direct child", reading right-to-left -->
<ul class="first:*:pt-0">

<!-- v4 equivalent : "any direct child, first one", reading left-to-right -->
<ul class="*:first:pt-0">
```

The upgrade tool rewrites common cases. ALWAYS manually review bespoke
arbitrary-variant stacks like `[&>div]:hover:bg-red-500` combined with
structural selectors. See `tailwind-syntax-variants` for the full rule set.

Source : https://tailwindcss.com/docs/upgrade-guide

## Renamed Utilities (auto-fixed by upgrade tool)

| v3 | v4 |
|----|-----|
| `bg-opacity-50`, `text-opacity-*`, `border-opacity-*`, `divide-opacity-*`, `ring-opacity-*`, `placeholder-opacity-*` | Use slash modifier : `bg-red-500/50`, `text-white/85` |
| `flex-shrink-*`, `flex-grow-*` | `shrink-*`, `grow-*` |
| `overflow-ellipsis` | `text-ellipsis` |
| `bg-gradient-to-r` | `bg-linear-to-r` (also `bg-radial-*`, `bg-conic-*`) |
| `!flex` (important prefix) | `flex!` (important suffix) |
| `bg-[--brand]` (CSS var arbitrary) | `bg-(--brand)` (parens, not brackets) |
| `grid-cols-[max-content,auto]` (comma) | `grid-cols-[max-content_auto]` (underscore for space) |

Full table in `references/methods.md`.

## New v4-Only APIs

| Directive | Purpose | v3 equivalent |
|-----------|---------|---------------|
| `@import "tailwindcss"` | Replaces all three `@tailwind` directives | `@tailwind base/components/utilities` |
| `@theme { --token: ... }` | Define design tokens as CSS variables | `theme.extend` in JS config |
| `@plugin "name"` | Load a JS plugin from CSS | `plugins: [require('name')]` |
| `@source "path"` | Add a content-scan path | `content: ['path']` |
| `@source inline("...")` | Safelist utilities by string | `safelist: [...]` |
| `@source not "path"` | Exclude a path from content scan | Could exclude via `content` glob negation |
| `@utility name { ... }` | Define a custom utility | `addUtilities()` in plugin |
| `@variant name` | Apply a variant to a block | n/a |
| `@custom-variant name (...)` | Register a new variant | `addVariant()` in plugin |
| `@reference "./app.css"` | Make `@apply` work in scoped `<style>` blocks (Vue, Svelte, CSS modules) | not needed (v3 auto-included context) |
| `@config "./tailwind.config.js"` | Opt-in load legacy v3 JS config | n/a (auto-loaded in v3) |
| `--value(--color-*)`, `--modifier()`, `--alpha()`, `--spacing()` | Functional CSS helpers inside `@utility` | not available |

## The `@reference` Trap (Vue, Svelte, CSS modules)

v3 scoped stylesheets in Vue SFC `<style>`, Svelte component `<style>`, and
CSS modules ALWAYS had implicit theme context. v4 compiles each scoped block
in isolation, so `@apply text-2xl` fails with "Cannot apply unknown utility
class".

```vue
<!-- v3 : works -->
<style scoped>
.btn { @apply px-4 py-2 bg-blue-500 text-white; }
</style>
```

```vue
<!-- v4 : requires @reference at the top of the scoped block -->
<style scoped>
@reference "../app.css";
.btn { @apply px-4 py-2 bg-blue-500 text-white; }
</style>
```

ALWAYS add `@reference` to every scoped `<style>` block in v4 projects.
NEVER assume `@apply` works without it. See `tailwind-errors-v4-migration`
for the full failure mode catalogue.

Source : https://tailwindcss.com/docs/functions-and-directives and
https://github.com/tailwindlabs/tailwindcss/issues/16346

## Decision Tree : Should I Upgrade Now?

```
START
  │
  ├── Browser support requires IE11, Safari <16.4, Chrome <111, or Firefox <128 ?
  │   └── YES → STAY v3.4 (hard blocker, v4 cannot work)
  │
  ├── Project uses corePlugins to disable utilities ?
  │   └── YES → STAY v3.4 until the disabled utilities are removed
  │       from source instead (no v4 replacement exists)
  │
  ├── Project uses Sass, Less, or Stylus preprocessor ?
  │   └── YES → STAY v3.4 until preprocessor is removed
  │
  ├── Project uses resolveConfig() in runtime JS (e.g. a charting lib that
  │   needs tailwind theme colours at runtime) ?
  │   └── YES → Refactor to read `getComputedStyle(...).getPropertyValue('--color-*')`,
  │             THEN upgrade
  │
  ├── Project uses safelist with regex patterns ?
  │   └── YES → Rewrite as `@source inline("...")` with brace expansion,
  │             THEN upgrade
  │
  ├── Project is Vue / Svelte / CSS-modules with scoped <style> blocks ?
  │   └── YES → UPGRADE possible, BUT add `@reference "../app.css";` to
  │             every scoped block first or post-upgrade
  │
  └── None of the above → UPGRADE
      ├── Run `npx @tailwindcss/upgrade` on a clean branch (Node 20+)
      ├── Apply the v3-default shims for border-color and ring (if visual
      │   parity matters more than clean v4 code)
      └── Verify shadow / blur / rounded / drop-shadow / backdrop-blur
          call sites visually (sizes shifted by one step)
```

## Partial Upgrade Strategy

v4 ALWAYS supports the v3 JS config via `@config "./tailwind.config.js"`,
so a partial upgrade path is :

1. Move to the v4 engine (replace `@tailwind` with `@import "tailwindcss"`).
2. Keep `@config "./tailwind.config.js";` at the top of the stylesheet.
3. Migrate `theme.extend` keys to `@theme` block one category at a time.
4. Remove `@config` when nothing remains in the JS config.

NEVER mix `@theme` and `theme.extend` for the SAME token category : the v4
`@theme` wins but the duplication causes silent drift. Migrate per category
and delete the JS-config entry in the same commit.

## Cross-References

| Topic | Skill |
|-------|-------|
| Upgrade execution (codemod, validation, rollback) | `tailwind-impl-migration-v3-v4` |
| Trap catalogue when an upgrade breaks builds | `tailwind-errors-v4-migration` |
| Variant stacking rules (with v3 vs v4 examples) | `tailwind-syntax-variants` |
| Dark mode setup (v3 `darkMode` vs v4 `@custom-variant dark`) | `tailwind-syntax-dark-mode` |
| Plugin authoring (v3 JS vs v4 CSS-first) | `tailwind-impl-plugins-custom` |
| Build integration per framework | `tailwind-impl-build-*` |

## Reference Files

- `references/methods.md` : complete API breaking-changes table (removed, renamed, new)
- `references/examples.md` : side-by-side v3 vs v4 code for install, config, dark mode, plugins, scoped styles
- `references/anti-patterns.md` : upgrade traps with root cause and fix

## Verified Sources

- https://tailwindcss.com/blog/tailwindcss-v4 (engine, performance numbers)
- https://tailwindcss.com/docs/upgrade-guide (breaking changes, shims)
- https://tailwindcss.com/docs/functions-and-directives (new v4 APIs)
- https://v3.tailwindcss.com/docs/configuration (v3 config surface)
- https://github.com/tailwindlabs/tailwindcss/issues/16346 (`@apply` + `@reference` trap)
