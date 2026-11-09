# Plugin and Settings Contract — <Project Name>

> Fill this in when the contract is shared across modules, teams or releases. The contract is the
> only thing the host and a contribution are allowed to know about each other.

- **Contract version:** <major.minor.patch>
- **Supported host range:** <e.g. 2.x>
- **Status:** draft | agreed | deprecated

---

## 1. Vocabulary

| Term | Meaning in this project |
|---|---|
| Host | <the closed runtime that loads, composes and isolates> |
| Contribution | <a module that adds settings rows, behavior or both> |
| Descriptor | <the data shape of one setting> |
| Patch | <a field-level override of an existing descriptor> |
| Context | <the coordinate a contribution is registered for: platform, tenant, plan> |
| Scope | <where a value is stored: global, per-context, per-user> |
| Shape | <a renderable control the host knows how to draw> |
| Authority | <the one function or class that answers a behavior> |

---

## 2. Host Interface

Only these members are stable. Everything else is internal and may change.

```text
Host:
    register(contribution: Contribution) -> void      # composition time
    compose(context: Context) -> list<Descriptor>      # pure, deterministic
    read(descriptor, context, fallback) -> Value        # scope-aware
    write(descriptor, context, value) -> void           # validated, scope-aware
    contains(descriptor, context) -> bool               # presence for the same scope
    capabilities(context) -> CapabilitySet              # what the host permits
```

Rules:

- `compose` is pure and must return the same list for the same inputs.
- `read`, `write` and `contains` go through the scope seam; the caller never names a container.
- `capabilities` is how a contribution asks for a permission; it never reaches the storage backend
  directly.

---

## 3. Contribution Interface

```text
Contribution:
    contextId: ContextId
    adds:      list<Descriptor>
    overrides: list<Patch>
    activate(host: Host) -> void        # optional, code contributions only
    deactivate() -> void                # optional, must be idempotent
```

| Member | Required | Must not |
|---|---|---|
| `contextId` | yes | be inferred from a name inside shared code |
| `adds` | no | mutate another contribution's rows |
| `overrides` | no | restate a full descriptor when only one field changes |
| `activate` | no | register global state, timers or listeners without cleanup |
| `deactivate` | if `activate` exists | throw on a second call |

---

## 4. Descriptor Fields

| Field | Type | Required | Validation |
|---|---|---|---|
| `key` | stable string | yes | unique, kebab or namespace-qualified |
| `shape` | host enum | yes | must exist in the renderer vocabulary |
| `scope` | host enum | yes | must exist in the storage seam |
| `section` | string | yes | non-empty |
| `order` | integer | yes | deterministic within a section |
| `label` | string | yes | non-empty |
| `hint` | string | no | — |
| `unit` | string | no | display only |
| `valueKind` | host enum | yes | matches the stored type |
| `default` | literal or context fact | no | equals the consumer fallback |
| `min`, `max`, `step` | number | no | reflect the consumer's real limit |
| `options` | list of stable values | no | required for enum shapes |
| `validation` | host enum | no | implemented by the host |
| `error` | template string | no | placeholders documented |
| `visibility` | named predicate | no | unknown predicate means visible |
| `platformIds` | map | no | test selectors only |
| `command` | string | no | registered by the host or the contributor |

---

## 5. Patch Rules

```text
Patch:
    key: string
    fields: exactly the fields this layer sets
```

1. Only declared fields are applied; the rest come from the lower layer.
2. Two patches at equal specificity setting one field is a failure, not a merge.
3. A patch for a missing key is ignored and reported.
4. A patch never changes identity (`key`, `scope`) without an explicit migration.

---

## 6. Manifest for Runtime Contributions

Use only when runtime code is permitted and trusted.

```json
{
  "id": "acme.exporter",
  "name": "Acme Exporter",
  "version": "1.4.0",
  "contractVersion": "2.1",
  "hostRange": ">=2.1 <3",
  "entry": "dist/index.js",
  "signature": "<detached signature>",
  "capabilities": ["settings:add", "http:outbound:acme.example"],
  "settings": [
    {
      "key": "acme.export.enabled",
      "shape": "toggle",
      "scope": "per-tenant",
      "section": "acme",
      "order": 10,
      "label": "Enable export",
      "valueKind": "bool",
      "default": false
    }
  ]
}
```

| Field | Meaning | Host action when invalid |
|---|---|---|
| `id` | Stable contribution identity | Reject activation |
| `version` | Contribution version | Record for support |
| `contractVersion` | Contract the plugin was built against | Reject outside the host range |
| `signature` | Detached signature over the package | Reject if unverifiable |
| `capabilities` | Requested capabilities | Grant only the allowlisted subset |
| `settings` | Descriptor rows, same schema as build-time | Validate each row; drop invalid rows with a report |

---

## 7. Polyglot Shape

The names differ; the contract does not. Keep the same fields and the same rules.

### TypeScript

```ts
export interface SettingDescriptor {
  key: string;
  shape: SettingShape;
  scope: SettingScope;
  section: string;
  order: number;
  label: string;
  hint?: string;
  valueKind: "bool" | "int" | "decimal" | "string" | "enum";
  defaultValue?: unknown;
  min?: number;
  max?: number;
  options?: readonly { value: string; label: string }[];
  validation?: "none" | "range" | "min" | "enum" | "parse";
  visibility?: string;
}

export interface SettingsContribution {
  readonly contextId: string;
  readonly adds: readonly SettingDescriptor[];
  readonly overrides: readonly SettingPatch[];
}
```

### C#

```csharp
public sealed record SettingsDescriptor(
    string Key,
    SettingsShape Shape,
    SettingsScope Scope,
    string Label,
    string Section,
    int Order);

public interface ISettingsContribution
{
    string ContextId { get; }
    IReadOnlyList<SettingsDescriptor> Adds { get; }
    IReadOnlyList<SettingsPatch> Overrides { get; }
}
```

### Python

```python
from dataclasses import dataclass, field
from typing import Literal

@dataclass(frozen=True)
class SettingsDescriptor:
    key: str
    shape: Literal["toggle", "number", "text", "enum", "action", "stat"]
    scope: Literal["global", "context", "user"]
    label: str
    section: str
    order: int
    value_kind: Literal["bool", "int", "decimal", "string", "enum"] = "string"
    default: object | None = None
    min: int | None = None
    max: int | None = None

@dataclass(frozen=True)
class SettingsContribution:
    context_id: str
    adds: list[SettingsDescriptor] = field(default_factory=list)
    overrides: list[dict] = field(default_factory=list)
```

### Go

```go
type Descriptor struct {
    Key       string
    Shape     Shape
    Scope     Scope
    Label     string
    Section   string
    Order     int
    ValueKind ValueKind
    Default   any
    Min       *int
    Max       *int
}

type Contribution interface {
    ContextID() string
    Adds() []Descriptor
    Overrides() []Patch
}
```

---

## 8. Versioning and Compatibility

| Change | Breaking? | Action |
|---|---|---|
| Add an optional descriptor field | No | Host defaults it |
| Add a shape | No for data, host work | Renderer branch plus tests |
| Add a scope | Host work | Seam branch plus migration |
| Rename a key | Yes | Alias read plus a deprecation window |
| Remove a field | Yes | Keep reading it for the window, then reject |
| Change a value type | Yes | New key, backfill, switch reads |
| Change a shape's meaning | Yes | New shape; never repurpose |

Deprecation window for this project: <duration and process>.

---

## 9. Activation and Isolation

```text
activate:
    verify signature and host range
    validate manifest and rows
    grant only allowlisted capabilities
    call activate under a timeout
    record id, version, capabilities
    on failure: disable with a reason, keep the host running
```

- Every host call into a contribution has a deadline.
- A repeated failure opens the breaker and disables the contribution.
- `deactivate` releases subscriptions, timers, handles and workers.
- Reload must be idempotent; test by activating N times and counting resources.

---

## 10. Contribution Checklist

- [ ] Identity is stable and namespaced.
- [ ] Adds and overrides are immutable data.
- [ ] Module-local keys stay in the module.
- [ ] No shared file names this contribution.
- [ ] The contribution can be deleted without a host edit.
- [ ] Defaults match the consumer.
- [ ] Patches set only the changed fields.
- [ ] Activation failure is isolated and reversible.
- [ ] Deactivation cleans up every resource.
- [ ] The contract version is declared and tested.

---

## 11. Change Log

| Contract version | Date | Change | Migration |
|---|---|---|---|
| <x.y> | <YYYY-MM-DD> | <...> | <...> |
