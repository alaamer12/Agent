# Migrating Legacy Documentation

> This document establishes constraints and a starting map for migrating legacy technical, structural, and product documentation into the **Two-Tier Steering Taxonomy**. See [`index.md`](index.md) for the master index.

The migration of legacy documentation is conducted as a **one-time full migration** adhering to the following non-negotiable constraints:

- **Keep the originals**: Never delete legacy source documents. Retain them in place or archive them to a dedicated archive directory (e.g. `docs/archive/legacy/`), stating the chosen location explicitly.
- **Move, do not rewrite**: Migrate passages into their canonical homes without introducing unrequested textual edits.
- **Passage-level evaluation**: A legacy document that mixes business concepts with technical mechanisms must be split by passage (using the Tier Test and Golden Rule in [`placement.md`](placement.md)) before placing.
- **Handle conflicts openly**: If two legacy sources disagree, retain both, document the source of each, and flag the contradiction for maintainer resolution. Never pick one silently.
- **Source-to-destination accounting**: Maintain an exhaustive mapping ledger during migration to guarantee that every passage is accounted for with zero accidental duplications.
- **No empty or silent placeholders**: Create files only when real, verified content exists. If later drafting reveals an unanswered question, disclose it immediately and use the structured `Pending (Drafting)` marker from [`documentation-conventions.md`](documentation-conventions.md#drafting-open-topic-lifecycle), never a bare placeholder.
- **Interview before technical placement**: Migration is not an exemption from the [Tech Directory Interview and Authoring Gate](documentation-conventions.md#mandatory-tech-directory-interview-and-authoring-gate). Inspect legacy technical claims as evidence, ask each target directory's mandatory questions, and obtain a user-confirmed decision recap before writing its mapping or migrated content.
- **Preserve structural patterns, not just paths**: Label migrated trees as observed current snapshots, approved targets, or illustrative examples. For growable groups, retain or add `...` plus a compact membership/extension rule; never freeze an old inventory or turn an example path into a mandate.
- **Minimalist shared, local delta**: Apply the [Universal Scope Test](layout.md#universal-scope-test) to every candidate shared passage. Keep only universal canonical facts in `shared/`; in the migrated steering copy, replace repeated area prose with a link to the shared owner plus the area's delta. Preserve the untouched legacy originals and record each deduplication in the mapping ledger.
- **No migration tombstones**: In living steering files, state current content and ordinary references only. Never write `Moved to`, `retired`, or assumption labels; replace wrong living text directly and keep genuine history only in its explicit historical home.

Preserve conflicting legacy sources and their provenance, but do not silently choose a side or document a proposed resolution as settled. A target directory stays **Blocked** until the user resolves the contradiction or explicitly narrows the migration scope to exclude it.

---

## Suggested Starting Map for Two-Tier Migration

In this map, `<area>` means `shared` only after the [Universal Scope Test](layout.md#universal-scope-test) passes; otherwise substitute the concrete owning area. The destination column selects a concern folder, not a scope.

| Legacy Section / Content | Destination Tier & Folder | Why |
| :--- | :--- | :--- |
| Product purpose, audience summary, business goals | `perception/<area>/product/` | Core product-level overview |
| Entity definitions, roles, lifecycles, structural vocabulary | `perception/<area>/domain/` | Nouns and relationships |
| Business functional capabilities across features | `perception/<area>/capabilities/` | What the platform provides |
| Business rules, entitlements, governance limits | `perception/<area>/policy/` | Allowed / forbidden constraints |
| Single feature specifications | `docs/features/<feature>.md` | Outside taxonomy (single feature scope) |
| Relational table schemas and API endpoint references | `docs/reference/` | Outside taxonomy (reference documentation) |
| Tool rosters, languages, databases ("We use X") | `tech/<area>/stack/` | Tools in use |
| Code layout, monorepo packages, directory trees | `tech/<area>/structure/` | Static project organization |
| System-wide technical runtime mechanisms | `tech/<area>/function/` | Steering function folder |
| Engineering guidelines and technical mandates | `tech/<area>/doctrine/` | Mandates for a specific technical part |
| Step-by-step operational setup or run recipes | `tech/<area>/playbook/` | How to operate a task |
| General developer setup and command guides | `AGENTS.md` / `CONTRIBUTING.md` | Outside taxonomy (general project guidance) |
