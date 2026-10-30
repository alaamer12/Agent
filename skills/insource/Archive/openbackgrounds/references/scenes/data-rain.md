---
id: data-rain
name: Data Rain
family: canvas-a2
renderer: canvas2d
poster: assets/posters/data-rain.jpg
complexity: M
source_lines: 420
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Data Rain

## 1. Identity

Three depths of monospace glyph columns fall at different speeds through a
near-black teal field, each led by a hot glyph, head glows on the near two,
while a bright sweep crosses left to right.

## 2. Perceived look

Crisp glyphs on a soft ground, layered by size: 21 px columns in front, 13.5 px
behind, 9.5 px back. Density is high — 101 columns at poster size — but tails
are short, so the frame reads as vertical streaks, not a wall of text. Contrast
peaks at the leading glyphs, 93% lightness against 56%. A faint teal haze
covers the top third. At t = 3 s the sweep has entered from the left, lifting a
423.868 px band by up to 55%.

## 3. Frame anatomy

1. **Ground** — full-rect vertical gradient, `#02090a` to `#01060a` at 0.4 to
   `#000204`. Opaque, repainted every frame, `source-over`.
2. **Top wash** — additive linear gradient over the top 34% of the height,
   `rgba(20, 118, 100, 0.26)` to `rgba(8, 54, 50, 0)`.
3. **Head glows** — additive radial sprites, 67.2 px on the near layer and
   32.4 px on the middle layer, once per column at the head position, alpha
   0.05–0.9.
4. **Glyph columns** — additive `drawImage` blits from a pre-baked strip, alpha
   0.03–1.
5. **Vignette** — radial gradient at (0.5W, 0.45H), inner radius 0.3R, outer
   R = 0.82·max(W, H), `rgba(0, 3, 4, 0)` to `rgba(0, 3, 4, 0.6)`.

Canvas alpha is false; under `lighter`, draw order is irrelevant.

## 4. Motion law

Each column's head advances by its speed in px/frame: layer 1 0.95–2.15
(57–129 px/s at 60 fps), layer 2 0.6–1.4 (36–84 px/s), layer 3 0.35–0.9
(21–54 px/s). The head snaps to the row grid, so glyphs jump one pitch at a
time — 23.94, 15.39 and 10.83 px — at 1.94–5.46 rows/s. Tails follow the ring
buffer. Respawn happens when head − tail·pitch > H, placing the new head between
−2·tail·pitch and −pitch. A column burns for 56 frames (0.93 s) with probability
0.0038 per frame when not already burning. The sweep crosses at 42 px/s; nothing
else moves horizontally.

## 5. Technique and math

The glyph set is 54 characters: 10 digits, 20 capitals, 14 punctuation marks and
10 Greek letters. At each layer's font size the advance is
`ceil(measureText("M").width)` with fallback `ceil(font·0.62)` — typically 13,
9 and 6 px. The atlas is `advance × 54` wide by `tileHeight` tall, where
`pitch = max(4, font·1.14)` = 23.94, 15.39, 10.83 and
`tileHeight = ceil(pitch·1.5)` = 36, 24, 17. Two atlases per layer are baked:
body at 56% lightness, head at 93% lightness in `hue − 10`. Layers with
`glow > 0` also get a glow sprite.

Columns: `ceil(W / cell) + 1` per layer = 22, 32, 47 at 640x400 and 63, 93, 139
at 1920x1080; x = i·cell + cell/2. Each column owns an `Int16Array` of
`tail + 3` glyph indices and a pointer. When the row index changes, the pointer
advances one step per crossed row and each new slot gets a random glyph; with
probability 0.05 one glyph 0–tail−2 rows behind the head is rewritten (the
formula can also land one slot ahead when the random draw hits its extreme).

Drawing: `startY = floor(head / pitch)·pitch`, then k = 0..tail at
`y = startY − k·pitch`. The source is the hot atlas for k = 0, and also for
k = 1 while a burn is above 0.25; otherwise the body atlas. Tail fade is
`(1 − k/(tail + 1))^1.5`. Alpha is `clamp(base·(0.95 + 0.5·burn), 0.25, 1)` at
the head and `clamp(base·fade·(k = 1 ? 1.35 : 1), 0.03, 0.92)` behind it, with
`base = gain·layerAlpha·sweep`, gain uniform 0.7..1.25.

Sweep: `sweepX = (frame·0.7 mod (W + 800)) − 400`, and
`sweep = 1 + 0.55·exp(−dx² / 64800)` with dx = column.x − sweepX and
σ = 180 px (FWHM 423.868 px).

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | device pixel ratio clamp | L |
| layers[0].cell | 31 | 20–48 | near column pitch in px | H |
| layers[0].font | 21 | 12–34 | near glyph size | H |
| layers[0].speed | [0.95, 2.15] | 0.4–3 | near fall speed in px/frame | H |
| layers[0].tail | [8, 14] | 3–24 | near trail rows | H |
| layers[1] | cell 21, font 13.5, alpha 0.66, hue 165, glow 2.4 | — | mid-depth column style | M |
| layers[2] | cell 14, font 9.5, alpha 0.42, hue 178, glow 0 | — | far column style; glow off | M |
| bodyLight | 56 | 40–70 | body glyph lightness, percent | H |
| headLight | 93 | 80–100 | leading glyph lightness, percent | M |
| rowPitch | 1.14 | 1.0–1.4 | row spacing as a multiple of font size | M |
| tailCurve | 1.5 | 1–3 | exponent of the tail fade | M |
| flicker | 0.05 | 0–0.15 | per-glyph brightness jitter | M |
| burnChance | 0.0038 | 0–0.01 | per-frame ignition chance per column | H |
| burnFrames | 56 | 20–120 | burn duration in frames | M |
| sweepWidth | 200 | 80–400 | gaussian sweep radius; σ = 0.9·width | H |
| sweepGain | 0.55 | 0–1.2 | peak brightness lift inside the sweep | H |
| sweepSpeed | 0.7 | 0.2–2 | sweep travel, px/frame | M |
| warmup | 70 | 20–200 | hidden pre-roll frames | L |

## 7. Palette and color

Each layer is one hue at 94% saturation: 152 (near), 165 (middle), 178 (far).
Body glyphs are hsl(hue, 94%, 56%), heads hsl(hue − 10, 94%, 93%) — head hues
142, 155, 168. Glows ramp from hsla(hue, 100%, 88%, 0.9) at the centre to
hsla(hue, 100%, 44%, 0) at 64 px. Ground `#02090a` → `#01060a` → `#000204`;
top wash `rgba(20, 118, 100, 0.26)`; vignette `rgba(0, 3, 4, 0.6)`. All display
sRGB. Additive overlap pushes dense heads toward `#E8FFF8`, never past it.

## 8. Composition and camera

Column pitch is absolute, so a small canvas gets fewer, chunkier columns and a
wide one gets a denser downpour. 101 columns at 640x400, 295 at 1920x1080; the
count scales with W, not W·H, so a portrait frame keeps the same column count
and reads sparser per unit width. Trails are 191.52–335.16 px long on the near
layer, 76.95–153.9 px middle, 32.49–75.81 px far. Heads are allowed to run off
the top and bottom; the first half-cell is inset from each edge.

## 9. Randomness and seeds

`Math.random()` only; any seed, same distribution. At build, heads are seeded
uniform in [−tail·pitch, 0.94H] so the frame opens full; respawns start above the
top in [−2·tail·pitch, −pitch]. Glyphs are uniform over 54, gain uniform
0.7..1.25, ignitions are Bernoulli trials at 0.0038 per column per frame.
Seventy warmup frames move the sweep to x = −351 px, so its right flank is
already on screen.

## 10. Performance budget

About 818 glyph blits per frame at 640x400 and 2381 at 1920x1080, plus 54 and
156 head glows. Three strip atlases (702×36, 486×24, 324×17 px) and two glows
bake once per resize. Two linear and one radial gradient are rebuilt per frame;
cost tracks column count linearly. DPR 1.5; holds 60 fps on integrated
graphics. Cut order: far layer `cell`, then `tail` maxima, then DPR.

## 11. Host integration

Standard contract: positioned `inset: 0` host, size from
`offsetWidth/offsetHeight` with window fallback, passive resize listener, a
synchronous 70-frame warmup, then RAF. Context is
`getContext("2d", { alpha: false })` with `imageSmoothingQuality = "high"`.
Resize re-measures the advance and re-bakes every atlas, because column geometry
depends on font metrics. Teardown cancels the frame, stops the meter, and clears
the layer array.

## 12. Failure modes and tells

- **Glyphs render as boxes →** the measuring and atlas contexts use different
  font strings, or the atlas was not rebuilt after resize.
- **Columns overlap or gap →** advance measured with the fallback while the
  atlas used the real font.
- **No sweep visible →** σ scaled with width; keep σ = 180 px and the 800 px
  off-screen margin.
- **Rain restarts mid-frame →** the respawn threshold uses tail·pitch, so a
  short tail recycles too early.
- **Heads not brighter →** hot atlas baked with `bodyLight`.
- **Whole frame milky →** glow alpha and the top wash double-count; lower 0.42
  first.
- **Trailing glyphs visibly flicker →** `flicker` above 0.1 rewrites too close
  to the head.

## 13. Tuning knobs

1. `cell` per layer — lower for a denser downpour (14–40).
2. `tail` — longer gives 300+ px streaks (3–24).
3. `bodyLight` — 45 dimmer, 64 brighter.
4. `sweepGain` — 0 removes the sweep, 0.9 gives a hot band.
5. `burnChance` — raise for more ignitions (0.001–0.008).

## 14. Verification checklist

- Hue band 142–178 only; no blue or white glyphs.
- 101 columns at 640x400, 295 at 1920x1080; no gap wider than 31 px.
- Near-layer trail 192–335 px; far layer 32–76 px.
- Head at 93% lightness, body at 56%, both 94% saturation.
- Sweep crosses in 15.24 s at 640x400 (914 frames).
- Compare to `assets/posters/data-rain.jpg`: same teal hue, three tiers, top
  haze. Glyphs differ.

## 15. Porting notes

Font metrics differ per platform, so measure the advance at runtime and never
hardcode 13/9/6. Non-monospace fallbacks break the strip layout: keep the
monospace stack. Sub-pixel text positioning costs sharpness; round column x to
whole pixels.
