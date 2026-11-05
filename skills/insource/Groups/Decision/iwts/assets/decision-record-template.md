# Decision record — <short title>

<!--
  ONE FILE PER DECISION: copy to the project's decisions location - the
  AGENTS.md Ambiguity/decision-records section owns where that is; default
  <docs>/decisions/<slug>.md (docs folder wherever it lives). A combined
  decisions.md log is the explosion anti-pattern; states.md indexes instead.
  Write for the reader who finds this in six months with zero context: they
  must be able to re-derive the choice. One record per lasting decision -
  not per commit, not per TODO. The decision NOT to ask (and what was
  assumed instead) deserves this file too, under anonymity above all.
-->

- date: <YYYY-MM-DD> · commit: <hash at the moment of deciding> · app-version: <version in effect;
  state the change when it differs from the previous record>
- decided by: <agent on iwts authority / user / team> · status: active · supersedes / superseded by:
  <links or none>

## Decision

<What was decided, in one or two sentences. State it as fact: "We use X for Y.">

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
