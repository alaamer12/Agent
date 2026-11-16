# Router — Workflow Awareness & Guidance
> How the Router tracks progress and guides — the awareness layer over `lifecycle.md`, reading the registry (`../commands/init.md`), the memory files (`memory.md`) and the supervision state (`supervision.md`).


## 1. Overview

The **Router** is a workflow-awareness layer that stays active throughout the project development process.

Its purpose is to help the user and AI agent understand where the project currently stands within the defined Project Lifecycle, what has already been accomplished, what remains to be done, and which skills may be useful at the current moment.

The Router does not implement features, make project decisions, or enforce a rigid development sequence. Instead, it observes the ongoing work and provides contextual guidance.

It should feel like a knowledgeable project guide working alongside the user while they are vibe coding.

### Core Principle

**Guide the workflow without controlling it.**

The Router should make the right information and skills visible at the right time, while leaving execution decisions to the user and agent.

---

## 2. Responsibilities

The Router has five primary responsibilities.

### 2.1. Track Workflow Progress

Keep track of the project's progress throughout the lifecycle.

It should identify:

- Which lifecycle steps have been started.
- Which lifecycle steps have been completed.
- Which skills have been used.
- Which skills are currently running or in progress.
- Which skills have not been used yet.
- Which optional skills have been skipped.
- Which completed skills need to be revisited.

The Router must distinguish between actual execution and assumptions.

For example, finding a `prototype` folder does not automatically mean the `prototype` skill was executed successfully.

Progress should be based on reliable evidence, such as skill execution, explicit user confirmation, or verified outputs.

### 2.2. Identify What Comes Next

Based on the current project state, identify the logical next actions.

Examples:

- "`idea-md` is completed. Consider running `reveal` before moving forward."
- "`steering-tech` is completed. The next expected skill is `architecture`."
- "The Vision stage appears complete. You can move to Project Foundation."
- "Several mandatory foundation skills are still incomplete."

The Router should consider:

- The lifecycle step currently being worked on.
- The skills already completed.
- Skill dependencies and expected order.
- Required outputs.
- Outstanding decisions or blockers, read from the project's `.viber/memory.md`; surface a deferred question when its blocker clears.
- Whether the user is intentionally working out of order.

It should recommend the next logical action, not blindly select the next item in a list.

### 2.3. Suggest Relevant Skills

The Router should recognize situations where another skill could help the current work.

These suggestions should be based on the actual context, not simply on whether a skill has not been used.

Examples:

| Situation | Suggested skill |
|---|---|
| Several unrelated topics are being discussed together | `close-topics` |
| Requirements or decisions are still unclear | `grill-me` |
| An initial project idea has not been checked for similar projects | `reveal` |
| Technical direction has not been established | `steering-tech` |
| Architecture is being designed before technical direction is clear | `steering-tech` |
| The user is discussing implementation without a clear plan | Relevant skill from `FULL CODE` |
| Repeated implementation problems need investigation | `debugging` or `fix` |
| Project documentation contains mistakes | `mistakes` |
| The same need keeps returning and no planned Skill covers it | `adapt` |
| A draft doc, doctrine, or prior answer is being treated as fixed law while drafting | `thaw` |
| An active Viber area grows fat with finished history (memory rows, superseded docs) | `vcompact` |
| The same multi-step sequence keeps being hand-assembled for a class of work | `vflow` |
| The project has public pages that must be found by search engines | `seo` (from the user's deck, when registered) |
| The interface needs stronger design quality | A design Skill — from the user's deck when one is registered, such as `impeccable`, otherwise from the Opensource Deck |
| A web interface needs end-to-end checks | `webapp-testing` (Opensource Deck, unless already registered) |
| A video tutorial or recorded demo must be understood | `watch-video` (from the user's deck, when registered) |

The Router should also be aware of optional skills and suggest them when their purpose is relevant.

The Router should also be aware of the two **Skill Decks**. Registration decides the deck, not authorship:

- **`<USERNAME>`'s Deck** — every Skill registered with the user's agent, global or project-level, plus any Skill repositories the user chose to add. For the author of Viber this is "Amr's Deck".
- **Opensource Deck** — every published Skill that is not registered.

Deck Skills are not part of the lifecycle; the Router suggests one only when the current project or task actually needs it. For example, it suggests `seo` for a public marketing website, never for an internal admin console.

Any Skill from either deck can be suggested — the decks are not limited to the examples above:

- **The user's deck:** look it up in the Viber registry written by `/viber init`, which indexes every registered Skill and every extension source.
- **Opensource Deck:** use `find-skills` or a web search to discover published Skills that fit the need. A Skill found this way is a suggestion to evaluate, not something to install automatically; once the user registers it, it belongs to the user's deck.

The Router may suggest **more than one Skill at a time** when the situation calls for it — for example a lifecycle Skill together with a deck Skill that strengthens it, or Skills from both decks. Each suggestion should state why it is relevant.

It must not recommend a skill merely because it exists in the lifecycle or in a deck.

### 2.4. Detect Missing Outputs and Workflow Issues

The Router should compare expected lifecycle outputs against the actual project state.

It should identify situations such as:

- A mandatory skill has not been completed.
- A skill was executed but its expected output is missing.
- An output exists but appears incomplete or outdated.
- A later skill depends on an unfinished earlier task.
- The project has moved to a later lifecycle stage without completing important foundation work.
- Previously completed work has been changed and may need review.

The Router should communicate these issues clearly.

Example:

> You're starting implementation, but the architecture and engineering foundation have not been completed. Consider reviewing the remaining Project Foundation requirements first.

This is a warning, not a restriction. The user can still proceed.

### 2.5. Keep the Workflow Flexible

The Router must support real-world development rather than force every project into a fixed sequence.

It should allow:

- Running skills out of their expected order.
- Running the same skill multiple times.
- Returning to an earlier lifecycle step.
- Revisiting completed work.
- Skipping optional skills.
- Invoking intermediary skills at any point.
- Working on multiple topics in parallel.
- Changing previously established decisions.

The Router should update its understanding of the project whenever the workflow changes.

---

## 3. Relationship with the Project Lifecycle

The Project Lifecycle document defines the workflow.

The Router reads and follows that definition rather than maintaining an independent copy of the lifecycle.

It must understand:

1. The four lifecycle steps.
2. The skills belonging to each step.
3. Which skills are Mandatory and which are Optional.
4. The expected order and dependencies between skills.
5. The expected outputs of each skill.
6. Skills that can be invoked across multiple steps.
7. Skill groups, such as `FULL CODE`.
8. The two Skill Decks, which sit outside the lifecycle.
9. The project's own Viber version, recorded in the Viber section of the project's `AGENTS.md`.

### Source of Truth

The Router should treat project lifecycle information as follows:

- **Project Lifecycle document:** Authoritative definition of steps, skills, classifications, dependencies, and expected outputs.
- **Mermaid graph (`diagrams/lifecycle-flow.mmd`):** Visual overview of the lifecycle and relationships.
- **Viber section of the project's `AGENTS.md`:** What this project adds to the fixed lifecycle — attached deck Skills and project Skills, with their lifecycle point and status. Written by `adapt`.
- **Viber registry (`<project-root>/.viber/registry.md`):** The index of every registered Skill — Viber Skills and the user's deck, including any extension repositories — written by `/viber init`. The Router reads it to find candidate Skills for a need, and each Skill's `Viber` participation (`part` / `separated` / `excluded`).
- **Viber memory (`<project-root>/.viber/memory.md`, `settled.md`, `learnt.md`):** The project's open questions, settled answers, and learned facts (see `memory.md`). The Router reads `memory.md` for outstanding decisions and blockers, `settled.md` to avoid re-suggesting settled decisions, and `learnt.md` for constraints that shape guidance.
- **Viber supervision (`supervision.md`):** Whether the project's `AGENTS.md` declares Viber (activation), and which Skills participate (the registry's `Viber` column). When active, the Router applies the rerouting rule to participating Skills' relocatable output (`.viber/<normal-path>`); code and root-files stay.
- **Skill Decks:** The Skills available outside the lifecycle, discovered as the Project Lifecycle document describes.
- **Actual project files and execution evidence:** Evidence of what has happened.
- **Router state:** Current progress tracking and recommendations.

The Router must not invent new lifecycle rules or change skill classifications based on its own assumptions.

For a given project, the Router reads the fixed lifecycle **plus** that project's Viber version. A Skill the project attached through `adapt` is tracked like any other Skill, at the lifecycle point and with the status recorded for it.

If the lifecycle definition changes, the Router should adapt to the updated definition.

---

## 4. Skill Status Management

The Router must distinguish between different skill execution states.

### 4.1. Status Definitions

| Status | Meaning |
|---|---|
| Not Started | No confirmed execution has occurred. |
| Suggested | The Router has recommended using the skill. |
| In Progress | The skill has started but has not finished. |
| Completed | The skill has successfully completed its intended task. |
| Skipped | The user explicitly decided not to use the skill. |
| Needs Review | Previously completed work may need to be revisited. |
| Blocked | The skill cannot reasonably proceed because a dependency or required input is missing. |

These statuses should not be confused.

For example:

- A suggestion is not an execution.
- Starting a skill does not mean it is completed.
- Skipping an optional skill does not mean the lifecycle is incomplete.
- Completing a skill does not guarantee that its output remains valid forever.

### 4.2. Mandatory vs Optional

The Router must respect the skill classifications defined in the lifecycle.

**Mandatory skills:**
- Should be tracked as expected workflow work.
- Their missing completion should be visible.
- Their outputs should be checked when applicable.
- Their incompletion may trigger a workflow warning.

**Optional skills:**
- Should be suggested when useful.
- Can be skipped without blocking lifecycle progression.
- Should not generate warnings simply because they were not used.

**Deck skills:**
- Are not part of the lifecycle and are never expected.
- Should be suggested only when the project or task needs them.
- Should never generate warnings for not being used.
- Become tracked workflow work only after `adapt` attaches them to the project's Viber version.

The Router must never silently reclassify a skill.

### 4.3. Repeated Execution

A skill may be executed more than once.

For example, `prototype` may be used to create an initial draft and later refine it after the pages and features have been clarified.

The Router should preserve the latest status while retaining enough history to understand previous executions.

A repeated execution should not automatically erase the fact that the skill was previously completed.

---

## 5. Intermediary Skills

Some skills are not tied to a specific lifecycle step.

They can be invoked whenever their purpose becomes relevant.

The Router must recognize these skills and suggest them across the entire workflow.

### 5.1. `grill-me`

Purpose: Clarify unclear requirements, decisions, assumptions, and project details through questions.

Suggest it when:

- The user has not provided enough information to make a decision.
- Requirements contain ambiguity.
- Several assumptions are being made without confirmation.
- Important details are missing.
- The agent is uncertain about the user's intended outcome.

Example:

> Some requirements are still unclear. Consider using `grill-me` to clarify them before proceeding.

### 5.2. `close-topics`

Purpose: Organize discussions into separate topics and track which topics are resolved and which remain open.

Suggest it when:

- Several unrelated subjects are being discussed together.
- Discussions are becoming difficult to follow.
- Some decisions are being postponed.
- Important topics are being repeatedly revisited.
- The project has accumulated many unresolved discussions.

Example:

> We have several open topics that are getting mixed together. Consider using `close-topics` to organize and resolve them independently.

### 5.3. `adapt`

Purpose: Adapt the project's own Viber version when the journey needs a capability that nothing planned covers.

Suggest it when:

- The same instruction or correction keeps being repeated.
- A need keeps returning that no lifecycle Skill covers.
- A deck Skill is needed again and again, and should become part of this project's path.
- A domain of the project has no Skill that owns it.

Example:

> This is the third time the same bilingual content rules have been explained. Consider using `adapt` to settle where they belong.

The Router detects the gap; `adapt` decides what closes it and records it in the project's `AGENTS.md`.

### 5.4. `mistakes`

Purpose: Help identify and correct mistakes in the relevant project work.

The Router can suggest it in different lifecycle contexts:

- During Project Foundation when documentation or engineering decisions contain mistakes.
- During Implementation when code or implementation decisions contain mistakes.

The Router should understand the context before recommending it.

### 5.5. `thaw`

Purpose: Keep drafting provisional. Melt decisions, docs, doctrines, and the user's earlier answers that have
frozen into assumed law, separate the stable invariant from the draft mechanism, and re-validate toward
better.

Suggest it when:

- A draft doc or doctrine is cited as a hard constraint that eliminates options.
- An agent is defending an earlier recommendation past its evidence.
- The user's prior answer is treated as non-questionable after the frame changed.
- Improvement has stopped at "good enough" while a materially better design is reachable.

Example:

> That constraint comes from a draft doc, not a fixed requirement. Consider using `thaw` to re-open the options and re-validate.

`thaw` is the drafting posture; `close-topics` keeps walking each reopened topic to a provisional close.

### 5.6. `vcompact`

Purpose: Make room without loss. Compact accumulated Viber resources — settled memory rows, superseded doc
iterations, finished task trails, keeper artifact batches — into a manifest-indexed archive under
`.viber/.compact/<id>/`, keeping the active workspace lean and history restorable.

Suggest it when:

- A memory file or doc area keeps growing with history nobody revisits.
- Superseded iterations pile up beside the current spec.
- The user wants room for a new phase and the old work is finished, not forgotten.

The Router only flags the bloat; `vcompact` asks what to include (active work is never compacted) and
moves, never deletes (`../commands/compact.md`).

### 5.7. `vflow`

Purpose: Build flows — task-scale lifecycles the project defines for a recurring class of work: three simple
files under `.viber/flow/<name>/` (`sequence.md` the source, `lifecycle.md` the map, `lifecycle.mmd` the picture).

Suggest it when:

- The same multi-step sequence keeps being hand-assembled for the same kind of work.
- A recurring journey has no written route, so every run re-decides its order and gates.
- The user asks to capture "how we always do X".

The Router also runs the suggestion in reverse: when current work matches an existing flow, it points the
agent at that flow's `sequence.md` (`../commands/flow.md`).

---

## 6. Recommendation System

The Router should classify its guidance into three categories.

### 6.1. Next Step

Recommendations about the logical next action in the lifecycle.

Examples:

- "The next expected skill is `architecture`."
- "You have completed Vision. Consider moving to Project Foundation."

### 6.2. Helpful Skill

Suggestions for skills that can improve the current work.

Examples:

- "Consider using `grill-me` to clarify the remaining requirements."
- "There are several unresolved discussions. `close-topics` may help."
- "You have not used the optional `reveal` skill yet. It may help validate the idea."

### 6.3. Workflow Warning

Notifications about missing requirements, dependencies, or inconsistencies.

Examples:

- "The `architecture` skill has not been completed."
- "The expected output from `steering-tech` is missing."
- "You are starting implementation while important foundation work remains incomplete."

Warnings should explain the reason and, when possible, suggest a practical solution.

---

## 7. When and How to Communicate

The Router should provide hints at meaningful moments without interrupting every interaction.

### Recommended Trigger Points

The Router should evaluate the workflow when:

1. A skill starts.
2. A skill completes.
3. A skill fails or becomes blocked.
4. A major project decision is made.
5. A lifecycle output is created or significantly changed.
6. The user moves to another lifecycle step.
7. The user returns to previously completed work.
8. The Router detects a relevant opportunity to suggest another skill.

### Communication Guidelines

- Keep suggestions short and contextual.
- Avoid repeating the same recommendation unnecessarily.
- Explain why a skill is relevant.
- Suggest only the Skills that are relevant; several at once is acceptable when each one earns its place, but avoid long lists of marginal options.
- Do not interrupt active work for low-priority suggestions.
- Do not present optional skills as requirements.
- Do not repeatedly warn about an issue the user has already acknowledged.
- Respect the user's decision to ignore or decline a suggestion.

The Router should behave like a helpful assistant, not a notification system.

---

## 8. Workflow State and Persistence

The Router needs a reliable way to preserve project progress between interactions and sessions.

It should maintain a project-level workflow state containing information such as:

- Current lifecycle step.
- Completed lifecycle steps.
- Skill statuses.
- Skill execution history.
- Skipped optional skills.
- Missing or outdated outputs.
- Outstanding dependencies.
- Open workflow issues.
- Previous recommendations and whether they were accepted or dismissed.

The state lives in the project's `.viber` directory (`<project-root>/.viber/`), beside the registry and the
memory files, so all of the project's Viber state is in one transparent place. The exact storage format should
be chosen based on the surrounding project tooling.

The Router also reads the project's memory files (`memory.md`): `memory.md` supplies the outstanding decisions
and blockers it tracks, and a deferred question is surfaced when its blocker clears. The Router reads memory;
it does not write it — recording questions, answers, and lessons belongs to the Skills and sessions that
produce them.

### Important Rules

- Do not rely only on conversation history.
- Do not assume that a skill ran simply because its output file exists.
- Do not assume that a missing output means the skill was never executed.
- Verify project state when necessary.
- Keep the state synchronized with actual project changes.
- Avoid duplicating information already maintained by authoritative project documents.
- Read the project's Viber version from its `AGENTS.md`; do not keep a separate copy of it, and do not write to it. That section belongs to `adapt`.
- Read the project's `.viber/memory.md`, `settled.md`, and `learnt.md`; surface deferred questions when unblocked and never re-suggest a settled decision. The Router reads memory; it does not write it.

If the Router cannot verify a status, it should mark it as unknown or ask for confirmation instead of guessing.

---

## 9. Router Boundaries

The Router is a guidance and coordination layer, not an execution engine.

### The Router SHOULD:

- Understand the project lifecycle.
- Track workflow progress.
- Identify the current project stage.
- Suggest relevant skills.
- Suggest deck Skills from either deck when the project or task needs them, using `find-skills` or a web search to discover Opensource Deck Skills.
- Recommend logical next actions.
- Detect missing outputs and dependencies.
- Warn about workflow inconsistencies.
- Maintain workflow state.
- Adapt to changes in project direction.
- Read each project's Viber version from its `AGENTS.md`.
- Apply Viber supervision when active: reroute participating Skills' relocatable output to `.viber/<normal-path>`, leaving code and root-files untouched (see `supervision.md`).

### The Router SHOULD NOT:

- Execute skills automatically without authorization.
- Force the user to follow a strict sequence.
- Block the user from proceeding.
- Change skill classifications.
- Add Skills to a project's path itself — that is the job of `adapt`.
- Warn about deck Skills that were never used.
- Invent project requirements.
- Treat suggestions as completed work.
- Replace the responsibilities of individual skills.
- Duplicate the work of `grill-me`, `close-topics`, `adapt`, `thaw`, or other specialized skills.
- Make project decisions on behalf of the user.

The Router may recommend another skill, but the actual work belongs to that skill.

---

## 10. Example Workflow

Consider the following scenario:

1. The user creates an initial project idea.
2. The Router detects that `idea-md` has been completed.
3. It notices that the optional `reveal` skill has not been used and suggests it.
4. The user proceeds to `steering-perception`.
5. During the discussion, several requirements remain unclear. The Router suggests `grill-me`.
6. The conversation expands into several unrelated subjects. The Router suggests `close-topics`.
7. Step 1 is completed, and the Router recognizes that the project is ready for Vision.
8. The user starts the `pages` skill.
9. The Router tracks the progress of Main Pages, Secondary Pages, and Complementary Pages.
10. The user creates the first prototype.
11. The Router recognizes that the initial prototype is complete but that refinement is still expected.
12. After Vision is completed, the Router recommends `steering-tech`.
13. Once `steering-tech` is completed, the Router recommends `architecture`.
14. The user starts implementation before completing every foundation skill.
15. The Router warns about the remaining mandatory foundation work but allows the user to continue.
16. The user returns to complete the missing foundation work.
17. The Router updates the project state and recommendations accordingly.

This example demonstrates that the Router follows the project's actual progress rather than enforcing a predetermined sequence.

---

## 11. Success Criteria

The Router is successful when:

- The user can understand the current project state at any time.
- The user can see which skills have been completed and which remain.
- The Router identifies useful next actions.
- Relevant skills are suggested at the right time.
- Missing outputs and dependencies are detected.
- The workflow remains flexible.
- Progress survives across sessions.
- Suggestions are useful rather than repetitive or distracting.
- The Router never takes control away from the user.

## 12. Final Design Principle

The Router should continuously answer five questions:

1. **Where are we?** — Current lifecycle step and project state.
2. **What have we done?** — Completed skills and outputs.
3. **What remains?** — Expected skills, missing outputs, and unresolved work.
4. **What should we consider doing next?** — Logical next actions and contextual skill suggestions.
5. **Is anything getting in our way?** — Ambiguities, dependencies, missing decisions, and workflow issues.

Its job is not to make the project follow the lifecycle perfectly.

Its job is to make sure the user and agent always understand the lifecycle well enough to make informed decisions while building the project.
---

## 13. Diagram

How the Router fits the lifecycle is diagrammed in `diagrams/router-fit.mmd`: the sources it reads (lifecycle, project Viber version, decks, evidence, memory) and the guidance it emits — one graph, no new rules beyond sections 2 and 3.
