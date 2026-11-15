"""Geometry shared by `sheet_probe.py` and `conform.py`: where the subjects are, and how to cut them.

Two scripts look at the same sheet - one reports what it measures, the other cuts on those numbers.
Keeping the measurement here means a change to how a band is found cannot make the report and the
cut disagree, and it means a staggered sheet is described the same way by both.

The vocabulary:

- **mask** - an L image, 255 where a subject is;
- **band** - one contiguous run of content along an axis; a gap between bands is a gutter;
- **layout** - how many bands each row holds, and whether rows line up: `regular`, `staggered`,
  `mixed`;
- **cut box** - the rectangle one slot is cut from; in band mode its edges sit in the measured
  gutters, never inside a subject.

Requires pillow for the image work; nothing here writes a file.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field

COMFORTABLE = (64, 96, 128, 192, 256, 384, 512)
LEVELS = (1, 2, 3, 4)

PROJECTION_LIMIT = 2048
SLIVER = 2


class MeasurementError(Exception):
    """An image that cannot be measured, or a plan the image does not support."""


class BandError(MeasurementError):
    """The image does not show the bands the plan claims - a count mismatch, not a bad spec."""

    def __init__(self, message, row=None, expected=None, found=None):
        super().__init__(message)
        self.row = row
        self.expected = expected
        self.found = found


@dataclass
class BandSet:
    count: int = 0
    starts: list = field(default_factory=list)
    ends: list = field(default_factory=list)
    sizes: list = field(default_factory=list)
    gaps: list = field(default_factory=list)

    @property
    def regular(self):
        """True when the gaps are close enough that an even split lands in them."""
        if len(self.gaps) < 2:
            return True
        median = statistics.median(self.gaps)
        return all(abs(gap - median) <= max(4, median * 0.25) for gap in self.gaps)

    def as_dict(self):
        return {
            "count": self.count,
            "starts": self.starts,
            "ends": self.ends,
            "sizes": self.sizes,
            "gaps": self.gaps,
            "regular": self.regular,
        }


# --------------------------------------------------------------------------- masks


def has_alpha(image):
    """True when the image has real transparency, not just an alpha channel that is opaque."""
    if image.mode not in ("RGBA", "LA"):
        return False
    return image.getchannel("A").getextrema()[0] < 250


def content_mask(image, threshold=8):
    """An L mask: 255 where a subject is, 0 where the background is."""
    from PIL import Image, ImageChops

    if has_alpha(image):
        alpha = image.getchannel("A")
        return alpha.point(lambda value: 255 if value > threshold else 0)
    rgb = image.convert("RGB")
    background = Image.new("RGB", rgb.size, rgb.getpixel((0, 0)))
    return ImageChops.difference(rgb, background).convert("L").point(
        lambda value: 255 if value > threshold else 0
    )


def trim_box(image, threshold=8, background=None):
    """Bounding box of the subject, or None when the area is uniform.

    `background` is the sheet's background colour. Using the sheet colour rather than the
    area's own corner matters when a subject touches the edge: the corner would then be the
    subject, and the subject would be measured as the gap.
    """
    from PIL import Image, ImageChops

    if has_alpha(image):
        alpha = image.getchannel("A")
        return alpha.point(lambda value: 255 if value > threshold else 0).getbbox()
    rgb = image.convert("RGB")
    colour = background or rgb.getpixel((0, 0))
    reference = Image.new("RGB", rgb.size, colour)
    diff = ImageChops.difference(rgb, reference).convert("L")
    return diff.point(lambda value: 255 if value > threshold else 0).getbbox()


def content_box(image, threshold=8):
    """Bounds of everything that is not background - where the subjects actually live."""
    width, height = image.size
    return trim_box(image, threshold) or (0, 0, width, height)


# --------------------------------------------------------------------------- bands


def bands(mask, axis, limit=PROJECTION_LIMIT, min_size=SLIVER):
    """Contiguous runs of content along `axis`, measured on a projection.

    `min_size` drops single-pixel slivers (antialiasing on a gap edge) that would otherwise be
    counted as a subject. `limit` caps the projection's long side; a larger sheet is downscaled
    first, which can merge gutters narrower than about `1/scale` pixels - so the projection is
    kept at full resolution for anything up to 2048px.
    """
    from PIL import Image

    width, height = mask.size
    scale = min(1.0, limit / max(width, height))
    if scale < 1:
        small = mask.resize((max(1, round(width * scale)), max(1, round(height * scale))),
                            Image.BOX)
    else:
        small = mask
    pixels = small.load()
    small_w, small_h = small.size
    if axis == "x":
        hits = [any(pixels[x, y] > 8 for y in range(small_h)) for x in range(small_w)]
    else:
        hits = [any(pixels[x, y] > 8 for x in range(small_w)) for y in range(small_h)]

    runs, start = [], None
    for index, hit in enumerate(hits):
        if hit and start is None:
            start = index
        elif not hit and start is not None:
            runs.append((start, index))
            start = None
    if start is not None:
        runs.append((start, len(hits)))

    found = BandSet()
    for start, end in runs:
        size = round((end - start) / scale)
        if size < min_size:
            continue
        found.starts.append(round(start / scale))
        found.ends.append(round(end / scale))
        found.sizes.append(size)
    found.count = len(found.starts)
    for index in range(len(found.ends) - 1):
        found.gaps.append(found.starts[index + 1] - found.ends[index])
    return found


def band_edges(found, extent):
    """Cut positions across `extent`: both edges, and the middle of every gap."""
    edges = [0]
    for index in range(len(found.ends) - 1):
        edges.append((found.ends[index] + found.starts[index + 1]) // 2)
    edges.append(extent)
    return edges


def band_boxes(image, counts, region=None, threshold=8, min_size=SLIVER):
    """Cut boxes for a sheet whose rows hold different numbers of subjects.

    `counts[i]` is how many subjects row `i` holds. Every cut line goes down the middle of a
    measured gutter, so nothing is sliced: an even split cannot do this, because the pitch is not
    the same in every row.

    Raises `BandError` when the image does not show the rows or columns the plan claims - the
    honest answer is to re-render or fix the plan, not to cut the wrong thing.
    """
    mask = content_mask(image, threshold)
    left, top, right, bottom = region or content_box(image, threshold)
    crop = mask.crop((left, top, right, bottom))
    rows = bands(crop, "y", min_size=min_size)
    if rows.count != len(counts):
        raise BandError(
            f"the plan has {len(counts)} row(s) but the image shows {rows.count} content row "
            "band(s); check the sheet or the plan before cutting",
            expected=len(counts), found=rows.count,
        )
    edges = []
    for index, count in enumerate(counts):
        strip = crop.crop((0, rows.starts[index], crop.width, rows.ends[index]))
        columns = bands(strip, "x", min_size=min_size)
        if columns.count != count:
            raise BandError(
                f"row {index + 1} of the plan has {count} subject(s) but the image shows "
                f"{columns.count} column band(s) in that row; subjects may be touching - "
                "regenerate with more spacing, or fix the plan",
                row=index, expected=count, found=columns.count,
            )
        edges.append(band_edges(columns, crop.width))
    vertical = band_edges(rows, crop.height)
    boxes = []
    for row, xs in enumerate(edges):
        for column in range(counts[row]):
            boxes.append((
                left + xs[column], top + vertical[row],
                left + xs[column + 1], top + vertical[row + 1],
            ))
    return boxes


def clipped_cuts(mask, region, columns, rows, tolerance=1):
    """Interior cut lines of an even split that land on content.

    An even split is safe only while every interior boundary falls in a gutter. This says which
    boundaries do not, so a run can point at `--bands` before it writes clipped files.
    """
    left, top, right, bottom = region
    hits = []
    if columns > 1:
        for index in range(1, columns):
            x = left + round(index * (right - left) / columns)
            strip = mask.crop((max(left, x - tolerance), top,
                               min(right, x + tolerance + 1), bottom))
            if strip.getbbox():
                hits.append({"axis": "x", "at": x, "index": index})
    if rows > 1:
        for index in range(1, rows):
            y = top + round(index * (bottom - top) / rows)
            strip = mask.crop((left, max(top, y - tolerance),
                               right, min(bottom, y + tolerance + 1)))
            if strip.getbbox():
                hits.append({"axis": "y", "at": y, "index": index})
    return hits


# --------------------------------------------------------------------------- layout


def _aligned(first, second, tolerance):
    """True when two rows' column centres agree within `tolerance` px."""
    if len(first) != len(second):
        return False
    for a, b in zip(first, second):
        if abs((a[0] + a[1]) / 2 - (b[0] + b[1]) / 2) > tolerance:
            return False
    return True


def row_layout(image, region=None, threshold=8):
    """How the sheet is arranged: one row per band, one column count per row.

    A generated grid whose x-projection finds no gaps at all is not a one-column sheet - it is a
    staggered or mixed layout, and the only honest way to read it is row by row. This is that
    reading, plus the master spec that describes it and the cut lines an even split would clip.
    """
    mask = content_mask(image, threshold)
    left, top, right, bottom = region or content_box(image, threshold)
    crop = mask.crop((left, top, right, bottom))
    rows = bands(crop, "y")
    detail, spans = [], []
    for index in range(rows.count):
        strip = crop.crop((0, rows.starts[index], crop.width, rows.ends[index]))
        columns = bands(strip, "x")
        spans.append(list(zip(columns.starts, columns.ends)))
        detail.append({
            "index": index,
            "top": top + rows.starts[index],
            "bottom": top + rows.ends[index],
            "height": rows.ends[index] - rows.starts[index],
            "columns": columns.count,
            "starts": [left + start for start in columns.starts],
            "sizes": columns.sizes,
            "gaps": columns.gaps,
        })
    counts = [row["columns"] for row in detail]
    tolerance = max(4, round((right - left) * 0.02))
    if not detail:
        kind = "empty"
    elif len(set(counts)) > 1:
        kind = "mixed"
    elif all(_aligned(spans[0], span, tolerance) for span in spans[1:]):
        kind = "regular"
    else:
        kind = "staggered"
    spec = None
    if detail and kind in ("regular", "mixed", "staggered"):
        if len(set(counts)) == 1:
            spec = f"{image.width}x{image.height} sheet {counts[0]}x{len(counts)}"
        else:
            spec = (f"{image.width}x{image.height} sheet rows "
                    + ",".join(str(count) for count in counts))
    cuts = clipped_cuts(mask, (left, top, right, bottom),
                        counts[0] if counts else 1, len(counts)) if detail else []
    return {
        "kind": kind,
        "region": [left, top, right, bottom],
        "rows": detail,
        "counts": counts,
        "subjects": sum(counts),
        "master": spec,
        "clipped_cuts": cuts,
    }


# --------------------------------------------------------------------------- cells


def split_boxes(box, columns, rows):
    """Evenly divide a box, distributing the remainder - the same rule conform uses."""
    left, top, right, bottom = box
    xs = [left + round(index * (right - left) / columns) for index in range(columns + 1)]
    ys = [top + round(index * (bottom - top) / rows) for index in range(rows + 1)]
    return [(xs[col], ys[row], xs[col + 1], ys[row + 1])
            for row in range(rows) for col in range(columns)]


def cell_subjects(image, box, columns, rows, threshold=8):
    """Subject bbox (relative to each cell) and whether the cell is empty."""
    mask = content_mask(image, threshold)
    cells = []
    for index, cell in enumerate(split_boxes(box, columns, rows)):
        piece = mask.crop(cell)
        found = piece.getbbox()
        cells.append({
            "index": index,
            "box": list(cell),
            "subject": list(found) if found else None,
            "size": [found[2] - found[0], found[3] - found[1]] if found else [0, 0],
            "empty": found is None,
        })
    return cells


def feasibility(ceiling, delivery=None):
    """Which (size, dpr) pairs a square master of `ceiling` can serve."""
    fits = {}
    for size in COMFORTABLE:
        levels = [level for level in LEVELS if size * level <= ceiling]
        if levels:
            fits[size] = levels
    out = {"max_square_master": ceiling, "fits": fits, "rejected": {}}
    for size in COMFORTABLE:
        if size in fits:
            continue
        out["rejected"][size] = f"needs {size}x{size} at 1x, ceiling is {ceiling}"
    if delivery:
        out["delivery"] = delivery
    return out
