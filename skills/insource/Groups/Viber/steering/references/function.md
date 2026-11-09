# steering function folder (`function`)

> **Terminology rule (mandatory).** The directory name `function/` in the technical tier (`tech/<area>/function/`) is always referred to as the **steering function folder** in prose, headings, index files, commit messages, and agent output. Never write just "function" or "the function folder", because in code "function" denotes a single code subroutine. The bare directory name `function/` appears only in file paths and layouts.
> Note: The business-tier counterpart to this folder is [`capabilities.md`](capabilities.md), which carries no naming ambiguity.

This document defines the steering function folder: system-wide technical functionality and runtime mechanisms that span features across the entire application or area.

**Holds.** Technical system-wide mechanisms and infrastructure-level runtime behaviors:
- System-wide error handling and user feedback patterns (`error-ux`).
- Cross-cutting authentication and session synchronization lifecycles.
- System-wide caching, polling, or state propagation mechanisms.
- Shared upstream partner integrations that serve the platform as a whole (e.g. data ingestion pipelines).

**Does not hold.**
- Business-level functional descriptions of what the platform provides ([`capabilities.md`](capabilities.md)).
- Engineering guidelines and quality mandates for a specific component ([`doctrine.md`](doctrine.md)).
- Static directory layout and module architecture ([`structure.md`](structure.md)).
- Technology selections stated as "We use X" ([`stack.md`](stack.md)).
- Single-feature technical implementation (which belongs in feature documentation outside the taxonomy).

**The test.** Scope and feature-independence:
1. *Feature Deletion Test*: If feature X were deleted, would this document still be true? If yes, it belongs in the steering function folder.
2. *System Capability*: A technical capability that the entire platform is built around (e.g., media streaming in a video app, or asynchronous price sync in a simulator) represents the system itself and belongs here.
3. *System vs. Component*: System-wide error handling lives here; the specific HTTP wire error format of an API endpoint lives in `doctrine.md`.

**Example (`tech/shared/function/external-feed-sync`).**
"The application maintains an asynchronous synchronization pipeline that ingests external provider pricing updates, validates wire envelopes against schema contracts, and pushes updated valuation snapshots to the internal caching layer on a scheduled interval."
