---
name: system-md
description: 'Produces and maintains SYSTEM-COMPONENTS.md for a confirmed application: an architectural inventory of the functional building blocks - subsystems, services, engines, integrations, processors, data systems, infrastructure - each with purpose, responsibilities, in/out-of-scope ownership, inputs and outputs, error handling, configuration, related components, plus an ASCII relationship map and a "removing it would" summary table. Answers "what exists and what does each piece own" without reading all the code. Application-scoped: in a monorepo, one document per confirmed app, never one blended document across apps. Extracted from like-a-pro phase 3 (as system-creator Mode A). Reusable-unit catalogs (UI builder blocks, and code units generally) belong to UNITS.md and are owned by units-md, not here; a button or card never appears in SYSTEM-COMPONENTS.md, a queue or rate limiter never in UNITS.md. Documents only - no code changes, no enforcement.'
when_to_use: The user asks to document or map the system's components, "what subsystems does this app have", write or refresh SYSTEM-COMPONENTS.md, produce a component hierarchy and relationship map for onboarding, or is running like-a-pro phase 3 after the application boundary was confirmed.
argument-hint: "[app path, defaults to the confirmed application]"
---

# system-md

Writes one document: **`SYSTEM-COMPONENTS.md`** — the architectural inventory of an application. It is for the
reader who must know what exists and who owns what before touching the system: onboarding, incident triage,
delegation briefs, and design reviews.

| Document | Owner | Contents |
|---|---|---|
| `SYSTEM-COMPONENTS.md` | **this skill** | the moving architectural pieces: services, engines, subsystems, integrations, data stores, infrastructure |
| `UNITS.md` | [`units-md`](../../Viber/units-md/SKILL.md) | reusable units to consult before building — components, rules, clients, and the UI builder blocks profile |
| `AGENTS.md` | [`agents-md`](../../Viber/agents-md/SKILL.md) | the obligations an agent follows, which may point at either file |

A button belongs in `UNITS.md`, not here. A queue, rate limiter, or sync engine belongs here, not there. When the
user asks for a units catalog, run `units-md`; do not produce a second inventory of the same thing in this
document's shape.

## Scope: per confirmed application

- One document per **application**, placed at the app root or in its docs folder
  (`apps/<app>/SYSTEM-COMPONENTS.md`), or the project root for a single-app project.
- **Never infer the boundary from the directory tree.** Confirm it: the protocol lives in
  [like-a-pro's app-boundary discovery reference](../../../like-a-pro/references/app-boundary-discovery.md); the short
  form is scan candidates, show the evidence (manifests, entry points, deployables), and ask the user which are
  applications before writing anything.
- Monorepo: each app gets its own document with its own component set. Shared platform code is listed in the app
  that consumes it, with a pointer to where it actually lives.

## Procedure

```
- [ ] 1. Confirm the application boundary (evidence, then ask)
- [ ] 2. Understand before judging: entry points, real call paths, deployables, data stores
- [ ] 3. Identify components (what stands alone, what is internal detail)
- [ ] 4. Write the document from references/components-template.md
- [ ] 5. Verify: every named component exists in code; links resolve; nothing invented
- [ ] 6. Report: components listed, what was excluded, what stayed unknown
```

**1–2.** Follow execution, not folder names. Read the manifests, the entry points, the routes or commands, the
jobs and workers, the storage access, the outbound calls. A directory called `services/` proves nothing about
boundaries.

**3. What counts as a component.** It stands alone if removing it would break something specific, or if someone
would have to be told about it to work on the system. Type vocabulary that has served well: Subsystem, Service,
Engine, Infrastructure, Integration, Processor, Data System, UI System, Architectural Pattern. A helper function
is not a component; a queue consumer usually is.

**4. Document structure** (full field notes: [`references/components-template.md`](references/components-template.md);
tone and depth: [`references/components-worked-example.md`](references/components-worked-example.md)):

1. Title, application name, version/channel scope, companion-document links (`UNITS.md`, specs).
2. System overview: one tight paragraph, then an ASCII box diagram of the major subsystems.
3. Component hierarchy: a text tree of subsystems, components, subcomponents.
4. Numbered component sections, each with Purpose, Responsibilities, In Scope / Out of Scope (strict ownership,
   with cross-links), Inputs / Outputs, Error Handling, Configuration, Related Components.
5. Relationship map: ASCII flow with verb-labelled arrows, tracing real call and data paths.
6. Identification summary: `| Component | Type | Removing it would… |` — the column that separates real components
   from decoration.

**5. Verify.** Open the file for each component and confirm it exists and does what the section claims. Mark what
could not be checked as *unknown* rather than filling it in.

## Refresh

| Change | Action |
|---|---|
| Component added | new numbered section, added to the tree and the map, in the same change that added the code |
| Component moved or renamed | update the path and the hierarchy; keep the old name visible once ("formerly X") if people cite it |
| Component removed | drop the section; if its responsibility survives elsewhere, say where it went |
| Ownership boundary shifted | edit In/Out of Scope for both sides — a boundary change is two sections, not one |
| Doc contradicts the code | the code wins; report the contradiction instead of quietly rewriting history |

Never renumber sections for cosmetics, and never split this file into a competing second inventory: extend the
existing one if `SYSTEM-COMPONENTS.md` already exists (also when the equivalent lives inside the app's main
README — update that section, do not create a parallel file).

## Boundaries

| Not this | Go instead |
|---|---|
| Cataloging reusable units to consult before building | `units-md` |
| The rules and obligations an agent follows | `agents-md` |
| Deciding the design topic by topic | `detailsup` |
| Fixing the code, refactoring, enforcing structure | `senior-refactor`, or ordinary implementation work |
| Judging whether a component is well built | `antipattern`, `code` review |
| Visual UI catalog for a designer | design docs; `capture` for images |

Documents only: this skill writes `SYSTEM-COMPONENTS.md` and touches nothing else in the project.

## Files

| Path | Owns |
|---|---|
| [`references/components-template.md`](references/components-template.md) | the copy-pasteable skeleton and per-field notes |
| [`references/components-worked-example.md`](references/components-worked-example.md) | a complete worked instance: depth, tone, diagrams |
| [`../../../like-a-pro/references/app-boundary-discovery.md`](../../../like-a-pro/references/app-boundary-discovery.md) | the confirmation protocol this skill depends on |
