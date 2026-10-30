---
id: aurora-waves
name: Aurora Waves
family: canvas-a3
renderer: canvas2d
poster: assets/posters/aurora-waves.jpg
complexity: M
source_lines: 315
dpr_max: null
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Aurora Waves

## 1. Identity

Three bundles of long translucent violet ribbons sweep along the 45° diagonal,
each a 160-strong fan of nested cubic curves curling through the center.

## 2. Perceived look

Smooth, glossy ribbons with no texture. Edges are soft because every curve is
32% opaque and overlaps brighten additively; crossings burn toward white-violet.
Density peaks in the middle third where all three bundles cross and falls away
at the corners. At t = 3 s the newest strands are teal-blue (HSL ≈184°) with a
tail back to ≈205°; as the hue parameter sweeps its 11–24 window the braid passes
violet, blue, teal and amber over ~22 s. The shipped poster captures the earlier
violet phase (h ≈ 11), so match its diagonal structure, strand count and soft
crossings rather than its exact hue at 3.5 s.

## 3. Frame anatomy

1. **Cleared canvas** — the context takes no options, so alpha is true and each
   frame clears to transparent.
2. **Backdrop** — one vertical linear gradient per frame, `#080015` at y = 0 to
   the current stroke color at alpha 0.32 at y = height, `source-over`. The
   lower stop is translucent, so the host `#000000` → `#1A0033` shows through.
3. **Ribbons** — three wave groups, oldest line first within each, under
   `lighter`. Each line is one cubic, stroke `rgba(r, g, b, 0.32)`, 1.6 device
   px, round caps and joins.
4. Composite restored to `source-over`; no vignette, grain, or post pass.

## 4. Motion law

Each wave owns four phase angles advancing independently at a random signed
0.0035–0.0075 rad per frame, i.e. 0.21–0.45 rad/s at 60 fps, a sine period of
13.96–29.92 s. The rates differ, so a bundle never repeats. One line is
appended per wave per frame and the oldest dropped past 160, so the fan is the
last 2.67 s of motion. The hue parameter rises 0.01 per frame from 11 to 24 and
falls back: 21.67 s each way, 43.33 s round trip. Motion is open-ended.

## 5. Technique and math

Each frame a wave appends one record of four sine values plus the current
color. Drawing evaluates, with R = 0.5·√(W² + H²) in device pixels, cx = W/2,
cy = H/2, rotation φ = 0.785398 rad, amplitude A = 0.5, and s0..s3 the recorded
sines:

P0 = (cx − R·cos(A·s0 + φ), cy − R·sin(A·s0 + φ))

P3 = (cx + R·cos(A·s3 + φ), cy + R·sin(A·s3 + φ))

P1 = (cx − (R/3)·cos(2A·s1), cy − (R/3)·sin(2A·s1))

P2 = (cx + (R/3)·cos(2A·s2), cy + (R/3)·sin(2A·s2))

Controls use twice the amplitude and no rotation, which is why each ribbon
pinches near the center and throws a curl the endpoints never show. Endpoints
lie on the circumscribed circle — R = 377.36 px at 640x400, 1101.45 px at
1920x1080 — so they reach the corners at most.

Color: r = floor(127·sin(0.3h) + 128), g = floor(127·sin(0.3h + 2) + 128),
b = floor(127·sin(0.3h + 4) + 128), alpha 0.32. The 2-rad offsets sweep the
wheel rather than shift one hue: h = 11 is rgb(107, 22, 236), h = 24 is
rgb(228, 156, 3). Preload advances the hue only three times while appending 160
lines per wave, so the opening fan is monochrome; each line then keeps its
birth color, giving a 1.6-unit hue gradient along the trail.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| dpr clamp | none | 1–3 | backing-store multiplier; stroke thinness | M |
| rotation | 45° (0.785398 rad) | 0–90° | ribbon direction | H |
| waves | 3 | 1–6 | bundle count, 160 curves each | H |
| width | 160 lines | 40–320 | trail depth in frames | H |
| hue | [11, 24] | 0–360 | palette window | H |
| hue step | +0.01 per frame | 0–0.03 | color travel speed | M |
| amplitude | 0.5 | 0.25–0.9 | curvature; below 0.25 ribbons straighten | H |
| speed | [0.0035, 0.0075] rad/frame | 0.001–0.02 | phase drift per angle | H |
| line width | 1.6 device px | 0.8–3 | stroke weight | M |
| stroke alpha | 0.32 | 0.1–0.6 | additive saturation per curve | H |
| preload | 160 per wave | 0–160 | lines present at first paint | M |
| background | on | on/off | paints the gradient ground | L |

## 7. Palette and color

Ground: `#080015` fading to the live stroke color at alpha 0.32 at the bottom,
over the host's `#000000` → `#1A0033`. Strokes: `rgba(r, g, b, 0.32)` from the
three-sine formula; anchors rgb(107, 22, 236) at h = 11 and rgb(228, 156, 3) at
h = 24. Additive overlap saturates toward white with a violet cast. All values
are display sRGB, interpolated in sRGB, with no tone mapping.

## 8. Composition and camera

Full-bleed 2D, no camera. The braid always runs at 45° from upper-left to
lower-right, so on 16:9 it crosses the side edges rather than the actual
corners, and on portrait it crosses top and bottom. R is half the diagonal, so
endpoints ride the corner circle at every aspect. No safe margins; curves leave
the frame by design.

## 9. Randomness and seeds

`Math.random()` throughout, no seed: four initial phases uniform in 0–2π per
wave, four speed magnitudes uniform 0.0035–0.0075 with random sign. Any seed
gives the same distribution. Priming is only the 160-line preload per wave (480
lines, hue advanced three steps), which hides the build-up.

## 10. Performance budget

480 cubics per frame, spanning up to 754.72 px at 640x400, stroked at 1.6
device px additively. No per-frame allocation beyond three records, a color
string and a gradient. DPR is uncapped, so 1920x1080 at DPR 2 fills a 3840x2160
backing store. Fill-bound at 4K. Cut order: waves, trail width, then DPR.

## 11. Host integration

Mount creates a class instance that builds three waves, preloads, then resizes;
start() begins the RAF and the shared meter. A passive window resize listener
is the only event; no ResizeObserver. Teardown calls destroy(), which cancels
the frame, stops the meter, removes the listener, clears and drops the lines.
Deviations: default-alpha context, no DPR clamp.

## 12. Failure modes and tells

- **Straight diagonal bars →** amplitude near 0; restore 0.5.
- **Hair-thin threads on retina →** a DPR transform was added; divide the 1.6 px
  stroke by dpr or keep the identity transform.
- **Black frame bottom →** opaque canvas; the end stop is 32% alpha.
- **Flat lilac wash →** too many waves or a longer trail without lower alpha.
- **Frozen or jumping color →** hue advanced per wave, or clamped off 11–24.
- **Blunt ends visible →** R taken from width instead of the diagonal.
- **Static braid →** phases re-randomized per frame, not accumulated.

## 13. Tuning knobs

1. `amplitude` — 0.7 for tighter curls, 0.35 for flatter ribbons.
2. `waves` — 4 or 5 for density; each adds 160 curves.
3. `width` — 220 for longer tails; below 80 the fan looks chopped.
4. `hue` — shift both ends to move the palette window.

## 14. Verification checklist

- Ground reads `#080015` top and translucent violet bottom; host shows through.
- Three braids, 160 strands each; crossings approach white.
- Stroke hue at t = 3.5 s is ≈184° HSL (newest) with a tail back to ≈205°; the
  hue parameter drifts 0.6 units/s. The poster's violet is an earlier phase.
- No caps inside the frame; every ribbon exits an edge.
- Compare with `assets/posters/aurora-waves.jpg` for diagonal, hue band and soft
  crossings; exact strands differ.

## 15. Porting notes

Geometry is authored in device pixels: a port with a DPR transform must divide
the 1.6 px stroke by the same factor and rebuild R from the backing store.
Additive blending and the transparent canvas are required.
