#!/usr/bin/env python3
"""Verify that swappable avatar parts fit: lint, isolation, gaps, sampled combinations.

  python scripts/verify_parts.py RIG_DIR [--combos 5] [--seed 1] [--out verify_out]

Checks (exit code 1 if any ERROR):
  lint       every part obeys the contract (owned layers, palette variables, unique ids)
  isolation  swapping ONE slot changes pixels only inside that slot's envelope
             (this is what "everything else stays unchanged" means, measured)
  gaps       the silhouette, rendered without the backdrop, has no enclosed holes, no thin
             cracks or seams, and stays one connected shape (nothing floating or detached)
  combos     N sampled combinations (greedy pairwise coverage of interacting slots) pass the
             same gap checks, because gaps appear where neighbouring parts meet
Outputs in --out: report.json, variants-sheet.png (each variant swapped into the default),
combos-sheet.png (the sampled combinations; failures outlined in red).
"""
import argparse
import itertools
import json
import random
import sys
from pathlib import Path

import numpy as np
import scipy.ndimage as ndi
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from _render import Renderer  # noqa: E402
from assemble import compose, lint, list_variants, load_rig  # noqa: E402

OPAQUE = 250      # alpha >= this counts as solid (anti-aliased edges stay below it)
SILHOUETTE = 8    # alpha > this counts as part of the character
DIFF = 10         # per-channel difference that counts as a changed pixel
ENVELOPE_TOL = 2  # viewBox units of slack on envelopes (anti-aliasing)


def analyze(img, units, min_gap_area, crack_radius, min_speck):
    """Gap analysis on a transparent render (no backdrop)."""
    a = np.asarray(img)[:, :, 3]
    solid = a >= OPAQUE
    # 1) connected pieces of the silhouette
    lab, n = ndi.label(a > SILHOUETTE)
    areas = ndi.sum(np.ones_like(a), lab, range(1, n + 1)) if n else []
    pieces = int(sum(1 for s in areas if s >= min_speck))
    # 2) enclosed non-solid regions = holes and seams between parts
    soft = ~solid
    lab2, n2 = ndi.label(soft)
    border = set(np.unique(np.concatenate([lab2[0], lab2[-1], lab2[:, 0], lab2[:, -1]]))) - {0}
    enclosed = soft & ~np.isin(lab2, list(border))
    lab3, n3 = ndi.label(enclosed)
    holes = []
    for i, sl in enumerate(ndi.find_objects(lab3), start=1):
        area = int((lab3[sl] == i).sum())
        if area >= min_gap_area:
            ys, xs = sl
            holes.append({"area_px": area, "bbox": [round(xs.start * units, 1), round(ys.start * units, 1),
                                                     round(xs.stop * units, 1), round(ys.stop * units, 1)]})
    # 3) hairline cracks that touch the outline (closing a thin crack fills it)
    r = crack_radius
    yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
    closed = ndi.binary_closing(solid, structure=(xx * xx + yy * yy) <= r * r)
    cracks = closed & ~solid & (a < OPAQUE)
    return {"pieces": pieces, "holes": holes, "cracks": cracks}


def to_units(box_px, units):
    return [round(v * units, 1) for v in box_px]


def changed_bbox(a, b):
    d = np.abs(np.asarray(a, np.int16) - np.asarray(b, np.int16)).max(axis=2) > DIFF
    if not d.any():
        return None
    ys, xs = np.where(d)
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def pick_combos(rig, variants, n, seed):
    """Greedy pairwise coverage over interacting slot pairs."""
    rnd = random.Random(seed)
    slots = list(rig["slots"])
    pairs = [tuple(p) for p in rig.get("interacts", [])] or list(itertools.combinations(slots, 2))
    pairs = [p for p in pairs if p[0] in variants and p[1] in variants]
    universe = {(a, b, va, vb) for a, b in pairs for va in variants[a] for vb in variants[b]}
    pool = [{s: rnd.choice(variants[s]) for s in slots} for _ in range(400)]
    covered, chosen = set(), []
    for _ in range(n):
        best = max(pool, key=lambda c: (len({(a, b, c[a], c[b]) for a, b in pairs} - covered), rnd.random()))
        chosen.append(best)
        covered |= {(a, b, best[a], best[b]) for a, b in pairs}
    pct = 100 * len(covered & universe) / max(1, len(universe))
    return chosen, pct


def crop_to(img, env, units, margin=24, out=210):
    x0, y0, x1, y1 = (v / units for v in (env[0] - margin, env[1] - margin, env[2] + margin, env[3] + margin))
    c = img.crop((max(0, int(x0)), max(0, int(y0)), min(img.width, int(x1)), min(img.height, int(y1)))).convert("RGB")
    c.thumbnail((out, out), Image.LANCZOS)
    return c


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rig_dir")
    ap.add_argument("--combos", type=int, default=5, help="sampled combinations (default 5)")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", default="verify_out")
    ap.add_argument("--scale", type=int, default=2, help="render scale; 2 is enough, 3-4 for hairline seams")
    ap.add_argument("--min-gap-area", type=int, default=6, help="smallest enclosed hole (px at render scale) to flag")
    ap.add_argument("--crack-radius", type=int, default=3, help="px at render scale; cracks narrower than ~2x this are caught")
    ap.add_argument("--crack-min", type=int, default=60, help="new crack pixels (vs the default) that count as a seam")
    a = ap.parse_args()

    rig = load_rig(a.rig_dir)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    vb = [float(v) for v in rig["viewBox"].split()]
    size = 600
    units = vb[2] / (size * a.scale)                 # viewBox units per rendered pixel
    min_speck = int(40 / units / units)               # ignore specks below ~40 square units
    errors, warns = [], []
    report = {"lint": [], "isolation": [], "variants": [], "combos": [], "coverage_pct": None}

    for level, msg in lint(a.rig_dir, rig):
        (errors if level == "error" else warns).append(f"lint: {msg}")
        report["lint"].append({"level": level, "message": msg})
    if errors:
        print("\n".join(f"ERROR {e}" for e in errors))
        sys.exit("fix lint errors before rendering")

    variants = list_variants(a.rig_dir, rig)
    default = dict(rig["default"])
    slots = list(rig["slots"])
    max_pieces = rig.get("max_components", 1)

    def render_pair(r, picks):
        full = r.svg(compose(a.rig_dir, rig, picks, include_backdrop=True))
        bare = r.svg(compose(a.rig_dir, rig, picks, include_backdrop=False), transparent=True)
        return full, bare

    def gap_report(bare, base_cracks=None):
        res = analyze(bare, units, a.min_gap_area, a.crack_radius, min_speck)
        issues = []
        if res["pieces"] > max_pieces:
            issues.append(f"{res['pieces']} separate pieces (expected {max_pieces}): a part is detached or floating")
        for h in res["holes"]:
            near = [s for s in slots if rig["slots"][s]["envelope"][0] - 8 <= (h["bbox"][0] + h["bbox"][2]) / 2 <= rig["slots"][s]["envelope"][2] + 8
                    and rig["slots"][s]["envelope"][1] - 8 <= (h["bbox"][1] + h["bbox"][3]) / 2 <= rig["slots"][s]["envelope"][3] + 8
                    and not rig["slots"][s].get("backdrop")]
            issues.append(f"enclosed gap {h['bbox']} ({h['area_px']} px); neighbours there: {', '.join(near) or '?'}; "
                          "extend one part so it overlaps the other by >= 8 units")
        new_cracks = 0
        if base_cracks is not None:
            grown = ndi.binary_dilation(base_cracks, iterations=3)
            new_cracks = int((res["cracks"] & ~grown).sum())
        return res, issues, new_cracks

    with Renderer(size, a.scale) as r:
        base_full, base_bare = render_pair(r, default)
        base_res, base_issues, _ = gap_report(base_bare)
        if base_issues:
            for m in base_issues:
                errors.append(f"default combination: {m}")
        base_cracks = base_res["cracks"]

        # ---- per-variant: isolation + gaps -------------------------------------------------
        rows = {}
        for slot in slots:
            env = rig["slots"][slot]["envelope"]
            rows[slot] = []
            for vid in variants[slot]:
                picks = dict(default, **{slot: vid})
                full, bare = (base_full, base_bare) if vid == default[slot] else render_pair(r, picks)
                entry = {"slot": slot, "variant": vid, "issues": []}
                if vid != default[slot]:
                    bb = changed_bbox(base_full, full)
                    if bb is None:
                        entry["issues"].append("renders identically to the default (duplicate variant?)")
                        warns.append(f"{slot}/{vid}: renders identically to the default")
                    else:
                        ub = to_units(bb, units)
                        entry["changed_bbox"] = ub
                        if (ub[0] < env[0] - ENVELOPE_TOL or ub[1] < env[1] - ENVELOPE_TOL or
                                ub[2] > env[2] + ENVELOPE_TOL or ub[3] > env[3] + ENVELOPE_TOL):
                            msg = (f"isolation: changed pixels {ub} exceed the {slot} envelope {env}; "
                                   "the part leaks outside its region (or the envelope is too small)")
                            entry["issues"].append(msg)
                            errors.append(f"{slot}/{vid}: {msg}")
                    res, issues, new_cracks = gap_report(bare, base_cracks)
                    for m in issues:
                        entry["issues"].append(m)
                        errors.append(f"{slot}/{vid}: {m}")
                    if new_cracks >= a.crack_min:
                        m = (f"seam: {new_cracks} thin-crack pixels not present in the default; a neighbouring part stops short "
                             "of this one. Inspect with --scale 4; raise --crack-min only for a legitimate concave corner")
                        entry["issues"].append(m)
                        errors.append(f"{slot}/{vid}: {m}")
                entry["ok"] = not any(not i.startswith("renders identically") for i in entry["issues"])
                report["variants"].append(entry)
                rows[slot].append((vid, crop_to(full, env, units), bool(entry["issues"]) and not entry["ok"]))

        # ---- sampled combinations ----------------------------------------------------------
        combos, pct = pick_combos(rig, variants, a.combos, a.seed)
        report["coverage_pct"] = round(pct, 1)
        tiles = []
        for i, picks in enumerate(combos, start=1):
            full, bare = render_pair(r, picks)
            res, issues, new_cracks = gap_report(bare, base_cracks)
            for m in issues:
                errors.append(f"combo {i}: {m}")
            if new_cracks >= a.crack_min:
                issues.append(f"seam: {new_cracks} thin-crack pixels not present in the default")
                errors.append(f"combo {i}: {issues[-1]}")
            report["combos"].append({"index": i, "picks": picks, "issues": issues, "ok": not issues})
            tile = full.convert("RGB")
            d = ImageDraw.Draw(tile)
            for h in res["holes"]:
                d.rectangle([v / units for v in h["bbox"]], outline=(255, 0, 0), width=3)
            tile.thumbnail((300, 300), Image.LANCZOS)
            tiles.append((i, picks, tile, bool(issues)))

    # ---- sheets ----------------------------------------------------------------------------
    lab_w, gap, label_h = 78, 8, 16
    row_h = {slot: max(im.height for _, im, _ in items) + label_h + gap for slot, items in rows.items()}
    width = lab_w + max(sum(im.width + gap for _, im, _ in items) for items in rows.values())
    sheet = Image.new("RGB", (width, sum(row_h.values())), "white")
    d = ImageDraw.Draw(sheet)
    y = 0
    for slot, items in rows.items():
        d.text((6, y + 6), slot, fill=(0, 0, 0))
        x = lab_w
        for vid, im, bad in items:
            sheet.paste(im, (x, y))
            if bad:
                d.rectangle([x, y, x + im.width - 1, y + im.height - 1], outline=(255, 0, 0), width=3)
            d.text((x + 2, y + im.height + 2), vid, fill=(200, 0, 0) if bad else (0, 0, 0))
            x += im.width + gap
        y += row_h[slot]
    sheet.save(out / "variants-sheet.png")

    cols = min(len(tiles), 5)
    th = 300 + 46
    rows_n = (len(tiles) + cols - 1) // cols
    cs = Image.new("RGB", (cols * 306, rows_n * th), "white")
    d = ImageDraw.Draw(cs)
    for k, (i, picks, tile, bad) in enumerate(tiles):
        x, y = (k % cols) * 306, (k // cols) * th
        cs.paste(tile, (x, y))
        if bad:
            d.rectangle([x, y, x + tile.width - 1, y + tile.height - 1], outline=(255, 0, 0), width=4)
        txt = f"#{i} " + " ".join(f"{s[:5]}={picks[s]}" for s in slots if s != "backdrop")
        words, line, ly = txt.split(" "), "", y + 304
        for w_ in words:
            if len(line) + len(w_) > 46:
                d.text((x + 2, ly), line, fill=(0, 0, 0)); ly += 11; line = ""
            line += w_ + " "
        d.text((x + 2, ly), line, fill=(0, 0, 0))
    cs.save(out / "combos-sheet.png")

    report["errors"], report["warnings"] = errors, warns
    (out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    n_var = sum(len(v) for v in variants.values())
    print(f"rig: {n_var} variants across {len(slots)} slots; default = {default}")
    print(f"combos: {len(combos)} sampled, covering {pct:.0f}% of interacting slot-pair tuples (seed {a.seed})")
    for w in warns:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"result: {'FAIL' if errors else 'PASS'} ({len(errors)} error(s), {len(warns)} warning(s))")
    print(f"wrote {out}/report.json, variants-sheet.png, combos-sheet.png")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
