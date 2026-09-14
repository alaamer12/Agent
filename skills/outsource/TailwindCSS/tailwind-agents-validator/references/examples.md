# Examples : Input Code and Generated Report

End-to-end example. A small codebase, the validator run, the report it
produces.

## Input Codebase

Tree :

```
example-app/
  package.json
  tailwind.config.js
  postcss.config.mjs
  src/
    app.css
    components/
      Tag.tsx
      Hero.vue
      Pill.tsx
      Card.tsx
```

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
  safelist: ['bg-red-500', 'bg-blue-500'],
  corePlugins: { float: false },
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

@theme {
  --color-brand: #5b21b6;
}

.legacy-card {
  background: #fff;
  border-radius: 1rem;
  padding: 1rem;
}
```

### `src/components/Tag.tsx`

```tsx
type Color = 'red' | 'green' | 'blue'

export function Tag({ color, label }: { color: Color; label: string }) {
  return (
    <span className={`bg-${color}-100 text-${color}-800 px-2 py-1 rounded`}>
      {label}
    </span>
  )
}
```

### `src/components/Hero.vue`

```vue
<template>
  <h1>Welcome — to the example.</h1>
</template>

<style scoped>
  h1 { @apply text-4xl font-bold text-zinc-900; }
</style>
```

### `src/components/Pill.tsx`

```tsx
export function Pill({ status }: { status: 'ok' | 'warn' | 'err' }) {
  const styles = {
    ok: 'bg-emerald-100 text-emerald-700',
    warn: 'bg-amber-100 text-amber-700',
    err: 'bg-red-100 text-red-700',
  }
  return (
    <span className={`${styles[status]} rounded-full px-2 py-1 text-xs`}>
      {status}
    </span>
  )
}
```

### `src/components/Card.tsx`

```tsx
export function Card({ children }: { children: React.ReactNode }) {
  return (
    <div className="border rounded-lg p-4">
      {children}
    </div>
  )
}
```

## Validator Run

User command : "validate my Tailwind code"

Agent steps :

1. Detect state : package = v4, css = v4, postcss = v4, vite = none.
   Consensus = v4.
2. Run rules R-01 through R-10.
3. Format report.

## Generated Report

```
Tailwind Validator Report
=========================
Project state : v4 detected (tailwindcss@^4.0.5)
Scan scope    : src/ tailwind.config.js postcss.config.mjs
Files scanned : 6
Issues        : 5 (2 errors, 2 warnings, 1 info)

---

[ERROR] R-01 : dynamic class string
  File       : src/components/Tag.tsx:5
  Code       : `className={`bg-${color}-100 text-${color}-800 px-2 py-1 rounded`}`
  Cite       : tailwind-errors-dynamic-classes (Fix 1, static map)
  Suggested  : replace the template literal with a lookup :

               const styles = {
                 red:   'bg-red-100 text-red-800',
                 green: 'bg-green-100 text-green-800',
                 blue:  'bg-blue-100 text-blue-800',
               }
               className={`${styles[color]} px-2 py-1 rounded`}

[ERROR] R-02 : scoped @apply without @reference
  File       : src/components/Hero.vue:5
  Block      : <style scoped> contains @apply, no @reference present
  Cite       : tailwind-impl-apply-directive
  Suggested  : prepend `@reference "../app.css";` inside <style scoped>

[WARNING] R-03 : forbidden v3 key in v4 config
  File       : tailwind.config.js:3
  Key        : safelist
  Cite       : tailwind-impl-migration-v3-v4 (Method 7)
  Suggested  : move to src/app.css :
               `@source inline("bg-red-500 bg-blue-500");`
               remove the `safelist` entry from tailwind.config.js

[WARNING] R-03 : forbidden v3 key in v4 config
  File       : tailwind.config.js:4
  Key        : corePlugins
  Cite       : tailwind-impl-migration-v3-v4 (Method 7)
  Suggested  : v4 has no corePlugins replacement ; remove the entry
               and add an ESLint rule banning `float-*` utilities, OR
               use `@source not "..."` to exclude files that may
               introduce floats.

[INFO] R-06 : bare border / ring under v4
  File       : src/components/Card.tsx:4
  Code       : `<div className="border rounded-lg p-4">`
  Cite       : tailwind-impl-migration-v3-v4 (Default colour changes)
  Suggested  : add explicit colour, e.g. `border border-zinc-200`,
               or restore v3 defaults globally in src/app.css :

               @layer base {
                 *, ::after, ::before, ::backdrop, ::file-selector-button {
                   border-color: var(--color-gray-200, currentColor);
                 }
               }

---
Total : 5 issues
  Errors   : 2
  Warnings : 2
  Info     : 1
```

Note : `R-07 em-dash` is NOT flagged on `Hero.vue:2` because the
text is example content in this fixture. In a real codebase the
agent would report it as Info.

## Follow-Up Workflow

Developer reads the report. Workflow :

1. Fix R-01 (Tag.tsx) by applying the suggested static map.
2. Fix R-02 (Hero.vue) by prepending `@reference`.
3. Fix R-03 (safelist) by converting to `@source inline` in CSS, then
   delete the JS entry.
4. Fix R-03 (corePlugins) by removing and accepting the loss of
   utility-disable capability, plus adding the ESLint rule.
5. Decide on R-06 : add explicit colour OR restore globally.

Re-run the validator after each fix to verify the count goes down. The
agent does NOT keep state between runs ; each run is fresh.

## Example : Clean Codebase Report

After all fixes :

```
Tailwind Validator Report
=========================
Project state : v4 detected (tailwindcss@^4.0.5)
Scan scope    : src/ tailwind.config.js postcss.config.mjs
Files scanned : 6
Issues        : 0

All rules passed.
```

## Example : Larger Codebase Excerpts

For a real codebase with hundreds of files, the report follows the
same format but groups by directory at the start :

```
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
  Code       : `className={`bg-${level === 'high' ? 'red' : 'amber'}-500`}`
  Cite       : tailwind-errors-dynamic-classes
  Suggested  : ternary should return COMPLETE class strings :
               `className={level === 'high' ? 'bg-red-500' : 'bg-amber-500'}`

...
```

The first-3 files with errors get full block treatment in the report.
The remainder is summarised in a tail section :

```
[ERROR] R-01 : dynamic class string (continued)
  Additional occurrences :
    src/components/TagList.tsx:8
    src/pages/dashboard/widget.tsx:34
    src/lib/badge-builder.ts:22
  Cite for all : tailwind-errors-dynamic-classes (same fix pattern)
```
