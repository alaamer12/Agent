# Settings & Plugin Architecture — <Project Name>

> Binding specification. Replace every `<...>` placeholder. Delete sections that do not apply and
> say why. Keep the decision tables; they are the review surface.

- **Status:** draft | agreed | superseded
- **Date:** <YYYY-MM-DD>
- **Owner:** <name or role>
- **Supersedes:** <doc or none>

---

## 1. Scope and Goals

- What problem does this architecture solve?
- Which surfaces are in scope: settings page, config service, per-tenant configuration, plugin host?
- What must stay out of scope?
- What does "growth" mean here: more settings, more platforms, more tenants, third-party plugins?

---

## 2. Growth Axes and the OCP Gate

| Axis | Current count | Expected in a year | Who adds one | Seam |
|---|---|---|---|---|
| Settings | <n> | <n> | <team> | <catalog file> |
| Platforms / sources | <n> | <n> | <team> | <contribution + registration> |
| Tenants | <n> | <n> | <ops> | <configuration> |
| Control shapes | <n> | <n> | <host team> | <shape plus renderer> |
| Storage scopes | <n> | <n> | <host team> | <scope plus seam> |

For each axis, answer: **which files change to add one?** List them. If shared code appears, move the
seam.

```text
Add setting N:        <files>
Add platform/tenant N: <files>
Add shape N:          <files>
Add scope N:          <files>
```

---

## 3. Build-Time vs Runtime Decision

One block per axis. See `references/build-time-vs-runtime.md` for the criteria.

| Axis | Choice | Payload | Reason | Revisit when |
|---|---|---|---|---|
| Code / behavior | build-time, runtime or hybrid | <what> | <why> | <trigger> |
| Catalog / metadata | <...> | <...> | <...> | <...> |
| Values | <...> | <...> | <...> | <...> |
| Defaults | <...> | <...> | <...> | <...> |
| Feature flags | <...> | <...> | <...> | <...> |
| Secrets | <secret manager> | <reference only> | <why> | <...> |

Platform constraints confirmed:

- [ ] Target platforms: <list>
- [ ] Any store policy forbidding downloaded code: <yes/no, citation>
- [ ] AOT, trimming or single-file constraints: <yes/no>
- [ ] Offline behavior required: <yes/no>
- [ ] Runtime code, if any, is signed and allowlisted: <yes/no/na>

---

## 4. Host Core

| Component | Responsibility | Location |
|---|---|---|
| Descriptor | <data shape of one setting> | <path> |
| Shape vocabulary | <closed set of renderable controls> | <path> |
| Scope vocabulary | <where a value lives> | <path> |
| Contribution contract | <adds and patches> | <path> |
| Registry | <discovery and enumeration> | <path> |
| Composition | <layers, specificity, collisions, ordering> | <path> |
| Storage seam | <scope to container> | <path> |
| Renderer | <draws a composed list> | <path> |
| Consumer authorities | <one per behavior> | <path> |

The host must not import a concrete contribution. State how that is enforced.

---

## 5. Descriptor Schema

| Field | Type | Required | Meaning |
|---|---|---|---|
| `key` | string | yes | Stable identity; never renamed after release |
| `shape` | enum | yes | Renderer vocabulary member |
| `scope` | enum | yes | Storage container |
| `section` | string | yes | Band or group |
| `order` | integer | yes | Position inside the band |
| `label` | string | yes | User-facing name |
| `hint` | string | no | Secondary line |
| `unit` | string | no | Display unit |
| `value_kind` | enum | yes | Bool, int, decimal, string, enum |
| `default` | literal or context fact | no | Shipped fallback |
| `min`, `max`, `step` | number | no | Bounds |
| `options` | list | no | Enum choices as stable values |
| `validation` | enum | no | Which validator runs |
| `error` | string | no | Error template |
| `visibility` | named predicate | no | Data-driven visibility |
| `platform_ids` | map | no | Test selectors per platform |
| `command` | string | no | Action or read-out binding |

Extra fields for this project:

| Field | Type | Meaning |
|---|---|---|
| <...> | <...> | <...> |

---

## 6. Contribution Contract

```text
interface SettingsContribution:
    contextId: ContextId
    adds:      list<Descriptor>          # full rows this context owns
    overrides: list<DescriptorPatch>     # only the fields changed

interface DescriptorPatch:
    key: string
    fields: map<FieldName, Value>        # exactly the fields set
```

Rules for this project:

- Module-local keys live where? <path>
- Which fields may a patch set? <list or all>
- Is a full replace allowed for a base key? <yes/no and why>
- How is an ignored override reported? <log, test, diagnostic>

---

## 7. Registry and Discovery

| Question | Answer |
|---|---|
| How is a contribution registered? | <DI collection, static list, scan, manifest> |
| Where is the composition root? | <path> |
| How is a duplicate registration detected? | <test or failure> |
| How is a removed contribution made inert? | <drop rows, ignore ids> |
| Is discovery build-time or runtime? | <choice and reason> |

---

## 8. Composition and Precedence

| Layer | Specificity | Example | May add | May patch |
|---|---|---|---|---|
| Base | 0 | shipped catalog | yes | no |
| Context | 1 | platform, tenant, plan | yes | yes |
| Narrow | 2 | user, device, experiment | yes | yes |
| Tie-breaker | 3 | named exception | yes | yes |

Conflict policy:

- Same specificity, same field: <fail build | fail test | explicit tie-breaker required>
- Patch for a missing key: <drop with report>
- Full replace of a base row: <allowed only when ...>
- Ordering: <band rank, then header-first, then row order, then key>
- Result mutability: <immutable list>

---

## 9. Storage and Scope

| Scope | Container | Who writes | Migration |
|---|---|---|---|
| Global | <flat key-value> | <app settings> | <none> |
| Per-context | <namespaced container or table> | <row> | <lazy read-through> |
| Per-user | <...> | <...> | <...> |

- Types stored: <bool, int, decimal, string, enum>
- Composite values split: <money, duration, range, phone, address, ...>
- Presence check: <how "unset" is distinguished from "set to default">
- Set invariants: <which set, how written atomically>
- Legacy keys: <list and alias window>
- Validation: <where and which kinds>
- Concurrency: <last-write-wins or versioned>
- Secrets: <store and reference shape>

---

## 10. Renderer Shapes

| Shape | Control | Notes |
|---|---|---|
| Toggle | <switch> | <...> |
| Numeric | <bounded input> | <unit, step> |
| Text | <entry> | <LTR isolation> |
| Enum | <picker> | <stable values, not indices> |
| Multi-select | <chips> | <...> |
| Action | <button> | <command> |
| Read-out | <stat> | <source> |
| Section header | <label + icon> | <band rank> |
| <custom> | <...> | <why a new shape is justified> |

Adding a shape is a **host change**: <one enum member plus one renderer branch plus tests>.

---

## 11. Consumers and Authorities

Every behavior names one authority that both the row and the runtime read.

| Behavior | Authority | Reads | Default | Test |
|---|---|---|---|---|
| <poll cadence> | <class> | <scope seam> | <constant> | <test> |
| <notifications> | <class> | <...> | <...> | <...> |
| <rate limit> | <class> | <...> | <...> | <...> |

Rules:

- No consumer reads the store directly; all go through the authority.
- No authority duplicates the row's default or bounds.
- The row's hint describes what the authority actually does.

---

## 12. Migration and Compatibility

| Change | Strategy | Marker | Rollback |
|---|---|---|---|
| Flat to namespaced | Read-through, write-on-first-save | none | Old build reads flat |
| Namespaced to flat | One-time harvest, explicit value wins | <marker> | Losing copies retained |
| Key rename | Alias read, write new | <alias window> | Alias removed later |
| Type change | New key, backfill, switch reads | <version> | Old key retained |

- Fixtures: <old-format values>
- Cleanup policy: <when legacy data is deleted, if ever>
- Unknown id behavior: <inert>

---

## 13. Security and Trust

- [ ] No secret in the settings store, export or logs.
- [ ] Runtime code, if any, is signed and allowlisted.
- [ ] Plugins receive capability tokens, not ambient authority.
- [ ] Tenant identity is enforced by the host.
- [ ] Resource limits: <cpu, memory, time, network>.
- [ ] Revocation is immediate and audited.
- [ ] Remote catalogs are schema-validated and never evaluated as code.

---

## 14. Failure Isolation

| Failure | Behavior | User sees | Log |
|---|---|---|---|
| Bad row | Drop and report | Row absent | Key and reason |
| Bad override | Ignore and report | Base row | Key |
| Unknown id | Skip | Nothing | Id and scope |
| Plugin activation failure | Disable | Reason | Id, version, error |
| Timeout | Abort call | Retry or disabled | Duration |
| Repeated failure | Circuit breaker | Disabled with reason | Count |

---

## 15. Checks

List the executable checks this specification requires.

- [ ] No concrete plugin/platform/tenant name in shared code.
- [ ] Every key has one descriptor and one reader.
- [ ] Every rendered row comes from the catalog.
- [ ] Every read goes through the scope seam; literal scopes match the catalog.
- [ ] Every default equals the consumer fallback.
- [ ] Every bound matches the consumer limit.
- [ ] Same-specificity patches on one field fail.
- [ ] Deleting a contribution leaves the host green.
- [ ] Shuffled registration order yields the same list.
- [ ] Unknown key, id and enum are inert.
- [ ] A secret scan of store, export and logs is clean.
- [ ] Migration fixtures pass in both directions.

---

## 16. Known Exceptions

| Exception | Why | Approved by | Revisit |
|---|---|---|---|
| <...> | <...> | <...> | <...> |

A deliberate exception is recorded once here, with its reason. It is not re-argued at every review.

---

## 17. Change Log

| Date | Change | Reason |
|---|---|---|
| <YYYY-MM-DD> | <...> | <...> |
