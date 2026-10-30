# Decision record — <short title>

<!--
  Copy to the project's decisions location (docs/decisions/, adr/, or a
  single DECISIONS.md log) and fill. Write for the reader who finds this in
  six months with zero context: they must be able to re-derive the choice.
  One record per lasting decision — not per commit, not per TODO.
-->

## Decision

<What was decided, in one or two sentences. State it as fact: "We use X for Y.">

### The question this answers

<The choice the work actually forced, as one sentence — the version a
successor could re-decide against: "How do we pin axis domains when the
chart library ignores a sibling `domain:` setting?" An answer recorded
without its question cannot be revisited; if you cannot phrase the
question, you are recording an implementation detail, not a decision.>

### Context

<Why this decision was necessary *now*: the problem, the trigger, the
constraints in force (requirements, existing architecture, user intent).
Include what was known at the time — and what was not.>

### Options considered

- **Option A** — <what it is; one-line trade-off>
- **Option B** — <what it is; one-line trade-off>
- **Option C (chosen)** — <what it is; why it wins>

<Reject the real alternatives, not straw men. "None — there was only one
viable path" is a legitimate entry when true.>

### Rationale

<Why the chosen option is preferred *under this project's priorities*:
correctness, simplicity, maintainability, reliability, consistency,
reversibility. Name the trade-off accepted — every real decision gives
something up; a record that admits nothing was sacrificed is marketing,
not engineering. If chosen under uncertainty, state what evidence was thin
and what would change the answer.>

### Consequences

<What this changes or guarantees going forward: new obligations, things
made harder, things now safe to rely on, cost incurred.>

### Reversal boundary

<If this decision must change later: **what has to be touched**. Name the
file/interface/boundary that isolates the change — e.g. "only the adapter in
`src/x.ts` needs swapping" — or, if it is genuinely hard to reverse, say so
plainly and why the commitment was still right.>

---
- decided by: <agent on iwts authority / user / team> · date: <YYYY-MM-DD>
- status: active · supersedes / superseded by: <links or none>
