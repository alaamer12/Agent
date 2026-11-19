# Raster media: formats, responsive sizing, loading strategy, caching

The lane for every non-vector bitmap. Doctrine order: first ask whether the
raster exists at all, then pick the format pipeline, then reserve its space,
then decide when it loads, then how it is cached. Each step has a citation in
the workshop dossier (confidence-marked); numbers here are documented as of
2026-11 and must be re-measured per asset.

## 1. Does the raster exist?

CSS/SVG/web-fonts beat raster; **text is never an image** (a11y + bytes +
locale). Icons are SVG (§svg-engineering). Looping GIF → `<video autoplay loop
muted playsinline>` with WebM first — the missing poster is a feature, not a
gap (it kills the GIF).

## 2. Format pipeline 2026: one transform layer, three outputs

| Format | Role | Evidence state |
|---|---|---|
| **AVIF** | default lossy photo | 96.7% baseline "high" (caniuse, fetched) |
| **WebP** | required fallback | 97.3% |
| **JPEG / PNG** | last-resort fallback (PNG for transparency fidelity) | universal |
| **JPEG XL** | niche: progressive / lossless / HDR | ~69% (Chrome 155 + Firefox 158 shipped `jxl-rs`; Safari partial — stills only) — only as a first `<picture>` slot when the use is genuinely one of those |

**One pipeline, three formats**: a single transform layer emits AVIF + WebP +
baseline per source; per-page encodings hand-placed are a defect. `<picture>`
source order AVIF → WebP → JPEG; `alt`/`width`/`height`/`loading`/`fetchpriority`
live on the `<img>` inside, never on the `<picture>`.

Auto-negotiation (Accept-header "format detection") has a verified hole:
Firefox only advertises AVIF/WebP for images loaded *inside a webpage* — a
direct image URL gets the original bytes — and animated GIFs with transparency
get mis-served as AVIF by real CDNs. `<picture>` in markup beats header
sniffing when correctness matters. Per-format byte tables in posts are single
examples: re-measure on your own assets before quoting a win.

## 3. Responsive: `w` + `sizes` or nothing

Spec facts, not folklore: with `w` descriptors and **no `sizes`, the browser
assumes `100vw`** — a 32px icon gets its 3× hero candidate; `x` descriptors
ignore layout entirely. The shippable recipe: same aspect ratio across
candidates, `srcset` with `w` + honest `sizes` (or `sizes="auto"` paired with
`loading="lazy"`), DPR capped at 2. Art direction (different crop per
breakpoint) is `<picture>` media queries, not `object-fit` prayer.

## 4. Loading strategy: the LCP rule is absolute

- **Never `loading="lazy"` the LCP image**; it must be eager,
  `fetchpriority="high"`, and **discoverable in the HTML**. Verified median
  p75 LCP: 3,546 ms on pages using lazy loading vs 2,922 ms without; the A/B
  fix (lazy only below the fold) reversed the regression while keeping 100% of
  the byte savings. `rel=preload as=image fetchpriority=high` only when the
  hero cannot be discovered in HTML (CSS background, JS-rendered).
- **Everything else below the fold: `loading="lazy"`.** That is the whole
  sentence; both halves matter.
- `decoding="async"` on non-LCP images; leave `auto` on the hero.
- **Space reservation is unconditional**: `width`/`height` on every `<img>`,
  `<video>`, `<iframe>`; `aspect-ratio` on containers. The trap is verified: a
  lazy image with no dimensions is 0×0 until loaded — the browser can deem an
  entire gallery "in viewport" and load everything, then reflow it. Late-
  arriving content goes lower in the viewport, or behind a skeleton (the
  `ui` pillar owns the skeleton contract; the media lane supplies the box).

## 5. Caching and delivery

- Media URLs are **content-hashed and immutable**:
  `Cache-Control: public, max-age=31536000, immutable` (+ ETag). `public` is
  only required when an `Authorization` header is present. Documents cannot be
  cache-busted → `no-cache` (+ `private` when cookie-personalized).
  Heuristic caching is real when `Cache-Control` is missing (~10% of
  Last-Modified delta) — never rely on it.
- `Vary` on `Accept-Encoding`/`Accept`/`Save-Data`; **avoid `User-Agent`
  varying** (fractures every shared cache). Shared caches: `CDN-Cache-Control`
  (RFC 9213); request collapse protects even `no-cache` origins.
- On-the-fly optimizers (imgix/Cloudinary/`next/image`-style): origin shield in
  front, signed transform URLs, **bounded** variant/quality allowlists (the
  variant space is a cache-key DoS if open), documented TTLs (Next.js default
  `minimumCacheTTL: 14400`).
- **Service-worker precaching is a declared budget, not a habit**: install-time
  bytes/storage/CPU — hash filenames, `revision: null`, and prefer runtime
  caching for anything uncertain. SW `Cache` ≠ HTTP cache. `prefetch` runs at
  lowest priority.
- Inlining (`data:` URI) gate — all four or don't: ≤ ~2 KB compressed, needed
  for first paint, used exactly once, in HTML only (CSS inlining multiplies:
  verified real failure: 7 logo copies in one stylesheet; 17 KB of touch icons
  base64'd). Inlining overrides the resource's own priority and destroys
  independent caching; a preload is usually the cheaper answer. Audit bundles
  for stray base64.
- **Raster sprite sheets (one PNG + `background-position`) are off**: they
  break `srcset` selection and DPR handling and cache as one big key; HTTP/2+
  serves many small assets. SVG sprites are the sprite that survives —
  same-origin only (§svg-engineering §6).

## 6. Budgets stated in the units the metrics use

LCP ≤ 2.5 s p75 with subparts TTFB≤400/…/≤100/≤100ms discipline; CLS ≤ 0.1;
**the LCP image ≈ ≤ 200 KB on the project's own p75 network**; third-party
embed JS ≈ 0 KB at first render (§time-based-media owns the facade mechanics).

## 7. Native mirror (brief)

- **iOS**: asset catalog = one asset set per resource with @1x/@2x/@3x idioms,
  format conversion + thinning at build; On-Demand Resources / `URLCache` for
  remote. Vector (SF Symbols/PDF) for icons, bitmaps only where needed.
- **Android**: density buckets ldpi120→xxxhdpi640, baseline mdpi=160 dpi,
  author bitmaps at 3:4:6:8:12:16, convert `px = dp * (dpi/160)` — never
  hardcode density. Google's stated preference: **one VectorDrawable**
  (SVG must be converted; it does not ship as SVG). Launcher icons in
  `mipmap-*` (launchers may scale +25%); `nodpi` opts out; a missing variant
  scales with visible blur.
- **Lazy lists** port the web lesson exactly: reserve row heights, cancel
  loads for recycled holders, lifecycle-scope the loader (RecyclerView +
  `Glide.with(fragment)`).
- **Memory/disk caches**: Glide's four layers (active → memory → transformed
  disk → original disk) before network, LRU both caches with automatic
  `ComponentCallbacks2` eviction — *avoid manual `clearMemory()` calls*. Cache
  keys embed size/transform/options → invalidate by **signature/version, not
  file deletion**; `AUTOMATIC` stores originals for remote, transformed for
  local — copy that asymmetry. Kingfisher/SDWebImage follow the same shape
  (`NSCache`+disk over `URLSession`); OS-level `URLCache` obeys the header
  rules of §5 — web cache doctrine applies to native media unchanged.

## Sources

web.dev (`optimize-lcp`, `lcp-lazy-loading`, `fetch-priority`,
`use-image-aspect-ratio`, `preload-critical-assets`, `font-best-practices`,
`embed-best-practices`), MDN (`srcset`/`sizes`, `picture`, `loading`,
`fetchpriority`, HTTP caching, CDN-Cache-Control), caniuse (AVIF/WebP/JXL),
Chrome blog (JXL 155), imgix (auto-format hole), Next.js image docs, perfplanet
(data-URI costs), developer.apple (asset catalogs, HIG images),
developer.android (screen densities, caching bitmaps), bumptech Glide docs
(caching), `paulirish/lite-youtube-embed` + `justinribeiro/lite-youtube`
READMEs. Full confidence-marked dossier: workshop research files for the imgery
lane (not doctrine, kept as evidence while building).
