"""Tests for `conform`: BOM parsing, sheet geometry, feasibility, naming and the split/verify run.

    python test_conform.py        # exit 0 = all passed (image checks skip without pillow)

The BOM fixtures mirror the slot table the `collection` skill writes, so a change here is a change
to that contract.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import conform  # noqa: E402

try:
    from PIL import Image
    HAVE_PIL = True
except Exception:  # pragma: no cover - environment dependent
    HAVE_PIL = False

BOM = """# home - image BOM

| Slot | Role | Source | Master | Delivery | Status |
|---|---|---|---|---|---|
| avatar-01..04 | avatar set | generate sheet 2x2 | 1024x1024 sheet 2x2 gutter 0 | 64x64 1:1 png q100 @1x,2x | pending |
| hero-home | hero | generate single | 1600x900 single | 800x450 16:9 webp q82 @1x,2x | pending |
| logo | brand | reuse brand/logo.svg | — | 240x64 - svg | shipped |
| photo-teaser | stock photo | fahlwy | — | 640x360 16:9 jpeg q80 @1x,2x | pending |
"""


def make_sheet(path, size=1024, cells=(0, 1, 2, 3), empty=None):
    """A 2x2 sheet: every cell holds a distinct filled disc, `empty` cells stay flat."""
    image = Image.new("RGB", (size, size), (245, 245, 245))
    cell = size // 2
    for index in cells:
        if empty is not None and index in empty:
            continue
        row, col = divmod(index, 2)
        colour = [(200, 30, 30), (30, 140, 60), (30, 60, 200), (180, 120, 20)][index]
        left, top = col * cell, row * cell
        image.paste(colour, (left + 20, top + 20, left + cell - 20, top + cell - 20))
    image.save(path)


class ParseDeliveryTest(unittest.TestCase):
    def test_full_spec(self):
        delivery = conform.parse_delivery("128x128 1:1 webp q82 @1x,2x,3x")
        self.assertEqual((delivery.width, delivery.height), (128, 128))
        self.assertEqual(delivery.fmt, "webp")
        self.assertEqual(delivery.quality, 82)
        self.assertEqual(delivery.dprs, [1.0, 2.0, 3.0])
        self.assertEqual(delivery.ladder(), [(1.0, 128, 128), (2.0, 256, 256), (3.0, 384, 384)])
        self.assertEqual(delivery.required_master(), (384, 384))

    def test_defaults(self):
        delivery = conform.parse_delivery("64x32")
        self.assertEqual(delivery.fmt, "png")
        self.assertEqual(delivery.dprs, [1.0])
        self.assertIsNone(delivery.quality)

    def test_jpg_normalised(self):
        self.assertEqual(conform.parse_delivery("64x64 jpg").fmt, "jpeg")

    def test_aspect_must_match_size(self):
        with self.assertRaises(conform.SpecError):
            conform.parse_delivery("128x64 1:1 webp")

    def test_rejects_unknown_token(self):
        with self.assertRaises(conform.SpecError):
            conform.parse_delivery("128x128 medium")

    def test_rejects_bad_quality(self):
        with self.assertRaises(conform.SpecError):
            conform.parse_delivery("128x128 q0")


class ParseMasterTest(unittest.TestCase):
    def test_sheet(self):
        master = conform.parse_master("1024x1024 sheet 2x2 gutter 0")
        self.assertEqual((master.width, master.kind, master.capacity), (1024, "sheet", 4))
        self.assertEqual(master.cell_size(), (512, 512))

    def test_gutter_is_subtracted(self):
        master = conform.parse_master("2048x2048 sheet 4x4 gutter 24")
        self.assertEqual(master.cell_size(), (494, 494))

    def test_single(self):
        master = conform.parse_master("1600x900 single")
        self.assertEqual((master.kind, master.capacity), ("single", 1))

    def test_blank_master(self):
        self.assertIsNone(conform.parse_master("-"))

    def test_multi_sheet_plan_is_separate_rows(self):
        # One BOM row is one render. A set spanning several sheets is several rows, each its own
        # conform run - accepting `sheets 4` here would silently cut only the first image.
        with self.assertRaises(conform.SpecError):
            conform.parse_master("1024x1024 sheet 2x2 sheets 4")

    def test_remainder_is_distributed(self):
        master = conform.parse_master("1024x1024 sheet 3x1")
        boxes = conform.plan_boxes(master, 3)
        self.assertEqual(boxes[0][0], 0)
        self.assertEqual(boxes[-1][2], 1024)
        self.assertEqual([box[2] - box[0] for box in boxes], [341, 342, 341])

    def test_rectangular_cells_are_allowed(self):
        master = conform.parse_master("1024x512 sheet 2x2")
        self.assertEqual(master.cell_size(), (512, 256))

    def test_bad_token(self):
        with self.assertRaises(conform.SpecError):
            conform.parse_master("1024x1024 mosaic")


class SlotsTest(unittest.TestCase):
    def test_range_keeps_padding(self):
        self.assertEqual(
            conform.expand_slots("avatar-01..04, hero"),
            ["avatar-01", "avatar-02", "avatar-03", "avatar-04", "hero"],
        )

    def test_range_without_padding(self):
        self.assertEqual(conform.expand_slots("a1..3"), ["a1", "a2", "a3"])

    def test_dedupes(self):
        self.assertEqual(conform.expand_slots("a, a"), ["a"])

    def test_descending_range_refused(self):
        with self.assertRaises(conform.SpecError):
            conform.expand_slots("a5..2")


class BomTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "bom.md"
        self.path.write_text(BOM, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_reads_rows(self):
        slots = conform.parse_bom(self.path)
        self.assertEqual(
            [slot.slot for slot in slots],
            ["avatar-01", "avatar-02", "avatar-03", "avatar-04",
             "hero-home", "logo", "photo-teaser"],
        )
        self.assertEqual(slots[0].delivery.fmt, "png")
        self.assertEqual(slots[0].master.cell_size(), (512, 512))
        self.assertIsNone(slots[5].master)
        self.assertEqual(slots[6].status, "pending")

    def test_range_row_expands_into_cells(self):
        slots = conform.parse_bom(self.path)
        avatars = [slot for slot in slots if slot.slot.startswith("avatar-")]
        self.assertEqual(len(avatars), 4)
        self.assertEqual(len({id(slot.master) for slot in avatars}), 1)

    def test_selection_by_group(self):
        slots = conform.parse_bom(self.path)
        selected, _ = conform.select_slots(slots, group="avatar")
        self.assertEqual([slot.slot for slot in selected],
                         ["avatar-01", "avatar-02", "avatar-03", "avatar-04"])

    def test_selection_skips_non_generated(self):
        slots = conform.parse_bom(self.path)
        selected, skipped = conform.select_slots(slots)
        self.assertEqual([slot.slot for slot in selected],
                         ["avatar-01", "avatar-02", "avatar-03", "avatar-04", "hero-home"])
        self.assertEqual({entry["slot"] for entry in skipped}, {"logo", "photo-teaser"})

    def test_missing_table_is_explained(self):
        empty = Path(self.tmp.name) / "empty.md"
        empty.write_text("# nothing here\n", encoding="utf-8")
        with self.assertRaises(conform.SpecError) as caught:
            conform.parse_bom(empty)
        self.assertIn("slot table", str(caught.exception))


class GeometryTest(unittest.TestCase):
    def test_boxes_are_row_major(self):
        master = conform.parse_master("1024x1024 sheet 2x2 gutter 0")
        self.assertEqual(
            conform.plan_boxes(master, 4),
            [(0, 0, 512, 512), (512, 0, 1024, 512), (0, 512, 512, 1024), (512, 512, 1024, 1024)],
        )

    def test_gutter_between_cells(self):
        master = conform.parse_master("1024x1024 sheet 2x2 gutter 16")
        self.assertEqual(conform.plan_boxes(master, 2), [(0, 0, 504, 504), (520, 0, 1024, 504)])

    def test_more_slots_than_cells_is_refused(self):
        master = conform.parse_master("1024x1024 sheet 2x2")
        with self.assertRaises(conform.SpecError):
            conform.plan_boxes(master, 5)

    def test_feasibility(self):
        master = conform.parse_master("1024x1024 sheet 2x2")
        small = conform.parse_delivery("128x128 1:1 webp @1x,2x,3x")
        self.assertEqual(conform.check_feasible(master, small), [])
        big = conform.parse_delivery("512x512 1:1 webp @1x,2x,3x")
        self.assertEqual(len(conform.check_feasible(master, big)), 1)
        self.assertEqual(conform.check_feasible(master, big, allow_upscale=True), [])


class NamingTest(unittest.TestCase):
    def test_default_adds_dpr_suffix(self):
        delivery = conform.parse_delivery("128x128 webp @1x,2x")
        self.assertEqual(conform.file_name("avatar-01", 1.0, 128, 128, delivery, "{slot}{ext}"),
                         "avatar-01.webp")
        self.assertEqual(conform.file_name("avatar-01", 2.0, 256, 256, delivery, "{slot}{ext}"),
                         "avatar-01@2x.webp")

    def test_width_pattern_needs_no_suffix(self):
        delivery = conform.parse_delivery("128x128 webp @1x,2x")
        self.assertEqual(
            conform.file_name("hero", 2.0, 256, 256, delivery, "{slot}-{w}{ext}"),
            "hero-256.webp",
        )

    def test_dpr_token(self):
        delivery = conform.parse_delivery("128x128 webp @1x,2x")
        self.assertEqual(
            conform.file_name("hero", 2.0, 256, 256, delivery, "{slot}-{dpr}{ext}"),
            "hero-2x.webp",
        )


class DryRunTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.bom = self.root / "bom.md"
        self.bom.write_text(BOM, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def run_main(self, *argv):
        return conform.main(list(argv))

    def test_plans_the_avatar_ladder_without_writing(self):
        code = self.run_main("--bom", str(self.bom), "--group", "avatar",
                             "--in", "sheet.png", "--out", str(self.root / "out"), "--dry-run")
        self.assertEqual(code, 0)
        self.assertFalse((self.root / "out").exists())

    def test_plan_is_json_serialisable(self):
        master = conform.Master(1024, 1024, kind="sheet", cols=2, rows=2)
        slot = conform.Slot(
            slot="avatar-01",
            master=master,
            delivery=conform.parse_delivery("64x64 png @1x,2x"),
        )
        result = conform.Result(sheet="sheet.png", expected=1)
        result.files.append({"slot": "avatar-01", "box": [0, 0, 512, 512], "dpr": 1.0,
                            "width": 64, "height": 64, "format": "png", "path": "out/a.png"})
        args = conform.build_parser().parse_args([
            "--in", "sheet.png", "--out", "out", "--grid", "2x2", "--cell", "512",
            "--slots", "avatar-01", "--delivery", "64x64 png @1x,2x", "--dry-run",
        ])
        payload = conform._payload(args, result, master, conform.plan_boxes(master, 1))
        self.assertEqual(json.loads(json.dumps(payload))["files"][0]["slot"], slot.slot)

    def test_group_without_match_fails(self):
        code = self.run_main("--bom", str(self.bom), "--group", "nope",
                             "--in", "sheet.png", "--out", str(self.root / "out"), "--dry-run")
        self.assertEqual(code, 2)

    def test_missing_bom_and_delivery_fails(self):
        with self.assertRaises(SystemExit):
            self.run_main("--in", "sheet.png", "--out", str(self.root / "out"))

    def test_grid_without_bom_needs_cell(self):
        with self.assertRaises(SystemExit):
            self.run_main("--in", "sheet.png", "--out", str(self.root / "out"),
                          "--grid", "2x2", "--slots", "a,b", "--delivery", "64x64 png")

    def test_grid_override_with_cell_plans(self):
        code = self.run_main("--in", "sheet.png", "--out", str(self.root / "out"),
                             "--grid", "2x2", "--cell", "64", "--slots", "a,b",
                             "--delivery", "32x32 png @1x,2x", "--dry-run", "--json")
        self.assertEqual(code, 0)


@unittest.skipUnless(HAVE_PIL, "pillow is not installed")
class ConformRunTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.bom = self.root / "bom.md"
        self.bom.write_text(BOM, encoding="utf-8")
        self.sheet = self.root / "sheet.png"
        self.out = self.root / "out"

    def tearDown(self):
        self.tmp.cleanup()

    def run_main(self, *argv):
        return conform.main(list(argv))

    def test_splits_four_avatars_and_writes_the_ladder(self):
        make_sheet(self.sheet)
        code = self.run_main("--bom", str(self.bom), "--slots", "avatar-01..04",
                             "--in", str(self.sheet), "--out", str(self.out), "--json")
        self.assertEqual(code, 0)
        for index in range(1, 5):
            for suffix, size in (("", 64), ("@2x", 128)):
                path = self.out / f"avatar-0{index}{suffix}.png"
                self.assertTrue(path.exists(), path)
                with Image.open(path) as image:
                    self.assertEqual(image.size, (size, size))
        report = json.loads((self.out / "conform-report.json").read_text(encoding="utf-8"))
        self.assertTrue(report["ok"])
        self.assertEqual(report["master"]["cell"], [512, 512])
        self.assertEqual(report["expected"], 4)
        self.assertEqual(len(report["files"]), 8)

    def test_padding_keeps_aspect(self):
        self.bom.write_text(
            "| Slot | Master | Delivery |\n|---|---|---|\n"
            "| wide | 1024x1024 sheet 1x1 | 200x200 png |\n",
            encoding="utf-8",
        )
        image = Image.new("RGB", (1024, 1024), (255, 255, 255))
        image.paste((10, 10, 10), (312, 412, 712, 612))
        image.save(self.sheet)
        code = self.run_main("--bom", str(self.bom), "--slots", "wide",
                             "--in", str(self.sheet), "--out", str(self.out))
        self.assertEqual(code, 0)
        with Image.open(self.out / "wide.png") as written:
            self.assertEqual(written.size, (200, 200))
            self.assertEqual(written.mode, "RGBA")
            self.assertEqual(written.getpixel((0, 0))[3], 0)

    def test_empty_cell_stops_the_run(self):
        make_sheet(self.sheet, empty=[3])
        code = self.run_main("--bom", str(self.bom), "--slots", "avatar-01..04",
                             "--in", str(self.sheet), "--out", str(self.out), "--json")
        self.assertEqual(code, 3)
        report = json.loads((self.out / "conform-report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["empty_cells"], ["avatar-04"])
        self.assertFalse(report["ok"])

    def test_allow_empty_writes_the_rest(self):
        make_sheet(self.sheet, empty=[2])
        code = self.run_main("--bom", str(self.bom), "--slots", "avatar-01..04",
                             "--in", str(self.sheet), "--out", str(self.out), "--allow-empty")
        self.assertEqual(code, 0)
        self.assertTrue((self.out / "avatar-01.png").exists())
        self.assertFalse((self.out / "avatar-03.png").exists())

    def test_sheet_size_must_match_the_plan(self):
        make_sheet(self.sheet, size=512)
        code = self.run_main("--bom", str(self.bom), "--slots", "avatar-01..04",
                             "--in", str(self.sheet), "--out", str(self.out))
        self.assertEqual(code, 2)

    def test_cut_lines_follow_content_not_canvas(self):
        sheet = Image.new("RGB", (400, 200), (255, 255, 255))
        sheet.paste((10, 10, 10), (10, 50, 90, 130))
        sheet.paste((20, 20, 120), (150, 50, 230, 130))
        self.assertEqual(conform._content_box(sheet, 8), (10, 50, 230, 130))
        master = conform.Master(400, 200, kind="sheet", cols=2, rows=1)
        content = conform.plan_boxes(master, 2, (10, 50, 230, 130))
        canvas = conform.plan_boxes(master, 2)
        self.assertEqual(content, [(10, 50, 120, 130), (120, 50, 230, 130)])
        self.assertEqual(canvas[1][0], 200)
        # The canvas cut at x=200 lands inside the second subject (150-230); the content cut
        # at x=120 lands in the gap.
        self.assertGreater(canvas[1][0], 150)
        self.assertLess(content[1][0], 150)

    def test_background_keying_keeps_interior_white(self):
        from PIL import ImageDraw

        sheet = Image.new("RGB", (300, 300), (255, 255, 255))
        draw = ImageDraw.Draw(sheet)
        draw.ellipse((50, 50, 250, 250), fill=(30, 30, 30))
        draw.rectangle((145, 145, 155, 155), fill=(255, 255, 255))
        keyed, applied, reason = conform._key_sheet(sheet, 8)
        self.assertTrue(applied, reason)
        self.assertEqual(keyed.getpixel((0, 0))[3], 0)
        self.assertEqual(keyed.getpixel((150, 150)), (255, 255, 255, 255))
        self.assertEqual(conform._trim_box(keyed, 8), (50, 50, 251, 251))

    def test_keying_is_skipped_for_a_flat_sheet(self):
        keyed, applied, reason = conform._key_sheet(Image.new("RGB", (50, 50), (9, 9, 9)), 8)
        self.assertFalse(applied)
        self.assertIn("flat", reason)
        self.assertEqual(keyed.size, (50, 50))

    def test_touching_cell_edge_warns(self):
        self.bom.write_text(
            "| Slot | Master | Delivery |\n|---|---|---|\n"
            "| a,b,c | 300x100 sheet 3x1 | 50x50 png |\n",
            encoding="utf-8",
        )
        sheet = Image.new("RGB", (300, 100), (255, 255, 255))
        sheet.paste((40, 40, 40), (0, 20, 90, 90))
        sheet.paste((40, 40, 40), (110, 20, 210, 90))
        sheet.paste((40, 40, 40), (220, 20, 300, 90))
        sheet.save(self.sheet)
        code = self.run_main("--bom", str(self.bom), "--slots", "a,b,c",
                             "--in", str(self.sheet), "--out", str(self.out))
        self.assertEqual(code, 0)
        report = json.loads((self.out / "conform-report.json").read_text(encoding="utf-8"))
        self.assertTrue(report["warnings"])
        self.assertIn("cell edge", report["warnings"][0])
        # The subject that spans the 100px cut is the one flagged; the outer cells are not.
        flagged = {warning.split(":")[0] for warning in report["warnings"]}
        self.assertNotIn("a", flagged)
        self.assertNotIn("c", flagged)

    def test_subject_smaller_than_spec_fails(self):
        self.bom.write_text(
            "| Slot | Master | Delivery |\n|---|---|---|\n"
            "| tiny | 256x256 sheet 1x1 | 256x256 png @1x |\n",
            encoding="utf-8",
        )
        make_sheet(self.sheet, size=256)
        code = self.run_main("--bom", str(self.bom), "--slots", "tiny",
                             "--in", str(self.sheet), "--out", str(self.out),
                             "--full-canvas")
        self.assertEqual(code, 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
