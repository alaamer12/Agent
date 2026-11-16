# Brand logos (and any fixed-name catalog) — resolve, never guess

A "find N sources of brand logos" task is not a URL-hunting task, it is a
**filename-resolution** task. Every provider here 404s politely, so guessing a
slug produces a fake ceiling: WorldVectorLogo scores 7/12 on bare slugs and
11/12 once you use its real `microsoft-1` / `figma-2` / `netflix-1` forms. The
method that worked, in order:

1. **Fix a brand matrix and hold it constant** across every candidate (12 brands
   worked well: github, youtube, google, microsoft, figma, slack, docker,
   spotify, netflix, vercel, **windsurf**, openai). "10 verified logos" is
   meaningless without naming which ten — and the young-brand columns are what
   actually separate the sources (only 4 of 15 had Windsurf; legacy icon fonts
   fail *every* AI-era tool).
2. **Pull each provider's own file index**, then derive slugs from it:
   ```bash
   # npm packages (resolve tags.latest from the UNVERSIONED url — the versionless
   # form returns metadata, not files; then ask for the flat tree):
   curl -s "https://data.jsdelivr.com/v1/packages/npm/simple-icons" | jq -r .tags.latest
   curl -s "https://data.jsdelivr.com/v1/packages/npm/simple-icons@16.32.0?structure=flat" | jq -r '.files[].name'
   # GitHub repos without the rate-limited API (also: LobeHub needs the NESTED
   # tree — ?structure=flat returns 0 files for that package):
   curl -s "https://data.jsdelivr.com/v1/packages/gh/gilbarbara/logos@main?structure=flat"
   # Iconify sets (200k+ icons; the per-icon names live here, not on the API):
   curl -s "https://cdn.jsdelivr.net/gh/iconify/icon-sets/json/simple-icons.json" | jq -r '.icons|keys[]'
   # Wikimedia Commons (2-call recipe; `aimime` is disabled and answers 200+{"error"}):
   curl -s "https://commons.wikimedia.org/w/api.php?action=query&format=json&list=allimages&aiprefix=GitHub%20logo&ailimit=30"
   ```
3. **Rights gate, like documents.** Logos are **trademarks** — availability proves
   nothing about permission. CC0 on Simple Icons covers the *file*, not the mark;
   Font Awesome Brands is **CC BY (attribution required)**; a Commons file tagged
   `{{PD-textlogo}}` still carries `{{Trademarked}}`, and some are third-party
   re-uploads of a mark claiming MIT/CC0. Set the row's `rights` accordingly
   (`trademarked` for the whole category, plus `cc-by` where attribution is owed);
   never present a scraped copy of a paid library (IconScout/LogoDB/Brandfetch) as
   free.
4. **Grade what the bytes actually are**, not what the site claims: count
   `<path>` and distinct `fill=` values. Multi-path/multi-fill ≈ official
   artwork; one `24×24` path with no fill = a community mono redraw (still
   useful, and the only tier that reliably has young brands). Then state
   colour support, and whether a PNG tier exists at all — most icon packages
   ship zero raster brand files.
5. **Three failure modes a status code cannot see**, all three hit here:
   - *Neighbouring slug*: `thesvg-color/github` 404s but `github-actions` exists —
     a prefix matcher "passes" on the **wrong mark**. Match the exact name, and
     beware theme suffixes (`<brand>-dark` / `-light`) and set-prefix stripping
     (`cib/github`, never `cib/cib-github`).
   - *Host ≠ provider*: `raw.githubusercontent.com` and `cdn.jsdelivr.net/gh/…`
     serve the same repo; proving one does not license the other.
   - *Release ≠ release*: **jsDelivr's versionless path serves a stale cached
     release** and will 200 a file the current one deleted. Measured:
     `npm/simple-icons/icons/openai.svg` → 200 / 1570 B, but
     `npm/simple-icons@16.32.0/icons/openai.svg` → **404** (openai and slack were
     removed at v16.0.0, microsoft at v13.0.0). A hand-probed versionless URL
     produced a false "12/12 brands" for a source that really serves 9. **Pin the
     resolved `tags.latest` into the URL before counting coverage.**
   Also: a "200" logo API that returns the **same 70 B 1×1 PNG** or the same
   434 KB HTML body for all 12 domains is a stub, not a catalog — hash-compare
   across brands before counting anything.

`scripts/brand_logos_matrix.py` encodes all of the above: it resolves each
provider's own slug index (npm/gh via jsDelivr's data API, Iconify via
`icon-sets`, Commons via `list=allimages`), **pins `tags.latest`**, tries exact
names only unless `--allow-derived`, sniffs magic past a UTF-8 BOM, counts SVG
`<path>`/`fill=` and PNG IHDR dimensions, flags cross-brand identical hashes as
stubs, respects per-provider rate delays, and exits non-zero unless every source
clears `--min`. Run it before publishing any count in this category, then write
the result into the rows: `coverage` = the honest score (`11/12`,
`7/12 consumer, 14/14 dev/AI`), `access` = `index-required` when the URL can only
be built from the provider's own slug manifest, and `notes` = the tier facts a
later reader cannot re-derive (colour vs mono, PNG tier present, frozen release).
Query them back with `python scripts/catalog.py list --category brand-logo
--cols id,coverage,access,rights,notes`.
