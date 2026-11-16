# dynamic-classes — runtime class names that never generate

The most-reported Tailwind bug: a class that exists in source only as a **fragment**
(`bg-${color}-500`, `text-{{variant}}-600`), or only in server JSON, a CMS field, an i18n string,
or a user-configured colour, never gets a CSS rule. The DOM receives the class attribute, the
stylesheet receives nothing, the element renders unstyled. Canonical report: tailwindlabs/tailwindcss
issue 18136 — a CMS-issued string passed through a class helper, present in the DOM, dead in the CSS.

## The one rule

> Tailwind treats every scanned file as **plain text**. It never parses code. A utility generates
> only when the complete class name exists as one literal token in some scanned file.

Universal across v3 and v4. Template literals, string concatenation, runtime composition, and
server-injected data are opaque to the scanner: the string it assembles exists only after the build.
Files that hold class strings as data — translation JSON, markdown — are read only if they are part of
the source set (`examples.md` §6).

```html
<!-- NEVER: no complete token exists -->
<div class="text-{{ error ? 'red' : 'green' }}-600"></div>
<div class={`bg-${color}-500`}></div>
<div :class="`p-${size}`"></div>

<!-- ALWAYS: each branch is a complete token -->
<div class="{{ error ? 'text-red-600' : 'text-green-600' }}"></div>
<div class={isError ? 'text-red-600' : 'text-green-600'}></div>
```

This is the Tailwind instance of the parent battery's law — conditional styling is a lookup, not a
build (`/styling` `build` level, rule 4). Interpolation inside the layer that **owns** the names is
legal; interpolation over token fragments at a consumption site is the bug.

## Why dev works and prod fails

Three mechanisms hide the bug until release:

1. **HMR re-scan.** The dev server re-runs the scanner on every save. Type `bg-red-500` anywhere —
   including a scratch test — and the rule appears in the live stylesheet. The runtime value now
   resolves, and nobody learns that nothing generated it.
2. **Stale dev cache.** A Storybook story or markdown demo once contained the literal class; the dev
   build cached the rule; the file was later moved or edited. The rule survives in the dev bundle and
   points at nothing in the shipped source.
3. **Prod purges once.** The production build scans the shipped source a single time from a clean
   state. Any class that never appeared as a complete token in that scan is absent from the CSS.

To see the bug honestly, build and serve the artifact:

```bash
npm run build && npm run preview   # Vite, Astro
npm run build && npm start         # Next
```

If a dynamic class fails there, it fails in production. Test prod-built bundles before shipping any
change that touches prop-driven styling.

## Decision tree — which fix

```text
Is the value bounded to a small known set (variant: 'primary' | 'secondary' | 'danger')?
├── YES → Fix 1 static map                ← preferred: type-checkable, zero runtime
└── NO  → is it a bounded range from a CMS/API (any shade 50–950)?
    ├── YES → v3: Fix 3 safelist + regex pattern
    │         v4: Fix 4 @source inline with a range
    └── NO  → genuinely arbitrary (hex, length, user-typed CSS)
              Fix 2 inline style, or the CSS-variable hybrid
```

Ranked by preference: **1 static map → 2 inline style → 3 v3 safelist → 4 `@source inline`.** A
pattern-generated or directive-generated rule set is a workaround for a decision the component should
have made itself; use it only when the set genuinely is too large to hand-write.

## Fix 1 — static map per prop (preferred)

ALWAYS when the value is bounded. Zero runtime, fully type-checkable, and the scanner sees every
class because each map value is a complete literal string.

```jsx
const colorVariants = {
  blue: 'bg-blue-600 hover:bg-blue-500 text-white',
  red: 'bg-red-500 hover:bg-red-400 text-white',
  green: 'bg-emerald-600 hover:bg-emerald-500 text-white',
}

function Button({ color = 'blue', children }) {
  return <button className={`${colorVariants[color]} rounded-md px-4 py-2`}>{children}</button>
}
```

TypeScript narrows the prop to the map's keys, so an unknown value is a compile error, not an
unstyled element:

```ts
type Color = keyof typeof colorVariants
function Button({ color }: { color: Color; children: ReactNode }) { /* … */ }
```

A missing key is a loud `undefined` — that is a defect in the map, fixed by extending it, never by
falling back to a constructed name. NEVER write `` className={`bg-${color}-500`} `` and plan to fix
it with a safelist later. The static map **is** the fix. Same pattern in Vue, Svelte, and server
templates: `references/fixes.md`.

## Fix 2 — inline style for arbitrary values

Truly arbitrary input (a hex from a colour picker, a length from a CMS field) is not expressible as a
utility. Do not try: put the value in `style`, keep the structure in classes.

```jsx
function ColorBlock({ hex }) {
  return <div style={{ backgroundColor: hex }} className="rounded-md p-4" />
}

function ThemedCard({ accent, children }) {
  return (
    <div className="rounded-lg p-6 shadow-sm"
         style={{ borderTopWidth: '4px', borderTopColor: accent, backgroundColor: `${accent}11` }}>
      {children}
    </div>
  )
}
```

When one runtime value drives several utilities, expose it as a custom property and reference it from
arbitrary values. The classes stay literal tokens; only the variable is dynamic:

```jsx
function ThemedSection({ accent, children }) {
  return (
    <section className="border-l-4 border-(--accent) bg-(--accent)/10 text-(--accent)"
             style={{ '--accent': accent }}>
      {children}
    </section>
  )
}
```

`border-(--accent)`, `bg-(--accent)/10`, `text-(--accent)` are complete tokens the scanner reads
verbatim; `style` carries the value. (v3 spells the same reference with brackets, `bg-[--accent]`;
that syntax change is catalogued in the `migration` module, `../migration/method.md`.)

## Fix 3 — v3 safelist (bounded set, too large to hand-write)

Current-v3 fix for a set too big for a map — a CMS that emits any shade from 50 to 900 for any of
fifteen colours. The `safelist` array lives in `tailwind.config.js` next to `content`.

Literal strings (variants allowed here):

```js
module.exports = {
  content: ['./src/**/*.{html,js,ts,jsx,tsx}'],
  safelist: ['bg-red-500', 'bg-blue-500', 'text-3xl', 'lg:text-4xl'],
}
```

Regex pattern, and pattern with a variants array:

```js
module.exports = {
  safelist: [
    { pattern: /bg-(red|green|blue|amber|purple)-(50|100|500|700|900)/ },
    { pattern: /bg-(red|green|blue)-(100|200|300)/, variants: ['hover', 'focus', 'lg', 'lg:hover'] },
  ],
}
```

NEVER put a variant inside the regex. A `pattern` matches **base utility names only**; a pattern
containing `hover:` matches nothing and ships no CSS.

```js
// WRONG — never matches
{ pattern: /hover:bg-(red|green)-500/ }
// RIGHT
{ pattern: /bg-(red|green)-500/, variants: ['hover'] }
```

Scope every pattern. `/bg-.*/` emits roughly 30 colours × 11 shades × the variants list; the catch-all
`/.*/` compiles the whole library into multiple megabytes. v4 has no `safelist` config key: the
directive below replaces it, and the conversion steps (with the rest of the v3→v4 breaking changes) are
the `migration` module's — `../migration/method.md`.

## Fix 4 — v4 `@source inline`

v4's safelist: a CSS directive in the stylesheet that imports Tailwind, with brace expansion and
numeric ranges that generate the Cartesian product in one line.

```css
@import "tailwindcss";

@source inline("underline");                          /* one class */
@source inline("bg-red-500 bg-blue-500");             /* space-separated list */
@source inline("{hover:,focus:,}underline");          /* variants, bare class included */
@source inline("bg-red-{50,{100..900..100},950}");    /* full shade palette */
```

### Grammar

This module owns the expansion grammar; `../config/method.md` points here instead of restating it.
The payload is brace-expanded the way a shell expands it
([GNU Bash brace expansion](https://www.gnu.org/software/bash/manual/html_node/Brace-Expansion.html),
cited by the Tailwind docs).

| Form | Generates |
|---|---|
| `{a,b,c}` | `a`, `b`, `c` |
| `{a,,b}` | `a`, empty, `b` — the empty alternative emits the class with **no** variant |
| `{a..z}` | `a` … `z` (single-character range) |
| `{1..10}` | `1` … `10` (step 1) |
| `{0..100..10}` | `0`, `10`, `20` … `100` (step 10) |
| `{a,b}{1,2}` | `a1`, `a2`, `b1`, `b2` (Cartesian product) |
| `{100..900..100}` nested in `{50,100..900..100,950}` | `50`, `100`, `200` … `900`, `950` |

Rules that matter in practice:

- `{hover:,focus:,}` — the **trailing comma** is the empty alternative. Without it every generated
  class carries a variant and the bare utility is missing.
- Variants are prefixed inside the braces, so v4 has no equivalent of the v3 "variants in a regex"
  failure mode: `@source inline("{hover:,}bg-red-500")` is the correct form of what v3 needs
  `pattern` + `variants` for.
- Ranges only make sense where the scale is numeric; for names, list them: `{sm,base,lg,xl}`.

The flagship line — all colours, all shades, common variants, in one directive:

```css
@source inline("{hover:,focus:,}bg-{red,blue,green,amber,purple,pink,zinc}-{50,{100..900..100},950}");
```

7 colours × 11 shades × 3 variant states = 231 rules. The hand-written v3 safelist equivalent is 231
lines.

Subtract with `@source not inline` — it removes classes even when the scanner found them in source:

```css
@source inline("bg-{red,blue,green}-{50,{100..900..100},950}");
@source not inline("bg-{red,blue,green}-{800,900,950}");
```

`@source inline` (adds classes) coexists with `@source "path"` (adds scan paths) in the same
stylesheet; path registration, `source(none)`, and `@source not <path>` are the `config` module's
(`../config/method.md`).

## When no fix applies

Input space the developer does not control — a CMS field where non-developers type Tailwind classes
freely — cannot be exhausted. Two answers, both better than guessing:

1. **Allowlist at the source.** Restrict the CMS field to a fixed set of approved utilities, then
   pre-generate exactly that set (Fix 3 or Fix 4). Reject free-form input at the CMS layer.
2. **Change the affordance to tokens.** Replace the text field with a colour picker or size slider
   that emits a runtime value, and consume it via inline `style` / a custom property (Fix 2).

NEVER safelist "all of Tailwind" — every utility, every variant. The output CSS bloats to megabytes,
page-load performance collapses, and the dead-code elimination that makes utility CSS worth it is
gone.

## Rejected fixes

People try these before finding the ranked four. Full teardown with the correct alternative:
`references/anti-patterns.md`.

| Tried | Why it fails |
|---|---|
| Disable purge/JIT (drop `content`, `purge: false`, switch the v4 scanner off) | v3 without `content` generates **zero** classes; `purge` died with v2; v4's scanner **is** the build engine |
| Comment the classes into the file | works until someone deletes the "dead" comment; no link to the runtime values |
| Split the name into constant pieces (`'bg-' + color + '-500'`) | the scanner sees `bg-` and `-500`, neither of which is a utility |
| Wrap it in `clsx` / `classnames` / `cn` / `tailwind-merge` | those run at runtime and change nothing about detection |
| Permissive regex (`{ pattern: /.*/ }`) | megabytes of CSS |
| Variants inside the v3 `pattern` regex | `pattern` matches base names only; matches nothing |
| A `_safelist.jsx` demo file of literal classes | a tree-shaker drops the unused file; behaviour differs across build setups |
| Patching `node_modules` / forking Tailwind to skip detection | dies on the next `npm install` |
| Inlining every style for the whole component | loses responsive/hover/focus/dark-mode and diverges from the codebase |
| A constants-file helper that builds the name (`DYNAMIC_BG(color)`) | centralising the construction does not make it a literal token |

## Verification checklist

Run all five after applying a fix. Item 1 is the only one that proves anything.

1. **Production build, then grep the emitted CSS** for a previously-missing selector:
   ```bash
   npm run build && grep -c "bg-red-500" dist/assets/*.css
   ```
   Zero matches means the fix did not land (wrong directive, wrong file, variant lost).
2. **Toggle every prop value.** Each member of the set must produce a visible style change; click
   through the list, do not spot-check one.
3. **Clean dev server.** Kill it, wipe `.next/` or `node_modules/.vite`, restart. Classes that only
   existed in the dev cache now disappear — the point of the check.
4. **Drift audit.** Every `safelist` entry and every `@source inline` directive must correspond to a
   value a component can actually emit at runtime. Anything else is dead CSS; re-audit each release.
5. **Guard the source.** Fail CI when a class attribute interpolates:
   ```bash
   grep -rEn 'class(Name)?=[^>]*\$\{' src --include="*.tsx" --include="*.jsx" --include="*.vue"
   ```
   A repo-wide audit and its report format belong to `../validator/method.md`; this is the tripwire.

## Resources

- `references/fixes.md` — the four fixes worked per framework (React, Vue, Svelte, server templates),
  the CSS-variable hybrid, v3 safelist shapes in full, every `@source inline` form, the local guard,
  prod-parity commands
- `references/examples.md` — ten broken/fixed pairs: template literal, composed props, the issue 18136
  CMS scenario, status pill, colour picker, i18n JSON, server-built markup, Storybook args, grid
  columns, a marketing-site v4 safelist
- `references/anti-patterns.md` — the ten wrong fixes, each with why it fails and what replaces it

## Sources

- https://github.com/tailwindlabs/tailwindcss/issues/18136
- https://tailwindcss.com/docs/detecting-classes-in-source-files
- https://v3.tailwindcss.com/docs/content-configuration
- https://www.gnu.org/software/bash/manual/html_node/Brace-Expansion.html
