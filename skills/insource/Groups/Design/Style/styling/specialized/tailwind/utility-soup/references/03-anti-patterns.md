# Anti-patterns — twenty ways to fight soup and lose

Each entry: what it looks like in the code, why it happens, the fix. The four that account for most
damage are marked; they are also summarised inline in `../method.md`.

## A1 — Extracting after the first duplicate *(premature extraction)*

**Symptom:** the codebase has 40 single-use "components" (`Button1`, `Card1`, `Wrapper1`) each
wrapping a minor variation of a utility list.

**Cause:** reacting to "this looks similar" instead of measuring actual reuse. Two duplicates is not
enough signal to know the abstraction boundary.

**Fix:** wait for the third use. Two copies stay inline; on the third, identify the shared shape and
extract only that shape.

## A2 — Never extracting (copy-paste forever)

**Symptom:** one 30-utility button definition appears in 12 files; a design change is a 12-file edit.

**Cause:** reading "utility-first" as "never abstract".

**Fix:** apply the 3-use rule. Three or more copies = component, or partial, or `@apply` class when
there is no framework.

## A3 — `@apply` when a component is available *(@apply everywhere)*

**Symptom:** `.btn-primary { @apply ... }` in a CSS file, alongside React/Vue/Svelte components that
already encapsulate the same buttons.

**Cause:** treating "extract to `@apply`" as a universal default instead of the no-framework branch
of the decision matrix.

**Fix:** replace `.btn-primary` with a `<Button>` component and delete the CSS rule. Keep `@apply`
for markup you cannot componentise.

## A4 — `@apply` for a single class with two utilities

**Symptom:** `.bold-title { @apply text-2xl font-bold; }`, used once.

**Cause:** reflex extraction.

**Fix:** inline it and delete the rule:

```diff
- <h1 class="bold-title">Welcome</h1>
+ <h1 class="text-2xl font-bold">Welcome</h1>
```

## A5 — Unsorted classes across the team *(class-order drift)*

**Symptom:** diffs show pure reordering noise; merge conflicts on class strings because two authors
used two different orders.

**Cause:** no formatter enforced on save; order decided per author.

**Fix:** install `prettier-plugin-tailwindcss`, run `prettier --write .` once in its own commit,
then enforce it in a pre-commit hook and with `format:check` in CI.

## A6 — Prettier and Headwind both running

**Symptom:** save the file, one tool sorts; save again, the other re-sorts. The order oscillates.

**Cause:** two sorters with two different default orders, both on save.

**Fix:** pick one. Prettier is the build-time canonical sorter, so:

```json
{ "headwind.runOnSave": false }
```

## A7 — ESLint flags every custom class *(unconfigured whitelist)*

**Symptom:** `no-custom-classname` errors on `.btn-primary`, `.container-narrow`,
`.swiper-container` — every project class.

**Cause:** the plugin was installed without `whitelist`.

**Fix:**

```js
settings: {
  tailwindcss: {
    whitelist: ["btn-primary", "container-narrow", "swiper-container"],
  },
}
```

## A8 — Disabling `no-custom-classname` globally

**Symptom:** the rule is switched off repo-wide to silence noise; `bg-bule-500` ships and does
nothing.

**Cause:** removing all positives to kill the false positives.

**Fix:** keep the rule on, add known custom classes to `whitelist`, and reserve a per-file disable
for third-party widget classes that churn between library versions.

## A9 — Class builders missing from `tailwindFunctions`

**Symptom:** class strings inside `clsx(...)`, `cva(...)`, `twMerge(...)` stay unsorted while the
file "passes" formatting.

**Cause:** nothing is auto-detected; the wrappers were never listed.

**Fix:**

```json
{ "tailwindFunctions": ["clsx", "cva", "tw", "twMerge", "classnames"] }
```

Keep the list current as the project adopts helpers — and mirror it in ESLint's `callees`, whose
defaults do NOT include `cva`, `twMerge`, or a local `cn`.

## A10 — Missing `tailwindConfig` / `tailwindStylesheet` path

**Symptom:** sorting is subtly wrong and custom utilities defined in the theme sort as unknown
classes.

**Cause:** the plugin looks for `tailwind.config.js` next to the Prettier config and falls back to
Tailwind defaults; on v4 there is no such file to find at all.

**Fix:** v3 `"tailwindConfig": "./packages/web/tailwind.config.ts"`; v4
`"tailwindStylesheet": "./packages/web/src/app.css"` (the sheet holding `@import "tailwindcss"`).
Paths resolve relative to the Prettier config.

## A11 — Wrapping every JSX element in a component

**Symptom:** `Div1`, `Wrapper2`, `Container3` — each wrapping one styled `div` used in one place.

**Cause:** conflating "extract on third use" with "extract anything nontrivial".

**Fix:** keep single-use markup inline. Extract when the same shape appears 3+ times, or for a
strong semantic reason: an accessibility role, shared interactive behaviour, runtime variants.

## A12 — Multi-line class strings under 15 utilities

**Symptom:** four-class lists written as `className="\n  flex\n  items-center\n"`.

**Cause:** multi-line treated as a style preference rather than a remedy for a real readability
problem.

**Fix:** multi-line is for genuine soup (25+). Shorter lists: one line plus the sorter.

## A13 — Ignoring `no-contradicting-classname`

**Symptom:** `p-2 p-3` or `text-red-500 text-blue-500` reach production; layout flickers as the
cascade resolves whichever was emitted last.

**Cause:** conditional class merging without a merge step.

**Fix:**

```diff
- className={`p-2 ${large ? "p-3" : ""}`}
+ className={twMerge("p-2", large && "p-3")}
```

## A14 — Class-string concatenation without merge

**Symptom:** a component does `` <div className={`p-4 ${className}`}> ``; a consumer passes `p-8`,
the result is `p-4 p-8`, and the winner depends on stylesheet order. Works locally, breaks when the
bundle order moves.

**Cause:** naive string join where merge semantics were needed.

**Fix:**

```diff
- <div className={`p-4 ${className}`} />
+ <div className={twMerge("p-4", className)} />
```

## A15 — Naming components after their utilities

**Symptom:** `RoundedBlueButtonWithShadow` in a design system.

**Cause:** naming after appearance instead of intent.

**Fix:** name for what it does — `Button`, `PrimaryAction`, `SubmitButton`. Visuals live inside the
component; when the visuals change, the name stays correct.

## A16 — Premature design tokens

**Symptom:** `--color-button-primary` and `--spacing-button-padding` defined before a single button
exists.

**Cause:** designing the design system in the abstract.

**Fix:** build with utilities first; after 3+ real usages, promote the values that actually repeat
and name them from observed usage. Scale design and namespace rules belong to the `design-system`
module (`../../design-system/method.md`).

## A17 — `// eslint-disable-next-line tailwindcss/...` everywhere

**Symptom:** disable comments scattered above every long class list.

**Cause:** treating lint warnings as noise instead of signals.

**Fix:** answer the rule. `classnames-order` → let the sorter run. `no-custom-classname` → whitelist.
`no-contradicting-classname` → fix the conflict with `twMerge`. A disable survives only where the
classes are not yours (A8).

## A18 — `no-arbitrary-value` on a young design system

**Symptom:** the rule is enabled strictly, then switched off the first time an exact
`h-[42vh]` is required.

**Cause:** over-restrictive enforcement before the system can express every case.

**Fix:** keep it off by default. Turn it on only when the design system is mature AND every
exception goes through review.

## A19 — Mixing class-builder helpers

**Symptom:** `clsx` in some files, `classnames` in others, template strings in a third set.

**Cause:** no team convention.

**Fix:** pick ONE builder, document it, migrate the rest (codemod or grep), and update
`tailwindFunctions` / `callees` to match. A mixed convention guarantees a permanently unsorted half.

## A20 — Auto-fix in CI

**Symptom:** unformatted code merges; CI rewrites files and the PR history fills with formatter
commits.

**Cause:** CI runs `prettier --write` and `eslint --fix`.

**Fix:** check in CI, fix on the developer's machine:

```yaml
- run: npm run format:check
- run: npm run lint          # no --fix
```

```json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": ["prettier --write", "eslint --fix"]
  }
}
```
