# `design` reference

Extracts how a site is designed. Two angles, one pipeline:

- **tokens**: the design system (colors, typography, spacing, ...)
- **patterns**: HTML usage patterns with their CSS, for a high-fidelity clone

## Fast path
1. Pick the mode: colors/fonts/spacing -> `tokens`; structure/components/markup/clone -> `patterns`.
2. `capture.py design tokens https://example.com -o colors.md`.
3. Reports also land in `--output-dir` (default `.capture/design/<name>`): `design-system.md/.json` and/or `design-patterns.md/.json`.
4. `-o report.json` or `--format both` chooses a single consolidated artifact.
5. Add `--json` for a summary; `--quiet` for silent runs.

## Contents
- Choosing a mode
- Pipeline and dumps
- `tokens` output
- `patterns` output
- Technology evidence
- Options
- JS-rendered pages
- Using the output to clone
- Limits

## Choosing a mode
`capture.py design <mode> <url>`; modes: `tokens`, `patterns`, `both`. Aliases: `system`, `colors`, `typography` -> tokens; `clone`, `html` -> patterns; `all` -> both. **If the user hasn't made the mode clear, ask** (the command exits with code 2 and prints the question when the mode is missing).

## Pipeline and dumps
1. **curl** (`curl.exe` on Windows, so PowerShell's `curl` alias is never used) fetches the page: `-L --compressed`, redirects followed, `--max-time` 30. A local file (path or `file://` URL) works too; relative stylesheets are resolved against it.
2. Stylesheets are discovered from `<link rel=stylesheet>` (and `preload as=style`), fetched with curl, and `@import` chains are followed (depth 3). Non-CSS responses (HTML 200 pages for missing files) and HTTP errors are skipped and recorded.
3. Dumps are written to the output folder (default `.capture/design/<host>/`):

| File | Content |
|---|---|
| `html.dump` | Page HTML as served, decoded with its declared charset and saved as **UTF-8**; first line is a provenance comment (`<!-- capture:design source=... encoding=... -->`) |
| `css.dump` | All CSS concatenated. Each source is wrapped: `/* ===== SOURCE: <url or label> \| <status, bytes> ===== */ ... /* ===== END ===== */`. Includes linked sheets, `@import`ed sheets, inline `<style>` blocks, and inline `style=""` attributes as `tag.class { ... }` rules |
| `sources.json` | Every fetch with status, bytes, errors, tool used |
| `headers.dump` | Response headers of the page request (final response after redirects). Cookie **values are redacted** (names kept). Absent when analysing `--html-file` or a local file |

4. The analysis reads **only the dumps** (so `--reuse` re-analyses without network, and results always match the dump), including `headers.dump` for technology evidence.

## `tokens` output
Files: `design-system.md` (readable) and `design-tokens.json` (same data, structured).

Sections:
- **Summary**: color scheme, color counts, variables, body/code font, font-size range, spacing grid, breakpoints, unit usage
- **Colors**: palette ramps from variables named like `--prefix-name-step` (one row per ramp); color variables outside ramps; colors in use (counted after resolving `var()` chains; hex-normalized from rgb/hsl/named; with hue/sat/light, neutral vs accent, and the roles: text/background/border/svg/shadow); **which tokens are used for which role** (e.g. which variable is the main text color)
- **Variables**: named scales (`--margin-xs..xxxl`, `--text-*`, `--br-*`, ...) with resolved values and **per-breakpoint overrides**; other variables; **context-switching variables** (families re-pointed by classes/attributes, a common theming mechanism)
- **Theme/variant scopes**: selectors or colour-scheme media queries that re-define most of the root's variables, found structurally (a theme called `.night` is detected as readily as `.dark`)
- **Typography**: `@font-face` table (family, weight, style, stretch, display, files), font stacks, distinct font sizes (px) with how they are authored, **type styles** (size + weight + line-height + letter-spacing + family + transform with example selectors), base element styles (body, h1-h6, code...), weights, line heights, letter spacing, text transform
- **Spacing / Radius / Borders / Shadows & effects / Gradients / z-index / opacity**
- **Motion**: durations, easings (cubic-bezier, ease...), transitioned properties, `@keyframes`, reduced-motion rules
- **Breakpoints and layout**: media-query widths, display/position/flex/grid usage, max-widths, modern CSS features and selector features (`:has`, `:is`, `:where`, container queries...)

Notes: values assume `1rem = 16px`; `var()` is resolved using the `:root`/`html` definition; fonts and images are listed, not downloaded.

## `patterns` output
Files: `design-patterns.md` and `design-patterns.json`.

Sections:
- **Overview**: class-naming verdict (BEM / utility-first / semantic + utility layer / hand-written; utility-first is measured from the stylesheet, not guessed from class names), landmarks, custom elements, technology summary, media counts
- **Document skeleton**: collapsed tag/id/class outline of `<body>` (repeated siblings shown as `xN`), head meta list
- **Page sections** in order: element, heading, contents, layout hints from CSS, child blocks
- **Head and assets**: stylesheets, preloads, icons, scripts (src, type, async/defer, inline size)
- **Technology evidence**: identified technologies with confidence and raw traces (see below)
- **Class conventions**: prefix families, most-used classes, JS-toggled state classes (classes CSS uses as modifiers, such as `.menu.is-open`, that never appear in the served HTML; found structurally, not by name)
- **Repeated components**: detected by structural signature (tag + classes + child structure, appears 3+ times). Each has the structure signature, parent, an **exemplar HTML snippet** (text replaced by `…`; `--keep-text` keeps truncated text), and the **CSS rules** that style its classes (with media context). Rules shared between components are listed once
- **Custom elements**: tags with a hyphen, counts, attributes with sample values, CSS rule counts
- **Variants, hooks and state**: attribute selectors used for variants (`[size=large]`, `[boxed]`, `[data-color]`), `data-*` attributes, ARIA/roles, ids referenced by CSS
- **Layout system**: centered max-width wrappers; flex/grid recipes for classes actually in the HTML; breakpoints
- **Media, icons, forms**; **Clone checklist** (ordered build steps)

## Technology evidence

A closed list of library names goes stale and silently misses anything new or unlisted, so detection works as **facts first, names second**:

1. **Raw evidence** (needs no vocabulary, so it works for technology the skill has never heard of): generator meta tags; informative response headers; cookie **names** (values never stored); packages inferred from CDN/URL grammars (`name@version`); attribute-prefix families (`hx-`, `wire:`, `data-astro-*`...); generated class-name shapes (`name-hash`, `module__hash`); inline JSON/script ids; window globals set inline; CSS banners; third-party hosts (labelled when on the tracker list); build fingerprints (content-hashed assets, module scripts, importmap, service-worker registration); html/body markers; informative HTML comments.
2. **Attribution** from `scripts/data/tech_signatures.json`: a starter set of fingerprints (static-site generators, meta-frameworks, UI and CSS frameworks, CMS and site builders, hosting/CDN, web servers, server frameworks). Each match gets a confidence: **high** = at least one strong signal, **medium** = two or more medium signals, **low** otherwise. Extend or override per run with `--signatures FILE`; see `data-files.md`.

Rules the report follows:
- A missing name never means the technology is absent. Server-side frameworks (Express, Hono, Django...) are visible only if they leave a header, cookie, form field or marker.
- URL signals match host and path only; query strings and fragments are ignored (so `?placement=animejscom` on an ad script does not identify anime.js).
- Header evidence needs a live fetch; with `--html-file` or a local file the report says headers were unavailable.
- Treat `low` as a lead to verify, not a finding.

## Options
| Option | Default | Notes |
|---|---|---|
| `MODE URL` (or `--mode`, `--url`) | required | Mode aliases: `colors`/`typography`/`system` -> tokens, `clone`/`html` -> patterns, `all` -> both. URL can be a bare domain (`https://` added; `localhost` gets `http://`) or a local file path |
| `--output-dir`, `--out` | `.capture/design/<name>` | `<name>` = host + path slug (`example.com_pricing`), plus a short hash when the URL has a query, so different pages never overwrite each other. Names are capped (long URLs get a hash) and Windows-reserved names are avoided |
| `-o, --output FILE` | none | Also write one consolidated report; `.md`/`.json` chooses the format |
| `--format` | inferred | `md`, `json`, or `both` for `-o` (extension wins unless `--format` is given) |
| `--json`, `--quiet` | off | Machine-readable summary / no progress |
| `--reuse` | off | Re-analyse existing `html.dump`/`css.dump`; no network |
| `--html-file F` | none | Use this HTML (e.g. from `dom`) instead of fetching the page; URL is the base for CSS |
| `--max-css` | 40 | Stylesheet cap |
| `--no-external-css` | off | Skip stylesheets on other hosts (Google Fonts CSS etc.) |
| `--keep-text` | off | Keep truncated text in exemplars |
| `--top` | 12 | Components / colors reported |
| `--timeout` | 30 | curl `--max-time` |
| `--max-bytes N` | 20 MB | Skip any single resource larger than this |
| `--header 'N: v'` | none | Extra curl header (repeatable); only for sites you may access |
| `--signatures FILE` | none | Extra/override technology signatures (same JSON format as `scripts/data/tech_signatures.json`) |
| `--user-agent`, `--insecure` | browser-like UA | UA override (env `CAPTURE_USER_AGENT` changes the default for `design` and `dom`); curl `-k` for self-signed local HTTPS |

## JS-rendered pages
curl returns what the server sends. For SPAs/hydrated pages the HTML may be a thin shell:
```
python scripts/capture.py dom https://spa.example.com -o .capture/dom/spa.html
python scripts/capture.py design patterns https://spa.example.com --html-file .capture/dom/spa.html
```
CSS is still fetched with curl; the HTML analysed is the rendered DOM. Styles injected at runtime by JS (CSS-in-JS, runtime Tailwind) won't be in `css.dump`; check `sources.json`/the "No CSS found" warning, and use `website` to capture the page's files if needed.

## Using the output to clone
1. Read `design-system.md` first: recreate variables (keep the same names), fonts, type styles, spacing and breakpoints.
2. Read `design-patterns.md`: build the skeleton, wrappers, then components using the exemplar HTML and CSS rules.
3. When a detail is missing, search the dumps (`grep` the class or selector in `css.dump`, the element in `html.dump`) for the exact rule/markup.
4. Rebuild with your own text, images and licensed fonts; behaviour (animation/interaction) lives in JS and is not captured here.

## Limits
- Server-delivered HTML/CSS only (see JS-rendered pages); no JS execution, no screenshots.
- Pseudo-state styles are listed as rules, not rendered.
- Fonts, images and scripts are referenced, not downloaded (use `website` for files).
- Component detection is structural: very small sites may have none; very large pages report the top `--top`.
- The CSS parser is lenient, not a validator; exotic syntax may be skipped. Escaped selectors (Tailwind-style `.md\:flex`, `.w-\[10px\]`) are parsed and matched to the HTML class names (`md:flex`).
- Dumps are always UTF-8. Pages in other encodings (e.g. Windows-1256, Shift_JIS) are decoded by the HTTP charset, BOM, or `<meta charset>` / `@charset`, and the original encoding is recorded on the first line of `html.dump`. A `<meta charset>` inside the dump may still name the old encoding, so open the dump as UTF-8.
- Inputs are checked first: a non-HTML response (JSON, PDF, image) or a file without tags is rejected with advice, and any single resource larger than `--max-bytes` is skipped (curl enforces this when the server states the size).
- Corrupt or hostile CSS/HTML cannot crash or hang the analysis: variable resolution is cycle-safe and size-capped, nesting depth is capped like a browser, and `scripts/test_robust.py` fuzzes the parsers.
- Technology attribution is evidence-based and incomplete by nature: unknown or purely server-side technology is reported as raw evidence at best.
- Only analyse sites you may analyse; respect terms and copyright.
