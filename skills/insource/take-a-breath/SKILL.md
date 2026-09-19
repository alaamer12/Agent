---
name: take-a-breath
description: Force a deliberate pause before implementing. Stop the urge to code from scratch, calm the overwhelmed engineering impulse, and apply sober judgment about whether a mature, production-proven solution already exists. Use when the agent is about to write custom code for a common problem, when the user says take a breath, pause and evaluate, don't reinvent, prefer existing solutions, or when the task feels like it might already have a solid library, framework, platform feature, or established pattern. Triggers include take-a-breath, take a breath, pause and think, don't reinvent the wheel, prefer proven solutions, evaluate existing options.
---

# Take a Breath

You are the stressed engineer who is about to write a lot of code because the problem feels urgent and solvable.  
Stop. Breathe. Look around.

This skill forces a short, deliberate pause so that engineering judgment — not the desire to demonstrate “muscle power” — decides the implementation path.

## Core Stance

You are **not required** to implement everything from scratch.

If a mature, production-proven solution already exists for the same problem (library, framework, built-in platform feature, established pattern, infrastructure tool, or other proven approach), you should seriously consider using it.

Do **not** choose a custom implementation merely because:
- it is possible to build it yourself, or
- building it from scratch feels more impressive.

Do **not** reject an established solution merely because it adds a dependency, some bundle size, an abstraction, or a bit of complexity — without first weighing the actual trade-offs against the project’s real requirements.

At the same time, do **not** blindly pull in a library just because one exists. If the existing solution is unnecessary, overly heavy, poorly maintained, mismatched to the requirements, or introduces a meaningful downside, a focused custom implementation can still be the better engineering decision.

**In short:** Prefer proven solutions when they provide a meaningful advantage. Implement it yourself when that is genuinely the better engineering decision — not simply to prove that you can.

Judge fairly. Do not be biased toward any particular idea, technology, or personal preference. Weigh the options on their actual merits for *this* project.

## Mandatory Pause Workflow

Whenever this skill is active (or the situation matches its triggers), execute the following steps **before writing implementation code**:

### 1. Name the Problem Clearly
State in one or two sentences the exact capability you are about to build.

### 2. Ask the Calm Questions
Answer these honestly (write the answers, do not skip):

- Does a mature, production-proven solution already exist for this exact problem (or a very close variant)?
- What are the real trade-offs of using that solution in *this* project (dependency cost, size, maintenance, license, learning curve, fit with existing stack, security posture, scalability)?
- What are the real costs of building it ourselves (time, complexity, ongoing maintenance, risk of subtle bugs, reinvention of solved edge cases)?
- Given the actual requirements and constraints of the current project, which path is the better engineering decision right now?

### 3. Decide Explicitly (Fair Judgment)
Choose one of three outcomes and state it clearly:

- **Use existing solution** — name it and explain why it is the better path.
- **Build custom** — explain why a custom implementation is genuinely superior here.
- **Hybrid** — reuse the proven core and only custom-build the thin adaptation layer that is truly project-specific.

Judge the options fairly. Do not favor a custom solution out of habit or pride, and do not favor an existing library out of convenience or trend. Base the decision only on the real requirements and trade-offs of the current project.

### 4. Ask When Unsure
If you are not confident about a meaningful decision — especially one that affects the project (installing an additional tool or dependency, changing architecture, adopting a new pattern, etc.) — **ask the user** before proceeding.  
Present the options and trade-offs briefly and let the user decide.

### 5. Only Then Proceed
After the decision is written and justified (and any necessary user confirmation is obtained), continue with implementation (or recommend the chosen path to the user).

## Hard Rules

- Never skip the pause when the problem is a common one that likely has existing solutions.
- Never justify a custom implementation with “because I can” or “to avoid a dependency.”
- Never justify adopting a library with “because it exists.”
- Judge fairly — do not be biased toward any idea, technology, or personal preference.
- Always ground the decision in the concrete requirements, constraints, and trade-offs of the current project.
- If unsure about a consequential choice (new dependency, new tool, architectural direction, etc.), ask the user instead of deciding alone.
- Stay language-agnostic and technology-neutral unless the project has already committed to a stack (polyglot principle).
- If the user explicitly wants a from-scratch implementation for learning or pedagogical reasons, respect that and note the exception.

## When This Skill Should Activate

- The agent is about to write a non-trivial piece of functionality that is a well-known problem domain (auth, validation, rate limiting, caching, retry, queue, serialization, form handling, date/time, HTTP client, etc.).
- The user says anything like “take a breath”, “pause”, “don’t reinvent”, “is there already a library for this?”, “prefer proven solutions”.
- The conversation shows signs of the “I can just build it myself” impulse under pressure.

## Supporting Material

- `references/decision-checklist.md` — short reusable checklist
- `references/example-judgments.md` — concrete before/after examples of good and bad decisions
---
