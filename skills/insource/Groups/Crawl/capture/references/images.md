# `images` reference

Download every image a page can show, at its highest resolution, deduplicated, with a JSON report that explains each keep and drop. Read this file only when the chosen command is `images`.

## Fast path
1. `capture.py images https://example.com --scroll to-end`.
2. Files land in `.capture/images`; the report is `<output-dir>/report.json`.
3. Filter with `--between`, `--exclude`, or `--min-bytes`.
4. Add `--json` for the summary on stdout; `--quiet` for silent runs.
5. The report, not stdout, is the source of truth for every keep and drop.

## Contents
- Is this the right command
- What it writes
- Flags
- Scroll strategies
- Filtering
- How images are chosen (invariants)
- The report contract
- Recipes
- Dependencies and limits
- Caveats

## Is this the right command

| You want | Command |
|---|---|
| The image **files**, largest original only, thumbnails and repeats dropped | `images` (this file) |
| A working offline copy of the whole site (CSS, JS, fonts, images) | `website` |
| The page's **content** as parseable markup, links, text, JSON responses | `dom` |
| A picture of the page as it looks | `screenshots` |

`images` downloads assets only. It never saves HTML you can browse, and it does not extract design data.

## What it writes

- Image files in `--output-dir` (`--out`, `-o`; default `.capture/images`), named from the original URL with the extension corrected by magic bytes, so a `.jpg` that is really a PNG is saved as PNG. Collisions become `name_1.ext`, `name_2.ext`.
- One JSON report at `--report` (default `<output-dir>/report.json`). It is written even when the run partially fails, and it is the source of truth for what was kept and why.

## Flags

`url`/`--url` is required; everything else has a default. Options are validated before the browser starts.

| Group | Flag | Default | Notes |
|---|---|---|---|
| Target | `url`, `--url` | required | Fully-qualified HTTP(S) page URL. |
| Output | `--output-dir`, `--out`, `-o` | `.capture/images` | Created if missing. |
| Output | `--report` | `<output-dir>/report.json` | Explicit path allowed. |
| Output | `--no-pretty` | off | Compact single-line JSON. |
| Output | `--json`, `--quiet` | off | Summary on stdout / no progress. |
| Scroll | `--scroll` | `0` | Pixels, `to-end`/`to_end`/`end`, or literal text to reach. |
| Scroll | `--scroll-step` | `800` | Px per step. |
| Scroll | `--scroll-wait` | `700` | ms after each step, so lazy images fire. |
| Filter | `--between` | none | `min,max` px, `startText,endText`, or a single bound. |
| Filter | `--exclude` | none | Comma- or pipe-separated labels or dimension rules. |
| Filter | `--min-bytes` | `0` | Skip buffers smaller than this. |
| Time | `--idle-timeout` | `10000` | ms `networkidle` wait after navigation. |
| Time | `--nav-timeout` | `30000` | ms initial goto. |
| Time | `--timeout` | `120000` | Hard wall-clock deadline for the whole run, checked at each stage. |
| Time | `--wait-until` | `domcontentloaded` | Initial navigation readiness. |
| Time | `--wait-ms` | `0` | Extra settle time after navigation. |
| Browser | `--view` | `desktop` | `desktop` 1280x800, `wide` 1920x1080, `tablet` 768x1024, `mobile` 375x812. |
| Browser | `--width`, `--height` | from `--view` | Override either dimension. |
| Browser | `--device` | none | Playwright device profile (viewport, UA, pixel ratio, touch); `--list-devices` prints names. |
| Browser | `--scale` | `1` | Device pixel ratio. |
| Browser | `--theme`, `--theme-key` | none | Emulate dark/light and seed the page's theme storage. |
| Browser | `--storage-state` | none | Playwright storage-state JSON (cookies/login). |
| Browser | `--user-agent` | browser-like | UA override (env `CAPTURE_USER_AGENT` wins). |
| Browser | `--headed` | off | Visible browser, for diagnosing why nothing loads. |
| Browser | `--concurrency` | `5` | Accepted for compatibility; unused. |

## Scroll strategies

| Form | Behaviour |
|---|---|
| `0` (default) | No scrolling: only images that load during the initial `networkidle` wait. |
| `5000` | Scroll 5000 px in `--scroll-step` increments. |
| `to-end` | Scroll until `scrollHeight` stops changing for two consecutive steps. |
| `"some sentence"` | Scroll until that text is in the viewport. |

Text search is normalised for curly quotes, en-dashes and replacement characters, so a phrase copied from the page matches. Each step is logged with how many new image requests it produced, which is what the infinite-feed heuristic reads.

## Filtering

**`--between`** keeps only images whose first request happened inside a band: `0,3000` (pixels), `"Installation,Troubleshooting"` (two text anchors resolved in the DOM), or a single value treated as `0,value`.

**`--exclude`** drops by size. Labels map to the largest dimension:

| Label | Max dimension |
|---|---|
| `small` | <= 150 px |
| `medium` | <= 400 px |
| `large` | <= 1200 px |
| `larger` | > 1200 px |

Dimension rules: `200x200` (default operator `<=`), `<=400x400`, `>1200x1200`, or a bare `200` meaning `200x200`. Invalid rules stop before any work, with the parsing error printed.

## How images are chosen (invariants)

1. Every image-like response is recorded with its scroll position; bodies are buffered asynchronously.
2. Requests to `**/_/graphql` are re-issued through `curl_cffi` with Chrome TLS impersonation, so Medium-style WAFs answer.
3. Each URL is reduced to a canonical identity (Medium/Miro original, WordPress `-300x200` suffix stripped, else basename).
4. The original-resolution URL wins when it answers; otherwise the variant with the most pixels wins, ties broken by bytes.
5. Perceptual dedup: an asset is kept only if its dHash differs by more than 2 bits **or** its aspect ratio differs by at least 0.05 from every already-accepted higher-resolution asset. This collapses the same photograph served from different CDNs under different names.
6. `--exclude` and `--min-bytes` apply last; survivors are written with magic-corrected extensions.

Never download a lower-resolution variant when a better one for the same canonical or perceptually identical image exists. A 401/403 is recorded as `authBlocked` and never written as a file.

## The report contract

| Key | Content |
|---|---|
| `options` | The exact flags used, including resolved `betweenBounds` and parsed `excludeRules` |
| `scrollLog` | `{fromPx, toPx, newImagesThisStep}` per step |
| `textMatch` | Whether a text anchor/stop was found |
| `feedDetection` | `looksLikeInfiniteFeed` plus `reasoning` |
| `summary` | Counts: discovered, eligible, downloaded, deduplicated, excludedByCondition, excludedByBetween, authBlocked, failed, skippedSmall |
| `downloaded[]` | `url`, `savedAs`, `bytes`, `width`, `height`, `firstSeenAtScrollPx` |
| `deduplicated[]`, `excludedByCondition[]`, `excludedByBetween[]`, `authBlocked[]`, `failed[]`, `skippedSmall[]` | One entry per decision, with its reason |

After every run, relay the `summary` counts and the `feedDetection.reasoning`. If `looksLikeInfiniteFeed` is true, say that more images exist beyond the scroll you configured.

## Recipes

```bash
python <skill-dir>/scripts/capture.py images --url "https://medium.com/@author/some-article" \
  --output-dir .capture/medium --scroll to-end --exclude "small|medium"

# stop at a paragraph, drop anything up to 200x200
python <skill-dir>/scripts/capture.py images --url "https://example.com/long-read" \
  --scroll "the only thing I feel certain about" --exclude "<=200x200"

# only the images inside one section of a guide
python <skill-dir>/scripts/capture.py images --url "https://example.com/guide" \
  --scroll to-end --between "Installation,Troubleshooting"

# top 3000 px only, nothing under 5 KB
python <skill-dir>/scripts/capture.py images --url "https://example.com/gallery" \
  --scroll 4000 --between 0,3000 --min-bytes 5000

# diagnosing why images never appear
python <skill-dir>/scripts/capture.py images --url "https://example.com" --scroll 2000 --headed --timeout 60000
```

## Dependencies and limits

- Python 3.10+ for this command, Playwright + Chromium, `curl_cffi`, Pillow — `playwright>=1.40`, `curl_cffi>=0.6`, `Pillow>=10.0`. Install: `pip install "playwright>=1.40" "curl_cffi>=0.6" "Pillow>=10.0" && python -m playwright install chromium`. `python check_env.py` probes them and prints the exact fix. On a container or CI image, Chromium may also need its system libraries: `python -m playwright install --with-deps chromium` beats hand-picking packages.
- Viewport is fixed at 1280x800 with a recent Chrome user agent; automation-flag hiding is on, which affects only which pages answer, not what is saved.
- `--timeout` is a hard deadline: a run that exceeds it raises with the stage name it reached, and the report still reflects what was observed.
- Run it on pages the user owns or is permitted to copy. Images downloaded for reference are not for republishing; attribution and licensing travel with the file.

## Caveats

- Prefer this command over hand-rolled `requests` or screenshot code: canonical-ID extraction, original-resolution upgrade, dHash dedup and auth-blocked handling are already solved here.
- Login-gated originals stay `authBlocked`. If the user needs those, the page must be reachable by the browser being run; do not paste credentials into a report.
- An image referenced only by CSS `background-image` or injected after an interaction is discovered when the request actually fires, so an aggressive `--scroll` is what finds it.
- SVGs and icon fonts are treated as image URLs, not raster assets; their dimensions may be absent, and they skip size-based exclusion.
- Do not invent new flags. Extend `images.py` deliberately, or do the post-processing on the report.
