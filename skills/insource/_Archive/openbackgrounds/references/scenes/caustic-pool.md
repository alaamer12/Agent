---
id: caustic-pool
name: Caustic Pool
family: webgl-f1
renderer: webgl1
poster: assets/posters/caustic-pool.jpg
complexity: M
source_lines: 263
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Caustic Pool

## 1. Identity

A cyan interference net of thin caustic lines and soft oval blooms drifts over a
near-black pool floor.

## 2. Perceived look

Smooth, high-contrast, full-bleed. A mesh of 1–4 px white-cyan lines with
20–40 px glows encloses cells 150–300 px across; dim teal ovals sit where the
ridge peaks. Every term is a smooth power of a sine, so there are no hard edges,
no grain, no focal point. At t = 3 s the net is fully formed, the brightest
crossing sits right of center, and corners are at 71 percent.

## 3. Frame anatomy

1. **Ground** — the shader's own deep navy, written by the same pass; alpha is 1
   everywhere, so the host gradient never shows.
2. **Caustic field** — one three-vertex oversized triangle, vertices (-1,-1),
   (3,-1), (-1,3), drawn with `TRIANGLES`. Blending is disabled (`ONE, ZERO`),
   depth test is off, culling is at default.

There is no clear call and no post pass. The context is `alpha: false,
antialias: false, depth: false, powerPreference: "high-performance"`; the missing
MSAA is why one-pixel net lines can shimmer at high DPR.

## 4. Motion law

Time is seconds since mount, scaled by speed 0.28 into t. The three plane waves
advance at 0.56, 0.476, and 0.308 rad/s — periods 11.22 s, 13.20 s, 20.40 s —
with crests travelling at 21.27, 19.39, 13.25 px/s at a 400 px short axis,
scaling with that axis. The net pulses at 0.42 rad/s, a 14.96 s cycle. A warp of
0.055 units (22 px) oscillates at **0.28 and 0.336 rad/s** — the shader
coefficients are 1.0 and 1.2, but they multiply the speed-scaled `t`, so the
wall-clock periods are 22.4 s and 18.7 s. The mesh therefore breathes slowly
while it slides. Motion is open-ended. The pointer shifts the sample by up to
0.06 units (24 px) with no smoothing.

## 5. Technique and math

The coordinate is p = (fragCoord − 0.5·resolution)/min(resolution.x,
resolution.y), so p spans ±0.8 by ±0.5 at 640x400 and one unit is 400 CSS px at
DPR 1. It is displaced first: p −= pointer·0.06, then p += 0.055·(sin(3·p.y + t),
cos(2.6·p.x − 1.2·t)). The pointer is in -1..1 with y down.

The scalar field is the mean of three plane waves:

- v = [sin((1.7·p.x + 1.1·p.y)·5.2 + 2t) + sin((1.1·p.x − 1.9·p.y)·5.2·0.86 −
  1.7t) + sin((2.6·p.x − 0.4·p.y)·5.2·0.68 + 1.1t)]/3.

Wave vectors are (8.84, 5.72), (4.9192, −8.4968), and (9.1936, −1.4144) rad per
p unit; wavelengths 0.596739, 0.639963, 0.675483 units, or 238.696, 255.985,
270.193 px at a 400 px short axis. The directions are 2.6 rad apart on average,
so v rarely reaches ±1 and the pattern never becomes stripes.

Two powers read that scalar. The ridge is `pow(max(0, 1 − |v|), 6)`, a soft band
on every zero crossing. The net is
`pow(max(0, 0.5 + 0.5·sin(6.2831·v + 1.5t)), 9)`, near zero except where the
argument nears π/2, giving thin rings offset from the ridge. The literal 6.2831,
not 2π, leaves a small phase error that is part of the look at high net powers.

Color is c = mix(deep, mid, 0.85·ridge) + hot·0.75·net + mid·0.22·ridge, then
multiplied by 1 − 0.6·smoothstep(0.55, 1.35, |p|). No tonemap; the sum can exceed
1 and is clamped by the 8-bit buffer.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| speed | 0.28 | 0.1–0.5 | time scale into the field | M |
| scale | 5.2 | 4–8 | wave number; cell size | H |
| ridgeSharpness | 6.0 | 3–10 | width of the soft zero-crossing band | M |
| netSharpness | 9.0 | 5–14 | thinness of the bright net | H |
| warpAmp | 0.055 | 0–0.1 | wobble amplitude | M |
| warpFreq | 3.0 / 2.6 | 1–5 | warp frequencies | L |
| warpRate | 1.0 / 1.2 | 0.2–2 | warp coefficients on scaled t; wall-clock 0.28 / 0.336 rad/s | L |
| netPhase | 1.5 | 0–3 | phase between net and ridge | M |
| netTau | 6.2831 | 6.28–6.29 | net period constant | H |
| deep | #020B14 | any dark | ground color | M |
| mid | #08476B | any teal | ridge fill | H |
| hot | #8CF2FF | any ice blue | net line color | H |
| vignette | 0.55–1.35 | 0.4–1.6 | corner falloff radii | M |
| maxDpr | 1.5 | 1–2 | DPR clamp | L |

## 7. Palette and color

Three stops: `#020B14` (0.008, 0.045, 0.078) deep, `#08476B` (0.03, 0.28, 0.42)
mid, `#8CF2FF` (0.55, 0.95, 1.0) hot. The ridge mix moves deep toward mid at
0.85, then a second term adds `0.22 · ridge` of mid, so a ridge at full strength
sums to 1.07 times mid and is clamped by the 8-bit buffer. The net adds
`0.75 · net · hot` on top of whatever ridge light is present, so crossings run
past 1.0 in all three channels and clamp to near-white cyan. Values are display
sRGB, no gamma, no tonemap. The vignette scales all three channels equally, so
hue is constant across the frame.

## 8. Composition and camera

Orthographic, centered, full-bleed. Because p is short-axis normalized, the net
keeps its 239–270 px wavelength on any window; 640x400 shows 2.7 wavelengths
across and 1920x1080 shows 7.2. Wide frames add cells horizontally, portrait
crops them. The vignette starts at 0.55 units (220 px radius at 640x400) and
reaches 0.6 strength at 1.35, so no cell is framed by the edge; the pattern runs
off in every direction with no safe margin.

## 9. Randomness and seeds

None. The frame is a closed-form function of position, time, and pointer; no
RNG, no seed, no warmup. Frame one equals a render at t = 0. The pointer starts at
(0, 0), so the field starts unshifted.

## 10. Performance budget

One draw call, three vertices, no textures, six sin/cos and two powers per pixel.
A 640x400 viewport at DPR 1.5 is 576,000 fragments; the poster itself is captured
at DPR 1 (256,000). 1080p is 2,073,600 fragments at DPR 1, or 4,665,600 at DPR
1.5. Fill-bound and cheap: the 9th power is the only expensive instruction. Holds
60 fps on an integrated GPU at poster size and at 1080p. Cut order: DPR, then
pointer warp, then netSharpness (which changes the look).

## 11. Host integration

Standard contract: mount into a positioned full-bleed holder, read
`offsetWidth/offsetHeight` floored times DPR with a window fallback, set the
viewport, listen to resize and pointermove passively. Pointer is window-
normalized, not container-normalized. The attribute location is fetched every
frame — harmless but unnecessary. Teardown removes listeners, deletes buffer and
program, and calls `WEBGL_lose_context`. No ResizeObserver.

## 12. Failure modes and tells

- **Round blobs instead of a net →** netSharpness below 5.
- **Oval cells stretched along one axis →** p divided by width, not the short axis.
- **Net disappears at 4K →** lines below one device pixel; lower scale.
- **Pattern slides with no breathing →** the warp term dropped.
- **Corners as bright as center →** vignette removed or inverted.
- **Blue-grey haze instead of black →** deep raised or net power lowered.

## 13. Tuning knobs

1. `scale` — denser net upward, larger cells downward (4.2–7).
2. `netSharpness` — raise for hairline caustics (7–12).
3. `speed` — faster drift (0.2–0.45).
4. `hot` — toward white for a hotter core.
5. `vignette` — outer 1.1 for darker corners.

## 14. Verification checklist

- Thin lines with soft halos, no hard aliasing at DPR 1.
- Wavelengths 239–270 px at a 400 px short axis.
- Dominant hue 190–200 degrees; no green or magenta.
- Corner brightness 0.71 at 640x400, 0.62 at 1920x1080.
- Net pulse 14.96 s; no flicker.
- Compare to `assets/posters/caustic-pool.jpg`: line-to-cell ratio and dim oval
  blooms inside the cells.

## 15. Porting notes

Keep the 6.2831 literal; 2π shifts the net by 0.0001 rad, invisible at 9th power
but enough to break a frame comparison. Keep short-axis normalization. If the
target lacks `pow`, clamp before the logarithm or a negative base is undefined.
No color-space conversion is applied.
