# Extending a font, and what is out of scope

Read this when the user wants more than a basic character set, kerning, web
formats, or something this skill deliberately does not do.

## Contents
- Adding characters
- Kerning
- Web formats
- Out of scope

## Adding characters

The builder includes every `uniXXXX.svg` in the folder, so extending a font means
adding drawings and rebuilding. Use the same grid for every new glyph.

1. **Lowercase.** Draw bodies at the x-height (about 500 on the default grid, so
   0.71 of cap height) and ascenders (b d f h k l) to cap height or slightly above.
   For descenders (g j p q y) use a taller viewBox and `--baseline`
   (see `svg-requirements.md`). With `glyph_kit`:
   `write_glyph("svgs", "o", [...])` writes `uni006F.svg`.
2. **Digits and punctuation.** Same naming: `uni0031.svg` for "1", `uni002E.svg` for ".".
   Punctuation sits on the baseline (period, comma) or at x-height (colon dots);
   check it in the specimen with real text like `"Rate: 4.5, ok!"`.
3. **Accented letters.** Draw them as full glyphs (`uni00E9.svg` for é). The
   builder has no anchor or composite-glyph support, so it cannot combine a base
   letter with a floating accent.
4. Rebuild, then run `check_font.py` with a `--text` string that uses the new
   characters. Each new character must appear in its "characters:" list.

Plan the set before drawing: write the full list of characters first, then
generate or draw them in one pass rather than piecemeal.

## Kerning

Uniform side bearings leave diagonal pairs (AV, To, LT) too loose. Kerning adds a
per-pair adjustment in the font's GPOS table. Apply it as a post-processing step
on the built TTF with fontTools' feature compiler:

```python
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

font = TTFont("MyFont.ttf")
addOpenTypeFeaturesFromString(font, """
feature kern {
    pos A V -60;
    pos T O -40;
} kern;
""")
font.save("MyFont-kerned.ttf")
```

Glyph names in `pos` lines are the font's glyph names (`A`, `V`, `zero`,
`uni00E9`). Values are font units; negative moves the pair closer. This was
verified to produce a GPOS table. Whether the kerning shows depends on the
application: browsers and modern editors apply it; check in the target app.
Choose pairs by looking at the specimen, a few at a time; typical starting values
are -30 to -80 on a 1000-unit em.

## Web formats

`--web` writes `.woff` and, when the `brotli` package is installed, `.woff2`
beside the `.ttf`. Reference them in CSS:

```css
@font-face {
  font-family: "MyFont";
  src: url("MyFont.woff2") format("woff2"), url("MyFont.woff") format("woff");
}
```

## Out of scope

This skill produces a monochrome TrueType font. It does not cover, and should not
be stretched to cover:

| Not covered | Use instead |
|-------------|-------------|
| Icon fonts from existing SVG icon sets | IcoMoon, Fontello, or the `svgtofont` npm package |
| Working on an existing font: subsetting, or converting TTF to OTF | `pyftsubset` (ships with fontTools) for subsetting; FontForge or a dedicated converter for TTF/OTF |
| CFF/OpenType (.otf) outlines | A separate fontTools CFF build path; not implemented here |
| Color fonts (COLR/CPAL, SVG-in-OpenType, emoji) | Dedicated color-font toolchains such as nanoemoji |
| Variable fonts and multi-master interpolation | fontmake with designspace sources |
| Hinting / ttfautohint, screen-size optimization | ttfautohint after building |
| Ligatures, tashkeel (Arabic vowel marks), Indic conjuncts | Hand-written OpenType feature code (feaLib); needs design decisions this skill does not make. **Arabic positional forms (isolated/initial/medial/final) ARE supported** — see `arabic-shaping.md`. |
| Auto-tracing a raster image or photo into glyphs | Trace to SVG first (Inkscape, potrace), then use this skill |
| Licensing or trademark clearance of the letterforms | The user's responsibility; do not copy commercial typefaces |
