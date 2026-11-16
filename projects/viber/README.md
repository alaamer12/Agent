# Viber

Disciplined vibe-engineering. A lifecycle regime that governs how agents design, build, and maintain projects — from first idea through post-production.

This repository is the independent source for the Viber skill suite: the design drafts that shape it and the shipped skills that agents execute.

## Where to start

| You want to… | Go to |
|---|---|
| Understand the lifecycle and its phases | [docs/lifecycle.md](docs/lifecycle.md) |
| See how skills are routed and selected | [docs/router.md](docs/router.md) |
| Understand the supervision umbrella | [docs/supervision.md](docs/supervision.md) |
| See the canonical project layout Viber enforces | [docs/structure.md](docs/structure.md) |
| Understand the memory ledger | [docs/memory.md](docs/memory.md) |
| Read a command's design spec (init / compact / flow) | [docs/init.md](docs/init.md) · [docs/compact.md](docs/compact.md) · [docs/flow.md](docs/flow.md) |
| See what agents actually execute | [skills/](skills/) — each subfolder is an installable skill |
| Understand how drafts become shipped skills | [PIPELINE.md](PIPELINE.md) |
| Install the full suite | `cd F:/Projects/Agent/skills/insource && python manager.py viber` |
| Browse all design docs | [docs/README.md](docs/README.md) |

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