# PVC Architecture Core — Full Reference

> Canonical home for the conceptual model: roles, principles, benefits, worked examples, recursive composition. Rules and violations live in `rules-and-violations.md`. Project folders live in `project-structure.md`.

Distilled from the original PVC Architecture documents.

---

## 1. Overview and Motivation

Modern web applications commonly organize around:

```
Page
└── Components
```

or a feature-oriented extension:

```
Pages
Features
Components
UI
```

These work, yet leave an important question unanswered:

> **How is an individual page actually constructed?**

A page is rarely a collection of unrelated components. It is composed of meaningful sections, each with a primary purpose, supporting information, supporting actions, and primitive interface elements.

PVC is a **role-based UI construction model**. A web page is constructed from Views; each View is constructed from a primary Component (or Components), its Decorations/Aligners, and lower-level UI Elements.

Hierarchy:

```
Application
    │
    └── Page
         │
         ├── View
         │    ├── Component
         │    ├── Decoration / Aligner
         │    └── UI Elements
         │
         ├── View
         │    └── ...
         │
         └── View
              └── ...
```

Central principle:

> **Pages compose Views. Views compose purposeful UI. UI Elements provide the primitive construction blocks.**

---

## 2. The Problem With a Generic Component Model

In component frameworks (React, Vue, Svelte, Solid, etc.) almost anything can be called a component:

```
Button
SearchInput
SearchSection
Modal
Dashboard
Page
```

All may be implemented as framework component units. Treating them as the same architectural concept loses useful information.

Consider:

```jsx
<Dashboard>
    <Welcome />
    <Statistics />
    <RecentActivity />
    <Goals />
</Dashboard>
```

The term "component" does not tell us what role each item plays:

- primitive controls?
- functional units?
- complete sections?
- supporting elements?
- entire compositions?

PVC separates **implementation technology** from **architectural role**.

- A framework component unit is an implementation mechanism.
- A View, Component, Decoration, or UI Element is an **architectural role**.

---

## 3. Core Hierarchy

Four primary concepts:

```
Page
  ↓
View
  ↓
Component
  ↓
UI Element
```

with Decorations/Aligners supporting the View and its Component(s):

```
Page
└── View
    ├── Decorations / Aligners
    ├── Component
    └── UI Elements
```

These concepts are not a strict tree in which every object must belong to exactly one category forever. They describe **what something is doing within a particular composition**.

---

## 4. Page

A **Page** represents an application-level screen or route.

Primary responsibility: composition.

A Page should answer:

> **What major Views make up this screen?**

Example:

```jsx
<DashboardPage>
    <WelcomeView />
    <StatisticsView />
    <RecentActivityView />
    <GoalsView />
    <RecommendationsView />
</DashboardPage>
```

The Page should not need to know every primitive detail inside those Views.

Conceptually:

```
Page = Composition of Views
```

A Page is therefore primarily a **container and composition boundary**.

---

## 5. View

A **View** is a meaningful, self-contained portion of a Page.

It represents a focused piece of UI rather than an entire route.

This is an intentional distinction from traditional MVC/MVVM terminology, where "View" can mean the entire user-interface layer or screen.

In PVC:

> **A View is a meaningful section of a Page with its own visual and functional purpose.**

Examples:

```
SearchPage
└── SearchView
```

```
DashboardPage
├── WelcomeView
├── StatisticsView
├── ActivityView
└── GoalsView
```

A View may contain:

- a primary Component (or multiple Components)
- supporting Decorations
- Aligners
- UI Elements
- other Views

### Views are composable

A View can contain another View:

```
DashboardView
└── DeleteAccountView
    └── ConfirmationModalView
```

There is no maximum depth rule. Nested Views are allowed whenever the UI naturally forms meaningful nested compositions.

Therefore:

> **A View is defined by its purpose and composition, not by its depth in the hierarchy.**

---

## 6. Component

A **Component** is the primary purposeful or functional unit within a View.

Key characteristic is **not** simply that it is reusable or implemented as a framework component unit.

Important characteristic:

> **It performs a meaningful action, interaction, or functional responsibility for the user.**

Examples:

```
SearchView
└── SearchInput          ← Component (the thing the user uses to search)
```

```
LoginView
└── LoginForm
```

```
CheckoutView
└── PaymentForm
```

```
ProfileView
└── ProfileEditor
```

The Component is the **functional focus** of the View.

"Primary Component" is common-case language only. A View may contain zero, one, or many Components. There is no hard requirement for exactly one.

---

## 7. Decorations

**Decorations** are supporting elements that provide context, explanation, emphasis, or additional information around the primary functional content.

Examples:

```
Title
Description
Caption
Hint
Badge
Section Label
Illustration
Supporting Text
Divider
Status Indicator
```

Example:

```
SearchView
├── Title                → Decoration
├── Description          → Decoration
├── SearchInput          → Component
└── CommonKeywords       → Decoration
```

Title and Description are not the primary interaction; they explain and contextualize it.

---

## 8. Aligners

**Aligners are a specialized form of Decorations** (Aligner ⊂ Decoration).

The term describes their typical relationship to the primary Component.

They commonly appear:

```
Leading
Trailing
Top
Bottom
```

or otherwise support and visually align with the main Component.

Example:

```
SearchInput
├── SearchIcon      → Leading Aligner
└── ClearButton     → Trailing Aligner
```

Visual:

```
[ Icon ] [ Input field ] [ Clear ]
   ↑          ↑             ↑
leading    component     trailing
aligner                   aligner
```

Important distinction:

> **Decoration describes the general supporting role; Aligner describes a decoration's positional/supporting relationship to the primary Component.**

Therefore:

```
Decoration
└── Aligner
```

An Aligner is a Decoration with a particularly meaningful positional role. The name need not contain the word "Aligner".

---

## 9. UI Elements

**UI Elements are the primitive construction tools of the interface.**

They are the lowest-level reusable pieces from which purposeful Components and Decorations can be constructed.

Examples:

```
Button
Input
Text
Icon
Chip
Checkbox
Radio
Avatar
Select
Image
Link
```

Critical distinction between the **primitive** and the **purposeful unit built from it**:

```
UI Elements
├── Input
├── Icon
└── Button
       ↓
SearchInput Component
```

The raw `Input` is merely a primitive interface element.  
`SearchInput` gives those primitives a meaningful user-facing purpose.

Therefore:

```
Input       → UI Element
SearchInput → Component
```

Likewise:

```
Button                  → UI Element
ConfirmAccountDeletion  → Component
```

Classification depends on role and abstraction level.

---

## 10. Full Example — Search View

Visual:

```
Search
Search for users, posts, or topics...

[ 🔍 Search..................... ]

Common searches:
[React] [Python] [JavaScript]
```

Architectural structure:

```
SearchView
│
├── Title
│     └── Decoration
│
├── Description
│     └── Decoration
│
├── SearchInput
│     └── Component
│          ├── SearchIcon
│          │     └── UI Element / Leading Aligner
│          │
│          ├── Input
│          │     └── UI Element
│          │
│          └── ClearButton
│                └── UI Element / Trailing Aligner
│
└── CommonKeywords
      └── Decoration
           └── Chip
                └── UI Element
```

The entire structure is one **View**.  
SearchInput is its primary **Component**.  
Surrounding information is **Decoration**.  
Leading/trailing supporting pieces can be classified as **Aligners**.  
Primitive controls are **UI Elements**.

---

## 11. Full Example — Modal View

A Modal is commonly treated as a reusable Component:

```
Modal
```

In this architecture a Modal can instead be understood as a **View** when it represents a complete focused interaction.

Example:

```
ConfirmationModalView
│
├── ImportantConfirmationText
│     └── Decoration / Aligner
│
└── Actions
      ├── Confirm
      │     └── Component
      │
      └── Cancel
            └── Component
```

The entire Modal is a View because it is a meaningful composition containing:

- context
- a decision
- one or more purposeful actions

The buttons are Components because they have meaningful user-facing purposes.  
Their underlying primitive button implementation may itself be a UI Element.

This does **not** mean a Modal cannot technically be implemented as a framework component unit.  
It simply means:

> **"framework component unit" and "architectural Component" are not synonymous.**

---

## 12. Contextual Classification

One of the most important principles: classification is **contextual**.

An object does not necessarily have one permanent architectural classification everywhere.

Always ask:

> **What role does this object play in this composition?**

Example — Button:

```
Button
└── UI Element
```

But a purposeful action constructed around that primitive:

```
ConfirmDeletion
└── Component
    └── Button
        └── UI Element
```

Similarly, a Modal can be implemented using framework component units while architecturally being:

```
Modal
└── View
```

Crucial separation:

```
Implementation identity
        ≠
Architectural role
```

A framework component unit is simply a technical implementation unit.  
The architecture classifies **what that unit represents in the UI composition**.

---

## 13. Role Over Implementation

Avoid the common mistake:

> Assuming that every framework component unit should be called a Component architecturally.

Example:

```jsx
function SearchView() {}
function ConfirmationModal() {}
function SearchInput() {}
function Button() {}
function Text() {}
```

All five may be framework component units. Architecturally:

```
SearchView           → View
ConfirmationModal    → View
SearchInput          → Component
Button               → UI Element
Text                 → UI Element / Decoration (depending on role)
```

This allows the architecture to describe the UI more accurately.

---

## 14. Recursive Composition

The model is intentionally recursive.

A View can contain another View:

```
Page
└── View
    ├── View
    │   ├── Component
    │   └── Decorations
    │
    └── Component
```

A Component can contain UI Elements:

```
Component
├── Input
├── Button
└── Icon
```

A View can contain multiple Components:

```
View
├── Component
├── Component
└── Component
```

A View can also contain another View alongside Components:

```
View
├── NestedView
├── Component
└── Decorations
```

There is **no requirement** for every View to have exactly one Component.  
The concept of a "primary Component" describes the common case where the View has a central functional focus.

---

## 15. Page Construction

With this model, Page construction becomes highly readable.

Example:

```
ProfilePage
│
├── ProfileHeaderView
├── ProfileInformationView
├── StatisticsView
├── PostsView
└── AccountActionsView
```

The page communicates the **major visual and functional sections**.

Each View then communicates its internal construction:

```
ProfileInformationView
│
├── Title
├── Description
├── ProfileEditor
└── SaveChangesAction
```

And the lower level:

```
ProfileEditor
├── Input
├── Select
├── Avatar
└── Button
```

Multiple useful levels of abstraction:

```
Page
    ↓
Major UI section
    ↓
Purposeful interaction
    ↓
Primitive interface
```

---

## 16. Separation of Concerns

| Concept       | Primary responsibility                                      |
|---------------|-------------------------------------------------------------|
| **Page**      | Compose the major sections of a route/screen                |
| **View**      | Represent a meaningful section of UI                        |
| **Component** | Provide a purposeful functional/interactive unit            |
| **Decoration**| Provide supporting context, information, or presentation    |
| **Aligner**   | Provide supporting positional/structural decoration         |
| **UI Element**| Provide primitive interface construction blocks             |

Each level answers a clear question:

- **Page** — What sections make up this screen?
- **View** — What is this section about?
- **Component** — What is the meaningful functionality here?
- **Decoration** — What supports or explains that functionality?
- **Aligner** — What supports or aligns with the primary functionality?
- **UI Element** — What primitive interface pieces are used to construct it?

---

## 17. Design Principles

### 17.1 Role over implementation

Do not classify something merely by how it is implemented.

```
Framework component unit
        ≠
Architectural Component
```

### 17.2 Purpose over size

A Component is not a Component because it is large.  
A UI Element is not a UI Element because it is small.  
Classification comes from **purpose and abstraction**.

### 17.3 Composition over rigid hierarchy

Views may contain Views.  
Components may contain other Components where appropriate.  
The architecture should follow the natural structure of the interface rather than enforcing artificial depth restrictions.

### 17.4 Context matters

The same technical implementation can have different architectural roles in different contexts.  
Always ask: **What role does this thing play here?**

### 17.5 Pages should remain compositional

A Page should primarily communicate:

```
"What makes up this screen?"
```

rather than:

```
"How does every small piece of this screen work?"
```

### 17.6 Views should have a clear purpose

A View should represent something users can conceptually recognize as a section, interaction, state, or focused piece of the interface.  
Avoid creating Views merely because a group of elements happens to occupy a rectangle.

---

## 18. Benefits

### Better readability

A developer can understand a page at a glance:

```
DashboardPage
├── WelcomeView
├── StatisticsView
├── ActivityView
└── GoalsView
```

### Better semantic meaning

Instead of calling everything a component, the architecture communicates why something exists.

### Better separation

Primitive UI controls do not become mixed with complete functional interactions.

### Better composition

Views become reusable composition units rather than only routes/pages.

### Better scalability

Large pages can be decomposed without turning the entire application into an enormous collection of generic components.

### Better communication

Developers can say:

> "This is a View with a primary Component and two supporting Aligners."

instead of:

> "This is a component containing some components."

The former communicates substantially more information.

---

## 19. Compact Mental Model

The entire architecture can be remembered through five questions:

```
PAGE
"What screen are we constructing?"

VIEW
"What meaningful section are we constructing?"

COMPONENT
"What purposeful functionality is the user interacting with?"

DECORATION / ALIGNER
"What supports, explains, or surrounds that functionality?"

UI ELEMENT
"What primitive interface pieces construct it?"
```

This results in a UI construction philosophy based not on the question:

> **"Is this a framework component unit?"**

but on:

> **"What role does this piece play in constructing the interface?"**

That distinction is the foundation of the model.

---

## 20. Final Model Diagram

```
                         PAGE
                           │
              ┌────────────┼────────────┐
              ↓            ↓            ↓
            VIEW         VIEW         VIEW
              │            │            │
        ┌─────┼─────┐      │      ┌─────┼─────┐
        ↓     ↓     ↓      ↓      ↓     ↓     ↓
   COMPONENT DECOR. ALIGNER COMPONENT DECOR. ALIGNER
        │      │      │      │      │      │
        └──────┴──────┴──────┴──────┴──────┘
                           │
                           ↓
                     UI ELEMENTS
```

The architecture is therefore not simply:

```
Pages → Components
```

nor simply:

```
Pages → Features → Components
```

It introduces a **semantic construction layer**:

```
Pages
  ↓
Views
  ↓
Purpose + Support + Primitives
```

Central idea:

> **A web interface should be constructed according to the roles that its pieces play, rather than treating every rendered unit as the same kind of "component."**

This makes:

- the Page the composition boundary
- the View the meaningful UI boundary
- the Component the purposeful functional boundary
- Decorations/Aligners the supporting boundary
- UI Elements the primitive construction boundary

---

## 21. Relationship With Feature-Based Architecture

PVC does not replace Feature-Based Architecture. They operate at different dimensions.

Feature architecture answers:

> **What domain or capability does this code belong to?**

PVC answers:

> **What role does this UI piece play in constructing its View?**

They work together:

```
Feature
└── Search
    │
    ├── Pages
    │   └── SearchPage
    │
    ├── Views
    │   └── SearchView
    │
    ├── Components
    │   └── SearchInput
    │
    └── UI
        ├── Input
        ├── Button
        └── Chip
```

Feature organization provides **ownership and domain boundaries**.  
View-based construction provides **UI composition semantics**.
