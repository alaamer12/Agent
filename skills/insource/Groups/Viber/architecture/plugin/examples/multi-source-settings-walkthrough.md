# Walkthrough: Multi-Platform Settings as a Plugin System

A real case study, generalized. A desktop and mobile application watches several websites. Each
website is a module with its own parsers, routes, capabilities and preferences. The settings page must
grow with each site without the shared page learning any site's name.

This walkthrough shows the before state, the seam design, and the exact edits for each growth axis.

---

## 1. Context

| Fact | Value |
|---|---|
| Platforms | Desktop and mobile, one shared codebase |
| Sources | Two sites at the start, more expected |
| Settings count | Roughly twenty, growing |
| Variation axis | Per-site preferences, plus app-wide behavior |
| Third-party plugins | None |
| Target constraints | Mobile store, AOT and trimming |

The last row decides build-time versus runtime before any code is written: **executable extensions
are build-time; the settings catalog is data**. See `../references/build-time-vs-runtime.md`.

---

## 2. Before: The Hand-Built Page

Symptoms collected before the redesign:

1. **The page was a layout.** Each setting was a control tree in two platform layouts. Adding one
   meant editing both layouts and the view-model.
2. **A platform section was hardcoded.** The shared page contained a per-site block and a switch per
   site. Adding a site meant editing the page.
3. **Scope was implicit.** Some values were global keys; others lived in a site's container. Nothing
   declared which, and callers picked `get` versus `getGlobal` by hand.
4. **A setting was dead.** A notification toggle persisted a value, but the dispatcher never read it.
   Turning it off changed a number on disk while toasts kept arriving.
5. **Copy drifted from behavior.** The page advertised a cadence the service did not use, because the
   default lived in two places.
6. **A per-site boolean pair encoded a set invariant.** Switching every site off was possible in
   principle, and a crash between two writes could produce an invalid state.

These are the failure modes from `../references/failure-modes-and-anti-patterns.md`: hand-built page,
`if platform`, scope drift, dead setting, default drift, set invariant split.

---

## 3. The Design

```text
┌────────────────────────────────────────────────────────────────────┐
│ HOST CORE                                                          │
│                                                                    │
│  SettingsDescriptor      one row as data                           │
│  SettingsShape           closed renderer vocabulary                │
│  SettingsScope           global | per-source                       │
│  ISettingsContribution   Adds + Overrides per context              │
│  SourceContributionRegistry   enumerates contributions             │
│  SettingsCatalog.Compose      base + context layers, deterministic │
│  ScopedSettings          the one scope-to-container seam           │
│  SettingsRow renderer    draws the composed list                   │
└───────────────┬───────────────────────────────┬────────────────────┘
                │                               │
      ┌─────────▼─────────┐           ┌─────────▼─────────┐
      │ Source A module   │           │ Source B module   │
      │ descriptor        │           │ descriptor        │
      │ settings adds     │           │ settings adds     │
      │ settings patches  │           │ settings patches  │
      │ consumers         │           │ consumers         │
      └───────────────────┘           └───────────────────┘
```

### 3.1 The descriptor

One row carries identity, storage, constraints, copy, defaults, selectors and visibility:

```text
SettingsDescriptor
├── key, shape, scope, section, order
├── label, hint, hint tone, placeholder, unit
├── value kind, validation, error copy
├── min, max, step, options
├── default literal, or a default fact from the context descriptor
├── automation ids for each platform
└── visibility flag, LTR, password, bare editor, command
```

A descriptor is data. The renderer knows shapes, never keys.

### 3.2 The contribution

```text
ISourceSettingsContribution
├── Source            the context this contribution belongs to
├── Adds              full rows this module owns
└── Overrides         field-level patches on shared rows
```

A module registers its contribution in its composition entry point. The shared page never imports the
module.

### 3.3 Composition

```text
base rows at specificity 0
+ contributions for the active source at specificity 1
  ├── Adds: full rows, replace by key at that layer
  └── Overrides: patch only declared fields
sort by band rank, header first, row order, key
emit visible rows
drop overrides for missing keys and report them
```

Two patches at the same specificity setting one field fail loudly. Registration order is never a
tie-breaker.

### 3.4 Storage

```text
ScopedSettings.Read / Save / HasValue
    global      -> flat container
    per-source  -> the source's namespaced container
```

A namespaced read falls through to the legacy flat key, so existing installs keep their values. The
first write moves the value into the container (lazy migration). The opposite move (per-source to
global) uses a one-time harvest with a marker, because a global read has no fallback into a platform
container.

### 3.5 Consumers

Each behavior has one authority that both the row and the runtime read:

| Behavior | Authority | Why |
|---|---|---|
| Poll cadence | `SourceCadence` | One clamp shared by pipeline, live apply and caption |
| Source notifications | `NotificationMute` | The row, dispatcher and test share container and default |
| Platform enablement | `PlatformEnablement` | The set invariant and its refusal reason live in one place |

The authority reads through the scope seam. The row's default is the same constant the authority uses.

---

## 4. The Growth Edits

### 4.1 Add a setting

```text
Edit: the base catalog file, one descriptor entry.
Optional: the consumer in the owning module.
Forbidden: renderer, layout, view-model, other rows.
```

Example: add a bounded numeric row.

```text
new(key: "settings_example_seconds",
    shape: NumericBounded,
    scope: Global,
    section: "system",
    order: 15,
    valueKind: Int,
    min: 10, max: 3600,
    default: <same constant the consumer uses>,
    validation: IntRange,
    error: "Must be between {0} and {1}.",
    automationId: "Settings_ExampleInput")
```

The renderer draws it because the shape already exists. No shared UI changes.

### 4.2 Add a site or module

```text
Edit: the new module's descriptor, contribution class and composition registration.
Forbidden: settings page, composition engine, other modules.
```

The module contributes:

```text
Adds:
  a section header with its band rank
  its own toggle, with module-local keys
  two mutually exclusive read-outs gated by capability flags

Overrides:
  a patch on the shared cookie row changing only its label
```

The platform switches row enumerates the registry, so the new site appears without a row edit. The
new site is enabled by default because the stored value is the set of **disabled** ids, and the new id
is absent.

### 4.3 Add a control shape

```text
Edit: one shape enum member, one renderer branch, renderer tests.
This is a deliberate HOST extension.
Forbidden: a branch keyed by setting key, source id or label.
```

A shape is added when a genuinely new control is needed, not to special-case one row.

### 4.4 Add a storage scope

```text
Edit: one scope enum member, one storage-seam branch, migration tests.
This is a deliberate HOST extension.
Forbidden: callers choosing a container by hand.
```

A scope is added when a new axis exists (for example per-user above per-device). The seam is the only
place that maps scope to storage.

---

## 5. What the Seams Prevented

| Before | After | Seam |
|---|---|---|
| Adding a site edited the page | One module registration | Contribution registry |
| Adding a setting edited two layouts | One catalog entry | Descriptor plus closed shapes |
| Scope chosen by each caller | One read/write path | `ScopedSettings` |
| Global read after a scope move saw the default | One-time harvest with a marker | Migration rule |
| A dead notification toggle | Row and dispatcher share one authority | `NotificationMute` |
| Advertised cadence differed from the pipeline | Default from one constant, clamped by one function | `SourceCadence` |
| Per-site booleans could all be off | One atomic disabled set, refusal reason | `PlatformEnablement` |
| Two modules could silently fight over a field | Same-specificity failure | Composition engine |
| Removing a base row could crash a module | Missing-key overrides dropped and reported | Composition engine |

---

## 6. Tests That Made It Real

1. Every catalog key is unique.
2. Every rendered row comes from the catalog; no hand-built row exists.
3. Every call site's literal scope matches the catalog.
4. Every default equals the service fallback.
5. Two patches at one specificity on one field throw.
6. Removing a contribution leaves the host green.
7. A removed base row leaves the modules green (their overrides are ignored).
8. The composed list is stable when registrations are reordered.
9. A scope move reads an old-format fixture correctly.
10. An unknown platform id is inert.
11. A secret scan of the store and logs is clean.

---

## 7. Transferable Lessons

- **Settings are plugins.** The descriptor is the manifest; the contribution is the module; the
  registry is the loader; composition is the host.
- **Build-time is the default.** The code and consumers are compiled; only catalog rows and values
  are data. A mobile target makes this non-negotiable.
- **One seam per axis.** Scope, shapes, composition and discovery each have exactly one owner.
- **Fail loudly on real conflicts, softly on missing data.** Two contributions disagreeing is a
  design bug; an override for a deleted row is expected history.
- **One authority per behavior.** The row, the dispatcher and the test must read the same source, or
  copy will drift from behavior.
- **Measure the OCP gate with edits, not intentions.** Name the files a new setting or site changes.
  If shared code appears, the seam is wrong.

---

## 8. When This Design Is Too Much

Do not build a contribution registry for a single-tenant CLI with eight stable options. Rung 2 or 3 of
the maturity ladder is enough:

- one typed config object, or
- a small descriptor catalog with a single renderer.

Add the registry when a second axis appears and modules genuinely own their configuration. The cost is
composition rules and tests; pay it for growth.
