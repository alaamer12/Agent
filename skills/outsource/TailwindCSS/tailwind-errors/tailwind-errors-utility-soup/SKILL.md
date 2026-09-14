---
name: tailwind-errors-utility-soup
description: >
  Use when a Tailwind element has 20+ utility classes on one line,
  when reviewers complain about "utility soup", or when deciding
  between leaving utilities inline, extracting a component, or
  pulling utilities into @apply. Prevents the premature-extraction
  trap (extracting after one duplicate destroys readability and adds
  indirection), the never-extract trap (copy-pasting 30 utilities
  across 8 files), the @apply-everywhere trap (rebuilding the CSS
  framework you opted out of), the unsorted-class trap (random
  order produces noisy diffs and merge conflicts), and the
  whitelist-blocks-arbitrary trap (eslint-plugin-tailwindcss
  no-custom-classname rejects valid arbitrary-value classes
  without `whitelist`). Covers the 3-use rule (extract on the
  third copy, not the first), component vs @apply vs template
  partial decision, prettier-plugin-tailwindcss install + config
  (tailwindConfig for v3, tailwindStylesheet for v4,
  tailwindFunctions for clsx/cva/tw, tailwindAttributes for
  custom props), eslint-plugin-tailwindcss rules (classnames-order,
  no-custom-classname, no-contradicting-classname,
  enforces-shorthand, no-arbitrary-value), Headwind VS Code
  extension for editor-side sorting, and multi-line formatting
  conventions when a line legitimately needs many utilities.
  Keywords: tailwind utility soup, too many classes tailwind,
  long class list, 30 classes one line, when to extract
  tailwind component, when to use @apply, prettier
  tailwindcss plugin, prettier-plugin-tailwindcss config,
  tailwindStylesheet, tailwindConfig, tailwindFunctions,
  clsx cva tw sorting, eslint-plugin-tailwindcss,
  classnames-order, no-custom-classname, no-contradicting-classname,
  enforces-shorthand, p-2 p-3 conflict, mx-5 my-5 shorthand,
  headwind vscode tailwind sort, class order tailwind,
  diff noise tailwind, merge conflict tailwind classes,
  utility-first philosophy, refactor tailwind classes,
  tailwind classes are too long, my JSX is unreadable
  with tailwind, how to clean up tailwind classes,
  tailwind 3-4 tooling.
license: MIT
compatibility: "Designed for Claude Code. Requires Tailwind CSS v3.4 or v4.0+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# Utility Soup : Diagnosis and Refactor

"Utility soup" describes a Tailwind element with so many utility
classes that the line wraps multiple times and the reader cannot
parse it. It is a symptom, not always a bug. This skill teaches when
to leave it, when to extract, and how to keep order stable with
tooling.

ALWAYS apply the 3-use rule : extract on the THIRD copy of a pattern,
not the first. Premature extraction is worse than long class lists.

Companion skills :

- `tailwind-impl-apply-directive` : @apply + @layer semantics
- `tailwind-core-philosophy` : utility-first design principles
- `tailwind-impl-config-v4` : v4 CSS-first config surface

## Quick Reference

### The 3-use rule

| Copies of the pattern | Action |
| --------------------- | ------ |
| 1                     | Leave inline. |
| 2                     | Leave inline. Add a TODO comment if the duplication is intentional. |
| 3+                    | Extract a component (preferred) or @apply class (when no framework). |

### Decision matrix

```
Repeated 3+ times AND
├── Framework available (React, Vue, Svelte, Solid) : extract a component
├── Template language (Blade, ERB, Nunjucks, Twig)  : extract a partial
└── Plain HTML / MDX / third-party widget           : @apply in @layer components
```

### Tooling baseline

| Tool                            | Purpose |
| ------------------------------- | ------- |
| `prettier-plugin-tailwindcss`   | Sort class names on save (stable diffs). |
| `eslint-plugin-tailwindcss`     | Lint for duplicate / contradicting / unknown classes. |
| Headwind VS Code extension      | Sort inside the editor (alternative to Prettier). |

ALWAYS install at least Prettier sorting. NEVER ship a codebase where
class order is decided per author.

## Decision Trees

### Is my long class list actually a problem ?

```
Count the utility classes on the element.
├── < 15 utilities                      : not utility soup, move on
├── 15-25 utilities, single component   : acceptable for a leaf node
├── 25+ utilities                        : continue
2. Is the pattern repeated elsewhere ?
   ├── No  : it is a leaf component. Long is acceptable.
   │        Apply multi-line formatting (see Patterns).
   └── Yes : continue
3. How many copies exist ?
   ├── 1 or 2 : leave inline. Add a TODO if intentional duplication.
   └── 3+     : extract (see decision matrix).
```

### Component or @apply ?

```
Are you in a component framework (React, Vue, Svelte, Solid) ?
├── Yes : ALWAYS a component. Pass props for variants.
└── No  : continue
Are you in a template language (Blade, ERB, Twig, Nunjucks, Astro) ?
├── Yes : ALWAYS a partial / include / slot.
└── No  : continue
Are you in plain HTML, MDX, or overriding a third-party widget ?
├── Yes : @apply in @layer components is the right tool.
└── No  : revisit. The cases above cover ~99% of real codebases.
```

### Prettier vs ESLint vs Headwind ?

```
Goal ?
├── Stable class order across the team    : prettier-plugin-tailwindcss
├── Catch unknown / duplicate / contradicting class names : eslint-plugin-tailwindcss
├── Editor-side sorting without running Prettier : Headwind VS Code extension
```

These are NOT mutually exclusive. Use Prettier as the build-time
formatter and ESLint for class validation in CI. Headwind is a
developer-comfort tool that overlaps with Prettier ; pick one to
avoid conflicting sort orders.

## Patterns

### Pattern : multi-line formatting for legitimate long lists

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

ALWAYS group by concern (layout, sizing, spacing, color, state) on
each line. Prettier sorting reshuffles inside its own group order ; do
NOT fight it.

### Pattern : extracting a component (preferred)

Before (utility soup repeated 5 times) :

```tsx
<button className="inline-flex items-center rounded-md bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600">Save</button>
<button className="inline-flex items-center rounded-md bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600">Confirm</button>
<button className="inline-flex items-center rounded-md bg-gray-200 px-4 py-2 text-sm font-medium text-gray-900 hover:bg-gray-300">Cancel</button>
```

After :

```tsx
function Button({ variant = "primary", children }: { variant?: "primary" | "secondary", children: ReactNode }) {
  const base = "inline-flex items-center rounded-md px-4 py-2 text-sm font-medium"
  const variants = {
    primary: "bg-blue-500 text-white hover:bg-blue-600",
    secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300",
  }
  return <button className={`${base} ${variants[variant]}`}>{children}</button>
}

<Button>Save</Button>
<Button>Confirm</Button>
<Button variant="secondary">Cancel</Button>
```

### Pattern : @apply when no framework is available

`src/styles/components.css` (loaded once) :

```css
@layer components {
  .btn-primary {
    @apply inline-flex items-center rounded-md bg-blue-500 px-4 py-2
           text-sm font-medium text-white hover:bg-blue-600;
  }
  .btn-secondary {
    @apply inline-flex items-center rounded-md bg-gray-200 px-4 py-2
           text-sm font-medium text-gray-900 hover:bg-gray-300;
  }
}
```

```html
<button class="btn-primary">Save</button>
```

ALWAYS wrap in `@layer components` so utility overrides still win.
See `tailwind-impl-apply-directive` for full semantics.

### Pattern : Prettier sorting setup

Install :

```bash
npm install -D prettier prettier-plugin-tailwindcss
```

`.prettierrc.json` v3 :

```json
{
  "plugins": ["prettier-plugin-tailwindcss"],
  "tailwindConfig": "./tailwind.config.js",
  "tailwindFunctions": ["clsx", "cva", "tw", "twMerge"],
  "tailwindAttributes": ["myClassList"]
}
```

`.prettierrc.json` v4 :

```json
{
  "plugins": ["prettier-plugin-tailwindcss"],
  "tailwindStylesheet": "./src/app.css",
  "tailwindFunctions": ["clsx", "cva", "tw", "twMerge"]
}
```

ALWAYS list every class-building function in `tailwindFunctions` so
Prettier sees the classes inside `clsx("foo bar baz")`. NEVER rely on
Prettier auto-detecting these.

### Pattern : ESLint validation setup

Install :

```bash
npm install -D eslint eslint-plugin-tailwindcss
```

`eslint.config.js` (flat config, ESLint 9+) :

```js
import tailwind from "eslint-plugin-tailwindcss"

export default [
  ...tailwind.configs["flat/recommended"],
  {
    settings: {
      tailwindcss: {
        config: "./tailwind.config.js",   // v3
        // or for v4 :
        // cssFiles: ["./src/app.css"],
        callees: ["clsx", "cva", "tw", "classnames"],
        whitelist: ["btn-primary", "card", "container-narrow"],
      },
    },
  },
]
```

ALWAYS list custom class names in `whitelist`, otherwise
`no-custom-classname` flags them as unknown.

### Pattern : Class-building helper functions

```tsx
import clsx from "clsx"

function Card({ active, className }: { active: boolean, className?: string }) {
  return (
    <div className={clsx(
      "rounded border bg-white p-4 shadow",
      active && "border-blue-500 ring-2 ring-blue-500",
      className,
    )}>
      ...
    </div>
  )
}
```

Combine with `tailwind-merge` for safe override semantics when both
the component and the consumer pass overlapping utilities :

```tsx
import { twMerge } from "tailwind-merge"

className={twMerge("p-4 px-6", className)}
```

`twMerge` resolves `p-4 px-6` correctly (the later `px-6` wins for
horizontal padding while `p-4` survives for vertical).

## Anti-Patterns (summary)

NEVER extract after the first duplicate. The 3-use rule exists because
two duplicates is too small a sample to know the right abstraction.

NEVER reach for `@apply` when a component is available. `@apply` is
for non-framework contexts.

NEVER let class order drift. Install Prettier sorting on day one.

NEVER copy-paste 30 utilities across 5+ files. That is the extraction trigger.

NEVER add `eslint-plugin-tailwindcss` without configuring `whitelist`
for your custom class names. Day-one onboarding error.

See `references/anti-patterns.md` for the full catalog.

## Reference Links

- `references/methods.md` : Prettier plugin options, ESLint rules,
  Headwind config, helper-function patterns
- `references/examples.md` : end-to-end refactors from soup to
  component, soup to @apply, soup to partial
- `references/anti-patterns.md` : premature extraction, @apply abuse,
  Prettier vs Headwind conflict, ESLint whitelist mistakes

## Sources

- Tailwind extraction guidance : https://tailwindcss.com/docs/styling-with-utility-classes
- prettier-plugin-tailwindcss : https://github.com/tailwindlabs/prettier-plugin-tailwindcss
- eslint-plugin-tailwindcss : https://github.com/francoismassart/eslint-plugin-tailwindcss
- Headwind extension : https://github.com/heybourn/headwind
- tailwind-merge : https://github.com/dcastil/tailwind-merge
- clsx : https://github.com/lukeed/clsx
