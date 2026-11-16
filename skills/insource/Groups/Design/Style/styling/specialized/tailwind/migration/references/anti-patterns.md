# anti-patterns — v3 → v4 upgrade mistakes

Consolidated catalog from the three consolidated sources, deduplicated: 45 source entries land as
26. Format per entry: symptom / root cause / fix / how to verify. Data tables:
[`breaking-changes.md`](breaking-changes.md); worked rewrites and scripts: [`examples.md`](examples.md);
workflow and shims: [`../method.md`](../method.md).

## AP-1 — Trusting the codemod's silence

- **Symptom:** `npx @tailwindcss/upgrade` finishes with zero errors; the deployed site has subtle
  differences — missing borders, thin focus rings, softer shadows, invisible custom-property values.
- **Root cause:** the codemod handles renames and syntactic flips. Default-behavior changes
  (breaking-changes §3) produce NO syntactic delta, so there is nothing for it to rewrite.
- **Fix:** treat a clean codemod run as the start of the audit, not the end: visual regression
  (examples §10) + leftovers script (examples §9) + manual pass over breaking-changes §3.
- **Verify:** every screenshot diff is triaged as intentional or bug; none blanket-masked.

## AP-2 — Leaving the `@tailwind` trio in v4

- **Symptom:** build fails or emits empty CSS after the version bump.
- **Root cause:** v4 removed the three directives outright; replacement is one
  `@import "tailwindcss";`. Custom multi-file CSS pipelines often miss one occurrence in a partial
  the codemod didn't scan.
- **Fix:** replace every trio with the single import (examples §1).
- **Verify:** `grep -rEn '@tailwind (base|components|utilities)' src/` is empty (examples §9).

## AP-3 — `@apply` in scoped blocks without `@reference`

- **Symptom:** Vue/Svelte/CSS-modules build fails with `Cannot apply unknown utility class: px-4`;
  the same class works fine in templates.
- **Root cause:** v3 implicitly carried theme context into every scoped block; v4 compiles each
  block in isolation, and the codemod does NOT add `@reference` lines (issue 16346).
- **Fix:** prepend `@reference "../app.css";` to each scoped block that uses `@apply`
  (examples §4; semantics: `../config/method.md`).
- **Verify:** build succeeds AND bundle size is unchanged (proves `@reference` didn't duplicate
  CSS); examples §9's scoped-`@apply` scan reports no file "needs @reference".

## AP-4 — Expecting `corePlugins` to still work

- **Symptom:** utilities the v3 config disabled (`float`, `container`, `preflight`, …) are back in
  the generated CSS, or autocomplete/docs copies keep reintroducing them. No warning — the config
  key is silently ignored, including when the file is loaded via the `@config` bridge.
- **Root cause:** v4 removed `corePlugins` with no direct replacement.
- **Fix:** refactor usage out and rely on tree-shaking; `@source not` to exclude paths; ESLint/CI
  ban; `@utility` no-op as last resort. `preflight: false` specifically → partial imports that skip
  preflight (examples §3.19). If disabling utilities is non-negotiable — STAY on v3.4.
- **Verify:** lint/CI gate fails on a planted banned class; output CSS lacks the unwanted utilities.

## AP-5 — Regex `safelist` left in the JS config under `@config`

- **Symptom:** runtime-composed classes (`bg-${color}-500`) render unstyled in production although
  the v3 `safelist` patterns matched them; dev mode looked fine.
- **Root cause:** the `@config` bridge does not process `safelist` in v4 (issue 18136); the
  replacement — `@source inline("…")` — lives in CSS, not JS.
- **Fix:** convert every pattern to brace expansion (examples §3.18; grammar:
  `../dynamic-classes/method.md`).
- **Verify:** `npm run build` then grep the output CSS for one selector per previously-safelisted
  group (examples §9 spot check).

## AP-6 — `resolveConfig()` call sites at runtime

- **Symptom:** crash after upgrade: `Cannot find module 'tailwindcss/resolveConfig'` — typically in
  charting libs, animation configs, Storybook addons, design-token exporters.
- **Root cause:** the export is removed; token values now live as CSS variables on the root element.
- **Fix:** `getComputedStyle(document.documentElement).getPropertyValue('--token')` per call site;
  no-DOM contexts parse the built CSS's `:root` block or read a build-step `tokens.json` / shared
  JS token module (examples §3.21).
- **Verify:** affected code path runs without the module error; returned value matches the design.

## AP-7 — Borders invisible or garish after upgrade

- **Symptom:** cards/inputs/dividers using bare `border` lose their outline (text color == surface),
  or render black-on-white where v3 drew `gray-200`.
- **Root cause:** default `border-color` flipped `gray-200` → `currentColor` (breaking-changes §3);
  every `border` without a color now inherits surrounding text color.
- **Fix:** explicit `border-<color>` everywhere (examples §3.9) or the time-boxed shim
  ([`../method.md`](../method.md) §6). NEVER leave bare `border` in v4 without one of the two.
- **Verify:** examples §9's bare-border grep is empty (shim removed) or every hit is covered by the
  shim; visual diff shows only intentional border changes.

## AP-8 — Focus rings shrink to 1px `currentColor`

- **Symptom:** `focus:ring` looks thin and grayish; accessibility audits flag insufficient focus
  indicators.
- **Root cause:** `--default-ring-width` 3px→1px and `--default-ring-color` blue-500→currentColor
  (breaking-changes §3).
- **Fix:** `focus:ring-3 focus:ring-blue-500` (examples §3.10), the §6 `@theme` shim, or consciously
  adopt 1px rings design-wide.
- **Verify:** tab through every focusable element — ring presence, width, color as specified.

## AP-9 — Scale-shift confusion and double-rename bugs

- **Symptom:** `shadow-sm`/`blur-sm`/`rounded-sm` components look smaller after upgrade; or after
  mixed manual + automated edits some are double-shifted (`shadow-sm` → `shadow-xs` twice).
- **Root cause:** a new `-xs` step was inserted; v3 `shadow-sm` ≡ v4 `shadow-xs` (identical CSS
  values, moved name). Designers' Figma specs still quote v3 step names. Hand-editing before/alongside
  the codemod creates double renames.
- **Fix:** run the codemod FIRST, never hand-rename in parallel (examples §3.8); if parity must be
  kept without touching call sites, remap the token itself:
  `@theme { --shadow-sm: var(--shadow-default); }`-style overrides. Communicate the step-name shift
  to design.
- **Verify:** visual diff per shadowed/blurred/rounded component; values are identical after a
  correct rename, so anything that LOOKS different was renamed in the wrong place.

## AP-10 — Variant chains flipped mechanically, or missed

- **Symptom:** styles that applied to bespoke selectors stop matching, or now apply to the wrong
  elements (`first:*:pt-0` padding the wrong item); buttons that should hide on hover always hide.
- **Root cause:** v3 evaluated chains right-to-left, v4 left-to-right. The codemod maps only common
  forms and misses arbitrary `[&…]` variants combined with structural pseudo-classes; a mechanical
  swap without a semantic check silently inverts intent.
- **Fix:** grep chains of 2+ variants (examples §9), review each, flip only where composition order
  changes meaning (breaking-changes §2.1, examples §3.1).
- **Verify:** read-aloud test — say the chain as English ("every direct child, when first, …") and
  confirm it matches intent; render the list and inspect first/last items in DevTools.

## AP-11 — Hover-only interactions dead on touch devices

- **Symptom:** `hover:` highlights, tap-and-hold states, hover-opened menus/tooltips stop working on
  phones/tablets after upgrade.
- **Root cause:** v4 wraps `hover:` in `@media (hover: hover)` — an intentional fix for v3's sticky
  touch-hover (the `future.hoverOnlyWhenSupported` option became the default and was removed).
- **Fix:** accept the default; add `active:` for tap feedback and click/`aria-expanded` state for
  menus (examples §3.11). The `@custom-variant hover (&:hover)` escape hatch ([`../method.md`](../method.md)
  §6) is a last resort, NEVER the preferred fix.
- **Verify:** tap on a real device or DevTools touch emulation — feedback state appears during tap.

## AP-12 — Sass / Less / Stylus chained with v4

- **Symptom:** build fails or produces broken CSS when another preprocessor touches v4 input/output.
- **Root cause:** v4 IS the preprocessor (Oxide + Lightning CSS); the v3 PostCSS pipeline tolerated
  stacking, v4 does not.
- **Fix:** remove the other preprocessor as part of the upgrade; Sass partials → native `@import`
  (Oxide bundles them), Sass nesting → native CSS nesting. Not feasible right now → STAY on v3.4.
- **Verify:** no preprocessor loaders remain in the pipeline; `npm run build` exits 0 and emits CSS
  (gate 1, [`../method.md`](../method.md) §8).

## AP-13 — Leaving the migration crutches in

- **Symptom:** three faces of the same neglect — (a) a token defined in BOTH `@theme` and the
  `@config`-loaded JS file resolves inconsistently across the bundle; (b) years later the project
  still ships `@config "./tailwind.config.js";`; (c) the `@layer base` border shim is permanent and
  new contributors write `border` expecting gray-200, never learning the v4 default.
- **Root cause:** migration aids (bridge, shim, dual definition) treated as permanent behavior.
  For (a): v4 specifies no winner for a doubly-defined token — outcome depends on file order,
  plugin order, and namespace overlap.
- **Fix:** one category at a time: move ALL `theme.extend.<ns>` entries to `@theme`, delete the JS
  block in the same commit, repeat per namespace, remove `@config` when the JS file is empty
  (examples §6). Shims: TODO with a target date, audit usage, convert to explicit classes, delete
  (time-box rule: [`../method.md`](../method.md) §6).
- **Verify:** no `@config` line in the entry stylesheet; no token key present in both surfaces;
  grep for the shim markers returns nothing after its expiry.

## AP-14 — Browser baseline drifted silently

- **Symptom:** production users on Safari 14 see a blank/unstyled site; CI passes because it runs
  Chrome 120.
- **Root cause:** v4 emits `@property` and uses `color-mix()`/container queries; engines below
  Safari 16.4 / Chrome 111 / Firefox 128 skip those rules entirely (breaking-changes §11).
- **Fix:** check the audience baseline BEFORE deciding (decision table: [`../method.md`](../method.md)
  §1); update browserslist to the v4 floors — `"safari >= 16.4", "chrome >= 111", "firefox >= 128"`.
  The only workable old-browser fallback (conditional v3 stylesheet via UA sniff) doubles build
  complexity — don't.
- **Verify:** browserslist config matches the shipped floor; a real test on an older engine, or the
  audience analytics say it's safe.

## AP-15 — Wrong Node version, or hand-migrating instead of codemod

- **Symptom:** `npx @tailwindcss/upgrade` errors with a Node version requirement; or a "careful"
  manual migration ends with missed renames and mangled variant chains.
- **Root cause:** the tool requires Node.js 20+; the sheer volume of renames and chain rewrites
  makes human migration error-prone for any non-trivial codebase.
- **Fix:** `nvm use 20` (or `fnm use 20`) then re-run. ALWAYS use the codemod as the first pass —
  manual work is for the residue list, not the bulk.
- **Verify:** `node --version` ≥ 20 before the run; the codemod commit exists in the branch history.

## AP-16 — Skipping the production gate, assuming a small codebase

- **Symptom:** upgrade looks perfect in `npm run dev`; the production bundle has missing classes.
  Or: "only 5 pages, the codemod will be fine" — three weeks later a designer notices borders are
  gone site-wide.
- **Root cause:** prod builds use a different content-detection path — classes present via dev
  in-source scanning get stripped by production tree-shaking; small apps hide regressions because
  nobody built a visual suite for 5 pages.
- **Fix:** production build + visual verification are mandatory regardless of size; runtime-only
  classes get `@source inline` (examples §3.18), not dev-mode parity assumptions.
- **Verify:** examples §9 script runs clean on the built app; screenshots of every page from the
  prod bundle (gate 3, [`../method.md`](../method.md) §8).

## AP-17 — Prefix-flip leftovers outside templates

- **Symptom:** some elements styled, others unstyled; tests fail on class assertions.
- **Root cause:** the codemod rewrites markup but misses `tw-` references in template strings, data
  attributes, test selectors, stories, and docs — e.g.
  `expect(button.className).toContain("tw-flex")` is now stale.
- **Fix:** grep the whole repo (not just `src/`) for the v3 prefix form (examples §9 pattern) and
  convert each hit to `tw:`.
- **Verify:** repo-wide grep for `tw-` utility patterns is empty; test suite green.

## AP-18 — Important-flip leftovers in class builders

- **Symptom:** some `!important` overrides still win, others silently stopped.
- **Root cause:** the codemod catches literal `!class` strings but misses conditional builders:
  `classNames("base", isPriority && "!font-bold")`.
- **Fix:** grep for a bang before a letter inside quoted strings (examples §9 pattern); flip every
  occurrence to the trailing `!`.
- **Verify:** grep clean; the priority-styling path exercised once in a production build.

## AP-19 — `*-opacity-*` reassembled at runtime

- **Symptom:** overlay divs fully opaque despite `bg-opacity-50` in the composed class list.
- **Root cause:** the utilities are removed; the codemod converts only the literal
  `bg-COLOR bg-opacity-N` pair, not `` `bg-${color} bg-opacity-${opacity}` ``.
- **Fix:** rebuild the template as the slash modifier — `` `bg-${color}/${opacity}` ``; if the
  templated form is unavoidable, add the resolved classes via `@source inline`
  (`../dynamic-classes/method.md`).
- **Verify:** click through every prop-driven color/opacity set on a production build
  (gate 5, [`../method.md`](../method.md) §8).

## AP-20 — `outline-none` where v3 meant `outline-hidden`

- **Symptom:** focus outlines vanish entirely; accessibility audit flags missing focus indication;
  forced-colors mode shows nothing.
- **Root cause:** v4's `outline-none` literally sets `outline-style: none`; v3's `outline-none`
  drew an invisible outline that stayed visible in forced-colors mode — that behavior was renamed
  to `outline-hidden`.
- **Fix:** `focus:outline-none` → `focus:outline-hidden` (examples §3.5); reserve `outline-none`
  for elements genuinely intended to have zero focus indication.
- **Verify:** audit EVERY `outline-none` hit for intent (examples §9); Windows high-contrast /
  forced-colors check on focusable elements.

## AP-21 — Arbitrary `[--var]` left unchanged — silently wrong

- **Symptom:** custom-property-driven backgrounds/text fall back to transparent/0; no build error,
  no warning anyone read.
- **Root cause:** v4 still parses `bg-[--brand]` but treats the content as a RAW value, not a
  variable reference; the canonical form is `bg-(--brand)`.
- **Fix:** grep `\[--` and convert each `[--var]` to `(--var)` (examples §3.6, §9).
- **Verify:** computed styles show the var resolving; grep for `[--` in class strings is empty.

## AP-22 — Commas in arbitrary multi-value utilities

- **Symptom:** `grid-cols-[max-content,auto]` produces invalid CSS / the grid ignores the value.
- **Root cause:** v3 substituted commas with spaces inside `[...]`; v4 removed that substitution —
  underscores carry spaces, commas are reserved for real CSS function argument lists.
- **Fix:** `grid-cols-[max-content_auto]`; keep commas inside `minmax(0,1fr)` (examples §3.6).
- **Verify:** inspect the built rule in DevTools — the value parses.

## AP-23 — `transform-none` expecting the old bulk reset

- **Symptom:** `hover:transform-none` handlers do nothing after upgrade.
- **Root cause:** v4 applies transforms as individual CSS properties; the composite `transform`
  utility and its `-none` reset no longer exist.
- **Fix:** reset the specific properties — `focus:rotate-none focus:scale-none` etc.; update
  transition property lists (`transform` → `scale`) (examples §3.7).
- **Verify:** trigger the interaction; the transform genuinely resets.

## AP-24 — Custom utilities authored with `@layer utilities`

- **Symptom:** build succeeds but the custom class never appears in output, or variants/modifiers
  on it silently fail.
- **Root cause:** v4 tolerates `@layer utilities { .x {} }` for plain static rules, but the utility
  API is `@utility`; functional utilities (parameterized ranges, variant support) do NOT work via
  the old form.
- **Fix:** migrate each to `@utility` (or `@utility tab-* { tab-size: --value(integer); }` for
  ranges) (examples §3.13; full semantics: `../config/method.md`).
- **Verify:** grep the output CSS for the custom class; exercise a variant (`hover:tab-4`-style).

## AP-25 — `theme()` dot notation left in CSS

- **Symptom:** `theme(spacing.4)` yields undefined values or build errors in plugin/user CSS.
- **Root cause:** dot notation is gone; the function takes the CSS-variable name (and `var()` is
  usually the better answer).
- **Fix:** `theme(screens.xl)` → `theme(--breakpoint-xl)`; `theme(colors.red.500)` →
  `var(--color-red-500)` (examples §3.17).
- **Verify:** grep `theme(` for dotted arguments is empty; media query resolves in output.

## AP-26 — `hidden` attribute losing to display utilities

- **Symptom:** `<div hidden class="block">` that v3 kept invisible is now VISIBLE in v4 (or the
  reverse surprise when toggling state via the attribute).
- **Root cause:** v3 preflight forced `[hidden] { display: none !important; }`; v4 removed the
  override so display utilities win (the change also respects `hidden="until-found"`).
- **Fix:** toggle a utility class instead of the attribute, or restore the v3 rule during
  migration (examples §5).
- **Verify:** one element carrying both `hidden` and a display utility behaves as chosen — hidden
  with the restore rule, visible without.

## Sources

- https://tailwindcss.com/docs/upgrade-guide
- https://tailwindcss.com/blog/tailwindcss-v4
- https://tailwindcss.com/docs/detecting-classes-in-source-files
- https://github.com/tailwindlabs/tailwindcss/issues/16346
- https://github.com/tailwindlabs/tailwindcss/issues/18136
