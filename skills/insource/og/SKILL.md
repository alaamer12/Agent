---
name: og
version: 1.0.0
author: Amr
specialized: none
description: >-
  Brand-asset and social-card pipeline for any product: one raster master in, every favicon, PWA/OS
  tile, store icon, splash and 1200x630 OG card out, plus a runtime renderer drawing per-entity cards
  in Arabic/RTL or any bidi script from live content with no browser at request time. Covers master
  analysis (bboxes, palette, SVG verdict), capability probing, resvg/HarfBuzz
  text with an embedded variable font, a hand-written indexed-PNG encoder (median cut +
  Floyd-Steinberg) that holds a byte ceiling without banding, per-file alpha contracts, iOS/Android
  icon sets, manifest, translation-key-only copy, LRU + ETag + degrade-never-fail card routes,
  conformance gates, an ADR, and the human platform checklist. Use for favicons, app icons, PWA tiles,
  splash, cards, OG/Twitter meta, RTL card rendering, dynamic images, or a blank link. Triggers: og,
  open graph, social card, share image, favicon, app icon, splash, maskable, mstile, apple-touch-icon,
  brand assets, twitter card, dynamic og, rtl card.
when_to_use: >-
  The user wants the brand/social surface built, audited or fixed: favicons and app icons, PWA/OS
  tiles, native store icons and splash, static or per-entity Open Graph cards, OG/Twitter meta tags,
  Arabic or RTL share images, or a shared link that renders as a bare URL. Also /og.
argument-hint: "[all | assets | cards | dynamic | native | verify] [target]"
---

# og — brand assets and social cards, end to end

Two layers, one generator, one encoder.

```
one raster master (+ background master + one font)
        │
        ├─► static asset set ──► favicons, PWA/OS tiles, iOS/Android icons, splash   (committed)
        └─► card model + SVG ──► static cards (committed) ──► dynamic cards (runtime, per entity)
```

**The failure this skill exists to prevent:** a page scores 100/100 on SEO and still shares as a bare
URL, because `og:image` points at an SVG that no scraper accepts, or at a path that never existed.
On-page SEO rubrics score **zero** Open Graph checks. Treat the social layer as its own contract.

## The ten laws (learned the hard way — do not re-derive them)

1. **OG images are PNG (or JPEG/WebP). Never SVG.** No major scraper rasterises SVG. A live SVG
   `og:image` is a blank card everywhere.
2. **Alpha is a per-file contract, not a global style.** Opaque: OG cards, `apple-touch-icon`,
   manifest icons, maskable, mstile, iOS AppIcon, Android legacy + adaptive background, splash.
   Transparent: `favicon.svg`, small favicon PNGs, `mask-icon.svg`, mark/wordmark layers, Android
   adaptive *foreground*. Wrong posture = a black square on iOS and in several previews.
3. **One script run per line.** Arabic and Latin never share a line on a card. resvg emits
   mixed-direction text in *logical* order; Chromium applies bidi. One line, one script — or the card
   disagrees with the page.
4. **Copy comes from the database / locale bundle, never from code.** Tagline, badge, stat labels and
   every entity name resolve through keys. Literal strings in the renderer are a defect (and usually a
   project golden-rule violation).
5. **Degrade, never fail.** Unknown entity, private entity, missing layer, render throw → the static
   family card, HTTP 200, plus a log line. A 500 in an image URL is an empty box in every preview.
6. **Generated assets are committed, with a drift gate.** Regenerate-and-compare in the build, or the
   palette and the shipped icons silently diverge.
7. **Hold the byte ceiling with dither, not with noise.** Quantise to an indexed palette with
   error-diffusion; a noise floor costs tens of KB and buys nothing.
8. **The logo is canonical.** Measure it, never re-tone it. If it is a raster, say so, trace a
   *favicon-grade* SVG from it, and record that a real vector master is a future upgrade.
9. **No browser at request time.** Rendering must be in-process (SVG rasteriser + shaping engine).
   A headless Chromium per card is a non-starter.
10. **The repo proves tags and pixels; a human proves the platforms.** Each social platform has its
    own fetcher and its own multi-day cache. Ship a checklist, not a claim.

## Pipeline (order is the contract)

| Phase | Do | Done when |
|---|---|---|
| 0. **Selection gate** | Probe the candidate renderer against a reference implementation on the hardest text in the product (usually Arabic). Write a learning test with numbers. | Ink boxes match within tolerance, or the candidate is rejected with evidence |
| 1. **Contracts first** | Palette module with documented roles; copy-key list; card geometry + byte ceiling as constants | One home for colour, one home for copy, no magic numbers in the renderer |
| 2. **Cards + meta (do this first if `og:image` is broken)** | Static cards per family/locale, full OG/Twitter tag block from the SSR injector, fallback path that really exists | Every indexable route × locale emits one complete block pointing at a committed PNG |
| 3. **Asset set** | Browser/OS icons, manifest, browserconfig, static handler for `/icons/*`, `/og/*`, `/brand/*` | Every file at its exact size with its declared alpha posture |
| 4. **Dynamic cards** | Route, entity resolvers, pure model + SVG composer, LRU + ETag, degradation ladder | Real entity renders; unknown/private/throwing all return the static card with 200 |
| 5. **Native** | iOS `AppIcon.appiconset`, Android legacy + adaptive + `anydpi-v26`, splash | Store icon sets match their manifests |
| 6. **Gates + governance** | Conformance suites, drift gate in `prebuild`, ADR, doctrine/pillar/rulebook/usage sweep | Build fails on drift; a human checklist exists for the platforms |

Phase 2 before phase 3 on purpose: the broken thing users feel is the shared link, not the favicon.

## Routing

| The task | Read |
|---|---|
| Which files do I need, at what size, opaque or transparent? | `references/01-asset-matrix.md` |
| Reconnaissance first: find the existing head, origin, asset roots, locales, fonts | `references/02-source-analysis.md` §10 |
| Analyse the master: ink measure, bbox, region split, palette, "is SVG enough?" | `references/02-source-analysis.md` |
| Rendering + encoding: which library, how to hit the byte ceiling, no banding | `references/03-render-and-encode.md` |
| Card layout, safe area, RTL mirroring, Arabic shaping, name fitting | `references/04-card-design-and-bidi.md` |
| Per-entity cards from the database, copy keys, cache, ETag, degradation | `references/05-dynamic-cards-and-copy.md` |
| iOS/Android/Windows/Capacitor: sizes, manifests, splash, adaptive icons | `references/06-native-and-os.md` |
| Fonts: where to get a variable font, licence duties, how to prove it is embedded | `references/07-fonts-and-licensing.md` |
| Conformance tests, drift gate, and the platform eyeball checklist | `references/08-verification-gates.md` |
| ADR, docs sweep, sync blocks, facts ledger, commit shape | `references/09-governance-and-adr.md` |
| How to choose a library (and how to reject one with evidence) | `references/10-library-selection.md` |
| A full worked run with real numbers and real failures | `examples/case-study-full-run.md` |

Copyable: `assets/templates/adr-template.md`, `assets/templates/brand-palette-module.ts`,
`assets/templates/verify-social-cards.md`.
Scripts: `scripts/analyze-master.ts` (bbox / bands / palette), `scripts/ink-box-probe.ts` (text
shaping proof), `scripts/ico-writer.ts` (multi-size ICO with no dependency).

## Two contracts to write before any pixel

**Palette — two roles, one module.** `mark` = measured from the logo; used for icons and cards, not
re-toneable. `accent` = the UI call-to-action colour, mirrored from the stylesheet with a test that
fails on drift. Collapsing them is the classic mistake: the icon inherits the button colour and the
brand quietly changes.

**Copy — keys, not strings.** `og.site_name`, `og.tagline`, `og.badge.*`, `og.stat.*`, plus the entity
name from its own table. The static generator reads the seed bundle; the runtime renderer reads the
same keys merged over live translations. One resolver function, two callers, so a seeded card and a
live card cannot disagree.

## Failure table

| Symptom | Cause | Fix |
|---|---|---|
| No card anywhere | `og:image` is a localhost URL, or SVG | Set the public origin; emit a PNG path |
| Tags present in `curl`, still no card | A CDN/proxy serves the SPA shell to scrapers; or the image 404s | Check the exact `og:image` URL with `curl -I` |
| Generic card for a real entity | Renderer degraded | Response header says which branch ran; check the render log |
| Arabic shows boxes | Font not deployed or `loadSystemFonts` left on with no file | Ship the TTF; assert with an empty-`fontFiles` contrast test |
| Arabic/Latin on one line | Entity name with two scripts | Split into script runs; one per line |
| Bands in the gradient | Dither strength 0 | Raise dither, lower palette, re-measure bytes |
| Card is 400 KB | Photo-like background at truecolour | Indexed palette + ladder until under the ceiling |
| Icon is black on iOS | Alpha channel in an app icon | Flatten onto the background and drop the channel |
| Artwork clipped by Android's mask | Mark outside the 80% safe zone | Full-bleed background, mark inside the safe zone |
| Icons drifted from the palette | No drift gate | Regenerate-and-compare inside `prebuild` |

## Honesty rules

- **Measure, never assume.** Every number in the ADR (ink boxes, bytes, millisecond cost) comes from a
  run you performed, with the method named.
- **A raster master is a raster master.** Say the ceiling out loud instead of pretending a trace is a
  vector.
- **Never claim a platform shows the card** because the tags are right. That is the human checklist's
  job; leave it unticked until someone looked.
- **Label the trade-off you accepted** (e.g. "dither instead of noise; 0.35 chosen by eye at 300px
  width") so the next agent can revisit it deliberately.
