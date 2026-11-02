# How assets are referenced - and how renames stay safe

An asset is a file plus every place the code names it. This page maps the common reference styles and
the protocol for changing a name without breaking the app.

## Reference styles by platform (examples, not a closed list)

| Platform / stack | Typical reference | Where it lives |
|---|---|---|
| Web HTML/CSS | `<img src="images/hero.webp">`, `url('../images/hero.webp')` | markup, stylesheets |
| Web bundlers (Vite/Webpack/etc.) | `import hero from './hero.webp'` or a `public/` path | module imports, config |
| Android | `@drawable/ic_logo`, `R.drawable.ic_logo` | `res/` folders, XML, code |
| iOS | asset catalog names (`AppIcon`, image sets) | `Assets.xcassets`, Interface Builder, code |
| Flutter | `assets/images/hero.png` declared in `pubspec.yaml` | manifest + `Image.asset()` |
| .NET (WPF/MAUI) | `pack://application:.../Assets/logo.png`, `MauiImage` build items | XAML, project file |
| Desktop GTK/Qt | resource paths or compiled resource bundles | resource files |
| Static site generators | relative paths from the content file | Markdown/HTML |

The rename script scans **text files** for the old filename and replaces plain matches; it does not
rewrite binary resources (compiled bundles, `.car`/`.resx` binaries) - those need the platform tool.

## The rename protocol

1. `inventory.py` - confirm how many files mention the asset and whether anything builds its name
   dynamically.
2. **Find the references before moving anything** - grep the old basename across the project
   (`rg -n "old-name\.png"`, or the editor's project search). This list is the change surface.
3. **Move the file** with the shell (`mv old new`, `Move-Item old new`) - no special tool needed; the
   file system move is trivial, the references are the work.
4. **Update every reference** in the same change - paths, imports, resource ids, manifest entries -
   then review the diff as you would code.
5. Rebuild/run the app; a renamed asset that no longer loads shows as a broken image/resource.
6. `inventory.py` again - the old name should no longer appear as a reference, and the file should no
   longer be unreferenced.

## Broken-reference symptoms

- Web: broken image icon, 404 in the network panel, a CSS `url()` that silently paints nothing.
- Android: build error for a missing resource, or a resource that resolves because the old copy still
  exists (delete the old copy in the same change).
- iOS: an asset that does not appear in the catalog build.
- Flutter: `Unable to load asset` at runtime - the `pubspec.yaml` entry is a reference too.

## Dynamic references - the limit

Names assembled at runtime (`"icon-" + state + ".svg"`, manifest-driven galleries, database-stored
paths) cannot be found by textual search. When the inventory flags an unreferenced file, check for
these patterns before deleting anything; when renaming, grep for the prefix/suffix fragments too and
update the code that builds the name.

## What this skill may edit in code

Allowed: the paths that name assets - a `<img src>`, a `url()`, an import, a resource id, a manifest
entry - in the same change that renames/moves the file.

Not allowed: feature logic, styling systems, component structure, anything unrelated to the asset
path. If the correct update needs a code change beyond a path, hand it to the implementation skill.
