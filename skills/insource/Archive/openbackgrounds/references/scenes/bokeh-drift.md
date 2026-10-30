---
id: bokeh-drift
name: Bokeh Drift
family: canvas-a2
renderer: canvas2d
poster: assets/posters/bokeh-drift.jpg
complexity: M
source_lines: 368
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Bokeh Drift

## 1. Identity

Sparse out-of-focus light discs — amber against teal — drift upward along a
loose diagonal, a third of them carrying a defocused lens ring.

## 2. Perceived look

Smooth and grainless, saturated light on near-black with almost no mid-tones
except where discs overlap. Density is deliberately low: 17 discs at poster
size, a crowd of 124 only at 1080p and above. Edges are soft, except that ring
sprites replace the edge with a thin brighter annulus at 72% of their radius. No focal
point; the eye reads the diagonal band. At t = 3 s the frame is 8–12% lit —
three large dim rings low-left, small teal points upper-right.

## 3. Frame anatomy

1. **Ground** — full-rect linear gradient from (0, H) to (W, 0), stops
   `#0b0704`, `#04080a` at 0.45, `#03060b`. Opaque, repainted every frame in
   `source-over`.
2. **Orbs** — one square sprite blit per orb, composite `lighter`, per-orb
   `globalAlpha` 0.05–0.55, no stroke or shadow.
3. **Shades** — three radial-gradient squares in `multiply`, core
   `rgba(12, 12, 18, 0.34)` falling to transparent at the full radius. This
   pass punches the empty ground back to black.
4. **Vignette** — radial gradient centred in frame, inner radius 0.28R, outer
   R = 0.82·max(W, H), `rgba(2, 3, 6, 0)` to `rgba(2, 3, 6, 0.7)`,
   `source-over`.

Canvas alpha is false and the ground covers every pixel, so the host's
`#000000`→`#1A0033` backdrop never shows.

## 4. Motion law

Velocity is fixed at placement: heading uniform in [−0.85π, −0.1π] rad
(up-left to up-right, y down), magnitude 0.16·(0.4 + 1.15·depth) px/frame —
depth is uniform 0.25–1, so 0.11 to 0.248 px/frame, or 6.6 to 14.88 px/s at
60 fps. Two sines add sway of
±0.03 px horizontally and ±0.025 px vertically per frame, with periods 2856
frames (47.6 s) and 3491 frames (58.2 s). Radius pulses ±13% on a per-orb period
of 8.06–26.18 s; sprite alpha pulses ±24% at 1.7× that rate. Shades crawl at up
to 6 px/s. Wrapping is toroidal with a margin of 1.1·radius, and the motion is
open-ended.

## 5. Technique and math

Count: n = clamp(round(W·H / 15500), 11, 124) — 17 at 640x400, 124 at
1920x1080 (134 before the clamp).

Placement uses b = sqrt(W·H), 505.964 px at 640x400 and 1440 px at 1920x1080.
With probability 0.58 the orb lands on the segment from (0.1W, 0.9H) to
(0.92W, 0.14H) at t uniform in 0..1, offset along the normal by j·b·0.26 with j
uniform in −1..1 — ±131.551 px at 640x400, ±374.4 px at 1080p. Otherwise it is
uniform over the rect.

Depth d is uniform 0.25..1. Radius
r = b·(0.042 + u·0.106)·(0.62 + 0.7d) with u uniform: 16.894–98.845 px at
640x400, 48.082–281.318 px at 1920x1080. Focus f = clamp(1.35 − d, 0.2, 1);
stored alpha a = clamp((0.1 + 0.4f)·(rim ? 0.78 : 1)·v, 0.07, 0.5) with v
uniform 0.8..1.2. The 0.4f term is what stops a hundred large additive discs
from lifting the ground to grey.

Colour: bias = dWarm/(dWarm + dCool), the two Euclidean distances in normalized
frame coordinates to the warm anchor (0.14, 0.88) and the cool anchor
(0.88, 0.12). Warm is chosen with probability 0.6·(1 − bias) + 0.2, then an
index is drawn from that half of the palette. The 0.2 floor lets the families
bleed.

Per frame: size = 2r·(1 + 0.13·sin(frame·s + φ)) with s uniform 0.004..0.013
rad/frame, and draw alpha = clamp(a·(0.86 + 0.24·sin(1.7·frame·s + φ)), 0.05,
0.55).

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | device pixel ratio clamp | L |
| orbArea | 15500 | 9000–26000 | area per disc; count = area / orbArea | H |
| minOrbs / maxOrbs | 11 / 124 | 5–40 / 60–300 | count clamp on small and large canvases | M |
| radiusRange | [0.042, 0.148] | 0.03–0.19 | radius before depth, as a fraction of sqrt(area) | H |
| bandBias | 0.58 | 0–1 | fraction placed on the diagonal | H |
| bandWidth | 0.26 | 0.1–0.45 | normal jitter of the band, in sqrt(area) | M |
| drift | 0.16 | 0.05–0.4 | base speed in px/frame before depth | M |
| sway | 0.5 | 0–1.5 | amplitude of the two sine displacements | L |
| breathe | 0.13 | 0–0.3 | radius pulse amplitude | L |
| rimShare | 0.34 | 0–1 | fraction drawn with the ring falloff | H |
| shade | 0.34 | 0–0.6 | multiply shade strength; keeps blacks black | H |
| vignette | 0.7 | 0.3–0.9 | corner darkening | M |
| warmWeight | 0.6 | 0.3–0.9 | warm/cool split near the anchors | H |
| warmup | 30 | 10–90 | hidden pre-roll frames | L |

## 7. Palette and color

Eight sprite colours, warm first: `#FFB248` hsl(35, 100%, 64%), `#FFD68A`
hsl(39, 100%, 77%), `#FF885C` hsl(16, 100%, 68%), `#E86078` hsl(350, 74%, 64%),
then `#3ED8CE` hsl(176, 66%, 55%), `#6CD0FF` hsl(199, 100%, 71%), `#A8F6E0`
hsl(163, 81%, 81%), `#C4B0FF` hsl(255, 100%, 85%). Ground `#0b0704` → `#04080a`
→ `#03060b`; shades `rgba(12, 12, 18, 0.34)`; vignette `rgba(2, 3, 6, 0.7)`.
The sprite colour is keyed on proximity to two anchors — warm at (0.14, 0.88)
and cool at (0.88, 0.12) in normalized frame coordinates — with `warmWeight`
0.6 shifting the split toward warm. All values are display sRGB; canvas
gradients interpolate in premultiplied sRGB. Overlap saturates toward pale amber
or pale cyan, rarely white.

## 8. Composition and camera

The band is the composition: a diagonal about three quarters of the frame long,
with enough normal jitter to read as a current rather than a line. Warm discs
concentrate near the lower-left anchor and cool ones near the upper-right; the
0.2 floor lets each invade the other, and off-band discs thin into the corners.
At 21:9 the band flattens; in portrait it turns near-vertical and reads as a
rising column. No safe margins — discs bleed off all four edges.

## 9. Randomness and seeds

`Math.random()` only, no seed; any seed, same distribution. Depth uniform
0.25..1, radius multiplier uniform, alpha multiplier 0.8..1.2, breathe speed
0.004..0.013, phase uniform 0..2π, shade radius 0.28–0.5·sqrt(area). Thirty
warmup frames (0.5 s) advance positions and phases before the first visible
frame; nothing accumulates, so warmup only breaks up the spawn diagonal.

## 10. Performance budget

17–124 sprite blits per frame from 16 pre-baked 160 px canvases; three multiply
gradient fills plus ground and vignette gradients, all rebuilt per frame. Fill
cost is dominated by the largest discs: a 197.69 px sprite covers 39,082 CSS px,
and 281.318 px radii at 1080p are several full-screen overdraws. DPR capped at
1.5; 60 fps on an integrated GPU. Cut in order: `maxOrbs`, `radiusRange`, DPR,
`rimShare`.

## 11. Host integration

Standard contract: positioned `inset: 0` container, size from
`offsetWidth/offsetHeight` with a window fallback, passive resize listener, a
synchronous 30-frame warmup, then RAF. Context is
`getContext("2d", { alpha: false })`. Resize re-runs `buildScene` but not the
sprite bake, which is size-independent. Teardown removes the listener, cancels
the frame, stops the shared FPS meter, and drops every array.

## 12. Failure modes and tells

- **Every disc equally bright →** alpha not tied to depth; restore the 0.4f
  focus term.
- **Ground reads as grey fog →** total sprite energy too high; raise `orbArea`
  before touching alpha.
- **Hard-edged circles →** the final gradient stop has nonzero alpha, or the
  sprite is drawn larger than its baked square.
- **Milky gaps →** the multiply shade pass is missing or runs before the orbs.
- **A clump on one diagonal at load →** warmup skipped.
- **Discs jump at the edge →** wrap margin below the radius; use 1.1·r.
- **Square outline around a ring →** rim stops compressed; keep alpha 0 at
  radius 1.0.

## 13. Tuning knobs

1. `orbArea` — lower for more discs (9000–26000).
2. `bandBias` — lower for a looser scatter (0.35–0.8).
3. `radiusRange` — raise the top for fewer, larger discs (0.03–0.19).
4. `shade` — raise to deepen the gaps (0.15–0.5).
5. `rimShare` — raise for more lens rings (0.15–0.55).

## 14. Verification checklist

- 17 discs at 640x400, 124 at 1920x1080, by the area formula.
- Warm pixels lower-left, cool upper-right; no green, no white field.
- Largest disc 197.69 px across at 640x400, sprite edges never visible.
- Mean luminance 3–8%; corners at or below `#050505` after the vignette.
- Rings are continuous annuli at 72% of the radius, not dotted.
- Compare to `assets/posters/bokeh-drift.jpg`: same sparse count, same lower-left
  amber cluster. Positions will differ.

## 15. Porting notes

Any 2D canvas works, but `multiply` is required for the shade pass; whole-element
CSS `mix-blend-mode` is not equivalent. If the wrapper forces `alpha: true`,
keep the opaque ground.
