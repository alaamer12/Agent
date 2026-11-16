## Skill types

This catalog uses three composition types. **A skill's entrypoint is its own `SKILL.md`; a folder name or its depth in the repository does not make it a skill.** Type describes what a skill contains, not where it is stored or which slash command an agent exposes.

### Why the type matters

`SKILL.md` is the unit everything else keys on. The type therefore decides concrete consequences, not labels:

| Consequence | What the type decides |
|---|---|
| Catalog rows | One row per `SKILL.md` in [_Docs/quick-index.md](quick-index.md) / [_Docs/skill-details.md](skill-details.md); battery modules get none. |
| Versioning | Each `SKILL.md` carries its own `version:`; modules have no frontmatter and ride the battery's version. |
| Change tracking | `manager.py lint` compares file hashes per skill; inside a battery every module edit reports as a change to the battery. |
| Installation | Junctions/install records reference `SKILL.md` directories. A battery installs as one unit; each meta-child needs its own install to be invocable — nesting does not install. |
| What an agent loads | Only the invoked `SKILL.md` plus what it routes to. A router entrypoint stays short ([skill-length.md](skill-length.md)); depth lives behind links (progressive disclosure). |
| Lint scope | Description cap, `specialized`, `name`/folder match, command/mode `argument-hint` ([argument-hint.md](argument-hint.md)), and link checks apply per entrypoint; modules inherit the battery's metadata. |

| Type | Root entrypoint | Functional children | Independent skill boundaries |
|---|---|---|---|
| **Meta-Skill** | `<meta-skill>/SKILL.md` | Sub-skills, each with its own `SKILL.md` | The parent and each sub-skill have separate entrypoints |
| **Battery-Skill** | `<battery-skill>/SKILL.md` | Internal modes/modules without their own `SKILL.md` | Only the battery is an independent skill |
| **Skill** | `<skill>/SKILL.md` | Supporting material, not a collection of sub-skills or internal methods | Only the skill itself |

The deciding question is one: **could each piece be wanted, installed, versioned, and invoked on its own?** If yes — separate `SKILL.md` files (Meta-Skill, or plain siblings). If no — one entrypoint with internal methods (Battery-Skill). If there are no pieces at all, just supporting material — plain Skill.

### Meta-Skill: compose independent sub-skills

The parent routes work to sub-skills. Each functional child carries its own skill instructions and metadata, so it can be identified and used as a skill in its own right. Its own composition can again be a Skill, Battery-Skill, or Meta-Skill. Separate slash-command exposure depends on the host agent; it is not the classification test.

```text
meta-skill/
  SKILL.md
  first/
    SKILL.md
    references/
  second/
    SKILL.md
    scripts/
```

Inventory and lint include each actual child entrypoint, with its nearest owning skill recorded as its parent. The child keeps its own catalog row, its own `version`, and its own install record — and can be invoked without the parent if the host exposes it.

Example: [`styling`](../Groups/Design/Style/styling/SKILL.md) hosts the independent children [`scss`](../Groups/Design/Style/styling/specialized/scss/SKILL.md) and [`tailwind`](../Groups/Design/Style/styling/specialized/tailwind/SKILL.md) — each separately invocable and separately installed, while `styling`'s own `build`/`retrofit` methods stay internal. That hybrid is why `styling` carries a `lint-accept: mixed-composition` entry — see [specialization.md](specialization.md) and [lint-accept.md](lint-accept.md).

**Use Meta-Skill only when the children are genuinely wanted apart.** The workshop's measured history runs the other way: meta trees were consolidated because every child frontmatter, version row, catalog row, and install junction cost tokens and bookkeeping without buying independence — `dbug`'s seven sub-skills became one normal skill, `type-up`+`tier-up` became the `typing` battery, the three page-map skills became `pages`, `styleup` folded into `styling`, four design skills became `design`, and `animation`'s three sub-skills became its internal methods on 2026-11-16.

### Battery-Skill: one skill, several internal methods

The root owns the shared rules and dispatches to internal methods. Those methods are parts of the battery, not separately installable skills: a `method.md`, `README.md`, or other internal guide does not substitute for a child `SKILL.md` — a nested `SKILL.md` would create a ghost skill the inventory counts whether anyone meant it or not.

```text
battery-skill/
  SKILL.md
  first-mode/
    method.md
    references/
  second-mode/
    method.md
    assets/
```

The router's `description:` absorbs every method's triggers — the battery is the only thing an agent can match on, so a user phrasing that belongs to one method must fire the parent. Internal methods do not receive independent catalog rows, versions, or installation records; change tracking belongs to the containing skill. Links between files inside one battery use relative paths freely; links across skills never do (installed junctions break them — the rule lives in [specialization.md](specialization.md)).

Examples: [`animation`](../animation/SKILL.md) routes `life`, `ascii`, and `svg` methods behind the single `/animation` address; [`design`](../design/SKILL.md) contains `design-md`, `playfile`, `prototype`, and `calibrate`; [`pages`](../Groups/Design/pages/SKILL.md) contains `main`, `secondary`, and `complementary`; [`typing`](../typing/SKILL.md) contains `harden` and `tiers`.

**Choose Battery when** the methods always travel together, the domain wants one invocation address, and the tree still benefits from per-method folders for progressive disclosure.

### Skill: one method with supporting material

A normal skill can have many files and folders. References, examples, scripts, assets, and templates support its method; their presence alone does not make it a battery. Several commands or a routing table alone also do not establish separate module boundaries.

```text
skill/
  SKILL.md
  references/
  examples/
  scripts/
  assets/
```

Example: [`techstack`](../techstack/SKILL.md) uses references, examples, and templates without making those directories independent skills or internal modes.

### Converting between types

The moves are mechanical and the manager verifies them; animation's meta→battery flip is the worked case:

**Meta-Skill → Battery-Skill** (the pieces turn out never to be wanted apart):

1. `git mv <parent>/<child>/SKILL.md <parent>/<child>/method.md` — the content survives untouched.
2. Collapse the child frontmatters into the parent `SKILL.md`: one merged trigger-first `description` (measure it — the 1024 cap is real), one `argument-hint` covering the modes, one `version` bump sized as a merge (major).
3. Rebase pointers: where a module file is the routing hub its references point at, `../SKILL.md` becomes `../method.md`; child `specialized`/`compatibility`/`license` frontmatter is dropped, and what still matters is carried as prose in the method or a router note.
4. Remove orphan installs of the retired children (`manager.py find <child>` first — if only the registry knew them, there is nothing to clean).
5. Regenerate the `_Docs/` catalog rows, update the README counts, and verify: `report <parent> --json` shows `battery-skill` with the modules listed and no issues, and `lint --strict --readme` passes.

**Battery-Skill → Meta-Skill** (a module earns independence): give the module a real `SKILL.md` with full frontmatter, its own install junction, and a catalog row; keep cross-skill references as name pointers. If the parent keeps internal modules too, record the hybrid with `lint-accept` rather than deleting anything. Adding a *technology-bound* child follows the specialized-skill procedure in [specialization.md](specialization.md).

### Groups, support folders, and mixed structures

- **Groups are organization, not a fourth skill type.** `Groups/Design/` has no entrypoint of its own. Moving a skill into a group does not change its type or make it a sub-skill.
- **Support names are contextual.** `references/method.md` is not automatically a battery mode. Conversely, [`assets`](../Groups/Design/assets/SKILL.md) is a real Battery-Skill even though `assets` is a support-folder name, because that directory has its own entrypoint.
- **Structure is evidence, not semantic proof.** The manager infers composition from actual entrypoints and Markdown-backed module directories outside conventional support folders. An unusually named reference collection can resemble a module; inspect the reported child/module paths rather than treating a label as proof that the content is independently usable.
- **Mixed composition needs an explicit correction.** A parent with both independent sub-skills and internal module branches does not cleanly satisfy either composite form. The manager preserves the real sub-skill entrypoints, reports the parent as Meta-Skill, and emits a composition warning. It does not add or delete `SKILL.md` files automatically.
- **Links are installation details, not types.** A symlink, junction, or hard copy can contain any of the three types. A broken link or a database record alone does not prove a live skill exists.

### Inspecting the types

```bash
python manager.py report --sort type
python manager.py report animation design pages techstack --json
python manager.py find design prototype
python manager.py lint --strict --verbose
python -m unittest discover -s _Test
```

`report` includes nested independent skills, type, parent, and composition evidence (`children`, `modules`, and `issues` in JSON). Internal modules are not independent report rows. Per-skill file counts include descendants, while the summary counts unique files to avoid counting a meta-child's files twice. `find` uses the same classification across the registry, agent folders, and recorded `--into` installations. `lint` checks actual skill entrypoints and flags mixed structures; `--strict` makes findings fail the command.

## Author tag

Every registry skill carries a top-level `author:` in its frontmatter - the person or organization that *created* the skill, not whoever edits it now. Skills in this workshop are authored by `Amr`. Favors (`Groups/Favor/`) keep their real creator, e.g. `ui-taste` -> `author: "UIZZE <business@uizze.com>"`; when the creator is unknown the tag stays present without a value. Battery modules have no frontmatter, so they inherit the battery's author. The tag travels with the skill on install and copy.
