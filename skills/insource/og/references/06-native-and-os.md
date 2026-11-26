# 06 — Native, OS, and packaging

Browser icons are half the job. The other half is the four native surfaces that each reject a different
thing: iOS rejects alpha, Android rejects a mark outside its mask, Windows wants a tile colour, and every
store wants a set, not a file.

## 1. iOS — `AppIcon.appiconset`

```
AppIcon.appiconset/
├── Contents.json
├── icon-20@2x.png      40
├── icon-20@3x.png      60
├── icon-29@2x.png      58
├── icon-29@3x.png      87
├── icon-40@2x.png      80
├── icon-40@3x.png      120
├── icon-60@2x.png      120
├── icon-60@3x.png      180
├── icon-76@1x.png      76
├── icon-76@2x.png      152
├── icon-83.5@2x.png    167
├── icon-20@1x-ipad.png 20
├── icon-29@1x-ipad.png 29
├── icon-40@1x-ipad.png 40
└── icon-1024.png       1024   (ios-marketing)
```

`Contents.json` entry shape:

```json
{ "filename": "icon-60@3x.png", "idiom": "iphone", "scale": "3x", "size": "60x60" }
```

Rules:

- **No alpha channel.** App Store Connect rejects it; on-device it composites on black. Flatten onto the
  brand background and *drop the channel* (see `03-render-and-encode.md` §5).
- **No pre-rounded corners.** iOS masks it. Rounded artwork inside a masked square shows a visible double
  curve.
- **No baked shadow.** Anything outside the artwork must be opaque background, not a shadow on transparency.
- The 1024 marketing icon is a real requirement, and it is the one that gets skipped because nobody sees it
  locally.
- `Contents.json` must list exactly the files that exist. A stale entry is a build warning on some setups and
  a silent missing icon on others.

## 2. Android — two generations, both shipped

**Legacy (pre-8.0 launchers)** — `mipmap-*/ic_launcher.png`, opaque:

| Density | px |
|---|---|
| mdpi | 48 |
| hdpi | 72 |
| xhdpi | 96 |
| xxhdpi | 144 |
| xxxhdpi | 192 |

**Adaptive (8.0+)** — a **108 dp** canvas with a 72 dp visible area and 18 dp bleed on each edge:

| Density | canvas px | visible px |
|---|---|---|
| mdpi | 108 | 72 |
| hdpi | 162 | 108 |
| xhdpi | 216 | 144 |
| xxhdpi | 324 | 216 |
| xxxhdpi | 432 | 288 |

Two layers:

- `ic_launcher_background.png` — **opaque**, full bleed. A gradient or the brand's deep colour.
- `ic_launcher_foreground.png` — **alpha required**, artwork inside the central **72 dp** zone. The launcher
  can mask to a circle, a squircle, or a teardrop; anything outside the safe zone is eaten.

```xml
<!-- mipmap-anydpi-v26/ic_launcher.xml -->
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
  <background android:drawable="@mipmap/ic_launcher_background" />
  <foreground android:drawable="@mipmap/ic_launcher_foreground" />
  <monochrome android:drawable="@mipmap/ic_launcher_foreground" />
</adaptive-icon>
```

The `<monochrome>` layer is what themed icons use on Android 13+. Point it at the foreground only if the
foreground reads as a silhouette; a full-colour mark renders as a blob.

**Testing the safe zone:** do not test "pixels different from the corner colour" — the corner colour *is*
the background. Threshold on **luminance**: the bright mark must be inside the central 80 % (40 % radius).
That single change is the difference between a passing test and a test that passes on a broken icon.

## 3. Windows

```
mstile-150x150.png     150×150, opaque
browserconfig.xml      <square150x150logo>, <TileColor>
```

Windows also wants a `theme-color`-adjacent tile colour; put the brand's deep colour there so the tile does
not flash white while the image loads.

## 4. PWA manifest

```json
{
  "name": "…", "short_name": "…",
  "start_url": "/", "display": "standalone",
  "background_color": "#0B1220", "theme_color": "#0B1220",
  "lang": "ar", "dir": "rtl",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any" },
    { "src": "/icons/icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

- `lang`/`dir` are not decoration: they decide how the installed app's chrome and splash text render.
- `purpose: "maskable"` on the **same** 512 file as `any` is wrong: the maskable file has more padding and a
  full-bleed background.
- `short_name` is what appears under the icon; keep it under ~12 characters or it truncates.

## 5. Capacitor and native packaging

```
resources/
├── icon.png                 1024×1024, opaque    → source for every platform icon
├── icon-foreground.png      1024×1024, alpha     → adaptive foreground
├── icon-background.png      1024×1024, opaque    → adaptive background
├── splash.png               2732×2732, opaque
├── splash-dark.png          2732×2732, opaque
├── ios/AppIcon.appiconset/  explicit, committed
└── android/mipmap-*/        explicit, committed
```

Capacitor can generate the platform trees from the 1024 sources, but **commit the generated trees anyway**:

- a reviewer can see the icons in the diff;
- a conformance test can read real files instead of trusting the generator;
- a platform quirk (one density wrong) is visible without running the generator.

Splash: 2732 × 2732 opaque, mark + wordmark centred. It is cropped by the OS to wildly different aspect
ratios, so keep the content inside the central ~55 % and never put type at the edge. Flattening the splash to
opaque removed ~40 % of its bytes in the reference run (978 KB → 586 KB each) because the all-255 alpha
channel and its entropy disappeared.

## 6. The alpha posture table — memorise this

| Asset | Alpha | Consequence if wrong |
|---|---|---|
| `favicon.svg` | yes | a white box in the tab |
| `favicon-16/32/48.png` | yes | a white box in the tab |
| `favicon.ico` | yes | same |
| `mask-icon.svg` | yes (monochrome) | a colour silhouette blob |
| `apple-touch-icon.png` | **no** | black square on iOS |
| `icon-192/512.png` | **no** | black or white plate when installed |
| `icon-512-maskable.png` | **no** | mask edge shows the page behind it |
| `mstile-150x150.png` | **no** | white tile |
| iOS `AppIcon` set | **no** | store rejection / black icon |
| Android legacy `ic_launcher` | **no** | black plate on old launchers |
| Android adaptive **background** | **no** | mask edge artefacts |
| Android adaptive **foreground** | **yes** | the mask shows a solid rectangle |
| splash | **no** | black bars / doubled background |
| OG cards | **no** | black card in several previews |
| mark / wordmark runtime layers | **yes** | they must composite onto the card |
| card background master | as authored | it is artwork, not an asset |

## 7. Directory layout that survives review

```
<web-app>/
├── index.html                 ← the only place favicon/manifest links live
├── public/
│   ├── favicon.ico            ← root alias, same bytes as icons/
│   ├── site.webmanifest
│   ├── browserconfig.xml
│   ├── icons/                 ← every browser/OS/PWA icon
│   ├── og/                    ← static cards
│   └── brand/                 ← mark, wordmark, background, font (runtime layers)
└── src/assets/brand/
    ├── icon-master.png        ← the supplied master
    ├── card-background-master.png
    └── fonts/<family>-var.ttf + OFL.txt
```

- **Masters live in `src/assets/brand/`**, not in `public/`: they are inputs, not deliverables.
- **Runtime layers live in `public/brand/`** because the backend reads them by URL path at request time.
- **`favicon.ico` is duplicated at the root** on purpose; browsers request it blind.
- The generator writes *into* `public/` and never reads from it, except the layers it just wrote.

## 8. Native checklist

- [ ] iOS set complete incl. 1024 marketing, all opaque, no rounded corners
- [ ] `Contents.json` matches the files exactly
- [ ] Android legacy 48–192 + adaptive 108–432, foreground alpha, background opaque
- [ ] `mipmap-anydpi-v26` XML present for both launcher and round launcher
- [ ] Maskable safe zone verified by luminance, not by colour difference
- [ ] `mstile` + `browserconfig.xml` with a real tile colour
- [ ] Manifest `lang`/`dir`/`purpose`/`short_name` correct
- [ ] Splash opaque, content inside the central 55 %, dark variant if the app has one
- [ ] Capacitor platform trees committed
