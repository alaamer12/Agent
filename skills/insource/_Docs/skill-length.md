# SKILL.md size limit

**A skill entrypoint must stay under 200 lines — unless it is the skill's only file.**

`SKILL.md` is a router, not the repository of the skill's knowledge. Depth belongs in `references/`, examples, templates, scripts, battery modules, or sub-skills that the entrypoint points at — loaded only when the task needs them (progressive disclosure). A long entrypoint taxes every agent that opens the skill, including those needing one paragraph of it.

The exemption: a **solo-file skill** — one whose directory contains exactly one file, its `SKILL.md`. With nothing to delegate to, the entrypoint is the whole skill, and its length is legitimate: the router would have nowhere to route. Live examples: [`tldr`](../Groups/Talk/tldr/SKILL.md), [`idk`](../Groups/Talk/idk/SKILL.md), [`learning-test`](../learning-test/SKILL.md). The exemption disappears the moment a second file exists: add a `references/` page and the entrypoint must shrink below the limit and link to it instead.

The limit is **200 lines** (a line is a line; no frontmatter discount): at or above it a non-solo skill gets a warning, below it passes.

## What the manager reports

```bash
python manager.py report                        # "SKILL.md only" column: yes marks solo skills
python manager.py report --sort files           # smallest-first: solo skills cluster at 1 file
python manager.py report --json                 # per row: "solo": true/false, plus "files" count
```

In JSON the flag is `"solo"`; the summary counts solo skills so a deck drifting toward monolith entrypoints is visible over time.

## What the manager lints

`python manager.py lint` (and `--strict`) reports `skill-length` on registry skills only — foreign skills installed into agent folders by other sources are not policed, and battery modules carry no `SKILL.md` to check. A meta-child is a real skill: the limit applies to its entrypoint too. The finding reads, e.g.:

```
SKILL.md has 214 lines (limit 200); split depth into references/ or modules
```

Genuinely intentional exceptions are waived with a recorded reason via [`lint-accept`](lint-accept.md):

```yaml
lint-accept:
  skill-length: "Reference tables are the skill's core payload; splitting would add hops for zero token savings."
```

## Fixing a finding

Move prose into the skill's existing support structure, or create it:

| What's long | Where it goes |
|---|---|
| Detailed rules, tables, checklists | `references/<topic>.md`, linked from the entrypoint |
| Worked cases | `examples/<case>.md` |
| Output skeletons | `assets/templates/<name>.md` |
| Modes of a large skill | battery modules (`<mode>/method.md`) or meta children with their own `SKILL.md` — see [skill-types.md](skill-types.md) |

The entrypoint keeps: identity, when to use it, the routing table, and the few laws every reader needs. Target well under the limit, not exactly at it.
