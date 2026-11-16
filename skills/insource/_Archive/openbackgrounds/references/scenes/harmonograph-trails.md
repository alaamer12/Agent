---
id: harmonograph-trails
name: Harmonograph Trails
family: canvas-a5
renderer: canvas2d
poster: assets/posters/harmonograph-trails.jpg
complexity: M
source_lines: 234
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Harmonograph Trails

## 1. Identity

Four damped Lissajous pens draw overlapping rosettes in warm ink on near-black,
each swing decaying toward a slowly breathing centre and restarting when it
collapses.

## 2. Perceived look

Fine, translucent ink on a black-violet ground, with a soft haze where dozens of
passes cross and a few near-white knots where they cross repeatedly. Density is
low — four pens — but each leaves a full rosette, so the frame reads as one
layered figure occupying the middle third. Strokes are 1.2–1.85 px and
anti-aliased. Contrast is low except at crossings. At t = 3 s the figure is
fully drawn at between 39% and 55% of frame width and still accumulating.

## 3. Frame anatomy

1. **Ground** — diagonal linear gradient `#080610` → `#05040c` at the midpoint
   → `#090711`, painted at mount and after every resize, never per frame.
2. **Veil** — full-rect `rgba(5, 4, 10, 0.02)` in `source-over`, every frame.
   This is the only thing that removes ink.
3. **Pens** — four paths of three points each, stroked in `lighter` with round
   caps and a 1.2–1.85 px width, then the composite is restored.

Canvas is opaque (`alpha: false`), so the host backdrop never shows and the
settled ground is the veil colour, not the gradient.

## 4. Motion law

Each pen's parameter advances `0.05` per frame (three 1/60 segments), so one
time unit is 20 frames and 3 units/s at 60 fps. Axis frequencies are
`ratio × 0.62` cycles per time unit, detuned ±0.75%: 0.62–5.58 cycles per unit,
which at 3 units/s is **1.86–16.74 cycles/s**, i.e. periods of **0.060–0.538 s**.
The figure near-repeats every 32.26 frames (one period of the 0.62 base
frequency), but the detune prevents exact closure, so each pass lands slightly
off the last.
Amplitude decays as `exp(−decay·t)` with decay 0.02–0.036 per unit, so a pen
falls to a tenth of its travel after 63.96–115.13 units (1279–2303 frames,
21.3–38.4 s) and is replaced. The registration point breathes with periods of
5712 and 6981 frames. Nothing loops; the scene runs open-ended.

## 5. Technique and math

For pen `i`, with `d = exp(−decay·t)`, `kx = 2π·fx`, `ky = 2π·fy`:

`X = A·d·sin(kx·t + φx)`, `Y = A·q·d·sin(ky·t + φy)`, then
`x = cx + ox + X·cosθ − Y·sinθ`,
`y = cy + oy + X·sinθ + Y·cosθ`.

`A` is `min(W, H) × 0.31..0.44` — 124–176 px at 640x400, 334.8–475.2 px at
1920x1080. `q` is the squash factor 0.78..1, `θ` the rotation ±0.42 rad. `cx` is
`0.5W ± 0.07W`, `cy` is `0.5H ± 0.05H`. The breathing origin is
`ox = sin(frame·0.0011 + seed)·0.05A` and
`oy = cos(frame·0.0009 + 1.7·seed)·0.05A`, which is 6.2–8.8 px at 640x400 — small
enough to widen the figure without displacing it.

Each stroke is 3 line segments; the polyline is coarse by design, and at the
fastest part of the swing a chord is a few pixels long, so the curve never reads
as a polygon. Stroke alpha is
`0.26 · min(1, t/4) · (0.32 + 0.68·d)` and lightness is `L + (1 − d)·12`, so a
pen brightens as it decays while contributing less.

Respawn triggers when `d < 0.1`, after the frame is drawn. The replacement pen
starts at full amplitude on the outer envelope, but its alpha ramp
`min(1, t/4)` keeps it invisible for the first frames, which is what hides the
jump.

The veil gives a steady-state gain of 50× for anything deposited every frame and
a half-life of 34.31 frames (0.572 s) for old ink — enough for near-repeats to
stack, not enough to grey the ground.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | DPR clamp; backing store 960x600 at 640x400 | L |
| pens | 4 | 2–6 | concurrent rosettes; more = denser figure | H |
| baseFreq | 0.62 | 0.4–0.9 | cycles per time unit before the ratio | H |
| detune | 0.0075 | 0–0.02 | per-axis frequency spread; 0 closes the figure | H |
| segment | 1/60 | 1/120–1/30 | time per segment; larger = polygonal arcs | M |
| segments | 3 | 1–5 | segments per pen per frame; 0.05 units at 3 | M |
| decayRange | [0.02, 0.036] | 0.01–0.06 | amplitude decay per time unit | M |
| endDecay | 0.1 | 0.05–0.2 | respawn threshold on the decay envelope | M |
| ampRange | [0.31, 0.44] | 0.2–0.5 | envelope radius as a fraction of min(W,H) | H |
| squashRange | [0.78, 1] | 0.6–1 | y-axis compression; 1 = circular | L |
| centreDrift | 0.05 | 0–0.12 | breathing amplitude as a fraction of A | L |
| lineWidth | 1.3 | 0.9–2.2 | base stroke width before the 0.88–1.42 jitter | M |
| baseAlpha | 0.26 | 0.12–0.4 | per-stroke alpha; higher blows out crossings | H |
| fade | 0.02 | 0.01–0.05 | veil alpha; lower = longer trails | H |
| warmup | 340 | 80–400 | primed frames; figure is empty below ~120 | H |

## 7. Palette and color

Ground `#080610`, `#05040c`, `#090711`; veil `rgba(5, 4, 10, 0.02)`. Pens pick
one of six HSL colours: `hsl(44, 92%, 66%)` gold, `hsl(34, 86%, 60%)` amber,
`hsl(16, 82%, 58%)` orange, `hsl(344, 74%, 64%)` rose, `hsl(158, 72%, 62%)`
green, `hsl(186, 78%, 66%)` cyan. Lightness rises by up to 12 points as a pen
decays. All values are display sRGB; additive compositing pushes repeated
crossings toward the pen's hue at full saturation, then toward white.

## 8. Composition and camera

Full-bleed, no camera. The figure is centred with small random offsets and sized
from the short edge, so at 640x400 the rosette spans at most 352 px and on a
portrait canvas it still fits the width. Wide frames leave empty margins left
and right; tall frames leave them top and bottom. Strokes are never clipped
mid-drawing because the envelope plus centre offset stays inside the frame.

## 9. Randomness and seeds

`Math.random()` for everything — no seed, any seed gives the same distribution.
Uniform draws: ratio from 7 pairs, colour from 6, phases 0..2π, decay
0.02..0.036, amplitude 0.31..0.44 of the short edge, squash 0.78..1, centre
±7%/±5%, rotation ±0.42 rad, width 1.3×0.88..1.42. Warmup is 340 frames: ink
older than 100 frames is at 13.26% of its deposit, so warmup sets equilibrium,
not composition.

## 10. Performance budget

Four pens, 3 points each: 8 line segments and 4 strokes per frame, plus one
full-screen veil fill. Backing store 960x600 at 640x400. Warmup costs 340
synchronous frames but allocates nothing. Trivially above 60 fps on any GPU;
the only real cost is the full-rect alpha fill at 1080p. Cut order: pens, then
DPR, then segment count.

## 11. Host integration

Standard contract. Mount: opaque context, resize (paints the ground and builds
four pens), 340 synchronous frames, passive resize listener, FPS meter, RAF.
Resize is destructive: it repaints the ground, which erases all ink, then
rebuilds the pens, so the figure restarts from empty. Teardown cancels the
frame, removes the listener, stops the meter and drops the context and pen
array. No assets, no dependencies.

## 12. Failure modes and tells

- **Near-black frame at load →** warmup below 120 frames, or the alpha ramp not
  reaching 1 within the first rosette pass.
- **White knots at crossings →** `baseAlpha` above 0.3; the reservoir gain is
  50×, so crossings saturate fast.
- **Arcs look like polygons →** `segment` too large or `segments` above 3 without
  shortening the step.
- **Pens sit at the centre →** respawn threshold unreachable, or decay applied
  to position instead of amplitude.
- **Single line, no rosette →** detune zero, so every pass retraces exactly.
- **Ink leaves a grey haze →** veil colour lighter than the ground, or the veil
  skipped on alternate frames.

## 13. Tuning knobs

1. `fade` — 0.012 for long trails, 0.035 for crisp recent ink.
2. `baseAlpha` — 0.18 quieter, 0.32 brighter (avoid 0.4).
3. `pens` — 3 for an airy figure, 6 for a dense one.
4. `baseFreq` — 0.45 slow lazy rosettes, 0.8 busy.

## 14. Verification checklist

- Four distinct rosettes visible, overlapping in the middle third.
- Dominant hues in 16–60° warm or 158–186° cool; no pure white fill.
- Ground stays near-black violet; corners never grey over.
- Ink left by a stroke is gone within 2 s; crossings persist longer.
- Figure width 39–55% of frame width at 640x400.
- Compare `assets/posters/harmonograph-trails.jpg`: same faint density and warm
  ink; rosette shape is random per run.

## 15. Porting notes

Any 2D canvas. Additive blending is load-bearing; `lighter` maps to `ONE, ONE`.
Keep the frame-based parameter step if you want the poster's density at 60 fps;
a time-based step changes both the figure scale and the decay. Preserve the
detune and the alpha ramp on respawn — without them the scene either closes into
one line or darts on restart.
