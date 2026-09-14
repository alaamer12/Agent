---
name: tailwind-errors-v4-migration
description: >
  Use when upgrading a Tailwind CSS v3 codebase to v4 and hitting
  silent visual regressions, build errors after switching imports,
  or unexpected behavior changes that the codemod did not catch.
  Catalogs every default-behavior change between v3 and v4 with
  symptoms, root causes, and surgical fixes. Prevents the
  variant-order trap (v3 right-to-left first:*:pt-0 silently
  becomes wrong in v4 left-to-right where the correct form is
  *:first:pt-0), the invisible-borders trap (v4 default
  border-color flipped from gray-200 to currentColor so every
  border now renders in the parent text color), the thin-ring
  trap (default ring width dropped from 3px to 1px so focus rings
  disappear under existing UI), the shadow-shift trap (shadow-sm
  in v3 became shadow-xs in v4, shadow in v3 became shadow-sm in
  v4, same shift applies to blur, drop-shadow, backdrop-blur,
  rounded), the removed-config trap (corePlugins / safelist /
  separator no longer exist in JS config), the bg-opacity-removed
  trap (bg-opacity-50 no longer works, use bg-black/50), the
  prefix-syntax-flip trap (tw-flex becomes tw:flex), the
  important-modifier-flip trap (!flex becomes flex!), the
  outline-none-rename trap (outline-none now sets
  outline-style:none, the old behavior is outline-hidden), the
  arbitrary-var-syntax trap (bg-[--brand] becomes bg-(--brand)),
  the arbitrary-comma trap (max-content,auto becomes
  max-content_auto), the transform-individual-properties trap
  (focus:transform-none becomes focus:scale-none), the @layer
  utilities trap (custom utilities now use @utility directive),
  and the hover-on-touch trap (hover only fires when @media
  (hover: hover) matches). Each trap section documents detection,
  root cause, surgical fix, and shim-in-@layer-base option for
  staged migration.
  Keywords: tailwind v3 to v4 migration, tailwind upgrade
  guide, upgrade trap, breaking changes tailwind 4, variant
  stacking order tailwind, first:*:pt-0 *:first:pt-0,
  default border color currentColor, default ring width 1px,
  ring-3 v4, shadow-sm shadow-xs rename, blur-sm blur-xs,
  drop-shadow rename, backdrop-blur rename, rounded-sm
  rounded-xs, removed corePlugins, removed safelist,
  removed separator, bg-opacity-50 removed, slash opacity
  modifier, prefix tw:flex v4, tw- vs tw:, important !flex
  to flex!, outline-none outline-hidden, outline-style none,
  bg-(--brand) v4, var syntax parentheses, grid-cols-[
  max-content_auto], underscore in arbitrary value,
  focus:transform-none focus:scale-none, individual transform
  properties, @utility directive, @layer utilities deprecated,
  hover hover media query, theme(--breakpoint-xl), @tailwind
  base components utilities removed, browser support safari
  16-4 chrome 111 firefox 128, what changed tailwind 4,
  borders are missing v4, focus ring is too thin v4,
  why are my shadows different v4, automated upgrade tool
  tailwind, npx @tailwindcss/upgrade.
license: MIT
compatibility: "Designed for Claude Code. Source Tailwind CSS v3.4. Target v4.0+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# v3 to v4 Upgrade Trap Catalog

Every documented breaking change between Tailwind v3 and v4 with
symptom, root cause, surgical fix, and (where applicable) a
`@layer base` shim that restores v3 behavior during staged migration.

ALWAYS run the official codemod first :

```bash
npx @tailwindcss/upgrade
```

The codemod handles ~80% of the renames mechanically. This skill
catalogs what it does NOT auto-fix, plus what to expect when
visually-equivalent classes silently change meaning.

Companion skills :

- `tailwind-impl-migration-v3-v4` : end-to-end migration process
- `tailwind-impl-config-v4` : target v4 config surface
- `tailwind-impl-config-v3` : source v3 config surface

## Quick Reference

### Top 10 traps

| Trap                                | v3 form              | v4 form              |
| ----------------------------------- | -------------------- | -------------------- |
| Variant stacking order              | `first:*:pt-0`       | `*:first:pt-0`       |
| Default border color                | `gray-200`           | `currentColor`       |
| Default ring width                  | `3px`                | `1px`                |
| Shadow scale shift                  | `shadow-sm`          | `shadow-xs`          |
| Opacity modifier removal            | `bg-opacity-50`      | `bg-black/50`        |
| Prefix syntax                       | `tw-flex`            | `tw:flex`            |
| Important modifier                  | `!flex`              | `flex!`              |
| Outline rename                      | `outline-none`       | `outline-hidden`     |
| Arbitrary CSS var                   | `bg-[--brand]`       | `bg-(--brand)`       |
| Arbitrary comma in grid             | `[max-content,auto]` | `[max-content_auto]` |

### Removed config options

| Removed         | Replacement                       |
| --------------- | --------------------------------- |
| `corePlugins`   | `@utility` for custom utilities ; no general off-switch |
| `safelist`      | `@source inline "{...}"` in CSS    |
| `separator`     | No replacement ; v4 uses `:` only |
| `@tailwind` directives | `@import "tailwindcss"`     |

### Removed utilities

| Removed              | Replacement              |
| -------------------- | ------------------------ |
| `flex-shrink-*`      | `shrink-*`               |
| `flex-grow-*`        | `grow-*`                 |
| `overflow-ellipsis`  | `text-ellipsis`          |
| `decoration-slice`   | `box-decoration-slice`   |
| `decoration-clone`   | `box-decoration-clone`   |

## Decision Trees

### My visual broke after upgrade : where to look ?

```
What changed visually ?
├── Borders disappear or take wrong color
│       → default border-color is currentColor in v4. Add explicit
│         border-gray-200 on every bordered element, OR shim in
│         @layer base.
├── Focus rings are thin / invisible
│       → default ring-width dropped from 3px to 1px. Replace `ring`
│         with `ring-3`, OR shim.
├── Shadows look wrong (too soft / too sharp)
│       → shadow scale shifted. shadow-sm became shadow-xs. shadow
│         became shadow-sm.
├── Variant order broke (first / last / odd / even on children)
│       → stacking order flipped. Swap right-to-left to left-to-right.
├── bg-opacity / text-opacity ignored
│       → removed. Use the slash modifier on the color utility.
├── !important utilities ignored
│       → moved from leading to trailing bang.
├── Custom prefix classes do not parse
│       → prefix is now a variant, not a string concat.
└── Arbitrary [--var] values do not resolve
        → use ([--var]) parentheses syntax now.
```

### Should I codemod or rewrite ?

```
Codebase size ?
├── < 50k LOC : run npx @tailwindcss/upgrade then audit manually
├── 50k-200k  : codemod + this trap catalog + visual regression suite
└── > 200k    : staged migration with @layer base shims for default-change traps,
                codemod per package, full audit per merge
```

## Patterns

### Pattern : variant stacking order (L-004)

v3 evaluated variants right-to-left :

```html
<!-- v3 : "first child, of every direct child" -->
<ul class="first:*:pt-0">
```

v4 evaluates left-to-right :

```html
<!-- v4 : "every direct child, when it is first" -->
<ul class="*:first:pt-0">
```

ALWAYS swap stacked variants when the new order changes semantics.
The codemod catches the common forms but multi-token chains
(`group-hover:*:first:opacity-100`) need manual review.

### Pattern : default border-color shim (L-005)

To preserve v3 default border color :

```css
@layer base {
  *, ::after, ::before, ::backdrop {
    border-color: var(--color-gray-200, currentColor);
  }
}
```

ALWAYS treat this as TEMPORARY. The right long-term fix is to add
explicit `border-gray-200` (or your token) to every bordered element.
Leave the shim in for one release cycle, then audit and remove.

### Pattern : default ring shim

```css
@layer base {
  * {
    --tw-ring-color: var(--color-blue-500);
  }
}
```

Or replace every `ring` with `ring-3 ring-blue-500` at the call site.

### Pattern : shadow scale renames (L-006)

Apply these renames everywhere :

| v3                 | v4                  |
| ------------------ | ------------------- |
| `shadow-sm`        | `shadow-xs`         |
| `shadow`           | `shadow-sm`         |
| `drop-shadow-sm`   | `drop-shadow-xs`    |
| `drop-shadow`      | `drop-shadow-sm`    |
| `blur-sm`          | `blur-xs`           |
| `blur`             | `blur-sm`           |
| `backdrop-blur-sm` | `backdrop-blur-xs`  |
| `backdrop-blur`    | `backdrop-blur-sm`  |
| `rounded-sm`       | `rounded-xs`        |
| `rounded`          | `rounded-sm`        |

The codemod handles these. ALWAYS visually diff a representative page
after to confirm no edge case was missed.

### Pattern : removed corePlugins / safelist / separator (L-003)

`corePlugins` removal :

```diff
- // tailwind.config.js (v3)
- corePlugins: { preflight: false }
```

v4 replacement : drop preflight by NOT importing the preflight layer.
Use `@layer base { ... }` to write your own base styles instead.

`safelist` removal :

```diff
- // tailwind.config.js (v3)
- safelist: ["bg-red-500", "bg-green-500"]
```

v4 replacement (in entry CSS) :

```css
@source inline "{bg-red-500,bg-green-500}";
```

`separator` removal : v4 only supports `:`. NEVER attempt to use
`__` or any other separator.

### Pattern : opacity modifier

```diff
- <div class="bg-black bg-opacity-50">
+ <div class="bg-black/50">
```

Same applies to `text-opacity`, `border-opacity`, `divide-opacity`,
`ring-opacity`, `placeholder-opacity`. All removed.

### Pattern : prefix flip

```diff
- <div class="tw-flex tw-bg-red-500 tw-hover:bg-red-600">
+ <div class="tw:flex tw:bg-red-500 tw:hover:bg-red-600">
```

Set prefix in CSS (v4) :

```css
@import "tailwindcss" prefix(tw);
```

### Pattern : important modifier flip

```diff
- <div class="!flex !bg-red-500">
+ <div class="flex! bg-red-500!">
```

Inside @apply :

```diff
- .btn { @apply font-bold !important; }
+ .btn { @apply font-bold!; }
```

### Pattern : outline-none rename

```diff
- <input class="focus:outline-none">
+ <input class="focus:outline-hidden">
```

The v4 `outline-none` now actually sets `outline-style: none`, which
removes the focus outline even in forced-colors mode. ALWAYS prefer
`outline-hidden` (the new name for v3 behavior) for accessibility.

### Pattern : arbitrary CSS var syntax

```diff
- <div class="bg-[--brand-color]">
+ <div class="bg-(--brand-color)">
```

Parentheses replaced square brackets for CSS-var references because
modern CSS parsing made square-bracket syntax ambiguous.

### Pattern : underscore for spaces in arbitrary values

```diff
- <div class="grid-cols-[max-content,auto]">
+ <div class="grid-cols-[max-content_auto]">
```

Use `_` for the space ; comma no longer becomes a space substitute.

### Pattern : individual transform reset

```diff
- <button class="scale-150 focus:transform-none">
+ <button class="scale-150 focus:scale-none">
```

v4 splits transform into individual CSS properties (`rotate`, `scale`,
`translate`). Reset each individually with `*-none`.

### Pattern : @layer utilities to @utility

```diff
- @layer utilities {
-   .tab-4 { tab-size: 4; }
- }
+ @utility tab-4 {
+   tab-size: 4;
+ }
```

The new `@utility` directive supports `--value()`, `--modifier()`,
`--alpha()`, `--spacing()` helpers for dynamic utilities. See
`tailwind-impl-config-v4`.

### Pattern : hover gating

v4 wraps `hover:` in `@media (hover: hover)` so it does NOT trigger on
tap devices. ALWAYS pair stateful hover with an explicit
`active:` / `focus:` variant for touch users :

```html
<button class="bg-blue-500 hover:bg-blue-700 active:bg-blue-800">
  Tap-friendly
</button>
```

## Anti-Patterns (summary)

NEVER trust the codemod's silence on default-behavior changes. Border
color and ring width changes produce visual regressions, not build
errors.

NEVER swap variant order mechanically without checking semantics. The
flip from right-to-left to left-to-right can change meaning when
multiple structural variants stack.

NEVER ship the @layer base default-color shim long term. It hides the
behavior change from new contributors.

NEVER use `bg-opacity-*` / `text-opacity-*` in v4. They do nothing.

See `references/anti-patterns.md` for the full catalog.

## Reference Links

- `references/methods.md` : exact rename table, codemod command,
  config-option migration map, browser-support matrix
- `references/examples.md` : before/after snippets for every trap,
  staged @layer base shims, audit scripts
- `references/anti-patterns.md` : every wrong assumption during
  upgrade with symptom, root cause, fix

## Sources

- v4 upgrade guide : https://tailwindcss.com/docs/upgrade-guide
- v4 announcement : https://tailwindcss.com/blog/tailwindcss-v4
- L-003 : v4 removed corePlugins, safelist, separator from JS config
- L-004 : v4 variant stacking flipped from right-to-left to left-to-right
- L-005 : v4 default border-color flipped from gray-200 to currentColor
