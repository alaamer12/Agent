---
id: iso-drift
name: Iso Drift
family: canvas-a3
renderer: canvas2d
poster: assets/posters/iso-drift.jpg
complexity: M
source_lines: 272
dpr_max: 1.5
deps: [simplex-noise]
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Iso Drift

## 1. Identity

An isometric field of indigo hexagonal columns whose heights ride a travelling
wave, tips catching amber at the crest.

## 2. Perceived look

Faceted and matte, crisp-edged and unblurred. The top third is a hazy
blue-violet sheet of shallow tiles; the lower half resolves into column faces,
darkest on the left, lighter on top, warm on the right at the crests. Full-bleed
and dense, roughly 45–55% coverage. At t = 3 s a downward height wave crosses the
lower third, with a few amber tips and gold rim strokes.

## 3. Frame anatomy

1. **Ground** — opaque vertical gradient `#07061a`, `#0a0722` at 0.36,
   `#05040f` at 0.62, `#030209` at 1.
2. **Cold bloom** — radial at (0.5W, 0.3H), radius 0.62·max(W, H):
   `rgba(96, 88, 224, 0.2)` → `rgba(52, 44, 140, 0.08)` at 0.45 → transparent.
3. **Columns** — far to near by ascending v, three fills each: top diamond, left
   body, right body, all `source-over`; a rim stroke only when crest > 0.05.
4. **Haze** — top 72%: `rgba(14, 12, 44, 0.62)` → `rgba(10, 9, 34, 0.22)` at
   0.55 → `rgba(6, 5, 18, 0)`. Canvas alpha is false.

## 4. Motion law

A frame counter drives everything. The row wave advances 0.0175 rad per frame —
a 359.0-frame period, 5.98 s at 60 fps. The column wave advances 0.0105 rad per
frame (598.4 frames, 9.97 s). The noise coordinate advances +0.0055 per frame on
both i and j, which is 0.0055 / 0.17 ≈ 0.0324 lattice steps; because v = i + j,
that moves the pattern up-screen by 2 · 0.0324 · 0.5a ≈ 0.84 px per frame —
about 50.3 px/s at 640x400 — while the sine crests travel down. That opposition
stops the field reading as one translating sheet. Warmup is 14 frames; motion is
open-ended.

## 5. Technique and math

Edge a = clamp(√(WH/(0.8660254·440)), 14, 58): 25.92 px at 640x400, the 58 px cap
at 1920x1080. Half-width w = 0.8660254·a; origin (0.5W, 0.44H). A column at
(u, v) has top center x = W/2 + u·w and y = 0.44H + v·0.5a − lift, with
lift = a·(0.06 + 1.56h); its body is 0.5a + lift tall, so every column meets one
ground plane. Only u + v even exists: a checkerboard of hex prisms.

Height, with i = (u + v)/2 and j = (v − u)/2: n = simplex2D(0.17i + 0.0055f,
0.17j + 0.0055f), along = sin(v·0.33 − 0.0175f), across = sin(u·0.19 + 0.0105f),
h = clamp(0.5 + 0.5·(0.54n + 0.30·along + 0.16·across), 0, 1). Wavelengths are
19.04 rows (246.8 px) and 33.07 steps (742.3 px).

Depth: t = (v − vMin)/(vMax − vMin), near = 0.34 + 0.66·t^0.62,
sat = 0.55 + 0.45t, crest = smoothstep(0.62, 0.94, h·near). Top
`hsl(249 − 9h, 34 + 26·sat, 0.92·(11 + 43h)·near)`; left
`hsl(257 − 9h, 22 + 18·sat, 0.3·(11 + 43h)·near)`; right a ramp from
`hsl(243, 30 + 16·sat, 0.52·L)` to `hsl(392, 92, 57·(0.5 + 0.5·near))`, the hue
taken the long way so it passes violet, magenta, red and amber rather than
green. Rim `hsla(44, 96%, 78%, 0.5·crest)` on the two upper edges.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | DPR clamp | L |
| tiles | 440 | 280–700 | column count | H |
| minEdge / maxEdge | 14 / 58 | 10–70 | edge bounds | M |
| gridScale | 0.17 | 0.08–0.3 | noise cell | H |
| scrollSpeed | 0.0055 | 0–0.02 | pattern drift | M |
| waveK | 0.33 | 0.1–0.6 | row wavelength | H |
| waveSpeed | 0.0175 | 0.004–0.04 | row rate | H |
| crossK | 0.19 | 0.05–0.4 | column wavelength | H |
| crossSpeed | 0.0105 | 0.002–0.03 | column rate | M |
| liftMin / liftSpan | 0.06 + 1.56h | 0.8–2.2 span | column height | H |
| hue | 249 | 0–360 | base hue | H |
| accentHue | 32 | 0–60 | warm ramp end | M |
| accentFrom / accentTo | 0.62 / 0.94 | 0.4–1 | crest threshold | H |
| accentLight | 57 | 45–70 | warm ramp lightness, percent | L |
| rimAlpha | 0.5 | 0–0.8 | rim strength | M |
| haze | 0.62 | 0.2–0.9 | top fade | M |
| warmup | 14 frames | 0–60 | priming | M |

## 7. Palette and color

Ground `#07061a` → `#0a0722` → `#05040f` → `#030209`. Faces are HSL: hue 240–249,
top lightness 0.92·(11 + 43h)·near, left one third of that, right a ramp from
raw violet to `hsl(32, 92%, 57%)` — about `#f6982c` — as crest rises. Rim
`hsla(44, 96%, 78%, 0.5)` is the pale gold `#fde091`. Haze is
`rgba(14, 12, 44, 0.62)`. All display sRGB, no tone mapping.

## 8. Composition and camera

Full-bleed orthographic isometric, no perspective. Columns run past every edge;
the ground plane sits at 44% height, so near columns dominate the bottom 60%.
The edge is area-derived, so the count stays roughly constant until the 58 px
cap: the parity lattice visits 544 cells at 640x400 (v −11..21, u −16..16) and
838 at 1080p. Ultra-wide frames add columns, portrait frames add rows.

## 9. Randomness and seeds

Simplex noise from `createNoise2D()` with an unseeded permutation table; no other
RNG. Any seed gives the same height distribution. Column positions are fixed;
only the terrain varies per load. Warmup advances 14 frames (0.23 s) to leave
the aligned t = 0 pattern.

## 10. Performance budget

544 lattice positions at 640x400 (838 at 1080p), each drawn as three fills plus
an occasional 1.25 px stroke, roughly 1,600 draw calls. Overdraw is
about 7× the frame area because bodies overlap the row behind. DPR 1.5, one
simplex sample per column per frame. Cut order: tiles, DPR, rim strokes.

## 11. Host integration

Mount creates the opaque context, builds the noise function, resizes (deriving
edge), runs 14 synchronous drawFrames, adds a passive window resize listener,
starts the meter and the RAF. Resize only re-derives edge; the frame counter is
kept. Teardown removes the listener, cancels the frame, stops the meter and
drops noise and context. No ResizeObserver.

## 12. Failure modes and tells

- **Flat diamonds →** liftSpan below 1.0.
- **Gaps between top and body →** body height not tied to 0.5a + lift.
- **Near rows hidden behind far ones →** v loop descending; sort ascending.
- **Green at the crests →** warm ramp shortened to 243→32 instead of 243→392.
- **One flat shade →** near and sat unused, or depthT constant.
- **Gold rim on every column →** accentFrom below 0.5.
- **Bright top →** haze pass missing.

## 13. Tuning knobs

1. `liftSpan` — 1.0 for calmer dunes, 2.0 for towers.
2. `tiles` — 320 for bigger columns, 600 for a finer field.
3. `scrollSpeed` — 0.002 for a slower drift.
4. `accentFrom` — 0.72 for fewer amber crests.
5. `haze` — 0.4 to clear the far field.

## 14. Verification checklist

- Top diamonds 2·0.866a wide and a tall; neighbours touch.
- Front bodies reach 2.1a at h = 1 and meet the ground.
- Base hue 240–249; amber crests on under 10% of columns.
- Top 30% hazier than the bottom, contrast under 20% of the near field.
- Noise drift ≈50.3 px/s up at 640x400; no column pops.
- Compare with `assets/posters/iso-drift.jpg` for pitch, indigo tone and crest
  placement; terrain differs per load.

## 15. Porting notes

Substitute any 2D simplex returning −1..1 and keep the permutation random. The
painter sort must follow v, not insertion order. HSL interpolation is in sRGB,
so a linear-light port will shift the violet-to-amber ramp.
