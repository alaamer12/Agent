---
id: moire-veil
name: Moire Veil
family: webgl-f1
renderer: webgl1
poster: assets/posters/moire-veil.jpg
complexity: M
source_lines: 323
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Moire Veil

## 1. Identity

Two concentric ring grids, the second detuned by up to 3.2%, orbit separate
centres over a near-black navy field, and a sparse lattice of pale cyan nodes
lights up only where both ring sets coincide.

## 2. Perceived look

Fine, crisp concentric rings at 8.6957 px pitch overlay a near-black navy
ground. Each grid is a 0.72 px hairline, so the frame reads as a dark veil, not
a lit mesh. Pale cyan nodes spark only where the two ring sets overlap.
Contrast is high locally and low globally, with no focal point beyond the two
orbit centres. Steel-blue tint builds toward the vignette-darkened corners. At
t = 3 s the pattern is full-bleed and reads almost static.

## 3. Frame anatomy

1. **Ground** — fragment-computed vertical mix from `#02040A` at the bottom to
   `#010206` at the top, every frame; opaque.
2. **Ring grid A** — gaussian hairlines centred on orbit centre c1, gain 0.085.
3. **Ring grid B** — the detuned copy on centre c2, same gain.
4. **Coincidence nodes** — the product of the two line fields, gain 1.5, plus a
   squared core at gain 0.16.
5. **Spoke grid** — 22 faint angular wedges at gain 0.04, 1.2x ring width.
6. **Tonemap and vignette** — exponential exposure, then radial darkening.

No blending, depth test, or cull: one fullscreen triangle in a context created
with alpha false, so the host gradient never shows.

## 4. Motion law

Centre c1 orbits at radius 0.14 with angular rates 0.075 rad/s on x and
0.09525 rad/s on y, giving 83.776 s and 65.973 s periods. Centre c2 orbits at
radius 0.17 at 0.06225 and 0.05325 rad/s, periods 100.931 s and 117.993 s. Peak
tangential speeds are 5.334 px/s (c1) and 4.233 px/s (c2) at 640x400. The detune factor
breathing at 0.12 rad/s beats the ring spacing every 52.360 s. Spokes rotate at
0.03 rad/s, one turn in 209.440 s. Pointer offset is added at 0.025 per unit,
at most 10 px. Nothing loops; motion runs open-ended.

## 5. Technique and math

Screen coordinate p is centred and divided by the short axis, so p spans -0.5 to
0.5 vertically. The line half-width is w = 0.72 / min(width, height) in the same
units, i.e. 0.72 backing pixels at any resolution. For a grid centred on c with
frequency f, s = |p - c| * f and the normalized distance to the nearest ring is
d = |fract(s) - 0.5| / f; the line field is exp(-(min(d / w, 5))^2). Grid A uses
f = 46 and c = c1; grid B uses f = 46 * (1 + 0.032 sin(0.12 t)) and c = c2, with
d divided by the same factor so the physical spacing stays symmetric.

Nodes are l1 * l2, a product rather than a mean: a node requires both grids to
pass through the same pixel, keeping the lattice sparse. The spoke field takes
ang = atan2(p.y, p.x) + 0.03 t, ss = ang * 22 / 2π, and ds = |fract(ss) - 0.5| *
(2π / 22) * r, the true arc distance at radius r; its field uses 1.2 w.

The envelope env = 1 - smoothstep(0.18, 0.95, r) fades all three fields before
the corners. Total emission is 1.5 * nodes * env + 0.085 * (l1 + l2) * env +
0.04 * l3 * env. Ground is mix(navyLow, navyHigh, up^2) with up =
clamp(0.7 * p.y + 0.5). Line tint is mix(steel, pale, clamp(2 r, 0, 1)); that
tint times emission is added, plus 0.16 * pale * nodes^2 * env. Tonemap is
1 - exp(-1.15 * col), then 1 - 0.5 * smoothstep(0.55, 1.2, r), all in mediump.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | device-pixel clamp | L |
| ringFreq | 46.0 | 30.0–70.0 | rings per short axis; 8.6957 px pitch at 640x400 | H |
| spokes | 22.0 | 12.0–40.0 | wedge count | L |
| thickPx | 0.72 | 0.45–1.10 | gaussian half-width, backing pixels | H |
| detune | 0.032 | 0.010–0.080 | ring-spacing beat depth | H |
| speed | 0.075 | 0.020–0.150 | orbit angular rate | M |
| nodeGain | 1.5 | 0.7–2.2 | node brightness | H |
| ringGain | 0.085 | 0.030–0.160 | single-grid filament | M |
| spokeGain | 0.040 | 0.000–0.090 | angular grid brightness | L |
| coreGain | 0.16 | 0.05–0.30 | squared-node glow | M |
| exposure | 1.15 | 0.80–1.80 | tonemap gain | H |
| pale | rgb(0.62, 0.93, 1.0) | hue 180–200 | node and edge tint | H |
| navyLow | rgb(0.006, 0.014, 0.04) | any near-black | bottom ground | M |
| navyHigh | rgb(0.0025, 0.007, 0.022) | any near-black | top ground | M |
| env | 0.18 / 0.95 | 0.1–1.1 | radial field fade | M |
| pointerGain | 0.025 | 0–0.05 | pointer shift, short-axis units | L |

## 7. Palette and color

Pale is `#9EEDFF` (hsl 191, 100%, 81%), the steel end of the line ramp is
`#C7E6FF` (hsl 207, 100%, 89%), navy low is `#02040A` (hsl 226, 74%, 2%) and
navy high `#010206` (hsl 226, 80%, 1%). Emission is added linearly before the
1 - exp(-1.15 x) tonemap, so nodes compress to pale cyan rather than clipping to
white; the corners never exceed 0.5 after the vignette. All values are authored
in display sRGB and written without gamma conversion.

## 8. Composition and camera

Pure screen space, no camera. Both orbit centres sit within 0.17 of the middle,
so the two ring systems dominate the centre and the envelope empties the
corners. The short axis is the unit, so rings stay circular at any aspect; wide
frames crop the outer rings horizontally and tall frames show the whole
envelope with empty top and bottom. No safe margins; the vignette is the only
framing device.

## 9. Randomness and seeds

None. Every value is analytic in p and t: no RNG, no hash, no seed, no warmup.
Any launch time produces the same pattern at a different phase, because the two
orbit centres are pure sinusoids and the detune is a third.

## 10. Performance budget

One oversized triangle, one draw call, no textures. Per pixel: two radii, one
atan2, three gaussians and one tonemap. It is fill-bound, so cost scales with
DPR squared. 60 fps expected on an integrated GPU at 640x400 and at 1080p with
DPR 1.5. Cut order: DPR to 1.25, then the spoke term, then ringFreq.

## 11. Host integration

Standard contract. Context is WebGL1 with alpha false, antialias false, depth
false and high-performance power preference. Size from the holder's
offsetWidth/offsetHeight with a window fallback, clamp DPR at 1.5, viewport the
backing store. Resize and pointermove listeners are passive; pointer is
normalized by the window, not the container, while the holder is
pointer-events-none. Time is performance.now() minus a stamp set just before the
first RAF. Teardown deletes the program and buffer and calls WEBGL_lose_context.
No external assets.

## 12. Failure modes and tells

- **Pale milky field instead of hairlines →** w is not divided by the short axis
  → divide 0.72 by min resolution.
- **Regular grid of dots, no fringes →** both grids share a centre or detune is
  zero → offset the centres.
- **Bright mesh everywhere →** nodes averaged instead of multiplied → use the
  product l1 * l2.
- **Rings vanish at DPR 1.5 →** width authored in CSS pixels → keep it in
  backing pixels.
- **Pattern slides far too much with the mouse →** pointer gain above 0.05.
- **Poster brighter than your render →** the poster predates the hairline
  tuning, with line width an order of magnitude larger; do not tune to it.

## 13. Tuning knobs

1. thickPx — 1.0 for a more visible veil, 0.5 for pointillist nodes.
2. ringFreq — 32–60 changes the ring scale without touching brightness.
3. detune — 0.020–0.050 sets the beating-band width.
4. nodeGain — 1.0–2.0 for node prominence before saturation.
5. speed — 0.04–0.10 for a slower or livelier orbit.

## 14. Verification checklist

- Mean frame luminance below 0.12; the brightest pixels are isolated nodes.
- Rings number 46 across the short axis and stay circular at 21:9.
- Dominant hue between 191 and 226 degrees; no green or magenta cast.
- Rings breathe with a 52.360 s beat; no flicker.
- No clipping to pure white and no banding in the navy ground.
- Compare to a fresh 640x400 capture at 3.5 s, not the archived poster.

## 15. Porting notes

Any GLSL ES 1.00 fragment pipeline will do. Keep the short-axis normalization
and the backing-pixel width; a framework that renders at CSS resolution shows
thicker rings. If the target color-manages to linear, skip that conversion here:
every constant is display-referred.
