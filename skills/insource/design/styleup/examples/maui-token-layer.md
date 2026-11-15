# Worked case: a compiled desktop/mobile app (XAML + C#)

One case, not a recipe. See `web-token-layer.md` for a different paradigm (browser + TypeScript).

## Starting point (measured)

- Roughly 300 theme-aware literal pairs across about two dozen XAML files
- A few hundred additional hex literals in C#: imperative painters, drawables, and native chrome
- A handful of components repainting themselves by subscribing to theme events
- Five brand keys already fed by a dynamic-resource bridge — the only tokenized values
- Two colors already disagreed between the XAML palette and the C# token class (drift)
- No professional styling library in use: framework resources and literals were the whole system

## Decision: native

Step 0 found no incumbent library, so the five tests applied. Necessity failed: the framework already
offers reactive resources. A markup library was evaluated and failed Necessity for a hardcoding
problem, and its health/interop evidence (single maintainer, undocumented desktop packaging path) was
too thin to justify adoption. It was recorded as an optional ergonomics pilot, not adopted, and not
proposed as a replacement for the framework mechanism.

## What was built

1. **One token table**: role-named light/dark pairs. Every value copied verbatim from current
   rendering; identical pairs collapsed; theme-invariant legacy values became fixed tokens with the
   same value in both columns.
2. **One bridge**: writes the table (plain values + brush twins) into the root resource dictionary in
   the app constructor, rewrites it on theme change, and exposes typed getters for code that cannot
   consume dynamic resources — canvas-like drawables, imperative painters, and native chrome. The
   brand/tenant palette stayed a separate writer of the same dictionary: two writers, one owner per key.
3. **Styles and screens**: every style setter and every screen literal became a dynamic-resource
   reference; the legacy palette file and its merge were deleted.
4. **Imperative code**: settings rows, cards, a sidebar, chart-like drawables, shimmer placeholders,
   badges, an onboarding page, and the native title bar now read the same getters; the row gained a
   token-changed subscription scoped to its on-screen lifetime.
5. **Guards**: source scans in the existing harness — no color theme-bindings; no hex/named colors on
   color attributes; no hex in shared code; no references to retired keys; every token reference
   resolves; the table is well-formed — each with a scanned-count floor. The pre-existing brand scan
   was tightened to treat the token table as the brand owner.

## Before / after

```xml
<!-- before: the value is decided at the consumption site -->
<Border Stroke="{AppThemeBinding Light=#E2E8F0, Dark=#1E293B}"
        BackgroundColor="{AppThemeBinding Light=White, Dark=#0F172A}" />

<!-- after: the value is named once, written once -->
<Border Stroke="{DynamicResource BorderSubtleBrush}"
        BackgroundColor="{DynamicResource Surface}" />
```

## Parity protocol (the part that makes it safe)

- Captured a state matrix **before any edit**: pages × themes × tenants, plus interactive states and
  a component gallery, at a fixed client size.
- Ran the baseline twice back-to-back to identify genuinely dynamic pixels, then masked only those:
  a live clock line, desktop bleed through a rounded window corner, a system focus visual, and a
  continuously animated sheen. The masks are tracked next to the captures.
- Migrated in slices, capturing after each; the final diff must be **zero pixels outside the proven
  dynamic regions**. A real regression (inverted native-chrome tokens, visible as a one-pixel frame
  shift) was caught and fixed before sign-off.
- Rebuilt after the last edit and spot-recaptured a couple of states with the **final binary** — the
  verified capture build and the shipped build are not automatically the same artifact.
- Result: every state exact outside the masks; project gates and suites green.

## Portable lessons

1. **Identical-value mapping is the safety mechanism.** Map mechanically, never by hand-typing values;
   "closest semantic" mapping changes pixels.
2. **Do not alias theme-varying tokens to theme-invariant legacy values.** A fixed value needs a fixed
   token, or dark mode silently repaints.
3. **Typed-property twins matter.** Properties that need a brush/gradient/platform color type need
   twins or a proven conversion; do not assume a raw color coerces.
4. **Imperative painters need an event.** A token table alone does not repaint code that assigns
   values directly; subscribe on load, release on unload.
5. **A mask requires proof.** Only mask a region that differs between two runs of the *same* build.
6. **Guards need floors.** A scan that matches nothing must fail, not pass vacuously.
7. **Spot-check the final binary.** The verified capture build and the last build can differ.
8. **Keep brand and neutral writers separate.** One dictionary, one owner per key, no ordering races.
