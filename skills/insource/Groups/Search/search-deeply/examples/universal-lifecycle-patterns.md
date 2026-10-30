# Universal Lifecycle Patterns (Illustrative)

These patterns are language- and domain-agnostic illustrations of the principles in the skill. They are not a complete solution for any specific stack or problem. Rename “resource”, “manager”, and “focus” to match the domain under study.

---

## 1. Ownership Hierarchy (Recommended Shape)

```
ContainerController          // owns focus / active-item selection + container state
    ↓
ResourceManager              // owns the pool, generation / epoch tokens, intent state
    ↓
ResourceInstance[]           // small fixed or bounded pool
    ↓
UnderlyingHandle / Surface   // the actual runtime object (connection, media element, worker, buffer, …)
    ↓
External dependency layer    // network, cache, hardware, service
```

Rationale: the container decides *which* item is focused; the manager decides *how* resources are acquired and released; the underlying handle never decides intent.

---

## 2. Intent versus Actual State

**Intent states** (owned by ResourceManager):

- IDLE
- PREPARE
- ACTIVATE
- PAUSE / HOLD
- RELEASE
- DISPOSE

**Actual runtime states** (observed from the underlying handle or runtime):

- EMPTY / UNINITIALIZED
- ACQUIRING / LOADING
- READY / HAVE_METADATA
- ACTIVE / RUNNING
- PAUSED / HELD
- WAITING / BACK-PRESSURED
- COMPLETED / ENDED
- ERROR
- DISPOSED

The manager never assumes that “I issued activate” means the resource is active. It waits for the corresponding actual signal or a timeout.

---

## 3. Generation / Epoch Token Pattern (Race Defense)

```text
onActivate(itemId):
  generation ← generation + 1
  myGen ← generation
  cancel previous token if any
  token ← new CancellationToken()
  acquire(itemId, token)
  when ready:
    if myGen ≠ generation: return   // stale
    if intent still ACTIVATE: drive(resource)
```

This pattern appears in every serious concurrent resource system.

---

## 4. Minimal Pool / Window Sizes (Starting Points)

These are *starting values*, not universal constants. They must be validated with long-session resource and performance measurements on the target environment.

| Role                        | Count | Notes                                      |
|-----------------------------|-------|--------------------------------------------|
| Active / focused            | 1     | Hard limit for exclusive resources         |
| Prepared / adjacent         | 1–2   | Previous + next or equivalent window       |
| Total live pool             | 2–4   | Beyond this, pressure usually rises quickly |

Adjust according to the cost of the resource (memory, hardware slots, network, etc.).

---

## 5. Cleanup Matrix (Excerpt)

| Event                              | Pause / Hold | Detach / Reset | Cancel | Dispose or return to pool | Keep light metadata |
|------------------------------------|--------------|----------------|--------|---------------------------|---------------------|
| Becomes adjacent / enters window   | —            | —              | —      | —                         | yes                 |
| Leaves preparation window          | yes          | yes            | yes    | return to pool            | yes                 |
| Removed from collection            | yes          | yes            | yes    | dispose                   | no                  |
| Page / session leave               | yes          | yes            | yes    | release window            | optional            |
| Application background             | yes          | optional       | —      | keep pool                 | yes                 |
| Application terminate              | —            | —              | —      | full dispose              | —                   |

---

## 6. Polyglot Sketch of Generation Guard

**TypeScript**

```ts
let generation = 0;
async function activate(id: string, signal: AbortSignal) {
  const myGen = ++generation;
  await acquire(id, signal);
  if (myGen !== generation || signal.aborted) return;
  await drive(resource);
}
```

**Go**

```go
var generation atomic.Uint64
func activate(ctx context.Context, id string) error {
  myGen := generation.Add(1)
  if err := acquire(ctx, id); err != nil { return err }
  if myGen != generation.Load() { return errStale }
  return drive()
}
```

**Python**

```python
generation = 0
async def activate(id: str, token: CancellationToken):
  nonlocal generation
  generation += 1
  my_gen = generation
  await acquire(id, token)
  if my_gen != generation or token.is_cancelled:
    return
  await drive()
```

**C#**

```csharp
long generation = 0;
async Task ActivateAsync(string id, CancellationToken ct)
{
  var myGen = Interlocked.Increment(ref generation);
  await AcquireAsync(id, ct);
  if (myGen != Interlocked.Read(ref generation) || ct.IsCancellationRequested) return;
  await DriveAsync();
}
```

The principle is identical across languages: a monotonically increasing token (or equivalent cancellation signal) that invalidates any in-flight work belonging to a previous activation.
