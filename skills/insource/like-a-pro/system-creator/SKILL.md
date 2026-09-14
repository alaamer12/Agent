---
name: system-creator
description: Produces two architecture docs for a confirmed application. Mode A writes SYSTEM-COMPONENTS.md, an architectural inventory of functional building blocks (services, engines, subsystems, infrastructure, data stores). Mode B writes UNITS.md, a catalog of reusable UI builder blocks and builder functions (explicit invocation only).
---

# System Creator (`system-creator`)

## Overview

`system-creator` produces and maintains two complementary architecture documents for a confirmed application across any language, framework, or platform (web, mobile, desktop, backend, distributed systems, CLI):

- **`SYSTEM-COMPONENTS.md`** — an architectural inventory of the application's functional building blocks: services, engines, subsystems, infrastructure pieces, integrations, and data stores (**Mode A**).
- **`UNITS.md`** — a catalog of the UI layer's reusable builder blocks: base/composite components, design-system primitives, and reusable builder functions (**Mode B**, explicit invocation only).

The two documents answer different questions: `SYSTEM-COMPONENTS.md` maps the moving architectural pieces and how they interact, while `UNITS.md` tracks reusable visual builder components and functions. A button or card never belongs in `SYSTEM-COMPONENTS.md`; a queue or rate limiter never belongs in `UNITS.md`.

**Application Scoping:** In multi-app projects, documents are placed within the confirmed application root or doc folder (e.g., `apps/<app>/SYSTEM-COMPONENTS.md` and `apps/<app>/UNITS.md`, or project root for single-application projects).

---

## Mode A: System Components (Architectural Inventory)

Produces a **System Components** document inventorying the moving parts, responsibilities, and relationship topologies of the application.

Read `references/components-worked-example.md` for structure and tone, and `references/components-template.md` for the copy-pasteable markdown skeleton.

### When to Use Mode A
- Mapping a non-trivial system with several moving parts (pipelines, services, worker pools, storage engines, error systems).
- An engineer needs a clear reference explaining "what exists and what each piece owns" without reading all code.
- Explicitly requested: "document system components", "map the architecture", "write components doc", "component hierarchy".

### Document Structure & Guidelines
1. **Title & Scope:** State application name, version scope, and companion doc links.
2. **System Overview:** One tight paragraph defining what the application is, accompanied by an ASCII box diagram of major subsystems.
3. **Component Hierarchy:** A clean text tree showing all subsystems, components, and subcomponents.
4. **Numbered Component Sections:**
   - `### Type`: Subsystem, Service, Engine, Infrastructure, Integration, Processor, Data System, UI System, Architectural Pattern.
   - `### Purpose`: 2–4 sentences on what it does and why it stands alone.
   - `### Responsibilities`: Imperative bullet points.
   - `### In Scope / Out of Scope`: Strict ownership boundaries with cross-links.
   - `### Inputs / Outputs`, `### Error Handling`, `### Configuration`, `### Related Components`.
5. **Component Relationship Map:** ASCII flow diagram tracing call/data paths with verb-labeled arrows.
6. **Component Identification Summary Table:** `| Component | Type | Removing It Would… |`.

---

## Mode B: UI Units Catalog (Explicit Invocation Only)

Discovers, captures, documents, and maintains UI builder blocks, design tokens, and reusable builder functions in **`UNITS.md`** across any UI technology stack.

> **CRITICAL ACTIVATION GUARD:**
> Mode B must **RUN ONLY WHEN EXPLICITLY INVOKED** (e.g., "use system-creator units mode", "update UNITS.md", "audit units"). Never auto-trigger Mode B implicitly.

### Operating Modes
- **B1 (Greenfield / Fresh App):** Detect tech stack, establish category taxonomy, seed planned primitives with status `Scaffold`.
- **B2 (Existing App Audit):** Scan presentation directories, identify reusable visual components and builder functions, reconcile with existing `UNITS.md`, and update statuses (`Scaffold` vs `Implemented`).

See `references/units-reference.md` for definitions, builder function inclusion/exclusion criteria, and template schemas.
