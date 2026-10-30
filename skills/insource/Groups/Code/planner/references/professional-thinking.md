# Professional Thinking Between the Lines

This reference teaches the planner how to generate high-quality hypotheses by reading between the lines of a user request. The goal is to surface what a senior engineer would expect even when the user never said it explicitly.

## What a Hypothesis Means

A hypothesis is **not** “I did not understand your query.”

A hypothesis is:  
**“I think your query could mean that <precise professional interpretation>.”**

It is a proposed, enriched reading that makes implicit expectations, constraints, and engineering judgment explicit so the user can confirm, correct, or reject it.

## Pre-Hypothesis Clarification Gate

Before any hypothesis is written:

- If the request (or key terms) is vague, ambiguous, or uses slang / informal language that could be misinterpreted → **stop and ask clarifying questions**.
- Do not invent meanings while the language itself is unclear.
- Only after the wording is clear enough to interpret professionally, proceed to generate hypotheses.

## Core Stance

A professional does not take the request at face value.  
They treat every prompt as incomplete and ask:

1. What is the user *really* trying to achieve?
2. What will break or become expensive if we ignore X?
3. What would a careful peer reviewer later complain about?
4. What constraints are present in the environment even if not mentioned?
5. What future change is likely and should be anticipated now?

These questions become the raw material for hypotheses.

## Hypothesis Categories to Always Consider

Generate at least one hypothesis (when relevant) in each of these professional lenses:

| Lens | What to surface | Typical signal in the request |
|------|-----------------|-------------------------------|
| **Explicit** | Directly stated goals | "I need X", "add feature Y" |
| **Implicit success criteria** | How the user will judge that it "works" | Vague words like "good", "fast", "nice", "secure" |
| **Hidden constraints** | Time, budget, team skill, existing tech debt, compliance | Project already has a stack, deadlines, legacy code |
| **Non-functional** | Performance, reliability, observability, security, operability | Any production-facing work |
| **Evolutionary** | What will need to change next | "MVP", "for now", "later we might" |
| **Failure & edge** | What happens when things go wrong | Uploads, money, auth, concurrency, external services |
| **Ownership & boundaries** | Who owns the data/lifecycle, what is in/out of scope | Multi-module or multi-service systems |
| **Human factors** | Developer experience, onboarding, debugging pain | Any code that other people will maintain |

## How to Phrase an Interpolation (Professional Style)

Bad (too literal):
> User said they want concurrent uploads, so we will allow concurrent uploads.

Good (between the lines):
> User asked for concurrent uploads. In practice this also requires independent progress tracking, cancellation isolation, bounded resource usage, and compatibility with the existing rate-limiter and auth middleware already present in the project. Without these, the feature will either be unsafe under load or will force a later rewrite.

## Hypothesizing Technique (Step-by-step)

1. **Quote the trigger**  
   Pull the exact words that sparked the thought.

2. **Name the professional concern**  
   "This is really about resource isolation / backward compatibility / graceful degradation / …"

3. **State the enriched requirement**  
   Turn the concern into a concrete, testable expectation.

4. **Anchor it**  
   Point to local evidence (files, config, patterns) or external best practice.

5. **Surface the assumption**  
   Explicitly list what you are assuming so the user can correct it.

6. **Leave an open question**  
   Never pretend certainty when the request is ambiguous.

## Universal / Language-Agnostic Rule

All hypotheses and the resulting plan must stay at the level of **principles and architecture**, not language syntax or framework fashion.

- Prefer "bounded concurrency with independent cancellation" over "use Promise.allSettled + AbortController".
- Prefer "stable public contract with additive evolution" over "keep the TypeScript interface identical".
- When a concrete technology is required, present it as one option among viable alternatives and let the user decide (polyglot principle).

## Anti-Patterns to Avoid

- Inventing features the user never implied and that have no engineering justification.
- Jumping to a specific library or language construct before the requirement is clear.
- Hiding uncertainty — always list assumptions and open questions.
- Producing a plan before the user has approved the hypotheses.
---
