---
name: svg-animate
description: "Animate a static, flat SVG logo or icon (solid-fill <path> elements) with one of ten animation styles: chrome-liquid (chrome outline draws, liquid rising fill, sheen sweep), draw-fill (outline draws itself then fill fades in), loading-loop (outline draws/reverses forever), elastic-entrance (elastic bounce, wobble, glow), rise (staggered rise-and-fade), iris (circular clip reveal), neon (neon-sign flicker-on with glow), pulse (calm breathing scale + glow), flip (3D card-flip reveal), comet (bright dash traces the outlines forever). Trigger when the user asks to animate a logo/SVG, names any of these effects, wants an existing treatment replicated on a new file, or needs light/dark theme variants. Always preserves fill-rule=evenodd so letterform holes (Arabic ص/ه, Latin a/o/e) never fill in solid."
argument-hint: "<style> <file.svg>  (style: liquid|draw|load|elastic|rise|iris|neon|pulse|flip|comet)"
---

# SVG Logo Animation Meta-Skill

Turns a static SVG (flat `<path>` elements with solid fills) into an animated
version using one of **ten animation styles**. The foundations below apply to
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

Aliases: `chrome`/`chrome-liquid`→`liquid`, `draw-fill`→`draw`,
`loading`/`loading-loop`→`load`. No command or an unknown command: ask ONE
question offering the ten; if asking is impossible, default to `liquid`.

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

```bash
python3 ~/.qoder/skills/svg-animate/scripts/extract_paths.py logo.svg --lengths
```

Outputs JSON: svg dims/viewBox, then per path its full attribute set plus
`length_total` / `length_longest_subpath`. Use `max_subpath_length` to set
`stroke-dasharray`/`stroke-dashoffset` (must be ≥ the longest single
subpath — every subpath draws completely only if the dash covers the longest).

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
- "same as that one" + a file → **replicate that file's exact style
  structure**; re-derive all numbers for the new SVG's size (see scaling
  table). Copy structure and ordering, never literal seconds or pixels.

If the request names no style and no reference, ask ONE question offering the
ten styles; if asking is impossible, default to `chrome-liquid`.

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
| Glow blur (elastic) | reference | ×0.5 | ×0.25 |

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

## Step 3 — Validate

```bash
python3 ~/.qoder/skills/svg-animate/scripts/validate.py original.svg output.svg
```

Checks well-formedness, verbatim `d` preservation, fill-rule counts, fill
colors, and unchanged viewBox. Then manually confirm:

- Path def count in the output == path count in the original.
- Each def carries every render-relevant attribute the original had, not just `d`.
- Timings/dimensions follow the scaling table for this SVG's size.

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
python3 ~/.qoder/skills/svg-animate/scripts/validate.py original_dark.svg animated_dark.svg
```

## Delivering

Present the output file(s) to the user for review — do not paste large SVG
source into chat. SVGs with SMIL/CSS animation can be opened directly in any
browser.

## Checklist

- [ ] Viewed the complete original source (not truncated)
- [ ] Extracted `d` **and** `fill-rule` (and other render-relevant attrs) per path, via the script
- [ ] Chose the style from the user's words or a referenced file
- [ ] Every `<path id="...">` def carries the same `fill-rule` as its original path
- [ ] Path count, colors, and viewBox match the original
- [ ] Dash values ≥ the target's longest subpath; timings/dimensions scaled per the table
- [ ] `validate.py` passes; output presented as a file
