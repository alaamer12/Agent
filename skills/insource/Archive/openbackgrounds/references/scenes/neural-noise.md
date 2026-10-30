---
id: neural-noise
name: Neural Noise
family: webgl-f1
renderer: webgl1
poster: assets/posters/neural-noise.jpg
complexity: M
source_lines: 282
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Neural Noise

## 1. Identity

Fourteen rotated sine octaves form cyan lobes and navy basins on a transparent
ground, bulging away from the pointer.

## 2. Perceived look

Smooth and full-bleed, no grain. Contrast is high because the field is
thresholded: cyan interiors, near-black voids, 40–120 px transitions. There is
no focal point: a bright region left-of-center, a dark basin above it. At
t = 3 s, 94.5 percent of pixels clear intensity 0.1, the median is 0.639, the
upper quartile clips at 1.0, and alpha peaks at 0.6.

## 3. Frame anatomy

1. **Host backdrop** — no ground is drawn. The canvas has `alpha: true` and the
   shader alpha tops out at 0.6, so the host's `#000000`–`#1A0033` vertical
   gradient shows through every pixel.
2. **Field pass** — one four-vertex `TRIANGLE_STRIP` over the viewport, blending
   `SRC_ALPHA, ONE_MINUS_SRC_ALPHA`, depth test disabled, culling at default.
   It writes straight-alpha color and alpha 0–0.6.

No clear color is set, so the default (0, 0, 0, 0) clear applies.

## 4. Motion law

Elapsed milliseconds become t = 0.00007·ms, or 0.07 per second. All fourteen
layers subtract the same t, so layer j drifts at 0.07/s in its own uv units:
14.36 px/s for the first octave at a 400 px height, 1.67 px/s for the last.
Each layer rotates by 1 rad first, so the drifts point in fourteen directions and
the motion is a slow deformation. It never loops.

The pointer target is smoothed by 0.05 per frame — a 20-frame, 0.333 s constant
at 60 fps — and shifts every layer's phase, so the field swells near the cursor.
Scroll progress only moves the palette.

## 5. Technique and math

Let vUv be the quad's 0..1 coordinates and R = drawingBufferWidth /
drawingBufferHeight. The sample point is uv = (0.3·vUv.x·R, 0.3·vUv.y). For
j = 0…13, with s_0 = 6.5 and s_{j+1} = 1.18·s_j:

- rotate uv and acc by 1 rad;
- layer = uv·s_j + j + acc − t;
- acc += sin(layer) + 2.1·p;
- res += (0.5 + 0.5·cos(layer))/s_j.

Here p = 0.18·(1 − d)^2.4 is the pointer bulge, d = |vUv − pointer| with x
scaled by R and clamped to 0..1. The field n = res.x + res.y lies in
0..1.818312 with mean 0.909156. The tone curve is n′ = 0.95·n³ + 0.45·n⁵ − 0.35,
clamped at 0; it crosses zero at n = 0.672023, which cuts the smooth mean field
into basins and lobes. Intensity is i = clamp(n′·smoothstep(1.08, 0.28,
|vUv − 0.5|)).

Octave wavelengths are 3.222·H/1.18^j px for canvas height H: 1288.86 px down
to 149.88 px at H = 400. The rotation and accumulated acc bend each octave
around the previous one, producing the scalloped folds. R on x only keeps the
field isotropic in pixels.

Color: base b = (0.04, 0.07, 0.18); accent a = mix((0.45, 0.35, 0.95),
(0.2, 0.85, 1.0), 0.5 + 0.5·cos(scroll)) — the argument is radians, not
`scroll·2π` — c = mix(b, mix(b, a, i^0.85), 0.75)
+ a·0.25·i, clamped. Alpha is smoothstep(0, 0.85, i)·0.6. No tonemap.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| iterations | 14 | 8–18 | cascade depth | H |
| baseScale | 6.5 | 3–10 | largest lobe size | H |
| scaleGrowth | 1.18 | 1.1–1.3 | octave frequency ratio | H |
| uvScale | 0.3 | 0.15–0.5 | sampling window | H |
| timeScale | 0.00007 /ms | 0.00002–0.0002 | phase drift | M |
| cubicGain | 0.95 | 0.5–1.2 | midtone contrast | M |
| quinticGain | 0.45 | 0–0.8 | core saturation | M |
| threshold | 0.35 | 0.2–0.5 | black cut | H |
| pointerGain | 0.18 | 0–0.4 | bulge amplitude | M |
| pointerFalloff | 2.4 | 1–4 | bulge radius | M |
| pointerLerp | 0.05 | 0.01–0.2 | follow speed | L |
| vignetteOuter | 1.08 | 0.8–1.4 | field cutoff radius | M |
| vignetteInner | 0.28 | 0.1–0.5 | full-bright radius | M |
| alphaMax | 0.6 | 0.3–1 | peak canvas alpha | H |
| maxDpr | 1.5 | 1–2 | DPR clamp | L |

## 7. Palette and color

Base `#0A122E` (0.04, 0.07, 0.18). Accent is
`mix(#7359F2, #33D9FF, 0.5 + 0.5·cos(scroll))` with `scroll ∈ [0, 1]`; at rest it
is exactly `#33D9FF`, and at scroll 1 the factor is 0.770, giving
≈(0.257, 0.735, 0.989) or `#429BFD` — the warm `#7359F2` end is unreachable
because `cos(1 rad) > −1`. Intensity mixes base toward accent at i^0.85, then
pulls the result 75 percent back to base and adds 0.25·i of raw accent, keeping
highlights off white. Alpha is smoothstep(0, 0.85, i)·0.6. Display sRGB, no
gamma, no tonemap; the host gradient supplies the dark end.

## 8. Composition and camera

Orthographic full-bleed, no camera. The field is isotropic in pixels: a wider
window reveals more lobes at the same size. At 640x400 the sampled window is
0.48 wide by 0.3 tall in vUv. At 21:9 the extra width adds about 40 percent more
field; portrait shows fewer lobes across as the vignette closes in. No safe
margins.

## 9. Randomness and seeds

None. The image is a deterministic function of position, time, pointer, and
scroll; no RNG, no seed, no warmup, so frame one equals t = 0. The pointer starts
at (0.5, 0.5), which puts p at its maximum 0.18 until the first pointer event.

## 10. Performance budget

One draw call, four vertices, no textures. Each pixel runs 14 iterations with
two sin and two cos each — about 56 trig calls — plus a length and two
smoothsteps. At DPR 1.5 the poster is 960x600 = 576,000 fragments; 1080p is
4,665,600. The pass is fill-bound and holds 60 fps on a laptop iGPU at poster
size. Cut DPR to 1.25 first, then iterations.

## 11. Host integration

Standard mount into a positioned full-bleed holder, sized from `offsetWidth` and
`offsetHeight` with a window fallback, backing store at CSS size times 1.5, one
4-vertex buffer. Listens to resize, pointermove, and touchmove; pointer
coordinates are window-relative, so an inset hero must remap them. The scroll
uniform reads `document.body.scrollHeight`; pin it to 0 inside a scrolled panel.
Teardown deletes the program and calls `WEBGL_lose_context`. No ResizeObserver.

## 12. Failure modes and tells

- **Flat blue rectangle, no lobes →** time fed in seconds; t is 1000x too slow.
- **Hard two-tone posterization →** threshold above 0.4; drop toward 0.3.
- **Even cyan wash, no basins →** threshold applied before the tone curve.
- **Cursor bulge missing →** p used only in color; it belongs in acc.
- **Bulge snaps to the cursor →** pointerLerp changed from 0.05.
- **Hue drifts violet while scrolling →** scroll wired to the page.
- **Opaque navy rectangle in a port →** canvas created without alpha.
- **Stair-step bands on mobile →** mediump cascade; promote to highp.

## 13. Tuning knobs

1. `threshold` — lower for more cyan, higher for void (0.25–0.45).
2. `uvScale` — raise for smaller, busier lobes (0.2–0.45).
3. `pointerGain` — raise for a stronger bulge (0.1–0.3).
4. `alphaMax` — lower for a subtler overlay (0.4–0.6).

## 14. Verification checklist

- Median intensity 0.639, top quartile clipped at 1.0.
- Alpha never above 0.6; host gradient visible in the dark basin.
- Dominant hue 185–200 degrees at rest; no red or green.
- Feature sizes 150–1290 px at a 400 px height; no visible axis alignment.
- No flicker and no loop point.
- Compare to `assets/posters/neural-noise.jpg`: same cyan-navy split and fold
  scale, dark basin above center.

## 15. Porting notes

Any GL port works. If the host renders in linear light, convert the constants or
the cyan shifts. Use highp where the 14-octave accumulator bands. Keep the quad's
vUv orientation and the pointer y-flip together, or the bulge mirrors.
