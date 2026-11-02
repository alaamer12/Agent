---
name: commitments-md
description: 'Creates and maintains COMMITMENTS.md - the project''s declared goals, priorities and trade-offs - or a small Commitments section in AGENTS.md when tiny. Premise: you cannot get the gold in every case. Some goals are mutually exclusive, some reinforce each other, and every priority has a price, a horizon (MVP vs later) and, where possible, a measurable bar. The skill never invents priorities: it collects the stated goals, maps which ones compete, asks which wins when they collide and what is sacrificed, marks the pairs that do not conflict so nobody pays for a fake trade-off, and records the hard constraints that are never traded. Placement: a small set goes into AGENTS.md; a big set (several dimensions, conflict tables, phases) becomes COMMITMENTS.md with a pointer from AGENTS.md. Triggers: ''what are our priorities'', ''what should we sacrifice'', ''is DX more important than perf here'', ''define the trade-offs''. Not the idea itself (idea-md), not choosing the stack (techstack/thebest), not task planning (planner).'
when_to_use: The user states competing goals, asks which priority wins, wants the project's trade-offs written down, or a project needs its commitments recorded/updated. Also /commitments-md.
argument-hint: "[the project, or the goals/priorities to record]"
---

# commitments-md — the project's declared trade-offs

A project's priorities are decisions, and decisions have prices. COMMITMENTS.md states **what we optimize
for, in what order, at what cost, over which horizon** - so that every later agent resolves a trade-off the
same way instead of optimizing whichever dimension it happens to be touching.

**The premise: you cannot get the gold in every case.**

> The dimensions and conflicts below are **examples, not a closed list, and not a web list**. A phone app, a
> CLI tool, a game, a data pipeline, a library or a firmware project each has its own set - the method is the
> same, the dimensions are the project's own. Unlisted dimensions and hybrid answers are always acceptable.

## What a commitment is

| Element | The question it answers |
|---|---|
| **Dimension** | What are we optimizing - [performance] / [latency] / [accuracy] / [battery use] / [install size] / [accessibility] / [DX] / [ecosystem maturity] / [time-to-market] / [security] / [privacy] / [maintainability] / [cost] / [design fidelity] / [offline behavior] / … (illustrative - use the ones this project actually has) |
| **Priority** | Where it ranks when two dimensions collide: the winner, and the loser's accepted degradation |
| **Price** | What we knowingly give up or pay to hold this priority |
| **Horizon** | When it applies - now (MVP), later (v1), at scale - because priorities legitimately change by phase |
| **Bar** | The measurable "good enough" where one exists (e.g. `[p95 latency < 100ms]`, `[crawlable with JS disabled]`, `[Battery ≤ 3%/hour]`, `[Lighthouse ≥ 95]`) - examples, not the only possible bars; measurements belong to `benchmark`, the bar belongs here |

## Three relationships - the heart of the skill

1. **Mutually exclusive (they collide).** Examples, not a fixed list: `[raw performance]` versus `[ecosystem
   maturity]` (a newer, faster option with a thin ecosystem against a mature one); `[time-to-market]` versus
   polish dimensions; `[accuracy]` versus `[battery use]` on an always-on sensor; `[throughput]` versus
   `[cost]` in a data pipeline; `[SEO]` versus rich client interactivity on a content site. When these
   collide, **one wins and the other pays**. Record which and why.
2. **Compatible (they reinforce).** Examples: `[security]` and `[maintainability]` (fewer data paths, fewer
   mechanisms); `[accessibility]` and `[clarity]` (both force plain structure); `[performance]` and
   `[accessibility]` on lean interfaces; `[latency]` and `[cost]` when batching serves both. **List these
   pairs explicitly**, so a future agent does not invent a sacrifice that the project never agreed to pay.
3. **Conditional (they depend on the phase or the context).** "Before launch: ship; after launch:
   performance." "Mobile reach matters more than desktop polish." The condition is part of the commitment,
   not an exception to it.

## Procedure

1. **Collect the stated goals** from the conversation, IDEA.md, AGENTS.md, the plan. Write them down in the
   user's words before ranking anything.
2. **Name the dimensions** the goals touch; add the ones the project's nature implies but the user has not
   mentioned, **as questions**, never as assumed priorities.
3. **Map the conflicts.** For every pair that competes, ask the decisive question: *"When <X> and <Y>
   collide, which wins - and what are we willing to give up?"* Also ask: *"What must we never sacrifice,
   even for a preferred goal?"* One focused question per real tension, not a fifty-question form.
4. **Mark the compatible pairs** to prevent fake trade-offs, and the conditional priorities with their
   horizon.
5. **Find the bar** where measurability exists: a number or a named check per dimension. No number means
   the priority is aspirational - label it so.
6. **Choose placement** (below), then write.
7. **Maintain:** when a priority changes - a new phase starts, a goal is dropped - update the document in
   the same change. Stale priorities are worse than none: every later trade-off resolves the old way.

## Placement - small into AGENTS.md, big into COMMITMENTS.md

| Size | Where | Why |
|---|---|---|
| A few lines: one or two dimensions, no conflict table, one horizon | **AGENTS.md**, as a short `Commitments` list (or a paragraph inside section 1/section 2's routing) | a small priority set is a rule, and rules belong in the rulebook |
| Bigger: several dimensions, conflict resolutions, phases, measured bars | **COMMITMENTS.md** at the project root, with a one-line reference + reading duty added to AGENTS.md's mandatory context | the rulebook stays under its per-section budget; the detail lives where it can grow |

The same extraction logic as agents-md's section budget: if the commitments would push an AGENTS.md
section past ~50 lines, they are a document. **agents-md owns AGENTS.md; this skill owns the commitments
content** - when the content goes into AGENTS.md, the section is written as rules plus the pointer to
COMMITMENTS.md, and agents-md's conventions for that file are followed.

## Rules

- **Never invent a priority.** Not from the stack, not from "what a good project would do", not from the
  code's current behavior. Unanswered is an open question.
- **Every priority states its price.** A priority with no price has not been decided - it is a wish.
- **Every priority states its horizon.** "Maximum performance" without "at launch / at scale" will be
  argued about forever.
- **Hard constraints are separate.** "Never sacrifice" items (security of user data, the privacy list,
  license, the project's core promise) are not optimizations and cannot be traded away.
- **No fake trade-offs.** Before recording a conflict, check whether one solution satisfies both. If it
  does, the pair is compatible, not exclusive.
- **One document, one owner.** The priorities live here or in AGENTS.md - never both, diverging.

## Boundaries

| Not this | Go instead |
|---|---|
| What the project is, who it serves, what it includes | `idea-md` |
| Choosing the framework/stack/approach | `techstack`, `thebest` - guided *by* these commitments |
| System design decisions | `detailsup` |
| Measuring the bars | `benchmark` |
| Task planning and sequencing | `planner` |
| Creating or auditing AGENTS.md itself | `agents-md` |

## Files

| Need | Load |
|---|---|
| The dimension catalogue, real conflict pairs, compatible pairs, the question bank | `references/01-dimensions-and-conflicts.md` |
| The COMMITMENTS.md skeleton | `assets/templates/COMMITMENTS-template.md` |
| Both placements worked: a three-line AGENTS.md commitment set, and a full COMMITMENTS.md | `examples/small-and-large.md` |
