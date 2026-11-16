---
id: spectrum-cascade
name: Spectrum Cascade
family: canvas-a3
renderer: canvas2d
poster: assets/posters/spectrum-cascade.jpg
complexity: M
source_lines: 303
dpr_max: 1.8
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Spectrum Cascade

## 1. Identity

Eighteen blurred vertical color bands — blue, teal, indigo, magenta — drift and
pulse out of phase into a soft curtain.

## 2. Perceived look

Soft-focus and layered, with no hard edge: blur radii of 13.07–21.52 px at
640x400 dissolve every boundary. Full-bleed but low-contrast; the brightest
column reaches roughly 40% luminance while corners stay under 8%. No focal
point, only a broad lavender node above center-right. At t = 3 s the frame is a
curtain of blue and violet washes with one pale blue column left of center.

## 3. Frame anatomy

1. **Clear** — canvas is created with alpha true; `clearRect` each frame.
2. **Background** — opaque vertical linear gradient `#030212` → `#14052c`,
   `source-over`, so the host backdrop never shows.
3. **Stripes** — 18 rectangles under `lighter`, each a three-stop diagonal
   gradient blurred by its own `ctx.filter`, alpha 0.126–0.396. They overrun by
   1.3 × width and 1.4 × height.
4. **Soft-light radial** — center (0.58W, 0.4H), radius 1.08·max(W, H),
   `rgba(42, 18, 74, 0.22)` inside to `rgba(14, 6, 32, 0)` outside.
5. **Screen beam** — horizontal gradient, `rgba(120, 90, 210, 0.12)` at the
   midpoint, transparent at 0.05 and 0.95.
6. **Multiply vignette** — radial at (0.5W, 0.54H), transparent at 0.1·max to
   `rgba(4, 1, 20, 0.78)` at 0.85·max.
7. **Overlay haze** — full-frame `rgba(8, 10, 26, 0.45)`.

## 4. Motion law

Time is elapsed seconds from `performance.now()`, so motion is frame-rate
independent. Each stripe's center sways as sin(t·s + φ) with |s| = 0.112–0.24
rad/s, a period of 26.18–56.11 s, over ±0.06–0.15 of the canvas width. Width
and brightness pulse at 0.2016–0.5376 rad/s (11.69–31.17 s) from a second sine
with its own phase. Width scales by 0.712–1.288 and alpha by 0.7–1.1. Nothing
loops; stripes are independent oscillators.

## 5. Technique and math

Stripe i gets a base center (i + 0.5)/18 plus uniform jitter of ±0.0125,
clamped to −0.18..1.18, and palette entry i mod 8. Per-stripe random values:
float amplitude 0.06–0.15, signed drift speed 0.112–0.24 rad/s, pulse speed
0.2016–0.5376 rad/s, width fraction 0.06–0.14, two phases uniform 0–2π, blur
scale 0.4–1.5, base alpha 0.18–0.36.

Per frame, with drift = sin(t·s + φ) and wave = (sin(t·p + ψ) + 1)/2:

- x = W·(center + drift·amplitude)
- sw = W·width·(1 + (wave − 0.5)·0.576)
- alpha = base alpha·(0.7 + 0.4·wave)
- blur = 10 + 0.012·max(W, H)·blur scale

The fill gradient runs from (x − 0.6sw, 0) to (x + 0.6sw, H), so bands lean
slightly. Its stops move each channel of the base hex toward 0 or 255 by
−0.5 − 0.2·wave at the top, 0.18 + 0.32·wave at the midpoint, and
−0.25 + 0.1·wave at the bottom: 50–70% darkening at the top edge, 18–50%
lightening in the core, 15–25% darkening at the bottom. The rect spans
x − 0.65sw to x + 0.65sw and −0.2H to 1.2H.

At 640x400 the blur is 13.07–21.52 px; at 1920x1080 it is 19.22–44.56 px,
because it scales with the larger dimension. Four post passes then tint, lift,
vignette and flatten the result.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.8 | 1–2 | backing-store clamp | M |
| stripeCount | 18 | 10–28 | band count | H |
| minStripeWidth | 0.06 | 0.03–0.1 | narrowest band | H |
| maxStripeWidth | 0.14 | 0.08–0.2 | widest band | H |
| floatStrength | 0.1 | 0.02–0.2 | lateral sway | H |
| pulseStrength | 0.24 | 0–0.5 | width breathing | M |
| baseSpeed | 0.16 | 0.08–0.3 | master rate | H |
| stripe alpha | 0.18–0.36 | 0.1–0.45 | per-band opacity | H |
| blur base | 10 px | 4–20 | minimum blur | H |
| blur slope | 0.012 | 0.006–0.02 | blur growth per px | H |
| overlay center | (0.58, 0.4) | 0–1 each | tint node position | M |
| vignette alpha | 0.78 | 0.4–0.95 | corner darkening | M |
| haze alpha | 0.45 | 0.2–0.6 | final flattening | L |
| palette | 8 stops | any 8 | band colors | H |

## 7. Palette and color

Eight authored sRGB hex values, reused twice: `#1f2d92` (hsl 233, 65%, 35%),
`#123d9c`, `#0f5894`, `#136c8b` (hsl 196, 76%, 31%), `#1e6f66`, `#3f4f8f`,
`#5a2c82`, `#7a2671` (hsl 306, 53%, 31%). Each gradient lightens the core
toward white and darkens both ends; the tint, beam, vignette and haze then
desaturate and deepen the stack. Alpha is per stripe, not in the colors; all
interpolation is display sRGB.

## 8. Composition and camera

Full-bleed, no camera. Centers and widths are fractions of W, so the band count
is fixed at any aspect: 18 bands across 1920 px sit 106.7 px apart with cores up
to 346 px wide. Blur scales with max(W, H), so a portrait frame is
proportionally softer. The radial tint stays at 58% across and 40% down; the
vignette center is 54% down. No margins.

## 9. Randomness and seeds

`Math.random()` on mount only, unseeded, for all 18 stripes. Any seed gives the
same distributions: centers jittered ±0.0125, width 0.06–0.14, speeds in their
ranges, two phases 0–2π. No warmup is needed because each stripe carries its own
phase. Stripes are never rebuilt on resize; only the canvas is resized.

## 10. Performance budget

18 blurred fills plus four full-frame blends; the stripe rects alone cover about
32.8 screens of fill (18 × 1.3 × 1.4) before the blur. The filters dominate: separable gaussians at 13.07–21.52 px radius at
640x400, up to 44.56 px at 1080p. DPR clamp 1.8. Holds 60 fps on a discrete GPU
at 640x400; drops on integrated at 1080p. Cut order: stripeCount, blur slope,
DPR.

## 11. Host integration

Mount order: context, resize, buildStripes, window resize listener,
ResizeObserver on the holder, meter, start time, RAF. Resize only re-sizes the
backing store and sets the transform; stripes survive. Teardown removes the
listener, disconnects the observer, cancels the frame and stops the meter. No
external assets. Deviations: alpha canvas, ResizeObserver.

## 12. Failure modes and tells

- **Hard-edged bars →** `ctx.filter` unsupported; bake blurred sprites.
- **Flat grey curtain →** `lighter` replaced, or the post passes dropped.
- **Bands missing at one edge →** drift pushes centers past the clamp; keep
  floatStrength at 0.1.
- **Core turns black or neon →** adjustColor sign flipped; negatives go toward
  0, positives toward 255.
- **Layout jumps on panel resize →** stripes rebuilt on resize; keep them.
- **Vignette too heavy →** 0.78 is the outer stop, not a flat fill.

## 13. Tuning knobs

1. `stripeCount` — 14 for cleaner columns, 22 for a denser curtain.
2. `blur slope` — 0.009 sharper, 0.016 softer.
3. `floatStrength` — 0.06 calm, 0.14 visible drift.
4. `baseSpeed` — 0.1 for a slower register.
5. `pulseStrength` — 0.15 for subtler breathing.

## 14. Verification checklist

- Dominant HSL hues 230–310; no warm band above 5% of pixels.
- Three or four soft column clusters at 640x400; no edge sharper than the blur.
- Corners under 8% luminance; the node at 58% across, 40% down.
- Drift period between 26.18 s and 56.11 s.
- No band snaps on resize.
- Compare with `assets/posters/spectrum-cascade.jpg` for hue class, blur scale
  and vignette; band positions differ per load.

## 15. Porting notes

Canvas filters and the soft-light, screen, multiply and overlay composites are
required. In WebGL, replace the blur with a separable gaussian or mip blur and
reproduce the four passes explicitly; CSS mix-blend-mode blends the whole
element, not the stack.
