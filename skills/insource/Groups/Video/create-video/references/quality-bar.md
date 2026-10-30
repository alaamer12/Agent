# The Quality Bar

Measurable acceptance thresholds. HyperFrames' own verify stage is `lint` +
`check` + a contact-sheet glance; those prove the composition is *valid*, not that
it is *good*. This file is the difference — a number for each claim, so "does this
look professional?" is answered by measurement and not by taste after the fact.

Every row is checked by `scripts/qa.py` where it can be, and by eye where it
cannot. Thresholds are starting points for a house style, not laws of nature:
when you deliberately break one, say which and why in the delivery note.

## Cut and rhythm

| Check | Threshold | How |
|---|---|---|
| Dead air | no gap > 0.25 s between scenes | `qa.py` timeline pass |
| Scene overlap | none beyond the transition budget | `qa.py` |
| First scene starts | t = 0 | `qa.py` |
| Last scene ends | within 2% of the declared duration | `qa.py` |
| Arrivals per scene | ≥ the count `spec.py` budgets | `qa.py` |
| Everything at t=0 | no scene where every clip starts at 0 | `qa.py` |
| Minimum dwell | ≥ 0.15 s between consecutive arrivals | `qa.py` |
| Rest before a cut | ≥ 0.2 s of settled frame at each scene end | eye, on the contact sheet |

The t=0 rule is the single strongest tell: content that all appears at once is a
slide, not a shot. Motion must keep arriving.

## Read time

| Element | Threshold |
|---|---|
| Headline | hold ≥ 2.5 s, or ≥ 1.5× the time to read it aloud |
| Body / caption text | ≥ 12 chars/sec of on-screen text |
| A statistic | ≥ 1.5 s to land the number, plus 0.5 s to read its label |
| Full-frame type | ≥ 1/12 of frame height; anything smaller is unreadable on a phone |
| Caption text | ≥ 1/18 of frame height, inside title-safe |
| Word count per beat | ≤ 12 words on screen at once, above that split the beat |

## Frame discipline

| Check | Threshold | How |
|---|---|---|
| Action-safe | all visible ink inside 90% of the frame (5% inset) | `qa.py` frame pass |
| Title-safe | captions and key content inside 80% (10% inset) | `qa.py` frame pass |
| Ink in the outer 5% band | < 2% of that band's pixels | `qa.py` |
| Edge-touching content | none, unless a deliberate full-bleed | eye |
| Contrast | WCAG AA on text, measured by `check --contrast` | `check` |

## Sound

| Check | Threshold |
|---|---|
| Loudness | −14 LUFS integrated for streaming delivery, ±1 LU. Verify the target for the actual platform before shipping; it changes. |
| True peak | ≤ −1 dBTP |
| Sync | VO to picture ≤ 1 frame; cut on music ≤ 1 beat-grid quantum |
| Bed under voice | carved, not merely ducked — the production loop is explicit that a duck alone is not a mix |
| Silence | no unintended silent stretch > 0.5 s |
| Last 0.5 s | audio reaches its target level; no clipping ramp into the end |

## The AI tells

What reads as machine-made. Each is checkable.

- **Everything arrives at t=0.** See the timeline rule above.
- **One ease for everything.** Tone should vary the easing family; a single
  `power2.out` across 20 tweens feels inert.
- **Centred, symmetric, full-width.** Every beat dead centre with no negative
  space and no off-axis weight.
- **Web type sizes.** 16–24 px type on a 1080p frame — video scale is 3–5× web.
- **A transition on every cut.** Dissolves between every shot flatten rhythm;
  hard cuts are the default and specials are the accent.
- **Generic gradient background.** A mesh gradient behind centred text is the
  sound of no concept.
- **No rest.** Every window packed to the brim, so nothing is emphasized.
- **First frame as thumbnail.** The opening frame is a still with no arrival, or
  the piece ends mid-motion with no settle.
- **Mismatched weights.** Display and body from one family at one weight, or a
  serif headline over a serif caption with no hierarchy.
- **Motion that contradicts the copy.** "Accelerate" over a slow dissolve;
  "calm" with a whip pan. The axes exist so this is catchable.

## Judgement calls that stay human

Concept, taste in restraint, whether the joke lands, whether the metaphor is the
right one, and whether the piece is *about* something. `qa.py` measures the
floor; nothing measures the ceiling. The review loop's checkpoints
(`/hyperframes` → `references/review-loop.md`) are where those get decided, and
they stay the only authority on them.
