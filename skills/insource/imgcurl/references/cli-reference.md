# imgcurl CLI Reference

All flags are defined in `scripts/download_images.py`. This document is the authoritative flag contract for agents.

## Required

| Flag | Type | Description |
|------|------|-------------|
| `--url` | string | Page to visit. Must be a fully-qualified HTTP(S) URL. |

## Output

| Flag | Default | Description |
|------|---------|-------------|
| `--out` | `./downloads` | Directory where images and (by default) the report are written. Created if missing. |
| `--report` | `<out>/report.json` | Path for the JSON report. |
| `--no-pretty` | false | Emit compact (single-line) JSON instead of indented. |

## Scrolling

| Flag | Default | Description |
|------|---------|-------------|
| `--scroll` | `0` | Scroll strategy. Accepts three forms:<br>• integer → scroll that many pixels<br>• `to-end` / `to_end` / `end` → scroll until page bottom stabilizes<br>• any other string → treat as target text; stop when the text is in the viewport |
| `--scroll-step` | `800` | Pixels scrolled per step. |
| `--scroll-wait` | `700` | Milliseconds to wait after each scroll step (lets lazy images fire). |

## Filtering

| Flag | Default | Description |
|------|---------|-------------|
| `--between` | none | Keep only images whose `firstSeenAtScrollPx` falls inside a range. Forms:<br>• `min,max` (both integers) → pixel range<br>• `startText,endText` → resolve text positions via DOM search<br>• single text or number → from 0 to that point |
| `--exclude` | none | Drop images matching size rules. Comma- or pipe-separated tokens:<br>• labels: `small`, `medium`, `large`, `larger`<br>• dimensions: `200x200`, `<=400x400`, `>1200x1200`, or single number (`200` ≡ `200x200`) |
| `--min-bytes` | `0` | Skip images whose final buffer is smaller than this many bytes. |

Size labels (used by `--exclude` and reported in the JSON):

| Label | Max dimension |
|-------|---------------|
| small | ≤ 150 px |
| medium | ≤ 400 px |
| large | ≤ 1200 px |
| larger | > 1200 px |

## Timeouts

| Flag | Default | Description |
|------|---------|-------------|
| `--idle-timeout` | `10000` | `networkidle` wait after navigation (ms). |
| `--nav-timeout` | `30000` | Initial `page.goto` timeout (ms). |
| `--timeout` | `120000` | Hard overall deadline for the entire run (ms). Raises `TimeoutError` when exceeded. |

## Browser

| Flag | Default | Description |
|------|---------|-------------|
| `--headed` | false | Launch Chromium headed (useful for debugging). |
| `--concurrency` | `5` | Accepted for compatibility; currently unused. |

## Exit Behaviour

- Always writes a report (even on partial failure).
- Prints a one-line human summary to stdout.
- Non-zero exit only on uncaught exceptions or argparse errors.
