# Script reference — every tool, every flag

A one-page card for the implementation in `scripts/`. Read this when you know *what* you want to do and need the exact flag; read `pipeline.md` when you need to understand which step a tool belongs to, and `matrix-config.md` for the JSON file schemas.

## Table of contents
1. Install and conventions
2. The eleven scripts at a glance
3. Capture: `snip_tool`, `capture_app`, `capture_mockup`, `capture_batch`
4. Scoring: `similarity`, `region_crop`
5. Orchestration: `parity_run`, `run_suite`
6. Diagnosis: `parity_cut`
7. Regression: `pixel_regression`
8. Mobile: `run_android_suite`
9. Programmatic use (import recipes)
10. Exit-code contract

---

## 1. Install and conventions

```bash
python -m pip install -r scripts/requirements.txt
python -m playwright install chromium
```

- Every script is standalone: `python scripts/<name>.py --help` is the authoritative flag list.
- Nothing is product-specific. Pages, themes, variants, binaries, window names, design folders and launch flags all arrive as arguments or config fields.
- Scripts import each other by name from the same directory (`sys.path` insertion at import time), so they can be copied into any project as a folder and run from anywhere.
- `pywin32` + `psutil` are Windows-only. `snip_tool.py`, `capture_app.py`, `parity_run.py`, `run_suite.py` and the live-capture path of `parity_cut.py` refuse to run elsewhere; the comparison scripts are cross-platform.
- Mockups are always captured from an HTTP URL. Never `file://`.

## 2. The eleven scripts at a glance

| Script | One-line purpose | Importable entry point |
|---|---|---|
| `snip_tool.py` | Capture one Windows window (or the whole screen) as a PIL image | `capture_window`, `find_target_windows` |
| `capture_app.py` | Window capture cropped to its content and fitted to the design canvas | `normalize_capture`, `capture_target` |
| `capture_mockup.py` | One deterministic Playwright screenshot of a served page | `capture` |
| `capture_batch.py` | A page × theme × variant mockup matrix in one pass | `build_url`, `build_path` |
| `similarity.py` | Five-method score + palette + regional grid + heatmap | `run_comparison` |
| `region_crop.py` | Crop by named region or explicit box, same split rule as the scorer | `crop_region`, `crop_box` |
| `parity_run.py` | One full state: launch → wait → capture → normalize → score → align | `run_state`, `score_pair` |
| `parity_cut.py` | Named sub-region comparisons with side-by-side pairs | `grid_regions`, `capture_app_client` |
| `run_suite.py` | Whole matrix with mockup server, retries, capture-only mode | `build_states`, `mockup_server` |
| `pixel_regression.py` | Exact app-vs-app gate with dynamic-region masks | `compare_state`, `apply_mask` |
| `run_android_suite.py` | Android/emulator screenshots over ADB, scored per screen | `load_screens`, `score_screen` |

## 3. Capture

### `snip_tool.py` — window capture primitive

```bash
python snip_tool.py --name app.exe --list
python snip_tool.py --name app.exe --output shots/app.png
python snip_tool.py --pid 12345 --output shots/app.png --debug
python snip_tool.py --title "My App" --include-frame --output shots/framed.png
python snip_tool.py --fullscreen --output shots/screen.png
```

| Group | Flags |
|---|---|
| Target | `-n/--name`, `-p/--pid`, `-t/--title` (title is a substring match) |
| Actions | `-l/--list`, `--include-hidden`, `--fullscreen`, `--include-frame` |
| Output | `-o/--output`, `--wait SECONDS` |
| RTL | `--flip-horizontal`, `--no-flip-fix` |
| Diagnostics | `--debug` |

Behaviour worth knowing:

- `capture_window` uses `PrintWindow`, so it works on occluded windows. `--include-frame` switches to a composited screen grab that includes the native title bar and DWM border, which requires the window to be visible.
- `WS_EX_LAYOUTRTL` windows capture mirrored at the GDI level; the bitmap is flipped back automatically. `--flip-horizontal` forces the flip, `--no-flip-fix` disables it (use when a non-RTL app captures mirrored for another reason).
- Process-name targeting prefers *root* pids, so an Electron/IDE app's renderer or GPU helper is never selected instead of the real window owner.
- Per-monitor DPI awareness is set at import, so rectangles are in physical pixels and captures are not blurred by Windows scaling.
- `--list` prints pid, process, size, visibility and title for every candidate, largest first. When nothing matches, the CLI explains whether the process is running but windowless.

### `capture_app.py` — window capture in design coordinates

```bash
python capture_app.py --name app.exe --output captures/app.png
python capture_app.py --pid 12345 --output captures/app.png --target-size 1280x800
python capture_app.py --title "My App" --chrome-crop 40 --fill "#0F172A"
```

| Flag | Values | Default |
|---|---|---|
| `--output` | path | required |
| `--chrome-crop` | `auto`, `flat`, `dark`, `none`, or a pixel count | `auto` |
| `--target-size` | `WxH` or `none` | `none` |
| `--fill` | `#RRGGBB` or `r,g,b` | `#F1F5F9` |
| `--anchor` | `top`, `center`, `bottom` | `top` |
| `--wait` | seconds before capture | `0` |
| `--include-hidden`, `--flip-horizontal`, `--no-flip-fix`, `--debug` | as `snip_tool` | — |

`auto` tries the flat-band scan first (first row that stops matching the title-bar colour) and falls back to the dark-band scan (leading majority-dark rows). Prefer detection over a constant; hard-coded chrome heights break on DPI changes, theme changes and framework updates.

`--target-size` decides the coordinate system every later crop refers to. Set it to the design viewport, not to whatever the window happens to be, so a mis-sized app window shows up as padding rather than as a silently rescaled comparison.

### `capture_mockup.py` — one deterministic reference frame

```bash
python capture_mockup.py --url http://localhost:8000/home.html --output caps/home_light.png
python capture_mockup.py --url http://localhost:8000/home.html --output caps/home_dark.png \
    --theme dark --dpr 1 --reduced-motion
python capture_mockup.py --url "http://localhost:8000/home.html?state=open" \
    --output caps/home_open.png --width 1440 --height 900 --wait-ms 800
```

| Flag | Purpose | Default |
|---|---|---|
| `--url`, `--output` | served page and output PNG | required |
| `--width`, `--height` | viewport | `1280`, `800` |
| `--dpr` | device scale factor; must match the app side | `1.0` |
| `--theme` | `light` or `dark` colour scheme | `light` |
| `--color-scheme` | explicit CSS colour-scheme override | follows `--theme` |
| `--reduced-motion` | emulate `prefers-reduced-motion: reduce` | off |
| `--set-storage` | seed `localStorage` before page scripts, repeatable `KEY=VALUE` | — |
| `--init-js` | run JS before page scripts, repeatable | — |
| `--toggle-dark-class` | toggle a class on `<html>` after load | off |
| `--dark-class` | class name used by the toggle | `dark` |
| `--full-page`, `--wait-ms` | whole scroll height, extra settle time | off, `300` |

`--reduced-motion` matters for parity: decorative animation is the only frame-varying content on an otherwise static mockup, and a varying reference makes every score noisy.

### `capture_batch.py` — the reference matrix

```bash
python capture_batch.py --base-url http://localhost:8000 \
    --design-root design --pages home settings profile
python capture_batch.py --base-url http://localhost:8000 \
    --pages home --themes light dark --variants alpha beta \
    --out-root captures --width 1440 --height 900
```

| Flag | Purpose | Default |
|---|---|---|
| `--base-url` | root URL the folder is served at | `http://localhost:8000` |
| `--url-template` | URL template with placeholders | `{base}/{page}.html?theme={theme}{variant_query}` |
| `--pages` | page ids | required |
| `--themes`, `--variants` | matrix axes | `light dark`, `default` |
| `--design-root` | folder being served; validates `<page>.html` exists | — |
| `--out-root` | output root | `parity_captures` |
| `--folder-template` | output folder template | `{page}` (one variant) or `{page}_{variant}` |
| `--filename-template` | output filename template | `design_{theme}.png` |
| `--width`, `--height`, `--dpr`, `--wait-ms` | capture geometry | `1280`, `800`, `1.0`, `500` |
| `--set-storage`, `--init-js`, `--toggle-dark-class`, `--dark-class`, `--reduced-motion`, `--full-page` | passed through to `capture_mockup` | — |
| `--json-out` | write the capture manifest | — |

`--design-root` exists to catch a real failure mode: capturing against the wrong served folder produces a full set of plausible-looking reference frames that all score wrong. The check fails loudly instead.

## 4. Scoring

### `similarity.py` — the engine

```bash
python similarity.py design.png app.png
python similarity.py design.png app.png --regional-score 6 --palette 8 \
    --heatmap-out diff.png --json-out report.json
python similarity.py design.png app.png --methods ssim,histogram,hash --fail-under 0.90
```

| Flag | Purpose | Default |
|---|---|---|
| `image_a`, `image_b` | reference, candidate | required |
| `--resize-mode` | `stretch`, `pad`, `crop` | `pad` |
| `--methods` | subset of `pixel,ssim,histogram,hash,orb` | all five |
| `--ssim-kernel` | odd SSIM window | `7` |
| `--no-region-report` | skip the 3×3 narrative | off |
| `--regional-score [N]` | numeric N×N grid plus worst-cell boxes | off (`4` if bare) |
| `--palette [N]` | dominant-colour comparison, N colours | off (`8` if bare) |
| `--heatmap-out`, `--heatmap-alpha` | jet heatmap over image A | —, `0.55` |
| `--json`, `--json-out` | JSON to stdout / to a file | off |
| `--fail-under` | exit 1 below this overall score | off |

Method weights: pixel `0.15`, ssim `0.30`, histogram `0.20`, hash `0.20`, orb `0.15`. Weights are renormalised over whichever methods actually ran, so `--methods ssim` is a pure SSIM verdict rather than a score silently divided by five.

Interpreting the five scores:

- `pixel` — literal per-pixel distance. Drops first on a one-pixel text shift; a low pixel score with high ssim is a rendering-engine difference, not necessarily a bug.
- `ssim` — structure. The right first number for "is this in the wrong place or the wrong size".
- `histogram` — colour distribution. A high ssim with a low histogram means right layout, wrong palette.
- `hash` — resize/compression-robust. Useful when the two sides were captured at different densities.
- `orb` — local texture. A low `match_ratio` with high ssim usually means shared structure with a different icon set or image assets.

### `region_crop.py` — crop what was scored

```bash
python region_crop.py --list-regions --region-layout 3x3
python region_crop.py shot.png --region mid-left --out crop.png
python region_crop.py shot.png --regions top-left,mid,bottom-right --out-dir crops/
python region_crop.py shot.png --all --region-layout 3-columns --out-dir crops/
python region_crop.py shot.png --box 320,600,640,200 --out worst.png
python region_crop.py shot.png --region mid --margin-pct 10 --out crop.png
```

| Flag | Purpose | Default |
|---|---|---|
| `image` | image to crop | required except for `--list-*` |
| `--region-layout` | `3x3`, `3-columns`, `3-rows` | `3x3` |
| `--region` / `--regions` / `--all` | one / several / every region | — |
| `--box` | explicit `X,Y,W,H` (mutually exclusive with regions) | — |
| `--margin-pct` | expand the crop by a percentage of its own size | `0` |
| `--out`, `--out-dir`, `--prefix` | single output path, multi output dir, filename prefix | — |
| `--list-regions`, `--list-layouts` | discovery | — |

`--box` requires `--out` (a single explicit crop has no natural filename), and is mutually exclusive with `--region`/`--regions`/`--all`.

The region names and boundaries come from the same `np.array_split` rule `similarity.py` uses, so "mid-left" is the identical pixel rectangle in the scorer, the heatmap and the crop. Boxes reported under `worst` in a `similarity.py` run can be fed straight to `--box`.

## 5. Orchestration

### `parity_run.py` — one state, end to end

```bash
python parity_run.py --exe build/app.exe \
    --launch-args "--page={page} --theme={theme}" \
    --pages home settings --themes light dark \
    --design-root parity_captures --viewport 1280x800 --threshold 0.92
python parity_run.py --exe build/app.exe --page home --theme dark \
    --design-root captures --json-out reports/home_dark.json
```

| Group | Flags |
|---|---|
| Launch | `--exe`, `--launch-args`, `--window-name`, `--window-title` |
| Matrix | `--page`, `--pages`, `--theme`, `--themes`, `--variant`, `--variants`, `--state`, `--states`, `--all` |
| Reference | `--design-root`, `--design-pattern`, `--fallback-pattern` |
| Normalize | `--viewport`, `--chrome-crop`, `--fill`, `--anchor` |
| Timing | `--settle`, `--wait`, `--min-area`, `--kill-first` / `--no-kill-first`, `--keep-open` |
| Scoring | `--threshold`, `--methods`, `--regional-grid`, `--palette`, `--no-align`, `--max-shift-dy`, `--max-shift-dx` |
| Output | `--out-root`, `--json-out`, `--debug` |

Defaults: `--design-pattern "{page}_{variant}/design_{theme}.png"`, `--fallback-pattern "{page}/design_{theme}.png"`, viewport `1280x800`, `--chrome-crop auto`, `--threshold 0.90`, alignment on, kill-first on.

Every token of `--launch-args` is substituted with `{page}`, `{theme}`, `{variant}` and `{state}`. That single mechanism is what keeps the script product-agnostic: the app's own flag vocabulary lives in the command line, not in the tool.

Design resolution is explicit: primary pattern, then fallback, then **UNVERIFIED** — never a silent score against the wrong reference. That third state is deliberate; a screen with no matching mockup is a hole in the run, not a pass.

Three numbers are reported per state, and they answer different questions:

- **raw** — the actual rendered similarity. This is the one the threshold applies to.
- **structure** — the same pair with a 1px Gaussian blur on both sides, blending ssim/histogram/hash. Structure high, raw low means a renderer difference (GDI vs Chromium glyph placement); both low means a real bug.
- **palette** — whether the colours are right, independent of layout.

Alignment is measured with a coarse-to-fine translation search (`8 → 2 → 1` px steps) that minimises mean absolute difference, and both raw and aligned scores are kept. A measured offset must stay visible in the report — absorbing it silently is how a real 34px layout bug gets "fixed" three times without ever being found.

### `run_suite.py` — the whole matrix

```bash
python run_suite.py --config parity.json --all
python run_suite.py --config parity.json --page home --theme dark
python run_suite.py --config parity.json --all --capture-only --out parity_out/before
python run_suite.py --config parity.json --all --update-baseline
```

| Group | Flags |
|---|---|
| Config | `--config`, `--exe`, `--window-name`, `--mockup-dir`, `--base-url`, `--viewport`, `--launch-args`, `--mockup-url-template` |
| Overrides | `--pages`, `--themes`, `--variants`, `--states`, `--threshold`, `--settle` |
| Selection | `--all`, `--page`, `--theme`, `--variant`, `--state` |
| Output | `--capture-only`, `--out`, `--out-root`, `--update-baseline`, `--debug` |

Flags override config values, so one checked-in config can serve both a full run and a single-state debug invocation.

What it adds over `parity_run`: a local HTTP server on a free port for the mockup folder, blank/splash/frame-stability retries (up to three attempts, each with a longer settle), and `--capture-only` mode that writes `<out>/<state>/app.png` plus a `manifest.json` — the exact input shape `pixel_regression.py` needs. Schema in `matrix-config.md`.

Splash colours are declared, not guessed: `splash_colors` in config lists the brand colours the app's splash screen uses, and a frame whose four corners mostly match one of them is treated as "not ready yet" and recaptured.

## 6. Diagnosis

### `parity_cut.py` — component-level cuts

```bash
python parity_cut.py --design-image design.png --app-image app.png \
    --regions-file regions.json --out cuts/
python parity_cut.py --url http://localhost:8000/home.html --theme dark \
    --window-name app.exe --regions-file regions.json --out cuts/
python parity_cut.py --design-image design.png --app-image app.png --all-grid 4 --out cuts/
```

| Group | Flags |
|---|---|
| Design side | `--design-image` or `--url`, `--theme`, `--variant`, `--dpr`, `--reduced-motion`, `--wait-ms`, `--set-storage`, `--init-js` |
| App side | `--app-image` or `--window-name` / `--pid`, `--client-size`, `--chrome-crop`, `--fill` |
| Regions | `--regions-file`, `--region NAME:X,Y,W,H` (repeatable), `--all-grid N` |
| Scoring | `--methods`, `--regional-grid`, `--palette` |
| Output | `--out`, `--debug` |

Live mode sizes the app window to `--client-size` before capturing, derives the client rectangle from the window/client size difference (not `ClientToScreen`, which RTL windows mirror), and normalises into that shared space. That is what makes one box mean the same pixels on both sides.

Per region it writes `design_<name>.png`, `app_<name>.png`, `pair_<name>.png` (side by side, labelled), `heatmap_<name>.png`, and a `summary.json` with overall, ssim, palette and the three worst inner cells. Default `--methods` is `ssim,histogram,hash` — pixel and ORB are noisier on small crops.

Boxes are `X,Y,W,H` in client space. This is a diagnostic, not a gate: it always exits 0 after writing artifacts.

## 7. Regression

### `pixel_regression.py` — the exactness gate

```bash
python pixel_regression.py --baseline parity_out/before --current parity_out/after
python pixel_regression.py --baseline B --current C --mask masks.json --tolerance 2 \
    --report C/report.md
python pixel_regression.py --baseline B --current C --intersect
```

| Flag | Purpose | Default |
|---|---|---|
| `--baseline`, `--current` | the two capture trees | required |
| `--image-name` | frame filename inside each state dir | `app.png` |
| `--mask` | mask JSON | `<baseline>/masks.json` if present |
| `--tolerance` | allowed max per-channel delta | `0` (exact) |
| `--report`, `--json-out` | Markdown / machine-readable output | — |
| `--no-heatmaps` | skip per-state diff PNGs | off |
| `--intersect` | compare only states present in both trees | off |

This answers a different question from `similarity.py`: not "does it look like the design" but "did the change alter anything it was not supposed to". The gate is exactness, with tolerance > 0 reserved for known dithering/compression noise, and masks reserved for genuinely dynamic pixels. A mask that hides a real regression is worse than no gate at all, so every rectangle should be justified in the project's docs.

Missing states and size mismatches fail the run. `--intersect` is the escape hatch when the two trees are legitimately different sizes (new screens added, old screens removed).

## 8. Mobile

### `run_android_suite.py` — ADB parity suite

```bash
python run_android_suite.py --package com.example.app \
    --screens-file screens.json --design-dir baselines
python run_android_suite.py --package com.example.app \
    --screens home,home_dark --crop-top 64 --crop-bottom 2270
python run_android_suite.py --package com.example.app \
    --screens-file screens.json --serial <device-serial> --threshold 0.9
```

| Flag | Purpose | Default |
|---|---|---|
| `--package` | application package | required |
| `--component` | launcher component; auto-resolved via `cmd package resolve-activity` | — |
| `--serial` | adb device serial | first device |
| `--screens-file` / `--screens` | JSON definitions / comma-separated names | `home` |
| `--design-dir`, `--design-pattern` | baseline root and path template | `baselines`, `{name}/design.png` |
| `--crop-top`, `--crop-bottom` | status-bar / content-end pixels in simple mode | `0`, image bottom |
| `--extra KEY=VALUE` | intent extras applied to every screen | — |
| `--wait` | settle seconds after launch | `14` |
| `--threshold` | pass threshold | `0.90` |
| `--no-force-stop`, `--json-out`, `--out-root` | behaviour and output | — |

Simple mode derives the rest from the name: `home_dark` becomes page `home` with theme `dark`. Use the JSON file when a screen needs its own crop rectangle or extra intent values — schema in `matrix-config.md`.

A screen whose baseline image is missing is reported **UNVERIFIED** and fails the run. It is never scored against a guess.

## 9. Programmatic use

Scripts are libraries first. Import and call; do not shell out to the CLI from inside a project's own harness.

```python
import sys
sys.path.insert(0, "path/to/parity/scripts")

from capture_app import normalize_capture, parse_fill
from similarity import run_comparison

# score one already-normalized pair
report = run_comparison("design.png", "app.png", resize_mode="pad",
                        regional_score=6, palette=8,
                        heatmap_out="diff.png")
print(report.overall_score)
print(report.regional_score_grid["worst"][:3])
```

```python
from snip_tool import find_target_windows, capture_window

window = find_target_windows(name="app.exe")[0]
img = capture_window(window["hwnd"])
```

```python
from run_suite import mockup_server, is_blank, build_states, state_id

with mockup_server("design") as base:
    print(base)  # http://127.0.0.1:<port>
```

Typical integration points: a project's own test runner calls `run_comparison` and asserts on `overall_score`; a firmware/desktop build script calls `capture_app.capture_target` instead of shelling out to a screenshot tool; a CI job calls `run_suite.run_capture_only` and then `pixel_regression.compare_state`.

## 10. Exit-code contract

| Script | Exit 0 | Exit 1 | Exit 2 |
|---|---|---|---|
| `snip_tool.py` | captured or listed matches | no match, or capture failure | — |
| `capture_app.py` | capture written | — | bad arguments |
| `capture_mockup.py` | capture written | capture error | — |
| `capture_batch.py` | all captures written | `--design-root` validation failed | — |
| `similarity.py` | compared (and above `--fail-under`) | below `--fail-under`, or load error | — |
| `region_crop.py` | crops written | source image missing | bad region/box arguments |
| `parity_run.py` | every state scored at threshold | any state failed, unverified or below threshold | not Windows |
| `parity_cut.py` | artifacts written (always) | — | missing inputs |
| `run_suite.py` | every state scored at threshold, or every capture succeeded in `--capture-only` | any blank, error or below-threshold state | not Windows |
| `pixel_regression.py` | zero unmasked differences | any diff, missing state or size mismatch | — |
| `run_android_suite.py` | every screen scored at threshold | unverified, error or below threshold | adb unavailable |

Exit codes are the gate. Wire `pixel_regression.py` and `run_suite.py` directly into CI; there is nothing to parse.
