---
name: fahlwy
description: 'Over-smart asset-source hunter. Find and PROVE a required number of working free asset sources (images, avatars, video, audio, icons, fonts, PDF books, brand logos) by fetching real bytes and validating magic signatures - never stopping at a guessed URL. Keeps its catalog as queryable CSV (data.csv: category, provider, family, url_form, kind, status, last_proven, access, rights, coverage, notes) plus an append-only growth ledger (log.csv), read and written through scripts/catalog.py. Use whenever asked to "find N sources", build an asset/placeholder source list, wire mockup media, or hunt down reliable hotlink/direct-download endpoints, then keep going until every slot is verified.'
when_to_use: The user wants a countable list of working external asset URLs (images/avatars/video/audio/icons/fonts/PDF books/brand logos), asks to "find a way" to source media for a mockup/demo, wants verified placeholder/stock endpoints, or asks what the catalog already knows (`catalog.py list/search/stale`).
---

# fahlwy — over-smart source hunter

## Overview

The ethos: **there is always a way.** When told to "find N sources," do not
settle for the first N plausible URLs or N guesses. Emit a script, hit the
network, and only count a source once it returns **real bytes of the right
type**. Iterate — more candidates, fixed paths, alternate hosts — until you hit
N genuinely-verified sources, or report the honest maximum with reasons.

`data.csv` **is** the catalog: 209 rows across images/avatars/video/audio/icons/
illustrations/PDF-books/**brand-logos**, in 148 provider families — 145 `verified`,
9 `degraded`, 13 `site-only` (library sites with no proven hotlink), and 42
`dead`/`refuse` rows, 37 of them filed under `graveyard-*`. It is data, not prose,
so it can be filtered instead of skimmed — `python scripts/catalog.py
list --category icon --status verified`, `... urls --category audio | xargs ...`,
`... stale --days 30`. Every row carries: `category, provider, family` (the dedup
group), `host, url_form, kind` (what `verify_sources.py` expects), `status`
(`verified · degraded · site-only · dead · refuse`), `last_proven` / `first_seen`
(ISO dates), `access` (`keyless · rate-limited · browser-ua · index-required ·
expiring-path · manual-download · blocked · rights-blocked`), `rights`, `coverage`
and `notes` — **the notes column is where the traps live** (the `sz=` ladder that
regresses to 16×16, the theme-suffixed `thesvg-color` names, PNG-only Doodle
Ipsum, the per-chapter-only OSTEP release). `log.csv` is the append-only ledger
(`date, action, category, subject, detail`) of every ADD / UPGRADE / DOWNGRADE /
CONFIRM / CORRECTION / NOTE.

Prefer reusing rows over re-hunting; re-verify anything before shipping it on a
new day (free hosts churn in weeks). Feed every hunt back through
`scripts/catalog.py` — that is what makes the skill compound.

## The rule that matters

**A passing source is proven by content, not by status code.** Many "asset"
sites answer `200 OK` with an HTML error/consent/landing page, or an image host
serves a 200 with a tiny stub. Always validate:
- images: `Content-Type: image/*` **and** > ~256 bytes (or PNG/JPEG/GIF/WEBP/SVG magic)
  ⚠️ That byte floor **false-fails valid icon-scale SVGs** — a 132–255 B mono
  brand glyph is a real asset. Use the `any` kind for icons/logos (it accepts on
  magic or Content-Type with no floor), and remember a legit SVG can start with a
  **UTF-8 BOM + CRLF**, so sniff past the BOM instead of testing offset 0.
- video: `Content-Type: video/*` **or** magic `ftyp` at offset 4 / EBML `1A 45 DF A3`
- audio: `Content-Type: audio/*` / `application/ogg` **or** magic `ID3`/`OggS`/`RIFF…WAVE`/`fLaC`/MPEG frame-sync `FF Ex`

Use `python scripts/verify_sources.py <image|video|audio|pdf|doc|any> URL [URL...]`
— it does exactly this, retries transient 5xx with backoff, prints one clean line
per URL, and exits non-zero unless all pass. Two environment facts: on Windows run
it with `python`, because `python3` is usually a Microsoft Store stub that fails
every documented invocation; and it has **no** `font` kind, so a genuine `woff2`
(`Content-Type: font/woff2`) false-fails under `any` — fonts need `wOF2`/`wOFF`
magic plus structure checks that this script does not make.

Each catalog row's `kind` column is exactly the argument this script wants, which
is what makes `catalog.py urls … | verify_sources.py <kind>` a coherent pipeline.
Rows whose `url_form` contains `<placeholders>` (Pexels ids, Pixabay signed paths,
DiceBear styles) **cannot** be bulk-verified — they 403/404 for a reason that says
nothing about the provider. Re-resolve a real id first, and never `stamp` such a
row off a bulk run.

## Workflow to reach "N verified sources"

1. **Seed candidates broadly, from knowledge first.** Write a candidate list
   with *real* direct-file URLs, not homepages. Homepages (`pexels.com`) are
   `text/html` and will (correctly) fail — you need the CDN path form:
   `https://images.pexels.com/photos/<id>/pexels-photo-<id>.jpeg`,
   `https://upload.wikimedia.org/wikipedia/commons/<hash>/<File>.jpg`,
   `https://archive.org/download/<item>/<file>.mp4`, etc.
2. **Probe in parallel** with the script (or a ThreadPool variant). Expect a big
   first batch to fail — that's normal; free endpoints rot. Do not conclude the
   target is impossible after one batch.
3. **For every failure, diagnose and fix the URL, don't just discard:**
   - `404` → wrong file path / id. Reconstruct the real path (Pexels needs
     `pexels-photo-<id>.jpeg` repeated slug; Wikimedia thumbnails only accept
     whitelisted widths → use full-res, or `Special:FilePath/<Name>?width=`).
   - `403` → hotlink/geo/anti-bot. Some need no/alternate User-Agent, some are
     just blocked from this region (drop them, don't claim them).
   - `500/503` → upstream flake. Retry; if persistent it's in a real outage —
     set `status=degraded` and keep it out of the guaranteed count.
   - `SSL CERTIFICATE_VERIFY` → server sends an incomplete chain; unusable with
     verification ON. Record it as a `graveyard-*` row with `status=dead` (never
     "fix" by disabling TLS verification in anything you ship).
   - magic-byte miss with `text/html` → the host fakes success (e.g.
     sample-videos.com returns an HTML page). Reject it.
4. **Hunt for new sources the right way.** WebSearch for "free random image
   API", "placeholder image service", "sample mp4 direct link",
   "direct mp3 for testing", "random avatar generator", etc. Then extract the
   **direct-file endpoint** from the result page (docs usually show one example
   URL) and feed that through the verifier. Reuse known-good *families*
   (see below) to spawn more distinct hosts.
5. **Dedup by the `family` column before counting.** `SoundHelix-Song-1` … `-10`
   is ONE family. `api.dicebear.com/9.x/<styleA>` and `<styleB>` is ONE family.
   Two domains of one service (`mdn.github.io` vs
   `interactive-examples.mdn.mozilla.net`) can count separately but say so.
   When a category can't reach N distinct *providers*, report the honest split
   (e.g. "10 providers + 5 labeled style endpoints = 15 assets"). Never pad a
   count with unverified or duplicate URLs.
6. **Ship a script + the catalog rows** (`catalog.py add` for each proven source,
   `catalog.py log ADD …` for the reasoning), run the verify once more against the
   rows you just wrote, then clean up any scratch you created.

## Documents (PDF books) — the rights gate comes first

For documents, "can I fetch the bytes" is the *easy* half. A PDF is only a
passing source if the **rights holder released it**. So run the gate before the
verifier, not after:

- Accept: CC / GFDL / public-domain / BSD-licensed full texts, and official
  author-or-publisher-hosted free downloads (MIT Press, Stanford, UPenn,
  `greenteapress.com`, `opendatastructures.org`, releases in the author's own
  repo).
- Refuse: lending-library or `/Encrypt`-ed items, DRM-stripped files, and any
  copy of a commercially-sold title. There is no legal free full-text PDF of
  Clean Code, Code Complete, Refactoring, The Pragmatic Programmer, CLRS, or K&R
  — so "found it on a GitHub repo / Archive item" is a red flag, not a win.
- A CC `LICENSE` file in a repo does **not** prove the repo holds the rights to
  what it contains (translations and link-dumps of paid books look CC-licensed).
  Check the copyright page inside the PDF itself.
- A refusal is catalog material too: write it as `status=refuse` so the next hunt
  does not rediscover the same tempting-looking upload.

Three harvest routes, in yield order — all license-gated:

```bash
# 1. GitHub: verify license, then list every PDF in the tree + release assets
echo "progit/progit2" | python scripts/gh_tree_pdfs.py | \
  python scripts/verify_sources.py pdf

# 2. Internet Archive: metadata-gated (skips access-restricted / no-license items)
python scripts/ia_open_pdfs.py 'mediatype:texts AND description:"creative commons"' 20 | \
  python scripts/verify_sources.py pdf

# 3. Landing pages: never guess a filename — harvest the page's own hrefs
python scripts/harvest_pdfs.py < pages.txt | python scripts/verify_sources.py pdf
```

`verify_sources.py pdf` checks `%PDF-` magic **and** a real `%%EOF` trailer,
because release assets serve `application/octet-stream` (Content-Type lies) and
"free book" hosts happily return `200` + HTML. Then run
`scripts/pdf_identity.py <dir>` to prove what is on disk: it inflates the object
streams and prints page `/Count`, `/Title`, and a first-page text fingerprint —
which is how you catch the 1.1 MB "book" that is really a sample chapter.

Write each proven book as `catalog.py add --category document --kind pdf
--rights <cc-by|gfdl|…> --coverage '<MB>, <N> pp' --notes '<the licence and where
it is hosted>'`; `coverage` holds the size and the poppler page count, because
"it fetched" is not what makes it a book.

## Brand logos (and any fixed-name catalog) — resolve, never guess

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

## High-yield source families (spawn many from a few)

- **Placeholder generators**: placehold.co, placehold.jp, dummyimage — accept
  `/WxH/fg/bg`, return png/svg. Reliable, controllable.
- **Random-photo CDNs**: picsum (`/seed/x`, `?grayscale`), gstatic webp gallery
  (`/1..4`), random.imagecdn.app.
- **Big content CDNs with predictable paths** (need a real id): images.pexels,
  cdn.pixabay, images.unsplash, upload.wikimedia (+ `Special:FilePath` by name).
- **Animals**: cataas, placebear, placedog.net, place.dog, cdn2.thecatapi.
- **Screenshots of arbitrary URLs**: thum.io, s0.wp.com/mshots.
- **GitHub image CDN trio** (all distinct hosts, stable): raw.githubusercontent,
  cdn.jsdelivr.net/gh/…, opengraph.githubassets.com/1/<owner>/<repo>.
- **Public-domain**: NASA `images-assets.nasa.gov` (`~small.jpg`), Internet
  Archive (`/download/<item>/<file>`), Wikimedia.
- **Media test files** (video/audio): test-videos.co.uk, w3schools,
  mdn.github.io/shared-assets, vjs.zencdn.net, download.blender.org,
  filesamples.com, actions.google.com/sounds (`media.w3.org` went 403 at the
  2026-10-26 re-check — it is a graveyard row now).
- **Avatars (distinct providers)**: api.dicebear, robohash, ui-avatars,
  i.pravatar.cc, gravatar, randomuser.me/api/portraits,
  avatars.githubusercontent.com, seccdn.libravatar.org, avataaars.io,
  cdn.discordapp.com/embed/avatars.
- **Brand logos (distinct providers)**: simple-icons, gilbarbara/logos,
  vectorlogo.zone, cdn.worldvectorlogo.com, yceballost/logotypes (repo only),
  @lobehub/icons-static-{svg,png}, Iconify sets (`thesvg-color`, `cib`, `bxl`,
  `logos`, `arcticons`, `streamline-logos`), icon-font npm paths
  (`remixicon/icons/Logos/`, `@tabler/icons/icons/outline/brand-*`,
  `@fortawesome/.../svgs/brands/`, `boxicons/svg/logos/bxl-*`), Commons, and the
  keyless domain APIs (google s2 `sz=256`, icon.horse, icons.duckduckgo.com/ip3,
  unavatar `?fallback=false`). See the Brand-logos section above for how to
  resolve their names; Clearbit/logo.dev/Brandfetch are all dead or token-gated.

## Practical gotchas learned

- Some sites block a browser-style User-Agent (GitHub gtv bucket 403s here but
  works in a real browser); others 403 with *no* UA. Try both before deciding.
- Wikimedia `/thumb/…/<W>px-…` only allows a fixed width set → 400 otherwise.
  Use the original full-size file or `Special:FilePath`.
- `filesamples.com` and `file-examples.com` are **different** sites; only the
  first serves direct files.
- Under heavy parallel load even good hosts (media.w3.org) rate-limit; confirm
  an individual failure with a single request before removing it.
- Keep TLS verification ON in anything shipped. A throwaway probe MAY relax it,
  but never ship a verifier that disables cert checks.

## Maintaining the catalog (compounding knowledge)

`data.csv` is **living** and `log.csv` is **append-only**. Every hunt must feed
results back through `scripts/catalog.py`, or the next agent re-learns from zero:

| What happened | Write |
|---|---|
| Proven a new source | `catalog.py add --id <slug> --category <cat> --provider <name> --url-form <direct-file-url> --kind <k> --notes '<trap/why>'` (auto-logs `ADD`) |
| Re-confirmed an existing row | `catalog.py stamp <id> [<id>…]` → bumps `last_proven` (auto-logs `CONFIRM`) |
| Flaky now, works sometimes | `catalog.py set <id> --status degraded --note "…"` |
| Dead / blocked / serves HTML | `catalog.py set <id> --status dead --action DOWNGRADE --note "…"` — or `add` it under `graveyard-<cat>` if it was never in the catalog |
| Not ours to ship (rights) | `--status refuse` with the rights reason in `notes` |
| A method lesson, not a URL | `catalog.py log NOTE <cat> <subject> "<why>"` |

Three rules that make the CSV worth more than prose ever was:

- **Never delete a failing row** — flip `status` to `dead`/`refuse`. The graveyard
  is what stops a re-hunt of Clearbit, Boring Avatars and paulgraham.com.
- **The ledger must explain, not just date-stamp.** `stamp` answers "was it alive";
  only `notes`/`log.csv` carry "why the naive URL is wrong", and that is the part
  that compounds. One line per hunt at minimum.
- **Dates are evidence, not decoration.** `catalog.py stale --days 30` lists what
  has outlived the ~week-to-month lifespan of a free host; `stats` prints the
  median age. Ship a row you have not re-proven on this day only if you say so.

The goal is the same as the hunt: each use leaves the catalog bigger, fresher and
better documented than it found it.

## Commands

```bash
# Prove candidates (real bytes of the declared kind, never just a 200):
python scripts/verify_sources.py video URL1 URL2 URL3

# Ask the catalog anything instead of skimming it:
python scripts/catalog.py stats
python scripts/catalog.py list --category brand-logo --cols id,provider,status,coverage
python scripts/catalog.py search "429"
python scripts/catalog.py get simple-icons

# Bulk re-verify a slice (concrete url_form rows only — see the placeholder note):
python scripts/catalog.py urls --category audio --status verified   | xargs python scripts/verify_sources.py audio
python scripts/catalog.py urls --kind pdf --status verified   | xargs python scripts/verify_sources.py pdf
python scripts/catalog.py stale --days 30            # what to re-prove first
python scripts/catalog.py stamp test-videos w3schools-video   # after they pass

# Render the catalog as readable markdown when a human (or a report) wants prose:
python scripts/catalog.py export --format md --category icon

# Prove brand-logo sources (resolves each provider's slug index, pins versions,
# exact-names-only, stub-hash detection):
python scripts/brand_logos_matrix.py                      # all 21 x 12 brands
python scripts/brand_logos_matrix.py -p thesvg-color,simple-icons --min 10
python scripts/brand_logos_matrix.py -b cursor,codeium,ollama,windsurf --json ai.json
```

## Resources

- `data.csv` — the catalog: 209 rows, one per source, with `category, provider,
  family, host, url_form, kind, status, last_proven, first_seen, access, rights,
  coverage, notes`. Read and write it through `catalog.py`, never by hand-editing
  quoted text — one stray comma shifts every later column in the row, and
  `csv.writer` is what keeps quoting correct.
- `log.csv` — the append-only growth ledger: `date, action, category, subject,
  detail`, newest first. Includes the corrections ("I published a wrong
  correction; pin the release before counting") that make the catalog trustworthy.
- `scripts/catalog.py` — the catalog's only interface: `stats`, `list`, `urls`, `get`,
  `search`, `stale`, `stamp`, `set`, `add`, `log`, `export --format md|json`. Writes
  are atomic, and every status-changing write appends a matching `log.csv` line, so
  the ledger cannot drift from the data. Filters (`--category/--status/--kind/
  --family/--host/--access/--rights/--older-than/--newer-than`) take comma-lists.
- `scripts/verify_sources.py` — magic-byte verifier with 5xx backoff-retry;
  exits 0 only when every URL serves real bytes. Run it before you trust or cite
  any endpoint.
- `scripts/brand_logos_matrix.py` — brand-logo source prover: 21 providers x a
  named brand matrix, with per-provider slug-index resolution (npm/gh/iconify/
  Commons), version pinning, exact-vs-derived name matching, SVG path/fill and
  PNG dimension reporting, stub-hash detection and rate-limit delays. Use
  `--list-providers` to see the registry; add a provider by appending one dict
  entry to `PROVIDERS`.
- `scripts/gh_tree_pdfs.py`, `scripts/ia_open_pdfs.py`, `scripts/harvest_pdfs.py`,
  `scripts/pdf_identity.py` — the document harvesters (GitHub tree + releases,
  licence-gated Internet Archive search, landing-page `href` mining) and the
  on-disk PDF prover (pages, encryption, first-page text).
