# Framework adapters — the same six roles, five ecosystems

> The bridge from this system's vocabulary to a framework's native constructs. The doctrine never borrows React's nouns; this file is where the borrowing happens, deliberately and in one place. Read [`roles.md`](./roles.md) first. Concrete code side by side: [`../examples/polyglot-walkthrough.md`](../examples/polyglot-walkthrough.md). Building and owning fact sources is **not** here — that is `/states`; this file covers only how to *recognise* a fact read, because the View/Rendition boundary depends on that and on nothing else from the facts world.

**Standing note:** the constructs below are the *idiomatic* way each ecosystem expresses a role, not the only way. Where a framework offers several (`[a local composable]`, `[a store]`, `[an injected service]` for a fact source), pick by the project's existing convention. A framework not listed here is not unsupported — map it through the four questions in §1.

## 1. The four questions that map any framework

1. **Unit** — what construct renders output? (component function, SFC, `.razor` component, `#[component]`, template partial)
2. **Inputs** — how does a unit declare that it receives data and takes nothing else?
3. **Fact read** — how does a unit *obtain a value it did not receive as input*, so you can tell whether it is reading a fact source?
4. **Primitive** — what is this ecosystem's raw control, and where does the project's skin over it live (`base` vs `adaptive`)?

Question 3 is the entire interface between this skill and `/states`: PVC needs to *detect* a fact read, never to classify which kind of fact it is.

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
| Props | props object | `defineProps<T>()` | typed props (accessed, not destructured) | `[Parameter]` properties | `#[derive(Props)]` struct |
| Events out | `onChange` callback | `defineEmits` / `@update` | `on:xxx` or callback prop | `EventCallback<T>` | `on_xxx` callback in props |
| Conditional rendering | `if`/ternary returning JSX | `v-if` in the View's template | ternary in JSX | `@if` block in the View's `.razor` | `match` inside `rsx!` |
| **A fact read looks like** | a `use…()` call not satisfied by props | `useXStore()`, `inject()`, an imported composable returning refs | a `createX…()` call, or reading a signal from outside props | `@inject` of anything that reports a fact | any `use_*` hook: `use_resource`, `use_signal`, `use_global` |

How those sources are *written* — hook vs composable vs creator vs service vs `#[hook]`, and which layer creates rather than listens — belongs to `/states`, which carries its own polyglot examples. This table stops at detection.

## 3. Notes per ecosystem

**React / Solid.** Views are the only components permitted to both call a fact source and return markup. Solid adds one wrinkle worth knowing: reactive sources are *created* (`createSignal`, `createResource`) and read by calling the accessor, and destructuring props at the top of a component breaks reactivity. Neither changes a role rule — but both change what a fact read looks like in review (§2's last row).

**Vue 3.** Two traps. (a) A template's `v-if` is still a *selection*, so fact-driven branching belongs in the View's template and never in a Rendition's. (b) Reading a store (Pinia or similar) inside a component is a fact read — a Rendition that reaches for a store has silently promoted itself to a View ([`view-and-rendition.md`](./view-and-rendition.md) §5), with the store standing in for the hook.

**Blazor.** The role boundary becomes an injection boundary: a Rendition is a `.razor` component whose only inputs are `[Parameter]`s and that `@inject`s nothing reporting a fact; a View is a `.razor` component that does inject one and selects with `@if`. Enforce it by folder — fact sources are services with no `.razor` at all, so "a source must not render" translates to "a source contains no markup", which is checkable by file type alone.

**Dioxus.** The compiler makes the rule cheap to check: a Rendition that wants a fact has to call a hook, and that call is visible in its body. Review rule: *if this component calls `use_resource` / `use_signal` / `use_global`, it is a View.* Naming follows Rust conventions — functions `snake_case`, components and props types `PascalCase`.

**Server-rendered and hypermedia stacks** (HTMX, Livewire, Rails/ERB, Phoenix, plain templates). The roles still apply; the layers just move. A Page is a route's template, a View is a partial that the controller or route handler *has already* resolved facts for, a Rendition is a partial selected by an `if` in the View, and a fact source is a query or a service call in the request handler. The "fact source returns data, never markup" rule maps directly: handlers return values, templates render. Treat "which partial do we show" as View logic and never let a Rendition partial reach for a model to decide its own existence.

## 4. Path aliases and module resolution

Examples elsewhere write `@/ui/adaptive/…`, a TypeScript-style alias. Substitute your project's mechanism — `@`/`~` aliases in `tsconfig`/`vite`/webpack, relative paths, Vue aliases, Blazor `_Imports.razor` plus namespaces, Rust `crate::ui::adaptive::…`. The rule being expressed is the import direction ([`primitives-and-imports.md`](./primitives-and-imports.md) §3), not the alias syntax.

## 5. What never translates

Three things are framework-independent and must survive any port:

1. A fact source returns data, never markup (`/states` defines sources; this skill enforces the seam).
2. The View is the only unit that both reads a fact and selects what renders ([`view-and-rendition.md`](./view-and-rendition.md) §3).
3. Imports point downward and never skip a primitive tier ([`primitives-and-imports.md`](./primitives-and-imports.md) §3).

If a framework makes one of these awkward, the framework is where you add discipline — the role model does not bend.
