# The same principle, four products, four different right answers

These are **not four categories to select from.** They are four records of the same five questions
(`references/what-its-for.md`) resolving differently, kept because the most reliable way to
misapply this skill is to learn one look and ship it everywhere. If you read these and come away
thinking "ERP means dense," you have read them wrong: the point is that *the answer came from what
the screen was for*, and a given ERP screen may well land somewhere else.

Each entry names the trap — the outcome where the pass is real work, every instrument is green,
and the result is worse for the person doing the job.

---

## A multi-tenant SaaS: the dashboard and the empty first one

**The calm instinct says:** reduce the aggregate to a few large quiet cards, drop the secondary
metrics into plain text, give the chart room to breathe.

**What the screen is for:** a returning user confirming nothing is wrong in two seconds, and a
new user deciding whether this product is for them. Those are different screens wearing the same
layout.

**What a correct pass does:** the populated view redistributes normally. The *empty* view gets
designed as its own surface — it is the highest-stakes screen in the product and the one the skill
never asks about. Zero-result, mid-save and forbidden states likewise get treated as states with an
obligation each (explain, reassure, offer the next action), rather than as the populated layout
with nothing in it.

**The trap:** a serene first-run dashboard. Beautiful, calm, and the user has no idea what to do
next. Activation drops and no measurement in this skill notices, because every one of them renders
the screen with data in it.

---

## An ERP or back office: the 40-column entry grid

**The calm instinct says:** too many columns; fold the rarely-scanned ones into plain text, open up
the row height, split the summary onto its own page, add breathing room.

**What the screen is for:** someone entering or reconciling hundreds of rows a day, keyboard-first,
who is *comparing across columns constantly* and whose errors cost money.

**What a correct pass does:** the working surface genuinely gets calmer — quieter rules, real
hierarchy among columns, tabular figures, a legible status encoding, no alternating-row noise that
isn't carrying information. But it holds floors: rows per screenful does not drop, comparison
targets stay visible simultaneously so no split is allowed between them, the edit path stays
reachable without pointer input, and validated feedback stays adjacent to the field being typed in.
Type scale goes *down* relative to a marketing screen here, and that is the accessibility call, not
a compromise.

**The trap:** the pass ships, the audit scores higher than the original, the person says "it looks
lovely," and the department quietly takes 15% longer to close the month. This is the single most
damaging way to use this skill, and the one its instruments are least equipped to catch — there is
no "too calm" ceiling, because calm is only ever *too* much relative to the work it displaces.

---

## A CMS: the editor is not a page about a page

**The calm instinct says:** restyle the chrome around the content, tidy the metadata panel, give
the canvas more air.

**What the screen is for:** someone composing an artifact that will be rendered *elsewhere*, and
judging it by how it looks while they compose it.

**What a correct pass does:** the chrome and the field lists get the full treatment. The canvas is
the one region where the pass must show restraint, because the surface's job is fidelity to the
output — typography and spacing there belong to the *document*, not to the admin theme. Long-form
composition needs a controlled measure and a stable caret position, which look nothing like a card
grid. Structural changes that move where a control lives are fine; restyling what the user is
writing to look like the product's design system is a defect that looks like a redesign.

**The trap:** the admin gets beautiful and WYSIWYG stops being WYSIWYG. The author now can't tell
what they're shipping without publishing it — a new step in the job, introduced by a pass whose
diff was entirely legitimate styling work.

---

## An LMS: three jobs in one product, one of them on a phone

**The calm instinct says:** one coherent visual language across the app; unify the patterns; the
learner and instructor views share components, so they should share treatment.

**What the screen is for:** a learner deciding in four seconds whether to resume and how much is
left; an instructor finding the three submissions that need attention today; an admin auditing
config. Those goals conflict, and the shared-component instinct flattens the wrong one — progress,
momentum and "you are here" cues are not noise to be reduced on the learner surface, they are the
content.

**What a correct pass does:** keeps the token system shared and lets *one* region diverge on
purpose. Reads which job each surface serves before deciding what counts as clutter. And it takes
the device seriously: if the learner traffic is phones, the pass must be evaluated at a phone
width, where the comfortable spacing scale is an obstacle and a wide table becomes an unreadable
horizontal scroll. The instructor and admin surfaces get the full calm treatment; the exam timer
stays loud, because a countdown is the one element where visual urgency is correct and a ceiling
would be a bug.

**The trap:** a gorgeous desktop redesign of a product that is used on a bus. Every measurement
passes because every measurement was taken at one width.

---

## What is common to all four

The pass went wrong each time by being **locally consistent and globally indifferent**: applying a
rule that was correct on the screens it was derived from to screens doing a different job. Which
means the check that matters is not "did I apply the moves" — it is whether, for each surface, you
can say out loud what someone is trying to do there, what it costs them today, and whether your
change lowers or raises that cost. If you cannot, you have not diagnosed anything yet, and a green
grade means nothing.
