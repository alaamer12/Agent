# migration — Tailwind v3 → v4: decide, audit, upgrade, verify

Audit first, automate second, verify third. Skipping the audit produces a build that compiles and
renders wrong. **This module is the single owner of every v3→v4 breaking-change table** — no other
module in the battery restates them.

## 1. Decide: migrate or stay on v3.4

| Constraint found in the project | Verdict |
|---|---|
| Must support Safari < 16.4, Chrome < 111, Firefox < 128 | **STAY** — v4 emits `@property` + `color-mix()` |
| Sass / Less / Stylus in the pipeline | **STAY** — v4 is itself the preprocessor; flatten to plain CSS first |
| `corePlugins: { x: false }` relied upon | **STAY** until disabled utilities are removed from source — no v4 replacement |
| Custom `separator` | **STAY** — v4 pins it to `:`, no replacement |
| `resolveConfig()` called at runtime | rewrite to `getComputedStyle(...).getPropertyValue('--*')`, **then upgrade** |
| `safelist` with regex patterns | rewrite as `@source inline` brace expansion (grammar: `../dynamic-classes/method.md`), **then upgrade** |
| Vue/Svelte/CSS-modules scoped `<style>` with `@apply` | **UPGRADE** — but every scoped block needs `@reference` (semantics: `../config/method.md`) |
| Greenfield, modern-browser baseline, want CSS-first config | **USE v4** |

v3.4 still receives security patches. NEVER migrate purely "to be current" — the decision is the
browser baseline plus the removed-option blockers, nothing else.

## 2. What actually changes under the hood

| Aspect | v3 (JIT) | v4 (Oxide) |
|---|---|---|
| Implementation | JavaScript | Rust + Lightning CSS |
| `@import` bundling / vendor prefixes | `postcss-import` + `autoprefixer` | built-in |
| Cascade layers | synthetic ordering | native CSS `@layer` |
| Opacity composition | `rgba()` mixing | `color-mix()` |
| RTL | extra config | logical properties by default |
| Config surface | `tailwind.config.js` (auto-detected) | CSS-first `@theme` + directives; JS config opt-in via `@config` |

Performance figures from the v4 announcement (official benchmarks, verify against current releases):
full build 378ms→100ms, incremental-with-CSS 44ms→5ms, no-CSS-change 35ms→192µs.

## 3. Pre-migration audit — ALWAYS before running the tool

grep the codebase; every hit is a manual conversion the codemod cannot do:

1. `corePlugins` in config → accept utilities cannot be disabled, or scope with `@source not` / lint rule.
2. `safelist` → `@source inline("...")` in CSS.
3. `separator:` → remove; refactor templates to `:`.
4. `prefix: 'tw-'` → `tw-` concatenation becomes the `tw:` variant; `@import "tailwindcss" prefix(tw)`.
5. `tailwindcss/resolveConfig` call sites → `getComputedStyle` reads.
6. Bare `class="border"` → v4 default is `currentColor`: add an explicit color or a time-boxed shim (§6).
7. Bare `class="ring"` → default width dropped 3px→1px: `ring-3` + color, or shim.
8. Sass/Less/Stylus loaders → remove from the pipeline.
9. `@apply` inside `.vue`/`.svelte`/`*.module.css` → prepend `@reference "../app.css";` to each.
10. `bg-opacity-${n}`-style dynamic opacity → static maps (`../dynamic-classes/method.md`).

## 4. Automated path

```bash
git checkout -b chore/tailwind-v4   # clean tree, reviewable diff
npx @tailwindcss/upgrade            # Node 20+
```

Three phases: dependency swap (v3 + postcss-import + autoprefixer → v4 + `@tailwindcss/postcss` or
`@tailwindcss/vite`), config conversion (`theme.extend` → `@theme` block), template codemods
(deterministic renames + variant-order flip). ALWAYS review the diff — the tool does NOT cover:
dynamic class strings built at runtime, scoped `@apply` needing `@reference`, plugins reading
`theme()` in missed patterns, and any visual regression from default-value shifts.

## 5. Breaking-change catalog — quick reference

Single-owner summary; full tables with root cause and shim options: [`references/breaking-changes.md`](references/breaking-changes.md) · worked rewrites per trap: [`references/examples.md`](references/examples.md) · upgrade-mistake catalog: [`references/anti-patterns.md`](references/anti-patterns.md).

| Trap | v3 | v4 |
|---|---|---|
| Variant stacking order | `first:*:pt-0` (right→left) | `*:first:pt-0` (left→right) |
| Border color default | `gray-200` | `currentColor` |
| Ring width / color default | `3px` / `blue-500` | `1px` / `currentColor` |
| Placeholder color | `gray-400` | current text at 50% |
| Size scales shift one step | `shadow-sm`, `shadow` | `shadow-xs`, `shadow-sm` (same for blur, drop-shadow, backdrop-blur, rounded) |
| Opacity utilities removed | `bg-opacity-50` | slash modifier `bg-black/50` |
| Prefix form | `tw-flex` | `tw:flex` |
| Important modifier | `!flex` | `flex!` (inside `@apply`: `font-bold!`) |
| Focus outline | `outline-none` | `outline-hidden` (v4's `outline-none` truly removes outlines — a11y trap) |
| Arbitrary CSS var | `bg-[--brand]` | `bg-(--brand)` |
| Arbitrary spaces | `grid-cols-[max-content,auto]` | `grid-cols-[max-content_auto]` |
| Transform reset | `focus:transform-none` | `focus:scale-none` (properties are individual now) |
| `@tailwind` trio | three directives | `@import "tailwindcss"` (trio always errors in v4) |
| Custom utilities | `@layer utilities { .x {} }` | `@utility x { }` |
| Hover on touch | always applies | gated behind `@media (hover: hover)` — pair with `active:` |

NEVER trust the codemod's silence on default-behavior changes — border/ring/placeholder shifts are
visual regressions, not build errors. ALWAYS visually diff a representative page after upgrade.

## 6. Staged migration: v3-default shims (temporary by design)

```css
@theme {
  --default-ring-width: 3px;
  --default-ring-color: var(--color-blue-500);
}
@layer base {
  *, ::after, ::before, ::backdrop, ::file-selector-button {
    border-color: var(--color-gray-200, currentColor);
  }
}
@custom-variant hover (&:hover);
```

ALWAYS time-box a shim: one release cycle, then audit and delete. NEVER ship the color/ring shims
long term — they hide the behavior change from new contributors.

## 7. Partial and monorepo strategy

- **One stylesheet at a time:** move to the v4 engine, keep `@config "./tailwind.config.js";`,
  migrate `theme.extend` categories into `@theme` one at a time, delete the JS entry in the same
  commit. NEVER define the same token category in both `@theme` and the JS config — silent drift.
- **Shared component library, mixed consumers:** library emits plain utility strings only (no
  `@apply`, no custom directives — lowest common denominator); publish a tokens package (JS config
  fragment for v3 apps, `@theme` CSS file for v4 apps); migrate one consumer at a time.

## 8. Verification gates

1. `npm run build` exits 0 and emits CSS.
2. grep output CSS for renamed selectors (`shadow-xs`, `outline-hidden`, …).
3. Visual regression: screenshot the top pages before/after (Percy, Playwright, Chromatic); default
   color shifts WILL diff — review each, don't blanket-mask.
4. Scoped-`@apply` scan: `find . -name '*.vue' -o -name '*.svelte' -o -name '*.module.css' | xargs grep -l '@apply'`
   → every match has `@reference` as its first line.
5. Dynamic-class smoke test: click through every prop-driven color/size set on a production build.
6. Plugin check: every `plugins` entry loads via `@plugin`; anything touching `corePlugins`/`safelist` config silently no-ops.

## Sources

- https://tailwindcss.com/docs/upgrade-guide
- https://tailwindcss.com/blog/tailwindcss-v4
- https://tailwindcss.com/docs/functions-and-directives
- https://v3.tailwindcss.com/docs/configuration
- https://github.com/tailwindlabs/tailwindcss/issues/16346 (scoped `@apply` + `@reference`)
