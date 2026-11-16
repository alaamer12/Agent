# _Docs — Documentation Index

The catalog data split out of [README.md](../README.md) on 2026-11-16. The README stays the slim entry point; everything it used to carry lives here. `manager.py lint --readme` checks these files against the skills on disk.

| File | What it holds |
|---|---|
| [skill-types.md](skill-types.md) | The three composition types (Meta-Skill, Battery-Skill, Skill), groups and support folders, how to inspect types. |
| [specialization.md](specialization.md) | The `specialized` frontmatter: meaning, naming conventions, and how to add a specialized skill to a battery. |
| [lint-accept.md](lint-accept.md) | `lint-accept` frontmatter: waiving an intentional lint finding with a recorded reason, rule ids, behavior. |
| [argument-hint.md](argument-hint.md) | The command/mode → `argument-hint` declaration rule: what the detector counts, what it ignores, how to waive a misfire. |
| [skill-length.md](skill-length.md) | The under-200-lines `SKILL.md` rule, the solo-file exemption, and the `report` solo flag. |
| [crossreferences.md](crossreferences.md) | `manager.py crossreference` (skill-to-skill mention graph) and `manager.py agent` (deploying `_Resources/AGENTS.md`). |
| [quick-index.md](quick-index.md) | Quick Index: one bullet per top-level skill, grouped by category. |
| [skill-details.md](skill-details.md) | Skill Details: path, description, use-case, usage, parent/sub-skills per skill, nested skills included. |
| [archive.md](archive.md) | Archived skills under `_Archive/`, kept for reference, not linked or synced. |
