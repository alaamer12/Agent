# Polyglot walkthrough — the same roles, five ecosystems

> The Search section and the Maintenance section, implemented in five frameworks, to show that every rule in [`../references/`](../references/) is about role and placement, never about a framework construct. Start with [`../references/roles.md`](../references/roles.md) §1 and [`../references/view-and-rendition.md`](../references/view-and-rendition.md) §3 — this file is those two rules, five times over.
>
> **Out of scope here:** how a fact source is *built* — hook vs composable vs creator vs service vs `#[hook]`, create-vs-listen ownership, read-only surfaces, cleanup. That is `/states`. This file treats a source as a black box that returns data, because the only thing PVC needs to know is whether a given unit reads one.

The case, once, for all five:

```
SearchView
├── reads    a network fact source (external, exists independently)
├── owns     a search fact source (this section's own request)
└── selects  one of four branches: disabled · loading · error · success
```

Four units to place: two sources (opaque here), three named Renditions, one View. The success case is the default and needs no Rendition of its own ([`view-and-rendition.md`](../references/view-and-rendition.md) §2).

---

## 1. React / TypeScript

**Anti-pattern** — a unit that renders while claiming to be data, and a Rendition that reads a source:

```tsx
// ✘ both defects in one file
export function SearchDisabledCondition() {          // renders AND claims to be a fact
  const { isOnline } = useNetworkCondition();
  return isOnline ? null : <SearchDisabledMessage />;
}
export function SearchErrorRendition() {
  const { error } = useSearchStore();                 // ✘ reading a source promotes it to a View
  return <SearchErrorMessage message={error} />;
}
```

**Renditions** — props in, markup out, no source read:

```tsx
export function SearchDisabledRendition() { return <SearchDisabledMessage />; }
export function SearchLoadingRendition()   { return <LoadingRendition text="Searching…" />; }
export function SearchErrorRendition({ message, onRetry }: Props) {
  return <SearchErrorMessage message={message} onRetry={onRetry} />;
}
```

**View** — the only place a source read and markup may coexist:

```tsx
export function SearchView({ initialQuery = "" }: SearchViewProps) {
  const [query, setQuery] = useState(initialQuery);
  const { isOnline } = useNetworkCondition();                  // a source: /states built it
  const { status, results, error, retry } = useSearchState(query);

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

Detection rule for review: **any `use…()` call in a body that also returns JSX makes that body a View.**

## 2. Vue 3 / TypeScript

**Anti-pattern** — the shortcut that turns a Rendition into a hidden View:

```vue
<!-- ✘ SearchErrorRendition.vue -->
<script setup lang="ts">
import { useSearchStore } from "@/stores/search";   // ✘ a store read is a fact read
const store = useSearchStore();
</script>
<template><SearchErrorMessage :message="store.error" /></template>
```

**Rendition** — `defineProps` only:

```vue
<!-- features/search/views/SearchView/SearchErrorRendition.vue -->
<script setup lang="ts">
defineProps<{ message: string; onRetry: () => void }>();
</script>
<template><SearchErrorMessage :message="message" :on-retry="onRetry" /></template>
```

**View** — the `v-if` chain *is* the selection, and it lives here:

```vue
<!-- features/search/views/SearchView/SearchView.vue -->
<script setup lang="ts">
import { useNetworkCondition } from "@/shared/conditions/useNetworkCondition";
import { useSearchState } from "../../behaviour/useSearchState";
const { isOnline } = useNetworkCondition();
const query = ref("");
const { status, results, error, retry } = useSearchState(query);
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

Detection rule: **a `v-if` fed by a prop is legal in a Rendition; a `v-if` fed by a store, an `inject()`, or a composable is not** — the template is choosing, so the unit is a View.

## 3. Solid / TypeScript

**Anti-pattern:**

```tsx
// ✘ Rendition reaching outside its props for a fact
export function SearchErrorRendition() {
  const { error } = useSearchContext();      // promotes itself to a View
  return <SearchErrorMessage message={error()} />;
}
```

**Renditions and View** — `Switch`/`Match` is the selection:

```tsx
export function SearchLoadingRendition() { return <LoadingRendition text="Searching…" />; }
export function SearchErrorRendition(props: { message: string; onRetry: () => void }) {
  return <SearchErrorMessage message={props.message} onRetry={props.onRetry} />;
}

export function SearchView(props: SearchViewProps) {
  const [query, setQuery] = createSignal(props.initialQuery ?? "");   // read props, then own them
  const { isOnline } = createNetworkCondition();
  const { status, results, error, retry } = createSearchState(query);

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

Detection rule: **a component that calls a `createX…()` source, or reads a signal it did not receive through props, is a View.** (Props must be accessed, not destructured — a Solid reactivity detail, not a role rule.)

## 4. Blazor / C#

The seam is an injection boundary: **a Rendition injects nothing that reports a fact.**

**Anti-pattern:**

```razor
@* ✘ Features/Search/Views/SearchView/SearchErrorRendition.razor *@
@inject ISearchState Search            @* ✘ consulting a fact → this is a View *@
@if (Search.Failed)
{
    <SearchErrorMessage Message="@Search.Error" />
}
```

**Rendition** — parameters only:

```razor
@* Features/Search/Views/SearchView/SearchErrorRendition.razor *@
<SearchErrorMessage Message="@Message" OnRetry="@OnRetry" />

@code {
    [Parameter] public string Message { get; set; } = "";
    [Parameter] public EventCallback OnRetry { get; set; }
}
```

**View** — injects the sources, selects with `@if`:

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
    protected override void OnInitialized() { Network.Changed += Redraw; Search.Changed += Redraw; }
    private void Redraw() => InvokeAsync(StateHasChanged);
    public void Dispose() { Network.Changed -= Redraw; Search.Changed -= Redraw; }
}
```

Detection rule: **any `@inject` of something that reports a fact makes the component a View.** The subscribe/unsubscribe pair in `@code` is the source's ownership contract — `/states` decides whether this component may hold it at all.

## 5. Dioxus / Rust

**Anti-pattern:**

```rust
#[component]
pub fn SearchErrorRendition() -> Element {
    let search = use_search_state();      // ✘ a Rendition calling a hook is a View
    rsx! { SearchErrorMessage { message: search.error.read().clone() } }
}
```

**Renditions:**

```rust
#[component]
pub fn SearchDisabledRendition() -> Element { rsx! { SearchDisabledMessage {} } }

#[component]
pub fn SearchErrorRendition(message: String, on_retry: EventHandler<()>) -> Element {
    rsx! { SearchErrorMessage { message, on_retry } }   // props only — a real Rendition
}
```

**View:**

```rust
#[component]
pub fn SearchView() -> Element {
    let is_online = use_network_condition();
    let query = use_signal(String::new);
    let search = use_search_state(query);

    if !is_online() { return rsx! { SearchDisabledRendition {} }; }
    match search() {
        None               => rsx! { SearchLoadingRendition {} },
        Some(Err(message)) => rsx! { SearchErrorRendition { message: message.clone(), on_retry: move |_| search.restart() } },
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

Detection rule, and it is the cheapest of the five to enforce: **if the component body calls any `use_*` hook, it is a View.**

## 6. A section with one owned source and one read source

`/states` decides *why* a section may own one source and only read another. What PVC adds is only the shape of the View that receives both:

```tsx
export function MaintenanceView({ children }: { children: ReactNode }) {
  const { isMaintenance } = useMaintenanceCondition();          // read
  const { state, etaMinutes, retry } = useMaintenanceEtaState(); // owned

  if (!isMaintenance) return <>{children}</>;                    // pass-through is a branch too
  if (state === "loading") return <MaintenanceLoadingRendition />;
  if (state === "error")   return <MaintenanceErrorRendition onRetry={retry} />;
  return <MaintenanceRendition etaMinutes={etaMinutes ?? 0} />;
}
```

Nothing about the View changes because one source is owned and the other is read — same role, same selection, same Renditions. That independence is the point: ownership reasoning lives in `/states`, and renaming or re-wiring the sources here could never change a role decision ([`view-and-rendition.md`](../references/view-and-rendition.md) §5).

## 7. Forwarding and grouping

The two sharing relationships from [`view-and-rendition.md`](../references/view-and-rendition.md) §5–6, in each idiom. Both are pure delegation — no source read, no choice — so neither can violate anything:

| Relationship | React | Vue | Solid | Blazor | Dioxus |
| --- | --- | --- | --- | --- | --- |
| Local Rendition forwarding to a global one | `<LoadingRendition text="Searching…" />` | same, in the template | same | `<LoadingRendition Text="@(\"Searching…\")" />` | `rsx! { LoadingRendition { text } }` |
| Wrapper Component (children don't coordinate) | `<div className="actions-row">` holding three Components | same | same | `@* _FundCardActions.razor *@` | `div { class: "actions-row", AddToWatchlist {}, CompareFund {}, RemoveFund {} }` |
| Nested View inside a Rendition | `<CameraView />` among the success markup | `<CameraView />` | same | `<CameraView />` | `CameraView {}` |

A source wrapping a source — a local one delegating to a generic shared one — is the same forwarding idea applied on the `/states` side of the seam; that skill covers it, including the fact that delegation never changes who owns the effect.

## 8. What stayed identical across all five

| Rule | Where it landed in each |
| --- | --- |
| View is the only fact-plus-render seam | `if` returns / `v-if` chain / `<Switch>` / `@if` / `match` |
| Rendition takes inputs only, reads nothing | props / `defineProps` / `props.x` / `[Parameter]` with no `@inject` / props struct with no `use_*` |
| A Rendition never chooses between Renditions | same detection rule per framework: the read makes the chooser |
| `_` scoped-shared convention | folder- and file-level, identical in all five |
| Downward imports, no skipped primitive tier | import graph / `@using` / `use` path — checked by [`../scripts/check_pvc.py`](../scripts/check_pvc.py) |

Nothing about the doctrine needed translating — only the syntax, which is the point of [`../references/roles.md`](../references/roles.md) §1.
