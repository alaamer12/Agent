# Roles — what each piece of UI is doing

> The taxonomy this whole system rests on: six architectural roles, and the law that a role is never the same thing as the implementation carrying it. Read this before any other reference. Folder placement is [`structure.md`](./structure.md); what a View is allowed to consult is [`facts.md`](./facts.md) and [`view-and-rendition.md`](./view-and-rendition.md).

## 1. The central law

> **"Component-framework-unit" and "architectural Component" are not synonymous.**

A unit of UI code — a React component, a Vue SFC, a Solid component, a Blazor Razor component, a Dioxus function — is an **implementation mechanism**. A role is **what that unit represents inside a particular UI composition**. Nothing in this document is decided by which framework renders it, how large the file is, or what the framework calls the construct.

The common failure this law exists to prevent: a codebase where every rendered unit is called a component, so the name carries no information about what the unit does.

```
components/
├── SearchPageComponent
├── SearchViewComponent
├── SearchInputComponent
├── SearchTitleComponent
├── SearchChipComponent
```

Versus the same UI read as roles: one Page, one View, one Component, two Decorations, one UI Element. The second communicates the composition; the first communicates that a framework can render it.

## 2. The hierarchy

Six roles, arranged in four composition levels plus one supporting role that is a subtype of another:

```
Application
└── Page                 ← level 1: a route or screen
    └── View             ← level 2: a meaningful section
        ├── Component    ← level 3: a purposeful functional unit
        ├── Decoration   ← supporting: context, explanation, emphasis
        │   └── Aligner    (a Decoration with a positional relationship)
        ├── View         (nesting is unrestricted — see §5)
        └── UI Element   ← level 4: primitive construction blocks
```

| Role | Responsibility | The question it answers |
| --- | --- | --- |
| **Page** | Compose the major sections of a screen | What sections make up this screen? |
| **View** | Represent one meaningful UI section | What is this section about? |
| **Component** | Deliver one purposeful user-facing function | What meaningful thing is the user doing here? |
| **Decoration** | Supply supporting context or presentation | What explains or surrounds that function? |
| **Aligner** | Supply *positional* support to the primary Component | What leads, trails, or aligns with it? |
| **UI Element** | Provide a primitive construction block | What pieces is it built from? |

Two summary statements, useful as the shortest form of the model:

> **Pages compose Views. Views compose purposeful UI. UI Elements are the primitives that purpose is built from.**

> The Page is the composition boundary, the View the meaningful-section boundary, the Component the purposeful-function boundary, Decoration/Aligner the supporting boundary, the UI Element the primitive boundary.

## 3. Page

A Page is an application-level screen or route. Its only job is **composition**: it names the Views that make up the screen and stops there. A Page that constructs primitive controls, or that holds the interaction logic of one section, has taken on a role that belongs lower down.

```
ProfilePage
├── ProfileHeaderView
├── ProfileInformationView
├── StatisticsView
├── PostsView
└── AccountActionsView
```

Read at a glance, that Page is a table of contents. It says nothing about how any section works, which is the point.

## 4. View

> **A View is a meaningful, self-contained section of a Page with its own visual and functional purpose.**

This is deliberately narrower than the "V" in MVC/MVVM, where View means the whole UI layer or the entire screen. Here a View is one section, not the app.

A View may contain a primary Component, Decorations, Aligners, UI Elements, and other Views. "Primary Component" describes the common case where a section has a central functional focus — it is not a requirement that every View have exactly one, nor that it have any.

```
SearchView                    ProfileEditor's surroundings
├── Title        → Decoration ─────────────┐
├── Description  → Decoration              │ the Component is the focus,
├── ProfileEditor → Component ←────────────┘ the rest explains it
└── SaveChangesAction → Component
```

**Views are defined by purpose, not depth.** `Page → View` is not a maximum. A modal reached from a danger zone is three Views deep and each is still a View:

```
AccountSettingsView
└── DangerZoneView
    └── DeleteAccountView
        └── ConfirmationModalView
```

A View should exist because a person would recognise that section as a thing — a search, a checkout, a confirmation. Do not create Views because elements happen to occupy one rectangle.

## 5. Component

> **A Component is the primary purposeful or functional unit within a View — it performs a meaningful action, interaction, or responsibility for the user.**

Reusability is not the test. Small size is not the test. Being renderable by a framework is not the test. The test is whether the unit carries a user-facing *purpose*:

```
SearchInput    → Component      (the user searches with it)
LoginForm      → Component
PaymentForm    → Component
ConfirmDeletion→ Component
Input          → UI Element     (it knows nothing about searching)
Button         → UI Element
```

A Component may contain other Components when they coordinate — see [`composition-shapes.md`](./composition-shapes.md) for the test that distinguishes a coordinated group from a merely adjacent one.

## 6. Decoration and Aligner

**Decorations** provide context, explanation, emphasis, or additional information around primary functional content: titles, descriptions, captions, hints, badges, section labels, illustrations, supporting text, dividers, status indicators.

**An Aligner is a Decoration with a stated positional relationship** to the primary Component — leading, trailing, above, below:

```
[ 🔍 ]  [ input field…      ]  [ ✕ ]
  ↑              ↑               ↑
leading       Component       trailing
Aligner                        Aligner
```

```
Decoration
└── Aligner        (Aligner ⊂ Decoration — not a sibling category)
```

Because an Aligner is a Decoration and not a separate tier, it does not need its own folder or its own framework construct. It lives wherever the surrounding Decoration belongs, and "Aligner" functions as an architectural classification rather than a name you must write into code.

## 7. UI Element

> **UI Elements are the primitive construction tools of the interface** — Buttons, Inputs, Text, Icons, Chips, Checkboxes, Radios, Avatars, Selects, Images, Links.

The distinction that matters is between the primitive and the purposeful unit built from it:

```
Input + Icon + Button   → (assembled) →  SearchInput
UI Elements                              Component
```

A primitive must not know which feature is using it. `Button` knows about `disabled`, `loading`, `size`, `variant`, `type`, `onClick`, `children`. It must not know about deleting accounts, checkout, or following users. The moment it does, it has been promoted into a Component and belongs in that feature.

This role is subdivided into two *placement tiers* (`base` and `adaptive`) in [`primitives-and-imports.md`](./primitives-and-imports.md). Tiers change where a primitive lives and what it may import; they never change its role.

## 8. Classification is contextual

An object has no permanent role stamped on it. Ask:

> **What role does this object play in *this* composition?**

```
Button                    in isolation            → UI Element
ConfirmAccountDeletion    wrapping that Button    → Component
Text                      as a paragraph of help  → Decoration
Modal                     as a full focused interaction → View
```

A Modal is the clearest illustration. It is conventionally "a reusable component", but when it presents context plus a decision plus purposeful actions, architecturally it *is* a View:

```
ConfirmationModalView
├── ConfirmationText   → Decoration
├── ConfirmAction      → Component
└── CancelAction       → Component
```

Nothing about that judgment depends on how the modal is implemented.

## 9. Design principles

- **Role over implementation** — never classify by the construct the framework gives you.
- **Purpose over size** — a Component is not a Component for being large; a UI Element is not a primitive for being small.
- **Composition over rigid hierarchy** — Views nest, Components may contain Components; follow the interface's real shape instead of enforcing depth.
- **Context matters** — the same implementation plays different roles in different compositions.
- **Pages stay compositional** — a Page says what makes up the screen, never how each piece works.
- **Views have a recognisable purpose** — a section a person could name.

Do not extract to satisfy the taxonomy. There is no requirement to turn `<h1>Search</h1>` into a named abstraction; the model exists to make structure clearer, not to increase file count.

## 10. What this does NOT replace

Feature-Based Architecture answers *what domain does this code belong to*. This model answers *what role does this piece play in constructing its section*. They are orthogonal axes and both are needed — see [`structure.md`](./structure.md) §2.

Neither does this model replace ordinary software architecture. State, business logic, data access, and services sit beside the UI hierarchy, not inside it — see [`facts.md`](./facts.md).

## 11. The five questions

```
PAGE        What screen are we constructing?
VIEW        What meaningful section are we constructing?
COMPONENT   What purposeful functionality is the user interacting with?
DECORATION  What supports, explains, or surrounds it?  (+ is it positional → Aligner?)
UI ELEMENT  What primitive pieces construct it?
```

If you can answer those five for a piece of UI, you have its role. Everything else in this system — facts, Renditions, placement poles, naming — is decided downstream of that answer.
