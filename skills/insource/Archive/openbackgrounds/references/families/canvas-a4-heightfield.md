---
family: canvas-a4
name: Heightfield & Contour
renderer: canvas2d
members: [contour-map]
---

# Canvas A4 — Heightfield & Contour

A sampled scalar surface, re-evaluated every frame, drawn as filled elevation
bands and marching-squares isolines. One member today; the rules below are what
any second heightfield scene must reproduce to join the family.

## Members

| id | name | lines | tier | distinguishing trait |
| --- | --- | --- | --- | --- |
| contour-map | Contour Map | 457 | XL | 2-octave 3D simplex, 5 contour levels, 2 index contours, 3-step hillshade, 6-band hypsometric fill |

## Shared scaffold

Canvas 2D, opaque context, one full-bleed holder. Size from
`offsetWidth/offsetHeight` with a window fallback, clamp `devicePixelRatio` to
1.5, floor the backing store, write the CSS size, set the transform to the DPR,
then rebuild every size-dependent structure from the CSS dimensions. The canvas
is never cleared by the browser; the first fill of each frame is an opaque
ground, so nothing accumulates and the host backdrop never shows.

Mount order: context, noise factory, palette, resize (which allocates the grid
and the path store), a short synchronous warmup, passive resize listener, FPS
meter, RAF. Warmup is 6 frames — enough to move the 3D noise slice off a
degenerate region, nothing more, because every frame is recomputed from scratch.

The frame body is a pure function of frame counter and size; only `frame`
carries between frames, which is why resize needs no cross-fade.

## Math primer

**Grid.** `cell = clamp(sqrt(W·H / 5200), 9, 16)`; `cols = ceil(W/cell) + 1`,
`rows = ceil(H/cell) + 1`. At 640x400 the raw cell is 7.0165, clamped to 9:
73x46 samples, 3240 cells. At 1920x1080 the raw cell is 19.9692, clamped to 16:
121x69 samples, 8160 cells. Thumbnails get chunky facets, large frames fine
ones, and visible contour density stays close to constant.

**Sampling.** `scale = 2π·0.82 / short` with `short = min(W, H)`, so one noise
unit spans 77.63 px at 640x400 and 209.51 px at 1920x1080. `ny = (j·cell −
frame·0.05)·scale` carries the drift. Height is
`h = clamp(0.5 + 0.34·(n₁ + 0.2·n₂), 0, 1)`, with `n₁ = noise3D(nx, ny, t)` and
`n₂ = noise3D(2.17·nx + 31.4, 2.17·ny + 12.7, 1.6t)`; both return −1..1, so `h`
spans 0.092..0.908 and never clips. The second octave is offset in x, y and z,
so the octaves do not share ridge lines.

**Bands and shade.** `band = clamp(floor(mean·6), 0, 5)`. With `g = 14/cell`,
`dhdx = (tr + br − tl − bl)·0.5·g`, `dhdy = (bl + br − tl − tr)·0.5·g` and light
`(−0.58, −0.81)`, normalized to 0.9963:
`shade = clamp(floor((0.5 + 0.5·(dhdx·lx + dhdy·ly))·3), 0, 2)`. Three levels,
not a smooth ramp, is what makes the relief read at thumbnail size.

**Contours.** Thresholds `v = (l+1)/6` for l = 0..4: 0.1667, 0.3333, 0.5,
0.6667, 0.8333. Corners are bits TL=8, TR=4, BR=2, BL=1; codes 0 and 15 skip,
the ten single-segment codes emit one segment, and saddles 5 and 10 emit two
disjoint segments with no asymptotic decider.

**Edge crossing.** `t = clamp((v − a)/(b − a), 0, 1)`, 0 when
`|b − a| < 1e-6`. The denominator's sign must survive: a
`max(epsilon, b − a)` guard turns every descending edge into a tiny positive
delta and flings its crossing far outside the cell.

Per frame the grid costs `2·cols·rows` noise calls and
`levels·(cols−1)·(rows−1)` threshold tests: 6716 and 16,200 at 640x400, 16,698
and 40,800 at 1920x1080.

## Shared helpers

**Path stores.** Contour segments go into one path per level (5), so each level
is a single stroke call; bands go into 18 (6 × 3), one fill each. Paths are
reallocated every frame — `Path2D` has no reuse API — and that is the family's
main garbage churn.

**Pixel snapping.** Band rects use rounded cell corners, so neighbours share an
edge exactly or leave no gap. Unrounded rects double-blend the overlap and print
a visible grid at band alpha.

**Index emphasis.** Draw order is minors first, index contours second, so the
bold ink wins wherever they touch. Index lines get a wide low-alpha halo
underlay (5.0 px at 0.05) plus a 2.9 px core at 0.95.

**Palette construction.** Seven HSL stops are interpolated at `b/5` to produce
one hue per band; each band's three shades are its lightness ±1.2, clamped
3..92. Minor lines desaturate to 34% and lift lightness by 30 points; index
lines use a single warm hue near 44–49°.

## Conventions

CSS pixels, origin top-left, y down. Time is the frame counter; multiply by 60
for per-second rates. Colours are display sRGB, authored as HSL strings, and
composited without linearization. Alpha is per-pass, not per-cell.

## Variation map

| if you want | change |
| --- | --- |
| bigger landforms | lower `freq` below 0.82 or widen the cell clamp |
| more contour lines | raise `levels`; keep indexEvery at 2 so half stay minor |
| flatter, more cartographic relief | lower `shadeGain` toward 8 and keep 3 shade steps |
| darker, moodier sheet | raise `bandAlpha` toward 0.34 and deepen the multiply gradient |
| crisper contours | raise `cells` toward 7000 (smaller cells, more facets) |

## Porting

A framework without `Path2D` needs per-cell line segments instead: slower,
visually identical. The noise substitute must return −1..1 and be continuous in
3D. Do not replace the
per-cell fill with an image-data shader unless you also reproduce the 3-level
shade quantization — smooth shading changes the look more than the palette does.
Keep the opaque context and the 6-frame warmup; without warmup the first visible
frame sits at z = 0.00022, which is a valid but different slice of the volume.

## Failure modes

- **Long straight chords across the sheet →** edge fraction divided by a
  clamped-positive delta; preserve the sign or guard on absolute value.
- **Visible grid of seams in the fill →** band rects not rounded to whole
  pixels, so overlaps double-blend at 0.24 alpha.
- **Sheet reads as coloured static →** too many levels or saturated minor
  lines; drop `levels` or reduce `lineSat` toward 34.
- **Contours look like staircases →** corners classified but crossings snapped
  to cell corners instead of interpolated.
- **Relief looks embossed, not lit →** shade sign or light vector flipped;
  `lx = −0.58`, `ly = −0.81` is upper-left light with y down.
- **Index lines disappear into the minors →** draw order reversed, or the halo
  drawn after the core.

## Verification heuristics

- Contours are closed or edge-terminated curves; no segment longer than one
  cell diagonal.
- Six distinct band values are present, two index levels heavier than the rest.
- Dominant hue band is teal-to-moss (170–200°) with buff index ink near 45°.
- Bottom-right is measurably darker than top-left (multiply gradient).
- Topology changes smoothly frame to frame; nothing pops on resize.
