"""Conform a generated master into the delivery slot files a project ships.

One render often carries several subjects - ten avatars inside one 2K image. This script reads the
bill of materials (BOM) written by the `collection` skill, slices the master into its cells, fits
each cell to its slot's delivery spec without distorting it, writes the DPR ladder with the slot's
format and quality, and then verifies every file it produced. A `single` master (a hero, a section
background) is one slot: used whole, fitted, laddered and verified the same way.

Two ways to cut a sheet:

- **even grid** (`sheet 5x2`) - divide the content box into equal cells. Correct while the gutters
  are regular; the run warns when an interior cut line lands on content.
- **measured bands** (`sheet rows 8,8,8,10`, or `--bands`) - cut down the middle of the gutters the
  image actually has. Required when the rows hold different numbers of subjects, or when an even
  pitch would slice one.

Usage:
    python scripts/conform.py --bom bom/home.md --group avatar --in raw/avatars.png --out assets/avatars
    python scripts/conform.py --bom bom/flow.md --slots welcome,permissions,finish \
        --in raw/flow.png --out assets/flow
    python scripts/conform.py --bom bom/home.md --slots hero-home --in raw/hero-home.png --out assets/home
    python scripts/conform.py --bom bom/home.md --slots avatar-01..10 --in raw.png --out out --dry-run
    python scripts/conform.py --in sheet.png --out out --rows 8,8,8,10 \
        --slots a,b --delivery "128x128 1:1 webp q82 @1x,2x"

Slot ids are whatever the project calls its assets: `avatar-01` and `welcome` are the same kind of
key. A range is only a shorthand for a numbered family; a sheet of unrelated subjects lists its ids
in sheet order (row-major), which is the order it is cut in.

Requires: pillow, for the image work only. Parsing and `--dry-run` are standard library.

Exit codes: 0 ok, 2 bad usage or spec, 3 slot/cell count mismatch, 4 verification failed.
"""

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sheet_geometry import (  # noqa: E402
    BandError,
    band_boxes,
    clipped_cuts,
    content_box,
    content_mask,
    has_alpha,
    trim_box,
)

FORMATS = ("png", "jpeg", "jpg", "webp", "avif")
ALIASES = {
    "slot": ("slot", "slots", "id", "slot id"),
    "role": ("role", "kind", "use"),
    "source": ("source", "route", "producer"),
    "master": ("master", "master spec", "source master"),
    "delivery": ("delivery", "delivery spec", "output", "deliverable"),
    "status": ("status", "state"),
}
BLANK = ("", "-", "--", "\u2014", "none", "n/a")


class SpecError(Exception):
    """A BOM row, delivery spec or master spec that cannot be executed."""


@dataclass
class Delivery:
    width: int
    height: int
    fmt: str = "png"
    quality: int | None = None
    dprs: list = field(default_factory=lambda: [1.0])
    aspect: str | None = None

    def ladder(self):
        """[(dpr, width, height)] for every requested density, ascending."""
        return [(dpr, round(self.width * dpr), round(self.height * dpr)) for dpr in self.dprs]

    def required_master(self):
        """Smallest master that serves the largest density without upscaling."""
        widest = max(self.dprs)
        return math.ceil(self.width * widest), math.ceil(self.height * widest)

    def ratio(self):
        return self.width / self.height

    def has_alpha(self):
        return self.fmt in ("png", "webp", "avif")


@dataclass
class Master:
    width: int
    height: int
    kind: str = "single"
    cols: int = 1
    rows: int = 1
    gutter: int = 0
    cell: int | None = None
    # A sheet whose rows hold different numbers of subjects: one column count per row.
    row_counts: list | None = None

    @property
    def capacity(self):
        if self.row_counts:
            return sum(self.row_counts)
        return self.cols * self.rows

    @property
    def banded(self):
        """True when this master must be cut on measured gutters, not on an even grid."""
        return bool(self.row_counts)

    def cell_size(self):
        """Smallest cell the grid yields - the conservative size for feasibility checks."""
        if self.cell:
            return self.cell, self.cell
        if self.row_counts:
            return self.width // max(self.row_counts), self.height // len(self.row_counts)
        usable_w = self.width - (self.cols - 1) * self.gutter
        usable_h = self.height - (self.rows - 1) * self.gutter
        if usable_w <= 0 or usable_h <= 0:
            raise SpecError(
                f"gutter {self.gutter} leaves no room in {self.width}x{self.height} grid "
                f"{self.cols}x{self.rows}"
            )
        return usable_w // self.cols, usable_h // self.rows



@dataclass
class Slot:
    slot: str
    role: str = ""
    source: str = ""
    master: Master | None = None
    delivery: Delivery | None = None
    status: str = ""
    line: int = 0

    def settled(self):
        return bool(self.status) and self.status.lower() in (
            "shipped", "no-image", "reused", "done", "skip",
        )


@dataclass
class Result:
    bom: str = ""
    sheet: str = ""
    group: str = ""
    expected: int = 0
    region: list = field(default_factory=list)
    key: dict = field(default_factory=dict)
    cut: dict = field(default_factory=dict)
    empty_cells: list = field(default_factory=list)

    files: list = field(default_factory=list)
    skipped: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    dry_run: bool = False

    @property
    def ok(self):
        return not self.errors


# --------------------------------------------------------------------------- parsing


def _split_row(line):
    """Split a markdown table row, honouring escaped pipes."""
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    cells, buf, escaped = [], [], False
    for char in body:
        if escaped:
            buf.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "|":
            cells.append("".join(buf).strip())
            buf = []
        else:
            buf.append(char)
    cells.append("".join(buf).strip())
    return cells


def _clean(cell):
    cell = cell.replace("`", "").replace("**", "").replace("*", "").strip()
    return "" if cell.lower() in BLANK else cell


def parse_delivery(text):
    """Parse `128x128 1:1 webp q82 @1x,2x,3x` into a Delivery."""
    text = _clean(text)
    if not text:
        raise SpecError("delivery spec is empty")
    size = fmt = aspect = quality = dprs = None
    for token in text.split():
        low = token.lower()
        if re.fullmatch(r"\d+x\d+", low):
            if size:
                raise SpecError(f"delivery spec has two sizes: {text}")
            width, height = (int(part) for part in low.split("x"))
            if width < 1 or height < 1:
                raise SpecError(f"delivery size must be positive: {token}")
            size = (width, height)
        elif re.fullmatch(r"\d+:\d+", low) or low == "auto":
            aspect = low
        elif low in FORMATS:
            fmt = "jpeg" if low == "jpg" else low
        elif re.fullmatch(r"q\d{1,3}", low):
            quality = int(low[1:])
            if not 1 <= quality <= 100:
                raise SpecError(f"quality must be 1-100: {token}")
        elif low.startswith("@"):
            dprs = _parse_dprs(low[1:])
        else:
            raise SpecError(
                f"unrecognised delivery token {token!r} in {text!r}: expected "
                "SIZE [ASPECT] [FORMAT] [qQUALITY] [@DPRS]"
            )
    if not size:
        raise SpecError(f"delivery spec has no size: {text}")
    delivery = Delivery(
        width=size[0], height=size[1], fmt=fmt or "png",
        quality=quality, dprs=dprs or [1.0], aspect=aspect,
    )
    if delivery.aspect and delivery.aspect != "auto":
        aw, ah = (int(part) for part in delivery.aspect.split(":"))
        if abs(delivery.ratio() - aw / ah) > 0.01:
            raise SpecError(
                f"delivery aspect {delivery.aspect} contradicts {delivery.width}x"
                f"{delivery.height} (ratio {delivery.ratio():.3f} vs {aw / ah:.3f})"
            )
    return delivery


def _parse_dprs(text):
    dprs = []
    for token in text.split(","):
        token = token.strip().lower().rstrip("x")
        if not token:
            continue
        try:
            value = float(token)
        except ValueError:
            raise SpecError(f"bad DPR value {token!r} (expected 1x,2x,3x)")
        if not 0.5 <= value <= 8:
            raise SpecError(f"DPR {value} is outside 0.5-8")
        if value in dprs:
            raise SpecError(f"duplicate DPR {value}")
        dprs.append(value)
    if not dprs:
        raise SpecError("empty DPR list")
    return sorted(dprs)


def parse_master(text):
    """Parse `2048x2048 sheet 4x4 gutter 24`, `1536x1024 sheet rows 8,8,8,10` or `1600x900 single`."""
    text = _clean(text)
    if not text:
        return None
    tokens = text.split()
    match = re.fullmatch(r"(\d+)x(\d+)", tokens[0].lower())
    if not match:
        raise SpecError(f"master spec must start with WxH: {text!r}")
    master = Master(width=int(match.group(1)), height=int(match.group(2)))
    index = 1
    while index < len(tokens):
        token = tokens[index].lower()
        if token in ("single", "sheet"):
            master.kind = token
            index += 1
        elif token == "gutter" and index + 1 < len(tokens):
            master.gutter = int(tokens[index + 1])
            index += 2
        elif token == "cell" and index + 1 < len(tokens):
            master.cell = int(tokens[index + 1])
            index += 2
        elif token == "rows" and index + 1 < len(tokens):
            master.row_counts = _parse_row_counts(tokens[index + 1], text)
            index += 2
        elif re.fullmatch(r"\d+x\d+", token) and master.kind == "sheet":
            master.cols, master.rows = (int(part) for part in token.split("x"))
            index += 1
        else:
            hint = (" - notes such as a fallback plan belong in the economy check, not the "
                    "Master cell" if token.startswith("(") else "")
            raise SpecError(
                f"unrecognised master token {tokens[index]!r} in {text!r}: expected "
                f"WxH [single|sheet CxR|sheet rows C1,C2,...] [gutter N] [cell N]{hint}"
            )
    if master.row_counts and master.cols * master.rows > 1:
        raise SpecError(
            f"master spec has both a grid and per-row counts: {text!r}; `sheet rows 8,8,8` "
            "already says the grid, so use one form"
        )
    if master.row_counts and master.gutter:
        raise SpecError(
            f"master spec has a gutter with per-row counts: {text!r}; a rows plan is cut on the "
            "measured gutters, so a fixed gutter means nothing - use `sheet CxR gutter N` instead"
        )
    if master.kind == "sheet" and master.capacity < 1:
        raise SpecError(f"sheet master needs a grid: {text!r}")
    return master


def _parse_row_counts(token, text):
    """`8,8,8,10` -> [8, 8, 8, 10], one positive column count per row."""
    try:
        counts = [int(part) for part in token.strip(",").split(",")]
    except ValueError:
        raise SpecError(f"rows must be comma-separated column counts: {token!r} in {text!r}")
    if not counts or any(count < 1 for count in counts):
        raise SpecError(f"every row needs at least one column: {token!r} in {text!r}")
    return counts



def expand_slots(spec):
    """Expand `avatar-01..10, hero` into concrete slot ids."""
    names = []
    for token in re.split(r"[,\s]+", spec.strip()):
        if not token:
            continue
        match = re.fullmatch(r"(.*?)(\d+)\.\.(\d+)", token)
        if not match:
            if ".." in token:
                raise SpecError(
                    f"slot range {token!r} must end in a number: a range is `prefixN..M`, "
                    "e.g. avatar-01..10 - not `prefixN..prefixM`"
                )
            names.append(token)
            continue
        prefix, start, end = match.group(1), int(match.group(2)), int(match.group(3))
        if end < start:
            raise SpecError(f"descending slot range {token!r}")
        width = len(match.group(2))
        names.extend(f"{prefix}{number:0{width}d}" for number in range(start, end + 1))
    if not names:
        raise SpecError("no slots selected")
    seen, unique = set(), []
    for name in names:
        if name not in seen:
            seen.add(name)
            unique.append(name)
    return unique


def parse_bom(path):
    """Read the slot table(s) out of a BOM markdown file."""
    text = Path(path).read_text(encoding="utf-8")
    slots, columns = [], None
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("|"):
            if slots:
                break
            columns = None
            continue
        cells = _split_row(stripped)
        if columns is None:
            headers = [cell.lower().strip("*` ") for cell in cells]
            mapped = {}
            for key, names in ALIASES.items():
                for index, header in enumerate(headers):
                    if header in names:
                        mapped[key] = index
                        break
            if "slot" in mapped and "delivery" in mapped:
                columns = mapped
            continue
        if set("".join(cells)) <= set("-: "):
            continue

        def cell(key):
            index = columns.get(key)
            return cells[index] if index is not None and index < len(cells) else ""

        name = _clean(cell("slot"))
        delivery_text = cell("delivery")
        if not name or not delivery_text:
            continue
        master = parse_master(cell("master"))
        delivery = parse_delivery(delivery_text) if master is not None else None
        names = expand_slots(name) if (".." in name or "," in name) else [name]
        for slot_name in names:
            slots.append(
                Slot(
                    slot=slot_name,
                    role=_clean(cell("role")),
                    source=_clean(cell("source")),
                    master=master,
                    delivery=delivery,
                    status=_clean(cell("status")),
                    line=number,
                )
            )
    if not slots:
        raise SpecError(
            f"no slot table found in {path}: expected a markdown table with Slot, Master and "
            "Delivery columns (see the collection skill's BOM template)"
        )
    return slots


# --------------------------------------------------------------------------- planning


def _spans(total, parts, gutter=0):
    """Split `total` px into `parts` spans separated by `gutter`, distributing the remainder."""
    usable = total - (parts - 1) * gutter
    if usable <= 0:
        raise SpecError(f"gutter {gutter} leaves no room for {parts} spans in {total}px")
    edges = [round(index * usable / parts) for index in range(parts + 1)]
    return [(index * gutter + edges[index], index * gutter + edges[index + 1])
            for index in range(parts)]


def plan_boxes(master, count, region=None):
    """Row-major (left, top, right, bottom) boxes for the first `count` cells.

    `region` is the area the grid covers - the sheet's content bounds by default. Cells divide
    that region evenly, so no cut line lands inside a subject when the gutters are regular.
    """
    if master.banded:
        raise SpecError(
            "a rows master has no even grid; cut it on the measured gutters (band mode) instead "
            "of dividing the region"
        )
    if count > master.capacity:
        raise SpecError(
            f"{count} slots need more than the {master.cols}x{master.rows} sheet "
            f"({master.capacity} cells); split into more sheets or fewer slots per sheet"
        )
    left, top, right, bottom = region or (0, 0, master.width, master.height)
    if master.cell:
        pitch = master.cell + master.gutter
        need = master.cols * master.cell + (master.cols - 1) * master.gutter
        if need > right - left:
            raise SpecError(
                f"{master.cols} cells of {master.cell}px plus gutters ({need}px) do not fit the "
                f"{right - left}px content width"
            )
    else:
        pitch = None
    columns = _spans(right - left, master.cols, master.gutter)
    rows = _spans(bottom - top, master.rows, master.gutter)
    boxes = []
    for index in range(count):
        row, col = divmod(index, master.cols)
        if pitch:
            x0 = left + col * pitch
            y0 = top + row * pitch
            x1, y1 = x0 + master.cell, y0 + master.cell
        else:
            x0, x1 = left + columns[col][0], left + columns[col][1]
            y0, y1 = top + rows[row][0], top + rows[row][1]
        boxes.append((x0, y0, x1, y1))
    return boxes


def check_feasible(master, delivery, allow_upscale=False, cell=None):
    """Problems that stop a cell from serving its delivery spec."""
    if allow_upscale:
        return []
    cell_w, cell_h = cell or master.cell_size()
    need_w, need_h = delivery.required_master()
    if cell_w < need_w or cell_h < need_h:
        return [
            f"cell {cell_w}x{cell_h} is smaller than the required master {need_w}x{need_h} "
            f"for {delivery.width}x{delivery.height} at {max(delivery.dprs):g}x; raise the "
            "master, lower the DPR, or pass --allow-upscale"
        ]
    return []


def select_slots(slots, group=None, names=None, force=False):
    selected, skipped = [], []
    for slot in slots:
        if names is not None:
            wanted = slot.slot in names
        elif group:
            wanted = slot.slot == group or slot.slot.startswith(group + "-")
        else:
            wanted = True
        if not wanted:
            continue
        if slot.master is None or slot.delivery is None:
            skipped.append({"slot": slot.slot, "why": "no master/delivery spec (not generated)"})
        elif slot.settled() and not force:
            skipped.append({"slot": slot.slot, "why": f"status {slot.status!r}"})
        else:
            selected.append(slot)
    return selected, skipped


def file_name(slot_name, dpr, width, height, delivery, pattern):
    """Slot filename, with the @Dx suffix unless the pattern names the density or width."""
    ext = "." + delivery.fmt
    name = pattern.format(slot=slot_name, w=width, h=height, dpr=f"{dpr:g}x", ext=ext)
    if not name.endswith(ext):
        name += ext
    if dpr != 1.0 and "{dpr}" not in pattern and "{w}" not in pattern:
        name = name[: -len(ext)] + f"@{dpr:g}x" + ext
    return name


# --------------------------------------------------------------------------- image work


def _require_pillow():
    try:
        from PIL import Image  # noqa: F401
    except Exception:  # pragma: no cover - environment dependent
        raise SystemExit(
            "conform: pillow is required for image work (pip install pillow). "
            "Parsing and --dry-run work without it."
        )


def _trim_box(image, threshold, background=None):
    """Bounding box of the subject, or None when the cell is uniform (see `sheet_geometry`)."""
    return trim_box(image, threshold, background)


def _has_transparency(image):
    """True when the image has real alpha, not just an alpha channel that is fully opaque."""
    return has_alpha(image)


def _content_box(image, threshold):
    """Bounds of everything that is not background - where the subjects actually live.

    Generated sheets carry arbitrary margins. Dividing the *content* box into the grid keeps
    every cut line in a gutter, which dividing the raw canvas does not (a wide left margin
    shifts every subject and the last column gets clipped).
    """
    return content_box(image, threshold)



def _uniform_border(image, threshold):
    """True when the cell's outer ring is one flat colour, so keying it out is safe."""
    rgb = image.convert("RGB")
    width, height = rgb.size
    corner = rgb.getpixel((0, 0))
    step_x = max(1, width // 64)
    step_y = max(1, height // 64)
    for x in range(0, width, step_x):
        for y in (0, height - 1):
            if _distance(rgb.getpixel((x, y)), corner) > threshold:
                return False
    for y in range(0, height, step_y):
        for x in (0, width - 1):
            if _distance(rgb.getpixel((x, y)), corner) > threshold:
                return False
    return True


def _distance(first, second):
    return max(abs(first[index] - second[index]) for index in range(3))


def _key_sheet(sheet, threshold, color=None):
    """Make the sheet's border-connected background transparent, once, before cropping.

    A border-seeded flood fill only reaches background connected to the edge of the *sheet*, so
    a white highlight inside an eye survives, and a subject that fills its cell is never keyed
    out from its own corner. Returns (image, keyed, reason).
    """
    from PIL import Image, ImageChops, ImageDraw, ImageOps

    if _has_transparency(sheet):
        return sheet, False, "sheet already has transparency"
    if color is not None:
        if _distance(sheet.convert("RGB").getpixel((0, 0)), color) > threshold:
            return sheet, False, "sheet corner is not the requested key colour"
    elif not _uniform_border(sheet, threshold):
        return sheet, False, "sheet border is not a flat colour"
    rgba = sheet.convert("RGBA")
    sentinel = (255, 0, 255, 255)
    ImageDraw.floodfill(rgba, (0, 0), sentinel, thresh=threshold)
    diff = ImageChops.difference(rgba, Image.new("RGBA", rgba.size, sentinel)).convert("L")
    background = diff.point(lambda value: 255 if value <= 2 else 0)
    covered = background.histogram()[255]
    if covered >= rgba.width * rgba.height * 0.995:
        return sheet, False, "sheet is one flat colour - nothing to separate"
    rgba.putalpha(ImageOps.invert(background))
    rgba.paste((0, 0, 0, 0), mask=background)
    return rgba, True, f"keyed {covered / (rgba.width * rgba.height):.1%} of the sheet"


def _fit(image, width, height, pad, pad_color):
    """Scale without distortion, then pad to the exact target box."""
    from PIL import Image

    scale = min(width / image.width, height / image.height)
    inner = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    if pad == "edge":
        return image.resize((width, height), Image.LANCZOS)
    resized = image.resize(inner, Image.LANCZOS) if inner != image.size else image
    if inner == (width, height):
        return resized
    canvas = Image.new(
        "RGBA", (width, height),
        (0, 0, 0, 0) if pad == "transparent" else pad_color,
    )
    canvas.paste(resized.convert("RGBA"), ((width - inner[0]) // 2, (height - inner[1]) // 2))
    return canvas


def _flatten(image, color=(255, 255, 255, 255)):
    from PIL import Image

    canvas = Image.new("RGBA", image.size, color)
    canvas.alpha_composite(image.convert("RGBA"))
    return canvas.convert("RGB")


def _save(image, path, delivery):
    """Write one ladder step; encoding settings are the delivery spec's own words."""
    path.parent.mkdir(parents=True, exist_ok=True)
    options = {}
    fmt = delivery.fmt.upper()
    if fmt in ("WEBP", "JPEG", "AVIF") and delivery.quality:
        options["quality"] = delivery.quality
    if fmt == "JPEG":
        image = _flatten(image) if image.mode == "RGBA" else image
        options.update(optimize=True, progressive=True)
    elif fmt == "WEBP":
        options.update(method=6)
    elif fmt == "PNG":
        options.update(optimize=True)
    try:
        image.save(path, fmt, **options)
    except (KeyError, OSError) as error:
        raise SpecError(f"cannot write {fmt} to {path}: {error} (pillow may lack that encoder)")


def _parse_color(text):
    if not text:
        return None
    value = text.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(char * 2 for char in value)
    if len(value) in (6, 8):
        try:
            return tuple(int(value[index:index + 2], 16) for index in range(0, len(value), 2)) + (
                (255,) if len(value) == 6 else ()
            )
        except ValueError:
            pass
    raise SpecError(f"pad colour must be #RGB, #RRGGBB or #RRGGBBAA: {text!r}")


# --------------------------------------------------------------------------- run


def _resolve(args):
    """Return (selected slots, master, peers, skipped) from the BOM and/or the explicit flags."""
    slots = []
    if args.bom:
        slots = parse_bom(args.bom)
        names = expand_slots(args.slots) if args.slots else None
        selected, skipped = select_slots(slots, args.group, names, args.force)
    else:
        if not args.slots:
            raise SpecError("without --bom, pass --slots <ids> and --delivery <spec>")
        delivery = parse_delivery(args.delivery)
        names = expand_slots(args.slots)
        selected = [Slot(slot=name, delivery=delivery) for name in names]
        skipped = []
    if not selected:
        raise SpecError(
            "no generated slots matched: pass --group <prefix> or --slots <ids>, and make sure "
            "the BOM rows carry master and delivery specs"
        )
    if args.delivery:
        override = parse_delivery(args.delivery)
        for slot in selected:
            slot.delivery = override
    if args.grid and args.rows:
        raise SpecError("pass one of --grid COLSxROWS or --rows C1,C2,... - not both")
    overridden = bool(args.grid or args.rows)
    master = None
    if args.grid:
        cols, rows = (int(part) for part in args.grid.lower().split("x"))
        base = selected[0].master
        if base is not None and base.kind == "single":
            raise SpecError(
                f"slot {selected[0].slot} has a single master; --grid only re-cuts sheet plans"
            )
        master = Master(
            width=base.width if base else 0, height=base.height if base else 0,
            kind="sheet", cols=cols, rows=rows, gutter=args.gutter,
        )
    elif args.rows:
        base = selected[0].master
        if base is not None and base.kind == "single":
            raise SpecError(
                f"slot {selected[0].slot} has a single master; --rows only re-cuts sheet plans"
            )
        master = Master(
            width=base.width if base else 0, height=base.height if base else 0,
            kind="sheet", row_counts=_parse_row_counts(args.rows, "--rows"),
        )
    else:
        master = selected[0].master
    if master is None:
        raise SpecError(
            "conform needs a master plan; write `WxH single`, `WxH sheet CxR` or "
            "`WxH sheet rows C1,C2,...` in the BOM's Master column, or pass --grid COLSxROWS / "
            "--rows C1,C2,..."
        )
    if args.bands and master.kind == "single":
        raise SpecError("--bands cuts a sheet; a single master is used whole")
    if master.kind == "single":
        if len(selected) != 1:
            raise SpecError(
                f"a single master holds one slot, but {len(selected)} matched "
                f"({', '.join(slot.slot for slot in selected)}); pass --slots <id>"
            )
        if args.cell:
            raise SpecError("--cell applies to sheet masters; a single master is used whole")
    elif args.cell:
        master.cell = args.cell
    # Slots on one run must share one master plan - but a --grid/--rows override replaces the
    # BOM's plan for this run, so the comparison is between slots, never against the override.
    base = selected[0].master
    if not overridden:
        for slot in selected[1:]:
            if base is None or slot.master is None:
                continue
            if (slot.master.kind != base.kind
                    or slot.master.capacity != base.capacity):
                raise SpecError(
                    f"slot {slot.slot} belongs to a different master plan than "
                    f"{selected[0].slot}; conform one master per run"
                )
    if overridden or not slots:
        peers = selected
    else:
        # Every slot on this master owns a cell, including the ones already shipped: a selection
        # is a subset of the sheet, not a sheet of its own.
        peers = [slot for slot in slots if slot.master is not None
                 and slot.master.kind == master.kind
                 and slot.master.capacity == master.capacity]
    return selected, master, peers, skipped


def _index_of(slot, peers, fallback):
    for index, peer in enumerate(peers):
        if peer.slot == slot.slot:
            return index
    return fallback


def plan_cuts(image, master, count, region, threshold=8, bands=False):
    """[(slot index, box)] for the sheet, and the cut mode used.

    `bands` cuts down the middle of the gutters the image actually has; the even grid divides the
    region into equal cells. A rows master implies band cutting: its rows do not share a pitch.
    """
    if master.banded or bands:
        counts = master.row_counts or [master.cols] * master.rows
        return band_boxes(image, counts, region, threshold), "bands"
    return plan_boxes(master, count, region), "grid"


def estimate_cuts(master, count):
    """Dry-run boxes: an even estimate through the canvas, no image needed."""
    counts = master.row_counts or [master.cols] * master.rows
    boxes = []
    for row, columns in enumerate(counts):
        top = round(row * master.height / len(counts))
        bottom = round((row + 1) * master.height / len(counts))
        for column in range(columns):
            left = round(column * master.width / columns)
            right = round((column + 1) * master.width / columns)
            boxes.append((left, top, right, bottom))
    return boxes[:count]


def align_boxes(boxes, selected, peers):
    """One box per selected slot, by the slot's position on the sheet.

    Selecting four of ten slots must cut *those* cells, not the first four: the sheet does not
    reshuffle because the command asked for a subset.
    """
    picked = []
    for position, slot in enumerate(selected):
        index = _index_of(slot, peers, position)
        if index >= len(boxes):
            raise SpecError(
                f"slot {slot.slot} sits at cell {index + 1} of the plan, which only has "
                f"{len(boxes)} cell(s)"
            )
        picked.append(boxes[index])
    return picked



def _plan(args, selected, boxes):
    planned = []
    for slot, box in zip(selected, boxes):
        for dpr, width, height in slot.delivery.ladder():
            planned.append({
                "slot": slot.slot,
                "box": list(box),
                "dpr": dpr,
                "width": width,
                "height": height,
                "format": slot.delivery.fmt,
                "path": (Path(args.out) / file_name(
                    slot.slot, dpr, width, height, slot.delivery, args.naming
                )).as_posix(),
            })
    return planned


def _keying(value):
    """Return (enabled, colour) for background keying."""
    value = (value or "off").strip().lower()
    if value in ("off", "none", "no"):
        return False, None
    if value == "auto":
        return True, None
    return True, _parse_color(value)


def run(args, result):
    selected, master, peers, skipped = _resolve(args)
    result.skipped = skipped
    result.expected = len(selected)
    result.group = args.group or (expand_slots(args.slots)[0] if args.slots else "")
    banded = master.banded or args.bands

    if args.dry_run:
        if not master.width and master.cell:
            master.width = master.cols * (master.cell + master.gutter) - master.gutter
            master.height = master.rows * (master.cell + master.gutter) - master.gutter
        if banded:
            boxes = estimate_cuts(master, master.capacity)
            result.region = [0, 0, master.width, master.height]
        else:
            boxes = plan_boxes(master, len(peers))
            result.region = [0, 0, master.width, master.height]
        boxes = align_boxes(boxes, selected, peers)
        result.cut = {
            "mode": "bands" if banded else "grid",
            "rows": master.row_counts or [master.cols] * master.rows,
            "estimated": banded,
        }
        problems = []
        for slot, box in zip(selected, boxes):
            if master.width:
                cell = (box[2] - box[0], box[3] - box[1])
            elif master.cell:
                cell = (master.cell, master.cell)
            else:
                cell = None
            if cell is None:
                continue
            problems.extend(f"{slot.slot}: {problem}" for problem in
                            check_feasible(master, slot.delivery, args.allow_upscale, cell))
        if problems:
            raise SpecError("; ".join(problems))
        result.files = _plan(args, selected, boxes)
        result.dry_run = True
        if args.report:
            write_report(args, result, master, boxes)
        else:
            payload = _payload(args, result, master, boxes)
            if args.json:
                print(json.dumps(payload, indent=2))
            else:
                _print_summary(payload, None)
        return result

    _require_pillow()
    from PIL import Image

    if not Path(args.inp).is_file():
        raise SpecError(f"--in must name one generated image file, not {args.inp!r}")
    with Image.open(args.inp) as handle:
        handle.load()
        sheet = handle.copy()
    if sheet.size != (master.width, master.height) and master.width:
        raise SpecError(
            f"{args.inp} is {sheet.width}x{sheet.height} but the sheet plan says "
            f"{master.width}x{master.height}"
        )
    if not master.width or not master.height:
        # No BOM (or a plan without a size): the image is the master, so its size is measured
        # rather than assumed - the report should state what was actually cut.
        master.width, master.height = sheet.width, sheet.height

    # Cut lines go through the content bounds, not the canvas: generated sheets have uneven
    # margins, and dividing the canvas shifts the last column into a subject. A single master is
    # composed art, so it is used whole and keeps its background unless the flags say otherwise.
    single = master.kind == "single"
    trim = (not single) if args.trim is None else args.trim
    key_value = args.key_bg if args.key_bg is not None else ("off" if single else "auto")
    region = (0, 0, sheet.width, sheet.height)
    if not (args.full_canvas or single):
        region = content_box(sheet, args.trim_threshold)
    result.region = list(region)
    boxes, mode = plan_cuts(sheet, master, len(peers), region, args.trim_threshold, args.bands)
    result.cut = {
        "mode": mode,
        "rows": master.row_counts or [master.cols] * master.rows,
    }
    boxes = align_boxes(boxes, selected, peers)

    problems = []
    for slot, box in zip(selected, boxes):
        cell = (box[2] - box[0], box[3] - box[1])
        problems.extend(f"{slot.slot}: {problem}" for problem in
                        check_feasible(master, slot.delivery, args.allow_upscale, cell))
    if problems:
        raise SpecError("; ".join(problems))


    planned = _plan(args, selected, boxes)
    keying, key_color = _keying(key_value)
    pad_color = _parse_color(args.pad_color)
    if keying:
        sheet, keyed, key_reason = _key_sheet(sheet, args.trim_threshold, key_color)
        result.key = {"applied": keyed, "reason": key_reason}
    elif single and args.key_bg is None:
        result.key = {"applied": False, "reason": "single master: keying is off unless --key-bg is passed"}
    background = None if _has_transparency(sheet) else sheet.convert("RGB").getpixel((0, 0))

    for slot, box in zip(selected, boxes):
        cell = sheet.crop(box)
        if trim:
            trimmed = _trim_box(cell, args.trim_threshold, background)
            if trimmed is None:
                if master.capacity == 1:
                    trimmed = (0, 0, cell.width, cell.height)
                else:
                    result.empty_cells.append(slot.slot)
                    continue
            if trimmed != (0, 0, cell.width, cell.height):
                if _touches_interior(trimmed, box, region):
                    result.warnings.append(
                        f"{slot.slot}: subject reaches the cell edge "
                        f"{tuple(trimmed)} of {cell.size}; the cut may clip it"
                    )
                cell = cell.crop(trimmed)
        target_w, target_h = slot.delivery.required_master()
        if (cell.width < target_w or cell.height < target_h) and not args.allow_upscale:
            result.errors.append(
                f"{slot.slot}: subject is {cell.width}x{cell.height} after trim but the spec "
                f"needs {target_w}x{target_h}"
            )
            continue
        pad = "transparent" if slot.delivery.has_alpha() else "color"
        if single and abs(cell.width / cell.height - slot.delivery.ratio()) > 0.01:
            result.warnings.append(
                f"{slot.slot}: master aspect {cell.width}:{cell.height} differs from delivery "
                f"{slot.delivery.width}:{slot.delivery.height}; padded, not cropped - regenerate "
                "at the delivery aspect or crop deliberately with transform.py"
            )
        fitted = _fit(cell, target_w, target_h, pad, pad_color or (255, 255, 255, 255))
        for dpr, width, height in slot.delivery.ladder():
            image = fitted if (width, height) == fitted.size else fitted.resize(
                (width, height), Image.LANCZOS
            )
            path = Path(args.out) / file_name(
                slot.slot, dpr, width, height, slot.delivery, args.naming
            )
            _save(image.copy(), path, slot.delivery)
            result.files.append({
                "slot": slot.slot, "dpr": dpr, "width": width, "height": height,
                "format": slot.delivery.fmt, "path": path.as_posix(),
                "bytes": path.stat().st_size,
            })

    if result.empty_cells and not args.allow_empty:
        result.errors.append(
            f"{len(result.empty_cells)} of {result.expected} cells are empty "
            f"({', '.join(result.empty_cells)}); the sheet does not match the BOM"
        )
    elif not result.errors:
        expected_files = sum(
            len(slot.delivery.dprs) for slot in selected
            if slot.slot not in result.empty_cells
        )
        if len(result.files) != expected_files:
            result.errors.append(
                f"wrote {len(result.files)} files but planned {expected_files}"
            )
    if not args.no_verify and not result.errors:
        verify(selected, result)
    if mode == "grid" and not result.errors:
        cuts = clipped_cuts(content_mask(sheet, args.trim_threshold), region,
                           master.cols, master.rows)
        if cuts:
            total = (master.cols - 1) + (master.rows - 1)
            where = ", ".join(f"{cut['axis']}={cut['at']}" for cut in cuts)
            result.warnings.append(
                f"{len(cuts)} of {total} interior cut line(s) of the even grid land on content "
                f"({where}); the gutters are not even - cut on the measured bands with `--bands` "
                "or plan `sheet rows ...`"
            )
    write_report(args, result, master, boxes)
    return result


def _touches_interior(trimmed, box, region):
    """True when the subject touches a cut line that is not the outer boundary.

    In content-box mode the first and last cells start at the subject's own edge, so touching
    the *outer* boundary proves nothing. Touching a cut line between two cells does: the
    neighbouring cell may hold the rest of that subject.
    """
    left = box[0] + trimmed[0]
    top = box[1] + trimmed[1]
    right = box[0] + trimmed[2]
    bottom = box[1] + trimmed[3]
    if trimmed[0] <= 1 and left > region[0] + 1:
        return True
    if trimmed[2] >= box[2] - box[0] - 1 and right < region[2] - 1:
        return True
    if trimmed[1] <= 1 and top > region[1] + 1:
        return True
    if trimmed[3] >= box[3] - box[1] - 1 and bottom < region[3] - 1:
        return True
    return False


def verify(selected, result):
    from PIL import Image

    by_slot = {}
    for entry in result.files:
        by_slot.setdefault(entry["slot"], []).append(entry)
    for slot in selected:
        entries = by_slot.get(slot.slot, [])
        if not entries:
            if slot.slot in result.empty_cells:
                continue
            result.errors.append(f"{slot.slot}: nothing was written")
            continue
        if len(entries) != len(slot.delivery.dprs):
            result.errors.append(
                f"{slot.slot}: {len(entries)} files written, expected {len(slot.delivery.dprs)}"
            )
            continue
        for entry in entries:
            path = Path(entry["path"])
            if not path.exists():
                result.errors.append(f"{path} is missing after the run")
                continue
            with Image.open(path) as image:
                if image.size != (entry["width"], entry["height"]):
                    result.errors.append(
                        f"{path} is {image.width}x{image.height}, expected "
                        f"{entry['width']}x{entry['height']}"
                    )
                if abs(image.width / image.height - slot.delivery.ratio()) > 0.01:
                    result.errors.append(
                        f"{path} aspect {image.width}:{image.height} does not match "
                        f"{slot.delivery.width}:{slot.delivery.height}"
                    )


# --------------------------------------------------------------------------- reporting


def _payload(args, result, master, boxes):
    return {
        "bom": args.bom,
        "sheet": args.inp,
        "group": result.group,
        "master": {
            "size": [master.width, master.height],
            "kind": master.kind,
            "grid": [master.cols, master.rows],
            "rows": master.row_counts,
            "gutter": master.gutter,
            "cell": list(master.cell_size()),
            "boxes": [list(box) for box in boxes],
        },
        "expected": result.expected,
        "region": result.region,
        "cut": result.cut,
        "key": result.key,

        "empty_cells": result.empty_cells,
        "files": result.files,
        "skipped": result.skipped,
        "warnings": result.warnings,
        "errors": result.errors,
        "ok": result.ok,
    }


def write_report(args, result, master, boxes):
    payload = _payload(args, result, master, boxes)
    path = Path(args.report) if args.report else Path(args.out) / "conform-report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        _print_summary(payload, path)


def _print_summary(payload, report_path):
    master = payload["master"]
    rows = master.get("rows")
    plan = (f"rows {','.join(str(count) for count in rows)}" if rows
            else f"{master['grid'][0]}x{master['grid'][1]} gutter {master['gutter']}")
    print(f"sheet     {payload['sheet']}")
    if master["size"][0]:
        print(f"master    {master['size'][0]}x{master['size'][1]} {master['kind']} "
              f"{plan} cell {master['cell'][0]}x{master['cell'][1]}")
    else:
        # A dry run does not open the image, so a no-BOM plan has no measured size yet.
        print(f"master    {master['kind']} {plan} (size measured at run time)")
    cut = payload.get("cut") or {}
    if cut:
        print(f"cut       {cut.get('mode', 'grid')}"
              f"{' (estimated - measured at run time)' if cut.get('estimated') else ''}")
    print(f"slots     {payload['expected']} expected, {len(payload['files'])} files")

    if payload["region"]:
        print(f"region    {payload['region'][0]},{payload['region'][1]} -> "
              f"{payload['region'][2]},{payload['region'][3]}")
    seen = set()
    for entry in payload["files"]:
        box = entry.get("box") or []
        # The source cell, once per slot: with arbitrary ids this is how a dry run proves that
        # `welcome` really is cell 1 and `error` cell 6.
        where = ""
        if box and entry["slot"] not in seen:
            where = (f"cell {box[0]},{box[1]} "
                     f"{box[2] - box[0]}x{box[3] - box[1]}")
            seen.add(entry["slot"])
        print(f"  {entry['slot']:<20} {where:<20} @{entry['dpr']:g}x "
              f"{entry['width']}x{entry['height']} {entry['format']} -> {entry['path']}")
    for entry in payload["skipped"]:
        print(f"  skip {entry['slot']:<15} {entry['why']}")
    if payload["empty_cells"]:
        print(f"empty     {', '.join(payload['empty_cells'])}")
    for warning in payload["warnings"]:
        print(f"warning   {warning}")
    for error in payload["errors"]:
        print(f"error     {error}")
    if report_path:
        print(f"report    {report_path}")
    print("result    " + ("ok" if payload["ok"] else "FAILED"))


# --------------------------------------------------------------------------- cli


def build_parser():
    parser = argparse.ArgumentParser(
        description="Conform a sheet or single master into the delivery slot files a BOM describes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--bom", help="BOM markdown file with the slot table")
    parser.add_argument("--group", help="select BOM slots by id: an exact id or a `prefix-` "
                                        "match, e.g. onboarding (slot ids are arbitrary; use "
                                        "--slots for names with no shared prefix)")
    parser.add_argument("--slots", help="explicit slot ids, ranges allowed (avatar-01..10)")
    parser.add_argument("--in", dest="inp", required=True, help="the generated master image (one file)")
    parser.add_argument("--out", dest="out", required=True, help="output folder")
    parser.add_argument("--grid", help="override the sheet grid, COLSxROWS")
    parser.add_argument("--rows", help="per-row column counts for a staggered sheet, e.g. "
                                       "8,8,8,10 - cut on the measured gutters")
    parser.add_argument("--bands", action="store_true",
                        help="cut on the measured gutters instead of an even split (a rows plan "
                             "implies this)")
    parser.add_argument("--gutter", type=int, default=0, help="gutter in px (with --grid)")

    parser.add_argument("--cell", type=int, help="override the cell size in px")
    parser.add_argument("--delivery", help="delivery spec applied to every selected slot")
    parser.add_argument("--naming", default="{slot}{ext}",
                        help="filename pattern; tokens {slot} {w} {h} {dpr} {ext}; @Dx is "
                             "appended for dpr > 1 unless the pattern uses {dpr} or {w}")
    parser.add_argument("--trim", action="store_true",
                        help="trim uniform margin before fitting (default: on for sheets, off "
                             "for single masters)")
    parser.add_argument("--no-trim", dest="trim", action="store_false",
                        help="keep the full cell")
    parser.add_argument("--trim-threshold", type=int, default=8,
                        help="pixel difference treated as subject (default: 8)")
    parser.add_argument("--pad-color", help="pad colour for formats without alpha, e.g. #FFFFFF")
    parser.add_argument("--full-canvas", action="store_true",
                        help="divide the whole canvas instead of the content bounds")
    parser.add_argument("--key-bg", nargs="?", const="auto",
                        help="make the border-connected background transparent: auto (default "
                             "for sheets), off (default for single masters), or a #hex seed colour")
    parser.add_argument("--no-key-bg", dest="key_bg", action="store_const", const="off",
                        help="keep the sheet background")
    parser.add_argument("--allow-upscale", action="store_true",
                        help="permit a cell smaller than the delivery master")
    parser.add_argument("--allow-empty", action="store_true",
                        help="write the non-empty cells instead of failing on holes")
    parser.add_argument("--force", action="store_true", help="overwrite slots marked shipped")
    parser.add_argument("--no-verify", action="store_true", help="skip the post-write check")
    parser.add_argument("--report", help="report path (default: <out>/conform-report.json)")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    parser.add_argument("--dry-run", action="store_true", help="print the plan, write nothing")
    parser.set_defaults(trim=None, key_bg=None)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.bom and not args.delivery:
        parser.error("pass --bom <file> or --delivery <spec>")
    if not args.bom and not args.cell and not args.rows and not args.bands:
        # A grid run needs a known pitch; a rows/bands run measures its own, so --cell is noise
        # there and demanding it made the documented rows command fail at the door.
        parser.error(
            "without --bom, pass --rows C1,C2,... or --bands (the image is measured), or "
            "--grid COLSxROWS with --cell <px> so the grid has a known cell size"
        )
    result = Result(bom=args.bom or "", sheet=args.inp, dry_run=args.dry_run)
    try:
        run(args, result)
    except BandError as error:
        print(f"conform: {error}", file=sys.stderr)
        return 3
    except SpecError as error:
        print(f"conform: {error}", file=sys.stderr)
        return 2
    if result.errors:
        print(f"conform: {len(result.errors)} problem(s) - see the report", file=sys.stderr)
        return 3 if result.empty_cells else 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
