# Settings Are Plugins: One Extensibility Family

This reference explains why settings and plugins share one architecture, when a product should
graduate from a config object to a contribution registry, and how to tell a real extension point from
a folder of conditionals.

---

## 1. The Shared Shape

Every extensible system has six parts. Settings and plugins differ in payload, not in structure.

| Part | Settings payload | Plugin payload |
|---|---|---|
| **Host** | Settings service, composition, renderer, storage | Plugin loader, lifecycle, sandbox, host API |
| **Contract** | Descriptor plus contribution interface | Manifest plus entry point plus host API |
| **Registry** | Collection of contributions | Collection of manifests or packages |
| **Contribution** | Rows and patch rows | Module with behavior and metadata |
| **Lifecycle** | Register, compose, validate, store, render, apply | Discover, verify, resolve, activate, deactivate, unload |
| **Isolation** | A bad row is dropped or fails a test | A bad plugin is disabled without taking the host down |

The host must be **closed**: it knows the contract, never the concrete item. The contribution must be
**open**: it supplies data or behavior, never edits the host.

---

## 2. Settings as Micro-Plugins

A single setting is a micro-plugin with a very small surface:

```text
Setting
├── identity        key, section, order
├── manifest        shape, scope, value kind, bounds, options, default
├── presentation    label, hint, unit, icon, automation id, visibility predicate
├── validation      kind plus error copy
├── storage         global or scoped container
└── activation      the consumer that reads it and the effect it has
```

Write that as a descriptor and the settings page becomes a **renderer over a registry**. Write it as
hand-built UI plus scattered constants and every new setting edits the page, the view-model, the
validator, the copy table, and probably a second platform's layout.

The descriptor is the setting's manifest. The difference from a plugin manifest is only that the
payload is configuration rather than code.

---

## 3. The Maturity Ladder

Move up only when the current rung hurts. Each rung buys something and costs something.

### Rung 1 — Hardcoded UI and behavior

The setting is a control in a layout and an `if` in the consumer.

- Buys: nothing to design.
- Costs: every change touches several files; platforms drift; copy and behavior disagree.
- Use for: a prototype with one or two fixed values.

### Rung 2 — Central config object

One typed object holds the values; consumers read fields.

- Buys: one place to see the values; type safety.
- Costs: the object grows without bound; adding a setting edits the object and every serializer;
  presentation and validation still live elsewhere.
- Use for: a small CLI or library with a stable, tiny option set.

### Rung 3 — Descriptor catalog

Rows are data with shape, scope, constraints, copy and default; one renderer draws them.

- Buys: adding a setting is one data entry; UI is uniform; copy and validation travel with the value.
- Costs: the renderer's shape vocabulary is a closed set the host owns; a new control is host work.
- Use for: most applications with a settings screen.

### Rung 4 — Contribution registry

Modules contribute rows and patches; the host composes them per context.

- Buys: a new platform, tenant or feature adds a file and a registration; zero shared edits.
- Costs: composition rules, specificity, collision policy, stale-override handling.
- Use for: multi-platform, multi-tenant or modular products.
- This is the sweet spot for internal extensibility.

### Rung 5 — Plugin host

External packages are discovered, verified, versioned, activated and isolated at runtime.

- Buys: third-party or post-release extensibility.
- Costs: trust, signing, sandboxing, compatibility windows, lifecycle, failure isolation, support.
- Use for: a genuine ecosystem, enterprise on-prem extensions, or a product whose value is the
  plugin API itself.
- Do not use for: an internal settings page, a mobile app store target, or a team that cannot support
  a plugin API.

---

## 4. When to Add the Seam

Add a contribution registry when **at least one** is true:

- A second axis of variation exists (platform, tenant, plan, region, module) and its items differ.
- Settings are owned by separate modules or teams, and the shared page should not know them.
- The setting count is large and growing, and every addition currently edits shared UI.
- The same setting must be overridden per context (a label, a bound, a default).
- The product already has module boundaries that could own their configuration.

Do **not** add one when all are true:

- One deployment, one tenant, one platform.
- Fewer than roughly a dozen settings, stable.
- One team owns all of them.
- No override axis exists.

A registry has real costs: composition rules, collision tests, ordering, migration. Pay them for
growth, not for fashion.

---

## 5. The OCP Growth Test, Worked

Take the four extensions from the pillar and show the exact edit for each.

### 5.1 Add a setting

```text
Before: the renderer builds a dark-mode toggle by hand.
After:  append one descriptor row.
Edits:  the catalog file only.
Forbidden: renderer, layout, view-model, another row.
```

If the new setting needs a consumer, add the consumer in the owning module and read the value through
the storage seam. That is still one module plus one row, never the renderer.

### 5.2 Add a platform, tenant or module

```text
Before: the settings page has a per-platform section and a switch per platform, hand-written.
After:  the module declares its descriptor, contribution, and registration.
Edits:  module file plus composition root.
Forbidden: settings page, composition engine, other modules.
```

The platform switch row should enumerate the registry, so a new registration appears without any row
edit. If the page needs a new switch, the registry was not the source of truth.

### 5.3 Add a control shape

```text
Before: the renderer supports toggle, number, text, enum.
After:  add one shape member and one renderer branch.
Edits:  shape enum plus renderer. This is a deliberate HOST extension.
Forbidden: a branch keyed by setting key, platform, tenant or label.
```

The distinction matters: adding a *shape* changes the host vocabulary for everyone; adding a *row*
changes only data. Never smuggle a new shape in as a special case for one setting.

### 5.4 Add a storage scope

```text
Before: global and per-platform.
After:  add one scope value and one storage-seam branch.
Edits:  scope enum plus the single storage seam plus migration tests. HOST extension.
Forbidden: callers choosing their own container.
```

Every caller reads through the seam with the descriptor's scope. A caller that picks a container by
hand is a future scope-drift bug.

---

## 6. Settings Are Not Everything

Keep these categories separate. Collapsing them into one settings blob causes most configuration bugs.

| Category | Nature | Belongs in |
|---|---|---|
| **Preference** | User choice, reversible, safe default | Settings store |
| **Policy** | Product or admin rule, may be enforced | Policy service plus read-only settings surface |
| **Feature flag** | Temporary rollout switch, has an owner and expiry | Flag service, not the user settings page |
| **Capability** | What a plugin or platform can do | Descriptor or contract, not a user toggle |
| **Environment** | Deployment fact (URL, region, mode) | Environment configuration, validated at boot |
| **Secret** | Credential or key | Secret manager, never the settings store |
| **Derived state** | Computed from other values | Computed at read time, never stored as a setting |

A settings page may *display* a capability or policy read-out. It must not become the authority for it.

---

## 7. Case Study: Multi-Platform Settings

A desktop and mobile app watches several websites. Each site is a module with its own parsers,
routes, capabilities and preferences. Before the redesign:

- The settings page was a hand-written layout with a per-platform section.
- Some values were global keys; others were in a platform container. Nothing declared which.
- A notification toggle was persisted but never read, so turning it off changed a number on disk
  while toasts kept arriving.
- Adding a site meant editing the settings page, the view-model and two layouts.

After the redesign:

- A base descriptor catalog holds every shipped row.
- Each site module contributes its own rows and field-level overrides.
- A registry enumerates contributions; composition folds base plus contributions per active site.
- Scope is declared on the descriptor and enforced by one storage seam.
- The renderer supports a closed set of shapes and names no site.
- A shared authority class answers each behavior; the row and the dispatcher read the same source.

Result: adding a site is one module registration; adding a setting is one catalog entry; a scope
change is one field plus a tested seam. The settings page contains no platform name.

The full walkthrough is in `../examples/multi-source-settings-walkthrough.md`.

---

## 8. Review Questions

1. If we add the Nth setting, which files change? If more than the catalog plus its consumer, fail.
2. If we add the Nth plugin, which files change? If the host changes, fail.
3. Does any shared file contain the name of a concrete plugin or platform?
4. Does every setting have a reader? Does every reader have a setting?
5. Can two contributions disagree about one field without a loud failure?
6. Is ordering declared, or does it depend on registration order?
7. Is the default the same constant the consumer uses?
8. Can a removed contribution leave a ghost row or a crash?
9. Is the build-time versus runtime choice written down with its reason?
10. Does the runtime path have a platform that forbids it?
