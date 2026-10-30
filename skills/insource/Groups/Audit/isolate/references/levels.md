# Levels of isolation

Contents: Level 1, Level 2, Level 3, adding another axis, when not to isolate.

Every named axis and value here is an example (`[platform]`, `[release channel]`, `[audience or region]`, `[tenant]`, `[hardware tier]`, `[experiment cohort]`, `[accessibility profile]`). The running component is only an illustration: a confirmation dialog, called `ConfirmationBox` in sketches. Any component with varying behavior works.

Teach the levels in order. Each level exists because the previous one hit a named constraint.

## Level 1: one axis varies

**Scenario.** The component behaves differently along one axis, for example `[platform]`: how it finds the native window, draws, or plays a sound.

**Solution: seams fulfilled by per-variant files.**
1. One public surface. Callers use one name and one import and never see a variant.
2. The shared file declares seams: members that are named but not implemented. Each variant file fulfils the seams for its own variant.
3. Selection happens at build time, so a variant that fails to fulfil a seam is a build error, not a production bug.
4. Variants that share a family (two `[mobile]` platforms, or three `[desktop]` platforms) put shared logic in one family file, marked by a convention such as a leading underscore. Each platform file forwards to it with one line, which keeps an explicit, searchable place to diverge later.

Layout (example):
```
Component.ext              shared logic; declares the seams
_Component.Mobile.ext      logic shared by the mobile family
Component.Android.ext      one-line forward to the mobile family file
Component.iOS.ext          one-line forward to the mobile family file
_Component.Desktop.ext     logic shared by the desktop family
Component.Windows.ext      one-line forward to the desktop family file
Component.macOS.ext        one-line forward to the desktop family file
Component.Linux.ext        one-line forward to the desktop family file
```
A platform that shares nothing needs no family file. A new platform joins a family with one forwarding file, and a new family is one new underscore file.

**Why it fits:** the axis is total. Every variant must answer every seam, and the compiler can check it. A name suffix is a coordinate, and one coordinate fits in a filename.

**Constraint.** A second axis arrives. A name such as `Component.Canary.Android.ext` has no correct order, and multiplying by components and values yields a grid of near-identical files that drift apart.

## Level 2: a second axis appears

**Scenario.** The product also varies by `[release channel]`, and the experimental variant changes code (for example a different render path), not just strings.

**Solution: move the second axis from the filename to the path.** The first axis stays in the name. The second becomes a directory overlaying the base. The build takes one property (the variant id), and an overlay file shadows the base file at the same relative path.

```
Component/                     base: every file the component has
Overlays/<variant-id>/Component/
  _Component.Mobile.ext        only the files that differ
```

Rules:
- Overlay, do not fork. The overlay holds only files that differ.
- Key overlays by id. The axis is an open set, so one fixed folder name is not enough.
- Shadowing replaces a file. It is not inheritance, so keep seam files small and single-purpose.
- Platform filtering still applies to overlay files.
- Seam signatures belong to the base. A mismatch is a compile error.

**Constraint.** Two things break: (1) a third axis arrives, and nesting it (`Overlays/<variant>/<audience>/`) is a grid one level up; (2) shadowing is fixed at build time and replaces rather than wraps, so it cannot switch at runtime or extend base behavior.

## Level 3: a third axis, and any that follow

**Scenario.** The product also varies by `[audience or region]`, and release tags such as `[channel]-[ring]-[audience]` appear.

**Solution: layers.** Separate two jobs Level 2 mixed:
- **Inclusion** decides which code exists in this binary. Directories and the build handle it.
- **Selection** decides which included implementation is used now. Code handles it, in one visible place: axis selectors, layer keys, a registry, and a resolver.

Resolution rule: a layer matches when every coordinate in its key equals the current value of that axis. The match with the most coordinates wins. Equal specificity is ambiguous and fails until a tie-breaker layer naming both is written. This generalizes to any number of axes with no special-case table. Details are in `layers.md`.

Level 3 is not limited to three axes. It is the first level whose structure does not change when another axis arrives, so it applies from two axes upward and pays for itself once Level 2 would form a grid.

## Adding another axis

With layers, a new axis such as `[hardware tier]` touches no existing component:
1. Add a selector that reports it.
2. Add its typed identifier values.
3. Add layer folders only for components that actually vary on it.
4. Extend the ambiguity check to include it.

No existing layer is renamed, copied, or moved.

## When not to isolate

Run these checks before adding anything to the source tree.
1. **Would the bytes differ?** If the binary is identical, it is distribution. A promotion ring such as a release candidate is a state: the candidate must be the exact artifact that later becomes stable, so promotion moves a pointer and never rebuilds.
2. **Would the code differ, or only values?** If only names, endpoints, locale, limits, or wording differ, it is data. Use a configuration pack, not a layer.
3. **Is it a capability or a policy?** A missing capability belongs in the platform layer as a new seam. Policy belongs in a layer keyed by channel or audience.

Parse composite tags such as `[channel]-[ring]-[audience]` into segments, and let each segment contribute only its own part: channel to build inputs, ring to distribution, audience to layer selection. Never hand-write one profile per combination, and fail the build when a segment has no definition.
