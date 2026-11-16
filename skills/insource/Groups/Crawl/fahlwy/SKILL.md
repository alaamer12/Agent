---
name: fahlwy
version: 1.1.1
author: Amr
specialized: none
description: 'Over-smart asset-source hunter. Find and PROVE a required number of working free asset sources (images, avatars, video, audio, icons, fonts, PDF books, brand logos) by fetching real bytes and validating magic signatures - never stopping at a guessed URL. Keeps its catalog as queryable CSV (data.csv: category, provider, family, url_form, kind, status, last_proven, access, rights, coverage, notes) plus an append-only growth ledger (log.csv), read and written through scripts/catalog.py. Use whenever asked to "find N sources", build an asset/placeholder source list, wire mockup media, or hunt down reliable hotlink/direct-download endpoints, then keep going until every slot is verified.'
when_to_use: The user wants a countable list of working external asset URLs (images/avatars/video/audio/icons/fonts/PDF books/brand logos), asks to "find a way" to source media for a mockup/demo, wants verified placeholder/stock endpoints, or asks what the catalog already knows (`catalog.py list/search/stale`).
argument-hint: "[<N asset kinds to source> | catalog <list|search|stats|get|stale>]"
---

# fahlwy — over-smart source hunter

## Overview

The ethos: **there is always a way.** When told to "find N sources," do not
settle for the first N plausible URLs or N guesses. Emit a script, hit the
network, and only count a source once it returns **real bytes of the right
type**. Iterate — more candidates, fixed paths, alternate hosts — until you hit
N genuinely-verified sources, or report the honest maximum with reasons.

The catalog (`data.csv`) is data, not prose — query it through
`scripts/catalog.py`, never skim or hand-edit it. Schema, the ledger, all
maintenance rules and the full command set:
[`references/catalog-and-scripts.md`](references/catalog-and-scripts.md).

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

Each catalog row's `kind` column is exactly the argument this script wants.
Rows whose `url_form` contains `<placeholders>` (Pexels ids, Pixabay signed
paths, DiceBear styles) **cannot** be bulk-verified — they 403/404 for a reason
that says nothing about the provider. Re-resolve a real id first, and never
`stamp` such a row off a bulk run.

## Workflow to reach "N verified sources"

1. **Seed candidates broadly, from knowledge first.** Real direct-file URLs,
   not homepages (`pexels.com` is `text/html` and will correctly fail — you
   want `https://images.pexels.com/photos/<id>/pexels-photo-<id>.jpeg`-style
   CDN forms). Known-good families to spawn candidates:
   [`references/source-families.md`](references/source-families.md).
2. **Probe in parallel** with the verifier (or a ThreadPool variant). Expect a
   big first batch to fail — that's normal; free endpoints rot. Do not conclude
   the target is impossible after one batch.
3. **For every failure, diagnose and fix the URL, don't just discard:**
   `404` → wrong path/id (reconstruct the real form); `403` → hotlink/geo/UA
   (try both UA styles, or drop without claiming); `500/503` → retry, then
   `status=degraded`; TLS-incomplete-chain → graveyard row, `status=dead`,
   never disable verification; `200`+`text/html` → the host fakes success,
   reject it. Full gotcha list in the families reference.
4. **Hunt new sources the right way.** WebSearch real queries ("placeholder
   image service", "sample mp4 direct link", "random avatar generator"),
   extract the **direct-file endpoint** from the docs, feed it through the
   verifier, reuse known-good families to spawn more distinct hosts.
5. **Dedup by the `family` column before counting.** `SoundHelix-Song-1…-10`
   is ONE family; DiceBear styles are ONE family. Two domains of one service
   can count separately — say so. When a category can't reach N distinct
   providers, report the honest split ("10 providers + 5 labeled style
   endpoints = 15 assets"). Never pad a count with unverified or duplicate URLs.
6. **Ship a script + the catalog rows** (`catalog.py add` per proven source,
   `catalog.py log ADD …` for the reasoning), verify the written rows once
   more, clean up scratch.

## Category depth — read the reference before hunting there

| Category | Extra law | Reference |
|---|---|---|
| PDF books | the **rights gate comes first**: licence-gated routes, `pdf_identity.py` proof, refuse-rows are catalog material | [`references/documents-pdf-books.md`](references/documents-pdf-books.md) |
| Brand logos | a **filename-resolution** task, not URL-hunting: pull each provider's own slug index, pin `tags.latest`, exact names only, hash-compare for stubs, trademark rights gate | [`references/brand-logos.md`](references/brand-logos.md) |
| Any category | source families to spawn candidates + field gotchas (UA traps, Wikimedia width sets, look-alike domains) | [`references/source-families.md`](references/source-families.md) |
| Catalog writes | schema, `add/stamp/set/log` discipline, never-delete, ledger-explains rule, date-evidence rule | [`references/catalog-and-scripts.md`](references/catalog-and-scripts.md) |

## The three laws in one place

1. **Prove bytes, not status codes** — `verify_sources.py` decides, always.
2. **Rights before availability** — a fetchable file the holder never
   released is a `refuse` row, not a find.
3. **Leave the catalog better** — every hunt ends in `catalog.py` writes with
   notes explaining traps; never delete, flip status.
