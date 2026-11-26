# stack

> This document defines the `stack` steering folder: what the project is built with, stated as "we use X". It lives exclusively in the **tech tier** (`tech/stack/`); see [`index.md`](index.md) for the taxonomy overview.

**Scope rule.** Default to `tech/<area>/stack/`; use `tech/shared/stack/` only after the [Universal Scope Test](layout.md#universal-scope-test) passes. Area files link to shared facts and contain only their delta.

**Holds.** What the project is built with: programming languages, runtimes, UI frameworks, libraries, databases, hosting environments, and external infrastructure services. For each item, a clean statement saying what tool is in use, what purpose it serves, and version constraints if significant.

**Does not hold.**
- Business decisions stated as technical facts (see below and [`placement.md`](placement.md)).
- Operational commands or how-to-use guides (which belong in [`playbook.md`](playbook.md) or project-wide developer guides).
- Technical guidelines or constraints for a component ([`doctrine.md`](doctrine.md)).
- Historical justifications or benchmark evaluations for why a technology was chosen (which belong in Architectural Decision Records outside the taxonomy).

**The test.** Does the line say *"we use X"*?
- *"We use TypeScript 5.6 and Vue 3 for the web client"* -> `tech/web/stack/frontend.md`
- *"Never use `any` in TypeScript"* -> `tech/<area>/doctrine/type-standards.md`
- *"How to install dependencies and run the build"* -> `tech/playbook/build-app.md` (or outside developer guide)

**Business Decisions Expressed as Technical Facts (Section 5.4 Rule).**
Statements that sound technical but represent business independence, governance, or strategic decisions must be moved to the perception tier.
- *Example*: *"We maintain an isolated database and distinct domain from the partner company"* is a strategic business boundary (`perception/<area>/policy/` or `perception/<area>/product/`), not a stack entry. `stack` records only the concrete database engine used (*"We use PostgreSQL 16"*).

**Interview before authoring.** Complete the [Tech Directory Interview and Authoring Gate](documentation-conventions.md#mandatory-tech-directory-interview-and-authoring-gate) for this directory. Ask or explicitly confirm:
- Which area and technical concerns does this directory own, and which facts pass the [Universal Scope Test](layout.md#universal-scope-test) for `shared/` rather than merely being reused by some areas?
- What languages, runtimes, frameworks, libraries, databases, hosting platforms, and external services are actually in use, and what role does each play?
- Which versions, compatibility ranges, and environment differences are intentional constraints?
- Which choices are already fixed, which remain open, and which observed dependencies are accidental rather than approved?
- Who owns each external service or technology decision, and are cost, licensing, support, or vendor constraints relevant?
- Where sources conflict, which source is authoritative and what must be verified before documenting the choice?

Record the confirmed tool roster, scope, significant constraints, ownership, rationale, and unresolved choices in the directory's ledger row. Do not turn a detected dependency into an endorsed stack choice without confirmation.

**Example (`tech/<area>/stack/platform`).**
"We use PostgreSQL 16 as our primary relational database, deployed as a managed cloud instance. We use Redis 7 for distributed rate limiting and temporary session caching."
