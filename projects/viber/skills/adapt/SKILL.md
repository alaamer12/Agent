---
name: adapt
version: 1.0.0
description: 'Grows a project''s own Viber version. Viber has fixed foundations, but no two projects walk the same path. When the journey needs a capability nothing covers, adapt proves the gap is real by walking a short ladder (a Viber or deck Skill, a project document, an installable Skill, a how-to recipe) and only when every rung fails creates a small project Skill, preferably an extension of the closest existing Skill. Every adaptation is recorded in the Viber section of the project''s AGENTS.md. Never edits the fixed base, never runs what it creates, never creates a Skill where a document, rule or existing Skill would do. Triggers: ''we keep doing this by hand'', ''no skill covers this'', ''this project needs its own skill'', ''adapt''. Not catalog authoring (skill-creator), fixed recipes (how-to-do), the rest of the rulebook (agents-md).'
when_to_use: A need keeps returning that no Skill covers, the same instruction or correction is given repeatedly, a project domain has no owning Skill, a deck Skill should become part of this project's path, or the user asks for a project-specific Skill. Also /adapt.
argument-hint: "[the gap or repeated need - or nothing, to scan the current work for gaps]"
---

# adapt - the project's own Viber version

Viber has a **fixed base** that no project changes: its phases, their order, its mandatory Skills.
Each project adds to it what its own path needs - its **Viber version**, recorded in the **Viber section
of the project's AGENTS.md**, wherever that file lives. The version only adds; it never removes, reorders
or reclassifies anything in the base.

## Where Skills come from

| Source | What it is | How to see it |
|---|---|---|
| **Viber** | The lifecycle's own Skills | The Viber lifecycle |
| **The user's deck** (`<USERNAME>`'s Deck) | Every registered Skill, global or project-level, plus Skill repositories the user chose to add | The Viber registry written by `/viber init` |
| **Opensource Deck** | Every published Skill that is not registered | `find-skills`, a web search |

Registration decides the deck, not authorship: a published Skill joins the user's deck once registered.

Deck Skills are used when the project or task needs them - not every project cares about SEO - so they
are never part of the base. Making one part of *this* project's path is an adaptation.

## Signals of a gap

The same instruction or correction given a second time · the same project-specific judgment reasoned out
again from scratch · a project domain no Skill owns · the same additions made to a base Skill every time ·
a deck Skill needed again and again · the user asks. A signal is a reason to check, not proof.

## The ladder - first rung that holds wins

| # | The need is covered when... | Outcome |
|---|---|---|
| 1 | A Viber Skill or a registered Skill in the user's deck already does the job | **Attach** it to this project at a lifecycle point. Create nothing. |
| 2 | It is a fact, rule or decision, not a procedure | Write it into the document that owns it. No Skill. |
| 3 | A maintained Opensource Deck Skill covers it | Propose installing it, then attach it. |
| 4 | It is a fixed recipe with no judgment | A `how-to-do` procedure. No Skill. |
| 5 | Nothing above holds | **Create a project Skill** - an extension of the closest Skill if one is close, standalone only if none is. |

For each rung that fails, note the evidence ("confirmed absent"). A project Skill earns its place only by
holding **repeatable judgment specific to this project**.

## Procedure

1. Name the gap in one sentence and quote the signal that raised it.
2. Walk the ladder: Viber and the user's deck, then the project's documents, then the Opensource Deck.
3. Propose to the user: the gap, the rung that holds, why the earlier rungs failed, and - when adding a
   Skill - where in the lifecycle it applies and whether it is mandatory or optional for this project.
4. Wait for approval. In an autonomous session (e.g. `iwts`), proceed and report at the end.
5. Write the outcome. A project Skill is one `SKILL.md`, named `<project>-<capability>`. An extension
   opens with "Read `<base Skill>` first and follow it; this adds only:" and never restates the base.
   Facts (schema, formulas, vocabulary) are pointed to, never copied.
6. Record it in the Viber section of AGENTS.md.

## The Viber section of AGENTS.md

One row per adaptation: the Skill, its source (deck or project Skill), lifecycle point, mandatory or
optional here, the gap it closes, the date. Rejected proposals and retired Skills stay as rows too, so a
settled gap is not proposed again without new evidence. `agents-md` owns AGENTS.md and its format; adapt
owns only the content of this section. Project Skills live in the folder this section names (default
`.agents/skills/<project>-<capability>/`), under version control. Installing them into an agent's own
Skills folder is the user's choice; adapt installs nothing.

## Rules

- Never touch the base. If the base itself looks wrong, report it - don't patch around it in one project.
- Creation is the last rung: attach before writing, document before codifying.
- Never invent a need: no gap without a signal, no Skill for a need that has not occurred.
- adapt creates and records; it never runs the Skill it created.
- Retire a project Skill when its need disappears or a deck Skill absorbs it. When a second project needs
  the same Skill, propose promoting it to the user's deck.

## Boundaries

General catalog Skills → `skill-creator` · fixed recipes → `how-to-do` · the rest of the rulebook →
`agents-md` · harvesting a session's work → `bequeath` · making a Skill auto-apply → `theskills`.
