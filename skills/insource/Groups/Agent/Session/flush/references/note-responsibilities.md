# The four notes — responsibilities and boundaries

One job per note. This is the include/exclude contract for each file and
the rule that keeps them from bleeding into one another; the copyable
skeletons are in [`../assets/note-templates.md`](../assets/note-templates.md).

### 1. CONTEXT.md — working context

The deepest note: how we arrived here and what the next agent must
understand. Include: user requirements and goals · important decisions and
their reasons · decisions changed or reversed · relevant assumptions ·
constraints · important discoveries · technical/domain knowledge learned
during the task · problems encountered · solutions attempted, worked, and
failed · trade-offs · relevant dependencies · terminology established
during work · earlier-conversation context that affects current work ·
unresolved questions that materially affect continuation.

Exclude (this is compression, not archiving): casual conversation,
greetings, repetitive discussion, tool-call noise, internal execution
details with no future value, temporary reasoning that doesn't affect the
resulting understanding, repeated versions of the same fact, information
represented more accurately elsewhere.

Rule: **never copy the conversation verbatim — reconstruct the meaningful
working context.**

### 2. PLAN.md — the current operating plan

Any form appropriate to the work — task list, phased implementation plan,
workflow, research process, debugging strategy, migration plan, design or
validation process, or a combination. **Do not force every project into a
generic TODO list.** Include: main objective · current phase · planned
phases · tasks/subtasks · dependencies · completed steps · the current step
· next steps · blocked steps · validation steps · important changes made to
the original plan **with their reasons** · conditions required before
continuing.

Rule: it must be the **actual current plan** — the latest valid direction
wins over the plan the conversation started with.

### 3. SNAPSHOT.md — objective point-in-time state

Answers *what objectively exists right now* — not how we got here (that is
CONTEXT.md) and not evaluation (that is STATUS.md). Include (as
applicable): existing/created/modified/deleted/missing files · implemented
and partially-implemented features · configurations · current architecture
· data/state · dependencies · tests **and current test results** · current
errors · build state · environment-relevant facts · other verifiable state.

Rule: **prefer factual statements over interpretation** —
"`src/search.ts` exists; the filter implementation is incomplete; search
tests currently pass" — never "the project is almost finished" (that
belongs in STATUS.md). Verify these claims against the project before writing
them.

### 4. STATUS.md — high-level assessment

Answers *where the project stands*: overall status · completed · in
progress · remaining · not started · blocked · known issues · important
risks · current priorities · immediate next actions · milestones · any
major deviation from the intended outcome. Structure (see templates) may be
adapted when another format represents the project more accurately.
