---
id: analog-grain
name: Analog Grain
family: canvas-a6
renderer: canvas2d
poster: assets/posters/analog-grain.jpg
complexity: M
source_lines: 291
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Analog Grain

## 1. Identity

A dark warm film frame: two rolling gate bands and an exposure flicker over a
breathing brown ground, with baked emulsion grain boiling across everything.

## 2. Perceived look

Grainy and low-contrast. The warm brown ground sits behind a wandering lamp
highlight and one or two soft diagonal slabs of light; corners fall to near
black. There is no subject, no edge and no geometry — only texture and a slow
luminance drift. The grain is 1–2 px rough, denser than television snow and
clumpier. At t = 3 s the first gate band is crossing the lower-left corner and
the grain has re-rolled once per frame, 226 times counting warmup.

## 3. Frame anatomy

1. **Ground** — linear gradient (0, 0)→(0.22W, H), three HSL stops, opaque,
   `source-over`.
2. **Lamp** — radial warm bloom, `lighter`, alpha 0.0528–0.12 at the core.
3. **Gate band A** — slab along −0.36 rad, `lighter`, peak alpha 0.085.
4. **Gate band B** — slab along 0.52 rad, `lighter`, peak alpha 0.05.
5. **Flicker** — full-frame warm fill, `lighter`, alpha 0.0143–0.026.
6. **Vignette** — radial at (0.5W, 0.48H), `source-over`, 0.16 at 0.62r and 0.8
   at the rim.
7. **Grain** — 6 baked 232 px tiles stamped at alpha 0.62, `source-over`, nearest
   sampling.

Canvas is opaque (`alpha: false`); the host backdrop never shows.

## 4. Motion law

The ground breathes with period 3927 frames (65.45 s), lifting the stops by up to
3.4 percentage points. The lamp orbits on two detuned sines, 5712 frames (95.2 s)
in x and 4170 frames (69.5 s) in y, and pulses every 2027 frames (33.8 s). Gate A
crosses in 940 frames (15.67 s), gate B in 1610 frames (26.83 s); the periods
share no small factor, so the highlights never lap. Flicker is three sines at
0.21, 0.37 and 1.31 rad/frame — 2.0, 3.5 and 12.5 Hz at 60 fps. Grain offsets
and tile choices re-roll every frame. Nothing loops on any practical timescale.

## 5. Technique and math

**Tiles.** Six 232x232 canvases, built once. A coarse 78x78 random lattice is
nearest-sampled in 3 px blocks; per texel
`v = clamp(0.46·coarse + 0.56·(2·rand − 1), −1, 1)`. Positive v paints
`rgb(255, 243, 219)`, negative paints `rgb(7, 5, 9)`, and the alpha is shared:
`round(|v|^1.55 · 0.4 · 255)`, range 0..102. The gamma is what keeps most grains
faint; a linear mapping turns the field into uniform static.

**Stamping.** Per frame, an integer offset uniform in 0..231 is drawn, then tiles
are stamped from (−ox, −oy) on a 232 px grid, each cell choosing a variant at
random. That is 6–12 stamps at 640x400 and 45–60 at 1920x1080.

**Lamp.** Centre `(0.5W + 0.32W·sin(0.0011f), 0.46H + 0.28H·sin(1.37·0.0011f +
2.1))`, radius `0.62·hypot(W, H)`, pulse `0.72 + 0.28·sin(0.0031f)`. Gradient
stops: `rgba(255,208,152, lampAlpha·pulse)` at the centre,
`rgba(226,168,112, 0.36·lampAlpha)` at 0.34r, `rgba(120,82,58, 0.03)` at 0.7r,
transparent at r.

**Gate slab.** With `d = (cos a, sin a)` and `u = d·p`, the four corners give
`uMin..uMax`. With span `= min(W, H)·width`, the centre runs
`u = uMin − span + ((frame mod period)/period)·(uMax − uMin + 2·span) + phase`;
a gradient from `d·(u − span)` to `d·(u + span)` fills the frame, giving a slab
2·span wide. Band B's phase offset is `0.4·min(W, H)`.

**Flicker.** `wobble = 0.5·sin(0.21f) + 0.3·sin(0.37f + 1.7) + 0.2·sin(1.31f +
0.4)`; the fill alpha is `0.026·(0.55 + 0.45·(0.5 + 0.5·wobble))`.

**Why not per-pixel.** At 1920x1080 with DPR 1.5 the main canvas is 4,665,600
device pixels; one ImageData pass per frame is 18.66 MB allocated, filled and
uploaded, sixty times a second. The baked tiles cost 322,944 texels once — 
1,291,776 bytes — and every later frame is a blit.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | DPR clamp | L |
| grainTile | 232 | 128–384 | tile edge in CSS px; visible grain weight | M |
| grainVariants | 6 | 3–12 | independent noise fields mixed per cell | M |
| grainPeak | 0.4 | 0.2–0.6 | maximum grain alpha before the 0.62 stamp alpha | H |
| grainGamma | 1.55 | 1.0–2.2 | histogram skew; lower = TV snow | H |
| grainAlpha | 0.62 | 0.3–0.85 | per-stamp alpha; overall grain strength | H |
| breatheSpeed | 0.0016 | 0.0005–0.004 | ground lift rate, 65.45 s period | L |
| lampSpeed | 0.0011 | 0.0005–0.003 | lamp orbit rate | L |
| lampAlpha | 0.12 | 0.05–0.25 | lamp core opacity | M |
| gateAPeriod | 940 | 600–1600 | first band crossing time, 15.67 s | H |
| gateAWidth | 0.5 | 0.3–0.8 | slab width as a fraction of min(W,H), doubled | M |
| gateBPeriod | 1610 | 1000–2400 | second band, 26.83 s; keep it off A's period | M |
| gateBWidth | 0.86 | 0.4–1.0 | second slab width; wider reads as a wash | L |
| gateAlpha | 0.085 / 0.05 | 0.03–0.15 | band peak opacity, A / B | M |
| flickerAlpha | 0.026 | 0.01–0.06 | exposure wobble depth | M |
| vignette | 0.8 | 0.4–0.95 | corner darkness | M |
| warmup | 46 | 0–200 | advances the gate phase before first paint | L |

## 7. Palette and color

Ground stops `hsl(33, 36%, 9.4 + 3.4b)`, `hsl(27, 27%, 6.2 + 2.38b)`,
`hsl(228, 22%, 3.2 + 1.19b)` with `b` the 0..1 breathe. Lamp
`rgba(255, 208, 152, a)` → `rgba(226, 168, 112, 0.36a)` → `rgba(120, 82, 58,
0.03)`; gate stops `rgba(255, 233, 199, α)` and `rgba(255, 224, 184, 0.7α)` with
α 0.085 for A and 0.05 for B; flicker `rgba(255, 232, 198, ...)`; vignette
`rgba(3, 2, 5, 0.8)`. Grain pixels `rgb(255, 243, 219)` and `rgb(7, 5, 9)`. All
display sRGB, added in sRGB.

## 8. Composition and camera

Full-bleed, no camera and no geometry. The lamp centre travels ±32% of width and
±28% of height around (0.5W, 0.46H), so it can leave the frame; the vignette
centre is fixed at (0.5W, 0.48H). Gate angles are absolute, so wide frames show
longer slabs and tall frames shorter ones. No safe margins — grain, bands and
lamp all run to the edges. Nothing is aspect-corrected, and nothing needs to be.

## 9. Randomness and seeds

`Math.random()` only, no seed. Tile baking draws 36,504 coarse lattice values and
one fine value per texel across six tiles; per frame it draws the offset pair and
one variant index per cell. Ground, lamp, gates and vignette are deterministic.
Warmup is 46 frames (0.767 s), which only advances the gate phase; it primes no
random state and no accumulation.

## 10. Performance budget

Bake cost: 6 × 232² = 322,944 texels, 1.29 MB of ImageData, once. Per frame:
6–12 `drawImage` calls at 640x400, 45–60 at 1080p, plus six full-screen gradient
fills (ground, lamp, two gates, flicker, vignette). Backing store 960x600 at
640x400. Fill-rate bound, not CPU bound; holds 60 fps on an iGPU. Cut order:
gate B, lamp radius, tile count.

## 11. Host integration

Standard contract. Mount: opaque context, bake six tiles, resize (which sets the
transform and disables image smoothing), 46 synchronous frames, passive resize
listener, FPS meter, RAF. Tiles are never rebuilt on resize because their size is
in CSS pixels; only the transform changes. Teardown cancels the frame, removes
the listener, stops the meter and drops the context and tiles. No assets, no
dependencies.

## 12. Failure modes and tells

- **Grain reads as television snow →** `grainGamma` at 1.0; restore 1.55 so the
  histogram stays bottom-heavy.
- **Static screen-door texture →** offset or variant not re-rolled per frame.
- **Visible rectangular patches →** smoothing enabled, or tiles drawn at a size
  other than 232 CSS px.
- **Flat, lifeless frame →** both gates omitted, or their periods made
  commensurate so they travel together.
- **Exposure pumps like a sine →** single-sine flicker; use three detuned terms.
- **Grain vanishes in the corners →** grain drawn before the vignette.
- **Warm cast turns grey →** the lamp and gate fills drawn `source-over` instead
  of `lighter`.

## 13. Tuning knobs

1. `grainAlpha` — 0.4 subtle, 0.8 heavy (0.3–0.85).
2. `grainPeak` — 0.3 finer, 0.5 coarser (0.2–0.6).
3. `gateA.alpha` — 0.12 for a stronger light leak (0.05–0.15).
4. `flickerAlpha` — 0.04 for visible exposure wobble (0.01–0.06).

## 14. Verification checklist

- Mean luminance 4–12%; the frame is dark but not black.
- Grain visible at 1:1 as 1–2 px speckle, evenly dense across the frame.
- A diagonal band crosses every 15.67 s and a second every 26.83 s.
- Corners lose about 35% of centre luminance (the vignette reaches 0.8 only at
  1.0·radius = 0.68·hypot(W, H), beyond the corners), and remain grainy.
- No banding or tile edges.
- Compare `assets/posters/analog-grain.jpg` for warm hue and near-black
  luminance; band position depends on capture time.

## 15. Porting notes

Bake the grain into textures and stamp quads; a full-resolution fragment-noise
grain costs what the tiles exist to avoid. Keep nearest sampling and integer
offsets. Additive fills must be additive in the same space as the ground: in a
linear-light pipeline convert the warm colours first, or the frame drifts yellow.
