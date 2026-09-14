# Reference : Refactor Examples

End-to-end refactors from utility soup to component, partial, or @apply.

---

## Example 1 : 35-utility leaf button (leave inline)

```tsx
<button className="
  inline-flex items-center justify-center gap-2
  rounded-lg px-4 py-2
  text-sm font-semibold
  bg-blue-600 text-white shadow-sm
  hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
  disabled:opacity-50 disabled:cursor-not-allowed
  transition
">
  Save changes
</button>
```

This button appears ONCE in the codebase. Long is acceptable. Apply
multi-line formatting and move on.

---

## Example 2 : 3-use refactor to React component

Before :

```tsx
// page1.tsx
<button className="inline-flex items-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">Save</button>

// page2.tsx
<button className="inline-flex items-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">Confirm</button>

// page3.tsx
<button className="inline-flex items-center rounded-lg bg-gray-200 px-4 py-2 text-sm font-semibold text-gray-900 hover:bg-gray-300">Cancel</button>
```

After :

```tsx
// components/Button.tsx
import { ReactNode } from "react"
import clsx from "clsx"

type Variant = "primary" | "secondary"

export function Button({
  variant = "primary",
  children,
  className,
}: {
  variant?: Variant
  children: ReactNode
  className?: string
}) {
  const base = "inline-flex items-center rounded-lg px-4 py-2 text-sm font-semibold"
  const variants: Record<Variant, string> = {
    primary: "bg-blue-600 text-white hover:bg-blue-700",
    secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300",
  }
  return <button className={clsx(base, variants[variant], className)}>{children}</button>
}
```

```tsx
<Button>Save</Button>
<Button>Confirm</Button>
<Button variant="secondary">Cancel</Button>
```

---

## Example 3 : 3-use refactor with cva

```tsx
import { cva, type VariantProps } from "class-variance-authority"

const button = cva(
  "inline-flex items-center rounded-lg px-4 py-2 text-sm font-semibold transition",
  {
    variants: {
      variant: {
        primary: "bg-blue-600 text-white hover:bg-blue-700",
        secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300",
        danger: "bg-red-600 text-white hover:bg-red-700",
      },
      size: {
        sm: "text-xs px-3 py-1",
        md: "text-sm px-4 py-2",
        lg: "text-base px-5 py-3",
      },
    },
    defaultVariants: { variant: "primary", size: "md" },
  }
)

type ButtonProps = VariantProps<typeof button> & {
  children: React.ReactNode
}

export function Button({ variant, size, children }: ButtonProps) {
  return <button className={button({ variant, size })}>{children}</button>
}
```

cva is the right tool when the variant matrix expands beyond
2 dimensions.

---

## Example 4 : @apply refactor for plain HTML

`src/styles/components.css` :

```css
@layer components {
  .btn {
    @apply inline-flex items-center rounded-lg px-4 py-2 text-sm font-semibold transition;
  }
  .btn-primary {
    @apply inline-flex items-center rounded-lg px-4 py-2 text-sm font-semibold transition
           bg-blue-600 text-white hover:bg-blue-700;
  }
  .btn-secondary {
    @apply inline-flex items-center rounded-lg px-4 py-2 text-sm font-semibold transition
           bg-gray-200 text-gray-900 hover:bg-gray-300;
  }
}
```

```html
<button class="btn-primary">Save</button>
<button class="btn-secondary">Cancel</button>
```

Use only when no component framework is available. The full utility
list is repeated per variant because `@apply .btn` is NOT supported
inside @apply.

---

## Example 5 : Template partial refactor (Blade, Nunjucks, ERB)

`views/_button.blade.php` :

```blade
@props(['variant' => 'primary'])

@php
$classes = [
  'primary' => 'bg-blue-600 text-white hover:bg-blue-700',
  'secondary' => 'bg-gray-200 text-gray-900 hover:bg-gray-300',
][$variant];
@endphp

<button {{ $attributes->merge(['class' => "inline-flex items-center rounded-lg px-4 py-2 text-sm font-semibold $classes"]) }}>
  {{ $slot }}
</button>
```

```blade
<x-button>Save</x-button>
<x-button variant="secondary">Cancel</x-button>
```

---

## Example 6 : Prettier setup for v4 + clsx + cva

`.prettierrc.json` :

```json
{
  "plugins": ["prettier-plugin-tailwindcss"],
  "tailwindStylesheet": "./src/app.css",
  "tailwindFunctions": ["clsx", "cva", "twMerge"],
  "tailwindAttributes": ["containerClass", "wrapperClass"]
}
```

After running `npx prettier --write src/`, all class strings inside
`clsx(...)`, `cva(...)`, `twMerge(...)`, and the listed attributes
are sorted in the canonical Tailwind order.

---

## Example 7 : ESLint validation for a design system

`eslint.config.js` :

```js
import tailwind from "eslint-plugin-tailwindcss"

export default [
  ...tailwind.configs["flat/recommended"],
  {
    settings: {
      tailwindcss: {
        callees: ["clsx", "cva", "twMerge", "classnames"],
        config: "./tailwind.config.ts",
        whitelist: [
          "btn-primary",
          "btn-secondary",
          "card",
          "card-header",
          "card-body",
          "container-narrow",
          "container-wide",
        ],
      },
    },
    rules: {
      "tailwindcss/no-custom-classname": "error",
      "tailwindcss/no-contradicting-classname": "error",
      "tailwindcss/enforces-shorthand": "warn",
      "tailwindcss/no-arbitrary-value": "off",
    },
  },
]
```

This config catches `p-2 p-3`, `mx-5 my-5` → `m-5`, and unknown
class names while allowing the seven custom design-system classes.

---

## Example 8 : Component with className override via twMerge

```tsx
import { twMerge } from "tailwind-merge"

export function Card({ className, children }: { className?: string, children: React.ReactNode }) {
  return (
    <div className={twMerge("rounded-lg border bg-white p-4 shadow-sm", className)}>
      {children}
    </div>
  )
}
```

Usage that overrides padding without breaking other defaults :

```tsx
<Card className="p-8">  {/* p-8 wins, rounded-lg + border + bg-white + shadow-sm survive */}
  ...
</Card>
```

ALWAYS use `twMerge` for components that accept a `className` prop. A
naive `${className} ${baseClasses}` produces `p-4 p-8` and lets the
cascade decide ; that is fragile across utility variants.

---

## Example 9 : Headwind config (alternative to Prettier)

`.vscode/settings.json` :

```json
{
  "headwind.runOnSave": true,
  "headwind.classRegex": {
    "html": "\\bclass\\s*=\\s*[\\\"\\'`]([_a-zA-Z0-9\\s\\-:/]+)[\\\"\\'`]",
    "javascript": "(?:\\bclass(?:Name)?\\s*=\\s*[\"'`]([_a-zA-Z0-9\\s\\-:\\/]+)[\"'`])",
    "javascriptreact": "(?:\\bclass(?:Name)?\\s*=\\s*[\"'`]([_a-zA-Z0-9\\s\\-:\\/]+)[\"'`])"
  }
}
```

If using Headwind, disable Prettier's Tailwind plugin to avoid
conflicting sort orders.

---

## Example 10 : Refactoring a 50-utility wrapper div

Before :

```tsx
<div className="
  fixed inset-0 z-50 flex items-center justify-center
  bg-black/50 backdrop-blur-sm
  p-4
">
  <div className="
    relative w-full max-w-md
    rounded-xl bg-white shadow-xl
    p-6
    transform transition-all
    data-[state=open]:scale-100 data-[state=closed]:scale-95
    data-[state=open]:opacity-100 data-[state=closed]:opacity-0
  ">
    {children}
  </div>
</div>
```

Identify the pattern : this is a modal wrapper used by every dialog
in the app. Extract :

```tsx
export function Modal({ open, children }: { open: boolean, children: React.ReactNode }) {
  return (
    <div
      data-state={open ? "open" : "closed"}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
    >
      <div className="
        relative w-full max-w-md rounded-xl bg-white shadow-xl p-6
        transform transition-all
        data-[state=open]:scale-100 data-[state=closed]:scale-95
        data-[state=open]:opacity-100 data-[state=closed]:opacity-0
      ">
        {children}
      </div>
    </div>
  )
}
```

```tsx
<Modal open={isOpen}>...</Modal>
```

---

## Example 11 : `package.json` scripts for CI

```json
{
  "scripts": {
    "lint": "eslint . --max-warnings 0",
    "format": "prettier --write .",
    "format:check": "prettier --check ."
  },
  "lint-staged": {
    "*.{ts,tsx,js,jsx,vue,svelte,astro,html,css}": [
      "prettier --write",
      "eslint --fix"
    ]
  }
}
```

`--max-warnings 0` makes any class-order warning fail CI. ALWAYS
combine with a husky pre-commit hook for `lint-staged`.

---

## Example 12 : Detecting utility soup with grep

A rough heuristic to find candidates :

```bash
grep -rE 'class(Name)?="[^"]{200,}"' src/
```

Lines with class strings longer than 200 characters are utility-soup
candidates. Manually review each : leaf component, or extraction candidate ?

```bash
grep -rE 'className="[^"]{300,}"' src/ | wc -l
```

If the count is non-zero, run the 3-use check.

---

## Example 13 : Disable specific ESLint rule per file

```tsx
/* eslint-disable tailwindcss/no-custom-classname */
import "swiper/css"
import "swiper/css/navigation"

<div className="swiper-container swiper-button-prev">...</div>
```

Use only for third-party class names that change between versions and
are not stable enough to whitelist project-wide.
