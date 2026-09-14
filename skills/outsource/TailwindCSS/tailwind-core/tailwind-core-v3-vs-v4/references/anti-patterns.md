# Upgrade Anti-Patterns : v3 to v4

Every entry below maps a real upgrade failure to its root cause and the
verified fix. Sources : official upgrade guide
(https://tailwindcss.com/docs/upgrade-guide) and the cited issues in
SOURCES.md.

## AP-1 : Leaving `@tailwind` directives in v4

### Symptom
Build fails or produces empty CSS after upgrading to v4.

### Root cause
v4 removed `@tailwind base`, `@tailwind components`, and `@tailwind utilities`
entirely. The replacement is a single `@import "tailwindcss";`.

### NEVER
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### ALWAYS
```css
@import "tailwindcss";
```

The `npx @tailwindcss/upgrade` codemod handles this, but custom multi-file
CSS pipelines often miss one of the three directives. Grep for `@tailwind `
across the codebase before declaring the upgrade done.

## AP-2 : `@apply` failing in scoped component styles

### Symptom
After upgrading a Vue, Svelte, or CSS-modules project, build error :
`Cannot apply unknown utility class : px-4` (or any other class) inside
a scoped `<style>` block.

### Root cause
v3 implicitly included theme context in every scoped block. v4 compiles
each block in isolation. The theme is invisible unless the block explicitly
references it.

### NEVER
```vue
<style scoped>
.btn { @apply px-4 py-2 bg-blue-500 text-white; }
</style>
```

### ALWAYS
```vue
<style scoped>
@reference "../app.css";
.btn { @apply px-4 py-2 bg-blue-500 text-white; }
</style>
```

The path points to the file that contains `@import "tailwindcss"`. A short
alias works too : `@reference "tailwindcss";` if the engine can resolve it.

Source : https://github.com/tailwindlabs/tailwindcss/issues/16346

## AP-3 : Expecting `corePlugins: { float: false }` to still work

### Symptom
After upgrade, disabled utilities (float, container, transitions, etc.) are
back in the generated CSS even though the v3 config disabled them.

### Root cause
v4 removed `corePlugins` entirely. There is NO direct replacement. The
`@config "./tailwind.config.js";` shim loads the legacy file but silently
ignores `corePlugins`, `safelist`, and `separator`.

### NEVER assume legacy `corePlugins` is honoured in v4

### Workarounds
- Refactor source to not use the unwanted utilities (and rely on tree-shaking).
- Use `@source not "path"` to exclude files that would generate them.
- Override the utility with a no-op via `@utility float-left { float: unset; }`.
- STAY on v3.4 if disabling utilities is non-negotiable.

Source : https://tailwindcss.com/docs/upgrade-guide

## AP-4 : Regex `safelist` patterns left in v3 config under `@config`

### Symptom
Dynamic classes generated at runtime (e.g. `bg-${color}-500`) are missing
from the bundle in production even though `safelist` patterns matched them
in v3.

### Root cause
The legacy `@config` loader does not process `safelist` in v4. The
replacement is `@source inline("...")` with brace expansion, written in
CSS not JS.

### NEVER
```js
// tailwind.config.js loaded via @config
module.exports = {
  safelist: [{ pattern: /bg-(red|blue|green)-(100|500|900)/ }],
}
```

### ALWAYS
```css
@import "tailwindcss";
@source inline("bg-{red,blue,green}-{100,500,900}");
```

Brace expansion supports ranges : `@source inline("p-{1..12}");` generates
`p-1` through `p-12`. Variants prefix : `@source inline("{hover:,focus:,}bg-{red,blue}-500");`.

Source : https://github.com/tailwindlabs/tailwindcss/issues/18136 and
https://tailwindcss.com/docs/detecting-classes-in-source-files

## AP-5 : `resolveConfig()` calls at runtime

### Symptom
After upgrade, runtime JS that read Tailwind tokens (charting libs, animation
configs, design-token exports) throws : `Cannot find module 'tailwindcss/resolveConfig'`.

### Root cause
v4 removed the `resolveConfig` export. Theme tokens live in CSS variables on
the root element ; read them via the DOM at runtime.

### NEVER
```js
import resolveConfig from 'tailwindcss/resolveConfig'
import config from '../tailwind.config.js'
const colours = resolveConfig(config).theme.colors
```

### ALWAYS
```js
function tokenValue(name) {
  return getComputedStyle(document.documentElement)
    .getPropertyValue(name).trim()
}
const brandColor = tokenValue('--color-brand')
const md = tokenValue('--breakpoint-md')
```

For SSR or build-time access, define brand tokens in a shared JS module
that BOTH the stylesheet (via `theme(--my-token)`) and runtime read from.

## AP-6 : Visual borders disappearing after upgrade

### Symptom
Cards, inputs, and dividers that used `border` (no colour) lose their visible
border after v4 upgrade.

### Root cause
v3 defaulted unscoped `border-color` to `gray-200`. v4 defaults it to
`currentColor`. If the text colour happens to match the background, the
border becomes invisible.

### ALWAYS apply ONE of these two fixes

Option A : explicit colour everywhere (clean v4 code).
```html
<!-- before : invisible in v4 -->
<div class="border rounded p-4"> ... </div>
<!-- after : visible -->
<div class="border border-gray-200 rounded-sm p-4"> ... </div>
```

Option B : v3-compatibility shim in the entry stylesheet (quick parity).
```css
@layer base {
  *, ::after, ::before, ::backdrop, ::file-selector-button {
    border-color: var(--color-gray-200, currentColor);
  }
}
```

NEVER leave borders without an explicit colour in v4 without the shim.

## AP-7 : Focus rings shrinking from 3px to 1px

### Symptom
After upgrade, focus rings (`focus:ring`, `focus:ring-2`, etc.) look much
thinner and grayish.

### Root cause
v4 changed `--default-ring-width` from `3px` to `1px` and
`--default-ring-color` from `blue-500` to `currentColor`.

### ALWAYS apply ONE of these two fixes

Option A : explicit width and colour (clean v4 code).
```html
<button class="focus:ring-3 focus:ring-blue-500"> ... </button>
```

Option B : restore v3 defaults globally.
```css
@theme {
  --default-ring-width: 3px;
  --default-ring-color: var(--color-blue-500);
}
```

## AP-8 : `shadow-sm`, `rounded-sm`, `blur-sm` looking smaller than before

### Symptom
Existing components using `shadow-sm`, `blur-sm`, `rounded-sm`,
`drop-shadow-sm`, or `backdrop-blur-sm` appear visually smaller after upgrade.

### Root cause
A new `-xs` step was inserted at the bottom of each scale. v3's `shadow-sm`
maps to v4's `shadow-xs`. The `npx @tailwindcss/upgrade` tool renames these
in source files, but the resulting v4 code uses `shadow-xs` where v3 used
`shadow-sm`.

### ALWAYS
- Run the upgrade codemod first, which renames the call sites.
- Visually verify every shadowed card, blurred backdrop, and rounded badge.
- If parity matters more than design refresh, accept the upgrade-tool rewrite ;
  visual size will be preserved because the rename targets the same step.

### NEVER
- Hand-edit a v3 `shadow-sm` to a v4 `shadow-xs` without running the codemod
  first. Mixed manual + automated edits make double-rename bugs likely.

## AP-9 : Hover styles disappearing on touch devices (now intended)

### Symptom
After upgrade, `hover:` utilities no longer apply on mobile / touch laptops.

### Root cause
v4 wraps `hover:` in `@media (hover: hover)` by default. v3 always applied
hover. The behaviour change is INTENDED ; tap-and-hold no longer triggers a
sticky hover state on iOS.

### ALWAYS
- Accept the new default. Hover should not apply on touch ; that was a v3 quirk.
- For interaction that needs touch-equivalent (e.g. menus that open on tap),
  use `active:` for tap-down and `aria-expanded` data-attributes for state.

### NEVER restore the v3 behaviour unless absolutely required
```css
/* Last-resort shim, NEVER preferred */
@custom-variant hover (&:hover);
```

## AP-10 : Sass / Less / Stylus in the same pipeline as v4

### Symptom
Build fails or produces broken CSS after upgrading to v4 if the project also
runs Sass, Less, or Stylus.

### Root cause
v4 is the preprocessor. Running another preprocessor on top of v4 output
(or feeding v4 input through one first) is no longer supported. The v3
PostCSS pipeline tolerated this ; the v4 Oxide engine does not.

### NEVER chain Sass with v4

### ALWAYS
- Remove the other preprocessor as part of the v4 upgrade.
- Replace Sass partials with `@import "..."` (Oxide bundles imports natively).
- Move nesting that depended on Sass into native CSS nesting (supported in v4).

If removing the preprocessor is not feasible right now, STAY on v3.4.

## AP-11 : Wrong variant chain order after upgrade

### Symptom
After upgrade, specific styles applied to bespoke selectors stop matching.
Example : `first:*:pt-0` no longer targets the first child of any direct child.

### Root cause
v4 reads variant chains left-to-right. v3 read them right-to-left. The
codemod handles common cases but misses bespoke `[&...]` arbitrary variants
combined with structural variants like `first:`, `last:`, `*:`.

### NEVER assume the codemod caught every chain

### ALWAYS
- Search source for chains of 2+ variants and review each.
- Flip the order if the chain combines structural selectors with arbitrary
  variants.
- Example : v3 `[&>[data-active]]:hover:bg-red-500` becomes
  v4 `hover:[&>[data-active]]:bg-red-500`.

## AP-12 : Mixing `@theme` tokens with `theme.extend` in legacy JS config

### Symptom
A token defined in BOTH `@theme` and the JS config loaded via `@config` has
inconsistent values across the bundle.

### Root cause
v4 does not specify a winner when the same token is defined twice. Behaviour
depends on file order, plugin order, and theme namespace overlap.

### NEVER
```css
@import "tailwindcss";
@config "../tailwind.config.js";  /* contains theme.extend.colors.brand */
@theme {
  --color-brand: #1da1f2;  /* same key defined again */
}
```

### ALWAYS migrate per category :
1. Move ALL `theme.extend.colors` entries to `@theme` as CSS variables.
2. Delete `theme.extend.colors` from the JS file in the same commit.
3. Repeat for spacing, fonts, breakpoints, etc.
4. Remove `@config` when the JS file is empty.

## AP-13 : Targeting browsers that don't support v4

### Symptom
v4 site is blank or unstyled in Safari < 16.4, Chrome < 111, or Firefox < 128.

### Root cause
v4 emits `@property` declarations and uses `color-mix()`. Older browsers do
not parse these and skip the entire rule.

### ALWAYS
- Check the project's browser-baseline requirement BEFORE deciding to upgrade.
- If users on older browsers must be supported : STAY on v3.4.
- If a polyfill is acceptable for `@property` only (limited fidelity) : a
  fall-back stylesheet built from v3 served conditionally via UA sniff is
  the only workable pattern, and it doubles build complexity.

### NEVER ship v4 to a project with broad legacy-browser support without testing

Source : https://tailwindcss.com/docs/upgrade-guide

## AP-14 : Running the upgrade tool on Node 18 or older

### Symptom
`npx @tailwindcss/upgrade` errors out with a Node version requirement message.

### Root cause
The upgrade tool requires Node.js 20 or newer.

### ALWAYS
```bash
nvm use 20  # or fnm use 20, or upgrade the system Node
npx @tailwindcss/upgrade
```

### NEVER attempt a manual upgrade by hand-editing files instead of using the
codemod. The volume of renamed utilities and rewritten variant chains makes
human migration error-prone for any non-trivial codebase.

## AP-15 : Forgetting to test in production build mode after upgrade

### Symptom
v4 upgrade looks fine in `npm run dev` but production bundle has missing
classes or wrong styles.

### Root cause
Production builds use a different content-detection path. Dynamic classes
generated only at runtime, or referenced only by string interpolation, may
be present in dev (via in-source scanning) but stripped from prod (via
production tree-shaking).

### ALWAYS run a production build and visually verify the deployed bundle
after every v4 upgrade. The `@source inline(...)` directive is the right
fix for runtime-only classes ; do not rely on dev-mode parity to declare
the migration complete.
