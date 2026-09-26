# scripts/

`accessible-audit.mjs` — renders a UI in headless Chrome and measures what this skill's
moves are supposed to have achieved, so "it looks calmer" is a number you can compare
against a reference instead of a claim you have to trust.

No npm dependencies. Needs Node ≥ 22 (uses the built-in global `WebSocket` to talk
Chrome DevTools Protocol) and any headless Chrome/Chromium binary.

## Usage

```
node scripts/accessible-audit.mjs <file-or-url> [options]

  --out <path>        write the full JSON report (default: OS temp dir)
  --shot <path>       write a PNG of the rendered viewport
  --chrome <path>     Chrome binary, if auto-discovery fails
  --width / --height  viewport, default 1440x1000
  --exclude "<sel>"   comma-separated selectors to treat as low-dwell chrome
  --baseline <json>   print a per-metric delta against a saved report
  --json              dump raw JSON instead of the scorecard
```

Exit code `0` = clean, `1` = findings above threshold, `2` = usage/runtime error.

### Chrome auto-discovery

Looks for `$CHROME_PATH`, then Playwright's cache (`~/.cache/ms-playwright/chromium*/…`),
then common system paths. Override with `--chrome`:

```
--chrome "$HOME/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome"
```

### Typical flow

```bash
# 1. measure the thing you just built
node scripts/accessible-audit.mjs build/redesign.html --out after.json --shot after.png

# 2. look at after.png. The numbers cannot see clipped text, wrapped filter rows,
#    a sticky bar covering content, or a heading that reads as decoration.

# 3. if the person already approved an output as the target, diff against it
node scripts/accessible-audit.mjs build/next-page.html --baseline after.json
```

## accessible-contrast.mjs — measured, not declared, contrast

```
node scripts/accessible-contrast.mjs <file.html|url> [--width 1440] [--height 1000]
                                      [--fails-only] [--json] [--csv out.csv] [--chrome path]
```

Screenshots the page, decodes the PNG in pure Node, and for every text run samples the
**surface pixels around it** rather than trusting CSS. Reports two numbers per run:

| | means | catches |
|---|---|---|
| `inner` | contrast against the dominant measured backdrop | wrong/incomplete DOM background resolution |
| `worst` | contrast against the nearest-luminance surface pixel in that region | **gradient ends, images, overlays** — a run can pass `inner` and fail `worst` |

`gradientRisk` = `inner − worst`. On a flat surface it is ~0; a large value means the text
sits on something that changes underneath it.

Three traps this script walked into and fixed, worth knowing if you extend it:
- **Anti-aliased glyph edges are not backdrop.** Sampling inside the text box makes every
  run report `worst ≈ 1.2` against its own halo. Sample a ring *around* the run.
- **That ring catches neighbouring text.** Comparing a label against the next label's
  glyphs also reports ~1.00. Restrict the worst-case scan to pixels near the dominant
  backdrop colour.
- **`oklch` and friends are not normalised anywhere readable** — resolve colour by
  rasterizing, in the page, before handing it to Node. A node-side parser silently drops
  every run on a modern palette and reports a clean page.

Exit code is the number of failing runs.

## Scoring and ranking

```
node scripts/accessible-score.mjs page1.html page2.html ... [--exclude ".rail,.chrome"] [--json]
```

Consumes the same audit and prints five weighted dimensions, a 0–100 composite and a letter
grade, ranked. Use it to compare directions against each other, or a redesign against its
own input.

| dimension | weight | driven by |
|---|---|---|
| Legibility | 22% | AA floor, median contrast band, smallest/median font size |
| Comfort | 24% | ceiling violations, halation, ink ratio, block rhythm, accent load |
| Hierarchy | 20% | signposts per screen, focus spread (low-confidence, capped), type steps |
| Length | 24% | effective screens (table-driven height discounted), longest unbroken run, sticky nav, distance to last control |
| Palette | 13% | competing saturated hue families, hue entropy, ramp temperature spread — **shades are rewarded, dispersion is not penalised** |
| Robustness | 10% | clipping, horizontal overflow, target sizes |

**Gates beat points.** AA floor breaches, halation on the reading surface and clipping cap
the grade outright; comfort-ceiling and *systemic* target failures cap less. Two 15px
checkboxes is a defect, not a gate — the target rule needs both a count floor and a share,
or a 13-control page trips on a denominator of thirteen.

**`--exclude` is ceiling-only.** Chrome may be loud; chrome's text must still be readable.

## What each metric is for

| Metric | Catches | Why this skill cares |
|---|---|---|
| `contrast.floor` | text below WCAG AA | the classic legibility check |
| `contrast.ceiling` | sustained text **above** ~14:1 on dark / ~19:1 on light | AA is a *minimum*; a palette can pass AA everywhere and still be painful. This is the check that was missing. |
| `contrast.halation` | high-chroma colour sitting on a near-black ground | the second eye-strain mechanism after raw contrast; blue/cyan/violet glow hardest |
| `whitespace.inkRatio` | share of the viewport covered by actual content | "open up spacing" as a number; climbing ink with flat gaps = density got worse, not better |
| `whitespace.medianGapPx` | breathing room between sibling blocks | distinguishes real spacing from a bigger font in the same box |
| `whitespace.densestRegions` | which container is the jammed one | a calm header can hide a 59%-ink table |
| `focus.ranked`, `hierarchySpread` | what visually dominates; top-vs-5th score ratio | flat information hierarchy = nothing wins the eye; spread under ~2x is the flag |
| `accents.coveragePct` | how much saturated colour is on screen | brand hue should be *concentrated* in chrome, not spread across every tile |
| `type.min/median/max` | the actual scale in effect | tells comfortable / large / enormous apart numerically instead of by feel |
| `hitTargets.aaViolations` | **controls** under 24×24 | WCAG 2.5.8 AA breach — counts against exit code |
| `hitTargets.belowComfort` | controls 24–44px | below 2.5.5 AAA; advisory, does not fail the run |
| `hitTargets.linkAdvisory` | text links under 24px | exempt by criteria (links in a sentence, or equivalent control elsewhere) — reported, never failed |
| `length.screens` | total height in viewport heights | soft signal only — see below |
| `length.longestWallScreens` | longest run with **no** heading/section break | **the real long-page failure**, not raw height |
| `length.lengthIsData` | is the height mostly inside `<table>` elements | long-because-data is legitimate; long-because-stacked is not |
| `length.stickyNav` | persistent orientation while scrolling | a long page with a sticky rail reads differently to one without |
| `length.tallest`, `length.repeats` | where height comes from; biggest run of near-identical sibling blocks | makes the finding actionable |
| `clipping` | overflowing text, boxes, page-level horizontal scroll | only ever visible once rendered |

## Why colours are resolved by rasterizing

Browsers hand back `oklch()`, `oklab()`, `lab()`, `lch()`, `color-mix()` and `color()`
**exactly as authored** — in computed styles, *and* in canvas `fillStyle`, which echoes
the string straight back. So neither string-parsing nor reading `fillStyle` normalises
them. A naive checker returns `null` for every colour, finds no violations, and reports a
clean pass on a page that is not clean — worse than no checker, because it looks like
evidence.

The only reliable resolution is to paint and read back the pixel:

```js
cx.globalCompositeOperation = 'copy';
cx.fillStyle = 'rgba(0, 0, 0, 0)';      // sentinel: setter rejects invalid colours
cx.fillStyle = str;
if (cx.fillStyle === 'rgba(0, 0, 0, 0)') return null;   // unparseable
cx.clearRect(0, 0, 1, 1);
cx.fillRect(0, 0, 1, 1);
const d = cx.getImageData(0, 0, 1, 1).data;             // true sRGB
```

If you adapt or rewrite any colour-measuring code for this skill, keep this.

## Reading the report honestly

- **Hard failures and advisories are separated deliberately.** The exit code counts only: contrast floor, contrast ceiling, halation, sub-24px *controls*, clipping, and length flags. Sub-44px controls, small text links, hierarchy spread, accent coverage and ink ratio are advisory — they inform a human judgement, they don't turn the run red. A page whose only findings are advisories exits 0.
- **Zero AA violations is not a pass.** Read `ceiling` and `halation` too.
- **Ceiling hits inside chrome are expected.** A saturated brand-hue rail is glanced at,
  not read, so it may carry contrast the working surface cannot. Scope it out with
  `--exclude ".rail"` rather than softening it — the fix for a harsh screen is almost
  never "quiet the bold region," it's "quiet the region people read."
- **Soft signals need a human.** Hierarchy spread, accent coverage and ink ratio are
  evidence, not verdicts. A screenshot you looked at outranks all three.
