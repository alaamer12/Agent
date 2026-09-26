# Recipe: assemble — `/svg-animate assemble`

The artwork is cut into rectangular fragments that fly in from scattered
positions and slight rotations and lock into the complete logo. One-shot; ends
pixel-exact.

Distinct from `rise` (whole paths translating, no clipping) and from `mosaic`
(tiles gate opacity in a mask; here the pieces themselves move).

## The fact this recipe rests on

**A `clip-path` travels with the element it is applied to when that element is
transformed.** Measured directly, with no animation in the way:

| test | ink |
|---|---|
| fragment clipped to x<150, then `translateX(-160px)` | **0 px** |
| same clip, no transform (control) | 7150 px |

If the clip were pinned to the canvas the first row would have shown artwork
sliding through a fixed window. It does not — the window moves with the art, so
each fragment carries its own piece. That is what makes a shatter-and-assemble
buildable in declarative SVG at all.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="path-teal" d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="path-navy" d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <clipPath id="frag-0" clipPathUnits="userSpaceOnUse"><rect x="0.0" y="0.0" width="75.0" height="55.0"/></clipPath>
    <clipPath id="frag-1" clipPathUnits="userSpaceOnUse"><rect x="75.0" y="0.0" width="75.0" height="55.0"/></clipPath>
    <!-- … one clipPath per fragment … -->
  </defs>

  <style>
    .f0 { clip-path: url(#frag-0); animation: fly-0 0.9s cubic-bezier(0.2, 0.9, 0.25, 1) 0.05s both; }
    @keyframes fly-0 {
      from { transform: translate(-83.4px, 61.2px) rotate(-7.1deg); opacity: 0; }
      to   { transform: translate(0, 0) rotate(0deg); opacity: 1; }
    }
    /* … one rule and one keyframe block per fragment: the offsets differ … */
    @media (prefers-reduced-motion: reduce) { .f0 { animation: none; } /* … */ }
  </style>

  <g class="f0"><use href="#path-teal"/><use href="#path-navy"/></g>
  <!-- … one group per fragment, each holding the COMPLETE artwork … -->
</svg>
```

## Notes

- **Every fragment group contains both full paths.** The clip is what makes it a
  fragment. Do not try to split the `d` data itself — that is how letterform
  holes get lost.
- **Each fragment needs its own `@keyframes`.** The flight offsets are different
  per piece, and a shared keyframe set makes the whole logo arrive as one rigid
  sheet, which is `rise` with extra steps.
- Fragment count ≈ 8 (4 × 2) on this canvas. Each fragment must be at least a
  few times F across or a thin feature straddles two pieces and arrives bent;
  with F = 4.84 the 75 × 55 fragments are comfortably safe.
- Offsets: `dx` up to ±0.55·W, `dy` up to ±1.1·H, rotation ±8°. Larger
  rotations start to read as a shuffle rather than an assembly, and the
  rotation is only legible at all because the clip rotates with the piece.
- Stagger ≈ 0.09s per fragment; `both` fill so a fragment is invisible before
  its own delay instead of sitting assembled for a moment first.
- Total beat = last delay + 0.9s. Keep it under ~1.8s or the pieces start
  looking unrelated.
- **Verified in Chromium 153 only.**
