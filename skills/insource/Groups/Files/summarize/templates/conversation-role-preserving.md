# Template: Role-preserving conversation summary (reserved structure)

Use when the source is a conversation/thread with distinct roles (e.g., user + agent) and the request preserves the turn structure — a content instruction, not a layout instruction (see references/07-conversation-and-custom-structure.md). Turn order and alternation from the source carry over unchanged.

```
**[Role A, turn 1 — e.g. "User"]:** [verbatim or near-verbatim, if this role is the one being preserved]

**[Role B, turn 1 — e.g. "Agent"]:** [summarized per the active mode, if this role is the one being condensed]

**[Role A, turn 2]:** [...]

**[Role B, turn 2]:** [...]
```

Rules specific to this template:
- One block per original turn, in original order — do not regroup, reorder, or merge turns from different points in the conversation.
- A role the user asked to keep is copied as given (03-compression-method.md's "lift" case) — no shortening, no paraphrase, no merging near-duplicate turns.
- A role the user asked to summarize gets full selection/compression/faithfulness treatment (02/03/05), scoped to that turn (or that turn paired with its adjacent counterpart, if the two are only legible together).
- If a summarized turn is very short in the source already, it's fine for the "summary" to be close to the original — don't pad it to look more condensed than it needs to be.
- Neither role is dropped entirely unless the user asked to remove one outright (different from asking to condense one) — condensing is not omitting.

## Example

Request: "Summarize this, keeping my questions and just summarizing the agent's answers."

```
**User:** What's the difference between the Normal and Extreme summary modes?

**Agent:** Normal keeps must-keep and should-keep content as prose; Extreme keeps only must-keep content as a flat list of term + one-line description entries, with zero repetition.

**User:** Can I mix them — extreme for one section, normal for another?

**Agent:** The skill doesn't define a mixed mode; pick one per summarization pass. For a multi-section source, run each section separately if different sections genuinely need different modes.
```

The user's two questions appear exactly as asked (not paraphrased, not shortened); the agent's answers are compressed per Normal mode's rules from 02-selection.md, and each answer still reads as a direct answer to its paired question because turn order and pairing were preserved.
