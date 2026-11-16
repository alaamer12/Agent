---
family: canvas-a3
name: Analytic Fields
renderer: canvas2d
members: [aurora-waves, halftone-tide, iso-drift, spectrum-cascade]
---

# Canvas A3 — Analytic Fields

Four canvas scenes that evaluate a closed-form scalar field at fixed sample
positions every frame instead of integrating particles. Nothing accumulates:
each frame repaints the ground and redraws from the field, so the image is a
pure function of position, index, and time. Every length derives from canvas
area, so the pattern keeps its scale from 640x400 to 4K.

## Members

| id | name | lines | tier | distinguishing trait |
| --- | --- | --- | --- | --- |
| aurora-waves | Aurora Waves | 315 | M | 480 additive cubic beziers from four phase angles per wave; no DPR clamp |
| halftone-tide | Halftone Tide | 243 | S | rotated hex lattice, 20 alpha buckets, three superposed waves |
| iso-drift | Iso Drift | 272 | M | painter-sorted isometric columns, simplex plus two sine fronts |
| spectrum-cascade | Spectrum Cascade | 303 | M | 18 blurred width-modulated stripes under four full-frame blends |

## Shared scaffold

All four are single-file components: a pointer-transparent holder at
absolute inset zero containing a block canvas at full size. AuroraWaves takes
the default alpha canvas, SpectrumCascade asks for alpha explicitly,
HalftoneTide and IsoDrift pass alpha false. All read the holder size with a
window fallback and multiply by a DPR clamp — 1.5 for HalftoneTide and
IsoDrift, 1.8 for SpectrumCascade, none for AuroraWaves.

The three clamped scenes set a DPR transform and work in CSS pixels.
AuroraWaves sets no transform and works in device pixels throughout, so its
1.6 px stroke is 0.8 CSS px at DPR 2 and its curvature is computed from the
backing-store size.

Mount order is context, size, derived state, prime, meter, RAF.
SpectrumCascade builds its 18 stripes once and never rebuilds them on resize;
HalftoneTide re-derives spacing and IsoDrift re-derives edge length in their
resize paths. Teardown removes listeners, cancels the frame, stops the meter
and drops references; SpectrumCascade also disconnects its ResizeObserver, and
AuroraWaves routes teardown through a class destroy().

## Math primer

**Wave superposition.** Each field is h = 0.5 + 0.5·Σ w_i·sin θ_i with Σ w_i = 1
and h clamped to 0..1, where θ_i is linear in position and time. HalftoneTide
weights a plane sweep 0.52, a radial ripple 0.30 and a diagonal tilt 0.18;
IsoDrift weights 2D simplex 0.54, a row wave 0.30 and a column wave 0.16. For a
plane wave θ = k·p − ωt, wavelength is 2π/|k| and phase speed ω/|k| px/s.
HalftoneTide sets |k| = 2πN/√(WH) so a frame always holds N wavelengths:
N = 2.4 gives 210.8 px at 640x400 and N = 3.6 gives 140.5 px. IsoDrift's waves
run in lattice indices, so its wavelengths are 19.04 rows and 33.07 steps.

**Halftone sampling.** A hex lattice has row pitch s·0.8660254 and a half-pitch
stagger on alternate rows; rotating it by 0.26 rad stops it reading as a
spreadsheet. Dot radius is r = r_min + (r_max − r_min)·h^1.35 with
r_max = 0.56·s, so crest dots overlap their neighbours by 12 percent while the
bottom sits at 0.16·s. Perceived tone follows dot area, so the radius exponent
1.35 becomes a tone gamma of 2.7.

**Isometric projection.** With edge a, the basis is e_u = (0.8660254·a, 0) and
e_v = (0, 0.5·a). A column at lattice (u, v) has top centre
(0.5W + u·0.8660254·a, 0.44H + v·0.5·a − lift). Its top face is a diamond with
half-diagonals 0.8660254·a and 0.5·a, and its body is 0.5·a + lift tall, which
anchors every column to one ground plane. Only u + v even exists, which yields
the checkerboard.

**Bezier string art.** AuroraWaves draws 160-deep strings of cubics. Endpoints
ride the circumscribed circle of radius R = 0.5·√(W² + H²) at angle
±(0.5·sin θ + 0.785398); the two controls sit at R/3 on directions 2·sin θ with
no rotation. Each new line advances its four phases by 0.0035–0.0075 rad, so a
string sweeps a slow fan rather than jittering.

## Shared helpers

Clamp in every scene. Smoothstep: HalftoneTide inlines h²(3 − 2h), IsoDrift
uses a configurable edge pair, SpectrumCascade has none. Area-derived lengths:
√(WH) for halftone's wave count, √(WH/(0.8660254·tiles)) for iso edge,
√(WH/2400) for dot spacing. Color is display sRGB everywhere: HSL strings for
halftone ink and iso faces, per-channel hex lerp for spectrum's three-stop
stripe gradients. HalftoneTide trades one fill per bucket for 2,772 arc
appends.

## Conventions

Origin top-left, y down, angles in radians from +x. AuroraWaves, HalftoneTide
and IsoDrift advance a frame counter, so their rates are per frame at
60 fps; SpectrumCascade derives elapsed seconds from performance.now. Space is
CSS pixels except AuroraWaves, which is device pixels throughout. Color is
8-bit display sRGB, no tone mapping, and every gradient interpolates in sRGB.
Motion is open-ended in all four.

## Variation map

| if you want | change |
| --- | --- |
| a denser halftone | raise cells toward 3200 and keep maxRadiusFactor at 0.56 |
| a bigger iso tile | lower tiles toward 300 until edge hits its 58 px cap |
| longer aurora trails | raise width toward 240; each line costs one cubic |
| a calmer spectrum | lower floatStrength and baseSpeed, not stripeCount |
| more amber crests | lower accentFrom toward 0.5 on IsoDrift |

## Porting

Canvas 2D blend modes are load-bearing: lighter, soft-light, screen, multiply
and overlay must all exist. Path2D is required by HalftoneTide and ctx.filter
by SpectrumCascade; a host without filter support must pre-blur into an
offscreen canvas. Recompute spacing, edge and radius after every resize — none
survive a size change. AuroraWaves must not add a DPR transform without
dividing its stroke width by the same factor. Transparent-canvas ports need the
original host gradient behind them or the frame bottom goes black.

## Failure modes

- **Uniform mid-grey field →** weights do not sum to 1, or h is not centred on
  0.5, so the crest never forms.
- **Visible tile grid on a large viewport →** spacing clamped to maxSpacing
  without letting the dot count fall; accept larger dots.
- **Stair-stepped wavefronts →** h quantized before radius, not only for the
  bucket.
- **Hard-edged spectrum stripes →** filter unsupported or blur below 8 px.
- **Depth inversion in iso →** rows drawn near to far.
- **Green fringe on iso crests →** the warm hue ramp shortened to 243→32
  instead of 243→392.
- **Half-size pattern on retina →** DPR applied to both the backing store and
  the transform or geometry.

## Verification heuristics

- Nominal dot count equals WH/(s²·0.8660254); no radius exceeds 0.56·s.
- Mean field value sits near 0.5, with crests reaching both ends of 0..1.
- Blend stack is ordered: additive light first, tint and vignette last.
- No frame shows residue of the previous one; a still of t = 3 s is identical
  to a re-render at t = 3 s.
- Measurable periods: halftone sweep 8.38 s, iso row wave 5.98 s, aurora hue
  round trip 43.33 s.
- Iso top faces tile without gaps and every body meets the ground plane.