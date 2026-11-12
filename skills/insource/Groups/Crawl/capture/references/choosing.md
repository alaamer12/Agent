# Choosing between the commands

Read this only when the command itself is unclear, or the user asked for two things at once. A single command's
flags and behaviour live in its own reference file.

## Fast path
1. Match the user's sentence to one "Answers" row in the side-by-side table.
2. If exactly one column fits, run that command and stop reading here.
3. If two still fit, read "The pairs people mix up".
4. If the user asked for two outputs, combine the commands (last section).

## Contents
- Side-by-side
- The pairs people mix up
- Combining commands
- Decision shortcuts

## Side-by-side

| | `designs` | `screenshots` | `page` | `website` | `dom` | `design` | `images` |
|---|---|---|---|---|---|---|---|
| Output | PNG per design/theme | PNG(s) per URL | PNG of app window | Folder of site files | One `.html` (+ `.txt`, `.responses.json`) | `html.dump`, `css.dump` + `design-system.md/.json` and/or `design-patterns.md/.json` | Image files + `report.json` |
| Source | Local HTML designs folder | Any URL or HTML file | Running Windows app | Live site | Live page(s) | Live page via curl (or `--html-file`) | Live page |
| Needs a browser | Yes | Yes | No (Win32 API, Windows only) | Yes | Yes | No (curl only) | Yes |
| Runs the page's JS | Yes | Yes | n/a | Yes | Yes | No (use `dom` first for JS-rendered pages) | Yes (scrolling triggers lazy loads) |
| Result works offline | n/a | n/a | n/a | **Yes** | No (markup only) | No (analysis, not a copy) | No (assets only, no page) |
| Styles/scripts preserved | n/a | n/a | n/a | **Yes** (that is the point) | No (links made absolute, nothing downloaded) | CSS preserved verbatim in `css.dump`; fonts/images/scripts only listed | n/a |
| Forces hidden content to load | No | `--lazy` only | No | Scrolls to trigger requests | **Yes**: scroll loop, load-more clicks, accordions, `<details>`, lazy attrs, shadow DOM, iframes | No | Scroll strategies: pixels, to-end, or until a text anchor |
| Follows links | No | No | No | `--depth N` | No (give it the URLs) | No (CSS `@import` chains only) | No (one page) |
| Verifies its result | No | No | No | **Yes** (VERIFY report) | Prints growth/stat counts | Prints counts; `sources.json` lists every fetch | **Yes** (`report.json` records every keep, drop and failure) |
| Answers | "what does it look like?" | "what does it look like?" | "what does the app look like?" | "give me the site" | "give me the content" | "how is it designed / built?" | "give me the pictures, biggest only" |
| Best consumed with | eyes / image diff | eyes / image diff | eyes / image diff | a browser | BeautifulSoup, lxml, regex | reading the `.md` reports; `grep` on the dumps | an asset folder plus the report |

## The pairs people mix up

**`design` vs `designs`**: one letter, different jobs. `designs` (plural) screenshots *your own* HTML mockups in a designs folder. `design` (singular) analyses *a site's* HTML/CSS and extracts tokens or patterns.

**`design` vs `website`**: `design` reads the CSS and HTML as data and tells you *how the site is built* (palette, type scale, components) without saving a runnable copy. `website` saves the files so the site *runs* offline. Use `design` to learn and rebuild, `website` to keep or browse.

**`design patterns` vs `dom`**: `dom` gives the full rendered markup (content). `design patterns` abstracts the markup into skeleton, components and the CSS that styles them (structure). For JS-rendered sites combine them: `dom` first, then `design patterns --html-file`.

**`design tokens` vs `screenshots`**: numbers and names vs pixels. Use screenshots to compare how it looks, tokens to reproduce it.

**`website` vs `dom`**
- `website` = "give me the site": it downloads the files so the page looks and behaves the same offline ("perfect view"), then verifies the copy loads without failures. The saved HTML is the original markup plus client-side JS that re-renders when opened; it does not click "load more" or expand accordions, so content that appears only after interaction is not in the markup.
- `dom` = "give me the content": it forces everything the page can show to load (scrolling, load-more, accordions, lazy images, shadow DOM, iframes) and saves the final DOM as static HTML. Parse it with no JavaScript. It is not a viewable copy: no CSS/JS/fonts are downloaded.
- Need both a faithful copy and all expanded content? Run both (see below).

**`images` vs `website`**: `website` saves every asset the page needs to *work*, one copy each, in the site's folder structure, with the original names and sizes the site chose. `images` saves only the image files, but takes the **largest original** of each (upgrading CDN-resized URLs), collapses duplicates of the same photograph, and filters by size or by where they sit on the page. Want the site? `website`. Want the artwork? `images`.

**`images` vs `screenshots`**: the page as pixels vs the pictures on it as files. `screenshots` renders what the viewport shows; `images` hands you the assets behind it, at their own resolution, so they can be reused or compared at full size.

**`images` vs `dom`**: `dom` records image **URLs** in markup (so you can see what is referenced, with alt text and surrounding content); `images` downloads the **bytes**. To find which image belongs to which article, run `dom`, then `images` with `--between` using text anchors from that markup.

**`screenshots` vs `website`**: an image of how a page looks vs the files that make it work. Use `screenshots` for evidence/comparison; `website` for an offline copy.

**`screenshots` vs `dom`**: pixels vs markup. Anything you want to extract as text/links/prices/attributes belongs in `dom`.

**`page` vs `screenshots`**: `page` grabs a native desktop app window (Windows); `screenshots` renders a web page in a headless browser.

**`designs` vs `screenshots`**: `designs` is the batch convenience for the project's own HTML mockups (auto-detects folder, serves it, themes, fixed naming). `screenshots` is for arbitrary URLs/files and richer capture modes.

## Combining commands
- Clone a site's look: `design both <url>` (read `design-system.md`, then `design-patterns.md`), then `screenshots` of the original and your clone to compare.
- Clone a site's look *with* its artwork: `design both`, `images --url <url> --scroll to-end --exclude small`, and `screenshots` for the visual reference.
- JS-rendered site: `dom <url> -o f.html`, then `design patterns <url> --html-file f.html`.
- Scrape a catalog and keep a copy: `website <url> --depth 1` for the offline copy, `dom <url> --api --text` for the complete content and JSON feeds.
- Design parity: `designs` + `page` with the same size (see `examples/workflows.md`).
- Document a site visually and structurally: `screenshots <url> --full-page --lazy` and `dom <url>`.

## Decision shortcuts
- "Save / download / clone / mirror the site", "browse it offline" -> `website`
- "Scrape", "get the HTML/DOM", "all the products/posts/links", "JS-rendered page", "load everything" -> `dom`
- "Screenshot", "what does it look like", "mobile view", "compare to the design" -> `screenshots` / `designs`
- "Download the images / the photos / the hero art from this page", "get the biggest versions, skip thumbnails" -> `images`
- "The running app / that window" -> `page`
- "Colors / fonts / design system / tokens of this site" -> `design tokens`
- "HTML structure / components / markup patterns / clone reference" -> `design patterns`
- `design` and the user didn't say which -> ask: tokens, patterns, or both
- "Images of the page" (a picture) vs "the page's images" (the files): first is `screenshots`, second is `images`
