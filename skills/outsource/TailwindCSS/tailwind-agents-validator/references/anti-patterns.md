# Anti-Patterns : High-Impact Violations the Validator Catches

Each entry : a real-world bad pattern, why it slips past code review,
what the validator detects, the sibling skill that documents the fix.

## Pattern 1 : The "Looks Fine Locally" Dynamic Class

### Bad

```tsx
function Tag({ color }: { color: 'red' | 'blue' | 'green' }) {
  return <span className={`bg-${color}-100 text-${color}-800 px-2 py-1`} />
}
```

### Why it passes review

The component works in development. TypeScript narrows `color` to
three known values. Code looks idiomatic. Reviewer assumes Tailwind
handles it.

### What the validator catches

R-01 Severity Error. Cites `tailwind-errors-dynamic-classes`. Reports
file path and line.

### Fix

Static map indexed by `color`. See sibling skill Method 1.

## Pattern 2 : The Migrated Vue Component That Builds Fine

### Bad

```vue
<style scoped>
  h1 { @apply text-4xl font-bold text-zinc-900; }
</style>
```

### Why it passes review

Build succeeds on the v3 project. After the v4 upgrade the build still
succeeds (the scanner does not error on individual SFCs in isolation).
The actual failure is a runtime "Cannot apply unknown utility class"
that only surfaces when the SFC is rendered.

### What the validator catches

R-02 Severity Error. Cites `tailwind-impl-apply-directive`.

### Fix

Prepend `@reference "../app.css";` inside the scoped style block.

## Pattern 3 : The Leftover safelist After v4 Upgrade

### Bad

```js
// tailwind.config.js, kept after migration
module.exports = {
  safelist: ['bg-red-500', 'bg-blue-500'],
}
```

### Why it passes review

The config file still loads (via `@config` directive in CSS, or as
an orphan). v4 silently ignores `safelist`. Developer sees no error,
assumes the safelist still works.

### What the validator catches

R-03 Severity Warning. Cites `tailwind-impl-migration-v3-v4` Method 7.

### Fix

Move to `@source inline("bg-red-500 bg-blue-500")` in CSS. Delete
the JS entry.

## Pattern 4 : The Leftover corePlugins Disable

### Bad

```js
module.exports = {
  corePlugins: { float: false, clear: false },
}
```

### Why it passes review

Same as Pattern 3 : v4 silently ignores. Developer assumes floats are
still banned project-wide. Months later, a junior adds
`<div className="float-right">` and no one notices.

### What the validator catches

R-03 Severity Warning. Cites `tailwind-impl-migration-v3-v4`.

### Fix

Add an ESLint rule banning `float-*` and `clear-*` utilities. OR
use `@source not` to exclude paths.

## Pattern 5 : The Bare Border That Used to Be Gray

### Bad (v4)

```tsx
<div className="border rounded-lg p-4">
  <h2 className="font-bold">Card</h2>
</div>
```

### Why it passes review

The same code worked perfectly under v3 with a subtle `gray-200`
border. After upgrade the border is `currentColor` (black against
white background) and looks ugly. Reviewer says "must be a one-off",
fixes that single component, moves on. Hundreds of other bare
`border` usages stay broken.

### What the validator catches

R-06 Severity Info per occurrence. Aggregates count in the by-area
summary.

### Fix

Either restore v3 default globally in `@layer base` (see sibling
skill `tailwind-impl-migration-v3-v4`) or add explicit `border-zinc-200`
to every bare `border`.

## Pattern 6 : The Ternary Chain That Should Be a Map

### Bad

```tsx
function Button({ variant }: { variant: 'primary' | 'secondary' | 'danger' }) {
  return (
    <button className={
      variant === 'primary'
        ? 'bg-indigo-600 text-white hover:bg-indigo-700'
        : variant === 'secondary'
        ? 'bg-zinc-200 text-zinc-900 hover:bg-zinc-300'
        : 'bg-red-600 text-white hover:bg-red-700'
    } />
  )
}
```

### Why it passes review

It works. Classes are complete literal strings. Tailwind generates
everything. The pattern is just ugly.

### What the validator catches

R-08 Severity Info. Cites `tailwind-core-design-system`. The agent
recognises the ternary-chain shape.

### Fix

```tsx
const variants = {
  primary: 'bg-indigo-600 text-white hover:bg-indigo-700',
  secondary: 'bg-zinc-200 text-zinc-900 hover:bg-zinc-300',
  danger: 'bg-red-600 text-white hover:bg-red-700',
}
function Button({ variant }: { variant: keyof typeof variants }) {
  return <button className={variants[variant]} />
}
```

## Pattern 7 : The twMerge With Wrong Argument Order

### Bad

```tsx
function Card({ className }: { className?: string }) {
  return (
    <div className={twMerge(className, 'p-4 bg-white rounded-lg')} />
  )
}
```

The intent : the consumer's `className` should be the override. The
result : the static `'p-4 bg-white rounded-lg'` wins because it is
the LAST argument.

### Why it passes review

The pattern looks correct (consumer-prop first, defaults after).
Reviewer assumes that is the right order ; it is the OPPOSITE of
correct for `twMerge`.

### What the validator catches

R-09 Severity Info. Cites `tailwind-impl-tailwind-merge`.

### Fix

```tsx
function Card({ className }: { className?: string }) {
  return (
    <div className={twMerge('p-4 bg-white rounded-lg', className)} />
  )
}
```

Last argument wins. Defaults first, overrides last.

## Pattern 8 : The Plugin That Works on the Author's Machine

### Bad

```js
// my-tab-plugin/index.js
const plugin = require('tailwindcss/plugin')

module.exports = plugin(function ({ matchUtilities, theme }) {
  matchUtilities(
    { tab: (v) => ({ tabSize: v }) },
    { values: theme('tabSize') }
  )
})
// no second-arg config
```

### Why it passes review

Author's project has `theme.extend.tabSize = { 1: '1', 2: '2', 4:
'4' }` already configured. Plugin works perfectly. Author publishes.
Consumer installs without `tabSize` in their config ; gets ZERO
classes.

### What the validator catches

R-10 Severity Warning when scanning a published-plugin source
directory or a workspace's local plugin folder.

### Fix

```js
module.exports = plugin(
  function ({ matchUtilities, theme }) {
    matchUtilities(
      { tab: (v) => ({ tabSize: v }) },
      { values: theme('tabSize') }
    )
  },
  { theme: { tabSize: { 1: '1', 2: '2', 4: '4', 8: '8' } } }
)
```

## Pattern 9 : The Variant Stack That Looks Fine

### Bad (v4)

```tsx
<ul className="space-y-2 first:*:pt-0 last:*:pb-0">
  {items.map(item => <li key={item}>{item}</li>)}
</ul>
```

### Why it passes review

The classes still compile under v4 ; the codemod did not flag them ;
the visual outcome is subtly wrong (the first list item still has top
padding because the selector applies to the wrong element).

### What the validator catches

R-05 Severity Warning. Cites `tailwind-syntax-variants` and
`tailwind-impl-migration-v3-v4`.

### Fix

```tsx
<ul className="space-y-2 *:first:pt-0 *:last:pb-0">
```

`*:` first, `first:` / `last:` second. v4 reads left-to-right.

## Pattern 10 : The Em-Dash in Component Text

### Bad

```tsx
<p>Subscribe now — get 20% off your first order.</p>
```

### Why it passes review

It looks typographically correct. Most reviewers do not check char
codes. Microsoft Word and many editors auto-substitute `--` with `—`.

### What the validator catches

R-07 Severity Info. Cites the workspace CLAUDE.md typografie rule.

### Fix

```tsx
<p>Subscribe now. Get 20% off your first order.</p>
```

Or :

```tsx
<p>Subscribe now, get 20% off your first order.</p>
```

NEVER substitute with a short hyphen ; the workspace rule explicitly
bans that workaround.
