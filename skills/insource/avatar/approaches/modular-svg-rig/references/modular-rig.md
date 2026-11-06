# Modular rig

How to turn one matched drawing into a rig whose parts swap independently.

## Contents

1. Concepts
2. rig.json
3. Layer order
4. Slot ownership
5. Anchors and envelopes
6. Decomposition parity
7. Extending the rig

## 1. Concepts

- **Slot**: a named region of the character (hair, nose, mouth, neck, ...). Holds exactly one part.
- **Part** (variant): one SVG file `parts/<slot>/<id>.svg` containing `<g data-layer="...">` groups, optional `<defs>`.
- **Layer**: a z-order band shared by all slots. A slot may paint only the layers it lists.
- **Envelope**: the box `[x0, y0, x1, y1]` a slot may change. Swapping that slot must alter no pixel outside it.
- **Default combination**: the parts in `rig.json` `default`; it reproduces the matched drawing.

## 2. rig.json

See `assets/rig-template/rig.json` for a complete file.

| Key              | Meaning                                                                                    |
| ---------------- | ------------------------------------------------------------------------------------------ |
| `viewBox`        | The one coordinate system all parts use                                                    |
| `frame`          | Optional clip (`circle`) applied to everything, backdrop included                          |
| `palette`        | Colour name to value; parts reference `var(--name)`                                        |
| `layers`         | Bottom-to-top order                                                                        |
| `slots`          | Per slot: `layers` it owns, `envelope`, `backdrop: true` for the backdrop slot             |
| `default`        | The default part id per slot                                                               |
| `interacts`      | Slot pairs that touch or overlap; drives combination sampling                              |
| `max_components` | Optional; connected pieces the silhouette may have (default 1)                             |
| `anchors`        | Informational landmarks (eye line, chin, neck port, shoulder line) authors measure against |

## 3. Layer order

Typical bottom-to-top: backdrop, back hair, torso, neck, ears, head, nose, mouth, eyes, brows, front hair.
- Ears sit **behind** the head and overlap it, so they never need to match the head's outline.
- The neck sits **over** the torso and **under** the head: the chin hides its top, and its lower edge forms the neckline over the clothing. The neck slot therefore owns the neckline; torso variants stay plain shoulders. This is what lets any neck fit any torso.
- Hair is split in two: back hair (behind head and torso) and front hair (over everything). Short styles use only the front layer.
- Features (nose, mouth, eyes, brows) lie on the head and must stay inside the head outline for every head variant. Cheek colour belongs to the head part so it cannot leak.

## 4. Slot ownership

Each region of the drawing belongs to exactly one slot. A shape that spans two regions (a collar around the neck, hair curling over an ear) is split at the layer boundary, with each half overlapping the other. If two slots cannot be made independent, merge them into one slot and say so.

## 5. Anchors and envelopes

- Measure anchors once from the matched drawing and write them in `rig.json`. Every part is authored against the same anchors.
- Size an envelope to the largest region any reasonable variant of that slot could occupy (long hair reaches the shoulders; a nose does not reach the brows). Too tight and good parts fail isolation; too loose and leaks go unnoticed.

## 6. Decomposition parity

After splitting, render the default combination and compare it to the render from before the split:
```bash
python scripts/assemble.py <rig> -o default.svg
python scripts/render.py default.svg default.png --scale 2
python scripts/compare.py pre_split.png default.png --out parity.png
```
Expect MAE near 0. A visible difference means a shape was cut wrongly, a layer is out of order, or a colour changed name. Fix before authoring variants, because every variant inherits the error.

## 7. Extending the rig

Add a slot (eyebrows, glasses, earrings, facial hair, hat) by: choosing layers (add one to `layers` if needed), adding the slot with an envelope, creating a default part (an "empty" part is allowed for optional items), and listing it in `interacts` with the slots it touches.
