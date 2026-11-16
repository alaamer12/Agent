# Viber Supervision — The Umbrella Mode

> Viber supervision: activation, participation, and the rerouting rule that gathers relocatable knowledge under `.viber/`. The layout it defers to is `structure.md`.

## 1. Overview

Viber Supervision is the mode in which **Viber owns the project's engineering-discipline artifacts**. When it is
active, the documentation and procedure outputs of every participating Skill are gathered under the project's
`.viber` directory, while the project's code and its root-files stay where they are.

The idea is **disciplined vibe-engineering**: the freedom of vibe coding, with the discipline of a single,
visible umbrella over everything the project decides, specifies, and learns. Viber does not touch the code; it
organizes the knowledge around the code.

This document defines four things:

1. **Activation** — how an agent knows Viber supervision is on (section 2).
2. **Participation** — which Skills fall under the umbrella (section 3).
3. **The frontmatter tag** — how a Skill declares its eligibility (section 4).
4. **The rerouting rule** — where a participating Skill's output goes (section 5).

### Core Principle

**Viber owns what can be relocated; it never moves what must stay at the root, and it never touches code.**

A Skill's relocatable artifact (a spec, a steering doc, a prototype, a plan) goes under `.viber`. A root-file
(`README.md`, `AGENTS.md`) and production code stay at the project root. The test is not a fixed list — it is a
question: *must this live at the root to function or by convention?* If yes, it stays; if it can be relocated
and still work, it goes under the umbrella.

---

## 2. Activation — How the Agent Knows

Viber supervision is active when the project's `AGENTS.md` carries a **Viber declaration**. The agent reads
`AGENTS.md` at the start of every session and detects it.

The wording is **flexible** — any clear declaration counts:

- `## Viber` section (the canonical form `init` writes — see `../commands/init.md` section 3).
- "This project uses Viber."
- "Vibe Mode On."
- any equivalent sentence that states the project follows Viber.

The canonical `## Viber` section is preferred because it also points to the registry and the memory files. But
the agent recognizes the intent, not one exact string. When no Viber declaration is present, supervision is
**off**: Skills write to their normal paths, and nothing is rerouted.

`init` ensures the declaration exists (it adds or refreshes the `## Viber` section). Turning supervision off is
the user's decision — removing the declaration — never something the agent does on its own.

---

## 3. Participation — Which Skills Are Under the Umbrella

**Deck membership is the gate.** A Skill that is in the user's deck (registered) falls under Viber's umbrella by
default — **even if it carries no frontmatter tag**. This is what lets deck Skills, not only Viber's own
lifecycle Skills, participate without being rewritten.

A Skill is under the umbrella when **all** of these hold:

1. Viber supervision is **active** (section 2).
2. The Skill is **in the deck** — a registered Skill (global or project-level) or an extension-source Skill.
   Viber's own lifecycle Skills always participate; they are Viber.
3. The Skill is **not excluded** by the user (section 3.1).
4. The Skill is **not tagged `viber: separated`** (section 4).

An untagged deck Skill participates (default `part`). A Skill **outside the deck** — an Opensource Deck Skill
used one-off, not registered — is **not** under the umbrella's guarantee until it is registered or attached via
`adapt`.

### 3.1. `init` Asks About Exclusions, and States the Consequence

Because deck membership decides participation, `init` **asks the user** whether any deck Skills should be
excluded from the umbrella, and **clarifies the consequence** of each choice:

| Choice | Consequence |
|---|---|
| **In the deck / under the umbrella** | Viber reroutes the Skill's relocatable output into `.viber`, and remembers it (the memory files, the Router's tracking). The Skill's work is part of the project's disciplined record. |
| **Excluded / out of the deck** | Viber does **not** guarantee control or always-remembering. The Skill writes to its normal path; its output is not gathered under `.viber` and not tracked as part of the umbrella. |

The user decides per Skill. `init` records the exclusions in the registry (section 4 of `../commands/init.md`) so the
Router and every later session honor them. Excluding a Skill is never silent — the consequence is stated first.

---

## 4. The Frontmatter Tag

Every Skill that Viber uses declares its eligibility with a frontmatter tag in its `SKILL.md`:

```yaml
---
name: <skill-name>
description: <...>
viber: part        # or: separated
---
```

| Value | Meaning |
|---|---|
| `viber: part` | The Skill can join the umbrella. Its relocatable output is rerouted when supervision is active. |
| `viber: separated` | The Skill stays independent. Its output is **not** rerouted, even if it is in the deck — for Skills that operate outside the project's discipline (e.g. a Skill that writes the user's global config). |
| *(no tag)* | Treated as `part` **if the Skill is in the deck**. Deck membership, not the tag, is the primary gate. |

The tag is a Skill's self-declaration; deck membership and the user's exclusions are the operative controls.
`init` reads the tag as metadata (it reads only the top of `SKILL.md`, never the body) and records it in the
registry. The tag never overrides a user exclusion, and a `separated` tag opts the Skill out regardless of deck
membership.

**Examples:**

```yaml
# steering — produces project specs; joins the umbrella
viber: part
```
```yaml
# personalize — writes the user's GLOBAL instructions, not this project's artifacts
viber: separated
```

---

## 5. The Rerouting Rule — Where Output Goes

When supervision is active and a Skill participates, its **relocatable artifacts** are written under `.viber`,
preserving the path they would normally have relative to the project root:

```text
<normal-path>  →  .viber/<normal-path>
```

| Skill output | Normal path | Under Viber |
|---|---|---|
| steering docs | `docs/steering/…` | `.viber/docs/steering/…` |
| feature docs | `docs/features/…` | `.viber/docs/features/…` |
| reference schema | `docs/reference/…` | `.viber/docs/reference/…` |
| prototype | `prototype/…` | `.viber/prototype/…` |
| a plan | `docs/plans/…` | `.viber/docs/plans/…` |

The path is preserved, not flattened: `.viber/docs/steering/tech/shared/stack/platform.md`, not
`.viber/platform.md`. The umbrella mirrors the project's knowledge layout inside `.viber`.

### 5.1. The Root-File Test (what stays)

Before rerouting an artifact, ask: **is it a root-file or code?**

- **Root-files stay at the project root.** `README.md` and `AGENTS.md` are root-files — they are conventionally
  and functionally anchored at the root (the harness loads `AGENTS.md` from there; `README.md` is the repo's
  front door). Moving them into `.viber` would break that. They are **never** rerouted.
- **Production code stays.** Code directories — whether **flat** (code lives directly in the project, not
  grouped under a single folder) or under `src/` (or any group directory) — are outside Viber's control. Viber
  never moves or reroutes code.
- **Layout homes come first.** The canonical layout (`structure.md`) assigns fixed homes that sit outside
  the umbrella by design: run output goes to `artifacts/<producer>/`, the agent's temporary work to
  `scratch/<task>/`, utilities and operations to `tools/` and `scripts/`.
- **Relocatable knowledge goes under `.viber`.** A prototype is *not* a root-file: `prototype/` works just as
  well at `design/prototype/`, so it is relocatable and goes under the umbrella. The same for specs, steering,
  plans, flows, and design artifacts — any knowledge with no other layout home.

The test is the principle, not a memorized list: *must this live at the root, is it code, or does the layout
give it a home (`artifacts/`, `scratch/`, `tools/`, `scripts/` — see `structure.md`)?* If any of those hold,
it goes there. Relocatable knowledge with no other home → `.viber`.

### 5.2. How the rerouting is applied

The rerouting is a convention the **agent applies when driving a Skill** under supervision; the Skill itself
need not be Viber-aware. The agent checks the registry (does this Skill participate?) and the root-file test
(is this artifact relocatable?), then writes the artifact to `.viber/<normal-path>`. This is how deck Skills
join the umbrella without modification.

### 5.3. Turning Supervision On Over an Existing Project

When supervision is activated for a project whose relocatable artifacts already sit at the root (an existing
`docs/`, for example), Viber does not move them silently and does not leave the choice undeclared: it **asks
the user**, and **recommends moving them under `.viber`** — one umbrella over the project's knowledge is the
point. Declining is fine: the artifacts stay where they are, and the rerouting rule governs future output.

The same pattern settles every case supervision flags as ambiguous — an unclear exclusion, or an artifact that
is partly code and partly documentation (a codegen Skill): Viber **asks the user and recommends the `.viber`
placement** for the relocatable part, and records the choice. Never a silent auto-move, never a silent skip.

---

## 6. What Viber Owns, and What It Does Not

| Under the umbrella (`.viber/…`) | Stays at the project root |
|---|---|
| Steering docs (perception + tech) | `AGENTS.md` (the marker + rulebook) |
| Feature docs, reference schemas, plans | `README.md` (the repo front door) |
| Prototypes and design artifacts | Production code — flat or `src/` (any layout) |
| The memory files (`memory.md`, `settled.md`, `learnt.md`) | |
| The registry (`registry.md`) and Router state | |

Viber owns the **knowledge around the code**, never the code itself. The full canonical layout — `tools/`,
`scripts/`, `artifacts/`, `scratch/`, and the git treatment of each — is `structure.md`; its section 6 maps
supervision's outputs to their homes.

---

## 7. How It Connects

| Component | Relationship to Supervision |
|---|---|
| `init` | Ensures the AGENTS.md declaration; reads the `viber` frontmatter tag; asks about deck exclusions and states the consequence; records participation in the registry; creates the `.viber` directory. |
| **Router** | Reads the declaration (is supervision active?) and the registry (which Skills participate?). When driving a participating Skill, applies the rerouting rule to its relocatable output. |
| `lifecycle` | Every lifecycle Skill participates; its outputs land under `.viber` when supervision is active. |
| `memory` | The memory files already live under `.viber`; they are the umbrella's conversational ledger (see `memory.md`). |
| `adapt` | Attaching a deck Skill to the project brings it under the umbrella; a Skill created by `adapt` declares its `viber` tag. |
| `structure` | The canonical layout gives run output (`artifacts/`), agent temp (`scratch/`) and utilities/operations (`tools/`, `scripts/`) fixed homes outside the umbrella; supervision reroutes only knowledge without a layout home (see `structure.md` section 6). |
| `agents-md` | Owns `AGENTS.md` (a root-file, never rerouted); the Viber declaration lives there. |

---

## 8. Rules

- **Code is never touched.** Viber reroutes knowledge artifacts only; production code (flat or `src/`) stays.
- **Root-files stay.** `README.md` and `AGENTS.md` are never rerouted.
- **Relocatable artifacts go under `.viber`**, preserving their relative path.
- **Layout homes win over the umbrella.** `artifacts/`, `scratch/`, `tools/`, `scripts/`, root-files and code keep their canonical placement (`structure.md`); `.viber` gathers the remaining relocatable knowledge.
- **Deck membership is the gate.** In-deck Skills participate by default, even untagged; out-of-deck Skills are
  not guaranteed.
- **Exclusions are explicit.** `init` asks and states the consequence; an exclusion is recorded, never silent.
- **The tag declares, the deck decides.** `viber: separated` opts a Skill out; an untagged deck Skill is `part`.
- **Activation is the user's.** Supervision is on when `AGENTS.md` declares it; the agent never turns it off.
- **Flagged items are asked, not assumed.** On migration and on ambiguous artifacts, Viber asks the user and recommends the `.viber` placement, then records the choice (section 5.3).
- **No secrets.** Nothing private is written into the registry or the rerouted artifacts' index.

---

## 9. Boundaries

### Supervision SHOULD

- Detect the Viber declaration in `AGENTS.md` at session start.
- Reroute participating Skills' relocatable artifacts to `.viber/<normal-path>`.
- Apply the root-file test before moving anything.
- Honor deck membership, the `viber` tag, and the user's recorded exclusions.
- Keep the code and root-files untouched.

### Supervision SHOULD NOT

- Move or reroute production code, `README.md`, or `AGENTS.md`.
- Reroute a Skill that is excluded, `separated`, or out of the deck.
- Flatten the path — the relative layout is preserved inside `.viber`.
- Turn itself off, or assume supervision is on without a declaration.
- Require a Skill to be rewritten to participate — the agent applies the umbrella.
- Guarantee control or memory for a Skill outside the deck.

---

## 10. Flow

The supervision decision path is diagrammed in [`diagrams/supervision-flow.mmd`](../diagrams/supervision-flow.mmd): declaration → participation → the root-file test → `.viber` or root.

---

## 11. Open Items

1. **Exclusion UX.** The exact form of `init`'s exclusion question (per-Skill prompt vs a single list) and how
   exclusions are revisited on a later `init`.

Resolved: migration asks the user and recommends `.viber` (section 5.3); mixed code-and-doc artifacts split
per artifact, the doc part under the umbrella, the code part at root, ambiguity asked.