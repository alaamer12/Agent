---
name: close-topics
version: 1.0.4
author: Amr
specialized: none
description: 'Guided, conversational, topic-by-topic technical specification: close one design area before opening the next. Use when a project has undecided architecture (scrapers, workers, pipelines, caching, data models, queues, storage, deployment) and the user wants to work through it sequentially - ask targeted questions with real options and trade-offs, collect the decision, write it into a specification document in the project''s docs, update the index, then hand off to the next topic. New topics are disclosed immediately; explicit deferrals use structured Pending (Drafting) markers, and every marker closes before Draft [DR] completes. Stops at design: no implementation until every agreed topic is resolved and the user says go. Standalone independent skill. Not for choosing a technology stack (techstack), not for deciding how to build something the agent already owns (dtb), not for planning a task list (planner), not for reorganizing or splitting docs (document).'
when_to_use: The user wants to "work through the design topic by topic", nail down missing architecture decisions, resolve open technical questions before building, review what a project has not specified yet, or invokes /close-topics. Also when a spec is half-written and the gaps need closing one at a time.
argument-hint: "[topic to close, or 'what is still unspecified?']"
---

# close-topics

One topic, one decision, one document. Chaos comes from asking about caching, database normalization and retry
policy in the same breath: the user answers in generalities, nothing closes, and the next session re-asks. This
skill makes design state visible by closing topics one at a time and writing each closed decision down where the
project keeps such things.

## The cycle

```text
1 triage     what design pillars are still open? pick ONE topic
2 deep dive  options with pros, cons and trade-offs; targeted questions until the user decides
3 close      write the decision down (form set by project state); link it in the index
4 hand off   one-line outcome, then propose the next topic
```

### 1. Triage

Read what already exists before asking anything: the project's docs folder, ADRs, `AGENTS.md`, existing specs,
the code that is already written. Open topics are the ones those sources do not settle. List them, let the user
pick, or start with the one that blocks the most other decisions. Disclose every newly discovered topic in the
same turn, with what it blocks; never hide it in a private agenda for a later handoff.

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
  name it and its impact immediately, then ask whether to close it now or explicitly defer it. Add it to the
  agenda only after the user agrees to defer.

### Drafting Pending Markers

During Draft [DR], a topic may depend on a later step. That permits a marker, not silence:

1. Disclose the question and its blocker immediately.
2. Ask whether to answer now or explicitly defer.
3. On explicit deferral, write only:

```text
Pending (Drafting) — <question>. Blocks: <claims or paths>. Discovered: <step>. Close before: Draft [DR] completion.
```

4. When Viber is active, also record the question in `memory.md` and link its ID from the marker.
5. Before Draft [DR] completes, close every marker through this cycle, update the canonical document and memory ledger, and re-sweep. Any unresolved marker keeps drafting incomplete.

Never write a bare `pending`, `not defined yet`, `TBD`, `TODO`, or placeholder.

### 3. Close and document

**The project's state decides the form.** Three states:

- **Draft [DR]** — still deciding and refining, before implementing. A close is a **provisional,
  revisable steering doc**: the current best, marked revisable, alternatives noted lightly. Do **not**
  cast it into a formal decision record / ADR / `decisions/` folder — that reifies a draft into law
  (see `thaw`). The decisions folder is premature during drafting.
- **In-Progress [IP]** — implementation, testing, launching. Drafting has ended; decisions settle into
  code. A close may now be a **formal decision record (ADR)** with rationale and superseded history.
- **Post-production [PP]** — first release is live. Decisions are settled history; changes are new
  records superseding old ones.

The drafting phase ends when implementation begins; formal `decisions/` records belong to IP/PP, not DR.

| Aspect | Rule |
|---|---|
| Where | **DR:** a provisional steering doc in the project's tech/docs convention. **IP/PP:** the project's decision-record convention (an ADR / `decisions/` folder). No new top-level folder when one exists; ask before inventing one |
| Depth | Concrete interfaces, state-transition tables, data flow, error strategy, boundaries of ownership. A summary that a builder could misread is not a spec |
| Alternatives | **DR:** note alternatives lightly so they can be revisited. **IP/PP:** record rejected options and why, so the next reader does not re-litigate them |
| Open ends | Disclose immediately; write only a structured `Pending (Drafting)` marker after explicit deferral, and close it before Draft [DR] completion |
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
- **Drafting cannot complete with pending topics.** Every `Pending (Drafting)` marker must close before Draft [DR] is declared complete.

## Boundaries

| Not this | Go instead |
|---|---|
| Picking the language, framework or store from requirements | `techstack` |
| Deciding *how* to build something already delegated to the agent | `dtb` |
| Breaking the work into ordered tasks or a backlog | `planner`, or the units index (`units-md`) |
| Cataloging units that already exist so work reuses them | `units-md` |
| Inventorying the system's architectural components | `system-md` |
| Reorganizing or splitting documentation that exists | `document` |
| Interviewing for a document type with its own method | `document` (its postmortem child) |

## Independent Operation

`close-topics` is a fully standalone, independent skill. It runs on any project, at any phase of the design or development lifecycle, with no lifecycle dependencies or prerequisites around it.
