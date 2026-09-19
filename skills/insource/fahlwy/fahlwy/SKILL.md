---
name: fahlwy
description: Over-smart asset-source hunter. Find and PROVE a required number of working free asset sources (images, avatars, video, audio, icons, fonts) by actually fetching bytes and validating magic signatures - never stop at a guessed URL. Can also discover fresh candidates via image search engines (icrawler + Baidu/Bing/Google) then verify them. Use whenever asked to find N sources, build an asset/placeholder source list, wire mockup media, or hunt down reliable hotlink/direct-download endpoints, then keep going until every slot is verified. Also for countable lists of working external asset URLs, finding ways to source media for a mockup/demo, catalogs of verified placeholder/stock endpoints, or topical/seasonal images beyond the static catalog.
---

# fahlwy — over-smart source hunter

## Overview

The ethos: **there is always a way.** When told to "find N sources," do not
settle for the first N plausible URLs or N guesses. Emit a script, hit the
network, and only count a source once it returns **real bytes of the right
type**. Iterate — more candidates, fixed paths, alternate hosts — until you hit
N genuinely-verified sources, or report the honest maximum with reasons.

`references/verified-urls.md` already contains 60+ verified endpoints across
images/avatars/video/audio (as of 2026-09-16) plus a "do-not-use" list. Prefer
reusing that catalog over re-hunting; re-verify any entry on a new day (free
hosts churn). When you discover new working/dead sources, append them to that
file — the skill compounds.

## The rule that matters

**A passing source is proven by content, not by status code.** Many "asset"
sites answer `200 OK` with an HTML error/consent/landing page, or an image host
serves a 200 with a tiny stub. Always validate:
- images: `Content-Type: image/*` **and** > ~256 bytes (or PNG/JPEG/GIF/WEBP/SVG magic)
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
   (see below) to spawn more distinct hosts. For topical or exhausted image
   needs, also run `scripts/search_images.py` (icrawler → Baidu/Bing) to
   surface candidates, then verify every hit the same way.
5. **Dedup by provider before counting.** `SoundHelix-Song-1` … `-10` is ONE
   provider. `api.dicebear.com/9.x/<styleA>` and `<styleB>` is ONE provider.
   Two domains of one service (`mdn.github.io` vs
   `interactive-examples.mdn.mozilla.net`) can count separately but say so.
   When a category can't reach N distinct *providers*, report the honest split
   (e.g. "10 providers + 5 labeled style endpoints = 15 assets"). Never pad a
   count with unverified or duplicate URLs.
6. **Ship a script + a markdown catalog**, run the verify once more, then clean
   up any `scratch/` you created.

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

## Search-engine discovery (new)

When the static catalog + known families are not enough, or the user asks for
fresh / topical assets (e.g. "find 10 free photos of mountains"), use image
search engines to surface candidate URLs, then **always** validate them with
`verify_sources.py`. Never trust a search hit as a final source until the
bytes prove it.

### Tool: icrawler

```bash
pip install icrawler   # one-time, if missing
```

**Engine ranking (icrawler):** Baidu is believed to have the highest precision
of the three. Bing and Google frequently return raw trash, broken links,
thumbnails that are not direct assets, or pages that fail verification.
Default to Baidu; only fall back to Bing or Google when Baidu is unavailable
or returns nothing useful.

```python
from icrawler.builtin import GoogleImageCrawler, BingImageCrawler, BaiduImageCrawler
import random

random_offset = random.randint(0, 50)  # vary this range as needed

# Prefer Baidu — highest precision; Bing/Google often yield trash or non-working URLs
baidu_crawler = BaiduImageCrawler(storage={'root_dir': "scratch/baidu"})
baidu_crawler.crawl(
    keyword='term',          # e.g. "free stock photo landscape"
    max_num=50,
    # offset=random_offset  # skips initial N results (supported by some backends)
)
```

Or use the helper script (defaults to Baidu):

```bash
python3 scripts/search_images.py "free stock photo landscape" --engine baidu --max 30
# then feed any direct URLs you can extract, or the downloaded files, into:
python3 scripts/verify_sources.py image <url-or-file> ...
```

### Rules for search results

1. **Search → candidates only.** Search engines return result pages, thumbnails,
   or CDN links that may be hotlink-protected, expiring, or HTML wrappers.
2. **Extract direct asset URLs** where possible (look for `images.pexels.com`,
   `cdn.pixabay.com`, Wikimedia upload paths, etc.). Prefer those over local
   downloads when the goal is a reusable hotlink.
3. **Prove every candidate** with `verify_sources.py image …`. Count only
   those that pass magic-byte + size checks.
4. **Prefer Baidu.** Bing and Google often surface trash or non-working results;
   keep max_num modest (20–50). Vary offset to avoid always seeing the same
   first page. Do not hammer any engine.
5. **Feed survivors back into the catalog** exactly as any other new source
   (Growth log + `✅` stamp). Local downloads under `scratch/` are ephemeral —
   clean them up; only durable direct URLs belong in `verified-urls.md`.

This path is especially useful for:
- topical / seasonal images the static catalog never covered
- expanding a category when known families are exhausted
- discovering new CDN patterns that can later become high-yield families

## Commands

```bash
# Verify arbitrary candidates (proves real bytes of the right type):
python3 scripts/verify_sources.py video URL1 URL2 URL3

# Re-check the whole shipped catalog quickly, then wire into a mockup:
grep -oE 'https://[^ )`]+' references/verified-urls.md | sort -u \
  | xargs python3 scripts/verify_sources.py any

# Discover new image candidates via search engines (then verify!):
python3 scripts/search_images.py "keyword" --engine baidu --max 30
```

## Resources

- `references/verified-urls.md` — the living catalog: 60+ verified sources by
  category, each with its exact direct-URL form, ⚠️/❌ markers, and the
  do-not-use graveyard (dead/blocked/HTML-faking hosts).
- `scripts/verify_sources.py` — magic-byte verifier with 5xx backoff-retry;
  exits 0 only when every URL serves real bytes. Run it before you trust or
  cite any endpoint.
- `scripts/search_images.py` — thin wrapper around icrawler (Baidu / Bing /
  Google) that downloads candidate images into `scratch/`; always follow with
  the verifier. Default and preferred engine is Baidu (highest precision);
  Bing and Google often return trash or non-working results.
