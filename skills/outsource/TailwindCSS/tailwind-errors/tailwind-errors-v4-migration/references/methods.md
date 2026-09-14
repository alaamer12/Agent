# Reference : v3 to v4 Migration Methods

Exhaustive rename tables, codemod command, config-option mapping, and
browser support.

## The official codemod

```bash
npx @tailwindcss/upgrade
```

What it does mechanically :

- Replaces `@tailwind base/components/utilities` with `@import "tailwindcss"`.
- Renames utilities (`shadow` → `shadow-sm`, `shadow-sm` → `shadow-xs`, etc.).
- Flips important modifier from `!class` to `class!`.
- Flips prefix syntax from `tw-class` to `tw:class`.
- Converts `bg-opacity-50` → `bg-black/50` where possible.
- Migrates `corePlugins` / `safelist` / `separator` config out.
- Wraps `theme()` calls in the new CSS-variable syntax.

What it does NOT catch :

- Variant order semantic changes (only the common forms are mapped).
- Default behavior changes (border color, ring width).
- @layer utilities to @utility migration.
- Custom plugin code calling removed APIs.
- Comments containing class names.
- Class names assembled from template strings (`bg-${color}-500`).

ALWAYS read the codemod's diff before committing. ALWAYS run a visual
regression suite afterwards.

## Utility rename table

### Shadow / blur / radius / drop-shadow / backdrop-blur

| v3                 | v4                  |
| ------------------ | ------------------- |
| `shadow-sm`        | `shadow-xs`         |
| `shadow`           | `shadow-sm`         |
| `shadow-md`        | (unchanged)         |
| `shadow-lg`        | (unchanged)         |
| `drop-shadow-sm`   | `drop-shadow-xs`    |
| `drop-shadow`      | `drop-shadow-sm`    |
| `blur-sm`          | `blur-xs`           |
| `blur`             | `blur-sm`           |
| `backdrop-blur-sm` | `backdrop-blur-xs`  |
| `backdrop-blur`    | `backdrop-blur-sm`  |
| `rounded-sm`       | `rounded-xs`        |
| `rounded`          | `rounded-sm`        |

Pattern : `*-sm` shrank by one step ; the unsuffixed base became `*-sm`.

### Removed utilities

| v3                   | v4                       |
| -------------------- | ------------------------ |
| `flex-shrink-*`      | `shrink-*`               |
| `flex-grow-*`        | `grow-*`                 |
| `overflow-ellipsis`  | `text-ellipsis`          |
| `decoration-slice`   | `box-decoration-slice`   |
| `decoration-clone`   | `box-decoration-clone`   |
| `bg-opacity-*`       | `bg-COLOR/OPACITY`       |
| `text-opacity-*`     | `text-COLOR/OPACITY`     |
| `border-opacity-*`   | `border-COLOR/OPACITY`   |
| `divide-opacity-*`   | `divide-COLOR/OPACITY`   |
| `ring-opacity-*`     | `ring-COLOR/OPACITY`     |
| `placeholder-opacity-*` | `placeholder-COLOR/OPACITY` |

### Renamed utilities

| v3              | v4               |
| --------------- | ---------------- |
| `outline-none`  | `outline-hidden` (v4 `outline-none` now means `outline-style:none`) |
| `transform`     | (removed ; v4 emits per-property)  |
| `transform-gpu` | (removed)        |
| `transform-cpu` | (removed)        |
| `transform-none`| (split : `rotate-none`, `scale-none`, `translate-none`) |

## Default-behavior change table

| Property                | v3 default             | v4 default        | Recovery shim |
| ----------------------- | ---------------------- | ----------------- | ------------- |
| `border-color`          | `var(--color-gray-200)`| `currentColor`    | `@layer base { *, ::after, ::before, ::backdrop { border-color: var(--color-gray-200, currentColor); } }` |
| `divide-color`          | `var(--color-gray-200)`| `currentColor`    | Same as border |
| `ring-width`            | `3px`                  | `1px`             | Replace `ring` with `ring-3` |
| `ring-color`            | `var(--color-blue-500)`| `currentColor`    | Add explicit `ring-blue-500` |
| Variant stacking order  | right-to-left          | left-to-right     | Swap order manually |
| `hover:`                | unconditional          | `@media (hover: hover)` | Pair with `active:` / `focus:` |
| `space-x-*` selector    | `> :not([hidden]) ~ :not([hidden])` | `> :not(:last-child)` | None ; verify visually |
| `divide-x-*` selector   | `> :not([hidden]) ~ :not([hidden])` | `> :not(:last-child)` | None ; verify visually |

## Config-option migration map

| v3 JS config option | v4 replacement |
| ------------------- | -------------- |
| `content`           | `@source "path"` in entry CSS, or rely on auto-detect |
| `theme.extend.colors` | `@theme { --color-name: value; }` |
| `theme.extend.spacing` | `@theme { --spacing-name: value; }` |
| `theme.extend.fontFamily` | `@theme { --font-name: value; }` |
| `darkMode: "class"` | `@custom-variant dark (&:where(.dark, .dark *));` |
| `corePlugins`       | NO direct replacement ; use `@utility` for custom |
| `safelist`          | `@source inline "{...}"` in entry CSS |
| `separator`         | NO replacement ; v4 only supports `:` |
| `prefix: "tw-"`     | `@import "tailwindcss" prefix(tw);` |
| `plugins: [...]`    | `@plugin "name"` in entry CSS for legacy JS plugins |

### Opt-in JS config bridge

For staged migration, keep the v3 JS config :

```css
@import "tailwindcss";
@config "./tailwind.config.js";
```

The bridge reads `theme`, `content`, `plugins` from the JS config.
NEVER use the bridge long-term ; it is a migration aid.

## Important-modifier syntax flip

| Context      | v3                              | v4                       |
| ------------ | ------------------------------- | ------------------------ |
| HTML class   | `class="!flex !bg-red-500"`     | `class="flex! bg-red-500!"` |
| @apply       | `@apply font-bold !important;`  | `@apply font-bold!;`     |
| Sass @apply  | `@apply font-bold #{!important};` | `@apply font-bold!;`   |

## Prefix syntax flip

```diff
- // tailwind.config.js (v3)
- prefix: "tw-"

- <div class="tw-flex tw-hover:bg-red-500">

+ /* app.css (v4) */
+ @import "tailwindcss" prefix(tw);

+ <div class="tw:flex tw:hover:bg-red-500">
```

## Arbitrary-value syntax changes

| Use case               | v3                                 | v4                                 |
| ---------------------- | ---------------------------------- | ---------------------------------- |
| CSS variable shortcut  | `bg-[--brand]`                     | `bg-(--brand)`                     |
| Space in arbitrary value | `grid-cols-[max-content,auto]`   | `grid-cols-[max-content_auto]`     |
| Function call          | `w-[calc(100%-1rem)]`              | (unchanged)                        |
| Color with opacity     | `bg-[#abc]/50`                     | (unchanged)                        |

## theme() function syntax

```diff
  /* v3 */
- @media (width >= theme(screens.xl)) { ... }

  /* v4 */
+ @media (width >= theme(--breakpoint-xl)) { ... }
```

Theme dot notation is gone. Use the underlying CSS-variable name with
the `--` prefix.

## Custom utilities migration

```diff
  /* v3 */
- @layer utilities {
-   .tab-4 { tab-size: 4; }
- }

  /* v4 */
+ @utility tab-4 {
+   tab-size: 4;
+ }
```

v4's `@utility` supports parameter helpers :

```css
@utility tab-* {
  tab-size: --value(integer);
}
```

## Browser-support matrix

| Browser   | v3 minimum | v4 minimum |
| --------- | ---------- | ---------- |
| Safari    | 14         | 16.4       |
| Chrome    | 99         | 111        |
| Firefox   | 99         | 128        |

v4 depends on `@property`, `color-mix()`, and modern container queries.
NEVER ship v4 to a project that must support browsers older than
the v4 minimums.

## Audit checklist (post-codemod)

1. Borders : grep `class="[^"]*border[^"]*"` and confirm explicit
   color OR base shim is in place.
2. Rings : grep for bare `ring` (without width suffix) and replace
   with `ring-3` if v3 visual is required.
3. Shadows : visually diff every layer that uses shadows.
4. Variant order : grep for stacked variants with `*:` or `first:`
   and confirm semantics.
5. Opacity modifiers : grep `*-opacity-` for any leftovers.
6. Outline : confirm every `outline-none` was meant as the v3 behavior
   (now `outline-hidden`).
7. `@layer utilities`: confirm custom utilities migrated to `@utility`.
8. JS config bridge : if `@config` is in use, plan removal.
9. Browser support : confirm target browsers meet v4 minimums.
10. Visual regression suite : run before / after the merge.

## CI-level migration check

`package.json` :

```json
{
  "scripts": {
    "audit:tailwind-v4": "node scripts/audit-tailwind-v4.mjs"
  }
}
```

`scripts/audit-tailwind-v4.mjs` (grep heuristics) :

```js
import { execSync } from "node:child_process"

const checks = [
  { pattern: /class=["'][^"']*!\w/, name: "leading-bang !class (v3 syntax)" },
  { pattern: /\btw-(?:flex|grid|block|hidden)\b/, name: "v3-style prefix tw-" },
  { pattern: /-opacity-\d+/, name: "bg-opacity-* / text-opacity-* (removed)" },
  { pattern: /\bring\b(?!-\d)/, name: "bare ring (default width changed)" },
  { pattern: /\[--[a-z]/, name: "v3 arbitrary CSS var [--var]" },
]

for (const { pattern, name } of checks) {
  const found = execSync(
    `grep -rEn "${pattern.source}" src/ || true`,
    { encoding: "utf-8" }
  )
  if (found) console.error(`[v3 leftover: ${name}]\n${found}`)
}
```

Wire this into CI to catch leftovers regression-style.
