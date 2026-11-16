# Localizing external assets

A project that loads fonts from a font CDN, icons from an icon CDN, or images from a media host depends
on someone else's uptime, privacy policy and URL stability. `localize.py` copies those files into the
project and verifies what arrived.

## The workflow

1. **Find what is external.** `inventory.py` lists http(s) URLs ending in asset extensions found in
   source files. It does not catch webfont CSS endpoints (`fonts.googleapis.com/css2?...`) - those are
   CSS, not an asset; handle them as step 4.
2. **Write a manifest** (`vendor-assets.txt`):

   ```text
   # URL                                              destination (optional)
   https://cdn.example.com/icons/arrow.svg            icons/arrow.svg
   https://cdn.example.com/fonts/Inter-Regular.woff2   fonts/Inter-Regular.woff2
   https://cdn.example.com/media/hero.jpg
   ```

3. **Fetch:** `localize.py --manifest vendor-assets.txt --out assets/vendor`
   - Each file is sniffed after download: an HTML error page saved as `.woff2` is reported (`WARN`),
     not silently kept.
   - Failures do not stop the batch; the summary counts them.
4. **Webfont CSS endpoints:** download the CSS first (it is a stylesheet, not an asset), then fetch the
   font files it references - or use a font package manager for the ecosystem. Keep the `@font-face`
   rules local too, or the browser still asks the CDN for them.
5. **Update references** to the local paths (same rules as `06-references-and-code.md`) and remove the
   external URLs from `inventory.py`'s report as a check.

## Licensing - local is not licensed

Downloading a file does not grant rights to redistribute it. Keep the license file the source ships
(for fonts, the OFL/APACHE/etc. text), keep the attribution required by the license, and check the
asset's terms before a public release. When a license is unclear, report it to the user rather than
shipping the file.

## Icon fonts vs SVG icons

- An **icon font** is a font file: localize it as a `.woff2`, keep its CSS, and accept that it renders
  glyphs, not images.
- **SVG icons** are individual files (or a sprite): localize each one; do not convert a font to SVG or
  the reverse without the icon set's official source.

## When NOT to localize

- Assets behind a license that forbids redistribution (use the provider's required embed instead).
- Truly dynamic media (user-uploaded content served by a service) - that is application infrastructure,
  not a static asset.
- Anything that must stay in sync with a third party's live data.

## Tested end-to-end: an HTML page on real CDNs

The flow below was run against a real page using Google Fonts and jsDelivr, and is the reference
procedure:

```text
1. inventory.py --root site --assets site
   -> external: fonts.googleapis.com/css2?..., fonts.gstatic.com/....woff2,
      cdn.jsdelivr.net/.../home.svg, cdn.jsdelivr.net/.../1f600.png

2. vendor-assets.txt:
   https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap   css/inter.css
   https://cdn.jsdelivr.net/npm/@material-design-icons/svg@0.14.15/filled/home.svg  icons/home.svg
   https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f600.png        images/emoji.png

3. localize.py --manifest vendor-assets.txt --out site/static
   -> css (4.9 KB), svg (136 B), png (806 B), all sniffed correctly

4. parse the downloaded CSS for its font URLs, fetch each woff2:
   localize.py --manifest vendor-assets-fonts.txt --out site/static
   -> 7 subset woff2 files, ~10-24 KB each

5. rewrite references: stylesheet href -> static/css/inter.css; each url(https://fonts.gstatic.com/...)
   in the CSS -> url(../fonts/<file>.woff2); image/icon paths -> their local files.

6. inventory.py again -> external asset URLs: 0, unreferenced: 0.
```

**The gotcha found in that test:** font CDNs negotiate the format by **User-Agent**. The first run
downloaded the CSS with a generic UA and got `format('truetype')` URLs - 2 files at ~325 KB each
instead of WOFF2 subsets at 10-24 KB. `localize.py` now defaults to a browser UA (override with
`--user-agent`). If a CSS already downloaded as TTF, delete it and re-fetch; do not "optimize" the
TTFs.

**What localize does not do:** it downloads, it does not rewrite your HTML/CSS. Step 5 is a normal
reference update (grep the URL, replace with the local path) - the protocol in
`06-references-and-code.md`, reviewed like code.

## Tested with provider catalogs (the /fahlwy data)

A second end-to-end run used the provider catalogue from the `fahlwy` skill (keyless image CDNs) with
real URLs, including URLs that carry no filename extension:

```text
# vendor-images.txt
https://picsum.photos/800/1400                                              photos/random-photo
https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&h=1400&fit=crop  photos/unsplash-lake
https://images.pexels.com/photos/1108099/pexels-photo-1108099.jpeg?auto=compress&cs=tinysrgb&w=800  photos/pexels-dog
```

```text
$ localize.py --manifest vendor-images.txt --out assets
ok  .../800/1400 -> assets/photos/random-photo.jpg (jpg, 46904 bytes) [added .jpg]
ok  .../photo-1506744038136-... -> assets/photos/unsplash-lake.jpg (jpg, 188963 bytes) [added .jpg]
ok  .../pexels-photo-1108099.jpeg -> assets/photos/pexels-dog.jpg (jpg, 53996 bytes) [added .jpg]
done: 3 fetched, 0 failed
```

What that test changed: **extensionless URLs and destinations now get the sniffed extension** (a
`photo` file with JPEG bytes is unfindable by name; `photo.jpg` is not), and a wrong extension is
corrected with a note. The images were opened and verified visually after download.

Provider notes that matter when localizing from a catalog:

- **Rights are not bundled with the bytes.** Picsum serves Unsplash photos; Unsplash/Pexels licenses
  have conditions (attribution, no reselling unmodified copies). Keep the license/attribution the
  provider requires, or use a provider whose terms fit the project.
- **Picsum serves a random subject** (`/800/1400`) - good for placeholders, wrong for topical imagery;
  pin an id (`/id/<n>/W/H`) when the subject matters.
- CDN URLs with query parameters (`?w=800&fit=crop`) download the transformed file, not the original -
  that is usually what you want for a local asset; record the requested size in the filename or notes.
