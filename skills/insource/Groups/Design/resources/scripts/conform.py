"""Conform a generated sheet into the delivery slot files a project ships.

One render often carries several subjects - ten avatars inside one 2K image. This script reads the
bill of materials (BOM) written by the `collection` skill, slices the sheet into its grid cells,
fits each cell to its slot's delivery spec without distorting it, writes the DPR ladder with the
slot's format and quality, and then verifies every file it produced.

Usage:
    python scripts/conform.py --bom bom/home.md --group avatar --in raw/avatars.png --out assets/avatars
    python scripts/conform.py --bom bom/home.md --slots avatar-01..10 --in raw.png --out out --dry-run
    python scripts/conform.py --in sheet.png --out out --grid 4x4 --cell 512 --gutter 24 \
        --slots a,b --delivery "128x128 1:1 webp q82 @1x,2x"

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

    @property
    def capacity(self):
        return self.cols * self.rows

    def cell_size(self):
        """Smallest cell the grid yields - the conservative size for feasibility checks."""
        if self.cell:
            return self.cell, self.cell
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
    """Parse `2048x2048 sheet 4x4 gutter 24` or `1600x900 single` into a Master."""
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
        elif re.fullmatch(r"\d+x\d+", token) and master.kind == "sheet":
            master.cols, master.rows = (int(part) for part in token.split("x"))
            index += 1
        else:
            raise SpecError(
                f"unrecognised master token {tokens[index]!r} in {text!r}: expected "
                "WxH [single|sheet CxR] [gutter N] [cell N]"
            )
    if master.kind == "sheet" and master.capacity < 1:
        raise SpecError(f"sheet master needs a grid: {text!r}")
    return master


def expand_slots(spec):
    """Expand `avatar-01..10, hero` into concrete slot ids."""
    names = []
    for token in re.split(r"[,\s]+", spec.strip()):
        if not token:
            continue
        match = re.fullmatch(r"(.*?)(\d+)\.\.(\d+)", token)
        if not match:
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
    """Bounding box of the subject, or None when the cell is uniform.

    `background` is the sheet's background colour. Using the sheet colour rather than the
    cell's corner matters when a subject touches the cell edge: the corner would then be the
    subject, and the "subject" would be measured as the gap.
    """
    from PIL import Image, ImageChops

    if image.mode in ("RGBA", "LA") and _has_transparency(image):
        alpha = image.getchannel("A")
        return alpha.point(lambda value: 255 if value > threshold else 0).getbbox()
    rgb = image.convert("RGB")
    colour = background or rgb.getpixel((0, 0))
    reference = Image.new("RGB", rgb.size, colour)
    diff = ImageChops.difference(rgb, reference).convert("L")
    return diff.point(lambda value: 255 if value > threshold else 0).getbbox()


def _has_transparency(image):
    """True when the image has real alpha, not just an alpha channel that is fully opaque."""
    if image.mode not in ("RGBA", "LA"):
        return False
    return image.getchannel("A").getextrema()[0] < 250


def _content_box(image, threshold):
    """Bounds of everything that is not background - where the subjects actually live.

    Generated sheets carry arbitrary margins. Dividing the *content* box into the grid keeps
    every cut line in a gutter, which dividing the raw canvas does not (a wide left margin
    shifts every subject and the last column gets clipped).
    """
    width, height = image.size
    return _trim_box(image, threshold) or (0, 0, width, height)


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
    """Return (selected slots, master) from the BOM and/or the explicit flags."""
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
    master = None
    if args.grid:
        cols, rows = (int(part) for part in args.grid.lower().split("x"))
        base = selected[0].master
        master = Master(
            width=base.width if base else 0, height=base.height if base else 0,
            kind="sheet", cols=cols, rows=rows, gutter=args.gutter,
        )
    else:
        master = selected[0].master
    if master is None or master.kind != "sheet":
        raise SpecError(
            "conform needs a sheet master plan; pass --grid COLSxROWS (with --gutter) or write "
            "a sheet row in the BOM"
        )
    if args.cell:
        master.cell = args.cell
    for slot in selected:
        if slot.master is not None and (slot.master.kind != "sheet"
                                        or slot.master.capacity != master.capacity):
            raise SpecError(
                f"slot {slot.slot} belongs to a different sheet plan than "
                f"{selected[0].slot}; conform one sheet group per run"
            )
    return selected, master, skipped


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


def _keying(args):
    """Return (enabled, colour) for background keying."""
    value = (args.key_bg or "off").strip().lower()
    if value in ("off", "none", "no"):
        return False, None
    if value == "auto":
        return True, None
    return True, _parse_color(value)


def run(args, result):
    selected, master, skipped = _resolve(args)
    result.skipped = skipped
    result.expected = len(selected)
    result.group = args.group or (expand_slots(args.slots)[0] if args.slots else "")

    if args.dry_run:
        if not master.width and master.cell:
            master.width = master.cols * (master.cell + master.gutter) - master.gutter
            master.height = master.rows * (master.cell + master.gutter) - master.gutter
        boxes = plan_boxes(master, len(selected))
        result.region = [0, 0, master.width, master.height]
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

    with Image.open(args.inp) as handle:
        handle.load()
        sheet = handle.copy()
    if sheet.size != (master.width, master.height) and master.width:
        raise SpecError(
            f"{args.inp} is {sheet.width}x{sheet.height} but the sheet plan says "
            f"{master.width}x{master.height}"
        )

    # Cut lines go through the content bounds, not the canvas: generated sheets have uneven
    # margins, and dividing the canvas shifts the last column into a subject.
    region = (0, 0, sheet.width, sheet.height)
    if not args.full_canvas:
        region = _content_box(sheet, args.trim_threshold)
    result.region = list(region)
    boxes = plan_boxes(master, len(selected), region)

    problems = []
    for slot, box in zip(selected, boxes):
        cell = (box[2] - box[0], box[3] - box[1])
        problems.extend(f"{slot.slot}: {problem}" for problem in
                        check_feasible(master, slot.delivery, args.allow_upscale, cell))
    if problems:
        raise SpecError("; ".join(problems))

    planned = _plan(args, selected, boxes)
    keying, key_color = _keying(args)
    pad_color = _parse_color(args.pad_color)
    if keying:
        sheet, keyed, key_reason = _key_sheet(sheet, args.trim_threshold, key_color)
        result.key = {"applied": keyed, "reason": key_reason}
    background = None if _has_transparency(sheet) else sheet.convert("RGB").getpixel((0, 0))

    for slot, box in zip(selected, boxes):
        cell = sheet.crop(box)
        if args.trim:
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
            "gutter": master.gutter,
            "cell": list(master.cell_size()),
            "boxes": [list(box) for box in boxes],
        },
        "expected": result.expected,
        "region": result.region,
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
    print(f"sheet     {payload['sheet']}")
    print(f"master    {master['size'][0]}x{master['size'][1]} {master['kind']} "
          f"{master['grid'][0]}x{master['grid'][1]} gutter {master['gutter']} "
          f"cell {master['cell'][0]}x{master['cell'][1]}")
    print(f"slots     {payload['expected']} expected, {len(payload['files'])} files")
    if payload["region"]:
        print(f"region    {payload['region'][0]},{payload['region'][1]} -> "
              f"{payload['region'][2]},{payload['region'][3]}")
    for entry in payload["files"]:
        print(f"  {entry['slot']:<20} @{entry['dpr']:g}x {entry['width']}x{entry['height']} "
              f"{entry['format']} -> {entry['path']}")
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
        description="Split a generated sheet into the delivery slot files a BOM describes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--bom", help="BOM markdown file with the slot table")
    parser.add_argument("--group", help="slot id prefix to conform, e.g. avatar")
    parser.add_argument("--slots", help="explicit slot ids, ranges allowed (avatar-01..10)")
    parser.add_argument("--in", dest="inp", required=True, help="the generated sheet")
    parser.add_argument("--out", dest="out", required=True, help="output folder")
    parser.add_argument("--grid", help="override the sheet grid, COLSxROWS")
    parser.add_argument("--gutter", type=int, default=0, help="gutter in px (with --grid)")
    parser.add_argument("--cell", type=int, help="override the cell size in px")
    parser.add_argument("--delivery", help="delivery spec applied to every selected slot")
    parser.add_argument("--naming", default="{slot}{ext}",
                        help="filename pattern; tokens {slot} {w} {h} {dpr} {ext}; @Dx is "
                             "appended for dpr > 1 unless the pattern uses {dpr} or {w}")
    parser.add_argument("--trim", action="store_true", default=True,
                        help="trim uniform margin before fitting (default: on)")
    parser.add_argument("--no-trim", dest="trim", action="store_false",
                        help="keep the full cell")
    parser.add_argument("--trim-threshold", type=int, default=8,
                        help="pixel difference treated as subject (default: 8)")
    parser.add_argument("--pad-color", help="pad colour for formats without alpha, e.g. #FFFFFF")
    parser.add_argument("--full-canvas", action="store_true",
                        help="divide the whole canvas instead of the content bounds")
    parser.add_argument("--key-bg", nargs="?", const="auto", default="auto",
                        help="make the border-connected background transparent: auto (default), "
                             "off, or a #hex seed colour")
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
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.bom and not args.delivery:
        parser.error("pass --bom <file> or --delivery <spec>")
    if not args.bom and not args.cell:
        parser.error("without --bom, pass --cell <px> so the grid has a known cell size")
    result = Result(bom=args.bom or "", sheet=args.inp, dry_run=args.dry_run)
    try:
        run(args, result)
    except SpecError as error:
        print(f"conform: {error}", file=sys.stderr)
        return 2
    if result.errors:
        print(f"conform: {len(result.errors)} problem(s) - see the report", file=sys.stderr)
        return 3 if result.empty_cells else 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
