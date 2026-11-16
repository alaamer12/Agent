---
id: firefly-meadow
name: Firefly Meadow
family: canvas-a1
renderer: canvas2d
poster: assets/posters/firefly-meadow.jpg
complexity: M
source_lines: 329
dpr_max: 1.5
deps: [simplex-noise]
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Firefly Meadow

## 1. Identity

Forty-nine motes wander slowly over a dark teal meadow and each fires a warm
pinprick flash on its own 2.5–10.33 s cycle, so the frame reads as scattered,
uncorrelated blinks.

## 2. Perceived look

Very dark, low contrast, no grain and no geometry. The ground runs blue-black,
through a muted green-teal band at 66% height, to near-black at the bottom. Motes
are pinpricks: a tight white-cream core inside a soft halo 11.2–62.8 px across at
640x400. Most of the population is unlit, so 10–20 flashes show at once. Edges
are all soft. The bottom 45% is veiled darker, partially occluding the lowest
motes. At t = 3 s the crowd has moved 30–70 px and roughly 20 motes are mid-flash.

## 3. Frame anatomy

1. **Ground** — one vertical linear gradient, five stops, lightness breathing
   between 3.2% and 8.7%: `hsl(206, 44%, 3.2–3.8%)`, `hsl(192, 40%, 5.2–6.1%)`,
   `hsl(160, 32%, 7.4–8.7%)` at 0.66, `hsl(154, 30%, 3.6%)`, `hsl(150, 24%, 1.9%)`.
   `source-over`, opaque, repainted every frame.
2. **Horizon glow** — radial at (cx, 0.66H), radius 0.7·max(W, H),
   `rgba(150, 214, 168, 0.13)` → 0.055 at 0.28 → 0.02 at 0.65 → transparent.
   Painted `source-over`, not additive.
3. **Motes** — additive. Each draws one 128 px tinted halo at alpha
   `0.5·flash + 0.028`, then a filled core disc in `rgb(255, 248, 226)` at alpha
   `0.95·flash + 0.07`.
4. **Foreground veil** — linear gradient over the bottom 45%:
   `rgba(2, 5, 5, 0)` → 0.42 at 0.62 of that band → `rgba(1, 3, 3, 0.86)`.
5. **Vignette** — radial at (0.5W, 0.56H), radius 0.66·hypot(W, H), inner
   0.32·radius, `rgba(1, 3, 4, 0)` → 0.68.

The canvas is opaque (`alpha: false`); the host gradient never shows.

## 4. Motion law

Speed is 0.1686–0.39 px/frame (10.12–23.4 px/s at 60 fps) across depth 0.18–1.
Heading comes from the noise field multiplied by 2π·1.7, so the direction can
point anywhere, but neighbouring motes share it locally and the paths curve. The
vertical component is scaled by 0.72, and a bob term of ±0.075 px at
0.006–0.019 rad/frame is added. Motes wrap once their centre is a full halo
diameter outside the frame, so nothing respawns.

Blink phase advances by 1/period per frame; period is 150–620 frames and is
re-rolled at every wrap. The lit window is the first 42% of the cycle (63–260.4
frames, 1.05–4.34 s); the other 58% is dark. Open-ended, no loop.

## 5. Technique and math

Count is `clamp(round(A / 5200), 26, 320)` → 49 at 640x400, 320 at 1920x1080
(399 before the cap).

Placement: x uniform across the width; `y = H·(0.2 + 0.8·u^0.72)`. Since
`u^0.72` has mean 0.5814, the mean y is 0.665H — the population sits low, thinning
upward, and never enters the top fifth.

Halo diameter is `√A·(0.034 + u·0.058)·(0.5 + 0.85·depth)`, which gives 11.233–62.84 px
at 640x400 and 31.97–178.85 px at 1920x1080. It is drawn at `0.72 + 0.5·flash`
times that, so a flashing mote also swells.

Core radius is `(0.9 + u·2.4)·(0.55 + 0.7·depth)` → 0.61–4.13 px. Note the quirk
in the source: the second range value is a span added to 0.9, not a maximum, so
cores reach 3.3 before the depth factor.

The blink envelope, with t = phase/0.42 inside the lit window: zero when
phase ≥ 0.42; `(t/0.22)^0.6` for t < 0.22; `(1 − (t − 0.22)/0.78)^1.9` after. The
peak is at t = 0.22. The 0.6 exponent makes the strike fast but not instant; the
1.9 exponent gives the long drain that reads as an insect rather than an LED.

Heading is 2D simplex noise (gradient variant, −1..1) sampled at
`(x·0.0017 + 17, y·0.0017 + frame·0.00042)`. One cell is 588.2 px; the second
argument drifts 0.0252 units/s, so the whole current slides slowly downward
through the field. The constant 17 is arbitrary but must be kept if you want the
wander pattern decorrelated from other scenes that sample the same function.

Alpha floors are 0.028 for the halo and 0.07 for the core, so an unlit mote still
prints a faint dot — those are the dim specks between flashes in the poster.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | device-pixel-ratio clamp | L |
| moteArea | 5200 | 3000–9000 | area per mote; 49 at 640x400 | H |
| minMotes | 26 | 12–40 | floor for small surfaces | M |
| maxMotes | 320 | 200–500 | cap at 1080p | L |
| haloRange | [0.034, 0.092] | 0.02–0.12 | halo diameter as √A fraction | H |
| coreRange | [0.9, 2.4] | 0.5–3 | core radius base plus uniform term | M |
| speed | 0.3 | 0.1–0.6 | base px/frame, depth-scaled | M |
| noiseScale | 0.0017 | 0.0008–0.003 | inverse cell; 588.2 px | M |
| fieldDrift | 0.00042 | 0–0.0012 | current drift per frame | L |
| bob | 0.075 | 0–0.2 | vertical sine amplitude px | L |
| period | [150, 620] frames | 80–1000 | blink cycle length | H |
| duty | 0.42 | 0.2–0.7 | fraction of cycle that is lit | H |
| rise | 0.22 | 0.08–0.5 | strike fraction of the lit window | H |
| haloAlpha | 0.5 | 0.2–0.8 | peak halo opacity | M |
| coreAlpha | 0.95 | 0.5–1 | peak core opacity | M |
| ember | 0.07 | 0.02–0.2 | unlit floor for core and halo | M |
| horizonY | 0.66 | 0.5–0.8 | glow band center as height fraction | M |
| warmup | 96 | 60–200 | hidden frames before first paint | M |

## 7. Palette and color

Ground: `hsl(206, 44%, 3.2–3.8%)` → `hsl(192, 40%, 5.2–6.1%)` →
`hsl(160, 32%, 7.4–8.7%)` at 0.66 → `hsl(154, 30%, 3.6%)` →
`hsl(150, 24%, 1.9%)`. Glow `rgb(150, 214, 168)` ≈ hsl(136.9, 43.8%, 71.4%). Halo
tints: `rgb(255, 214, 138)` ≈ hsl(39, 100%, 77.1%), `rgb(255, 236, 186)` ≈
hsl(43.5, 100%, 86.5%), `rgb(214, 255, 190)` ≈ hsl(97.9, 100%, 87.3%) — amber,
cream, pale green. Core `rgb(255, 248, 226)` ≈ hsl(45.5, 100%, 94.3%). Foreground
`rgba(2, 5, 5)`. The halo sprite is baked per tint at 128 px with stops 0.9, 0.46
at 0.09, 0.16 at 0.22, 0.05 at 0.46, 0.014 at 0.76, 0 at 1. Additive overlap
pushes a double flash toward white; display sRGB, no tonemapping, and the
gradient stops interpolate in sRGB.

## 8. Composition and camera

No camera. Horizon sits at 66% height and the glow centre sways ±24% of the width
on a 171.7 s period, so the band drifts laterally over minutes. Motes occupy
0.2H–1H only. Halo size scales with √A, so 1080p holds 6.53× as many motes with
halos 2.846× larger: the same texture at the same relative scale, not a coarser
one. The bottom veil is anchored at 0.55H and always covers 45% of the height.
Narrow frames keep the count per area — a 320x1080 column shows 66 motes.

## 9. Randomness and seeds

`Math.random()`, no seed; any seed gives the same distribution. Uniform: x,
tint, halo fraction, core, depth, phase (0–1), period, bob speed, blink seed.
Height is biased by the 0.72 exponent. The first frame already contains a full
age spread because phase is randomized at placement. Warmup: 96 frames (1.6 s).

## 10. Performance budget

49–320 motes, each one `drawImage` of a 128 px sprite plus one arc fill; three
baked sprites; four full-screen gradient passes per frame. DPR capped at 1.5.
Runs at 60 fps at 1920x1080 on a laptop iGPU. Cut order: halo draw (already
skipped below alpha 0.004), then mote count, then the per-mote core arc, then DPR.

## 11. Host integration

Standard contract. Sprites are baked once at mount, before the first resize; the
context is created with `alpha: false`. Resize re-derives size and re-places every
mote from scratch — the meadow re-seeds and the sky jumps. Passive window resize
is the only listener; no observer. Teardown cancels the RAF, removes the
listener, stops the meter, and drops the sprites and the mote array.

## 12. Failure modes and tells

- **Frame reads blue-black, not green** → ground hue stops not 206→192→150, or
  the glow omitted; the glow is `source-over` at 0.13, not additive.
- **Meadow blinks together** → shared period; each mote needs its own phase and
  period.
- **Symmetric, mechanical blinks** → envelope replaced by a sine; the 0.6 strike
  and 1.9 decay exponents are the tell.
- **Motes crowd the sky** → y exponent inverted; 0.72 biases downward (mean
  0.665H).
- **Motes never go fully dark** → `ember` raised above 0.07 or the alpha floors
  dropped.
- **Squares around halos** → last sprite gradient stop above alpha 0.
- **Motes pop at edges** → wrap pad smaller than the halo diameter.
- **No dim specks between flashes** → core floor missing; it should still print
  at 0.07.

## 13. Tuning knobs

1. `duty` — 0.25 for rare flashes, 0.55 for a busy meadow.
2. `period` — 80–300 frames for nervous, 400–1000 for lazy.
3. `haloRange` — raise for out-of-focus discs, lower for pinpricks.
4. `ember` — 0.03 for a blacker sky, 0.15 for a visible crowd.
5. `moteArea` — 3000 for density, 9000 for isolation.

## 14. Verification checklist

- 49 motes at 640x400, 320 at 1920x1080.
- Green-teal band centred at 66% height ±2%; dominant hue 150–206.
- 10–20 lit motes at once; most of the population dark.
- Halo diameters 11.233–62.84 px at 640x400, never a crisp circle edge.
- One flash lasts 1.05–4.34 s, not a uniform pulse.
- Mean luminance 3–8%; no white region; bottom 20% nearly black.
- Compare to `assets/posters/firefly-meadow.jpg` for band height and mote scale.

## 15. Porting notes

Keep the additive pass and the pre-baked sprite; a per-frame radial gradient per
mote is 50–320 gradients and will not hold 60 fps. In a premultiplied-alpha
pipeline, multiply the sprite colour by its alpha. The ground's lightness steps
are under 2 percentage points, so quantize to full 8-bit channels rather than a
coarse palette or the horizon will band.
