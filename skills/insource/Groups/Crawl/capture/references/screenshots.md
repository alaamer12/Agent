# `screenshots` reference

Capture one or many URLs / local HTML files with Playwright/Chromium. Read this when choosing a mode, a viewport, or when output naming matters.

## Contents
- Targets
- Modes
- Viewport, zoom, scale
- Limits and validation
- Output naming
- Waiting and lazy content
- Themes
- Caveats

## Targets
Positional, or `--url` / `--urls` (several allowed; duplicates are dropped):

| Input | Treated as |
|---|---|
| `https://x.com/a` | as is |
| `example.com/pricing` | `https://example.com/pricing` |
| `localhost:3000` | `http://localhost:3000` |
| `design/home.html` or `/abs/home.html` | `file://` (error if missing) |

Root-relative assets (`/css/app.css`) do not resolve under `file://`; use `designs` (serves the folder) or `--base-url` there instead.

One failing target does not stop the rest; failures are listed at the end and the exit code is 1.

## Modes
At most one. Default is a single viewport-sized image.

| Flag | Result | Use for |
|---|---|---|
| (none) | One image, viewport size | Above-the-fold, parity with a fixed-size app window |
| `--full-page` (`--big-shot`) | One image, entire page | Whole-page review |
| `--scroll` | One image per viewport step, `--overlap` px shared (default 100) | Reading long pages at real size, sticky headers visible |
| `--slices N` (`--symmetrical`) | N equal-height slices tiling the whole page, no overlap | Splitting a very tall page into reviewable chunks |
| `--selector CSS` | First matching element only | Components |

`--slices` clips in document coordinates, so a slice taller than the viewport is complete (an earlier approach clipped inside the viewport and cut tall segments). `--selector` cannot combine with the other modes.

## Viewport, zoom, scale
- `--view`: `desktop` 1280x800 (default), `wide` 1920x1080, `tablet` 768x1024, `mobile` 375x812. `--width` / `--height` override either dimension.
- `--zoom 50` (also `50%`, `0.5`): browser-style zoom. The CSS viewport is resized and the pixel ratio compensates, so layout, media queries and page height are correct and image size stays `width x height`. Below 100 fits more page into the same image; above 100 magnifies.
- `--scale 2`: device pixel ratio for sharper images (output is 2x pixels).
- The `--view` presets are generic sizes, not specific devices, and set only the viewport (no touch or user-agent emulation). For a real device use `--device "iPhone 13"`: Playwright's maintained profile (viewport, user agent, pixel ratio, touch). `--list-devices` prints the available names, and a near-miss name gets suggestions. `--device` cannot be combined with `--zoom`.

## Limits and validation
Options are validated before any browser starts, so mistakes fail instantly and offline. The limits are named constants at the top of `screenshots.py`; `--help` shows the defaults.
- `--width`/`--height` must be positive and within Chromium's practical texture limit; `--zoom` has a sane range; `--scale` is capped.
- `--scroll`: `--overlap` must be smaller than the viewport height (otherwise every step barely moves).
- `--scroll` and `--slices` are capped by `--max-shots` so a mistake cannot write thousands of images; `--slices` also refuses slices thinner than a minimum height and more slices than the page has pixels.

## Output naming
- `--output file.png`: one target, single-image mode. `{n}` becomes the next unused integer (`shot_v{n}.png`).
- Otherwise: `<output-dir>/<name>/<i>.png`, default dir `.capture/screenshots`. `<name>` is derived from the target: `example.com/a/b` -> `example.com_a_b`, `designs/home.html` -> `home`.
- With `--theme dark` the series files get a suffix: `1_dark.png`.
- `--output` with several targets, `--scroll` or `--slices` is an error that says to use `--output-dir`.

## Waiting and lazy content
- Default readiness is `networkidle`. Use `--wait-until load` for pages with websockets/polling that never go idle.
- `--wait-ms` (300) is extra settle time after load and after each scroll step; raise it for animations/charts.
- `--lazy` scrolls through the page once first so lazy-loaded images and sections render before a `--full-page` / `--slices` capture.

## Themes
`--theme` and `--theme-key`: see `theming.md`.

## Caveats
- Auth-gated pages are not supported; capture a mock/static state.
- Interactive states are only reachable if the page exposes them via URL params.
- Folder names derived from URLs are capped (long URLs get a short hash) and Windows-reserved names (`CON`, `NUL`, ...) get a `_` prefix.
- Sticky/fixed headers repeat in `--scroll` images (accurate to what a user sees) and appear once in `--full-page`/`--slices`.
- `--selector` fails immediately with a clear message when nothing matches (it does not wait for a timeout). Raise `--wait-ms` if the element renders late.
