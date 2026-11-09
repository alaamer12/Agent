# stack

> This document defines the `stack` steering folder: what the project is built with, stated as "we use X". It lives exclusively in the **tech tier** (`tech/stack/`); see [`index.md`](index.md) for the taxonomy overview.

**Holds.** What the project is built with: programming languages, runtimes, UI frameworks, libraries, databases, hosting environments, and external infrastructure services. For each item, a clean statement saying what tool is in use, what purpose it serves, and version constraints if significant.

**Does not hold.**
- Business decisions stated as technical facts (see below and [`placement.md`](placement.md)).
- Operational commands or how-to-use guides (which belong in [`playbook.md`](playbook.md) or project-wide developer guides).
- Technical guidelines or constraints for a component ([`doctrine.md`](doctrine.md)).
- Historical justifications or benchmark evaluations for why a technology was chosen (which belong in Architectural Decision Records outside the taxonomy).

**The test.** Does the line say *"we use X"*?
- *"We use TypeScript 5.6 and Vue 3 for the web client"* -> `tech/web/stack/frontend.md`
- *"Never use `any` in TypeScript"* -> `tech/shared/doctrine/type-standards.md`
- *"How to install dependencies and run the build"* -> `tech/playbook/build-app.md` (or outside developer guide)

**Business Decisions Expressed as Technical Facts (Section 5.4 Rule).**
Statements that sound technical but represent business independence, governance, or strategic decisions must be moved to the perception tier.
- *Example*: *"We maintain an isolated database and distinct domain from the partner company"* is a strategic business boundary (`perception/shared/policy/` or `perception/shared/product/`), not a stack entry. `stack` records only the concrete database engine used (*"We use PostgreSQL 16"*).

**Example (`tech/shared/stack/platform`).**
"We use PostgreSQL 16 as our primary relational database, deployed as a managed cloud instance. We use Redis 7 for distributed rate limiting and temporary session caching."
