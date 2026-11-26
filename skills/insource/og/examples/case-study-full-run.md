# Case study — one full run, with the numbers

An anonymized worked run: an Arabic-first (RTL) product, one supplied PNG logo, no vector master, a
multi-app monorepo (SSR frontend + self-hosted backend), and a share link that rendered as a bare URL.
Everything below is what was **measured**, not what was planned. Names are replaced with roles; the numbers
are the real ones, because the numbers are the method.

## The starting position

| Fact | Value |
|---|---|
| Brand input | one PNG, 816 × 846, RGBA, containing a symbol **and** a wordmark |
| Background input | one PNG, 1733 × 907, with a bright ribbon crossing a corner |
| Vector master | none — searched the whole tree for `.svg/.ai/.eps/.pdf`, and the git history |
| Font | none in the repo |
| Product languages | `ar` (default), `ar-EG`, `en` |
| SEO state | 100/100 on-page, **zero** OG checks in the rubric |
| Share state | bare URL on every platform |
| Constraint | no browser process at request time |

## Phase 0 — the gate that decided the renderer

Hypothesis: a pure-JS SVG rasteriser will disagree with Chromium on Arabic. Test: render the same strings at
the same size in `@resvg/resvg-js@2.6.2` and in Chromium, measure the ink box of the raster.

| String | resvg ink box | Chromium ink box | Verdict |
|---|---|---|---|
| pure Arabic, diacritics, one line | identical within 1 px | — | pass |
| pure Latin, one line | identical within 1 px | — | pass |
| mixed Arabic + Latin, one line | **differs** — logical order | visual (bidi) order | **design law, not a renderer bug** |

Consequence, adopted as a law: **one script run per line**. The card composer splits runs
(`splitScriptRuns`) and never places two scripts on one line. `bidi-js@1.1.0` is used for direction
detection and single-line reordering (`og:title`), not for card layout.

Chromium was rejected for the runtime anyway: a browser process per card is a non-starter.

## The library probes

`Bun.Image` — introspected, not documented:

```
present: avif blob buffer bytes dataurl flip flop heic height jpeg metadata modulate
         placeholder png resize rotate toBase64 toBuffer webp width write
absent : composite  extend/pad  crop/extract  SVG input  text  ICO  alpha flattening
```

`pngjs@7` — `dePalette` is **read-only**. It cannot write a colour-type-3 PNG.

Consequence: a hand-written 8-bit indexed encoder + median-cut quantiser + Floyd–Steinberg dither, living in
the shared package (`<shared-package>/brand/encode/`) and exposed as a subpath because it imports
`node:zlib` and must stay out of the browser barrel. Both the static generator and the runtime renderer call
it, so there is one encode path.

## The master analysis

Row ink profile → two content bands (an opaque plate, so the measure is luma, not alpha):

| Band | Rows | Share |
|---|---|---|
| mark | 0 – 499 | ~59 % |
| gap | 500 – 534 | ~4 % |
| wordmark | 535 – 845 | ~36 % |

The mark crop boundary sits **inside the gap**, so a resample blur cannot drag wordmark pixels into the mark
crop.

Palette, measured by 5-bit bucketing over opaque pixels. Values below are **illustrative** (a neutral
deep-plate + emerald scheme); the run produced its own, and yours will too:

| Role | Illustrative values |
|---|---|
| highlight | `#34D399`, `#6EE7B7` |
| body | `#10B981`, `#059669` |
| shadow | `#0D9488`, `#14B8A6` |
| plate | `#0B1220`, `#12203A`, `#1B2C4A` |
| wordmark | `#FFFFFF` |
| tagline | `#BFFBE0` |

The stylesheet's CTA accent was a **different hue family** from the artwork's primary — visibly different
when substituted. Two roles were declared, not one: `BRAND_MARK` (never re-toned) and `BRAND_ACCENT`
(mirrored from the stylesheet token file, locked by a test).

A decorative ribbon speck inside the mark's bbox was masked with a measured mask rectangle rather than
edited out of the master.

## The SVG hypothesis, and its death

| Check | Result |
|---|---|
| vector source in repo / history | none |
| trace at 16 / 32 / 48 px vs downscaled master | holds at 48+, mushes at 16–32 |
| distinct hues in the mark | 6+ across two gradients — a flat trace changes the brand |
| SVG as `og:image` | no major consumer rasterises it |

Shipped: a *favicon-grade* `favicon.svg` (silhouette, two colours, 32 grid), PNG fallbacks for every size, and
an ADR line saying a real vector master is a future upgrade.

## The generated set

**70 files, 6 491.6 KiB**, one script (`scripts/brand-assets.ts`), `--check` mode wired into `prebuild`.

| Group | Files |
|---|---|
| browser/OS | `favicon.svg`, 16/32/48 PNG, `favicon.ico` (16+32+48), `mask-icon.svg`, `apple-touch-icon` 180, `icon-192`, `icon-512`, `icon-512-maskable`, `mstile-150` |
| manifests | `site.webmanifest`, `browserconfig.xml` |
| OG cards | 8 families × 2 locales + 2 defaults = **18** |
| runtime layers | `og-background.png`, `mark.png`, `wordmark.png`, `<family>-var.ttf` |
| iOS | `AppIcon.appiconset` (14 sizes) + `Contents.json` |
| Android | legacy 48/72/96/144/192 + adaptive 108/162/216/324/432 + `mipmap-anydpi-v26` XML |
| splash | 2732² opaque, ×2 |

Card results: **124–136 KB**, colour type 3, opaque, 1200 × 630, on the first rung of the palette ladder
(`[256, 128, 64]`), `ditherStrength 0.35` chosen by eye at 300 px display width. The default card is
byte-identical to the home card — intentional.

Splash flattening (composite over background, drop the alpha channel): **978 KB → 586 KB** each.

## The meta layer

One head-tag builder emits the full OG + Twitter block, from one owner, per indexable route. Two defects it
fixed:

- `og:locale` was hand-written as `ar_AR` — a territory that does not exist. Now derived:
  a BCP-47 constant `ar-EG` → `toOgLocale()` → `ar_EG`; `en` → `en_US`.
- The crawler-facing `<img>` in the first packet pointed at a 404; now a real 48 px PNG path.

The public-origin variable defaulted to a loopback address — the single most likely cause of blank previews in
production, and it fails silently.

## The dynamic layer

```
GET /og/{family}/{locale}/{slug}.png
```

- LRU: 256 entries **and** 64 MB, key `(family, entityId, locale, entityVersion)`.
- ETag = hash of the key → `304` on match.
- The upstream sync job invalidates entities; the translation cache clear also clears the OG cache.
- Cold render **550–1100 ms**; never on the page path.
- Degradation ladder: unknown / private / no copy / missing layer / render throw / unknown locale → static
  card, **HTTP 200**, `X-Og-Card: static`, one structured fallback log line with a reason.

## The gates

| Suite (role) | Tests |
|---|---|
| OG tag contract | 3 |
| dynamic cards | 6 |
| render fallback | 1 |
| render fidelity | 2 (five ±2 px baselines; `fontFiles: []` → 0 × 0) |
| brand asset set | 6 |
| brand palette | 3 |

Total conformance run: **22 files / 47 tests green**. The SEO first-packet suite stayed 3/3 — the meta change
cost no SEO point. The project check: 0 no-hardcode, 0 architecture, 0 missing translations, "Brand assets
verified: 70 files up to date". Doc sentinel: 227 files, 0 orphans, 0 broken links.

The `fontFiles: []` → **0 × 0** contrast is the test that proves the font is embedded rather than inherited.

## The governance sweep (same commit)

| Document (role) | What changed |
|---|---|
| the media/asset **pillar** | rewritten: roles, generator, opacity table, card artwork |
| the SEO **doctrine** §social cards | the Social Card Contract |
| the backend **function** doc | OG routes, cache, invalidation |
| the palette **sync block** | brand palette, every home |
| the **ADR** | the encoder section + Phase 0 measurements |
| the **decision log** | the decision |
| the **rulebook** | one router row + two facts |
| the **changelog** | dated revision |
| the **usage guide** | `assets:brand` / `assets:brand:check` |
| new **playbook** | `verify-social-cards.md`, indexed |

Commit shape: `feat(seo): serve OG cards from a shared indexed-PNG encoder and gate the brand asset set` —
roughly 43 files, ~1.1k insertions, 64 deletions.

## What went wrong (kept, because it will happen again)

| Problem | Cause | Fix |
|---|---|---|
| Card bands in the gradient | quantising a photo-like background to 256 colours with no dither | Floyd–Steinberg at 0.35 |
| Cards 400 KB+ | a noise floor added before quantising to "avoid banding" | deleted the noise; dither does the job at ~75 KB less per card |
| Drift gate would not run in CI | encoder used `Bun.Image`, undefined under Node/vitest | hand-written encoder, no runtime-specific API |
| Arabic letters disconnected in a subset | subsetting stripped GSUB | no subsetting for the card font |
| Icons "harmonised" with the button colour | one palette role instead of two | `BRAND_MARK` vs `BRAND_ACCENT` + a conformance test |
| Maskable test passed on a broken icon | thresholded on "different from the corner colour" | threshold on luminance |
| Silent generic cards | no observability on the fallback path | `X-Og-Card` header + reason log |

## The lesson in one line

The pipeline is not "make icons". It is: **prove the renderer, measure the master, key the copy, degrade
instead of failing, gate the bytes, and hand the platforms to a human.**
