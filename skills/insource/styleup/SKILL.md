---
name: styleup
description: >-
  Turns an existing project's styling into a maintainable, professional system on any stack:
  inventories every hardcoded or duplicated style, works inside the styling system the project
  already uses (or makes one evidence-based build-vs-library decision only when it has none), builds
  a semantic token layer as the single source of truth, migrates all consumers in pixel-safe slices,
  and locks the result with no-hardcoding guards plus before/after parity evidence. Use when asked to
  styleup/style-up a project, make styles maintainable or professional, centralize colors/typography/
  spacing/radii, remove hardcoded or duplicated styles, introduce design tokens, or decide whether to
  adopt a styling library versus staying framework-native.
---

# styleup

Make an existing project's styling **token-driven, single-sourced, and enforced** — on whatever
framework the project actually uses — without changing what users see, unless a visual change is
explicitly in scope.

This is an up-skill: one purpose, a fixed procedure, no clarifying questions. The only judgment it
makes is the library decision below.

## When to use

- "Style up" / "styleup" this project; make styling maintainable, professional, consistent
- Colors/typography/spacing/radii/shadows repeated across files; theme pairs duplicated at call sites
- Per-platform, per-locale, or per-tenant/brand variants hardcoded in consumers
- "Should we use <styling library>?" (markup builders, CSS-in-JS kits, component suites)
- Existing tokens drifted between two sources of truth
- Styling that lives in more than one place: stylesheets/components, imperative drawing (canvas/SVG/
  chart code), and native/OS chrome

**Not for:** greenfield design-system creation, pure visual redesigns, or one-off component tweaks.
For those, use `styling` — both skills aim to enhance the styling experience at different layers:
`styleup` takes action to update code that already exists (inventory, migrate, guard, prove
parity); `styling` constructs the project so a true design system can exist (structure, layer
chain, naming, getting the decisions right the first time).

## First gate: is a styling system already in use?

Inventory the incumbent before anything else. This gate decides whether the library question exists
at all.

- **A professional styling library is already adopted** — a CSS-in-JS/theme provider (Emotion,
  styled-components, Tamagui), a utility-CSS framework with theme config (Tailwind, UnoCSS), a
  component/design-system suite, or a platform theming library. **Do not question it and do not
  propose replacing it.** The library question is closed. Work inside its model: extend its
  token/theme configuration, replace arbitrary/hardcoded values with its tokens, and enforce its
  usage. Restyling the stack is a different project.
- **A framework-native token mechanism is already in use** — CSS custom properties, MAUI/WinUI
  resource dictionaries, Compose theme, React Native theme context, SwiftUI environment. Also
  closed: centralize the remaining values into that mechanism.
- **Plain styling only** — raw CSS/SCSS/StyleSheet/inline styles/loose constants, with no
  token/theme system. Only here does the build-vs-library decision below apply.

If the incumbent exists but is unmaintained or incompatible, record that as a separate upgrade
candidate/follow-up; do not hijack this run with a library migration.

## The one judgment: framework-native tokens or a styling library (only when there is none)

Applies **only** when the first gate found plain styling. Decide from evidence. Never ask the user
which one they prefer; the skill owns this decision.

| Test | Question | Failing this means |
|---|---|---|
| **Necessity** | Does the platform lack a capability the token layer needs? | Stay native — the platform already covers it |
| **Fit** | Does it respect packaging, runtime loading, crash-safety, RTL, offline, build-time checks? | Stay native or hybrid |
| **Health** | Active releases, contributor count, adoption, license, compatibility with the pinned framework version | Stay native unless small and vendorable |
| **Interop** | Coexists with existing components/styles? Incremental adoption? Escape hatch? | Stay native or hybrid |
| **Exit** | Can it be removed later? Can it be vendored? | Do not adopt without a rollback path |

Hard rules:

- A library whose contribution is only **where styles are authored** (fluent/markup builders, JSX
  style helpers, thin wrapper kits) relocates values; it does not centralize them. Reject it as the
  cure for hardcoded styles. It may still be piloted separately as an ergonomics choice.
- If the platform already provides **reactive token primitives** — illustrative: [CSS custom
  properties + media queries], [.NET MAUI/WinUI resource dictionaries + dynamic resources], [Compose
  theme + composition locals], [React Native theme context], [SwiftUI environment values] — native is
  the default; a library must add a capability you would otherwise build.
- Verdict is **native**, **library**, or **hybrid** (pilot one isolated area, keep rollback), with a
  written evidence trail. A genuine unresolvable blocker (license, unsupported target) is an Open
  Question — stop that branch, do not guess.

Full criteria, evidence sources, case notes, and a decision-record template:
`references/library-decision.md`.

## Core principles (stack-agnostic)

| Principle | Why |
|---|---|
| **Definition site over consumption site** | A value written where it is used cannot be changed once, everywhere |
| **One authority** | Duplicated tables drift; the drift is invisible until a screen looks wrong |
| **Reactive, not reloaded** | Theme/brand/tenant/locale flips must repaint existing views without rebuilding pages |
| **Pixel-preserving mapping** | Identical current value → identical token; never substitute a "cleaner" value mid-migration |
| **Role-named tokens** | `surface-raised`, not `slate-900-two`; aliases only when the role genuinely differs |
| **Full coverage** | Color, type scale, spacing, radius, elevation, border widths, motion — not colors alone |
| **Guards over guidelines** | A rule without a failing check is a suggestion |
| **Prove with captures** | "No visual change" is a measurement, not an intention |

## Fixed workflow

0. **Recon & scope.** Identify the framework(s), every current styling mechanism (stylesheets,
   CSS-in-JS, design-system objects, resource dictionaries, canvas/SVG drawing, native chrome),
   targets, and existing lint/test/capture tooling. Count hardcoding per category — colors,
   typography, spacing, radii, shadows, motion — per file. Default scope: the entire project.
1. **Incumbent gate → decision.** If a styling system is already in use, adapt to it (the library
   question is closed). Only for plain styling, run the five tests and write the decision record.
   This is the skill's only branch.
2. **Baseline BEFORE edits.** Capture the real app in every state that matters with the project's own
   tooling (browser screenshots and/or DOM + computed-style snapshots, emulator/desktop capture,
   platform screenshot harness). Freeze theme, locale, data seed, and tenant/source. Run the capture
   twice back-to-back to identify genuinely dynamic pixels (clocks, animation phases, focus visuals,
   desktop bleed). Record a manifest: build version, states, hashes. `scripts/capture_matrix.py` runs
   a user-supplied capture config for exactly this step.
3. **Token model.** Design role names and copy current values verbatim. Define: the single table,
   aliases for genuinely different roles, typed twins for properties that cannot take a plain value
   (brush/gradient/platform color types), and the bridge lifecycle — initialize before first paint,
   rewrite on every theme/brand event, and expose typed getters for code that cannot consume reactive
   tokens (canvas, chart libraries, imperative painters, native/OS chrome).
4. **Migrate in slices.** Style definitions → screens/components → imperative/draw/canvas code →
   native/OS chrome. Convert mechanically (same current value → same token), never by hand-typing
   values. Every slice must lint/build/test green; do not leave a half-migrated vocabulary.
5. **Guards.** Add source checks to the project's existing harness — linter rules (stylelint, ESLint,
   detekt), analyzers (Roslyn), or custom test scans / grep gates. Rules: no raw style values in
   consumers; no theme-pair duplication where a token exists; no references to retired names; every
   token reference resolves; the token table is well-formed (unique names, parsable values, no orphan
   twins). Give every scan a scanned-count floor so a scan that matches nothing cannot pass.
6. **Verify.** Run project gates/builds/suites; capture the same matrix after; diff exactly against
   the baseline (pixels, computed styles, or DOM snapshots as the stack allows). Mask only regions
   **proven** dynamic by the two-run check, and keep the mask file tracked. Fix every other
   difference. Recapture a couple of states with the final build. `scripts/palette_diff.py` performs
   the exact diff; `--propose-masks` drafts masks from the two-run delta.
7. **Lock & document.** Update the design-system docs, unit/component catalog, decision record,
   version and changelog per project convention. Report evidence, not intent.

## Definition of done

- [ ] One token authority; consumers contain no raw style values
- [ ] Tokens cover every style category the project actually uses, not colors only
- [ ] Theme/brand/tenant/platform variants expressible without editing consumers
- [ ] Guards fail on new hardcoding and cannot pass vacuously (floors present)
- [ ] Before/after render parity is exact outside documented dynamic regions, or the visual diff was
      explicitly approved
- [ ] Project gates, builds, and suites are green on the final commit state
- [ ] Library verdict recorded with evidence; docs/version/changelog updated

## Out of scope

- New features, redesigns, or aesthetic changes (only when explicitly in scope)
- Layout/component-structure refactors, platform-parity rewrites
- Unrelated dependency upgrades
- Deleting user-authored experiments or "unused" code to make numbers look better

## Output expectations

Leave behind: the decision record (native/library/hybrid + evidence), a token-table summary, files
touched per slice, guard tests added, parity evidence (states, masks, diff result), gate results, and
follow-ups. Report raw evidence; do not summarize away differences.

## Additional resources

- `references/library-decision.md` — incumbent gate, five tests, evidence sources, case notes
- `scripts/capture_matrix.py` — run a capture config into before/after dirs with a manifest
- `scripts/palette_diff.py` — exact before/after diff, masks, and mask proposals from two runs
- `examples/web-token-layer.md` — CSS + TypeScript case (custom properties, Playwright parity)
- `examples/maui-token-layer.md` — XAML/MAUI case (dynamic resources, desktop capture parity)

Scripts are Python 3; `palette_diff.py` needs Pillow (install it in a local virtualenv). Neither
script knows your stack: the capture commands are user-provided in `capture.json`.
