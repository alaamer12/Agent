# 07 — Fonts: acquisition, variables, licensing, proof

The renderer is only as good as the font file you hand it. Two failure modes dominate: the font is not
there at runtime (boxes instead of Arabic), and the font is there but the licence did not ship with it.

## 1. Why a font file, not the system

- A container has **no** system fonts. `loadSystemFonts: true` works on the developer's machine and fails in
  production — the worst possible failure distribution.
- The same string must render identically on the build machine, CI, and the server, or the fidelity test is
  meaningless.
- Arabic needs a font with real Arabic coverage *and* shaping tables (GSUB/GPOS). Many "Arabic-looking" fonts
  ship presentation forms without the joining logic; HarfBuzz then produces disconnected letters.

So: commit the TTF, set `loadSystemFonts: false`, and let a missing file be a hard, visible failure.

## 2. Choosing the family

Criteria, in order:

1. **Script coverage** — the product's actual scripts, including the ones you forgot (digits, diacritics).
2. **Variable weight axis** — one file serves title (700) and support line (400) without shipping two files.
3. **Personality match** — a geometric Latin face next to a calligraphic Arabic face reads as two brands.
   If the product is Arabic-first, choose the Arabic face and let it carry the Latin.
4. **Licence** — OFL/Apache preferred; anything "free for personal use" is a defect.
5. **File size** — a full variable Arabic font is 200–600 KB; acceptable for a server, not for a web bundle.

A choice that satisfies all five: an Arabic-first variable family with Latin coverage under OFL. Several
exist on Google Fonts (Changa is one common default; check the `wght` range and Latin quality before
committing). One file — `<family>-var.ttf`, committed with `OFL.txt` — serves every card in every locale.

## 3. Getting a variable font

| Source | What you get | Notes |
|---|---|---|
| Google Fonts UI → "Download family" | a zip with **static** instances per weight | Usually *not* the variable file |
| `github.com/google/fonts` → `ofl/<family>/` | `Family[wght].ttf` (variable) + `OFL.txt` | The reliable route; the `[...]` in the filename is the variable marker |
| Font source repo (e.g. the designer's) | variable TTF/OTF + sources | Best when it exists; check the release assets |
| `fonts.gstatic.com` (the CSS URL) | **WOFF2**, subsetted | Not usable: resvg needs TTF/OTF, and the subset may lack the script you need |

Steps that actually work:

```
1. Find the family directory in github.com/google/fonts (ofl/ or apache/).
2. Download the file whose name contains [wght] (or [wght,wdth]) and the LICENSE/OFL.txt beside it.
3. Verify it is a real font, not an HTML error page:
      first 4 bytes: 00 01 00 00  (TrueType)  or  'OTTO'  (CFF)  or  'true'  (legacy)
      `name` table present, `fvar` table present for a variable font
4. Commit the TTF and the licence together, same directory.
```

If you can only find a WOFF2 (for example, you must match a web font exactly), decompress it — do not
hand-edit bytes:

```
python -m pip install fonttools brotli
python -c "from fontTools.ttLib import TTFont; f=TTFont('x.woff2'); f.flavor=None; f.save('x.ttf')"
```

## 4. Variable fonts: axes, instancing, and when to flatten

A variable font carries axes (`wght`, `wdth`, `slnt`, `opsz`). Two ways to use it:

**A. Keep it variable, select by `font-weight` in the SVG.** Simplest, one file, the renderer picks the
instance. Use this by default — it is why you chose a variable font.

**B. Instance it down to the weights you actually use.** Smaller file, no axis surprises:

```
python -m fontTools.varLib.instancer <family>-var.ttf wght=400 -o <family>-400.ttf
python -m fontTools.varLib.instancer <family>-var.ttf wght=700 -o <family>-700.ttf
```

Do **B** only when the file size matters (a client bundle, a mobile shell). For a server-side renderer, one
variable file is easier to reason about and to test.

**Do not subset an Arabic font** without keeping the shaping tables. Subsetting that strips GSUB/GPOS
produces disconnected letters that look *almost* right in a Latin review and completely wrong to an Arabic
reader. If you must subset, use `--layout-features='*'` and re-run the ink-box probe afterwards.

## 5. Proving the font is embedded

A test, not a claim:

```ts
// with the font
const withFont = render(model)          // expect non-empty ink, expected width
// without the font
const withoutFont = render(model, { fontFiles: [] })   // expect 0×0 ink box
```

If `fontFiles: []` still renders text, something else supplied the glyphs (a system font, a cached renderer,
a fallback family) and the test is passing for the wrong reason. The reference run asserted exactly this:
empty `fontFiles` → a **0 × 0** ink box.

Also assert the file is *loaded* by the production path: the layer loader must fail loudly when the TTF is
missing, not fall back to a default family.

## 6. Licensing duties

- **Ship the licence text with the font**, in the same directory, named as the licence (`OFL.txt`). The
  repository is the distribution.
- **OFL**: keep the copyright notice; do not sell the font by itself; if the font declares a Reserved Font
  Name, a modified version must be renamed. Subsetting and instancing count as modification for the RFN
  clause in most readings — rename if you instance.
- **Apache-2.0**: include the NOTICE if present.
- **Record the choice in the ADR**: family, source URL, licence, axes, file size, and why this face.
- Never commit a font whose licence you cannot name. "It was in the project already" is not a licence.

## 7. Fallback chain

Even with one embedded family, declare a chain so a missing glyph degrades in a controlled way:

```
defaultFontFamily: '<BrandFace>'
fontFiles: ['…/<family>-var.ttf']
loadSystemFonts: false
```

If a card needs a second face (a display face for the wordmark — **don't**: use the wordmark image), it goes
in `fontFiles` as well. The renderer does not fetch anything over the network, ever.

## 8. Font checklist

- [ ] One committed TTF/OTF, real font magic bytes, `fvar` present if variable
- [ ] Licence file beside it, licence named in the ADR
- [ ] `loadSystemFonts: false`
- [ ] Ink-box probe passed on the hardest script in the product
- [ ] `fontFiles: []` contrast test asserts 0 × 0 (proves the file is what renders)
- [ ] No WOFF2 in the runtime path
- [ ] No subsetting that strips Arabic shaping tables
- [ ] Font served to the client only if the UI actually uses it (the card font is a server asset)
