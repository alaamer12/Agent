# Anti-Patterns : v3 to v4 Migration

Common upgrade mistakes, the symptom, the cause, and the fix.

---

## AP-1 : Trusting the codemod's silence

**Symptom :** `npx @tailwindcss/upgrade` finishes with no errors.
Deployed site has subtle visual differences : missing borders, thin
focus rings, slightly softer shadows.

**Cause :** The codemod handles renames and removals. It does NOT
detect default-behavior changes (border-color, ring-width) because
those produce no syntactic delta.

**Fix :** ALWAYS run a visual regression suite after the codemod.
Audit borders, rings, shadows manually using the trap catalog.

---

## AP-2 : Variant order swapped mechanically without semantic check

**Symptom :** Buttons that should hide on hover suddenly always hide,
or vice versa. The class string looks correct but means the opposite.

**Cause :** v3 evaluated stacked variants right-to-left ;
v4 evaluates left-to-right. Mechanical swap without thinking through
"what does this READ as in English" breaks intent.

**Fix :** Read each stacked variant aloud :

```html
*:first:pt-0  →  "every direct child, when first, padding-top zero"
```

If the read-aloud does not match the intended behavior, the order is wrong.

---

## AP-3 : Keeping the @layer base border-color shim forever

**Symptom :** Years later, the codebase still carries the v3-recovery
border-color shim. New contributors do not realize the v4 default is
`currentColor`. They write `border` expecting gray-200, and it works
locally because of the shim.

**Cause :** Treating a migration aid as a permanent behavior.

**Fix :** Plan removal. Add a TODO with a target date. Audit all
`border` usage. Replace with explicit `border-gray-200` (or your
project's token). Remove the shim.

---

## AP-4 : Ignoring ring-width default change

**Symptom :** Focus rings disappear or look unbalanced. Accessibility
audits flag insufficient focus indicators.

**Cause :** v3 default ring width was 3px. v4 default is 1px. Code
that wrote `focus:ring focus:ring-blue-500` got a 3px ring in v3 and
gets a 1px ring in v4.

**Fix :** Replace bare `ring` with `ring-3` everywhere :

```diff
- <button class="focus:ring focus:ring-blue-500">
+ <button class="focus:ring-3 focus:ring-blue-500">
```

Or update the design system to embrace 1px rings.

---

## AP-5 : Manual shadow rename without test

**Symptom :** UI elements that used `shadow-sm` now feel different.
Some look right, others wrong.

**Cause :** The shift moves `shadow-sm` to `shadow-xs`. The codemod
renames automatically, BUT visual reviewers may have memorized "this
button uses shadow-sm" and not noticed the new look matches the
original CSS values.

**Fix :** Visually diff every component using shadows after the
upgrade. The CSS values are identical ; only the names changed. If a
component looks different, the rename was applied to the wrong place.

---

## AP-6 : Forgetting bg-opacity removal

**Symptom :** Overlay divs are fully opaque despite `bg-opacity-50`
in the class list.

**Cause :** v4 removed `bg-opacity-*`, `text-opacity-*`, etc. The
codemod converts `bg-COLOR bg-opacity-N` to `bg-COLOR/N`, but does
NOT handle templated class names :

```tsx
className={`bg-${color} bg-opacity-${opacity}`}
```

**Fix :** Convert templated class building to the slash modifier :

```tsx
className={`bg-${color}/${opacity}`}
```

If the templated form is unavoidable, add the resolved class to
`@source inline`.

---

## AP-7 : Prefix flip leftovers

**Symptom :** Some elements work, others have unstyled appearance.

**Cause :** The codemod missed prefix references in template strings,
data attributes, or test selectors :

```ts
expect(button.className).toContain("tw-flex")   // OUTDATED
```

**Fix :** Grep for the v3 prefix pattern :

```bash
grep -rEn '\btw-(flex|grid|block|hidden|p-|m-|w-|h-)' .
```

Replace each occurrence with the v4 form. Include test files, stories,
documentation.

---

## AP-8 : !important flip leftovers

**Symptom :** Some `!important` overrides still work, others stopped.

**Cause :** The codemod found the obvious `!class` cases. It misses
template strings and conditional class builders :

```ts
classNames("base", isPriority && "!font-bold")   // OUTDATED
```

**Fix :** Grep for the v3 syntax :

```bash
grep -rEn '["'\''`!][!][a-z]+-' .
```

Flip every occurrence.

---

## AP-9 : Using outline-none expecting v3 behavior

**Symptom :** Focus outlines disappear entirely in v4. Accessibility
audit flags missing focus indication.

**Cause :** v4's `outline-none` literally sets `outline-style: none`.
v3's `outline-none` actually applied an invisible outline that still
satisfied forced-colors mode.

**Fix :** Replace with `outline-hidden` (the new name for v3 behavior) :

```diff
- <input class="focus:outline-none focus:ring-2" />
+ <input class="focus:outline-hidden focus:ring-2" />
```

`outline-none` should be reserved for elements that genuinely have no
focus indication.

---

## AP-10 : Arbitrary [--var] left unchanged

**Symptom :** Custom property values silently fall back to default
(transparent / 0). No build error.

**Cause :** v4 changed `bg-[--brand]` to `bg-(--brand)`. The square-
bracket form is still parsed but treated as a raw value, not a
CSS-variable reference.

**Fix :** Grep and replace :

```bash
grep -rEn '\[--[a-z]' src/
```

Convert each `[--var]` to `(--var)`.

---

## AP-11 : Comma in arbitrary grid/object values

**Symptom :** `grid-cols-[max-content,auto]` produces invalid CSS in v4.

**Cause :** v3 substituted commas for spaces in arbitrary values. v4
removed that substitution ; use underscores instead.

**Fix :**

```diff
- <div class="grid-cols-[max-content,auto]">
+ <div class="grid-cols-[max-content_auto]">
```

---

## AP-12 : transform-none reset still in code

**Symptom :** Hover handlers that used `hover:transform-none` to reset
transforms now do nothing.

**Cause :** v4 splits transform into individual properties. The bulk
`transform` utility (and its `-none` reset) no longer exists.

**Fix :** Reset each individual property :

```diff
- <button class="rotate-45 scale-150 focus:transform-none">
+ <button class="rotate-45 scale-150 focus:rotate-none focus:scale-none">
```

---

## AP-13 : @layer utilities for custom utilities

**Symptom :** Build succeeds but the custom utility never appears in
the output CSS.

**Cause :** v4 still understands `@layer utilities { .tab-4 { tab-size: 4; } }`
but the preferred API is `@utility`. For functional utilities (with
variants, modifiers), the old `@layer utilities` form does not work.

**Fix :** Migrate :

```diff
- @layer utilities {
-   .tab-4 { tab-size: 4; }
- }
+ @utility tab-4 {
+   tab-size: 4;
+ }
```

For dynamic ranges, use the parameter helpers :

```css
@utility tab-* {
  tab-size: --value(integer);
}
```

---

## AP-14 : Keeping safelist in v4 JS config

**Symptom :** `safelist` entries in `tailwind.config.js` do not appear
in the v4 output.

**Cause :** v4 ignores `safelist` from JS config.

**Fix :** Move to `@source inline` in the entry CSS :

```diff
  // tailwind.config.js
- safelist: ["bg-red-500", "bg-green-500"],

  /* app.css */
+ @source inline "{bg-red-500,bg-green-500}";
```

---

## AP-15 : corePlugins disable still in v4 JS config

**Symptom :** Trying to disable preflight via `corePlugins: { preflight: false }`
in v4 does nothing.

**Cause :** v4 removed the `corePlugins` option.

**Fix :** Selectively import Tailwind layers :

```css
/* skip preflight */
@import "tailwindcss/theme.css";
@import "tailwindcss/utilities.css";
```

Or override preflight rules in `@layer base`.

---

## AP-16 : Hover-only state with no fallback

**Symptom :** Touch users on tablets cannot trigger hover-only states
(menu opens, tooltip shows, button highlights).

**Cause :** v4 wraps `hover:` in `@media (hover: hover)`. Touch
devices report no hover capability, so the variant never fires.

**Fix :** Pair hover with active and/or focus :

```diff
- <button class="bg-blue-500 hover:bg-blue-700">
+ <button class="bg-blue-500 hover:bg-blue-700 active:bg-blue-800">
```

For menus and tooltips, switch to click / focus interaction.

---

## AP-17 : Bridging @config indefinitely

**Symptom :** Project has v4 entry CSS importing `tailwindcss` AND a
`@config` directive pointing at the old `tailwind.config.js`. Years
later, the bridge is still there.

**Cause :** Migration aid treated as permanent.

**Fix :** Plan removal :

1. Migrate `theme.extend` to `@theme` in CSS.
2. Migrate `plugins` to `@plugin` in CSS.
3. Migrate `content` to `@source` in CSS.
4. Delete `@config` line and `tailwind.config.js`.

---

## AP-18 : Forgetting to update browser-support matrix

**Symptom :** Production users on Safari 14 see broken styles. The
test suite passes because CI uses Chrome 120.

**Cause :** v4 requires Safari 16.4+. The browser-support assumption
silently changed.

**Fix :** Update browserslist :

```json
{
  "browserslist": [
    "safari >= 16.4",
    "chrome >= 111",
    "firefox >= 128"
  ]
}
```

If the project's audience requires older browsers, NEVER upgrade to
v4 until the audience moves.

---

## AP-19 : Ignoring theme() dot-notation deprecation

**Symptom :** `theme(spacing.4)` calls produce undefined values or
build errors.

**Cause :** v4 replaced dot notation with CSS-variable names.

**Fix :**

```diff
- @media (width >= theme(screens.xl)) {
+ @media (width >= theme(--breakpoint-xl)) {
```

```diff
- padding: theme(spacing.16);
+ padding: theme(--spacing-16);
```

---

## AP-20 : Skipping audit on a "small" upgrade

**Symptom :** "We only have 5 pages, the codemod will be fine." Three
weeks later, a designer notices borders are missing throughout.

**Cause :** Small codebases hide visual regressions because the
regression suite is shallow.

**Fix :** ALWAYS run the audit script, regardless of codebase size :

```bash
bash scripts/audit-tailwind-v4.sh
```

ALWAYS visually diff every page that ships. The audit takes minutes ;
the visual fix after a missed regression takes days.
