# anti-patterns — the wrong fixes, and what replaces them

Ten attempts that look like solutions. Each is the same mistake in different clothes: asking the
build-time scanner to guess what runtime code will produce. The scanner cannot guess; it reads text.

## 1. Disable purge / JIT

**Tried:** delete the v3 `content` array, set `purge: false` in a config copied from an old tutorial,
or hunt for v4's "turn the scanner off" switch.

**Fails because:** v3 with no `content` has nothing to scan and generates **zero** classes. `purge` was
a v2 option, removed in v3. v4's scanner is the build engine — `source(none)` disables automatic
*path* discovery, not class detection, so registered sources are still parsed as text. And even if the
whole library shipped, the bundle is 3+ MB of CSS and page-load performance is the loss.

**Instead:** one of the four ranked fixes (`../method.md`). Path/source configuration belongs to
`../../config/method.md`.

## 2. Comment the classes in

**Tried:**

```jsx
// className includes bg-red-500 bg-blue-500 bg-green-500
function Tag({ color }) {
  return <span className={`bg-${color}-500`} />
}
```

**Fails because:** it works — that is the trap. The comment is text, so the tokens are detected. Then
someone refactors, sees a comment with no code behind it, deletes it, and the styles vanish in the
next production build. Nothing links the comment to the runtime values, and nothing fails loudly when
the link breaks.

**Instead:** the static map. Its literals are the component's logic; deleting one breaks the build, not
silently the CSS.

## 3. Split the name into "static" pieces

**Tried:**

```jsx
function Tag({ color }) {
  const prefix = 'bg-'
  const shade = '-500'
  return <span className={prefix + color + shade} />
}
```

**Fails because:** the scanner sees the literals `'bg-'` and `'-500'`. Neither is a utility name, and
`bg-red-500` exists only in the assembled string at runtime. Moving the fragments into constants,
enums, or a theme object changes nothing — no file ever contains the whole token.

**Instead:** static map, values being complete class strings.

## 4. Blame or lean on `clsx` / `classnames` / `cn` / `tailwind-merge`

**Tried:**

```jsx
import { cn } from '@/lib/utils'
function Button({ color }) {
  return <button className={cn(`bg-${color}-500`, 'p-2')} />
}
```

**Fails because:** these helpers run at runtime and only join strings. Detection happened long before,
and a template literal is opaque whichever helper swallows it. Expecting `tailwind-merge` to "make the
class real" is a category error — it resolves conflicts among classes that already exist.

**Instead:** keep the helper, fix the source of the class.

```jsx
const colorVariants = { red: 'bg-red-500', blue: 'bg-blue-500' }
function Button({ color }) {
  return <button className={cn(colorVariants[color], 'p-2')} />
}
```

## 5. Safelist everything with a permissive regex

**Tried (v3):**

```js
module.exports = {
  safelist: [{ pattern: /.*/ }],
}
```

**Fails because:** it compiles every utility Tailwind knows — multiple megabytes. Utility CSS earns its
keep on dead-code elimination; a catch-all throws that away and reintroduces the framework's original
complaint. The same mistake in v4 is an `@source inline` directive over every colour, every shade, and
every variant "to be safe".

**Instead:** narrow to the values actually emittable:

```js
{ pattern: /bg-(red|blue|green)-(500|700|900)/, variants: ['hover'] }
```

## 6. Variants inside the v3 pattern regex

**Tried:**

```js
module.exports = {
  safelist: [{ pattern: /hover:bg-(red|green)-500/ }],
}
```

**Fails because:** a `pattern` is matched against base utility names, then the variants listed in
`variants` are applied. `hover:` inside the regex matches nothing, so the directive looks correct and
emits no CSS at all.

**Instead:**

```js
{ pattern: /bg-(red|green)-500/, variants: ['hover'] }
```

In v4 the same rule inverts: variants are part of the expanded string, so
`@source inline("{hover:,}bg-red-500")` is correct there (`../method.md` §Fix 4 grammar).

## 7. A demo file full of literal classes

**Tried:**

```jsx
// SafelistDemo.jsx — never imported, exists for the scanner
export const _safelist = (
  <>
    <div className="bg-red-500 bg-blue-500 bg-green-500" />
    <div className="text-red-500 text-blue-500 text-green-500" />
    {/* every class the app might use */}
  </>
)
```

**Fails because:** it works at first, then the bundler's tree-shaker drops the unused export, and
whether the scanner still sees the file depends on the build setup — some configurations read every
file under the source root, others honour the module graph. The result is unpredictable across setups
and unexplainable in review. This is also the trick behind "I pasted a Storybook demo and the styles
came back": the dev cache kept rules the shipped source never contained.

**Instead:** `safelist` (v3) or `@source inline` (v4) — explicit, build-time, versioned mechanisms.

## 8. Patch the build to skip detection

**Tried:** edit `node_modules`, fork Tailwind, or monkey-patch the plugin pipeline to ship unminified
full output.

**Fails because:** the patch dies on the next `npm install`, is invisible to a clean checkout, and
lands the project on the same megabyte outcome as anti-pattern 5. It converts a one-line application
bug into an infrastructure fork.

**Instead:** there is no Tailwind defect to patch; the application is constructing names it should be
selecting. Static map.

## 9. Give up and inline every style

**Tried:** for the dynamic component, abandon classes entirely and pass a `style` object with padding,
radius, typography, colours, and states.

**Fails because:** inline declarations lose responsive prefixes, `hover:`/`focus:`, dark mode, and
reduced-motion handling for that component, override the design system's specificity politely and its
intent rudely, and read as a foreign dialect in a utility codebase.

**Instead:** inline style for the one genuinely arbitrary value (`fixes.md` §Fix 2), Tailwind classes
for everything bounded. The CSS-variable hybrid keeps the structure in the system:
`className="border-(--accent) bg-(--accent)/10"` with `style={{ '--accent': accent }}`.

## 10. A "dynamic class" helper in a shared constants file

**Tried:**

```js
// constants.js
export const DYNAMIC_BG = (color) => `bg-${color}-500`
```

Used everywhere as `className={DYNAMIC_BG(color)}` — tidier, centralised, still broken.

**Fails because:** the scanner reads `constants.js` as text and finds a template literal, exactly the
original defect with better marketing. Centralising construction does not materialise literals; it just
puts the bug where every consumer inherits it.

**Instead:** hold the tokens, not the builder.

```js
// constants.js
export const BG_COLORS = {
  red: 'bg-red-500',
  blue: 'bg-blue-500',
  green: 'bg-green-500',
}
```

Consumers index in (`BG_COLORS[color]`); the file is now the layer that owns the names, which is the
only place interpolation is legal.
