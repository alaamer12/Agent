# Project Lifecycle
## A Skill-Based Workflow for Taking a Project from Idea to Implementation

## 1. Overview

The Project Lifecycle is a structured workflow that guides a project from its initial idea to a working product.

It divides the development journey into **four main phases**:

1. **Idea & Understanding** — Understand the idea, its purpose, and the problem it aims to solve.
2. **Vision** — Define what the product should look like and how users will interact with it.
3. **Project Foundation** — Establish the technical direction, architecture, engineering standards, and project documentation.
4. **Implementation** — Turn the vision and technical foundation into a working product.

Each phase contains a collection of Skills. These Skills have different responsibilities and produce outputs that help move the project forward.

The workflow also includes shared Skills that can be invoked during any phase. These are not separate lifecycle phases and do not have to follow the main sequence.

Beside the lifecycle sit two **Skill Decks** — **`<USERNAME>`'s Deck** (every Skill registered with the user's agent, optionally extended with Skill repositories the user chooses; for the author, "Amr's Deck") and the **Opensource Deck** (published Skills that are not registered). Deck Skills can be used whenever a project or task needs them, but they are not part of Viber itself (see section 8).

Viber has **fixed foundations**, but no two projects are the same. Each project therefore has its **own Viber version**: the fixed lifecycle plus what that project adds to it. The project version is recorded in the Viber section of the project's `AGENTS.md` and is maintained by the `adapt` Skill (see section 7.3).

Work with Viber starts with **`/viber init`**: it indexes every registered Skill into the project's `.viber/registry.md`, creates the project's memory files (`.viber/memory.md`, `settled.md`, `learnt.md`), points to the registry from the project's `AGENTS.md`, and starts the lifecycle at the right step (see `vinit` skill → `references/init.md`).

Viber can run in **supervision mode**: when the project's `AGENTS.md` declares Viber, the relocatable documentation and procedure outputs of every participating Skill are gathered under the project's `.viber` directory, while production code and root-files (`README.md`, `AGENTS.md`) stay put. Participation follows deck membership and a per-Skill `viber: part | separated` frontmatter tag. This is disciplined vibe-engineering — Viber owns the knowledge around the code, never the code (see `supervision.md`). The canonical project layout — root-files, code, `tools/`, `scripts/`, `artifacts/`, `scratch/`, and `.viber` — is defined in `structure.md`.

### 1.1. Workflow Principles

The lifecycle follows these principles:

- **Phase-based:** The project progresses through four main phases.
- **Skill-driven:** Each phase is carried out through specialized Skills.
- **Output-oriented:** Every phase should produce useful outputs that support the next phase.
- **Flexible execution:** Not every Skill needs to run in a rigid sequence.
- **Mandatory and Optional Skills:** Some Skills are essential to the workflow, while others provide additional capabilities and can be skipped.
- **Shared capabilities:** Some Skills can be invoked whenever needed, regardless of the current phase.
- **Fixed foundations, adaptable per project:** The lifecycle itself does not change between projects; each project adds to it what its own path needs, and never removes from it.
- **Decks outside the lifecycle:** Skills that only some projects need live in decks and are pulled in by relevance, never expected by default.
- **Supervision umbrella:** When Viber is declared in `AGENTS.md`, participating Skills' relocatable outputs gather under `.viber`; code and root-files stay (see `supervision.md`).

### 1.2. Project Phases — [DR] · [IP] · [PP]

The four lifecycle phases run inside three **project phases** — the states a project passes through:

| Project phase | Name | Covers | Document posture |
|---|---|---|---|
| 1 | **Draft [DR]** | Lifecycle Phases 1–3 — deciding and refining before implementing | every doc is the current best, revisable; closes are provisional steering notes, never formal decision records (`thaw`) |
| 2 | **In-Progress [IP]** | Lifecycle Phase 4 — implementation, testing, launching | drafting has ended; decisions may be cast into formal records (ADRs) as they settle into code |
| 3 | **Post-production [PP]** | From the first real release onward | decisions are settled history; changes supersede them |

Viber itself is still in development, so the flowchart (`lifecycle-flow.mmd`) draws the first two bands —
DRAFT and IN-PROGRESS; POST-PRODUCTION begins beyond the "Working product" milestone, at first release,
and is not yet governed.

Iterating back into an earlier lifecycle phase is normal **within** a project phase; crossing
[DR] → [IP] is the one that changes the posture — provisional becomes formal there, which is why the
`decisions/` record convention belongs to [IP]/[PP], never [DR].

## 2. Skill Classification

Skills are classified into two categories:

### 2.1. Mandatory Skills

Mandatory Skills are considered part of the standard lifecycle.

They are expected to be executed as part of the phase unless there is a clear reason not to.

### 2.2. Optional Skills

Optional Skills provide additional capabilities or improvements.

They can be executed when they are useful for the project, but they are not required to complete the lifecycle.

### 2.3. Shared / Intermediate Skills

Some Skills do not belong to a single phase.

They can be invoked during the execution of any phase to solve a particular need. For example, a Skill might help clarify requirements (`grill-me`), organize unresolved topics (`close-topics`), adapt the project's own Viber version (`adapt`), keep a draft from freezing into law (`thaw`), or correct mistakes.

These Skills are described separately because they do not represent additional lifecycle phases.

### 2.4. Deck Skills

Deck Skills are not part of Viber.

They come from one of the two Skill Decks and are used only when the project or task calls for them. For example, not every project cares about SEO, so the `seo` Skill lives in a deck rather than in the lifecycle.

Deck Skills are never Mandatory and never expected. They are described in section 8.

---

# 3. Phase One — Idea & Understanding

## 3.1. Objective

The first phase focuses on understanding the project before making detailed product or technical decisions.

The goal is to transform an initial idea into a clear understanding of:

- What the project is.
- What problem it solves.
- Why the project should exist.
- Who it is intended for.
- What makes it valuable.
- What the project is trying to achieve.

At this stage, the focus is on understanding the business and the idea, not designing the complete product or choosing its technical architecture.

## 3.2. Skills

### 1. idea-md

**Status:** Mandatory

Creates the initial `idea.md` file.

This file captures the original project idea and acts as an initial reference for the project.

It should preserve the main concept, purpose, and initial information without prematurely forcing detailed decisions.

### 2. reveal

**Status:** Optional

Investigates how unique or similar the project idea is compared with existing products and projects.

It can research public sources such as:

- Search engines.
- GitHub.
- Reddit.
- Product websites.
- Social media.
- Application stores.
- Other relevant public sources.

The goal is to discover existing alternatives, competitors, similar ideas, and potential differences.

The result helps the project owner understand the existing landscape before moving further.

### 3. steering-perception

**Status:** Mandatory

Develops a deeper understanding of the business and the project's overall perception.

It focuses on understanding the problem, purpose, business context, and intended direction.

It helps establish a shared understanding of what the project represents.

### 4. agents-md

**Status:** Mandatory

Creates the `AGENTS.md` file.

This file provides project context and instructions for AI agents working on the project.

It helps agents understand the project, its conventions, and important instructions before performing tasks.

It also provides a foundation for future agent-based workflows and parallel work.

## 3.3. Execution Flow

A typical execution sequence is:

1. Capture the original idea using `idea-md`.
2. Optionally investigate existing projects using `reveal`.
3. Develop a deeper understanding using `steering-perception`.
4. Establish project context and agent instructions using `agents-md`.

The `reveal` Skill can be skipped if competitive research is not needed at this point.

## 3.4. Expected Outputs

At the end of this phase, the project should have:

- An initial `idea.md`.
- A clearer understanding of the business and problem.
- An initial assessment of similar projects, if `reveal` was executed.
- A documented project perception.
- An `AGENTS.md` file containing project context and agent instructions.

**Completion result:** The project idea is understood well enough to begin defining the product vision.

---

# 4. Phase Two — Vision

## 4.1. Objective

The Vision phase defines the product from the user's perspective.

It focuses on what the product should contain, how users will interact with it, what pages and features are needed, and how the overall experience should look.

The main goal is to establish a clear product vision before moving into technical architecture.

This phase is independent of technology choices.

In other words, the product vision should describe what needs to be built without being unnecessarily limited by the implementation technology.

## 4.2. Skills

### 1. pages

**Status:** Mandatory

The `pages` Skill defines the product's page structure.

It is divided into three internal sections:

#### A. Main Pages

These are the core pages of the product.

They are usually accessible at any time and are central to the primary user experience.

They represent the main navigation structure and the most important parts of the application.

#### B. Secondary Pages

These pages are important but are not usually the primary focus of the user's journey.

They support the main pages and provide additional functionality when needed.

#### C. Complementary Pages

These pages provide additional information, supporting functionality, or supplementary experiences.

They complete the product without necessarily being part of the main navigation or primary user flow.

The three sections together provide a complete map of the product's pages.

### 2. prototype

**Status:** Mandatory

Creates the visual prototype of the product.

The prototype is developed progressively rather than being treated as a one-time task.

It has two main stages:

**First Draft**

- Create an initial visual representation of the product.
- Represent the main pages and core experience.
- Establish the initial layout and visual direction.

**Refinement**

- Incorporate additional pages.
- Include missing features.
- Improve the user experience.
- Refine layouts and interactions.
- Ensure the prototype reflects the complete product vision.

The prototype is a visual representation of the product, not its final technical implementation.

### 3. denoise

**Status:** Optional

Helps improve the clarity and quality of the product vision.

It can be used to identify unnecessary complexity, unclear elements, or noise in the proposed experience.

### 4. anti-slop

**Status:** Optional

Helps improve the quality and intentionality of the product's visual and experiential decisions.

It can be used to identify generic, low-quality, or poorly considered design choices and improve the overall result.

## 4.3. Execution Flow

A typical execution sequence is:

1. Start defining the product using `pages`.
2. Identify and document the Main Pages.
3. Create the first prototype draft using `prototype`.
4. Continue defining Secondary Pages.
5. Define Complementary Pages.
6. Refine the prototype to include the complete page structure and product features.
7. Optionally use `denoise` and `anti-slop` to improve the result.

The prototype and page definitions can be revisited as the product becomes clearer.

The process is iterative: new information can lead to updates in both the page structure and prototype.

## 4.4. Expected Outputs

At the end of this phase, the project should have:

- A complete page structure.
- Main Pages.
- Secondary Pages.
- Complementary Pages.
- A clear understanding of the product's features and user experience.
- An initial prototype.
- A refined prototype representing the intended product.

**Completion result:** The project has a clear product vision and a visual representation of what needs to be built.

---

# 5. Phase Three — Project Foundation

## 5.1. Objective

The Project Foundation phase establishes the technical and engineering foundation required to implement the product.

While the Vision phase describes what the product should be, this phase defines how the project should be engineered.

It establishes:

- Technical direction.
- System architecture.
- Engineering decisions.
- Technical contracts.
- Component and state conventions.
- Styling and type conventions.
- Project rules and documentation.

The objective is to reduce ambiguity before implementation begins.

## 5.2. Skills

### A. Technical Direction & Architecture

#### 1. steering-tech

**Status:** Mandatory

This Skill comes first in the technical foundation phase.

It captures the initial technical aspects and direction of the project.

It helps establish the technical context and important engineering considerations before defining the architecture.

#### 2. architecture

**Status:** Mandatory

This Skill follows `steering-tech`.

It defines the system's engineering design based on the established technical direction.

It focuses on the system structure, major components, responsibilities, boundaries, and relationships between different parts of the system.

**Important ordering:**

`steering-tech` → `architecture`

The technical direction should be established before the architecture is defined.

### B. Engineering Foundation

These Skills establish the conventions and engineering rules used throughout implementation.

#### 3. steering

**Status:** Mandatory

Defines the general project steering and guidance.

It helps maintain consistency in how the project is developed.

#### 4. contract

**Status:** Mandatory

Defines technical contracts and agreements between different parts of the system.

These contracts help establish clear expectations and reduce integration ambiguity.

#### 5. pvc

**Status:** Mandatory

A frontend component-related Skill.

It contributes to establishing the component foundation and conventions used by the project.

#### 6. states

**Status:** Mandatory

Defines how application states should be handled and organized.

It helps establish consistency in state management across the project.

#### 7. styling

**Status:** Mandatory

The styling battery — one skill, two levels. `build` defines the project's styling foundation and conventions for new work (structure, layer chain, tokens, naming); `retrofit` takes an existing project's hardcoded or duplicated styling into a token-driven system with before/after parity evidence.

It helps ensure a consistent visual implementation and contributes to the project's overall styling quality.

#### 8. typing

**Status:** Mandatory

Establishes type-related conventions and standards.

It helps improve consistency and clarity in the project's type definitions.

#### 9. antipattern

**Status:** Mandatory

Creates documentation describing anti-patterns that AI agents should avoid.

It records undesirable approaches, practices, or implementation decisions.

The purpose is to make these restrictions explicit and accessible to agents throughout the project.

This is a project documentation and guidance responsibility, not simply a code-review activity.

### C. Project Documentation

These Skills create important documentation files that help maintain project knowledge.

#### 10. readme-md

**Status:** Mandatory

Creates or maintains the project's `README.md`.

It provides an accessible introduction to the project and its important information.

#### 11. commitments-md

**Status:** Mandatory

Creates the project's commitments documentation.

It records important commitments and agreed project principles.

#### 12. glossary-md

**Status:** Mandatory

Creates the project's glossary.

It documents important terminology and definitions to maintain consistent language across the project.

#### 13. system-md

**Status:** Mandatory

Creates the project's system documentation.

It provides a reference for understanding the system and its important characteristics.

#### 14. units-md

**Status:** Mandatory

Creates and maintains the project's `UNITS.md`.

It indexes the project's reusable units (components, rules, clients, helpers), so agents extend what already exists instead of building a parallel version.

### D. Optional Foundation Skills

#### 15. packages

**Status:** Optional

Helps investigate, select, or manage packages and dependencies that may be useful for the project.

#### 16. personalize

**Status:** Optional

Provides additional project-specific personalization and customization.

It can help adapt agent context and instructions to the project's needs.

#### 17. mistakes

**Status:** Optional

Can be used during this phase to identify and correct mistakes in project documentation, technical decisions, or other foundation-related work.

## 5.3. Execution Flow

A typical execution sequence is:

1. Establish technical direction using `steering-tech`.
2. Define the architecture using `architecture`.
3. Establish general project steering using `steering`.
4. Define contracts and engineering conventions.
5. Establish the frontend component foundation, states, styling, and type conventions.
6. Document anti-patterns using `antipattern`.
7. Generate the required project documentation.
8. Optionally investigate packages and dependencies using `packages`.
9. Optionally personalize the project context using `personalize`.
10. Use `mistakes` when documentation or foundation-related corrections are needed.

The Skills do not all need to execute as one uninterrupted sequence. Their dependencies and the information they require should determine their actual order.

## 5.4. Expected Outputs

At the end of this phase, the project should have:

- A documented technical direction.
- A defined system architecture.
- Engineering guidance and project steering.
- Technical contracts.
- Component-related conventions.
- State management conventions.
- Styling conventions.
- Type conventions.
- Documented anti-patterns.
- Project documentation files.

**Completion result:** The project has the technical and engineering foundation required for implementation.

---

# 6. Phase Four — Implementation

## 6.1. Objective

The Implementation phase transforms the product vision and technical foundation into a working product.

It is where the actual code is written, features are developed, problems are debugged, and the product is continuously improved.

Unlike the previous phases, this phase focuses directly on producing and maintaining working software.

## 6.2. FULL CODE

**Status:** Mandatory Skill Group

`FULL CODE` is a folder or group containing multiple code-related Skills.

It should not be treated as one individual Skill.

Its purpose is to organize the different activities required to implement and maintain the product.

The group includes Skills such as:

### 1. Plan

Defines the implementation plan for a task or feature.

It helps break down work into manageable parts before implementation.

### 2. Implement

Carries out the actual coding work.

It transforms the requirements and technical decisions into working software.

### 3. Debugging

Investigates and diagnoses technical problems.

It focuses on understanding why something is not working as expected.

### 4. Fix

Addresses underlying technical problems and corrects their root causes.

It should focus on solving the actual problem rather than simply hiding symptoms or satisfying superficial checks.

### 5. Update

Handles updates and changes to existing implementations.

It helps evolve the existing codebase while respecting the project's established conventions.

These are examples of the internal Skills within the `FULL CODE` group. The group can contain additional code-related Skills as its structure evolves.

## 6.3. Optional Skill

### mistakes

**Status:** Optional

Can be used during implementation to identify and correct mistakes in code or implementation decisions.

It is useful when problems are discovered during development.

## 6.4. Execution Flow

A typical implementation cycle is:

1. Define the task or feature.
2. Plan the implementation.
3. Implement the required changes.
4. Debug problems when they occur.
5. Fix the underlying issues.
6. Update existing implementations when requirements or decisions change.
7. Repeat the cycle until the required functionality is complete.

This phase is iterative.

Implementation may reveal missing requirements, unclear decisions, or problems in the previous phases. When that happens, the workflow can return to an earlier phase to clarify or update the relevant information.

## 6.5. Expected Outputs

At the end of this phase, the project should have:

- Implemented features.
- Working application functionality.
- Corrected technical issues.
- Updated implementations.
- A product that reflects the established vision and technical foundation.

**Completion result:** A working product.

---

# 7. Shared / Intermediate Skills

Not every Skill belongs to a specific lifecycle phase.

Some Skills are designed to help the workflow itself. They can be invoked whenever their capabilities are needed.

These Skills should be treated as shared tools rather than fixed steps in the lifecycle.

## 7.1. grill-me

**Role:** Clarification and questioning.

`grill-me` helps identify unclear information, missing decisions, assumptions, and gaps.

It can be invoked during any phase when additional clarification is required.

Examples:

- During Idea & Understanding: clarify the business idea or problem.
- During Vision: clarify user flows, features, or page behavior.
- During Project Foundation: clarify architecture or engineering decisions.
- During Implementation: clarify expected behavior or task requirements.

It is not a separate lifecycle phase and does not need to run at a fixed point.

## 7.2. close-topics

**Role:** Topic organization and closure.

`close-topics` helps organize multiple open topics and handle them independently.

It can be invoked during any phase when discussions or decisions become too broad or when several unresolved topics need to be tracked.

Its purpose is to help ensure that topics are addressed and closed rather than being lost in the middle of the workflow.

## 7.3. adapt

**Role:** Adapting the project's own Viber version.

`adapt` helps a project grow its own Viber version. Viber's foundations are fixed, but every project's path is different, so a project may need a capability that nothing planned covers.

It can be invoked during any phase when a need keeps returning that no planned Skill covers.

Examples:

- During Idea & Understanding: the project's domain needs a Skill that no lifecycle or deck Skill provides.
- During Vision: a deck Skill, such as a design Skill, should become a standing part of this project's path.
- During Project Foundation: the same project-specific rules keep being explained again for each decision.
- During Implementation: the same correction is given repeatedly across features.

It checks, in order, and stops at the first answer that holds:

1. A Viber Skill or a registered Skill from the user's deck already does the job — attach it to this project.
2. The need is a fact, rule or decision rather than a procedure — write it into the document that owns it.
3. A maintained Skill from the Opensource Deck covers it — propose installing it, then attach it.
4. It is a fixed recipe with no judgment — record it as a `how-to-do` procedure.
5. None of the above — create a small project Skill, preferably extending the closest existing Skill.

Every adaptation is approved by the user and recorded in the Viber section of the project's `AGENTS.md`. `adapt` never removes, reorders or reclassifies anything in the fixed lifecycle, and never runs the Skills it creates.

It is not a separate lifecycle phase and does not need to run at a fixed point.

## 7.4. mistakes

**Role:** Mistake identification and correction.

**Status:** Optional

`mistakes` can be used in more than one phase.

- During Project Foundation: identify and correct mistakes in documentation, technical decisions, or project conventions.
- During Implementation: identify and correct mistakes in code and implementation work.

It is not restricted to one phase.

## 7.5. Viber Memory

**Role:** The project's conversational ledger.

Viber Memory is a shared persistence mechanism, not a Skill that runs on its own. It keeps three files in the
project's `.viber` directory: `memory.md` (open and deferred questions), `settled.md` (answered questions, with
reasons), and `learnt.md` (facts learned about the user and the project). Every phase feeds it — `grill-me` and
`close-topics` record questions and answers, `agents-md` records its pending items, and any session records a
learned fact — and the Router reads it to surface deferred questions when their blockers clear.

It is specified in `memory.md`. Like the other shared capabilities, it can be used during any phase and does
not need to run at a fixed point.

## 7.6. thaw

**Role:** Anti-rigidity during drafting.

`thaw` melts the draft material that has frozen into assumed law: a draft doc cited to eliminate options, an
agent defending its own earlier recommendation, the user's prior answer treated as non-questionable, or
improvement stopped at "good enough" while a better design is reachable. It separates the stable invariant
from the draft mechanism, re-opens the options a draft constraint pruned, and re-validates — then the topic
closes provisionally again.

It can be invoked during any phase in which something is being drafted: a perception or tech steering doc
treated as fixed, a stack choice defended past its evidence, or a user answer from an earlier frame applied
unchanged to a new one.

It pairs with `close-topics`: `thaw` re-opens the frozen topic, `close-topics` walks it to its provisional
close. During Draft [DR] a re-closed decision is written as a revisable steering note, never a formal decision
record.

It is not a separate lifecycle phase and does not need to run at a fixed point.

## 7.7. vcompact

**Role:** Making room without loss. A Viber **command** — a real Skill carrying the `v` prefix (section 7.8) — callable in any phase.

`vcompact` compacts accumulated Viber resources — settled memory rows, superseded doc iterations, finished
task trails, keeper artifact batches — into a timestamped, manifest-indexed archive under
`.viber/.compact/<id>/`, so the active workspace stays lean while history stays restorable. It runs when
the user asks or when the Router flags a bloated area, never on its own; active work is never compacted,
and ambiguous targets are asked with a recommendation.

It is specified in `vcompact` skill → `references/compact.md`, and like the other shared capabilities it can be invoked during any
phase — accumulation is phase-blind.

## 7.8. Viber Commands — the `v` prefix

Viber's own utility Skills are **commands**: each is a real Skill (not a shell alias or script), but every
name carries the `v` prefix — `vinit`, `vcompact`, `vflow`, and whatever Viber grows next. They produce no
phase output of their own; they serve Viber itself and the project's state across the phases — starting
and refreshing the setup, keeping the workspace lean, and whatever maintenance the need earns later.

- `vinit` — the Skill behind `/viber init`: indexes the deck, creates the `.viber` state and its memory
  files, marks the activation in `AGENTS.md`, starts the flow (`vinit` skill → `references/init.md`).
- `vcompact` — compaction with no losses (`vcompact` skill → `references/compact.md`).
- `vflow` — builds flows: task-scale lifecycles under `.viber/flow/`, mini-Vibers for recurring work
  (`vflow` skill → `references/flow.md`).
- A new command registers itself here (section 7 listing + the Skills inventory), gets its own spec file
  beside the others, and declares `viber: part` in its `SKILL.md` frontmatter.

The naming law: a Viber-native command always starts with `v`; a deck Skill keeps its own name and joins
the umbrella through registration (`supervision.md` 3), never by being renamed.

---

# 8. Skill Decks

## 8.1. What a Deck Is

A Skill Deck is a collection of Skills that can be used during a project but are **not part of Viber itself**.

The lifecycle contains what every project needs. Decks contain what only some projects or tasks need. A public marketing website may need SEO; an internal admin console does not. Putting such Skills into the lifecycle would make every project carry work it does not need.

There are two decks, and **registration decides which deck a Skill is in — not who wrote it**:

| Deck | Contains |
|---|---|
| **`<USERNAME>`'s Deck** | Every Skill registered with the user's agent — global or project-level — plus any Skill repositories the user chooses to add |
| **Opensource Deck** | Every published Skill that is not registered |

A published Skill moves from the Opensource Deck to the user's deck the moment the user registers it.

## 8.2. `<USERNAME>`'s Deck

**All registered Skills**, whatever their level:

- **Global Skills** registered with the user's agent.
- **Project-level Skills** registered inside the project.
- **Extension sources (optional):** Skill repositories the user chooses to add to the deck, so their Skills count as available too. Whether to extend the deck, and with which repositories, is entirely the user's decision.

The deck is named after the user: `<USERNAME>` is the user running Viber.

**For the author of Viber, the deck is "Amr's Deck":** the Skills registered in Amr's agent, extended with Amr's own repository, which holds a large collection of professional Skills:

- https://github.com/alaamer12/Agent/tree/main/skills/insource

Examples from Amr's Deck, not a closed list: `seo`, `scraper-optimizer`, `watch-video`, `capture`, `fahlwy`, `mine`, `benchmark`, `pdf`, and open-source Skills Amr has registered, such as `impeccable`.

- **Where to find them:** the registry written by `/viber init` (see `vinit` skill → `references/init.md`), which indexes every registered Skill and every extension source.
- **Note:** the Viber lifecycle Skills are registered too, but they belong to Viber, not to the deck.

## 8.3. Opensource Deck

**All published Skills that are not registered** with the user's agent — the open-ended world of Skills written and shared by others.

Examples by area, not a closed list:

| Area | Examples |
|---|---|
| Design and UI | `impeccable`, `frontend-design`, `ui-ux-pro-max`, `web-design-expert`, `ui-taste`, `design-taste-frontend` |
| Frameworks and styling | `vue-development`, `react-best-practices`, `react-native-best-practices`, `tamagui-best-practices`, TailwindCSS Skills, `daisyui` |
| Mobile | `mobile-design`, `ios-design`, `building-native-ui`, `expo-ui` |
| Testing and review | `webapp-testing`, `code-review`, `code-review-and-quality`, `gh-fix-ci` |
| Writing | `humanizer`, `anti-ai-writing` |
| Agent tooling | `skill-creator`, `agent-creator`, `find-skills`, `agent-browser` |
| Thinking | `brainstorming`, `creative-thinking-for-research` |

Any of these that a user has registered is in that user's deck instead.

- **Where to find them:** `find-skills` and web search.
- **Before adopting one:** check that it is maintained and actually used, and that it does not contradict the Viber Skill covering the same area. Registering it moves it into the user's deck.

## 8.4. How Decks Are Used

- **By relevance only.** A deck Skill is suggested when the project or task needs it, never because it exists.
- **Any Skill from either deck.** Viber may suggest any Skill from the user's deck or the Opensource Deck, not only the examples listed here. Opensource Deck Skills are discovered with `find-skills` or a web search.
- **Several at once is fine.** Viber may suggest more than one Skill for the same situation — for example a lifecycle Skill plus a deck Skill that strengthens it, or Skills from both decks — as long as each one is relevant.
- **No warnings.** A deck Skill that is never used is not a missing step.
- **One-off use** for a single task is simply using the Skill.
- **Becoming part of the project's path** — for example, `seo` for every public page of a project — is an adaptation: `adapt` records it in the project's `AGENTS.md` with its lifecycle point and status.
- **Complement, never replace.** When a deck Skill overlaps a Viber Skill, the Viber Skill still owns the lifecycle output, and the deck Skill adds to it. For example, `impeccable` can strengthen the work of `prototype` or `anti-slop` without replacing either.

---

# 9. Complete Lifecycle Flow

The overall workflow is:

**Idea & Understanding → Vision → Project Foundation → Implementation**

Each phase produces outputs that become useful inputs for the following phase.

However, this does not mean the project can never move backward.

The lifecycle supports iteration and revision. If implementation reveals a missing requirement, the workflow can return to Vision. If a technical decision needs to change, it can return to Project Foundation.

Shared Skills such as `grill-me`, `close-topics`, `adapt`, `thaw` and `vcompact` can be invoked at any point. Deck Skills can be pulled in at any point when the project or task needs them.

## 9.1. Mermaid Flowchart

The complete lifecycle flowchart lives in [`lifecycle-flow.mmd`](../assets/diagrams/lifecycle-flow.mmd) — one renderable diagram file, so the lifecycle document and its graph each have a single owner. The graph mirrors sections 3–6: the four phases with their mandatory and optional Skills (carried by node color, see the diagram legend), the milestones between them, the intermediate Skills (`grill-me`, `close-topics`, `adapt`, `thaw`) reachable from any step, the two Skill Decks pulled in by relevance, and the project-phase bands DRAFT [DR] and IN-PROGRESS [IP] (section 1.2).

## 9.2. Phase Summary

| Phase | Main Objective | Main Result |
|---|---|---|
| 1. Idea & Understanding | Understand and validate the idea | Project understanding |
| 2. Vision | Define the product and user experience | Product vision and prototype |
| 3. Project Foundation | Establish technical and engineering foundations | Architecture and project documentation |
| 4. Implementation | Build and improve the product | Working product |

---

# 10. Skills Inventory

The following table summarizes the current Skill classification.

| Skill | Phase / Group | Status |
|---|---|---|
| idea-md | Idea & Understanding | Mandatory |
| reveal | Idea & Understanding | Optional |
| steering-perception | Idea & Understanding | Mandatory |
| agents-md | Idea & Understanding | Mandatory |
| pages | Vision | Mandatory |
| prototype | Vision | Mandatory |
| denoise | Vision | Optional |
| anti-slop | Vision | Optional |
| steering-tech | Project Foundation | Mandatory |
| architecture | Project Foundation | Mandatory |
| steering | Project Foundation | Mandatory |
| contract | Project Foundation | Mandatory |
| pvc | Project Foundation | Mandatory |
| states | Project Foundation | Mandatory |
| styling | Project Foundation | Mandatory |
| typing | Project Foundation | Mandatory |
| antipattern | Project Foundation | Mandatory |
| readme-md | Project Foundation | Mandatory |
| commitments-md | Project Foundation | Mandatory |
| glossary-md | Project Foundation | Mandatory |
| system-md | Project Foundation | Mandatory |
| units-md | Project Foundation | Mandatory |
| packages | Project Foundation | Optional |
| personalize | Project Foundation | Optional |
| FULL CODE | Implementation | Mandatory Group |
| Plan | FULL CODE | Internal Skill |
| Implement | FULL CODE | Internal Skill |
| Debugging | FULL CODE | Internal Skill |
| Fix | FULL CODE | Internal Skill |
| Update | FULL CODE | Internal Skill |
| grill-me | Shared | Intermediate |
| close-topics | Shared | Intermediate |
| adapt | Shared | Intermediate |
| thaw | Shared | Intermediate |
| vcompact | Viber Command | Any phase |
| vflow | Viber Command | Any phase |
| vinit | Viber Command | Entry · refresh |
| mistakes | Shared | Optional |

Deck Skills are not listed here. They are not part of Viber; each deck is discovered as described in section 8. Viber Memory (section 7.5) is a shared mechanism, not a Skill, and is not listed here.

---

# 11. Skills Awaiting Classification

Some Skill names have been mentioned but their final role, phase, or status has not yet been established.

They should remain outside the confirmed lifecycle structure until their responsibilities are clarified.

- `assets`
- `treat`
- `ladder`
- `bleed`
- `seam`
- `theskills`

Their placement should be decided based on what each Skill actually does, rather than assigning them to a phase prematurely.

---

# 12. Final Workflow Definition

The Project Lifecycle is a four-phase, Skill-based workflow:

1. **Idea & Understanding** establishes what the project is and why it should exist.
2. **Vision** establishes what the product should be and how users should experience it.
3. **Project Foundation** establishes how the product should be engineered and maintained.
4. **Implementation** turns the defined product and technical foundation into working software.

Mandatory Skills provide the standard workflow. Optional Skills add capabilities when needed. Shared Skills support the workflow across all phases. Deck Skills, from the user's deck and the Opensource Deck, are pulled in only when a project or task needs them.

The lifecycle's foundations are fixed, but each project has its own Viber version: `adapt` records what the project adds in its `AGENTS.md`, without ever changing the fixed foundations.

The lifecycle is structured but not rigid. It provides a clear direction from idea to product while allowing clarification, iteration, and correction whenever necessary.

The four lifecycle phases live inside the project phases of section 1.2: drafting [DR] spans understanding,
vision, and foundation; implementation opens In-Progress [IP]; Post-production [PP] begins at the first real
release, after this workflow's endpoint.

**The ultimate goal is not merely to complete four phases. It is to create a repeatable process that takes a project from an initial idea to a well-defined, properly engineered, and working product.**