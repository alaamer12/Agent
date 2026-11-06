# Framework adapters — the same six roles, five ecosystems

> The bridge from this system's vocabulary to a framework's native constructs. The doctrine never borrows React's nouns; this file is where the borrowing happens, deliberately and in one place. Read [`roles.md`](./roles.md) and [`facts.md`](./facts.md) first. Concrete code side by side: [`../examples/polyglot-walkthrough.md`](../examples/polyglot-walkthrough.md).

**Standing note:** the constructs below are the *idiomatic* way each ecosystem expresses a role, not the only way. Where a framework offers several (`[local state + effect]`, `[a store]`, `[a server call]` for a State source), pick by the project's existing convention. A framework not listed here is not unsupported — map it through the same four questions in §1.

## 1. The four questions that map any framework

For each role, ask the same thing of any ecosystem:

1. **Fact source** — what construct returns *data* and is not allowed to return markup? (If the framework has no such separation, that is a discipline you impose by folder and review, not one it enforces.)
2. **View** — where may a unit read facts *and* choose what to render in the same body?
3. **Rendition** — how do you declare a unit that takes inputs only, and how do you keep it from reading global/reactive state?
4. **Primitive** — what is this ecosystem's raw control, and where does the project's skin over it live (`base` vs `adaptive`)?

Answer those four and the remaining vocabulary falls out.

## 2. Vocabulary bridge

| This system | React / Next | Vue 3 | Solid / SolidStart | Blazor (Server + WASM) | Dioxus |
| --- | --- | --- | --- | --- | --- |
| Page | route component / `page.tsx` | route SFC in `views/` | route component | `.razor` with `@page "/x"` | `#[component]` in `router` match arms |
| View | component fn | SFC | component fn | `.razor` component | `#[component]` returning `Element` |
| Component (purposeful) | component fn | SFC | component fn | `.razor` component | `#[component]` |
| Rendition | component fn, props only | SFC with `defineProps`, no store reads | component fn, props only | `.razor` with `[Parameter]` only, no service injection | `#[component]` taking a props struct |
| Decoration / Aligner | component / plain JSX | SFC / template block | component / JSX | `.razor` / template block | `rsx!` block or component |
| UI Element (`base`) | re-export of the DOM/HEADless control | re-export of a native element or library control | same | re-export of a library component (`<MudButton>`) | re-export of a library control or an `rsx!` of `button` |
| UI Element (`adaptive`) | styled wrapper | styled wrapper | styled wrapper | wrapper `.razor` applying tokens/CSS vars | wrapper component applying class/theme |
| State fact source | `useXState()` custom hook | `useXState()` composable returning `ref`/`computed` | `createXState()` returning signal/resource, or `useXState()` | a service method or property, e.g. `IOrderSubmitState` | `#[hook] fn use_x_state() -> Signal<T>` / `Resource<T>` |
| Condition fact source | `useXCondition()` | `useXCondition()` composable | `createXCondition()` | injected singleton/scoped service, e.g. `INetworkCondition` | `Global<Signal<T>>` + accessor hook |
| Props | props object | `defineProps<T>()` | typed props (accessed, not destructured) | `[Parameter]` properties | `#[derive(Props)]` struct |
| Events out | `onChange` callback | `defineEmits` / `@update` | `on:xxx` or callback prop | `EventCallback<T>` | `on_xxx` callback in props |
| Conditional rendering | `if`/ternary returning JSX | `v-if` in the View's template | ternary in JSX | `@if` block in the View's `.razor` | `match` inside `rsx!` |
| Async effect issuing a request | `useEffect` + `fetch` | `watchEffect` / composable + `fetch` | `createResource` / `createEffect` | `OnInitializedAsync` + `HttpClient` | `use_resource` / `spawn` |
| Subscribing to an external signal | `addEventListener` in `useEffect` | listener in `onMounted`, removed `onUnmounted` | listener in `onMount`, removed `onCleanup` | service with a `Changed` event + `StateHasChanged` | `use_effect` subscribing, `drop`/cancel on unmount |

## 3. Notes per ecosystem

**React / Solid (hooks and signals).** Closest to the doctrine's original phrasing: fact sources are functions returning data, Views are the only components allowed to both call them and return markup. Solid's conventions differ in one important way — reactive sources are created (`createSignal`, `createResource`) and read by calling the signal; the "never renders" rule then means a `createX…State()` returns an accessor, never JSX. Solid also warns against destructuring props at the component top level (it breaks reactivity) — that constraint is an implementation detail of Solid, not a change to the role rules.

**Vue 3.** Composables (`useX()`) map to fact sources and are the natural home for the "returns data only" discipline. Two Vue-specific cautions: (a) a template's `v-if` is still a *selection*, so fact-driven branching belongs in the View's template and never in a Rendition's; (b) reading a store (Pinia or similar) inside a component is a fact read — so a Rendition that reaches for a store has silently promoted itself to a View, exactly as [`view-and-rendition.md`](./view-and-rendition.md) §5 describes, with the framework's store replacing the hook as the mechanism.

**Blazor.** There are no hooks, so the doctrine maps onto *services* instead: a Condition is an injected scoped or singleton service exposing a property plus a change event; a State is either component-local fields or an injected per-operation service. The "fact source never renders" rule becomes "a service returns data and contains no `.razor`" — enforce it by folder: services under `shared/conditions/`, never in the component tree. A Rendition is a `.razor` component whose only inputs are `[Parameter]`s and that injects nothing that reports a fact; a View is a `.razor` component that does inject one, and uses `@if` to select. Because Blazor components re-render imperatively (`StateHasChanged`), subscribing to a Condition service needs the same care as removing a listener in JS — unsubscribe in `Dispose`/`AsyncDisposable`, or the Condition outlives the View that thought it owned it.

**Dioxus.** Fact sources are hooks returning `Signal<T>` or `Resource<T>`; app-wide Conditions are usually `Global<Signal<T>>` so every View reads one shared source rather than each subscribing. Views are `#[component]` functions whose body `match`es over the fact and returns different `rsx!`. A Rendition is a separate `#[component]` taking a props struct — the compiler helps here: a Rendition that wants a fact must call a hook, and the review rule is simply "if this component calls `use_resource`/`use_signal`, it is a View". Naming follows Rust conventions: functions `snake_case` (`search_view`, `use_network_condition`), components and props types `PascalCase` (`SearchInput`, `FundCardProps`).

**Server-rendered and hypermedia stacks** (HTMX, Livewire, Rails/ERB, Phoenix, plain templates). The roles still apply; the layers just move. A Page is a route's template, a View is a partial that the controller or route handler *has already* resolved facts for, a Rendition is a partial selected by an `if` in the View, and a fact source is a query or a service call in the request handler. The "fact source returns data, never markup" rule maps directly: handlers return values, templates render. Treat "which partial do we show" as View logic and never let a Rendition partial reach for a model to decide its own existence.

## 4. Path aliases and module resolution

Examples elsewhere write `@/ui/adaptive/…`, a TypeScript-style alias. Substitute your project's mechanism — `@`/`~` aliases in `tsconfig`/`vite`/webpack, relative paths, Vue aliases, Blazor `_Imports.razor` plus namespaces, Rust `crate::ui::adaptive::…`. The rule being expressed is the import direction ([`primitives-and-imports.md`](./primitives-and-imports.md) §3), not the alias syntax.

## 5. What never translates

Three things are framework-independent and must survive any port:

1. A fact source returns data, never markup ([`facts.md`](./facts.md) §0).
2. The View is the only unit that both reads a fact and selects what renders ([`view-and-rendition.md`](./view-and-rendition.md) §3).
3. Imports point downward and never skip a primitive tier ([`primitives-and-imports.md`](./primitives-and-imports.md) §3).

If a framework makes one of these awkward, the framework is where you add discipline — the role model does not bend.
