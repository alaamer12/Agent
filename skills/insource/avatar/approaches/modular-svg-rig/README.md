# Approach: modular SVG rig

The first approach in `/avatar`'s catalog (`data.csv` id: `modular-svg-rig`, status: verified).
Everything built under this approach so far is registered in [`wagba-avatars.csv`](wagba-avatars.csv);
this file is the method. The parent skill ([`../../SKILL.md`](../../SKILL.md)) owns the lifecycle and
approach choice; this card owns *how to build one of these*.

Build the avatar as a **rig**: one fixed coordinate system with named **slots** (hair, nose, mouth, ...),
each holding one interchangeable **part**. *Explodable* means any single part can be swapped without
changing anything else: swapping the haircut leaves face, neck and clothing pixel-identical.

## When this approach fits (and when to pick another row from data.csv)

Pick the rig when the request is: recreate/refine a character **from a reference image**, and/or the user
wants **swappable, mix-and-match parts** (multiple hairstyles, noses, outfits) that stay consistent under
one palette. Skip it when a single fixed avatar suffices (a monogram or photo-crop row of `data.csv` is
cheaper), when the output must be raster/photoreal, or when the identity is procedural (hash/seed-driven).

## Scope

**Includes**
- Reproducing the character in a reference image as vector art (SVG; an HTML page on request).
- Decomposing it into slots and authoring as many variants per slot as the user asks for.
- Verifying that parts fit (no gaps, seams, leaks or floating pieces) and delivering preview sheets and a report.

**Excludes**
- Interface elements around the character in a reference screenshot (icons, badges, buttons, labels, text).
  They are noise: never draw them, mask them out of comparisons (`compare.py --ignore`), and note in the
  report that they were ignored.
- Raster or photoreal output, 3D, animation rigging, full-body characters (unless asked), and application
  integration such as upload flows or profile pages.

## Setup

Needs Python 3 with Playwright (Chromium), Pillow, NumPy and SciPy. Check first:
`python3 -c "import playwright, PIL, numpy, scipy"`. If missing, install into a **project-local venv**
(never the global interpreter):
`python3 -m venv .venv && .venv/bin/pip install playwright pillow numpy scipy && .venv/bin/playwright install chromium`
(Windows: `.venv\Scripts\pip install ...`). Rendering uses `file://` pages, so no local server is needed.

## Workflow

Copy this checklist and tick it off:

```
- [ ] 1 Match: reference inspected, character drawn, compare loop converged
- [ ] 2 Explode: split into slots; default combination equals the matched render
- [ ] 3 Parts: requested variants authored for every requested slot
- [ ] 4 Verify: lint, isolation, gap and sampled-combination checks pass
- [ ] 5 Deliver: rig, previews, report — then register what was built in wagba-avatars.csv
```

### 1. Match the reference

Details: [references/reference-matching.md](references/reference-matching.md)
1. Find the character, list out-of-scope elements, and zoom in: `scripts/inspect_ref.py ref.png --box ... --zoom 8 --grid 10 --palette 6`.
2. Draw with a `viewBox` equal to the crop box so measured coordinates are used as-is.
3. Loop: `scripts/render.py` -> `scripts/compare.py` -> fix the largest discrepancy first (silhouette,
   proportions, features, colour, then detail). Stop when nothing salient differs at 100% zoom or progress
   stalls after about five rounds; state what still differs.

### 2. Make it explodable

Details: [references/modular-rig.md](references/modular-rig.md)
1. Copy `assets/rig-template/` and adapt `rig.json` (palette, layer order, slot envelopes, anchors) to the
   matched drawing.
2. Move each region of the drawing into its slot as the **default part**.
3. Prove parity: the assembled default must match the pre-split render. Do not continue until it does.

### 3. Generate the parts

Details: [references/part-authoring.md](references/part-authoring.md)
- Create exactly the slots and counts the user requests; if no count is given, make 3 variants per requested
  slot and say so.
- Every part uses palette variables only, stays inside its envelope, overlaps neighbours by at least 8 units
  and matches the default's drawing style.

### 4. Verify

Details: [references/verification.md](references/verification.md)

```bash
python scripts/verify_parts.py <rig-dir> --combos 5 --out <rig-dir>/verify
```

Testing every combination grows exponentially, so the script samples combinations by greedy pairwise coverage
of slots that touch each other and reports the coverage. Fix the **part** (not the thresholds) until the
result is PASS, then look at `variants-sheet.png` and `combos-sheet.png` at full size: a pass is necessary,
not sufficient.

### 5. Deliver — and register

Rig folder (`rig.json`, `parts/<slot>/<id>.svg`), the default `avatar.svg`, the two sheets, and a short
report: match quality and remaining differences, ignored elements, slots and counts, verify result with
coverage. Offer `scripts/assemble.py <rig> --picker picker.html`, a self-contained page for swapping parts
interactively. Then every new slot/part/combo you shipped gets a row in `wagba-avatars.csv`
(`catalog.py` writes it for you) — an unregistered part is a part the next run will re-invent.

## Rules that prevent the usual failures

- A part paints only the layers its slot owns. Otherwise swapping it changes things it should not touch.
- Overlap neighbours instead of abutting them. Edge-to-edge shapes leave hairline seams.
- Colours come from palette variables, so one part works under any palette.
- When verification fails, fix the part. Change the rig only when an anchor or envelope is wrong, then
  re-verify everything.

## Resources

| File | Read when |
|---|---|
| [references/reference-matching.md](references/reference-matching.md) | Phase 1: measuring, drawing and the compare loop |
| [references/modular-rig.md](references/modular-rig.md) | Phase 2: `rig.json`, layer order, slots, anchors, parity check |
| [references/part-authoring.md](references/part-authoring.md) | Phase 3: the part contract and per-slot guidance |
| [references/verification.md](references/verification.md) | Phase 4: reading failures, sampling, review checklist |
| [wagba-avatars.csv](wagba-avatars.csv) | Always: what slots/parts/combos already exist and their status |
| `assets/rig-template/` | Working generic rig (10 slots, 25 parts) to copy and adapt |
| `examples/walkthrough.md` | A complete worked request with real command output |
| `examples/broken-parts/` | Known-bad parts; `scripts/selftest.py` proves the verifier catches them |
| `scripts/` | `inspect_ref`, `render`, `compare`, `assemble`, `verify_parts`, `selftest`; run with `--help` |

**Verification status:** `scripts/selftest.py` and the full five-phase walkthrough were executed against
this template on 2026-10-30 (the run that produced `examples/` sheets and the 25 registered parts). The
Playwright-dependent scripts have not been re-run since the folder move; paths are relative to this
directory's root and were preserved by the move, but re-run the selftest once before trusting a fresh rig.
