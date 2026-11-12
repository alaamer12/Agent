# `designs` reference

Batch-captures every HTML design in a designs folder. Read this when the defaults don't fit (unusual layout, custom server, partial pages).

## Fast path
1. `capture.py designs --list` to confirm the folder and pages.
2. `capture.py designs --themes light dark --output-dir shots`.
3. PNGs land at `<output-dir>/<page>/design_<theme>.png` (default `.capture`).
4. Add `--json` for a machine-readable summary; `--quiet` for silent runs.
5. Only read the sections below when the folder or server is unusual.

## Contents
- Folder detection
- Page discovery and naming
- Options
- Using an existing dev server
- Output layout

## Folder detection
Order tried, relative to the CWD (stop at first hit):
1. `--dir <path>` (explicit; always wins)
2. Direct children with a conventional folder name (default `designs`, `design`, `mockups`, `mockup`, `wireframes`; replace the list with `--folder-names NAME...`)
3. Those same names inside hidden folders (e.g. `.config/design`)
4. Any directory with one of those names up to 3 levels deep (ignores `node_modules`, `.git`, `.venv`, `dist`, `build`)

If several candidates exist, run `--list` with each `--dir` and ask the user which is current. Do not guess between two plausible folders.

## Page discovery and naming
- Recursively collects `*.html` under the folder. Files beginning with `_` (partials/fragments) and ignored folders are skipped.
- Page name = path relative to the folder, no extension: `projects.html` -> `projects`, `mvp/settings.html` -> `mvp/settings`.
- The folder itself is the server root, so relative assets (`./css/app.css`, `../img/x.png`) resolve like they would in production.

## Options
| Option | Default | Notes |
|---|---|---|
| `--dir` | auto | Designs folder |
| `--folder-names NAME...` | defaults above | Folder names to look for when auto-detecting |
| `--list` | off | Print folder and pages, capture nothing |
| `--pages a b` | all | Names as above; `.html` suffix optional; unknown names error with the valid list |
| `--themes` | `light` | `light`, `dark`, or both (`--theme dark` = one theme) |
| `--theme-key` | none | localStorage key; see `theming.md` |
| `--output-dir`, `--out` | `.capture` | Output root (`-o` also names this folder) |
| `--view` | `desktop` | `desktop` 1280x800, `wide` 1920x1080, `tablet` 768x1024, `mobile` 375x812; `--width`/`--height` override either dimension |
| `--device NAME` | none | Playwright device profile (viewport, UA, pixel ratio, touch); overrides `--view`; `--list-devices` prints names |
| `--scale` | 1 | Device pixel ratio (retina = 2) |
| `--full-page` | off | Capture full scroll height (changes image height per page) |
| `--wait-ms` | 500 | Extra settle time after network idle |
| `--wait-until` | `networkidle` | `load` for pages with long-lived connections |
| `--storage-state FILE` | none | Playwright storage-state JSON (cookies/login) |
| `--timeout`, `--headed`, `--user-agent` | 30000 / off / browser default | Browser knobs shared by every browser command |
| `--base-url` | none | Skip the built-in server |
| `--json`, `--quiet` | off | Machine-readable summary / no progress |

## Using an existing dev server
Pass `--base-url http://localhost:5173` when the designs need a build step or a framework dev server. `--dir` is still used to enumerate page names; URLs become `<base-url>/<page>.html`.

## Output layout
```
<out>/<page>/design_<theme>.png
.capture/projects/design_light.png
.capture/projects/design_dark.png
.capture/mvp/settings/design_light.png
```
Add `.capture/` to `.gitignore` unless the user wants captures committed.
