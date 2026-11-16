"""Tests for `contact_sheet`: collection, edge measurement, composition and the report.

    python test_contact_sheet.py     # exit 0 = all passed (image checks skip without pillow)
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

import contact_sheet  # noqa: E402

try:
    from PIL import Image
    HAVE_PIL = True
except Exception:  # pragma: no cover - environment dependent
    HAVE_PIL = False


@unittest.skipUnless(HAVE_PIL, "pillow is not installed")
class ReviewTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def disc(self, name, size=64, background=(255, 255, 255), radius=None):
        from PIL import ImageDraw

        image = Image.new("RGB", (size, size), background)
        inset = size // 8 if radius is None else radius
        ImageDraw.Draw(image).ellipse((inset, inset, size - inset, size - inset),
                                      fill=(30, 30, 40))
        path = self.root / name
        image.save(path)
        return path

    def test_analyse_reads_alpha_edges(self):
        path = self.root / "slot.png"
        image = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
        from PIL import ImageDraw
        ImageDraw.Draw(image).ellipse((4, 4, 35, 35), fill=(30, 30, 40, 255))
        image.save(path)
        record = contact_sheet.analyse(path)
        self.assertTrue(record["alpha"])
        self.assertEqual(record["corner_alpha"], 0)
        self.assertGreater(record["transparent_share"], 0.15)
        self.assertLess(record["border_opaque"], 0.5)
        self.assertEqual((record["width"], record["height"]), (40, 40))

    def test_analyse_flags_an_opaque_border(self):
        path = self.root / "unkeyed.png"
        Image.new("RGBA", (20, 20), (250, 250, 250, 255)).save(path)
        record = contact_sheet.analyse(path)
        self.assertEqual(record["border_opaque"], 1.0)
        self.assertIn("fully opaque", record["note"])

    def test_analyse_notes_a_file_without_alpha(self):
        record = contact_sheet.analyse(self.disc("flat.png"))
        self.assertFalse(record["alpha"])
        self.assertIsNone(record["transparent_share"])
        self.assertIn("no alpha channel", record["note"])

    def test_collect_filters_and_skips_density(self):
        self.disc("a.png")
        self.disc("a@2x.png")
        self.disc("b.webp")
        (self.root / "notes.txt").write_text("not an image", encoding="utf-8")
        paths = contact_sheet.collect(self.root)
        self.assertEqual([path.name for path in paths], ["a.png", "a@2x.png", "b.webp"])
        base = contact_sheet.collect(self.root, skip_density=True)
        self.assertEqual([path.name for path in base], ["a.png", "b.webp"])

    def test_collect_refuses_an_empty_folder(self):
        (self.root / "notes.txt").write_text("no images", encoding="utf-8")
        with self.assertRaises(contact_sheet.ReviewError):
            contact_sheet.collect(self.root)

    def test_compose_writes_a_labelled_grid(self):
        paths = [self.disc(f"slot-{index}.png") for index in range(5)]
        records = [contact_sheet.analyse(path) for path in paths]
        out = self.root / "review.png"
        contact_sheet.compose(records, out, tile=48, columns=3, gap=8)
        with Image.open(out) as sheet:
            self.assertEqual(sheet.size, (3 * (48 + 8) + 8, 2 * (48 + 14 + 8) + 8))
            self.assertEqual(sheet.mode, "RGB")

    def test_report_flags_only_suspicious_files(self):
        good = contact_sheet.analyse(self.disc("good.png"))
        bad_path = self.root / "bad.png"
        Image.new("RGBA", (20, 20), (250, 250, 250, 255)).save(bad_path)
        bad = contact_sheet.analyse(bad_path)
        report = contact_sheet.build_report([good, bad], self.root / "sheet.png")
        self.assertFalse(report["ok"])
        self.assertEqual(report["flagged"], ["bad"])
        self.assertEqual(report["count"], 2)
        json.dumps(report)

    def test_missing_file_is_an_error(self):
        with self.assertRaises(contact_sheet.ReviewError):
            contact_sheet.collect(files=[self.root / "nope.png"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
