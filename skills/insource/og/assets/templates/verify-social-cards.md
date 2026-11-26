# Playbook template — verify social cards on real platforms

> Copy to `<docs>/steering/tech/shared/playbook/verify-social-cards.md` (or your project's playbook folder),
> index it, and link it from the social-card doctrine. It is the **human** half of the contract: the repo
> proves the tags and the pixels, this proves the platforms.

## What is automated and what is not

| Automated (repo) | Not automated (this document) |
|---|---|
| every route emits the full OG + Twitter block | that a platform's fetcher accepts the response |
| `og:image` is an absolute URL to a committed PNG | that a CDN does not serve the SPA shell to crawlers |
| the image is 1200 × 630, opaque, ≤ 300 KB | that the platform's cache has refreshed |
| entity cards render; failures degrade to static | that the card is legible in that platform's crop |
| layout is stable within ±2 px | that the description is not truncated |

## Preconditions

- [ ] Deployed to a real HTTPS origin (not `localhost`, not an IP)
- [ ] The public-origin variable (whatever this project calls it) points at that origin
- [ ] The static card set is present in the built client output
- [ ] The dynamic route is reachable for at least one real entity per family
- [ ] `curl` available; the origin does not require auth for `/og/*`

## Step 1 — pre-flight (5 minutes, do this first)

```bash
BASE=https://example.com
ROUTE=/ar/listings/some-entity

# tags in the raw packet
curl -s "$BASE$ROUTE" | grep -E 'og:|twitter:' | sort

# the image URL from og:image, exactly as emitted
curl -sI "$BASE/og/listings/ar/some-entity.png"
#   → 200, content-type: image/png, etag, cache-control

# a crawler user-agent sees the tags, not the SPA shell
curl -s -A 'facebookexternalhit/1.1' "$BASE$ROUTE" | grep og:image

# caching
ETAG=$(curl -sI "$BASE/og/listings/ar/some-entity.png" | grep -i '^etag:' | tr -d '\r' | cut -d' ' -f2)
curl -sI -H "If-None-Match: $ETAG" "$BASE/og/listings/ar/some-entity.png"   # → 304

# the fallback branch
curl -sI "$BASE/og/listings/ar/does-not-exist.png"                          # → 200, X-Og-Card: static
```

Stop here if any line fails: no platform will show a card that `curl` cannot fetch.

## Step 2 — eyeball, one surface at a time

Paste the **page URL**, not the image URL.

| # | Surface | Method | Expect | Result | Date |
|---|---|---|---|---|---|
| 1 | Facebook | Sharing Debugger → paste → "Scrape Again" | large image, title, description, no warnings | ☐ | |
| 2 | LinkedIn | Post Inspector | image renders, title not truncated | ☐ | |
| 3 | X / Twitter | compose a post, paste URL, wait for card | `summary_large_image`, image not cropped | ☐ | |
| 4 | Telegram | send the link to yourself | image, title, description | ☐ | |
| 5 | WhatsApp | send the link to yourself | image present (strictest on size) | ☐ | |
| 6 | Slack | paste in a channel | unfurl block, image not letterboxed | ☐ | |
| 7 | Discord | paste in a channel | embed colour, image | ☐ | |
| 8 | iMessage | send the link | preview card | ☐ | |
| 9 | Google / Bing | URL inspection in the webmaster console | the crawler sees the same first packet | ☐ | |

Per surface record one of: **pass** / **generic card** / **no card** / **wrong image**.

## Step 3 — failure triage

| Symptom | Likely cause | Check |
|---|---|---|
| no card anywhere | `og:image` is relative, `localhost`, or SVG | `curl -sI` the exact URL |
| card appears in the browser devtools but not on a platform | CDN/bot challenge returns the SPA shell | `curl -A facebookexternalhit/1.1` |
| generic family card for a real entity | renderer degraded | response header `X-Og-Card` + the fallback log line |
| 404 on the image | asset not in the built output, or the static handler does not serve `/og/*` | fetch the static card path directly |
| Arabic boxes | font not deployed, or `loadSystemFonts` on with no file | the `fontFiles: []` contrast test |
| Arabic/Latin on one line, wrong order | mixed-script line on the card | split into script runs |
| image cropped oddly | content outside the safe area | re-check the layout constants |
| card unchanged after a fix | platform cache | re-scrape (Facebook) or wait (others) |

## Step 4 — sign-off

| Field | Value |
|---|---|
| Commit | `<sha>` |
| Deployed origin | `<url>` |
| Families checked | `<list>` |
| Locales checked | `<list>` |
| Machine gates | `<n>/<n> green` |
| Platforms passing | `<n>/9` |
| Known gaps | `<e.g. WhatsApp not tested on a real device>` |
| Verified by | `<name>` |
| Date | `<YYYY-MM-DD>` |

## Pass criteria

The task is **done** when every machine gate is green **and** every platform row has an observed result.
A green build with an untested platform is "implemented", not "working" — say which one you are claiming.
