# Naming and organization

The filename and the folder are the asset's documentation. A future agent (or person) finds an asset by
name first, path second; both should answer "what is this and where does it belong".

## Naming rules

| Rule | Good | Bad |
|---|---|---|
| Describe content, not sequence | `hero-launch-banner.webp` | `one.png`, `image-3.png` |
| kebab-case (or the project's own convention) | `app-icon-1024.png` | `App Icon Final FINAL.png` |
| No version suffixes in the name unless the version is real | `logo-2024.svg` for a brand refresh | `logo-v2-final2.svg` |
| State size/scale when it is the point | `logo@2x.png`, `avatar-128.png` | `small.png`, `big.png` |
| Keep the extension truthful | correct extension, correct format | PNG saved as `.jpg` (`convert.py --fix`) |

Renaming is a shell job (`mv` / `Move-Item`); what leaves dead paths behind is renaming without updating
the references - use `references/06-references-and-code.md` for the protocol.

## The brand vs content separation

Two kinds of images that look alike and must not mix:

- **Brand assets** - logo, app icon, splash, favicon, OG template, brand illustrations. Owned by the
  product's identity; rarely reference-specific.
- **Content assets** - images the application itself ships or displays: gallery samples, category
  art, placeholder photography, a game's sprites. Owned by the feature that uses them.

Keep them in different folders (`brand/` vs `images/` or `assets/content/`) and never restyle a content
image to fit the brand, or the reverse. A shared CDN folder with both is how a feature's photos end up
on the marketing page.

## One kind per home

Suggested layout when the project has none (adapt to the project's own):

```
assets/
├── brand/        logo.svg, logo-1024.png, og-template.png
├── icons/        app and UI icons (SVG preferred; favicon.ico lives with web root)
├── images/       content photos and illustrations
├── fonts/        self-hosted font files + licenses
└── media/        video/audio
```

Platform conventions win when they exist (Android `res/mipmap-*`, iOS asset catalogs, web `public/`).

## The same rules cover every medium

Naming, brand-vs-content separation and "one kind per home" apply to fonts (`Inter-Regular.woff2`),
audio (`click-success.mp3`), video (`launch-teaser-1080p.mp4`) and documents (`handbook-2026.pdf`) -
not only images. There is no per-medium script for those files; there is one naming/organization rule
and `inventory.py` to audit it (it reports each category's file count and total size).

## SVG and PNG are different assets

- The SVG is the source of truth for vectors: edit it, derive rasters from it.
- The PNG exports are build outputs for platforms that need raster - do not hand-edit an export.
- "The same picture in two formats" is not a duplicate to delete; it is a source/derivative pair.
  `inventory.py` reports identical **bytes**, which catches the real duplicates (the same file saved
  twice under two names), not this pair.

## Auditing an existing folder

1. `inventory.py --root . --assets <folders>` - duplicates, unreferenced files, external URLs.
2. Unreferenced is a lead, not a verdict: names assembled at runtime look unreferenced. Check the
   feature that might build the name before deleting anything.
3. Rename toward descriptive names in batches, updating references in the same change (see `06`).
4. Never delete an asset the inventory flags without confirming nothing loads it dynamically.
