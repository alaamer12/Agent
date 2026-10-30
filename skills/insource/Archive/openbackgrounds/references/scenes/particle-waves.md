---
id: particle-waves
name: Particle Waves
family: webgl-f3
renderer: webgl1
poster: assets/posters/particle-waves.jpg
complexity: L
source_lines: 583
dpr_max: 1.75
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Particle Waves

## 1. Identity

A rectangular grid of glowing points becomes a rolling ocean as two perpendicular
sine waves lift and drop its vertices, seen in perspective from above the surface.

## 2. Perceived look

A sparse point-mesh landscape. The dots are round with hot white centers and soft
cyan-to-violet halos, arranged on a regular rectangular lattice that is obvious
in the foreground and compresses toward the horizon. Two wave trains cross at
right angles, producing a regular lattice of peaks and saddles rather than organic
terrain. Near rows are large and bright; far rows shrink to the 4 px clamp. The
frame is dense in the lower two-thirds and empty in the top third. Negative space
is the host gradient, black at the top fading to deep purple.

## 3. Frame anatomy

One draw call of `POINTS`; positions and colors live in static buffers built on
mount and rebuilt on resize.

1. **Background** — not drawn. The canvas is transparent
   (`alpha: true`, `premultipliedAlpha: false`) and cleared to `(0, 0, 0, 0)`, so
   the host's `#000000 → #1A0033` vertical gradient shows through.
2. **Point grid** — one dot per lattice vertex, additive blending
   (`SRC_ALPHA, ONE`), depth test off, point sprite sizes 4–120 px.
3. **No post** — no vignette, no fog, no tone map.

Because the canvas is transparent and the blend is additive, overlapping halos
accumulate toward white; the purple in the background comes entirely from the
page, never from the shader.

## 4. Motion law

Two traveling waves at 3 spatial cycles across each axis:
`y += 22 [cos(6π x/W + 0.6 t) + sin(6π z/D + 0.45 t)]`. The X train moves at
0.6 rad/s (10.472 s per cycle), the Z train at 0.45 rad/s (13.963 s). At t = 0 the
field is a fixed phase — a crest at the center line. The surface is not simulated:
every frame is a closed-form function of time. The trains are in a 4:3 ratio, so
the combined pattern repeats exactly every 41.888 s (X completes 4 cycles, Z 3),
not every 20.94 s — at half that time the Z train is phase-inverted. The
camera adds parallax: pointer x moves the eye ±32 units and the target ±20,
pointer y moves the eye 24 units down and 60 units closer; both are smoothed at
0.08 per frame, so the response lags about 12 frames.

## 5. Technique and math

**Grid.** `fieldBase = 420`; width is `420 · max(1, aspect)` and depth is 420.
With `step = 6`, x and z segments are `max(24, round(size/6))`, so at 640x400 the
grid is 113 × 71 = 8023 points and at 1920x1080 it is 125 × 71 = 8875. Points
are laid out row-major in X, then Z, centered on the origin at `y = −42`.

**Displacement.** In the vertex shader, using the actual grid extents:
`y = −42 + 22·(cos(6π·x/W + 0.6t) + sin(6π·z/D + 0.45t))`. The 6π means three
full cycles across each axis regardless of size — the wavelength scales with the
grid, so the wave count is constant at every aspect ratio. Summing perpendicular
trains gives the characteristic egg-carton pattern; a single train would read as
corrugation.

**Camera.** Standard look-at: eye
`(32 px, 82 − 24 py, 320 − 60 py)`, target `(20 px, −42, 0)`, up +Y, 52° vertical
FOV, near 0.1, far 1000. The eye sits 124 units above the mean surface (82 − (−42);
the surface swings ±44) and 320 units back from the center, so the near edge of
the grid is about 166 units away and the far edge about 544 (110 and 530
horizontally).

**Point size.** `size = 28 · min(devicePixelRatio, 1.75)`, then
`clamp(size / max(clip.w, 0.25), 4, 120)`. The 4 px floor is what keeps far rows
visible as a texture instead of disappearing.

**Color.** Computed per grid index on the CPU and stored per vertex. With
`t = xi/(nx−1)` and `d = zi/(nz−1)`:
`wave = sin(1.5π (t + 0.65 d))`, `mixRatio = clamp(0.25 + 0.55 t + 0.2 wave)`,
`fade = 0.55 + 0.35 (1 − d)`. RGB is `lerp(start, end, mixRatio) · fade` with
start `(0.14, 0.72, 1.0)` and end `(1.0, 0.32, 0.95)`, plus small sinusoidal
modulations on G and B; alpha is `0.9 + 0.1 (1 − d)`.

**Fragment.** `uv = 2·pointCoord − 1`, discard beyond unit disc,
`falloff = (1 − |uv|²)^2.3`, `color = rgb · (1 + 3.2 falloff)`, alpha =
`falloff · a`. The 3.2 gain pushes the center of every dot past white in the
additive buffer; the halo stays cyan or magenta-tinted.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| fieldBase | 420 | 300–600 | world size of the grid | H |
| step | 6 | 4–10 | lattice spacing; sets point count | H |
| amplitude | 22 | 8–40 | wave height | H |
| baseHeight | −42 | −80–0 | mean surface height relative to target | M |
| basePointSize | 28 | 14–40 | dot size at unit depth | H |
| speed | 0.6 | 0.2–1.2 | X-train speed (Z is 0.75 ×) | M |
| fov | 52° | 35–70 | perspective strength | H |
| cameraHeight | 82 | 40–160 | above the surface | H |
| cameraDistance | 320 | 200–500 | distance from the grid center | H |
| maxDpr | 1.75 | 1–2 | resolution clamp | L |
| glow | 3.2 | 1.5–6 | core over-brightening | H |
| wave cycles | 3 | 1–6 | crests across the frame | H |
| palette start | (0.14, 0.72, 1.0) | — | near-left cyan | H |
| palette end | (1.0, 0.32, 0.95) | — | far-right magenta | H |
| pointer x gain | 32 / 20 | 0–60 | eye and target lateral shift | L |
| pointer y gain | 24 / 60 | 0–60 | eye height and distance shift | L |
| pointer lerp | 0.08 | 0.03–0.2 | follow speed | L |

## 7. Palette and color

Start `#24B8FF` cyan, end `#FF52F2` magenta, mixed by index with a sinusoidal
bias and darkened by up to 45% toward the far edge. In practice the dots read
white with colored halos because `1 + 3.2 falloff` saturates the core. The
background is not authored: `#000000` at the top to `#1A0033` at the bottom,
from the preview host. Alpha per point is 0.9–1.0 and is multiplied by the
falloff, so a dot's edges are nearly transparent and additive stacking is gentle.
No gamma handling; values go straight into the 8-bit buffer.

## 8. Composition and camera

The grid fills the lower two-thirds; the horizon is the far grid edge, not a
drawn line, and it sits around 28% from the top at the default camera. The
camera looks slightly down at the surface, so wave crests occlude the rows
behind only through size and brightness, not depth. Wide aspect widens the grid
(segments grow with aspect) so the wave count stays 3 on both axes; tall aspect
narrows it and the horizon rises. The top third is empty gradient — keep it.

## 9. Randomness and seeds

None. Positions are a regular lattice, colors are functions of index, and motion
is closed-form. The scene is identical at a given t on every run. No warmup; no
allocation per frame (buffers are rebuilt only on resize).

## 10. Performance budget

One draw call, about 8–9k point sprites with sizes up to 120 px near the camera —
this is fill-rate bound. At DPR 1.75 and an action-camera aspect the buffer is
large; 60 fps on desktop, 30–45 on integrated at high DPR. Cut order: maxDpr to
1.0, basePointSize to 20, step to 8 (fewer points, larger gaps).

## 11. Host integration

Deviates from the standard contract: it uses a `ResizeObserver` on the holder in
addition to `window.resize`, listens for `touchmove` as well as `pointermove`,
and relies on the host gradient — this is a transparent-canvas scene. DPR clamp
is 1.75 (RibbonFlow is the gallery's only 2.0). Teardown disconnects the
observer, removes
three listeners, deletes both buffers and the program, and loses the context.
The pointer is smoothed at 0.08 per frame toward the target.

## 12. Failure modes and tells

- **Canvas is a black rectangle instead of the host gradient →** context created
  without `alpha: true`, or `clearColor` set to opaque black.
- **Waves read as parallel ridges →** only one wave train is applied; the two
  perpendicular trains are what make the egg-carton surface.
- **Wave count changes with window width →** the wavelength uses a fixed world
  number instead of scaling with the grid width.
- **Dots vanish at the horizon →** the 4 px minimum point-size clamp was
  removed; perspective size falls below one pixel.
- **Surface looks like a solid sheet →** `step` too small or point size too
  large; the lattice gaps are the style.
- **Everything is grey →** the fragment's `1 + glow·falloff` boost was dropped,
  so additive summing never reaches white.
- **Grid rebuilds every frame and stutters →** `rebuildGrid` is being called in
  the render loop instead of on resize.

## 13. Tuning knobs

1. `amplitude` — calm swell versus rough sea (12–32).
2. `step` — point density and lattice legibility (5–9).
3. `cameraHeight` and `cameraDistance` — high overhead versus low grazing view.
4. `glow` — soft dots versus hot white cores (2–5).
5. `speed` — drifting versus rolling (0.3–0.9).

## 14. Verification checklist

- Regular rectangular lattice, not a random cloud.
- Two crossing wave directions visible as a saddle pattern.
- Near dots large and white-cored; far dots tiny and colored.
- Host gradient visible at the top: black fading to purple.
- No depth occlusion or sorting artifacts.
- Motion is a closed-form loop: X train 10.472 s, Z train 13.963 s, combined
  pattern 41.888 s.
- Compare with `assets/posters/particle-waves.jpg`: same lattice pitch and wave
  count; phase differs with time.

## 15. Porting notes

`gl_PointSize` must be divided by clip-space w after the matrix multiply — in
three.js, write the size manually in a `ShaderMaterial` rather than relying on
`PointsMaterial`, whose attenuation formula differs by a factor of the viewport
height. Reproduce the transparent-cleared canvas and additive blend or the
background gradient will not show.
