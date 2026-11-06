# Part authoring

How to generate interchangeable parts that pass verification the first time.

## Contents

1. The part contract
2. Procedure per slot
3. Guidance by slot
4. Counts and naming
5. Common mistakes

## 1. The part contract

1. File: `parts/<slot>/<id>.svg`, a root `<svg xmlns="http://www.w3.org/2000/svg">` holding `<g data-layer="LAYER">` groups. Only layers the slot owns.
2. Same coordinate system as the rig `viewBox`. No `transform` tricks that move the origin.
3. Colours only as palette variables (`fill="var(--skin)"`), never hex values.
4. Stay inside the slot envelope.
5. Overlap every neighbouring shape by at least 8 units, placing the overlap **underneath** the neighbour (see layer order). Never let two shapes meet edge to edge.
6. Any `id` in `<defs>` starts with `<slot>-<id>`; no scripts, raster images, remote links or `xlink:`.
7. Match the default part's drawing language: stroke width, corner roundness, outline colour, shading approach.

`python scripts/assemble.py <rig> --lint` checks items 1, 3 and 6 mechanically.

## 2. Procedure per slot

1. Open the default part and the anchors it uses; note what it must connect to.
2. Decide the variation axes (size, shape, length, spacing, style) so the variants are visibly different, not near duplicates.
3. Write each variant, then render it in the default combination: `python scripts/assemble.py <rig> --pick <slot>=<id> -o t.svg && python scripts/render.py t.svg t.png`.
4. Look at it at 100% before moving on. After the slot is done, run `verify_parts.py` for that rig.

## 3. Guidance by slot

| Slot              | Must connect to           | Watch for                                                                                                                    |
| ----------------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| hair (front/back) | head outline, ears, brows | Inner edge of side hair must lie inside the head outline; fringe must stay above the brows; back hair stays behind the torso |
| head              | ears, neck, features      | Keep ear attach points and chin depth so the neck top stays hidden; features must still fit inside                           |
| ears              | head                      | Overlap the head by 8+ units on each side; remain behind the head layer                                                      |
| eyes, brows       | head                      | Stay inside the face; keep the eye line and brow line distances so expression does not break                                 |
| nose              | head, mouth               | Stay between brows and mouth; do not touch the mouth envelope                                                                |
| mouth             | head, nose                | Keep corners inside the cheeks; teeth and lips as one part                                                                   |
| neck              | head, torso               | Top hidden under the chin by 8+ units; sides run below the shoulder line; owns the neckline                                  |
| torso / clothing  | neck                      | Plain shoulders that rise to the neck; top edge hidden under the neck width range of every neck variant                      |
| backdrop          | frame                     | Fill the whole viewBox; no content the frame would reveal                                                                    |

Optional accessories (glasses, hats, earrings): own layers above the features, an "empty" default, and an envelope covering the worst case.

## 4. Counts and naming

- Produce exactly what was asked: "5 haircuts and 3 noses" means 5 and 3 new variants plus the default, unless the default is one of the five (say which).
- Unspecified count: 3 variants per requested slot.
- Ids are lowercase kebab-case and describe the look (`short-wave`, `button`, `wide-grin`), not numbers.
- Variants must differ visibly. `verify_parts.py` warns when a variant renders identically to the default.

## 5. Common mistakes

- A hair edge that falls just short of the head outline leaves a sliver of backdrop.
- A neck that ends above the shoulder line detaches the head from the body.
- Ears or features that are positioned for one head variant and float on another.
- Re-drawing a neighbour's region "to make it fit". Fix the overlap, not the neighbour.
- Hard-coded colours that ignore a palette change.
