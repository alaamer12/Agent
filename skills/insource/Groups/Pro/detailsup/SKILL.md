---
name: detailsup
description: 'Guided, conversational, topic-by-topic technical specification: close one design area before opening the next. Use when a project has undecided architecture (scrapers, workers, pipelines, caching, data models, queues, storage, deployment) and the user wants to work through it sequentially - ask targeted questions with real options and trade-offs, collect the decision, write it into a specification document in the project''s docs, update the index, then hand off to the next topic. Stops at design: no implementation until every agreed topic is resolved and the user says go. Extracted from like-a-pro phase 2. Not for choosing a technology stack (techstack), not for deciding how to build something the agent already owns (dtb), not for planning a task list (planner), not for reorganizing or splitting docs (document).'
when_to_use: The user wants to "work through the design topic by topic", nail down missing architecture decisions, resolve open technical questions before building, review what a project has not specified yet, or invokes /detailsup. Also when a spec is half-written and the gaps need closing one at a time.
argument-hint: "[topic to close, or 'what is still unspecified?']"
---

# detailsup

One topic, one decision, one document. Chaos comes from asking about caching, database normalization and retry
policy in the same breath: the user answers in generalities, nothing closes, and the next session re-asks. This
skill makes design state visible by closing topics one at a time and writing each closed decision down where the
project keeps such things.

## The cycle

```text
1 triage     what design pillars are still open? pick ONE topic
2 deep dive  options with pros, cons and trade-offs; targeted questions until the user decides
3 close      write the decision into a spec document; link it in the index
4 hand off   one-line outcome, then propose the next topic
```

### 1. Triage

Read what already exists before asking anything: the project's docs folder, ADRs, `AGENTS.md`, existing specs,
the code that is already written. Open topics are the ones those sources do not settle. List them, let the user
pick, or start with the one that blocks the most other decisions.

Typical pillars, examples not a checklist: ingestion or scraping strategy, workers and scheduling, pipelines and
ordering, caching and invalidation, data model and storage, external integrations and rate limits, error and retry
policy, identity and permissions, deployment and environment layout, migration and rollback. A topic that the
project has already decided is **not** reopened for conversation — record where the answer lives.

### 2. Deep dive

- Present real options, not a menu of one. For each: what it costs, what it protects, what it forecloses.
- Say **why it matters here** (runtime cost, memory, offline resilience, operability, developer experience),
  never in the abstract.
- Mark which option you would choose and why, then let the user decide. They own the requirement; you own the
  reasoning.
- Do not re-ask a settled point unless the user changes direction or new evidence appears.
- One topic at a time: do not leak a database question into a caching discussion. If a second topic surfaces,
  write it down for the agenda and continue the current one.

### 3. Close and document

| Aspect | Rule |
|---|---|
| Where | The project's existing convention (`docs/tech/`, `docs/architecture/`, an ADR folder). No new top-level folder when one exists; ask before inventing one |
| Depth | Concrete interfaces, state-transition tables, data flow, error strategy, boundaries of ownership. A summary that a builder could misread is not a spec |
| Alternatives | Record the options rejected and why, so the next reader does not re-litigate them |
| Open ends | Anything not decided is listed as open, not quietly omitted |
| Index | Link the new document from the folder's map or the docs index in the same change |
| Preserve | Existing docs are merged into, never clobbered; user edits are never reverted |

Do not commit or push unless the user asked for it; closing a document is not a release step.

### 4. Hand off

One short bullet summary of what was decided, one line for what changed in the docs, then propose the next topic
from the agenda and ask whether to take it. The agenda is the user's to reorder.

## Gates

- **Design stays design.** No implementation while topics are open. Build only when the user says to, and then the
  spec is what the code gets judged against.
- **Decisions belong to the user; the analysis belongs to you.** Recommend plainly, decide only inside the
  implementation details that were delegated.
- **Silence is not agreement.** An unanswered question stays open; it never becomes a written "decision".

## Boundaries

| Not this | Go instead |
|---|---|
| Picking the language, framework or store from requirements | `techstack` |
| Deciding *how* to build something already delegated to the agent | `dtb` |
| Breaking the work into ordered tasks or a backlog | `planner`, or the units index (`units-md`) |
| Cataloging units that already exist so work reuses them | `units-md` |
| Inventorying the system's architectural components | `system-md` |
| Reorganizing or splitting documentation that exists | `document` |
| Interviewing for a document type with its own skill | `postmortem`, `document` |

## In the lifecycle

This is phase 2 of `like-a-pro`: idea → **detailsup** → app-boundary confirmation → standards
(`language-handling`, `sql-handling`, `error-handling`, `ui-handling`) and `system-md`. It also runs alone, on any
project, with no lifecycle around it.
