---
name: plugin
description: Authors an application's plugin and settings architecture as one extensibility system. Settings and plugins are the same family: a closed host exposes a small extension contract, and an open set of contributions adds behavior without editing shared code. Use when designing, reviewing or refactoring settings pages, configuration catalogs, feature flags, per-tenant or per-platform preferences, extension points, module systems, or plugin hosts. Decides build-time versus runtime loading per axis, enforces an Open/Closed growth gate, and specifies descriptor data, contribution registries, layered composition, scope and storage, renderer shapes, consumer authorities, migration, versioning, trust and failure isolation.
argument-hint: "[project root or app name]"
---

# Plugin & Settings Architecture Skill

## 1. Overview & Philosophy

Settings and plugins are the same architecture wearing different clothes.

Both answer one question: **how does a closed host grow without being edited?** A plugin adds a
capability; a setting adds a configurable behavior. Each is a contribution with a contract, a
lifecycle, defaults, and a consumer. The host owns loading, validation, storage, composition,
rendering and failure isolation. The contribution owns only its own data and behavior.

Treating settings as a pile of hand-written UI and scattered constants is the same mistake as
treating a plugin system as a folder of `if` statements. Both turn every new item into an edit to
shared code, and both fail the Open/Closed Principle:

> **Open for extension, closed for modification.** Adding the Nth setting or the Nth plugin must not
> modify the host, the renderer, another plugin, or unrelated settings.

This pillar exists to make that law observable and testable. It does not prescribe a framework; it
prescribes a **shape**: host core, extension contract, registry, composition, storage seam, renderer
vocabulary, and one authority per behavior.

---

## 2. Two Faces of One Contract

| Concern | Setting | Plugin |
|---|---|---|
| What grows | Configured behavior | Code or capability |
| Contribution unit | Descriptor row | Module or package |
| Manifest | Key, shape, scope, default, bounds, copy, validation | Id, version, dependencies, capabilities, entry point |
| Host owns | Load, validate, store, render, apply, isolate | Load, verify, activate, isolate, unload |
| Extension points | New row (data); new control shape (host change) | New contribution; new extension-point type (host change) |
| Typical failure | Dead setting, scope drift, drift between copy and consumer | Version skew, trust, activation failure, leak |
| Growth law | One descriptor entry, zero shared edits | One registration, zero shared edits |

The maturity ladder is the same for both:

```text
1. Hardcoded UI / hardcoded behavior
2. One central config object (still edited per feature)
3. Descriptor catalog (data-driven rows, closed renderer)
4. Contribution registry (modules add rows and behavior)
5. Plugin host (discovery, lifecycle, versioning, trust, isolation)
```

Most products need level 3 or 4. Level 5 is earned by third-party code, not by a large settings page.
See `references/settings-as-plugins.md` for the full isomorphism and the threshold for adding the seam.

---

## 3. The Open/Closed Growth Gate

Before accepting a design, run these four extensions. Each must be achievable **without editing shared
code beyond the declared extension point**.

| Extension | Allowed edit | Forbidden edit |
|---|---|---|
| Add the Nth setting | One descriptor entry | Renderer, page layout, another setting, shared constant |
| Add the Nth platform, tenant or module | One contribution file plus one registration | Settings page, composition engine, other modules |
| Add a new **control shape** | One shape member plus one renderer branch (a deliberate host change) | Any per-setting branch in the renderer |
| Add a new **storage scope** | One scope value plus one storage seam (a deliberate host change) | Any caller choosing `Get` versus `GetGlobal` by hand |

If an extension needs a fifth kind of edit, the seam is in the wrong place. Name the edit, then move
the seam until the edit disappears. This gate is the pillar's primary review test.

Two supporting tests:

- **Zero-name test.** Shared code contains no plugin, platform, tenant or setting name. Search the
  host for the concrete names; every hit is a leak.
- **Deletion test.** Deleting a contribution leaves the host compiling and running, with that
  contribution absent and no ghost row, dead route or crash. Stale overrides are dropped, not fatal.

---

## 4. Directory Structure & Assets

```text
plugin/
├── SKILL.md                                                  # Entry point, doctrine, workflow, OCP gate
├── assets/
│   └── templates/
│       ├── settings-architecture-template.md                 # Binding settings/plugin specification
│       └── plugin-contract-template.md                       # Polyglot contract and manifest skeleton
├── references/
│   ├── settings-as-plugins.md                                # Isomorphism, maturity ladder, when to add the seam
│   ├── build-time-vs-runtime.md                              # Per-axis decision matrix, trust, versioning, lifecycle
│   ├── composition-and-layering.md                           # Base plus contributions plus patches, collisions, order
│   ├── storage-scope-and-migration.md                        # Scope seam, typed values, lazy migration, atomic sets
│   └── failure-modes-and-anti-patterns.md                    # Dead settings, scope drift, boolean explosion, trust gaps
└── examples/
    └── multi-source-settings-walkthrough.md                  # End-to-end case study with a real multi-platform app
```

---

## 5. Workflow & Conversational Discovery

When invoked, either standalone or via the parent `architecture` skill:

### Step 1: Inspect before asking

Find the current answers in the repository:

- Where do settings live today: one config object, a database table, key-value storage, env files, or
  rows in each screen?
- How many settings exist, and how many axes of variation exist: platforms, tenants, users, plans,
  regions, devices?
- Which settings have a reader, and which are written but never consumed?
- Which screens hardcode a platform, tenant or setting name?
- Is executable code ever loaded after startup? Which platform targets are involved: mobile store,
  desktop, server, browser?

### Step 2: Ask only the forks that change the design

> *"Which axes vary: platform, tenant, user, plan, region or device? Is the list of plugins known at
> build time, or must it change after release? Who authors plugins: your team, another internal team,
> customers, or the public? Does any target platform forbid downloading executable code? Should
> settings be data-only, or can a setting carry custom behavior? Are any of these values secrets?"*

Do not ask what the repository already answers.

### Step 3: Decide build-time versus runtime per axis

Run the decision matrix in `references/build-time-vs-runtime.md`. Record one row per axis: code,
catalog metadata, values, copy, feature flags, secrets. A single product often needs different answers
on different rows. The normal, safest answer is:

- **Contracts and consumers:** build-time.
- **Catalog rows, copy, defaults and enablement:** runtime data is acceptable, if validated.
- **Executable third-party code:** runtime only on a trusted server with signing, allowlisting and
  isolation; never on a mobile app store.

### Step 4: Define the host core

Specify, in this order:

1. **Descriptor** — the complete data shape of one setting or plugin.
2. **Contribution contract** — additive and patch contributions, never mutation of a shared list.
3. **Registry** — discovery and registration from the framework's collection mechanism.
4. **Composition** — layers, specificity, field ownership, collision policy, ordering.
5. **Storage seam** — one path that turns a scope into a container; typed values; migration.
6. **Renderer vocabulary** — a closed set of shapes; new setting is data, new control is host work.
7. **Consumer authority** — one class or function per behavior that both the row and the runtime read.
8. **Isolation** — what happens when one contribution fails.

### Step 5: Author the specification

Use `assets/templates/settings-architecture-template.md` into `<docs>/architecture/plugin-architecture.md`
(or `<docs>/architecture/settings-architecture.md` when the product has settings but no third-party
plugins). Use `assets/templates/plugin-contract-template.md` when the contract itself must be written
down in code shape.

### Step 6: Produce the checks

Every rule must have a check that can fail. Minimum set:

- No shared file names a concrete plugin, platform or tenant.
- Every setting key has exactly one descriptor and at least one reader.
- Every rendered row has a descriptor; no row is built by hand.
- Every consumer reads through the scope seam, never by choosing a container directly.
- Same-specificity patches on one field fail the build or test.
- Removing a contribution leaves the host green.
- Adding the Nth contribution changes only the declared extension point.

---

## 6. Reference Architecture

```text
┌──────────────────────────────────────────────────────────────────────┐
│                              HOST CORE                               │
│  descriptor schema · shape vocabulary · scope vocabulary · registry  │
│  composition engine · storage seam · renderer · isolation · checks   │
└───────────────┬───────────────────────────────┬──────────────────────┘
                │ contract                      │ contract
      ┌─────────▼─────────┐           ┌─────────▼─────────┐
      │  Contribution A   │           │  Contribution B   │
      │ rows + patches    │           │ rows + patches    │
      │ consumers         │           │ consumers         │
      └───────────────────┘           └───────────────────┘
                │                               │
      ┌─────────▼─────────┐           ┌─────────▼─────────┐
      │ Storage scope     │           │ Storage scope     │
      │ global / scoped   │           │ global / scoped   │
      └───────────────────┘           └───────────────────┘
```

The host never imports a contribution by name. The composition root registers contributions; the
registry enumerates them; the composition engine folds them; the renderer draws the result; the
consumer reads through the storage seam. Every arrow points from host to contract, never host to
concrete plugin.

A production example of this shape (a multi-platform app whose settings are contributed by per-source
modules) is walked through in `examples/multi-source-settings-walkthrough.md`.

---

## 7. The Laws

1. **One descriptor per setting, one reader per setting.** A row with no consumer is a lie; a
   consumer with no row is hidden magic. Both fail review.
2. **Closed shapes, open rows.** A new setting is data. A new control is a deliberate host change,
   never a per-setting branch in the renderer.
3. **Scope is declared once and enforced by one seam.** No caller chooses a container by hand.
4. **Contributions are additive or patch-based, never mutating.** `Adds` and `Overrides`, not
   `RemoveWhere` on a shared list.
5. **Specificity decides; equal specificity fails loudly.** Never resolve a real conflict by
   registration order.
6. **Ordering is data.** A section or row places itself by a declared rank, not by arrival order.
7. **Defaults are single-sourced.** The value a row advertises is the constant the consumer uses.
8. **Visibility is data.** A named predicate evaluated against the live descriptor; the shared
   renderer does not branch on a plugin name.
9. **Storage values are atomic and typed.** No formatted strings, no unit words, no composite blobs.
   Split money into amount plus currency; split a measurement into value plus unit.
10. **Secrets are not settings.** A secret lives in a secret store; settings may hold only a
    reference or a public identifier.
11. **Migration is lazy and lossless.** A new container reads through to the legacy location and
    moves the value on first write. Never rewrite user data behind their back on a read.
12. **A set invariant is stored as a set.** One atomic write, never N independent booleans that a
    crash can leave contradictory.
13. **Unknown identifiers are inert, not fatal.** A removed plugin's id must not take the host down.
14. **One behavior has one authority.** The settings row, the dispatcher and the tests describe the
    same container and the same default.
15. **Build-time is the default; runtime is earned.** Move to runtime only for a real requirement,
    and only on a platform that permits it.

---

## 8. Build-Time vs Runtime in One Page

| Criterion | Build-time | Runtime |
|---|---|---|
| Author | First-party team | Third party, customer, or changing catalog |
| Trust | Trusted code | Must be signed, allowlisted, sandboxed |
| Delivery | Follows app release | Changes without redeploy |
| Mobile app store | Required for code | Downloaded executable code is normally forbidden |
| AOT, trimming, single-file | Native fit | Fragile: reflection and dynamic loading break |
| Type safety | Full | Contract and serialization only |
| Failure blast radius | Compile or test time | Production, per activation |
| Isolation | Process boundary not needed | Needs supervision, timeouts, circuit breakers |
| Versioning | Lockstep | Explicit contract version and compatibility window |
| Discovery | DI, static registration, linker roots | Manifest, scan, dynamic import, remote catalog |

**The usual correct answer is hybrid:** build-time code plus runtime data. Keep contracts, consumers
and effectful behavior compiled; let the catalog, copy, defaults and enablement be data. That is what
makes a settings page grow without a release while keeping behavior reviewable and type-checked.

Full matrix, platform constraints, trust model and lifecycle: `references/build-time-vs-runtime.md`.

---

## 9. Output Documents

Default placement, confirmed with the user:

- `<docs>/architecture/plugin-architecture.md` — plugin and settings system, build-time versus
  runtime decision, contracts, composition, storage, checks.
- `<docs>/architecture/settings-architecture.md` — settings-only variant when no code plugins exist.
- `<docs>/architecture/plugin-contract.md` — optional, when the contract is shared across teams.

Cross-link from `AGENTS.md`, `UNITS.md` or the architecture index. Update the project's decision log
when a build-time versus runtime choice is made; that choice is architectural, not cosmetic.

---

## 10. Core Invariants

1. **Never author a settings page that hardcodes its rows.** Rows are data.
2. **Never accept a setting without a consumer, or a consumer without a setting.**
3. **Never let shared code name a concrete plugin, platform, tenant or setting.**
4. **Never resolve a same-specificity conflict by order.** Fail loudly.
5. **Never store a composite value as one formatted string.** Split primitives at storage.
6. **Never put a secret in settings.** Reference the secret store.
7. **Never choose runtime executable loading on a platform that forbids it.** State the constraint.
8. **Never claim the OCP gate passes without running the four extensions.** Show the edits.
