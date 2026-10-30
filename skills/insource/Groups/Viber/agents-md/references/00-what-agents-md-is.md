# What `AGENTS.md` is, and what it is not

## The one distinction that decides every drafting argument

| Belongs here | Belongs elsewhere |
|---|---|
| An obligation: "read X before implementing" | What X says |
| A restriction: "do not edit `.env` directly" | How the config system works |
| A route: "active version is V1; `v2/` is out of scope" | The version history |
| A failure-avoidance rule: "PowerShell hangs; use CMD" | A shell tutorial |
| A pointer: "units index at `docs/UNITS.md`" | The units list itself |

`AGENTS.md` governs behavior. Everything else is a reference *to* something. When content could be read as
documentation, it is documentation, and the file should hold the sentence that makes the agent open it.

## Worked pairs

**Context loading.**

Bad - the file becomes a summary of the summary:
```md
The pipeline uses a worker pool with a rate limiter that caps concurrent diff operations at 4 and uses a
token bucket refreshed every 250ms.
```

Good - the obligation, plus where truth lives:
```md
Before touching the pipeline, read .repertoire/.steering/v1/tech/worker-pool-and-rate-limiter.md in full.
Concurrency limits and token behavior are defined there; do not restate them in code comments or here.
```

The first version is wrong twice: it duplicates a document that will change, and it *displaces* reading it.

**Units.**

Bad: listing 40 components in `AGENTS.md`. Good: the duty, plus the pointer, plus who updates it, and the
same-task requirement that prevents a rotting index.

**Workflow.**

Bad: `git checkout -b feature/x` tutorials. Good: "work lands on `canary` first; never commit directly to
`main`; `main` advances only by owner-approved promotion." Constraints, not commands.

## Why ~500 lines, and what the limit is really protecting

The file is loaded every session. A 1,200-line rulebook costs context permanently and, worse, **dilutes
compliance**: when everything is mandatory, nothing is. The limit is not vanity; it is attention budget.

Practical consequences:

- Prefer one line per rule, with the reason in a clause ("because X hangs"), not a paragraph.
- Tables beat prose for routing (file → purpose, task → skill, location → scope).
- If a section needs 100 lines, it is a document with a pointer missing.
- Cut in this order when over budget: (1) duplicated content from referenced docs, (2) explanatory prose,
  (3) examples that the referenced file already carries, (4) rarely-triggered conditional rules → move behind
  a conditional pointer, (5) never the scope fence or the delegation contract.

## Stability and drift

Rules here are the ones that stay true across versions, channels, and phases. Anything that changes with them
either belongs in the version/channel-scoped file it changes with, or in a table row keyed by the active
context. The drift test: **when we ship V2, does this line become wrong?** If yes, it does not belong in
section 1; it belongs in section 2's table.

## The "pending" discipline

An unanswered decision is written as `pending - not assumed`, numbered, and reported at the end. Never fill
the gap with a plausible default. Two reasons:

1. The agent cannot distinguish a decided rule from an invented one and will enforce the invented one with the
   same confidence.
2. A visible pending item invites the answer. An invented default quietly blocks it forever.

`scripts/agents_lint.py --strict` counts pending markers so a file can never look finished while it is not.

## What "good" looks like when reading it back

A competent new agent should be able to answer, from the file alone, in under a minute:

- Which documents must I open first, and which directory must I ignore?
- Where does my work land, and what must not be committed directly?
- What is the one package manager, and which shell do I avoid?
- How do I change an environment value without breaking the rules?
- What am I allowed to inspect or modify while debugging?
- If I delegate, what must be in the subagent's prompt, and what does it owe me back?

Anything it cannot answer is a hole in the file. Anything it can answer but only after reading three paragraphs
of explanation is a hole in the *shape* of the file.
