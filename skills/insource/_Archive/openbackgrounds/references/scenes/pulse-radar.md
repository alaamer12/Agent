---
id: pulse-radar
name: Pulse Radar
family: canvas-a5
renderer: canvas2d
poster: assets/posters/pulse-radar.jpg
complexity: L
source_lines: 420
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Pulse Radar

## 1. Identity

A phosphor radar scope: a rotating sweep wedge charges target returns inside
expanding rings, all of it eroding on a translucent green-black veil.

## 2. Perceived look

Monochrome green on near-black, with two edge qualities in deliberate contrast —
soft radial glows around each blip and a hard 2–4 px diamond at its centre.
Four grid rings, twelve spokes and 72 bezel ticks sit faintly beneath. Density
is sparse: 26 returns at 640x400. The focal point is the origin. At t = 3 s the
sweep sits 4.5 rad in and six rings are expanding, with the returns it has
already crossed lit.

## 3. Frame anatomy

1. **Veil** — full-rect `rgba(4, 12, 10, 0.1)` in `source-over`, every frame;
   the phosphor's resting colour, never a clean clear.
2. **Grid** — 4 rings, 12 spokes, 72 bezel ticks, `source-over`; strokes
   `hsla(162, 62%, 26%, 0.13)` at 1.2 px, ticks at 0.2.
3. **Rings and sweep** — in `lighter`: 5–6 aged rings with echoes, the 26-slice
   wedge, the 1.7 px leading edge.
4. **Returns** — additive: one 64 px glow sprite per blip, a hard
   `rgb(226, 255, 240)` diamond, 18 random 1.4 px specks.
5. **Origin and bezel** — `source-over`: 2.2 px dot, 7 px ring, then a radial
   shadow to `rgba(1, 4, 4, 0.6)`.

Canvas is opaque (`alpha: false`); the host backdrop never shows.

## 4. Motion law

The sweep advances 0.0125 rad per frame — 0.75 rad/s, one revolution every
502.65 frames (8.378 s). A ring is emitted every 42 frames (0.7 s) and lives 250
frames (4.167 s), expanding at `maxR/250` = 1.6906 px/frame (101.4 px/s) at
640x400 and 4.9345 px/frame (296.1 px/s) at 1920x1080. Blips are static; only
their charge moves, decaying by 0.9925 per frame and reset to 1 when the sweep
crosses their bearing. A ring passing within 3.2 px of a blip's radius lifts it
to 0.3 of its weight. Eighteen clutter specks are re-randomised every frame.
Nothing loops; the sweep phase is derived from the global frame counter.

## 5. Technique and math

**Grid and bezel.** Four rings at `gridR·i/4`, twelve spokes, and 72 ticks at
1.2 px: every sixth tick runs `1.02–1.085·gridR`, the rest `1.055–1.075·gridR`,
all at alpha 0.2. The bezel shadow is a radial gradient from transparent at
`0.34·0.62·hypot(W,H)` to `rgba(1,4,4,0.6)` at the outer radius.

`sweep = (frame·0.0125) mod 2π`. A blip at bearing `α` is crossed when
`((α − from) mod 2π) ≤ ((to − from) mod 2π)`, both angles normalised to 0..2π.

The wedge spans 1.15 rad behind the edge in 26 slices of 0.04423 rad; slice `i`
has gain `k = (1 − i/26)^2.3`, fill `hsla(166, 100%, 50 + 16k%, 0.062k)`, and is
bounded by `maxR` and an inner radius of `0.05·gridR` = 8.4 px. The edge is a
1.7 px radial line with alpha 0.8 at the centre, 0.44 at 45% and 0.06 at the rim.

Rings: `r = (age/250)·maxR`, alpha `0.32·weight·(1 − t)^1.15`,
width `max(1.2, 1.9·(1 − 0.45t))`, hue `163 + U(−12, 16)`, lightness `64 − 12t`.
An echo ring at `0.974r`, hue + 10, lightness 70, alpha × 0.3, staves off the
"static circle" read.

Blips are uniform over the disc, not the radius:
`r = 0.97·maxR·sqrt(U)`, so areal density is even. Count is
`clamp(round(W·H/15000), 26, 190)` — 26 at 640x400, 138 at 1920x1080. Charge
follows `charge ← max(0.9925·charge, 0.3·ringWeight, sweep hit = 1)`. A blip is
drawn only above 0.03; glow diameter is `size·(5.2 + 7.4·charge)` (26.5–45.4 px
at full charge), glow alpha `min(0.85, 0.66·charge·weight)`, diamond alpha
`min(0.96, 0.9·charge)`.

Persistence is the compositing constraint: with a 0.1 veil, anything deposited
every frame reaches a 10× steady state. That is why discharged blips are skipped
entirely and why the grid, although `source-over`, still settles near 0.6 alpha
rather than its nominal 0.13.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | DPR clamp | L |
| fade | rgba(4,12,10,0.1) | alpha 0.05–0.2 | veil; sets tail length and 1/alpha gain | H |
| sweepSpeed | 0.0125 | 0.006–0.03 | rad/frame; 8.378 s per revolution | H |
| sweepSpan | 1.15 | 0.4–1.6 | wedge angular width behind the edge | H |
| sweepSteps | 26 | 10–40 | wedge slices; banding vs cost | L |
| sweepAlpha | 0.062 | 0.03–0.12 | wedge fill opacity at the edge | M |
| edgeAlpha | 0.8 | 0.4–1 | leading-edge line opacity | M |
| innerR | 0.05 | 0.02–0.12 | wedge inner radius as a fraction of gridR | L |
| emitEvery | 42 | 20–90 | frames between rings | H |
| ringLife | 250 | 120–400 | ring lifetime; sets expansion speed | H |
| ringAlpha | 0.32 | 0.15–0.5 | ring stroke opacity | M |
| ringWidth | 1.9 | 1.2–3 | ring stroke at birth | L |
| ringHue | 163 | 140–200 | ring colour hue | M |
| echo | 0.974 | 0.95–0.99 | echo ring radius factor | L |
| blipArea | 15000 | 8000–30000 | area per blip; count = area/blipArea | H |
| blipDecay | 0.9925 | 0.985–0.998 | charge decay per frame | H |
| blipMin | 0.03 | 0.01–0.1 | draw threshold; below it a blip is skipped | H |
| blipRing | 0.3 | 0.1–0.6 | charge injected by a passing ring | M |
| blipSweep | 1 | 0–2 | charge injected when the sweep passes a blip | M |
| minBlips / maxBlips | 26 / 190 | 10–80 / 80–400 | blip count clamp | M |
| clutter | 18 | 0–40 | random specks per frame; persistence multiplies by 10 | L |
| gridRings / gridSpokes | 4 / 12 | 2–8 / 6–24 | polar grid density | L |
| gridAlpha / bezelAlpha | 0.13 / 0.2 | 0.05–0.3 / 0.1–0.4 | grid and bezel line opacity | L |
| warmup | 180 | 60–300 | primed frames; leaves 4 rings, sweep 2.25 rad | M |

## 7. Palette and color

Veil `rgba(4, 12, 10, 0.1)`; ground after resize `#020605`. Everything luminous
is green: rings `hsl(163 ± 12..16, 100%, 64 − 12t%)`, wedge `hsl(166, 100%, 50 +
16k%)`, edge `hsl(160–168, 100%, 60–82%)`, grid `hsl(162, 62%, 26%)`, origin dot
`hsl(160, 100%, 88%)`, diamond `#E2FFF0`. The glow sprite runs
`rgba(198, 255, 232, 0.95)` → `rgba(96, 255, 208, 0.5)` → `rgba(34, 214, 168,
0.14)` → `rgba(18, 140, 118, 0.03)` → transparent. Display sRGB; additive
stacking pushes hot cores toward white-green.

## 8. Composition and camera

Orthographic top-down, centre pinned to `(0.5W, 0.5H)`. The grid radius is
`0.42·min(W, H)` = 168 px at 640x400; the sweep and rings reach
`0.56·hypot(W, H)` = 422.64 px, well past the 377.4 px half-diagonal, so rings
and wedge always run off-frame rather than ending inside it. The scope stays
circular at any aspect ratio. Bezel shadow darkens the corners. At very wide
aspect ratios the circle occupies less height, and the wedge reads as a long
horizontal slash.

## 9. Randomness and seeds

`Math.random()` throughout, unseeded; any seed gives the same distribution.
Blip bearing is uniform 0..2π, radius `0.97·maxR·sqrt(U)`, initial charge 1 draw
of U(0,1), weight 0.4..1, size 2.1..3.6 px. Ring hue and weight, and all 18
clutter specks, are re-drawn every frame. Warmup of 180 frames leaves 4 rings
and the sweep at 2.25 rad (0.358 turn) — the source comment claims a full
revolution, but the frame arithmetic does not.

## 10. Performance budget

At 640x400: 26 blips, 5–6 rings × 2 arcs, 26 wedge fills, 1 gradient stroke, 18
specks, 4 grid rings + 12 spokes + 72 ticks, plus 3 full-screen passes (veil,
bezel shadow, and the 26 wedge fills together covering 40.1% of the frame).
Backing store 960x600. Holds 60 fps comfortably. Cut order: `sweepSteps`, then
`blipArea` (fewer returns), then `clutter`.

## 11. Host integration

Standard contract. Mount: opaque context, bake the 64 px glow sprite, resize
(centre, radii, clear to `#020605`, build blips), 180 synchronous frames,
passive resize listener, FPS meter, RAF. Resize also empties the ring array and
re-rolls every blip, so the field re-composes; the sweep phase continues from
the frame counter and does not reset. Teardown cancels the frame, removes the
listener, stops the meter, drops the sprite, blips and rings.

## 12. Failure modes and tells

- **Grid burns in →** drawn inside the additive bracket; fixed marks must stay
  `source-over`.
- **Every blip glows permanently →** blips drawn below `blipMin`; the 10×
  reservoir turns the floor deposit into standing light.
- **Blips never light →** sweep and blip angles in different units, or the wrap
  at 0/2π ignored.
- **Returns cluster at the centre →** radius sampled uniformly instead of by
  square root.
- **Rings freeze as static circles →** echo ring missing, or ring alpha not
  decaying with `(1 − t)^1.15`.
- **No tail behind the sweep →** veil alpha too high; at 0.2 the comet is ~5
  frames long.

## 13. Tuning knobs

1. `fade` — 0.06 for a long phosphor tail, 0.15 for a crisp one.
2. `sweepSpeed` — 0.008 for a stately sweep, 0.02 for urgent.
3. `blipArea` — 9000 for a busy scope, 22000 for a sparse one.
4. `sweepSpan` — 0.7 for a thin blade, 1.4 for a wide wash.

## 14. Verification checklist

- One hue family, 150–180°; no non-green light except the white-green diamond
  cores.
- Sweep completes a revolution in 8.378 s; rings appear every 0.7 s.
- Rings expand past the frame edge; none freeze or shrink.
- No blip stays lit for a full revolution at constant brightness.
- Compare `assets/posters/pulse-radar.jpg`: same ring spacing, wedge width and
  green; blip positions differ per run.

## 15. Porting notes

The look depends on framebuffer persistence: in GL, keep an uncleared buffer and
draw a translucent full-screen quad as the veil, never `clearColor`. Keep the
additive bracket around moving light only. The glow sprite must be baked once,
not regenerated per frame, and the hard diamond must stay vector-crisp — a
texture diamond reads as a dust mote.
