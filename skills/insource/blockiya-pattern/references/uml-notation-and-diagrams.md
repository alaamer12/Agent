# UML Notation System

## Table of Contents

- [Notation system overview](#notation-system-overview)
- [Block representation](#block-representation)
- [Stereotypes](#stereotypes)
- [Visibility modifiers](#visibility-modifiers)
- [Flow direction markers](#flow-direction-markers)
- [Relationships](#relationships)
- [Complete notation reference](#complete-notation-reference)
- [Diagram examples](#diagram-examples)
- [Mermaid template (updated v2.0)](#mermaid-template-updated-v20)
- [Naming conventions](#naming-conventions)
- [Full Example Class Diagram: BillingOverview](#full-example-class-diagram-billingoverview)
- [Runtime Sequence Diagram Example: TodoBlock Edit & Save Flow](#runtime-sequence-diagram-example-todoblock-edit--save-flow)

---

## Notation system overview

### Core principles

1. **Minimal syntax** — use only essential markers
2. **Directional clarity** — arrows and symbols indicate flow direction
3. **Contextual visibility** — scope is relative to hierarchy level
4. **Standard base** — built on UML class diagrams for familiarity
5. **Tool agnostic** — works in Mermaid, PlantUML, or hand-drawn diagrams

### Notation categories

| Category | Purpose | Symbols |
| --- | --- | --- |
| **Stereotypes** | Classify block types | `<<Page>>`, `<<Compound>>`, `<<Atomic>>`, `<<Behavioral>>`, `<<Adapter>>` |
| **Visibility** | Show export/scope level | `●`, `○`, `◆` |
| **Flow Direction** | Indicate data/event flow | `▼`, `▲` |
| **Relationships** | Show composition/usage | `*--`, `..>`, `⊙--`, `··>` |

---

## Block representation

### Standard block structure

Every Blockiya is represented as a UML class with four sections:

```
┌─────────────────────────────────────┐
│ <<Stereotype>> Visibility           │  ← Header: Type & Scope
│ BlockName                           │  ← Block Name
├─────────────────────────────────────┤
│ ▼ Props (Inflow):                   │  ← Section 1: Inputs
│   - prop1: Type                     │
│   - prop2: Type                     │
│   - onEvent: Function               │
├─────────────────────────────────────┤
│ ◆ Internal State:                   │  ← Section 2: Hidden State
│   - state1: Type                    │
│   - derivedValue: Type              │
│   - useQuery() hook                 │
├─────────────────────────────────────┤
│ ▲ Events (Outflow):                 │  ← Section 3: Outputs
│   - onEventName()                   │
│   - onAnotherEvent()                │
└─────────────────────────────────────┘
```

### Section breakdown

**Header** — stereotype (block classification) + visibility marker + block name.

**Props section (▼ Inflow)** — all props passed from parent, including type annotations. Callback props received as props are marked `▼` because they flow *into* the block.

**Internal section (◆ Hidden)** — local state (`useState`, `useReducer`), derived values (`useMemo`), internal query hooks, helper functions, context consumption. Never exposed in diagrams unless showing implementation detail.

**Events section (▲ Outflow)** — callback props *invoked* by this block, custom events emitted, navigation intents. The same callback that appears in `▼` as a received prop appears in `▲` when this block calls it.

### Minimal block (simple cases)

For simple blocks, omit empty sections:

```
┌─────────────────────────────────────┐
│ <<Primitive>>                       │
│ Button                              │
├─────────────────────────────────────┤
│ ▼ Props:                            │
│   - variant: ButtonVariant          │
│   - onClick: Function               │
│   - children: ReactNode             │
└─────────────────────────────────────┘
```

---

## Stereotypes

Stereotypes classify blocks by architectural role. They appear in the header of every block diagram.

| Stereotype | Meaning | When to use | Example |
| --- | --- | --- | --- |
| `<<Page>>` | Top-level route component | Framework route pages (Next.js, React Router, etc.) | `BillingOverviewPage` |
| `<<Feature>>` | Large workflow orchestrator | Multi-step processes, wizards | `CheckoutWizardBlock` |
| `<<Compound>>` | Multi-component Blockiya | Combines 2–5 child blocks | `BillingOverviewBlock` |
| `<<Atomic>>` | Single-purpose Blockiya | Focused, leaf-level block | `UsageChartsBlock` |
| `<<Primitive>>` | Non-behavioral design system component | Visual tokens only, no interaction state | `Button`, `VStack`, `Text` |
| `<<Behavioral>>` | Behavioral design system component | Owns interaction state internally | `Dropdown`, `Modal`, `Tooltip` |
| `<<Adapter>>` | Third-party library wrapper | Wraps external tools, translates tokens and events | `CodeEditorAdapter`, `TerminalAdapter` |
| `<<Context>>` | Context object provider | State sharing across descendants | `ProjectContext` |
| `<<Hook/Query>>` | Data fetching hook | External data source | `useBillingUsage` |

### Stereotype guidelines

**`<<Page>>`** — always at the top of hierarchy diagrams. Handles routing, layout, and styled orchestration. Passes configuration down to feature blocks.

**`<<Feature>>`** — complex workflows (wizards, multi-step forms). Typically 5+ child blocks. May provide context to descendants.

**`<<Compound>>`** — the most common type. Orchestrates 2–5 child blocks. Pure composition logic.

**`<<Atomic>>`** — single responsibility. Few or no child blocks. Leaf nodes in hierarchy.

**`<<Primitive>>`** — pure visual tokens. No interaction model. Referenced via dependency (`..>`), never as main subjects. Part of the design system.

**`<<Behavioral>>`** — carries interaction complexity (open/close state, keyboard nav, focus trapping). Always uses compound component API shape. Owns its interaction state internally — callers never see `isOpen`. Referenced via dependency (`..>`).

**`<<Adapter>>`** — wraps a third-party library. Owns token translation, event translation, and lifecycle management. The Blockiya treats it like a primitive — mounts it, passes data, receives clean events back. The library's internals never reach the Blockiya.

**`<<Context>>`** — a context object provided by a parent Blockiya. Consumed by descendants via `useContext`. Use the `⊙--` / `··>` relationship symbols.

**`<<Hook/Query>>`** — data fetching hooks. Consumed internally by Blockiyas. Shown as a dependency when worth documenting.

---

## Visibility modifiers

Visibility is **contextual** and **relative** to the parent block.

| Symbol | Name | Meaning | Export location |
| --- | --- | --- | --- |
| `●` | Public | Exported from feature module | `features/billing/blockiyas/index.ts` |
| `○` | Private | Internal to parent Blockiya | `BillingOverviewBlock/children/` |
| `◆` | Internal | Implementation detail (state/hooks) | Never exported, runtime only |

### Contextual scoping rules

```
Feature Level:
  ● BillingOverviewBlock        (public — exported from feature)
    ○ UsageChartsBlock          (private — child of BillingOverview)
    ○ InvoiceHistoryBlock       (private — child of BillingOverview)

Another feature:
  ● ProjectEditorBlock          (public in projects feature)
    ○ ProjectFormFields         (private child)
    ● TaskListBlock             (public — reused across features)
```

A block can be public (`●`) at the feature level and private (`○`) relative to its parent. The same block may have different visibility in different contexts.

The `◆` internal marker covers: `useState`/`useReducer` state, `useMemo`/`useCallback` derived values, internal query hooks, helper functions, local variables. Never expose these in diagrams unless showing implementation detail.

---

## Flow direction markers

| Symbol | Direction | Meaning | Example |
| --- | --- | --- | --- |
| `▼` | Downward | Props/data flowing from parent to child | `subscription: Subscription` |
| `▲` | Upward | Events/callbacks flowing from child to parent | `onSaveIntent()` |

### The callback distinction

A callback prop like `onUpgradeIntent: Function` is marked `▼` because it **flows into** the block as a prop. The same callback invocation `onUpgradeIntent()` is marked `▲` because the **event flows out** when called.

- `▼` — what does this block receive?
- `▲` — what does this block emit/trigger?

```
┌─────────────────────────────────────┐
│ BillingOverviewBlock                │
├─────────────────────────────────────┤
│ ▼ Props (Inflow):                   │
│   - subscription: Subscription      │
│   - onUpgradeIntent: Function       │  ← received as prop (▼)
├─────────────────────────────────────┤
│ ◆ Internal:                         │
│   - usage: UsageData                │
├─────────────────────────────────────┤
│ ▲ Events (Outflow):                 │
│   - onUpgradeIntent()               │  ← this block calls it (▲)
│   - onViewInvoicesIntent()          │
└─────────────────────────────────────┘
```

---

## Relationships

| Symbol | Name | Meaning | When to use |
| --- | --- | --- | --- |
| `*--` | Composition | Strong ownership (parent creates/destroys child) | Direct JSX children |
| `..>` | Dependency | Uses/references (weak coupling) | Primitives, adapters, utilities |
| `⊙--` | Context Provision | Provides context to descendants | `Context.Provider` |
| `··>` | Context Consumption | Consumes context | `useContext` hook |

```
Parent *-- Child       : ◆ owns (composition)
Block  ..> Primitive   : uses (dependency)
Provider ⊙-- Context  : provides
Consumer ··> Context  : consumes
```

### Relationship annotations

```
BillingOverviewBlock *-- UsageChartsBlock    : ◆ owns, controls via props
BillingOverviewBlock ..> VStack              : uses for layout
BillingOverviewBlock ..> Dropdown            : uses (<<Behavioral>>)
BillingOverviewBlock ..> CodeEditorAdapter   : uses (<<Adapter>>)
ProjectEditorBlock ⊙-- ProjectContext       : provides shared state
FormFields ··> ProjectContext               : consumes for validation
```

---

## Complete notation reference

```
┌─────────────────────────────────────────────────────────────┐
│                  BLOCKIYA UML NOTATION v2.0                 │
├─────────────────────────────────────────────────────────────┤
│ STEREOTYPES:                                                │
│   <<Page>>       Top-level route                            │
│   <<Feature>>    Large workflow orchestrator                │
│   <<Compound>>   Multi-component Blockiya                   │
│   <<Atomic>>     Single-purpose Blockiya                    │
│   <<Primitive>>  Non-behavioral design system component     │
│   <<Behavioral>> Behavioral design system component         │
│   <<Adapter>>    Third-party library wrapper                │
│   <<Context>>    Context provider                           │
│   <<Hook/Query>> Data fetching hook                         │
├─────────────────────────────────────────────────────────────┤
│ VISIBILITY (contextual):                                    │
│   ●  Public      (exported from feature)                    │
│   ○  Private     (internal to parent)                       │
│   ◆  Internal    (state/hooks/implementation)               │
├─────────────────────────────────────────────────────────────┤
│ FLOW DIRECTION:                                             │
│   ▼  Props/Data  (flowing downward into block)              │
│   ▲  Events      (flowing upward out of block)              │
├─────────────────────────────────────────────────────────────┤
│ RELATIONSHIPS:                                              │
│   *--  Composition    (strong ownership)                    │
│   ..>  Dependency     (uses/references)                     │
│   ⊙--  Provides       (context provision)                   │
│   ··>  Consumes       (context consumption)                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Diagram examples

### Example 1: Simple hierarchy

```
┌──────────────────────┐
│ <<Page>>             │
│ DashboardPage        │
└──────┬───────────────┘
       │ props ▼ / events ▲
       ▼
┌──────────────────────┐
│ <<Compound>> ●       │
│ DashboardBlock       │
├──────────────────────┤
│ ▼ userId: string     │
│ ▲ onRefresh()        │
└──────┬───────────────┘
       │
       ├─── *-- ○ StatsBlock    <<Atomic>>
       ├─── *-- ○ ActivityBlock <<Atomic>>
       └─── *-- ○ NotificationsBlock <<Atomic>>
```

### Example 2: Context object pattern

```
┌─────────────────────────────────────┐
│ <<Compound>> ●                      │
│ ProjectEditorBlock                  │
├─────────────────────────────────────┤
│ ▼ Props:                            │
│   - initialProject: Project         │
│   - onSaveIntent: Function          │
├─────────────────────────────────────┤
│ ◆ Internal:                         │
│   - project: Project                │
│   - errors: ValidationErrors        │
│   - isDirty: boolean                │
├─────────────────────────────────────┤
│ ⊙ Provides: ProjectContext          │
│   { project, updateProject,         │
│     errors, validate }              │
├─────────────────────────────────────┤
│ ▲ Events:                           │
│   - onSaveIntent(project)           │
└────────┬────────────────────────────┘
         │ ⊙ provides context
    ┌────┴────────┬──────────────┐
┌───────────┐ ┌────────────┐ ┌──────────┐
│ ○         │ │ ○          │ │ ○        │
│FormFields │ │Preview     │ │SaveCtrls │
│··> ctx    │ │··> ctx     │ │··> ctx   │
└───────────┘ └────────────┘ └──────────┘
```

### Example 3: Adapter in hierarchy

```
┌──────────────────────────┐
│ <<Compound>> ●           │
│ CodeEditorBlock          │
├──────────────────────────┤
│ ▼ fileId: string         │
│ ▼ onSaveIntent: Function │
├──────────────────────────┤
│ ◆ content: string        │
│ ◆ useFileContent() query │
├──────────────────────────┤
│ ▲ onSaveIntent(content)  │
└──────────┬───────────────┘
           │
           ├── ..> <<Adapter>> CodeEditorAdapter
           │         token translation (theme → CodeMirror)
           │         event translation (updateListener → onChange)
           │         lifecycle (mount, destroy)
           │
           └── ..> <<Primitive>> Box, Text
```

---

## Mermaid template (updated v2.0)

```mermaid
---
config:
  theme: default
  look: handDrawn
  layout: elk
---
classDiagram
    note "VISIBILITY:
    ● Public (exported from feature)
    ○ Private (internal children)
    ◆ Internal (state/hooks/queries)"
    note "FLOW DIRECTION:
    ▼ Props flowing in
    ▲ Events flowing out"
    note "STEREOTYPES:
    <<Page>>       Route / styled orchestrator
    <<Compound>>   Multi-component Blockiya
    <<Atomic>>     Single-purpose Blockiya
    <<Primitive>>  Non-behavioral design system component
    <<Behavioral>> Behavioral design system component (owns interaction state)
    <<Adapter>>    Third-party library wrapper
    <<Hook/Query>> External data source"
    note "RELATIONSHIPS:
    *--  Strong composition (owns)
    ..>  Dependency (uses)"

    class YourPage {
        <<Page>>
        ▼ route params
        ◆ state
        ▲ renders()
    }

    class YourBlock {
        <<Compound>> ●
        ▼ prop: Type
        ◆ state: Type
        ▲ onEvent()
    }

    class YourAdapter {
        <<Adapter>>
        ▼ value: Type
        ▼ onChange: Function
        ◆ translates tokens + events
    }

    class YourBehavioral {
        <<Behavioral>>
        ▼ onSelect: Function
        ◆ isOpen: boolean (internal)
    }

    YourPage ..> YourBlock : props ▼ / events ▲
    YourBlock ..> YourAdapter : uses
    YourBlock ..> YourBehavioral : uses
```

---

### Naming conventions

- Block names: use actual component names, include `Block` suffix — `BillingOverviewBlock`
- Adapter names: include `Adapter` suffix — `CodeEditorAdapter`, `TerminalAdapter`
- Props: use the host language's types — `subscription: Subscription` in TypeScript, `Subscription subscription` in C#, etc.
- Events: use `Intent` suffix — `onSaveIntent()`, `onUpgradeIntent()`

---

## Full Example Class Diagram: BillingOverview

> Source: `Diagram` specification (`assets/billing-overview-diagram.mmd`). Demonstrates `<<Page>>`, `<<Compound>>`, `<<Atomic>>`, `<<Primitive>>`, `<<Behavioral>>`, `<<Adapter>>`, and `<<Hook/Query>>` with contextual visibility (`●`, `○`, `◆`), flow direction (`▼`, `▲`), and relationship arrows (`*--`, `..>`).

```mermaid
---
config:
  theme: default
  look: handDrawn
  layout: elk
---
classDiagram
    note "VISIBILITY:
    ● Public (exported from feature)
    ○ Private (internal children)
    ◆ Internal (state/hooks/queries)"
    note "FLOW DIRECTION:
    ▼ Props flowing in
    ▲ Events flowing out"
    note "STEREOTYPES:
    <<Page>>       Route / styled orchestrator
    <<Compound>>   Multi-component Blockiya
    <<Atomic>>     Single-purpose Blockiya
    <<Primitive>>  Non-behavioral design system component
    <<Behavioral>> Behavioral design system component (owns interaction state)
    <<Adapter>>    Third-party library wrapper
    <<Hook/Query>> External data source"
    note "RELATIONSHIPS:
    *--  Strong composition (owns)
    ..>  Dependency (uses)"

    %% ── Page ──────────────────────────────────────────────────
    class BillingOverviewPage {
        <<Page>>
        ▼ route params
        ◆ subscription: Subscription
        ◆ navigate: NavigateFn
        ▲ renders()
    }

    %% ── Main Feature Block (Public) ────────────────────────────
    class BillingOverviewBlock {
        <<Compound>> ●
        ▼ subscription: Subscription
        ▼ onUpgradeIntent: Function
        ▼ onViewInvoicesIntent: Function
        ◆ usage: UsageData
        ◆ useBillingUsage() query
        ▲ onUpgradeIntent()
        ▲ onViewInvoicesIntent()
    }

    %% ── Child Blocks (Private) ─────────────────────────────────
    class UsageChartsBlock {
        <<Atomic>> ○
        ▼ data: UsageData
        ◆ chartConfig: Config
        ▲ renders charts
    }

    class InvoiceHistoryBlock {
        <<Atomic>> ○
        ▼ onViewAll: Function
        ◆ recentInvoices: Invoice[]
        ◆ useRecentInvoices() query
        ▲ onViewAll()
    }

    class PlanSummaryBlock {
        <<Atomic>> ○
        ▼ subscription: Subscription
        ▼ onChangePlan: Function
        ◆ planDetails: PlanInfo
        ▲ onChangePlan()
    }

    %% ── Non-Behavioral Primitives ──────────────────────────────
    class Card {
        <<Primitive>>
        ▼ variant?: string
        ▼ children: ReactNode
    }

    class VStack {
        <<Primitive>>
        ▼ gap: SpacingToken
        ▼ align: AlignValue
        ▼ children: ReactNode
    }

    class HStack {
        <<Primitive>>
        ▼ gap: SpacingToken
        ▼ justify: JustifyValue
        ▼ children: ReactNode
    }

    class Text {
        <<Primitive>>
        ▼ variant: TypographyToken
        ▼ children: string
    }

    class Button {
        <<Primitive>>
        ▼ variant: ButtonVariant
        ▼ onClick: Function
        ▼ children: ReactNode
    }

    %% ── Behavioral Primitives ──────────────────────────────────
    class Dropdown {
        <<Behavioral>>
        ▼ onSelect: Function
        ◆ isOpen: boolean
        ◆ manages focus + keyboard nav
    }

    %% ── Adapters ───────────────────────────────────────────────
    class UsageChartAdapter {
        <<Adapter>>
        ▼ data: UsageData
        ▼ height: SpacingToken
        ◆ translates tokens → chart lib
        ◆ translates onHover → onDataPoint
        ◆ manages chart lifecycle
    }

    %% ── Hooks / Queries ────────────────────────────────────────
    class useBillingUsage {
        <<Hook/Query>>
        + fetch usage data
        + returns UsageData
    }

    class useRecentInvoices {
        <<Hook/Query>>
        + fetch invoices
        + returns Invoice[]
    }

    %% ── Relationships: Hierarchy ───────────────────────────────
    BillingOverviewPage ..> BillingOverviewBlock : props ▼ / events ▲
    BillingOverviewBlock *-- UsageChartsBlock : ◆ owns
    BillingOverviewBlock *-- InvoiceHistoryBlock : ◆ owns
    BillingOverviewBlock *-- PlanSummaryBlock : ◆ owns

    %% ── Relationships: Non-Behavioral Primitive Usage ──────────
    BillingOverviewBlock ..> Card : uses
    BillingOverviewBlock ..> VStack : uses
    BillingOverviewBlock ..> HStack : uses
    BillingOverviewBlock ..> Text : uses
    BillingOverviewBlock ..> Button : uses
    UsageChartsBlock ..> VStack : uses
    UsageChartsBlock ..> Card : uses
    InvoiceHistoryBlock ..> HStack : uses
    InvoiceHistoryBlock ..> Text : uses
    PlanSummaryBlock ..> Card : uses
    PlanSummaryBlock ..> Button : uses

    %% ── Relationships: Behavioral Primitive Usage ──────────────
    PlanSummaryBlock ..> Dropdown : uses

    %% ── Relationships: Adapter Usage ───────────────────────────
    UsageChartsBlock ..> UsageChartAdapter : uses

    %% ── Relationships: Internal Queries ────────────────────────
    BillingOverviewBlock ..> useBillingUsage : ◆ internal query
    InvoiceHistoryBlock ..> useRecentInvoices : ◆ internal query
```

---

## Runtime Sequence Diagram Example: TodoBlock Edit & Save Flow

> Source: `Design` specification (`assets/todo-edit-sequence-diagram.png`, rendered in v2.2.0 from `assets/todo-edit-sequence-diagram.mmd` — the canonical text source; earlier builds trace to `Capture.png`, archived as `todo-edit-sequence-diagram-legacy.png`). Illustrates the complete 17-step Strict Blockiya runtime lifecycle across a stateless View, a `<<Compound>>` Blockiya, `useDerivedState`, `useIntent`, and the parent Page.

Visual asset bundled at: `assets/todo-edit-sequence-diagram.png`

### Participants

1. **User** — End user interacting with the UI
2. **TodoItem** (`View`) — Stateless presentational child view
3. **TodoBlock** (`«Compound»`) — Compound Blockiya owning `editingId`, `todos`, and `useDerivedState` for `editDraft`
4. **useIntent** (`saveEdit`) — `blockiya-core` async intent lifecycle manager (`fire`, `isLoading`, `await handler`)
5. **TodoPage** — Parent route/page receiving upward intents

### Complete 17-Step Runtime Sequence

1. **User -> TodoItem**: `click "edit" button`
2. **TodoItem -> TodoBlock**: `onEditIntent(id)` *(annotation: `view fires & stops`)*
3. **TodoBlock (self)**: `setEditingId(id)`
4. **TodoBlock (self)**: `useDerivedState detects source Δ` -> `setState(editingTodo.text)`
5. **TodoBlock -->> TodoItem**: `re-render: isEditing=true, editDraft=text`
   - *Phase: `user types in the input field`*
6. **User -> TodoItem**: `onChange(newText)`
7. **TodoItem -> TodoBlock**: `onEditDraftChange(newText)`
8. **TodoBlock (self)**: `setEditDraft(v)`
   - *Phase: `user clicks "save"`*
9. **User -> TodoItem**: `click "save"`
10. **TodoItem -> TodoBlock**: `onSaveEditIntent(id)` *(annotation: `= saveEditIntent.fire(id)`)*
11. **TodoBlock -> useIntent (saveEdit)**: `fire(id)`
12. **useIntent (saveEdit) (self)**: `isLoading = true`
    - **useIntent (saveEdit) -->> TodoItem**: `re-render: button disabled`
13. **useIntent (saveEdit) (self)**: `await handler(id)`
    - **TodoBlock (self)**: `setTodos(...) · setEditingId(null)`
14. **useIntent (saveEdit) (self)**: `isLoading = false`
15. **TodoBlock -> TodoPage**: `onTodoCountChangeIntent(n)` *(annotation: `block fires & stops`)*
16. **TodoPage (self)**: `setActiveCount(n)`
17. **TodoBlock -->> TodoItem**: `re-render: display mode restored`
    - **TodoBlock (self)**: `useDerivedState resets editDraft`

### Text-Native Mermaid Sequence Equivalent

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant TodoItem as TodoItem<br/>(View)
    participant TodoBlock as TodoBlock<br/>(«Compound»)
    participant saveEdit as useIntent<br/>(saveEdit)
    participant TodoPage

    User->>TodoItem: click "edit" button
    TodoItem->>TodoBlock: onEditIntent(id) — view fires & stops
    TodoBlock->>TodoBlock: setEditingId(id)
    Note over TodoBlock: useDerivedState detects source Δ<br/>setState(editingTodo.text)
    TodoBlock-->>TodoItem: re-render: isEditing=true, editDraft=text

    Note over TodoBlock: user types in the input field
    User->>TodoItem: onChange(newText)
    TodoItem->>TodoBlock: onEditDraftChange(newText)
    TodoBlock->>TodoBlock: setEditDraft(v)

    Note over TodoBlock: user clicks "save"
    User->>TodoItem: click "save"
    TodoItem->>TodoBlock: onSaveEditIntent(id) = saveEditIntent.fire(id)
    TodoBlock->>saveEdit: fire(id)
    Note over saveEdit: isLoading = true
    saveEdit-->>TodoItem: re-render: button disabled
    Note over saveEdit: await handler(id)
    TodoBlock->>TodoBlock: setTodos(...) · setEditingId(null)
    Note over saveEdit: isLoading = false
    TodoBlock->>TodoPage: onTodoCountChangeIntent(n) — block fires & stops
    TodoPage->>TodoPage: setActiveCount(n)
    TodoBlock-->>TodoItem: re-render: display mode restored
    Note over TodoBlock: useDerivedState resets editDraft
```

### Stereotype Synchronization Note (v2.0 -> v2.2.0)

`UML Notation System` is versioned `v2.0` and lists the 9 original stereotypes (`<<Page>>`, `<<Feature>>`, `<<Compound>>`, `<<Atomic>>`, `<<Primitive>>`, `<<Behavioral>>`, `<<Adapter>>`, `<<Context>>`, `<<Hook/Query>>`). Methodology `v2.1.0` adds a 10th stereotype; `v2.2.0` redefines its semantics as an interoperability slot (the notation symbols are unchanged):

- `<<Utility>>` — Compatible helper in the interoperability slot (`useIntent`, `If`, `Maybe`, `For`, `Repeat`, `Compose`, `useDerive`, `useDerivedState`): works alongside Blockiya machinery without contradiction and without taking over control — no domain knowledge, no styling, no visual output; referenced via dependency (`..>`).
