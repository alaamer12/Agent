# `dom` reference

Saves the fully rendered, fully expanded DOM of JavaScript-heavy pages as static `.html` for scraping. A real headless Chromium runs the page's JS, then the command forces hidden content to load and serializes the result. Compare with DevTools "copy outerHTML" after you've clicked and scrolled everything, automated.

## Fast path
1. `capture.py dom https://example.com/products -o product.html`.
2. Add `--text` for visible text and `--api` for JSON responses seen on the wire.
3. Several pages use `--output-dir`; each becomes `<dir>/<name>.html`.
4. Add `--no-expand` where a click has side effects.
5. Add `--json` for paths/counts; `--quiet` for silent runs.

## Contents
- What "forcing content to load" does
- Options
- Outputs
- Parsing tips
- Limits
- `dom` vs `website`

## What "forcing content to load" does
Order of operations per page:
1. Navigate (`--wait-until networkidle` by default; a timeout is tolerated and the page is used as rendered so far). `--wait-for SELECTOR` waits for a known element first.
2. **Force loop** (skip with `--no-force`), up to `--max-rounds` (20):
   - first pass scrolls down a viewport at a time so IntersectionObserver-driven sections fire;
   - each round: click "show more" style buttons, scroll the window to the bottom, scroll inner scrollable panels (feeds, virtualized lists) to their bottom, pause `--scroll-pause-ms`;
   - stops after `--stable-rounds` (2) consecutive rounds where page height and element count don't change.
3. Final pass: open every `<details>`, flatten open **shadow DOM** into `<div data-shadow-root>` inside each host, promote lazy media (a `data-*` attribute whose value looks like a URL is a candidate and becomes the real `src`/`srcset`/`poster` when that is missing or a placeholder; a single candidate needs no name hint, with several the ones whose name hints at a source win, and ambiguous ones are left alone; `--lazy-attr NAME` adds explicit names; `loading=lazy` -> eager), make `href/src/srcset/poster/action` **absolute** (relative links are useless once the file is moved).
4. Optional: inline **iframes** (`--iframes`) as `<div data-iframe-src=...>` after each iframe.
5. Serialize with `page.content()`.

What gets clicked automatically (disable with `--no-expand`): `<button>`, `[role=button]`, `<summary>`, `a[href^="#"]` and href-less anchors whose short text equals, or starts with and is only slightly longer than (e.g. a trailing count), a "show more" phrase from `scripts/data/more_phrases.json` (many languages, including Arabic, Spanish, French, German, Chinese, Japanese; narrow with `--more-lang`, add with `--more-phrase` or `--more-pattern`), plus controls with `aria-expanded="false"` outside nav/header/menus/dialogs. Real links (`<a href="/page">`) are never clicked, so the page is never navigated away.

## Options
| Option | Default | Notes |
|---|---|---|
| `URL...` / `--url` / `--urls` | required | URLs, bare domains, local paths |
| `-o/--output` | none | Single page; when omitted, `<output-dir>/<name>.html`; `{n}` auto-numbers |
| `--output-dir`, `--out` | `.capture/dom` | Several pages: `<dir>/<name>.html`, name from the URL (`-o` names the dir too) |
| `--json`, `--quiet` | off | Machine-readable summary / no progress |
| `--no-force` | off | Plain rendered snapshot (still opens `<details>`, promotes lazy attrs, absolutizes links, flattens shadow DOM) |
| `--max-rounds` | 20 | Raise for very long feeds; the log warns when the cap is hit |
| `--stable-rounds` | 2 | Rounds without growth before stopping |
| `--scroll-pause-ms` | 800 | Raise for slow APIs |
| `--click SEL` | none | Extra selector clicked each round; repeatable. Use for site-specific "next batch" buttons |
| `--no-expand` | off | Don't auto-click buttons/accordions |
| `--more-lang CODE...` | all | Languages of "show more" phrases to recognise (codes from `more_phrases.json`, e.g. `ar es fr`) |
| `--more-phrase TEXT` | none | Extra button text meaning "show more"; repeatable |
| `--more-pattern RE` | none | Extra regex for such labels, in addition to the phrases |
| `--lazy-attr NAME` | none | Extra attribute holding a lazy-loaded media URL; repeatable |
| `--wait-for SEL` | none | Wait for an element before forcing |
| `--no-shadow` | off | Skip shadow-DOM flattening |
| `--iframes` | off | Include iframe contents (may add ads/trackers) |
| `--keep-relative` | off | Don't absolutize URLs |
| `--base-tag` | off | Inject `<base href>` so the saved file renders when opened (BeautifulSoup ignores it) |
| `--text` | off | Also write visible text to `<name>.txt` |
| `--api` | off | Also write JSON responses seen on the network to `<name>.responses.json` |
| `--wait-ms` | 2000 | Final settle before serializing |
| `--wait-until` | `networkidle` | Navigation readiness; `load` for long-lived connections |
| `--timeout` | 60000 | Navigation timeout (ms) |
| `--view` | `desktop` | `desktop` 1280x800, `wide` 1920x1080, `tablet` 768x1024, `mobile` 375x812; `--width`/`--height` override |
| `--device NAME` | none | Playwright device profile (viewport, UA, pixel ratio, touch); `--list-devices` prints names |
| `--scale` | 1 | Device pixel ratio |
| `--theme`, `--theme-key` | none | Emulate dark/light and seed the page's theme storage; see `theming.md` |
| `--storage-state FILE` | none | Playwright storage-state JSON (cookies/login) for pages behind a session; only for accounts you're allowed to use |
| `--user-agent`, `--headed` | browser-like UA | Override UA (env `CAPTURE_USER_AGENT` changes the default); show the browser for debugging |

## Outputs
- `<name>.html`: final DOM (UTF-8).
- `<name>.txt` (`--text`): `innerText` of the body; flattened shadow/iframe content is included.
- `<name>.responses.json` (`--api`): list of `{url, method, data}` for JSON responses (<= 2 MB each, <= 200). Often the cleanest data source: prefer it over parsing markup when it contains the fields you need.
- Console summary per page: rounds, clicks, details opened, shadow roots flattened, lazy attributes promoted, iframes included, size.

## Parsing tips
```python
from bs4 import BeautifulSoup
soup = BeautifulSoup(open(".capture/dom/example.com_products.html", encoding="utf-8"), "lxml")
items = soup.select(".product-card")          # all batches loaded, not just the first
shadow = soup.select("[data-shadow-root] p")   # content that lived in shadow DOM
frames = soup.select("[data-iframe-src]")      # inlined iframe content (with --iframes)
```
Sanity check completeness: count a known selector before and after (`--no-force` vs default) and compare with the page's own total ("245 results").

## Limits
- Pagination across URLs (`?page=2`, "Next" links) is not followed: pass each URL, or script the page numbers. For a link crawl of a whole site use `website --depth`.
- Content requiring login, search input, hover, drag, or multi-step flows isn't triggered (except via `--click` for simple buttons or `--storage-state` for sessions).
- Infinite feeds are bounded by `--max-rounds`; very long ones need a higher cap.
- A non-HTML response (PDF, JSON, image) is saved as the browser rendered it, with a warning. Numeric options and `--storage-state` are validated before the browser starts.
- Closed shadow roots and cross-origin iframes that block access can't be read.
- Anti-bot walls and consent overlays may block rendering; try `--headed` to see, or `--click` the consent button.
- Scrape only what you're permitted to; respect terms of service and rate limits (run pages sequentially; there's no parallelism).

## `dom` vs `website`
`dom` = all content as plain, parse-ready HTML (no assets, not viewable offline). `website` = a working offline copy (assets, JS, CSS), without forced expansion. See `choosing.md`. To analyse the design of a JS-rendered page (palette, components, CSS), save it with `dom` and pass it to `design --html-file`.
