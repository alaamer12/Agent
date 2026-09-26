---
name: fahlwy
description: Over-smart asset-source hunter. Find and PROVE a required number of working free asset sources (images, avatars, video, audio, icons, fonts) by actually fetching bytes and validating magic signatures - never stop at a guessed URL. Use whenever asked to "find N sources", build an asset/placeholder source list, wire mockup media, or hunt down reliable hotlink/direct-download endpoints, then keep going until every slot is verified.
when_to_use: The user wants a countable list of working external asset URLs (images/avatars/video/audio), or asks to "find a way" to source media for a mockup/demo, or wants a catalog of verified placeholder/stock endpoints.
---

# fahlwy — over-smart source hunter

## Overview

The ethos: **there is always a way.** When told to "find N sources," do not
settle for the first N plausible URLs or N guesses. Emit a script, hit the
network, and only count a source once it returns **real bytes of the right
type**. Iterate — more candidates, fixed paths, alternate hosts — until you hit
N genuinely-verified sources, or report the honest maximum with reasons.

`references/verified-urls.md` already contains 80+ verified endpoints across
images/avatars/video/audio/icons/illustrations/PDF-books/**brand-logos** (brand
logos added 2026-09-21) plus a "do-not-use" list. Prefer
reusing that catalog over re-hunting; re-verify any entry on a new day (free
hosts churn). When you discover new working/dead sources, append them to that
file — the skill compounds.

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

Use `scripts/verify_sources.py <image|video|audio|any> URL [URL...]` — it does
exactly this, retries transient 5xx with backoff, prints one clean line per URL,
and exits non-zero unless all pass.

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
     mark ⚠️ and keep it out of the guaranteed count.
   - `SSL CERTIFICATE_VERIFY` → server sends an incomplete chain; unusable with
     verification ON. Record in the do-not-use list (never "fix" by disabling
     TLS verification in anything you ship).
   - magic-byte miss with `text/html` → the host fakes success (e.g.
     sample-videos.com returns an HTML page). Reject it.
4. **Hunt for new sources the right way.** WebSearch for "free random image
   API", "placeholder image service", "sample mp4 direct link",
   "direct mp3 for testing", "random avatar generator", etc. Then extract the
   **direct-file endpoint** from the result page (docs usually show one example
   URL) and feed that through the verifier. Reuse known-good *families*
   (see below) to spawn more distinct hosts.
5. **Dedup by provider before counting.** `SoundHelix-Song-1` … `-10` is ONE
   provider. `api.dicebear.com/9.x/<styleA>` and `<styleB>` is ONE provider.
   Two domains of one service (`mdn.github.io` vs
   `interactive-examples.mdn.mozilla.net`) can count separately but say so.
   When a category can't reach N distinct *providers*, report the honest split
   (e.g. "10 providers + 5 labeled style endpoints = 15 assets"). Never pad a
   count with unverified or duplicate URLs.
6. **Ship a script + a markdown catalog**, run the verify once more, then clean
   up any `scratch/` you created.

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

Three harvest routes, in yield order — all license-gated:

```bash
# 1. GitHub: verify license, then list every PDF in the tree + release assets
echo "progit/progit2" | python3 scripts/gh_tree_pdfs.py | \
  python3 scripts/verify_sources.py pdf

# 2. Internet Archive: metadata-gated (skips access-restricted / no-license items)
python3 scripts/ia_open_pdfs.py 'mediatype:texts AND description:"creative commons"' 20 | \
  python3 scripts/verify_sources.py pdf

# 3. Landing pages: never guess a filename — harvest the page's own hrefs
python3 scripts/harvest_pdfs.py < pages.txt | python3 scripts/verify_sources.py pdf
```

`verify_sources.py pdf` checks `%PDF-` magic **and** a real `%%EOF` trailer,
because release assets serve `application/octet-stream` (Content-Type lies) and
"free book" hosts happily return `200` + HTML. Then run
`scripts/pdf_identity.py <dir>` to prove what is on disk: it inflates the object
streams and prints page `/Count`, `/Title`, and a first-page text fingerprint —
which is how you catch the 1.1 MB "book" that is really a sample chapter.

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
   re-uploads of a mark claiming MIT/CC0. Flag these in the catalog; never present
   a scraped copy of a paid library (IconScout/LogoDB/Brandfetch) as free.
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
clears `--min`. Run it before publishing any count in this category.

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
  filesamples.com, actions.google.com/sounds, media.w3.org.
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

## Growing the catalog (compounding knowledge)

`references/verified-urls.md` is **living**: it carries an ISO `YYYY-MM-DD`
"last proven" date per category and an append-only **Growth log**. Every time
you run a hunt you must feed results back so the skill never re-learns from
zero:
- **Proven a new source** → add it under its category, stamp `✅ <today>`, and
  write a Growth-log line `today | ADD | cat | provider — url/note`.
- **Re-confirmed existing** → bump its date (and the header "Last full
  re-verification").
- **Now failing** → `✅`→`⚠️` (rate-limit) or →`❌` (dead/blocked/HTML-fake) and
  log a DOWNGRADE line. Do **not** delete — the ❌ graveyard prevents re-hunting
  known-bad hosts.
- Free hosts churn on the order of **weeks**; treat any entry older than ~30
  days as a hint to re-verify, not a fact to ship blind.

The goal is the same as the hunt: each use leaves the catalog bigger, fresher,
and better documented than it found it.

## Commands

```bash
# Verify arbitrary candidates (proves real bytes of the right type):
python3 scripts/verify_sources.py video URL1 URL2 URL3

# Re-check the whole shipped catalog quickly, then wire into a mockup:
grep -oE 'https://[^ )`]+' references/verified-urls.md | sort -u \
  | xargs python3 scripts/verify_sources.py any

# Prove brand-logo sources (resolves each provider's slug index, pins versions,
# exact-names-only, stub-hash detection):
python3 scripts/brand_logos_matrix.py                      # all 21 x 12 brands
python3 scripts/brand_logos_matrix.py -p thesvg-color,simple-icons --min 10
python3 scripts/brand_logos_matrix.py -b cursor,codeium,ollama,windsurf --json ai.json
```

## Resources

- `references/verified-urls.md` — the living catalog: 80+ verified sources by
  category, each with its exact direct-URL form, ⚠️/❌ markers, and the
  do-not-use graveyard (dead/blocked/HTML-faking hosts).
- `scripts/verify_sources.py` — magic-byte verifier with 5xx backoff-retry;
  exits 0 only when every URL serves real bytes. Run it before you trust or
  cite any endpoint.
- `scripts/brand_logos_matrix.py` — brand-logo source prover: 21 providers x a
  named brand matrix, with per-provider slug-index resolution (npm/gh/iconify/
  Commons), version pinning, exact-vs-derived name matching, SVG path/fill and
  PNG dimension reporting, stub-hash detection and rate-limit delays. Use
  `--list-providers` to see the registry; add a provider by appending one dict
  entry to `PROVIDERS`.
