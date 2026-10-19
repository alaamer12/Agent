---
name: capture
description: Capture visuals, files, data, or design from designs, web pages, sites, and apps, invoked as `/capture designs|screenshots|page|website|dom|design`. `designs` batch-screenshots HTML mockups; `screenshots` images URLs/HTML files; `page` images a running Windows app window; `website` downloads a whole site for offline use and verifies it; `dom` saves fully rendered, fully expanded HTML for scraping; `design` uses curl to dump a site's HTML and CSS (html.dump, css.dump) and extracts either design tokens (colors, typography, spacing...) or HTML/CSS usage patterns for a high-fidelity clone. Use whenever the user types /capture, or asks to screenshot, mirror, download, scrape, get a page's DOM, or extract a site's colors, fonts, design system, or HTML structure to clone or reference.
compatibility: Python 3.8+, curl (curl.exe on Windows), Playwright + Chromium (designs, screenshots, website, dom); pywin32 + psutil + Pillow on Windows (page)
---

# capture

One dispatcher, six commands (names are case-insensitive: `/capture DOM` = `dom`). Run from the project root so the designs folder can be auto-detected.

```
python <skill-dir>/scripts/capture.py <designs|screenshots|page|website|dom|design> [options]
```

## Choose the command

| Command | Produces | Use when | Does NOT |
|---|---|---|---|
| `designs` (plural) | PNGs, one per HTML design per theme | Reviewing/comparing the project's own mockups | Capture live sites |
| `screenshots` | PNGs of any URL/HTML file (viewport, full-page, scroll steps, slices) | A visual of a page at a given size | Save any HTML or assets |
| `page` | PNG of a running desktop app window (Windows) | Comparing a real app against a mockup | Work on web pages |
| `website` | A browsable offline copy: HTML, JS, CSS, fonts, images, data | The site must look and work the same offline ("perfect view") | Expand "load more"/accordions, or give analysed design data |
| `dom` | One parse-ready `.html` of the final rendered DOM (+ text, JSON API responses) | Scraping: all content in the markup | Keep styles/scripts working |
| `design` (singular) | `html.dump`, `css.dump`, `headers.dump`, plus `design-system.md/.json` (tokens) and/or `design-patterns.md/.json` (patterns) | Learning how a site is designed: its color/type/spacing system, or its HTML+CSS patterns to rebuild it faithfully, plus the technology it is built with (observed evidence, not a guess) | Run JS, download fonts/images, or give a viewable copy |

Key contrasts: **`website` preserves the experience** (files that run offline), **`dom` preserves the content** (everything the page can show, as plain HTML), **`design` extracts the design language** (analysed tokens and patterns, from raw curl dumps). `designs` (plural, screenshots of your own mockups) is not `design` (singular, analysis of a site). More: `references/choosing.md`.

For a bare `/capture`, infer from context (a designs folder exists -> `designs`), otherwise ask which one.

## `design` needs a mode: ask if unclear

`design` has two modes plus both:

- **tokens**: the design system (colors and palette ramps, CSS variables, typography, spacing, radius, shadows, motion, breakpoints, theming)
- **patterns**: HTML usage patterns (page skeleton, sections, repeated components with exemplar HTML and their CSS, naming conventions, layout recipes, custom elements, clone checklist)
- **both**

If the user's request does not make the mode clear, **ask them which one they want before running** (one question, options: tokens / patterns / both). Mentions of colors, fonts, typography, spacing, palette, "design system" mean tokens; HTML structure, components, markup, "clone", "reference to rebuild" mean patterns. Running without a mode exits with code 2 and prints the question to ask.

## Quick start

```
python scripts/capture.py designs                         # every .html in the designs folder, light
python scripts/capture.py screenshots example.com --view mobile --full-page
python scripts/capture.py page --pid 1234 --output .capture/home/app_v{n}.png
python scripts/capture.py website https://example.com --depth 1   # offline mirror + verification
python scripts/capture.py dom https://example.com/products --text --api   # scrape-ready HTML
python scripts/capture.py design tokens https://example.com        # colors, typography, spacing...
python scripts/capture.py design patterns https://example.com      # HTML patterns for a clone
```

Designs live in a designs folder and are normally `.html`. `designs` finds the folder (or take `--dir`), serves it on a local port itself, and writes `<out>/<page>/design_<theme>.png`. Use identical `--width/--height` for design and app captures so they align.

## Workflow

1. If anything fails to import or launch, run `python scripts/check_env.py` and apply the printed fix.
2. Run the command. Prefer `designs --list` first when the folder or page set is uncertain.
3. Check the evidence: dark captures need a look; `website` prints `VERIFY` lines; `dom` prints per-round growth; `design` prints counts (colors, variables, components): read `design-system.md` / `design-patterns.md` and confirm they match the site before reporting.
4. Report the saved paths and the key findings. For design-vs-app work, name the matching pairs.

## Where to read next

Load only what the task needs:

- `references/choosing.md`: commands compared side by side, common mix-ups, combining them
- `references/design.md`: the `design` pipeline, dump formats, every output section, technology evidence, options, JS-rendered pages, limits, using the outputs to clone
- `references/data-files.md`: the editable data files (technology signatures, trackers, "show more" phrases, colour names) and how to extend them
- `references/designs.md`, `references/screenshots.md`, `references/page.md`: image commands
- `references/website.md`: mirror, crawling, external hosts, verification, serving
- `references/dom.md`: forced loading, options, outputs, parsing tips
- `references/theming.md`: how light/dark is applied to screenshots
- `references/troubleshooting.md`: symptom -> fix table
- `examples/workflows.md`: ready-to-adapt command sequences
- `examples/sample-designs/`, `examples/tall-page.html`: tiny pages for smoke tests (`check_env.py --smoke`)

## Boundaries

- `page` needs Windows and `pip install pywin32 psutil pillow` (bundled `scripts/winshot.py` does the capture); elsewhere it exits with a clear message. Use `page --list` to find the window before capturing.
- `website`, `dom` and `design` only for sites the user owns or is permitted to copy/analyse; follow the site's terms. Copies and analyses are for reference, not republishing: when cloning from `design` output, rebuild the structure and styling with original content and assets rather than copying the site's text, images, or fonts.
- `design` uses curl, so it sees what the server sends. JS-rendered pages: run `dom` first and pass `--html-file`.
- `website --serve` / `--serve-only` block until Ctrl+C; only use them when the user wants a live local server.
- `dom` clicks buttons that look like "load/show/read more" and collapsed accordions; use `--no-expand` where clicks have side effects.
- Options are validated before any work starts (instant, offline failure) and runaway output is capped (`--max-shots`, `--max-pages`, `--max-bytes`). Exit codes: 0 success, 1 error, 2 usage (e.g. `design` without a mode), 130 interrupted with Ctrl+C.
- Do not silently report a "dark" capture that rendered light; check it.
