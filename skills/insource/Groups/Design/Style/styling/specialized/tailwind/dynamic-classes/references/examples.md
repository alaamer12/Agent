# examples — broken and fixed, side by side

Ten scenarios that produce the same symptom: the class reaches the DOM, no rule reaches the CSS.
Each carries the bug, the fix, and why the fix satisfies the plain-text rule (`../method.md`).

## 1. The classic template literal

```jsx
// broken — no complete token exists
function Tag({ color, label }) {
  return (
    <span className={`bg-${color}-100 text-${color}-800 rounded px-2 py-1`}>
      {label}
    </span>
  )
}

<Tag color="red" label="Error" />     // unstyled in production
<Tag color="green" label="Success" /> // unstyled in production
```

```jsx
// fixed — every value is a literal
const tagStyles = {
  red: 'bg-red-100 text-red-800',
  green: 'bg-green-100 text-green-800',
  blue: 'bg-blue-100 text-blue-800',
  amber: 'bg-amber-100 text-amber-800',
}

function Tag({ color, label }) {
  return (
    <span className={`${tagStyles[color]} rounded px-2 py-1`}>
      {label}
    </span>
  )
}
```

The static part (`rounded px-2 py-1`) stays in the attribute; only the colour pair moves into the map.

## 2. Two props composed

```jsx
// broken
function Card({ accent, size }) {
  return <div className={`border-${accent}-500 p-${size}`}>…</div>
}
```

```jsx
// fixed — one map per prop, joined at the call site
const accents = {
  red: 'border-red-500',
  blue: 'border-blue-500',
  green: 'border-green-500',
}
const sizes = {
  sm: 'p-2',
  md: 'p-4',
  lg: 'p-6',
}

function Card({ accent = 'blue', size = 'md', children }) {
  return (
    <div className={`${accents[accent]} ${sizes[size]} rounded-lg`}>
      {children}
    </div>
  )
}
```

Two bounded axes never become one cartesian regex. Separate maps keep each axis readable and each
token literal; a cartesian product of the two is what a safelist is for when the set is genuinely
large.

## 3. CMS-driven class string (issue 18136)

The canonical report: the CMS returns a class string per page, the component merges it into a static
list, the class shows in the DOM and produces nothing.

```jsx
// data from the CMS
const webPages = { className: 'my-4 sm:my-5 md:my-8 lg:my-10' }

<div className={cn(
  "space-y-8 md:space-y-12 lg:space-y-14",
  webPages?.className
)}>
```

`my-4`, `sm:my-5`, `md:my-8`, `lg:my-10` are tokens in a database row, not in a scanned file. The
merging helper is irrelevant — `cn` runs at runtime and detection happens at build time
(`anti-patterns.md` §4).

**Fix A — v4 `@source inline`:**

```css
@import "tailwindcss";

@source inline("{sm:,md:,lg:,xl:,}m{x,y,t,r,b,l,}-{0..16}");
```

Every margin utility `m-0` … `ml-16` at four breakpoints, plus the unprefixed originals. Anything in
that shape the CMS can issue now resolves.

**Fix B — v3 safelist:**

```js
module.exports = {
  safelist: [
    {
      pattern: /m[xytrbl]?-\d+/,
      variants: ['sm', 'md', 'lg', 'xl'],
    },
  ],
}
```

Same coverage, and note the variant prefixes are in `variants`, never in the pattern.

**Fix C — constrain the input:** the CMS field is a dropdown whose options are design-system values.
Only those strings can be emitted, so the pre-generated set is small, reviewable, and cannot drift.
Fix C is the right answer whenever the editor is under your control; A and B are for data you do not
own (`../method.md` §When no fix applies).

## 4. Status pill with a typed key

```tsx
// broken
type Status = 'success' | 'warning' | 'error' | 'info'

function Pill({ status }: { status: Status }) {
  return <span className={`bg-${status}-100 text-${status}-700`}>{status}</span>
}
```

Doubly broken: `success` is not a Tailwind colour name, and even if it were, the interpolation is
invisible to the scanner.

```tsx
// fixed — the map is also the semantic translation layer
const styles: Record<Status, string> = {
  success: 'bg-emerald-100 text-emerald-700',
  warning: 'bg-amber-100 text-amber-700',
  error: 'bg-red-100 text-red-700',
  info: 'bg-sky-100 text-sky-700',
}

function Pill({ status }: { status: Status }) {
  return (
    <span className={`${styles[status]} rounded-full px-2 py-1 text-xs font-medium`}>
      {status}
    </span>
  )
}
```

`Record<Status, string>` makes an unmapped status a compile error — the domain vocabulary is allowed
to differ from the palette, which is exactly what a map is for.

## 5. User colour picker

The input space is every colour a person can type; nothing can be enumerated.

```tsx
// inline style — the honest channel
function ColorSwatch({ hex, name }: { hex: string; name: string }) {
  return (
    <button
      className="flex flex-col items-center gap-2 rounded-md p-3 ring-1 ring-zinc-200 hover:ring-zinc-400"
      style={{ '--swatch': hex } as React.CSSProperties}
    >
      <span className="block size-10 rounded-full" style={{ backgroundColor: hex }} />
      <span className="text-xs font-medium text-zinc-700">{name}</span>
    </button>
  )
}
```

```tsx
// hybrid — Tailwind owns the structure, the variable owns the colour
function ColorSwatch({ hex, name }: { hex: string; name: string }) {
  return (
    <button
      style={{ '--swatch': hex } as React.CSSProperties}
      className="flex flex-col items-center gap-2 rounded-md p-3 ring-1 ring-zinc-200 hover:ring-(--swatch)"
    >
      <span className="block size-10 rounded-full bg-(--swatch)" />
      <span className="text-xs font-medium text-zinc-700">{name}</span>
    </button>
  )
}
```

`bg-(--swatch)` and `hover:ring-(--swatch)` are literal tokens, generated once; the hex arrives at
runtime through the variable, so no CSS is produced per picked colour.

## 6. Classes inside translation files

```json
// en.json
{
  "alert": "Click the <a class='text-red-600 underline'>red link</a> below."
}
```

Whether these tokens are found depends on the version. v3 reads only files matching its `content`
globs, and a glob of code extensions never opens a locale JSON — the classes are missing. v4's automatic
detection walks the project and does read plain-text `.json` (it skips CSS, binaries, gitignored paths,
and lock files), so the markup in a translation file may already resolve — but a style that survives
only because a translator wrote a class into a string is not a contract: it breaks when the file moves,
when a lock-file rule changes, or when `source(none)` is used. Either way, fix the registration or
pre-generate the set.

**Fix A — register the locale files as sources.** v3:

```js
module.exports = {
  content: [
    './src/**/*.{html,js,ts,jsx,tsx}',
    './src/locales/**/*.json',
  ],
}
```

v4, in the stylesheet that imports Tailwind:

```css
@source "../locales";
```

Path patterns and `@source` registration are the `config` module's (`../../config/method.md`). Scanning
markup inside JSON means the translator is now writing style, so treat this fix as a stopgap.

**Fix B — pre-generate exactly the classes translations are allowed to use:**

```css
@source inline("text-{red,blue,green}-600 underline");
```

Then document that set in the localization guide; anything outside it renders unstyled. The v3 form is
`safelist: ['text-red-600', 'text-blue-600', 'text-green-600', 'underline']`.

## 7. Class string built server-side

```js
// broken — the concatenation happens in the request, after the build
function buildBadge(level) {
  // level is 1..5
  return `<span class="bg-zinc-${level * 100} text-white p-2">${level}</span>`
}
```

```js
// fixed — the literals are in the file that generates the markup
const bgByLevel = {
  1: 'bg-zinc-100',
  2: 'bg-zinc-200',
  3: 'bg-zinc-300',
  4: 'bg-zinc-400',
  5: 'bg-zinc-500',
}

function buildBadge(level) {
  return `<span class="${bgByLevel[level]} text-white p-2">${level}</span>`
}
```

Arithmetic on a shade number (`level * 100`) is the extreme case: the name does not exist as a
substring anywhere, in any form. The map is the fix in plain JS, template strings, and SSR alike.

## 8. Storybook args

```tsx
// Button.stories.tsx
export default {
  component: Button,
  argTypes: {
    color: { control: 'select', options: ['red', 'blue', 'green'] },
  },
}
```

`Button` builds `bg-${color}-500`. The stories file does contain the option strings, but as colour
names, not as class tokens, and the class never assembles in a scanned file.

Fix the component (example 1). Storybook is downstream of the implementation. Two secondary traps: the
dev-only story can make the class appear to work while the app bundle lacks it, and pasting the
generated classes into a story as literal text can make the rule exist in dev and vanish later
(`../method.md` §Why dev works and prod fails, `anti-patterns.md` §7).

## 9. Dynamic grid columns

```tsx
// broken
function Grid({ cols, children }) {
  return <div className={`grid grid-cols-${cols} gap-4`}>{children}</div>
}
```

```tsx
// fixed A — bounded layout choices belong in a map
const colsClasses = {
  1: 'grid-cols-1',
  2: 'grid-cols-2',
  3: 'grid-cols-3',
  4: 'grid-cols-4',
  6: 'grid-cols-6',
  12: 'grid-cols-12',
}

function Grid({ cols = 1, children }) {
  return <div className={`grid ${colsClasses[cols]} gap-4`}>{children}</div>
}
```

```tsx
// fixed B — genuinely arbitrary column counts go through the property, not a utility
function Grid({ cols, children }) {
  return (
    <div
      className="grid gap-4"
      style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}
    >
      {children}
    </div>
  )
}
```

Choose A when the design permits a fixed number of column counts (it usually does); B when a user or
a measured container really can demand any count. A v4 directive such as
`@source inline("grid-cols-{1..12}")` also works but generates twelve rules to cover a decision the
component should express — that is the ranked-4 trade-off, not a free win.

## 10. Marketing site with CMS-managed pages

v4, one stylesheet, everything the CMS can issue, nothing more:

```css
@import "tailwindcss";

/* palette the CMS can choose from */
@source inline(
  "{hover:,focus:,}bg-{rose,amber,emerald,sky,violet}-{50,100,500,700,900}"
);
@source inline(
  "text-{rose,amber,emerald,sky,violet}-{500,700,900}"
);

/* spacing scale */
@source inline("p-{2,4,6,8,12,16}");
@source inline("m-{2,4,6,8,12,16}");
@source inline("gap-{2,4,6,8}");

/* type scale */
@source inline("text-{sm,base,lg,xl,2xl,3xl,4xl}");

/* responsive type */
@source inline("{sm:,md:,lg:,xl:,}text-{base,lg,xl,2xl,3xl}");
```

A few hundred emitted rules, each traceable to an allowed CMS choice. The list is reviewed as part of
the design-system change, not extended ad hoc when a page looks wrong — that drift audit is checklist
item 4 in `../method.md`.
