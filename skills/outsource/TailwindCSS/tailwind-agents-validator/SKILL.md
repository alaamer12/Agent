---
name: tailwind-agents-validator
description: >
  Use when reviewing a Tailwind CSS codebase for cross-rule violations,
  performing a pre-PR audit of changes that touch styling, validating
  a v3-to-v4 migration result, or running a periodic codebase health
  check across utility classes, plugin authoring, and configuration
  files. The agent acts as a Tailwind-specific code reviewer that
  enforces every rule documented in the sibling skills of this
  package, producing an actionable report that cites the authoritative
  sibling skill for each finding. Prevents the four highest-impact
  Tailwind code-review misses: dynamic template-literal class strings
  that compile cleanly but emit no CSS in production, scoped @apply
  blocks in Vue/Svelte/CSS-modules without @reference under v4,
  v3-only config keys (corePlugins, safelist, separator) silently
  ignored after a v4 upgrade, and bare border/ring/placeholder usage
  inheriting the wrong default colour post-migration. Covers the full
  rule catalogue (no dynamic class strings, no scoped @apply without
  @reference, no v3 keys in v4 config, no undefined custom classes
  outside @layer, variant-stack order consistency, explicit border
  and ring colours, no em-dash in user-facing strings, deterministic
  prop-to-class mapping, twMerge ordering correctness, plugin theme()
  default-shipping), the report format (severity, file:line, rule
  citation, sibling-skill link, fix suggestion), the recursive scan
  pattern (TSX, JSX, Vue, Svelte, CSS, MDX), the v3-or-v4 detection
  heuristic, and integration into CI as a non-blocking advisory.
  Keywords: tailwind code review, tailwind validator, tailwind audit,
  tailwind linter, pre-PR check tailwind, post-migration audit, v3 v4
  consistency check, cross-rule check tailwind, dynamic class
  detection, scoped @apply check, @reference missing, corePlugins
  leftover, safelist leftover, separator leftover, bare border bare
  ring, prop-to-class consistency, variant order check, twMerge
  audit, my codebase upgrade looks clean but, find all dynamic
  classes, find all scoped @apply, find tailwind antipatterns,
  tailwind health check, before I ship audit.
license: MIT
compatibility: "Designed for Claude Code. Requires Tailwind CSS v3.4 or v4.0+."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# Tailwind Validator : Cross-Skill Consistency Agent

Acts as a Tailwind-specific code reviewer. Reads the codebase, runs
every rule documented in the sibling skills, produces an actionable
report that cites the authoritative source per finding.

The validator does NOT modify code. It reports. The developer (or a
follow-up agent) applies fixes guided by the cited sibling skill.

## How To Invoke

The user asks "validate my Tailwind code" or "audit this codebase for
Tailwind issues" or "run a pre-PR check on the styling changes". The
agent :

1. Detects v3 vs v4 (heuristic in Method 1, `references/methods.md`).
2. Runs each rule in the catalogue (Section : Rule Catalogue).
3. Emits the report in the standard format (Section : Report Format).

## Detect : v3 or v4

Decision sources, in priority order :

1. `package.json` `dependencies.tailwindcss` semver. `^3.x` is v3.
   `^4.x` is v4.
2. CSS entry file contains `@import "tailwindcss"` (v4) OR three
   `@tailwind` directives (v3).
3. PostCSS config plugin is `@tailwindcss/postcss` (v4) OR
   `tailwindcss` (v3).
4. Vite config imports `@tailwindcss/vite` (v4) OR uses the PostCSS
   plugin (v3).

If signals conflict, report a Severity-Error mismatch FIRST. Mixed
configurations produce silent failures.

Mixed-state cross-link : `tailwind-impl-migration-v3-v4`.

## Rule Catalogue

Each rule names a check, the file types it scans, the sibling skill
that documents the rule, and the severity.

### Rule R-01 : No Dynamic Template-Literal Class Strings

**Scans** : `.tsx`, `.jsx`, `.vue`, `.svelte`, `.astro`, `.mdx`

**Detect** : grep for `` className=`...${...}...` `` and `class="...{{ ...?... }}...{{ ... }}"` patterns that build a class fragment from a variable.

**Severity** : Error (production bug, classes silently missing)

**Sibling skill** : `tailwind-errors-dynamic-classes`

**Fix** : static map per Method 1 of the sibling skill.

### Rule R-02 : Scoped @apply Without @reference (v4 only)

**Scans** : `.vue`, `.svelte`, `*.module.css`

**Detect** : file contains `@apply` inside a scoped `<style>` block or
a CSS module, and the same block does NOT contain `@reference`.

**Severity** : Error (build fails with "Cannot apply unknown utility
class")

**Sibling skill** : `tailwind-impl-apply-directive`

**Fix** : prepend `@reference "../path/to/app.css";` inside the style
block.

### Rule R-03 : Forbidden v3 Config Keys in v4 Project

**Scans** : `tailwind.config.js`, `tailwind.config.ts`

**Detect** : project is v4 AND config file contains any of
`corePlugins`, `safelist`, `separator`.

**Severity** : Warning (silently ignored, original intent lost)

**Sibling skill** : `tailwind-errors-v4-migration`, fallback to
`tailwind-impl-migration-v3-v4`

**Fix** :
- `corePlugins` : remove and replace with ESLint rule or `@source not`
- `safelist` : convert to `@source inline("...")` in CSS
- `separator` : remove ; v4 fixes separator to `:`

### Rule R-04 : Undefined Custom Class Outside @layer

**Scans** : `.css`

**Detect** : project is v3 and file contains a custom class
declaration `(.classname { ... })` outside `@layer base` / `@layer
components` / `@layer utilities`. Project is v4 and file contains a
custom class without `@utility` or `@layer`.

**Severity** : Warning (cascade ordering unpredictable, overrides
behave inconsistently)

**Sibling skill** : `tailwind-impl-config-v3`, `tailwind-impl-config-v4`

**Fix** : wrap in `@layer components` (v3) or rewrite as `@utility`
(v4).

### Rule R-05 : Variant Stack Order

**Scans** : `.tsx`, `.jsx`, `.vue`, `.svelte`, `.html`

**Detect** : v4 project contains a class with two or more variants
that look v3-style. Common patterns : `first:*:`, `last:*:`,
`hover:lg:` (the lg should come first under v4 left-to-right rule for
breakpoints AT the variant level).

**Severity** : Warning (visual regression after v3 to v4)

**Sibling skill** : `tailwind-syntax-variants`,
`tailwind-impl-migration-v3-v4`

**Fix** : flip the order. `first:*:pt-0` becomes `*:first:pt-0`.

### Rule R-06 : Bare border / ring / placeholder Under v4

**Scans** : `.tsx`, `.jsx`, `.vue`, `.svelte`, `.html`

**Detect** : v4 project AND class list contains a bare `border`,
`ring`, `placeholder` token with no following colour or width
modifier on the same element.

**Severity** : Info (visual regression risk : default colour changed
from `gray-200` / `blue-500` / `gray-400` to `currentColor`)

**Sibling skill** : `tailwind-errors-v4-migration`,
`tailwind-impl-migration-v3-v4`

**Fix** : add explicit colour (`border-zinc-200`, `ring-blue-500`,
`placeholder-zinc-400`) OR restore v3 defaults globally via `@layer
base` (see method).

### Rule R-07 : Em-Dash in User-Facing String

**Scans** : `.tsx`, `.jsx`, `.vue`, `.svelte`, `.html`, `.mdx`

**Detect** : literal `—` (U+2014) inside JSX text, attribute strings
that render to users (`title`, `aria-label`, `placeholder`), or
component children.

**Severity** : Info (typography standard ; CLAUDE.md project rule)

**Sibling skill** : (project rule, see workspace CLAUDE.md)

**Fix** : replace with `.`, `,`, or rewrite the sentence. NEVER
replace with `-`.

### Rule R-08 : Deterministic Prop-to-Class Mapping

**Scans** : `.tsx`, `.jsx`, `.vue`, `.svelte`

**Detect** : component receives a `variant` / `color` / `size` prop
and constructs the class via a switch statement, ternary chain, or
function call that returns differently-shaped strings per branch.

**Severity** : Info (maintainability ; not a bug, but harder to
audit)

**Sibling skill** : `tailwind-core-design-system`

**Fix** : refactor to a single object literal mapping prop value to
complete class string.

### Rule R-09 : twMerge Order Mistake

**Scans** : `.tsx`, `.jsx`, `.vue`, `.svelte`

**Detect** : `twMerge(...)` or `cn(...)` call with conflicting
utilities where the LATER argument is the loser (e.g.
`twMerge('p-4', 'p-2')` resolves to `p-2` ; if the intent was `p-4`
as the override, the argument order is wrong).

**Severity** : Info (requires intent inference ; flag for human
review only)

**Sibling skill** : `tailwind-impl-tailwind-merge`

**Fix** : reverse the argument order so the override is last.

### Rule R-10 : Plugin Missing Default Theme Values

**Scans** : `*.js`, `*.ts` files exporting a Tailwind plugin

**Detect** : the plugin body calls `theme('someNamespace')` AND the
plugin's second-arg config does NOT define
`theme.extend.someNamespace`.

**Severity** : Warning (plugin works only when consumer happens to
configure the namespace, fails silently otherwise)

**Sibling skill** : `tailwind-impl-plugins-custom`

**Fix** : ship defaults via the `plugin(fn, { theme: { ... } })`
second argument.

## Report Format

```
Tailwind Validator Report
=========================
Project state : v4 detected (tailwindcss@^4.0.5)
Scan scope    : src/ tests/ tailwind.config.js postcss.config.mjs
Files scanned : 412
Issues        : 7 (1 error, 3 warnings, 3 info)

---

[ERROR] R-01 : dynamic class string
  File       : src/components/Tag.tsx:14
  Code       : `className={`bg-${color}-100 text-${color}-800`}`
  Cite       : tailwind-errors-dynamic-classes (Fix 1, static map)
  Suggested  : replace with lookup object indexed by `color`.

[ERROR] R-02 : scoped @apply without @reference
  File       : src/components/Hero.vue:42
  Block      : <style scoped> @apply text-2xl font-bold </style>
  Cite       : tailwind-impl-apply-directive
  Suggested  : prepend `@reference "../app.css";` inside <style>.

[WARNING] R-03 : forbidden v3 key in v4 config
  File       : tailwind.config.js:8
  Key        : safelist
  Cite       : tailwind-impl-migration-v3-v4 (Method 7)
  Suggested  : move to `@source inline(...)` in src/app.css and
               remove from JS config.

... etc
```

Per-issue fields :

- Severity tag in brackets
- Rule code
- File and line number
- The offending snippet
- The sibling skill name (NOT a URL ; the in-package skill reference)
- A one-line suggested fix

## Cross-Reference Index

| Rule | Authoritative Skill |
|------|---------------------|
| R-01 dynamic classes | `tailwind-errors-dynamic-classes` |
| R-02 scoped @apply | `tailwind-impl-apply-directive` |
| R-03 v3 keys in v4 | `tailwind-impl-migration-v3-v4` |
| R-04 undefined custom class | `tailwind-impl-config-v3`, `tailwind-impl-config-v4` |
| R-05 variant stack order | `tailwind-syntax-variants` |
| R-06 bare border/ring | `tailwind-impl-migration-v3-v4` |
| R-07 em-dash | workspace CLAUDE.md |
| R-08 prop-to-class shape | `tailwind-core-design-system` |
| R-09 twMerge ordering | `tailwind-impl-tailwind-merge` |
| R-10 plugin theme defaults | `tailwind-impl-plugins-custom` |

## CI Integration

The validator is ADVISORY by default. Exit code is 0 unless errors
exceed the configured threshold. Sample GitHub Actions step :

```yaml
- name: Tailwind audit
  run: |
    claude --skill tailwind-agents-validator . > tailwind-report.txt
    cat tailwind-report.txt
    # fail only if errors > 0
    grep -q '^\[ERROR\]' tailwind-report.txt && exit 1 || exit 0
```

NEVER block PRs on info or warning levels. Errors (R-01, R-02)
indicate real production bugs and SHOULD block.

## Sequencing With Sibling Skills

The validator is NOT a substitute for the per-area skills. When a
finding cites `tailwind-errors-dynamic-classes`, the developer (or
the follow-up agent) opens that skill for the full fix catalogue.

Recommended workflow :

1. Run `tailwind-agents-validator`.
2. For each error : open the cited skill, apply the documented fix.
3. Re-run the validator. Iterate until errors = 0.
4. Optional : address warnings and info as time allows.

## References

- `references/methods.md` : per-rule detection commands (grep, AST,
  PostCSS) and the v3-or-v4 heuristic in detail
- `references/examples.md` : sample input codebase plus the validator
  report it should produce
- `references/anti-patterns.md` : ten high-impact violations the
  validator catches, with before/after

## Sources

- All sibling skills in this package
- Project CLAUDE.md (workspace conventions)
