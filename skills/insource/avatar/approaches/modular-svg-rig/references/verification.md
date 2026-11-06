# Verification

What `scripts/verify_parts.py` checks, how to read failures, and what a person must still look at.

## Contents

1. Run it
2. The checks
3. Why a sample of combinations
4. Failure to fix table
5. Manual review
6. Report template

## 1. Run it

```bash
python scripts/verify_parts.py <rig-dir> --combos 5 --out <rig-dir>/verify
```
Options: `--seed N` (different sample), `--scale 3` or `4` (finer seam detection and sheets), `--min-gap-area`, `--crack-min` (thresholds; raise only for a justified legitimate corner). Exit code 0 means PASS. Self-check the verifier with `python scripts/selftest.py`.

## 2. The checks

| Check     | Meaning                                           | Method                                                                                                                                             |
| --------- | ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| lint      | Parts obey the contract                           | Layers owned, palette variables known, ids prefixed, no external references                                                                        |
| isolation | Swapping one slot changes only that slot's region | Render default and default-with-one-swap; changed pixels must lie inside the slot envelope                                                         |
| gaps      | No holes, seams or detached pieces                | Render without backdrop on a transparent canvas; flood-fill for enclosed non-solid regions; closing filter for thin cracks; count connected pieces |
| combos    | Parts work together                               | Same gap checks on sampled combinations                                                                                                            |

Gap checks run on every variant swapped into the default, and again on the sampled combinations.

## 3. Why a sample of combinations

Combinations multiply: 6 slots with 5 variants each give 15,625 characters. Defects, though, appear where two parts touch. Single-swap checks cover each variant against the default; sampling covers variant-against-variant at touching slots. The script builds the sample greedily to cover as many (slot pair, variant pair) tuples as possible, using the rig's `interacts` list, and prints the coverage. Default is 5 combinations. Raise `--combos` when coverage is low or a pair interaction is risky (long hair with wide shoulders); change `--seed` to get a different sample.

## 4. Failure to fix table

| Message                         | Likely cause                                                                   | Fix                                                                                                     |
| ------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| `exceed the <slot> envelope`    | Part paints outside its region                                                 | Pull the shape in, or enlarge the envelope if the region is legitimately larger, then re-run everything |
| `N separate pieces`             | A part floats or does not reach its neighbour                                  | Extend it so it overlaps the neighbour by 8+ units under the neighbour layer                            |
| `enclosed gap [box]`            | Backdrop shows through between parts                                           | Extend one of the neighbours listed in the message across the gap                                       |
| `seam: ... thin-crack pixels`   | A neighbour stops a few units short, leaving a sliver that touches the outline | Same as above; confirm with `--scale 4`                                                                 |
| `renders identically` (warning) | Duplicate variant                                                              | Make it visibly different or delete it                                                                  |
| lint errors                     | Contract violation                                                             | Edit the part as the message states                                                                     |

## 5. Manual review

Open both sheets at full size.
- `variants-sheet.png`: one row per slot, each variant swapped into the default and cropped to the slot region. Check each is recognisable, in style, and complete.
- `combos-sheet.png`: sampled characters in full. Check face, neck and clothing look identical across combinations apart from the swapped parts.
  Look specifically at: hairline against forehead and ears, chin against neck, neckline against clothing, ears against head.

## 6. Report template

```
Match: <good / close / partial>; remaining differences: <list>
Ignored (out of scope): <elements of the reference not reproduced>
Slots and counts: hair 4, nose 3, ... (defaults included)
Verification: PASS, 5 combinations (seed 1), pair coverage 69%
Files: rig.json, parts/, avatar.svg, verify/variants-sheet.png, verify/combos-sheet.png
```
