# 02 — Reading the master before drawing anything

Every number in the asset set descends from three measurements of the supplied artwork: **where the ink
is**, **which regions it contains**, and **which colours it uses**. Measure once, record the numbers in the
ADR, and derive everything from them. Eyeballing a logo produces a favicon with a clipped edge and a card
with the mark sitting on the brightest part of the background.

Assume the worst input: one PNG, RGBA, no vector, no brand guide, possibly with a decorative ribbon or
glow that is *not* part of the mark.

## 1. Decode without dependencies

`node:zlib` plus the PNG spec is enough, and it keeps the analysis script runnable in any project:

```
IHDR  width, height, bitDepth, colourType, compression, filter, interlace
      colourType 6 = RGBA(4ch)  2 = RGB(3ch)  3 = indexed  0 = grey  4 = grey+alpha
IDAT  zlib.inflateSync(concat(all IDAT chunks))
      then per scanline: filter byte (0 none,1 sub,2 up,3 average,4 paeth) + bytes
PLTE  palette for colourType 3; tRNS = alpha table or a single transparent index
```

Only 8-bit, non-interlaced is worth supporting in a probe; anything else is converted upstream by the
designer's export. Refuse to guess rather than produce a wrong bbox.

## 2. Which measure is "ink"? (decide this before anything else)

A designer exports "RGBA" and calls it a logo, but the file may have a **baked plate**: alpha is 255 across
the artwork and 0 only outside a rounded rectangle. An alpha-only profile then reports `bbox = the whole
canvas`, `padding = 0`, and **no gaps** — worse than useless, because it looks like a measurement.

Pick the measure that matches what "ink" means in *this* artwork:

| Artwork | Measure | Rule |
|---|---|---|
| cut-out logo on transparency | **alpha** | transparent fraction ≥ ~35 %; ink = `a > 8` |
| bright artwork on a dark plate (baked background) | **luma** | plate luma < 60 and bright share < ~45 %; ink = `a > 200 && luma > 100` |
| flat background, content differs in hue | **colour** | ink = `|Δr|+|Δg|+|Δb| > ~28` from the modal colour |

The master in one run was the second case, and this is what the difference looked like:

```
alpha mode   bbox = full canvas      bands = 1 (no gap found), padding "0"
luma mode    bbox = inset a few px   bands = mark | gap | wordmark   ← correct
```

So: run all three, look at the band count, and trust the one that finds a gap. Print the mode in the output —
"0 padding" from the wrong mode has sent people cropping artwork for an afternoon.

## 3. Alpha bounding box — the real content box

```
for each pixel with a > 0 (or a > 8 to ignore a halo):
    minX, minY, maxX, maxY
```

Then record the **padding** on each side. Padding is not part of the artwork and must not survive into
icons: a mark with 60 px of transparent margin becomes a mark at 70 % scale in a 512 px icon.

- If the artwork was exported with padding, crop to the alpha box first, then add the *destination's*
  optical padding.
- If the alpha box touches an edge, the master is already cropped — do not "fix" it by inventing margin;
  centre it and accept the tighter framing.

## 4. Row/column ink profile — find the internal regions

The supplied file was one image containing **two** things: a symbol and a wordmark underneath it. The
profile finds the seam without guessing:

```
inkRows[y] = count of pixels in row y that pass the ink test from §2
```

Scan for runs of rows where `inkRows[y] == 0` — the gaps between content bands. In the master from that run
(a near-square file with a dark plate, `luma > 100`) the result was:

| Band | Share of height | What it is |
|---|---|---|
| mark | ~59 % | the symbol, including a decorative element that belongs to the background |
| gap | ~4 % (~30 rows) | empty rows — the seam |
| wordmark | ~36 % | the logotype, including its tagline |

So `MARK_REGION.y1` sits **inside the gap**, a few rows below the last mark pixel, not exactly at it: a
resample blur cannot drag wordmark pixels into the mark crop. Always take margin on the side of the gap you
are cutting.

Sanity check the gap's width before trusting it: ~4 % of the height is a real design gap. A 4-row gap is
usually a rendering artefact between two letters, not a seam.

The same profile transposed (`inkCols[x]`) gives horizontal centring and the widest glyph, which is what
you need to size a wordmark layer for the card.

## 5. Palette measurement — count, do not pick by eye

Quantise to 5-bit channels and count:

```
key = (r >> 3, g >> 3, b >> 3)  →  count, sumR, sumG, sumB
sort by count; report mean colour per bucket and its share
```

Report by **role**, not by hex list — the role is the durable fact, the hex is a measurement:

| Role | What you are looking for |
|---|---|
| highlight | the lightest tint of the primary hue |
| body | the primary hue at its dominant value (usually the top bucket) |
| shadow | the same hue, darker, where the artwork turns |
| plate | the deep background colour, if the artwork has one |
| on-plate | the wordmark's colour (often pure white) |
| muted | the tagline / secondary text colour |

Two rules that follow from this:

1. **The icon palette is the measured one.** Do not substitute the stylesheet's accent, even when the two look
   close. In one run the UI accent was a yellow-green while the artwork's primary was a mint — close enough to
   look interchangeable, different enough that the substitution visibly changed the icon.
2. **The accent is a second, separate role.** It is mirrored from the stylesheet and locked by a test
   (see `04-card-design-and-bidi.md` §6). Two roles, one module, no third.

## 6. Region extraction and the mask problem

Cut the mark and the wordmark as separate **alpha** layers. They are runtime inputs, not shipped icons:

- `mark.png` — mark only, alpha, tight crop.
- `wordmark.png` — logotype only, alpha, tight crop.

A decorative element that belongs to the *background artwork* (a bright ribbon crossing a corner, a glow,
a light streak) will be caught inside the mark's bounding box. Do not delete it from the master and do not
try to trace it — mask it:

```
MARK_MASK = { x0, y0, x1, y1 }   // the measured rectangle of the decorative element
```

The mask lives as a constant next to the region constants, so the next person sees *why* a rectangle of the
mark is being erased instead of finding a silently damaged artwork.

## 7. The "can this be an SVG?" investigation

The tempting shortcut is: trace the PNG once into an SVG, then every size is free and the file is 3 KB. It
is worth investigating properly, and worth refusing honestly.

**Where the hypothesis was searched, and what killed it:**

| Hypothesis | Where it was checked | Verdict |
|---|---|---|
| The original vector exists in the repo | full-tree search for `.svg`, `.ai`, `.eps`, `.pdf`, sketch/figma exports; `git log` on any candidate | Nothing. The only brand file was the raster PNG |
| A trace is good enough at 16 px | traced the alpha contour, rasterised the trace at 16/32/48 and compared with a downscale of the master | The trace holds at 48+, mushes at 16–32: anti-aliasing on a 4-colour gradient artwork does not survive a 16 px grid |
| The gradient survives a flat trace | counted distinct hues in the mark | 6+ distinct colours across two gradients; a flat 4-colour trace changes the brand |
| SVG is acceptable as `og:image` | each platform's documented accepted image types, plus what scrapers actually fetch | No major consumer rasterises SVG. Rejected outright |
| A traced SVG is smaller | traced file vs 48 px PNG | True (≈4 KB vs ≈3 KB) and irrelevant: size was never the constraint |

**The verdict that shipped:** generate `favicon.svg` as a *favicon-grade* simplification (the mark's
silhouette, the two dominant colours, no gradient, drawn on a 32 grid), keep PNG fallbacks for every size,
and record in the ADR that a real vector master is a **future upgrade**, not a completed task. A trace is
not a vector master, and saying so costs one sentence.

## 8. Master hygiene checklist

- [ ] Alpha present, 8-bit, non-interlaced, at least 512 px on the short side
- [ ] Alpha bbox measured; padding recorded
- [ ] Content bands found; region constants chosen inside the gaps
- [ ] Decorative elements identified and masked by rectangle, not edited away
- [ ] Palette measured, grouped, and written into the palette module
- [ ] Wordmark exists as pixels (never re-typeset it — the typeface's spacing is the brand)
- [ ] Background master kept separate, never cropped, only resized
- [ ] Every number above appears in the ADR with the method that produced it

## 9. When the master is the wrong shape

| Situation | Do |
|---|---|
| Mark is wider than tall | Size by the **long** side; the short side gets the padding. Never stretch |
| Wordmark is much wider than the card allows | Scale the wordmark layer, do not re-wrap it: a logotype is not text |
| Master is < 512 px | Say so. Icons up to the master's content box are honest; anything larger is invented detail |
| Master has a background baked in | Treat it as an opaque master; there is no alpha to trace. Rebuild the mark region as a crop, not a cutout. Its row profile needs the **luma** measure (§2), not alpha |
| Two versions exist (light/dark) | Ship both only if the product really has a dark surface; otherwise pick the one that survives a light card and a dark OS tile |

## 10. Reconnaissance: what the codebase must tell you before you draw

The master is one input. The other is the *current* state of the brand surface — and it is usually wrong in
ways nobody has noticed. Do this pass first; it takes 20 minutes and it defines half the task list.

| Find | Search for | What it tells you |
|---|---|---|
| existing icon references | `<link rel="icon"`, `apple-touch-icon`, `mask-icon`, `manifest`, `theme-color` | the head is the single place icon links live; count them |
| the head builder | the function that emits `<title>`/meta (SSR injector, layout component, `useHead`) | **one owner**; two owners fight and the loser is whoever ran last |
| existing OG/Twitter tags | `og:image`, `twitter:card`, `property="og:` | usually absent, or pointing at a file that does not exist |
| public origin | `PUBLIC_*_ORIGIN`, `SITE_URL`, `baseURL`, `localhost` | the most common cause of blank cards; check the *default* |
| asset roots | `public/`, `static/`, `assets/`, `dist/` | what is served, and whether the build copies it |
| static handler | route rules for `/icons/*`, `/og/*`, `/favicon.ico` | does the server even serve these paths? |
| route inventory | the router / page tree | the families and the count of indexable routes you must cover |
| locale inventory | `i18n`, `locales/`, `messages/`, `lang` | the card matrix is families × locales |
| copy source | translation bundles, a CMS table, hardcoded strings | where card copy must come from |
| font situation | `*.ttf`, `*.woff2`, `@font-face`, `font-family` | is there a file you may embed, or only a web font? |
| design tokens | `_variables.scss`, `tokens.ts`, `theme.css` | the accent role you must mirror, and the values you must not duplicate |
| existing brand art | `logo`, `brand`, `icon`, `favicon` in `assets/` | the master, and whether a vector already exists |

Then write the gap list before touching anything: *tags missing on N routes, image path 404, no manifest,
no native icons, no font in the repo, origin defaults to localhost*. That list is the task; the design work
is the smaller half.

Two rules that come out of this pass:

1. **One owner for the head.** If both the SSR injector and a client component emit `og:image`, remove one
   before adding anything.
2. **Never trust a path you have not fetched.** A reference to `/og/home.png` in the code proves nothing;
   `curl -I` proves it exists.

