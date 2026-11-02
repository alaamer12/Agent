# SVG Build Foundations

> The single home of every rule shared by all 25 styles. Read this **top to bottom, once, for any build
> job**, then read your one recipe `references/<style>.md`. Style identification and routing live in
> [`../SKILL.md`](../SKILL.md); each recipe is the sole home of its own geometry numbers — this file never
> repeats them.

## 1. Read the ENTIRE original SVG source

View the full raw file. For **every** `<path>` record as one unit: complete `d`, `fill`, **`fill-rule`**,
`stroke`, and any render-relevant attribute (`opacity`, `transform`, `clip-path`). If the file viewer
truncates long path data, re-read with an explicit range or via shell. Never proceed with a partial or
guessed `d` string.

## 2. Preserve `fill-rule` — the #1 silent killer

Letterforms with inner counters/apertures — the cavity inside a Latin `a`, `o`, `e`, or an Arabic letter
like `ص`/`ه` — are drawn as ONE `<path>` whose `d` contains an outer contour **and** inner sub-paths. The
hole only renders if `fill-rule="evenodd"` (or correctly opposed winding) travels with the path. **Dropping
it defaults browsers to `nonzero`, which fills the holes solid and silently destroys the letterform.**
Whatever non-`d` attributes affect rendering must travel with the `d` string everywhere it is copied —
into `<defs>`, onto `<use>` elements, everywhere.

## 3. Extract with the bundled script, not by hand

`<skill>` below means the directory holding the svg `SKILL.md` — in this repo, `skills/insource/animation/svg`.
It is not `~/.qoder/skills/...`, which does not exist here.

```bash
python <skill>/scripts/extract_paths.py logo.svg --lengths
```

Outputs JSON: svg dims/viewBox, then per path its full attribute set plus `length_total` /
`length_longest_subpath`. Use `max_subpath_length` to set `stroke-dasharray`/`stroke-dashoffset` (must be
≥ the longest single subpath — every subpath draws completely only if the dash covers the longest).

**Assemble the output file from that JSON rather than hand-copying `d` into the template.** A wordmark
path here is 6,407 characters; retyping or re-flowing one is exactly how the verbatim-`d` and `fill-rule`
guarantees get quietly broken. Write the animation shell with `d="…"` placeholders and substitute the
extracted strings in a script — which also lets tile, slat, wedge and fragment counts be computed instead
of typed.

## 4. Structural rules for every output file

- **One `<path id="...">` def + one pair of `<use>` elements per original path.** Scale to the source
  logo's actual path count and fill colors; never assume two paths. (`neon` and `comet` intentionally
  repeat each path inline rather than using defs — the rule that matters is *never dropping attributes*,
  not strict count equality.)
- Name ids by role, e.g. `id="path-<color>"` (`path-white`, `path-blue`, `path-teal`).
- The def in `<defs>` carries `fill-rule` and every render-relevant attribute from the original path;
  `<use>` elements inherit them.
- Keep the original `width`/`height`/`viewBox` unchanged.
- **Decorative geometry is `<rect>`/`<circle>`/`<polygon>`, never `<path>`.** Keeps the `<path>` count
  equal to the source, so the Validate count check stays meaningful.

## 5. Numeric scaling — re-derive, never copy

The reference recipes were tuned on a 1800×1800 hero lettermark. Scale to the target SVG's own size:

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

**Derive F, not just W.** `W/120` alone is not a safe softness: on the 300×110 test logo it gives 2.5px
while the thinnest feature is **4.84px**, so any glow or blur at that size swallows the small marks.
Compute F from per-subpath bounding boxes (`extract_paths.py` already flattens curves; take the smallest
subpath height) and clamp every σ, morphology radius, displacement scale and tile size against it.

**Check edge clearance before anything expands.** The root `<svg>` clips (`overflow: hidden`), and artwork
usually sits within a few units of the frame — the test logo reaches x≈296 of 300 and y≈108 of 110. A
widening filter region does **not** help, because the viewport clips after the filter; nor may you edit
`viewBox` (structural rule above, and `validate.py` fails). Shrink the effect instead: on that logo the
largest safe uniform scale about the centre is ~1.03. Every number tied to dimensions (translate
distances, blur stdDeviation, rect sizes) derives from THIS svg's width/height — never a magic number
from another logo.

## 6. Hard rules — each was learned from a measured failure

- **An XML comment may not contain `--`, anywhere.** Using two hyphens as a dash inside `<!-- … -->`
  makes the whole file fail to parse, and the error points at a column in the comment rather than at the
  idea. Hit while writing `lantern`. Use a single hyphen, an em-dash, or restructure.
- **A reveal must accumulate.** A moving light, spotlight or spark with no growing mask behind it
  animates perfectly and ends almost empty — measured at 1% of the artwork visible. Whatever travels,
  pair it with something that stays.
- **Check that the end state actually lands.** "It animates" is half the test; sample the final frame
  against the source. A gradient that stops growing too early, or a mask that parks off-edge, moves
  beautifully and reveals nothing.
- **`color-interpolation-filters="sRGB"` on every `<filter>`.** The default is `linearRGB`; for
  displacement maps it produces a systematic offset and dulls colours. None of the older glow recipes
  (`neon`, `elastic-entrance`, `pulse`) set it — treat those as legacy on this point, and do not copy
  the omission.
- **A `<mask>` child is never the artwork.** Masks key on luminance, so a `<use>` of near-black artwork
  inside a mask hides everything. Masks are black-and-white drawings of *where*; `fill="#fff"` the
  reveal geometry.
- **`animation` is a shorthand and replaces the whole list.** Declaring a fade on one class and a move
  on a later class means the later rule wins outright and the fade silently never runs (`chroma` shipped
  with this bug). Any element needing two animations lists both in one declaration.
- **CSS cannot animate filter primitive attributes.** `stdDeviation`, `baseFrequency`, `radius`, `scale`
  take SMIL `<animate>` only, and number-*list* values interpolate only between same-cardinality stops
  (`"0.02;0.005"` yes, `"0.014 0.005;0.02"` no).
- **`clip-path: inset(… view-box)` does not interpolate in Chromium** — the animation runs and the frame
  never changes. Use bare `inset()`, and know that percentages then resolve against the element's
  **object bounding box**, not the canvas.
- **Avoid a trailing `;` in `keyTimes`/`values`.** Reported to kill SMIL silently in some Chromium
  builds. Chromium 153 here tolerates it, so this is cheap insurance, not a measured blocker — but the
  failure mode is silent.
- **No JS and no `:hover` in the asset.** These files ship as standalone images; the review harness
  embeds them through `<img>`, where scripts and pointer events do not exist.
- **`prefers-reduced-motion` works inlined, not through `<img>`.** Measured: inlined, the query flips a
  variant from mid-beat to resting; embedded as an image, Chromium does not propagate the setting and
  both animate. Add the block anyway — it is free and helps the inline and object cases — but never
  claim it protects an `<img>` usage. For SMIL-driven styles the escape hatch is that a CSS property
  outranks its presentation attribute: `filter: none` and `mask: none` disable `ripple` and `mosaic`
  outright.
- **Every recipe was verified in Chromium 153 only**, and each recipe's reduced-motion block disables
  the properties *that style* actually uses (`mask:none`, `filter:none`, `animation:none`, …) — keep the
  recipe's block, don't swap in a generic one. Re-render before trusting any change.

## 7. Validate

```bash
python <skill>/scripts/validate.py original.svg output.svg
```

Checks well-formedness, verbatim `d` preservation, fill-rule counts, fill colors, and unchanged viewBox.
Then manually confirm:

- Path **def** count in the output == path count in the original (extra `<path>` copies are what to look
  for; decorative geometry should be rect/circle/polygon).
- Each def carries every render-relevant attribute the original had, not just `d`.
- Timings/dimensions follow the scaling table for this SVG's size.

How the checks actually behave, so a PASS is not over-read:

- `d` preservation is a **substring** test — one verbatim copy in `<defs>` satisfies it no matter how
  many `<use>` elements reference it.
- `fill-rule` is a **floor** (`count in output ≥ count in source`), so adding copies can never fail it.
  It catches loss, not duplication.
- Fill colours are harvested **from the original only** and then substring searched in the output.
  Moving them into CSS classes is fine; a style that *replaces* a colour outright fails, and
  channel-split colours written as `rgb(...)` do not count as carrying the hex — the solid landing
  layer must.
- It proves nothing about motion. **A green `validate.py` says the file is a faithful static; it cannot
  see an animation that never starts**, which is the most common failure of all. Render it: open the
  file, or load it through an `<img>` and confirm the frame actually changes.

## 8. Theme / color-only variants

For a "dark mode" or other color-only variant of an already-animated logo with identical geometry —
**this section alone is enough for a variant job; you do not need a recipe re-read:**

1. `diff` the two static sources first — confirm only colors differ.
2. Targeted find/replace of just the changed color in the already-correct animated SVG — do not
   regenerate from scratch (regeneration risks re-losing `fill-rule` and other attributes).

```bash
diff original_light.svg original_dark.svg
sed 's/fill: #OLDCOLOR;/fill: #NEWCOLOR;/' animated_light.svg > animated_dark.svg
python <skill>/scripts/validate.py original_dark.svg animated_dark.svg
```

### Dark-stage legibility: the order of resort

A dark background can swallow the artwork — the test logo's navy `#040c24` against `#0a0a12` is a
~1.05:1 contrast ratio, effectively invisible. Fix it in this order, never by silently overriding a
colour in the animation:

1. **Backlight halo.** A white `<use>` of the paths drawn *behind* the artwork, blurred and at low
   opacity, so the navy reads as a silhouette over its own glow. Keeps every original colour, passes
   `validate.py`, and works for fill-based styles. It does **not** combine with `screen` blending —
   screen against white is white — so `chroma` cannot use it.
2. **A colour variant, per this section.** Make the lightened *source* first, animate that, and
   validate the result against its own source. `validate.py` is relative to whichever original you
   pass, so this is the sanctioned way to change a colour.
3. **Never** an inline `fill` override in the animated file. It fails the colour check and hides which
   source the file belongs to.

`neon` accepts the dim read as-is; that is a per-style judgement, recorded in its recipe, not a general
licence.

## 9. Delivering

Present the output file(s) to the user for review — do not paste large SVG source into chat. SVGs with
SMIL/CSS animation can be opened directly in any browser.

Reviewing more than one style at a time? Ship a single dependency-free `index.html` **beside** the
files (so `src="focus.svg"` resolves) with one card per variant, each embedding the real file through an
`<img>`. That choice is the point: `<img>` runs CSS animations and SMIL but blocks JS, pointer events
and outbound references, so a variant that secretly needs to be inlined shows up as a still. Add a
per-card Replay (bust the cache with `src = name + '?r=' + ++n`, which restarts both clocks), a
light/dark/checkerboard stage switch — the checkerboard exposes a wrongly-baked opaque rect as a hard
edge — and a zoom control, because a 300px logo's 5px details are unjudgeable at 1×.
`test-svgs/animated/index.html` is a worked example.

## Checklist

- [ ] Viewed the complete original source (not truncated)
- [ ] Extracted `d` **and** `fill-rule` (and other render-relevant attrs) per path, via the script
- [ ] Style chosen from the router table or the recipe the command named
- [ ] Every `<path id="...">` def carries the same `fill-rule` as its original path
- [ ] Path count, colors, and viewBox match the original
- [ ] Dash values ≥ the target's longest subpath; timings/dimensions scaled per §5
- [ ] **F derived** from per-subpath boxes, and every σ / radius / scale / tile clamped against it
- [ ] **Edge clearance checked** — nothing expands past the viewport, which clips after the filter
- [ ] Every `<filter>` region clears its own blur/offset, with `color-interpolation-filters="sRGB"`
- [ ] Decorative geometry is rect/circle/polygon — no extra `<path>` elements
- [ ] Mask contents are explicitly white; nothing animated by SMIL and CSS on the same property
- [ ] Any element with two animations declares both in one `animation` shorthand
- [ ] `prefers-reduced-motion` block present per the recipe, with the `<img>` limitation understood, not claimed away
- [ ] `validate.py` passes **and the motion was actually watched** — a green validator never sees a dead animation
- [ ] Output presented as a file (plus `index.html` beside it when reviewing several)
