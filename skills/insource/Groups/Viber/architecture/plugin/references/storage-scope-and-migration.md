# Storage, Scope and Migration

Settings storage fails in quiet ways: a value is written to one container and read from another, a
scope changes and the old value becomes invisible, or a formatted string becomes the source of truth.
This reference defines the storage seam, the scope vocabulary, and the migration rules that keep a
changing settings model from losing user data.

---

## 1. Scope Is a First-Class Field

Every setting declares **where its value lives**, not just what it is.

```text
scope: global      one value shared by every context (app behavior)
scope: per-source  one value per platform, tenant, user or device
scope: per-user    one value per signed-in user, above the device
scope: per-tenant  one value per organization, below the user
```

The scope is **architecture**, not presentation. It decides which container is read and written. A row
that says "on all platforms" while its value lives in one platform's container is a lie caused by a
missing scope contract.

Rules:

1. Declare scope once, on the descriptor.
2. Enforce it in one seam. Callers pass the descriptor or the scope; they never pick a container.
3. A scope change is a migration, not a field edit.
4. A capability fact (a site's minimum poll interval, a tenant's plan limit) is **not** a setting
   scope. It lives on the context descriptor and may clamp a shared value.
5. Keep the scope vocabulary closed. Adding a scope is a host change with tests, not a per-row string.

---

## 2. The Single Seam

```text
read(descriptor, context, fallback):
    if descriptor.scope == global: return store.getGlobal(descriptor.key, fallback)
    else:                          return store.get(context, descriptor.key, fallback)

write(descriptor, context, value):
    if descriptor.scope == global: store.setGlobal(descriptor.key, value)
    else:                          store.set(context, descriptor.key, value)

contains(descriptor, context):
    if descriptor.scope == global: return store.containsGlobal(descriptor.key)
    else:                          return store.contains(context, descriptor.key)
```

Why one seam:

- A caller that chooses `get` versus `getGlobal` by hand will eventually choose wrong, especially after
  a scope change.
- Tests can assert that every call site uses the seam and that its literal scope matches the catalog.
- The seam is the only place that knows the container mapping; the rest of the app knows descriptors.

A call site that holds only a key may pass an explicit scope, but a lint or test must compare that
literal to the catalog and fail on disagreement.

---

## 3. Storage Backends

| Backend | Good for | Watch out for |
|---|---|---|
| Key-value (Preferences, localStorage) | Small scalar values, offline-first | No query, no transaction, type loss on read |
| Relational table | Many rows, audit, multi-tenant | Schema and migrations, connection scope |
| JSON file | CLI, single-user desktop | Concurrent writes, partial corruption |
| Environment variables | Deployment facts, secrets references | Not user-editable at runtime, restart needed |
| Remote config | Fleet-wide flags and defaults | Network dependency, schema drift, tampering |

Whatever the backend, the **contract** is the same: typed read, typed write, explicit scope, explicit
default, explicit presence check.

### Relational shape

```sql
create table settings (
  scope_kind   text not null,          -- global | tenant | user | source
  scope_id     text not null,          -- '' for global, otherwise the context id
  key          text not null,
  value_type   text not null,          -- bool | int | decimal | string | enum
  value_text   text,                   -- canonical serialized value
  updated_at   timestamp not null,
  version      integer not null default 1,
  primary key (scope_kind, scope_id, key)
);
```

- Store canonical scalars, not display strings.
- Add a `value_type` so a read can reject a type mismatch instead of coercing silently.
- Index by scope for rendering one context's settings.
- Keep a version for optimistic concurrency when multiple windows can edit.

### Key-value shape

- One container per scope id, named deterministically from the context descriptor.
- A namespaced read falls back to the legacy flat key; the first write moves the value.
- Presence checks must ask the same scope they read, or they answer about a different container.

---

## 4. Typed Values and Atomic Fields

A settings value is a primitive or a small structured record, never a formatted display string.

| Bad | Why | Good |
|---|---|---|
| `price = "$12.50"` | Currency, amount and formatting in one field | `amount_minor = 1250`, `currency = "USD"` |
| `duration = "5 min"` | Number and unit inseparable | `value = 5`, `unit = "min"` |
| `size = "12kg"` | Unit lost on conversion | `value = 12`, `unit = "kg"` |
| `enabled = "yes"` | Locale and type ambiguity | `enabled = true` |
| `range = "10-20"` | Cannot compare or validate per bound | `min = 10`, `max = 20` |
| `tags = "a,b,c"` | Escaping and empty-element bugs | a list type, or a join table |

The same rule as any data model: if a value encodes more than one primitive, split it. Formatting
belongs in the renderer; parsing belongs at the boundary; storage stays atomic.

Three-state values need an explicit representation:

- Nullable boolean with documented semantics (`null` = never asked, `false` = declined).
- Or an enum (`unknown`, `granted`, `denied`) plus a timestamp.
- `contains(key)` is how you distinguish "unset" from "set to the type's default". A fallback read
  cannot answer that question.

---

## 5. Set Invariants

When the setting is "which items are enabled", store the **set**, not one boolean per item.

```text
disabled = "platform-c,platform-f"      # one atomic value
```

Why:

- The invariant ("at least one enabled") is a property of the set. N booleans require N writes; a crash
  between writes can leave zero enabled.
- A newly added item is enabled by default because it is simply absent from the disabled set.
- A removed item's id left in the set is inert, not fatal.
- The UI can derive every switch from the set plus the registry.

Rules:

1. One atomic write for a set invariant.
2. Unknown ids are ignored, not an error.
3. The set is ordered deterministically before writing, so diffs are stable.
4. The refusal reason is a stable key, not a sentence; the row owns the copy.
5. A stale view or second window is re-checked at the write, not only in the UI.

---

## 6. Migration

Settings schemas change for three reasons: a value moves scope, a key is renamed, or a value's type or
shape changes. Treat each as a migration with a marker and a test.

### 6.1 Adding a scope (flat to namespaced)

Lazy, lossless, no downtime:

```text
read(context, key):
    if namespaced container contains key: return it
    if legacy flat container contains key: return it      # read-through
    return fallback

write(context, key, value):
    write namespaced only                                  # first write migrates
```

The legacy copy becomes dead data the next read ignores. Never delete it on a read.

### 6.2 Removing a scope (namespaced to flat)

There is no automatic fallback in this direction: a global read does not look in a platform container.
Harvest explicitly, once:

```text
if marker not present:
    for each moved key:
        if global already has a value: skip                 # user wins
        else copy from active context, then any other context
    stamp marker
```

Precedence: an explicit global value wins; otherwise the active context (the value the user last saw);
otherwise any context that has one. Keep the losing copies on disk; deleting user data is not a
migration's call.

### 6.3 Renaming a key

- Read the new key; if absent, read the old key; write the new key on first save.
- Keep an alias map with the old key and the type, so a typed read is possible.
- Retire the alias only after a documented window.

### 6.4 Changing a type or shape

- Never reinterpret existing bytes in place.
- Introduce a new key or a versioned value, backfill, then switch reads.
- Keep a reversible step; a rollback must not lose values written after the migration.

### 6.5 Migration checklist

1. A marker key or a version row, written once.
2. Idempotent: running twice changes nothing.
3. Never overwrites an explicit newer value.
4. Never deletes the source until a later, deliberate cleanup.
5. Logs what moved, with key and source.
6. A test with old-format fixtures proves the new read sees the old value.
7. A rollback rehearsal proves the old build still reads something sane.

---

## 7. Defaults, Presence and Precedence

```text
effective value =
    explicit user value
    else explicit context value
    else environment or deployment value
    else shipped default
```

- The shipped default is a constant shared with the consumer.
- The environment value is validated at boot and fails fast on a missing required key.
- `contains` answers presence for the scope being read; a fallback does not.
- A tri-state seed (theme) needs presence, because "unset" and "set to the default" are different.
- Never infer presence from "the read equals the default".

Document the precedence once. Different layers disagreeing silently is a support ticket generator.

---

## 8. Validation, Concurrency and Secrets

### Validation

- Validate shape, range and enum membership at the write boundary.
- Re-validate on read for values that may predate a constraint; clamp or report, never crash.
- An invalid row is dropped with a diagnostic; it must not blank the page.
- Error copy lives on the row, not in the validator.

### Concurrency

- Multiple windows or devices can write the same key. Decide: last write wins, or optimistic version
  check with a conflict message.
- A set invariant is written as one value, so two writers cannot interleave halves.
- Deferred writes (for keystroke-heavy inputs) need a deterministic flush on save and teardown.

### Secrets

- A secret never lives in settings, a catalog, a log or an export.
- Settings may hold a reference: a secret id, a key name, a public client id.
- A cookie editor stores the cookie in a secret store, not in the preference container.
- Redact secret values in diagnostics and never print them in an audit report.

---

## 9. Export, Backup and Reset

- Export must be typed and versioned, not a dump of raw strings.
- Import validates before writing and reports rejected keys.
- A reset can target one scope or one key; a global reset is explicit and confirmed.
- Secrets are excluded from export by default.
- A backup taken before a migration is the cheapest rollback.

---

## 10. Storage Checks

1. Every setting has a scope and a value kind in its descriptor.
2. Every call site reads through the seam; no direct container choice remains.
3. Every literal scope at a call site matches the catalog.
4. Every default equals the consumer's fallback.
5. A value round-trips through the store with the same type.
6. A set invariant is one atomic value, and a crash test cannot produce an invalid set.
7. An old-format fixture is read correctly after the migration.
8. An unknown id, key or enum value is inert, not fatal.
9. No secret is present in the settings store, export or logs.
10. Multi-window writes produce a defined outcome.
