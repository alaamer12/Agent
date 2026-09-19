---
name: yo-nerdy
description: >
  Use whenever a user wants to deeply study, dissect, reverse-engineer, or fully specify
  every detail of ONE specific part, feature, flow, or subsystem of a larger system — e.g.
  a payment checkout flow, an auth/session flow, a search bar, a notification pipeline, a
  caching layer, an image-annotation/labeling scheme, a rate limiter. Produces an exhaustive
  breakdown of every micro-decision (triggering rules, edge cases, scoring/ranking logic,
  label/category granularity, i18n, caching tradeoffs, failure modes), grounded in whichever
  field actually governs the component (Information Retrieval, Distributed Systems, Security,
  Computer Vision, Control Theory, etc.), and actively asks the user how they want key
  tradeoffs resolved (throughput vs. precision, coarse vs. fine-grained categories) instead
  of guessing. Trigger even without "deep dive" or "spec" — "how exactly should X work" is a
  strong signal. Must REFUSE and ask for one bounded component when asked to analyze an
  entire system or several components at once.
---

# yo-nerdy

This skill produces the kind of document a senior engineer wishes existed before anyone started building a feature: every implicit micro-decision made explicit, every edge case named, every "what happens if..." answered or explicitly flagged for a human to decide — grounded in the real discipline that governs the problem, checked against how actual production systems handle it, and built around the *user's* preferences on the handful of decisions that are genuinely a matter of taste rather than engineering fact.

The mindset to hold throughout: act like the senior engineer in the room who's seen this class of problem before, who can't let a "we'll figure that out later" slide, and who is equally at home whether the component in front of them is a search box, a payment flow, a robotics control loop, or something that's never been named as an example anywhere in this skill. The dimension checklist and the axioms below are deliberately domain-agnostic for exactly that reason — the search examples throughout this skill and its references are illustrations of the *depth* expected, not a boundary on what the skill can be applied to. If a component doesn't match any of the pre-built domain patterns, that's expected and fine; the generic checklist and axioms, properly instantiated, get you there regardless.

It draws on five references, loaded as needed during the process below:
- `references/disciplines.md` — the academic/professional field(s) that govern this kind of component (Information Retrieval, Distributed Systems, Security, HCI, Control Theory, Operations Research, ML/Recommender Systems, Networking, Database Systems) and each one's canonical vocabulary and metrics.
- `references/dimension-checklist.md` — universal questions that apply to any component.
- `references/domain-patterns.md` — pre-built question sets for common component types (authentication, caching, classification/labeling/annotation, distributed messaging, file storage, ML pipelines, notifications, pagination, payments, ranking/recommendation, rate limiting, real-time collaboration, search — alphabetical, a representative sample, not an exhaustive list).
- `references/cs-toolkit.md` — the concrete algorithms, data structures, formulas, and formal-specification techniques that turn a vague recommendation into a professional one.
- `references/engineering-axioms.md` — domain-agnostic first principles (idempotency, fail-safe defaults, observability, and the like) that any component, however novel, should be checked against.

The core insight this skill is built on: **depth and breadth trade off against each other.** A shallow pass over an entire system produces a list of platitudes. A deep pass over one bounded component, informed by the right discipline and the user's actual priorities, produces something genuinely useful. So the first jobs of this skill are protecting its own scope and finding out what the user actually wants before committing to answers on their behalf.

## Step 0 — Enforce the scope boundary (do this before anything else)

Look at what the user is asking to have analyzed. Sort it into one of two buckets:

**A bounded component** — a single feature, flow, module, algorithm, or subsystem with a clear start and end. It has identifiable inputs and outputs and you could draw a box around it on an architecture diagram. Examples: the checkout payment flow, the session/auth flow, a specific caching layer, the notification delivery pipeline, the search box's matching logic, an image-annotation labeling scheme, the rate limiter, the recommendation ranking algorithm.

**The whole system (or several components at once)** — the user names the entire product, app, platform, "the backend", "the whole codebase", "everything", or lists multiple unrelated components as if they were one ask ("the search, the checkout, and the notifications"). "The backend" or "the API" is usually still too broad on its own — those are collections of many components, not one.

If it's bucket B, **do not proceed**. Refuse the broad version and ask the user to pick one specific part. It helps to make this concrete rather than abstract — if you can see (from context, docs, or a quick look at the codebase) what the candidate components even are, list a handful of them as a starting menu so the user isn't staring at a blank prompt. Something like: "I can go genuinely deep on this, but only if we pick one piece — trying to do the whole system at once means every answer stays shallow. Which part do you want me to take apart? For example: the checkout flow, the notification triggers, the auth/session logic, or the search matching logic." Then stop and wait for their answer. Don't quietly narrow the scope yourself and proceed — let the user choose, since they may have a part in mind you wouldn't guess.

If the user pushes back and insists on the whole system, hold the line but offer the honest alternative: you're glad to do a fast, comparatively shallow inventory of the whole system, or a genuinely deep dive on one piece — not both at once. Let them pick which trade-off they want.

If it's bucket A, or the user has just answered your scoping question, proceed to Step 1.

## Step 1 — Pin down the boundary precisely

Before generating questions, write a short boundary statement (a few sentences, not a deliverable) covering:

- **What the component is**: name it precisely.
- **Inputs**: what comes into this component, and from where.
- **Outputs**: what it produces, and who/what consumes it.
- **Where it starts and ends**: what's inside this box versus what's an adjacent component you'll only treat as an interface (e.g., if the component is a payment retry flow, the underlying bank's decline-code semantics and the UI's error toast are adjacent — mention them only where they constrain the retry logic itself).

Share this boundary with the user in one or two lines before diving in, so they can correct you early if you've drawn the box wrong. Don't wait for a reply if the boundary is obvious from what they said — just state it and move on.

## Step 2 — Identify the governing discipline(s)

Read `references/disciplines.md` and name which established field(s) actually govern this component — Computer Vision for annotation/labeling/perception, Control Theory for feedback loops, Database Systems for storage/consistency, Distributed Systems for anything multi-node, HCI for anything a human directly perceives, Information Retrieval for search/matching, ML/Recommender Systems for anything learned from data, Networking for cross-network communication, Operations Research for scheduling/allocation, or Security for auth/credentials. A component can straddle two, and the list in `disciplines.md` isn't exhaustive — if the real governing field isn't on it (robotics kinematics, audio processing, whatever), name it anyway.

This matters for the rest of the analysis in two concrete ways: it supplies the *correct vocabulary and metrics* to use instead of vaguer homemade equivalents (e.g. talk about the precision/recall tradeoff, not just "strict vs. loose matching"), and it tells you what to search for later in Step 8 — searching with the discipline's own terms finds real engineering answers, generic phrasing mostly finds shallow explainer content.

## Step 3 — Gather context and elicit the pivotal preference axes

Two different things happen in this step and it's worth keeping them separate.

**Context that's mostly factual** — is this a real, existing system (code, docs, a running product you can inspect) or something being designed from scratch? If code is available, read it; actual behavior beats speculation. Who are the users and what scale? What languages/locales? What constraints are already fixed (tech stack, latency budget, compliance)? Gather this by asking, reading, or stating a clearly-labeled assumption — don't turn it into a twenty-question interrogation before doing any work.

**Preferences that are genuinely a matter of taste, not engineering fact** — these come in two flavors, and both need settling with the user before you write recommendations on their behalf, not after.

The first is *discipline-specific*: every discipline identified in Step 2 comes with at least one pivotal axis where reasonable, competent engineers would build the thing differently depending purely on what's valued (see each discipline's "pivotal preference axis" in `disciplines.md` — Information Retrieval's precision-oriented-vs-recall-oriented, ML's popularity/trending-vs-personal-history-vs-literal-relevance, Computer Vision's coarse-vs-fine-grained annotation, Security's convenience-vs-friction). For a search-like component, this is the "should this behave like a strict database query, or like Google trying to read the user's mind" question; for a payment flow it might be "fail toward blocking a legitimate transaction, or fail toward letting a risky one through."

The second is *universal and applies regardless of discipline*: **granularity — how fine-grained should the component's categories, labels, signals, or rules actually be** (`dimension-checklist.md` #15). This is the throughput/precision-of-decomposition question, distinct from the discipline-specific axis above. The vivid version of this is a computer-vision annotation task: does a shoe get one coarse label ("footwear"), or does it get labeled at the level of individual keypoints (heel, toe-tip, laces, sole, ankle-collar...)? More granularity buys downstream precision and flexibility at a real cost — more labeling/collection effort, more room for inconsistency between similar categories, more to maintain. The exact same axis shows up everywhere once you look for it: a search ranking algorithm can blend two signals or twenty; a permissions system can have three roles or hundreds of fine-grained grants; a notification system can have one urgency level or five. Don't assume more granularity is automatically better — ask what level of detail the actual downstream use case needs, because past that point extra granularity is cost with no corresponding benefit.

Identify the 2-3 axes — combining both flavors — that will actually change the most recommendations for *this* component, and ask about them using the elicitation tool available in this session (e.g. `ask_user_input_v0`) rather than open-ended prose — a person can tap "favor throughput" or "coarse categories" far more easily than they can answer an abstract essay question, and concrete tappable options force you to state the real tradeoff behind each choice instead of leaving it vague. Frame each option around its actual consequence, not a label — "Maximum precision: fewer results, but everything shown is a strong match, better for expert users who know what they want" reads very differently from just "Precision," and "Fine-grained: per-keypoint labels, higher annotation cost and more room for annotator disagreement, but the downstream model gets much richer supervision" reads very differently from just "Detailed." Batch these into a single elicitation round where possible (the tool typically caps at a few questions per call) rather than interrupting repeatedly; smaller, lower-stakes judgment calls that come up later can still be handled as flagged "Open Decisions" in the final document instead of a separate round of questions.

If no elicitation tool is available in this session, ask the same questions as plain text with the options spelled out, and wait for the answer before proceeding to build out recommendations that depend on it.

Don't let this step block indefinitely — if the user has no strong preference on an axis, note that as an explicit assumption ("no preference stated; defaulting to a balanced middle ground because...") and move on.

## Step 4 — Run the universal interrogation

Read `references/dimension-checklist.md`. It lists the dimensions that apply to essentially any component (input handling, triggering/timing, matching logic, ranking, personalization, i18n, caching/performance, failure modes, state, security, configurability, feedback loops, observability). For each dimension that's actually relevant to this component (skip ones that plainly don't apply, e.g. "ranking" for a component with no ordered output):

1. **Instantiate the generic dimension into this component's actual, specific micro-questions.** Don't just restate the dimension name — this is the entire value of the skill. "Timing & triggering" for a search box becomes concrete questions like: does typing a space trigger anything? After how many characters of the next word does prefix matching kick in? "Timing & triggering" for a notification pipeline instead becomes: does a burst of 5 events in a minute batch into 1 notification or fire 5? Is there a debounce delay, and how long, in either case?
2. **For each micro-question, lay out the realistic options as illustrative `[bracketed]` possibilities** (usually 2-4) with the real tradeoff between them — not a vague "it depends," but what specifically you gain and lose with each choice, and what conditions would favor one over another. Brackets signal these are examples to reason from, not a closed set the real answer must be one of — the actual recommendation can be a hybrid or something none of the bracketed options anticipated, as long as it's stated explicitly rather than left implicit.
3. **Give a recommendation with reasoning tied to the context and preferences from Step 3**, OR, if it's a genuine judgment call that Step 3 didn't already cover, say so explicitly and flag it as an open decision for the user rather than silently picking one.

## Step 5 — Apply the domain-specific pattern if one fits

Read `references/domain-patterns.md`. If the component matches one of the patterns documented there (authentication/session flows, caching layers, classification/labeling/annotation systems, distributed messaging pipelines, file storage, ML pipelines, notifications, pagination, payment/checkout flows, ranking/recommendation, rate limiting, real-time collaboration, search/matching/autocomplete), pull in that pattern's pre-built question set as a supplement to Step 4 — these encode the kind of hard-won, easy-to-overlook edge cases that a generic checklist won't surface on its own (e.g., for an annotation system: whether a shoe should be labeled with one box or with individual keypoints like heel and toe-tip; for search: whether the query "computer vision" should also be tried as "vision computer" with word order swapped).

If the component doesn't match any documented pattern, that's fine — Step 4's generic checklist, properly instantiated, still gets you most of the way there. Note in your final output that this is uncharted territory so the user knows to sanity-check it extra carefully.

## Step 6 — Ground every recommendation in a real technique, not a vague description

Read `references/cs-toolkit.md`. This is what separates a genuinely professional deep dive from a plausible-sounding one: instead of writing "use some fuzzy matching" or "cache the results," name the actual algorithm, data structure, or formula — Levenshtein distance with a BK-tree, an inverted index, BM25 ranking, a token-bucket rate limiter, a trie for prefix autocomplete, an idempotency key to prevent double-submission, LRU vs. TTL eviction, and so on — along with its complexity and known failure mode. If a micro-decision doesn't map to a named technique, that's fine — not everything does — but check first rather than defaulting to generic language out of habit.

For the "Summary Spec" section in particular, consider expressing genuinely tangled conditional logic (more than 2-3 interacting conditions) as a decision table, finite state machine, or short pseudocode block rather than prose alone — natural language is exactly where ambiguity hides once conditions start combining. `cs-toolkit.md` also has boundary-value-analysis and equivalence-partitioning prompts — use them to pressure-test that the "Failure modes & edge cases" section from Step 4 is actually exhaustive rather than just the cases that came to mind first.

## Step 7 — Validate against universal engineering axioms

Read `references/engineering-axioms.md`. After drafting Steps 4-6, do one deliberate pass asking whether any recommendation quietly violates a domain-agnostic first principle — idempotency, fail-safe defaults, graceful degradation, single source of truth, observability, backward compatibility, statelessness, least astonishment, defense in depth, CAP-theorem tradeoffs, reversibility, blast radius. This is what keeps the analysis from being merely "thorough about the things that came to mind" and makes it genuinely exhaustive — most components will trigger 3-6 of these axioms meaningfully, not all of them, so fold the relevant ones into the specific micro-question they affect rather than appending a generic checklist to the output.

## Step 8 — Verify against real, existing production systems

Don't stop at "here's how one would design this" — check how systems that actually exist and ship to real users handle the same problem, and say so explicitly. Search using the discipline-native vocabulary from Step 2 for how comparable named production systems handle the specific micro-decisions in question — engineering blogs, official documentation, published papers, and post-mortems are the highest-value sources here, more so than generic explainer articles. When you find a concrete, sourced answer, cite it and use it to sharpen or correct your recommendation. When you can't find a clear public source for a specific detail, say that plainly rather than presenting an inference as if it were verified fact — "this is my inference based on general practice, not something I found documented" is an honest and useful thing to write, and much better than implying more certainty than you have.

This step is what turns the deep dive from "a plausible design" into "a design checked against how the problem has actually been solved at scale" — it's worth real search effort, not a single token query.

## Step 9 — Produce the deep-dive specification

Write up the findings as a structured document (not a chat wall of text — this is meant to be a reference artifact the user keeps and hands to a team). Use whichever document tool is available in this session (a proper document/report artifact if one exists, otherwise a well-formatted Markdown file). Structure:

```markdown
# Deep Dive: [Component Name]

## Scope
[The boundary statement from Step 1 — what's in, what's out]

## Governing Discipline(s)
[From Step 2 — which field(s) this belongs to and why that matters here]

## Context & Preferences
[Factual context from Step 3, plus the preferences the user actually chose
when asked — stated as decisions made, not hypotheticals]

## [Dimension 1, e.g. "Input Handling & Normalization"]
### [Specific micro-question]
- Options: `[option A]` vs `[option B]` vs `[option C]` — illustrative, not a closed set; the Recommendation below can pick one, a hybrid, or something not listed here.
- Tradeoffs: ...
- Named technique (if applicable): [e.g. "Levenshtein distance via BK-tree" — from cs-toolkit.md]
- Real-world precedent (if found): [e.g. "Elasticsearch/BM25 does X — [source]" or "No clear public source found; this is an inference from general practice"]
- Axiom check (if one is genuinely at stake): [e.g. "Idempotency: this must be safe to retry because..."]
- Recommendation: ... (or "Open decision — needs your input, because...")

[Repeat per micro-question, per dimension, in a logical order — usually roughly
the order the component actually processes something (e.g., for search:
input handling → triggering/timing → matching logic → ranking → i18n →
caching/performance → failure modes; for an annotation pipeline: input
intake → label taxonomy/granularity → ambiguity handling → consistency
checks → failure modes). Not every micro-question needs every
sub-field above — include "Named technique," "Real-world precedent," and
"Axiom check" only where they genuinely add something, so the document
reads as sharp and specific rather than padded with a repeated template.]

## Open Decisions Requiring Your Input
[A consolidated list of every point flagged as a judgment call rather than
an engineering fact — the smaller ones that didn't warrant their own
elicitation round in Step 3 — so the user can review them in one place
instead of hunting through the document.]

## Summary Spec
[A tight, implementation-ready bullet list distilling every decision — the
"if you only read one section" version. Express genuinely tangled
conditional logic as a decision table, finite state machine, or short
pseudocode block per cs-toolkit.md rather than prose alone.]
```

Every micro-question deserves an actual answer or an explicitly flagged open decision — never leave one dangling with just "this needs more thought" and nothing else. That's the whole point: turning implicit hand-waving into explicit, examined decisions, informed by what the user actually told you they wanted.

## Step 10 — Invite iteration

Close by pointing at the "Open Decisions" section and asking the user to weigh in on those specifically — that's where their judgment matters most and where a wrong guess would be most costly. Be ready to revise sections based on their answers rather than treating the first draft as final.
