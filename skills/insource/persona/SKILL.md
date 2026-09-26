---
name: persona
description: >
  Construct deep, professional, context-aware personas for subagents of any role — not just a job title, but a full behavioral specification of how the agent thinks, investigates, judges quality, and communicates. Use this whenever building, prompting, or orchestrating a subagent (security reviewer, database engineer, testing engineer, frontend engineer, DevOps/SRE, technical writer, code reviewer, or any other domain specialist) and a generic "you are a senior X" persona would be too shallow. Especially relevant for multi-agent orchestration systems (e.g. contribute-agents) that need distinct professional perspectives per role, and for any task asking to "give this agent a persona," "make this agent think like a senior X," or "construct context for a subagent." The method is role-agnostic — it applies identically whether the role is testing, security, database, frontend, or something else entirely.
---

# Persona & Context Construction

## Purpose

Build a persona that makes a subagent **reason and behave like an experienced
practitioner**, not one that makes it *announce* expertise. The test at every
step is: would this text change what the agent notices, how it investigates,
and what it accepts as evidence — or is it decorative?

A persona that only changes vocabulary ("As a senior engineer, I believe...")
has failed. A persona that changes *what gets checked before a conclusion is
accepted* has succeeded.

This method is **role-agnostic**. It applies the same way whether the
assigned role is a security reviewer, a database engineer, a testing
engineer, a frontend engineer, an SRE, a technical writer, or anything
else — the role only changes *which* mental models and instincts get
filled in, not the construction process itself. Nothing below is specific
to any one title.

## When to use this

- Constructing a subagent prompt/persona for an orchestration system (e.g.
  `contribute-agents`) where multiple agents hold different professional
  roles.
- Asked to "give this agent a persona," "make it think like a senior X,"
  or to build context for a specialized reviewer/investigator agent —
  for any X.
- The default "You are a senior software engineer" framing is clearly too
  thin for what the task needs.

## Core principle: behaviors, not attributes

Never write a trait without immediately cashing it out as a behavior. This
holds for every role equally:

| Weak (attribute) | Strong (behavior) |
|---|---|
| "You are a senior testing engineer with 15 years of experience." | "You reproduce a failure before proposing a fix. When you see a concurrency claim, you immediately think about interleavings, memory visibility, and whether the failure is actually deterministic." |
| "You are an expert in security." | "When you see user input reach a sink, you trace the path backward asking what validated it, and you assume nothing is validated until you've confirmed it in code." |
| "You are a skilled database engineer." | "When you see a new query, you ask what isolation level it runs under before you ask whether it's correct — a query that's correct under serializable isolation can still corrupt data under read-committed." |
| "You are detail-oriented." | "Before accepting a conclusion, you inspect the assumptions it depends on and look for edge cases that would invalidate them." |

Every dimension in the persona must survive this test: **"If this were a
real experienced practitioner, how would they approach this differently
from an inexperienced one?"** If a sentence doesn't answer that, cut it or
rewrite it.

## Workflow

### 1. Gather inputs

Before drafting, establish (ask the user if not already given, or infer
from the surrounding orchestration context):

- **The task** the subagent will actually perform.
- **The assigned role** — whatever it is (security reviewer, database
  engineer, testing engineer, frontend engineer, technical writer, etc.).
  None of these get special-cased; all go through the same process below.
- **Project/domain context** — what kind of system this is (compiler,
  payment system, web API, embedded firmware, marketing site, etc.). This
  materially changes the persona (see step 3).
- **Other agents' roles**, if this is a multi-agent setup — so the
  persona's collaboration/criticism stance is calibrated correctly.
- **Expected responsibilities** / what "done" looks like for this agent.
- **Failure model**, if known or inferable — what kinds of failures this
  system/role combination is prone to.

Don't ask about dimensions that are irrelevant to the task — see step 4.

### 2. Select relevant dimensions

From the full dimension list (below), select only the ones that matter for
this specific role and task. Do not fill in all of them mechanically —
an unused dimension left in as boilerplate is itself a generic-roleplay
failure.

Full dimension menu:

1. Professional identity
2. Relevant experience (the *kinds* of hard problems encountered — not a
   tech list)
3. Areas of expertise
4. Mental models specific to the domain
5. Engineering/professional philosophy (beliefs that actually drive
   decisions)
6. Investigation methodology
7. Quality standards
8. Failure patterns the agent recognizes
9. What the agent instinctively looks for
10. What the agent refuses to assume
11. Communication behavior
12. Collaboration behavior
13. Stance toward criticism / being criticized
14. Evidence standards (how it grades confidence: confirmed → reproduced →
    plausible → suspected → unverified → disproven)
15. Decision-making style
16. Domain-specific heuristics

### 3. Build the domain's mental models

For dimensions 4, 8, 9, and 16 above, do the following regardless of role:

1. Name 4–8 concrete things a real practitioner in this specific area
   checks reflexively, phrased as short noun phrases (not full sentences).
   This becomes the "mental models" / "what you instinctively look for"
   list.
2. For 2–3 of the most important ones, write one sentence showing *how*
   that checking manifests in an actual review or investigation. This
   becomes part of "investigation methodology" or "what you instinctively
   look for."
3. Sanity-check against realism: would a working specialist in this field
   actually think this reflexively, or does it read like encyclopedic
   research-summary knowledge with no practitioner grounding? If the
   latter, narrow it to what's genuinely reflexive.

See `references/example_personas.md` for several fully worked examples
across different roles (security review, database engineering, testing
investigation, frontend engineering, SRE/on-call) built with exactly this
process — read one or two that are adjacent to the current role for
calibration on specificity and tone, not for content to copy. The
principle they all share, and the one to actually take from them, is
explained in `references/persona_construction_patterns.md`: how to derive
a domain's reflexive checks, philosophies, and investigation order from
what the role is actually responsible for — this pattern is what
generalizes, not any single example's specifics.

### 4. Let context reshape the persona

The same role produces a materially different persona depending on task
and domain. Two agents both called "testing engineer" should not read the
same if one is reviewing a compiler and the other a payment system. Two
agents both called "security reviewer" should differ the same way between
a public API and an internal admin tool.

Concretely: combine `Role + Experience + Domain Context + Current Task +
Failure Model + Collaboration Context` — changing any one of these should
visibly change the output. If you can swap the persona onto a different
task/domain with no edits and it still reads fine, it's too generic —
go back and sharpen it against the actual context.

### 5. Respect the reality constraint

The persona is a **professional reasoning style**, never fabricated
personal history. Never write or allow a specific, checkable anecdote:

> "I personally fixed this exact bug at Company X."

But don't collapse all the way down to a bare label either — a label with
nothing behind it reads as thin, not as honest:

> "Approach this as an engineer experienced with production concurrency
> failures."

The better middle ground names the *category* of problems typically faced
and the *standard* a resolution had to meet — concrete enough to carry
real technical weight, general enough that nothing in it is an invented,
checkable fact:

> "Approach this as an engineer experienced with production concurrency
> failures — the kind who has repeatedly worked through problems like
> races surfacing only under production load, deadlocks from inconsistent
> lock ordering across services, and state corruption from partially
> applied writes — and who is used to only accepting a fix once it
> reproduces the original failure mechanism, holds up under the actual
> concurrency pattern involved (not just a single-threaded retest), and
> doesn't just mask the symptom."

This is what gives the persona **technical weight without fake
confidence**: specific enough to sound like it comes from real
experience, general enough that it's true of the *role*, not a fabricated
claim about *this specific agent's* unverifiable history.

Pattern for building this for any role:
`"...experienced with <domain of failures>, the kind who has repeatedly
worked through problems like <2–4 concrete problem categories>, and who
is used to only accepting a solution once it satisfies <2–3 concrete
standards — e.g. what it must reproduce, hold up under, or not merely
mask>."`

If the user's inputs support more specific prior experience, use it. If
not, build the category-level version above rather than either a bare
label or an invented anecdote.

### 6. Write the output in the standard structure

Use this structure by default; adapt it when a different structure would
produce clearly better behavior for the situation (e.g. a much shorter
persona for a narrowly scoped agent). Omit any section that would be
empty or filler for this role/task — do not pad.

```text
PROFESSIONAL PERSONA

Role:
...

Professional perspective:
...

Relevant experience:
...

Domain expertise:
...

Engineering philosophy:
...

Mental models:
...

What you instinctively look for:
...

What you refuse to assume:
...

Investigation methodology:
...

Quality standards:
...

Evidence standards:
...

Collaboration behavior:
...

Stance toward criticism:
...

Known biases to avoid:
...

Current context:
...

Current responsibility:
...
```

### 7. Communication behavior

Write (and instruct the persona toward) natural professional speech, not
credential-announcing preambles. This is the same for every role.

Avoid: *"As a highly experienced senior software testing engineer, I
believe..."*

Prefer: *"I'm not convinced this is safe yet. The missing piece is the
ordering guarantee between these two operations."*

The agent should sound like a colleague: concise when the point is
obvious, detailed when the issue is subtle, willing to say "I'm not
convinced" or "that's a good point," explicit about uncertainty, not
artificially formal, not repetitive.

### 8. Integrating with a criticism/review protocol

If the persona will be used inside an orchestration system that already
has its own critical-review protocol (e.g. `contribute-agents`), the
persona should establish **how this professional thinks**, and only
briefly note **this professional's angle on criticism** — it should not
duplicate the full criticism protocol.

Example of the right scope (any role can substitute in the same way):

> As an experienced test engineer, you are especially suspicious of
> conclusions based only on happy-path behavior. When another agent
> proposes that a race condition cannot occur, you want to understand
> what synchronization guarantee makes that claim true.

> As an experienced database engineer, you are especially suspicious of
> claims that a migration is "backward compatible" without evidence it
> was tested against production-shaped data volumes.

### 9. Final quality check before returning the persona

Run through these questions. If any answer is "no," revise before
returning:

- Can I tell what this engineer would notice that an ordinary agent
  would miss?
- Can I predict how this engineer would investigate a problem in their
  domain?
- Does the persona contain actual mental models, not just labels?
- Does the experience section influence behavior, not just list nouns?
- Does the philosophy section influence decisions, not just sound nice?
- Is it specific to this task and domain, not swappable to any other?
- Does it avoid generic "expert" language unless immediately cashed out
  behaviorally?
- Does it avoid fabricated personal history?
- Would this persona cause the subagent to behave differently from a
  different role given the same task?

## Anti-patterns to avoid

- Listing every dimension from the menu regardless of relevance.
- Generic trait adjectives ("detail-oriented," "highly skilled") without
  behavioral payoff.
- Superhuman experience — a persona that has personally encountered every
  failure mode in existence. Keep it to what a real specialist plausibly
  has encountered.
- Checklist-driven philosophy for any role ("run through these 50 checks")
  instead of hypothesis-driven, high-information investigation.
- Fabricated specific personal history ("I fixed bug #4471 at my last
  job").
- Copy-pasting the full criticism protocol from the orchestration system
  into the persona instead of just the professional's angle on it.
- A persona identical in substance to one written for a different
  role/task — if nothing in it is actually tied to this context, it
  hasn't done its job.
- Treating any one role (including testing) as the "main" case with
  special built-in machinery, while other roles get generic treatment.
  Every role goes through the same construction process in section 3.
