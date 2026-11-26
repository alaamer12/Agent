# 01 — The complete asset matrix

Every file a product needs, why it exists, and the two facts that break it when wrong: **exact size**
and **alpha posture**. Sizes below are the platform's contract, not a preference.

Legend for alpha: **opaque** = no alpha channel at all and no `tRNS` chunk; **alpha** = transparency
required.

## 1. Browser tab and bookmarks

| File | Size | Alpha | Where it is referenced | Breaks when |
|---|---|---|---|---|
| `favicon.svg` | any (design on a 32 grid) | alpha | `<link rel="icon" type="image/svg+xml">` | It is the only icon and the browser is old — always keep PNG fallbacks |
| `favicon-16x16.png` | 16×16 | alpha | `<link rel="icon" sizes="16x16">` | Drawn by downscaling a detailed mark: mush. Simplify first |
| `favicon-32x32.png` | 32×32 | alpha | `<link rel="icon" sizes="32x32">` | Same |
| `favicon-48x48.png` | 48×48 | alpha | Crawler `<img>` in the first packet, some browsers | Missing → a 404 in the crawler layer |
| `favicon.ico` | 16, 32, 48 inside one file | alpha | `/favicon.ico` (browsers request it blind) | Single-size ICO, or a stale copy at the public root |
| `mask-icon.svg` | any, monochrome | alpha | `<link rel="mask-icon" color="#…">` (Safari pinned tab) | Colour artwork: the mask paints it as a silhouette blob |
| `apple-touch-icon.png` | 180×180 | **opaque** | `<link rel="apple-touch-icon">` | Alpha or rounded corners: iOS composites on black and rounds it itself |
| `theme-color` | — | — | `<meta name="theme-color">` | Missing → the browser chrome clashes with the page |

The ICO is a real container: a 6-byte header, then a 16-byte directory entry per image, then the PNG
or BMP payloads. Browsers request `/favicon.ico` at the origin root even when a `<link>` exists, so
ship the same bytes at the root **and** under `/icons/`.

## 2. PWA / installable web app

| File | Size | Alpha | Notes |
|---|---|---|---|
| `icon-192.png` | 192×192 | **opaque** | Manifest `any` purpose |
| `icon-512.png` | 512×512 | **opaque** | Manifest `any` purpose; used for splash generation by the OS |
| `icon-512-maskable.png` | 512×512 | **opaque** | Manifest `purpose: "maskable"`; background must be full-bleed, artwork inside a centred **80% safe zone** (40% radius) |
| `site.webmanifest` | — | — | `name`, `short_name`, `start_url`, `display`, `background_color`, `theme_color`, `icons[]`, `lang`, `dir` |
| `mstile-150x150.png` | 150×150 | **opaque** | Windows tiles |
| `browserconfig.xml` | — | — | `<square150x150logo>`, `<TileColor>` |

Maskable is the file everyone gets wrong: the background reaching the edges is *required*, so a
"artwork bounding box inside the safe zone" test must threshold on **luminance** (the bright mark),
not on "pixels different from the corner colour" — the corner colour *is* the background.

## 3. Social cards

| File | Size | Alpha | Notes |
|---|---|---|---|
| static card per family/locale | 1200×630 (1.91:1) | **opaque** | One per content family, per shipped locale. This is the layer that must always exist |
| dynamic card per entity | 1200×630 | **opaque** | Same geometry, same encoder; rendered at request time behind the static layer |
| byte ceiling | ≤ 300 KB | — | Not a platform hard limit (most allow 5–8 MB) but a preview-quality limit: heavy images are skipped or slow |
| `og:image:alt` | — | — | Describe the card's content; it is read by screen readers in some clients |

Platform fetch constraints worth knowing:

- Absolute HTTPS URL. Relative paths are ignored.
- PNG, JPEG or WebP. **SVG is rejected.**
- The image must be publicly reachable without cookies, auth, or a bot challenge.
- Scrapers send their own User-Agent and follow redirects; a CDN that blocks unknown agents kills the
  card while `curl` works.
- `og:type`, `og:title`, `og:description`, `og:url`, `og:image` + `:type/:width/:height/:alt`,
  `og:locale`, `og:locale:alternate`, `og:site_name`; Twitter: `twitter:card=summary_large_image`,
  `twitter:title`, `twitter:description`, `twitter:image`, `twitter:image:alt`.

## 4. iOS app icon

`AppIcon.appiconset/` with a `Contents.json` that lists, at minimum:

| Idiom | Size (pt) | Scale | Pixels |
|---|---|---|---|
| iphone | 20 | 2x, 3x | 40, 60 |
| iphone | 29 | 2x, 3x | 58, 87 |
| iphone | 40 | 2x, 3x | 80, 120 |
| iphone | 60 | 2x, 3x | 120, 180 |
| ipad | 20 | 1x, 2x | 20, 40 |
| ipad | 29 | 1x, 2x | 29, 58 |
| ipad | 40 | 1x, 2x | 40, 80 |
| ipad | 76 | 1x, 2x | 76, 152 |
| ipad | 83.5 | 2x | 167 |
| ios-marketing | 1024 | 1x | 1024 |

Rules that fail review or render wrong:

- **No alpha channel.** App Store Connect rejects icons with transparency; the device paints black.
- **No rounded corners.** iOS masks the icon itself; pre-rounded corners double-round.
- **No transparency-derived shadow.** Anything outside the artwork is opaque background.
- `Contents.json` must name every file that exists, with `size`, `scale`, `idiom`.

## 5. Android

Two generations ship together:

**Legacy (pre-8.0 launchers):** `mipmap-{mdpi,hdpi,xhdpi,xxhdpi,xxxhdpi}/ic_launcher.png` at
48/72/96/144/192 px, **opaque**, plus `ic_launcher_round.png` if the launcher asks for it.

**Adaptive (8.0+):** two layers on a **108 dp** canvas (72 dp visible + 18 dp bleed per edge):

| Density | Canvas |
|---|---|
| mdpi | 108 |
| hdpi | 162 |
| xhdpi | 216 |
| xxhdpi | 324 |
| xxxhdpi | 432 |

- `ic_launcher_background.png` — **opaque**, full bleed.
- `ic_launcher_foreground.png` — **alpha required**, artwork inside the central 72 dp safe zone.
- `mipmap-anydpi-v26/ic_launcher.xml` (+ `ic_launcher_round.xml`) referencing both layers, with an
  optional `<monochrome>` layer for themed icons.
- Splash: a 2732×2732 **opaque** image (Capacitor) or a launch theme drawable; centre the mark and
  wordmark, keep it readable when the OS crops to different aspect ratios.

## 6. Capacitor / native packaging

Capacitor reads a `resources/` folder and generates the platform trees:

```
resources/
├── icon.png                     (1024×1024, opaque)          → source for every iOS/Android icon
├── icon-foreground.png          (1024×1024, alpha)           → adaptive foreground
├── icon-background.png          (1024×1024, opaque)          → adaptive background
├── splash.png                   (2732×2732, opaque)
├── splash-dark.png              (2732×2732, opaque)
├── ios/AppIcon.appiconset/      (explicit, committed)
└── android/mipmap-*/            (explicit, committed)
```

Committing the explicit trees (not only the 1024 sources) makes the icons reviewable in a diff and
lets a conformance test read real files instead of trusting the generator.

## 7. What the product also needs but nobody lists

| Asset | Why |
|---|---|
| mark layer (alpha PNG) | composited onto cards; never the rounded app icon |
| wordmark layer (alpha PNG) | the real logotype, as an image — do not re-typeset it |
| card background master | the photographic/gradient artwork, kept as a master and resized, never cropped |
| the font file + its licence | the renderer must embed it; the licence must ship with it |
| a static fallback card per family **and per locale** | the degradation target; it must exist before the dynamic layer does |
| a runtime-independent encoder | so the drift gate can run under any JS runtime |

## 8. Sizing discipline

- **Resize, never crop** a background master: crop changes the composition and can put text over the
  bright part of the artwork.
- **Never upscale.** If a requested size exceeds the master's content box, say so; a soft icon is
  worse than a smaller honest one.
- **Downscale small icons from a pre-simplified intermediate**, not from the 800 px master: detail
  that survives at 128 px becomes noise at 16 px.
- Keep the master's alpha and padding intact; derive, do not edit in place.
