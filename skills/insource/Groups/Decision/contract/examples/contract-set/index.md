# Sample Contracts

A worked `contract/` set: one index, a default rule, an explicit exception to it, an AoU
protocol, and a two-contract split that prevents runaway retries. Copy the shape, never the
decisions — ownership is per-project.

## Layers

- **0 — Database:** PostgreSQL; storage, native querying, migrations.
- **1 — Backend:** the API service; business rules, authorization, data shaping.
- **2 — Frontend:** the SPA; rendering, local interaction, optimistic UI.

## Documents

- Automatic Retry — who silently re-attempts transient failures, and why not the client.
- Hot-path Filtering — the narrow exception where the frontend filters an already-authorized dataset.
- Manual Retry — the user-facing retry affordance after automatic policy is exhausted.
- Search Query Filtering — who filters user-provided search queries; the default rule.
- Timestamp Representation — an AoU protocol: every layer adheres to one shared format rule.