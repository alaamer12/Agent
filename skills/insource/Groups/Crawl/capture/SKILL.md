---
name: capture
description: Capture visuals, files, data, or design from designs, web pages, sites, and apps, invoked as `/capture designs|screenshots|page|website|dom|design|images`. `designs` batch-screenshots HTML mockups; `screenshots` images URLs/HTML files; `page` images a running Windows app window; `website` downloads a whole site for offline use and verifies it; `dom` saves fully rendered, fully expanded HTML for scraping; `design` uses curl to dump a site's HTML and CSS (html.dump, css.dump) and extracts either design tokens (colors, typography, spacing...) or HTML/CSS usage patterns for a high-fidelity clone; `images` downloads a page's images at their highest original resolution with scroll triggering, text/pixel range and size filtering, perceptual deduplication and a JSON report of every decision. Use whenever the user types /capture, or asks to screenshot, mirror, download, scrape, get a page's DOM, pull a page's images, or extract a site's colors, fonts, design system, or HTML structure to clone or reference.
compatibility: Python 3.8+ (`images` needs 3.10+); Playwright + Chromium (designs, screenshots, website, dom, images); curl (`design`); pywin32 + psutil + Pillow on Windows (`page`); curl_cffi + Pillow (`images`)
when_to_use: The user types /capture, or asks to screenshot a page or a running app window, mirror or download a site offline, get a page's rendered HTML for scraping, download a page's images at full resolution, extract a site's design tokens or HTML patterns, or compare any of those against the project's own designs.
argument-hint: "[designs|screenshots|page|website|dom|design tokens|design patterns|images] [url or options]"
---

# capture

Seven commands, one dispatcher. **This file routes; it does not teach.** Each command has exactly one
reference file, and you read only the one for the command you picked.

```
python <skill-dir>/scripts/capture.py <command> [options]      # command names are case-insensitive
```

## Pick a command, then read one file

| Command | Produces | Minimal run | Reference |
|---|---|---|---|
| `designs` | PNG per HTML design per theme | `... capture.py designs` | [references/designs.md](references/designs.md) |
| `screenshots` | PNG(s) of any URL or HTML file: viewport, full-page, scroll steps, slices, one element | `... capture.py screenshots example.com --view mobile --full-page` | [references/screenshots.md](references/screenshots.md) |
| `page` | PNG of a running Windows app window, OS chrome cropped | `... capture.py page --pid 1234 --output .capture/home/app_v{n}.png` | [references/page.md](references/page.md) |
| `website` | A browsable offline copy: HTML, JS, CSS, fonts, images, data, verified | `... capture.py website https://example.com --depth 1` | [references/website.md](references/website.md) |
| `dom` | One parse-ready `.html` of the fully expanded DOM (+ `.txt`, `.responses.json`) | `... capture.py dom https://example.com/products --text --api` | [references/dom.md](references/dom.md) |
| `design` | `html.dump`, `css.dump`, `headers.dump`, plus `design-system.md/.json` and/or `design-patterns.md/.json` | `... capture.py design tokens https://example.com` | [references/design.md](references/design.md) |
| `images` | Every image the page can show, largest original kept, duplicates dropped, + `report.json` | `... capture.py images --url https://example.com --scroll to-end --exclude "small|medium"` | [references/images.md](references/images.md) |

## Loading contract

| Situation | Read |
|---|---|
| You know the command | its reference row above, and nothing else |
| The command itself is unclear, or two were asked for at once | [references/choosing.md](references/choosing.md) |
| Light/dark correctness matters | [references/theming.md](references/theming.md) |
| A run failed, or the output looks wrong | [references/troubleshooting.md](references/troubleshooting.md) |
| A vocabulary must be extended (technology signatures, trackers, "show more" phrases, colour names) | [references/data-files.md](references/data-files.md) |
| Several commands must be chained | [examples/workflows.md](examples/workflows.md) |

Do not read a reference for a command you are not running, and do not read two for one command. Each reference
is self-contained: flags, output naming, limits, caveats.

## The pairs that get mixed up

- **`design` vs `designs`** — one letter, different jobs. `designs` (plural) screenshots *your own* HTML
  mockups from a designs folder. `design` (singular) analyses *someone else's site* via curl.
- **`website` vs `dom` vs `design` vs `images`** — `website` preserves the **experience** (files that run
  offline), `dom` preserves the **content** (everything the page can show, as static markup), `design` extracts
  the **design language** (tokens and patterns, as analysed data), `images` takes the **image bytes** only
  (originals, deduplicated). None of them substitutes for another.
- **`design` needs a mode**: `tokens` (colors, typography, spacing, radius, shadows, motion, breakpoints),
  `patterns` (page skeleton, repeated components with exemplar HTML and their CSS, naming, layout recipes), or
  `both`. If the request does not make it clear, **ask one question before running** — colors/fonts/design
  system means tokens; structure/components/markup/clone means patterns. Running without a mode exits 2 and
  prints the question to ask.
- **`page` vs `screenshots`** — a native app window (Windows, Win32 API) vs a web page rendered in a headless
  browser. Use identical `--width`/`--height` on both when comparing a design against the app.

## Every run

1. Run the command. `designs --list` first when the folder or page set is uncertain; `page --list` to find the
   window before capturing it.
2. If anything fails to import or launch, run `python <skill-dir>/scripts/check_env.py` once and apply the exact
   fix it prints (`--smoke` renders the bundled examples end to end).
3. Read the evidence before reporting: `website` prints `VERIFY` lines, `dom` prints per-round growth,
   `design` prints counts, `images` writes `report.json` — relay its `summary` counts and the feed-detection
   reasoning. Confirm `design-system.md` / `design-patterns.md` match the site.
4. Report saved paths and findings. For design-versus-app work, name the matching pairs.

## Cross-cutting rules

- Run from the project root so `designs` can auto-detect its folder; otherwise pass `--dir`.
- Options are validated **before any work starts**, so mistakes fail instantly and offline. Output is capped
  (`--max-shots`, `--max-pages`, `--max-bytes`, `--timeout`) against a runaway command.
- Exit codes: 0 success · 1 error · 2 usage (e.g. `design` with no mode) · 130 interrupted with Ctrl+C.
- `dom` clicks buttons that look like "load/show/read more" and collapsed accordions; use `--no-expand` where a
  click has side effects. `website --serve` / `--serve-only` block until Ctrl+C — only when the user wants a live
  local server.
- `design` uses curl, so it sees what the server sends, not what JavaScript builds: for a JS-rendered page run
  `dom` first and pass `--html-file`.
- Consent and use: run `website`, `dom`, `design` and `images` only on sites the user owns or is permitted to
  copy or analyse. Everything captured is **reference material, not republication** — when cloning from `design`
  output, rebuild structure and styling with original content and assets, and never pass credentials or
  session cookies into any of these commands to reach paid or private content.
- Do not report a "dark" capture that rendered light. Look at it.
