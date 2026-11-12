# Pipeline: Capture, Compare, Diagnose

## Table of contents
1. Mockup capture
2. On-device/emulator capture
3. Capture reliability (avoiding blank/black frames)
4. Comparison suite: what each metric is actually good for
5. Regional grid scoring
6. How the toolkit maps onto these steps

---

## 1. Mockup capture

- Serve the mockup over an actual local HTTP server (**`python -m http.server`** or equivalent) — **never open it via a `file://` URL.** Query-parameter-driven state forcing (see `debug-state-simulation.md`), relative asset paths, and any `fetch`/XHR-based dummy-data loading are all unreliable or outright broken over `file://` in most browsers. This is a common, easy-to-miss setup mistake that silently corrupts every capture downstream of it.
- Capture with a headless browser (Playwright, Puppeteer, or equivalent) at a **fixed, explicitly documented viewport size and device-scale-factor (DPR)** matching the target device's actual screen density. A mismatched DPR between mockup and device capture inflates every downstream similarity score's noise floor before a single pixel of real content is compared.
- Capture once per entry in the full matrix from `SKILL.md` Step 0 (screen × ItC-state × theme × language) — the mockup side of the matrix is normally cheap and fast since it's just re-navigating a URL with different query parameters, so there's no reason to under-capture it.

Implemented by `scripts/capture_mockup.py` (one frame) and `scripts/capture_batch.py` (the matrix, with URL/folder/filename templating and an optional `--design-root` existence check so a wrong served folder cannot quietly produce a full set of wrong references). Flags in `scripts-reference.md`.

## 2. On-device/emulator capture

- Use the platform's real screenshot mechanism (e.g. `adb shell screencap` / `adb exec-out screencap` for Android, `xcrun simctl io booted screenshot` for iOS Simulator, or the equivalent for the target platform) rather than a manual screenshot — this needs to be scriptable to run unattended across the full matrix.
- Reach each screen/state via the deep-link/launch-flag mechanism from `debug-state-simulation.md`, not manual navigation — manual navigation cannot be looped unattended.
- Capture at the device's native resolution; downscale/upscale during normalization (`frame-normalization.md`), not by requesting a non-native capture resolution from the OS, which can introduce its own scaling artifacts.

On Windows, `scripts/snip_tool.py` is the capture primitive (`PrintWindow`, so occluded windows still capture), and `scripts/capture_app.py` wraps it into a content-cropped, canvas-fitted frame. On Android, `scripts/run_android_suite.py` drives `adb exec-out screencap -p` per screen and crops the status/navigation bars. Both paths reach the target state through launch arguments, not manual navigation — `--page`/`--theme`/`--state` extras on Android, a templated `--launch-args` string on Windows.

## 3. Capture reliability (avoiding blank/black frames)

A screenshot taken before the app/window has finished its first real render produces a black, blank, or partially-drawn frame. Scored against a real mockup, this reads as a catastrophic mismatch that has nothing to do with actual visual parity — and if the diagnosis step (`SKILL.md` Step 3) isn't aware this is a capture-reliability failure rather than a real regional score, it will waste cycles "fixing" a bug that doesn't exist.

- Wait for a positive signal that rendering is stable before capturing: a known UI element confirmed present, a fixed settle delay after navigation/launch (tuned to this app's actual cold-start time, not a guess), or a framework-specific "did finish rendering" hook if the platform exposes one.
- After capturing, run a cheap sanity check before treating the image as valid: is it suspiciously uniform in color (near-solid black, white, or a single brand splash color) across a large fraction of its area? If so, treat it as a capture failure — retry the capture (with a longer settle delay) rather than scoring it.
- This check matters most right after an app launch/deep-link, and right after any obstacle-screen bypass (`debug-state-simulation.md` §5) — both are moments where the app is mid-transition and most likely to be caught mid-render.

`scripts/run_suite.py` implements this as a gate before scoring, not after: a frame is rejected when grayscale standard deviation is below `blank_std`, when one exact colour covers more than `blank_dominant` of the image, or when at least three of four corners match a declared splash colour. Rejected frames are recaptured up to three times with a longer settle; a frame that still fails is recorded as `blank` and never scored. Two consecutive frames are also compared (`frames_stable`, mean absolute difference under 2.0 on a downscaled copy) so an animating or half-drawn frame does not become the baseline.

## 4. Comparison suite: what each metric is actually good for

Don't rely on a single global number — different metrics catch different failure modes, and a low score with no breakdown gives no actionable signal:

- **Structural similarity (SSIM or equivalent)** — sensitive to layout/structure: element position, size, and shape. Good at catching "this is in the wrong place" or "this is the wrong size." Not very sensitive to color-only differences.
- **Palette/color-fidelity comparison** (e.g. dominant-color extraction via k-means, or a color-histogram comparison) — catches "the structure is right but the colors are wrong" (a brand color that's slightly off, a dark-mode variant that isn't actually using the dark palette). SSIM alone can score deceptively high on a structurally-correct-but-wrong-colored screen.
- **Pixel-difference heatmap** — not a score by itself, but the visualization that makes regional diagnosis possible: overlay the absolute difference between the two normalized images and look at *where* the difference concentrates, not just how much there is.

Run all of these together, not just whichever is cheapest to compute — a screen that's failing on color alone and a screen that's failing on layout alone need completely different fixes, and a single blended score can't tell them apart.

`scripts/similarity.py` is the engine: five methods with separate scores (pixel `0.15`, ssim `0.30`, histogram `0.20`, perceptual hash `0.20`, ORB `0.15`, renormalised over whichever subset actually ran), plus k-means palette comparison, the 3×3 narrative breakdown, an N×N numeric grid and a jet heatmap. Beyond the three metrics above it adds two that answer different questions: **perceptual hash** (resize/compression-robust, useful when the two sides were captured at different densities) and **ORB feature matching** (local texture; a low match ratio with high SSIM usually means shared structure with a different icon or image set).

## 5. Regional grid scoring

Divide the normalized frame into a grid (a 4×4 grid is a reasonable default; finer for very tall/complex screens) and compute the comparison suite from §4 **per cell**, not just globally. This is what turns "72%, not sure why" into "the bottom-right cell is 30%, everything else is 90%+" — the signal `SKILL.md` Step 3's diagnosis step actually needs to act autonomously.

- Map low-scoring cells back to the actual UI elements occupying that screen region (a failing bottom row usually implicates a bottom nav bar/CTA; a failing top row usually implicates a header or status-bar-adjacent element).
- A **structural** failure pattern in the heatmap (bright, sharply-bounded regions — "things in the wrong place") points to a different fix category than a **texture/softness** failure pattern (diffuse, low-magnitude differences — often anti-aliasing, shadow blur, or minor sub-pixel rendering differences that may not be worth chasing below a reasonable point of diminishing returns).
- Re-run the full grid after every fix attempt, not just the previously-failing cell — a fix aimed at one region can move a previously-passing region's score too (usually for the better, occasionally for the worse — see `SKILL.md`'s regression-flagging rule).

Two details that decide whether the grid is usable:

- **Regional scores must be arithmetic, not narrative.** `similarity.py --regional-score N` emits the numeric N×N matrix *and* the pixel box of the worst cells, so the diagnosis step can hand a box to a crop tool instead of eyeballing a heatmap. `--no-region-report` exists for scripted runs where the prose is noise.
- **The crop tool must use the same split rule.** `scripts/region_crop.py` reuses `np.array_split` over row and column indices, so `mid-left` is byte-identical to the rectangle the scorer averaged. A crop tool with its own coordinate guess produces confident conclusions about the wrong pixels.

For component-level diagnosis (rather than a uniform grid), `scripts/parity_cut.py` takes named boxes from a JSON file and emits, per region, the design crop, the app crop, a labelled side-by-side pair, a heatmap and a score — which is what makes "the header card is wrong, the feed is fine" a direct observation instead of an inference from cell coordinates.

## 6. How the toolkit maps onto these steps

The `scripts/` folder is the executable form of this document. Each script owns exactly one step, and the chain is linear:

| Step | Script | What it guarantees |
|---|---|---|
| §1 mockup capture | `capture_mockup.py` | same URL, viewport, DPR, colour scheme, preloaded state every run |
| §1 matrix | `capture_batch.py` | every page × theme × variant captured, with a manifest |
| §2 Windows capture | `snip_tool.py` | `PrintWindow` capture that survives occlusion, DPI scaling and RTL mirroring |
| §2 + normalization | `capture_app.py` | chrome cropped by detection, content fitted onto the design canvas |
| §2 Android capture | `run_android_suite.py` | `adb screencap` per screen, OS bars cropped, launch extras forced |
| §3 reliability | `run_suite.py` | blank/splash/frame-stability gate with retries; never scores an unrendered frame |
| §4–5 scoring | `similarity.py` | five separate scores, palette, 3×3 report, N×N grid, heatmap |
| §5 localization | `region_crop.py` | crops that match the scored cells exactly |
| §5 component cuts | `parity_cut.py` | named-region pairs with per-region scores |
| loop iteration | `parity_run.py` | launch → wait → capture → normalize → score → align, one state at a time |
| whole matrix | `run_suite.py` | the loop across every state, with reports |
| regression gate | `pixel_regression.py` | exact app-vs-app diff with documented masks |

Two boundaries worth stating plainly:

- **This is a design-vs-app pipeline, not just a regression pipeline.** `similarity.py` and `parity_run.py` answer "does the app match the mockup". `pixel_regression.py` answers a separate question — "did this refactor change anything it shouldn't have" — and its gate is exactness rather than similarity. Run both; a build can look 95% like the design and still have regressed nine pixels that used to be correct.
- **The score is a diagnostic input, not the goal.** A number at threshold with a wrong-looking header still needs the regional grid read. The threshold decides *when to stop*, the regional signal decides *what to do next*.

Exact flags for every script: `scripts-reference.md`. JSON schemas for configs, regions and masks: `matrix-config.md`. Install and pipeline examples: `scripts/README.md`.
