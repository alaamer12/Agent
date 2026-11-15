# The yes/no capability matrix

A recommendation often turns on a handful of hard capability questions: can a candidate do the specific thing this project needs, in the specific mode it needs it? The capability matrix makes those questions explicit and answers them identically for every candidate, so the comparison is fair and the disqualifying facts are visible instead of buried in prose.

It is a **decision table**:

- **Rows are candidates** — and a candidate is a *(product, mode)* pair, not a bare product name (see "Split variations" below).
- **Columns are binary capability questions** derived from this project's requirements — the same questions for every row.
- **Cells are yes / no**, each carrying a short mechanism note, the version it was verified against, and its evidence (`evidence.md`).

The matrix is the **hard-gate layer** of the decision. It does not replace the dimensional weighing in `dimensions.md` — it sits in front of it. A "no" on a capability the project *must* have disqualifies a candidate regardless of how strong it is elsewhere; the dimensions then weigh the candidates that survive the gates. Soft trade-offs (ergonomics, ecosystem depth, performance under the relevant load) stay in the dimensions; the matrix is for capabilities that are present or absent, not better or worse.

## When to build one

Build a matrix when the decision has real capability gates: several plausible candidates, a concrete feature list from Step 1B, and especially when a product offers more than one mode that could change an answer. For a trivial decision with one obvious candidate and no contested capability, naming the one or two facts that settle it is enough — do not manufacture a table to look thorough. Size the matrix to the decision's stakes and the number of genuine gates, never to a desire for completeness.

## Derive the questions from the requirements

The columns come from **this project's** capability list and critical concerns (Step 1B of `process.md`, and the concrete-capability axis of `question-method.md`) — not from a generic feature checklist. Turn each requirement into a question that:

1. **Is binary and decidable.** It can be answered yes or no from public evidence, not "how good is it." 
   - Weak: "Is the data layer good?" — not decidable, not binary.
   - Strong: "Can a client read and write rows directly, with per-row permissions, without a custom backend in between?" — yes/no, checkable.
2. **Names the mode that matters.** If the project needs the capability *in a particular configuration*, the question says so, because the answer often flips by mode.
3. **Is the same for every row.** Fairness means every candidate faces the identical question set. Do not add a question only where a favorite happens to shine.
4. **Is answerable from evidence.** If a question cannot be settled yes/no from the current docs, source, and real-world proof, it is not yet a good matrix question — reformulate it into one that is, or carry it as an explicit unknown rather than forcing a guess.

Phrase questions in the project's own vocabulary. A few illustrative shapes (not a checklist to copy): "Does it support `[capability]` natively, without a plugin?", "Can `[actor]` do `[operation]` under `[constraint]`?", "Is `[feature]` available in the latest stable release, or only in `[pre-release]`?"

## Split variations into separate candidates

**A product name can hide several distinct configurations with different — sometimes opposite — capability profiles. Each mode that changes a yes/no answer is its own row.** This is the matrix form of "surface parity is not implementation parity" (`process.md`, principle 8): the product name is the surface; the mode is the mechanism.

- Name rows precisely: `[Product] — [mode]`, never bare `[Product]` when the modes differ.
- Split when a configuration flips an answer — for example a backend-as-a-service offered both as a managed document/SDK layer and as a bring-your-own relational engine; a framework in client-rendered vs server-rendered mode; a data tool accessed through a permissioned client API vs raw SQL. These are different candidates for this project even though they share a brand.
- **Do not average a product's modes into one mushy row, and do not silently pick the favorable mode.** Show the split so the user sees the real trade-off: one mode may grant client-direct access but deny raw SQL, another grants raw SQL but requires a backend in between, and a third grants both. Collapsing them hides exactly the fact that decides the choice.
- A mode that does not change any answer does not need its own row; split on *decision-relevant* difference, not on every configuration knob.

## Fill the cells with grounded evidence

Every cell is more than a bare yes/no:

- **yes / no / qualified yes / unknown.** A qualified yes ("yes, but only via `[mechanism]`") records the qualification — that is often the whole point. Unknown is an honest answer when the public record cannot settle it; never fill a gap with an assumed mechanism.
- **A short mechanism note** — *how* the capability is delivered, since two yeses can hide different internals (`dimensions.md` §Mechanism).
- **The version pin** — verified against the candidate's latest stable release per `evidence.md` Part 1. A cell about an old version is not a current answer.
- **The evidence pointer** — the doc/source/real-world proof behind the answer.

**Every disqualifying "no" must pass the real-world-proof check** (`evidence.md` Part 2) before it is allowed to eliminate a candidate. If a real application does the thing, the cell becomes a qualified yes with the mechanism cost, not a no. A false no is the failure that wrongly drops a viable option; the matrix makes that failure visible and correctable.

## Read the matrix to decide

1. **Apply the must-have gates.** Any row with a "no" on a capability the project cannot do without is eliminated (after the real-world check confirms the no is real). State which gate eliminated it.
2. **Compare the survivors** on the remaining columns and then on the dimensions that matter here. The split rows now show the genuine trade-off surface — e.g. "you can have client-direct access or raw SQL, but only `[candidate — mode]` gives both."
3. **Lead with the decision** (`process.md` Step 4). The matrix is evidence for a judgment, not a neutral menu handed back to the user. Say which row wins and what it costs.

## Output

The matrix belongs in the recommendation's **Capability matrix** section (`assets/templates/recommendation-template.md`), shown when it carried the decision — close calls, hard gates, or multi-mode candidates. Keep it proportional: a few rows and the few questions that actually decided the call, not an exhaustive grid. A worked illustration, including the variation split and a real application overturning a "no", is in `examples/capability-matrix-example.md` (illustrative; verify named tools fresh).