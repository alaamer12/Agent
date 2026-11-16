# Tooling reference — sorters, linters, class builders

Everything the method page needs but should not carry: full option lists, rule tables, editor
config, CI wiring, and how to find the soup candidates in the first place.

## prettier-plugin-tailwindcss

The canonical sorter. It reorders class strings so the order matches the generated stylesheet, which
makes diffs stable and merge conflicts on class strings rare.

### Install and requirements

```bash
npm install -D prettier prettier-plugin-tailwindcss
```

- Prettier v3 or newer (as of plugin v0.5.x).
- Tailwind CSS v3.0 or newer.
- ESM-only: it cannot be loaded with `require()`.
- When several Prettier plugins are installed, `prettier-plugin-tailwindcss` MUST come **last** in
  the `plugins` array — it uses a Prettier API only one plugin may hold.

### Minimal config

`.prettierrc.json`:

```json
{
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

With no path options the plugin looks for `tailwind.config.js` next to the Prettier config and falls
back to Tailwind's defaults when it finds nothing — which silently means "your custom tokens are
sorted as unknown classes". Configure the path explicitly whenever the project is non-default or on
v4.

### v3: `tailwindConfig`

```json
{
  "plugins": ["prettier-plugin-tailwindcss"],
  "tailwindConfig": "./styles/tailwind.config.js"
}
```

MUST point at the real config file. Paths resolve relative to the Prettier config. If configs are
split per environment, use the build-time canonical one.

### v4: `tailwindStylesheet`

```json
{
  "plugins": ["prettier-plugin-tailwindcss"],
  "tailwindStylesheet": "./resources/css/app.css"
}
```

MUST point at the CSS entry sheet — the file holding `@import "tailwindcss"`, `@theme`, `@utility`,
and `@source`. Without it the plugin cannot resolve tokens defined in CSS. The v4 config surface
itself belongs to the `config` module (`../../config/method.md`); only the option name matters here.

### `tailwindFunctions`

Sorts class strings inside function calls and tagged template literals:

```json
{ "tailwindFunctions": ["clsx", "cva", "tw", "twMerge", "classnames"] }
```

Recognised shapes:

```ts
clsx("flex items-center gap-2")
cva("rounded px-4", { variants: { /* ... */ } })
tw`flex items-center gap-2`
twMerge("p-4 px-6")
classnames("flex", { hidden: condition })
```

ALWAYS list EVERY class-building wrapper the project uses; there is no auto-detection, and an
unlisted wrapper leaves its strings unsorted forever. Regex patterns in slashes are accepted
(`"/^use.*Class$/"`) for teams with a naming convention instead of a fixed list.

### `tailwindAttributes`

Sorts attributes other than `class` / `className` (and framework equivalents such as `:class`,
`[ngClass]`, and Tailwind `@apply` directives, which are handled by default):

```json
{ "tailwindAttributes": ["myClassList", "/data-class.*/"] }
```

Useful for design-system prop names like `wrapperClass`, `containerClass`, `tw`.

### `tailwindPreserveWhitespace` / `tailwindPreserveDuplicates`

Both default to `false`: extra whitespace is collapsed and duplicate class names are removed.
Almost no project should set `tailwindPreserveWhitespace` — if you want unsorted classes, do not
install the plugin. `tailwindPreserveDuplicates: true` is a real escape hatch for templating
languages where classes cannot be distinguished from template syntax (Blade, Shopify Liquid/Fluid):

```html
<div class="
  {f:if(condition: isCompact, then: 'grid-cols-3', else: 'grid-cols-5')}
  grid gap-4 p-4
"></div>
```

If duplicate removal breaks such a template, turn the option on rather than excluding the folder
from formatting.

### Sort order

Utilities sort in the order they appear in the generated stylesheet, i.e. cascade order:

1. Layout primitives (`flex`, `grid`, `block`).
2. Box model (`m-*`, `p-*`).
3. Sizing (`w-*`, `h-*`).
4. Typography (`text-*`, `font-*`).
5. Visual (`bg-*`, `border-*`).
6. State variants (`hover:*`, `focus:*`) after their base utility.
7. Responsive variants (`sm:*`, `md:*`) after the mobile-first base.

NEVER hand-order to a personal preference; following the emitted order is what makes the class list
predictable. Multi-line strings keep their line structure but are sorted inside it — group by
concern, then let the tool settle each line.

## eslint-plugin-tailwindcss

The validator. It does not replace the sorter; it catches names that do not exist, duplicated
tokens, and contradictions the formatter happily keeps.

### Install

```bash
npm install -D eslint eslint-plugin-tailwindcss
```

### Legacy config (`.eslintrc`, ESLint < v9)

```js
module.exports = {
  root: true,
  extends: ["plugin:tailwindcss/recommended"],
}
```

### Flat config (ESLint 9+)

```js
import tailwind from "eslint-plugin-tailwindcss"

export default [...tailwind.configs["flat/recommended"]]
```

### Parsers — the silent day-one failure

The plugin ships no parsers. Without them the rules never see the file and report nothing:

| Files | Needs |
|---|---|
| `.ts` / `.tsx` / `.js` / `.jsx` | `@typescript-eslint/parser` (flat: `typescript-eslint`) |
| `.vue` | `vue-eslint-parser` (`eslint-plugin-vue`) |
| `.html`, `.blade.php` | `@angular-eslint/template-parser` |

```js
import ts from "typescript-eslint"
import tailwind from "eslint-plugin-tailwindcss"

export default [
  ...ts.configs.recommended,
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
      cssFiles: ["**/*.css", "!**/node_modules", "!**/.*", "!**/dist", "!**/build"],
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

| Setting | Purpose | Default |
|---|---|---|
| `callees` | Function names whose argument is a class string | `["classnames", "clsx", "ctl"]` |
| `config` | v3 JS config path | `tailwind.config.js` |
| `cssFiles` | v4 CSS files scanned for `@theme` / `@utility` / custom classes | `**/*.css` minus vendor/build dirs |
| `cssFilesRefreshRate` | Cache TTL (ms) for the `cssFiles` scan | `5000` |
| `removeDuplicates` | Strip duplicate classnames on `--fix` | `true` |
| `skipClassAttribute` | Ignore the `class` attribute itself | `false` |
| `whitelist` | Custom class names allowed by `no-custom-classname` | `[]` |
| `tags` | Tagged template literal names to inspect | `[]` |
| `classRegex` | Which attribute names hold class lists | `^class(Name)?$` |

`callees` defaults to `["classnames", "clsx", "ctl"]` — `cva`, `twMerge`, and any local `cn` helper
MUST be added or their contents go unchecked, exactly like `tailwindFunctions` on the Prettier side.

### Rules

| Rule | Catches |
|---|---|
| `classnames-order` | Unsorted classes — the lint-side mirror of the Prettier sort (stable diffs, fewer conflicts). |
| `no-custom-classname` | Names that are neither a Tailwind utility nor whitelisted: typos (`bg-bule-500`), dead classes. |
| `no-contradicting-classname` | `p-2 p-3`, `text-red-500 text-blue-500` — same property, same variant, two values. |
| `enforces-shorthand` | `mx-5 my-5` where `m-5` says it once. |
| `enforces-negative-arbitrary-values` | The wrong negative form: `top-[-5px]` where `-top-[5px]` is meant. |
| `no-unnecessary-arbitrary-value` | `m-[1.25rem]` where the scale has `m-5`. |
| `no-arbitrary-value` | Every `text-[14px]`, `h-[42vh]`. Strict design-system enforcement. |
| `migration-from-tailwind-2` | Renamed v2 classes with an autofix; a v2→v3 step, not a v3→v4 one. |

`recommended` severity: `no-contradicting-classname` is an error; `classnames-order`,
`no-custom-classname`, `enforces-shorthand` are warnings; `no-arbitrary-value` is **off**. Run with
`--max-warnings 0` if warnings should fail the build.

```js
rules: {
  "tailwindcss/no-custom-classname": "error",
  "tailwindcss/no-contradicting-classname": "error",
  "tailwindcss/enforces-shorthand": "warn",
  "tailwindcss/no-arbitrary-value": "off",
}
```

Keep `no-arbitrary-value` off until the design system is mature AND every exception goes through a
review; a strict setting that the team disables per file enforces nothing.

### Tailwind v4 support

v4 support in this plugin is partial and evolving (`eslint-plugin-tailwindcss@beta`, built on
`tailwind-api-utils`); expect false positives, notably from `no-contradicting-classname`. Configure
`cssFiles` instead of `config` on v4. Do not chase version differences here — the breaking-change
catalog is the `migration` module's (`../../migration/method.md`).

### Per-file disables

```js
/* eslint-disable tailwindcss/no-custom-classname */
import "swiper/css"
import "swiper/css/navigation"

<div className="swiper-container swiper-button-prev">...</div>
```

ALWAYS prefer `whitelist` over a per-file disable. Reserve disables for third-party class names that
change between library versions and are not stable enough to whitelist project-wide. NEVER disable a
rule repo-wide to silence noise — that removes the typos along with the false positives.

## Headwind (editor-side alternative)

An opinionated VS Code class sorter: sorting runs in the editor, no formatter in the build.

- Install "Headwind" from the marketplace (`heybourn/headwind`). A JetBrains port exists
  (`Tailwind Formatter`).
- Runs on save only when a `tailwind.config.js` is present in the working directory.
- Manual commands: `Sort Tailwind CSS Classes` (file) and `... on Entire Workspace`, or
  `Ctrl+Alt+T` (`Alt+Shift+T` on macOS).
- Unknown classes and breakpoints are moved to the end of the list; duplicates are removed.
- Its default order ships in the extension's `package.json` (`headwind.defaultSortOrder`) — it is
  the extension's own order, not necessarily the Prettier plugin's. That is precisely why the two
  must not both run.

`.vscode/settings.json`:

```json
{
  "headwind.runOnSave": true,
  "headwind.removeDuplicates": true,
  "headwind.prependCustomClasses": false,
  "headwind.classRegex": {
    "html": "\\bclass\\s*=\\s*[\\\"\\'`]([_a-zA-Z0-9\\s\\-:/]+)[\\\"\\'`]",
    "javascript": "(?:\\bclass(?:Name)?\\s*=\\s*[\"'`]([_a-zA-Z0-9\\s\\-:\\/]+)[\"'`])",
    "javascriptreact": "(?:\\bclass(?:Name)?\\s*=\\s*[\"'`]([_a-zA-Z0-9\\s\\-:\\/]+)[\"'`])"
  }
}
```

`headwind.classRegex` takes an array for multi-step matching and an object form
(`{ "regex", "separator", "replacement" }`) for languages that separate classes with something
other than whitespace. Changes to these JSON options may need `Developer: Reload Window`.

Prettier OR Headwind, never both:

```json
{ "headwind.runOnSave": false }
```

## Class builders

### clsx

```ts
import clsx from "clsx"

clsx("flex", isActive && "bg-blue-500", { hidden: !visible })
```

Joins truthy parts into one space-separated string. NEVER use it for override semantics — it cannot
resolve a conflict, it only orders the string.

### classnames

Same shape and behaviour as `clsx`, older API. Pick one per project; NEVER mix the two in one
codebase (a split convention is how half the repo ends up unsorted, since only the named one is in
`tailwindFunctions`/`callees`).

### class-variance-authority (cva)

```ts
import { cva } from "class-variance-authority"

const button = cva("rounded px-4 py-2", {
  variants: {
    intent: { primary: "bg-blue-500 text-white", secondary: "bg-gray-200 text-gray-900" },
    size: { sm: "text-sm", md: "text-base" },
  },
  defaultVariants: { intent: "primary", size: "md" },
})

<button className={button({ intent: "secondary" })}>Cancel</button>
```

The variant matrix as data: exhaustive, typed, greppable. Right tool once variants exceed two
dimensions.

### tailwind-merge

```ts
import { twMerge } from "tailwind-merge"

twMerge("p-4 px-6")                     // -> "py-4 px-6"
twMerge("text-red-500", "text-blue-500") // -> "text-blue-500"
```

Resolves conflicts by property family, last one wins. ALWAYS use it where a component accepts a
`className` prop and must let the caller override its defaults. The two are commonly composed into a
local `cn` helper (`twMerge(clsx(...))`) — if you do, add `cn` to `tailwindFunctions` and `callees`.

## Multi-line formatting conventions

For an unavoidably long list, a multi-line string keeps diffs reviewable:

```tsx
className="
  inline-flex items-center justify-center
  rounded-md px-4 py-2
  text-sm font-medium
  bg-blue-500 text-white
  hover:bg-blue-600 focus:ring-2 focus:ring-blue-500
"
```

NEVER for lists under ~15 utilities: added visual weight, no clarity gain. NEVER as a substitute for
extraction: if the same block is wrapped identically in four files, the answer is a component, not
more lines.

## CI integration

`package.json`:

```json
{
  "scripts": {
    "lint": "eslint . --max-warnings 0",
    "lint:fix": "eslint . --fix",
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

Workflow:

```yaml
- run: npm install
- run: npm run lint
- run: npm run format:check
```

ALWAYS `--check` in CI, never `--write`/`--fix`: auto-fixing in CI hides developer-side mistakes and
pollutes history with formatter commits. Auto-fix belongs in a pre-commit hook (husky +
`lint-staged`). `--max-warnings 0` makes class-order drift fail the build instead of rotting as a
warning.

## Finding the candidates

```bash
grep -rE 'class(Name)?="[^"]{200,}"' src/
```

Class strings over ~200 characters are soup candidates; review each as leaf or extraction candidate.

```bash
grep -rE 'className="[^"]{300,}"' src/ | wc -l
```

A non-zero count means the long-stack pattern is worth a repetition check: search the file for a
distinctive pair from the stack (`grep -rn "inline-flex items-center rounded" src/`) and count the
copies. The copy count, not the character count, decides.
