# Viber — `init` Command (`vinit`)

## 1. Overview

`init` is the entry command of the Viber Skill — a Viber **command** (`viber` skill → `references/lifecycle.md` 7.8): a real Skill
whose name carries the `v` prefix (`vinit`):

```text
/viber init
```

It prepares Viber to work on a project in three steps:

1. **Understand the user's deck** — index every registered Skill (plus any Skill repositories the user chooses to add) into a **registry file** inside the project's `.viber` directory, and create the project's memory files.
2. **Mention it in `AGENTS.md`** — so every agent working on the project knows the registry exists and where it is.
3. **Start the flow** — find where the project stands in the lifecycle and begin the next step.

`init` can be run again at any time. A second run refreshes the registry and re-checks where the project stands; it never starts the project over.

---

## 2. Step 1 — Understand the User's Deck

### 2.1. What Is Read

The user's deck is named **`<USERNAME>`'s Deck**, where `<USERNAME>` is the user running Viber. **Registration decides what is in it, not who wrote the Skill.** It contains:

- **Every registered Skill**, whatever its level:
  - **Global** — registered with the agent for every project, in the Skills folder of each agent the user works with.
  - **Project-level** — registered inside the current project.
- **Extension sources (optional)** — Skill repositories the user chooses to add, so their Skills count as available too. `init` asks whether the user wants to add any; extending the deck is entirely the user's decision.

For the author of Viber, the deck is **Amr's Deck**: the Skills registered in Amr's agent, extended with Amr's own repository of professional Skills, https://github.com/alaamer12/Agent/tree/main/skills/insource.

`init` asks for `<USERNAME>` on the first run and stores it in the registry.

### 2.2. How It Is Read

- **Metadata only.** For each Skill, `init` reads its name, description and when-to-use from the top of its `SKILL.md`. It does not load whole Skills; the registry is an index, not a copy.
- **Each Skill is classified** as one of:
  - **Viber** — a Skill that is part of the lifecycle (as listed in the Project Lifecycle document).
  - **`<USERNAME>`'s Deck** — every other registered or extension-source Skill.
- **Each Skill records its scope**: global, project-level (with its project path), or extension source.
- **Each Skill gets an area**, such as design, audit, code, research or media, so the Router can find candidates for a need quickly.
- **Each Skill records its `viber` tag** — `part`, `separated`, or untagged — read from the `SKILL.md` frontmatter. It declares whether the Skill joins the supervision umbrella (see `viber` skill → `references/supervision.md`).
- **Conflicts are noted.** When the same Skill name appears in more than one source with different content, both are recorded and the user is told.

The Opensource Deck — every published Skill that is not registered — is **not** scanned by `init`. It is open-ended, so its Skills are discovered when they are needed, with `find-skills` or a web search. A Skill the user registers later joins the user's deck on the next `init`.

### 2.3. Where the Registry Is Stored

The registry lives in the **project's** `.viber` directory — `<project-root>/.viber/registry.md` — not in a
user-home folder. Keeping it inside the project makes it visible and transparent to the user: they can see
exactly which Skills Viber considers available for this project. The deck's membership is still decided by
registration (a registered Skill belongs to the user's deck), but each project materializes its own snapshot
of that deck. Project-level Skills are recorded with the project they belong to.

| Platform | Location |
|---|---|
| Windows | `<project-root>\.viber\registry.md` |
| macOS / Linux | `<project-root>/.viber/registry.md` |

### 2.4. Registry Format

```markdown
# Viber Registry — <USERNAME>'s Deck

| Field | Value |
|---|---|
| User | <USERNAME> |
| Last scanned | <YYYY-MM-DD> |
| Sources | <each agent Skills folder, project, and extension repository, with its commit or date when known> |
| Skills | <count> Viber · <count> in <USERNAME>'s Deck |

## Viber

| Skill | Purpose | When to use | Source |
|---|---|---|---|
| <name> | <one line> | <one line> | <path> |

## <USERNAME>'s Deck

| Skill | Scope | Area | Viber | Purpose | When to use | Source |
|---|---|---|---|---|---|---|
| <name> | global / project: <path> / extension | <area> | part / separated / excluded | <one line> | <one line> | <path or URL> |

## Conflicts

| Skill | Sources | Difference |
|---|---|---|
| <name> | <source A> · <source B> | <what differs> |
```

### 2.5. Refreshing

When the registry already exists, `init` rescans and reports what changed since the last scan: Skills added, removed, or whose description changed. It then rewrites the registry. The user's Skills are never modified.

### 2.6. The Project Memory Files

Alongside the registry, `init` creates the project's three memory files in the same `.viber` directory, each
with its empty template (see `viber` skill → `references/memory.md`):

- `memory.md` — open and deferred questions.
- `settled.md` — answered questions, with reasons.
- `learnt.md` — facts learned about the user and the project.

On a later run, `init` refreshes the registry but **never erases or resets the memory files** — they are the
project's durable conversational ledger. If a memory file already exists, `init` leaves it untouched.

### 2.7. Deck Exclusions and the Umbrella

Because deck membership decides which Skills fall under Viber's supervision umbrella (see `viber` skill → `references/supervision.md`),
`init` asks the user whether any deck Skills should be **excluded**, and states the consequence of each choice:

- **Under the umbrella** — Viber reroutes the Skill's relocatable output into `.viber` and remembers it.
- **Excluded / out of the deck** — Viber does not guarantee control or always-remembering; the Skill writes to
  its normal path.

`init` records the exclusions in the registry's `Viber` column. A Skill tagged `viber: separated` is independent
regardless. The user's exclusions are honored on every later run.

### 2.8. The Project Layout

`init` aligns the project with the canonical layout (`viber` skill → `references/structure.md`): it ensures the `.gitignore` carries the
layout duties (`artifacts/` and `scratch/` fully ignored, plus language env and build outputs), and creates a
layout folder the first time something needs to live there — no empty scaffolding. Existing folders are
adopted as-is; relocating a project's files to match the layout follows supervision's migration rule — ask the
user, recommend the move (`viber` skill → `references/supervision.md` 5.3).

---

## 3. Step 2 — Mention It in `AGENTS.md`

`init` makes sure the project's `AGENTS.md` has a **Viber section** that points to the registry. This section is
also the **activation marker** for Viber supervision (see `viber` skill → `references/supervision.md`): when it is present, participating
Skills' relocatable output is rerouted under `.viber`.

```markdown
## Viber

- This project follows Viber. The registry of every registered Skill (Viber and <USERNAME>'s Deck) is at
  `.viber/registry.md` in this project. Read it before suggesting or choosing a Skill.
- The project's conversational memory is at `.viber/memory.md` (open questions), `.viber/settled.md`
  (answered questions), and `.viber/learnt.md` (learned facts). Read them before re-asking or re-deciding.
- Project adaptations (attached deck Skills and project Skills) are recorded below by `adapt`.
```

- **`AGENTS.md` exists:** `init` adds the Viber section, or refreshes it if it is already there. Nothing else in the file is touched.
- **`AGENTS.md` does not exist yet:** `init` creates it with only the Viber section. The rest of the file is written later by `agents-md`, which is a mandatory step of Phase 1.

`agents-md` owns `AGENTS.md` and its format. `init` owns the registry pointer in the Viber section; `adapt` owns the adaptations recorded under it.

---

## 4. Step 3 — Start the Flow

### 4.1. New Project

When the project has no lifecycle outputs yet, `init` starts Phase 1 — Idea & Understanding — with its first step, `idea-md`.

### 4.2. Existing Project

When the project already has work in it — documents, a prototype, code — `init` does not start from the beginning and does not assume anything is finished.

1. It looks for the expected output of every lifecycle Skill.
2. An output that exists is marked **Needs Review**, not Completed. A file existing does not prove its Skill ran correctly or that the output is still valid.
3. An output that is missing is marked **Not Started**.
4. The Router then names the first mandatory step that is not Completed as the next step, and suggests reviewing the outputs marked Needs Review.

### 4.3. Suggestions at the Start

Using the registry, `init` can also point out Skills from the user's deck that fit this project, and Opensource Deck Skills found with `find-skills` or a web search. For example, `seo` for a public marketing website, never for an internal admin console. More than one suggestion is fine when each one is relevant. Suggestions are not part of the lifecycle and are never required.

### 4.4. Starting the Step

Running `/viber init` is the user's go-ahead to begin. `init` shows where the project stands and which step comes next, then starts that step. From that point on the Router guides the work, as described in the Router document.

---

## 5. Rules

- **Read-only on Skills.** `init` reads the user's Skills; it never edits, moves or installs them.
- **Index, not copy.** The registry holds names, one-line purposes, when-to-use and source paths, never Skill bodies.
- **Project-local state.** The registry and the memory files live in `<project-root>/.viber/`, visible to the user; nothing is written to a user-home folder.
- **Never assume completion.** Existing outputs are Needs Review until verified.
- **Extending is the user's choice.** `init` adds an extension repository to the deck only when the user asks for it.
- **Safe to repeat.** Running `init` again refreshes; it does not reset the project or erase its history.
- **No secrets.** Nothing private from Skill sources or the project is written into the registry or the memory files.
- **Supervision umbrella.** `init` reads each Skill's `viber` tag and asks about deck exclusions; under supervision, participating Skills' relocatable output goes to `.viber` (see `viber` skill → `references/supervision.md`).

---

## 6. Flow

The init flow is diagrammed in [`init-flow.mmd`](../assets/diagrams/init-flow.mmd): understand the deck (scan · classify · registry · exclusions · memory files) → mention it in `AGENTS.md` → start the flow.

---

## 7. Open Items

1. The exact format of the Router's project-level progress state, which lives beside the registry and memory
   in `<project-root>/.viber/` (see the Router document, section 8). The location is decided; the file format
   is chosen from the surrounding project tooling.
