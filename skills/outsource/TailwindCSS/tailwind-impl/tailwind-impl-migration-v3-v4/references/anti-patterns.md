# Anti-Patterns : Migration Traps

Each trap : symptom, root cause, fix, verification.

## Trap 1 : Running the Tool Without an Audit

### Symptom
Tool finishes, build succeeds, but the running app silently drops
classes used by dynamic templates. Pages render unstyled in
production after the safelist disappears.

### Root cause
The upgrade tool rewrites LITERAL class strings only. It cannot rewrite
class names assembled at runtime from string interpolation, JSON
config, or i18n bundles. Anything that used `safelist` to keep these
classes alive in v3 silently breaks because `safelist` is removed in
v4.

### Fix
Audit BEFORE the tool runs :

```bash
grep -rn "safelist" tailwind.config.js
grep -rn 'bg-opacity-\${' src
grep -rn 'class\s*=\s*[`"][^`"]*\${' src
```

For every dynamic class found, after the upgrade replace v3 `safelist`
entries with `@source inline("...")` in CSS :

```css
@source inline("bg-{red,green,blue}-{100,500,900}");
@source inline("{hover:,focus:,}text-zinc-{500,700,900}/{50,70,100}");
```

### Verification
Build the production bundle. Grep the output CSS for one rule from
each previously-safelisted class group :

```bash
npm run build
grep -c "bg-red-500\|bg-blue-500" dist/assets/*.css
```

All previously-safelisted selectors should appear.

## Trap 2 : Assuming the Codemod Handles Scoped @apply

### Symptom
After upgrade, Vue / Svelte / CSS-modules build fails with
"Cannot apply unknown utility class : <something>". The class works
fine when used directly in templates.

### Root cause
Scoped stylesheets compile in isolation in v4 and have no implicit
theme context. The codemod does NOT add `@reference` lines.

### Fix
For every scoped stylesheet using `@apply`, add `@reference` at the
top :

```vue
<style scoped>
  @reference "../app.css";
  h1 { @apply text-2xl font-bold text-red-500; }
</style>
```

Bulk fix script :

```bash
find src -name '*.vue' -o -name '*.svelte' -o -name '*.module.css' \
  | xargs grep -l '@apply' \
  | while read f; do
      echo "needs @reference : $f"
    done
```

### Verification
Build succeeds. Bundle size stays the same (proves `@reference` did
not duplicate CSS).

## Trap 3 : Forgetting the Shadow Scale Shift

### Symptom
After upgrade the UI looks slightly off ; shadows are smaller than
before, panels look flatter. No errors, no warnings.

### Root cause
Every size scale (`shadow`, `blur`, `drop-shadow`, `backdrop-blur`,
`rounded`) shifted by one in v4. v3 `shadow-sm` = v4 `shadow-xs` (one
level smaller). v3 `shadow` (no suffix) = v4 `shadow-sm`. The codemod
catches literal class strings, but designers' Figma specs still
reference v3 scale names.

### Fix
Either accept the new defaults (smaller shadows are an intentional
v4 design refresh) or restore v3 sizes via theme overrides :

```css
@theme {
  --shadow-sm: var(--shadow-default);   /* match old v3 shadow */
}
```

Or rewrite component-by-component as you encounter them.

### Verification
Visual diff with Playwright / Percy. Shadow regions in the diff are
the v4 scale change. Confirm intentional.

## Trap 4 : Missing Default Border Colour

### Symptom
Pages render with garish or wrong-coloured borders after upgrade.
Borders that were `gray-200` are now black (inherited `currentColor`).

### Root cause
v4 changed the default `border` colour from `gray-200` to
`currentColor`. Every `class="border"` (no explicit colour) inherits
the parent text colour, which is rarely `gray-200`.

### Fix
Either restore the v3 default globally :

```css
@layer base {
  *,
  ::after,
  ::before,
  ::backdrop,
  ::file-selector-button {
    border-color: var(--color-gray-200, currentColor);
  }
}
```

Or grep for bare `border` and add explicit colours :

```bash
grep -rEn 'class="[^"]*\bborder\b[^-/]' src
```

### Verification
Visual regression diff highlights every changed border. Either
intentional (added explicit colour) or restored by the `@layer base`
block.

## Trap 5 : Ring Width Default Change

### Symptom
Focus rings around inputs and buttons are 1px thin and the wrong
colour after upgrade. Used to be the chunky blue ring developers
recognise.

### Root cause
v3 `ring` (no suffix) = 3px `blue-500`. v4 `ring` = 1px `currentColor`.

### Fix
Either rewrite usages :

```html
<!-- v3 -->
<button class="focus:ring focus:ring-blue-500"></button>

<!-- v4 -->
<button class="focus:ring-3 focus:ring-blue-500"></button>
```

Or restore globally :

```css
@theme {
  --default-ring-width: 3px;
  --default-ring-color: var(--color-blue-500);
}
```

### Verification
Tab through focusable elements. Rings should look as before.

## Trap 6 : Variant-Stacking Order Flip Not Caught

### Symptom
Compound variants like `first:*:pt-0` silently apply to the wrong
elements after upgrade. The first list item gets padding instead of
losing it, or vice versa.

### Root cause
v4 reads variant stacks left-to-right ; v3 read right-to-left. The
codemod catches the most common patterns but compound custom variants
slip through.

### Fix
Audit every class with two or more chained variants where ORDER
matters :

```bash
grep -rnE 'class="[^"]*\b\w+:\w+:' src
```

Manually flip each occurrence :

```html
<!-- v3 -->
<ul class="first:*:pt-0 last:*:pb-0">

<!-- v4 -->
<ul class="*:first:pt-0 *:last:pb-0">
```

### Verification
Render a list. Inspect the first and last items in DevTools. Padding
must be on the correct items.

## Trap 7 : Hover Effects Dead on Touch Devices

### Symptom
Buttons that highlight on hover desktop work fine, but on
phone/tablet a tap does NOT trigger the hover styles between tap-down
and tap-up.

### Root cause
v4 wraps `hover:` in `@media (hover: hover)`. Touch devices without
real hover capability skip the rule.

### Fix
For "tap-flash" interactions, use `active:` instead of `hover:`. For
projects that want v3 behaviour everywhere :

```css
@import "tailwindcss";
@custom-variant hover (&:hover);
```

### Verification
Tap a button on a mobile device or DevTools touch emulation. Active
or hover style appears during the tap.

## Trap 8 : Forgetting Hidden-Attribute Behavior Change

### Symptom
Elements with the `hidden` HTML attribute become visible when they
have a `block` / `flex` / `grid` Tailwind class on them. v3 hid them ;
v4 shows them.

### Root cause
v3 Preflight overrode the `hidden` attribute with `display: none !important`. v4 removed that override. Display utilities now win
over the attribute.

### Fix
Either remove the `hidden` attribute when you want the element shown,
or restore the v3 override :

```css
@layer base {
  [hidden]:where(:not([hidden="until-found"])) {
    display: none !important;
  }
}
```

### Verification
An element with `<div hidden class="block">` should be hidden if you
applied the v3 override, visible if not.

## Trap 9 : corePlugins Silently Ignored

### Symptom
A v3 project disabled `float`, `clear`, `boxSizing`, or other
utilities via `corePlugins: { float: false, ... }`. After upgrade,
those classes appear in user code (autocomplete suggestions, copy-paste
from docs) and the original intent (forbid floats) is lost.

### Root cause
`corePlugins` is removed in v4 with no replacement. The build does NOT
warn ; the config is silently ignored.

### Fix
Replace with one of :

1. ESLint rule banning specific utilities :
   ```js
   // .eslintrc
   rules: {
     'tailwindcss/no-custom-classname': [
       'error',
       { whitelist: ['^(?!(float|clear)-).*$'] },
     ],
   }
   ```
2. `@source not "path"` to exclude files where forbidden utilities
   might appear.
3. CI grep check :
   ```bash
   ! grep -rEn 'class="[^"]*\bfloat-' src
   ```

### Verification
Lint runs and fails on banned utility usage.

## Trap 10 : resolveConfig Removal Breaks Runtime Code

### Symptom
After upgrade, app crashes with `Cannot find module
'tailwindcss/resolveConfig'`. Often in Storybook addons, design-token
exporters, or theme-reading utilities.

### Root cause
v4 removed `resolveConfig`. The function read the full v3 config
object ; v4 stores the same data as CSS variables, accessible only at
runtime through the DOM.

### Fix
Replace each call site :

```js
// before
import resolveConfig from 'tailwindcss/resolveConfig'
import config from '../../tailwind.config.js'
const full = resolveConfig(config)
const red = full.theme.colors.red['500']

// after
const red = getComputedStyle(document.documentElement)
  .getPropertyValue('--color-red-500')
  .trim()
```

For Node-side code with no DOM, parse the entry CSS file with PostCSS
and extract the `:root { ... }` declarations, or write a build step
that emits `tokens.json` alongside the CSS.

### Verification
Run the affected code path. No `Cannot find module` error. The
returned colour value matches the design.
