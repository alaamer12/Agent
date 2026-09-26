---
name: svg-animate
description: "Animate a static, flat SVG logo or icon (solid-fill <path> elements) with one of twenty-five animation styles: chrome-liquid, draw-fill, loading-loop, elastic-entrance, rise, iris, neon, pulse, flip, comet, focus (rack-focus, blur resolves), crt (TV power-on + scanlines), chroma (RGB ghosts converge), mosaic (tiled mask dissolve), ripple (turbulence warps geometry), spark (a travelling spark reveals), engrave (emboss under raking light), grain (noise-threshold dissolve), tide (wavy waterline rises), polarity (inverting band sweeps), blinds (slats open), assemble (fragments fly in and lock), lantern (a wandering light reveals), pinwheel (wedges scale open), unroll (falls from a top hinge). Per-style signatures are in the SKILL.md table. Trigger when the user asks to animate a logo/SVG, names any of these effects, wants an existing treatment replicated on a new file, or needs light/dark theme variants. Always preserves fill-rule=evenodd so letterform holes (Arabic ص/ه, Latin a/o/e) never fill in solid."
argument-hint: "<style> <file.svg>  (style: liquid|draw|load|elastic|rise|iris|neon|pulse|flip|comet|focus|crt|chroma|mosaic|ripple|spark|engrave|grain|tide|polarity|blinds|assemble|lantern|pinwheel|unroll)"
---

# SVG Logo Animation Meta-Skill

Turns a static SVG (flat `<path>` elements with solid fills) into an animated
version using one of **twenty-five animation styles**. The foundations below apply to
EVERY style; the per-style build recipes live in `references/`.

| Style | Reference file | Signature | Duration |
|---|---|---|---|
| `chrome-liquid` | `references/chrome-liquid.md` | Chrome outline draws itself → true colors rise like liquid bottom-to-top → diagonal sheen sweeps across | ~8s, then sheen loops |
| `draw-fill` | `references/draw-fill.md` | Each outline draws itself, then its fill fades in | ~3.5s one-shot |
| `loading-loop` | `references/loading-loop.md` | Outlines draw and reverse endlessly, never filling | infinite |
| `elastic-entrance` | `references/elastic-entrance.md` | Logo elastically scales/rotates in, wobbles, glows, fades out | ~8s loop |
| `rise` | `references/rise.md` | Shapes rise from below and fade in, one after another | ~2.5s one-shot |
| `iris` | `references/iris.md` | Circular clip grows from the center, revealing the logo like a camera iris | ~1.5s one-shot |
| `neon` | `references/neon.md` | Dark stage, outlines flicker on like a neon sign, then fill glows steady | ~2s, holds |
| `pulse` | `references/pulse.md` | Logo breathes — calm scale + glow inhale/exhale | infinite |
| `flip` | `references/flip.md` | Logo flips in like a card around its vertical axis | ~0.9s one-shot |
| `comet` | `references/comet.md` | Bright dash traces each outline endlessly like a comet; fills stay lit dimly | infinite |
| `focus` | `references/focus.md` | Camera rack-focus — the artwork itself is soft and sharpens, with one deliberate re-blur | ~1.4s one-shot |
| `crt` | `references/crt.md` | Hot line on the centreline, logo opens vertically out of it through scanlines that then fade | ~1.2s one-shot |
| `chroma` | `references/chroma.md` | Artwork splits into RGB channel ghosts, slides apart, converges back to the exact brand color | ~1.8s one-shot, dark stage |
| `mosaic` | `references/mosaic.md` | Grid of mask tiles each opening on its own jittered beat, so a wave crosses the logo | ~1.4s one-shot |
| `ripple` | `references/ripple.md` | Fractal noise displaces the actual geometry and the warp relaxes to crisp | ~1.6s one-shot |
| `spark` | `references/spark.md` | A bright spark travels the logo and the artwork stays lit in its wake | ~1.6s one-shot |
| `engrave` | `references/engrave.md` | Blind embossed relief under a raking light that sweeps around, then real colors land | ~1.8s one-shot |
| `grain` | `references/grain.md` | Resolves out of film grain as a noise threshold is raised until nothing is masked | ~1.5s one-shot |
| `tide` | `references/tide.md` | A wavy waterline rises and flattens, filling the logo from below | ~1.6s one-shot |
| `polarity` | `references/polarity.md` | A band sweeps across and inverts whatever it touches | ~1.3s one-shot |
| `blinds` | `references/blinds.md` | Horizontal slats open one after another, each growing its own height | ~0.9s one-shot |
| `assemble` | `references/assemble.md` | Rectangular fragments fly in from scattered offsets and lock into the whole logo | ~1.6s one-shot |
| `lantern` | `references/lantern.md` | A soft round light wanders across and blooms, revealing the logo in its path | ~1.5s one-shot |
| `pinwheel` | `references/pinwheel.md` | Wedges each scale up from the center on their own beat, sweeping like a turbine | ~1.4s one-shot |
| `unroll` | `references/unroll.md` | The logo falls into place around a fixed top hinge, like paper unrolling | ~1.1s one-shot |

## Commands

Each style has its own command argument — `/svg-animate <command> <file.svg>`.
Running a command on a target SVG must reproduce the matching reference
treatment (structure and ordering; numbers re-derived per the scaling table):

| Command | Style | Reproduces |
|---|---|---|
| `/svg-animate liquid <file.svg>` | `chrome-liquid` | `variations/1 (3).svg` (= `1 (6).svg`) — chrome stroke → liquid fill → sheen |
| `/svg-animate draw <file.svg>` | `draw-fill` | `variations/1 (4).svg` (= `1 (7).svg`) — outline draws, fill fades in |
| `/svg-animate load <file.svg>` | `loading-loop` | `variations/1 (5).svg` — outline draws/reverses forever |
| `/svg-animate elastic <file.svg>` | `elastic-entrance` | `variations/1 (2).svg` — elastic entrance, wobble, glow loop |
| `/svg-animate rise <file.svg>` | `rise` | — (new style) staggered rise-and-fade |
| `/svg-animate iris <file.svg>` | `iris` | — (new style) circular clip reveal |
| `/svg-animate neon <file.svg>` | `neon` | — (new style) neon-sign flicker-on with glow |
| `/svg-animate pulse <file.svg>` | `pulse` | — (new style) breathing scale + glow loop |
| `/svg-animate flip <file.svg>` | `flip` | — (new style) 3D card-flip reveal |
| `/svg-animate comet <file.svg>` | `comet` | — (new style) bright dash traces outlines forever |
| `/svg-animate focus <file.svg>` | `focus` | `examples/focus.svg` — rack-focus, blur resolves with one re-blur |
| `/svg-animate crt <file.svg>` | `crt` | `examples/crt.svg` — band opens off the centreline through scanlines |
| `/svg-animate chroma <file.svg>` | `chroma` | `examples/chroma.svg` — RGB channel ghosts converge on a dark stage |
| `/svg-animate mosaic <file.svg>` | `mosaic` | `examples/mosaic.svg` — tiled mask dissolve, wave left-to-right |
| `/svg-animate ripple <file.svg>` | `ripple` | `examples/ripple.svg` — turbulence displaces the geometry, then settles |
| `/svg-animate spark <file.svg>` | `spark` | `examples/spark.svg` — travelling spark, artwork stays lit behind it |
| `/svg-animate engrave <file.svg>` | `engrave` | `examples/engrave.svg` — embossed relief under a raking light, colors land |
| `/svg-animate grain <file.svg>` | `grain` | `examples/grain.svg` — resolves out of film grain |
| `/svg-animate tide <file.svg>` | `tide` | `examples/tide.svg` — wavy waterline rises and flattens |
| `/svg-animate polarity <file.svg>` | `polarity` | `examples/polarity.svg` — inverting band sweeps across the logo |
| `/svg-animate blinds <file.svg>` | `blinds` | `examples/blinds.svg` — slats open one after another |
| `/svg-animate assemble <file.svg>` | `assemble` | `examples/assemble.svg` — fragments fly in and lock together |
| `/svg-animate lantern <file.svg>` | `lantern` | `examples/lantern.svg` — wandering light reveals, then blooms |
| `/svg-animate pinwheel <file.svg>` | `pinwheel` | `examples/pinwheel.svg` — wedges scale open from the centre in sequence |
| `/svg-animate unroll <file.svg>` | `unroll` | `examples/unroll.svg` — falls into place around a fixed top hinge |

The four `variations/1 (n).svg` rows above refer to the original external
reference set, which is **not in this repository** — the recipes in
`references/` are the authoritative description of those treatments, and the
fifteen `examples/` files are committed.

Aliases: `chrome`/`chrome-liquid`→`liquid`, `draw-fill`→`draw`,
`loading`/`loading-loop`→`load`, `rack-focus`/`defocus`→`focus`,
`tv`/`power-on`/`scanline`→`crt`, `rgb-split`/`chromatic-aberration`→`chroma`,
`dissolve`/`tiles`→`mosaic`, `water`/`liquid-warp`→`ripple`,
`weld`/`torch`→`spark`, `emboss`/`deboss`/`letterpress`→`engrave`,
`noise`/`film-grain`/`static`→`grain`, `fill-up`/`wave-fill`→`tide`,
`invert`/`negative`/`xray`→`polarity`, `louver`/`shutters`→`blinds`,
`shatter`/`explode-in`/`pieces`→`assemble`, `sweep`/`spotlight`→`lantern`,
`iris-blades`/`turbine`→`pinwheel`, `paper`/`fall-in`→`unroll`. No command or
an unknown command: ask ONE question offering the twenty-five; if asking is
impossible, default to `liquid`.

## Foundations — do these for EVERY style

### 1. Read the ENTIRE original SVG source

View the full raw file. For **every** `<path>` record as one unit: complete
`d`, `fill`, **`fill-rule`**, `stroke`, and any render-relevant attribute
(`opacity`, `transform`, `clip-path`). If the file viewer truncates long path
data, re-read with an explicit range or via shell. Never proceed with a
partial or guessed `d` string.

### 2. ⚠️ Preserve `fill-rule` — the #1 silent killer

Letterforms with inner counters/apertures — the cavity inside a Latin `a`,
`o`, `e`, or an Arabic letter like `ص`/`ه` — are drawn as ONE `<path>` whose
`d` contains an outer contour **and** inner sub-paths. The hole only renders
if `fill-rule="evenodd"` (or correctly opposed winding) travels with the path.
**Dropping it defaults browsers to `nonzero`, which fills the holes solid and
silently destroys the letterform.** Whatever non-`d` attributes affect
rendering must travel with the `d` string everywhere it is copied — into
`<defs>`, onto `<use>` elements, everywhere.

### 3. Extract with the bundled script, not by hand

`<skill>` below means the directory holding this SKILL.md — in this repo,
`.qoder/skills/svg-animate`. It is not `~/.qoder/skills/...`, which does not
exist here.

```bash
python3 <skill>/scripts/extract_paths.py logo.svg --lengths
```

Outputs JSON: svg dims/viewBox, then per path its full attribute set plus
`length_total` / `length_longest_subpath`. Use `max_subpath_length` to set
`stroke-dasharray`/`stroke-dashoffset` (must be ≥ the longest single
subpath — every subpath draws completely only if the dash covers the longest).

**Assemble the output file from that JSON rather than hand-copying `d` into the
template.** A wordmark path here is 6,407 characters; retyping or re-flowing one
is exactly how the verbatim-`d` and `fill-rule` guarantees get quietly broken.
Write the animation shell with `d="…"` placeholders and substitute the extracted
strings in a script — which also lets tile, slat, wedge and fragment counts be
computed instead of typed.

## Step 1 — Choose the style

If invoked as `/svg-animate <command>`, the command already chose the style —
use the Commands table directly. Otherwise map the user's words (or an
existing animated reference file they point at):

- "liquid fill", "liquid metal", "chrome reveal", "same animation as <file
  with chrome stroke + rising fill + sheen>" → `chrome-liquid`
- "draw itself", "self-drawing", "draw on", "line by line", "sign itself",
  one-shot intro → `draw-fill`
- "loading", "progress", "loop forever", "draws over and over" → `loading-loop`
- "playful", "bounce in", "elastic", "pop in", "wobble", animated intro loop → `elastic-entrance`
- "rise up", "staggered", "fade in one by one", "cascade" → `rise`
- "iris", "circle reveal", "cinematic reveal", "spotlight" → `iris`
- "neon", "glow sign", "flicker on", "dark stage" → `neon`
- "breathing", "ambient", "idle", "calm loop" → `pulse`
- "flip", "card flip", "3D reveal" → `flip`
- "comet", "energy line", "trace", "light traces the outline" → `comet`
- "rack focus", "defocus", "blur resolves", "soft to sharp", "camera focus" → `focus`
- "tv power on", "crt", "scanlines", "band opens from the middle", "retro screen" → `crt`
- "chromatic aberration", "rgb split", "channel separation", "anaglyph" → `chroma`
- "mosaic", "tiles", "dissolve in", "pixelated reveal", "wave of squares" → `mosaic`
- "ripple", "water", "liquid warp", "refraction", "heat haze" → `ripple`
- "spark", "weld", "torch", "travelling light draws it in" → `spark`
- "emboss", "deboss", "engraved", "letterpress", "blind seal", "raking light" → `engrave`
- "film grain", "noise dissolve", "static resolves", "analog reveal" → `grain`
- "water fills up", "wavy line rises", "tide", "liquid with a meniscus" → `tide`
- "invert", "negative", "x-ray", "polarity flip", "band of inversion" → `polarity`
- "blinds", "shutters", "louver", "slats open" → `blinds`
- "shatter", "pieces fly in", "assemble", "explode-in" → `assemble`
- "lantern", "spotlight sweep", "soft light wanders across" → `lantern`
- "pinwheel", "turbine", "wedges open", "segmented iris" → `pinwheel`
- "unroll", "paper falls into place", "hinged at the top" → `unroll`
- "same as that one" + a file → **replicate that file's exact style
  structure**; re-derive all numbers for the new SVG's size (see scaling
  table). Copy structure and ordering, never literal seconds or pixels.

If the request names no style and no reference, ask ONE question offering the
twenty-five styles; if asking is impossible, default to `chrome-liquid`.

### Mechanics this logo rejects, and why

Four candidates were built, measured, and cut. Record failures here so nobody
re-derives them:

- **`bloom`** (`feMorphology` dilate swell → sharpen). Technically animates —
  `radius` is animatable and it landed exact — but a square dilate kernel closes
  every counter narrower than 2·radius. On this logo the wordmark fuses into one
  blob for most of the beat, and it duplicates `focus`'s "sharpness settles"
  read anyway.
- **`halftone`** (dot-grid mask growing in place). SMIL inside `<pattern>` was
  predicted fragile and actually *does* repaint in Chromium 153 — but a periodic
  mask aperture cannot resolve features smaller than the tile, and this logo's
  thinnest mark is 4.84px. Measured: the 5px bar came back as a row of
  semicircles. Per-tile growth also reads as a dot-thickness change, not a
  spreading reveal. `mosaic` is the same idea at a scale that resolves.
- **`aperture`** (camera iris from rotating blades). Rotating a tiling of the
  plane by a common angle leaves the union unchanged — measured **zero frames of
  change** with full coverage throughout. Blades must change their *own* extent
  to open; `pinwheel` gets the segmented-radial read by scaling wedges instead.
- **`dropshadow`** (offset silhouette that stays). Physically correct, and it
  filled **92 of 111** letterform counters at rest: an offset shadow of a
  letter's stroke falls inside its own hole. A permanent offset shadow is
  incompatible with a logo that has small counters.

## Step 2 — Build per the style's recipe

Open `references/<style>.md` and follow its template. Rules shared by all
styles:

- **One `<path id="...">` def + one pair of `<use>` elements per original
  path.** Scale to the source logo's actual path count and fill colors; never
  assume two paths.
- Name ids by role, e.g. `id="path-<color>"` (`path-white`, `path-blue`,
  `path-teal`).
- The def in `<defs>` carries `fill-rule` and every render-relevant attribute
  from the original path; `<use>` elements inherit them.
- Keep the original `width`/`height`/`viewBox` unchanged.

### Numeric scaling — re-derive, never copy

The reference recipes were tuned on a 1800×1800 hero lettermark. Scale to the
target SVG's own size:

| Parameter | Large (viewBox ≥ 1000) | Medium (500–999) | Small (< 500) |
|---|---|---|---|
| Sequence timings (draw/liquid/fade) | reference values | ×0.7 | ×0.4 |
| Loop durations (sheen/loading/elastic) | reference values | ×0.8 | ×0.6 |
| `stroke-width` (chrome stroke / draw styles) | reference values | ×0.5, min 2 | ×0.3, min 1 |
| `stroke-dasharray/-offset` | ≥ `max_subpath_length` of the target | same | same |
| Sheen `translateX` + rect width | ±2×W / 2×W | same rule | same rule |
| Glow / softness σ (elastic, neon, focus, backlight) | reference | ×0.5 | ×0.25 |
| **σ clamp — all of them** | σ ≤ min(**F**/2, W/120) | same | same |
| **F — smallest feature** | min per-subpath height across the artwork; see below | same | same |
| Filter / mask region | ≥ 3σ of the largest blur, offset or displacement in the filter | same | same |
| **Uniform scale ceiling** | (H/2)/(H/2 − y_max) and the W equivalents — see clearance | same | same |

**Derive F, not just W.** `W/120` alone is not a safe softness: on the 300×110
test logo it gives 2.5px while the thinnest feature is **4.84px**, so any glow
or blur at that size swallows the small marks. Compute F from per-subpath
bounding boxes (`extract_paths.py` already flattens curves; take the smallest
subpath height) and clamp every σ, morphology radius, displacement scale and
tile size against it.

**Check edge clearance before anything expands.** The root `<svg>` clips
(`overflow: hidden`), and artwork usually sits within a few units of the frame
— the test logo reaches x≈296 of 300 and y≈108 of 110. A widening filter
region does **not** help, because the viewport clips after the filter; nor may
you edit `viewBox` (Step 2 rule, and `validate.py` fails). Shrink the effect
instead: on that logo the largest safe uniform scale about the centre is ~1.03,
which is why `focus` carries no scale settle at all.

Also: every number tied to dimensions (translate distances, blur stdDeviation,
rect sizes) derives from THIS svg's width/height — never a magic number from
another logo.

### Style-specific geometry — re-derive per SVG

| Style | Key dimension | Formula |
|---|---|---|
| `rise` | translateY offset | ≈ H/10, clamp 10–80px; stagger 0.12s per path |
| `iris` | clipPath circle final r | 0.55 × √(W²+H²) |
| `neon` | feGaussianBlur stdDeviation | ≈ W/120; dark stage rect `#0a0a12` |
| `pulse` | scale peak | 1.03; loop 4s |
| `flip` | perspective | ≈ 1.5×W px |
| `comet` | dasharray pattern | C = 0.15 × max_subpath, G = remainder |
| `focus` | start softness | σ = min(F/2, W/120) → `blur(σ)`; re-blur 0.5σ at ~80%; **no scale** |
| `crt` | clip band / scan pitch | `inset(50% 0)`→`inset(0)`; hot line `h = max(1.5, H/73)`; pitch 4, stripe ≥1.5 |
| `chroma` | channel offset | ±W/85 (≈3px here), horizontal only; 3 single-channel ghosts per path; converge at 70% |
| `mosaic` | tile / stagger | tile ≈ W/15 and ≥ 4F; `begin` = 0.7·x + 0.15·y + ≤0.12 jitter; per-tile dur ≈ 0.25 × total |
| `ripple` | displacement | `scale` peaks ~F (recovering to 0), `baseFrequency` ≈ 1/(H/2.2), 1 octave |
| `spark` | motion + bulge | reveal accumulates in a mask rect; spark radius ≈ r/6 of a H/4 mask bulge |
| `engrave` | relief | blur `stdDeviation` ≈ F/2, `surfaceScale` 2–4, azimuth sweep ≈ 180°, `elevation` 35–45 |
| `grain` | grain + threshold | `baseFrequency` ≈ 0.9, 2 octaves; `tableValues` must end `1 1` to land exact |
| `tide` | wave | amplitude ≈ H/12, one wavelength across W, identical command sequence per stop |
| `polarity` | band | width ≈ W/2.3; end offset must clear the canvas (W + band) or inversion survives |
| `blinds` | slats | count ≈ H/10, `slat_h = H / count` exactly, and each slat ≥ 4F tall |
| `assemble` | fragments | ~8 pieces; `dx` ±0.55W, `dy` ±1.1H, rotate ±8°, stagger ~0.09s, `both` fill |
| `lantern` | gradient | `cx` 0.04→1.0 while `r` stays ~0.3, then `r`→≥2.0 in the last ~28% |
| `pinwheel` | wedges | 6–12 wedges; R ≥ (max corner distance)/cos(θ/2); stagger ~0.075s; `transform-box: view-box` |
| `unroll` | hinge | `transform-origin` on the top edge, `perspective(1.4·W)`, start `rotateX(-88deg)` |

### Rules the new styles had to learn the hard way

- **An XML comment may not contain `--`, anywhere.** Using two hyphens as a
  dash inside `<!-- … -->` makes the whole file fail to parse, and the error
  points at a column in the comment rather than at the idea. This repo hit it
  while writing `lantern`. Use a single hyphen, an em-dash, or restructure.
- **A reveal must accumulate.** A moving light, spotlight or spark with no
  growing mask behind it animates perfectly and ends almost empty — measured at
  1% of the artwork visible. Whatever travels, pair it with something that
  stays.
- **Check that the end state actually lands.** "It animates" is half the test;
  sample the final frame against the source. A gradient that stops growing too
  early, or a mask that parks off-edge, moves beautifully and reveals nothing.

- **Decorative geometry is `<rect>`/`<circle>`/`<polygon>`, never `<path>`.**
  Keeps the `<path>` count equal to the source, so Step 3's count check stays
  meaningful.
- **`color-interpolation-filters="sRGB"` on every `<filter>`.** The default is
  `linearRGB`; for displacement maps it produces a systematic offset and dulls
  colours. None of the older glow recipes (`neon`, `elastic-entrance`, `pulse`)
  set it — treat those as legacy on this point, and do not copy the omission.
- **A `<mask>` child is never the artwork.** Masks key on luminance, so a
  `<use>` of near-black artwork inside a mask hides everything. Masks are
  black-and-white drawings of *where*; `fill="#fff"` the reveal geometry.
- **`animation` is a shorthand and replaces the whole list.** Declaring a fade
  on one class and a move on a later class means the later rule wins outright
  and the fade silently never runs (`chroma` shipped with this bug). Any
  element needing two animations lists both in one declaration.
- **CSS cannot animate filter primitive attributes.** `stdDeviation`,
  `baseFrequency`, `radius`, `scale` take SMIL `<animate>` only, and
  number-*list* values interpolate only between same-cardinality stops
  (`"0.02;0.005"` yes, `"0.02;0.014 0.005"` no).
- **`clip-path: inset(… view-box)` does not interpolate in Chromium** — the
  animation runs and the frame never changes. Use bare `inset()`, and know that
  percentages then resolve against the element's **object bounding box**, not
  the canvas.
- **Avoid a trailing `;` in `keyTimes`/`values`.** Reported to kill SMIL
  silently in some Chromium builds. Chromium 153 here tolerates it, so this is
  cheap insurance, not a measured blocker — but the failure mode is silent.
- **No JS and no `:hover` in the asset.** These files ship as standalone
  images; the review harness embeds them through `<img>`, where scripts and
  pointer events do not exist.
- **`prefers-reduced-motion` works inlined, not through `<img>`.** Measured:
  inlined, the query flips a variant from mid-beat to resting; embedded as an
  image, Chromium does not propagate the setting and both animate. Add the
  block anyway — it is free and helps the inline and object cases — but never
  claim it protects an `<img>` usage. For SMIL-driven styles the escape hatch
  is that a CSS property outranks its presentation attribute: `filter: none`
  and `mask: none` disable `ripple` and `mosaic` outright.

## Step 3 — Validate

```bash
python3 <skill>/scripts/validate.py original.svg output.svg
```

Checks well-formedness, verbatim `d` preservation, fill-rule counts, fill
colors, and unchanged viewBox. Then manually confirm:

- Path **def** count in the output == path count in the original (extra
  `<path>` copies are what to look for; decorative geometry should be
  rect/circle/polygon). Note that `neon` and `comet` intentionally repeat each
  path inline rather than using defs — the rule is about *dropping* attributes,
  not about a strict equality.
- Each def carries every render-relevant attribute the original had, not just `d`.
- Timings/dimensions follow the scaling table for this SVG's size.

How the checks actually behave, so a PASS is not over-read:

- `d` preservation is a **substring** test — one verbatim copy in `<defs>`
  satisfies it no matter how many `<use>` elements reference it.
- `fill-rule` is a **floor** (`count in output ≥ count in source`), so adding
  copies can never fail it. It catches loss, not duplication.
- Fill colours are harvested **from the original only** and then substring
  searched in the output. Moving them into CSS classes is fine; a style that
  *replaces* a colour outright fails, and channel-split colours written as
  `rgb(...)` do not count as carrying the hex — the solid landing layer must.
- It proves nothing about motion. **A green `validate.py` says the file is a
  faithful static; it cannot see an animation that never starts**, which is the
  most common failure of all. Render it: open the file, or load it through an
  `<img>` and confirm the frame actually changes.

## Step 4 — Theme / color-only variants

For a "dark mode" or other color-only variant of an already-animated logo
with identical geometry:

1. `diff` the two static sources first — confirm only colors differ.
2. Targeted find/replace of just the changed color in the already-correct
   animated SVG — do not regenerate from scratch (regeneration risks
   re-losing `fill-rule` and other attributes).

```bash
diff original_light.svg original_dark.svg
sed 's/fill: #OLDCOLOR;/fill: #NEWCOLOR;/' animated_light.svg > animated_dark.svg
python3 <skill>/scripts/validate.py original_dark.svg animated_dark.svg
```

### Dark-stage legibility: the order of resort

A dark background can swallow the artwork — the test logo's navy `#040c24`
against `#0a0a12` is a ~1.05:1 contrast ratio, effectively invisible. Fix it in
this order, never by silently overriding a colour in the animation:

1. **Backlight halo.** A white `<use>` of the paths drawn *behind* the artwork,
   blurred and at low opacity, so the navy reads as a silhouette over its own
   glow. Keeps every original colour, passes `validate.py`, and works for
   fill-based styles. It does **not** combine with `screen` blending — screen
   against white is white — so `chroma` cannot use it.
2. **A colour variant, per Step 4.** Make the lightened *source* first, animate
   that, and validate the result against its own source. `validate.py` is
   relative to whichever original you pass, so this is the sanctioned way to
   change a colour.
3. **Never** an inline `fill` override in the animated file. It fails the colour
   check and hides which source the file belongs to.

`neon` accepts the dim read as-is; that is a per-style judgement, recorded in
its recipe, not a general licence.

## Delivering

Present the output file(s) to the user for review — do not paste large SVG
source into chat. SVGs with SMIL/CSS animation can be opened directly in any
browser.

Reviewing more than one style at a time? Ship a single dependency-free
`index.html` **beside** the files (so `src="focus.svg"` resolves) with one card
per variant, each embedding the real file through an `<img>`. That choice is the
point: `<img>` runs CSS animations and SMIL but blocks JS, pointer events and
outbound references, so a variant that secretly needs to be inlined shows up as
a still. Add a per-card Replay (bust the cache with `src = name + '?r=' + ++n`,
which restarts both clocks), a light/dark/checkerboard stage switch — the
checkerboard exposes a wrongly-baked opaque rect as a hard edge — and a zoom
control, because a 300px logo's 5px details are unjudgeable at 1×.
`test-svgs/animated/index.html` is a worked example.

## Checklist

- [ ] Viewed the complete original source (not truncated)
- [ ] Extracted `d` **and** `fill-rule` (and other render-relevant attrs) per path, via the script
- [ ] Chose the style from the user's words or a referenced file
- [ ] Every `<path id="...">` def carries the same `fill-rule` as its original path
- [ ] Path count, colors, and viewBox match the original
- [ ] Dash values ≥ the target's longest subpath; timings/dimensions scaled per the table
- [ ] **F derived** from per-subpath boxes, and every σ / radius / scale / tile clamped against it
- [ ] **Edge clearance checked** — nothing expands past the viewport, which clips after the filter
- [ ] Every `<filter>` region clears its own blur/offset, with `color-interpolation-filters="sRGB"`
- [ ] Decorative geometry is rect/circle/polygon — no extra `<path>` elements
- [ ] Mask contents are explicitly white; nothing animated by SMIL and CSS on the same property
- [ ] Any element with two animations declares both in one `animation` shorthand
- [ ] `prefers-reduced-motion` block present, with the `<img>` limitation understood, not claimed away
- [ ] `validate.py` passes **and the motion was actually watched** — a green validator never sees a dead animation
- [ ] Output presented as a file (plus `index.html` beside it when reviewing several)
