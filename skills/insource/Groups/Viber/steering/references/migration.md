# Migrating the legacy docs

> This document sets the constraints and a starting map for the one-time move of the old tech / structure / product docs into the steering taxonomy. Where each destination folder is defined, see the [index](index.md); how to choose between two folders is in [placement.md](placement.md).
> **Terminology reminder.** The steering folder whose directory name is `function` is always called the **steering function folder**, never just "function". Full rule: [function.md](function.md).

The old tech / structure / product docs get a **one-time full migration**. The method is left to the agent that performs it. These constraints apply:

- **Keep the originals.** Never delete sources. Leave them in place or move them to an archive path, and say which.
- **Move, do not rewrite.** Each passage lands in exactly one place. A legacy file that mixes roles is split by role first (see the golden rule in [placement.md](placement.md)). If a single passage serves two roles, keep it where it belongs most and link from the other.
- **Handle conflicts openly.** If two sources disagree, keep both, label where each came from, and flag it. Do not pick silently.
- **Keep a source-to-destination map** so nothing is lost, and verify at the end that every passage is accounted for with nothing duplicated by accident.
- **Create only files with real content.** No placeholders.

## Suggested starting map (to be confirmed during migration)

This is a starting suggestion, not a decided mapping. The migrating agent should confirm it against the actual legacy files.

| Old location | Likely destination |
|---|---|
| tech: libraries, frameworks, tools | `stack` |
| tech: code organization | `structure` |
| tech: runtime behavior that spans features | steering function folder |
| tech: behavior of one feature | that feature's own documentation |
| tech: how to run or set up one specific thing | `playbook` |
| tech: general how-to-work guidance (development flow, debugging, commands, environment, versions) | outside this taxonomy |
| tech: guidelines for a specific part or task, with reasoning | `doctrine` |
| tech: binding constraints on a specific part | `doctrine` |
| structure | `structure` |
| product: overall purpose and audience | `product` |
| product: one feature's spec | that feature's own documentation |
