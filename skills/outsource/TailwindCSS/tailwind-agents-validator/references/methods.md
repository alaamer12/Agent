# Methods : Detection Logic per Rule

Concrete commands and patterns. The agent runs these in order ; the
output feeds the report formatter.

## Method 1 : Detect v3 vs v4

```bash
# 1. package.json signal
TW_VERSION=$(node -p "require('./package.json').dependencies?.tailwindcss || require('./package.json').devDependencies?.tailwindcss || ''")
case "$TW_VERSION" in
  ^3*|~3*|3*) STATE_PKG=v3 ;;
  ^4*|~4*|4*) STATE_PKG=v4 ;;
  *)          STATE_PKG=unknown ;;
esac

# 2. CSS entry signal
if grep -rln '@import "tailwindcss"' src/ 2>/dev/null | head -1 >/dev/null; then
  STATE_CSS=v4
elif grep -rln '@tailwind base' src/ 2>/dev/null | head -1 >/dev/null; then
  STATE_CSS=v3
else
  STATE_CSS=unknown
fi

# 3. PostCSS signal
if grep -q '@tailwindcss/postcss' postcss.config.* 2>/dev/null; then
  STATE_POSTCSS=v4
elif grep -q '"tailwindcss":\s*{}\|tailwindcss:' postcss.config.* 2>/dev/null; then
  STATE_POSTCSS=v3
else
  STATE_POSTCSS=none
fi

# 4. Vite signal
if grep -q '@tailwindcss/vite' vite.config.* 2>/dev/null; then
  STATE_VITE=v4
else
  STATE_VITE=none
fi

# Consensus or mismatch
echo "package=$STATE_PKG css=$STATE_CSS postcss=$STATE_POSTCSS vite=$STATE_VITE"
```

If signals disagree, emit a Severity-Error mismatch row BEFORE any
rule runs. The remaining rules use the package-json signal as the
authoritative state, but the mismatch itself must be reported.

## Method 2 : R-01 Dynamic Class String Detection

### Grep pattern (first pass, cheap)

```bash
grep -rEn 'class(Name)?\s*=\s*[`{][^`}]*\${' src \
  --include="*.tsx" --include="*.jsx" --include="*.vue" --include="*.svelte" --include="*.astro"
```

This catches `` className=`bg-${color}-500` `` and JSX equivalents.

### Vue / template binding

```bash
grep -rEn ':class\s*=\s*[`"][^`"]*\${' src --include="*.vue"
grep -rEn 'v-bind:class\s*=\s*[`"][^`"]*\${' src --include="*.vue"
```

### Mustache templating

```bash
grep -rEn 'class="[^"]*{{[^}]*\?[^}]*}}' src --include="*.html"
```

### False-positive filter

Skip lines where the template literal is fully resolved at compile
time (constants module). The agent verifies by checking if the
interpolated variable comes from a string literal map :

```js
const COLOR = 'red'
className={`bg-${COLOR}-500`}  // safe : COLOR is a compile-time literal
```

Lower the severity to Info when the binding is a top-level `const`
assignment with a string literal value. Otherwise stay at Error.

## Method 3 : R-02 Scoped @apply Without @reference

```bash
# Vue and Svelte SFCs
for f in $(grep -rln '@apply' src --include="*.vue" --include="*.svelte"); do
  if ! grep -q '@reference' "$f"; then
    echo "$f : @apply without @reference"
  fi
done

# CSS modules
for f in $(grep -rln '@apply' src --include="*.module.css"); do
  if ! grep -q '@reference' "$f"; then
    echo "$f : @apply without @reference"
  fi
done
```

### v3 false-positive

In v3, scoped `@apply` works without `@reference`. Run this rule only
when the detected state is v4.

## Method 4 : R-03 v3 Keys in v4 Config

```bash
# Only when state = v4
for key in corePlugins safelist separator; do
  matches=$(grep -nE "^\s*${key}\s*:" tailwind.config.* 2>/dev/null)
  if [ -n "$matches" ]; then
    echo "FORBIDDEN_V3_KEY $key : $matches"
  fi
done
```

`tailwind.config.js` is allowed in v4 only when loaded via `@config
"./tailwind.config.js"`. The forbidden-key check applies to that
loaded file. If no `@config` directive exists, the JS config is
orphaned and the warning escalates to Error.

## Method 5 : R-04 Undefined Custom Class Outside @layer

### v3 check

```bash
# Find CSS files imported by the build
for f in $(find src -name "*.css"); do
  # Custom class declarations
  CLASSES=$(grep -nE '^\.[a-zA-Z][\w-]*\s*\{' "$f" | grep -v "@layer")
  # If found and the file does NOT have an enclosing @layer scope
  if [ -n "$CLASSES" ] && ! grep -q '@layer' "$f"; then
    echo "$f : custom classes outside @layer"
    echo "$CLASSES"
  fi
done
```

### v4 check

Same but the wrapper rule is `@utility` instead of `@layer
components` :

```bash
for f in $(find src -name "*.css"); do
  CLASSES=$(grep -nE '^\.[a-zA-Z][\w-]*\s*\{' "$f")
  if [ -n "$CLASSES" ] && ! grep -q '@utility\|@layer\b' "$f"; then
    echo "$f : custom classes outside @utility / @layer"
  fi
done
```

## Method 6 : R-05 Variant Stack Order

```bash
# v4 only : detect v3-style stacks
grep -rEn 'class[=Name]+="[^"]*\bfirst:\*:|class[=Name]+="[^"]*\blast:\*:' src \
  --include="*.tsx" --include="*.jsx" --include="*.vue" --include="*.svelte" --include="*.html"
```

`*:` should come BEFORE `first:` / `last:` in v4. The grep finds
flipped patterns.

The detection misses semantically equivalent custom variants. The
agent reports findings as Warning and asks the developer to verify
visually.

## Method 7 : R-06 Bare border / ring / placeholder (v4)

```bash
# Tokens: a class attr containing standalone `border`, `ring`, or `placeholder`
# without a colour-suffix on the same token
grep -rEnP 'class[=Name]+="[^"]*\b(border|ring|placeholder)(?![\w/:-])' src \
  --include="*.tsx" --include="*.jsx" --include="*.vue" --include="*.svelte" --include="*.html"
```

The `(?!...)` negative lookahead excludes `border-2`, `border-zinc-200`,
`ring-blue-500`, etc.

The check is Info-level (visual regression risk, not always wrong).
Restoration via `@layer base` block negates the warning ; the agent
checks for that block in the entry CSS file first :

```bash
grep -q "border-color.*var(--color-gray-200" src/app.css 2>/dev/null && \
  echo "R-06 skipped : v3 default restored globally"
```

## Method 8 : R-07 Em-Dash in User-Facing Text

```bash
# Literal U+2014 in source files
grep -rln $'\xe2\x80\x94' src \
  --include="*.tsx" --include="*.jsx" --include="*.vue" --include="*.svelte" --include="*.html" --include="*.mdx"
```

### False-positive filter

Skip files inside `node_modules`, `docs/research`, `CHANGELOG.md`, and
git diff outputs. Em-dashes in markdown research notes are not user-
facing.

## Method 9 : R-08 Prop-to-Class Mapping Shape

This rule cannot be fully automated by grep. The agent uses pattern
recognition :

```bash
# Switch statement returning class strings
grep -rEnB 1 -A 5 'switch\s*\(\s*[a-zA-Z]+\s*\)\s*{' src \
  --include="*.tsx" --include="*.jsx" | grep -E 'return\s+[`"]bg-|return\s+[`"]text-'

# Ternary chain
grep -rEn '\?\s*[`"][^`"]*[`"]\s*:\s*[`"][^`"]*[`"]\s*:' src \
  --include="*.tsx" --include="*.jsx"
```

When found, the agent reads the surrounding function and asks : could
this be a single object literal? If yes, report Info-level with the
suggested refactor.

## Method 10 : R-09 twMerge Argument Order

```bash
grep -rEnA 2 'twMerge\s*\(|cn\s*\(\s*' src \
  --include="*.tsx" --include="*.jsx" --include="*.vue" --include="*.svelte"
```

For each call site, the agent reads the arguments. If the LAST argument
contains a class that conflicts with an EARLIER argument's class on the
same Tailwind dimension, the result is the LAST argument's value.

The rule is Info-level because intent is required to judge.

## Method 11 : R-10 Plugin Missing Theme Defaults

```bash
# Find plugin source files
for f in $(grep -rln "require\('tailwindcss/plugin')\|from 'tailwindcss/plugin'" .); do
  # Theme reads
  READS=$(grep -E "theme\(['\"]([\w.]+)" "$f" -o | sort -u)
  # Theme defaults shipped (second-arg config object)
  HAS_CONFIG=$(grep -E 'plugin\(\s*function|plugin\(function' "$f" | grep -c ',')
  if [ -n "$READS" ] && [ "$HAS_CONFIG" -eq 0 ]; then
    echo "$f : plugin reads $READS but ships no default theme"
  fi
done
```

The check is approximate ; the agent reads the file content to confirm
the second-arg config exists and covers the read namespaces.

## Method 12 : Generate the Report

After running all rules, the agent assembles the report in the format
defined in `SKILL.md` (Section : Report Format). One block per
finding. Group by file, then by rule, then by line number.

Footer summary :

```
---
Total : 7 issues
  Errors   : 1
  Warnings : 3
  Info     : 3
Run again with --autofix to apply suggested fixes for safe categories.
```

The `--autofix` flag is NOT implemented by this skill ; it is reserved
for a future remediation agent that consumes this report.

## Method 13 : Hot Paths to Skip

To stay fast on large codebases :

- Skip files in `.gitignore`
- Skip `node_modules`, `dist`, `build`, `.next`, `out`, `target`
- Skip lock files (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`)
- Skip binary files (use `file --mime-type` if uncertain)
- Skip files larger than 1 MB (likely generated)

```bash
RIPGREP_IGNORE='--glob !node_modules --glob !dist --glob !build --glob !.next --glob !out --glob !target --glob !*.lock'
```

Prefer `rg` over `grep -r` when available ; respects `.gitignore` by
default and is 10x faster on large trees.
