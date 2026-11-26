# 03 — Rendering and encoding

Two independent decisions: **who rasterises the SVG** and **who writes the PNG**. They are independent
because the first is about text shaping and the second is about bytes on disk. Getting them confused is how
projects end up needing a browser at request time.

## 1. The renderer: in-process, shaped, no browser

Requirements, in order:

1. Rasterise SVG with correct **text shaping** — Arabic needs joining and contextual forms, not just
   codepoint-to-glyph mapping.
2. Embed a font file; never depend on system fonts (a container has none).
3. No subprocess, no browser, no daemon. The card route is an HTTP handler; a 1 s Chromium cold start per
   image is unacceptable and unshippable in a small container.
4. Deterministic output for a given input, so a fidelity test can compare pixels.

`@resvg/resvg-js` (resvg + tiny-skia + HarfBuzz) satisfies all four. A headless browser satisfies 1 and 2
and fails 3. Canvas bindings satisfy 2 and 3 and are weaker on 1.

### The selection gate (do this before writing any layout code)

Prove the renderer against a reference on the **hardest text in the product** — for an Arabic product, pure
Arabic with diacritics and a long word. Method:

1. Render the same string at the same size in the candidate and in Chromium (the reference every designer
   trusts).
2. Measure the **ink box** of the rasterised result (bbox of non-background pixels), not the advance width.
3. Compare.

Measured outcome in the reference project:

| Case | resvg ink box | Chromium ink box | Verdict |
|---|---|---|---|
| pure Arabic, one line | identical within 1 px | — | accepted |
| pure Latin, one line | identical within 1 px | — | accepted |
| **mixed** Arabic + Latin on one line | differs — logical order | visual (bidi) order | **renderer is not at fault; the design is** |

That third row is the important one. resvg does not implement the Unicode Bidirectional Algorithm over a
whole line; it emits runs in logical order. Chromium applies bidi. The fix is not a bidi pass bolted onto
the renderer — it is a **design law**: one script run per line, and mixed content is split into lines. See
`04-card-design-and-bidi.md` §3.

Keep the probe as a learning test with the numbers in it; the next agent will otherwise re-litigate the
choice.

### resvg usage notes

```
new Resvg(svg, {
  fitTo: { mode: 'width', value: 1200 },
  font: { fontFiles: [ttfPath], loadSystemFonts: false, defaultFontFamily: '<BrandFace>' },
  background: '#0B1220',            // only when the artwork is already opaque
})
.render().asPng()
```

- `loadSystemFonts: false` is mandatory: it makes a missing font a **visible** failure instead of a
  machine-dependent one.
- `fontFiles` takes real TTF/OTF paths. A WOFF2 will not load.
- Rendering is CPU-bound and synchronous; at 1200 × 630 with one font the reference cost was **550–1100 ms
  cold**, which is why the result is cached and why the route degrades instead of retrying.

## 2. The encoder: why not the obvious options

The requirement was a **palette PNG** (colour type 3) under a byte ceiling, produced by a script that must
also run inside a Node-based test runner.

| Candidate | Capability | Verdict |
|---|---|---|
| `sharp` | full libvips, quantise + palette output | Native binary; heavy install; rejected for a build script that only needs one encode |
| `pngjs` | decode + encode truecolour; `dePalette` is **read-only** | **Cannot write an indexed PNG.** Verified by reading its API, not by trying and failing |
| `Bun.Image` | `resize`, `rotate`, `flip`, `flop`, `modulate`, `placeholder`, `png/jpeg/webp/avif/heic` | No palette output, no compositing, no padding/crop, no SVG input, no text, no ICO. And it only exists under Bun — a Vitest run in Node throws |
| hand-written indexed encoder + quantiser | ~150 lines, `node:zlib` only | **Chosen** |

Measured `Bun.Image` surface at the time (from runtime introspection, not from docs):

```
present: avif blob buffer bytes dataurl flip flop heic height jpeg metadata modulate
         placeholder png resize rotate toBase64 toBuffer webp width write
absent : composite  extend/pad  crop/extract  SVG input  text  ICO  alpha flattening
```

The absence of `composite` and `extend` alone rules it out for icon assembly (mark over background, padded
to a square). The absence of palette output rules it out for the byte ceiling.

### The encoder, precisely

```
signature   89 50 4E 47 0D 0A 1A 0A
IHDR        width, height, bitDepth=8, colourType=3, compression=0, filter=0, interlace=0
PLTE        up to 256 RGB triples
tRNS        optional alpha per palette entry — omit entirely for an opaque file
IDAT        zlib.deflateSync(filtered scanlines)   filter byte 0 per row is fine for indexed data
IEND        empty
```

Each chunk: `length(4) type(4) data crc32(type+data)(4)`. Indexed 8-bit means one byte per pixel, so a
1200 × 630 card is 756 000 bytes of indices before deflate — which compresses extremely well **because
adjacent pixels share indices**; that is the whole reason a palette wins here.

Practical detail that cost time: **do not emit `tRNS` for opaque files**. Some consumers treat the presence
of `tRNS` as "has transparency" and composite on black. Opacity is a chunk-level fact, not a style.

### Quantisation: median cut

```
box = all pixels; repeatedly split the box with the largest channel range at its median
until boxCount == target
palette[i] = mean colour of box i
```

Then map each pixel to the nearest palette entry. Median cut on a photo-like gradient background gives
256 usable colours with no visible clustering; a naive uniform cube does not.

### Dithering: Floyd–Steinberg, and why not noise

```
err = oldPixel - newPixel
right      += err * 7/16
down-left  += err * 3/16
down       += err * 5/16
down-right += err * 1/16
```

- **Noise** (adding random ±n before quantising) breaks up banding but costs tens of KB per card: measured
  ≈ 75 KB per card, deleted from the generator.
- **Error diffusion** moves the error to neighbours instead of discarding it; the gradient stays smooth at a
  fraction of the cost.
- `ditherStrength = 0.35` was chosen **by eye at 300 px display width** — the size a card is actually seen
  at in a chat client. Record the display size when you record the strength, or the number is meaningless.
- Serpentine traversal (alternate the direction per row) removes the diagonal worm pattern of plain
  left-to-right diffusion.

### The byte-ceiling loop

```
for paletteSize of [256, 128, 64]:
    png = encode(quantise(raster, paletteSize, dither))
    if png.length <= maxBytes: accept
fall back to the largest palette and log the overrun
```

A **ladder** is the difference between "it fits today" and "it fits when someone adds a photo". Measured
outcome for 1200 × 630 cards with the reference artwork: **124–136 KB**, colour type 3, opaque, on the first
rung. The ceiling (`maxBytes = 300 KB`) was never approached, which is exactly why the ladder exists.

## 3. Where the encoder lives

Put it in the **shared** package, but outside the barrel that the app imports: it imports `node:zlib`, and a
barrel that pulls `node:zlib` into a browser bundle is a build error waiting to happen. Expose it as a
subpath (`<shared-package>/brand/encode`) and let the generator and the backend import that path explicitly.

This also fixes a real bug class: the drift gate (`--check`) must run in the same runtime as the build. If
the encoder needs Bun, the gate becomes runtime-dependent and someone will "fix" it by skipping the gate.

## 4. Composition without a compositor

`Bun.Image` cannot composite, `pngjs` cannot composite cheaply, and a graphics library is a large
dependency. Compose **in the SVG** instead:

```
<image href="data:image/png;base64,…" />   // mark, wordmark, background
<text>…</text>                              // copy
```

resvg resolves embedded data URIs, so the whole card is one SVG string and one rasterisation. The layer
loader reads the PNG files once, caches the base64, and the composer stays pure. This is also why the
encoder never needs `extend`/`pad`: padding is geometry in the SVG, not pixels in a bitmap.

## 5. Alpha flattening

To make an opaque file from an alpha one: composite over the background colour, then **drop the channel**.
Compositing without dropping leaves an alpha channel that is 255 everywhere — some iOS and Windows paths
still treat that as "transparent image" and composite on black. Measured effect on the splash: flattening
took 978 KB → **586 KB** each, because an all-opaque alpha channel and its entropy disappeared.

## 6. Determinism checklist

- [ ] `loadSystemFonts: false` and an explicit `fontFiles`
- [ ] Font file committed, referenced by a stable path
- [ ] No timestamps or random values inside the SVG (they break byte comparison)
- [ ] Fixed palette ladder, fixed dither strength
- [ ] `--check` mode: regenerate to a temp dir, compare bytes, exit non-zero on drift
- [ ] The same encoder used by the static generator and the runtime renderer (one code path, two callers)
