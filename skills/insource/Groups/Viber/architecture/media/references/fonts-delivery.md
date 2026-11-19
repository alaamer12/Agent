# Fonts delivery: earn the download

Fonts are media: they cost bytes, block paint, and shift layout. The doctrine
is one sentence — **a custom font must be paid for; everything about its
delivery is a declared decision, never a default.**

*Numbers below are the documented web.dev/MDN semantics (fetched; links at
end). Verify per project: browser timing values drift with versions.*

## 1. Discovery mechanics (the facts agents get backwards)

- `@font-face` alone **downloads nothing** — the font is fetched only when used
  styling matches rendered content. A `preload` for a never-referenced face is
  pure waste; audits start from CSS usage, not from the face list.
- Face declarations hide inside external CSS: browsers must fetch+parse the
  stylesheet before discovering the font need. The fix is **inline the
  `@font-face` block in `<head>`** (never inline the font files themselves);
  partial inlining still waits for the rest of the CSS.
- Third-party hosts: `preconnect` twice — plain for the CSS origin, **with
  `crossorigin`** for the font origin (fonts travel over a CORS connection;
  canonical pair: `fonts.googleapis.com` plain + `fonts.gstatic.com`
  crossorigin). A `<link preconnect>` beats `@import` for the stylesheet itself.
- `preload` is a scalpel, not a policy: it bypasses content negotiation and
  **ignores `unicode-range`** — use only for the one critical face, one format,
  and **always with `crossorigin`, or the font is fetched twice.** Unused
  preloads warn in Chrome ~3s after `load`; over-prioritizing means nothing is.

## 2. Format: WOFF2 only

WOFF2 (Brotli) compresses ~30% vs WOFF with the widest support; the practitioner
verdict quoted by web.dev: "Use only WOFF2 and forget about everything else…
prevents any accidental double or incorrect font downloads." Older formats
(WOFF1/TTF) delay LCP when the LCP candidate is text. Exception: variable-font
`tech()` declarations and static-fallback stacks (both official Google Fonts
practice) — ship a static face for non-supporting targets behind
`@supports (font-variation-settings: normal)`.

## 3. Subsetting and rights

`unicode-range` slices the font per script (Latin ≈ 100–1000 glyphs; CJK can
exceed 10,000) — files download only when a matching character renders.
Google Fonts ships per-script subsets automatically; **self-hosting teams
re-introduce the whole-font file by forgetting this** — the named missed
optimization. Tools: subfont / glyphhanger / the `text=` API parameter.
**Check licenses allow subsetting and self-hosting** — the license clause is
part of delivery, not a lawyer problem afterwards. Self-hosting is not
automatically faster: Web Almanac measured third-party-font sites rendering
*faster* on average — self-host only with CDN + HTTP/2 confirmed.

## 4. `font-display`: the swap-window contract

Mechanics: block period renders the fallback **invisible** (FOIT); swap period
renders it visible and replaces when the face lands (FOUT); after the failure
period the load is abandoned. Documented timings (Chromium/Firefox; Safari
historically blocks **indefinitely**):

| value | block period | swap period | when it is right |
|---|---|---|---|
| `block` | ~2–3s | infinite | guaranteed web-font first paint — deliver early or you show nothing |
| `swap` | ~0ms | infinite | branding/display faces — visible text fast, shift risk after |
| `fallback` | ~100ms | ~3s | rare; text you can afford to miss once |
| `optional` | ~100ms | none | body text on slow paths: no shift ever, font may never appear |
| `auto` | UA | UA | initial value; not a choice you should keep |

Mix per role (web.dev): `swap` for brand-critical faces, `optional` for body.
One documented discrepancy to treat carefully: web.dev's CLS section suggests
"preload + default `block`", while MDN makes `auto` the initial value — read
`block` as an explicit opt-in, and the honest pair as: **preload+`block` =
no shift but slow paint; `optional` = no shift and never blocks.** Neither is
free; the free option is §6.

## 5. Killing the shift itself: metric overrides

`font-display` chooses *when* text paints; only metrics decide whether it
*moves*. Declare an adjusted fallback face: `size-adjust` scales every metric
(glyph advances, baselines) of a `local()` font — e.g.
`@font-face { font-family: "Roboto-fallback"; size-adjust: 100.06%; src: local(Arial); }`
— plus `ascent-override` / `descent-override` / `line-gap-override` when plain
scaling is not enough (Chromium 87+/Firefox 89+; Safari lagged — verify). Two
calibration targets: adjust fallbacks **toward the brand** (design-system
default), or match a benchmark face. List multiple adjusted `local()` fallbacks
(Arial *and* Arimo) — `local(Arial)` is not everywhere — and font-family order
is critical. This belongs in the architecture document as a table per brand
face, values computed once (tools: fontsize.be-style calculators).

## 6. The zero-cost option: `system-ui`

System fonts need no download, no swap window, no CLS mitigation, no subsetting
pipeline, no license audit. "System fonts can work particularly well for body
text" (web.dev). Doctrine: unless the typeface is load-bearing brand, the
answer to "web fonts strategy" is: **system stack for text, custom face only
where the brand demands it** — then apply §1–5 for that one face.

## 7. Variable fonts

One file replaces N static styles (registered axes `wght/wdth/slnt/opsz/ital`;
`src … format('woff2-variations')` legacy twin documented). Economics are
conditional: Monotype's 48-style case = 88% smaller total, but *one* style of
a variable file is usually **larger** than the static face. The sharp trap:
`font-variation-settings` **resets every axis you don't restate** (no
inheritance between declarations) — drive axes via custom properties feeding
one declaration; animations must target the settings directly (custom-property
animation doesn't reach the font). Bigger single file ⇒ wider visible swap
window: §4/§5 apply harder than with static faces.

## 8. Icon fonts are legacy

Official performance verdict (web.dev): fallbacks mean wrong-looking glyphs
with wrong meanings, big layout shifts, "When possible, **replace icon fonts
with SVGs**, which is also better for accessibility." Real CMS cores are open
on migrating (WP Trac: Dashicons). Residual legitimate uses: decorating pseudo-
elements with no DOM node, and migrating native systems. Platform icon systems
(SF Symbols, VectorDrawable) are vector *images* with text traits — not the
icon-font pattern. (SVG icon mechanics: [svg-engineering.md](./svg-engineering.md) §4–6.)

## Sources

- web.dev: [font best practices](https://web.dev/articles/font-best-practices.md.txt),
  [preload critical assets](https://web.dev/articles/preload-critical-assets),
  [variable fonts](https://web.dev/articles/variable-fonts.md.txt),
  [css-size-adjust](https://web.dev/articles/css-size-adjust.md.txt),
  [embed best practices](https://web.dev/articles/embed-best-practices.md.txt)
- MDN: [font-display](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@font-face/font-display),
  [size-adjust](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@font-face/size-adjust)
- [WordPress Trac #65089](https://core.trac.wordpress.org/ticket/65089) (icon-font migration discussion, search-asserted)
Per-claim confidence marks: see the research dossier for this lane
(`.subagents/research-imgery-vectors-media.md`, kept as workshop evidence, not
doctrine).
