# Blockiya Methodology (Full Reference)

Source: The Blockiya Pattern v2.1 — principles are framework-agnostic; original examples are React. See blockiya-core-polyglot.md for Vue and other frameworks.

# Blockiya Methodology (Full Reference)

Source: The Blockiya Pattern v2.1

## What is Blockiya

A Blockiya is an orchestrator. It owns domain state, talks to data sources, derives props before passing them down, and translates user actions into intents that fire upward. It never writes CSS. It never reaches into a library's internals. It never decides what happens after it fires an intent — that is always the caller's concern.

The name comes from the Arabic word for "block" — a deliberate building unit with a clear shape, clear boundaries, and a known interface. Like a physical block, it can be picked up, moved, and placed in a different context without changing its internals.

The mental model is an architect, not a craftsman. An architect does not make bricks. An architect does not build walls. An architect decides what the building looks like and assembles the right materials in the right places. Everything else is someone else's concern.

## Why Blockiya exists

Before the pattern, components were catch-alls. A single file would fetch data, manage three pieces of local state, write inline styles, import xterm.js directly, and also fire a navigation call after a save. Changing one thing broke everything. Testing was impossible without mocking the entire world.

Blockiya exists to enforce a single rule that solves all of that: **every piece of the system knows only about the layer directly below it, and fires intentions only upward.**

## The layer stack

```
Page
  └── Blockiya                        ← orchestrates domain state, talks to data, derives props
        ├── Child components           ← receive derived props, fire intents up
        ├── Behavioral Primitives      ← own interaction state internally (Dropdown, Modal)
        ├── Non-Behavioral Primitives  ← visual tokens only (Text, Box, Flex)
        ├── Adapters                   ← wrap third-party tools, translate tokens and events
        └── Utilities                  ← pattern-native structural helpers (If, useIntent, useDerive)
```

## Stereotypes

Stereotypes classify blocks by architectural role. They appear in UML diagrams and in code comments as `<<Stereotype>>`. They are not enforced by the compiler — they are a shared vocabulary that makes intent visible at a glance.

| Stereotype | Meaning | When to use | Example |
| --- | --- | --- | --- |
| `<<Page>>` | Top-level route component | Next.js / React Router pages | `BillingOverviewPage` |
| `<<Feature>>` | Large workflow orchestrator | Multi-step processes, wizards | `CheckoutWizardBlock` |
| `<<Compound>>` | Multi-component Blockiya | Combines 2–5 child blocks | `BillingOverviewBlock` |
| `<<Atomic>>` | Single-purpose Blockiya | Focused, leaf-level block | `UsageChartsBlock` |
| `<<Primitive>>` | Non-behavioral design system component | Visual tokens only, no interaction | `Button`, `VStack`, `Text` |
| `<<Behavioral>>` | Behavioral design system component | Owns interaction state internally | `Dropdown`, `Modal`, `Tooltip` |
| `<<Context>>` | Context object provider | State sharing across descendants | `ProjectContext` |
| `<<Hook/Query>>` | Data fetching hook | External data source | `useBillingUsage` |
| `<<Adapter>>` | Third-party library wrapper | Wraps external tools, translates tokens and events | `CodeEditorAdapter` |
| `<<Utility>>` | Pattern-native structural helper | Serves the pattern mechanics — no domain, no styling, no visual output | `useIntent`, `If`, `useDerive` |

**On `<<Primitive>>` vs `<<Behavioral>>`:** both live in the design system and are consumed by Blockiyas the same way. The distinction matters because they are built differently and constrained differently. A `<<Primitive>>` is a pure visual token — it has no opinion about interaction. A `<<Behavioral>>` owns interaction state internally and must use the compound component API shape.

**On `<<Utility>>`:** the test for membership is removal. If you removed every domain word from the codebase and the utility still made complete sense, it belongs here. `useIntent` does not know what operation it is wrapping. `If` does not know what it is conditionally rendering. Remove the Blockiya pattern and these utilities have no reason to exist — that is what makes them `<<Utility>>` and not just generic React helpers.

**Stereotypes are growth signals.** A block labeled `<<Atomic>>` that starts accumulating multiple children is telling you it wants to become `<<Compound>>`. Pay attention to the mismatch between the label and the reality — it is usually the first sign a refactor is needed.

## The Blockiya

A Blockiya is the only piece in the stack that:

- Fetches or mutates data (via hooks, never via direct `invoke()` or `fetch()`)
- Owns domain state (`isEditing`, `draft`, `isLoading`, `isSaving`)
- Derives props before passing them down
- Decides which children to render and when
- Fires intents upward to its caller

**Rules:**

- Zero styling. No `className`, no `style` props, no inline CSS. All visual output goes through primitives.
- Never call data APIs directly. Always through a hook from the `queries/` layer.
- 3–7 props in, 3–7 intents out. Beyond this ceiling, something needs to be extracted.
- Derive before you pass. The raw API response never reaches a child component.
- Fire intents and stop. The Blockiya does not know or care what happens after.

**The intent contract:**

When a user deletes something, the Blockiya fires `onDeleteIntent(id)` and its job ends there. It does not show a confirmation dialog. It does not navigate away. It does not refresh a sibling list. Those are all the page's decisions.

```tsx
// ✅ correct — fires intent, job done
const handleDelete = () => {
  onDeleteIntent(userId)
}

// ❌ wrong — Blockiya is making a UX decision that belongs to the caller
const handleDelete = () => {
  if (window.confirm("Are you sure?")) {
    onDeleteIntent(userId)
  }
}
```

## Strict Blockiya — v2.1 (recommended)

Strict Blockiya is the recommended way to apply the pattern. Like the Repository pattern — which has a traditional form and a more flexible form — Blockiya has its base form and Strict Blockiya as its disciplined, opinionated variant. Strict Blockiya is not enforced by the compiler; it is a team convention.

What Strict Blockiya adds on top of the base pattern:

- **`blockiya-core` utilities are required.** Every async handler goes through `useIntent`. Every data derivation goes through `useDerive` or `useDerivedState`. Structural rendering uses `If`, `Maybe`, `For`, `Repeat`, and `Compose`. Manual `useMemo`, inline ternaries for conditional rendering, and hand-rolled `isLoading`/`error` state pairs are replaced.
- **No `useState` for async lifecycle.** `useIntent` owns `isLoading` and `error` for every intent. The Blockiya body stays clean.
- **No inline derivation.** `const displayUser = { ...user, roleBadge: ... }` inline in the Blockiya body is not allowed. It moves to a named deriver function and goes through `useDerive`.
- **Structural rendering is explicit.** `{condition && <Component />}` and `{items.map(...)}` are replaced with `<If>` and `<For>`. The rendering shape is visible in JSX, not hidden in JS expressions.

The base pattern allows any of the above. Strict Blockiya removes the discretion — you apply the utilities consistently, not only when you feel like it.

## Coexisting with other React patterns

Blockiya does not prescribe how you structure the internal children of a Blockiya. It only prescribes what the Blockiya itself does — orchestrate state, derive props, fire intents.

The React ecosystem has produced many named patterns for separating concerns. They all share one underlying idea: **split the thing that knows from the thing that shows.**

| Pattern | The "knows" side | The "shows" side |
| --- | --- | --- |
| Smart / Dumb | owns data fetching and state logic | renders only, receives props, emits events |
| Container / Presentational | owns business logic, API calls, state | owns markup, no domain knowledge |
| Feature / UI | owns domain behavior and rules | owns visual primitives, no domain knowledge |
| Hook / Component | owns stateful logic, side effects, derived data | renders what the hook produces |

**Blockiya does not conflict with any of them.** It sits at the "knows" side of every one of these splits. What Blockiya adds on top is a set of additional constraints the "knows" side must follow: zero styling, derive before passing, fire intents and stop, 3–7 props ceiling. The separation itself is not new — the discipline around it is.

### Example: Smart/Dumb inside a Blockiya

```tsx
// ---- Dumb (shows) side: display mode ----
function ProfileDisplay({ user, onEditIntent }: { user: DisplayUser; onEditIntent: () => void }) {
  return (
    <Flex direction="column" gap={3}>
      <Button variant="secondary" onClick={onEditIntent}>Edit</Button>
    </Flex>
  )
}

// ---- Dumb (shows) side: edit mode ----
function ProfileEdit({
  draft, isSaving, onChange, onSaveIntent, onCancelIntent
}: {
  draft: User
  isSaving: boolean
  onChange: (field: keyof User, value: string) => void
  onSaveIntent: () => void
  onCancelIntent: () => void
}) {
  return (
    <Flex direction="column" gap={3}>
      <input value={draft.name} onChange={e => onChange("name", e.target.value)} />
      <input value={draft.email} onChange={e => onChange("email", e.target.value)} />
      <Flex direction="row" gap={2}>
        <Button variant="primary" onClick={onSaveIntent} disabled={isSaving}>
          {isSaving ? "Saving..." : "Save"}
        </Button>
        <Button variant="ghost" onClick={onCancelIntent} disabled={isSaving}>
          Cancel
        </Button>
      </Flex>
    </Flex>
  )
}

// ---- Smart (knows) side — this is the Blockiya ----
function UserProfileBlock({ userId, onSaveIntent }: { userId: number; onSaveIntent: (user: User) => void }) {
  const [user, setUser] = useState<User | null>(null)
  const [draft, setDraft] = useState<User | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    setIsLoading(true)
    fetchUser(userId).then(data => { setUser(data); setIsLoading(false) })
  }, [userId])

  const handleEdit = () => { setDraft(user); setIsEditing(true) }
  const handleChange = (field: keyof User, value: string) =>
    setDraft(prev => prev && { ...prev, [field]: value })
  const handleSave = async () => {
    if (!draft) return
    setIsSaving(true)
    const saved = await saveUser(draft)
    setUser(saved); setIsEditing(false); setIsSaving(false)
    onSaveIntent(saved) // fires upward — Blockiya's job ends here
  }
  const handleCancel = () => { setDraft(null); setIsEditing(false) }

  if (isLoading) return <Text variant="muted">Loading...</Text>
  if (!user) return <Text variant="danger">Could not load user.</Text>

  const displayUser = deriveDisplayUser(user) // derive before passing down

  return (
    <Box p={4} radius="lg" border>
      {isEditing && draft
        ? <ProfileEdit draft={draft} isSaving={isSaving} onChange={handleChange}
            onSaveIntent={handleSave} onCancelIntent={handleCancel} />
        : <ProfileDisplay user={displayUser} onEditIntent={handleEdit} />
      }
    </Box>
  )
}
```

The Dumb pieces — `ProfileDisplay` and `ProfileEdit` — are just React components. You could call them Views, Presentational components, or nothing at all. What defines them is behavior: they own no state, they receive derived props, they fire intents upward.

**Controlled Components inside children:** when a child component has form inputs, the Controlled Components pattern applies — the value lives in the Blockiya, the input reflects it, and `onChange` fires upward.

**Naming conventions:** `View`, `Dumb`, `Smart` suffixes are optional clarity aids, not requirements.

## Primitives — two kinds

Primitives are the visual layer of the system. The "zero styling" rule is only enforceable because primitives exist — they are the only available path for visual output.

### Non-behavioral primitives

`Text`, `Box`, `Flex`, `Avatar`, `Button` — pure visual tokens. They expose a prop-based token API (spacing, color, typography) and have no interaction model of their own.

### Behavioral primitives

`Dropdown`, `Modal`, `Tooltip`, `Tabs`, `Accordion` — carry interaction complexity. They manage open/closed state, keyboard navigation, focus trapping, and ARIA attributes. They are assembled from non-behavioral primitives plus behavior from a headless library (Radix UI, for example).

The key rule: behavioral primitives own their own interaction state **internally**. The Blockiya and its children never see `isOpen`. This is only possible with the right API shape.

**Compound component is the prescribed API for behavioral primitives.** Not a hook. Not a render prop. A hook-based API forces interaction state upward into the caller — the Blockiya or the child would have to manage `isOpen`. With compound components, the correct behavior is the only available behavior.

```tsx
// ✅ compound component — isOpen lives inside Dropdown
<Dropdown>
  <Dropdown.Trigger>
    <Button variant="secondary">Actions</Button>
  </Dropdown.Trigger>
  <Dropdown.Content>
    <Dropdown.Item onSelect={onEditIntent}>Edit</Dropdown.Item>
    <Dropdown.Item onSelect={onDeleteIntent}>Delete</Dropdown.Item>
  </Dropdown.Content>
</Dropdown>

// ❌ hook-based — forces isOpen into the Blockiya or child
const { isOpen, toggle, getMenuProps } = useDropdown()
<button onClick={toggle}>Actions</button>
{isOpen && <menu {...getMenuProps()}>...</menu>}
```

### Imperative primitives — the exception

Some system-level UI has no trigger and no declarative placement in the component tree. Toast notifications are the clearest example: fired programmatically from anywhere, queued and stacked independently, auto-dismissed on a timer.

These are **imperative primitives**. They do not follow the compound component API shape. Their API is a hook or a function call — `showToast(...)`, `notify(...)` — not JSX composition. They are not `<<Primitive>>` and not `<<Behavioral>>` in the compound sense. They sit between the two and must be documented explicitly as imperative.

## Adapters

Adapters exist because the real world contains third-party tools — CodeMirror, xterm.js, chart libraries — that do not speak the design system's language.

An adapter's job is exactly three things:

**Token translation** — convert the design system's tokens into whatever the third-party library understands.

**Event translation** — convert the library's internal events into the clean callback shape that Blockiyas expect. A Blockiya should never see a `CodeMirror EditorView.updateListener` event. It should only see `onChange: (value: string) => void`.

**Lifecycle management** — own the setup and teardown that the library requires. Mount it, configure it, destroy it on unmount.

```tsx
// The adapter — translation layer, not a Blockiya
function CodeEditorAdapter({ language, value, onChange, height }) {
  const theme = useTheme()
  const containerRef = useRef(null)

  useEffect(() => {
    const view = new EditorView({
      extensions: [
        basicSetup,
        mapThemeToCodeMirror(theme),              // token translation
        EditorView.updateListener.of((update) => {
          if (update.docChanged) {
            onChange(update.state.doc.toString()) // event translation
          }
        }),
      ],
      parent: containerRef.current,
    })
    return () => view.destroy()                   // lifecycle management
  }, [])

  return <Box ref={containerRef} height={height} />
}

// The Blockiya sees only this — no CodeMirror, no extensions, no disposal
<CodeEditorAdapter language={file.language} value={content} onChange={setContent} height="100%" />
```

**Adapters do not own domain state.** If the editor has a "current file" concept, that state belongs in the Feature Blockiya, not in the adapter. Adapters live in their own top-level `adapters/` folder, not nested inside features. A Blockiya imports an adapter the same way it imports a primitive.

## Styling philosophy

The rule is simple: **Blockiyas have zero styling.** No `className`, no `style` props, no inline CSS, no Tailwind utility classes. All visual output goes through primitives.

This is not an aesthetic preference. It is a structural constraint:

**Testing becomes trivial.** A Blockiya with no styling is easy to test in isolation — assert on state, on intents fired, on which child is rendered. Never on CSS class names.

**The rule is enforceable.** Because primitives are the only available path to visual output, a developer who wants to add styling has nowhere to put it except the right place.

Without a primitive layer, the zero-styling rule is aspirational. With it, the rule has teeth.

## TypeScript and the token system

When your design tokens are typed constants rather than magic strings or raw numbers, the compiler enforces the token system at every call site.

```tsx
// tokens.ts — typed design tokens
export const direction = { row: "row", column: "column" } as const
export const spacing = { gap1: 4, gap2: 8, gap3: 16, gap4: 24 } as const
export const radius = { sm: "4px", md: "8px", lg: "12px" } as const

// primitive usage — autocomplete, type safety, no magic values
<Flex direction={direction.column} gap={spacing.gap1}>
  <Box p={spacing.gap3} radius={radius.lg}>
    <Text>{user.name}</Text>
  </Box>
</Flex>
```

A Blockiya author never types `gap={16}` — they reach for `spacing.gap3`. If that token doesn't exist, TypeScript tells them before the browser does. Renaming `gap3` to `spacingMd` produces a type error everywhere it is used.

## Emotion — the recommended styling foundation

Emotion is the recommended styling engine for the primitive layer. It addresses the architecture's needs directly: a full design token system, enforced boundaries between domain and visual concerns, and adapter edge cases.

**Token system as primitives.** Emotion's `styled` API combined with `styled-system` lets you express your entire token scale as a prop-based API. `styled-system` maps prop values to token scale stops, making the primitive itself the enforcer.

```tsx
import styled from "@emotion/styled"
import { space, layout, flexbox } from "styled-system"

export const Flex = styled.div(
  { display: "flex" },
  space,    // p, m, gap — constrained to token scale
  layout,   // width, height
  flexbox,  // direction, align, justify
)
```

**`ClassNames` for adapters.** Some third-party libraries cannot be styled through props. Emotion's `<ClassNames>` component provides a render-prop API for adapter authors that still respects the theme and token system. The adapter uses `ClassNames` internally; the Blockiya never sees it.

```tsx
import { ClassNames } from "@emotion/react"

function ChartAdapter({ value, onChange }) {
  return (
    <ClassNames>
      {({ css, theme }) => (
        <ThirdPartyChart
          className={css({ backgroundColor: theme.colors.background, borderRadius: theme.radii.lg })}
          value={value}
          onChange={onChange}
        />
      )}
    </ClassNames>
  )
}
```

**`shouldForwardProp` prevents token leakage.** Filters token props from reaching the DOM — only valid HTML attributes pass through.

```tsx
import styled from "@emotion/styled"
import { shouldForwardProp } from "styled-system"

export const Box = styled("div", { shouldForwardProp })(space, layout)
```

The recommendation in one sentence: use Emotion with `styled-system` for primitives, `ThemeProvider` for the token context, `ClassNames` for adapter boundaries, and `shouldForwardProp` to keep the DOM clean.

## The React pattern toolkit

| Situation | Pattern |
| --- | --- |
| Child component has form inputs | Controlled Components — value lives in the Blockiya, input just reflects it |
| Passing data to a child component | Derived Props — process raw data first, pass only what the child needs |
| Two children need the same value | Lifting State Up — state lives in the Blockiya, both children receive it |
| Behavioral primitive needs interaction state | Compound Components — state lives inside the primitive, never in the caller |
| Edit form has many fields | Context Object + Compound Components — bundle the form contract into context |
| Props list is getting long | Prop Grouping by Domain — split into `userProps`, `uiProps`, etc. |

## State complexity decision table

| State type | Characteristics | Where it lives |
| --- | --- | --- |
| Local UI state | One component, transient (tooltip open, input focus) | `useState` inside the component |
| Form draft state | Editable copy of domain data during edit session | `useState` in the Blockiya, passed down as controlled props |
| Server state | Fetched from API, needs caching and invalidation | React Query / SWR via hook in `queries/` |
| Shared feature state | Needed by multiple Blockiyas within one feature | Context Object provided by parent Blockiya |
| Global app state | Needed across features, survives navigation | Zustand store, outside `features/` |
| URL state | Filters, pagination — should survive refresh | URL search params via router |

**The decision in practice — three questions in order:**

1. Does any other component need this? If no — `useState` locally.
2. Does it come from or sync with a server? If yes — React Query in `queries/`.
3. Do multiple Blockiyas across the app need it? If yes — global store.

Everything else is a Context Object scoped to the feature that needs it. A common mistake is reaching for a global store too early — state that feels "shared" is often only shared within one feature.

## How a Blockiya grows

### Growth signals

**Props ceiling breached (>7):** two concerns have probably merged. Identify them and extract one into a child Blockiya.

**Two different domains in one component:** profile editing and avatar management both living in `UserProfileBlock` is a signal. Extract `AvatarManagerBlock` as its own Blockiya with its own intents.

**A private child getting reused:** a child that started internal and is now imported by two Blockiyas wants to be promoted — to a primitive, a utility, or a public child Blockiya depending on whether it carries domain logic.

**The stereotype is a growth signal:** `<<Atomic>>` means single responsibility, leaf node. When it starts accumulating children, the stereotype should change. This is not a failure — it is the natural lifecycle.

### The `<<Atomic>>` → `<<Compound>>` transition

```
UserProfileBlock <<Atomic>>         UserProfileBlock <<Compound>>
  - fetches user                      - fetches user
  - owns isEditing                    - owns isEditing, draft, errors
  - renders everything inline   →     - renders ProfileDisplayView
                                      - renders ProfileEditView
                                      - renders AvatarManagerBlock (child Blockiya)
```

### When to extract a child Blockiya vs a presentational child

Extract a **presentational child** when: the child has no state, no API calls, and is only used by this Blockiya.

Extract a **child Blockiya** when: the child has its own domain state, its own data calls, or is reused across multiple parent Blockiyas.

## Battle-tested situations

**"My child component needs to confirm before firing an intent"** — it does not. Confirmation is a UX decision that belongs to the caller. The child fires the intent. The caller decides whether to show a modal first.

**"I need `isOpen` in my component for the dropdown"** — this means `Dropdown` is not using the compound component API shape. Fix the primitive, not the component using it. `isOpen` should never reach a Blockiya or any of its children.

**"My Blockiya has 10 props and I cannot split it"** — you can. The feeling that you cannot is usually because two concerns have been so tightly coupled in your mental model that they feel like one thing. Name the two concerns separately. Extract one into a child Blockiya.

**"I want to navigate after a save inside the Blockiya"** — the Blockiya fires `onSaveIntent(saved)` and stops. Navigation is the page's concern. The page receives the intent and decides: navigate, show a toast, refresh a list, do nothing.

**"A presentational child grew and now needs its own state"** — this is the `<<Atomic>>` → `<<Compound>>` signal. Give the child a `queries/` folder if needed, move the state in, rename it to `SomethingBlock`. The parent renders it the same way.

**"My adapter's third-party library has styled components that look wrong"** — the adapter owns this. Map the library's theming API to your design tokens inside the adapter. Never pass `className` or `style` props from a Blockiya into an adapter to fix visual issues.

## Project structure

The recommended structure is vertical feature slices — each feature owns its Blockiyas, queries, routes, and child components together. This is a recommended structure, not a rigid requirement.

```
src/
  shared/
    ui/
      primitives/            ← <<Primitive>> components (Box, Text, Flex, Button)
      behavioral/            ← <<Behavioral>> components (Dropdown, Modal, Tooltip)
    blockiya-core/           ← <<Utility>> — all pattern-native helpers

  entities/                  ← Domain models shared across features

  features/
    projects/
      blockiyas/
        ProjectListBlock/
          index.tsx          ← The Blockiya — pure orchestrator, zero styling
          context.ts         ← Optional Context Object for deep prop sharing
          children/          ← Presentational child components
        ProjectEditorBlock/
          index.tsx
          context.ts
          children/
      routes/
        list.page.tsx
        editor.page.tsx
      queries/
        useProjects.ts
        useProjectMutations.ts

    billing/
      blockiyas/
      routes/
      queries/

  adapters/
    code-editor/
    terminal/

  app/
    layout.tsx
    page.tsx
```

**Key rules:**

- A feature's Blockiyas live in `features/<n>/blockiyas/` — never inside another feature's folder.
- `queries/` contains only hooks. No `invoke()` or `fetch()` calls directly in Blockiyas.
- `children/` holds presentational components private to their parent Blockiya. If reused across two Blockiyas, it moves up or becomes its own Blockiya.
- `adapters/` is its own top-level folder. An adapter is not a feature concern.

## Quick reference

```
BLOCKIYA LAYERS:
  Blockiya              owns state, talks to data, derives props, fires intents
  Presentational child  receives derived props, fires intents, owns no state
  <<Primitive>>         Box, Text, Flex — visual tokens, no interaction model
  <<Behavioral>>        Dropdown, Modal — own interaction state internally
  <<Adapter>>           wraps third-party library, translates tokens + events + lifecycle
  <<Utility>>           If, For, useIntent, useDerive — serve the pattern mechanics

RULES:
  Zero styling in Blockiyas     all visual output via primitives
  Derive before you pass        raw API data never reaches a child component
  Fire intents and stop         Blockiya has no opinion on what happens next
  3-7 props / intents           beyond this, extract a child Blockiya
  Compound component            required API shape for all behavioral primitives

STRICT BLOCKIYA (v2.1 — recommended):
  useIntent                 required for every async handler
  useDerive / useDerivedState  required for all derivation
  If / Maybe / For / Repeat / Compose  required for conditional, list, and composition rendering
  No inline isLoading/error state pairs
  No inline useMemo derivation

GROWTH SIGNALS:
  Props > 7                 split the Blockiya
  Two domains merged        extract a child Blockiya
  Atomic accumulating       promote to Compound
  Private child reused      promote to public Blockiya or utility

REACT PATTERN MAP:
  Form inputs in child       Controlled Components
  Passing data down          useDerive first
  Shared value, two children Lifting State Up
  Behavioral primitive       Compound Components
  Long form, many fields     Context Object + Compound Components
  Long props list            Prop Grouping by Domain
```

## Version history

**v2.1.0** (2026-03-25)
- Added: Strict Blockiya section — recommended disciplined variant
- Added: `<<Utility>>` stereotype
- Added: `blockiya-core/`
- Updated: Layer stack, Stereotypes table, Project structure

**v2.0.0** (2026-03-25)
- Added: TypeScript and the token system
- Added: Emotion as recommended styling foundation
- Added: React pattern toolkit
- Added: `<<Adapter>>` stereotype
- Added: Styling philosophy, Why primitives are essential
- Added: Project structure, State complexity decision table
- Added: Stereotypes section with growth signal guidance

**v1.0.0** (2026-01-25)
- Initial release
- Core rules: zero styling, 3–7 props ceiling, lift state up, intents upward
- Stereotypes: Page, Feature, Compound, Atomic, Primitive, Context, Hook/Query
