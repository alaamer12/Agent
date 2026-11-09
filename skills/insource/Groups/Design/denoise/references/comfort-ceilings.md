# Comfort ceilings, work floors, and name/content fit

Every "more accessible" instinct in this skill pushes a value up. Each has a ceiling past which it causes the harm it was meant to fix, and a check that only tests a minimum cannot see it. The other half is missing in the opposite direction: instincts that improve the render and make the *work* worse have no ceiling at all, because nothing about them is visual — so they need floors, and they need them named, because no instrument in this skill will catch them by itself. Naming is the third failure that styling alone does not catch.

## Comfort ceilings — the checks that run the other way

Every "make it more accessible" instinct in this skill pushes a value *up*: bigger type, more padding, more contrast, more separation. Each of those has a ceiling past which it starts causing the harm it was meant to fix, and a check that only tests a minimum cannot see it. The type scale already has one (see the typography move: past *enormous*, density itself has to drop). These are the others.

**Contrast is a range, not a floor.** WCAG AA specifies a *minimum*; it is entirely silent about the maximum, which is why "every pairing passes AA" is not evidence that a screen is comfortable. Near-white text on a near-black ground reaches 15–17:1 and reads as harsh, buzzing edges to a large share of readers — the text bleeds outward (halation) rather than sitting crisply, and it is especially painful for people with astigmatism or light sensitivity, and over a long session for everyone else. Rough working targets, for text that is actually *read* for more than a moment:

- **Light working surface:** body text ~7:1 to ~13:1. Soften the ground off pure white and the ink off pure black rather than running both to the extreme.
- **Dark working surface:** cap body text around 12–13:1 — use an off-white ink, not `#fff`. Then desaturate status and accent colours and lift them slightly *toward* the surface instead of placing full-chroma mid-luminance hues on black, which is the second-halation mechanism after raw contrast. Short-wavelength hues (blue, violet, cyan) glow hardest on dark grounds; they belong in small doses there, not as body-colour.
- **Large display numerals and headings** are read for a moment, not tracked across a paragraph, so high contrast on them is fine. The ceiling applies to sustained text — table cells, labels, body copy, anything a user scans down a long list.

**Chrome is exempt from the ceiling, and that exemption is the point of the dwell-time split.** A saturated brand-hue rail or top bar is glanced at, not read, so it can carry contrast and chroma the working surface cannot. When measuring, scope the chrome region out rather than softening it — the fix for a harsh screen is almost never "make the bold region quieter," it is "make the *read* region quieter."

**Page length has a ceiling too.** Scrolling is a physical cost and a comprehension cost: past a few screens a reader loses track of where they were, and content below the fold is content that does not exist for a fraction of users. But long is not automatically wrong — **a page that is long because a paginated data table has many rows is fine; a page that is long because a dozen summary blocks are stacked is the redistribution move failing to happen.** Judge by attributing the height first. The specific failure is the *unbroken run*: several screens of content with no heading, section boundary or sticky orientation to re-anchor on. That, not raw screen count, is what makes a long page inaccessible. If an Ultra pass leaves the detail page longer than the input's, the split did not go far enough — moving the aggregate to its own page should shorten the remaining page, not merely reorganise it.

**Density has a ceiling too.** Opening up spacing reduces how much is visible per screenful; on a table someone compares across many rows, past a certain point every additional pixel of padding costs scrolling and eye travel, which is its own fatigue. The measurable symptom is ink coverage climbing while median block gap stays flat or drops — more air in one dimension, less in the other, net worse.

These are the failure modes `scripts/denoise-audit.mjs` measures. It exists because reading your own output is not the same as measuring it: a palette can look calm, pass AA on every pairing, and still be the one a person says "that hurts my eyes" about.


## Floors — the checks that have no instrument at all

Ceilings bound the *treatment*: how big, how loud, how airy a surface may get before it hurts the
eye. Floors bound the *job*: how much of the work a surface may make harder before the redesign is
a regression, whatever it does for the eye. The skill had the first and not the second, and the
asymmetry explains why: a ceiling is a property of the render, so a script can measure it. A floor
is a property of a task performed over time by a person, so nothing here could see it — the pass
would ship a screen with 15% fewer rows per screenful and every number in the audit would improve.

**The rule: calm is never purchased with cost.** Where the two conflict, the surface's job decides,
and the pass says out loud which one it chose. The floors are countable from structure — see the
cost measure in `references/what-its-for.md` — and the four that get crossed most often:

- **Volume per screen.** Rows or records visible without scrolling, for a surface someone works
  through rather than reads. Opening up spacing raises height, which lowers this, which adds
  scrolling and eye travel — the same fatigue the move exists to remove, reached by another route.
  On an entry or reconciliation grid, the calm treatment goes into encoding and hierarchy and the
  density is defended; on a screen read occasionally, the density gives way.
- **Steps to the common task.** Clicks, keystrokes, and screens between opening the surface and
  finishing what the user came to finish. Every added confirmation, every "are you sure" on a
  routine high-frequency action, every field that now needs a scroll to reach, is a cost someone
  pays hundreds of times a day.
- **Simultaneity of comparison.** Whether the values a person compares are ever on screen at the
  same time. This is the floor the page-split move crosses by accident: splitting an aggregate from
  a detail view helps a reader and disables a comparer, and the two populations are not obvious from
  the markup.
- **Recovery from a mistake.** What it costs to undo, and whether the error tells the person which
  thing to fix. A redesign that moves validation feedback away from the field being typed in, or
  buries an undo, has raised the price of being wrong — which is the accessibility failure with the
  largest effect on the people who are least confident, and invisible in a screenshot of a
  successful path.

**A pass that lowers a floor has to say so and say why.** "Rows per screenful 22 → 18, accepted
because this table is read, not keyed" is a complete justification and a perfectly ordinary trade.
The same trade made silently is the defect — the difference is not the outcome, it is whether a
designer looked at it.


## Naming and content must match — check this at every mode, not just Ultra

This is failure mode 10, and unlike the numbered moves above, it isn't something a mode unlocks — it's a check to run regardless of mode, because a mislabeled heading is just as misleading in a Lite pass that never touches structure as it is in an Ultra pass that invents new pages. Two situations, handled differently:

**The input already has the mismatch (Claude didn't create it).** Notice it as part of looking at the actual input (workflow step 2) — read section/page names against what's actually under them, not just at layout/density. When a name's promise doesn't match its content, this is worth surfacing to the person even though it's not strictly a visual-crowding problem this skill was asked to fix: name the specific mismatch in one line ("this page is titled 'Overview' but the content is a full data table with per-row detail — want me to keep the name as-is, retitle it to something that matches what's actually there, or split it so the aggregate view and the detail view are separate?") and let them decide, rather than either silently relabeling something they may have named intentionally (an internal tool's "Overview" might just be established team vocabulary, not a mistake) or silently leaving a misleading label in place because renaming wasn't explicitly requested. This is a genuine consult, not a rhetorical one — proceed with whichever of the offered paths the person picks, and if they don't respond to the callout, default to leaving the name as-is rather than guessing which fix they'd have wanted.

**A move in this pass would create the mismatch (Ultra's page-split is the main case, but any mode can introduce a new heading or section name).** Don't create it in the first place — check the fit as part of the same step that decides the name, the way the page-split move above now does explicitly. This is prevention, not detection-after-the-fact, and it doesn't need a consult, since Claude is the one choosing the name and can just choose one that fits what it's putting under it.

Either way, the underlying judgment is the same: does this name, read cold with no other context, correctly set expectations for the density and complexity of what follows? If not, that's the mismatch to catch.

