# Universal Engineering Axioms

The dimension checklist, domain patterns, and CS toolkit are about *this specific component*. This file is different on purpose: it's a set of first-principles checks that apply to literally any component — a search bar, a payment flow, a video-streaming buffer, a robotics control loop, a spreadsheet formula engine, anything. These are not "search-flavored" ideas dressed up as generic ones; they're the actual invariants a senior engineer checks by reflex, regardless of domain. Run every recommendation from Steps 4-6 back through this list before finalizing it. A recommendation that violates one of these without an explicit, stated reason is very likely a bug the analysis missed, not a legitimate design choice.

**How to read the "Check" lines below**: each axiom includes a `[bracketed]` illustrative pair or set of the way a component typically leans on that axiom. As with `domain-patterns.md`, these are examples to reason from, not a mandatory checklist to force the component into — the point of each Check line is to surface the question, not to require the answer be literally one of the bracketed words.

**Idempotency.** If the same operation happens twice (a retried request, a duplicate event, a repeated click), does the result stay correct, or does it double up? Anything that writes, charges, sends, or mutates state needs an explicit answer here — "the client won't ever retry" is not an answer, because networks retry regardless of what you assume.
- Check: `[safe to repeat, e.g. protected by an idempotency key]` vs `[not safe to repeat, and nothing currently prevents a repeat]`.

**Determinism (where it should hold).** Given the same input and the same state, does this component produce the same output? If not, is the non-determinism deliberate and bounded or is it an accident of implementation that will make debugging and testing miserable?
- Check: `[deliberate, bounded non-determinism, e.g. intentional randomized A/B assignment or exploration in a ranking algorithm]` vs `[accidental non-determinism, e.g. unordered iteration, race conditions, floating-point drift]`.

**Fail-safe defaults.** When this component is uncertain, times out, or hits an error it didn't anticipate, which way does it fail?
- Check: `[fails toward safety/restriction]` vs `[fails toward permissiveness/action]` — for anything security- or money-adjacent, the latter (failing open) is usually the wrong default even if it's more convenient.

**Graceful degradation vs. total failure.** If one dependency of this component goes down or slows down, what happens?
- Check: `[degrades to a reduced-but-functional state, e.g. cached/stale data, a simpler fallback algorithm, partial results]` vs `[the whole component stops working]`. Name the actual degraded behavior — "it handles errors gracefully" is not a design; "falls back to the last cached ranking for up to 10 minutes, then shows an explicit stale-data notice" is.

**Single source of truth.** Is there ever a second copy of the same fact (a cached value, a denormalized field, a client-side mirror of server state) that can silently drift from the original?
- Check: `[a single authoritative copy]` vs `[multiple copies with an explicit, stated reconciliation rule]` vs `[multiple copies with no reconciliation rule — a latent bug]`.

**Observability by construction.** Could someone looking only at logs/metrics/traces tell *why* this component made a particular decision, or only *that* it produced some output?
- Check: `[decisions are traceable to the signals that caused them]` vs `[only the final output is visible, the reasoning is a black box]`.

**Backward/forward compatibility.** If this component's behavior or output format changes later, what breaks?
- Check: `[a version field or migration path exists]` vs `[the next change will be a breaking one by default]`. Are there consumers (other services, cached data, client apps that can't be forced to update instantly) that assumed the old behavior?

**Statelessness where it's not needed.** Does this component hold state in memory that could instead live in a well-defined store?
- Check: `[stateless, trivially scalable and recoverable]` vs `[stateful by genuine necessity, e.g. an in-progress multi-step flow, with an explicit recovery/replication story]` vs `[stateful by accident, with no recovery story]`.

**Principle of least astonishment.** Would a reasonable user or downstream engineer be surprised by this behavior even after it's explained to them?
- Check: `[behavior matches the obvious expectation]` vs `[a subtle, technically-defensible deviation, e.g. a search that silently excludes exact matches in favor of "smarter" ones, a payment retry that silently changes the charged amount, a permission check that behaves differently depending on request order]`.

**Defense in depth.** Is there exactly one layer responsible for catching a given class of error, or are there independent layers that would each catch it if the other failed?
- Check: `[a single point of enforcement, e.g. only client-side validation or only one permission check]` vs `[independent layers that each catch the error class]`. A single point of enforcement is a single point of failure.

**Explicit tradeoff naming in distributed contexts.** If this component spans multiple nodes/services, the CAP theorem says you cannot get perfect consistency, availability, and partition tolerance simultaneously.
- Check: `[explicitly names which of consistency/availability is sacrificed, and under what condition]` vs `[implies the design achieves all three without saying which is traded away]`.

**Reversibility.** Given a choice between two designs of similar quality, does one leave more room to change your mind later?
- Check: `[a reversible choice, e.g. soft deletes, versioned config, additive schema changes]` vs `[an irreversible choice, e.g. hard deletes, hard-coded constants, destructive schema changes]`. Early-stage or fast-moving components should lean reversible unless there's a concrete reason not to.

**Blast radius of a wrong default.** How many users, how much data, or how much money does this component touch before a mistake would be noticed and correctable?
- Check: `[small blast radius — an internal tool, easily caught in review]` vs `[large blast radius — silently applied to every user for months before anyone would notice]`. Weigh how much scrutiny and reversibility a decision deserves against how much it could hurt if wrong.

## How to use this list

Don't turn this into fourteen extra questions bolted onto every micro-decision — that would bury the specific, useful analysis under generic process. Instead, after drafting Steps 4-6's answers, do one pass asking: "does any recommendation I just wrote down quietly violate one of these axioms without me noticing?" Call out the ones that are genuinely at stake for this component (most components will trigger 3-6 of these, not all 14) and fold that into the relevant micro-question's answer rather than as a separate wall of text.
