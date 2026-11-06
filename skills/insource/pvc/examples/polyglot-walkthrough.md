# Polyglot walkthrough — one case, five ecosystems

> The same Search section and the same maintenance-countdown case, implemented in five frameworks, to show that every rule in [`../references/`](../references/) is about role and placement, never about a framework construct. Start with [`../references/facts.md`](../references/facts.md) §0 and [`../references/view-and-rendition.md`](../references/view-and-rendition.md) §3 — this file is those two rules, five times over.

The case, once, for all five:

```
SearchView
├── READS   the network Condition (app-wide, exists independently of this View)
├── OWNS    the search State (this View's own request)
└── SELECTS one of four branches: disabled · loading · error · success
```

Every implementation below has exactly four units to place: two fact sources, three named Renditions, one View. The success case is the default and needs no Rendition of its own ([`../references/view-and-rendition.md`](../references/view-and-rendition.md) §2).

---

## 1. React / TypeScript

**Anti-pattern** — a fact suffix on something that renders, and a Rendition that reads a fact:

```tsx
// ✘ two defects in one file
export function SearchDisabledCondition() {          // renders AND claims to be a fact
  const { isOnline } = useNetworkCondition();
  return isOnline ? null : <SearchDisabledMessage />;
}
export function SearchErrorRendition() {              // ✘ a Rendition reading a store
  const { error } = useSearchStore();                 //    silently promoted to a View
  return <SearchErrorMessage message={error} />;
}
```

**Fact sources** — data only, never markup:

```tsx
// shared/conditions/useNetworkCondition.ts — LISTENS, so it is a Condition
export function useNetworkCondition() {
  const [isOnline, setIsOnline] = useState(() => navigator.onLine);
  useEffect(() => {
    const on = () => setIsOnline(true);
    const off = () => setIsOnline(false);
    window.addEventListener("online", on);
    window.addEventListener("offline", off);
    return () => { window.removeEventListener("online", on); window.removeEventListener("offline", off); };
  }, []);
  return { isOnline };
}

// features/search/behaviour/useSearchState.ts — CREATES the request, so it is a State
export function useSearchState(query: string) {
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [results, setResults] = useState<Hit[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [nonce, setNonce] = useState(0);

  useEffect(() => {
    if (!query) { setStatus("idle"); return; }
    const controller = new AbortController();
    setStatus("loading");
    fetchSearchResults(query, controller.signal)
      .then((hits) => { setResults(hits); setStatus("success"); })
      .catch((e) => { if (e.name !== "AbortError") { setError(String(e)); setStatus("error"); } });
    return () => controller.abort();
  }, [query, nonce]);

  return { status, results, error, retry: () => setNonce((n) => n + 1) };
}
```

**Renditions** — props in, markup out, no fact consulting:

```tsx
export function SearchDisabledRendition() { return <SearchDisabledMessage />; }
export function SearchLoadingRendition()   { return <LoadingRendition text="Searching…" />; }
export function SearchErrorRendition({ message, onRetry }: Props) {
  return <SearchErrorMessage message={message} onRetry={onRetry} />;
}
```

**View** — the only unit where fact and render meet:

```tsx
export function SearchView({ initialQuery = "" }: SearchViewProps) {
  const [query, setQuery] = useState(initialQuery);
  const { isOnline } = useNetworkCondition();                 // Condition — read
  const { status, results, error, retry } = useSearchState(query);  // State — owned

  if (!isOnline)             return <SearchDisabledRendition />;
  if (status === "loading")  return <SearchLoadingRendition />;
  if (status === "error")    return <SearchErrorRendition message={error!} onRetry={retry} />;

  return (
    <section>
      <SearchDescription />
      <DebouncedSearchInput onSearch={setQuery} />
      <ResultsList results={results} />
    </section>
  );
}
```

## 2. Vue 3 / TypeScript

**Anti-pattern** — the composable renders, and a Rendition reaches for the store:

```vue
<!-- ✘ SearchErrorRendition.vue — a Rendition reading a store is a View -->
<script setup lang="ts">
import { useSearchStore } from "@/stores/search";   // ✘ fact consult inside a Rendition
const store = useSearchStore();
</script>
<template><SearchErrorMessage :message="store.error" /></template>
```

**Fact sources** — composables returning refs:

```ts
// shared/conditions/useNetworkCondition.ts
import { onScopeDispose, readonly, ref } from "vue";

export function useNetworkCondition() {
  const isOnline = ref(navigator.onLine);
  const on = () => (isOnline.value = true);
  const off = () => (isOnline.value = false);
  window.addEventListener("online", on);
  window.addEventListener("offline", off);
  onScopeDispose(() => {
    window.removeEventListener("online", on);
    window.removeEventListener("offline", off);
  });
  return { isOnline: readonly(isOnline) };   // read-only: Conditions are never written
}

// features/search/behaviour/useSearchState.ts
export function useSearchState(query: Ref<string>) {
  const status = ref<"idle" | "loading" | "success" | "error">("idle");
  const results = ref<Hit[]>([]);
  const error = ref<string | null>(null);
  let controller: AbortController | null = null;

  async function run() {
    controller?.abort();
    if (!query.value) { status.value = "idle"; return; }
    controller = new AbortController();        // CREATES the request → State
    status.value = "loading";
    try { results.value = await fetchSearchResults(query.value, controller.signal); status.value = "success"; }
    catch (e) { if ((e as Error).name !== "AbortError") { error.value = String(e); status.value = "error"; } }
  }
  watchEffect(() => { query.value; run(); });
  return { status, results, error, retry: run };
}
```

**Renditions** — `defineProps` only, no store, no composable that reads a fact:

```vue
<!-- features/search/views/SearchView/SearchErrorRendition.vue -->
<script setup lang="ts">
defineProps<{ message: string; onRetry: () => void }>();
</script>
<template><SearchErrorMessage :message="message" :on-retry="onRetry" /></template>
```

**View** — the `v-if` chain is the selection and lives here, in the View's template:

```vue
<!-- features/search/views/SearchView/SearchView.vue -->
<script setup lang="ts">
import { useNetworkCondition } from "@/shared/conditions/useNetworkCondition";
import { useSearchState } from "../../behaviour/useSearchState";
const { isOnline } = useNetworkCondition();               // Condition — read
const query = ref("");
const { status, results, error, retry } = useSearchState(query);  // State — owned
</script>

<template>
  <SearchDisabledRendition v-if="!isOnline" />
  <SearchLoadingRendition  v-else-if="status === 'loading'" />
  <SearchErrorRendition    v-else-if="status === 'error'" :message="error" :on-retry="retry" />
  <section v-else>
    <SearchDescription />
    <DebouncedSearchInput v-model="query" />
    <ResultsList :results="results" />
  </section>
</template>
```

A Vue-specific trap: `v-if` in a *Rendition's* template driven by a prop that came from a fact is still legal (the Rendition is not consulting anything), but `v-if` driven by a store or an injected composable is not — the Rendition has become a View ([`../references/view-and-rendition.md`](../references/view-and-rendition.md) §5).

## 3. Solid / TypeScript

**Anti-pattern** — destructuring props (breaks reactivity) and a Rendition reading a signal:

```tsx
// ✘ Rendition reaching outside its props for a fact
export function SearchErrorRendition() {
  const { error } = useSearchContext();     // ✘ consulting a fact → this is a View
  return <SearchErrorMessage message={error()} />;
}
```

**Fact sources** — creators returning accessors:

```ts
export function createNetworkCondition() {
  const [isOnline, setIsOnline] = createSignal(navigator.onLine);
  const on = () => setIsOnline(true);
  const off = () => setIsOnline(false);
  window.addEventListener("online", on);
  window.addEventListener("offline", off);
  onCleanup(() => { window.removeEventListener("online", on); window.removeEventListener("offline", off); });
  return { isOnline };                       // accessors, never markup
}

export function createSearchState(query: Accessor<string>) {
  const [status, setStatus] = createSignal<"idle" | "loading" | "success" | "error">("idle");
  const [results, setResults] = createSignal<Hit[]>([]);
  const [error, setError] = createSignal<string | null>(null);
  let attempt = 0;

  createEffect(() => {
    const q = query();
    if (!q) { setStatus("idle"); return; }
    const controller = new AbortController();
    const my = ++attempt;
    setStatus("loading");
    fetchSearchResults(q, controller.signal)
      .then((hits) => { if (my === attempt) { setResults(hits); setStatus("success"); } })
      .catch((e) => { if (e.name !== "AbortError") { setError(String(e)); setStatus("error"); } });
    onCleanup(() => controller.abort());
  });

  return { status, results, error, retry: () => { /* bump attempt and refetch */ } };
}
```

**Rendition and View** — Solid's ternaries in JSX are the selection:

```tsx
export function SearchLoadingRendition() { return <LoadingRendition text="Searching…" />; }
export function SearchErrorRendition(props: { message: string; onRetry: () => void }) {
  return <SearchErrorMessage message={props.message} onRetry={props.onRetry} />;
}

export function SearchView(props: SearchViewProps) {
  const [query, setQuery] = createSignal(props.initialQuery ?? "");  // read props, then own them
  const { isOnline } = createNetworkCondition();                     // Condition — read
  const { status, results, error, retry } = createSearchState(query); // State — owned

  return (
    <Switch>
      <Match when={!isOnline()}><SearchDisabledRendition /></Match>
      <Match when={status() === "loading"}><SearchLoadingRendition /></Match>
      <Match when={status() === "error"}><SearchErrorRendition message={error()!} onRetry={retry} /></Match>
      <Match when={true}>
        <section>
          <SearchDescription />
          <DebouncedSearchInput onSearch={setQuery} />
          <ResultsList results={results()} />
        </section>
      </Match>
    </Switch>
  );
}
```

## 4. Blazor (Server and WebAssembly) / C#

No hooks exist, so fact sources become **services**, and the "never renders" rule becomes "a service has no `.razor`". Renditions are components that declare `[Parameter]`s and **inject nothing**.

**Anti-pattern** — a Rendition that injects a Condition and branches:

```razor
@* ✘ Features/Search/Views/SearchView/SearchErrorRendition.razor *@
@inject ISearchState Search            @* ✘ a Rendition consulting a fact is a View *@
@if (Search.Failed)
{
    <SearchErrorMessage Message="@Search.Error" />
}
```

**Fact sources:**

```csharp
// Shared/Conditions/NetworkCondition.cs — LISTENS → Condition, read-only surface
public interface INetworkCondition
{
    bool IsOnline { get; }
    event Action? Changed;
}

public sealed class NetworkCondition : INetworkCondition, IAsyncDisposable
{
    private readonly IJSRuntime _js;
    public bool IsOnline { get; private set; } = true;
    public event Action? Changed;
    private DotNetObjectReference<NetworkCondition>? _ref;

    public NetworkCondition(IJSRuntime js) => _js = js;

    public async Task StartAsync()
    {
        _ref = DotNetObjectReference.Create(this);
        IsOnline = await _js.InvokeAsync<bool>("pvc.net.online");
        await _js.InvokeVoidAsync("pvc.net.subscribe", _ref);   // raises Handle(_, online)
    }

    [JSInvokable]
    public void Handle(object _, bool online)
    {
        IsOnline = online;
        Changed?.Invoke();
    }

    public async ValueTask DisposeAsync()
    {
        if (_ref is not null) await _js.InvokeVoidAsync("pvc.net.unsubscribe", _ref);
        Changed = null;
    }
}
```

```csharp
// Features/Search/Behaviour/SearchState.cs — CREATES the request → State
public sealed class SearchState : IDisposable
{
    private readonly SearchApi _api;
    private CancellationTokenSource? _cts;
    private int _attempt;

    public SearchStatus Status { get; private set; } = SearchStatus.Idle;
    public IReadOnlyList<Hit> Results { get; private set; } = [];
    public string? Error { get; private set; }
    public event Action? Changed;

    public SearchState(SearchApi api) => _api = api;

    public async Task SearchAsync(string query)
    {
        _cts?.Cancel();
        _cts = new CancellationTokenSource();
        var mine = ++_attempt;
        Status = SearchStatus.Loading; Changed?.Invoke();
        try
        {
            var hits = await _api.SearchAsync(query, _cts.Token);
            if (mine != _attempt) return;
            Results = hits; Status = SearchStatus.Success;
        }
        catch (OperationCanceledException) { return; }
        catch (Exception e) { if (mine == _attempt) { Error = e.Message; Status = SearchStatus.Error; } }
        Changed?.Invoke();
    }

    public void Dispose() => _cts?.Cancel();
}
```

Registration — a global Condition is a *shared* service; a per-operation State is registered where the View's lifetime lives (a scoped service per page on Blazor Server, a transient instance held by the View in WASM):

```csharp
builder.Services.AddScoped<INetworkCondition, NetworkCondition>();  // app-wide Condition
```

**Renditions** — parameters in, markup out, no `@inject` of anything factual:

```razor
@* Features/Search/Views/SearchView/SearchErrorRendition.razor *@
@* a Rendition: [Parameter] only, no fact consulting, not independently addressable *@
<SearchErrorMessage Message="@Message" OnRetry="@OnRetry" />

@code {
    [Parameter] public string Message { get; set; } = "";
    [Parameter] public EventCallback OnRetry { get; set; }
}
```

**View** — the only component that injects facts, and the `@if` chain is its selection:

```razor
@* Features/Search/Views/SearchView/SearchView.razor *@
@implements IDisposable
@inject INetworkCondition Network
@inject SearchState Search

@if (!Network.IsOnline)
{
    <SearchDisabledRendition />
}
else if (Search.Status == SearchStatus.Loading)
{
    <SearchLoadingRendition />
}
else if (Search.Status == SearchStatus.Error)
{
    <SearchErrorRendition Message="@Search.Error!" OnRetry="@(() => Search.SearchAsync(_query))" />
}
else
{
    <section>
        <SearchDescription />
        <DebouncedSearchInput OnSearch="Search.SearchAsync" />
        <ResultsList Results="@Search.Results" />
    </section>
}

@code {
    private string _query = "";
    protected override void OnInitialized()
    {
        Network.Changed += Redraw; Search.Changed += Redraw;
    }
    private void Redraw() => InvokeAsync(StateHasChanged);
    public void Dispose()
    {
        Network.Changed -= Redraw; Search.Changed -= Redraw;
    }
}
```

The unsubscribe in `Dispose` is the Blazor equivalent of the cleanup return in the JS examples — and it is the same ownership test: this View *listened* to a Condition that existed before it and will exist after it.

## 5. Dioxus / Rust

Fact sources are hooks returning `Signal` / `Resource`. A Rendition is a `#[component]` taking a props struct — the compiler makes the rule cheap to check, because a Rendition that wants a fact has to call a hook, and that is visible in its body.

**Anti-pattern:**

```rust
#[component]
pub fn SearchErrorRendition() -> Element {
    let search = use_search_state();      // ✘ a Rendition calling a hook is a View
    rsx! { SearchErrorMessage { message: search.error.read().clone() } }
}
```

**Fact sources:**

```rust
// shared/conditions/use_network_condition.rs — LISTENS → Condition
#[hook]
pub fn use_network_condition() -> ReadSignal<bool> {
    // App-wide: one Global<Signal> fed by the platform's online/offline bridge,
    // so every View reads the same source instead of each subscribing separately.
    let online = use_global(|| Signal::new(true));   // GLOBAL — see placement.md §5
    use_effect(move {
        let mut online = online.clone();
        // subscribe to the platform event here; the guard returned on drop unsubscribes
    });
    online.read_only()
}

// features/search/behaviour/use_search_state.rs — CREATES the request → State
#[hook]
pub fn use_search_state(query: ReadSignal<String>) -> Resource<Result<Vec<Hit>, String>> {
    use_resource(move {
        let q = query.read().clone();
        async move {
            if q.is_empty() { return Ok(vec![]); }
            fetch_search_results(&q).await.map_err(|e| e.to_string())
        }
    })
}
```

**Renditions:**

```rust
#[component]
pub fn SearchDisabledRendition() -> Element {
    rsx! { SearchDisabledMessage {} }
}

#[component]
pub fn SearchErrorRendition(message: String, on_retry: EventHandler<()>) -> Element {
    rsx! { SearchErrorMessage { message, on_retry } }   // props only — a real Rendition
}
```

**View:**

```rust
#[component]
pub fn SearchView() -> Element {
    let is_online = use_network_condition();                    // Condition — read
    let query = use_signal(String::new);
    let search = use_search_state(query);                       // State — owned

    if !is_online() {
        return rsx! { SearchDisabledRendition {} };
    }
    match search() {
        None              => rsx! { SearchLoadingRendition {} },
        Some(Err(message)) => rsx! {
            SearchErrorRendition {
                message: message.clone(),
                on_retry: move |_| search.restart(),
            }
        },
        Some(Ok(hits)) => rsx! {
            section {
                SearchDescription {}
                DebouncedSearchInput { on_search: move |q| query.set(q) }
                for hit in hits { ResultsList { hit } }
            }
        },
    }
}
```

---

## 6. The nested ownership case (Condition owning a State)

[`../references/facts.md`](../references/facts.md) §5's asymmetry, in the two ecosystems where it is least obvious. A `MaintenanceView` **reads** an ops-driven Condition and **owns** a countdown fetch that exists only because this View needed it.

**React** — the asymmetry is visible in which effect creates and which listens:

```tsx
// shared/conditions/useMaintenanceCondition.ts — subscribes to an external ops channel
function useMaintenanceCondition() {
  const [isMaintenance, setIsMaintenance] = useState(false);
  useEffect(() => subscribeToOpsChannel(setIsMaintenance), []);   // LISTENS
  return { isMaintenance };
}

// shared/views/MaintenanceView/behaviour/useMaintenanceEtaState.ts — created and killed here
function useMaintenanceEtaState() {
  const [state, setState] = useState<"loading" | "success" | "error">("loading");
  const [etaMinutes, setEtaMinutes] = useState<number | null>(null);
  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/maintenance/eta", { signal: controller.signal })  // CREATES
      .then(r => r.json())
      .then(d => { setEtaMinutes(d.eta); setState("success"); })
      .catch(() => setState("error"));
    return () => controller.abort();                              // DESTROYS with the caller
  }, []);
  return { state, etaMinutes, retry: () => setState("loading") };
}

export function MaintenanceView({ children }: { children: ReactNode }) {
  const { isMaintenance } = useMaintenanceCondition();             // read
  const { state, etaMinutes, retry } = useMaintenanceEtaState();   // owned
  if (!isMaintenance) return <>{children}</>;
  if (state === "loading") return <MaintenanceLoadingRendition />;
  if (state === "error")   return <MaintenanceErrorRendition onRetry={retry} />;
  return <MaintenanceRendition etaMinutes={etaMinutes ?? 0} />;
}
```

**Blazor** — the same split, expressed as service lifetimes rather than effect bodies. The Condition is a shared-scoped service every feature may inject; the ETA State is an instance the View creates and disposes:

```csharp
// Shared/Conditions/MaintenanceCondition.cs — subscribes, never renders, app-wide
builder.Services.AddSingleton<IMaintenanceCondition, MaintenanceCondition>();  // Global

// Shared/Views/MaintenanceView/MaintenanceEtaState.cs — created by the View alone
public sealed class MaintenanceEtaState : IDisposable
{
    public int? EtaMinutes { get; private set; }
    public EtaStatus Status { get; private set; } = EtaStatus.Loading;
    public event Action? Changed;
    private readonly MaintenanceApi _api;
    private readonly CancellationTokenSource _cts = new();

    public MaintenanceEtaState(MaintenanceApi api) => _api = api;

    public async Task LoadAsync()
    {
        Status = EtaStatus.Loading; Changed?.Invoke();
        try { EtaMinutes = await _api.GetEtaAsync(_cts.Token); Status = EtaStatus.Success; }
        catch (OperationCanceledException) { }
        catch { Status = EtaStatus.Error; }
        Changed?.Invoke();
    }
    public void Dispose() => _cts.Cancel();
}
```

```csharp
// in MaintenanceView.razor — the View owns the State's lifetime, reads the Condition
@implements IDisposable
@inject IMaintenanceCondition Ops        @* read: existed before this View *@
@inject MaintenanceEtaState Eta          @* owned: dies with this View *@
```

The ownership test passes through unchanged in both: *does the effect create the thing, or merely listen to a thing that already exists?* Renaming the View changes nothing — the answer lives inside the fact source, which is exactly why ownership is never a naming question ([`../references/facts.md`](../references/facts.md) §5).

## 7. Forwarding and wrappers, across frameworks

The two sharing relationships from [`../references/view-and-rendition.md`](../references/view-and-rendition.md) §6, in each ecosystem's idiom. Both are pure delegation — no fact consulted, no choice made — so neither can violate anything:

| Relationship | React | Vue | Solid | Blazor | Dioxus |
| --- | --- | --- | --- | --- | --- |
| Local Rendition forwarding to the global one | `<LoadingRendition text="Searching…" />` inside `SearchLoadingRendition` | `<LoadingRendition text="Searching…" />` in the Rendition's template | same as React | `<LoadingRendition Text="@(\"Searching…\")" />` in the Rendition's markup | `rsx! { LoadingRendition { text } }` |
| Local State source wrapping a global generic one | `useSearchState = () => useAsyncState(() => api.search(q))` | `useSearchState = () => useAsyncState(() => api.search(q))` | `createSearchState = q => createAsyncState(() => api.search(q))` | `SearchState` delegating to a generic `AsyncState<T>` | `use_search_state` calling `use_async_state` |
| Wrapper Component (no coordination, several targets) | `<div className="actions-row">` holding three Components | same, in template | same | `@* _FundCardActions.razor *@` holding three components | `div { class: "actions-row", AddToWatchlist {}, CompareFund {}, RemoveFund {} }` |

Ownership passes through every wrapper layer untouched: the layer that actually issues the request or registers the listener is the owner, no matter how many delegating layers sit above it ([`../references/view-and-rendition.md`](../references/view-and-rendition.md) §6).

## 8. What stayed identical across all five

| Rule | Where it landed in each |
| --- | --- |
| Fact source returns data, never markup | hook / composable / creator / service / `#[hook]` |
| View is the only fact-plus-render seam | `if` returns / `v-if` chain / `<Switch>` / `@if` / `match` |
| Rendition takes inputs only, consults nothing | props / `defineProps` / `props.x` / `[Parameter]`, no `@inject` / props struct, no hook |
| `_` scoped-shared convention | folder- and file-level, identical in all five |
| Downward imports, no skipped primitive tier | import graph / `@using` / `use` path — checked by [`../scripts/check_pvc.py`](../scripts/check_pvc.py) |

Nothing about the doctrine needed translating. Only the syntax did — which is the point of [`../references/roles.md`](../references/roles.md) §1.
