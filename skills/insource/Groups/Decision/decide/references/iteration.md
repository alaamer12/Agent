# Iteration loop

Delivering the page is the start of the conversation, not the end. Keep thinking with the user until they decide. Options and examples here are illustrative, not exhaustive or mandatory. A hybrid or unlisted response is always acceptable.

## The closing question

End every delivery with one question: **which of these dimensions matter most to you for this decision?** Under it, list the page's dimensions by name (short) so the user can pick, rank or add their own. If a question tool exists, show the dimensions as a multi-select with an "other" option.

Add one sentence of offers after the question, for example: re-weight the rating to your priorities, go deeper on any section, add a tab, add or remove a candidate, or re-run the research.

## Handling the reply

These are examples of what a reply can ask for and how to respond.

- **Names priorities.** Recompute the rating with those weights and show the weights under the chips. Show the equal-weight rating next to it so the effect is visible. Rewrite the verdict for the stated priorities. Say whether the leader changed or the tie remains.
- **Wants more detail on a dimension.** Extend that section in place: more points, a chart or table if the data supports it, more sources. Research more if the page lacks the data.
- **Wants a new angle** such as [cost] [migration] [risks] [team fit] [security]. Add a tab with one purpose, add it to the tab bar and to the PDF order.
- **Adds or removes a candidate.** Research a new candidate to the same depth on every existing dimension, then recompute ratings, charts and colors. If one is removed, remove it from the rating and mention it.
- **Doubts a claim or asks if it is still true.** Redo the research for that item, update the source and say what changed.
- **Wants a fresh comparison.** Re-run the full search or `/compare` step. Set a new Compared on date. Keep the earlier file if the user wants to compare versions.
- **Wants different examples.** Add showcase blocks or a showcase tab for the new types.
- **Cannot decide.** Ask the next narrowing question, one at a time: a deal-breaker, the cost of being wrong, the constraint that cannot move. Suggest a small trial with clear success criteria when the data cannot settle it.
- **Says they decided.** Write a short decision record: the choice, the reasons tied to their stated priorities, the risks accepted, and the re-check date. Offer to add it to the page as a Decision section or tab.

## Updating the page

- Patch the existing file (data arrays, one section, one tab) instead of rebuilding it. Keep candidate colors, keys and layout stable so the user can see what changed.
- Add an **Updated** line to the freshness section with the date and what changed (for example "[date]: added Cost tab"). Change Compared on and Data covers only when the research itself was redone.
- Run `scripts/check_page.py` after every change.
- Republish to the same link or present the updated file. Say what changed in one or two lines.

## Staying fair in the loop

- Do not tilt toward a candidate because the user leans that way. Apply their priorities only as stated weights.
- New and existing candidates get the same research depth.
- Say when new information changes the verdict and when it does not.
- Do not expand the page for its own sake. When the decision is clear, offer to stop or to write the decision record.
