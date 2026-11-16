# Arabic and other context-shaped scripts

Read this when the user wants Arabic (or any script where a letter's drawing
depends on its position in the word). This covers the **positional forms**
Arabic needs; it does not cover tashkeel (vowel marks), lam-alif ligatures, or
Indic conjuncts — see the end of the file.

## The problem: a letter is not one glyph

A Latin `a` is always the same drawing. An Arabic letter changes shape by where
it sits in a word, so one Unicode codepoint maps to up to four glyphs:

| Form | Joins | When |
|------|-------|------|
| isolated (`isol`) | neither | alone, or a non-joiner between two non-joiners |
| final (`fina`) | from the right | at the end of a connected run |
| initial (`init`) | to the left | at the start of a connected run |
| medial (`medi`) | both | in the middle of a connected run |

Six letters (ا د ذ ر ز و, plus the forms ة ى آ أ إ ؤ) only join from the right,
so they have **isolated and final only**. HarfBuzz never asks them for
initial/medial, so you do not have to draw those.

## How the build handles it

The builder never guesses the form at render time — the **text renderer**
(HarfBuzz, in every browser and modern editor) picks the form. The font's job is
to (1) expose one glyph per codepoint (the isolated form) through `cmap`, and
(2) carry a **GSUB** table with `init`/`medi`/`fina` features that substitute the
contextual forms. `build_font.py` does both from file naming alone:

```
uni0628.svg          -> U+0628 isolated; this is what cmap points at
uni0628_init.svg     -> U+0628 initial form
uni0628_medi.svg     -> U+0628 medial form
uni0628_fina.svg     -> U+0628 final form
```

For every codepoint that has any suffixed form, the build emits GSUB rules like
`feature init { sub uni0628 by uni0628_init; } init;` (compiled with feaLib). A
folder with no `_init/_medi/_fina` files builds exactly as before, so Latin fonts
are unaffected.

## The joining line: a shared spine

Arabic letters connect through a horizontal stroke at one fixed height. The
whole trick is that **every form ends its connectors at the same y (the spine)
and reaches the glyph's left/right edge**, so when HarfBuzz places glyphs
edge-to-edge the strokes meet. Requirements:

- Build with `--side-bearing 0 --tracking 0`. Advance = the drawing's own width,
  so the spine reaches the exact edges and there is no gap at the seam.
- Give every glyph the same spine height and the same `--baseline`.
- A form that does not connect on a side simply stops its stroke short of that
  edge (a curl or a terminal); it does not reach x=0 or x=W.

`examples/arabic/make_letters.py` shows the data-driven way: one skeleton per
letter plus a dot pattern, and `build_forms()` derives the forms by attaching or
detaching a spine stub. Adding a letter is one table row, not four hand-drawn files.

## Grid and metrics for Arabic

Use a taller viewBox than the Latin default because Arabic has deep descenders
(j ح خ ع غ ق ن ي) and high ascenders (ا ل ك):

```
viewBox="0 0 W 1000"   baseline y=700   -> 700 up, 300 down
build: --baseline 700 --ascender 800 --descender -400 --side-bearing 0 --tracking 0
```

Dots go above or below the body; keep them inside the viewBox height or widen
`--descender`/`--ascender` so nothing is clipped.

## Verifying: you must shape the text

PIL/FreeType render each character in isolation and do **not** apply GSUB or
reverse RTL, so a naive specimen shows unjoined boxes. `check_font.py` renders
its specimen through **HarfBuzz** (`pip install uharfbuzz`) so the specimen PNG
shows the real connected, right-to-left output. Without uharfbuzz it warns and
falls back to unshaped output — which will look broken for Arabic and is not a
font bug. Always judge the shaped PNG.

**Gotcha when writing your own shaped renderer:** HarfBuzz returns glyphs in
*visual* order (already reversed for RTL), so you must lay them out left-to-right
in buffer order. Starting the pen at the right and moving left for RTL mirrors the
word — the letters look joined but read backwards. Cross-check against a second
shaping engine (a browser, or Windows WPF/DirectWrite) before trusting one render.

## Still out of scope for Arabic

| Need | Why not here | How |
|------|--------------|-----|
| Tashkeel (harakat: fatha, damma, kasra ...) | Combining marks need GPOS anchor positioning + a `mark` attachment, not single substitution | Hand-written feaLib mark anchors; draw marks as separate combining glyphs (U+064B+) |
| Lam-alif ligature (لا لآ for) | Requires a `liga`/`rlig` multi-glyph substitution keyed on a pair | feaLib `sub uni0644 uni0627 by lam_alef;` with a hand-drawn pair glyph |
| Kashida / tatweel (U+0640) elongation | A `calt`/stretch behavior | separate glyph + feature |
| Indic, Hebrew, Thai joining | Different feature sets and shaping models | the same file-naming + feaLib approach extends, but the spine/geometry rules are script-specific |

For a first Arabic font, positional forms (this file) already produce connected,
legible words; add tashkeel and lam-alif only when the user asks.
