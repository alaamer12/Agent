# Breaking-Changes API Reference

Complete table of every Tailwind CSS v3 to v4 API change. Source : official
upgrade guide at https://tailwindcss.com/docs/upgrade-guide (verified
2026-05-19).

## 1. Removed APIs (no v4 replacement OR opt-in only)

| v3 API | v4 status | Workaround |
|--------|-----------|------------|
| `@tailwind base` | REMOVED | `@import "tailwindcss"` covers all three |
| `@tailwind components` | REMOVED | Same as above |
| `@tailwind utilities` | REMOVED | Same as above |
| `tailwind.config.js` auto-load | REMOVED | Opt-in via `@config "./tailwind.config.js";` |
| `corePlugins: { float: false }` | REMOVED | No direct replacement ; use `@source not "..."` or post-process |
| `safelist: [...]` array/regex | REMOVED | `@source inline("classnames")` with brace expansion |
| `separator: '_'` | REMOVED | None ; refactor templates to `:` |
| `resolveConfig` JS export | REMOVED | `getComputedStyle(...).getPropertyValue('--color-*')` |
| `theme()` JS function in user code | REMOVED | Use CSS `var(--color-*)` directly |
| Sass / Less / Stylus pipeline | NOT SUPPORTED | Remove preprocessor ; Tailwind v4 is the preprocessor |
| `postcss-import` plugin | NOT NEEDED | `@import` is bundled by Oxide |
| `autoprefixer` plugin | NOT NEEDED | Vendor prefixing built-in |
| `theme.future.hoverOnlyWhenSupported` | REMOVED (now default) | n/a, behaviour is the new default |

## 2. Renamed Utilities (auto-fixed by `npx @tailwindcss/upgrade`)

### 2.1 Opacity Utilities → Slash Modifier

| v3 | v4 |
|----|----|
| `bg-opacity-50` | `bg-red-500/50` (slash modifier on the colour utility) |
| `text-opacity-*` | `text-white/85` |
| `border-opacity-*` | `border-blue-500/25` |
| `divide-opacity-*` | `divide-gray-200/50` |
| `ring-opacity-*` | `ring-blue-500/50` |
| `placeholder-opacity-*` | `placeholder-gray-500/40` |

### 2.2 Flexbox Shorthands

| v3 | v4 |
|----|----|
| `flex-shrink-0` | `shrink-0` |
| `flex-shrink` | `shrink` |
| `flex-grow-0` | `grow-0` |
| `flex-grow` | `grow` |

### 2.3 Text Overflow

| v3 | v4 |
|----|----|
| `overflow-ellipsis` | `text-ellipsis` |

### 2.4 Gradient Direction

| v3 | v4 |
|----|----|
| `bg-gradient-to-r` | `bg-linear-to-r` |
| `bg-gradient-to-br` | `bg-linear-to-br` |
| (n/a) | `bg-radial`, `bg-radial-[at_25%_25%]` |
| (n/a) | `bg-conic`, `bg-conic-180` |

### 2.5 Important Modifier Position

| v3 | v4 |
|----|----|
| `!flex` | `flex!` |
| `!bg-red-500` | `bg-red-500!` |
| `hover:!underline` | `hover:underline!` |

### 2.6 CSS-Variable Arbitrary Syntax

| v3 | v4 |
|----|----|
| `bg-[--brand]` | `bg-(--brand)` |
| `text-[--fg]` | `text-(--fg)` |
| `w-[--my-width]` | `w-(--my-width)` |

The bracket form `bg-[--brand]` still parses in v4 but emits a warning ; the
canonical form is parentheses.

### 2.7 Arbitrary Values With Spaces

| v3 | v4 |
|----|----|
| `grid-cols-[max-content,auto]` | `grid-cols-[max-content_auto]` |
| `bg-[200px,100px]` | `bg-[200px_100px]` |

v3 used a comma separator. v4 uses underscore (which Tailwind converts to a
space at output time). Commas are reserved for value lists in modern CSS.

### 2.8 Outline

| v3 | v4 |
|----|----|
| `outline-none` (was visually hidden, screen-reader friendly) | `outline-hidden` |
| `outline outline-2` | `outline-2` (width 1px default) |

### 2.9 Transform Reset

| v3 | v4 |
|----|----|
| `transform-none` (resets everything) | Use individual `scale-none`, `rotate-none`, `translate-none`, `skew-none` |

## 3. Scale Renames (size-shifted by one step)

A new `-xs` step was inserted at the bottom of each size scale. ALL existing
size suffixes shifted down by one. The visual size of `shadow-sm` in v4 is
SMALLER than v3's `shadow-sm` (it equals v3's pre-`shadow-xs` step).

| Utility | v3 step 1 | v3 step 2 | v4 step 1 | v4 step 2 |
|---------|-----------|-----------|-----------|-----------|
| Box shadow | `shadow-sm` | `shadow` | `shadow-xs` | `shadow-sm` |
| Drop shadow | `drop-shadow-sm` | `drop-shadow` | `drop-shadow-xs` | `drop-shadow-sm` |
| Blur | `blur-sm` | `blur` | `blur-xs` | `blur-sm` |
| Backdrop blur | `backdrop-blur-sm` | `backdrop-blur` | `backdrop-blur-xs` | `backdrop-blur-sm` |
| Border radius | `rounded-sm` | `rounded` | `rounded-xs` | `rounded-sm` |

Steps `-md`, `-lg`, `-xl`, `-2xl` etc. did NOT change position.

## 4. Default Value Shifts (visual breaking)

| Property | v3 default | v4 default | Restore CSS |
|----------|------------|------------|-------------|
| `border-color` | `theme(colors.gray.200)` | `currentColor` | `@layer base { *, ::after, ::before, ::backdrop, ::file-selector-button { border-color: var(--color-gray-200, currentColor); } }` |
| `--default-ring-width` | `3px` | `1px` | `@theme { --default-ring-width: 3px; }` |
| `--default-ring-color` | `theme(colors.blue.500)` | `currentColor` | `@theme { --default-ring-color: var(--color-blue-500); }` |
| `::placeholder` color | `theme(colors.gray.400)` | current text colour at 50% opacity | `@layer base { input::placeholder, textarea::placeholder { color: var(--color-gray-400); } }` |
| `button` cursor | `pointer` | `default` | `@layer base { button:not(:disabled), [role="button"]:not(:disabled) { cursor: pointer; } }` |
| `space-y-*` selector | `> :not([hidden]) ~ :not([hidden])` | `> :not(:last-child)` with margin-bottom | (performance change ; no shim needed unless ordering matters) |
| `divide-*` selector | Complex `~` chain | `> :not(:last-child)` with border-bottom | Same as above |

## 5. Variant Stacking Order (silent behaviour change)

v3 reads chains right-to-left (innermost first). v4 reads chains
left-to-right (outermost first). The CSS output is the same SHAPE but the
SELECTOR composes differently.

| v3 input | v4 input (semantically equivalent) |
|----------|------------------------------------|
| `first:*:pt-0` | `*:first:pt-0` |
| `last:hover:bg-red-500` | `hover:last:bg-red-500` |

Variants that target only ONE thing (single `hover:`, single `focus:`) are
unaffected. Only chains of 2+ variants need flipping.

## 6. Hover Variant Gating

v3 : `hover:bg-blue-500` applies on every device, including touch devices
where hover is a brief tap-and-hold artefact.

v4 : `hover:bg-blue-500` is wrapped in `@media (hover: hover)` so it ONLY
applies on devices with a real hover capability.

```css
/* v4 escape hatch : restore v3 always-apply behaviour */
@custom-variant hover (&:hover);
```

## 7. New v4-Only Directives

| Directive | Syntax | Purpose |
|-----------|--------|---------|
| `@import "tailwindcss"` | top of stylesheet | Loads base, components, utilities |
| `@import "tailwindcss/preflight"` | partial import | Just the reset |
| `@import "tailwindcss/utilities"` | partial import | Just the utilities layer |
| `@theme { ... }` | block | Defines CSS-variable design tokens |
| `@theme inline { ... }` | block | Defines tokens that resolve at build time, not runtime |
| `@theme static { ... }` | block | Forces emission of all theme variables (even if unused) |
| `@plugin "name"` | one-liner | Loads a JS plugin from CSS |
| `@source "path"` | one-liner | Adds a content-scan glob |
| `@source not "path"` | one-liner | Excludes a path from content scan |
| `@source inline("...")` | one-liner | Safelists utilities (supports `{a,b,c}` brace expansion and `{1..9}` range) |
| `@utility name { ... }` | block | Defines a custom utility (replaces `addUtilities()`) |
| `@variant name` | inline | Applies a variant inside CSS |
| `@custom-variant name (...)` | one-liner | Registers a new variant (replaces `addVariant()`) |
| `@reference "./app.css"` | top of scoped block | Makes theme tokens available in Vue/Svelte/CSS-modules `<style>` |
| `@config "./tailwind.config.js"` | top of stylesheet | Opt-in legacy v3 config loader |
| `@apply` | inline | Same as v3, but requires `@reference` in scoped contexts |

## 8. New v4-Only Functional Helpers (inside `@utility`)

| Function | Returns | Example |
|----------|---------|---------|
| `--value(--color-*)` | Resolved value of the matched theme key | `background: --value(--color-*);` |
| `--modifier()` | The modifier portion of the utility class | `opacity: --modifier(integer);` |
| `--alpha()` | Composes alpha into a colour | `background: --alpha(var(--color-red-500), 0.5);` |
| `--spacing()` | Multiplies the spacing base by N | `padding: --spacing(4);` (resolves to `calc(var(--spacing) * 4)`) |

These functions exist ONLY in v4. They replace many v3 plugin patterns that
previously required JS. See `tailwind-syntax-functional-utilities` for the
full reference.

## 9. Prefix Syntax

| Topic | v3 | v4 |
|-------|----|----|
| Config | `prefix: 'tw-'` in JS | CSS-first via prefix-mode invocation : `@import "tailwindcss" prefix(tw);` |
| Applied | `<div class="tw-flex hover:tw-bg-red-500">` | `<div class="tw:flex tw:hover:bg-red-500">` |
| Inside chain | `hover:tw-bg-red-500` | `tw:hover:bg-red-500` (prefix at the front) |

## 10. Theme Token Access at Runtime (JS)

| Need | v3 | v4 |
|------|----|----|
| Read a theme colour in JS | `import resolveConfig from 'tailwindcss/resolveConfig'; const cfg = resolveConfig(tailwindConfig); cfg.theme.colors.red['500']` | `getComputedStyle(document.documentElement).getPropertyValue('--color-red-500').trim()` |
| Read spacing | Same `resolveConfig` path | `getComputedStyle(document.documentElement).getPropertyValue('--spacing')` (the base step) |
| Read breakpoint | `cfg.theme.screens.md` | `getComputedStyle(document.documentElement).getPropertyValue('--breakpoint-md')` |

## 11. Package Layout

| Topic | v3 | v4 |
|-------|----|----|
| Core install | `npm install -D tailwindcss postcss autoprefixer` | `npm install tailwindcss @tailwindcss/postcss` OR `@tailwindcss/vite` |
| PostCSS config plugin | `tailwindcss: {}` and `autoprefixer: {}` | `'@tailwindcss/postcss': {}` only |
| Vite integration | Via PostCSS | First-class plugin `@tailwindcss/vite` (Vite 5+) |
| Standalone CLI | `npx tailwindcss -i ./src/in.css -o ./dist/out.css` | `npx @tailwindcss/cli -i ./src/in.css -o ./dist/out.css` |

## 12. Browser Baseline

| Engine | Browsers |
|--------|----------|
| v3 (JIT) | All modern browsers ; downlevel support possible with autoprefixer config |
| v4 (Oxide) | REQUIRES Safari 16.4+, Chrome 111+, Firefox 128+ (uses `@property`, `color-mix()`) |

Source : https://tailwindcss.com/docs/upgrade-guide

## 13. Verification

All entries verified against :
- https://tailwindcss.com/docs/upgrade-guide (sections 1 through 8)
- https://tailwindcss.com/docs/functions-and-directives (new directives)
- https://tailwindcss.com/blog/tailwindcss-v4 (engine details)
- https://v3.tailwindcss.com/docs/configuration (v3 baseline)
