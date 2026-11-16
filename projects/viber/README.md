# Viber

Disciplined vibe-engineering. A lifecycle regime that governs how agents design, build, and maintain projects — from first idea through post-production.

This repository is the independent source for the Viber skill suite: the design drafts that shape it and the shipped skills that agents execute.

## Where to start

| You want to… | Go to |
|---|---|
| Understand the lifecycle and its phases | [docs/regime/lifecycle.md](docs/regime/lifecycle.md) |
| See how skills are routed and selected | [docs/regime/router.md](docs/regime/router.md) |
| Understand the supervision umbrella | [docs/regime/supervision.md](docs/regime/supervision.md) |
| See the canonical project layout Viber enforces | [docs/regime/structure.md](docs/regime/structure.md) |
| Understand the memory ledger | [docs/regime/memory.md](docs/regime/memory.md) |
| Read a command's design spec (init / compact / flow) | [docs/commands/init.md](docs/commands/init.md) · [docs/commands/compact.md](docs/commands/compact.md) · [docs/commands/flow.md](docs/commands/flow.md) |
| See what agents actually execute | [skills/](skills/) — each subfolder is an installable skill |
| Understand how drafts become shipped skills | [PIPELINE.md](PIPELINE.md) |
| Install the full suite | `cd F:/Projects/Agent/skills/insource && python manager.py viber` |
| Browse all design docs | [docs/index.md](docs/index.md) |

## Structure

```
viber/
├── docs/          design drafts — provisional, iterated, grilled
├── skills/        shipped agent skills — lean, imperative, installed via symlink
├── viber.json     manifest: every skill the lifecycle walks, tagged by phase
└── PIPELINE.md    the draft → settle → promote → ship workflow
```

## Relationship to insource

Viber owns its five skills (`viber`, `vinit`, `vcompact`, `vflow`, `adapt`). The deck skills it references (steering, architecture, agents-md, etc.) remain in the insource registry at `F:/Projects/Agent/skills/insource/Groups/Viber/` and are resolved by name at install time. The manifest's `FULL CODE` group entry points back into insource's `Groups/Code`.

Installation is still driven by insource's `manager.py viber` command, which reads this project's `viber.json` via a relative path. No separate installer is needed.

## Status

The project is in [DR] Draft / [IP] In-Progress. Design docs are provisional (thaw posture applies). Shipped skills are functional and installed. Post-production [PP] begins at first real release.