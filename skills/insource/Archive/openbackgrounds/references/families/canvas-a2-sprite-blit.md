---
family: canvas-a2
name: Sprite Blit
renderer: canvas2d
members: [bokeh-drift, data-rain, golden-bloom, kaleido-bloom]
---

# Canvas A2 — Sprite Blit

Four scenes that pre-render every mark once into offscreen canvases and then
spend their frame budget on `drawImage` calls. None of them samples noise, and
only KaleidoBloom tessellates a path. The shared problem is compositing: each
source is a semi-transparent sprite, and the look is decided by where the
alphas and the blend mode put the light.

## Members

| id | name | lines | tier | distinguishing trait |
| --- | --- | --- | --- | --- |
| bokeh-drift | Bokeh Drift | 368 | M | two baked falloffs per colour (plain and rim), plus 3 multiply shade lights |
| data-rain | Data Rain | 420 | L | 54-glyph strip atlas per layer, per-column ring buffer, travelling sweep gain |
| golden-bloom | Golden Bloom | 276 | M | no per-item objects; positions from index alone, 18 hue-step glows |
| kaleido-bloom | Kaleido Bloom | 412 | L | vector petals (bezier fill + stroke), mirrored per wedge, 5 counter-rotating layers |

## Shared scaffold

All four are single-file components with the same mount code. A holder div at
`absolute inset 0` with pointer events disabled contains a block canvas at full
width and height. The context is `getContext("2d", { alpha: false })`. Resize
reads `holder.offsetWidth/offsetHeight` with a `window.innerWidth/Height`
fallback, clamps `devicePixelRatio` to 1.5, floors the backing store to
`width·dpr` by `height·dpr`, writes the CSS size in pixels, sets the transform
to `(dpr, 0, 0, dpr, 0, 0)`, then rebuilds scene state from the CSS size. A
passive window resize listener is the only host event. Mount order is: create
context, bake sprites (Bokeh, Golden, Kaleido), resize (which calls buildScene),
run a synchronous warmup of N `drawFrame()` calls, start the shared FPS meter,
start the RAF loop. Teardown removes the listener, cancels the frame, stops the
meter, and drops the context and every array.

The loop body is always `frame += 1` followed by drawing; `step()` ticks the FPS
meter before drawing.

## Math primer

Counts are area-derived and clamped, never fixed:

- Bokeh: `clamp(round(W·H / 15500), 11, 124)` → 17 at 640x400, 124 at
  1920x1080 (134 before the clamp).
- Golden: `clamp(round(W·H / 620), 640, 2100)` → 640 at 640x400, 2100 at
  1920x1080 (3345 before the clamp).
- Kaleido sparks: `clamp(round(W·H / 46000), 12, 60)` → 12 and 45.
- DataRain: `ceil(W / cell) + 1` columns per layer → 101 columns at 640x400,
  295 at 1920x1080.

Length scales use the square root of area. Bokeh's base length is
`sqrt(W·H)`; Golden's `radiusUnit` is `reach / sqrt(count)` with
`reach = 0.53·hypot(W,H)`; Kaleido's reach is `0.345·hypot(W,H)`; DataRain's
column pitch is absolute.

Phyllotaxis is the one closed-form layout in the family:
`θ_i = i·π(3 − √5)` and `r_i = radiusUnit·√i`, where the golden angle is
2.399963 rad (137.5078°).

The sweep in DataRain is a gaussian gain `1 + G·exp(−x²/(2σ²))` with σ = 180 px
and G = 0.55.

Alpha under `lighter` composes as `out = min(1, Σ c_i·a_i)` per channel, so
overlap saturates toward white instead of averaging. This is why sprite alpha
must fall as sprite size rises: energy, not opacity, is what accumulates.

## Shared helpers

**Radial falloff baking.** A square canvas, a radial gradient centred at
`(s/2, s/2)` with radius `s/2`, filled over the whole square. Bokeh uses
s = 160; Golden and Kaleido s = 48; DataRain's head glow s = 64. The final stop
always has alpha 0, so the square edge never prints. Stops are authored in
display sRGB and interpolated there.

**Sprite variants.** Bokeh bakes 8 colours × 2 falloffs = 16 sprites; the rim
variant puts its brightest stop at 0.72 of the radius (alpha 0.92) with a dim
0.34 core, the plain variant decays monotonically (0.96, 0.62, 0.3, 0.09, 0 at
0, 0.24, 0.48, 0.74, 1). Golden bakes 18 hue steps from 38 to 104; Kaleido
bakes 6 from 192 to 322; DataRain bakes two text atlases and one glow per
glowing layer.

**Glyph strips.** A single row of 54 glyphs, one `advance` wide each. The
advance is `ceil(measureText("M").width)` at the layer's font size, falling
back to `ceil(font·0.62)`. Drawing uses the 9-argument `drawImage` with a source
rect of `advance × tileHeight`; the tile is never resampled because source and
destination sizes match, so glyphs stay crisp at DPR 1.5.

**Additive blitting.** `globalCompositeOperation = "lighter"` brackets the
sprite loop, `globalAlpha` is set per item, and both are reset after.

**Depth sorting.** None of the four sorts. Additive draws commute, so array
order is irrelevant; depth is expressed as size, alpha and speed (Bokeh), font
size and layer alpha (DataRain), spark radius (Kaleido). The only ordered passes
are non-additive: Bokeh's multiply shades run after the orbs and its vignette
last; everyone's vignette is last. A port adding a sorted queue must sort
back-to-front and keep the veil pass outside it.

## Conventions

Space is CSS pixels, origin top-left, y down. Angles are radians measured from
+x and increase clockwise on screen. Time is the frame counter; multiply by 60
for per-second rates. Colour is display sRGB, 8-bit, authored as `rgba` or
`hsla` strings. Sprite alpha is peak alpha, not average. Every scene repaints an
opaque ground each frame, so none of them accumulates and none can show the
host backdrop.

## Variation map

| if you want | change |
| --- | --- |
| more, smaller lights | lower Bokeh `orbArea`, or raise Golden `seedArea` |
| a denser downpour | lower DataRain `cell` values, not `speed` |
| a tighter bloom | raise Kaleido `reach` and lower `foldRange` |
| more colour travel | raise Golden `hueRange` span or Kaleido `hueSpan` |

## Porting

Any 2D canvas works. Rebuild offscreen sprites after a context loss, not on
resize. CSS `mix-blend-mode` is not a substitute for the in-canvas composite: it
blends the whole element, vignette included. Keep `alpha: false`; a transparent
canvas shows the host gradient through antialiased ground edges.

## Failure modes

- **Evenly bright sprites →** per-item alpha is constant; depth must modulate
  alpha, not only size.
- **Flat grey field →** total sprite energy too high for the count; raise the
  area constant or lower peak alpha.
- **Hard-edged squares or circles →** the outer gradient stop has nonzero
  alpha, or the sprite is drawn larger than its baked square.
- **Square seams in a glow →** gradient radius is not exactly half the sprite.
- **Text turns to blocks →** the measuring context and the atlas context use
  different font strings.
- **Bloom loses its core →** additive pass replaced with source-over.
- **Resize leaves a stale frame →** scene state rebuilt without its
  size-derived scale, or the transform set before the backing store changed.

## Verification heuristics

- Mean frame luminance stays between 2% and 12%; no large white region.
- Sprite count matches the area formula at both 640x400 and 1920x1080.
- Edges of every glow reach zero before the sprite boundary; no visible box.
- Overlaps brighten (additive), never darken.
- Motion is per-frame smooth: no jump when a column or orb respawns.
