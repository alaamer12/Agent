#!/usr/bin/env python3
"""
similarity.py — multi-method image similarity engine for parity diagnosis.

A single similarity number cannot tell you *why* two renders differ. This engine
runs five independent techniques and keeps their scores separate, because each
one fails on a different kind of difference:

  1. pixel       MSE + normalized cross-correlation — literal per-pixel distance
  2. ssim        structural similarity with a Gaussian window — layout/shape
  3. histogram   HSV per-channel correlation — colour distribution
  4. hash        aHash / pHash / dHash — robustness to resize/compression
  5. orb         ORB keypoint matching — robustness to crop/rotation/viewpoint

On top of the scores it localises the difference:

  * a humanized 3x3 regional breakdown,
  * an arbitrary NxN numeric score grid with the worst cells' pixel boxes,
  * a dominant-colour palette comparison (k-means) that separates "wrong
    colours" from "wrong layout",
  * a jet-colormap diff heatmap overlaid on image A.

Resize strategies (``--resize-mode``):
  stretch  resize both to the smaller size (fast; distorts aspect ratio)
  pad      letterbox into the target box (default; no distortion, no crop)
  crop     cover the box then centre-crop (no distortion, content lost)

Usage:
    python similarity.py design.png app.png
    python similarity.py design.png app.png --resize-mode pad --json
    python similarity.py design.png app.png --regional-score 6 --palette 8 \
        --heatmap-out diff.png
    python similarity.py design.png app.png --methods ssim,histogram,hash \
        --fail-under 0.90

Requires: numpy, opencv-python(-headless), scikit-image, imagehash, pillow
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import cv2
from PIL import Image
import imagehash
from skimage.metrics import structural_similarity as ssim


# --------------------------------------------------------------------------- #
# Data structures
# --------------------------------------------------------------------------- #

@dataclass
class SimilarityReport:
    resize_mode: str
    final_size: tuple
    scores: dict = field(default_factory=dict)
    overall_score: Optional[float] = None
    region_breakdown: Optional[list] = None
    region_report_text: Optional[str] = None
    heatmap_path: Optional[str] = None
    regional_score_grid: Optional[dict] = None
    palette_report: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "resize_mode": self.resize_mode,
            "compared_at_size": self.final_size,
            "scores": self.scores,
            "overall_similarity": self.overall_score,
            "region_breakdown": self.region_breakdown,
            "region_report": self.region_report_text,
            "heatmap_image": self.heatmap_path,
            "regional_score": self.regional_score_grid,
            "palette": self.palette_report,
        }

    def pretty_print(self) -> None:
        print("=" * 56)
        print(" IMAGE SIMILARITY REPORT")
        print("=" * 56)
        print(f" Resize mode     : {self.resize_mode}")
        print(f" Compared size   : {self.final_size[0]}x{self.final_size[1]}")
        print("-" * 56)
        for name, val in self.scores.items():
            if isinstance(val, dict):
                print(f" {name}:")
                for k, v in val.items():
                    print(f"    - {k:<18}: {v:.4f}")
            else:
                print(f" {name:<20}: {val:.4f}")
        print("-" * 56)
        if self.overall_score is not None:
            verdict = _verdict(self.overall_score)
            print(f" OVERALL SCORE     : {self.overall_score:.4f}  ({verdict})")
        if self.regional_score_grid:
            print("-" * 56)
            print(_format_regional_score(self.regional_score_grid))
        if self.palette_report:
            print("-" * 56)
            print(_format_palette(self.palette_report))
        if self.region_report_text:
            print("-" * 56)
            print(self.region_report_text)
        if self.heatmap_path:
            print("-" * 56)
            print(f" Heatmap saved to  : {self.heatmap_path}")
        print("=" * 56)


def _verdict(score: float) -> str:
    if score >= 0.95:
        return "near-identical"
    if score >= 0.85:
        return "very similar"
    if score >= 0.65:
        return "moderately similar"
    if score >= 0.40:
        return "somewhat different"
    return "very different"


# --------------------------------------------------------------------------- #
# Loading & resizing
# --------------------------------------------------------------------------- #

def load_image(path: str) -> np.ndarray:
    """Load an image as an RGB ``uint8`` numpy array."""
    img = Image.open(path).convert("RGB")
    return np.array(img)


def resize_to_match(a: np.ndarray, b: np.ndarray, mode: str = "stretch") -> tuple:
    """Bring two differently-sized images to one shape (see module docstring)."""
    ha, wa = a.shape[:2]
    hb, wb = b.shape[:2]
    target_w, target_h = min(wa, wb), min(ha, hb)

    if mode == "stretch":
        a_r = cv2.resize(a, (target_w, target_h), interpolation=cv2.INTER_AREA)
        b_r = cv2.resize(b, (target_w, target_h), interpolation=cv2.INTER_AREA)
        return a_r, b_r, (target_w, target_h)

    if mode == "pad":
        a_r = _resize_letterbox(a, target_w, target_h)
        b_r = _resize_letterbox(b, target_w, target_h)
        return a_r, b_r, (target_w, target_h)

    if mode == "crop":
        a_r = _resize_center_crop(a, target_w, target_h)
        b_r = _resize_center_crop(b, target_w, target_h)
        return a_r, b_r, (target_w, target_h)

    raise ValueError(f"Unknown resize mode: {mode}")


def _resize_letterbox(img: np.ndarray, target_w: int, target_h: int) -> np.ndarray:
    h, w = img.shape[:2]
    scale = min(target_w / w, target_h / h)
    new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
    x_off = (target_w - new_w) // 2
    y_off = (target_h - new_h) // 2
    canvas[y_off:y_off + new_h, x_off:x_off + new_w] = resized
    return canvas


def _resize_center_crop(img: np.ndarray, target_w: int, target_h: int) -> np.ndarray:
    h, w = img.shape[:2]
    scale = max(target_w / w, target_h / h)
    new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    x_off = (new_w - target_w) // 2
    y_off = (new_h - target_h) // 2
    return resized[y_off:y_off + target_h, x_off:x_off + target_w]


# --------------------------------------------------------------------------- #
# Comparison methods
# --------------------------------------------------------------------------- #

def compare_pixel(a: np.ndarray, b: np.ndarray) -> dict:
    """MSE-based similarity + normalized cross-correlation."""
    a_f = a.astype(np.float64)
    b_f = b.astype(np.float64)

    mse = np.mean((a_f - b_f) ** 2)
    mse_similarity = 1.0 / (1.0 + mse / 255.0)

    a_flat = a_f.flatten() - a_f.mean()
    b_flat = b_f.flatten() - b_f.mean()
    denom = (np.linalg.norm(a_flat) * np.linalg.norm(b_flat))
    ncc = float(np.dot(a_flat, b_flat) / denom) if denom != 0 else 0.0
    ncc_similarity = (ncc + 1) / 2

    return {
        "mse": float(mse),
        "mse_similarity": float(mse_similarity),
        "cross_correlation": float(ncc_similarity),
    }


def compare_ssim(a: np.ndarray, b: np.ndarray, kernel_size: int = 7) -> float:
    """SSIM (Gaussian-weighted window) over luminance, contrast and structure."""
    a_gray = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY)
    b_gray = cv2.cvtColor(b, cv2.COLOR_RGB2GRAY)
    score, _ = ssim(a_gray, b_gray, win_size=kernel_size, full=True)
    return float(score)


def compare_histogram(a: np.ndarray, b: np.ndarray, bins: int = 64) -> dict:
    """Per-channel HSV histogram correlation (hue-weighted)."""
    a_hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV)
    b_hsv = cv2.cvtColor(b, cv2.COLOR_RGB2HSV)

    results = {}
    for i, ch_name in enumerate(["hue", "saturation", "value"]):
        hist_a = cv2.calcHist([a_hsv], [i], None, [bins], [0, 256])
        hist_b = cv2.calcHist([b_hsv], [i], None, [bins], [0, 256])
        cv2.normalize(hist_a, hist_a)
        cv2.normalize(hist_b, hist_b)
        corr = cv2.compareHist(hist_a, hist_b, cv2.HISTCMP_CORREL)
        results[ch_name] = float(max(0.0, corr))

    results["combined"] = float(np.mean(list(results.values())))
    return results


def compare_hash(a: np.ndarray, b: np.ndarray) -> dict:
    """Perceptual hashing (aHash/pHash/dHash) via Hamming distance."""
    img_a = Image.fromarray(a)
    img_b = Image.fromarray(b)

    results = {}
    for name, fn in [
        ("average_hash", imagehash.average_hash),
        ("perceptual_hash", imagehash.phash),
        ("difference_hash", imagehash.dhash),
    ]:
        ha, hb = fn(img_a), fn(img_b)
        max_bits = len(ha.hash) ** 2
        dist = ha - hb
        results[name] = float(1.0 - (dist / max_bits))

    results["combined"] = float(np.mean(list(results.values())))
    return results


def compare_orb_features(a: np.ndarray, b: np.ndarray, max_features: int = 500) -> dict:
    """ORB keypoints + Lowe-ratio descriptor matching.

    Robust to cropping, rotation and viewpoint changes, unlike pixel/hash
    methods. A low ``match_ratio`` on an otherwise high-SSIM pair usually means
    the pair shares structure but not local texture (e.g. different icon set).
    """
    a_gray = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY)
    b_gray = cv2.cvtColor(b, cv2.COLOR_RGB2GRAY)

    orb = cv2.ORB_create(nfeatures=max_features)
    kp_a, des_a = orb.detectAndCompute(a_gray, None)
    kp_b, des_b = orb.detectAndCompute(b_gray, None)

    if des_a is None or des_b is None or len(kp_a) == 0 or len(kp_b) == 0:
        return {"good_matches": 0, "keypoints_a": len(kp_a or []),
                "keypoints_b": len(kp_b or []), "match_ratio": 0.0}

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    matches = bf.knnMatch(des_a, des_b, k=2)

    good = []
    for pair in matches:
        if len(pair) == 2:
            m, n = pair
            if m.distance < 0.75 * n.distance:
                good.append(m)

    match_ratio = len(good) / max(1, min(len(kp_a), len(kp_b)))
    return {
        "keypoints_a": len(kp_a),
        "keypoints_b": len(kp_b),
        "good_matches": len(good),
        "match_ratio": float(min(1.0, match_ratio)),
    }


# --------------------------------------------------------------------------- #
# Regional breakdown + heatmap
# --------------------------------------------------------------------------- #

REGION_LABELS = [
    ["top-left", "top", "top-right"],
    ["mid-left", "mid", "mid-right"],
    ["bottom-left", "bottom", "bottom-right"],
]


def compute_diff_map(
    a: np.ndarray, b: np.ndarray, ssim_weight: float = 0.6,
    pixel_weight: float = 0.4, kernel_size: int = 7,
) -> np.ndarray:
    """Per-pixel dissimilarity map (0 identical, 1 maximally different).

    Blends local structural dissimilarity with raw luminance difference so it
    flags both "structurally different here" and "literally a different colour".
    """
    gray_a = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY)
    gray_b = cv2.cvtColor(b, cv2.COLOR_RGB2GRAY)

    _, ssim_map = ssim(gray_a, gray_b, win_size=kernel_size, full=True)
    ssim_diff = 1.0 - np.clip(ssim_map, 0.0, 1.0)

    pixel_diff = np.abs(gray_a.astype(np.float64) - gray_b.astype(np.float64)) / 255.0

    combined = ssim_weight * ssim_diff + pixel_weight * pixel_diff
    return np.clip(combined, 0.0, 1.0)


def regional_breakdown(diff_map: np.ndarray, grid_rows: int = 3,
                       grid_cols: int = 3) -> list:
    """Split the diff map into a named 3x3 grid and score each region."""
    regions = []
    for r_idx, row_block in enumerate(np.array_split(diff_map, grid_rows, axis=0)):
        for c_idx, cell in enumerate(np.array_split(row_block, grid_cols, axis=1)):
            mean_diff = float(np.mean(cell))
            regions.append({
                "region": REGION_LABELS[r_idx][c_idx],
                "dissimilarity": mean_diff,
                "similarity": 1.0 - mean_diff,
            })
    return regions


def regional_score_grid(diff_map: np.ndarray, grid: int = 4) -> dict:
    """Numeric per-cell similarity on an NxN grid, plus the worst cells' boxes.

    The named 3x3 split is too coarse to separate "component styled wrong" from
    "component a few pixels off". A finer grid localises the offending band, and
    the emitted boxes are exactly what ``region_crop.py`` needs to produce a
    targeted crop pair.
    """
    cells = []
    for r_idx, row_block in enumerate(np.array_split(diff_map, grid, axis=0)):
        row = []
        for c_idx, cell in enumerate(np.array_split(row_block, grid, axis=1)):
            row.append(1.0 - float(np.mean(cell)))
        cells.append(row)

    height, width = diff_map.shape
    flat = [
        {
            "row": r,
            "col": c,
            "similarity": cells[r][c],
            "box": [
                int(width * c / grid), int(height * r / grid),
                int(width * (c + 1) / grid), int(height * (r + 1) / grid),
            ],
        }
        for r in range(grid) for c in range(grid)
    ]
    return {"grid": grid, "cells": cells,
            "worst": sorted(flat, key=lambda x: x["similarity"])[:5]}


def _format_regional_score(data: dict) -> str:
    grid = data["grid"]
    lines = [f"Regional score grid ({grid}x{grid}, 1.00 = identical):"]
    for row in data["cells"]:
        lines.append("  " + "  ".join(f"{v:.2f}" for v in row))
    lines.append("")
    lines.append("Worst cells (crop these from both images to compare them in isolation):")
    for cell in data["worst"]:
        x1, y1, x2, y2 = cell["box"]
        lines.append(
            f"  r{cell['row']}c{cell['col']} similarity {cell['similarity']:.2f} "
            f"box=({x1},{y1})-({x2},{y2})"
        )
    return "\n".join(lines)


def compare_palettes(a: np.ndarray, b: np.ndarray, colors: int = 8) -> dict:
    """Dominant-colour palette comparison via k-means quantisation.

    Each palette entry of image A is matched to its nearest counterpart in B.
    A large weighted distance or a large coverage delta means a real colour or
    theme mismatch, not a layout one.
    """
    def palette(img):
        pixels = img.reshape(-1, 3).astype(np.float32)
        if len(pixels) > 60_000:
            pixels = pixels[:: len(pixels) // 60_000]
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(pixels, colors, None, criteria, 3,
                                        cv2.KMEANS_PP_CENTERS)
        counts = np.bincount(labels.flatten(), minlength=colors).astype(np.float64)
        shares = counts / counts.sum()
        order = np.argsort(-shares)
        return [(tuple(int(v) for v in centers[i]), float(shares[i])) for i in order]

    pal_a, pal_b = palette(a), palette(b)
    entries = []
    total_distance = 0.0
    for color, share in pal_a:
        nearest, distance = None, None
        for other_color, other_share in pal_b:
            d = float(np.linalg.norm(np.array(color, float) - np.array(other_color, float)))
            if distance is None or d < distance:
                nearest, distance = (other_color, other_share), d
        total_distance += distance * share
        entries.append({
            "design": {"rgb": color, "hex": "#%02X%02X%02X" % color, "share": share},
            "nearest": {"rgb": nearest[0], "hex": "#%02X%02X%02X" % nearest[0],
                        "share": nearest[1]},
            "distance": distance,
            "share_delta": share - nearest[1],
        })

    # 441.673 = max RGB distance (black to white), inverted into 0..1 similarity.
    return {
        "colors": colors,
        "weighted_distance": total_distance,
        "palette_similarity": float(max(0.0, 1.0 - total_distance / 441.673)),
        "entries": entries,
    }


def _format_palette(data: dict) -> str:
    lines = [
        f"Dominant colour palette ({data['colors']} colours, "
        f"palette_similarity: {data['palette_similarity']:.4f}):",
        "  image A colour  share   nearest in B    dist   share delta",
    ]
    for e in data["entries"]:
        lines.append(
            f"  {e['design']['hex']}        {e['design']['share']:.3f}  "
            f"{e['nearest']['hex']}       {e['distance']:6.1f}  {e['share_delta']:+.3f}"
        )
    worst = max(data["entries"], key=lambda e: e["distance"] * e["design"]["share"])
    if worst["distance"] > 12:
        lines.append("")
        lines.append(
            f"Biggest colour mismatch: {worst['design']['hex']} "
            f"({worst['design']['share']:.1%} of image A) has no close counterpart "
            f"in image B (nearest {worst['nearest']['hex']}, "
            f"distance {worst['distance']:.1f})."
        )
    return "\n".join(lines)


def _describe_region(dissim: float) -> str:
    if dissim >= 0.5:
        return "severely different"
    if dissim >= 0.3:
        return "notably different"
    if dissim >= 0.15:
        return "somewhat different"
    if dissim >= 0.07:
        return "nearly identical"
    return "identical"


def humanize_regions(regions: list) -> str:
    """Turn the region table into a plain-English narrative report."""
    ranked = sorted(regions, key=lambda r: r["dissimilarity"], reverse=True)
    lines = ["Region-by-region breakdown (most to least divergent):"]
    for i, r in enumerate(ranked, 1):
        desc = _describe_region(r["dissimilarity"])
        lines.append(
            f"  {i}. {r['region']:<11} — {desc:<20} (similarity: {r['similarity']:.2f})"
        )

    top = ranked[0]
    lines.append("")
    if top["dissimilarity"] >= 0.15:
        lines.append(
            f"Summary: the '{top['region']}' region is the single biggest driver of the "
            f"low similarity score (only {top['similarity']:.0%} similar there)."
        )
        others = [r for r in ranked[1:] if r["dissimilarity"] >= 0.15]
        if others:
            names = ", ".join(f"'{o['region']}'" for o in others)
            lines.append(f"Other regions with notable differences: {names}.")
        untouched = [r for r in ranked if r["dissimilarity"] < 0.07]
        if untouched:
            names = ", ".join(f"'{u['region']}'" for u in untouched)
            lines.append(f"Regions that matched almost perfectly: {names}.")
    else:
        lines.append(
            "Summary: no single region stands out — the two images are either very "
            "similar overall, or their differences are spread evenly across the frame."
        )
    return "\n".join(lines)


def generate_heatmap(
    diff_map: np.ndarray, out_path: str, base_image: Optional[np.ndarray] = None,
    alpha: float = 0.55, grid_overlay: bool = True,
) -> str:
    """Render a jet-colormap heatmap (blue similar, red different).

    Optionally blended over image A, with 3x3 grid lines and region labels burned
    in so the report and the image refer to the same coordinates.
    """
    h, w = diff_map.shape
    heat_u8 = np.uint8(np.clip(diff_map, 0.0, 1.0) * 255)
    heat_color = cv2.applyColorMap(heat_u8, cv2.COLORMAP_JET)

    if base_image is not None:
        base_bgr = cv2.cvtColor(base_image, cv2.COLOR_RGB2BGR)
        blended = cv2.addWeighted(base_bgr, 1 - alpha, heat_color, alpha, 0)
    else:
        blended = heat_color

    if grid_overlay:
        for i in range(1, 3):
            x, y = int(w * i / 3), int(h * i / 3)
            cv2.line(blended, (x, 0), (x, h), (255, 255, 255), 1, cv2.LINE_AA)
            cv2.line(blended, (0, y), (w, y), (255, 255, 255), 1, cv2.LINE_AA)
        for r_idx in range(3):
            for c_idx in range(3):
                label = REGION_LABELS[r_idx][c_idx]
                cx, cy = int(w * (c_idx + 0.5) / 3), int(h * (r_idx + 0.5) / 3)
                (tw, _), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
                cv2.putText(blended, label, (cx - tw // 2, cy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 3, cv2.LINE_AA)
                cv2.putText(blended, label, (cx - tw // 2, cy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)

    cv2.imwrite(out_path, blended)
    return out_path


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #

METHOD_WEIGHTS = {
    "pixel": 0.15,
    "ssim": 0.30,
    "histogram": 0.20,
    "hash": 0.20,
    "orb": 0.15,
}


def run_comparison(
    path_a: str,
    path_b: str,
    resize_mode: str = "pad",
    methods: Optional[list] = None,
    ssim_kernel: int = 7,
    region_report: bool = True,
    heatmap_out: Optional[str] = None,
    heatmap_alpha: float = 0.55,
    regional_score: Optional[int] = None,
    palette: Optional[int] = None,
) -> SimilarityReport:
    """Run the requested methods and return a full :class:`SimilarityReport`."""
    methods = methods or list(METHOD_WEIGHTS.keys())

    img_a = load_image(path_a)
    img_b = load_image(path_b)
    a_r, b_r, final_size = resize_to_match(img_a, img_b, mode=resize_mode)

    report = SimilarityReport(resize_mode=resize_mode, final_size=final_size)
    contributing = {}

    if "pixel" in methods:
        px = compare_pixel(a_r, b_r)
        report.scores["pixel"] = px
        contributing["pixel"] = px["mse_similarity"]

    if "ssim" in methods:
        s = compare_ssim(a_r, b_r, kernel_size=ssim_kernel)
        report.scores["ssim"] = s
        contributing["ssim"] = s

    if "histogram" in methods:
        h = compare_histogram(a_r, b_r)
        report.scores["histogram"] = h
        contributing["histogram"] = h["combined"]

    if "hash" in methods:
        ph = compare_hash(a_r, b_r)
        report.scores["perceptual_hash"] = ph
        contributing["hash"] = ph["combined"]

    if "orb" in methods:
        orb = compare_orb_features(a_r, b_r)
        report.scores["feature_matching"] = orb
        contributing["orb"] = orb["match_ratio"]

    if contributing:
        total_weight = sum(METHOD_WEIGHTS[k] for k in contributing)
        weighted = sum(contributing[k] * METHOD_WEIGHTS[k] for k in contributing)
        report.overall_score = float(weighted / total_weight)

    if palette:
        report.palette_report = compare_palettes(a_r, b_r, colors=palette)

    if region_report or heatmap_out or regional_score:
        diff_map = compute_diff_map(a_r, b_r, kernel_size=ssim_kernel)

        if regional_score:
            report.regional_score_grid = regional_score_grid(diff_map, grid=regional_score)

        if region_report:
            regions = regional_breakdown(diff_map)
            report.region_breakdown = regions
            report.region_report_text = humanize_regions(regions)

        if heatmap_out:
            report.heatmap_path = generate_heatmap(
                diff_map, heatmap_out, base_image=a_r, alpha=heatmap_alpha
            )

    return report


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare two images using multiple similarity techniques.")
    parser.add_argument("image_a", help="first image (usually the design reference)")
    parser.add_argument("image_b", help="second image (usually the app capture)")
    parser.add_argument("--resize-mode", choices=["stretch", "pad", "crop"],
                        default="pad",
                        help="how to reconcile different sizes (default: pad)")
    parser.add_argument("--methods", default="pixel,ssim,histogram,hash,orb",
                        help="comma-separated subset of pixel,ssim,histogram,hash,orb")
    parser.add_argument("--ssim-kernel", type=int, default=7,
                        help="odd SSIM window size (default 7)")
    parser.add_argument("--no-region-report", action="store_true",
                        help="skip the humanized 3x3 regional breakdown")
    parser.add_argument("--heatmap-out", metavar="PATH", default=None,
                        help="save a jet-colormap diff heatmap overlaid on image A")
    parser.add_argument("--heatmap-alpha", type=float, default=0.55,
                        help="heatmap overlay opacity (default 0.55)")
    parser.add_argument("--regional-score", nargs="?", type=int, const=4,
                        default=None, metavar="GRID",
                        help="print an NxN numeric similarity grid plus worst boxes")
    parser.add_argument("--palette", nargs="?", type=int, const=8, default=None,
                        metavar="COLORS",
                        help="compare dominant colour palettes (default 8 colours)")
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--json-out", metavar="PATH", default=None,
                        help="write the JSON report to a file")
    parser.add_argument("--fail-under", type=float, default=None, metavar="SCORE",
                        help="exit 1 when the overall score is below this value")
    args = parser.parse_args()

    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    invalid = set(methods) - set(METHOD_WEIGHTS.keys())
    if invalid:
        parser.error(f"Unknown method(s): {', '.join(invalid)}")

    try:
        report = run_comparison(
            args.image_a, args.image_b,
            resize_mode=args.resize_mode,
            methods=methods,
            ssim_kernel=args.ssim_kernel,
            region_report=not args.no_region_report,
            heatmap_out=args.heatmap_out,
            heatmap_alpha=args.heatmap_alpha,
            regional_score=args.regional_score,
            palette=args.palette,
        )
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - CLI guard
        print(f"Error during comparison: {exc}", file=sys.stderr)
        return 1

    data = report.to_dict()
    if args.json_out:
        out_dir = os.path.dirname(os.path.abspath(args.json_out))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        report.pretty_print()

    if args.fail_under is not None and (
        report.overall_score is None or report.overall_score < args.fail_under
    ):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
