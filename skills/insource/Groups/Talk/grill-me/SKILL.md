---
name: grill-me
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round, then wait for the user's answers before the next round.

## How to ask

**Prefer the ask tool over plain text.** If an interactive ask tool is available (e.g. `AskUserQuestion`, `ask_user_input`), use it for every question that has a discrete set of reasonable options or preferences. Only fall back to a numbered prose question in the terminal when:

- the question is genuinely open-ended (a name, a number, a free-form description), or
- no ask tool is available.

If the frontier is larger than the tool allows per call, split it into consecutive calls within the same round, and wait for all answers before recomputing the frontier.

**Mark exactly one option as recommended.** Put your pick first in the option list and label it "(Recommended)". Word each question so that choosing the recommended option means "yes, go with your suggestion".

**Every question must carry the following**, so the user can decide knowing their limits:

1. **Title**: a short label for the decision (a few words).
2. **Description**: what is being decided, why it matters, and what it unblocks downstream. Add the context the user needs to answer without re-deriving it.
3. **Options, each with pros & cons**: for every option, state concretely what it gives the user and what it costs them (effort, risk, reversibility, money, time, complexity, lock-in). Be honest about the recommended option's downsides too.
4. **Why you recommend one**: one or two sentences tying the recommendation to what you already know about the user's goals and constraints.

Put the pros & cons in each option's description field when the tool supports it. If the tool has no room for them, put them in the question body above the options.

### Fallback format (prose questions)

When you must ask in plain text, format a round like so:

```
❓ **Q1** - **<question title>**: <description: what's being decided, why it matters, what it unblocks>

**Options**
- **A. <option>** (recommended)
  - Pros: <...>
  - Cons: <...>
- **B. <option>**
  - Pros: <...>
  - Cons: <...>

➡️ <your recommended answer and why>

---

❓ **Q2** - ...
```

## Rounds and the design tree

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

## Done

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.