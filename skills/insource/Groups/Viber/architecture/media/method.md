# Media Architecture Pillar — imgery

## 1. Overview & Philosophy

Every image, icon, font, and clip the app renders is a stack of decisions —
**what it is, where it comes from, which format, when it loads, how it is
cached, what it costs**. Left undecided, the default path is the model's
habit: hand-draw the Google logo in inline SVG, ship one JPEG everywhere,
lazy-load the hero, autoplay without a poster. Each habit has a documented
price. This pillar decides all of it once, per application.

The pillar's doctrine:

- **Sourcing before pixels.** A brand mark is obtained, never improvised.
  Hand-drawn recreations read amateur at exactly the sizes users judge, can
  violate brand terms, and go stale on rebrands the drawer never heard of.
  Official vector → verified bytes → vendored with a pinned revision. The
  law and the evidence: [brand-marks](references/brand-marks.md).
- **Rights before availability.** A fetchable file says nothing about
  permission: trademark ≠ file license (CC0 covers the SVG, not the mark).
  Every third-party asset carries a rights row in the ledger.
- **Geometry is a contract.** `viewBox` → `preserveAspectRatio` → `overflow`,
  in that order; build steps that delete viewBox are the "cut-off logo" bug
  waiting to ship. ([svg-engineering](references/svg-engineering.md))
- **The load mode is the security boundary.** Inline/`<object>`/direct SVG
  executes scripts; `<img>`/background does not. Untrusted uploads get a
  sanitizer or image mode — optimization is not sanitization.
- **Space reservation is unconditional.** Every `<img>`/`<video>`/`<iframe>`
  ships width/height or an aspect-ratio box; an unreserved 0×0 lazy box is
  the gallery-load-everything reflow, and the `ui` pillar's skeleton exists
  to cover what media cannot pre-declare.
- **The LCP rule is absolute.** Never lazy-load the LCP candidate; eager +
  `fetchpriority="high"` + HTML-discoverable. Below the fold, lazy by default
  — both halves or neither.
- **Facade every non-primary third-party embed.** 100 KB–2 MB of foreign JS,
  a 10–80 s timeout can block render, and ≈500 KB is saved by deferring the
  one YouTube iframe; the load→preconnect→click ladder is the documented
  pattern, consent-gate the swap, nocookie is hygiene not consent.
- **Earn the download: fonts and formats.** Format pipeline (AVIF/WebP/
  baseline from one transform layer), `w`+`sizes` or nothing, and a custom
  font pays for itself (WOFF2, subset, metric-matched fallback, declared
  `font-display` per role) or the answer is `system-ui`.
- **Budgets in metric units.** LCP ≤ 2.5 s p75, CLS ≤ 0.1, hero image ≈ ≤200 KB
  on the project's own p75 network, third-party JS ≈ 0 KB at first render —
  re-measured per asset, never quoted from blogs.
- **Motion is a user preference.** Reduced-motion honored (remove/reduce/
  replace), pause controls on auto-motion, static fallbacks always available
  (poster, first frame, none). The `accessibility` pillar's user overrides
  outrank every default here.

Boundary map: `ui` owns layout mechanics and RTL mirroring; `accessibility`
owns user adaptation + the motion/autoplay obligations (this pillar supplies
their media-side mechanics and yields); `display` owns typeface *selection*
(this pillar owns *delivery*); `plugin` owns nothing here. The hunt-and-verify
tooling for asset sourcing is the external skill **fahlwy**; this pillar owns
the policy that makes the hunt a decision rather than a scramble.

## 2. Directory Structure & Assets

```text
media/
├── method.md                                          # this file — doctrine & workflow
├── assets/templates/
│   └── media-architecture-template.md                 # binding document skeleton
├── references/
│   ├── brand-marks.md                                 # icon/brand sourcing law + ledger (the Google-button rule)
│   ├── raster-loading.md                              # formats, srcset/sizes, loading posture, caching, budgets
│   ├── svg-engineering.md                             # viewBox contract, SVGO pins, sanitizer boundary, a11y naming, sprites
│   ├── fonts-delivery.md                              # WOFF2/subset/font-display/metrics; icon fonts legacy
│   ├── time-based-media.md                            # preload/poster/autoplay, facade ladder, consent, Lottie/Rive, native players
│   └── discovery-interview.md                         # targeted questions + which decision each drives
├── examples/
│   └── media-walkthrough.md                           # hero-image + embed + icon-policy pass on one screen
└── scripts/
    └── imgery_lab.py                                  # live verification of this pillar's empirical claims
```

**The lab (`python scripts/imgery_lab.py`)** re-probes the doctrine's
measured claims against the live vendors: the Google/GitHub asset bundles
(URL, size, SVG anatomy, the blur/foreignObject composite), clause strings
on the Apple/Meta pages, ghost-serving on versionless CDNs, facade byte
scale vs the embed document, thumbnail error-body traps, font CORS headers,
the SVGO default list read from **npm source** rather than docs, and a
citation-liveness sweep over every URL this pillar quotes. Structural drift
FAILs (the doctrine must then be re-read, not silently kept); size drift is
INFO with the measured value. Web doctrine ages — run the lab before citing
any number in a generated `media-architecture.md`.

## 3. Workflow

1. **Recon (read first, never ask what the repo answers):** inventory shipped
   media — formats in use, embeds/iframes present, icon mechanism (font?
   sprite? components? hand-drawn paths — grep for suspiciously long `d="` on
   brand shapes), font stack + `font-display` usage, image pipeline (CDN?
   build transforms? `next/image`-style component?), existing cache headers,
   reduced-motion handling. Note which claims need measurement vs which the
   code answers.
2. **Interview** ([references/discovery-interview.md](references/discovery-interview.md)):
   ask only what the code cannot — primary content declaration (what *is* the
   LCP candidate), embed interaction probability, brand-asset authority,
   typeface load-bearing-ness, platform/data constraints.
3. **Decide per lane,** reading the reference that owns it: raster/format &
   loading posture (raster-loading.md), icon system + brand ledger
   (brand-marks.md, svg-engineering.md), fonts (fonts-delivery.md), time-based
   + facades (time-based-media.md).
4. **Author** `media-architecture.md` from the template; register shared
   units (transform layer, facade component, icon tokens, fallback-face
   generator) in UNITS.md cross-check.
5. **Verify against the numbers, not vibes:** LCP subparts before/after the
   posture change; byte weight of one real hero at the p75 network; facade
   swap works with JS off or states the loss; every reserved box survives a
   slow-profile load without reflow; sanitizer path has a negative test
   (`<svg><script>` upload stays inert).

## 4. Anti-patterns (the easy paths, all reproduced in the wild)

| The shortcut | The documented cost |
|---|---|
| Hand-drawn brand glyph in JSX/CSS | wrong mark, stale after rebrand, trademark exposure ([brand-marks](references/brand-marks.md)) |
| One JPEG everywhere, per-page encodings | pays 2×+ over the pipeline; drift between copies |
| `loading="lazy"` on the hero | verified LCP regression (3.5 s vs 2.9 s p75 medians) |
| `srcset` with `w` and no `sizes` | 100vw assumption fetches hero bytes for a 32 px icon |
| PNG sprite sheet | breaks responsive selection, caches one huge key |
| Icon font for UI icons | wrong-meaning fallbacks, layout shift, a11y noise; official verdict: replace with SVG |
| Inline `@font-face` list untouched since generation | FOIT windows nobody chose; `preload` without `crossorigin` fetches twice |
| Raw YouTube iframe above the fold on a blog post | 100 KB–2 MB foreign JS to a video most visitors never play |
| `maxresdefault.jpg` trusted, `onerror` relied on | the 404 returns a valid JPEG body; the error never fires |
| "SVG optimized" treated as "SVG safe" | `removeScripts` is not in any default preset; upload paths need a real sanitizer |
| Base64 everything "for fewer requests" | 7 logo copies in one stylesheet is a verified real failure |
| Service-worker precache list grown by habit | install-time bytes/storage/CPU for content that may never render |

Tier-irrelevant: none of this changes under the `tiers` type architecture;
media doctrine composes with every level.

## 5. Definition of Done

`media-architecture.md` exists and names, per class: the format pipeline, the
loading posture with the LCP candidate declared, the space-reservation rule,
the icon system (one style grammar) + a brand-mark ledger whose rows trace to
official or explicitly-waived sources, the font decisions (or the `system-ui`
declaration), the embed ledger (direct/lazy/facade per embed with the cost
numbers), cache & delivery policy, budgets in metric units, reduced-motion
fallbacks, and open decisions listed — never defaulted silently. Shared units
registered; sync points declared with their same-change duty.
