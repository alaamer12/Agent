"""Tests for `sheet_probe`: content bounds, band detection, cell measurement, delivery ceiling.

    python test_sheet_probe.py     # exit 0 = all passed (image checks skip without pillow)
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

import sheet_probe  # noqa: E402

try:
    from PIL import Image
    HAVE_PIL = True
except Exception:  # pragma: no cover - environment dependent
    HAVE_PIL = False


@unittest.skipUnless(HAVE_PIL, "pillow is not installed")
class ProbeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def make(self, name, size, blocks, background=(255, 255, 255)):
        image = Image.new("RGB", size, background)
        for box in blocks:
            image.paste((20, 20, 30), box)
        path = self.root / name
        image.save(path)
        return path

    def test_content_box_ignores_margins(self):
        image = Image.new("RGB", (400, 200), (255, 255, 255))
        image.paste((10, 10, 10), (10, 50, 90, 130))
        image.paste((10, 10, 10), (150, 50, 230, 130))
        self.assertEqual(sheet_probe.content_box(image), (10, 50, 230, 130))

    def test_bands_find_each_subject(self):
        image = Image.new("RGB", (300, 200), (255, 255, 255))
        for column in range(3):
            image.paste((0, 0, 0), (column * 100 + 10, 20, column * 100 + 90, 180))
        mask = sheet_probe.content_mask(image)
        columns = sheet_probe.bands(mask, "x")
        rows = sheet_probe.bands(mask, "y")
        self.assertEqual(columns.count, 3)
        self.assertEqual(rows.count, 1)
        self.assertTrue(columns.regular)

    def test_uneven_gutters_are_reported(self):
        image = Image.new("RGB", (300, 100), (255, 255, 255))
        image.paste((0, 0, 0), (0, 10, 40, 90))
        image.paste((0, 0, 0), (60, 10, 100, 90))
        image.paste((0, 0, 0), (220, 10, 300, 90))
        columns = sheet_probe.bands(sheet_probe.content_mask(image), "x")
        self.assertFalse(columns.regular)

    def test_split_boxes_distributes_the_remainder(self):
        boxes = sheet_probe.split_boxes((0, 0, 100, 100), 3, 1)
        self.assertEqual([box[2] - box[0] for box in boxes], [33, 34, 33])
        self.assertEqual(boxes[-1][2], 100)

    def test_feasibility_lists_only_what_fits(self):
        result = sheet_probe.feasibility(269)
        self.assertEqual(result["fits"][128], [1, 2])
        self.assertEqual(result["fits"][256], [1])
        self.assertNotIn(384, result["fits"])
        self.assertIn(384, result["rejected"])

    def test_probe_reports_cells_subjects_and_verdict(self):
        sheet = self.make("sheet.png", (320, 200), [
            (10, 20, 90, 100), (110, 20, 190, 100), (210, 20, 290, 100),
            (10, 110, 90, 190), (110, 110, 190, 190), (210, 110, 290, 190),
        ])
        report = sheet_probe.probe(sheet, 3, 2, "128x128 1:1 png @1x")
        self.assertEqual(report["size"], [320, 200])
        self.assertEqual(report["grid"], {"columns": 3, "rows": 2, "cell": [93, 85]})
        self.assertEqual(report["subject"]["count"], 6)
        self.assertEqual(report["subject"]["min"], [80, 80])
        self.assertEqual(report["empty_cells"], [])
        self.assertEqual(report["delivery_ceiling"]["max_square_master"], 80)
        self.assertTrue(report["verdict"])
        json.dumps(report)

    def test_empty_cell_is_reported(self):
        sheet = self.make("holes.png", (300, 100), [(10, 10, 90, 90), (210, 10, 290, 90)])
        report = sheet_probe.probe(sheet, 3, 1)
        self.assertEqual(len(report["cells"]), 3)
        self.assertEqual(report["empty_cells"], [1])
        self.assertTrue(any("empty" in note for note in report["verdict"]))

    def test_missing_file_is_an_error(self):
        with self.assertRaises(sheet_probe.ProbeError):
            sheet_probe.probe(self.root / "nope.png")


if __name__ == "__main__":
    unittest.main(verbosity=2)
