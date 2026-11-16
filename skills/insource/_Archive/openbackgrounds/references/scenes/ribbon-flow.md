---
id: ribbon-flow
name: Ribbon Flow
family: webgl-f4
renderer: webgl1
poster: assets/posters/ribbon-flow.jpg
complexity: L
source_lines: 362
dpr_max: 2
deps: []
poster_capture: 640x400
---

# Ribbon Flow — scene reference

## 1. Identity

A single soft-edged band of light — pale blue drifting into lilac — that rises and folds across a black field like a slow, silent aurora seen edge-on.

## 2. Perceived look

Almost nothing is lit: the field is black, and one horizontal ribbon of varying thickness crosses the frame, brightest where its surface tilts toward the viewer and invisible where it faces flat-on. That selectivity comes from shading by surface slope rather than by depth or texture, so the ribbon reads as a solid, glossy sheet seen in silhouette, with no internal lines. The colour is low-contrast and cool: lilac-pink on the left, steel blue toward the right, with a slight brightening along the fold. Edges are extremely soft — the alpha falls to zero over tens of pixels — so there is no line at the ribbon's boundary, only a gradient. A parameter-space vignette (strength 0.8) fades the band toward both its near and far depth edges: alpha is 0.60 of centre at an edge midpoint and 0.434 at a parameter corner. The whole field sits on the host's dark backdrop (the canvas is transparent). The 3.5 s poster shows one bright lilac band at about 37% of frame height with a fainter blue line just below it; everything else in the frame is the smooth black→`#1A0033` backdrop, not shader output.

## 3. Frame anatomy

Back to front:

1. **Backdrop** — the canvas is cleared to `(0, 0, 0, 0)` and composited over the host's background (in the source preview: a `from-black to-[#1A0033]` gradient). The poster's violet-black field is that backdrop, not the shader.
2. **Single sheet** — a 129×129 vertex grid whose model positions are `(u, v, 0)` with u, v ∈ [−1, 1]. The vertex shader reads the grid's y as **depth** (it maps to world z) and writes displaced height into world y; the model-view then scales x by aspect·1.55 and y by 0.75 and translates to z = −2. Drawn in one `drawElements` of 32,768 triangles.
3. **Alpha** — normal alpha blending `SRC_ALPHA, ONE_MINUS_SRC_ALPHA` (not additive), so the sheet darkens/tints rather than glows; where alpha is 0 the backdrop shows through untouched.

No depth test, no depth writes, no culling; the plane is single-sided but the shading does not depend on facing (the normal comes from derivatives and is dotted with `up`), so back-facing folds shade the same. Antialiasing on. Because the sheet recedes from z = −1 to z = −3, perspective makes its near edge about three times its far edge: the near edge is roughly twice the frame width and runs off both sides, the far edge covers only ~67% of the width, and the band occupies roughly 20–55% of frame height. It never reaches the top or bottom edge.

## 4. Motion law

- **Ripple.** `v.y = cos(4z)·cos(z + t/10 + x)/8` — a carrier at spatial frequency 4 in z modulated by a slow plane wave with period **62.8 s** travelling in x/z at about 0.1 rad/s of phase.
- **Fold drift.** `v.y −= cos(2x − t/2)/5` — a broad travelling fold along x whose crest moves with period **12.6 s** (0.5 rad/s); this is the visible "ribbon" motion.
- **Noise scroll.** The 3D value noise is sampled at `((x − t/5)/4, −t/100, z − t/10)·7`, so its pattern slides in x at 0.35 noise-units/s, in z at 0.7/s (after the ×7), and drifts very slowly in y. The result is a slow, non-repeating crinkle rather than a translating texture.
- **Baseline.** A constant `+0.3` lift sets the sheet's resting height.
- **Colour drift.** `themeColor(vUv.x + 0.05t)` — the blue→lilac ramp slides across the frame in 20 s per unit of UV, so the hue at a fixed pixel completes a cycle every 28.6 s.
- **Phase at t = 0.** All sines at their t = 0 values; the frame is a coherent, almost static sheet that begins folding immediately. Open-ended.

## 5. Technique and math

Single pass, single mesh, all displacement in the vertex shader; there is no texture and no per-frame CPU work beyond **two** matrix uniforms (`u_projection` and `u_modelView`) and the time uniform.

- **Mesh.** Grid of 129×129 vertices spanning u, v ∈ [−1, 1] (position z = 0), indexed with two triangles per cell into a `Uint16Array` (32,768 triangles; 16,641 vertices fit under the 65,536 limit).
- **Camera.** Hand-built perspective: `f = 1/tan(37.5°) ≈ 1.3033`; the projection is the standard GL matrix with diagonal `(f/aspect, f)`, `[10] = (far+near)/(near−far) ≈ −1.002`, `[11] = −1`, `[14] = 2·far·near/(near−far) ≈ −0.2` (near 0.1, far 100). Model-view is identity with `[14] = −2` (translate z −2), `[0] = aspect·1.55`, `[5] = 0.75`. The aspect cancels between the model x-scale and the projection's first entry, so the sheet's on-screen width is aspect-independent by construction.
- **Displacement.** The model position is `(u, v, 0)`; the shader swaps the grid axes into `(x, 0, z)` with `x = u` and `z = v`, so grid y is depth and world y is height. Then
  `v.y = cos(4z)·cos(z + t/10 + x)/8` (amplitude 0.125)
  `− valueNoise(((x − t/5)/4, −t/100, z − t/10)·7)/15`
  `− cos(2x − t/2)/5 + 0.3`;
  `v.z = z − valueNoise(same input)/15`.
  The noise is 3D value noise: floor/fract with smoothstep fade, hashed lattice via `fract(sin(n)·43758.5453)` with the integer triple `n = px + 57py + 113pz` and the standard 8-corner trilinear mix. It is **one octave** — no fbm.
- **Shading.** `vEC` is the displaced model position before the model-view, so `dFdx(vEC)` and `dFdy(vEC)` are its change per screen pixel along x and y. Their cross product, taken in that order, is the surface normal in model space: `normal = normalize(cross(dFdx(vEC), dFdy(vEC)))`. Then `c = 1 − dot(normal, up)` with `up = (0,0,1)`; then `c = (1 − cos(c²))/3` — a strong flattening that keeps most of the sheet near 0 and only steep slopes bright. If `OES_standard_derivatives` is unavailable, `c` falls back to a constant 0.35 (sheet becomes a flat translucent tint).
- **Alpha.** `clamp(c · (1 − length(uv − 0.5)·0.8) · 1.05, 0, 1)` — slope × a vignette in **grid parameter space** (uv.y is depth, not screen height). The vignette is symmetric in depth, so alpha falls toward both the near and far edges of the band: 0.60 of centre at an edge midpoint, 0.434 at a parameter corner. It is not a screen-space vignette; frame corners are unaffected.
- **Colour.** `accent = mix((0.38, 0.68, 1.0), (0.82, 0.45, 0.96), 0.5 + 0.5·sin((uv.x + 0.05t)·4.398))`; `colour = clamp(mix((0.05, 0.08, 0.16), accent, 0.86) + accent·c^1.25·0.36, 0, 1)`. The base only shows where `accent` is dark; the highlight term adds the sheen along steep folds.

## 6. Parameters

| name | value | range | effect | sensitivity |
|---|---|---|---|---|
| `maxDpr` | 2 | 1–2 | DPR cap; the mesh fills the frame so cost is fill-rate | M |
| `resolution` | 128 | 64–200 | grid subdivisions; 256 would overflow Uint16 indices | H |
| `fov` | 75 | 50–90 | vertical FOV; widens or flattens the sheet | M |
| `near` / `far` | 0.1 / 100 | fixed | clip range only | L |
| model Z | −2.0 | −1.5…−3 | camera distance; sheet scale and slope sensitivity | H |
| x-scale | `aspect·1.55` | coefficient 1.4–1.7 | horizontal coverage; 1.55 makes the mid-depth edge ~1% wider than the frame | M |
| y-scale | 0.75 | 0.4–1.2 | scales displacement and lift together; sets the band's vertical size and position, not full-frame coverage | H |
| noise scale | 7.0 | 3–12 | crinkle frequency | M |
| drift x / z / y | 1/5, 1/10, 1/100 | — | noise scroll speeds per axis | M |
| ripple amplitude | 1/8 | 0.05–0.25 | carrier wave height (`cos4z·cos(z+t/10+x)`) | H |
| fold amplitude | 1/5 | 0.1–0.4 | travelling fold depth (`cos(2x − t/2)`) | H |
| noise amplitude | 1/15 | 0.03–0.12 | per-vertex crinkle displacement | M |
| baseline lift | 0.3 | 0.15–0.45 | resting height of the band in frame; shifts the whole sheet | H |
| slope gain | `1.05` | 0.8–1.4 | alpha multiplier on slope term | M |
| vignette | 0.8 | 0.3–1.2 | radial darkening strength | M |
| accent mix | 0.86 | 0.6–0.95 | how far toward the hue ramp the base colour moves | M |
| highlight gain | 0.36 | 0.2–0.6 | sheen added on steep folds | M |
| hue drift | 0.05 | 0–0.12 | rate the blue/lilac ramp slides across the frame | L |

## 7. Palette and color

Sheet base `#0D1429` (0.05, 0.08, 0.16 — a deep navy). Hue ramp endpoints: blue `#61ADFF` (0.38, 0.68, 1.0) and lilac `#D173F5` (0.82, 0.45, 0.96); the ramp oscillates on `0.5 + 0.5·sin(4.398·(uv.x + 0.05t))`. Across uv.x 0→1 the phase spans 4.398 rad, which is **0.70 of a cycle**, not a full one. At the 3.5 s capture the phase at uv.x = 0 is 0.77 rad, so the left edge sits near the lilac end of the ramp and the right edge near the blue end. The delivered colour is 86% toward the ramp plus a `c^1.25·0.36` accent highlight, so bright folds move toward saturated blue-lilac while flat regions fall back to navy. Alpha is slope-driven, so **the backdrop dominates**: on the source preview the field is violet-black (`#1A0033` at the bottom-right of a black→violet gradient) and the ribbon appears as a lighter, hazier overlay of that. No tone map, no gamma handling (values written as-is, alpha-blended over an sRGB backdrop by the compositor).

## 8. Composition and camera

The sheet is edge-on, so its composition is set by the baseline lift (0.3) rather than by a horizon: the band crosses the frame between roughly 20% and 55% of its height, brightest around mid-depth. The mesh does not reach the top or bottom of the frame; it runs off the left and right edges only on its near side, while its far edge is inset to ~67% of the width. Raising the lift raises the whole sheet — displacement and lift are both scaled by 0.75 and then projected — so the band moves bodily, it is not just a crest that slides. Aspect changes only how much horizontal room the band has: its vertical position and thickness are aspect-independent, so a portrait frame keeps it horizontal and full-width. The parameter-space vignette fades both depth edges of the band (section 5); frame corners are unaffected. No safe margins are needed because the ribbon is not a discrete object.

## 9. Randomness and seeds

None. There is no RNG: the only noise is a deterministic hash-based 3D value noise (`fract(sin(n)·43758.5453)`), sampled from the vertex position and time. Every run on every machine produces the same frame at the same `t`, and the field is a pure function of `u_time`.

## 10. Performance budget

One draw call, 32,768 triangles, 16,641 vertices, no textures. With normal (non-additive) alpha blending each pixel is shaded once and then written; the mesh covers the whole frame, so GPU cost is approximately one full-screen pass with a 3D noise evaluation per vertex. 60 fps on integrated GPUs at DPR 2 on a 1920×1080 window is fine. Cut-first: `resolution` 128→96, then `maxDpr` 2→1.5, then `far` 100→50 (no visual change).

## 11. Host integration

Holder `absolute inset-0 pointer-events-none`; canvas `block w-full h-full` plus a scoped CSS rule setting width/height 100% and `pointer-events: none`. **The canvas is transparent** (`alpha: true`, clear to 0), so the host must supply a dark backdrop — the source gallery uses a black→`#1A0033` gradient, and against a white page the ribbon would read as a pale stain rather than a glow. Sizing uses holder offsets × `min(devicePixelRatio, 2)`; resize listeners are on `window`, and the aspect used for the projection reads the *canvas* pixel dimensions (so it is DPR-independent). Teardown deletes both buffers and the program, then calls `WEBGL_lose_context.loseContext()`. Requests `OES_standard_derivatives` (WebGL1); with WebGL2 the extension is core and `#extension` is unnecessary.

## 12. Failure modes and tells

- **Whole plane visible as a flat violet haze** — `OES_standard_derivatives` missing so `c = 0.35` everywhere. Confirm the extension; do not "fix" by raising alpha.
- **Ribbon invisible** — baseline lift or fov changed so the sheet's folds never tilt relative to `up = (0,0,1)`; keep lift 0.25–0.35 and y-scale 0.7–0.9.
- **Harsh band edges** — slope shading is very sensitive to mesh resolution; below 96 the crease becomes a visible polyline.
- **Moiré / shimmer under motion** — derivative-based normals on a coarse grid alias; raise resolution or damp the high-frequency ripple term.
- **Ribbon turns pink only** — hue drift term missing (`uv.x + 0.05t`); without it the ramp is fixed in space.
- **Canvas looks black** — an opaque clear or `alpha: false`; the backdrop is part of the composition.
- **Index overflow** — `resolution` above ~255 exceeds Uint16 element indices; keep ≤200.
- **Aspect-dependent stretch** — forgetting `[0] = aspect·1.55`; without it the sheet squashes on wide frames.

## 13. Tuning knobs

1. baseline lift — vertical placement and how much of the sheet's fold is lit; 0.25–0.35.
2. ripple amplitude — ribbon thickness/weight; 0.08–0.18.
3. noise scale — how fine the crinkle reads; 5–9.
4. accent mix and highlight gain — how saturated the folded light is; 0.8/0.36 is rested.
5. hue drift — how quickly blue gives way to lilac in one spot; 0.03–0.08.

## 14. Verification checklist

- Frame is dark overall: mean luma < 12/255 outside the ribbon band; the band sits between roughly 20% and 55% of frame height and is brightest near mid-depth.
- Dominant hue 205–290° (steel blue to lilac); no warm hues.
- Ribbon edges have no hard line — alpha falls over ≥20 px on a 1920-wide frame.
- Fold motion period ≈ 12.6 s; a fixed point on the crest should rise and fall visibly in 6 s.
- Alpha at a parameter edge midpoint ≈ 0.60 of centre and at a parameter corner ≈ 0.434, for the same surface slope (vignette 0.8); this is not a screen-corner test.
- No z-fighting or popping during motion; no shimmer bands at DPR 1.
- Transparent canvas: the page background must be visible where alpha = 0.

## 15. Porting notes

This is the one f4 scene that is a **shaded surface**, not lines: a Canvas 2D port needs per-quad gradients, not strokes, and will look appreciably flatter. In WebGL2, `dFdx` is core — drop the extension pragma but keep the slope math. If you move to three.js, `MeshBasicMaterial` cannot do this; use a `ShaderMaterial` with `derivatives: true` on WebGL1. The projection is a normal 75° camera at z −2, so unlike the other f4 scenes there is no inverse-square double divide to emulate.
