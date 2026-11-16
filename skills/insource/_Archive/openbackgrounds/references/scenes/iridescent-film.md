---
id: iridescent-film
name: Iridescent Film
family: webgl-f1
renderer: webgl1
poster: assets/posters/iridescent-film.jpg
complexity: M
source_lines: 410
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Iridescent Film

## 1. Identity

A soap film seen close up: saturated interference bands in magenta, orange,
green and teal, cut by crisp black contour lines and drained black patches. It
reads as a lit surface, not a wash.

## 2. Perceived look

Bands are 20–60 px wide at poster size and follow warped, lens-like contours
stretching toward the edges; a 3–8 px dark line sits between any two bands.
The poster runs magenta/orange upper-left, green center, teal lower-right, with a
large black drained patch at lower left. Highlights are sparse and warm-white on
the steepest folds; there is no grain.

## 3. Frame anatomy

1. **Film surface** — one oversized `TRIANGLES` draw with vertices (−1, −1),
   (3, −1), (−1, 3); no depth buffer, no index buffer.
2. **No compositing** — the shader always writes alpha 1.0. Context: `alpha:
   false, antialias: false, depth: false`, blending default off, no clear color.
   Every pixel is covered.

## 4. Motion law

Time is seconds. The field rotates about the center at 0.035
rad/s (period 179.52 s) and translates (0.04, −0.028) units/s; because that is
added to the sampling coordinate, the visible pattern slides 16 px/s left and
11.2 px/s up at a 400 px short axis. The thickness phases advance at
0.31, 0.23, 0.17 and 0.42 rad/s (periods 20.27, 27.32, 36.96 and 14.96 s).
Drainage breathes at 0.09, 0.07 and 0.05 rad/s (69.81–125.66 s), so dry patches
open and close slowly. Pointer offsets the sample by (0.08, 0.06) units, at most
32x24 px, unsmoothed and unclamped. Motion is open-ended.

## 5. Technique and math

Let p = (fragCoord − 0.5·resolution)/min(width, height); rl = |p|. Build q by
rotating p through 0.035t, adding (0.04t, −0.028t), adding pointer·(0.08, 0.06),
then shearing q += p·rl·0.18, bending bands around the center.

Thickness is film(q, t) = 0.5 + 0.5·v/4.75, where v sums four sines:

- sin(q.x·66 + sin(q.y·12 + 0.31t)·2.2)
- sin(q.y·80 + sin(q.x·10 − 0.23t)·2.0)
- sin((q.x + q.y)·50 + 0.17t)
- 0.75·sin(|q|·110 − 0.42t).

Carrier periods are 38.08, 31.42, 50.27 (35.54 along the diagonal) and 22.85 px
at a 400 px short axis. The result already lies in 0.105–0.895, so the clamp to
0–1 is inert. A drainage field, plate = 0.5 + 0.5·w/2.8, sums
sin(q.x·16 + 1.4·sin(q.y·13 − 0.09t)), sin(q.y·19 + 0.07t) and
0.8·sin((0.8q.x + 1.2q.y)·12 + 0.05t). Dryness is dry = smoothstep(0.25, 0.62,
plate); th = ripple·(0.06 + 0.94·dry); absolute thickness um = 2.9·th^3.2. Below
about 0.55 µm the film is black.

Normals come from a central difference of film with eps 0.006 (2.4 px at 400):
gx, gy, then n = normalize(−0.018·gx, −0.018·gy, 1). L is normalize(0.35, 0.55,
0.75), H is normalize(L + (0, 0, 1)), diff = 0.4 + 0.7·max(0, n·L), spec =
max(0, n·H)^44, fres = (1 − n.z)^2.2. Flat patch: diff 0.928, spec 0.056, fres 0 (inert).

Color is physical in intent: interfere(um) = 0.5 + 0.5·cos(2π·(um/λ + offset))
for λ = 0.65, 0.546, 0.454 µm and offsets 0, 0.12, 0.24; irid = interfere².
black = smoothstep(0, 0.55, um). fence = smoothstep(0, 0.24, |fract(um/1.1) −
0.5|·2), so contours fall at um = 0.55, 1.65, 2.75 µm. lit = black·(0.05 +
0.95·fence). The color is deep + irid·diff·lit·1.45 + tint·fres·0.35·(0.25 +
black) + light·spec·(0.35 + 0.85·black), then 1 − exp(−1.05·col) and a vignette
1 − 0.55·smoothstep(0.42, 1.15, rl).

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | device pixel ratio clamp | L |
| thicknessUm | 2.9 | 1.5–4 | peak film thickness | H |
| bias | 3.2 | 2–5 | area pushed toward thin film | H |
| thinUm | 0.55 | 0.3–0.8 | black threshold | H |
| orderUm | 1.1 | 0.6–1.6 | black contour spacing | H |
| bandPow / bandGain | 2.0 / 1.45 | 1–3 / 1–2 | band saturation and strength | M |
| lineSharpness | 0.24 | 0.1–0.4 | contour half-width | M |
| dryLo / dryHi | 0.25 / 0.62 | 0.1–0.8 | drained-patch threshold | H |
| dryFloor | 0.06 | 0–0.2 | ripple left in dry patches | M |
| lineFloor | 0.05 | 0–0.15 | reflectance left inside a black contour | M |
| bump | 0.018 | 0.005–0.04 | normal tilt | M |
| rot / flow / shear | 0.035 / 0.04 / 0.18 | 0–0.08 / 0–0.1 / 0–0.4 | motion and edge stretch | M |
| sampleEps | 0.006 | 0.002–0.012 | normal sample offset | H |
| specPower / exposure | 44 / 1.05 | 10–80 / 0.7–1.5 | highlight and tonemap | M |
| fresnelGain / specGain | 0.35 / 1.0 | 0–0.8 / 0.5–2 | fresnel weight and highlight strength | M |

## 7. Palette and color

Deep is `#030205`, tint `#809EE6`, light `#FFF7E6`. Band colors are generated,
not stored: the interference vector is (0.615, 0.72, 0.001) at um = 0.55, green
at 1.0, (0, 0.662, 0.726) cyan at 1.65, (0.889, 0.364, 0.038) orange at 2.0, and
(0.314, 0.603, 0.125) at 2.75. Squaring removes the cosine's 50% grey floor, so
bands keep near-zero channels. Tonemap compresses the top end; no sRGB conversion.

## 8. Composition and camera

Orthographic, full-bleed, no horizon. The field is isotropic, so the eye reads
the largest dry patch and tightest band cluster. At 4:3 the shear pushes bands
outward; at 16:9 extra width reveals more pattern unstretched. The vignette
starts at rl = 0.42, so corners are 45% darker while the center stays bright.

## 9. Randomness and seeds

None. Everything derives from position, time and pointer; no RNG, no warmup. The
first frame at t = 0 is the full pattern; a nonzero clock offset only shifts band
positions.

## 10. Performance budget

Six field evaluations per fragment (film once, four for the central difference,
drainage once), each with nested modulator sines: about 34 sine calls in total.
At DPR 1.5 the poster backs 960x600 = 576,000 fragments; 1080p is 2880x1620 =
4,665,600. Fill-bound and arithmetic-heavy; mediump suffices because phases stay
small per fragment.

## 11. Host integration

The holder is sized by `offsetWidth`/`offsetHeight` times DPR, clamped at 1.5;
the backing store is reassigned on resize. `pointermove` is bound to the
window and normalized by window size, not canvas size, so a small canvas in a
large window sees smaller pointer offsets. Only `resize` is observed;
container-only resizes are missed. Teardown cancels the frame, removes both
listeners, deletes buffer and program, and calls `WEBGL_lose_context`.

## 12. Failure modes and tells

- **Smooth rainbow sweep →** carrier frequencies dropped; bands must be 20–60 px.
- **Milky pastel bands →** bandPow left at 1.0; squaring is what saturates.
- **No black contour lines →** fence omitted, or orderUm far above 1.1.
- **No dry patches →** drainage step replaced by a taper, or dryLo/dryHi outside
  0.25–0.62.
- **Glossy plastic →** bump past 0.04; normal tilt overpowers the bands.
- **Wrong highlights →** H built from an unnormalized L.

## 13. Tuning knobs

1. `thicknessUm` — lower to thin the film and widen magenta/green zones (2.2).
2. `orderUm` — lower for denser contour lines (0.8).
3. `dryHi` — raise for larger dry patches (0.72).
4. `rot` — raise for a livelier sheet (0.06), or zero it for a static poster.

## 14. Verification checklist

- Bands 20–60 px wide at 640x400, with 3–8 px black lines between them.
- At least one large near-black drained patch is visible.
- Highlights are sparse, warm-white and aligned with band edges.
- Magenta, orange, green and teal appear at once; no grey wash.
- `assets/posters/iridescent-film.jpg`: same band scale, same black lacquer lines.

## 15. Porting notes

Keep the carriers in the ratio 66 : 80 : 50 : 110; that is what makes the pattern
read at thumbnail size. The normal is a finite difference despite the source
comment calling it analytic; true derivatives change the highlight speckle and are
not equivalent. The fence needs the half-order offset, |fract(um/1.1) − 0.5|·2, or
black lines land on band centers. Rebuild H from the normalized L.
