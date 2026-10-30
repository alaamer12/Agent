# Rendering Gotchas: Why It Looks Right But Scores Low

A categorized catalog of recurring root causes behind a low regional score. Check these categories *before* assuming a novel bug — most low-scoring regions turn out to be one of these, not something new. Each entry states the general symptom pattern (so it transfers to any framework) plus one concrete worked example from a real .NET MAUI/Android project (so "root cause → fix" is grounded, not abstract).

## Table of contents
1. Setup/measurement gotchas (check these first — they're not real design bugs)
2. Native decoration bleed-through
3. Spacing/margin double-counting
4. Font-metric divergence
5. Chrome elements that don't auto-hide
6. Asset/icon path resolution differences
7. Color-space / theme-token mismatches

---

## 1. Setup/measurement gotchas — check these first

These aren't rendering bugs at all — they're pipeline-setup mistakes that produce a low score for reasons unrelated to the actual UI. Rule these out before diagnosing anything in §2 onward, since "fixing" one of these in application code will do nothing.

- **Chrome/frame noise** (scrollbar on the mockup side, status bar on the device side, safe-area insets) — see `frame-normalization.md` in full. This is the single most common false-positive source.
- **Dummy-data mismatch** — the mockup's placeholder content and the real app's real/random data will never match no matter how correct the layout is. See `debug-state-simulation.md` §4 — this needs a fixture dataset, not a layout fix.
- **Obstacle-screen capture** — accidentally capturing a splash/onboarding screen instead of the intended target because a bypass didn't fire. See `debug-state-simulation.md` §5.
- **Black/blank-frame capture** — a screenshot taken before the app finished its first real render. See `pipeline.md` §3.

## 2. Native decoration bleed-through

**Symptom pattern**: a custom-styled component still shows a faint native visual artifact underneath the custom styling — an underline, a default border, a default focus ring, a platform-standard shadow — because the native control's default decoration was suppressed visually but not actually removed at the control level.

**Worked example (MAUI/Android)**: a custom-styled `Entry` (text input) still shows a thin Android-native underline beneath the app's own custom border, because Android's `EditText` draws its underline via the platform's default background drawable, which isn't removed just by setting a custom `BackgroundColor` or wrapping it in a styled container — the underline is a separate drawable layer. The fix is to explicitly clear/replace the native background drawable on the platform-specific renderer/handler for that control, not to try to visually cover it with the custom styling.

## 3. Spacing/margin double-counting

**Symptom pattern**: a stack of elements has more total spacing between items than the mockup, because both the layout container's built-in "spacing between children" property *and* an explicit margin on the individual children are contributing distance simultaneously — the mockup's CSS `gap` (or margin) is being represented twice on the native side.

**Worked example (MAUI/Android)**: a `VerticalStackLayout` with `Spacing="16"` set at the container level, where each child *also* has a `Margin="0,8,0,8"` — the effective gap between two children becomes 16 (container spacing) + 8 (bottom margin of the first) + 8 (top margin of the second) = 32, double what the mockup's `gap: 16px` actually specifies. The fix is to pick exactly one mechanism (container spacing *or* per-child margin) per axis and remove the other, not to average them or halve one arbitrarily.

## 4. Font-metric divergence

**Symptom pattern**: text at the "same" font size and line-height in both mockup and native still occupies visibly different vertical space, because the browser's font renderer and the native platform's font renderer compute line-height/leading/internal font padding differently for the same nominal values — this compounds across every line of text on a text-heavy screen.

**Worked example (MAUI/Android)**: Android's default `TextView` includes built-in top/bottom font padding derived from the font's internal metrics (ascent/descent) that a browser's CSS `line-height` calculation doesn't apply the same way, so identical `font-size`/`line-height` values produce a native text block that's visibly taller than the mockup's. The fix (on Android specifically) is often to disable the platform's default include-font-padding behavior on the relevant text renderer and re-tune line-height empirically against the mockup, rather than trusting the nominal CSS value to translate 1:1.

## 5. Chrome elements that don't auto-hide

**Symptom pattern**: a persistent UI chrome element (a tab bar, a navigation bar) that the mockup shows hidden on a specific screen (e.g. a full-screen modal, a deep detail page) remains visible in the native app, because hiding it requires an explicit per-screen instruction that was never added — the native navigation framework doesn't infer "this screen shouldn't show the tab bar" from the mockup's design intent.

**Worked example (MAUI/Android)**: pushing a detail page onto a `Shell`-based navigation stack doesn't automatically suppress the app's bottom tab bar the way the mockup's full-screen modal implies it should — `Shell.TabBarIsVisible="False"` (or the equivalent property) has to be set explicitly on that specific page, or the tab bar persists and eats into vertical space the mockup didn't allocate for it.

## 6. Asset/icon path resolution differences

**Symptom pattern**: an icon or image that renders correctly in the mockup fails to render (or renders as a placeholder/broken-image glyph) in the native app, because the mockup references it by a web-style relative file path while the native platform expects it to be registered as a named resource (or vice versa) — the two ecosystems don't resolve "where is this asset" the same way at all.

**Worked example (MAUI/Android)**: a mockup's `<img src="/assets/icons/search.svg">` has no direct native equivalent — MAUI resolves images by resource name from a shared `Resources/Images` folder with platform-specific naming/density rules, not by an arbitrary file path, so the fix is registering the asset correctly in the resource system and referencing it by its resolved name, not attempting to mirror the mockup's literal path structure.

## 7. Color-space / theme-token mismatches

**Symptom pattern**: colors look close but not identical between mockup and native even when both are "using the same design token," because one side is applying a color-space conversion, an opacity/blend the other side doesn't, or the dark-mode token resolution takes a different code path than light mode and was never verified against the mockup's actual dark-mode colors (as opposed to just the light-mode colors with a dark filter over them).

**Worked example**: a brand color defined as a hex value in the mockup's CSS renders at slightly different perceived brightness/saturation on-device due to a platform color-management step (wide-gamut display color conversion) the browser capture didn't go through identically — usually only worth chasing if the palette-similarity metric (`pipeline.md` §4) flags it as a real, consistent, non-trivial gap, not for sub-perceptible rounding differences.
