# Conversations, roles, and custom output structure

Everything in 01–06 assumes a single undifferentiated source. Two situations need an extra decision layered on top, made **before** applying mode (02) or structure/length (04):

1. The source has **distinct roles or turns** (a conversation, a Q&A thread, an interview, a support ticket chain) rather than one continuous voice.
2. The user's request specifies **how the output should be organized**, not just how short it should be.

Get this decision right first — selection and compression still apply within it, but this decision determines the shape they're applied *into*.

## Step 0: does the request specify a new output structure?

Read the request and classify it as one of two kinds before doing anything else:

### A. Reserved structure (default)

The user describes *what to do with the content* — what to compress, what to keep verbatim, what to focus on — without describing a different arrangement of the output. The source's existing shape carries over: if the source is turn-by-turn (question, answer, question, answer...), the summary stays turn-by-turn, in the same order, with the same alternation. Only the *content inside each part* is affected by the instruction.

> "Summarize this, keeping my questions and just summarizing the agent's answers."
> "Condense the assistant's replies but leave my messages as-is."
> "Summarize this conversation." (no structural instruction at all — still reserved, apply role-aware defaults below)

In all of these, nothing tells you to regroup, reorder, or re-label the content. The turn sequence is not a "should-keep" detail to be optimized away — it is part of what must survive, because the user never asked for a new shape.

### B. Custom structure (explicit)

The user describes a **different arrangement** than the source has — a new grouping, a new ordering, new sections or headers that don't mirror the source's own turn sequence.

> "Write all my questions at the top, tagged with header sections, then the agent's answers underneath."
> "Group everything by topic instead of by who said it."
> "List every question I asked as a numbered index, then answer each one in one line below."
> "Pull out only the action items into one section, and put my open questions in another."

Here the request itself *is* a structure spec. Build the output to that spec directly — sections 02/03/05 (selection, compression, faithfulness) still govern what content survives and how it's phrased, but section 04's "mirror the source's shape" guidance and any template in `templates/` are both starting points to adapt, not shapes to preserve. If the user's structure conflicts with bottom-line-first ordering, the user's explicit structure wins — they asked for it.

**Test to tell them apart:** does the instruction describe a *content operation* (compress X, keep Y, focus on Z) or a *layout* (put A before B, group by C, add headers per D)? Content operations → reserved structure. Layout instructions → custom structure. A request can contain both — e.g. "keep my questions verbatim, and put them all at the top" — in which case follow the layout instruction (questions grouped at top) while applying the content rule (verbatim) within it.

If genuinely ambiguous which is meant, default to reserved structure (the lower-risk assumption) and note the assumption briefly rather than asking — per the skill's general instruction, proceeding beats stalling on an assumption that's easy to state.

## Role-aware selection and compression (reserved structure, conversational sources)

When the source has roles — most commonly a user and an agent/assistant, but also interviewer/interviewee, customer/support, or multiple named speakers — and the structure is reserved, apply mode and selection **per role**, not uniformly across the whole transcript:

- **A role the user asks to preserve** (e.g., "keep my questions") is copied verbatim or near-verbatim — this is the lift case from 03-compression-method.md, not the rewrite case. Do not paraphrase, shorten, or merge turns from a preserved role even if they seem repetitive; repetition across a preserved role is the user's own record, not summarization material.
- **A role the user asks to summarize** (e.g., "focus on summarizing the agent's answers") gets full selection (02) and compression (03) treatment, independently for each turn or, if turns are short and tightly coupled to the adjacent question, collapsed per question-answer pair — whichever keeps each summarized turn legible as an answer to its paired turn.
- **Neither role specified** ("summarize this conversation," no further instruction) — treat it as a normal single-voice source per 01–06, but still preserve turn order and enough attribution (who said what) that the result is self-contained; don't flatten speaker identity out of the record if the conversation's meaning depends on who said what (a negotiation, a disagreement, a decision made by one party).
- Still apply the faithfulness check (05) to every summarized turn — role-based compression is compression, with the same risks (dropped hedges, invented connections) as any other content.

Length calibration (04) applies per role when roles are treated differently: a preserved role has no target length (it's copied), while a summarized role is calibrated the normal way against its own original length, not the transcript's total length.

## Building a custom structure

When the request specifies layout (case B above):

1. Extract the structural spec literally from the request — what are the sections, what goes in each, what order, what labels or tags. Don't infer a fancier structure than was asked for, and don't fall back to a `templates/` shape that doesn't match what was requested.
2. Populate each section by running the normal selection/compression/faithfulness passes (02, 03, 05) on the content that belongs in it — a custom layout changes *where* content goes, not whether it still has to be selected and verified like any other content.
3. Preserve traceability: if questions and answers are being separated (e.g., all questions first, then answers), keep an explicit link between them — a shared tag, number, or heading id — so the reader can still match each answer to its question once they're no longer adjacent. This is the same self-contained requirement as 04's "resolve pronouns and references," applied to structure instead of prose: separating parts that were adjacent in the source creates the same kind of dangling reference a pronoun does, and needs the same fix.
4. If the user named a specific tagging scheme (e.g., "tag-id `#` them with headers"), use exactly that scheme; if they described the shape but not the exact syntax, choose a simple, consistent scheme (e.g., `## Q1`, `## Q2` ... with matching `**A1:**` labels below) and apply it uniformly.

## Quality checks

- [ ] Classified the request as reserved or custom structure *before* applying selection or compression, using the content-operation vs. layout test.
- [ ] Reserved structure: source's turn order and alternation survived unchanged; only in-role content was affected.
- [ ] Reserved structure with a "keep verbatim" role: that role was copied, not paraphrased, shortened, or merged.
- [ ] Reserved structure with a "summarize" role: normal selection/compression/faithfulness (02/03/05) applied to that role only.
- [ ] Custom structure: output matches the requested layout, not a default template, and any user-specified tagging/labeling scheme was followed exactly.
- [ ] Custom structure: separated parts that were originally adjacent (e.g., a question and its answer) still carry an explicit link back to each other.
- [ ] If the reserved-vs-custom call was ambiguous, the assumption was stated briefly rather than left silent.
