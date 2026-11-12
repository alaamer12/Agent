# `website` reference

Downloads a site into a folder so it can be served and used offline. A real Chromium browser loads the site and every response it receives is saved, so assets requested by JavaScript (chunks, fetched JSON, fonts, wasm, models, lazy images) are captured, not only what appears in the HTML.

> Need scrape-ready content (everything expanded, plain HTML) rather than a working copy? Use `dom`; see `choosing.md`.

## Fast path
1. `capture.py website https://example.com --output-dir mirror` (default `.capture/website/<host>`).
2. `--depth 1` also follows same-site links; `--external` saves CDN/font hosts.
3. Verification runs automatically; read the `VERIFY` lines before reporting.
4. `--serve-only mirror` serves the copy locally; `--json` emits the manifest summary.
5. `--depth 0` (default) is the fastest useful run.

## Contents
- What it does, step by step
- Options
- External hosts (CDNs, fonts)
- Crawling
- Verification
- Serving the copy
- Limits

## What it does, step by step
1. Opens the entry URL (default view `wide`, 1920x1080), waits `--wait-ms`, then scrolls down in `--scroll-steps` steps so lazy content loads.
2. Saves every successful `GET` response from the site's origin to disk, preserving URL paths. Extensionless HTML routes are saved as `route/index.html` so `/about` and `/about/team` can coexist.
3. Fetches icons/manifests referenced in `<link>`/`<img>` that the page never requested at runtime.
4. Rewrites text files (HTML, JS, CSS, JSON, SVG, XML) so absolute references to the site's origin become root-relative (`https://site.com/x.js` -> `/x.js`, also JSON-escaped forms), and removes `integrity="..."` attributes (hashes break once files are rewritten).
5. Verifies the copy (see below), writes `.capture-manifest.json` (source, time, pages, file count, verify result).

Default output: `.capture/website/<host>/`. Re-running into the same folder overwrites matching files and keeps the rest.

## Options
| Option | Default | Notes |
|---|---|---|
| `url`, `--url` | required | `https://` added if missing; `localhost` gets `http://` |
| `--output-dir`, `--out` | `.capture/website/<host>` | `-o` also names this folder |
| `--json`, `--quiet` | off | Machine-readable manifest summary / no progress |
| `--depth N` | 0 | Follow same-site links N levels. 0 = entry page + its assets |
| `--max-pages` | 50 | Crawl cap |
| `--delay-ms` | 0 | Pause between crawled pages; use for small or shared servers |
| `--ignore-robots` | off | By default links disallowed by robots.txt are skipped |
| `--no-head-check` | off | Do not probe crawled links by Content-Type; every same-site link is navigated |
| `--external [HOST ...]` | off | See next section |
| `--block HOST` | none | Never save assets from this host (repeatable); added to the default tracker blocklist |
| `--no-default-blocklist` | off | Ignore `scripts/data/trackers.txt`; only `--block` hosts are blocked |
| `--wait-ms` | 2000 | Settle time per page before scrolling |
| `--wait-until` | `domcontentloaded` | `load`/`networkidle` for pages whose assets appear later |
| `--scroll-steps` | 10 | 0 disables scrolling |
| `--timeout` | 30000 | Navigation timeout (ms) |
| `--view` | `wide` | `desktop` 1280x800, `wide` 1920x1080, `tablet` 768x1024, `mobile` 375x812; `--width`/`--height` override |
| `--device NAME` | none | Playwright device profile (viewport, UA, pixel ratio, touch); `--list-devices` prints names |
| `--scale`, `--headed`, `--user-agent` | 1 / off / browser default | Browser knobs shared by every browser command |
| `--theme`, `--theme-key` | none | Emulate dark/light and seed the page's theme storage; see `theming.md` |
| `--storage-state FILE` | none | Playwright storage-state JSON (cookies/login) for the download and verify passes |
| `--no-verify` | off | Skip the verification pass |
| `--serve`, `--serve-only DIR`, `--port`, `--open`, `--spa` | | See "Serving" |

## External hosts (CDNs, fonts)
Without `--external` only the site's own origin is saved, so pages that load Google Fonts, jsDelivr, etc. still need the internet. Then:
- `--external` (no hosts): save every other host except those on the blocklist (`scripts/data/trackers.txt`, a starter list of analytics/ads/telemetry domains; subdomains included). Add hosts with `--block HOST` (repeatable) or lift the defaults with `--no-default-blocklist`.
- `--external fonts.googleapis.com fonts.gstatic.com cdn.jsdelivr.net`: only those hosts (subdomains match).
Saved under `_external/<host>/...` and references are rewritten to `/_external/<host>/...`. Prefer an explicit host list when the site pulls many third-party calls.

## Crawling
`--depth 1` follows same-origin `<a href>` links from the entry page; `--depth 2` goes one level further, bounded by `--max-pages`. Before visiting a crawled link, `website` probes it with a HEAD request and skips anything whose `Content-Type` is not HTML/XML (PDFs, archives, images, media, and extensionless downloads alike); if the probe fails or HEAD is unsupported the link is visited. `--no-head-check` disables the probe. robots.txt is read once and honoured for followed links. Only link-following is bounded; every asset a visited page loads is saved.

## Verification
After downloading, the copy is served on a temporary local port and opened in the browser with the same scroll routine. The report lists:
- requests that returned 4xx/5xx or failed against the local copy (`404 /data.json`): files that were not captured, usually because they load only on interaction, after a delay, or from a URL with a query string;
- external hosts the copy still contacts: either rerun with `--external`, or accept that the copy needs the internet for those.

A clean run prints `VERIFY: local copy loaded with no failed requests`. Fix reported items by raising `--wait-ms`/`--scroll-steps`, adding `--depth`, or adding `--external`, then re-run.

## Serving the copy
- `--serve` (with the download) or `--serve-only DIR` (existing copy) starts a local server on `--port` (default 8000; falls back to a free port) bound to 127.0.0.1 with CORS enabled. It blocks until Ctrl+C. `--open` launches the browser.
- `--spa` serves `index.html` for unknown extensionless routes, for single-page apps with client-side routing.
- A copy is plain static files, so any static server works (`python -m http.server` in the folder). Open it over HTTP, not `file://`: root-relative paths and `fetch()` need a server.

## Limits
- Static snapshot: server-side behaviour (APIs with POST, auth, search, databases) is not reproduced. GET responses seen during the visit are saved, but a URL's query string is ignored when naming files, so endpoints differing only by query collide (last one wins).
- Content that loads only after clicks, logins, or long delays is missed; the verification report usually reveals it.
- Range/streamed media (video) and responses that are not HTTP 200 are skipped.
- URL path segments longer than a fixed limit are shortened with a hash (extension kept) to fit filesystem name limits; very deep URLs can still exceed Windows' total path length.
- Sites with strong anti-bot protection may block headless browsers.
- Respect the site's terms and copyright: mirror only what you own or have permission to copy.
