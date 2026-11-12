# Matrix configuration — JSON schemas

Four small JSON payloads drive the toolkit. All of them are plain data: no product names, no absolute paths baked into code, no schema versioning ceremony. Keep them next to the project's parity harness and commit them.

## Table of contents
1. `run_suite.py` config
2. Template tokens, per consumer
3. `run_android_suite.py` screens file
4. `parity_cut.py` regions file
5. `pixel_regression.py` mask file
6. Artifact layouts
7. Worked example: a full project harness

---

## 1. `run_suite.py` config

Pass with `--config parity.json`. Any command-line flag overrides the matching field, so the same file serves the unattended run and a single-state debug invocation.

| Key | Type | Default | Meaning |
|---|---|---|---|
| `exe` | string | — (required) | application binary to launch |
| `window_name` | string | basename of `exe` | process image name used for window lookup |
| `viewport` | `[w, h]` | `[1280, 800]` | design canvas; every capture is normalised to it |
| `mockup_dir` | string | `design` | folder served over HTTP as the mockup root |
| `base_url` | string | — | use an existing server instead of starting one |
| `launch_args` | list or string | `[]` | launch flag template, tokenised |
| `mockup_url_template` | string | `{base}/{page}.html?theme={theme}{variant_query}{state_query}` | reference page URL template |
| `pages` | list | `[]` | page ids |
| `themes` | list | `["light", "dark"]` | theme axis |
| `variants` | list | `["default"]` | data-source / locale / layout axis |
| `states` | list | `["default"]` | ItC state axis |
| `matrix` | list of objects | — | explicit states; replaces the cartesian product |
| `splash_colors` | list of `[r,g,b]` | `[]` | brand splash colours treated as "not ready yet" |
| `storage` | object | `{}` | mockup `localStorage` seeds, values tokenised |
| `blank_std` | number | `3.0` | grayscale std-dev below which a frame is blank |
| `blank_dominant` | number | `0.985` | single-colour share above which a frame is blank |
| `settle` | number | `5.0` | fixed settle seconds after the window appears |
| `min_area` | int | `200000` | ignore windows smaller than this (helper windows) |
| `fill` | string | `#F1F5F9` | canvas colour for padded areas |
| `chrome_crop` | string | `auto` | `auto`, `flat`, `dark`, `none`, or pixels |
| `threshold` | number | `0.90` | pass threshold on the raw overall score |
| `env` | object | — | extra environment variables for the launched binary |

### Matrix semantics

Without `matrix`, states are the cartesian product `pages × themes × variants × states`. State ids follow `page__variant__theme`, with `__state` appended when the state is not `default`:

```
home__default__light
home__default__dark
settings__beta__dark__filters-open
```

With `matrix`, the product is skipped entirely and only the listed states run. Object keys `page`, `theme`, `variant`, `state` — all optional except `page`:

```json
{
  "matrix": [
    {"page": "home",  "theme": "light", "variant": "default", "state": "default"},
    {"page": "home",  "theme": "dark",  "variant": "default", "state": "filters-open"},
    {"page": "about", "theme": "dark",  "variant": "beta",    "state": "default"}
  ]
}
```

Use the product for coverage. Use `matrix` when a page has no dark variant, or a state exists on only one screen — otherwise the product generates states that CANNOT be verified and the run fails on holes that are not bugs.

### Blank and splash detection

A frame is rejected before scoring when either check fires:

- **blank** — grayscale standard deviation below `blank_std`, *or* one exact colour covering more than `blank_dominant` of the image.
- **splash** — at least three of the four corners match one of `splash_colors` within 18 per channel.

A rejected frame is recaptured, up to three attempts, each attempt getting a progressively longer settle budget (+15s per retry). A frame that still fails is recorded as `blank` and never scored — the distinction between "not rendered" and "rendered wrong" is the whole point.

## 2. Template tokens, per consumer

Three scripts substitute tokens; each supports a slightly different set. Using an unsupported token leaves the literal `{token}` in the output, which usually fails loudly (bad path, bad URL) rather than silently.

| Token | `run_suite.py` | `parity_run.py` | `capture_batch.py` |
|---|---|---|---|
| `{page}` | yes | yes | yes |
| `{theme}` | yes | yes | yes |
| `{variant}` | yes | yes | yes |
| `{state}` | yes | yes | no |
| `{base}` | yes | no | yes |
| `{variant_query}` | yes | no | yes |
| `{state_query}` | yes | no | no |
| `{page_query}` | no | no | yes |

`{variant_query}` expands to `&variant=<id>` for a non-default variant and to an empty string otherwise; `{state_query}` behaves the same for the state. They exist so a default state does not leave `&state=default` in the URL, which some mockups treat as a real, distinct state.

`run_suite.py` applies the same substitution to `launch_args` and to `storage` values, so a mockup can be seeded per state:

```json
{
  "launch_args": ["--page={page}", "--theme={theme}", "--state={state}"],
  "storage": {"ui.theme": "{theme}", "ui.page": "{page}"}
}
```

## 3. `run_android_suite.py` screens file

Either a top-level object with a `screens` key or a bare array. Each screen object:

| Key | Type | Default | Meaning |
|---|---|---|---|
| `name` | string | — (required) | screen id; also the output folder and state id |
| `page` | string | `name` with `_dark` removed | value passed as the `default-page` intent extra |
| `theme` | string | `dark` if `name` ends `_dark`, else `light` | value passed as the `theme` extra |
| `extra` | object | `{}` | additional intent extras for this screen only |
| `crop` | object | `--crop-top` / `--crop-bottom` | pixel rectangle to keep, keys `top`, `bottom`, `left`, `right` |

```json
{
  "screens": [
    {"name": "home", "page": "home", "theme": "light",
     "extra": {"design-data": "1"}, "crop": {"top": 64, "bottom": 2270}},
    {"name": "home_dark", "page": "home", "theme": "dark",
     "extra": {"design-data": "1"}, "crop": {"top": 64, "bottom": 2270}},
    {"name": "settings", "crop": {"top": 64, "bottom": 2270}}
  ]
}
```

Crop values are absolute pixels in the device screenshot: `top` and `left` are offsets, `bottom` and `right` are coordinates. `bottom: 0` or a value beyond the image means "to the edge".

The intent built per screen is:

```
am start -S -a android.intent.action.MAIN -c android.intent.category.LAUNCHER \
  -n <component> -e default-page <page> -e theme <theme> [-e K V]...
```

Anything the app reads from intent extras can be driven this way, which is what makes the mobile suite loopable without a UI-automation framework.

## 4. `parity_cut.py` regions file

A flat object of `name → [x, y, w, h]`, in client-space pixels (the shared `--client-size` canvas):

```json
{
  "header_card": [1120, 0, 1280, 104],
  "search_row":  [64, 104, 1028, 184],
  "side_panel":  [1020, 104, 1280, 800]
}
```

Rules that matter:

- Boxes must fit inside the client canvas; anything outside is clamped by PIL and yields a smaller crop than expected.
- Name the region after the *component*, not after the coordinate, so the summary reads as a diagnosis.
- `--region NAME:X,Y,W,H` adds or overrides one entry from the command line; `--all-grid N` adds an `rNcN` grid on top. Both can be combined with `--regions-file`.
- `summary.json` in the output folder is ordered as the regions were declared, with `overall`, `ssim`, `palette` and the three worst inner cells per region.

## 5. `pixel_regression.py` mask file

```json
{
  "global": [[0, 0, 1280, 64]],
  "states": {
    "home__default__light": [[1040, 16, 240, 48]],
    "settings__default__dark": [[8, 740, 1264, 60]]
  }
}
```

- Rectangles are `[x, y, w, h]`. `global` applies to every state; `states` is keyed by the exact state id.
- Auto-loaded from `<baseline>/masks.json` when `--mask` is omitted, so a capture tree can carry its own mask and stay self-describing.
- Rectangles are zeroed in the diff before the exactness test — they do not "reduce" a difference, they erase it. Never mask a region you have not proven is genuinely dynamic (a live clock, a randomised feed, a user avatar).
- Masked rectangles still count toward the reported `total_pixels`, so the percentage column stays comparable across runs.

## 6. Artifact layouts

### `run_suite.py --all`

```
parity_out/
  <timestamp>/
    home__default__light__mockup.png
    home__default__light__app.png
    home__default__light__diff.png
    ...
    results.json
    report.md
  baseline.md              # only with --update-baseline
```

### `run_suite.py --capture-only`

```
parity_out/before/
  home__default__light/app.png
  home__default__light/          # pixel_regression adds diff.png here
  settings__default__dark/app.png
  manifest.json
  masks.json                     # optional, hand-authored
```

`manifest.json` records `generated_at`, `exe`, `exe_mtime`, `git_commit` (of the binary's directory), `settle_s`, `frame`, and a per-state list with `ok`, `app_png` and capture `meta`. It exists so a baseline can be traced back to the build that produced it — a capture tree without provenance is unusable six weeks later.

### `parity_run.py`

```
parity_out/
  <page>/
    app_<variant>_<theme>_v<N>.png
    app_<variant>_<theme>_v<N>_aligned.png
    diff_<variant>_<theme>_v<N>.png
    diff_<variant>_<theme>_v<N>_aligned.png
  report.md
  results.json
```

Versions never overwrite: the next free `v<N>` is chosen per page/variant/theme, so the capture history of a page stays inspectable across iterations.

### `parity_cut.py`

```
parity_cuts/
  design_<region>.png
  app_<region>.png
  pair_<region>.png
  heatmap_<region>.png
  design_full_<theme>.png        # live mode only
  app_full.png                   # live mode only
  summary.json
```

### `run_android_suite.py`

```
parity_mobile/
  <screen>/current_raw.png
  <screen>/current.png
  <screen>/heatmap.png
  report.md
  results.json
```

## 7. Worked example: a full project harness

A complete, product-agnostic starting point. Replace the placeholder values; nothing else changes.

```json
{
  "exe": "build/app.exe",
  "window_name": "app.exe",
  "viewport": [1280, 800],
  "mockup_dir": "design",
  "launch_args": ["--page={page}", "--theme={theme}", "--state={state}", "--data=fixture"],
  "mockup_url_template": "{base}/{page}.html?theme={theme}{state_query}",
  "storage": {"ui.theme": "{theme}"},
  "pages": ["home", "settings", "profile"],
  "themes": ["light", "dark"],
  "variants": ["default"],
  "states": ["default"],
  "splash_colors": [[255, 255, 255]],
  "settle": 4.0,
  "threshold": 0.92
}
```

Three commands then cover the whole pipeline:

```bash
# 1. reference frames for the whole matrix (a reference archive you keep and diff)
python scripts/capture_batch.py --base-url http://localhost:8000 \
    --design-root design --pages home settings profile \
    --themes light dark --out-root parity_captures

# 2. score everything; this run serves the HTML folder itself
python scripts/run_suite.py --config parity.json --all

# 3. gate a refactor on byte-identical output
python scripts/run_suite.py --config parity.json --all --capture-only --out out/before
python scripts/run_suite.py --config parity.json --all --capture-only --out out/after
python scripts/pixel_regression.py --baseline out/before --current out/after
```

Step 2 does **not** consume step 1's PNGs. `run_suite.py` serves `mockup_dir` (the HTML folder) and requests `{page}.html?theme=...` per state, capturing its own reference frame inside each run. `capture_batch.py` output is a separate artifact: a stable set of reference images you can inspect, archive, or compare against a design handoff without re-rendering. Point step 2 at the served HTML, not at the PNG archive.

Step 3 replaces `<mockup_dir>` with nothing: `--capture-only` captures the app side only, so the two trees are pure app-vs-app and `pixel_regression.py` gates exactness with no design involved.
