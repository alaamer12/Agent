# `siteshots` reference

Finds a site's routes, then screenshots each one top to bottom as an overlapping series of images. One run
answers "show me the whole site" without naming a single URL by hand.

> Need an image of **one** page and any of its capture modes (full-page, slices, one element)? Use `screenshots`.
> Need the site's **files** to run offline? Use `website`. See `choosing.md`.

## Fast path
1. `python scripts/capture.py siteshots https://example.com` (writes `.capture/siteshots/<host>/`).
2. Read `report.json`: `meta.method` says whether routes came from a sitemap, the crawler, or `--routes`.
3. Check `summary.errored`; each failed URL is listed with its error under `pages.errored`.
4. Add `--max-pages N` to keep a first run small, `--routes "about, contact"` to skip discovery entirely.

## Contents
- What it does, step by step
- Route discovery order
- Locale handling
- Slug collapsing
- Navigation-safe capture
- Options
- Output and report
- Limits
- Consent

## What it does, step by step
1. Normalises the entry URL (`https://` added for a bare host, `http://` for localhost).
2. Discovers routes in the order below, then keeps only the entry URL's locale.
3. Collapses families of slug routes into one representative page each (unless `--all-routes`).
4. Caps the list at `--max-pages` and launches one browser.
5. For each route: navigate, wait until the URL and `document.readyState` stop changing, measure the page,
   scroll in overlapping steps, and screenshot the viewport at each step into `<output-dir>/<route-folder>/`.
6. Writes `report.json` and prints a summary; a route that still fails after one retry makes the run exit 1.

Viewport defaults to `mobile` (375x812), unlike the other browser commands, because route sweeps are usually
reviewed on a phone layout. Override with `--view`, `--width/--height`, `--scale`, or `--device`.

## Route discovery order

| Order | Source | What is read |
|---|---|---|
| 1 | `robots.txt` | Every `Sitemap:` line, on the **origin** (not under the entry path) |
| 2 | Sitemap | `<sitemapindex>` children expanded recursively (depth 3), `.xml.gz` decompressed, `&amp;` decoded, `<xhtml:link rel="alternate">` locale URLs included |
| 3 | Standard sitemaps | Locale-prefixed paths first, then `/sitemap.xml`, `/sitemap.xml.gz`, `/sitemap_index.xml`, `/sitemap-index.xml`, `/wp-sitemap.xml`, `/sitemap/sitemap.xml`, `/sitemaps/sitemap.xml` |
| 4 | Playwright crawler | Same-origin `<a href>` links, breadth-first, bounded by `--max-depth` (default 3) and `--max-pages` |
| 5 | `--routes` | Your list; nothing is discovered |

A sitemap is authoritative when it exists: no crawling, far fewer requests, and pages that are not linked from
the entry page still get captured. `--force-crawl` skips steps 1-3 when a sitemap is stale or wrong.

Sitemap `<loc>` values that point at another XML file, a PDF, an image, or anything not on the entry origin are
dropped. A child sitemap is read, never screenshotted as if it were a page.

`--routes` accepts bare names, rooted paths, and full URLs in one comma/space-separated string:
`--routes "about, /eg/contact, https://other.test/y"` (bare names are resolved against the entry origin).

## Locale handling

A bilingual site publishes both `?lang=ar` and `?lang=en` (or `/ar/` and `/en/`) for the same page. Capturing
both doubles the run and mixes languages in one folder. `siteshots` reads the locale from the entry URL and:

- keeps only URLs with the same `lang`/`locale`/`language`/`hl` query value, when the entry has one;
- keeps the entry's path prefix (`/eg/...`) and drops sibling locale trees (`/sa/...`), while keeping shared
  paths that are not language-prefixed at all.

Falling back never empties the run: if no URL matches the entry's locale, everything discovered is kept. Pass the
entry URL in the language you want captured — `https://snduk.com/eg?lang=ar`, not the bare domain.

## Slug collapsing

`/funds/alpha`, `/funds/beta`, `/funds/gamma` are the same page template with different data. Capturing all three
(and every fund on a catalog site) produces thousands of near-identical images. By default the family becomes one
`[slug]` pattern plus one real example page, and `report.json.routes.patterns` records the pattern, the example,
and up to 100 variants. Names in `scripts/siteshots.py`'s `STATIC_NAMES` (`about`, `pricing`, `login`, ...) are
never collapsed together, and a family of one is captured as itself.

`--all-routes` (alias `--no-collapse`) disables collapsing and captures every discovered URL. Use it when the
user wants each item of a catalog, and raise `--max-pages` deliberately.

The example page keeps the entry's locale (`?lang=ar` survives), so collapsing never silently switches language.

## Navigation-safe capture

Single-page apps and A/B scripts redirect shortly after load. The capture loop survives that:

- waits for two identical readings of `page.url` and a `document.readyState` of `interactive`/`complete`, plus
  `--wait-ms`, before measuring the page;
- retries `evaluate` and `screenshot` up to 3 times when Chromium reports a destroyed execution context, a
  detached frame, or an interrupted navigation;
- restarts a route's whole series (its folder is wiped first) once if the context dies mid-series;
- takes the final URL into account (`pages.succeeded[].finalUrl`), so a route that redirects is reported by where
  it ended up.

Add `--wait-for "<selector>"` when the page is known to render its main content late; `--wait-until networkidle`
is rarely needed and can hang on pages with long-lived connections.

## Options

| Flag | Default | Meaning |
|---|---|---|
| `url` / `--url URL` | required | Entry URL; `https://` added for a bare host |
| `-o, --output, --output-dir, --out DIR` | `.capture/siteshots/<host>` | Folder holding one subfolder per route |
| `--routes LIST` | — | Manual routes; skips discovery |
| `--force-crawl` | off | Skip robots/sitemaps, use the Playwright crawler |
| `--max-depth N` | 3 | Crawler link depth |
| `--max-pages N` | 50 | Cap on **captures** (after collapsing) |
| `--all-routes`, `--no-collapse` | off | Capture every discovered URL |
| `--max-shots N` | 500 | Cap on images for one route |
| `--overlap PX` | 100 | Shared pixels between scroll steps; must be smaller than the viewport height |
| `--wait-ms N` | 500 | Settle time after load and between scroll steps |
| `--wait-for CSS` | — | Wait for this selector before the first screenshot |
| `--wait-until` | `domcontentloaded` | `networkidle`, `load`, or `domcontentloaded` |
| `--report FILE` | `<output-dir>/report.json` | Report path |
| `--delay-ms N` | 0 | Pause between routes (small or shared servers) |
| `--view/--width/--height/--scale` | `mobile` 375x812 @1x | Viewport and pixel ratio |
| `--device NAME`, `--list-devices` | — | Playwright device profile instead of the viewport |
| `--theme`, `--theme-key` | untouched | Emulate light/dark and toggle `.dark`/`data-theme` |
| `--timeout MS`, `--headed`, `--user-agent`, `--storage-state FILE` | 30000 / off / default / — | Same as every browser command |
| `--json`, `--quiet` | off | Machine-readable summary on stdout / no progress |

Values are validated before the browser starts; `--overlap` must be smaller than the viewport height, and
`--scale` must be between 0 and 8.

## Output and report

```
.capture/siteshots/example.com/
├── report.json
├── example.com_              # route "/" (1.png, 2.png, ... top to bottom)
├── example.com_eg_about/
└── example.com_eg_funds_1a2b3c/   # folders carrying a query get a short hash
```

The report keeps the capturer's shape, extended with the pattern list:

```json
{
  "command": "siteshots",
  "meta": {"targetUrl": "...", "method": "sitemap (robots.txt)", "viewport": "375x812",
           "overlap": 100, "collapsed": true},
  "routes": {"method": "...", "discovered": 12,
             "patterns": [{"type": "dynamic", "pattern": "https://site/funds/[slug]",
                           "example": "https://site/funds/beta?lang=ar", "slugs": ["alpha", "beta"]}]},
  "summary": {"total": 12, "succeeded": 12, "failed404": 0, "failed5xx": 0,
              "errored": 0, "totalShots": 87, "avgShotsPerPage": 7.25},
  "pages": {"succeeded": [{"url": "...", "finalUrl": "...", "dir": "...", "shots": 8}],
            "404": [], "5xx": [], "errored": [{"url": "...", "error": "...", "dir": "..."}]}
}
```

Report `summary` counts and the discovery `method`; do not claim a sitemap when it says `playwright`, and do not
claim full coverage when `failed404`/`errored` is non-zero.

## Limits
- At most 50 sitemaps are read, each up to 8 MB, with index recursion limited to depth 3. Larger sites: raise
  `--max-pages` for coverage and pass a `--report` you can inspect.
- One browser, sequential routes: a 50-route sweep is slow by nature. Use `--max-pages` for a first pass,
  `--delay-ms` on small servers, and `--quiet`/`--json` when the console noise is not useful.
- `--storage-state` is the only auth mechanism (a Playwright state file the user already has). Never feed
  credentials or session cookies to reach paid or private content, and never use the capturer's cookie exporter
  for that purpose.
- Captures are reference material, not republication: run this on sites the user owns or may copy, and rebuild
  with original content when cloning.

## Consent
Only run on sites the user owns or is permitted to copy or analyse. Screenshotting every route of someone else's
site is a load on their server even when the pages are public; use `--max-pages`, `--delay-ms`, and
`--overlap`/`--max-shots` to keep it modest.
