---
name: tailwind-errors-dynamic-classes
description: >
  Use when Tailwind classes work in development but disappear in
  production builds, or when class names assembled at runtime (template
  literals like bg-${color}-500, server-injected JSON, CMS-driven
  attributes, i18n strings, user-configured colours) render in the DOM
  but produce no visible style. This is the most-reported Tailwind
  issue (tailwindlabs/tailwindcss issue 18136). Prevents the four most
  common wrong fixes: turning off purge/JIT entirely (no longer
  possible in v4 and wastes bundle weight in v3), pasting a massive
  hand-written safelist that drifts out of sync with the design
  system, listing every possible class as plain strings somewhere in
  source then deleting them (the cache survives only one build), and
  monkey-patching the build to ship the full unminified Tailwind output
  to production. Covers the four supported fixes ranked by preference:
  (1) map prop to complete static class string via lookup object,
  (2) inline style for truly arbitrary user values, (3) v3 safelist
  array and regex pattern with variants, (4) v4 @source inline with
  brace expansion and range syntax {100..900..100} including hover
  focus prefixes. Explains why Tailwind scans plain text rather than
  parsing code, why dev-server HMR re-scanning masks the bug, the full
  brace-expansion grammar, the canonical issue 18136 walkthrough, and
  the rule that pattern-based v3 safelisting cannot include variants
  inside the regex.
  Keywords: tailwind dynamic class, template literal class, bg-${color}-500,
  classes work in dev not prod, classes missing production, my tailwind
  styles disappeared, dynamic className not applying, server-injected
  class no style, CMS color not working tailwind, tailwind safelist,
  safelist pattern regex, safelist variants array, @source inline,
  @source inline brace expansion, {hover:,}bg-{red,blue}-{500,700},
  range syntax {100..900..100}, @source not, complete class names rule,
  Tailwind plain text scanning, why does dev work but prod fail,
  issue 18136, user-configured colour tailwind, i18n string class
  tailwind, contentful tailwind class, sanity tailwind class, why are
  classes not generated, dynamic class names not detected.
license: MIT
compatibility: "Designed for Claude Code. Requires Tailwind CSS v3.4 or v4.0+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# Tailwind Dynamic Class Names : The #1 Reported Issue

If a class only exists in source code as a fragment (`bg-${color}-500`,
`text-{{variant}}-600`, server JSON, CMS attributes), Tailwind never
generates the CSS rule. The DOM gets the class attribute, the
stylesheet does not get the rule, the element renders unstyled.

Companion skills :

- `tailwind-impl-config-v4` : `@source inline` directive in depth
- `tailwind-impl-config-v3` : v3 `safelist` configuration
- `tailwind-errors-purge-issues` : adjacent purge-detection failures
- `tailwind-core-design-system` : prop-to-class mapping pattern

## The Rule

> Tailwind treats all source files as plain text and does NOT parse
> them as code. A class must exist as a literal complete token in
> some scanned file to be generated.

This rule is universal across v3 and v4. Template literals, string
concatenation, runtime composition, server-injected strings, and CMS
data are ALL opaque to the scanner.

```html
<!-- NEVER works (no complete token) -->
<div class="text-{{ error ? 'red' : 'green' }}-600"></div>
<div class={`bg-${color}-500`}></div>
<div :class="`p-${size}`"></div>

<!-- ALWAYS works (complete tokens) -->
<div class="{{ error ? 'text-red-600' : 'text-green-600' }}"></div>
<div class={isError ? 'text-red-600' : 'text-green-600'}></div>
```

## Why Dev Works But Prod Fails

In development the bundler may include the full unpurged Tailwind
output (HMR re-runs the scanner on every save, picking up classes you
just typed in a test). Production builds run purge once against the
shipped source, and any class that never appeared as a complete token
during that one scan is gone.

Some teams discover the bug after pasting a Storybook story or a
markdown demo into the project ; that file briefly contained
`bg-red-500`, the dev build cached the rule, then the file moved or
was edited and the rule survived in the dev bundle. The prod build
runs from a clean state and discovers no `bg-red-500` token anywhere.

## Decision Tree : Which Fix

```
Is the value bounded to a small known set
(e.g. variant: 'primary' | 'secondary' | 'danger')?
├── YES : Fix 1 (static map)
└── NO : Is the value a numeric range from a CMS / API?
    ├── YES (e.g. user-picked shade 50-950) :
    │   ├── v4 : Fix 4 (@source inline with range)
    │   └── v3 : Fix 3 (safelist with regex pattern)
    └── NO : truly arbitrary colour / size string :
        Fix 2 (inline style)
```

## Fix 1 : Static Map (PREFERRED)

ALWAYS use this when the value is bounded to a known set. It is
zero-runtime, fully type-checkable, and the static analyser sees every
class.

```jsx
function Button({ color, children }) {
  const variants = {
    blue: 'bg-blue-600 hover:bg-blue-500 text-white',
    red: 'bg-red-500 hover:bg-red-400 text-white',
    green: 'bg-emerald-600 hover:bg-emerald-500 text-white',
  }
  return <button className={variants[color]}>{children}</button>
}
```

Why it works : every class string (`'bg-blue-600 hover:bg-blue-500
text-white'`) is a complete literal token in the source file. The
Tailwind scanner reads it verbatim.

TypeScript narrows further :

```ts
type Variant = keyof typeof variants
function Button({ color }: { color: Variant }) { /* ... */ }
```

NEVER write `` className={`bg-${color}-500`} `` and expect a fix
later. The static map is the fix.

## Fix 2 : Inline Style for Arbitrary Values

When the value is truly arbitrary (a hex code from a user colour
picker, a CSS length from a CMS field), NEVER try to express it as a
Tailwind class. Use the `style` attribute :

```jsx
function ColorBlock({ hex }) {
  return <div style={{ backgroundColor: hex }} className="rounded-md p-4" />
}

function CustomSpacing({ pixels }) {
  return <div style={{ marginBlock: `${pixels}px` }} />
}
```

Inline `style` bypasses Tailwind entirely. The class system covers
the design system ; truly free-form values bypass it.

Hybrid pattern (Tailwind structure + inline runtime value) :

```jsx
<button
  className="rounded-md px-4 py-2 font-medium text-white transition"
  style={{ backgroundColor: userTheme.primary }}
>
  Tap
</button>
```

## Fix 3 : v3 Safelist (Bounded but Many Classes)

For projects on v3 where the set is too large to inline as a map (a
CMS that emits any shade between 50 and 900 for any of fifteen
colours), use the `safelist` array in `tailwind.config.js`.

Literal strings :

```js
module.exports = {
  content: ['./src/**/*.{html,js,ts,jsx,tsx}'],
  safelist: [
    'bg-red-500',
    'bg-blue-500',
    'text-3xl',
  ],
}
```

Regex pattern :

```js
module.exports = {
  safelist: [
    {
      pattern: /bg-(red|green|blue|amber|purple)-(50|100|500|700|900)/,
    },
  ],
}
```

Pattern with variants array :

```js
module.exports = {
  safelist: [
    {
      pattern: /bg-(red|green|blue)-(100|200|300)/,
      variants: ['hover', 'focus', 'lg', 'lg:hover'],
    },
  ],
}
```

CRITICAL RULE : patterns can only match BASE utility names. NEVER
include variants inside the regex itself :

```js
// WRONG : variants in regex never match
{ pattern: /hover:bg-(red|green)-500/ }

// RIGHT : variants in the variants array
{
  pattern: /bg-(red|green)-500/,
  variants: ['hover'],
}
```

## Fix 4 : v4 @source inline (PREFERRED for v4)

v4 replaces the `safelist` config option with the `@source inline`
CSS directive. The grammar supports brace expansion AND numeric
ranges, generating the Cartesian product in one line.

Single class :

```css
@import "tailwindcss";
@source inline("underline");
```

With variants via brace expansion :

```css
@source inline("{hover:,focus:,}underline");
```

The empty alternative in `{hover:,focus:,}` (note the trailing comma)
includes the bare class WITHOUT a variant. So this generates :
`underline`, `hover:underline`, `focus:underline`.

Numeric ranges :

```css
@source inline("bg-red-{50,{100..900..100},950}");
```

`{100..900..100}` generates `100, 200, 300, 400, 500, 600, 700, 800,
900`. Combined with literal `50` and `950`, all eleven shades emit.

The flagship pattern (all colours, all shades, common variants) :

```css
@source inline("{hover:,focus:,}bg-{red,blue,green,amber,purple,pink,zinc}-{50,{100..900..100},950}");
```

This single line generates 7 colours × 11 shades × 3 variant states =
231 rules. Hand-written safelist equivalent : 231 lines.

Excluding subsets with `@source not inline` :

```css
@source not inline("bg-{red,green}-{700,800,900}");
```

## When None of the Fixes Apply

Truly user-typed CSS (a CMS-managed Tailwind class string entered by
non-developers) cannot be exhaustively safelisted because the input
space is unbounded. Two options :

1. Restrict the input field to a fixed allowlist of approved utility
   classes ; pre-safelist exactly that allowlist via Fix 3 or Fix 4.
2. Convert the editor's affordance to design tokens (colour picker,
   size slider) that emit inline `style` (Fix 2).

NEVER attempt to safelist "all of Tailwind" by including every utility.
The output CSS bloats to megabytes and the JIT performance benefit
disappears.

## Brace Expansion Grammar (v4 @source inline)

The full grammar :

| Pattern | Generates |
|---------|-----------|
| `{a,b,c}` | `a`, `b`, `c` |
| `{a,,b}` | `a`, `` (empty), `b` |
| `{a..z}` | `a`, `b`, `c`, ..., `z` (single-char range) |
| `{1..10}` | `1`, `2`, `3`, ..., `10` (numeric range, step 1) |
| `{0..100..10}` | `0`, `10`, `20`, ..., `100` (numeric range, step 10) |
| `{a,b}{1,2}` | `a1`, `a2`, `b1`, `b2` (Cartesian product) |

Nested expansion :

```css
@source inline("bg-red-{50,{100..900..100},950}");
```

`{100..900..100}` is a nested range expansion inside the outer comma
list.

## Verification Checklist

1. Production build : `npm run build`. Inspect the output CSS for one
   of the previously-missing selectors :
   ```bash
   grep -c "bg-red-500" dist/assets/*.css
   ```
2. Toggle the dynamic prop : every value in the set must produce a
   visible style change. Manually click through each option.
3. Clean dev server : kill the dev server, wipe `.next/` or
   `node_modules/.vite`, restart. Classes still apply.
4. Safelist drift check : every entry in `safelist` or `@source
   inline` must correspond to a real prop value still in code. Audit
   periodically.

## References

- `references/methods.md` : full implementation of each fix with
  framework-specific patterns (React, Vue, Svelte, server templates)
- `references/examples.md` : working code for every fix, including
  the issue 18136 SSR scenario
- `references/anti-patterns.md` : ten wrong fixes that people try
  before they find the right one

## Sources

- https://github.com/tailwindlabs/tailwindcss/issues/18136
- https://tailwindcss.com/docs/detecting-classes-in-source-files
- https://v3.tailwindcss.com/docs/content-configuration
