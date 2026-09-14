# Anti-Patterns : Wrong Fixes

Each trap : the wrong fix people try, why it fails, what to do
instead.

## Wrong Fix 1 : Disable Purge / JIT

### What people try

In v3 : delete the `content` array, or set `purge: false` in old
configs. In v4 : try to find a way to "turn off the scanner."

### Why it fails

v3 with no `content` generates ZERO classes (the scanner has nothing
to scan). v3 with `purge: false` is a v2 option, removed in v3. v4
has no way to disable scanning ; the scanner is the build engine.

Even if it worked, the output bundle would be 3+ MB of every possible
Tailwind class, breaking page-load performance.

### Right answer

Use one of the four supported fixes (static map, inline style,
safelist, or `@source inline`).

## Wrong Fix 2 : Comment the Classes Somewhere

### What people try

```jsx
// className includes bg-red-500 bg-blue-500 bg-green-500
function Tag({ color }) {
  return <span className={`bg-${color}-500`} />
}
```

The idea : Tailwind scans the file, sees `bg-red-500` etc. in the
comment, and generates them.

### Why it fails

It DOES work for the comment scan. But the comment drifts. Three
months later someone refactors, removes the comment thinking it is
dead code, and the bug returns. There is no link between the comment
and the runtime values.

### Right answer

Static map (Fix 1). The lookup itself contains the literal tokens,
they cannot be removed without removing the component logic.

## Wrong Fix 3 : Concat Classes With Variables to "Make It Static"

### What people try

```jsx
function Tag({ color }) {
  const prefix = 'bg-'
  const shade = '-500'
  return <span className={prefix + color + shade} />
}
```

### Why it fails

The scanner sees only the literal strings `'bg-'` and `'-500'`.
Neither matches a Tailwind utility name on its own. The concatenated
result `bg-red-500` exists only at runtime in the DOM.

### Right answer

Static map.

## Wrong Fix 4 : clsx / classnames / cn Helper Misuse

### What people try

```jsx
import { cn } from '@/lib/utils'
function Button({ color }) {
  return <button className={cn(`bg-${color}-500`, 'p-2')} />
}
```

### Why it fails

`cn`, `clsx`, `classnames`, `tailwind-merge` all operate at runtime.
The template literal `` `bg-${color}-500` `` is opaque to Tailwind
regardless of which helper consumes it. The helper joins classes, it
does not change the scanner's behaviour.

### Right answer

```jsx
const colorVariants = {
  red: 'bg-red-500',
  blue: 'bg-blue-500',
}
function Button({ color }) {
  return <button className={cn(colorVariants[color], 'p-2')} />
}
```

The helper is fine ; the source of the colour class needs to change.

## Wrong Fix 5 : Safelisting "Everything" With a Permissive Regex

### What people try (v3)

```js
module.exports = {
  safelist: [
    { pattern: /.*/ },
  ],
}
```

### Why it fails

Compiles every utility in the entire Tailwind library : multiple
megabytes of CSS. The whole point of utility-CSS is dead-code
elimination ; safelisting everything throws that away.

### Right answer

Narrow the pattern to the colours and shades actually in use :

```js
{
  pattern: /bg-(red|blue|green)-(500|700|900)/,
  variants: ['hover'],
}
```

## Wrong Fix 6 : Variants Inside the v3 Regex

### What people try

```js
module.exports = {
  safelist: [
    { pattern: /hover:bg-(red|green)-500/ },
  ],
}
```

### Why it fails

v3 safelist patterns match BASE utility names only. A pattern with
`hover:` inside it never matches anything.

### Right answer

```js
{
  pattern: /bg-(red|green)-500/,
  variants: ['hover'],
}
```

## Wrong Fix 7 : Static Demo File With Every Class

### What people try

```jsx
// SafelistDemo.jsx
export const _safelist = (
  <>
    <div className="bg-red-500 bg-blue-500 bg-green-500" />
    <div className="text-red-500 text-blue-500 text-green-500" />
    {/* every class your app uses */}
  </>
)
```

The file is never imported, exists only to give the scanner literal
tokens.

### Why it fails (subtly)

It WORKS at first. Then a tree-shaker (Rollup, esbuild) detects the
unused export and excludes the file from the production bundle. Some
scanners read all files in `src/` regardless ; others honour the
tree-shaker's view. The result is unpredictable across build setups.

### Right answer

Use `safelist` (v3) or `@source inline` (v4). Both are explicit
build-time mechanisms designed for this. The demo-file trick is a
hack with side-effects.

## Wrong Fix 8 : Patch the Build to Skip the Scanner

### What people try

Modifying `node_modules` or forking Tailwind to skip the dead-code
elimination step.

### Why it fails

The patch never survives an `npm install`. Maintenance burden is
infinite. The same outcome (every class shipped) is available via the
permissive regex anti-pattern (also wrong).

### Right answer

There is no Tailwind problem ; there is an application architecture
problem. Use a static map.

## Wrong Fix 9 : Inline All Styles, Never Use Tailwind Classes

### What people try

Give up on Tailwind for the dynamic component. Pass every style as an
inline `style={{ ... }}` object.

### Why it fails

Loses the design-system benefits (responsive variants, hover/focus
states, dark mode) for the affected component. Verbose. Inconsistent
with the rest of the codebase.

### Right answer

Inline `style` is the right answer for TRULY arbitrary values (a
user-typed colour). For bounded enumerations, a static map keeps the
Tailwind benefits.

## Wrong Fix 10 : Adding Dynamic Classes to a Global Constants File

### What people try

```js
// constants.js
export const DYNAMIC_BG = (color) => `bg-${color}-500`
```

Imported everywhere, used as `className={DYNAMIC_BG(color)}`.

### Why it fails

The scanner reads `constants.js` and sees the template literal in the
function body, exactly the same opacity problem as the original
template-literal antipattern. Centralising the bug does not fix it.

### Right answer

```js
// constants.js
export const BG_COLORS = {
  red: 'bg-red-500',
  blue: 'bg-blue-500',
  green: 'bg-green-500',
}
```

The constants file holds the literal tokens. Consumers index in via
`BG_COLORS[color]`.
