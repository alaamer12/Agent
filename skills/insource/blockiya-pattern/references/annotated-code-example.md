# Annotated Reference Code Example (`UserProfileBlock`)

Complete annotated React/TypeScript reference implementation demonstrating every architectural layer and numbered React pattern annotation in one cohesive file.

**Framework note:** the roles shown here — Blockiya, presentational ("Dumb") views, Adapter, Page — and the intent contract are framework-agnostic. This React/TypeScript syntax is the canonical expression, not a requirement; see "Blockiya beyond React" in [methodology-and-rules.md](methodology-and-rules.md) for the mapping onto Vue composables, Svelte, Solid, or MAUI/Blazor C#.

## Table of Contents

- [Pattern & Clarity Suffix Index](#pattern--clarity-suffix-index)
- [Part 1: Types, Dummy API, Derived Props Selector & Edit Context](#part-1-types-dummy-api-derived-props-selector--edit-context)
- [Part 2: Primitives, Adapter (`UserAvatarAdapter`) & Dumb Views (`ProfileDisplayDumb`, `ProfileEditFormDumb`)](#part-2-primitives-adapter-useravataradapter--dumb-views-profiledisplaydumb-profileeditformdumb)
- [Part 3: Smart Blockiya (`UserProfileBlockSmart`) & Page (`App`)](#part-3-smart-blockiya-userprofileblocksmart--page-app)

---

## Pattern & Clarity Suffix Index

- **Clarity suffixes (`Smart`, `Dumb`, `Primitive`, `Adapter`)**: Included for teaching clarity only; in production code name components `UserProfileBlock`, `ProfileDisplayView`, `ProfileEditView`, and import primitives directly from `@ui`.
- **Annotated React Patterns preserved inline**:
  - **Pattern #1 — Context Object**: `EditContext` bundles the edit form contract (`draft`, `isSaving`, `onChange`, `onSaveIntent`, `onCancelIntent`) into a single object instead of drilling 5 separate props.
  - **Pattern #2 — Lifting State Up**: `draft` lives in `UserProfileBlockSmart`; sub-fields stay stateless and controlled.
  - **Pattern #3 — Controlled Components**: `ProfileEditFormDumb.NameField` and `EmailField` reflect `draft` from `UserProfileBlockSmart` and emit `onChange`.
  - **Pattern #8 — Compound Components**: Used both for behavioral primitive `<Dropdown>` (`Dropdown.Trigger`, `Dropdown.Content`, `Dropdown.Item` owning `isOpen` internally) and `<ProfileEditFormDumb>` (`NameField`, `EmailField`, `Actions`).
  - **Pattern #11 — Derived Props**: `deriveDisplayUser(user)` transforms raw `User` into `DisplayUser` (`fullName`, `email`, `roleBadge`) so Dumb views never see the raw enum or API shape.

---

### Part 1: Types, Dummy API, Derived Props Selector & Edit Context

```tsx
import { useState, useEffect, createContext, useContext } from "react"
import { Text, Box, Flex, Button, Avatar, Dropdown } from "@ui" // Tokens system, supposing they exist

// NOTE ON SUFFIXES
// The suffixes below (Smart, Dumb, Primitive, Adapter) are for clarity only.
// They do not need to exist in a real codebase — you would just call it
// UserProfileBlock, ProfileDisplayView, etc. The suffixes are here to make
// the role of each piece immediately visible while reading this file.

// ---- types ----

type User = {
  id: number
  name: string
  email: string
  role: "admin" | "editor" | "viewer"
}

// derived type — dumb views never receive raw User directly.
// Pattern: Derived Props (#11)
type DisplayUser = {
  fullName: string
  email: string
  roleBadge: string
}

// ---- dummy API ----

const fetchUser = (id: number): Promise<User> =>
  new Promise((res) =>
    setTimeout(
      () =>
        res({
          id,
          name: "Ahmed Hassan",
          email: "ahmed@symphony.dev",
          role: "admin",
        }),
      800
    )
  )

const saveUser = (user: User): Promise<User> =>
  new Promise((res) => setTimeout(() => res(user), 600))

// ---- derived props selector ----
// Pattern: Derived Props (#11)
// Smart Blockiya calls this before passing data to any Dumb view.
function deriveDisplayUser(user: User): DisplayUser {
  const roleBadgeMap = {
    admin: "Admin",
    editor: "Editor",
    viewer: "Viewer (read only)",
  }
  return {
    fullName: user.name,
    email: user.email,
    roleBadge: roleBadgeMap[user.role],
  }
}

// ---- context for edit form ----
// Pattern: Context Object (#1) + Compound Components (#8)
type EditContextValue = {
  draft: User
  isSaving: boolean
  onChange: (field: keyof User, value: string) => void
  onSaveIntent: () => void
  onCancelIntent: () => void
}

const EditContext = createContext<EditContextValue | null>(null)
```

### Part 2: Primitives, Adapter (`UserAvatarAdapter`) & Dumb Views (`ProfileDisplayDumb`, `ProfileEditFormDumb`)

```tsx
function useEditContext() {
  const ctx = useContext(EditContext)
  if (!ctx) throw new Error("useEditContext must be used inside ProfileEditFormDumb")
  return ctx
}

// =============================================================================
// PRIMITIVES (suffix: Primitive)
// Non-behavioral: Text, Box, Flex, Avatar, Button — imported from @ui.
// Behavioral: Dropdown — imported from @ui, compound component shape.
// Suffix exists for clarity only. In real code these are just @ui imports.
// =============================================================================

// Text          → TextPrimitive (non-behavioral)
// Box           → BoxPrimitive  (non-behavioral)
// Flex          → FlexPrimitive (non-behavioral)
// Avatar        → AvatarPrimitive (non-behavioral)
// Button        → ButtonPrimitive (non-behavioral)
// Dropdown      → DropdownPrimitive (behavioral — owns isOpen internally)
//
// In real code you just import and use them. The suffix is conceptual.

// =============================================================================
// ADAPTER (suffix: Adapter)
// Wraps a third-party library. Translates tokens, events, and lifecycle.
// The Smart Blockiya never sees the library directly.
// Suffix exists for clarity only.
// =============================================================================

// Suppose avatar images come from a third-party library (e.g. boring-avatars).
// The adapter owns token translation (size → px) and event translation
// (onError → silent fallback to initials). The Blockiya never sees the library.
//
// [clarity suffix: Adapter]
function UserAvatarAdapter({ name, size }: { name: string; size: "sm" | "lg" }) {
  // In a real adapter: import BoringAvatar from "boring-avatars"
  // translate Symphony size token → px, translate onError → fallback silently.
  // Here we just render the @ui Avatar as a stand-in.
  // The Smart Blockiya only ever sees <UserAvatarAdapter name={...} size={...} />
  // — it has no idea what library renders the actual image.
  return <Avatar name={name} size={size} />
}

// =============================================================================
// DUMB VIEWS (suffix: Dumb)
// No state. No API calls. No decisions.
// Receive derived props, fire intents upward. Fully controlled by Smart Blockiya.
// Suffix exists for clarity only — in real code these would just be named
// ProfileDisplayView and ProfileEditView.
// =============================================================================

type ProfileDisplayDumbProps = {
  user: DisplayUser       // derived, not raw User
  onEditIntent: () => void
  onDeleteIntent: () => void
}

// [clarity suffix: Dumb]
function ProfileDisplayDumb({
  user,
  onEditIntent,
  onDeleteIntent,
}: ProfileDisplayDumbProps) {
  return (
    <Flex direction="column" gap={3}>
      <Flex align="center" gap={3}>
        {/* uses Adapter — has no idea what library renders the avatar */}
        <UserAvatarAdapter name={user.fullName} size="lg" />
        <Flex direction="column" gap={1}>
          <Text variant="heading">{user.fullName}</Text>
          <Text variant="muted">{user.email}</Text>
        </Flex>
      </Flex>

      <Box>
        <Text variant="label">Role</Text>
        {/* roleBadge is derived — this view has no idea the raw enum exists */}
        <Text>{user.roleBadge}</Text>
      </Box>

      {/*
        Dropdown is a behavioral Primitive (compound component shape).
        isOpen lives inside Dropdown — this Dumb view never sees it.
        The Smart Blockiya never sees it either.
        Pattern: Compound Components (#8)
      */}
      <Dropdown>
        <Dropdown.Trigger>
          <Button variant="secondary">Actions</Button>
        </Dropdown.Trigger>
        <Dropdown.Content>
          <Dropdown.Item onSelect={onEditIntent}>Edit profile</Dropdown.Item>
          <Dropdown.Item onSelect={onDeleteIntent} variant="danger">
            Delete account
          </Dropdown.Item>
        </Dropdown.Content>
      </Dropdown>
    </Flex>
  )
}

// ProfileEditFormDumb — compound component shell.
// Provides EditContext to sub-fields instead of prop-drilling.
// Pattern: Compound Components (#8) + Context Object (#1)
//
// [clarity suffix: Dumb]
function ProfileEditFormDumb({
  value,
  children,
}: {
  value: EditContextValue
  children: React.ReactNode
}) {
  return (
    <EditContext.Provider value={value}>
      <Flex direction="column" gap={3}>
        {children}
      </Flex>
    </EditContext.Provider>
  )
}

// Sub-fields are also Dumb — each reads only what it needs from context.
// Pattern: Controlled Components (#3) — value lives in Smart Blockiya, field reflects it.
ProfileEditFormDumb.NameField = function NameField() {
  const { draft, onChange } = useEditContext()
  return (
    <Flex direction="column" gap={1}>
      <Text variant="label">Name</Text>
      <input
        value={draft.name}
        onChange={(e) => onChange("name", e.target.value)}
      />
    </Flex>
  )
}

ProfileEditFormDumb.EmailField = function EmailField() {
  const { draft, onChange } = useEditContext()
  return (
    <Flex direction="column" gap={1}>
      <Text variant="label">Email</Text>
      <input
        value={draft.email}
        onChange={(e) => onChange("email", e.target.value)}
      />
    </Flex>
  )
}

ProfileEditFormDumb.Actions = function Actions() {
  const { isSaving, onSaveIntent, onCancelIntent } = useEditContext()
  return (
    <Flex direction="row" gap={2}>
      <Button variant="primary" onClick={onSaveIntent} disabled={isSaving}>
        {isSaving ? "Saving..." : "Save"}
      </Button>
      <Button variant="ghost" onClick={onCancelIntent} disabled={isSaving}>
        Cancel
      </Button>
    </Flex>
  )
}
```

### Part 3: Smart Blockiya (`UserProfileBlockSmart`) & Page (`App`)

```tsx
// =============================================================================
// SMART BLOCKIYA (suffix: Smart)
// Owns all state. Talks to API. Derives props before passing down.
// Decides which Dumb view to render. Fires intents upward only.
// Zero styling — all visual output via Primitives and Adapters.
// Suffix exists for clarity only — in real code this is just UserProfileBlock.
// =============================================================================

type UserProfileBlockSmartProps = {
  userId: number
  onSaveIntent: (user: User) => void
  onDeleteIntent: (userId: number) => void
}

// [clarity suffix: Smart]
function UserProfileBlockSmart({
  userId,
  onSaveIntent,
  onDeleteIntent,
}: UserProfileBlockSmartProps) {
  const [user, setUser] = useState<User | null>(null)
  const [draft, setDraft] = useState<User | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    setIsLoading(true)
    fetchUser(userId).then((data) => {
      setUser(data)
      setIsLoading(false)
    })
  }, [userId])

  const handleEdit = () => {
    setDraft(user)
    setIsEditing(true)
  }

  const handleChange = (field: keyof User, value: string) => {
    setDraft((prev) => prev && { ...prev, [field]: value })
  }

  const handleSave = async () => {
    if (!draft) return
    setIsSaving(true)
    const saved = await saveUser(draft)
    setUser(saved)
    setIsEditing(false)
    setIsSaving(false)
    onSaveIntent(saved) // fires upward — Smart Blockiya's job ends here
  }

  const handleCancel = () => {
    setDraft(null)
    setIsEditing(false)
  }

  if (isLoading) return <Text variant="muted">Loading...</Text>
  if (!user) return <Text variant="danger">Could not load user.</Text>

  // derive before passing down — Dumb views never touch raw User
  // Pattern: Derived Props (#11)
  const displayUser = deriveDisplayUser(user)

  return (
    <Box p={4} radius="lg" border>
      {isEditing && draft ? (
        // Pattern: Lifting State Up (#2) — draft lives here, Dumb fields are fully controlled
        // Pattern: Context Object (#1) — form contract as one object, not 5 separate props
        <ProfileEditFormDumb
          value={{ draft, isSaving, onChange: handleChange, onSaveIntent: handleSave, onCancelIntent: handleCancel }}
        >
          <ProfileEditFormDumb.NameField />
          <ProfileEditFormDumb.EmailField />
          <ProfileEditFormDumb.Actions />
        </ProfileEditFormDumb>
      ) : (
        <ProfileDisplayDumb
          user={displayUser}
          onEditIntent={handleEdit}
          onDeleteIntent={() => onDeleteIntent(userId)}
          // onDeleteIntent fires upward — Smart Blockiya doesn't confirm, doesn't navigate.
          // The page decides what happens next.
        />
      )}
    </Box>
  )
}

// =============================================================================
// PAGE
// Mounts the Smart Blockiya. Owns what happens after each intent.
// =============================================================================

export default function App() {
  return (
    <Flex direction="column" align="center" p={8}>
      <UserProfileBlockSmart
        userId={1}
        onSaveIntent={(user) => console.log("saved:", user)}
        onDeleteIntent={(id) => console.log("delete intent:", id)}
        // page decides: navigate away? show confirmation modal? refresh a list?
        // the Smart Blockiya has no opinion.
      />
    </Flex>
  )
}
```
