# imgery — Media Loading & Optimization Research (largest chapter)

Research target: doctrine for AI coding agents deciding how a product loads, formats, delivers,
and defers media (images, posters, third-party embeds) on the web, with a short native section.

Method: WebSearch + WebFetch of web.dev / developer.chrome.com / MDN / caniuse / vendor docs /
practitioner write-ups. Every claim is tagged:

- `[VERIFIED-fetched]` — read from the fetched primary page this session (quoted or closely paraphrased).
- `[SEARCH-asserted]` — seen in search-result snippets/titles of the named URL, page body not fully read.
- `[REASONED]` — engineering inference from verified premises; arithmetic or doctrine, not a quoted rule.

Browser-support numbers reflect **caniuse data with StatCounter usage for October 2026** (fetched 2026‑11‑18).
Treat them as "late 2026 reality". Re-verify before pinning a doctrine version to them.

---

## 0. Headline conclusions (read first)

1. **Format doctrine 2026: AVIF as the default lossy photo format, WebP as the required fallback,
   JPEG/PNG as the last-resort fallback.** AVIF is at 96.71% global usage (Baseline "high" since
   2026‑07‑25), WebP at 97.32%. `[VERIFIED-fetched caniuse]`
2. **JPEG XL is not dead.** Chrome 155 shipped a Rust decoder (`jxl-rs`), Firefox 158 shipped it;
   caniuse reports 53.99% full + 15.26% partial = **69.25%** global — but Safari is still
   "partial" (stills only, no progressive decoding) and Edge is behind. It is a *progressive/HDR/
   lossless-first* niche format in 2026, not the default. `[VERIFIED-fetched caniuse + Chrome blog]`
3. **The LCP rule is absolute: never `loading="lazy"` the LCP image**, and give it
   `fetchpriority="high"`. Verified data: pages using lazy loading have a median p75 LCP of
   3,546 ms vs 2,922 ms without; the A/B fix (lazy only below the fold) *reversed* the regression
   while keeping 100% of the byte savings. `[VERIFIED-fetched web.dev]`
4. **Third-party embeds: facade by default.** A YouTube facade costs ~2 KB against a ~540 KB player;
   lazy-loading the iframe alone already saves ~500 KB; embed JS runs "over 100 KB, sometimes up to 2 MB".
   `[VERIFIED-fetched web.dev + developer.chrome.com]`
5. **Responsive-image failure mode is a spec fact, not folklore:** with `w` descriptors and no
   `sizes`, the browser assumes `sizes` = `100vw`; with `x` descriptors layout is ignored entirely.
   Both produce "2x raster for a 32 px icon". Use `w` + `sizes` (or `sizes="auto"` + `loading="lazy"`
   where supported). `[VERIFIED-fetched MDN + Next.js docs]`
6. **Space must be reserved.** `width`/`height` attributes (or CSS `aspect-ratio`) on every image and
   iframe; a lazy image with no dimensions is 0×0 until loaded, which can make the browser treat an
   entire gallery as in-viewport and load everything. `[VERIFIED-fetched web.dev + MDN]`
7. **Inlining (data: URIs) is a narrow tool.** It destroys independent caching, inherits the container's
   priority, and inflates bytes. Inline only what is needed for first render and used exactly once.
   `[VERIFIED-fetched perfplanet + web.dev]`
8. **Delivery: content-hashed URLs + `Cache-Control: public, max-age=31536000, immutable` for media;
   `no-cache` (+`private` if personalized) for documents.** The HTTP cache spec's own doc set recommends
   `immutable` precisely to stop reload revalidation. `[VERIFIED-fetched MDN]`
9. **Auto-format negotiation has a real hole:** Firefox only advertises AVIF/WebP for images loaded
   *inside a webpage*, so direct image URL loads get the original format; imgix also documents
   animated-GIF-with-transparency being mis-served as AVIF. `<picture>` in markup beats header
   sniffing when correctness matters. `[VERIFIED-fetched imgix]`
10. **YouTube thumbnails are technically fragile and legally undocumented for hotlinking.**
    `maxresdefault.jpg` frequently does not exist, 404s still return a valid JPEG body (so `onerror`
    does not fire), and only `hqdefault` is close to universal. Self-host or fetch server-side.
    `[VERIFIED-fetched lite-youtube-embed/youtube-thumbnail-urls.md]`

---

## 1. Format decision matrix

### 1.1 The matrix

| Format | Transparency | Animation | Lossy | Lossless | Progressive | 2026 browser reality | Use for |
|---|---|---|---|---|---|---|---|
| JPEG | no | no | yes | no | yes (PJPEG) | universal | photos if no modern format available |
| PNG | yes (alpha) | yes (APNG) | no | yes | no | universal | line art, screenshots, alpha where AVIF/WebP unavailable |
| WebP | yes (even lossy) | yes | yes | yes | yes (chroma/quality scaling) | **97.32%** (Chrome 32, Edge 18, Firefox 65, Safari 16, iOS 14) | the universal modern fallback |
| AVIF | yes | yes | yes | yes | yes (spatial + quality scalability) | **96.71%** (Chrome 85, Edge 121, Firefox 93, Safari 16.4) | default lossy photo + HDR/WCG |
| JPEG XL | yes | yes | yes | yes | yes (real progressive) | **53.99% + 15.26% partial = 69.25%**; Chrome 155+, Firefox 158+, Safari 17+ partial (stills, no progressive), Edge no | lossless-first, high-quality, progressive, edit-friendly archiving |
| SVG | yes | yes (SMIL/CSS) | n/a (lossy opt via svgo) | n/a | n/a | universal (as `<img>`; `<use>` cross-origin restricted) | icons, logos, diagrams, flat-color illustration |
| GIF | 1-bit alpha | yes | no | palette | no | universal | **delete it** → `<video>` or animated WebP/AVIF/APNG |
| `<video>` (MP4/H.264, WebM/VP9, AV1) | no (poster) | yes | yes | no | streaming | universal | every animated-GIF replacement |

Sources: web.dev *Choose the right image format* (feature table, "WebP and AVIF will generally provide
better compression than older formats, and should be used where possible. You can use WebP or AVIF images
along with a JPEG or PNG image as a fallback"), web.dev *Image performance* (lossy/lossless per format),
caniuse `avif`/`webp`/`jpegxl` pages (2026‑11 fetched). `[VERIFIED-fetched]`

### 1.2 The precedence questions web.dev gives (verbatim decision tree)

From https://web.dev/articles/choose-the-right-image-format:

- "The very first question you should ask yourself is whether an image is, in fact, required…
  If you can eliminate an image resource… then that is always the best optimization strategy."
  → Then: CSS effects/gradients/animations and web fonts are resolution-independent and
  "often at a fraction of the bytes required by an image file". `[VERIFIED-fetched]`
- "If you ever find yourself encoding text in an image asset, stop and reconsider." Text-in-image is
  not selectable/searchable/zoomable/accessible and "not friendly for high-DPI devices". `[VERIFIED-fetched]`
- Q1 "Do you need animation? Use `<video>` elements." GIF ≤256 colors and "significantly larger file sizes
  than `<video>` elements. APNG offers more colors than GIF, but is also significantly larger than video". `[VERIFIED-fetched]`
- Q2 "Do you need to preserve fine detail with highest resolution? Use PNG or lossless WebP."
  ("WebP has a lossless encoding mode that may be more efficient than PNG"; geometric content → convert to SVG). `[VERIFIED-fetched]`
- Q3 "Are you optimizing a photo, screenshot, or a similar image asset? Use JPEG, lossy WebP, or AVIF."
  ("Try several JPEG quality levels"; lossy modes may shift exact colors vs JPEG). `[VERIFIED-fetched]`
- WebView/native-app exception: "if you are using a WebView… you have full control of the client and
  can use WebP exclusively! Facebook and many others use WebP to deliver all of their images." `[VERIFIED-fetched]`

### 1.3 Numbers per format (measured, quotable)

AVIF
- ">50% savings vs JPEG" reported by web.dev and Netflix ("AVIF… tests have shown greater than 50%
  savings when compared to JPEG in some cases"). `[VERIFIED-fetched web.dev]`
- web.dev's own pair: **1120×840 AVIF at 18,769 bytes vs the same JPEG at 20,036 bytes** (i.e. only ~6%
  here — AVIF savings are content- and target-quality-dependent, "a statistical average across requests,
  not a per-image guarantee" per imgix). `[VERIFIED-fetched web.dev + imgix]`
- Recommended encoder settings (web.dev/avif): `avifenc --min 0 --max 63 -a end-usage=q -a cq-level=18
  -a tune=ssim`; add `--minalpha 0 --maxalpha 63` for alpha; `--jobs 8` → "speeds up AVIF encoding by
  roughly 5x"; speed default 6 = "a balance of encode speed, compression efficiency, and quality".
  libaom 2.0.0→3.1.0 gave "5x reduction in memory usage" and "6.5x reduction in CPU usage"
  (measured at speed=6, cq-level=18 on 8.1 MP images). `[VERIFIED-fetched]`
- Features beyond size: HDR + wide color gamut, film-grain synthesis, and two kinds of progressive
  decoding (spatial scalability and quality scalability). `[VERIFIED-fetched]`
- Encode cost reality (Next.js): "AVIF generally takes 50% longer to encode but it compresses 20% smaller
  compared to WebP." `[VERIFIED-fetched]`

WebP
- Lossy WebP is VP8-keyframe-based: luma blocks 16×16, chroma 8×8, 4×4 sub-blocks; unlike JPEG it applies
  **block prediction** and **adaptive block quantization** ("an image is broken into up to four visually
  similar segments, and compression parameters for those segments are tuned independently"). Practical
  consequence: smooth gradients in the background survive where JPEG block-artifacts show. `[VERIFIED-fetched web.dev/learn/images/webp]`
- Standard quality knob: "a single 'quality' value—expressed from 0–100, just like JPEG". Example
  invocation `cwebp -q 80 butterfly.jpg -o butterfly.webp` → 208,418 bytes for a 1676×1418 image. `[VERIFIED-fetched]`
- Lossy WebP still carries alpha ("supports alpha channel transparency even when using lossy
  compression—a feature the JPEG codec doesn't offer"). `[VERIFIED-fetched]`

JPEG
- 8×8 blocks, DCT, separate luma/chroma planes, chroma **subsampling**; quality is one integer 0–100 and
  tools disagree on its meaning ("not every tool will interpret a value of '75' the same way"). `[VERIFIED-fetched]`
- Squoosh data point quoted by web.dev: "with the 'quality' set to 60, the file size is reduced by 79%". `[VERIFIED-fetched]`
- Progressive JPEG: baseline renders top-to-bottom; PJPEG renders full-size scans, "the entire image appears
  immediately, albeit blurry"; "except for the smallest images, encoding an image as PJPEG almost always means
  a smaller file size compared to a baseline JPEG"; trade-off is "a little more strain on the browser"
  during decode, "very minor… except for with severely underpowered devices" → web.dev's verdict:
  "progressive is a sensible default approach whenever encoding an image as JPEG." `[VERIFIED-fetched]`
  Note: PJPEG's perceptual benefit is *not* an LCP benefit — LCP is painted at final render of the element. `[REASONED]`
- Practitioner tuning guidance: "it's almost always a safe bet to nudge JPEG compression just a little lower
  than you think might be noticeable—especially when that image is going to be displayed *smaller* than its
  intrinsic size." `[VERIFIED-fetched]`

JPEG XL
- caniuse description: "generally has better compression than WebP, JPEG, PNG and GIF… competes with AVIF
  which has similar compression quality but fewer features overall." Baseline status = **limited**. `[VERIFIED-fetched]`
- Support reality: Chrome 91–109 flag → **110–144 removed** → 145–154 flag → **155–160 supported**;
  Firefox 90–157 disabled-by-default (152 opt-in via Firefox Labs) → **158+ supported**; Edge 156 = not supported;
  Safari 17–TP = **partial** ("Supports still images. Animated image sequences are not supported" +
  "Partial support refers to not supporting progressive decoding"); Opera 139 supported. `[VERIFIED-fetched caniuse]`
- Chrome blog 155 beta (2026‑09‑16): "Adds support for decoding JPEG XL (`image/jxl`) in Blink using jxl-rs,
  a memory-safe pure Rust decoder… offers progressive decoding…, support for wide color gamut, HDR, and high
  bit depth, and support for animation." `[VERIFIED-fetched]`
- Compression claims from vendors/research (not fetched, treat as secondary): Cloudinary "up to 55% smaller
  than JPEG… up to 25% smaller than AVIF"; Google's own AVIF-vs-JXL study reported gains of "about 20 to 25%
  vs WebP and 30 to 35% vs MozJPEG"; practitioner reviews put AVIF ahead for low/mid-quality photos and
  JXL ahead at high quality, flat graphics and lossless. `[SEARCH-asserted]`
- **Doctrine:** treat JXL as opt-in for (a) lossless/ archival-grade assets, (b) progressive-first-paint
  experiences, (c) WebView/owned clients. Serve via `<picture>` *before* AVIF only if you can measure it;
  otherwise keep AVIF/WebP/JPEG chain. `[REASONED]`

Animated replacements (GIF-killers)
- web.dev measured example: **GIF 3.7 MB → MP4 (H.264, `-crf 25`) 551 KB → WebM (VP9, `-crf 41`) 341 KB**;
  a DevTools screenshot in the same article shows a 13.7 MB GIF. `[VERIFIED-fetched]`
- Markup equivalent of a GIF: `<video autoplay loop muted playsinline>` with `<source>` per codec.
  "Browsers don't speculate about which `<source>` is optimal, so the order of `<source>`'s matters" —
  put WebM first if you want WebM used. `[VERIFIED-fetched]`
- LCP interaction: "`<video>` elements without a `poster` image are not LCP candidates" and you should *not*
  add `poster` for GIF replacements "because that image will go unused"; moving the LCP to another element
  "will likely even improve the site's LCP". `[VERIFIED-fetched]`
- Format chain for the loop-video: `<source type="video/mp4">` + `<source type="video/webm">` (VP9);
  AV1 is the cheapest bytes but is not universally decodable in browsers/OS combos → keep H.264 as the
  fallback. `[REASONED from web.dev guidance]`
- Animated WebP/AVIF: both formats technically support animation (caniuse: AVIF animation *not* supported in
  Safari 16.1–16.3, and Firefox 111–112 gated sequences behind `image.avif.sequence.enabled`); imgix warns
  that `auto=format` on transparent animated GIFs produces broken AVIF. So for animated UI assets in 2026 the
  safe ordering is `<video>` first, animated WebP second, animated AVIF only inside `<picture>` with fallbacks. `[VERIFIED-fetched caniuse + imgix]`

### 1.4 Quality defaults practitioners actually ship

| Knob | Observed default | Source |
|---|---|---|
| JPEG/WebP quality | 0–100 scale; 60 → −79% size (Squoosh); web.dev says experiment, no universal value | `[VERIFIED-fetched]` |
| AVIF | `cq-level=18`, `tune=ssim`, min 0/max 63, speed 6 | `[VERIFIED-fetched]` |
| imgix `auto=compress` | "setting the quality standard (`q`) to **45**", strip metadata, transparency-aware format pick | `[VERIFIED-fetched]` |
| Next.js Image | `quality` default **75**, and since v16 `qualities` allowlist defaults to `[75]` | `[VERIFIED-fetched]` |
| Cloudinary | `q_auto` perceptual quality tiers (default `good`) | `[SEARCH-asserted]` |
| Rule for agents | pick *one* pipeline default (AVIF q≈50 / WebP q≈75 / JPEG q≈70–75 progressive), then tune per asset class; never let per-page ad-hoc quality sprawl | `[REASONED]` |

### 1.5 `prefers-reduced-data` / `Save-Data` (the "reduced data" hook)

- `Save-Data` request header: "indicates the client's preference for reduced data usage… A value of `On`
  indicates explicit user opt-in into a reduced data usage mode… allows them to deliver alternative content
  to reduce the data downloaded such as smaller image and video resources". It is a **low-entropy client
  hint**, so it may be sent without `Accept-CH`, and "should be used to reduce data sent to the client
  irrespective of the values of other client hints… like `Downlink` and `RTT`". MDN marks the header
  `status: experimental`. Any variant served on it **must** declare `Vary: … Save-Data`, and MDN's own
  example pairs it with `Cache-Control: public, max-age=31536000`. `[VERIFIED-fetched MDN]`
- CSS `prefers-reduced-data`: MDN's Save-Data page links it as `{{experimental_inline}}`. The media feature
  has **not** reached cross-browser availability; do not write product logic that depends on it. Use
  `Save-Data` server-side (or the CDN's auto mode) and `prefers-reduced-motion` for motion, not data. `[VERIFIED-fetched MDN; caniuse page not fetched]`
- web.dev lists exactly the signals an image CDN "auto" mode may use: client hints (viewport width, DPR,
  image width), `Save-Data`, `User-Agent`, and the Network Information API. `[VERIFIED-fetched web.dev + imgix]`
- Related cost lever: `<link rel="prefetch">`/prerender/speculation-rules and service-worker precaching
  should be skipped when `Save-Data` is on ("avoid prefetching altogether if the user has enabled the
  `Save-Data` signal"). `[VERIFIED-fetched web.dev]`

---

## 2. Responsive & art-directed images

### 2.1 Mechanics as specified (not folklore)

From MDN `<img>`/`<picture>`/responsive guide (fetched raw markdown):

- `srcset` candidates carry **either** a width descriptor ("A positive integer directly followed by `w`.
  It _must_ match the intrinsic width of the referenced image") **or** a pixel density descriptor;
  "**It is incorrect to mix width descriptors and pixel density descriptors in the same `srcset` attribute.**
  Duplicate descriptors… are also invalid." Missing descriptor ⇒ implied `1x`. `[VERIFIED-fetched]`
- "When the `<img>` element's `srcset` uses `x` descriptors, browsers also consider the URL in the `src`
  attribute… On the other hand, **if the `srcset` attribute uses width descriptors, `src` is not
  considered**, and the `sizes` attribute is used instead." → `src` remains only a legacy fallback. `[VERIFIED-fetched]`
- `sizes`: "One or more values separated by commas… **The spec requires that the `sizes` attribute only be
  present when `srcset` uses width descriptors.**" Values are non-negative CSS lengths (math functions
  allowed) with viewport-relative units resolved against the **root**, "**Percentage values are not allowed.
  If the `sizes` attribute is not provided, it has a default value of `100vw`** (the viewport width)." `[VERIFIED-fetched]`
- Selection algorithm (MDN guide): browser looks at "screen size, pixel density, zoom level, screen
  orientation, and network speed", takes the first true `sizes` condition, then "**the first image that is
  bigger than the chosen slot size** and scale it down to fit". `[VERIFIED-fetched]`
- Discretion clause: "**The user agent selects any of the available sources at its discretion.** This
  provides them with significant leeway to tailor their selection based on things like user preferences or
  bandwidth conditions." ⇒ you cannot force a specific file; treat `srcset` as a hint set. `[VERIFIED-fetched]`
- `sizes="auto"` (newer): "The `auto` keyword indicates that the browser should use the expected layout width
  of the element to select the image… **This is only valid when combined with `loading="lazy"`**". Fallback
  order if it cannot resolve: source sizes → `width`/`height` attributes → **UA default intrinsic size 300×150**.
  Compatible syntax: `sizes="auto, (max-width: 30em) 100vw, …"`. `[VERIFIED-fetched]`
- `<picture>`: browser "examines each `<source>`'s `srcset`, `media`, and `type` attributes"; `<source>`
  with an unsupported `type` is skipped; `<img>` is mandatory ("In all cases, you must provide an `<img>`
  element, with `src` and `alt`, right before `</picture>`, otherwise no images will appear"). web.dev adds
  the semantics: `srcset` = *hints*, `media` on `<source>` = "**a command** to be followed by the browser". `[VERIFIED-fetched]`
- **DPR rule from the spec docs, not from blogs:** MDN `<picture>` — "If providing higher-density versions of
  an image for high-DPI (Retina) display, use `srcset` on the `<img>` element instead [of `<picture>`+media].
  This lets browsers opt for lower-density versions in data-saving modes, and you don't have to write explicit
  `media` conditions." `[VERIFIED-fetched]`
- Why JS/CSS can't do it: "When the browser starts to load a page, it starts to download (preload) any images
  before the main parser has started to load and interpret the page's CSS and JavaScript… By then, the original
  image would already have been loaded, and you would load the small image as well, which is even worse." `[VERIFIED-fetched]`

### 2.2 The 2x-raster pitfall (the user's "2x for small icons")

Mechanism, assembled from verified premises:

1. `srcset="icon-32.png, icon-64.png 2x"` with **no `sizes`** → descriptor is `x`, so DPR alone selects the
   64 px asset on any DPR≥2 device, irrespective of the rendered CSS size, and `src` is also treated as 1x. `[VERIFIED-fetched MDN]`
2. `srcset="… 32w, … 64w"` with **no `sizes`** → `sizes` defaults to `100vw`, so slot = viewport width × DPR;
   for a 32 px icon on a 1200 px viewport the browser legitimately requests the largest candidate. Next.js
   states this directly: "**If `sizes` is missing, the browser assumes the image will be as wide as the
   viewport (`100vw`). This can cause unnecessarily large images to be downloaded.**" `[VERIFIED-fetched]`
3. web.dev's DPR arithmetic explains the cost: doubling device resolution "**quadruples** the number of
   required pixels" (100×100 CSS px: 40,000 B at 1x, 160,000 B at 2x, 360,000 B at 3x uncompressed), while
   "in most cases, the human eye is unable to benefit from a DPR of 3". `[VERIFIED-fetched]`

Doctrine for agents:
- Prefer `w` descriptors + accurate `sizes`; never ship `w` without `sizes` unless the image really is 100vw.
- Use `x` descriptors only for genuinely fixed-size assets (icons, avatars at a known box), and cap at 2x.
- Icons/logos/flat-color UI: use SVG (resolution-independent), not density buckets.
- Where the framework can measure layout, use `sizes="auto"` with `loading="lazy"` and keep a media-condition
  fallback list after `auto` for older engines. `[REASONED from verified MDN text]`

### 2.3 Format + art-direction chains

```html
<picture>
  <source type="image/jxl"    srcset="hero.jxl"    sizes="(max-width:600px) 100vw, 600px" srcset="...">
  <source type="image/avif"   srcset="hero-480.avif 480w, hero-960.avif 960w" sizes="(max-width:600px) 100vw, 960px">
  <source type="image/webp"   srcset="hero-480.webp 480w, hero-960.webp 960w" sizes="(max-width:600px) 100vw, 960px">
  <source srcset="hero-480.jpg 480w, hero-960.jpg 960w" media="(max-width: 600px)">
  <img src="hero-960.jpg" alt="…" width="960" height="540" fetchpriority="high" decoding="async">
</picture>
```
Ordering rules: most-preferred format first (AVIF before WebP before JPEG — web.dev's own snippet),
art-direction `<source media=…>` branches per breakpoint, `alt`/`width`/`height` live on `<img>` and
"are used regardless of which `<source>` is selected". `[VERIFIED-fetched]`
`width`/`height` **can now be set on `<source>`** (Chrome, Firefox, Safari) for art-directed aspect-ratio
changes — web.dev shows the exact markup. `[VERIFIED-fetched web.dev/optimize-cls]`

Server-side alternative: `Accept`-header negotiation (`image/avif` → `image/webp` → `image/jpeg`), with the
warning that "The `Accept` request header usually only communicates what image types are supported in requests
for **HTML** resources" and that any such variance needs `Vary` for shared caches/CDNs. Firefox's real
behaviour (only advertising AVIF/WebP for in-page image loads) confirms the caveat. `[VERIFIED-fetched web.dev + imgix]`

### 2.4 Variant-count economics

web.dev *Image performance*, "Manage complexity": "every additional image variant comes at a cost and makes
less efficient use of the browser cache. With only one variant, every user receives the same image, so it can be
cached very efficiently… if there are many variations, each variant requires another cache entry. Server costs can
increase and may degrade performance if the variant's cache entry has expired… the size of your HTML document grows
with each variation. You could find yourself shipping multiple kilobytes of HTML for each image." Their heuristic:
"a full-width hero image may require more variants than thumbnail images on an ecommerce product listing page." `[VERIFIED-fetched]`

Practical budget `[REASONED]`: 3–5 width steps per breakpoint class for hero-scale images (e.g. 480/768/1080/1600),
2 steps for mid-size cards, 1–2 for thumbnails; formats ×2 (AVIF+WebP) with a JPEG/PNG `<img>` fallback — not a
cross-product of every size × every format × every DPR.

### 2.5 Image CDN / framework conventions (URL contracts to copy)

| Service | Convention | Verified behaviour |
|---|---|---|
| web.dev's framing | "Switching your website to an image CDN can yield a **40–80% savings** in image file size" vs build-time scripts; URL carries origin, image, **security key**, transformations | `[VERIFIED-fetched]` |
| imgix | `?auto=format,compress&fit=crop&w=…` | `auto=format` = "automatic content negotiation… headers, user agents, and image analytics", serves AVIF → WebP → JPG/PNG; `auto=compress` sets q=45 and strips metadata; `fm` becomes only the non-modern fallback once `auto=format` is on; `fm=mp4`/`fm=pdf` take precedence | `[VERIFIED-fetched]` |
| Cloudinary | `f_auto`, `q_auto`, `fetch_format=auto`; transparency caveat: if `f_auto` can't use WebP/AVIF the transparent image falls back to PNG | `[SEARCH-asserted]` |
| Cloudflare Images/CDN | `/cdn-cgi/image/width=…,format=auto/…` path-style transforms; source origins configurable | `[SEARCH-asserted]` |
| Next.js `next/image` | `/_next/image?url=%2Fprofile.jpg&w=640&q=75` (x-descriptor srcset when no `sizes`); `deviceSizes [640,750,828,1080,1200,1920,2048,3840]`, `imageSizes [32,48,64,96,128,256,384]`; `formats: ['image/webp']` default, `['image/avif','image/webp']` for AVIF-preferred; `qualities: [75]` allowlist since v16 (out-of-list quality coerced to nearest, direct hit → 400); `minimumCacheTTL: 14400` (4 h) default; disk cache default = 50% of free space, LRU-evicted (`maximumDiskCacheSize` since 16.1.7); `maximumResponseBody: 50 MB`; `unoptimized` recommended for "<1KB, SVG, GIF"; SVG never optimized by default (`dangerouslyAllowSVG:false`) and should ship `contentDispositionType:'attachment'` + CSP if enabled; `priority` **deprecated in v16** in favour of `preload` + `loading="eager"` + `fetchPriority`; custom `loader`/`loaderFile` for third-party CDNs | `[VERIFIED-fetched]` |
| Thumbor / Imaginary / Imagor | self-managed image CDNs (Thumbor used by Wikipedia, Square, 99designs) | `[VERIFIED-fetched web.dev]` |

Two LCP-relevant CDN facts: (a) a third-party image host adds a connection, so "try to use an image CDN that
proxies through the primary origin"; (b) if the LCP image isn't discoverable in HTML, `rel=preload` +
`fetchpriority=high` + `preconnect` are the mitigations. `[VERIFIED-fetched web.dev/image-cdns + optimize-lcp]`

### 2.6 Placeholders: LQIP, blur-up, dominant colour

- Next.js contract `[VERIFIED-fetched]`: `placeholder="blur"` + `blurDataURL` (a data URL),
  "The image is automatically enlarged and blurred, so a very small image (**10px or less**) is recommended";
  auto-generated for static `jpg/png/webp/avif` imports (not animated); manual for remote/dynamic via tools
  (png-pixel.com, Plaiceholder); explicit warning "**A large blurDataURL may hurt performance**."
  `placeholder` also accepts a raw `data:image/...` (shimmer/colour tricks).
- web.dev's own LCP guidance sanctions inlining *only* small things: "if your LCP resource is small, it may make
  sense to inline the resources as a data URL, which will also eliminate the additional network request. However,
  using data URLs comes with caveats because then the resources cannot be cached and in some cases can lead to
  longer render delays because of the additional decode cost." `[VERIFIED-fetched]`
- Practitioner taxonomy of LQIP types (blur / colour / trace / hash encodings such as blurhash) and their
  trade-offs: responsive-image.dev docs, Mux's "A clear look at blurry image placeholders on the web",
  `vite-plugin-lqip` ("'Blur Up' was previously great, but lqip-modern seems to deliver identical quality in
  much smaller sizes"). `[SEARCH-asserted]`
- Dominant-colour backgrounds: derive a per-asset average/dominant colour at build or transform time and store
  it beside the asset (imgix exposes a Color Palette API; `sharp.stats()` gives channel means; Cloudinary exposes
  `x_`/`e_outline`-style palette params). Use it as CSS `background-color` on the reserved box so the placeholder
  phase is colour-correct rather than grey. `[VERIFIED-fetched existence of imgix palette API; REASONED for the pattern]`
- Firefox 67+ shows a **white** background while an image loads and Safari 15–16.3 shows a **gray border** on
  `loading="lazy"` images — both documented by Next.js as "known browser bugs" with fixes (`clip-path: inset(0.6px)`
  under an `@supports` guard, `placeholder`, eager loading above the fold, or AVIF). Any blur-up implementation
  should be tested against these. `[VERIFIED-fetched]`

---

## 3. Loading strategy

### 3.1 `loading` semantics

`[VERIFIED-fetched web.dev/articles/browser-level-image-lazy-loading + MDN img]`

- Values: `lazy` = "defer loading… until it reaches a calculated distance from the viewport";
  `eager` = **default** ("the image is loaded regardless of where it's located"), and setting it explicitly is
  useful when tooling auto-inserts `lazy`.
- Support: Chrome 77, Edge 79, Firefox 121 (image lazy in the web.dev table; `<iframe loading=lazy>` earlier),
  Safari 15.4/16.4. web.dev: "Browser-level lazy loading is well supported… no need for extra dependencies on JavaScript."
- Hard rule: "**Don't lazy-load images that are likely to be in-viewport when the page loads, especially LCP images.**"
  and "Always eager-load images visible in the first viewport".
- Mechanism of the harm: "The browser can't lazy-load an image until it knows where the image should be on the page,
  which causes them to load more slowly" — the request waits for CSS download/parse/layout instead of being found by
  the preload scanner. web.dev's lazy-load module: a lazy `<img>` in the viewport "is only requested *after* all CSS is
  downloaded, parsed, and applied". `[VERIFIED-fetched]`
- Lazy ≠ priority: "`loading` attribute does not affect the image's network priority";
  `loading="lazy" + fetchpriority="high"` is still delayed off-screen, then fetched high. `[VERIFIED-fetched]`
- `loading` does not apply to CSS `background-image` (needs JS or `content-visibility`). `[VERIFIED-fetched]`
- `<picture>`: put `loading` on the `<img>`, not the `<picture>` element. `[VERIFIED-fetched]`
- Non-obvious spec facts: lazy loading "is only deferred when JavaScript is enabled" (anti-tracking rationale);
  lazy images "will never be loaded if they do not intersect a visible part of an element, even if loading them would
  change that, because unloaded images have a `width` and `height` of `0`"; in-viewport lazy images may still be
  unloaded when `Window.load` fires; `display:none` images (self or ancestor) are not fetched in Chrome/Safari/Firefox,
  but `opacity:0` images are. `[VERIFIED-fetched MDN + web.dev]`
- Chrome 121 changed carousels: horizontally-offscreen images now use the same thresholds as vertical,
  "so images will be loaded before they [are] visible… less likely to be noticeable… at the cost of more downloads". `[VERIFIED-fetched]`
- Lite mode / `loading="auto"` are deprecated; "there are no plans to provide automatic lazy-load of images in Chrome". `[VERIFIED-fetched]`

### 3.2 Distance-from-viewport thresholds

- Chromium (July 2020 change, still the documented numbers): "On fast connections (4G), we reduced Chrome's
  distance-from-viewport thresholds from **3000px to 1250px** and on slower connections (3G or lower), changed the
  threshold from **4000px to 2500px**." Values are "hardcoded and can't be changed through the API", and vary by
  resource type + effective connection type (source cited: `third_party/blink/.../settings.json5`). `[VERIFIED-fetched]`
- Effectiveness: "on 4G, **97.5%** of lazy-loaded images were fully loaded within 10ms of becoming visible. Even on
  slow 2G networks, **92.6%**…". `[VERIFIED-fetched]`
- Safari: practitioner measurement says Safari grants "a full viewport in every direction" for images and does not
  load lazy iframes until on screen. Treat cross-browser thresholds as non-portable. `[SEARCH-asserted calibreapp]`
- Feature-detect before relying on it: `if ('loading' in HTMLImageElement.prototype) { … } else { /* polyfill/lazysizes */ }`. `[VERIFIED-fetched]`

### 3.3 `fetchpriority`

`[VERIFIED-fetched web.dev/articles/fetch-priority + MDN fetchpriority]`

- Attribute values `high` / `low` / `auto` (default `auto`), applies to `img`, `link`, `script` (+ SVG counterpart);
  JS side is `fetch(url, {priority})`. "The attribute should be used sparingly, as excessive or incorrect
  prioritization can degrade performance"; it is "a hint, not a directive" and sets **relative** priority.
- Support: Chrome/Edge 102, Firefox 132, Safari 17.2.
- Chrome's internal ordering (verified table): images start at **Low**; at layout, in-viewport images are boosted to
  **High**; "As of Chrome 117, the **first 5 large images** (> 10,000 px²) are set to Medium" and two can be fetched
  in the initial "tight mode". "By tagging important images in markup using `fetchpriority="high"`, they can start
  at High immediately and load much faster."
- Measured wins: Google Flights LCP **2.6 s → 1.9 s** with `fetchpriority=high` on the hero; Oodle carousel
  (high on the first slide only, low on the rest) "decreased page load time by 2 seconds".
- Correct combos: CSS-background LCP images still need `<link rel="preload" as="image" fetchpriority="high">`
  (preload = mandatory fetch, priority = ordering); `fetchpriority="low"` is the right tool for carousel slides that
  are "close enough" to the viewport to otherwise load even with `loading=lazy`.
- Limits: benefit is largest under bandwidth contention (HTTP/1.x or low-bandwidth HTTP/2/3), and "CDNs don't
  implement HTTP/2 prioritization uniformly", so test rather than assume. `[VERIFIED-fetched]`

### 3.4 `decoding`

- `sync` / `async` / `auto` (default). MDN: "in practice, `async` means that the next paint does not wait for the
  image to decode"; effects are "often difficult to perceive" for static `<img>`s but more noticeable for
  dynamically inserted images; web.dev: "The effects of `decoding` and `decode()` may only be noticeable on very
  large, high-resolution images." Next.js ships `decoding="async"` as its default. `[VERIFIED-fetched]`
- Doctrine: `decoding="async"` on non-LCP imagery, leave `auto` (or `sync`) on the LCP hero so it does not arrive
  in a separate paint from its container. `[REASONED]`

### 3.5 CLS interaction (mandatory reserve)

`[VERIFIED-fetched web.dev/articles/optimize-cls]`

- Target: "**sites should strive to have a CLS of 0.1 or less** for at least 75% of page visits" (poor > 0.25).
- "Images without dimensions" is listed as the **first** common cause. "Always include `width` and `height` size
  attributes on your images and video elements. Alternatively, reserve the required space with CSS `aspect-ratio`."
- Mechanism: browsers compute a **default aspect ratio** from the attributes *before* the image loads
  (Chrome shows `aspect-ratio: auto 640 / 360`; Firefox uses it without displaying it). The `auto` keyword means the
  loaded image's real ratio wins afterwards — "If the image dimensions are different, this still causes some layout
  shift after the image loads", but far less than the "0x0 default size of an image with no dimensions".
- Responsive images: "each image should use the same aspect ratio" across `srcset` candidates so the attributes stay
  truthful; art-directed crops → put `width`/`height` on `<source>` too.
- Lazy + unsized is the worst case (see 3.1: unloaded lazy images are 0×0).
- 500 ms grace: shifts "within 500 milliseconds" of user input are excluded — reserve space *before* that window if
  the content needs a network fetch. `[VERIFIED-fetched]`

### 3.6 Intrinsic-size defaults per format (what the browser reserves with nothing specified)

- `<img>` with no attributes/`sizes="auto"` fallback: **300 × 150 px** UA default. `[VERIFIED-fetched MDN]`
- Image without `width`/`height` before load: effectively 0×0 for lazy candidates; unsized eager images reserve
  nothing until headers arrive. `[VERIFIED-fetched MDN/web.dev]`
- SVG with no `width`/`height` on the root: "**SVG images… have no intrinsic dimensions if their root `<svg>`
  element doesn't have a `width` or `height` set on it**" → must give `viewBox` + CSS `aspect-ratio` or the layout
  jumps. `[VERIFIED-fetched MDN img styling section]`
- Animated GIF/video: video without `poster` is not an LCP candidate; iframes need explicit `width`/`height` and
  Chrome shows a placeholder for lazy iframes. `[VERIFIED-fetched]`

---

## 4. The third-party deferral doctrine (the user's YouTube-facade observation)

The observation — *"YouTube embed icons are deferred, not loaded at first render, which improves page response"* —
is the **facade / import-on-interaction** pattern, and it is documented, tool-enforced, and quantified.

### 4.1 Why deferring a YouTube embed helps (the cost model)

1. **JS payload + main thread.** "Many popular embeds include over 100 KB of JavaScript, sometimes even going up to
   2 MB. They take more time to load and keep the main thread busy when executing." Third-party scripts "can delay
   rendering… If a third party has server issues and fails to deliver a resource, rendering is blocked until the
   request times out, which can be anywhere from **10 to 80 seconds**." `[VERIFIED-fetched web.dev]`
2. **The iframe is a whole document.** "an `<iframe>` is a completely separate HTML document with its own
   subresources. While `<iframe>` elements can be run in a separate process, it's not uncommon for them to share a
   process with other threads, which can create conditions where pages become less responsive to user input" →
   lazy-loading iframes improves **INP during startup**, not just LCP. `[VERIFIED-fetched web.dev learn module]`
3. **Measured byte savings.** "Lazy loading the YouTube embed can save approximately **500 KB** on the initial page
   load"; "lazy loading a YouTube video's embed saves more than **500 KiB**… while lazy loading the Facebook Like
   button plugin saves more than **200 KiB**—most of which is JavaScript"; Instagram embeds "can be over 100 KB gzipped". `[VERIFIED-fetched]`
4. **Connection count / origins.** Third-party origins cost DNS + TCP + TLS before any byte: "Setting up connections
   takes time…"; preconnect "can save **100–500 ms**" but "the browser closes any connection that isn't used within
   10 seconds", so preconnect only to domains you will certainly use. `[VERIFIED-fetched]`
5. **Privacy/cookies.** The embed sets cookies and reports viewing behaviour; see 4.4.
6. **The payoff asymmetry.** "if the user never plays the video, the resources required to deliver it are never
   downloaded. This is a good pattern, as it ensures the user only downloads what they *actually* want to." `[VERIFIED-fetched]`

### 4.2 Facade mechanics (canonical pattern)

Definition: "**A facade is a static element that looks similar to the embedded third-party, but is not functional
and therefore much less taxing on the page load.**" Lighthouse's worked example: **facade ≈ 3 KB vs player ≈ 540 KB.**
Interaction ladder (identical in web.dev and the Lighthouse doc): *on load* render the facade; *on mouseover*
`preconnect` to the provider's origins; *on click* replace the facade with the real iframe/API. `[VERIFIED-fetched]`

Reference implementations (both fetched):

| | `paulirish/lite-youtube-embed` | `justinribeiro/lite-youtube` |
|---|---|---|
| Claimed speed-up | "This custom element renders just like the real thing but **approximately 224× faster**" | — |
| Weight | small CSS+JS pair | **2.2 KB min+gzip, 1.7 KB min+br** |
| Privacy default | "the default embed uses **youtube-nocookie.com**. On browsers that need the YouTube IFrame Player API, the API script also loads from youtube.com" | `nocookie` attr (default off, uses youtube.com) |
| Poster | `hqdefault.jpg` from `i.ytimg.com` set as inline `background-image`, custom poster possible; test page `poster-image-availability.html` | "Loads placeholder image as **WebP with a Jpeg fallback**"; `posterquality` ∈ `maxresdefault|sddefault|mqdefault|hqdefault`, default `hqdefault`; `posterloading` default `lazy` |
| Progressive enhancement | recommended: static `<lite-youtube style="background-image:url(...)">` + `<a class="lyt-playbtn">` in light DOM so it works before JS runs | fallback `<a>` slot; **`noscript` SEO injector** (v1.7, disable via `disablenoscript`) |
| Lazy on scroll | — | `autoload` = IntersectionObserver loads the iframe when scrolled into view; `autopause` pauses when scrolled out |
| API access | `js-api` attr → `await el.getYTPlayer()` → IFrame Player API (`player.seekTo(15)`) | `liteYoutubeIframeLoaded` event; `params` passes player query params |
| Known cost | iOS/iPadOS Safari blocks audible playback when the iframe is created *after* a tap, so the component "automatically prepares the hidden iframe and IFrame Player API ahead of time on iPhone and iPad Safari (**trading off some of its usual loading and privacy benefits** on those devices)" | `autoplay` "generally does not work" because of the click-to-load design |
| A11y | `playlabel` / title, keyboard-focusable button | `videotitle`, `videoplay` (localised), keyboard accessible, CSP `nonce` support |

Other facades named by Google: `luwes/lite-vimeo-embed`, `slightlyoff/lite-vimeo`, `Daugilas/lazyYT`,
`karim-mamdouh/ngx-lite-video`, `calibreapp/react-live-chat-loader` (chat), `vb/lazyframe` (generic lazy iframe).
The Lighthouse audit that flagged non-facaded embeds **was removed as of Lighthouse 13** — the doctrine survives, the
automated check does not. `[VERIFIED-fetched developer.chrome.com]`

Trade-offs Google states for facades: facades lose live functionality ("the Drift Live Chat bubble has a badge
indicating the number of new messages… appears… after the browser fires `requestIdleCallback`. For videos, autoplay may
not work consistently if they're loaded lazily"). web.dev adds an SEO fence: "It's best to use the techniques described
in this post to load only offscreen or non-primary page content. This ensures that all the critical content gets indexed
by search engines." `[VERIFIED-fetched]`

### 4.3 When a facade is *required* vs when a direct load is fine

Facade required (all three true) `[REASONED from verified criteria in web.dev's quiz text — "resources… are not only
substantial, but there is a decent probability that not all users may interact with them" + the docs above]`:
- the embed is **not** the primary content of the page, **and**
- the embed pulls >100 KB of JS or its own subresource tree, **and**
- the user must interact for it to be useful (video, map, chat, social post, reviews).

Direct `<iframe>` (with `loading="lazy"` + `width`/`height`) is fine when:
- the video *is* the page's purpose and is in/above the first viewport (a facade would delay the real LCP/INP target),
- autoplay of a muted looping clip is required (facades break autoplay),
- you must guarantee no-JS operability or avoid web-component support gaps,
- the embed is tiny (<100 KB) and privacy-consented.

Alternatives short of a facade, in cost order `[VERIFIED-fetched web.dev/embed-best-practices]`:
`loading="lazy"` on the iframe (≈500 KB saved) → `defer`/`async` script ordering after first-party tags →
static image in place of a map ("DevTools → Capture node screenshot", convert to WebP) → **dynamic** image facade via
Maps Static API / tweet-screenshot APIs → plain link with `target="_blank"` → removal.
Facebook plugins expose `data-lazy="true"` which just sets `loading="lazy"` internally.

### 4.4 Privacy-gated embeds: `youtube-nocookie.com` and consent

Verbatim from YouTube Help (answer 171780, fetched): `[VERIFIED-fetched]`
- "The Privacy Enhanced Mode of the YouTube embedded player **prevents the use of views of embedded YouTube content
  from influencing the viewer's browsing experience on YouTube.** This means that the view of a video shown in the
  Privacy Enhanced Mode… will not be used to personalize the YouTube browsing experience, either within your Privacy
  Enhanced Mode embedded player or in the viewer's subsequent YouTube viewing experience."
- "If ads are served on a video shown in the Privacy Enhanced Mode of the embedded player, those ads will likewise be
  non-personalized."
- Enable: "Change the domain for the embed URL in your HTML from `https://www.youtube.com` to
  `https://www.youtube-nocookie.com`." Network admins "will need to add youtube-nocookie.com to the firewall allowlist."
  "Privacy Enhanced Mode is available only for embedded players on **websites**" (apps → WebView).
- Compliance caveat from the same page: "If your website or app is child directed, you must self-designate… **even if
  you embed YouTube videos with the Privacy Enhanced Mode player**."
- Important nuance practitioners flag: nocookie ≠ no cookies at all, and under GDPR/ePrivacy an embed that can set
  non-essential cookies or localStorage still needs consent first. Two consent vendors state exactly this. `[SEARCH-asserted consently.net, infotrust.com; REASONED conclusion]`
- Doctrine: **CMP-gate the facade's second step.** Render the poster facade unconditionally (it only touches your own
  CDN), and only swap in `youtube-nocookie.com/embed/…` after consent; where consent is refused, fall back to a plain
  `youtube.com/watch?v=…` link. lite-youtube's `noscript`/light-DOM fallback link makes this implementable without JS. `[REASONED from verified component behaviour]`

### 4.5 Thumbnails: hotlink vs self-host (the `vi/<id>/hqdefault.jpg` pattern)

Facts from `paulirish/lite-youtube-embed/youtube-thumbnail-urls.md` `[VERIFIED-fetched]`:
- Resolutions: `maxresdefault` **1280px**, `sddefault` **640px**, `hqdefault` **480px**, `mqdefault` **320px**,
  `default` **120px**.
- "not every resolution thumbnail is available for every video" — e.g. rickroll `lXMskKTw3Bc` has no
  `maxresdefault`, `lQKdEdzHnfU` has no `sddefault`; "(In many, but not all, cases, the deciding factor of having an
  sddefault is being published after ~2010.)"
- **Broken error handling:** "When YouTube serves a response for a 404 thumbnail, they serve a true 404 response code
  (good), however they still serve `content-type: image/jpeg` and **valid JPEG data in the response body**… this also
  means you can't rely on `img.onerror`. The linked SO post and amp-youtube both use `onload` plus a `naturalWidth`
  check." (Same trap reported for the "empty video icon" GIF.) `[VERIFIED-fetched + SEARCH-asserted SO 23834025]`
- Aspect ratios differ: `maxresdefault` and `mqdefault` are **30:17**; `sddefault`, `hqdefault`, `default` are
  **4:3** — "Using `background-position: center` ensures the (possible) black bars in the 4:3 images are hidden."
- WebP variants exist at `https://i.ytimg.com/vi_webp/<id>/<name>.webp`; their availability matrix over sampled videos
  (maxresdefault.webp 178, hqdefault.jpg 89, sddefault.webp 21, …) ⇒ "**it'd be very reasonable and efficient to try
  first for the `maxresdefault.webp`**… then fall back to `hqdefault.jpg`"; the component itself defaults to
  `sddefault.webp` and paulirish chose `hqdefault` from `i.ytimg` "to optimize for origin reuse" (same origin as the
  player embed, saving a connection). `[VERIFIED-fetched]`
- Host aliases seen in the wild: `i.ytimg.com`, `img.youtube.com`, plus API-returned hosts; a Google issue-tracker case
  shows the Data API's `thumbnails` object changing shape over time. `[VERIFIED-fetched lite-youtube doc; SEARCH-asserted issuetracker.google.com/225014740]`

Legal/ToS position `[REASONED, marked low-confidence, needs a legal read of the exact clauses]`:
- YouTube's public documentation sanctions *embedding via the player* and *reading thumbnail URLs returned by the
  YouTube Data API*; the raw `vi/<id>/…jpg` path pattern is **not documented as an officially supported hotlink surface**
  (it appears only in community/tooling docs and the Data API responses). The YouTube ToS and API Services Developer
  Policies restrict obtaining/reproducing/distributing Service content outside provided features and impose
  display/attribution rules (e.g. required minimum thumbnail sizes were called out in the 2017 policy update
  "no… less than 120 pixels wide by 70 pixels tall"). `[SEARCH-asserted developers.google.com/youtube/terms/developer-policies, tubepress.com blog; primary clause text not fetched this session]`
- Practical doctrine for agents (defensible on both legal and reliability grounds):
  1. If you use the Data API, store the returned `thumbnails[].url` with the video record, **fetch the bytes
     server-side once, optimize (AVIF/WebP + width ladder), and self-host** on your own CDN — this is the option
     that survives YouTube URL-shape changes, is cacheable, and keeps the browser on one origin (better for LCP).
  2. If you hotlink anyway, use `i.ytimg.com/vi/<id>/hqdefault.jpg` (near-universal), keep the `naturalWidth` probe,
     and treat the third-party origin as *non-critical* (never the LCP resource).
  3. Never depend on `maxresdefault` existing; never depend on `onerror`.
  `[REASONED]`

### 4.6 Deferral numbers worth quoting in a doctrine

| Item | Number | Source |
|---|---|---|
| YouTube embed, lazy iframe only | ~500 KB saved initially | `[VERIFIED-fetched web.dev]` |
| YouTube facade vs player | 3 KB vs 540 KB | `[VERIFIED-fetched developer.chrome.com]` |
| `lite-youtube` script | 2.2 KB gzip / 1.7 KB brotli | `[VERIFIED-fetched README badge]` |
| `lite-youtube-embed` claim | ~224× faster | `[VERIFIED-fetched README]` |
| Facebook Like plugin, lazy | >200 KB (mostly JS) | `[VERIFIED-fetched web.dev]` |
| Instagram embed | >100 KB gzipped | `[VERIFIED-fetched web.dev]` |
| Typical embed JS range | >100 KB, up to 2 MB | `[VERIFIED-fetched web.dev]` |
| Third-party failure blocking render | timeout 10–80 s | `[VERIFIED-fetched web.dev]` |
| `preconnect` saving | 100–500 ms; unused connections closed after 10 s | `[VERIFIED-fetched web.dev]` |
| Deferring all scripts (Telegraph, ads+analytics) | ad load ~4 s faster | `[VERIFIED-fetched web.dev]` |
| Lazy-loading ads (MediaVine) | page load "200% improvement" | `[VERIFIED-fetched web.dev]` |
| Self-hosting an A/B script (Casper) | −1.7 s | `[VERIFIED-fetched web.dev]` |

---

## 5. Caching and delivery

### 5.1 Cache headers for media (MDN HTTP caching guide, fetched)

- Model: freshness by **age** vs `max-age`; `Age: 86400` on a `max-age=604800` response leaves 518400 s fresh. `[VERIFIED-fetched]`
- Heuristic caching (no `Cache-Control` at all) is real: "the specification recommends about **10%** (in this case 0.1
  year) of the time after storing" — "basically all responses should explicitly specify a `Cache-Control` header." `[VERIFIED-fetched]`
- Cache busting is the recommended pattern for media: "for resources that *do* change, it is a common best practice to
  change the URL each time the content changes" (hash in filename preferred; MDN lists hash-in-filename/query and
  version-in-filename/query). "The technique can be applied to all subresources, such as images." `[VERIFIED-fetched]`
- Immutable long-life media recipe, verbatim from MDN's example: `Cache-Control: public, max-age=31536000, immutable`
  + `Last-Modified` + `ETag`. `immutable` exists to "prevent unnecessary revalidation during reloads" because
  "when the user reloads, a revalidation request is sent even though the server knows that the content is immutable".
  Chrome historically implemented the same behaviour by policy instead of the directive. `[VERIFIED-fetched]`
- Which `max-age`: MDN points at the **QPACK static table** — commonly used values are `max-age=0`, `604800`
  (1 week), `2592000` (1 month), `31536000` (1 year with `public`) — and notes "Because the cache removes old entries
  when new entries are saved, the probability that a stored response still exists after one week is not that high…
  in practice, it does not make much difference which one you choose." `[VERIFIED-fetched]`
- `public` is only needed "if there is a need to store the response when the `Authorization` header is set". `[VERIFIED-fetched]`
- Documents can't be cache-busted → `Cache-Control: no-cache` (+ `private` when cookie-personalized) with `ETag`/
  `Last-Modified` so you get `304`s; `no-store` is discouraged ("you lose many advantages… including the browser's
  back/forward cache"). Note `no-cache` does not force revalidation on history navigations (bfcache). `[VERIFIED-fetched]`
- `Vary`: key the cache on `Accept-Encoding`, `Accept`, `Save-Data`, etc.; "**the `User-Agent` request header generally
  has a very large number of variations, which drastically reduces the chance that the cache will be reused**" — so
  prefer feature detection (or client hints) over UA-based variants, and remember a UA-shaped `Vary` multiplies
  CDN cache entries. `[VERIFIED-fetched]`
- Request collapse (stampede protection at the shared cache) makes even `max-age=0`/`no-cache` responses get reused
  for simultaneous requests. `[VERIFIED-fetched]`
- Shared-cache/CDN extras: `CDN-Cache-Control` (RFC 9213) standardizing vendor headers like `Surrogate-Control`;
  purge APIs make "managed caches" able to hold documents too; `Clear-Site-Data: cache` only clears the browser. `[VERIFIED-fetched]`
- Next.js concrete TTL policy for an on-the-fly optimizer: `minimumCacheTTL: 14400` (4 h) default, effective max-age =
  "the upstream image `Cache-Control` header, whichever is larger", with "**There is no mechanism to invalidate the
  cache at this time, so its best to keep `minimumCacheTTL` low**" — i.e. prefer static imports, which "will
  automatically hash the file contents and cache the image with a long-lived `immutable` `Cache-Control` header." `[VERIFIED-fetched]`

### 5.2 Service workers and precaching budgets

`[VERIFIED-fetched web.dev/learn/performance/prefetching-prerendering-precaching]`

- Precaching = cache-only strategy executed "when the service worker is installed", via a **precache manifest**
  (`[{url:'script.ffaa4455.js', revision:null}, {url:'/index.html', revision:'518747aa'}]`); `revision: null` when the
  filename is already hashed. Workbox's value is version bookkeeping: "if you update your service worker in the future,
  Workbox automatically removes expired entries from the cache."
- Budget doctrine, verbatim: "service worker precaching consumes network bandwidth, storage, and CPU. It's recommended
  to only precache resources that are likely to be used, and to [not specify] too many resources in a precache
  manifest. **When in doubt, it's better to precache too little than too much**, and rely on runtime caching."
- The SW `Cache` API ≠ HTTP cache ("a high-level cache controlled by JavaScript" vs one controlled by `Cache-Control`) —
  so double-caching media can double storage and defeat header-driven freshness. `[VERIFIED-fetched]`
- `prefetch` runs at **lowest priority**; speculation-rule prefetches land in the *memory* cache (faster than the HTTP
  cache); avoid prefetching personalized or cross-origin documents; skip speculative loading under `Save-Data`. `[VERIFIED-fetched]`
- Self-hosting third-party scripts/SW caching of them is the sanctioned middle path between vendor CDNs and
  uncontrolled caching. `[VERIFIED-fetched web.dev/efficiently-load-third-party-javascript]`

### 5.3 HTTP/2+ and the sprite question

- Verified adjacent fact: web.dev/Next.js-era guidance pushes *many small, individually cacheable* assets; MDN's caching
  guide explains why per-URL cache keys make concatenation expensive (one changed item invalidates the whole file). `[VERIFIED-fetched]`
- Practitioner consensus (HTTP/2): "If the user is on HTTP/2: You'll serve more and smaller assets. You'll avoid stuff
  like image sprites, inlined CSS…" (css-tricks, *Musings on HTTP/2 and Bundling*); "If your WordPress hosting supports
  HTTP/2 (over 95% do), CSS sprites likely won't improve your site speed" (Jetpack). `[SEARCH-asserted]`
- Doctrine `[REASONED]`: raster sprites (one big PNG + `background-position`) are **off** — they break responsive/
  format negotiation, waste decoded memory (the whole sheet), invalidate cache on any single change, and hurt a11y
  (`<img>` has no `alt` per sub-image). What *is* still correct: (a) **SVG symbol sprites** — one cached SVG with
  `<symbol>`s referenced by `<use href="#id">` in the same document, (b) icon **fonts replaced by inline SVG**,
  (c) HTTP/2 does not remove the per-resource overhead of decode/dispatch, so dozens of 1 KB icons still justify
  inlining (see 5.4) or a single sprite sheet.

### 5.4 Inlining thresholds (data: URIs, `<svg>` in markup)

`[VERIFIED-fetched calendar.perfplanet.com/2020/the-dangers-of-data-uris/ (Andy Davies)]`

- Costs: "**Prioritisation** — Embedding a resource within another overrides its download priority"; "**Caching** — The
  embedded resource cannot be cached separately and will get the same caching lifetime as its container… might be cached
  multiple times e.g. for every page it's included in"; "**Sizes** — Converting binary resources to base64 typically
  increases their size" (+33% before compression `[REASONED — standard base64 overhead]`); "**Redundancy** — a data URI
  is going to be downloaded whether it is used or not"; "**Opaqueness**" — duplicates are invisible to grep-level audits.
- Real failures cited: 7 copies of a logo inside one stylesheet; **17 KB** of Apple touch icons base64'd into a React
  bundle (4 sizes, only one ever used, fetched at script priority); a bundler inlining everything **<10 KB** which added
  ~**30 KB** of unused bytes; VWO inlining experiment images into its tag; Feefo injecting a **500 KB** `<style>` that
  was "approximately half base64-encoded fonts" (each `@font-face` shipping 6 formats); Emarsys shipping inline source
  maps (+600 KB uncompressed, one 1.7 MB map seen).
- The author's own policy: "I tend to restrict data URIs to resources that need to be loaded quickly for first render
  e.g. logo's, hero images etc., and limit myself to embedding them in **documents** rather than stylesheets or scripts";
  "it might be acceptable to embed a large hero image on a landing page, but it's probably never acceptable to embed a
  favicon no matter how small it is"; and "**Preloading increases the download priority without altering a resource's
  caching characteristics**, and still enables the browser to choose the most appropriate image" — i.e. prefer
  `rel=preload` over embedding. `[VERIFIED-fetched]`
- web.dev agrees on the boundary for the LCP resource and repeats the two penalties (no caching, extra decode cost). `[VERIFIED-fetched]`
- Threshold for agents `[REASONED]`: inline into **HTML** only (i) ≤ ~2 KB after compression, (ii) needed for first
  paint, (iii) used exactly once, (iv) not format/DPR-negotiable. Inline **SVG markup** directly when it is small and
  needs CSS/JS hooks (fill/colour theming) — web.dev notes inlining "allows for direct access to an SVG's child elements
  in JavaScript"; but keep SVGs as files when shared across pages so they cache, and minify/compress them either way
  ("SVG… is text-based, so techniques such as minification and compression apply. Lossy optimization is also possible
  using svgo"). `[VERIFIED-fetched]`

### 5.5 SVG `<use>`/`<symbol>` sprite caveats (verified from MDN)

- "`<use>`… duplicates [nodes]… The effect is the same as if the nodes were deeply cloned into a **non-exposed DOM**." `[VERIFIED-fetched]`
- **Cross-origin is blocked**: "For security reasons, browsers may apply the same-origin policy on `<use>` elements and
  may **refuse to load a cross-origin URL** in the `href` attribute. **There is currently no defined way to set a
  cross-origin policy for `<use>` elements.**" ⇒ an icon sprite on a CDN cannot be consumed with
  `<use href="https://cdn/…/sprite.svg#icon">`; options are same-origin hosting (proxy it), fetching and injecting the
  sprite into the document, or bundling it into the page. `[VERIFIED-fetched]`
- `data:` URIs in `href` are "**deprecated for security reasons**". External same-origin files work, fragment optional
  in modern implementations for whole-document loads. `[VERIFIED-fetched]`
- Styling: "CSS properties are not guaranteed to be inherited by the cloned DOM unless you explicitly request them";
  and "Most attributes on `<use>` are ignored if the corresponding attribute is already defined on the element
  *referenced*" — only `x`,`y`,`width`,`height`,`href` win; `width`/`height` only take effect when the target has a
  `viewBox` (i.e. refers to `<svg>`/`<symbol>`). ⇒ design symbols with `fill="currentColor"` / CSS custom properties. `[VERIFIED-fetched]`
- `xlink:href` is deprecated in favour of `href` (SVG 2). `[VERIFIED-fetched]`
- Accessibility: give `<img src="*.svg">` an explicit `role="img"` because of a VoiceOver bug ("VoiceOver does not
  correctly announce SVG images as images"); SVG-as-`<img>` also cannot reference external resources, and CSS inside
  it is scoped. `[VERIFIED-fetched MDN]`
- Security: SVG is HTML-like; Next.js "never optimizes SVG… SVG has many of the same features as HTML/CSS, which can
  lead to vulnerabilities without proper CSP headers" — serve user-supplied SVG with `Content-Disposition: attachment`,
  `script-src 'none'; sandbox;`, or rasterize it. `[VERIFIED-fetched]`

---

## 6. Performance budgets

### 6.1 Time budgets

- LCP: "**sites should strive to have an LCP of 2.5 seconds or less for at least 75% of page visits**"; >4.0 s is poor. `[VERIFIED-fetched web.dev/optimize-lcp]`
- CLS: ≤ **0.1** at 75% of visits; poor > 0.25. `[VERIFIED-fetched]`
- LCP subpart split on a well-optimized page: TTFB ~**40%**, resource load delay **<10%**, resource load duration ~**40%**,
  element render delay **<10%**; explicitly "guidelines, not strict rules", and "it is not recommended" to convert the
  percentages into absolute ms. Rule of thumb: "the LCP resource should start loading at the same time as the first
  resource loaded by that page." `[VERIFIED-fetched]`
- Counterweight the byte obsession: "**our research shows that the load duration portion of LCP tends not to be a
  significant bottleneck for most sites**" — delay phases usually matter more (and match the A/B finding that lazy
  loading cost 250–300 ms of LCP on WordPress archive pages). `[VERIFIED-fetched]`
- Decode/render: "All browsers today render images on the main thread, which means anything that blocks the main thread
  can also lead to unnecessary element render delay." `[VERIFIED-fetched]`

### 6.2 Byte budgets (what the sources actually say, and what to write down)

- Images dominate weight: "According to HTTP Archive, images are the most-requested asset type for most websites, and
  they usually take up more bandwidth than any other resource. **At the 90th percentile, sites send over 5 MB of
  images on desktop and mobile.**" `[VERIFIED-fetched web.dev]`
- Median home page 2025: "**2.86 MB on desktop and 2.56 MB on mobile… Images accounted for the most bytes** on both"
  (Web Almanac 2025); 2024 medians were 2,652 KB desktop / 2,311 KB mobile. `[SEARCH-asserted almanac.httparchive.org]`
- There is **no official web.dev byte ceiling per image**; the practitioner figure circulating in 2026 guides is
  "keep individual images under 200 KB, total page weight under 2 MB, hero up to 500 KB". `[SEARCH-asserted; treat as folklore]`
- Defensible derivation `[REASONED arithmetic, stated so in the skill]`: if resource-load-duration should be ≤ ~40% of a
  2.5 s LCP budget (≈1.0 s) and a mid-tier 4G cell is ~1.6 Mbps effective (~200 KB/s), then an **LCP image transfer
  budget of ≈200 KB** is the honest number for that link; on faster links the same file is nearly free, which is why
  the delay phases usually dominate. Write the budget as "LCP image ≤ 200 KB *at the p75 network of your traffic*",
  not as a universal constant, and gate it with real CrUX/RUM data.
- Concrete derived targets `[REASONED from verified per-format numbers]`: hero 1600×900 AVIF q50 ≈ 60–140 KB; card
  image 800×450 AVIF ≈ 20–45 KB; thumb 320×180 ≈ 6–12 KB; icon ≤ 2 KB (SVG preferred); loop-video replacing a GIF
  should land at ~10% of the GIF size (3.7 MB → 341–551 KB measured).

### 6.3 Origin-shield / delivery topology for image CDNs

- Same-origin first: "While preconnecting to the origin can mitigate some of this cost, **the best option is to serve
  images from the same origin as your HTML document**. Many CDNs allow you to proxy requests from your origin to theirs." `[VERIFIED-fetched web.dev/image-cdns + optimize-lcp]`
- Tiered caching: an **origin shield** is "a secondary caching layer that sits between Bunny's edge PoPs and your
  origin server. Instead of each PoP fetching [a miss]…" — imgproxy's docs give the identical advice ("Add a secondary
  cache layer between your CDN and imgproxy origin if your CDN supports it"). This matters extra for on-the-fly
  optimizers, where a cold miss = an encode (AVIF "50% longer to encode" than WebP) in the request path. `[VERIFIED-fetched bunny.net docs via search, imgproxy docs via search]`
- Protect the on-the-fly origin: allowlist sources (`remotePatterns`/`localPatterns`, exact `search` values), cap
  `qualities` and size steps (else "malicious actors could optimize more qualities than you intended" → CPU/money DoS),
  cap `maximumResponseBody`, keep `maximumRedirects` small, and add a **security key/signature** on transform URLs
  ("each new version of an image requires a unique security key"). `[VERIFIED-fetched Next.js + web.dev]`
- Cold-miss amplification: with an on-the-fly optimizer, the first request per (size × format) pays encode cost;
  `minimumCacheTTL`, disk cache (LRU, default 50% of free disk in Next.js), warm-on-build, and a bounded variant set
  are the controls. `[VERIFIED-fetched]`
- Cache-key explosion warning: every extra `Vary` dimension (`Accept`, `Save-Data`, UA) multiplies edge entries —
  which is exactly why `<picture>` in markup is often better than header negotiation. `[VERIFIED-fetched MDN + REASONED]`

### 6.4 Fonts ↔ LCP (hand-off to the next research task)

- The LCP resource "of a page (if it has one) will either be an image **or a web font**" — text LCP elements are
  blocked by font loading. `[VERIFIED-fetched optimize-lcp]`
- "If your LCP resource is a web font, in addition to reducing web font size, you should also consider whether you need
  to block rendering on the web font resource load. If you set a `font-display` value of anything other than `auto` or
  `block`, then text will always be visible during load, and LCP won't be blocked on an additional network request." `[VERIFIED-fetched]`
- CLS side: both FOUT and FOIT shift layout; mitigations listed are `font-display: optional`, a matching generic
  fallback (`sans-serif` vs the default "Times"), `size-adjust`/`ascent-override`/`descent-override`/`line-gap-override`
  metric overrides, the Font Loading API, and `<link rel=preload>` for critical fonts ("A preloaded font will have a
  higher chance to meet the first paint, in which case there's no layout shifting"). `[VERIFIED-fetched optimize-cls]`
- Text must never be baked into an image (see §1.2) — that converts a font problem into a much worse LCP/a11y problem. `[VERIFIED-fetched]`

---

## 7. Native / mobile (brief, one paragraph each; confidence marked)

**iOS asset catalogs — confidence high (Apple docs named, page body not fully read).** An `.xcassets` catalog holds
*asset sets*, each "represent[ing] one resource — like an image, color, or data file — that your app loads at runtime",
with per-idiom/per-scale variations; the HIG's rule is "As you add each image to your project's asset catalog, identify
its scale factor by appending '@1x,' '@2x,' or '@3x' to its filename", and Xcode "converts the image format into the
most efficient supported format" (HEIC/APNG handling, thinning at build time, On-Demand Resources/`NSURLCache` for
remote media). Doctrine mirror of the web one: vector (`symbol`/SF Symbols/PDF) for icons, 1x/2x/3x bitmaps for photos
only where needed, and let asset-catalog thinning ship just the device variant. `[SEARCH-asserted:
developer.apple.com/documentation/xcode/adding-images-to-your-xcode-project, .../managing-assets-with-asset-catalogs,
human-interface-guidelines/images; REASONED synthesis]`

**Android drawable densities — confidence high (page fetched).** Baseline `mdpi` ≈ **160 dpi**; buckets
`ldpi`~120, `mdpi`~160, `hdpi`~240, `xhdpi`~320, `xxhdpi`~480, `xxxhdpi`~640 (plus `tvdpi`~213 sized at
**1.33 × mdpi**), and you author bitmaps at the **3:4:6:8:12:16** scaling ratio (48 px mdpi ⇒ 36/48/72/96/144/192).
Conversion is `px = dp * (dpi / 160)` and `DisplayMetrics.density` is 0.75/1.0/1.5/2.0(/3.0) — never hardcode it, use
`TypedValue.applyDimension` or `ViewConfiguration.getScaled*`. Google's stated preference is **one vector drawable**
("Vector graphics are often provided as SVG files, but Android doesn't support this format so you must convert SVG
files to Android's vector drawable format" via Vector Asset Studio, and it lives in plain `res/drawable/`). Launcher
icons go in `mipmap-*` because "some app launchers display your app icon as much as **25% larger** than what's called
for by the device's density bucket"; `nodpi` opts a resource out of scaling; missing variants are scaled by the system
"resulting in scaling artifacts such as blurring". `[VERIFIED-fetched developer.android.com/training/multiscreen/screendensities]`

**Lazy lists of media — confidence medium.** The web lesson ports directly: materialize/recycle row views, bind by
position, cancel/detach loads for recycled holders (RecyclerView + `Glide.with(fragment)` lifecycle scoping), and
reserve row heights so scrolling doesn't shift. Android's own "Caching Bitmaps" lesson exists for exactly this pattern
(`LruCache` of decoded bitmaps + disk cache + downsampled decoding). `[SEARCH-asserted developer.android.com/topic/performance/graphics/cache-bitmap; REASONED]`

**Image memory caches — confidence high for Glide (fetched), medium for iOS libraries.**
Glide checks four layers in order — active resources → memory cache → transformed-resource disk cache → original-data
disk cache — and only hits the network after all four miss; memory and disk caches are **LRU** ("they take
increasingly more memory and/or disk space until they reach their limit at which point they will use at or near the
limit continuously"), and both memory cache and `BitmapPool` "respond to `ComponentCallbacks2` and automatically evict
their contents", so manual clearing (`clearMemory()` on the main thread, `clearDiskCache()` off it) "should be avoided
whenever possible to avoid jank". Cache keys include width/height, transformation, options and requested data type —
so invalidation means **changing the identifier or mixing in a `signature()`** (`MediaStoreSignature`, `ObjectKey`,
version metadata), not deleting files; `DiskCacheStrategy.AUTOMATIC` stores the *original* bytes for remote data and
only the *transformed* thumbnail for local data, which is the right default asymmetry to copy anywhere. Sizing knobs:
`setMemoryCategory(LOW/HIGH/NORMAL)` temporarily. `[VERIFIED-fetched bumptech.github.io/glide/doc/caching.html]`
SDWebImage/Kingfisher follow the same shape (memory `NSCache` + disk + `URLSession`/`URLCache` underneath); a reported
Kingfisher default is `memoryStorage` total cost limit ≈ **25% of device RAM** with no count limit — treat that number
as folklore until read from the library docs. URLCache is the OS-level HTTP cache, so the web header rules
(`max-age`, `immutable`, hashed URLs) apply to native media too, and `SDImageCache`/`Kingfisher` exist because
URLCache's defaults are too small/opaque for image grids. `[SEARCH-asserted onevcat/Kingfisher issue #1268 /
stackoverflow 44048657; REASONED]`

---

## 8. Decision rules for the skill (distilled, with the evidence behind each)

1. **Ask whether the media exists at all.** CSS/SVG/web-fonts beat raster; text is never an image. `[web.dev §1.2]`
2. **One pipeline, three formats.** Emit AVIF + WebP + (JPEG or PNG) from a single transform layer; never hand-place
   per-page encodings. Order `<picture>` sources AVIF→WebP→JPEG; put `alt`/`width`/`height`/`loading`/`fetchpriority`
   on the `<img>`. `[web.dev, MDN]`
3. **Consider JXL only for lossless/progressive/HDR niches behind `<picture>`'s first slot, with data to back it.**
   Support ≈69% and Safari is partial (no animation/progressive). `[caniuse, Chrome blog]`
4. **Kill GIFs.** Looping media = `<video autoplay loop muted playsinline>` with WebM first; not an LCP candidate
   without a poster, which is a feature. `[web.dev]`
5. **Icons are SVG**, inlined when one-off and tiny, same-origin `<use>` sprite when shared; never a raster sprite sheet. `[MDN use, HTTP/2 practice]`
6. **`w` descriptors + real `sizes` (or `sizes="auto"`+lazy) are the only responsive recipe you ship**; cap DPR at 2;
   same aspect ratio across candidates. `[MDN, Next.js, web.dev]`
7. **Reserve space unconditionally**: `width`/`height` on every `<img>`, `<video>`, `<iframe>` and `<source>`;
   `aspect-ratio` in CSS for containers; skeleton/min-height for late content; place late content lower in the viewport. `[web.dev CLS]`
8. **LCP image: eager + `fetchpriority="high"` + discoverable in HTML; never `loading="lazy"`.** Add
   `rel=preload as=image fetchpriority=high` only for CSS backgrounds or JS-discovered heroes. `[web.dev optimize-lcp, lcp-lazy-loading, fetch-priority]`
9. **Everything else below the fold: `loading="lazy"`.** Verified: byte savings preserved, LCP regression reversed. `[web.dev]`
10. **`decoding="async"` on non-LCP images**; leave `auto` for the hero. `[MDN, web.dev]`
11. **Facade every non-primary third-party embed** (video, map, chat, social) with load→mouseover-preconnect→click-replace;
    use `lite-youtube-embed`/`lite-youtube` rather than writing one; keep the facade's own poster self-hosted. `[developer.chrome.com, web.dev, both READMEs]`
12. **Consent-gate the swap**, use `youtube-nocookie.com` for the real player, and remember nocookie is not a consent substitute. `[YouTube Help; consent vendors]`
13. **Never trust a third-party thumbnail URL to exist.** Probe `naturalWidth` on `onload`, ladder
    `maxresdefault.webp → sddefault.webp → hqdefault.jpg`, prefer self-hosted copies. `[youtube-thumbnail-urls.md]`
14. **Media is immutable and versioned in the URL**: `Cache-Control: public, max-age=31536000, immutable` + ETag;
    documents get `no-cache(+private)`; avoid UA-vary. `[MDN]`
15. **Inline with a 2 KB/first-paint/once/HTML-only gate**, prefer preload over inlining, and audit bundles for stray
    base64 (favicons, source maps, experiment images). `[perfplanet, web.dev]`
16. **Budget in the same units the metric uses**: LCP ≤2.5 s p75, subparts 40/<10/40/<10, CLS ≤0.1, LCP image ≈≤200 KB
    at your p75 network, third-party embed JS ≈0 KB at first render. `[web.dev, almanac]`
17. **Same-origin media delivery, origin shield in front of any on-the-fly optimizer, signed transform URLs, bounded
    variant/quality allowlists.** `[web.dev, bunny.net, imgix, Next.js]`
18. **Do not precache generously.** SW precache = install-time cost in bytes, storage and CPU; hash the filenames,
    set `revision: null`, and prefer runtime caching for anything uncertain. `[web.dev]`

---

## 9. Verification gaps / next-pass items

- YouTube ToS + API Services Developer Policies **clause text** on thumbnails/reproduction was not read this session —
  read `https://developers.google.com/youtube/terms/api-services-terms-of-service` and
  `https://developers.google.com/youtube/terms/developer-policies` before writing the hotlink rule as law. `[open]`
- `prefers-reduced-data` support table not fetched (MDN path 404'd) — confirm whether it is still flag-only. `[open]`
- Safari/Firefox lazy-load distance thresholds are practitioner-measured, not spec'd. `[open]`
- Per-format byte tables quoted here are single examples (web.dev's dog photo, monarch butterfly, imgix bridge.jpg);
  a skill should re-measure on its own assets rather than reuse them. `[open]`
- Cloudinary/imgix/Cloudflare/Contentful/Sanity URL conventions: imgix and Next.js verified; the rest search-only. `[open]`
- HTTP/2 vs sprite question has no primary-spec source; the doctrine rests on css-tricks/Jetpack plus cache-key logic. `[open]`
- iOS asset catalog page bodies not fetched (Apple docs are JS-rendered); statements are HIG/Xcode-doc snippets plus synthesis. `[open]`

## 10. Source list (exact URLs)

**Primary (fetched this session)**
- https://web.dev/articles/choose-the-right-image-format
- https://web.dev/learn/performance/image-performance
- https://web.dev/articles/browser-level-image-lazy-loading
- https://web.dev/articles/lcp-lazy-loading
- https://web.dev/articles/fetch-priority
- https://web.dev/articles/optimize-lcp
- https://web.dev/articles/optimize-cls
- https://web.dev/articles/image-cdns
- https://web.dev/articles/compress-images-avif
- https://web.dev/articles/replace-gifs-with-videos
- https://web.dev/articles/embed-best-practices
- https://web.dev/learn/performance/lazy-load-images-and-iframe-elements
- https://web.dev/learn/performance/prefetching-prerendering-precaching
- https://web.dev/learn/images/webp
- https://web.dev/learn/images/jpeg
- https://web.dev/articles/third-party-javascript
- https://web.dev/articles/efficiently-load-third-party-javascript
- https://developer.chrome.com/docs/lighthouse/performance/third-party-facades
- https://developer.chrome.com/blog/chrome-155-beta
- https://caniuse.com/jpegxl · https://caniuse.com/avif · https://caniuse.com/webp
- https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images (+ raw: elements/img, elements/picture, attributes/fetchpriority, svg/element/use, http/guides/caching, http/headers/save-data)
- https://docs.imgix.com/apis/rendering/automatic
- https://nextjs.org/docs/app/api-reference/components/image
- https://developer.android.com/training/multiscreen/screendensities
- https://bumptech.github.io/glide/doc/caching.html
- https://github.com/paulirish/lite-youtube-embed + https://raw.githubusercontent.com/paulirish/lite-youtube-embed/main/youtube-thumbnail-urls.md
- https://raw.githubusercontent.com/justinribeiro/lite-youtube/master/README.md
- https://support.google.com/youtube/answer/171780
- https://calendar.perfplanet.com/2020/the-dangers-of-data-uris/

**Secondary (search-asserted only)**
- https://almanac.httparchive.org/en/2025/page-weight · …/2024/page-weight
- https://cloudinary.com/documentation/image_optimization · https://cloudinary.com/blog/advanced-image-formats-and-when-to-use-them
- https://css-tricks.com/musings-on-http2-and-bundling/ · https://jetpack.com/resources/combine-images-using-css-sprites/
- https://calibreapp.com/blog/native-lazy-loading · https://addyosmani.com/blog/better-image-lazy-loading-in-chrome/
- https://calendar.perfplanet.com/2019/native-image-lazy-loading-in-chrome-is-way-too-eager/
- https://stackoverflow.com/questions/34763547/youtube-maxresdefault-thumbnails · …/58560120 · …/23834025 · https://issuetracker.google.com/issues/225014740
- https://developers.google.com/youtube/terms/developer-policies · https://www.youtube.com/static?template=terms · https://tubepress.com/blog/2017/02/dont-stress-about-the-updated-youtube-api-terms-of-service/
- https://developers.cloudflare.com/images/optimization/transformations/sources/ · https://bunny.net/docs/cdn/performance/origin-shield · https://docs.imgproxy.net/cache/external
- https://alistairshepherd.uk/writing/cloudflare-worker-image-proxy/
- https://responsive-image.dev/usage/lqip · https://www.mux.com/blog/blurry-image-placeholders-on-the-web · https://github.com/drwpow/vite-plugin-lqip · https://cloudinary.com/tools/lqip-blur-placeholder
- https://bumptech.github.io/glide/doc/caching.html · https://developer.android.com/topic/performance/graphics/cache-bitmap · https://github.com/onevcat/Kingfisher/issues/1268 · https://stackoverflow.com/questions/44048657
- https://developer.apple.com/documentation/xcode/adding-images-to-your-xcode-project · …/managing-assets-with-asset-catalogs · https://developer.apple.com/design/human-interface-guidelines/images
- https://imagedimensions.com/guides/recommended-image-sizes · https://www.debugbear.com/blog/lazy-loading-performance · https://www.corewebvitals.io/core-web-vitals/largest-contentful-paint/optimize-lcp-image
- https://blog.logrocket.com/jpeg-xl-web-performance/ · https://blog.openreplay.com/jpeg-xl-vs-avif/ · https://netflixtechblog.com/avif-for-next-generation-image-coding-b1d75675fe4
- https://consently.net/blog/is-youtube-embed-gdpr-compliant · https://infotrust.com/articles/are-your-embedded-youtube-videos-compliant-discover-privacy-enhanced-mode/
