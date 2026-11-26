# 10 — Choosing libraries, and rejecting them with evidence

This domain is a minefield of plausible libraries that each fail on one specific capability. The method
below turns "which library?" into a checklist that produces a rejection reason you can put in the ADR.

## 1. Probe capabilities, do not read marketing

Documentation lies in both directions: it advertises what the author is proud of and omits the missing
primitive. Probe the **installed** package at runtime:

```ts
// object surface
const img = Bun.file('x.png') // or the package's factory
console.log(Object.getOwnPropertyNames(Object.getPrototypeOf(img)))
console.log(Object.keys(img))

// the specific primitives this domain needs
const needed = ['resize','crop','extend','composite','png','jpeg','webp','metadata','toBuffer']
console.log(needed.map(k => [k, typeof img[k]]))
```

Reference outcome for `Bun.Image` (measured, not quoted):

```
present: avif blob buffer bytes dataurl flip flop heic height jpeg metadata modulate
         placeholder png resize rotate toBase64 toBuffer webp width write
absent : composite  extend/pad  crop/extract  SVG input  text  ICO  alpha flattening
```

Three absences decided the architecture: no `composite` (mark over background), no `extend` (pad to a
square), no palette output (byte ceiling). And it only exists under Bun, which would have made the drift gate
runtime-dependent.

**Rule:** the probe output goes into the ADR verbatim. "We chose X because Y was missing Z" is only credible
with the list.

## 2. The four jobs, and what actually qualifies

### Job 1 — rasterise SVG with shaped text

| Candidate | Qualifies? | Reason |
|---|---|---|
| `@resvg/resvg-js` | **yes** | resvg + tiny-skia + HarfBuzz; embeds font files; in-process; deterministic; ~10 MB native binary |
| headless Chromium (`puppeteer`/`playwright`) | no | perfect text, but a browser process per image; ~300 MB; cold start seconds; unacceptable in a request path |
| `sharp` | no | rasterises SVG through librsvg (no reliable bidi/shaping control), and its strength is photo processing |
| `canvas` (node-canvas) | partial | Cairo/Pango shaping is good, but a native build, and text layout must be done by hand anyway |
| `satori` | no | JSX→SVG, but it lays text out itself and does **not** implement bidi: Arabic word order comes out wrong |
| `svg2png` / `svg-to-img` wrappers | no | thin wrappers over the above, same limits, less control |
| hand-rolled SVG text | no | shaping is the hard part; you would be writing a text engine |

### Job 2 — encode a palette PNG under a byte ceiling

| Candidate | Qualifies? | Reason |
|---|---|---|
| hand-written indexed encoder + median cut + Floyd–Steinberg | **yes** | ~150 lines on `node:zlib`; exact control of colour type, `tRNS`, dither, palette size |
| `sharp` | yes, but heavy | `.png({ palette: true, colours: 256, dither })` works; a native dep for one encode |
| `pngjs` | **no** | encodes truecolour only; `dePalette` is read-only (verified from its API) |
| `Bun.Image` | no | no palette output, and Node-hostile |
| `imagemin` + `pngquant-bin` | no | spawns a binary; not deterministic across platforms; build-time only |

### Job 3 — bidi and script runs

| Candidate | Qualifies? | Reason |
|---|---|---|
| `bidi-js` | **yes** | small, pure, UBA implementation: paragraph level, run resolution, reordering for single-line contexts |
| `bidi-js` used for *layout* | no | the renderer still emits logical order; the fix is one script run per line |
| `Intl.Segmenter` | partial | grapheme/word segmentation, not direction |
| hand-rolled direction detection | no | Unicode ranges are a starting point, not a bidi algorithm |

### Job 4 — ICO

No maintained library is worth a dependency for a 6-byte header plus a directory of PNGs. Write it
(`scripts/ico-writer.ts`): header, `count` directory entries (16 bytes each), then the PNG payloads. Browsers
accept PNG-compressed entries; BMP is legacy.

## 3. Decision rules

1. **Probe first, docs second.** A capability you have not observed is a capability you do not have.
2. **One job, one library.** Do not pick a platform because it could also do the other three jobs.
3. **Reject with a named missing primitive**, not with "it felt heavy". "No palette output" is a reason;
   "didn't like it" is not.
4. **Prefer the dependency you can run in every runtime the build touches.** A library that only exists in
   one runtime makes every gate conditional.
5. **Prefer a small dependency over a hand-rolled engine**, and a hand-rolled 150-line encoder over a 10 MB
   native binary — the line is "is the hard part already solved elsewhere?" Shaping: yes, use resvg. Byte
   layout of a PNG: no, write it.
6. **Pin exact versions.** `@resvg/resvg-js@2.6.2`, `bidi-js@1.1.0`. Rasteriser output changes between
   versions; a fidelity test on `^2` is a flaky test.
7. **Record `when_not` boundaries** for anything you adopt: when would the next person be wrong to use it?
   (e.g. "resvg is not a photo pipeline; use sharp if you need EXIF, CMYK, or colour management".)
8. **Count the install cost** honestly: native binaries, post-install downloads, and platform-specific
   builds all show up as CI failures on someone else's machine.

## 4. Dependency budget for this domain

The reference run added **two** runtime dependencies and **zero** build tooling:

```
@resvg/resvg-js@2.6.2     rasteriser (native, prebuilt for win/linux/mac)
bidi-js@1.1.0             bidi resolution
pngjs@7 + @types/pngjs    already present (decode + baseline comparison in tests)
```

Rejected and recorded: `sharp`, `puppeteer`/`playwright`, `satori`, `canvas`, `pngquant`, `imagemin`.
No Chromium anywhere. The whole pipeline runs in a plain Node/Bun process, which is what makes the drift gate
and the runtime route share one code path.

## 5. When to revisit

| Signal | Revisit |
|---|---|
| A real vector master appears | drop the trace, keep the pipeline |
| resvg adds full UBA | the one-script-per-line law can relax (it still should not: mixed lines read badly at 300 px) |
| Card artwork becomes photographic | the palette ladder may not hold; consider JPEG for those families |
| More than ~10 000 distinct cards/day | render off the request path into a queue + object store |
| A platform starts accepting SVG | still do not: raster is universally safe |

## 6. Library-selection checklist

- [ ] Capability probed at runtime; output quoted in the ADR
- [ ] Every rejected candidate has a named missing primitive
- [ ] The chosen library runs in **every** runtime the build uses
- [ ] Versions pinned exactly
- [ ] Native/binary install cost stated
- [ ] `when_not` boundary written down
- [ ] No second library doing the same job "just in case"
