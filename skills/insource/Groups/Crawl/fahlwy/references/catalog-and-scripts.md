# The catalog and its scripts — schema, interfaces, compounding rules

## What `data.csv` is

`data.csv` **is** the catalog: 209 rows across images/avatars/video/audio/icons/
illustrations/PDF-books/**brand-logos**, in 148 provider families — 145
`verified`, 9 `degraded`, 13 `site-only` (library sites with no proven
hotlink), and 42 `dead`/`refuse` rows, 37 of them filed under `graveyard-*`. It
is data, not prose, so it can be filtered instead of skimmed — `python
scripts/catalog.py list --category icon --status verified`, `... urls --category
audio | xargs ...`, `... stale --days 30`.

Every row carries: `category, provider, family` (the dedup group), `host`,
`url_form`, `kind` (what `verify_sources.py` expects), `status` (`verified ·
degraded · site-only · dead · refuse`), `last_proven` / `first_seen` (ISO
dates), `access` (`keyless · rate-limited · browser-ua · index-required ·
expiring-path · manual-download · blocked · rights-blocked`), `rights`,
`coverage` and `notes` — **the notes column is where the traps live** (the `sz=`
ladder that regresses to 16×16, the theme-suffixed `thesvg-color` names,
PNG-only Doodle Ipsum, the per-chapter-only OSTEP release).

`log.csv` is the append-only ledger (`date, action, category, subject, detail`)
of every ADD / UPGRADE / DOWNGRADE / CONFIRM / CORRECTION / NOTE.

## Files and scripts

- `data.csv` — the catalog, one row per source. Read and write it through
  `catalog.py`, never by hand-editing quoted text — one stray comma shifts every
  later column in the row, and `csv.writer` is what keeps quoting correct.
- `log.csv` — the growth ledger, newest first. Includes the corrections ("I
  published a wrong correction; pin the release before counting") that make the
  catalog trustworthy.
- `scripts/catalog.py` — the catalog's only interface: `stats`, `list`, `urls`,
  `get`, `search`, `stale`, `stamp`, `set`, `add`, `log`, `export --format
  md|json`. Writes are atomic, and every status-changing write appends a
  matching `log.csv` line, so the ledger cannot drift from the data. Filters
  (`--category/--status/--kind/--family/--host/--access/--rights/--older-than/
  --newer-than`) take comma-lists.
- `scripts/verify_sources.py` — magic-byte verifier with 5xx backoff-retry;
  exits 0 only when every URL serves real bytes. Run it before you trust or cite
  any endpoint. Its `kind` argument is exactly each row's `kind` column, which
  is what makes `catalog.py urls … | verify_sources.py <kind>` a coherent
  pipeline.
- `scripts/brand_logos_matrix.py` — brand-logo source prover: 21 providers × a
  named brand matrix, with per-provider slug-index resolution
  (npm/gh/iconify/Commons), version pinning, exact-vs-derived name matching,
  SVG path/fill and PNG dimension reporting, stub-hash detection and rate-limit
  delays. `--list-providers` shows the registry; add a provider by appending one
  dict entry to `PROVIDERS`.
- `scripts/gh_tree_pdfs.py`, `scripts/ia_open_pdfs.py`,
  `scripts/harvest_pdfs.py`, `scripts/pdf_identity.py` — the document
  harvesters (GitHub tree + releases, licence-gated Internet Archive search,
  landing-page `href` mining) and the on-disk PDF prover (pages, encryption,
  first-page text).

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
- **The ledger must explain, not just date-stamp.** `stamp` answers "was it
  alive"; only `notes`/`log.csv` carry "why the naive URL is wrong", and that is
  the part that compounds. One line per hunt at minimum.
- **Dates are evidence, not decoration.** `catalog.py stale --days 30` lists
  what has outlived the ~week-to-month lifespan of a free host; `stats` prints
  the median age. Ship a row you have not re-proven on this day only if you say
  so.

Prefer reusing rows over re-hunting; re-verify anything before shipping it on a
new day (free hosts churn in weeks). The goal is the same as the hunt: each use
leaves the catalog bigger, fresher and better documented than it found it.

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
