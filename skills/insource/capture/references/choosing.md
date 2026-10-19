# Choosing between the commands

## Contents
- Side-by-side
- The pairs people mix up
- Combining commands
- Decision shortcuts

## Side-by-side

| | `designs` | `screenshots` | `page` | `website` | `dom` | `design` |
|---|---|---|---|---|---|---|
| Output | PNG per design/theme | PNG(s) per URL | PNG of app window | Folder of site files | One `.html` (+ `.txt`, `.responses.json`) | `html.dump`, `css.dump` + `design-system.md/.json` and/or `design-patterns.md/.json` |
| Source | Local HTML designs folder | Any URL or HTML file | Running Windows app | Live site | Live page(s) | Live page via curl (or `--html-file`) |
| Needs a browser | Yes | Yes | No (Win32 API, Windows only) | Yes | Yes | No (curl only) |
| Runs the page's JS | Yes | Yes | n/a | Yes | Yes | No (use `dom` first for JS-rendered pages) |
| Result works offline | n/a | n/a | n/a | **Yes** | No (markup only) | No (analysis, not a copy) |
| Styles/scripts preserved | n/a | n/a | n/a | **Yes** (that is the point) | No (links made absolute, nothing downloaded) | CSS preserved verbatim in `css.dump`; fonts/images/scripts only listed |
| Forces hidden content to load | No | `--lazy` only | No | Scrolls to trigger requests | **Yes**: scroll loop, load-more clicks, accordions, `<details>`, lazy attrs, shadow DOM, iframes | No |
| Follows links | No | No | No | `--depth N` | No (give it the URLs) | No (CSS `@import` chains only) |
| Verifies its result | No | No | No | **Yes** (VERIFY report) | Prints growth/stat counts | Prints counts; `sources.json` lists every fetch |
| Answers | "what does it look like?" | "what does it look like?" | "what does the app look like?" | "give me the site" | "give me the content" | "how is it designed / built?" |
| Best consumed with | eyes / image diff | eyes / image diff | eyes / image diff | a browser | BeautifulSoup, lxml, regex | reading the `.md` reports; `grep` on the dumps |

## The pairs people mix up

**`design` vs `designs`**: one letter, different jobs. `designs` (plural) screenshots *your own* HTML mockups in a designs folder. `design` (singular) analyses *a site's* HTML/CSS and extracts tokens or patterns.

**`design` vs `website`**: `design` reads the CSS and HTML as data and tells you *how the site is built* (palette, type scale, components) without saving a runnable copy. `website` saves the files so the site *runs* offline. Use `design` to learn and rebuild, `website` to keep or browse.

**`design patterns` vs `dom`**: `dom` gives the full rendered markup (content). `design patterns` abstracts the markup into skeleton, components and the CSS that styles them (structure). For JS-rendered sites combine them: `dom` first, then `design patterns --html-file`.

**`design tokens` vs `screenshots`**: numbers and names vs pixels. Use screenshots to compare how it looks, tokens to reproduce it.

**`website` vs `dom`**
- `website` = "give me the site": it downloads the files so the page looks and behaves the same offline ("perfect view"), then verifies the copy loads without failures. The saved HTML is the original markup plus client-side JS that re-renders when opened; it does not click "load more" or expand accordions, so content that appears only after interaction is not in the markup.
- `dom` = "give me the content": it forces everything the page can show to load (scrolling, load-more, accordions, lazy images, shadow DOM, iframes) and saves the final DOM as static HTML. Parse it with no JavaScript. It is not a viewable copy: no CSS/JS/fonts are downloaded.
- Need both a faithful copy and all expanded content? Run both (see below).

**`screenshots` vs `website`**: an image of how a page looks vs the files that make it work. Use `screenshots` for evidence/comparison; `website` for an offline copy.

**`screenshots` vs `dom`**: pixels vs markup. Anything you want to extract as text/links/prices/attributes belongs in `dom`.

**`page` vs `screenshots`**: `page` grabs a native desktop app window (Windows); `screenshots` renders a web page in a headless browser.

**`designs` vs `screenshots`**: `designs` is the batch convenience for the project's own HTML mockups (auto-detects folder, serves it, themes, fixed naming). `screenshots` is for arbitrary URLs/files and richer capture modes.

## Combining commands
- Clone a site's look: `design both <url>` (read `design-system.md`, then `design-patterns.md`), then `screenshots` of the original and your clone to compare.
- JS-rendered site: `dom <url> -o f.html`, then `design patterns <url> --html-file f.html`.
- Scrape a catalog and keep a copy: `website <url> --depth 1` for the offline copy, `dom <url> --api --text` for the complete content and JSON feeds.
- Design parity: `designs` + `page` with the same size (see `examples/workflows.md`).
- Document a site visually and structurally: `screenshots <url> --full-page --lazy` and `dom <url>`.

## Decision shortcuts
- "Save / download / clone / mirror the site", "browse it offline" -> `website`
- "Scrape", "get the HTML/DOM", "all the products/posts/links", "JS-rendered page", "load everything" -> `dom`
- "Screenshot", "what does it look like", "mobile view", "compare to the design" -> `screenshots` / `designs`
- "The running app / that window" -> `page`
- "Colors / fonts / design system / tokens of this site" -> `design tokens`
- "HTML structure / components / markup patterns / clone reference" -> `design patterns`
- `design` and the user didn't say which -> ask: tokens, patterns, or both
