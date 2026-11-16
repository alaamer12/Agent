# breaking-changes — the complete v3 → v4 change catalog

Single-owner data catalog for every rename, removal, default shift, syntax flip, and config-option
replacement. [`../method.md`](../method.md) owns the decision table, audit workflow, shim snippets,
and the 15-row quick summary; this file is what those summaries compress. Directive *semantics*
(what `@theme`/`@utility`/`@source` accept) belong to `../config/method.md`; the `@source inline`
expansion grammar belongs to `../dynamic-classes/method.md`; default token *values* belong to
`../design-system/method.md`. Worked code for every row: [`examples.md`](examples.md); mistakes made
while applying these rows: [`anti-patterns.md`](anti-patterns.md).

## 1. Renamed utilities

All rows in this section are auto-fixed by `npx @tailwindcss/upgrade` in literal class strings.

### 1.1 Size-scale shift (shadow / blur / radius family)

A new `-xs` step was inserted at the bottom of each scale; every existing suffix moved one step down.
The CSS values of a renamed pair are **identical** — only the name moved. Steps `-md`, `-lg`, `-xl`,
`-2xl` and the unsuffixed extremes did NOT change position.

| Utility family | v3 step 1 | v3 step 2 | v4 step 1 | v4 step 2 |
|---|---|---|---|---|
| Box shadow | `shadow-sm` | `shadow` | `shadow-xs` | `shadow-sm` |
| Drop shadow | `drop-shadow-sm` | `drop-shadow` | `drop-shadow-xs` | `drop-shadow-sm` |
| Blur | `blur-sm` | `blur` | `blur-xs` | `blur-sm` |
| Backdrop blur | `backdrop-blur-sm` | `backdrop-blur` | `backdrop-blur-xs` | `backdrop-blur-sm` |
| Border radius | `rounded-sm` | `rounded` | `rounded-xs` | `rounded-sm` |

Pattern: `*-sm` shrank by one step; the unsuffixed base became `*-sm`.

### 1.2 Opacity utilities → slash modifier

The six standalone opacity utilities are removed; opacity composes into the color utility itself.

| v3 | v4 form |
|---|---|
| `bg-opacity-*` | `bg-red-500/50` (slash modifier on the color utility) |
| `text-opacity-*` | `text-white/85` |
| `border-opacity-*` | `border-blue-500/25` |
| `divide-opacity-*` | `divide-gray-200/50` |
| `ring-opacity-*` | `ring-blue-500/50` |
| `placeholder-opacity-*` | `placeholder-gray-500/40` |

Composed at runtime as `bg-opacity-${n}`-style strings, the codemod cannot see them —
`../dynamic-classes/method.md`.

### 1.3 Flexbox shorthands, text overflow, text decoration

| v3 | v4 |
|---|---|
| `flex-shrink-*` | `shrink-*` (`flex-shrink-0` → `shrink-0`, bare `flex-shrink` → `shrink`) |
| `flex-grow-*` | `grow-*` (`flex-grow-0` → `grow-0`, bare `flex-grow` → `grow`) |
| `overflow-ellipsis` | `text-ellipsis` |
| `decoration-slice` | `box-decoration-slice` |
| `decoration-clone` | `box-decoration-clone` |

### 1.4 Gradient renames

| v3 | v4 |
|---|---|
| `bg-gradient-to-t` / `-tr` / `-r` / `-br` / `-b` / `-bl` / `-l` / `-tl` | `bg-linear-to-t` … `bg-linear-to-tl` (all eight directions renamed) |
| `from-*` / `via-*` / `to-*` color stops | unchanged |
| (n/a) | new: `bg-radial`, `bg-radial-[at_25%_25%]`, `bg-conic`, `bg-conic-180` |

### 1.5 Outline

| v3 | v4 |
|---|---|
| `outline-none` (visually hidden outline, still visible in forced-colors mode) | `outline-hidden` |
| `outline outline-2` (style + width pair) | `outline-2` (width utilities stand alone; default width 1px) |
| — | v4's `outline-none` now literally sets `outline-style: none` — an a11y trap (see AP-20) |

### 1.6 Transform family

| v3 | v4 |
|---|---|
| `transform` (composition hint) | REMOVED — v4 applies scale/rotate/translate as individual CSS transform properties; no composition utility needed |
| `transform-gpu` | REMOVED |
| `transform-cpu` | REMOVED |
| `transform-none` (resets everything) | SPLIT — use individual `scale-none`, `rotate-none`, `translate-none`, `skew-none` |
| `transition-[opacity,transform]` | `transition-[opacity,scale]` — transition property lists name the individual properties now |

## 2. Syntax flips (selector-level changes)

### 2.1 Variant stacking order

v3 evaluates variant chains right-to-left (innermost first); v4 evaluates left-to-right (outermost
first). The output CSS has the same shape but the selector composes differently. Only chains of
2+ variants need flipping; single `hover:`/`focus:` are unaffected.

| v3 input | v4 input (semantically equivalent) |
|---|---|
| `first:*:pt-0` | `*:first:pt-0` |
| `last:hover:bg-red-500` | `hover:last:bg-red-500` |
| `group-hover:first:*:opacity-100` | `group-hover:*:first:opacity-100` |
| `[&>[data-active]]:hover:bg-red-500` | `hover:[&>[data-active]]:bg-red-500` |

The codemod maps only the common forms; arbitrary `[&…]` variants combined with structural
pseudo-classes need manual review (see AP-10).

### 2.2 Important modifier position

| Context | v3 | v4 |
|---|---|---|
| HTML class | `!flex`, `!bg-red-500`, `hover:!underline` | `flex!`, `bg-red-500!`, `hover:underline!` |
| inside `@apply` | `@apply font-bold !important;` | `@apply font-bold!;` |
| inside Sass | `@apply font-bold #{!important};` | `@apply font-bold!;` |

### 2.3 Prefix form

| Topic | v3 | v4 |
|---|---|---|
| Declaration | `prefix: 'tw-'` in JS config | `@import "tailwindcss" prefix(tw);` |
| Applied | `class="tw-flex hover:tw-bg-red-500"` | `class="tw:flex tw:hover:bg-red-500"` |
| Inside a chain | prefix glued to the utility, variants outside | prefix becomes a variant and goes FIRST: `tw:hover:bg-red-500` |

The `tw-` → `tw:` flip is mechanical but touches EVERY utility containing the prefix — including test
selectors, stories, and docs (see AP-17).

### 2.4 Arbitrary values

| Use case | v3 | v4 |
|---|---|---|
| CSS-variable shortcut | `bg-[--brand]`, `text-[--fg]`, `w-[--my-width]` | `bg-(--brand)`, `text-(--fg)`, `w-(--my-width)` |
| Space inside arbitrary value | `grid-cols-[max-content,auto]`, `object-[center,top]`, `bg-[200px,100px]` | `grid-cols-[max-content_auto]`, `object-[center_top]`, `bg-[200px_100px]` |
| Function call | `w-[calc(100%-1rem)]` | unchanged |
| Color with opacity | `bg-[#abc]/50` | unchanged |

Root causes: modern CSS made the bracket var form ambiguous (v4 still parses `bg-[--brand]` but as a
raw value with a warning, not a variable reference — silent fallback, see AP-21); commas are now
reserved for value lists in real CSS functions, so underscores carry spaces
(`grid-cols-[max-content_auto_minmax(0,1fr)]` — commas INSIDE `minmax()` stay commas).

## 3. Default-behavior changes (visual breaking, no build error)

None of these produce a compile error; the codemod is silent on all of them (see AP-1). Shim column:
`method.md` §6 carries the border/ring/hover shims verbatim; the additional restore rules live in
[`examples.md`](examples.md) §5.

| Change | v3 default | v4 default | Root cause | Explicit fix | Shim |
|---|---|---|---|---|---|
| `border-color` on `border*` utilities | `theme(colors.gray.200)` | `currentColor` | Preflight no longer seeds a palette color; borders follow text color | add `border-<color>` at every usage | `method.md` §6 base rule |
| `divide-color` on `divide*` utilities | `theme(colors.gray.200)` | `currentColor` | same | add `divide-<color>` | same base rule (covers dividers) |
| Ring width on bare `ring` | `3px` (`--default-ring-width`) | `1px` | theme variable changed | `ring-3` | `method.md` §6 `@theme` |
| Ring color on bare `ring` | `theme(colors.blue.500)` (`--default-ring-color`) | `currentColor` | theme variable changed | explicit `ring-<color>` | `method.md` §6 `@theme` |
| `::placeholder` color | `theme(colors.gray.400)` | current text color at 50% opacity | placeholder opacity utilities removed; preflight switched to inherited-color mixing | explicit `placeholder:<color>` | `examples.md` §5 |
| `button` cursor | `pointer` | `default` | preflight dropped the cursor rule | add `cursor-pointer` | `examples.md` §5 |
| `dialog` centering | preflight kept UA `margin: auto` behavior usable | centering lost | preflight change | `m-auto` utility | `examples.md` §5 |
| `hidden` attribute vs display utilities | preflight forced `[hidden] { display: none !important }` | that override removed; `block`/`flex`/`grid` win over the attribute | preflight slimmed to respect `hidden="until-found"` semantics | toggle the class, not the attribute | `examples.md` §5 |
| `hover:` variant | applies on every device, including touch tap-and-hold | wrapped in `@media (hover: hover)` | v3's opt-in `future.hoverOnlyWhenSupported` is now the hard default (the option itself is removed) | pair with `active:` / `focus:`; use `aria-expanded` state for menus | `method.md` §6 `@custom-variant hover (&:hover)` — last resort only |
| Variant stacking order | right-to-left | left-to-right | engine selector-composition rewrite | flip chains | none — semantic, codemod can't guess intent (§2.1) |
| `space-x-*` / `space-y-*` selector | `> :not([hidden]) ~ :not([hidden])` (sibling combinator skipping hidden children) | `> :not(:last-child)` + margin-inline / margin-block | performance: one simpler selector replaces the fragile `~` chain | none required; hidden siblings now still receive the gap — verify visually when lists mix visible and `hidden` children | none documented |
| `divide-x-*` / `divide-y-*` selector | complex `~` chain | `> :not(:last-child)` + border-right / border-bottom | same | same caveat — verify visually | none documented |
| `*-sm` / base sizes (§1.1 scales) | — | — | name move only; CSS values identical | run the codemod, don't hand-rename (double-rename risk, see AP-9) | n/a |

## 4. theme() function forms

Dot notation is gone; the function now takes the CSS-variable name, and in most cases the variable
reference replaces the function outright.

| v3 usage | v4 replacement |
|---|---|
| `background-color: theme(colors.red.500);` | `background-color: var(--color-red-500);` (preferred) or `theme(--color-red-500)` |
| `@media (min-width: theme(screens.xl))` | `@media (width >= theme(--breakpoint-xl))` |
| `padding: theme(spacing.16);` | `padding: theme(--spacing-16);` or `var(--spacing-16)` |
| `theme()` calls inside JS/plugin code | REMOVED — read/write CSS variables directly (`../config/method.md`) |

The codemod wraps existing `theme()` calls in the new CSS-variable syntax automatically.

## 5. Removed and relocated config options

`@config "./tailwind.config.js";` loads the legacy file for `theme`, `content`, and `plugins` — it
SILENTLY ignores `corePlugins`, `safelist`, and `separator` (see AP-4, AP-13).

| v3 JS config option | v4 status | Migration replacement |
|---|---|---|
| `tailwind.config.js` auto-load | REMOVED | opt-in via `@config "./tailwind.config.js";` (staged bridge only) |
| `content: [...]` | REMOVED (auto-detect) | usually nothing; else `@source "path"` / `@source not "path"` in CSS |
| `safelist` (array + regex patterns) | REMOVED | `@source inline("…")` with brace expansion — grammar owned by `../dynamic-classes/method.md` |
| `corePlugins: { x: false }` | REMOVED, NO replacement | remove utilities from source and rely on tree-shaking; `@source not`; lint/CI ban; `@utility` no-op override (last resort); disabling utilities is a STAY trigger (`method.md` §1) |
| `corePlugins: { preflight: false }` | REMOVED | skip the preflight import (partial imports, §6.1) and write your own reset in `@layer base` |
| `separator: '_'` | REMOVED, no replacement | v4 pins the separator to `:`; refactor templates — STAY trigger (`method.md` §1) |
| `prefix: 'tw-'` | MOVED to CSS | `@import "tailwindcss" prefix(tw);` + `tw:` variant form (§2.3) |
| `darkMode: 'class'` / `'media'` / `['selector', …]` | MOVED to CSS | `@custom-variant dark (&:where(.dark, .dark *));`; selector form in `examples.md` §3.16 |
| `theme.container` (`center`, `padding`, …) | REMOVED | override the utility: `@utility container { margin-inline: auto; padding-inline: 2rem; }` (`examples.md` §3.15) |
| `theme.extend` vs `theme` (replace) distinction | NO v4 equivalent | `@theme` always extends; namespace reset/replace semantics: `../config/method.md` |
| `plugins: [require(...)]` | MOVED to CSS | `@plugin "name"` in the entry stylesheet |
| `future.hoverOnlyWhenSupported` | REMOVED (behaviour is the default) | n/a — escape hatch in §3 |
| `resolveConfig` JS export | REMOVED | runtime table below (§7) |
| `theme()` JS function in user code | REMOVED | `var(--color-*)` in CSS; DOM reads in JS (§7) |

## 6. Pipeline and package changes

### 6.1 Entry CSS and partial imports

| v3 | v4 |
|---|---|
| `@tailwind base; @tailwind components; @tailwind utilities;` | `@import "tailwindcss";` — one line covers all three; the trio always errors in v4 |
| importing only some layers | partial imports: `@import "tailwindcss/preflight";` (just the reset), `@import "tailwindcss/utilities";` (just utilities); file-style `tailwindcss/theme.css`, `tailwindcss/preflight.css`, `tailwindcss/utilities.css` also valid for layer-skipping setups |

### 6.2 Toolchain

| Topic | v3 | v4 |
|---|---|---|
| Core install | `npm install -D tailwindcss postcss autoprefixer` | `npm install tailwindcss @tailwindcss/postcss` OR `@tailwindcss/vite` |
| PostCSS config | `tailwindcss: {}` + `autoprefixer: {}` (+ `postcss-import`) | `'@tailwindcss/postcss': {}` only |
| Vite integration | via PostCSS | first-class `@tailwindcss/vite` plugin (Vite 5+); delete `postcss.config.js` if Vite was its only consumer |
| `@import` bundling / vendor prefixes | `postcss-import` + `autoprefixer` | built into Oxide — delete both packages |
| Standalone CLI | `npx tailwindcss -i in.css -o out.css` | `npx @tailwindcss/cli -i in.css -o out.css` |
| Sass / Less / Stylus | tolerated by the v3 PostCSS pipeline | NOT SUPPORTED — v4 is itself the preprocessor; flatten to plain CSS first (STAY trigger, `method.md` §1) |
| Upgrade tool runtime | — | `npx @tailwindcss/upgrade` requires Node.js 20+ |

## 7. Theme token access at runtime (JS)

| Need | v3 | v4 |
|---|---|---|
| Read a theme color | `resolveConfig(tailwindConfig).theme.colors.red['500']` | `getComputedStyle(document.documentElement).getPropertyValue('--color-red-500').trim()` |
| Read spacing | same `resolveConfig` path | `getPropertyValue('--spacing')` (the base step; scale values are `calc()` multiples) |
| Read a breakpoint | `cfg.theme.screens.md` | `getPropertyValue('--breakpoint-md')` |
| SSR / build-time / Node-side | trivially available | no DOM: parse the entry CSS's `:root` block (e.g. PostCSS) or emit `tokens.json` from a build step; or keep tokens in a shared JS module that both the stylesheet (`@theme` via `var()`/`theme()`) and runtime read |

## 8. New v4 API surface — directive → purpose → v3 equivalent

Semantics of each directive are owned by `../config/method.md`; this table is the migration view.

| Directive / construct | Purpose | v3 equivalent |
|---|---|---|
| `@import "tailwindcss"` | loads theme vars, base reset, utilities | the `@tailwind` trio |
| `@import "tailwindcss" prefix(tw);` | prefix mode as a call option | `prefix: 'tw-'` |
| `@import "tailwindcss" source(none);` | disables automatic source detection (unrelated to preflight — it pairs with explicit `@source`) | `content: []` with `content: { relative: … }` opt-outs |
| `@theme { … }` | define CSS-variable design tokens | `theme.extend` in JS config |
| `@theme inline { … }` | tokens resolve at build time, not runtime | (new) |
| `@theme static { … }` | forces emission of ALL theme variables even if unused | closest v3 analog: safelisting every generated var |
| `@plugin "name"` | load a JS plugin from CSS | `plugins: [require(…)]` |
| `@source "path"` | add a content-scan glob | `content: [...]` |
| `@source not "path"` | exclude a path from the scan | `content` ignore patterns / `corePlugins` side effects |
| `@source inline("…")` | safelist utilities with brace/range expansion | `safelist` array + regex |
| `@utility name { … }` | define a custom utility | `addUtilities()` / `@layer utilities { .x {} }` |
| `@variant name` | apply a variant inside a CSS block | plugin-internal variant nesting |
| `@custom-variant name ( … )` | register a new variant | `addVariant()` / `variants` config |
| `@reference "./app.css"` | make the theme visible to a scoped `<style>`/module block | implicit theme context in every v3 scoped block |
| `@config "./tailwind.config.js"` | opt-in legacy JS config loader | automatic config discovery |
| `@apply` | expand utilities inline — same as v3, but requires `@reference` in scoped contexts | `@apply` |

Inside `@utility`, v4 adds functional helpers that replace many JS plugin patterns:
`--value(--color-*)` (resolved matched theme value), `--modifier(integer)` (modifier portion of the
class), `--alpha(var(--color-red-500), 0.5)` (compose alpha into a color), `--spacing(4)` (spacing
base × N → `calc(var(--spacing) * 4)`). Reference: `../config/method.md`.

## 9. Theme namespace mapping — `theme.extend.*` → `@theme` variables

| v3 path | v4 CSS variable |
|---|---|
| `theme.extend.colors.<name>` | `--color-<name>` |
| `theme.extend.colors.<group>.<shade>` | `--color-<group>-<shade>` (incl. `DEFAULT` → `--color-<group>`) |
| `theme.extend.spacing.<key>` | `--spacing-<key>` |
| `theme.extend.fontFamily.<key>` | `--font-<key>` |
| `theme.extend.fontSize.<key>` | `--text-<key>` |
| `theme.extend.fontWeight.<key>` | `--font-weight-<key>` |
| `theme.extend.borderRadius.<key>` | `--radius-<key>` |
| `theme.extend.boxShadow.<key>` | `--shadow-<key>` |
| `theme.extend.screens.<key>` | `--breakpoint-<key>` |
| `theme.extend.animation.<key>` | `--animate-<key>` |
| `theme.extend.transitionTimingFunction.<key>` | `--ease-<key>` |

## 10. Codemod coverage — `npx @tailwindcss/upgrade`

What it does mechanically:

| # | Auto-fixed |
|---|---|
| 1 | `@tailwind base/components/utilities` → `@import "tailwindcss"` |
| 2 | utility renames (§1: `shadow` → `shadow-sm`, `shadow-sm` → `shadow-xs`, …) |
| 3 | important modifier flip `!class` → `class!` |
| 4 | prefix flip `tw-class` → `tw:class` |
| 5 | `bg-opacity-50` → `bg-black/50` where the pair appears literally |
| 6 | pulls `corePlugins` / `safelist` / `separator` config out of the JS file (does not write the CSS replacements) |
| 7 | wraps `theme()` calls in the new CSS-variable syntax |
| 8 | variant-order flip for the COMMON stacking forms only |

What it does NOT catch — every one of these is a manual conversion:

| # | Missed | Lands in |
|---|---|---|
| 1 | variant-order semantics beyond common forms (bespoke `[&…]` chains) | §2.1, AP-10 |
| 2 | default-behavior changes (border color, ring width, placeholder, cursor, `hidden`) | §3, AP-1 |
| 3 | `@layer utilities` → `@utility` migration | AP-24 |
| 4 | custom plugin code calling removed APIs | §8, `../config/method.md` |
| 5 | comments containing class names | grep leftovers (§9 of `examples.md`) |
| 6 | class names assembled from template strings (`bg-${color}-500`) | `../dynamic-classes/method.md`, AP-5/AP-19 |
| 7 | `@reference` lines in scoped stylesheets | AP-3 |
| 8 | any visual regression from §3 default shifts | `method.md` §8 gates |

ALWAYS read the diff — the tool writes through `package.json`, config files
(`tailwind.config.js`, `postcss.config.js`, `vite.config.ts`), and templates
(`.html`, `.tsx`, `.vue`, `.svelte`). Walkthrough: [`examples.md`](examples.md) §7.

## 11. Browser-support matrix

| Engine | Safari | Chrome | Firefox | Dependency |
|---|---|---|---|---|
| v3 (JIT) | 14+ | 99+ | 99+ | all modern browsers; downlevel possible via autoprefixer config |
| v4 (Oxide) | **16.4+** | **111+** | **128+** | REQUIRES `@property`, `color-mix()`, modern container queries; older engines skip the rules entirely → blank/unstyled page |

NEVER ship v4 to an audience that includes browsers below the v4 minimums; the only workable
fallback (a conditionally-served v3 stylesheet via UA sniff) doubles build complexity. Update the
project's browserslist to the v4 floors as part of the upgrade (see AP-14).

## Sources

- https://tailwindcss.com/docs/upgrade-guide
- https://tailwindcss.com/blog/tailwindcss-v4
- https://tailwindcss.com/docs/functions-and-directives
- https://tailwindcss.com/docs/detecting-classes-in-source-files
- https://v3.tailwindcss.com/docs/configuration
- https://github.com/tailwindlabs/tailwindcss/issues/16346
- https://github.com/tailwindlabs/tailwindcss/issues/18136
