# Troubleshooting

Start with `python scripts/check_font.py Font.ttf --png specimen.png` and look at
the image. Most entries below show up as a checker message or are visible in the
specimen. Search this file for the message text or the symptom.

| Symptom | Cause | Fix |
|---------|-------|-----|
| Letters hang below the line, are cut off, or checker says "sits entirely below the baseline" | The y-flip had no baseline offset (y' = -y puts the whole glyph under y=0), or `--baseline` does not match where the drawings put the baseline. | Use `build_font.py`, which offsets by the baseline. For custom code: `font_y = (baseline - svg_y) * scale`. For descenders pass `--baseline` explicitly. |
| Small notches or holes where two strokes cross or meet | Several shapes were merged into one glyph under TrueType's non-zero winding rule. Overlapping shapes drawn in opposite directions cancel each other. | `build_font.py` unions every element with skia-pathops, so just use it. In custom code, union with `pathops.op(a, b, pathops.PathOp.UNION)` before writing the glyph. |
| Counter (the hole in A, B, O, R) is filled in | The hole was drawn as a white shape, or the path lacks `fill-rule="evenodd"`. | Put the hole in the same `<path>` as an extra sub-contour and add `fill-rule="evenodd"` (see `assets/templates/uni0041.svg`). |
| A glyph is missing; build prints "skip X.svg: cannot derive a character" | File name does not map to a character. | Rename to `uniXXXX.svg` (hex code point). |
| Only one of `a` / `A` exists, or one overwrote the other | Windows and macOS treat `a.svg` and `A.svg` as the same file. | Name by code point: `uni0061.svg`, `uni0041.svg`. |
| "duplicate codepoint U+XXXX" | Two files map to one character (for example `A.svg` and `uni0041.svg`). | Delete or rename one. |
| A hollow rectangle shows instead of a letter | That character has no glyph, so the font's `.notdef` box appears. | Add the SVG, or check the character is in the "characters:" list printed by `check_font.py`. |
| `X.svg: <ErrorType>: ...` from the build | The SVG has no `viewBox` or `width`/`height`, or an unsupported `transform` function. | Add a viewBox. Supported transform functions: translate, scale, rotate, skewX, skewY, matrix. |
| Shape in the SVG is missing from the glyph | It was stroke-only (`fill="none"`), inside `<defs>`, `<use>`, a mask or clip path, or inherits `fill="none"` from a group. | Convert strokes to outlines and expand `<use>`; see `svg-requirements.md`. |
| Warning "different viewBox heights" | Files were drawn on different-height artboards, so baselines disagree. | Re-export at one height, or pass `--baseline` and make every drawing share it. |
| Warning "above --ascender" / "below --descender" | Drawing extends past the reserved line space; some programs will clip it. | Raise `--ascender` or lower `--descender`. |
| Pairs such as AV or To look too far apart | Uniform side bearings cannot account for diagonal shapes. | Add kerning (`extending.md`). Do not widen all bearings. |
| Specimen image is cropped or letters touch the edge | The canvas was a fixed size. | `check_font.py` sizes the canvas from the font's metrics; use it. |
| `.woff2` skipped | The `brotli` package is missing. | `pip install brotli`, then rebuild with `--web`. |
| Reinstalled font still looks old in an app | Operating systems and apps cache fonts by family name. | Uninstall the old file, restart the app, then install the new one; changing the `--family` name for test builds avoids the clash. |
