# Migrating Legacy Documentation

> This document establishes constraints and a starting map for migrating legacy technical, structural, and product documentation into the **Two-Tier Steering Taxonomy**. See [`index.md`](index.md) for the master index.

The migration of legacy documentation is conducted as a **one-time full migration** adhering to the following non-negotiable constraints:

- **Keep the originals**: Never delete legacy source documents. Retain them in place or archive them to a dedicated archive directory (e.g. `docs/archive/legacy/`), stating the chosen location explicitly.
- **Move, do not rewrite**: Migrate passages into their canonical homes without introducing unrequested textual edits.
- **Passage-level evaluation**: A legacy document that mixes business concepts with technical mechanisms must be split by passage (using the Tier Test and Golden Rule in [`placement.md`](placement.md)) before placing.
- **Handle conflicts openly**: If two legacy sources disagree, retain both, document the source of each, and flag the contradiction for maintainer resolution. Never pick one silently.
- **Source-to-destination accounting**: Maintain an exhaustive mapping ledger during migration to guarantee that every passage is accounted for with zero accidental duplications.
- **No empty placeholders**: Create files only when real, verified content exists to populate them.

---

## Suggested Starting Map for Two-Tier Migration

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
