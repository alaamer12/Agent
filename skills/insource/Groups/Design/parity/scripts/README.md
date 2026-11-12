# parity scripts — reusable toolkit

A project-agnostic implementation of the parity pipeline. Nothing here knows a product name, a page list, an executable path, or a design folder — every one of those arrives as a flag or a config field.

## Install

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

`pywin32` and `psutil` are only needed for the Windows capture path. The comparison engine (`similarity.py`, `region_crop.py`, `pixel_regression.py`) works on any OS.

## What each script does

| Script | Role | Pipeline step |
|---|---|---|
| `snip_tool.py` | Windows window capture library + diagnostic CLI (`PrintWindow`, RTL flip, DPI awareness, root-process targeting) | capture |
| `capture_app.py` | Capture a window, detect/crop the caption band, fit the design canvas | capture + normalize |
| `capture_mockup.py` | Deterministic Playwright screenshot of a served mockup (DPR, colour scheme, reduced motion, storage/JS seeding) | capture |
| `capture_batch.py` | Capture a page × theme × variant matrix in one pass | capture |
| `similarity.py` | Five comparison methods + palette + 3×3 report + N×N grid + heatmap | score + diagnose |
| `region_crop.py` | Crop by named region (same split rule as `similarity.py`) or explicit box | diagnose |
| `parity_run.py` | One full state: launch → wait → capture → normalize → score → align → heatmap | loop iteration |
| `parity_cut.py` | Compare named sub-regions and emit side-by-side pairs + per-region heatmaps | diagnose |
| `run_suite.py` | Full matrix with a local mockup server, blank/splash retries, and capture-only mode for regression baselines | orchestration |
| `pixel_regression.py` | Exact app-vs-app pixel gate with documented dynamic-region masks | regression |
| `run_android_suite.py` | Android/emulator parity suite over ADB | orchestration (mobile) |

## The two pipelines

### Design → app parity

```bash
# 1. reference frames (served folder, one per page/theme/variant)
python capture_batch.py --base-url http://localhost:8000 \
    --design-root design --pages home settings \
    --themes light dark --out-root parity_captures

# 2. one state, with scoring + alignment + heatmap
python parity_run.py --exe build/app.exe \
    --launch-args "--page={page} --theme={theme}" \
    --page home --theme dark \
    --design-root parity_captures --viewport 1280x800 --threshold 0.92

# 3. the whole matrix, unattended
python run_suite.py --config parity.json --all
```

### Refactor → regression

```bash
# baseline (before the change)
python run_suite.py --config parity.json --all --capture-only --out parity_out/before

# after rebuilding
python run_suite.py --config parity.json --all --capture-only --out parity_out/after

# exact gate (exit 1 on any unmasked difference)
python pixel_regression.py --baseline parity_out/before --current parity_out/after \
    --report parity_out/after/regression.md
```

### Mobile (Android)

```bash
python run_android_suite.py --package com.example.app \
    --screens-file screens.json --design-dir baselines --threshold 0.90
```

## Direct comparison

```bash
# all five methods, 3x3 narrative, 6x6 numeric grid, palette, heatmap
python similarity.py design/home.png parity_out/home/app.png \
    --resize-mode pad --regional-score 6 --palette 8 \
    --heatmap-out parity_out/home/diff.png

# crop the worst cell exactly as it was scored
python region_crop.py parity_out/home/app.png --box 320,600,640,200 --out worst.png
```

## Masking dynamic regions

`pixel_regression.py` reads `masks.json` from the baseline directory (or `--mask`):

```json
{
  "global": [[0, 0, 1280, 64]],
  "states": {
    "home__default__light": [[1040, 16, 240, 48]]
  }
}
```

Rectangles are `[x, y, w, h]`. Mask only genuinely dynamic pixels (live clocks, avatars, randomised feeds) and document each one.

## Notes

- Mockups must be served over HTTP, never `file://`.
- The design capture DPR must match the app capture's effective DPR.
- `parity_run.py` and `run_suite.py` force-kill stale instances by default; single-instance apps otherwise redirect the launch and capture the wrong state.
- Blank or splash-coloured frames are treated as capture failures and retried, never scored.
- The aligned score in `parity_run.py` removes a measured translation offset (usually window chrome); report both raw and aligned so a real offset cannot hide inside the correction.
