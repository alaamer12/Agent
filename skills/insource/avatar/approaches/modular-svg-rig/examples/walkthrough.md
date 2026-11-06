# Worked example

A complete pass through the five phases. Command output is copied from a real run against `assets/rig-template`.

## Request

"Recreate the portrait in this screenshot as a modular avatar and give me 4 hairstyles, 3 noses, 3 mouths and 3 necks. The screenshot also contains a badge icon and a settings icon."

## 1. Match

Triage: the character sits in a circular frame; the badge and settings icon are out of scope and are neither drawn nor scored.

```bash
python scripts/inspect_ref.py ref.png --box 95,15,195,100 --zoom 8 --grid 10 --palette 6 --out ref_zoom.png
python scripts/render.py draft.svg draft.png --size 600 --scale 2
python scripts/compare.py ref.png draft.png --ref-box 95,15,195,100 --ignore 160,70,190,100 --out compare.png
```
Typical rounds: (1) proportions and silhouette wrong, colours approximate; (2) feature placement and a sliver between hair and forehead; (3) neck width and jaw shape. Stop when the blend panel shows no salient difference.

## 2. Explode

Copy `assets/rig-template` to `avatar-rig/`, then edit `rig.json` (palette from the measured colours, anchors from the measurements) and move each region of the drawing into its slot as the default part. Parity check: `compare.py pre_split.png default.png` returns an error near 0.

## 3. Parts

Requested: hair 4, nose 3, mouth 3, neck 3. The template already holds that many:

```
$ python scripts/assemble.py assets/rig-template --list
backdrop   *flat, gradient
hair       buzz, *crop, long, wavy
torso      broad, *standard
neck       *regular, slim, v-neck
ears       *round, small
head       *oval, square
nose       button, long, *wedge
mouth      closed, grin, *smile
eyes       almond, *round
brows      *arched, flat
```
(`*` marks the default.) For a real request, author only the slots and counts asked for.

## 4. Verify

```
$ python scripts/verify_parts.py assets/rig-template --combos 5 --out verify
rig: 25 variants across 10 slots; default = {...}
combos: 5 sampled, covering 69% of interacting slot-pair tuples (seed 1)
result: PASS (0 error(s), 0 warning(s))
wrote verify/report.json, variants-sheet.png, combos-sheet.png
```
Review [sample-variants-sheet.png](sample-variants-sheet.png) and [sample-combos-sheet.png](sample-combos-sheet.png) at full size.

### What a failure looks like

Dropping `examples/broken-parts/hair/gap.svg` into the rig (a hair whose inner edge stops 2 units short of the head outline):

```
ERROR hair/gap: seam: 143 thin-crack pixels not present in the default; a neighbouring part stops short of this one. Inspect with --scale 4; raise --crack-min only for a legitimate concave corner
```
Fix: move the hair's inner edge inside the head outline so the two overlap by at least 8 units, then re-run. The other fixtures demonstrate the remaining failure classes:

| Fixture         | Reported as                                                |
| --------------- | ---------------------------------------------------------- |
| `ears/floating` | changed pixels exceed the ears envelope; 3 separate pieces |
| `nose/leaky`    | changed pixels exceed the nose envelope                    |
| `neck/short`    | 2 separate pieces (head detached from body)                |

`python scripts/selftest.py` runs all of them and fails if any is missed.

## 5. Deliver

```
Match: close; remaining differences: painted texture and soft shading are flat in the vector version
Ignored (out of scope): badge icon, settings icon
Slots and counts: hair 4, nose 3, mouth 3, neck 3 (defaults included); other slots single default
Verification: PASS, 5 combinations (seed 1), pair coverage 69%
Files: rig.json, parts/, avatar.svg, verify/variants-sheet.png, verify/combos-sheet.png, picker.html
```
`python scripts/assemble.py <rig> --picker picker.html` produces a self-contained page for swapping parts interactively.
