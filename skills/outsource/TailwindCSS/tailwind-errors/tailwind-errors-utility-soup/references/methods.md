# Reference : Tooling and Refactor Methods

Exhaustive reference for Prettier plugin, ESLint plugin, Headwind, and
class-merging helpers.

## prettier-plugin-tailwindcss

### Install

```bash
npm install -D prettier prettier-plugin-tailwindcss
```

Requirements :

- Prettier v3+
- Tailwind CSS v3.0+
- ESM-only (cannot `require()`)

### Minimal config

`.prettierrc.json` :

```json
{
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

The plugin auto-discovers `tailwind.config.js` next to the Prettier
config. For non-default locations or v4, configure explicitly.

### v3-specific options

```json
{
  "plugins": ["prettier-plugin-tailwindcss"],
  "tailwindConfig": "./styles/tailwind.config.js"
}
```

`tailwindConfig` MUST point at the actual config file. If you split
configs by environment, use the build-time canonical one.

### v4-specific options

```json
{
  "plugins": ["prettier-plugin-tailwindcss"],
  "tailwindStylesheet": "./resources/css/app.css"
}
```

`tailwindStylesheet` MUST point at the entry CSS containing `@import "tailwindcss"`,
`@theme`, `@utility`, and `@source` directives. Without it, the
plugin cannot resolve custom tokens defined in your CSS.

### tailwindFunctions

Sorts class names inside function calls and tagged template literals :

```json
{ "tailwindFunctions": ["clsx", "cva", "tw", "twMerge", "classnames"] }
```

The plugin recognizes these patterns :

```ts
clsx("flex items-center gap-2")
cva("rounded px-4", { variants: { ... } })
tw`flex items-center gap-2`
twMerge("p-4 px-6")
classnames("flex", { hidden: condition })
```

ALWAYS list EVERY class-building wrapper you use. The plugin does NOT
auto-detect ; unknown wrappers leave their class strings unsorted.

### tailwindAttributes

Sorts class names inside HTML/JSX/Vue attributes other than `class`
and `className` :

```json
{ "tailwindAttributes": ["myClassList", "/data-class.*/"] }
```

The `/regex/` syntax allows pattern matching. Useful for design-system
prop names like `tw`, `wrapperClass`, `containerClass`.

### tailwindPreserveWhitespace / tailwindPreserveDuplicates

Both default to `false`. Setting them to `true` keeps original
whitespace / duplicates in the input. Almost no project should
override these ; if you want unsorted classes, do not install the
plugin.

### Sort order

The plugin sorts utilities in the order they appear in the generated
stylesheet. This means :

1. Layout primitives (`flex`, `grid`, `block`).
2. Box-model (`m-*`, `p-*`).
3. Sizing (`w-*`, `h-*`).
4. Typography (`text-*`, `font-*`).
5. Visual (`bg-*`, `border-*`).
6. State variants (`hover:*`, `focus:*`) AFTER their base utility.
7. Responsive variants (`sm:*`, `md:*`) AFTER mobile-first base.

The exact order is what Tailwind itself emits ; following it makes
class order match cascade order.

## eslint-plugin-tailwindcss

### Install

```bash
npm install -D eslint eslint-plugin-tailwindcss
```

### Legacy config (`.eslintrc`)

```js
module.exports = {
  root: true,
  extends: ["plugin:tailwindcss/recommended"],
}
```

### Flat config (ESLint 9+)

```js
import tailwind from "eslint-plugin-tailwindcss"

export default [
  ...tailwind.configs["flat/recommended"],
]
```

### Settings

```js
{
  settings: {
    tailwindcss: {
      callees: ["clsx", "cva", "tw", "twMerge", "classnames"],
      config: "./tailwind.config.js",
      cssFiles: [
        "**/*.css",
        "!**/node_modules",
        "!**/.*",
        "!**/dist",
        "!**/build",
      ],
      cssFilesRefreshRate: 5000,
      removeDuplicates: true,
      skipClassAttribute: false,
      whitelist: ["btn-primary", "card", "container-narrow"],
      tags: ["tw", "css"],
      classRegex: "^class(Name)?$",
    },
  },
}
```

| Setting              | Purpose |
| -------------------- | ------- |
| `callees`            | Function names whose first arg is a class string. |
| `config`             | v3 config path. |
| `cssFiles`           | v4 CSS files containing `@theme`, `@utility`, custom classes. |
| `cssFilesRefreshRate`| Cache TTL in ms for cssFiles scanning. |
| `removeDuplicates`   | Strip duplicate classnames automatically. |
| `whitelist`          | Custom class names that pass `no-custom-classname`. |
| `tags`               | Tagged template literal names. |
| `classRegex`         | Regex for attribute names that hold classes. |

### Rules

| Rule                          | Default | Purpose |
| ----------------------------- | ------- | ------- |
| `classnames-order`            | warn    | Sort classes for stable diffs. |
| `no-custom-classname`         | warn    | Forbid unknown classes (not Tailwind utility, not whitelisted). |
| `no-contradicting-classname`  | error   | Catch `p-2 p-3`, `text-red-500 text-blue-500`. |
| `enforces-shorthand`          | warn    | Merge `mx-5 my-5` to `m-5`. |
| `no-arbitrary-value`          | off     | Reject `text-[14px]`, `h-[42vh]`. Strict design-system mode. |
| `enforces-negative-arbitrary-values` | warn | Catch invalid negative arbitrary values. |
| `migration-from-tailwind-2`   | warn    | Auto-fix v2 → v3 class renames. |
| `classnames-on-multiple-lines`| off     | Force multi-line formatting at a threshold. |

### Disabling rules per-file

```js
/* eslint-disable tailwindcss/no-custom-classname */
```

ALWAYS prefer adding to `whitelist` over disabling rules per file.

## Headwind (VS Code extension)

### Install

VS Code Marketplace : "Headwind" by Ryan Olson.

### Settings (`.vscode/settings.json`)

```json
{
  "headwind.runOnSave": true,
  "headwind.classRegex": {
    "html": "\\bclass\\s*=\\s*[\\\"\\'`]([_a-zA-Z0-9\\s\\-:/]+)[\\\"\\'`]",
    "javascript": "(?:\\bclass(?:Name)?\\s*=\\s*[\"'`]([_a-zA-Z0-9\\s\\-:\\/]+)[\"'`])"
  }
}
```

### Conflict with Prettier

Headwind and Prettier sort independently and may produce different
orders. ALWAYS disable one : if Prettier runs on save, set
`headwind.runOnSave` to false.

## clsx / classnames / cva / tailwind-merge

### clsx

Conditional class string builder :

```ts
import clsx from "clsx"

clsx("flex", isActive && "bg-blue-500", { hidden: !visible })
```

Returns a space-joined string. NEVER use for override semantics.

### classnames

Same shape as clsx, older API, same behavior in practice. Pick one
per project, NEVER mix.

### cva (class-variance-authority)

Variant-aware class composition :

```ts
import { cva } from "class-variance-authority"

const button = cva("rounded px-4 py-2", {
  variants: {
    intent: {
      primary: "bg-blue-500 text-white",
      secondary: "bg-gray-200 text-gray-900",
    },
    size: {
      sm: "text-sm",
      md: "text-base",
    },
  },
  defaultVariants: { intent: "primary", size: "md" },
})

<button className={button({ intent: "secondary" })}>Cancel</button>
```

### tailwind-merge

Resolves conflicting utilities :

```ts
import { twMerge } from "tailwind-merge"

twMerge("p-4 px-6")           // "py-4 px-6" semantically
twMerge("text-red-500", "text-blue-500")  // "text-blue-500"
```

ALWAYS use `twMerge` when a component accepts a `className` prop and
needs to let the caller override its defaults.

## Multi-line formatting conventions

When a class list is unavoidably long, multi-line template literals
keep diffs reviewable :

```tsx
className="
  inline-flex items-center justify-center
  rounded-md px-4 py-2
  text-sm font-medium
  bg-blue-500 text-white
  hover:bg-blue-600 focus:ring-2 focus:ring-blue-500
"
```

NEVER use this format for class strings under ~15 utilities ; it adds
visual weight without clarity gain.

Prettier respects the multi-line shape but still sorts INSIDE its own
preferred order. Group manually if you want a specific layout.

## CI integration

`package.json` :

```json
{
  "scripts": {
    "lint": "eslint .",
    "lint:fix": "eslint . --fix",
    "format": "prettier --write .",
    "format:check": "prettier --check ."
  }
}
```

CI workflow :

```yaml
- run: npm install
- run: npm run lint
- run: npm run format:check
```

ALWAYS run `format:check`, not `format --write`, in CI. Auto-fixing
in CI hides developer-side mistakes.
