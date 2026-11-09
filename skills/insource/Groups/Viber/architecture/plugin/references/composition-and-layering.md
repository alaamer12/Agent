# Composition and Layering

A registry without composition rules becomes a pile. This reference defines how base rows,
contributions and patches combine into one deterministic result, and how conflicts fail.

---

## 1. The Layers

```text
specificity 0   base layer            every shipped row, no context
specificity 1   context layer         per platform, tenant, plan, region or module
specificity 2   narrower context      per user, per device, per experiment
specificity 3   explicit tie-breaker  a named exception, rare and reviewed
```

A row is registered at a coordinate such as `{source: nafezly}` or `{tenant: acme}`. A contribution
for coordinates the current context does not satisfy is simply absent; that is normal for a
collection seam, not an error.

Higher specificity wins. Equal specificity does not resolve by arrival order.

---

## 2. Two Contribution Kinds

### Additive

A full descriptor for a key that may or may not exist in the base.

```text
Adds: [
  section header for this module,
  its own rows,
  its own read-outs,
]
```

- A new key is appended.
- A full descriptor for an existing key **replaces** it at that layer.
- Module-local keys stay in the module; shared code never learns them.

### Patch

A partial record that changes only the fields it names.

```text
Overrides: [
  patch("session-cookie") { label: "...", hint: "..." },
]
```

- Unnamed fields keep the value from the base or the previous layer.
- A patch naming a missing key is **dropped** and reported, never fatal. Removing a base row must not
  break the module that once customized it.
- A patch must not restate the whole descriptor; that is a replace, not a patch.

Why the distinction matters: a replace resets every field (including future fields the module never
knew about), while a patch survives base evolution. Prefer patches for copy and bounds; use replaces
only when the module genuinely owns the row.

---

## 3. Field Ownership

A patch declares which fields it sets. Composition tracks the owner per field.

```text
for each registration at increasing specificity:
    for each field the patch sets:
        if field already owned at the SAME specificity:
            fail loudly (ambiguous layer)
        record owner
        apply field
```

Rules:

1. **Same specificity, same field** is a design conflict. Throw or fail the build. Never pick one.
2. **Different specificity** is a legitimate override. Higher wins.
3. **Different fields at the same specificity** is fine; merge both.
4. **A full replace** clears ownership and starts again from the replacing layer.
5. **A tie-breaker layer** exists to resolve a real conflict explicitly, with a name and a comment.

The failure must name the seam and the two layers. A silent winner is a bug that appears months later
as "why is this label wrong on one tenant?".

---

## 4. Deterministic Ordering

Never order by registration, dictionary enumeration or file system order.

**Ordering is data.** Two common models:

### Band rank

A section header carries the rank of its band; every row carries its position inside the band.

```text
section header "system"   order 0
section header "platform" order 10
section header "module"   order 12
section header "actions"  order 90
row inside "platform"     order 20, 50, 60
```

Sort by band rank, then header first, then row order, then key as a stable tie-break. A contributed
section places itself with data; the host never learns its name.

### Explicit sort key

A single monotonic number per row when bands are unnecessary. Still add the key as a final tie-break
so the result is total.

Do not let a section header's own numeric order mean both "band rank" and "position inside the band".
That ambiguity makes a row in one band jump above another band. Separate the two concepts or document
the exact rule.

---

## 5. Composition Algorithm

```text
compose(context, baseLayer, contributions):
    groups = map key -> list of registrations
    register base rows at specificity 0
    for each contribution:
        coordinate = coordinateFor(contribution)
        register its Adds at that coordinate
        collect its Overrides as patches

    for each key:
        chain = matching registrations sorted by specificity, then stable key
        if chain is empty: skip            # additive seam, not a missing base
        value = chain[0]
        for each later full registration: value = it; clear field owners
        for each patch at increasing specificity:
            for each field it sets:
                assert no same-specificity owner
                value[field] = patch[field]
        if value.visible and predicate(value.visibilityFlag, context):
            emit value

    sort emitted rows by band rank, header-first, row order, key
    return emitted rows plus ignored overrides
```

The result is immutable. The renderer receives a plain list and never composes.

---

## 6. Visibility

Visibility is data, not a renderer branch.

```text
visibilityFlag: "NeedsSessionForFullEnrichment"
visibilityFlag: "HasCurrency"
visibilityFlag: "Never"          # temporarily hide without deleting
```

Evaluate the named predicate against the live context descriptor. Rules:

- An unknown flag stays visible and is reported. A typo should fail review, not silently hide a row.
- A module that needs the negative condition contributes a named negative flag
  (`WorksWithoutSession`) rather than asking the host to branch on a capability.
- Mutually exclusive read-outs are two rows with opposite flags, so the choice stays in data.
- Visibility never changes storage. A hidden row still has a scope and a value.

---

## 7. Defaults and Consumer Agreement

A default is part of the contract between the row and the consumer.

- The row's default literal and the consumer's fallback must be the **same constant**.
- If a default depends on the context (a platform's rate limit), expose it as a named fact on the
  context descriptor, not a literal in the row.
- A system-wide row must not take a per-context default; that would make the advertised value depend
  on which context happens to be open.
- Test that every default in the catalog equals the value the service uses on an untouched install.

A row that advertises 60 while the service defaults to 30 is worse than no row: it trains users to
distrust Settings.

---

## 8. Validation

Validation is declared per row and runs before a write is queued.

| Kind | Input | Shared with |
|---|---|---|
| Range | `min`, `max` | The consumer's clamp or pool limits |
| Minimum | `min` | The consumer's rejection rule |
| Enum membership | option values | The consumer's parser |
| Structured parse | cookie, URL, list | The module's parser |

Rules:

- Do not invent a maximum the consumer does not enforce, or a minimum it does not reject.
- Validate at the boundary and again before persistence if the value can arrive from outside the UI.
- Error copy is data on the row, with placeholders for bounds and the offending value.
- An invalid value never reaches storage; a stored legacy value that no longer validates is clamped or
  reported, not crashed on.

---

## 9. Worked Example

Base catalog:

```text
key: max-requests-per-minute   scope: per-source   min: 1   default: from context
key: session-cookie            scope: per-source   shape: cookie
```

Module A contributes a replace for its own row:

```text
key: module-a-retry   scope: per-source   shape: toggle   default: true
```

Module B patches shared copy only:

```text
patch(session-cookie) { label: "Upload the session file for B" }
```

Composition for module B:

```text
max-requests-per-minute  -> base, default from B's descriptor
session-cookie           -> base + B's label patch, all other fields from base
module-a-retry           -> absent: registered for A, not B
```

Composition for module A:

```text
max-requests-per-minute  -> base
session-cookie           -> base, shared label
module-a-retry           -> A's row
```

No shared file changed. No module sees the other's rows. Deleting module A removes its row and leaves
B untouched. Adding module C is one registration.

---

## 10. Checks That Must Exist

1. **Every base key is unique.** Duplicate keys are a build failure, not a last-wins merge.
2. **Every patch names an existing key or is reported as ignored.**
3. **Two patches at the same specificity on one field fail.**
4. **The composed list is stable across reordered registrations.**
5. **Every visible row has a descriptor and every descriptor has a stable key.**
6. **Every setting key has a reader** (a call-site lint, a search test, or a registry of consumers).
7. **Every rendered row came from the catalog;** no hand-built row exists.
8. **Every default equals the consumer's fallback.**
9. **Deleting a contribution leaves the host green.**
10. **Adding a contribution touches only its file and the composition root.**

---

## 11. Anti-Patterns

| Anti-pattern | Symptom | Fix |
|---|---|---|
| Merge by arrival order | Output changes when registration order changes | Explicit specificity plus stable tie-break |
| Last-wins silently | Two modules disagree and nobody knows | Same-specificity failure with both layer names |
| Full replace used as patch | A base field resets to default after an update | Field-level patch |
| Patch restates the descriptor | Duplicated copy drifts | Patch only the changed fields |
| Override crashes on a missing key | Deleting a base row breaks a module | Drop and report ignored overrides |
| Section order doubles as row order | A row jumps above another section | Separate band rank from in-band order |
| Unknown visibility flag hides the row | A typo silently removes a setting | Unknown means visible plus a report |
| Default duplicated in the row and service | Advertised value disagrees with behavior | One shared constant or a context fact |
| Composition inside the renderer | Renderer grows conditionals per module | Compose once, render a plain list |
| Mutable shared list | One module's removal deletes another's row | Immutable contributions plus registry |
