# Fact sources in five ecosystems (plus one with no UI at all)

> The same two sources — one owned State, one read-only Condition — expressed per framework, with the create-vs-listen test marked at the exact line that decides it. Rules being expressed: [`../references/ownership.md`](../references/ownership.md) §2–§5. What *consumes* these values is out of scope here — in a UI, that is the `/pvc` skill's View/Rendition boundary.
>
> Frameworks are illustrative, not a supported set: any system with requests and subscriptions maps through the same four questions in §7.

## 1. React / TypeScript

```tsx
// shared/conditions/useNetworkCondition.ts
export function useNetworkCondition() {
  const [isOnline, setIsOnline] = useState(() => navigator.onLine);
  useEffect(() => {
    const on = () => setIsOnline(true);
    const off = () => setIsOnline(false);
    window.addEventListener("online", on);          // ← LISTENS: the browser caused this
    window.addEventListener("offline", off);
    return () => {                                   // released per consumer
      window.removeEventListener("online", on);
      window.removeEventListener("offline", off);
    };
  }, []);
  return { isOnline };                               // data only; no setter exposed
}

// features/search/behaviour/useSearchState.ts
export function useSearchState(query: string) {
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [results, setResults] = useState<Hit[]>([]);
  const [nonce, setNonce] = useState(0);

  useEffect(() => {
    if (!query) { setStatus("idle"); return; }
    const controller = new AbortController();
    setStatus("loading");
    fetchResults(query, controller.signal)           // ← CREATES: this consumer caused it
      .then(setResults)
      .then(() => setStatus("success"))
      .catch((e) => { if (e.name !== "AbortError") setStatus("error"); });
    return () => controller.abort();                 // ownership means destroying it too
  }, [query, nonce]);

  return { status, results, retry: () => setNonce((n) => n + 1) };
}
```

**Pass-through wrappers** ([`ownership.md`](../references/ownership.md) §5) — the generic layer still holds the effect, so the caller still owns:

```tsx
export function useAsyncState<T>(fetcher: (signal: AbortSignal) => Promise<T>, deps: unknown[]) {
  /* issues the request, aborts on cleanup — the ONLY place fetch() appears */
}
export function useSearchState(q: string) { return useAsyncState((s) => fetchResults(q, s), [q]); }

export function useBrowserEventCondition(on: string, off: string) { /* add/removeEventListener */ }
export const useNetworkCondition = () => ({ isOnline: useBrowserEventCondition("online", "offline") });
```

## 2. Vue 3 / TypeScript

The read-only surface is a framework feature here, not a convention:

```ts
import { onScopeDispose, readonly, ref } from "vue";

export function useNetworkCondition() {
  const isOnline = ref(navigator.onLine);
  const on = () => (isOnline.value = true), off = () => (isOnline.value = false);
  window.addEventListener("online", on);             // LISTENS
  window.addEventListener("offline", off);
  onScopeDispose(() => {
    window.removeEventListener("online", on);
    window.removeEventListener("offline", off);
  });
  return { isOnline: readonly(isOnline) };           // writers cannot reach a Condition
}

export function useSearchState(query: Ref<string>) {
  const status = ref<"idle" | "loading" | "success" | "error">("idle");
  const results = ref<Hit[]>([]);
  let controller: AbortController | null = null;

  async function run() {
    controller?.abort();
    if (!query.value) { status.value = "idle"; return; }
    controller = new AbortController();              // CREATES
    status.value = "loading";
    try { results.value = await fetchResults(query.value, controller.signal); status.value = "success"; }
    catch (e) { if ((e as Error).name !== "AbortError") status.value = "error"; }
  }
  const stop = watchEffect(() => { query.value; run(); });
  onScopeDispose(() => { stop(); controller?.abort(); });
  return { status, results, retry: run };
}
```

Store caveat: a Pinia/Vuex store is a *source*, so `useXStore()` inside a consumer is a fact read. If that read is what decides an outcome, the consumer is doing the deciding, not the store — and the store should expose the value, never the verdict.

## 3. Solid / TypeScript

Sources return **accessors**, never values, or reactivity is lost at the boundary:

```ts
export function createNetworkCondition() {
  const [isOnline, setIsOnline] = createSignal(navigator.onLine);
  const on = () => setIsOnline(true), off = () => setIsOnline(false);
  window.addEventListener("online", on);             // LISTENS
  window.addEventListener("offline", off);
  onCleanup(() => { window.removeEventListener("online", on); window.removeEventListener("offline", off); });
  return { isOnline: () => isOnline() };             // read-only by convention: no setter returned
}

export function createSearchState(query: Accessor<string>) {
  const search = createResource(query, (q) => {
    const controller = new AbortController();        // CREATES
    setTimeout(() => onCleanup(() => controller.abort()), 0);
    return fetchResults(q, controller.signal);
  });
  return { state: search, refetch: search.refetch };  // refetch = the retry the owner may call
}
```

## 4. Blazor / C#

No hooks exist, so sources are **services**, and the read-only rule becomes an interface shape:

```csharp
// Shared/Conditions/NetworkCondition.cs
public interface INetworkCondition { bool IsOnline { get; } event Action? Changed; }   // no setter

public sealed class NetworkCondition : INetworkCondition, IAsyncDisposable
{
    private readonly IJSRuntime _js;
    private DotNetObjectReference<NetworkCondition>? _self;
    public bool IsOnline { get; private set; } = true;
    public event Action? Changed;

    public NetworkCondition(IJSRuntime js) => _js = js;

    public async Task StartAsync()
    {
        _self = DotNetObjectReference.Create(this);
        IsOnline = await _js.InvokeAsync<bool>("pvc.net.online");
        await _js.InvokeVoidAsync("pvc.net.subscribe", _self);   // LISTENS
    }

    [JSInvokable] public void Handle(object _, bool online) { IsOnline = online; Changed?.Invoke(); }

    public async ValueTask DisposeAsync()
    {
        if (_self is not null) await _js.InvokeVoidAsync("pvc.net.unsubscribe", _self);
        Changed = null;
    }
}
```

```csharp
// Features/Search/Behaviour/SearchState.cs — CREATES, and owns the cancellation
public sealed class SearchState : IDisposable
{
    private CancellationTokenSource? _cts;
    private int _attempt;
    public SearchStatus Status { get; private set; }
    public IReadOnlyList<Hit> Results { get; private set; } = [];
    public event Action? Changed;

    public async Task SearchAsync(string query)
    {
        _cts?.Cancel();
        _cts = new CancellationTokenSource();
        var mine = ++_attempt;
        Status = SearchStatus.Loading; Changed?.Invoke();
        try { var hits = await _api.SearchAsync(query, _cts.Token); if (mine == _attempt) { Results = hits; Status = SearchStatus.Success; } }
        catch (OperationCanceledException) { }
        catch (Exception e) { if (mine == _attempt) { Error = e.Message; Status = SearchStatus.Error; } }
        Changed?.Invoke();
    }
    public void Dispose() => _cts?.Cancel();
}
```

Registration encodes the answer: a Condition is `AddSingleton`/`AddScoped` (one source, many readers); a State is created per operation or held by the consumer that owns it — never a singleton, because a singleton would mean nobody can tell which consumer caused it.

## 5. Dioxus / Rust

```rust
#[hook]
pub fn use_network_condition() -> ReadSignal<bool> {         // ReadSignal = read-only surface
    let online = use_global(|| Signal::new(true));           // one app-wide source, many readers
    use_effect(move {
        let mut online = online.clone();
        // subscribe to the platform's online/offline bridge — LISTENS;
        // the guard returned when this effect's owner drops unsubscribes
    });
    online.read_only()
}

#[hook]
pub fn use_search_state(query: Signal<String>) -> Resource<Result<Vec<Hit>, String>> {
    use_resource(move {                                      // CREATES
        let q = query.read().clone();
        async move { if q.is_empty() { Ok(vec![]) } else { fetch_results(&q).await.map_err(|e| e.to_string()) } }
    })
    // Resource exposes restart() to its owner — that is the retry permission, and nothing else
}
```

## 6. A worker with no UI at all

```ts
// sync/queueWorker.ts
export function createSyncWorker(api: Api, onEvent: (f: SyncFact) => void) {
  let abort: AbortController | null = null;
  let stopped = false;

  async function drain() {
    abort = new AbortController();                 // CREATES → State: backlog, inFlight, lastError
    while (!stopped) {
      const batch = api.takePending(abort.signal); // own work; waiting DOES resolve this
      if (batch.ok) publish(batch.value);
      else if (batch.reason === "rejected-by-server") break;  // CONDITION: waiting fixes nothing
    }
  }

  const heartbeat = setInterval(() => api.ping(), 30_000);   // LISTENS to server posture
  return {
    start: drain,
    stop() { stopped = true; abort?.abort(); clearInterval(heartbeat); },  // owner destroys what it created
  };
}
```

`backlog`, `inFlight`, `lastRunAt` are States. `serverRejected`, `maintenanceWindow`, `diskFull` are Conditions — and a worker that retries forever against a Condition is the exact §1 misread, in code that never renders anything.

## 7. Nested ownership — owning one source while reading another

The maintenance countdown is the case that proves the asymmetry is about the *source*, not about the consumer's name: the countdown exists only because something already reacting to maintenance needed it, so it is created and destroyed by that consumer, while the maintenance signal itself pre-exists it.

```tsx
// shared/conditions/useMaintenanceCondition.ts
function useMaintenanceCondition() {
  const [isMaintenance, setIsMaintenance] = useState(false);
  useEffect(() => subscribeToOpsChannel(setIsMaintenance), []);   // LISTENS → read-only source
  return { isMaintenance };
}

// features/maintenance/behaviour/useMaintenanceEtaState.ts
function useMaintenanceEtaState() {
  const [state, setState] = useState<"loading" | "success" | "error">("loading");
  const [etaMinutes, setEtaMinutes] = useState<number | null>(null);
  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/maintenance/eta", { signal: controller.signal })  // CREATES → owned source
      .then((r) => r.json())
      .then((d) => { setEtaMinutes(d.eta); setState("success"); })
      .catch(() => setState("error"));
    return () => controller.abort();                                // destroyed with its caller
  }, []);
  return { state, etaMinutes, retry: () => setState("loading") };
}
```

**Blazor, same rule, expressed as service lifetimes.** The Condition is registered so every consumer shares one source; the State is created per operation so exactly one consumer owns its cancellation:

```csharp
builder.Services.AddSingleton<IMaintenanceCondition, MaintenanceCondition>();  // listens; app-wide
// MaintenanceEtaState: instantiated by (or scoped to) the consumer that starts the fetch,
// and disposed by it — a singleton here would mean nobody can tell who caused the request.
```

Renaming the consumer changes nothing: the create-versus-listen answer lives inside each source ([`../references/ownership.md`](../references/ownership.md) §1–§2). What the consumer then *renders* with these two values is out of scope here — that is `/pvc`'s View boundary.

## 8. The four questions, any ecosystem

| Question | React | Vue | Solid | Blazor | Dioxus | worker |
| --- | --- | --- | --- | --- | --- | --- |
| What returns data, never output? | hook | composable | creator | service method/property | `#[hook]` | plain functions |
| Where is the read-only surface? | return no setter | `readonly()` | return accessor only | interface without setter | `ReadSignal` | event + getter |
| What creates? | `fetch` in `useEffect` | `fetch` in composable | `createResource` | `HttpClient` in the service | `use_resource` | `api.takePending` |
| What destroys it? | effect cleanup | `onScopeDispose` | `onCleanup` | `Dispose` | drop / `restart` | `stop()` |
