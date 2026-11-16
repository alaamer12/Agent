# Refactor examples — soup to component, partial, or `@apply`

Each example states the measurement first (utility count, copy count), then the move. Tooling-only
config (Headwind settings, CI scripts, detection greps) is in `01-tooling.md`, not repeated here.

## 1. Long leaf, one use — leave it

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

~30 utilities, ONE use in the codebase. Long is acceptable for a leaf: group by concern, let the
sorter keep the order, move on. Wrapping this in a `<SaveButton>` to feel tidy removes nothing but
indirection.

## 2. Repetition inside a loop — not duplication at all

```tsx
{contributors.map((user) => (
  <img key={user.id} class="inline-block size-12 shrink-0 rounded-full ring-2 ring-white" src={user.avatarUrl} alt="" />
))}
```

Five rendered copies, one authored class list. There is no extraction to do; the same stack
duplicated across three different files WOULD be a different answer.

## 3. Three copies → component (the default move)

Before, one stack in three files:

```tsx
// page1.tsx
<button className="inline-flex items-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">Save</button>
// page2.tsx
<button className="inline-flex items-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">Confirm</button>
// page3.tsx
<button className="inline-flex items-center rounded-lg bg-gray-200 px-4 py-2 text-sm font-semibold text-gray-900 hover:bg-gray-300">Cancel</button>
```

After:

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

The shared shape is what survived; the coincidental parts (label, colour of one instance) stayed at
the call site. If a consumer must override a utility the base sets, swap `clsx` for `twMerge(clsx(...))`
— example 7.

## 4. Variant matrix grows → cva

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
  },
)

type ButtonProps = VariantProps<typeof button> & { children: React.ReactNode }

export function Button({ variant, size, children }: ButtonProps) {
  return <button className={button({ variant, size })}>{children}</button>
}
```

`cva` earns its place when the matrix exceeds two dimensions: the variants become typed data, the
component's style API is one declaration, and call sites pass intent. Below that, example 3's plain
map is enough.

## 5. No framework → `@apply` in `@layer components`

`src/styles/components.css`, loaded once:

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

Only for markup you cannot turn into a component: plain HTML, MDX, a CMS template, a third-party
widget. The base list is repeated per variant because `@apply` cannot pull in another component
class. Whether a rule belongs in `components` or `utilities`, how layers interact with the cascade,
and the scoped-CSS traps are the `config` module's — see `../../config/method.md`.

## 6. Template language → partial

`views/components/button.blade.php`:

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

Same shape as the framework answer — base string plus a lookup — with the language's own prop and
attribute-merge mechanics. ERB/Twig/Nunjucks partials work identically with their own local
variable syntax. Watch Prettier's duplicate removal in these files; if template expressions collide
with it, set `tailwindPreserveDuplicates` (`01-tooling.md`).

## 7. Consumer overrides → twMerge, not a longer class list

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

```tsx
<Card className="p-8">   {/* p-8 wins; rounded-lg, border, bg-white, shadow-sm survive */}
  ...
</Card>
```

The naive version, `` className={`p-4 ${className}`} ``, produces `p-4 p-8` and lets the generated
stylesheet decide — fragile, and it breaks the moment bundling order changes. ALWAYS give extracted
components a `className` prop and merge it with `twMerge`.

## 8. A 50-utility modal pair → one component

Before, pasted around every dialog:

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

The stack encodes a modal wrapper, and the `data-[state=*]` pairs are one component's open/closed
contract, not decoration. Extract, and let the state live on the element:

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

The long inner list stays long — it is now authored once, and the call site reads as a name. That is
the win; shrinking the string was never the goal.

## 9. Prettier, v4 + clsx + cva

`.prettierrc.json`:

```json
{
  "plugins": ["prettier-plugin-tailwindcss"],
  "tailwindStylesheet": "./src/app.css",
  "tailwindFunctions": ["clsx", "cva", "twMerge"],
  "tailwindAttributes": ["containerClass", "wrapperClass"]
}
```

`npx prettier --write src/` then sorts every class string in attributes, in those calls, and inside
the listed design-system attributes. Run the one-off normalisation commit alone, never mixed into a
feature branch: otherwise every file in the diff looks touched.

## 10. ESLint for a design system with custom classes

`eslint.config.js`:

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

Catches `p-2 p-3`, suggests `mx-5 my-5` → `m-5`, and rejects unknown names, while the seven
`@layer components` classes pass. Every new component class is added to `whitelist` in the same
commit that defines it — the day the list drifts, the team starts disabling the rule.

## 11. Third-party widget classes

```tsx
/* eslint-disable tailwindcss/no-custom-classname */
import "swiper/css"
import "swiper/css/navigation"

<div className="swiper-container swiper-button-prev">...</div>
```

The one honest per-file disable: class names owned by a library, which change between its versions
and are not stable enough to whitelist project-wide.
