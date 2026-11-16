# validator — cross-module Tailwind code review

Read the code, run the rule catalogue, emit a report. The validator is a reviewer, not a fixer: it
changes nothing on disk. Every finding names the one battery module that owns the fix, and the
reader opens that module to do the work.

Two failure classes this exists to catch: styling that compiles clean and emits no CSS in
production, and a v3→v4 upgrade that "looks finished" while half the old semantics are silently
gone. Both are invisible to a normal code review and to the build.

## Scope

| Job | Owner |
|---|---|
| Decide which Tailwind major a workspace is on, at review time | this module (`Detect: v3 or v4`) |
| Run the rule catalogue over a scan set and print the report | this module |
| Decide whether/when to upgrade, and sequence the upgrade | `../migration/method.md` |
| Author or repair the subject of a rule (dynamic classes, config, tokens, merges) | the cited module |

The validator does **not** modify files, propose an upgrade, run a codemod, or keep state between
runs. Each pass is fresh; the report is the only output.

Link convention: module citations are paths, not skill names or URLs. From this file a sibling is
`../<module>/method.md`; from `references/` it is `../../<module>/method.md`.

## Procedure

1. Detect the major (`Detect: v3 or v4`). Conflict → `[ERROR] R-00`, printed before everything else.
2. Build the scan set: source globs plus config files, minus the skip list (Method 12).
3. Run each rule whose version gate matches the detected state.
4. Print the report (`Report Format`): grouped by file, then rule, then line.
5. Hand off. A finding is a pointer to a module, not a fix instruction.

Detection commands per rule: `references/01-detection-methods.md`. Worked input and output:
`references/02-example-run.md`. Violation shapes with before/after:
`references/03-anti-patterns.md`.

## Detect: v3 or v4

Evidence, strongest first. Stop at the first signal that resolves; then check the rest for
agreement.

| # | Signal | Reads as v3 | Reads as v4 |
|---|---|---|---|
| 1 | `package.json` `dependencies`/`devDependencies`.`tailwindcss` | `^3.x`, `~3.x`, `3.x` | `^4.x`, `~4.x`, `4.x` |
| 2 | CSS entry file | `@tailwind base; @tailwind components; @tailwind utilities;` | `@import "tailwindcss"` |
| 3 | PostCSS config | plugin `tailwindcss` | plugin `@tailwindcss/postcss` |
| 4 | Vite config | PostCSS route only | imports `@tailwindcss/vite` |

```bash
node -p "require('./package.json').dependencies?.tailwindcss || require('./package.json').devDependencies?.tailwindcss || ''"
rg -l '@import "tailwindcss"' src
rg -l '@tailwind base' src
rg -l '@tailwindcss/(postcss|vite)' postcss.config.* vite.config.*
```

| Result | Action |
|---|---|
| Signals agree | State the major and the exact semver in the report header. Run version-gated rules. |
| Signals conflict | **`[ERROR] R-00 : version mismatch` first, before any rule finding.** Then run the version-gated rules against signal 1 (the installed package beats any file text) and header them `state: CONFLICT — assumed v4`. |
| Signal 1 unresolved (no dependency) | Report `R-00` as Error too: a Tailwind codebase with no declared version is not auditable. |

A mixed install fails quietly — v4 package with the `@tailwind` trio, or v4 CSS driven by the v3
PostCSS plugin. Under a wrong assumption the version-gated rules switch off and their real bugs go
unreported, so the mismatch outranks every other finding.

This section answers one question: *what is this project today*. Whether it should move to v4, what
breaks, and in which order — `../migration/method.md`. The detection logic is owned here because it
is a review-time precondition, not an upgrade step.

## Rule catalogue

| Rule | Check | Scans | Version gate | Severity | Fix lives in |
|---|---|---|---|---|---|
| R-00 | v3/v4 evidence conflicts or is absent | `package.json`, CSS entry, PostCSS/Vite config | any | Error | `../migration/method.md` (install state) |
| R-01 | Class name built from an interpolated fragment | `.tsx .jsx .vue .svelte .astro .html .mdx` | any | Error | `../dynamic-classes/method.md` |
| R-02 | Scoped `@apply` with no `@reference` | `.vue .svelte *.module.css` | v4 | Error | `../config/method.md` |
| R-03 | v3-only config keys in a v4 project | `tailwind.config.{js,ts,cjs,mjs}` | v4 | Warning (Error if orphaned) | `../migration/method.md` |
| R-04 | Custom class outside `@layer` / `@utility` | `.css` | v3 and v4, differently | Warning | `../config/method.md` |
| R-05 | Order-sensitive variant stack left in v3 order | `.tsx .jsx .vue .svelte .html` | v4 | Warning | `../migration/method.md` |
| R-06 | Bare `border` / `divide` / `ring` / placeholder colour | `.tsx .jsx .vue .svelte .html` | v4 | Info | `../migration/method.md` |
| R-08 | Prop-to-class mapping that is not deterministic | `.tsx .jsx .vue .svelte` | any | Info | `../design-system/method.md`, `../utility-soup/method.md` |
| R-09 | `twMerge`/`cn` argument order puts the loser last | `.tsx .jsx .vue .svelte` | any | Info | `../utility-soup/method.md` |
| R-10 | Plugin reads a theme namespace it never defaults | plugin `.js`/`.ts` | any | Warning | this module (Method 10, Pattern 9) |

Rule IDs are stable and cited by other documents: never renumber to close a gap. **R-07 is vacant** —
that rule was never about Tailwind. The ID is retired, not reused.

### R-01 : Dynamic template-literal class strings

**Detect** — a class attribute whose value interpolates a *fragment* of a class name:
`` className={`bg-${color}-100 text-${color}-800`} ``, Vue `:class="`text-${x}-500`"`, mustache-built
fragments. **Severity** Error: the build passes, the scanner never sees the string, the class is
never emitted, the element ships unstyled.

**Escape hatch** — interpolation that yields a *complete* class name taken from a literal map in
the same file is legal and is the recommended shape (`${styles[status]}` where `styles` holds full
class strings). Downgrade to Info only when the interpolated binding is a top-level `const` string
literal. Detection and false-positive filter: Method 2.

**Fix owner** `../dynamic-classes/method.md` — static map or variant registry, one entry per state.

### R-02 : Scoped `@apply` without `@reference` (v4)

**Detect** — `@apply` inside a scoped `<style>` block, an Astro/Svelte style block, or a
`*.module.css` file, with no `@reference` in the same block. **Severity** Error: v4 builds each
bundled-adjacent stylesheet in isolation, so the block has no access to theme variables, custom
utilities, or custom variants defined elsewhere and the build fails with "Cannot apply unknown
utility class". Silent on v3, hence the gate. Detection: Method 3.

**Fix owner** `../config/method.md` — either `@reference "../app.css";` inside the block, or drop
`@apply` and read the generated theme variable directly. Which one a project uses is a config
decision, not a report decision.

### R-03 : v3-only config keys in a v4 project

**Detect** — state v4 and the JS config contains `corePlugins`, `safelist`, or `separator`.
**Severity** Warning: v4 ignores these silently and the original intent is lost without an error.
**Escalate to Error** when no `@config "<path>";` directive loads that file — v4 does not
auto-detect a JS config, so an orphaned file means the whole config is dead, not just those keys.

| Key | v4 disposition |
|---|---|
| `safelist` | `@source inline("...")` in the CSS entry |
| `corePlugins` | no replacement; lint rule banning the utilities, or `@source not` to exclude paths |
| `separator` | dropped; v4 fixes the separator at `:` |

**Fix owner** `../migration/method.md` (Method 4 for the orphan check).

### R-04 : Undefined custom class outside `@layer` / `@utility`

**Detect, v3** — a `.css` file declaring `.some-class { … }` where the file has no `@layer` at all.
**Detect, v4** — a bare custom class with neither `@utility` nor `@layer` wrapping it.
**Severity** Warning: cascade ordering becomes unpredictable and overrides behave inconsistently —
in v4 a class Tailwind does not know is not sorted against the utilities that will fight it.

**Fix owner** `../config/method.md` — wrap in `@layer components` (v3) or register with `@utility`
(v4). Detection: Method 5.

### R-05 : Variant stack order

**Detect** — state v4 and a class stacks variants in v3 right-to-left order. v4 applies stacked
variants left to right, so the old order compiles, builds, and targets the wrong element. Only
selector-shaping variants are order-sensitive; media and simple state variants commute, so `sm:hover:`
and `hover:sm:` are the same rule and are never reported. The order-sensitive hits in practice:

```html
<ul class="py-4 first:*:pt-0 last:*:pb-0"></ul>   <!-- v3 order, wrong under v4 -->
<ul class="py-4 *:first:pt-0 *:last:pb-0"></ul>   <!-- v4 order -->
```

- the direct-child variant `*` stacked after `first:` / `last:` / `odd:` / `even:`;
- an arbitrary child selector (`[&>*]:`, `*:hover:`) stacked with a state variant in the old order;
- compound marker variants such as `prose-headings:` stacked with another variant.

**Severity** Warning: no build failure, a visual regression, and the upgrade codemod does not flag it.
The check cannot tell an accidental stack from a deliberate `@custom-variant`, so report and ask for a
visual pass. Detection: Method 6.

**Fix owner** `../migration/method.md` (syntax reversal).

### R-06 : Bare `border` / `divide` / `ring` / placeholder colour (v4)

**Detect** — state v4 and a class list carries a bare `border`, `divide-*`, `ring`, or a
placeholder colour, with no explicit colour or width on the same element.

| Utility | v3 default | v4 default |
|---|---|---|
| `border-*`, `divide-*` | configured `gray-200` | `currentColor` |
| `ring` | `3px`, `blue-500` | `1px`, `currentColor` (`ring-3` restores the width) |
| placeholder | configured `gray-400` | current text colour at 50% opacity |

**Severity** Info: a visual regression risk, not always wrong — plenty of designs want
`currentColor`. Skip the rule where the project restored the v3 defaults globally (a `@layer base`
`border-color` block, or `@theme { --default-ring-width: 3px; --default-ring-color: … }`); the check
for that block runs before the sweep (Method 7).

**Fix owner** `../migration/method.md` — per-site explicit colour vs one global restoration is a
migration trade-off.

### R-08 : Deterministic prop-to-class mapping

**Detect** — a component takes a `variant` / `color` / `size` / `tone` / `status` prop and builds the
class through a `switch`, a ternary chain, or a function returning differently-shaped strings per
branch. Not grep-complete: the agent reads the surrounding function and asks whether one object
literal could hold it. If yes, report.

**Severity** Info: works, renders, and rots. The same state gets styled two ways in two places, and
nobody can grep a state's full style surface. Detection: Method 8.

**Fix owner** `../design-system/method.md` for the closed variant set the map is drawn from, and
`../utility-soup/method.md` for the branches that duplicate utilities which should collapse into one
named layer. Shape of the target: one object literal, one key per state, a complete class string per
key, prop typed to the key union.

### R-09 : `twMerge` argument order

**Detect** — a `twMerge(…)` or `cn(…)` call where two arguments conflict on the same utility
dimension and the argument carrying the *default* sits last, since the last occurrence wins
(`twMerge('p-4', 'p-2')` → `p-2`). Consumer `className` passed before the component's own defaults is
the classic inversion.

**Severity** Info: the rule cannot know intent. Flag for human review, never auto-judge. Detection:
Method 9.

**Fix owner** `../utility-soup/method.md` — defaults first, overrides last, consumer prop is the
final argument.

### R-10 : Plugin missing default theme values

**Detect** — a file exporting a Tailwind plugin that calls `theme('<namespace>')` while its
second-argument config defines no `theme.extend.<namespace>`. **Severity** Warning: the plugin works
on the author's machine and emits zero classes for a consumer who never configured that namespace —
no error, just nothing.

No sibling module owns plugin authoring; the fix stays here.

```js
module.exports = plugin(
  function ({ matchUtilities, theme }) {
    matchUtilities({ tab: (v) => ({ tabSize: v }) }, { values: theme('tabSize') })
  },
  { theme: { tabSize: { 1: '1', 2: '2', 4: '4', 8: '8' } } }   // the defaults ship with the plugin
)
```

Under v4, a small plugin is usually a `@utility` block plus `@theme` variables in CSS instead; that
rewrite is a config concern. Detection: Method 10, worked case: Pattern 9.

## Report format

Plain text, one block per finding, machine-greppable at column zero.

```text
Tailwind Validator Report
=========================
Project state : v4 detected (tailwindcss@^4.0.5)
Scan scope    : src/ tailwind.config.js postcss.config.mjs
Files scanned : 8
Issues        : 6 (2 errors, 3 warnings, 1 info)

---

[ERROR] R-01 : dynamic class string
  File       : src/components/Tag.tsx:5
  Code       : className={`bg-${color}-100 text-${color}-800 px-2 py-1 rounded`}
  Cite       : ../dynamic-classes/method.md (static map)
  Suggested  : replace the interpolated fragment with a lookup keyed by `color`.

[WARNING] R-03 : forbidden v3 key in v4 config
  File       : tailwind.config.js:3
  Key        : safelist
  Cite       : ../migration/method.md (v3 config keys)
  Suggested  : move to `@source inline("bg-red-500 bg-blue-500")` in src/app.css.

... 1 more error, 2 more warnings, 1 info — full blocks, same format

---
Total : 6 issues
  Errors   : 2
  Warnings : 3
  Info     : 1
```

Per-finding fields, in this order:

| Field | Content |
|---|---|
| Header line | `[ERROR]`/`[WARNING]`/`[INFO]`, rule code, one-line name |
| `File` | repo-relative path and line number |
| `Code` / `Block` / `Key` | the offending snippet, verbatim |
| `Cite` | battery module path (`../<module>/method.md`), or `this module` for R-10 |
| `Suggested` | one line, the direction of the fix — never the applied fix |

Rules: severity tag always uppercase in brackets at column zero (CI greps it). `Cite` is a module
path, not a skill name, not a URL. Group by file, then rule, then line. On large trees the first
three files per rule get full blocks and the rest collapse into an `Additional occurrences` list
under one `Cite`. No footer flag promises a fixer: the validator has no autofix mode.

## CI integration

The pass is **advisory by default**. It reports; the pipeline keeps running.

```yaml
- name: Tailwind validator pass
  continue-on-error: true
  run: |
    # "run the validator pass" = this module's Procedure over the workspace.
    # Whatever harness executes the skill supplies the concrete command.
    <run the validator pass> > tailwind-report.txt
    cat tailwind-report.txt

- name: Gate on validator errors        # optional, opt-in
  if: always()
  run: |
    if grep -q '^\[ERROR\]' tailwind-report.txt; then
      echo "validator errors: $(grep -c '^\[ERROR\]' tailwind-report.txt)"
      exit 1
    fi
```

| Level | Gate? | Why |
|---|---|---|
| `[ERROR]` — R-00, R-01, R-02, orphaned-config R-03 | yes, when the team opts in | real production or build failure |
| `[WARNING]` — R-03, R-04, R-05, R-10 | never | intent-dependent, needs a human or the cited module |
| `[INFO]` — R-06, R-08, R-09 | never | judgement calls; gating them gets the step deleted |

Blocking on warning/info is how this check dies: one unavoidable Info turns the step into a
`continue-on-error` relic nobody reads.

## Sequencing with the modules

```text
run validator  →  open the cited module  →  fix there  →  re-run  →  errors = 0  →  warnings/info as time allows
```

The validator is not a substitute for the per-area modules; it is the index into them.

| Finding | Open first |
|---|---|
| R-00 version mismatch | `../migration/method.md` — settle the install, then re-run; a report built on the wrong gate is worthless |
| R-01 dynamic class | `../dynamic-classes/method.md` |
| R-02 scoped `@apply` | `../config/method.md` |
| R-03 v3 keys / orphaned config | `../migration/method.md` |
| R-04 custom class outside a layer | `../config/method.md` |
| R-05 variant order | `../migration/method.md` |
| R-06 bare border/ring/placeholder | `../migration/method.md` |
| R-08 prop-to-class shape | `../design-system/method.md`, then `../utility-soup/method.md` |
| R-09 merge order | `../utility-soup/method.md` |
| R-10 plugin defaults | `references/03-anti-patterns.md` (Pattern 9) |

Routing into the battery: module entry points are listed in `../SKILL.md`; the platform-neutral
styling levels outside the battery are `/styling` `retrofit` (existing mess, token migration with
parity evidence) and `/styling` `build` (new styling on any stack).

## Resources

- `references/01-detection-methods.md` — version heuristic in full, per-rule grep/rg commands,
  false-positive filters, scan-set skip list, report assembly
- `references/02-example-run.md` — fixture codebase, the report it must produce, what must *not* be
  flagged, and the follow-up loop
- `references/03-anti-patterns.md` — ten high-impact violations, each with why it survives review,
  the rule that catches it, and before/after

## Sources

- https://tailwindcss.com/docs/upgrade-guide#variant-stacking-order
- https://tailwindcss.com/docs/upgrade-guide#default-border-color
- https://tailwindcss.com/docs/upgrade-guide#default-ring-width-and-color
- https://tailwindcss.com/docs/upgrade-guide#new-default-placeholder-color
- https://tailwindcss.com/docs/upgrade-guide#using-a-javascript-config-file
- https://tailwindcss.com/docs/upgrade-guide#disabling-core-plugins
- https://tailwindcss.com/docs/upgrade-guide#using-apply-with-vue-svelte-or-css-modules
- https://tailwindcss.com/docs/functions-and-directives#reference-directive
- https://tailwindcss.com/docs/detecting-classes-in-source-files#safelisting-specific-utilities
- https://tailwindcss.com/docs/adding-custom-styles#adding-custom-utilities
- https://tailwindcss.com/docs/hover-focus-and-other-states#styling-direct-children
- https://tailwindcss.com/docs/box-shadow#adding-a-ring
- https://tailwindcss.com/docs/plugins
- https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.0.0
- https://github.com/dcastil/tailwind-merge
