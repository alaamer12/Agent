# Detection methods — one per rule

Commands the validator runs, in order, and the output that feeds the report formatter (`Method 11`).
Prefer `rg` (respects `.gitignore`, ~10x faster on large trees); `grep -rE` is the fallback wherever
`rg` is unavailable. Every command is a **candidate generator**: the agent reads the surrounding code
before it files a finding. A grep hit is not a violation.

Paths are relative to the repo root. `src` means the project's source root — use the tree the
project actually has, not a guessed folder name.

## Method 1 : Detect v3 vs v4

```bash
# 1. package.json signal (authoritative for rule gating)
TW_VERSION=$(node -p "require('./package.json').dependencies?.tailwindcss \
  || require('./package.json').devDependencies?.tailwindcss || ''")
case "$TW_VERSION" in
  ^3*|~3*|3*|>=3*) STATE_PKG=v3 ;;
  ^4*|~4*|4*|>=4*) STATE_PKG=v4 ;;
  *)               STATE_PKG=unknown ;;
esac

# 2. CSS entry signal
if rg -q '@import "tailwindcss"' src; then STATE_CSS=v4
elif rg -q '@tailwind base' src;          then STATE_CSS=v3
else                                       STATE_CSS=unknown; fi

# 3. PostCSS signal
if rg -q '@tailwindcss/postcss' postcss.config.* 2>/dev/null; then STATE_POSTCSS=v4
elif rg -q 'tailwindcss'        postcss.config.* 2>/dev/null; then STATE_POSTCSS=v3
else                                                            STATE_POSTCSS=none; fi

# 4. Vite signal
if rg -q '@tailwindcss/vite' vite.config.* 2>/dev/null; then STATE_VITE=v4
else                                                       STATE_VITE=none; fi

echo "package=$STATE_PKG css=$STATE_CSS postcss=$STATE_POSTCSS vite=$STATE_VITE"
```

| Consensus | Gate result |
|---|---|
| all resolved signals agree | run rules for that major |
| any two resolved signals disagree | emit `[ERROR] R-00` **before** any rule finding; gate the remaining rules on `STATE_PKG` |
| `STATE_PKG=unknown` and no CSS signal | emit `[ERROR] R-00 : no version evidence`; run only the version-agnostic rules (R-01, R-08, R-09, R-10) |

`STATE_POSTCSS=none` / `STATE_VITE=none` are absence of evidence, not disagreement — a project with
no PostCSS config and no Vite plugin may be using the Tailwind CLI. A CLI build needs
`@tailwindcss/cli` under v4; the bare `tailwindcss` binary in a v4 project's scripts is a
disagreement, so check it:

```bash
rg -n '"(build|dev|start)"' package.json | rg 'tailwindcss'
```

The detection stops here. Choosing to upgrade, and the order of an upgrade, is
`../../migration/method.md`.

## Method 2 : R-01 dynamic class strings

First pass, cheap — an interpolation *inside* a class token (fragment construction):

```bash
rg -n --pcre2 -g '*.{tsx,jsx,vue,svelte,astro,html,mdx}' \
  '(?<![\s`{])\$\{[^}]+\}(?![\s`}\),])' src
```

`${color}` touching non-space characters on either side is a fragment (`bg-${color}-100`). The
lookarounds deliberately pass `${styles[status]} rounded` untouched: the interpolation is delimited
by whitespace on both sides, so it supplies a complete class name and the scanner can see it.

Second pass — the attribute forms:

```bash
rg -n -g '*.{tsx,jsx,astro}'    'className=\{\s*`[^`]*\$\{' src
rg -n -g '*.vue'               '(?::class|v-bind:class)="[^"]*\{\{' src
rg -n -g '*.svelte'            'class="[^"]*[^"\s]\{' src
rg -n -g '*.html'              'class="[^"]*[-\w]\{\{[^}]*\?\s' src
rg -n -g '*.{ts,tsx,js,jsx}'   "(class(?:Name)?\s*[:=])\s*['\"][\w-]*\s*\+\s*\w+" src   # string concat
```

**False-positive filter.** Resolve the interpolated binding:

```js
const COLOR = 'red'
className={`bg-${COLOR}-100`}      // literal, resolvable → downgrade to Info
const COLOR_MAP = { red: 'bg-red-100' }
className={COLOR_MAP[color]}       // complete class from a map → no finding
className={`bg-${color}-100`}      // runtime value → Error
```

Downgrade to Info only when the binding is a top-level `const` with a string literal value, and the
class token exists verbatim somewhere the scanner reads. Everything else stays Error: the utility
never reaches the CSS. Fix shape: `../../dynamic-classes/method.md`.

## Method 3 : R-02 scoped `@apply` without `@reference`

Run only when the gate is v4 (under v3 a scoped `@apply` works, so this rule is a false-positive
machine there).

```bash
for f in $(rg -l '@apply' -g '*.{vue,svelte,astro}' -g '*.module.css' src); do
  rg -q '@reference' "$f" || echo "R-02 $f"
done
```

The check is file-level; the requirement is block-level. Confirm before filing:

- a file with two `<style>` blocks needs `@reference` in the block that uses `@apply`;
- `@reference` resolves to a stylesheet, and that target must exist — a stale path still fails the
  build, so resolve it relative to the file, not the repo root;
- if the block uses `@apply` only with stock utilities and no theme values, the build may pass today
  and break the first time a custom token is referenced: file it as Error anyway, the rule is about
  the missing link, not the current symptom.

Fix shape: `../../config/method.md`.

## Method 4 : R-03 v3-only keys in a v4 config

```bash
# forbidden keys (v4 gate)
for key in corePlugins safelist separator; do
  rg -n --glob 'tailwind.config.*' "^\s*${key}\s*:" && echo "R-03 $key"
done

# is the JS config loaded at all?
rg -n --glob '*.css' '^\s*@config\b' src
```

v4 does not auto-detect a JavaScript config. A `tailwind.config.*` file no `@config` directive names
is **orphaned**: every key in it is inert, not just the three forbidden ones. Escalate R-03 from
Warning to Error and say so in the `Suggested` line.

Disposition table for the report body:

| Key | v4 answer |
|---|---|
| `safelist` | `@source inline("bg-red-500 bg-blue-500")` in the CSS entry |
| `corePlugins` | no equivalent; ban the utilities with a lint rule, or exclude paths with `@source not` |
| `separator` | removed; v4 fixes the separator to `:` |
| file itself | `@config "../tailwind.config.js";` if the JS config is still wanted |

Fix sequence: `../../migration/method.md`.

## Method 5 : R-04 custom class outside `@layer` / `@utility`

```bash
# candidate files: class selectors with no layer/utility wrapper anywhere in the file
for f in $(rg --files -g '*.css' src); do
  rg -q '^\s*\.[A-Za-z][\w-]*\s*[,{]' "$f" || continue
  rg -q '@(layer|utility)\b' "$f"          && continue
  echo "R-04 $f"
done
```

```bash
rg -n --glob '*.css' '^\s*\.[A-Za-z][\w-]*\s*[,{]' src   # line numbers for the report
```

Confirm before filing — grep cannot see enclosure:

- a class inside `@layer components { … }` or `@utility name { … }` is compliant;
- `@layer base { h1 { … } }` element selectors are not this rule (no class token);
- under v3 the compliant wrappers are `@layer base|components|utilities`; under v4 prefer `@utility`
  and treat `@layer components` as legacy-but-legal;
- a file that is hand-written third-party CSS is reported once, at file level, not per class.

Severity Warning: an unlayered class sits outside the cascade plan, so whether it wins against
`p-4` or loses to it depends on import order. Fix shape: `../../config/method.md`.

## Method 6 : R-05 variant stack order

v3 applied stacked variants right to left; v4 applies them left to right. Only variants that change
the **selector** are order-sensitive — media/state variants commute, so `sm:hover:` and `hover:sm:`
are the same rule and must not be reported.

```bash
rg -n --no-filename -o -g '*.{tsx,jsx,vue,svelte,html}' \
  '\b(first|last|odd|even|only|nth-[a-z0-9-]+):\*' src
rg -n --no-filename -o -g '*.{tsx,jsx,vue,svelte,html}' \
  '\b(first|last|odd|even):(has-\[[^]]+\]|\*)' src
rg -n --no-filename -o -g '*.{tsx,jsx,vue,svelte,html}' \
  '\bprose-headings:[a-z-]+:|\b[a-z-]+:prose-headings:' src
rg -n --no-filename -o -g '*.{tsx,jsx,vue,svelte,html}' '\[[^]]*\*[^]]*\]:(first|last|hover):' src
```

The first pattern is the common hit: the direct-child variant `*` stacked *after* a structural
pseudo-class is v3 order.

```html
<ul class="py-4 first:*:pt-0 last:*:pb-0"></ul>   <!-- v3 order: reported -->
<ul class="py-4 *:first:pt-0 *:last:pb-0"></ul>   <!-- v4 order: clean -->
```

Severity Warning: it compiles, the codemod does not flag it, and it styles the wrong element. The
check cannot know whether a project's own `@custom-variant` makes an unusual stack intentional —
report the finding and ask for a visual confirmation. Fix shape: `../../migration/method.md`.

## Method 7 : R-06 bare `border` / `ring` / `divide` / placeholder

Probe the restoration first; a hit suppresses the rule for that token project-wide.

```bash
rg -n --glob '*.css' 'border-color:\s*var\(--color-(gray|zinc)-200' src   # borders restored
rg -n --glob '*.css' -- '--default-ring-(width|color)' src                # ring restored
rg -n --glob '*.css' '::placeholder' src                                   # placeholder handled in base
```

Then the sweep — bare tokens delimited by whitespace or the end of the attribute:

```bash
rg -n -g '*.{tsx,jsx,vue,svelte,html}' \
  '(class|className)=["`{][^"`}]*[ "](border|ring)([ "`}])' src
rg -n -g '*.{tsx,jsx,vue,svelte,html}' \
  '(class|className)=["`][^"`]*(divide-[xy])(?![\w-])' src
rg -n -g '*.{tsx,jsx,vue,svelte,html,astro}' '<(input|textarea)\b' src   # then check for placeholder: colour
```

`border-2`, `border-zinc-200`, `ring-3`, `ring-blue-500` are excluded by the trailing-delimiter
test; a bare `border` or `ring` is not.

Severity Info on purpose: `currentColor` is often the right answer. The default changes behind this
rule are the report's payload:

| Token | v3 | v4 |
|---|---|---|
| `border-*` / `divide-*` colour | `gray-200` from config | `currentColor` |
| `ring` | `3px`, `blue-500` | `1px`, `currentColor` |
| placeholder | `gray-400` from config | current text colour at 50% opacity |

Aggregate the count into the by-area summary instead of listing hundreds of blocks. Per-site colour
vs one global restoration: `../../migration/method.md`.

## Method 8 : R-08 prop-to-class mapping shape

Not grep-complete; grep only narrows the candidates, then read the function.

```bash
rg -n -U -A 8 -g '*.{tsx,jsx,vue,svelte}' \
  'switch\s*\(\s*(variant|size|color|tone|status|type)\s*\)' src
rg -n -g '*.{tsx,jsx,vue,svelte}' \
  '\?\s*["`][^"`]*(bg|text|border)-[^"`]+["`]\s*:\s*["`][^"`]*(bg|text|border)-' src
rg -n -g '*.{tsx,jsx,vue,svelte}' \
  'function\s+(get|resolve|compute)[A-Z]?\w*(Class|Styles)\w*\s*\(' src
```

Ask one question per candidate: could this be a single object literal keyed by the prop? Report
Info only when the answer is yes. Escalate nothing: the code works, the shape is the problem. If the
function also interpolates class fragments, that is R-01 (Error), filed separately — never fold the
two severities together. Fix shape: `../../design-system/method.md` and `../../utility-soup/method.md`.

## Method 9 : R-09 merge order

```bash
rg -n -U -A 3 -g '*.{tsx,jsx,vue,svelte}' '\b(twMerge|cn|clsx)\s*\(' src
```

For each call: collect the class tokens per argument, bucket them by utility dimension, and check
the conflicting pair. The last occurrence wins, so a **default placed after an override** is the
finding.

| Dimension | Conflicting family |
|---|---|
| padding | `p-`, `px-`, `py-`, `pt-`, `pb-`, `pl-`, `pr-` |
| margin | `m-`, `mx-`, `my-`, `mt-`, `mb-`, `ml-`, `mr-` |
| size | `w-`, `h-`, `size-`, `min-w-`, `max-w-` |
| colour | `bg-`, `text-`, `border-`, `ring-` |
| radius / shadow / flex | `rounded-*`, `shadow-*`, `flex-*` |

Typical inversion — the consumer prop is meant to win and cannot:

```tsx
twMerge(className, 'p-4 bg-white rounded-lg')  // defaults are last: they always win
twMerge('p-4 bg-white rounded-lg', className)  // override last: consumer wins
```

Severity Info: the rule reports the shape, a human supplies the intent. Custom `extendTailwindMerge`
config changes which tokens conflict — check for it before filing. Fix shape:
`../../utility-soup/method.md`.

## Method 10 : R-10 plugin theme defaults

```bash
for f in $(rg -l "tailwindcss/plugin" -g '*.{js,ts,cjs,mjs}'); do
  rg -o --no-filename "theme\(\s*['\"][^'\"]+" "$f" | sort -u          # namespaces read
  rg -Uq 'plugin\s*\([\s\S]+,\s*\{' "$f" || echo "R-10 $f: no second-arg config"
done
```

Approximate by design: the second-argument probe cannot tell whether the shipped defaults cover every
read namespace. Open the file and diff the two sets; report only namespaces that are read and never
defaulted. Severity Warning: the plugin yields zero utilities for a consumer who has not configured
the namespace, with no error to show for it. No sibling module owns plugin authoring — the fix is in
`03-anti-patterns.md` (Pattern 9).

## Method 11 : Assemble the report

1. `R-00` findings, if any, go above everything else.
2. Group by file path; inside a file, group by rule; inside a rule, sort by line number.
3. One block per finding, fields in the fixed order defined in `../method.md` (Report Format).
4. Large trees: the first three files per rule get full blocks; the remainder collapses into one
   `Additional occurrences` list under a single `Cite`.
5. Footer counts must equal the blocks above them; recount, do not carry a running total.
6. `Cite` is a battery module path (`../<module>/method.md`), never a skill name or a URL.
7. Offer nothing to run: this module has no autofix mode, and the footer must not imply one.

```text
---
Total : 6 issues
  Errors   : 2
  Warnings : 3
  Info     : 1
```

## Method 12 : Scan set

Skip before anything else — one wrong file in the report costs more review time than one missed
generated file:

| Skip | Reason |
|---|---|
| anything in `.gitignore` | generated or vendored |
| `node_modules`, `dist`, `build`, `.next`, `out`, `target` | generated output |
| lock files, `*.min.css`, `*.map` | noise |
| files over 1 MB | almost certainly generated |
| binary files (`file --mime-type` when unsure) | not source |

```bash
rg --files -g '!node_modules' -g '!dist' -g '!build' -g '!.next' -g '!out' \
   -g '!target' -g '!*.lock' -g '!*.{min.css,map}' src | wc -l
```

Include in the scan set: framework source files (`tsx`, `jsx`, `vue`, `svelte`, `astro`, `html`,
`mdx`), every `.css` the build consumes, `tailwind.config.*`, `postcss.config.*`, `vite.config.*`,
and `package.json` (for Method 1 only — it is never a finding source).
