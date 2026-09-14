# Anti-Patterns : Utility Soup

Common mistakes when fighting long class lists, the symptom, the cause, and the fix.

---

## AP-1 : Extracting after the first duplicate

**Symptom :** Codebase has 40 single-use "components" (Button1, Card1,
Wrapper1) that wrap minor variations of utility lists.

**Cause :** Reacting to "this looks similar" rather than measuring
actual reuse. Two duplicates is not enough signal.

**Fix :** ALWAYS wait for the third use. Two copies can stay inline.
On the third, identify the shared shape and extract.

---

## AP-2 : Never extracting (copy-paste forever)

**Symptom :** A 30-utility button definition appears in 12 files.
Updating the design means editing 12 places.

**Cause :** Treating utility-first as "never abstract".

**Fix :** Apply the 3-use rule. Three or more copies of the same
pattern = extract a component (or partial, or @apply class).

---

## AP-3 : Using @apply when a component is available

**Symptom :** `.btn-primary { @apply ... }` definitions in `.css`
alongside React/Vue/Svelte components that already encapsulate the
same buttons.

**Cause :** Misreading the "extract to @apply" advice as a universal
default. @apply is for non-framework contexts.

**Fix :** Replace `.btn-primary` with a `<Button>` component. Delete
the @apply rule.

---

## AP-4 : Unsorted classes across the team

**Symptom :** Git diffs show class reordering noise. Merge conflicts
on class strings because two authors used different orders.

**Cause :** No formatter enforced on save.

**Fix :** Install `prettier-plugin-tailwindcss`, configure
`.prettierrc.json`, run `prettier --write .` once to normalize the
codebase, then enforce in pre-commit via lint-staged or husky.

---

## AP-5 : Prettier and Headwind both running

**Symptom :** Save the file. Prettier sorts one way. Headwind sorts
another. You re-save. They fight forever.

**Cause :** Two tools, two sort orders, both run on save.

**Fix :** Disable one. Prettier is the build-time canonical formatter ;
disable Headwind unless your team explicitly prefers it.

```json
{ "headwind.runOnSave": false }
```

---

## AP-6 : ESLint flags every custom class

**Symptom :** `no-custom-classname` errors on every project-specific
class (`.btn-primary`, `.container-narrow`, `.swiper-container`).

**Cause :** No `whitelist` configured.

**Fix :** Add the custom class names :

```js
settings: {
  tailwindcss: {
    whitelist: ["btn-primary", "container-narrow", "swiper-container"],
  },
}
```

---

## AP-7 : Disabling no-custom-classname globally

**Symptom :** Team disables the rule project-wide to silence noise.
Real typos (`bg-bule-500` instead of `bg-blue-500`) slip through.

**Cause :** Reacting to false positives by removing all positives.

**Fix :** Use `whitelist` for known custom classes. Keep the rule on
to catch typos and outdated class names.

---

## AP-8 : Not listing class-building helpers in Prettier

**Symptom :** Class strings inside `clsx(...)`, `cva(...)`,
`twMerge(...)` remain unsorted.

**Cause :** `tailwindFunctions` not set.

**Fix :**

```json
{ "tailwindFunctions": ["clsx", "cva", "tw", "twMerge", "classnames"] }
```

ALWAYS keep this list current as your project adopts new helpers.

---

## AP-9 : Wrapping every JSX element in a component

**Symptom :** Components named `Div1`, `Wrapper2`, `Container3`
appear ; each wraps a single styled div used in one place.

**Cause :** Conflating "extract on third use" with "extract anything
nontrivial".

**Fix :** Keep single-use markup inline. Only extract WHEN the same
shape appears 3+ times OR there is a strong semantic reason
(accessibility role, shared interactive behavior, runtime variants).

---

## AP-10 : @apply for a single class with two utilities

**Symptom :** `.bold-title { @apply text-2xl font-bold; }` used in
one place.

**Cause :** Reflex extraction.

**Fix :** Use the utilities inline :

```diff
- <h1 class="bold-title">Welcome</h1>
+ <h1 class="text-2xl font-bold">Welcome</h1>
```

Delete the CSS rule.

---

## AP-11 : Ignoring no-contradicting-classname errors

**Symptom :** Production CSS shows `p-2 p-3` or `text-red-500 text-blue-500`.
Layout flickers as the cascade resolves last-declared.

**Cause :** Conditional class merging without `tailwind-merge`.

**Fix :** Wrap the merge in `twMerge` :

```diff
- className={`p-2 ${large ? "p-3" : ""}`}
+ className={twMerge("p-2", large && "p-3")}
```

`twMerge` resolves the conflict deterministically.

---

## AP-12 : Multi-line class strings under 15 utilities

**Symptom :** Short class lists wrapped in `className="\n  flex\n  ..."`
template strings for "readability".

**Cause :** Multi-line formatting applied as a style preference, not
where it solves a real readability problem.

**Fix :** Multi-line is for genuine soup (25+ utilities). For shorter
lists, single-line + Prettier sorting is enough.

---

## AP-13 : Naming components after their utilities

**Symptom :** Component `RoundedBlueButtonWithShadow` exists in a
design system.

**Cause :** Naming after visuals instead of semantics.

**Fix :** Name by intent : `Button`, `PrimaryAction`, `SubmitButton`.
Visuals belong inside the component, not in its name. When visuals
change, the name stays correct.

---

## AP-14 : Premature design tokens

**Symptom :** Custom theme tokens like `--color-button-primary` and
`--spacing-button-padding` defined before any button exists.

**Cause :** Designing the design system in the abstract.

**Fix :** Build buttons with utilities first. After 3+ exist, look
for repeated values and promote those to tokens. Drive token names
from observed usage.

---

## AP-15 : Class string concatenation without merge

**Symptom :** Component accepts `className` prop and concatenates it :
`<div className={`p-4 ${className}`}>`. Consumer passes `p-8`. Result
is `p-4 p-8`, leaving the cascade to decide. Works locally, breaks in
specific CSS bundling orders.

**Cause :** Naive string join.

**Fix :** Use `twMerge` :

```diff
- <div className={`p-4 ${className}`} />
+ <div className={twMerge("p-4", className)} />
```

---

## AP-16 : Forgetting tailwindConfig / tailwindStylesheet path

**Symptom :** Prettier sorts wrong, missing custom utilities defined
in your theme.

**Cause :** Plugin defaults to looking for `tailwind.config.js` next
to `.prettierrc` ; if your project keeps configs elsewhere or uses
v4 CSS-first config, the plugin cannot resolve custom tokens.

**Fix :**

v3 :

```json
{ "tailwindConfig": "./packages/web/tailwind.config.ts" }
```

v4 :

```json
{ "tailwindStylesheet": "./packages/web/src/app.css" }
```

---

## AP-17 : `// eslint-disable-next-line tailwindcss/...` everywhere

**Symptom :** Many disable comments before JSX lines with long classes.

**Cause :** Treating ESLint warnings as noise.

**Fix :** Address the root issue. If the warning is `classnames-order`,
let Prettier sort. If it is `no-custom-classname`, add to whitelist.
If it is `no-contradicting-classname`, fix the conflict with `twMerge`.

---

## AP-18 : `no-arbitrary-value` blocks legitimate one-offs

**Symptom :** Team turns on `no-arbitrary-value` strictly, then has
to disable it whenever an exact design value (`h-[42vh]`) is needed.

**Cause :** Over-restrictive design-system enforcement.

**Fix :** Keep `no-arbitrary-value` OFF by default. Turn on only when
the design system is mature AND every exception goes through a
review process.

---

## AP-19 : Mixing class-builder helpers

**Symptom :** Codebase uses `clsx` in some files, `classnames` in
others, plain template strings in a third set.

**Cause :** No team convention.

**Fix :** Pick ONE class builder. Document it. Migrate the others
with a codemod or grep + manual editing. Update `tailwindFunctions`
accordingly.

---

## AP-20 : Auto-fix on CI

**Symptom :** Developers commit unformatted code ; CI auto-fixes and
pushes back. PR history becomes noisy.

**Cause :** CI runs `prettier --write` and `eslint --fix` instead of
`--check`.

**Fix :**

```yaml
- run: npm run format:check
- run: npm run lint   # without --fix
```

Move auto-fix to a pre-commit hook so developers fix locally :

```json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": ["prettier --write", "eslint --fix"]
  }
}
```
