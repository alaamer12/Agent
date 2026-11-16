# Agent Skills Catalog

The inventory skills system of this workshop — a collection of modular Agent Skills developed by **Amr**. Each skill provides specialized domain instructions, operational workflows, patterns, and best practices for agents; [`manager.py`](manager.py) inventories, lints, versions, and installs them.

Total active skills: **118** — 34 standalone at the repository root and the rest organized under 16 topic groups. 29 archived skills are catalogued in [`_Docs/archive.md`](_Docs/archive.md).

> **Refactored 2026-11-16.** This README used to carry the whole catalog (≈1,400 lines). It has been refactored into a slim entry point, and almost all of its data now lives in [`_Docs/`](_Docs/index.md) as separate files. Nothing was dropped — every section moved; the catalog data (Quick Index, Skill Details, Archive) was regenerated fresh from the skills on disk. `manager.py lint --readme` follows the split layout and checks these files against the registry.

## Where everything lives

Full map: [`_Docs/index.md`](_Docs/index.md).

| Document | About |
|---|---|
| [skill-types.md](_Docs/skill-types.md) | Meta-Skill / Battery-Skill / Skill composition types and how the manager inspects them |
| [specialization.md](_Docs/specialization.md) | The `specialized` frontmatter, naming conventions, adding a specialized skill to a battery |
| [lint-accept.md](_Docs/lint-accept.md) | Waiving an intentional lint finding with a recorded reason |
| [skill-length.md](_Docs/skill-length.md) | `SKILL.md` must stay under 200 lines unless it is the skill's only file; the `report` solo flag |
| [argument-hint.md](_Docs/argument-hint.md) | Skills that present commands or modes must declare `argument-hint`; what the detector counts and ignores |
| [crossreferences.md](_Docs/crossreferences.md) | `crossreference` (skill mention graph) and `agent` (instruction deployment) |
| [quick-index.md](_Docs/quick-index.md) | One bullet per top-level skill, grouped by category |
| [skill-details.md](_Docs/skill-details.md) | Path, description, use-case, usage, parent/sub-skills per skill |
| [archive.md](_Docs/archive.md) | Archived skills under `_Archive/` |

## Daily commands

```bash
python manager.py lint --strict --readme   # registry vs README + _Docs must match
python manager.py report --sort type       # per-skill inventory
python manager.py find <name>              # where a skill exists: inventory, agents, installs
python manager.py skill <name>             # install a skill into the agent folders
```

To add or move a skill, update the catalog data in `_Docs/` (regenerate or edit `quick-index.md` / `skill-details.md` / `archive.md`), then verify with `lint --strict --readme`.
