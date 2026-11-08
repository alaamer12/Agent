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

**Ambiguity and decision records (section 13).**

Bad: the section storing the questions that were asked - transcripts, quoted intent, example wording.
AGENTS.md states POLICY here, nothing else: question types and their triggers. Good: "Mode: Broad - the
user answers intent-level questions; internals are the agent's, best-for-project. Exact list: cipher suite,
retention window (the decisions the user claimed)" - plus the always-ask mandate for weight-bearing
decisions, the rule that critical questions get asked before any anonymous run, and the record
convention: one file per decision at `docs/decisions/<slug>.md` anchored Date + Commit + App-Version (a
single combined decisions.md is the explosion anti-pattern), where even the decision NOT to ask gets
recorded. The moment this section quotes a question, it has become a transcript of one session instead
of the standing policy every session follows.

**Version control (section 12).**

Bad: "use git responsibly" - unfalsifiable; and a wall of git commands for a tool the project may not even
use. Good: the VCS named first ([Git], [Unity VCS/Plastic], [Perforce], [SVN] - concepts bind, commands
illustrate), the tiers as concepts ("allowed: inspect history/state + local check-ins per section 3; ask
first: anything outward - push/submit, PRs, shared merges; never without explicit order: published-history
rewrites, destructive restores, workspace purges, hook bypass"), a parked-work verdict (stash/[shelve]
allowed with an `agent/<task>` naming pattern, or forbidden in favor of a WIP check-in / separate
workspace), and the identity line ("check-ins keep the configured human author; no `Co-authored-by`
trailer" - or the exact trailer name, decided once). The `commit` and `branch` skills look for this answer
and stop asking; without it they must ask every session.

**Review sections.**

Bad (what it becomes after three months): twenty named review tasks with per-task checklists inlined into
`AGENTS.md` - fifty lines of procedure the agent carries into every session to run in a few. Good: the
always-first rule stays ("hunt rulebook violations, code and docs, before any named task"); the task bodies
live in `<docs>/review.md`; AGENTS.md keeps one index line per task plus `Read: <docs>/review.md`. Growth is
the failure mode - sections that start as obligations end as documents unless they are watched *as they grow*,
not at next year's audit. Extracting to a referenced doc is one valid answer; inlining is another, chosen by the
user.

## Size guidance, and where the rules live

`AGENTS.md` is loaded every session. A very long rulebook costs context permanently and, worse, **dilutes
compliance**: when everything is mandatory, nothing is. But length alone is not a defect, and the skill does not
enforce a ceiling.

**Placement is the user's choice.** Two valid shapes:

- **Inline in `AGENTS.md`** - guaranteed to be in front of the agent on every message; nothing is forgotten or
  skipped. Costs context and attention, and every line is paid on every turn.
- **Referenced from `AGENTS.md`** - the agent opens the doc only for the task that needs it. Keeps the rulebook
  cheap, but relies on the agent actually reading it; a skipped read means missing rules, and pressure invites
  invention.

By convention the referenced files live under a `rules/` folder beside `AGENTS.md` - `rules/development.md`,
`rules/debugging.md`, or a folder split `rules/debugging/ui.md`, `rules/debugging/backend.md`,
`rules/version/main.md` - or under the project's declared docs root. These are examples, not a required layout;
use what the project already has and ask when neither is evident.

**~500 lines for the whole file and ~50 lines for one section are guidance, not rules.** They are heuristics for
the referenced style. A file that is longer because the user chose to inline is not a violation; length alone is
never a finding.

Practical consequences:

- One line per rule, with the reason in a clause ("because X hangs"), not a paragraph.
- Tables beat prose for routing (file → purpose, task → skill, location → scope).
- When a section becomes unwieldy and the user agrees to reference it, **extract**: move the detail into a doc
  at the project's docs root (conventionally `rules/...`), leave the obligations plus one pointer line.
  Trimming loses information; extracting keeps it one `Read` away.
- Cut in this order when shrinking for clarity: (1) duplicated content from referenced docs, (2) explanatory
  prose, (3) examples that the referenced file already carries, (4) rarely-triggered conditional rules → move
  behind a conditional pointer, (5) never the scope fence or the delegation contract.

The inline/referenced split, bad and good:

Bad - section 3 grows to 70 lines: the env-validation library's rationale, a table of every variable, three
examples of the generation script's output, and the fallback behavior, all inline. Every session pays for the
generation-script trivia even when the task is a one-line CSS fix.

Good - section 3 is 8 lines:

```markdown
## 7. Environment and Secrets
- Strategy: build-time generation from `.env.example` - never edit `.env` by hand.
- Validation: typed schema at startup; a missing var fails boot, no silent defaults.
- Read: `rules/environment.md` (variable table, generator, fallbacks).
```

The agent obeys the three obligation lines every session and opens the doc only when the task touches
environment code. The rulebook stays cheap; the detail stays findable.

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

Count the pending markers before declaring the file finished - it can never look done while one is still open.

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
