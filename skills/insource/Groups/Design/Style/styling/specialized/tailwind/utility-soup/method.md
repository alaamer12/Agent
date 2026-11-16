# utility-soup — when to extract, and the tooling that keeps order stable

A long class list is a symptom, not a bug. Utility-first buys locality and pays for it with a
30-utility `className`. Two different problems can be hiding in that line, and each has its own
answer: **duplication** (the same stack appears in N places → extract something) and **order** (the
stack is unreadable and the diffs are noisy → install tooling). Diagnose first, then treat only the
problem that is actually present.

NEVER refactor by reflex. Premature extraction destroys the locality that made Tailwind worth
choosing and adds an indirection layer no one can grep. Measure the copy count before writing a
component, a partial, or a CSS class.

## Measure before you touch it

| Utilities on the element | Verdict |
|---|---|
| < 15 | Not soup. Keep it on one line and let the formatter sort it. |
| 15-25, one component | A leaf node. Acceptable; group multi-line only when the wrap hurts reading. |
| 25+ | Long. Length alone is still not a defect — check repetition next. |
| any length x 3 copies | This is the real problem. Extract. |

```text
Long class list seen.
├── Is the markup emitted from a loop?      -> authored once; no duplication exists; stop here
├── < 15 utilities                          -> not utility soup, move on
├── 15-25 utilities, single component       -> acceptable for a leaf node
├── 25+ utilities
│   └── Is the pattern repeated elsewhere?
│       ├── No   -> it is a leaf component. Long is acceptable. Group it multi-line.
│       └── Yes  -> how many copies?
│           ├── 1-2  -> leave inline; add a TODO comment if the duplication is intentional
│           └── 3+   -> extract (decision matrix below)
```

Leaf vs repeated is the only distinction that matters. A 35-utility button used once is fine; a
12-utility stack copied into eight files is a maintenance defect regardless of how short each copy
looks.

## The 3-use rule

ALWAYS extract on the THIRD copy of a pattern, never the first.

| Copies | Action |
|---|---|
| 1 | Leave inline. |
| 2 | Leave inline. Add a TODO comment if the duplication is intentional. |
| 3+ | Extract a component (preferred), a partial, or an `@apply` class when there is no framework. |

Two duplicates is too small a sample to know the right abstraction: the third copy is what reveals
which parts are genuinely shared and which were coincidence. Extracting on the third copy is a
measurement, not a deadline — a shape may also earn extraction earlier on a strong semantic reason
(a shared interactive behaviour, an accessibility role, runtime variants).

## Cheaper than extraction

When a stack repeats but the copies sit side by side, prefer the lighter tool:

- **Loop.** If the repeated markup renders from a list, the class list is authored exactly once.
  There is no duplication to solve.
- **Multi-cursor edit.** Duplication confined to one file or one group of siblings is an editing
  problem. Select all the class attributes and change them together; abstraction adds a layer for
  zero gain.

Reach for a component/partial/`@apply` when the copies live in different files, or when the shape
carries behaviour and state, not just pixels.

## Where a repeated stack goes

```text
Repeated 3+ times AND
├── Framework available (React, Vue, Svelte, Solid)  -> extract a component; pass props for variants
├── Template language (Blade, ERB, Twig, Nunjucks)   -> extract a partial / include / slot
└── Plain HTML / MDX / third-party widget            -> @apply inside @layer components
```

```text
Component or @apply?
├── In a component framework (React, Vue, Svelte, Solid)?
│   └── Yes -> ALWAYS a component. Variants are props, never extra CSS classes.
├── In a template language (Blade, ERB, Twig, Nunjucks, Astro)?
│   └── Yes -> ALWAYS a partial / include / slot.
├── In plain HTML, MDX, or overriding a widget you do not control?
│   └── Yes -> @apply in @layer components is the right tool.
└── None of the above -> revisit; these cases cover almost every real codebase.
```

NEVER reach for `@apply` when a component is available. `@apply` exists for the markup you cannot
turn into a component; used elsewhere it rebuilds the semantic CSS framework the project opted out
of, and the class names silently stop meaning anything.

The minimal shape, for the third branch:

```css
@layer components {
  .btn-primary {
    @apply inline-flex items-center rounded-md px-4 py-2 text-sm font-medium
           bg-blue-500 text-white hover:bg-blue-600;
  }
}
```

```html
<button class="btn-primary">Save</button>
```

Keep the rule inside `@layer components` so utilities still win over it in the cascade. Layer
choice, `@apply` limitations (no composing one component class from another with `@apply`), scoped
`@apply` in SFC/CSS-module files, and the `@reference` requirement are all owned by the `config`
module — `../config/method.md`. Do not restate them here.

## If the stack stays: group it

When a legitimately long list stays inline, break it across lines **by concern**, one concern per
line: layout, then box model, sizing, typography, colour/visual, states, motion.

```tsx
<button
  className="
    inline-flex items-center justify-center
    rounded-md px-4 py-2
    text-sm font-medium
    bg-blue-500 text-white
    hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500
    disabled:opacity-50 disabled:cursor-not-allowed
    transition
  "
>
  Save
</button>
```

ALWAYS group by concern (layout, sizing, spacing, colour, state) on each line. NEVER fight the
formatter for line placement: sorting reorders *inside* the string, and the grouping above only
survives because each line happens to sort as a block. Set the format once, let the tool keep it.

NEVER use multi-line formatting for a list under ~15 utilities — it adds visual weight with no
clarity gain. Multi-line is for genuine soup (25+).

## Long lists are often an override problem in disguise

Before extracting, check whether the length comes from a consumer fighting the component's defaults.
If so, the fix is merge semantics, not a new abstraction.

Utility conflicts resolve by **position in the generated stylesheet, not position in the class
attribute**: in `class="grid flex"` the element is grid, because `.grid` is emitted first. String
concatenation therefore cannot express "keep everything except the padding" — that is why a merge
step exists.

Three distinct jobs, keep them separate:

| Job | Tool | Never confuse with |
|---|---|---|
| Join truthy parts | `clsx` (or `classnames` — one per project) | override resolution |
| Later intent wins on conflict | `tailwind-merge` (`twMerge`) | joining |
| Declare a variant matrix | `class-variance-authority` (`cva`) | a component's props API |

Every argument is a complete literal class name. NEVER assemble one from a variable
(`bg-${intent}-500`): a joined string is sorted, linted, and generated only from text that exists in
source — that failure is owned by the `dynamic-classes` module.

```tsx
import { twMerge } from "tailwind-merge"

export function Card({ className, children }: { className?: string, children: ReactNode }) {
  return (
    <div className={twMerge("rounded-lg border bg-white p-4 shadow-sm", className)}>
      {children}
    </div>
  )
}
```

```tsx
<Card className="p-8" />   {/* p-8 wins; rounded-lg, border, bg-white, shadow-sm survive */}
```

ALWAYS wrap in `twMerge` when a component accepts a `className` prop. A naive
`` `p-4 ${className}` `` produces `p-4 p-8` and hands the decision to stylesheet order — works on
your machine, breaks when the bundle order moves. `twMerge("p-4 px-6")` resolves to `py-4 px-6`,
which is the deterministic answer no cascade rule can give.

ALWAYS order merge arguments **defaults → variants → consumer prop last**. In `twMerge`/`cn` the
last occurrence of a conflicting utility wins, so a consumer `className` passed before the
component's own defaults is an inversion: the component silently overrides the caller.

`cva` becomes the right tool when the variant matrix grows past two dimensions; a plain
`base + variants[variant]` map is enough below that. The framework-neutral version of these three
jobs is in the `styling` `build` level (`/styling`).

## The tooling that keeps order stable

```text
Goal?
├── Stable class order across the team -----------------> prettier-plugin-tailwindcss
├── Catch unknown / duplicate / contradicting classes --> eslint-plugin-tailwindcss
└── Sorting inside the editor, no formatter in the loop > Headwind
```

| Tool | Purpose | Runs |
|---|---|---|
| `prettier-plugin-tailwindcss` | Sorts class names, removes duplicates | on save / on format |
| `eslint-plugin-tailwindcss` | Lints order, unknown, duplicate, contradicting, shorthand | editor + CI |
| Headwind | Editor-side sorter with its own order | on save, in the editor |

Prettier and ESLint are complementary: Prettier is the build-time formatter, ESLint validates class
names in CI. Headwind overlaps with Prettier — pick ONE sorter. Two sorters running on save produce
two different orders and fight forever.

Minimum viable setup, day one:

```json
{
  "plugins": ["prettier-plugin-tailwindcss"],
  "tailwindStylesheet": "./src/app.css",
  "tailwindFunctions": ["clsx", "cva", "tw", "twMerge", "classnames"]
}
```

Tailwind v3 points at the JS config instead (`"tailwindConfig": "./tailwind.config.js"`); v4 MUST
point at the CSS entry that holds `@import "tailwindcss"`, or custom tokens sort as unknown. v3/v4
config-surface differences belong to the `config` module and the version breakage catalog to the
`migration` module (`../migration/method.md`).

ALWAYS list every class-building wrapper in `tailwindFunctions`. Nothing is auto-detected: a wrapper
that is not named leaves its class strings unsorted, and the file passes CI while staying soup.
Design-system props that hold class lists (`wrapperClass`, `containerClass`, `myClassList`) need the
matching `tailwindAttributes` entry — plain identifiers or `/regex/` patterns.

ESLint side, the settings that decide whether the plugin is usable:

```js
import tailwind from "eslint-plugin-tailwindcss"

export default [
  ...tailwind.configs["flat/recommended"],
  {
    settings: {
      tailwindcss: {
        config: "./tailwind.config.js",        // v3; v4: cssFiles: ["./src/**/*.css"]
        callees: ["clsx", "cva", "tw", "twMerge", "classnames"],
        whitelist: ["btn-primary", "card", "container-narrow"],
      },
    },
  },
]
```

The rules that carry this module: `classnames-order` (the lint-side mirror of the sorter, hence
stable diffs), `no-custom-classname` (unknown names and typos, satisfied by `whitelist`),
`no-contradicting-classname` (`p-2 p-3`, `text-red-500 text-blue-500`), `enforces-shorthand`
(`mx-5 my-5` → `m-5`), and `callees`, without which the class helpers above are never scanned.

ALWAYS populate `whitelist` the same day you add the plugin, and NEVER silence `no-custom-classname`
project-wide instead: the rule is what catches `bg-bule-500`. Per-file disables are for third-party
class names that churn between library versions, nothing else.

Full option lists, rule tables, Headwind settings, parser setup, and CI wiring:
`references/01-tooling.md`.

## CI

```json
{
  "scripts": {
    "lint": "eslint . --max-warnings 0",
    "lint:fix": "eslint . --fix",
    "format": "prettier --write .",
    "format:check": "prettier --check ."
  }
}
```

ALWAYS run `--check` in CI, never `--write`/`--fix`. Auto-fixing in CI hides developer-side mistakes
and fills PR history with formatter commits; the fix belongs in a pre-commit hook (`lint-staged`).
`--max-warnings 0` turns class-order drift into a red build.

## Anti-patterns

The four that show up in every codebase fighting soup:

1. **Premature extraction** — 40 single-use `Button1`/`Card1` wrappers. Extract on the third copy.
2. **`@apply` everywhere** — `.btn-primary` in CSS next to a `<Button>` component. Pick one home.
3. **Class-order drift** — no sorter installed; diffs show reordering, merges conflict on class
   strings. Install Prettier on day one.
4. **Unconfigured `whitelist`** — `no-custom-classname` errors on every project class, the team
   disables the rule, and typos ship.

Symptom / cause / fix for all twenty, including the `no-arbitrary-value` trap, mixed class builders,
utility-named components, and premature tokens: `references/03-anti-patterns.md`.

## Procedure

1. Count the utilities. Under 15, stop.
2. Ask whether the markup is emitted from a loop. If yes, stop — no duplication exists.
3. Count the copies of the stack across the repo (`grep -rE 'class(Name)?="[^"]{200,}"' src/` finds
   the candidates; the 3-use rule decides them).
4. 1-2 copies: leave inline, group by concern if long, TODO if the duplication is intentional.
5. 3+ copies: route through the decision matrix — component, partial, or `@apply` in
   `@layer components`.
6. Name the extraction for intent (`Button`, `Modal`), never for its utilities.
7. Give the extracted component a `className` prop merged with `twMerge`, variants via props or
   `cva`; the consumer prop is the final argument.
8. Install the sorter and the linter, list your helpers in `tailwindFunctions`/`callees`, whitelist
   your custom classes, and enforce `--check` in CI.
9. Promote repeated raw values to tokens only after 3+ real usages — token scales belong to the
   `design-system` module (`../design-system/method.md`).

## Boundaries

| Owned elsewhere | What they own | Where |
|---|---|---|
| `config` | `@apply`, `@layer`, `@reference` semantics, the v4 CSS-first config surface | `../config/method.md` |
| `migration` | the v3→v4 breaking-change catalog, renamed classes, upgrade order | `../migration/method.md` |
| `design-system` | token scales, theme namespaces, where a value should be named | `../design-system/method.md` |
| `dynamic-classes` | classes built at runtime (`bg-${x}-500`) that never generate, `@source`/safelist fixes | `../dynamic-classes/method.md` |
| `validator` | the cross-module audit rules and the review/CI report | `../validator/method.md` |
| `styling` build level | the platform-neutral join / merge / variant-registry contract | `/styling` `build` method |

This module owns exactly one question: *does this long class list stay inline, and if not, where
does it go* — plus the formatter/linter wiring that keeps order stable either way.

## Resources

- `references/01-tooling.md` — Prettier options, ESLint rules and settings, Headwind, parsers, CI wiring, detection greps
- `references/02-refactor-examples.md` — worked refactors: leaf left inline, soup to component, to `cva`, to `@apply`, to partial
- `references/03-anti-patterns.md` — twenty named anti-patterns with symptom, cause, fix

## Sources

- https://tailwindcss.com/docs/styling-with-utility-classes
- https://tailwindcss.com/blog/automatic-class-sorting-with-prettier
- https://github.com/tailwindlabs/prettier-plugin-tailwindcss
- https://github.com/francoismassart/eslint-plugin-tailwindcss
- https://github.com/heybourn/headwind
- https://marketplace.visualstudio.com/items?itemName=heybourn.headwind
- https://github.com/dcastil/tailwind-merge
- https://github.com/lukeed/clsx
- https://cva.style/
