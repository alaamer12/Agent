# Reference matching

Goal: a vector drawing that a person would accept as "the same character" next to the reference, reached by measuring and comparing instead of guessing.

## Contents

1. Triage the reference
2. Measure
3. Draw
4. Render and compare loop
5. Stop criteria
6. Pitfalls

## 1. Triage the reference

- Identify the character region and the frame it sits in (circle, square, none). Everything else in the image is out of scope: interface icons, badges, buttons, captions, page background beyond the avatar frame.
- Several references (angles, expressions) mean one rig with the frontal view first; ask before building more views.
- Note the resolution. Small references hide detail; do not invent detail the reference cannot support, and say so in the report.

## 2. Measure

```bash
python scripts/inspect_ref.py ref.png --box x0,y0,x1,y1 --zoom 8 --grid 10 --sample 130,40 --palette 6 --out ref_zoom.png
```

- Read feature positions from the labelled grid (original pixel coordinates). Record: silhouette edges of hair, face, ears, neck, shoulders; eye, brow, nose and mouth positions; the frame circle or rectangle.
- Take colours from `--sample` and `--palette`, not by eye. Assign them to palette names (skin, skin-shade, hair, shirt, ...), because the rig recolours through those names.
- Note asymmetries (head tilt, off-centre mouth). Keep them in the default parts; they are part of the likeness.

## 3. Draw

- Use `viewBox="x0 y0 w h"` equal to the crop box. Coordinates measured above then need no conversion.
- Paint back to front: backdrop, back hair, body, neck, ears, head, nose, mouth, eyes, brows, front hair. This is the same order the rig uses later, which keeps step 2 of the workflow cheap.
- Block in large shapes first (silhouette, hair mass, face, shirt), then features, then shading. Use plain paths with a few curves; avoid filters and blurs that a later part could not reproduce consistently.

## 4. Render and compare loop

```bash
python scripts/render.py draft.svg draft.png --size 600 --scale 2
python scripts/compare.py ref.png draft.png --ref-box x0,y0,x1,y1 --ignore <out-of-scope box> --out compare.png
```
Open `compare.png` (reference | render | blend | difference) and read the printed worst regions. Fix in this order, because earlier items dominate perceived likeness:
1. Silhouette and proportions (head size, jaw, hair volume, shoulder width)
2. Feature placement and size (eyes, brows, nose, mouth)
3. Colours
4. Shape character (hair outline, ear shape, smile shape)
5. Fine detail and shading

Fix the worst three or four items per round, then re-render. Compare scores across rounds as a trend; absolute values depend on how painterly the reference is.

## 5. Stop criteria

Stop when either holds:
- At 100% zoom no discrepancy stands out in the blend panel, or
- Two consecutive rounds improve the score by almost nothing. Report what still differs (typically texture, soft shading, outline weight) instead of looping further.

## 6. Pitfalls

- A render that shows only part of the drawing: the viewport is smaller than the content. Size the render to the whole drawing (`--size`).
- A tiny reference makes every difference look large. Compare crops, not the whole image, and exclude out-of-scope regions with `--ignore`.
- Do not paint out-of-scope elements "to match the reference". They are not part of the character.
- Hold the palette in one place so a colour fix is one edit.
