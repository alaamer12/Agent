# structure

> This document defines the `structure` steering folder: how the project is organized and where each kind of thing is defined. It lives exclusively in the **tech tier** (`tech/structure/`); see [`index.md`](index.md) for the taxonomy overview.

**Holds.** The static technical shape of the project: monorepo boundaries, package boundaries, directory trees, file placement conventions, and naming rules for folders and files. It answers where things live and how directories are arranged.

**Does not hold.**
- Business domain concepts, module breakdowns, or product functional areas (which belong in [`domain.md`](domain.md) or [`capabilities.md`](capabilities.md)).
- What technologies are used ([`stack.md`](stack.md)).
- How components behave at runtime (the steering function folder, [`function.md`](function.md)).
- Data schemas, table columns, or API route payloads (which belong in reference documentation outside the taxonomy).
- In-code identifier naming (variables, types, classes), which belongs in coding standards or linter configurations outside the taxonomy.

**The test.** Does it describe static file/directory layout and code organization?
- *"Where do UI views live versus UI components?"* -> `tech/web/structure/client-tree.md`
- *"How are shared backend packages split from application workspaces?"* -> `tech/shared/structure/repo-layout.md`
- *"What entities exist in the business domain?"* -> `perception/shared/domain/`

**Anti-Assumption Rule.** An agent must never unilaterally guess or invent directory layouts. The technical structure must be confirmed with the user via a decision round (or reflect actual files in the repository).

**Example (`tech/web/structure/client-tree`).**
```text
apps/web/src/
  pages/        Route-level entry components
  views/        Composite layout views
  components/   Reusable visual widgets
  stores/       Client state containers
```
