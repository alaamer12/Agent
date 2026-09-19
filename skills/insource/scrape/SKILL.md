---
name: scrape
description: Fetch full framework documentation as clean local Markdown files. Commands per framework (currently `ionic` covering all guide pages + every API component page; capacitor/react/vue planned) plus `--auto` URL discovery for any Docusaurus-style docs site and explicit `--url` scraping, with a `--verify` mode that proves every page is reachable and server-rendered. Use whenever the agent needs authoritative external docs - e.g. Ionic component props/events/methods/CSS custom properties before building mobile UI, API reference lookups, or confirming doc URLs exist - instead of guessing from memory or fetching pages one by one.
---

# Scrape — full framework docs, locally

## Overview

One script, `scripts/scrape.py` (Python 3, `requests` + `beautifulsoup4` only), that downloads complete documentation sets as Markdown and guarantees nothing silently: every failure mode (404, JS-rendered page, thin content) is reported.

## Commands and flags

```
python3 scripts/scrape.py <mode> [flags]

Modes (exactly one):
  ionic                     All Ionic docs: 90 guide pages + every /docs/api/* component (from live sitemap)
  --auto START_URL          Best effort: sitemap.xml (incl. nested sitemapindex), else bounded BFS link crawl (<=300 pages)
  --url URL                 Explicit URL(s); repeatable, also accepts comma-separated

Flags:
  --output DIR              Write one .md file per page (URL path -> filename). Omit -> full content to stdout
  --verify                  Check all resolved URLs; print "OK" iff all pass; exit 1 with FAIL lines otherwise
  --workers N               Concurrent fetches (default 16)
  --min-chars N             verify-mode content threshold (default 120)
```

Examples:

```bash
S=<skill-dir>/scripts/scrape.py
python3 $S ionic --verify                          # gate: is the whole docs set alive & SSR? -> OK
python3 $S ionic --output scratch/docs-ionic       # cache ~186 pages, flattened names (api-button.md)
python3 $S --url https://ionicframework.com/docs/api/button          # single page to console
python3 $S --auto https://capacitorjs.com/docs --verify              # unregistered site, best effort
```

## Agent workflow (use this skill like this)

1. For Ionic work: cache once with `--output scratch/docs-ionic`, then answer from the local files with Grep/Read. Re-download only when stale.
2. For any other framework not yet registered: `--auto` first. If it discovers the right subtree, use it; if it discovers 0 or wrong pages, fall back to explicit `--url` of the pages you need and tell the user the site needs a registered command.
3. Never dump a whole multi-page scrape to the console — `--output` + targeted Read. Console output is for single pages.
4. Before trusting a cached set, `ionic --verify` must print `OK`.

## What "verify OK" guarantees

- HTTP 200 for every URL (redirects followed; 429 retried with backoff), AND
- the server HTML contains a content element (`div.theme-doc-markdown` / `article` / `main`) with >= `--min-chars` text — i.e. the page is genuinely server-rendered, not a JS shell. A page that would come back empty from a naive fetch fails as `THIN` / `JS-RENDERED` instead of silently producing an empty file.
- Scrape mode enforces the same per page (`EMPTY CONTENT`, `JS-RENDERED` are failures).

## Known caveats

- Generators proven end-to-end (discovery + full-content scrape): Docusaurus (Ionic, Capacitor), MkDocs Material (FastAPI), Sphinx (docs.pypi.org), mdbook + rustdoc (Rust Book: 113/113; stdlib Vec: 171 method signatures) — content selectors cover `theme-doc-markdown`/`article`/`main`/`#main-content`/Sphinx `div.body`.
- `--auto` resolves redirects (e.g. `doc.rust-lang.org/book` -> `/stable/book/`), filters versioned copies and non-HTML assets, and honestly reports source-site dead links (PyPI's own 4 broken attestations links show as FAIL — that is the site's fault, correctly caught).
- Sidebar/API lists are client-rendered; URL sets come from `https://ionicframework.com/docs/sitemap.xml` (current version only, `/v8/`-style versioned copies are filtered out).
- **API playground code examples are NOT in the server HTML** (rendered by JS into `div.playground`). Props/events/methods/CSS tables, prose, and anchors ARE. If an agent needs exact Angular/React/Vue snippet code, say so — it comes from the ionic-team GitHub repos, not this site.
- Ionic's own sitemap contains a few stale `developing/config/*` URLs that 404; `ionic` command is unaffected (hardcoded verified nav), `--auto` honestly reports them.

## Adding a new framework command (e.g. capacitor)

Lessons baked in — follow them or the command will lie:

1. **Titles != URL slugs.** Never kebab-case the sidebar title: `Developing for iOS` -> `developing/ios`, `What are PWAs?` -> `core-concepts/what-are-progressive-web-apps`, `iOS App Store` -> `deployment/app-store`. Resolve real URLs from the site's sitemap.xml.
2. In `scrape.py`, add a `<name>_NAV` dict (section -> [(title, path), ...]) and a `resolve_<name>(session)`; register the name in argparse `choices` and `main()`.
3. Run `<name> --verify` until it prints `OK`; only then document the command in this file.

## Resources

- `scripts/scrape.py` — the whole tool; run with `--help` for the same contract.
