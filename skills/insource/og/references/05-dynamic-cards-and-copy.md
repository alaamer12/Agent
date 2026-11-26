# 05 — Dynamic cards, copy resolution, and never failing

A static card per family is enough to stop blank previews. Per-entity cards are what make a shared link
*about the thing it links to* — and they are the part that can turn a share into a 500.

## 1. Route shape

```
GET /og/{family}/{locale}/{slug}.png
```

- `family` is a closed, declared set — one entry per kind of indexable content that has its own card layout and
  badge (typically: home, a listing kind, a detail kind, a profile kind, a policy kind). It is closed on
  purpose: an unknown family falls back to the static card instead of inventing a layout.
- `locale` is a shipped locale, validated against the seed list.
- `slug` identifies the entity; the resolver decides what it means per family (a listing slug, a category slug,
  a username, a numeric id).
- The extension is `.png` because scrapers look at it; `.png` also documents the contract to humans.

Content type is `image/png`, `Cache-Control: public, max-age=…, immutable` for the cached form, and an
`ETag` derived from the **cache key**, so an entity edit changes the URL's meaning without changing the URL.

## 2. Pure model, impure shell

Split hard:

```
shared/seo/og/model.ts    buildOgCardModel(entity, family, copy, locale) -> plain object
shared/seo/og/svg.ts      model -> SVG string            (pure, no I/O)
backend/seo/og/layers.ts  read + cache mark/wordmark/background/font  (I/O)
backend/seo/og/render.ts  svg + font -> PNG via resvg -> indexed PNG
backend/seo/og/cache.ts   LRU + ETag
backend/seo/og/routes.ts  HTTP: resolve entity, call the above, degrade
```

The model builder is testable without a filesystem, a font, or a server. The SVG composer is a pure function
of the model — which is exactly what makes the fidelity test possible: feed the same model, get the same
pixels.

## 3. Cache

- **LRU, bounded twice**: `256` entries *and* `64 MB`, whichever hits first. A single entry is a 1200 × 630
  PNG of ~130 KB, but the *raster* before encoding is 3 MB, so bound by bytes as well as count.
- **Key**: `(family, entityId, locale, entityVersion)`. Including `entityVersion` means an edited entity gets a
  new key and the old entry ages out naturally; including the family and locale means one entity that appears
  in two families does not collide.
- **ETag**: stable hash of the key. `If-None-Match` → `304` with no body. This is what keeps a busy card hot
  without re-rendering.
- **Invalidation**: the sync/ingest path that updates the entity calls `invalidate(family, id)`. The
  translation-refresh path calls the cache clear, which clears **both** the translation cache and the OG
  cache — a card rendered with stale copy is the same bug as a page rendered with stale copy.
- **Cold cost**: measured **550–1100 ms** per card (resvg + quantise). That number is why the cache exists,
  why the route degrades, and why the card is never rendered on the page-render path.

## 4. The degradation ladder

Every rung returns **HTTP 200** with a PNG. There is no failure branch that returns an error status.

| Situation | Response | Log |
|---|---|---|
| Entity found, render ok | dynamic card, `X-Og-Card: dynamic` | — |
| Unknown slug | static family card | `og_render_fallback` + reason `unknown_entity` |
| Entity is private / unpublished | static family card | reason `not_public` |
| Entity exists but has no name in this locale | static family card | reason `no_copy` |
| Layer file missing (mark/background/font) | static family card | reason `missing_layer` |
| Renderer throws | static family card | reason `render_error` + the error |
| Locale not shipped | static default card | reason `unknown_locale` |

Two rules make this work:

1. **The static card is read from disk, not re-rendered.** If the renderer is the thing that failed, it must
   not be in the fallback path.
2. **The header is observability.** `X-Og-Card: static|dynamic` plus one structured log line per fallback
   turns "why is this link generic?" into a one-command answer. Without it, a silent degradation looks like
   a design choice.

**Why 200 and not 404:** scrapers cache errors aggressively and some clients render a broken-image glyph.
A generic card is strictly better than a hole, and the log already records the truth.

## 5. Copy resolution, shared by both layers

```
resolveCopy(locale, keys) -> Record<key, string>
```

- Static generator: reads the **seed** locale bundle from the repo.
- Runtime renderer: reads **live** translations (database/cache), merged over the seed so a missing key
  degrades to the seeded text instead of an empty string.
- Both go through the same function, so a card cannot be seeded with one string and rendered with another.

Entity names are not copy keys. They come from the entity row, in the entity's own locale column, with a
documented fallback (e.g. `name_ar ?? name`). Record the fallback in the ADR; "the Arabic name is empty so
the card shows nothing" is a real and common defect.

## 6. Locale tags on the meta layer

`og:locale` is `ll_TT` — language, underscore, territory. Not a BCP-47 tag, not `ar_AR`.

```
LOCALE_BCP47 = { ar: 'ar-EG', 'ar-EG': 'ar-EG', en: 'en-US' }
toOgLocale(tag) = tag.replace('-', '_')        // ar-EG -> ar_EG, en-US -> en_US
```

Reference bug that this fixed: the injector emitted `ar_AR` — a territory that does not exist — because
someone hand-wrote the string. Derive it; never write it.

Also emit:

- `og:locale` = the page's locale
- `og:locale:alternate` = every *other* shipped locale for that route
- `<html lang>` and `dir` from the same table, so the card and the page agree

## 7. The meta layer is not optional

Per indexable route, in the **raw first HTML packet**:

```
og:type, og:title, og:description, og:url, og:site_name, og:locale, og:locale:alternate
og:image, og:image:type, og:image:width, og:image:height, og:image:alt
twitter:card=summary_large_image, twitter:title, twitter:description,
twitter:image, twitter:image:alt
```

Rules that break cards in practice:

- **`og:url` and `og:image` must be absolute and HTTPS.** A relative path is ignored; a `localhost` origin
  ships blank previews in production. The single most common cause is a public-origin variable left at its
  loopback default — and it fails silently.
- **`og:image` must point at a file that exists at build time.** The static handler must serve `/og/*` even
  when the dynamic route is down.
- **`twitter:image` is separate.** Some clients read only Twitter tags; leaving it unset is a blank card on
  X.
- **`og:image:alt` is read by assistive tech** in some clients; write a sentence, not a filename.
- **Only the SSR injector emits these tags.** If a client-side component also sets them, two sources fight
  and the loser is whichever ran last. One owner.

## 8. Serving the files

The static handler serves `/icons/*`, `/og/*`, `/brand/*`, `/favicon.ico`, `/apple-touch-icon.png`,
`/site.webmanifest`, `/browserconfig.xml` from the built client directory, with:

- an **extension allowlist** (`.png .svg .ico .webmanifest .xml .ttf`) so the handler is not a file server;
- a **traversal guard** (reject `..`, absolute paths, and anything resolving outside the root);
- long `Cache-Control` (assets are content-addressed by name and gated by drift check);
- a **root alias** for `/favicon.ico`: browsers request it at the origin root even when a `<link>` exists.

## 9. Dynamic-card checklist

- [ ] Unknown / private / throwing all return a static card with 200
- [ ] Response header names the branch that ran
- [ ] One log line per fallback, with a reason
- [ ] Cache bounded by count **and** bytes; key includes entity version and locale
- [ ] `ETag` + `304` verified with `curl -I`
- [ ] Entity edits and translation refreshes both invalidate
- [ ] Cold render measured and recorded; nothing renders on the page path
- [ ] `og:locale` derived from a table, `ll_TT` shape
- [ ] Absolute HTTPS origin in production, verified by fetching the real `og:image` URL
