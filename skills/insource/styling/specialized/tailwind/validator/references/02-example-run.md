# Example run — fixture, report, and the follow-up loop

One small codebase, the pass over it, and the report the pass must produce. Use it to calibrate
severity and wording: if a finding here would not survive a reviewer's first question, it does not
belong in the report.

Report blocks are verbatim output, so the `Cite` paths inside them are validator-root-relative
(`../<module>/method.md`), not relative to this file. Prose in this file uses `../../<module>/`.

## Fixture

```text
example-app/
  package.json          state detection input (v4)
  tailwind.config.js    R-03 x2
  postcss.config.mjs    agrees with package.json, no finding
  src/
    app.css             R-04
    components/
      Tag.tsx           R-01
      Hero.vue          R-02
      Card.tsx          R-06
      Pill.tsx          clean, and the shape the fixes aim at
```

Eight files in the set. Every finding below is reproducible from this text alone.

### `package.json`

```json
{
  "name": "example-app",
  "dependencies": {
    "tailwindcss": "^4.0.5",
    "@tailwindcss/postcss": "^4.0.5",
    "next": "^15.0.0",
    "react": "^19.0.0"
  }
}
```

### `tailwind.config.js`

```js
module.exports = {
  content: ['./src/**/*.{html,js,ts,jsx,tsx,vue}'],
  safelist: ['bg-red-500', 'bg-blue-500'],      // line 3
  corePlugins: { float: false, clear: false },  // line 4
  theme: {
    extend: { colors: { brand: '#5b21b6' } },
  },
}
```

### `postcss.config.mjs`

```js
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}
```

### `src/app.css`

```css
@import "tailwindcss";
@config "../tailwind.config.js";   /* the JS config is loaded, so R-03 stays a Warning, not an Error */

@theme {
  --color-brand: #5b21b6;
}

.legacy-card {                        /* line 8: no @utility, no @layer */
  background: #fff;
  border-radius: 1rem;
  padding: 1rem;
}
```

### `src/components/Tag.tsx`

```tsx
1  type Color = 'red' | 'green' | 'blue'
2
3  export function Tag({ color, label }: { color: Color; label: string }) {
4    return (
5      <span className={`bg-${color}-100 text-${color}-800 px-2 py-1 rounded`}>
6        {label}
7      </span>
8    )
9  }
```

### `src/components/Hero.vue`

```vue
1  <template>
2    <h1>Ship it</h1>
3  </template>
4
5  <style scoped>
6    h1 { @apply text-4xl font-bold text-zinc-900; }
7  </style>
```

### `src/components/Card.tsx`

```tsx
1  export function Card({ children }: { children: React.ReactNode }) {
2    return (
3      <div className="border rounded-lg p-4">
4        {children}
5      </div>
6    )
7  }
```

### `src/components/Pill.tsx`

```tsx
1  const styles = {
2    ok: 'bg-emerald-100 text-emerald-700',
3    warn: 'bg-amber-100 text-amber-700',
4    err: 'bg-red-100 text-red-700',
5  } as const
6
7  type Status = keyof typeof styles
8
9  export function Pill({ status }: { status: Status }) {
10   return (
11     <span className={`${styles[status]} rounded-full px-2 py-1 text-xs`}>
12       {status}
13     </span>
14   )
15 }
```

## Pass

1. Method 1: `package=v4 css=v4 postcss=v4 vite=none`. No disagreement, so no `R-00`; the gate is v4.
2. Method 12: 8 files in the scan set (`node_modules`, `dist`, `.next` absent).
3. Methods 2–10: gated rules run (R-02, R-03, R-04 v4 branch, R-05, R-06 all live under v4).
4. Method 11: assemble.

## Report

```text
Tailwind Validator Report
=========================
Project state : v4 detected (tailwindcss@^4.0.5)
Scan scope    : src/ tailwind.config.js postcss.config.mjs
Files scanned : 8
Issues        : 6 (2 errors, 3 warnings, 1 info)

---

[ERROR] R-01 : dynamic class string
  File       : src/components/Tag.tsx:5
  Code       : className={`bg-${color}-100 text-${color}-800 px-2 py-1 rounded`}
  Cite       : ../dynamic-classes/method.md (static map)
  Suggested  : interpolate whole class names from a lookup keyed by `color`; `bg-${color}-100`
               never reaches the CSS, so the tag ships unstyled.

[ERROR] R-02 : scoped @apply without @reference
  File       : src/components/Hero.vue:6
  Block      : <style scoped> h1 { @apply text-4xl font-bold text-zinc-900; }
  Cite       : ../config/method.md (@reference directive)
  Suggested  : add `@reference "../app.css";` inside the block, or read the theme variable
               directly (`color: var(--text-zinc-900);`) and drop `@apply`.

[WARNING] R-03 : forbidden v3 key in v4 config
  File       : tailwind.config.js:3
  Key        : safelist
  Cite       : ../migration/method.md (v3 config keys)
  Suggested  : move to src/app.css as `@source inline("bg-red-500 bg-blue-500");` and delete the
               JS entry.

[WARNING] R-03 : forbidden v3 key in v4 config
  File       : tailwind.config.js:4
  Key        : corePlugins
  Cite       : ../migration/method.md (v3 config keys)
  Suggested  : no v4 equivalent. Remove the entry, then keep the ban where it still bites: a lint
               rule on `float-*`/`clear-*`, or `@source not` for the paths that drift.

[WARNING] R-04 : custom class outside @layer / @utility
  File       : src/app.css:8
  Code       : .legacy-card { background: #fff; border-radius: 1rem; padding: 1rem; }
  Cite       : ../config/method.md (@utility, @layer)
  Suggested  : register as `@utility legacy-card { … }` so utilities can be ordered against it;
               `@layer components` remains legal but is the legacy shape.

[INFO] R-06 : bare border under v4
  File       : src/components/Card.tsx:3
  Code       : <div className="border rounded-lg p-4">
  Cite       : ../migration/method.md (default colour changes)
  Suggested  : add an explicit colour (`border border-zinc-200`), or restore the v3 default once
               in `@layer base` instead of per call site.

---
Total : 6 issues
  Errors   : 2
  Warnings : 3
  Info     : 1
```

## What is deliberately absent

| Candidate | Why no finding |
|---|---|
| `Pill.tsx:11` `${styles[status]}` | the interpolation is whitespace-delimited and yields a **complete** class name that exists verbatim in a literal map. This is the fix shape for R-01, not a violation of it. |
| `Pill.tsx:1–7` object map + key union | the recommended R-08 target shape, so R-08 stays quiet. |
| `rounded-lg` in `Tag.tsx:5` and `Card.tsx:3` | v4 renamed the bare `rounded`/`shadow`/`blur` scale, not `rounded-lg`. Bare-scale drift is a migration sweep item, not a rule here. |
| `#fff` and `1rem` in `src/app.css:9–11` | hardcoded raw values are a token question, not a rule: see `../../design-system/method.md`, or the styling `retrofit` level at project scale. The catalogue has no rule for it — do not invent one mid-report. |
| `Card.tsx:3` `border` severity | Info, not Warning: `currentColor` may be exactly what the design wants. The report states the default change and stops there. |

Filing a clean file as a violation costs more than missing one: the reader stops trusting the
report and the step gets switched off.

## Follow-up loop

1. Fix R-01 in `../../dynamic-classes/method.md` — static map, then delete the template fragment.
2. Fix R-02 and R-04 in `../../config/method.md` — `@reference` in the block, `@utility` for
   `.legacy-card`.
3. Fix R-03 and R-06 in `../../migration/method.md` — `@source inline` for the safelist, decide the
   global border default once.
4. Re-run the pass. The counts must go down; if a count is unchanged, the fix did not land where the
   rule looks.
5. R-08/R-09/R-10 findings, when present, are addressed only after errors are zero.

## Clean and large-tree variants

```text
Tailwind Validator Report
=========================
Project state : v4 detected (tailwindcss@^4.0.5)
Scan scope    : src/ tailwind.config.js postcss.config.mjs
Files scanned : 8
Issues        : 0

All rules passed.
```

```text
Tailwind Validator Report
=========================
Project state : v4 detected (tailwindcss@^4.0.5)
Scan scope    : 1247 files in src/ tests/
Issues        : 23 (4 errors, 11 warnings, 8 info)

By area :
  src/components/      14 issues (3 errors)
  src/pages/            6 issues (1 error)
  src/lib/              3 issues
  tailwind.config.js    0 issues (post-migration clean)

---

[ERROR] R-01 : dynamic class string
  File       : src/components/StatusBadge.tsx:12
  Code       : className={`bg-${level === 'high' ? 'red' : 'amber'}-500`}
  Cite       : ../dynamic-classes/method.md (static map)
  Suggested  : the ternary must return complete class strings:
               `level === 'high' ? 'bg-red-500' : 'bg-amber-500'`.

[ERROR] R-01 : dynamic class string (continued)
  Additional occurrences :
    src/components/TagList.tsx:8
    src/pages/dashboard/widget.tsx:34
    src/lib/badge-builder.ts:22
  Cite for all : ../dynamic-classes/method.md (same fix shape)
```

Group the by-area block first, then full blocks for the first three files per rule, then the
collapsed remainder. State stays fresh between runs — no cache, no baseline file, no suppressed
findings carried forward.
