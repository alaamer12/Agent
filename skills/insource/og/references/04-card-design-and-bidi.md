# 04 — Card design, bidi, and the copy contract

A social card is read at 300 px wide in a chat list and at 500 px in a feed. It is not a page: one idea, one
name, one line of support, one mark. Everything here exists to keep it legible at that size — and to keep it
*correct* in a bidirectional script.

## 1. Geometry

| Constant | Value | Why |
|---|---|---|
| canvas | 1200 × 630 | 1.91:1, the ratio every platform crops least |
| outer margin | 64–80 px | survives the rounded corners some clients add |
| safe area | canvas minus margin | no text or mark outside it |
| mark height | 15–22 % of canvas height | readable, not dominant |
| title | 64–96 px, 2 lines max | at 300 px display the title is ~20 px; below that it is decoration |
| support line | 28–36 px | one line, truncated with an ellipsis |
| badge / stat row | 22–26 px, uppercase or tracked | the third tier is optional; two tiers is the honest default |
| byte ceiling | ≤ 300 KB | preview-quality limit, not a platform limit |

Freeze these as `OG_LAYOUT` in the shared package — one object, imported by the composer and by the fidelity
test. A layout number written twice is a card that drifts.

**Safe area, not "full bleed".** Some clients letterbox, some crop to 1.91:1, some add a play button or a
domain chip at the bottom. Keep the bottom ~12 % free of anything load-bearing.

## 2. What goes on the card

```
┌──────────────────────────────────────────────┐
│  [mark]                        [family badge]│
│                                              │
│  Title line one                              │
│  Title line two                              │
│                                              │
│  Support line, one line, ellipsis            │
│                                              │
│  stat · stat · stat            [site name]   │
└──────────────────────────────────────────────┘
```

- **The mark is the logo's symbol**, never the rounded app icon. An app icon already carries its own
  background and corner radius; on a card it looks pasted on.
- **The wordmark is the logo's logotype as pixels.** Never re-typeset a logotype: its spacing is the brand.
- **One family per card.** A listing card, a category card, a profile card - each with its own badge key, not a
  generic "site" badge.
- **The stat row is optional and must be true.** If a family has no meaningful number, drop the row; a
  fabricated count on a share card is a product bug that ships to every chat.

## 3. Bidi: the law, the mechanism, and the proof

**The law: one script run per line.** Arabic and Latin never share a line on a card.

Why a law and not a library call: resvg emits a line's runs in **logical** order; Chromium (and every
browser) applies the Unicode Bidirectional Algorithm and emits them in **visual** order. Measured on the
reference artwork, pure-Arabic ink boxes matched Chromium within 1 px, and mixed-script ink boxes did not.
A bidi pass can be added for *positioning* decisions, but it cannot make a single mixed line look right at
every length without a full UBA implementation in the rasteriser — and the rasteriser is the thing you
cannot replace.

So: split, don't fix.

```
splitScriptRuns(text) -> [{ text, script }]
    script = arabic | latin | other, per grapheme cluster
    adjacent clusters of the same class merge into one run
    digits and punctuation inherit the run they sit inside (a number inside an Arabic name stays Arabic)
```

Then place **one run per line**, and mirror the *block* for RTL rather than reordering characters:

```
<g transform="translate(1200,0) scale(-1,1)">   // mirror the background artwork
<text text-anchor="end" x="1128">…</text>       // right-align the RTL text
```

Mirroring the background is what makes the EN card the same design, not a different one: the bright ribbon
ends up on the opposite side, so the mark and text must move with it.

**`bidi-js` earns its place for the pieces that are not text layout:** resolving the paragraph level,
detecting the direction of an entity name, and ordering a mixed string for a *single-line* context such as
an `og:title`. It is not used to lay out the card.

### Name fitting

Entity names arrive from a database and have no length contract. The sequence:

1. Try the full name at the title size.
2. Wrap at a **word boundary** (`wrapAtWordBoundary`), max 2 lines.
3. Still too long → reduce to the "long name" size once.
4. Still too long → truncate at the last whole word that fits, append `…`.
5. Never truncate mid-word in Arabic: the joining form changes and the fragment reads as a different word.

Measure with the font's real metrics (advance width from the renderer), not `length * fontSize * 0.5`. An
Arabic glyph run is typically narrower than the Latin heuristic predicts, and the heuristic produces
needlessly shortened names.

## 4. Contrast and the bright-ribbon problem

The reference artwork has a bright ribbon crossing a corner. Text placed there is unreadable and no amount
of shadow fixes it at 300 px.

- **Measure the artwork's luminance map** and place text and mark in the dark region. This is a design
  constraint on the master, recorded in the ADR.
- If the dark region is too small, add a **scrim**: a soft linear gradient in the brand's deep colour, from
  0 % to ~70 % alpha, over the text half. A scrim is honest; a drop shadow on 24 px text is not.
- The badge sits on the *quiet* corner, away from the bright element, even if that means mirroring the
  layout between locales.

## 5. Static cards: one per family, per locale

The static set is the layer that must always exist, because it is the degradation target for everything
else.

```
og-{family}-{locale}.png     for every family × every shipped locale
og-default-{locale}.png      the last resort
```

Reference shape from one run: a family per content kind (a home card, a listing kind, a detail kind, a person
kind, a policy kind), two locales, plus one default per locale. That is `families × locales + locales` files —
five and two gives twelve. The default card may legitimately be byte-identical to the home card: the default
*is* the home message, and a duplicate file is cheaper than a second design to maintain.

**Membership, not a list.** A family is not "one of the eight"; it is *any content kind that passes all four
tests*: it has a static card per locale, a badge copy key, a resolver (what a slug means for it), and a route
in the contract test. Add a family by adding those four in one change — never by borrowing another family's
badge "for now", which is how a legal page ends up wearing a product badge.

**Extension.** The matrix grows in exactly two directions: a new family (four things above) or a new locale
(one card per family, plus its badge copy). Anything else — a per-entity static card, a per-route card — is
the dynamic layer's job, not the static set's.

Generation is deterministic: same model → same SVG → same pixels → same bytes. That is what lets `--check`
compare bytes instead of "looks similar".

## 6. The palette contract (two roles, one module)

```
BRAND_MARK    // measured from the artwork; icons and cards; NEVER re-toned
BRAND_ACCENT  // the UI call-to-action colour; mirrored from the stylesheet
BRAND         // composed tokens for surfaces
OG_CARD       // ditherStrength, paletteLadder, maxBytes, geometry
```

The drift that this prevents: someone "harmonises" the icon with the new button colour, the icons no longer
match the logo, and nobody notices for a year. Lock it with a test that parses the stylesheet and asserts
the accent token still equals the module's value — see `08-verification-gates.md` §2.

## 7. Copy: keys, never strings

Every word on a card resolves through a key:

| Key | Content |
|---|---|
| `og.site_name` | the product name |
| `og.tagline` | the support line |
| `og.badge.{family}` | the family badge |
| `og.stat.{name}` | a stat label |
| entity name | from the entity's own table, never a copy key |

One resolver, two callers (static generator and runtime renderer), so a seeded card and a live card cannot
disagree. A literal string in the composer is a defect, and in most projects it is also a rulebook
violation — the same check that catches hardcoded UI copy should catch it here.

## 8. Card review checklist

- [ ] Readable at 300 px wide (zoom the PNG out before approving)
- [ ] Title ≤ 2 lines, no mid-word truncation in Arabic
- [ ] One script run per line; no mixed lines anywhere
- [ ] Mark is the symbol, not the app icon; wordmark is the logotype, not type
- [ ] Text and mark avoid the bright region of the artwork
- [ ] RTL and LTR cards are the *same* design mirrored, not two designs
- [ ] Badge and stats are true for that entity
- [ ] ≤ 300 KB, opaque, 1200 × 630
- [ ] The default card exists and looks deliberate
