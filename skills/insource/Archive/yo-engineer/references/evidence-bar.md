# Evidence Bar — When to Refuse, When to Ask, When to Draft

## Contents
- The four evidence categories
- Classification: decided-with-evidence / assumed / unasked
- The refusal decision
- What to hand back on refusal
- Conflicting evidence
- What "enough" looks like (worked example)

---

## The four evidence categories

Before drafting any `structure.md`, an answer needs to exist somewhere — in a doc, or stated plainly by the user in conversation — for each of these:

1. **What the project is.** The core problem it solves and for whom. Not a tagline — enough that two different competent engineers would design the same general shape from it.
2. **The aspiration / scope boundary.** What's in v1 versus deferred. A project with no stated boundary produces a tree that tries to be everything, which is really a tree that's honest about nothing.
3. **The expected final output.** What actually ships — a deployable service, a library, a CLI, an app on a store. This alone determines huge structural facts (deployables vs. packages, whether a build/release pipeline is even in scope).
4. **The load-bearing domain decisions.** Whatever this specific project can't be correctly structured without knowing — this varies by project, which is why it can't be a fixed checklist. Examples from real cases: single-language or multi-language fleet, one repo or two, offline-first or server-authoritative, i18n/RTL scope. The way to find these: ask "what would make me redraw the tree if I learned it was different?" Anything that answers yes belongs in this category.

## Classification

For each category, classify what you actually have as one of:

- **Decided-with-evidence** — stated in a doc, or stated plainly and specifically by the user in this conversation.
- **Assumed** — you could infer a plausible answer, but nothing actually pins it down. This is the dangerous middle: it doesn't feel like a gap because an answer is available, it's just not grounded.
- **Unasked** — no answer exists yet, plausible or otherwise, and nobody has raised it.

Do this classification explicitly and show it to yourself before deciding whether to draft. This is the premises ledger from `principles.md`, applied at the intake stage rather than the drafting stage — catching an unasked question here is far cheaper than catching it after a tree's been drawn around its absence.

## The refusal decision

**Refuse to draft `structure.md` if any of categories 1–3 are unasked, or if a category-4 item that would clearly reshape the tree is unasked.**

Assumed items don't automatically block drafting — but every assumed item must be surfaced to the user before drafting starts, stated as an assumption, with a chance to correct it. An assumption that's wrong and never surfaced is exactly the "answering the wrong question eloquently" failure mode from `principles.md`.

This is not a high bar in the sense of being slow — it's often one message. It's a high bar in the sense of being non-negotiable: no structure gets drawn while a load-bearing question is still open, no matter how confidently a plausible answer could be generated to fill it.

## What to hand back on refusal

Never just say "I need more documentation." Hand back something actionable:

1. **Name the specific gap** — which category, and why it's load-bearing for structure specifically (not documentation for its own sake).
2. **Give the question set**, not a vague prompt to "write more docs." If scope is unasked, the actual questions might be: one repo or two? which platforms ship in v1 versus later? what's explicitly out of scope? Model this on a real one-message exchange rather than an open-ended essay assignment — the user should be able to answer in a few lines each.
3. **Say what doc it becomes**, if the project doesn't already have a natural home for it — a short scope doc, a components doc, whatever fits the project's existing doc conventions. Don't prescribe a heavyweight doc format for a two-paragraph answer.

The goal is the same move as the mobile Q&A case in `principles.md`: turn "I can't do this yet" into a short, concrete list of exactly what's missing, so answering it takes one message instead of a guessing game.

## Conflicting evidence

If two docs (or a doc and something the user just said) disagree, do not average them, do not silently prefer the more recent one, and do not pick the one that produces a cleaner tree. Stop and name the conflict specifically: "Doc A says X, but you just said Y — which is current?" One targeted question, not a hedge in the output.

## What "enough" looks like — worked example

A project has: a components doc describing orchestrator/worker roles, a benchmarks doc with measured request shapes for the external APIs it depends on, and a stated deployment target (a platform that builds from a lockfile). That's categories 1, 3, and part of 4 covered with evidence. If nothing says whether workers are single-language or a multi-language fleet, and the benchmarks doc implies at least one dependency is easiest to use in its native language — that's a category-4 item that's *assumed* at best (the population-average assumption is "everything's one language because the rest of the stack is") and needs to be surfaced and confirmed before the worker tree gets drawn, not discovered after.
