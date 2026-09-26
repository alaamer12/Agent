# Prior-pass detection: recognizing already-accessible input, and re-approaching it

**Note:** the constraint-derivation method in point 3 below (look at what's actually fixed about the input, ask what's plausible given it, reject options that don't fit rather than forcing them in) is also the method `/accessible taste` uses to generate its `n` directions from a fresh input — see that command's section in `SKILL.md`. This file's own before/after is framed around the re-approach-after-a-prior-pass case specifically, but the derivation method itself isn't specific to that case.

## The shape of the failure this guards against

A person runs this skill at Ultra on a crowded admin screen. The result is a genuine two-page split: a new tonal ramp, a rebuilt elevation system, an "Overview" dashboard extracted from a "Sources" detail page. Later in the same conversation — or in a brand new conversation — the person hands back one or both of those files and asks for another Ultra pass, without saying it's the same file.

The naive failure: treat this as a fresh crowded input. Run the standard diagnosis (flat hierarchy, text-as-stats, inline overflow, and so on), find that most of it is already fixed, and ship a result that only nudges what's left — a slightly bigger type scale here, a slightly softer shadow there. The output *looks* like a pass happened (numbers changed, a few things moved), but structurally almost nothing changed, because almost nothing needed the standard fixes anymore. The person asked for another full pass and got a rounding error.

The two things that make this recoverable, in order:

## 1. Check the conversation's own history before checking the input's shape

If this skill already ran earlier in the same conversation, that is a strictly stronger signal than anything inferable from the file alone — use it first. This applies even when:
- The filename changed, or wasn't mentioned before.
- Only one file of a multi-file prior result is what's being handed back now (the person re-shares the "Sources" detail page but not the "Overview" page that was built alongside it — it's still recognizable as one half of a prior pass).
- The person doesn't say it's the same file, or seems to be testing whether it gets noticed.

Diagnostic question: does anything about what's being handed in now — a filename, a page's role, a structural feature — match something already built earlier in this conversation? If yes, treat it as that prior output, directly, rather than falling back to inferring "this looks polished" from generic signals as if the conversation didn't already answer the question.

## 2. Absent conversation history, read the input's own shape

Without a session match, judge from what the input actually contains — not a checklist to tick, but a real look at whether the standard diagnosis (flat hierarchy, text-as-stats, undifferentiated repetition, etc.) still finds much to fix:

- A deliberate, multi-step tonal ramp (not one or two swapped colors) assigned per-region.
- Type and spacing already generous, not cramped.
- An aggregate/overview view already separated from a detail view, where the content clearly once lived on one crowded page.
- Warnings or errors already promoted into their own callout blocks rather than crammed inline.
- Real elevation (deliberate shadow + radius system), not flat 1px borders.
- A consistent icon system already in place.

None of these alone is proof — a genuinely well-designed original could show one or two by coincidence. What's diagnostic is several of them together, especially the overview/detail split, which is a specific structural move this skill makes and is unlikely to appear in an unexamined original by chance.

## What "stop and report" looks like

Not a silent redirect into a smaller job, and not a blocking wall before doing anything. One message that does three things at once:

1. **States the finding with evidence**, in a sentence or two — "This already looks like it went through a full accessible-style pass — [it's the Overview page I built earlier this conversation / it already has a rebuilt tonal ramp, a separated overview page, and a real elevation system]."
2. **Says plainly that the standard crowded-screen fixes mostly don't apply here** — not "I'll look for small things to improve," but "there isn't much left to fix in the usual sense."
3. **Offers specific, input-derived alternate directions**, not a stock list. This is the part most prone to becoming generic — the fix is to look at what's actually *fixed* about the current design and ask, for each fixed thing, whether a different concrete choice is even plausible for this product:

   - *Current: nav lives in a persistent dark side rail with text labels, ~8 items across two labeled sections.* Because the item count is moderate and labels are already short, a plausible alternate is collapsing that into a top bar, or into a slide-out panel — worth naming. An icon-only nav is a weaker fit here only if the items aren't individually recognizable as icons (e.g. "Runs & workers" vs. "Catalog" aren't obviously iconographic) — say so rather than proposing it anyway just to fill out a list.
   - *Current: cards are dense rows, one source per row, in a single vertical list.* A grid-of-tiles or a timeline-by-run-date are both structurally plausible alternates for this specific content (each source has independent state, no inherent chronological ordering requirement) — name them as real options, not hypotheticals.
   - *Current: light working surface, dark chrome, red brand accent.* A genuinely different tonal direction (e.g. a cooler neutral instead of warm, or concentrating the accent differently) is a real option since nothing about an ops console demands the current specific palette — but reversing the light/dark call (going all-dark) would contradict the dwell-time reasoning that put it here in the first place, so that's not a neutral "different taste" option to offer casually; if raised, it should be flagged as trading away the light-surface rationale, not presented as equally valid.

   The last example matters: not every "different" direction is a good-faith offer. An alternate that undoes a reasoned decision from the original pass (like reverting a deliberately light working surface back to dark) should be named as a tradeoff, if named at all — not slipped in as one bullet among equals.

4. **Asks which direction, if any, to pursue**, and only proceeds once that's answered — unless the person's own request already specified a direction, said explicitly they want more of the same anyway, or said to just proceed.

## What doesn't count as satisfying this check

- Silently doing a smaller, patchier version of the requested mode because "there wasn't much to fix" — this is the exact failure being guarded against, just relabeled as caution instead of under-delivery.
- Naming alternate directions that don't fit the input's actual constraints, to look thorough — see the icon-nav counterexample above.
- Treating a re-run detection as a hard stop that blocks all progress until the person answers — it's one message with a finding, a reason, options, and a question, not a multi-turn interrogation.
- Skipping this check because the person didn't ask "is this a re-run" — they usually won't ask; recognizing it is Claude's job, not something to wait to be told.