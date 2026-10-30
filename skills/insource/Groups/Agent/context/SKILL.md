---
name: context
description: 'Project-context reconstruction — build a reliable mental model of a project from all available artifacts (docs, source, config, git history with a 5-commit default, Flush notes, images, prototypes, design artifacts) before any work. Two modes: light (default) inspects and reads only, never running tests, builds, installs, or scripts; utter allows active verification when inspection alone cannot answer. Neither mode modifies the project for context. Treats docs as unverified, cross-checking claims against code; conflicts resolve by priority (current state > source/config > docs > recent git > flush notes > history), and fact, intention, decision, assumption, unknown stay distinct — assumptions never silently become facts. Completes when the agent could work without blindly rediscovering fundamentals. Reads companion Flush files (incl. the SESSIONS.md journal), works without them. Use at session start, before nontrivial tasks, after compaction. Triggers: load context, understand the project, get oriented.'
---

# context — reconstruct the project model before touching it

The goal is not to perform the task. The goal is a **reliable mental model**
so the agent can work on the project correctly. Observation, not
implementation: context never modifies the project simply to understand it.

## Modes

| | **light** (default) | **utter** |
|---|---|---|
| Read files, docs, configs, git, visuals | ✅ | ✅ |
| Execute tests/builds/scripts, install deps, start tooling, inspect runtime | ❌ never | ✅ when it answers something inspection cannot |
| Modify the project | ❌ | ❌ (only if the surrounding workflow explicitly requires it) |

- No mode given → `light`. Use `utter` only when the user or the invoking
  workflow explicitly asks for active verification, runtime behavior is
  needed to understand the project, or static inspection is insufficient.
  **When in doubt, stay in `light`.**
- Execution in `utter` serves context reconstruction — running a test is
  evidence gathering, not implementation, and the result is *additional
  evidence* layered on understanding the test code itself.

## Sources and reading order

Guideline for efficiency, not a rule to ignore earlier-needed information:

```text
1. Documentation → 2. Flush notes → 3. Source code & project files
→ 4. Git history → 5. Visual artifacts → 6. Active verification (utter)
```

Source code is **not** the only source of truth. What exists depends on the
project.

### 1. Documentation

`README`, architecture/technical docs, requirements, specs, design docs,
API docs, dev guides, project notes, config documentation, any Markdown or
text. Extract: what the project is, its purpose, main requirements,
architecture, major concepts, expected behavior, conventions, known
constraints. **Docs are assumed neither complete nor current** — validate
important claims against source and other evidence.

### 2. Flush notes (if present)

Look for `CONTEXT.md`, `PLAN.md`, `SNAPSHOT.md`,
`STATUS.md` (the `flush` skill's persisted state) and `SESSIONS.md` — an
append-only journal with one row per past session: read it FIRST to learn
which sessions happened, what each was for and how it ended, so the four
notes are understood as the latest snapshot of a multi-session history
rather than one agent's story. They hold what code
alone cannot explain: previous decisions, current understanding, why an
approach was chosen, active plans, past problems, known unfinished work,
important constraints. They are **contextual evidence, not unquestionable
truth** — when a note contradicts the verified current state, prefer the
current state and *account for the discrepancy* (the note may explain how
the drift happened). If no flush files exist, reconstruct from everything
else; this skill works independently of flush and merely benefits from it.

### 3. Source code, tests, configuration

Build understanding of: structure · main modules · components · services ·
data flow · APIs · state management · configuration · dependencies · key
abstractions · entry points · tests · scripts · generated files ·
integration points. **Prioritize architecturally significant files; never
blind-read everything.**

- **Tests** (read in both modes; execute only in `utter` when useful): they
  encode expected behavior, edge cases, existing guarantees, intended APIs,
  known workflows.
- **Configuration & dependencies**: package manifests, lockfiles, build/env/
  compiler/tool/CI/deployment config — how the project is assembled and what
  it depends on externally. `light` inspects; never installs or changes.

### 4. Git history (after the current structure is understood)

Default window: **the most recent 5 commits**, unless another depth is
requested. Inspect messages, files changed, additions/deletions/modifications,
important refactors, feature additions, reverted work, between-commit diffs,
evolution of key parts. Answer not only *what changed?* but *why might the
project have changed this way?* — reading messages, diffs, and surrounding
context **together**; a commit message alone is never sufficient evidence,
open the diff when it matters. Useful comparisons: what was added/removed/
renamed, what behavior likely changed, what work looks incomplete, what
existed and disappeared, what assumptions shifted. **No git (or no usable
history)? Skip git analysis — never invent historical context.**

### 5. Visual & prototype context

Images, screenshots, UI designs, prototypes, wireframes, design exports,
diagrams, visual references — **not ignored merely for not being source
code.** If the agent can understand visuals, inspect the relevant ones for
intended UI, layout, user flows, interaction patterns, visual hierarchy,
component relationships, design requirements, and gaps between
implementation and intended design. Triangulate when useful: *prototype →
expected flow; design → expected structure; code → current implementation.*
The aim is holding both what exists and what the project intends to become.

### 6. Active verification (`utter` only)

Run what answers an open context question: tests, builds, scripts,
generated output, runtime behavior, dependency install checks, dev tooling
startup, other safe commands with meaningful informational payoff. Stop
when execution stops adding understanding — it is a means, not a ritual.

## Context reconstruction (the output is a model, not a file list)

Never deliver "files I read." The reconstructed model should answer:

- **Project** — what is it, what problem does it solve, who/what uses it?
- **Architecture** — how is it structured, major components, interactions?
- **Behavior** — what does it currently do, what is expected of it?
- **State** — what exists, what is incomplete, what is missing?
- **History** — what important changes happened recently, why this way?
- **Intent** — what is it trying to achieve; requirements invisible in code?
- **Visuals** — what should the UI/experience look like?
- **Continuity** — what did the previous agent already know, which
  decisions are settled, what must not be pointlessly rediscovered?

## Evidence and confidence

Prefer **current** source code, project files, documentation, git state,
and visual artifacts over unsupported assumptions. When sources disagree:
1) identify the conflict; 2) prefer current, directly verifiable evidence
for *current state*; 3) preserve historical information that explains *how*
the conflict occurred; 4) mark unresolved uncertainty explicitly.
**Assumptions never silently become facts.** General priority (not absolute
— a flush note may hold the one decision code cannot reveal):

```text
current project state > current source/config > current docs
> recent git history > flush notes > older history
```

Keep these categories distinct in anything written or relied upon:
**current fact · historical fact · intended behavior · agent decision ·
assumption · unknown.**

## Completion criteria

Context reconstruction is complete when the agent could work the project
without blindly rediscovering its fundamentals. At minimum understand:
project purpose · main architecture · important files · current
implementation state · relevant docs · relevant flush notes (if any) ·
relevant recent git history (if any) · visual/design context (if any) ·
important unfinished or uncertain areas · important constraints and
decisions.

> The objective is not to read everything. The objective is to understand
> enough of everything important.
