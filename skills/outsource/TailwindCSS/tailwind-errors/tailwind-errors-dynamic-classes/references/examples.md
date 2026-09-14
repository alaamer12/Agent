# Examples : Working Code

Each example is a complete, runnable snippet showing the bug and the
fix side by side.

## Example 1 : The Classic Mistake

### Broken (template literal)

```jsx
function Tag({ color, label }) {
  return (
    <span className={`bg-${color}-100 text-${color}-800 rounded px-2 py-1`}>
      {label}
    </span>
  )
}

// usage
<Tag color="red" label="Error" />     // no styles in prod
<Tag color="green" label="Success" /> // no styles in prod
```

### Fixed (static map)

```jsx
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

## Example 2 : Multiple Props Composed

### Broken

```jsx
function Card({ accent, size }) {
  return (
    <div className={`border-${accent}-500 p-${size}`}>
      ...
    </div>
  )
}
```

### Fixed (compose two static maps)

```jsx
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

## Example 3 : CMS-Driven Colour (Issue 18136 Scenario)

The original bug report : a CMS returns a class string per page, the
React component appends it to a static class list, the class shows in
DOM but produces no style.

### Original broken code

```jsx
// data from CMS
const webPages = { className: 'my-4 sm:my-5 md:my-8 lg:my-10' }

// component
<div className={cn(
  "space-y-8 md:space-y-12 lg:space-y-14",
  webPages?.className
)}>
```

Tailwind never scanned the CMS payload. `my-4`, `sm:my-5`, `md:my-8`,
`lg:my-10` are never tokens in any source file.

### Fix A : v4 @source inline

```css
/* app.css */
@import "tailwindcss";

@source inline("{sm:,md:,lg:,xl:,}m{x,y,t,r,b,l,}-{0..16}");
```

Generates every margin utility from `m-0` through `mb-16` with every
breakpoint prefix. CMS-issued classes from this set will resolve.

### Fix B : v3 safelist

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

### Fix C : restrict the CMS input to a fixed allowlist

The cleanest answer : the CMS dropdown for "page margin" emits ONLY
values from the design system. Pre-safelist exactly that set, reject
free-form input at the CMS layer.

## Example 4 : Status Pill Component

### Broken

```tsx
type Status = 'success' | 'warning' | 'error' | 'info'

function Pill({ status }: { status: Status }) {
  return (
    <span className={`bg-${status}-100 text-${status}-700`}>
      {status}
    </span>
  )
}
```

`success`, `warning`, `error`, `info` are not Tailwind colour names.
Even if they were, the template literal would still break.

### Fixed

```tsx
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

## Example 5 : User Colour Picker

User picks an arbitrary colour. There is no way to safelist every
possible value : the input space is 16.7 million hex codes.

### Wrong : try to safelist

You cannot. Skip this approach.

### Right : inline style

```tsx
function ColorSwatch({ hex, name }: { hex: string; name: string }) {
  return (
    <button
      className="flex flex-col items-center gap-2 rounded-md p-3 ring-1 ring-zinc-200 hover:ring-zinc-400"
      style={{ '--swatch': hex } as React.CSSProperties}
    >
      <span
        className="block size-10 rounded-full"
        style={{ backgroundColor: hex }}
      />
      <span className="text-xs font-medium text-zinc-700">{name}</span>
    </button>
  )
}
```

### Hybrid : Tailwind structure + CSS variable

```tsx
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

`bg-(--swatch)` and `ring-(--swatch)` are literal tokens. The CSS
variable carries the runtime hex.

## Example 6 : i18n String With Inline Class

A translation file containing markup is invisible to the scanner.

### Broken

```json
// en.json
{
  "alert": "Click the <a class='text-red-600 underline'>red link</a> below."
}
```

Tailwind does NOT scan `.json` files by default. `text-red-600` and
`underline` are not detected.

### Fix A : add the JSON file to the content scan

v3 `tailwind.config.js` :

```js
module.exports = {
  content: [
    './src/**/*.{html,js,ts,jsx,tsx}',
    './src/locales/**/*.json',
  ],
}
```

v4 :

```css
@source "../locales";
```

### Fix B : safelist the specific classes used in translations

```css
@source inline("text-{red,blue,green}-600 underline");
```

## Example 7 : Tailwind Class String Built Server-Side

### Broken (Node template)

```js
function buildBadge(level) {
  // level is 1..5
  return `<span class="bg-zinc-${level * 100} text-white p-2">${level}</span>`
}
```

`bg-zinc-100`, `bg-zinc-200`, ..., `bg-zinc-500` are runtime
concatenations. Never literal tokens in this file.

### Fixed

```js
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

## Example 8 : Storybook Dynamic Args

Storybook control passes a colour prop to the component via Storybook
args. The actual class string only exists in code when Storybook is
running.

### Broken

```tsx
// Button.stories.tsx
export default {
  component: Button,
  argTypes: {
    color: { control: 'select', options: ['red', 'blue', 'green'] },
  },
}
```

`Button` uses `bg-${color}-500`. Tailwind scans `Button.tsx`, sees the
template literal, generates nothing.

### Fixed

Same `Button.tsx` fix as Example 1. Storybook is downstream of the
component implementation ; fix the component, not Storybook.

## Example 9 : Dynamic Grid Columns

### Broken

```tsx
function Grid({ cols, children }) {
  return (
    <div className={`grid grid-cols-${cols} gap-4`}>
      {children}
    </div>
  )
}
```

### Fixed (static map)

```tsx
const colsClasses = {
  1: 'grid-cols-1',
  2: 'grid-cols-2',
  3: 'grid-cols-3',
  4: 'grid-cols-4',
  6: 'grid-cols-6',
  12: 'grid-cols-12',
}

function Grid({ cols = 1, children }) {
  return (
    <div className={`grid ${colsClasses[cols]} gap-4`}>
      {children}
    </div>
  )
}
```

### Fixed (arbitrary value)

```tsx
function Grid({ cols, children }) {
  return (
    <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}>
      {children}
    </div>
  )
}
```

## Example 10 : Full v4 Design-System Safelist for a Marketing Site

The site renders CMS-managed marketing pages with limited but variable
colour and spacing choices.

```css
/* app.css */
@import "tailwindcss";

/* limited colour palette CMS can choose from */
@source inline(
  "{hover:,focus:,}bg-{rose,amber,emerald,sky,violet}-{50,100,500,700,900}"
);
@source inline(
  "text-{rose,amber,emerald,sky,violet}-{500,700,900}"
);

/* spacing scale the CMS can pick from */
@source inline("p-{2,4,6,8,12,16}");
@source inline("m-{2,4,6,8,12,16}");
@source inline("gap-{2,4,6,8}");

/* typography sizes */
@source inline("text-{sm,base,lg,xl,2xl,3xl,4xl}");

/* responsive variants of the above */
@source inline("{sm:,md:,lg:,xl:,}text-{base,lg,xl,2xl,3xl}");
```

Total emitted classes : a few hundred. Bundle stays small, CMS-issued
classes always resolve. The set is documented and reviewed each
release.
