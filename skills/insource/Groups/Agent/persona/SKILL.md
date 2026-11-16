---
name: persona
version: 1.1.0
author: Amr
specialized: none
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

Pick only the dimensions this role and task actually need; the full 16-item
menu, why mechanical filling is a failure, and the selection rule:
`references/dimensions-and-mental-models.md`.

### 3. Build the domain's mental models

Derive the 4–8 reflexive checks for dimensions 4, 8, 9 and 16 and
sanity-check them for practitioner grounding:
`references/dimensions-and-mental-models.md` (second half of the file).

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

A professional reasoning style, never fabricated personal history — the
forbidden anecdote, the too-thin bare label, the worked middle ground, and
the reusable pattern: `references/reality-constraint.md`.

### 6. Write the output in the standard structure

The default section structure, with the adapt-or-omit rules (never pad):
`references/output-structure.md`.

### 7. Communication behavior

Natural professional speech instead of credential-announcing preambles,
with avoid/prefer examples and the colleague tone:
`references/output-structure.md`.

### 8. Integrating with a criticism/review protocol

The persona states how this professional thinks and only briefly notes its
own angle on criticism — it never copies the orchestration system's full
protocol: `references/output-structure.md`.

### 9. Final quality check before returning the persona

Run the nine questions, and check the result against the anti-pattern
list they guard against: `references/quality-check.md`.

## Reference index

| File | Load when |
|---|---|
| `dimensions-and-mental-models.md` | steps 2–3: choosing dimensions, deriving reflexive checks |
| `reality-constraint.md` | step 5: writing the experience section without invented history |
| `output-structure.md` | steps 6–8: rendering the persona, its voice, its criticism scope |
| `quality-check.md` | step 9 plus the anti-pattern catalog |
| `example_personas.md` | calibrating specificity and tone against finished personas (never copy) |
| `persona_construction_patterns.md` | deriving a domain's checks when the role has no example |
