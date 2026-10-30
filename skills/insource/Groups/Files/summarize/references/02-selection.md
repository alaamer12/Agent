# Selection: deciding what survives, in two modes

Once you understand the source (see 01-reading-for-the-point.md), decide content, not prose: what goes in, what's cut, how much weight each surviving point gets. This is where summary quality is actually won or lost — polished sentences cannot fix a wrong selection.

## Two modes

This skill runs in one of two modes. **Normal is the default.** Only switch to Extreme when the user asks for it explicitly, or with words that clearly mean it — "as short as possible," "bare minimum," "just the terms," "bullet list only, no explanations," "extreme summary."

### Normal mode

Sort content into three tiers and draft from the first two:

- **Must-keep.** The point itself, and the one or two things it cannot be understood without: the main conclusion or recommendation, the evidence it most depends on, any caveat that changes what is being claimed. If cut, the summary would misrepresent the source.
- **Should-keep.** Real supporting content that strengthens or nuances the point — a secondary finding, an important example, a relevant number — but that a shorter summary could survive without. This is what gets cut first if the target length shrinks further.
- **Can-cut.** Redundant restatement, throat-clearing, illustrative color beyond the first example, procedural or administrative detail, anything that supports a point already established without adding a new one.

Draft with must-keep content always present; add should-keep content until the target length is reached; treat can-cut content as cut by default. The result reads as ordinary prose or a short structured digest — see templates/executive-summary.md and templates/structured-digest.md.

### Extreme mode

The goal shifts from "shortest good summary" to "smallest artifact that still names every distinct point, with zero repetition." Concretely:

- Keep **must-keep content only**. Should-keep and can-cut are both dropped entirely — no secondary findings, no examples, no supporting numbers unless a must-keep point is meaningless without one.
- Collapse each surviving point to a **term or short label plus a one-line description** — not a sentence written in flowing prose, a labeled fact. Aim for the density of a glossary entry or a spec sheet row, not a paragraph.
- **No point appears twice** in any form, even reworded. If two must-keep points overlap, merge them into one line rather than keeping both.
- **No connective or transitional prose.** Extreme mode output is a list, not a narrative. Cut "furthermore," "as a result," "building on this" entirely — see templates/extreme-digest.md for the expected shape.
- Still passes the faithfulness check (05-faithfulness-check.md) in full — extreme compression is not license to distort, hedge less, or drop a caveat that changes the claim. If a caveat is must-keep, it survives, compressed to a clause, not omitted for brevity.

> Normal: "The team recommends Vendor C. Although Vendor A was cheapest and Vendor B had the best support, C balances price and support reasonably well and — critically — integrates with the existing system without custom work, which the other two do not."
>
> Extreme:
> - **Recommendation:** Vendor C.
> - **Why:** only option integrating without custom work.
> - **Trade-off accepted:** not cheapest (A) or best-supported (B).

Both are faithful to the same source. Extreme is not a shorter version of the same sentences — it is a different artifact: terms and their descriptions, not prose.

## Weight by argumentative importance, not word count or position

A source's own emphasis is not always visible from surface features. Do not let length or position stand in for importance. Two specific traps:

- **Recency/position bias** — the last thing read tends to feel most memorable; check against the source's own structure before assuming the ending is the conclusion.
- **Ease-of-lifting bias** — crisp, quotable sentences get selected more often than sentences carrying more importance but requiring paraphrase. Select on importance, not convenience.

## What almost always survives (both modes)

- The decision, recommendation, or conclusion, stated plainly.
- Numbers that are the point, with enough context to be meaningful.
- Action items: what happens next, who owns it, by when — if stated.
- Material disagreement or dissent.
- Anything that would change the reader's decision if silently omitted.

## What almost always cuts (both modes; Extreme cuts further)

- Restatement of a point already made.
- The second, third, and further illustrative examples once the first has made the point.
- Procedural scaffolding ("In this section we will discuss…").
- Attribution detail beyond what credibility requires.
- Background the target audience can be assumed to already have.

## Multi-part or multi-topic sources

Select per-topic, then decide the summary's proportions separately — a source with one major decision and four minor updates should produce a summary that is mostly about the decision, in both modes. In Extreme mode this often means the four minor updates each collapse to a single line, or are merged into one "minor updates" line, while the major decision still gets a full labeled entry.

## The "so what" test

For each candidate point, ask: does this tell the reader something usable — a decision, an action, an update to belief? Content that only says "this topic was covered" without saying what was concluded fails this test in both modes, and is the first thing to cut in Extreme.

## Quality checks

- [ ] The mode (Normal or Extreme) matches what was requested or clearly implied; Normal was used unless Extreme was clearly signaled.
- [ ] In Normal mode, must-keep content is complete and should-keep content fills remaining space in priority order.
- [ ] In Extreme mode, only must-keep content survives, each point appears once, and every line is a term/label plus a single-line description — no prose paragraphs.
- [ ] Weight in the summary mirrors weight in the source's argument, not surface word count or position.
- [ ] No point survives because it was easy to lift; none was cut because it was hard to compress.
