---
id: template
name: Scene reference template
family: template
renderer: template
poster: assets/posters/<id>.jpg
complexity: S
source_lines: 0
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Scene reference template

Copy this file to `scenes/<id>.md` and fill every section. `flow-field.md` is the
reference implementation of this template — match its density and specificity.
Lint (`scripts/lint.mjs`) enforces the headings, order, and the no-code rule.

## Authoring rules

1. **No code.** No fenced blocks. No GLSL, JS, TS, or Vue source. Formulas are
   allowed as inline or display math, but every symbol must be defined in the
   same sentence or the line below.
2. **Exact numbers.** Never round, never write "about". `2.6` stays `2.6`,
   `0.035` stays `0.035`. If a value is derived, give the formula and the
   evaluated value at 640x400 and at 1920x1080.
3. **Name the noise.** "2D simplex, gradient-noise variant returning -1..1" —
   not "noise". Same for easing, palettes, projections, and blend modes.
4. **Units.** Time in seconds, space in CSS pixels, angles in radians (say so),
   speeds in px/s at 60 fps. Pixel quantities are device-independent.
5. **Frame anatomy owns render state.** Clear color, canvas alpha, blend,
   depth/cull, layer order, and the effective backdrop all live in section 3.
6. **The reader cannot see the code.** If the effect depends on a quirk — an
   odd constant, an unseeded RNG, a precision choice, a warmup, a host gradient
   showing through — say it explicitly.
7. **Length caps.** Stay within the per-section ranges. If a section overflows,
   move shared material to the family doc, not into another scene doc.

## Frontmatter

Keep all keys. `family` must match `references/families/<family>-*.md`, `renderer`
is one of `canvas2d`, `webgl1`, `three`, `complexity` is one of `S`, `M`, `L`,
`XL`, `dpr_max` is the numeric device-pixel-ratio clamp (or `null` if uncapped),
and `poster_capture` records how the poster was made so a comparison run can
reproduce it.

## 1. Identity

One sentence. What the viewer sees, with the subject and the dominant motion.
No adjectives that do not survive a screenshot.

## 2. Perceived look

Texture (smooth, grainy, banded, faceted), density (sparse, layered, full-bleed),
edge quality (crisp, soft, glowing, aliased), contrast, focal point or lack of
one, and what the frame looks like at t = 3 s. 50–80 words.

## 3. Frame anatomy

Numbered back-to-front layers. For each: what geometry draws it, its blend mode,
opacity, depth test and cull state, and its clear or fill color. State canvas
alpha and whether a host backdrop shows through. 80–120 words.

## 4. Motion law

What moves and by what law. Give periods or frequencies in seconds, speeds in
px/s at 60 fps, phase at t = 0, particle lifetimes, respawn rules, and whether
the motion loops or runs open-ended. Note anything that is time-accumulated
rather than periodic. 80–120 words.

## 5. Technique and math

The core. Sampling domain, coordinate normalization, iteration or integration
scheme with step counts, noise type and octave count, projection, and the color
composition rule. Formulas may use inline notation with defined symbols.
180–300 words.

## 6. Parameters

A markdown table with columns: `name | value | range | effect | sensitivity`.
Include every look-affecting literal from the scene's config, 10–18 rows. Range
is the span that still looks like the same effect; sensitivity is H/M/L.

## 7. Palette and color

Stops as hex plus HSL where discoverable, alpha ramps, blend behavior, gamma or
tonemapping, and whether values are authored in display or linear space. For
procedural palettes give the formula and the hue/saturation/lightness ranges.
60–100 words.

## 8. Composition and camera

Frame occupancy, horizon or center placement, FOV or orthographic scale, aspect
behavior, safe margins, and what happens at very wide or very tall aspect
ratios. 60–90 words.

## 9. Randomness and seeds

RNG kind and seed, or the explicit statement "any seed, same distribution".
Distributions for each randomized quantity, and the warmup or priming count that
advances state before the first visible frame. 40–70 words.

## 10. Performance budget

Counts (particles, vertices, segments, draw calls), fill-rate notes, DPR clamp,
measured FPS class, and the ordered list of what to cut first. 50–80 words.

## 11. Host integration

Mount order, resize semantics, teardown, any deviation from the standard host
contract, and external assets. 50–90 words.

## 12. Failure modes and tells

Five to eight bullets in the form **symptom → cause → fix**. These are the
highest-value lines in the document; derive them from the effect's actual
sensitivities, not from generic advice. 70–110 words.

## 13. Tuning knobs

Three to six knobs in the order you would try them, with direction of change and
safe range. 30–50 words.

## 14. Verification checklist

Observable assertions an agent or a screenshot can check: coverage percentage,
dominant hue band, motion period, absence of clipping, flicker, or banding, and
how to compare against the poster. 40–70 words.

## 15. Porting notes

Only non-obvious deltas for a non-original framework: color management, filter
support, math-library substitutes, precision. Omit the section body if there is
nothing to say. 0–60 words.
