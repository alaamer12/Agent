# Agent Skills Catalog

The inventory skills system of this workshop — a collection of modular Agent Skills developed by **Amr**. Each skill provides specialized domain instructions, operational workflows, patterns, and best practices for agents; [`manager.py`](manager.py) inventories, lints, versions, and installs them.

Total active skills: **122** — 36 standalone at the repository root and the rest organized under 16 topic groups. 29 archived skills are catalogued in [`_Docs/archive.md`](_Docs/archive.md).

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
python manager.py skill <name>...           # install one or more skills into the agent folders
python manager.py skill --remove <name>...  # uninstall them wherever deployed: links, junctions, tracked copies (agent folders or --into)
python manager.py agents                   # list code-agent locations from the agents table (defaults seeded on first use)
python manager.py agents --inventory       # every skill installed in each agent folder, with kind and source
python manager.py claim <X> <Y>            # claim X into Y: Y ends with X's skill set (default override: replace shared, add missing, remove Y's managed extras; unmanaged folders are protected unless --force)
python manager.py claim <X> <Y> --append   # only add what Y lacks; existing Y entries are never touched (deduped by name)
python manager.py skill --remote URL <name...>  # install skill(s) fetched from a remote git repo (https/ssh/git@/local repo); registers the remote, clones into the manager cache, deploys from it
python manager.py remote                   # list registered remotes: url, subpath, ref, skill count, last fetch
python manager.py remote --add URL [-n NAME] [-p SUBPATH] [--ref REF]  # register + fetch without installing; conflicts need --force
python manager.py remote --update          # re-fetch all remotes (git fetch --depth 1, reset to the tracked ref); names narrow it
python manager.py remote --remove NAME     # unregister and delete its cache; warns which agent links point into it
python manager.py lint --remote          # also lint every skill found in the registered remotes
python manager.py report --remote        # include remote skills in the inventory (their own git state shown)
python manager.py find <name> --remote   # search remotes too: a remote skill resolves even if absent from the registry
python manager.py interactive            # arrow-key multi-select checklist: toggle which skills stay installed (space toggles, typing filters, ctrl-a all, ctrl-i invert, enter plans) - shows the install/uninstall plan and applies nothing until you confirm; --no-tui falls back to a numbered prompt
python manager.py agents --set NAME --skill-dir PATH [--md-path PATH ...]  # register or update an agent; conflicting values error unless --override
python manager.py agents --remove NAME     # unregister an agent (a seeded default stays unregistered until re-set)
```

To add or move a skill, update the catalog data in `_Docs/` (regenerate or edit `quick-index.md` / `skill-details.md` / `archive.md`), then verify with `lint --strict --readme`.
