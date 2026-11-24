# Blockiya — React + TypeScript (Canonical Reference)

The baseline every other port is measured against. Uses Strict Blockiya v2.1: `blockiya-core` utilities for intent lifecycle, draft derivation, and structural rendering. Layers top-down: primitives → behavioral → adapter → views → Blockiya → Page.

## 1. Primitives and tokens (shared/ui)

Primitives are the only path to visual output — the zero-styling rule is enforceable precisely because nothing else renders pixels for a Blockiya.

```tsx
// shared/ui/tokens.ts
export const spacing = { xs: 4, sm: 8, md: 16, lg: 24 } as const
export const radius  = { sm: 4, md: 8, lg: 12 } as const

// shared/ui/primitives.tsx  (Emotion + styled-system per methodology recommendation)
import styled from "@emotion/styled"
import { space, layout, flexbox } from "styled-system"

export const Box   = styled("div", { shouldForwardProp })(space, layout)
export const Flex  = styled("div", { shouldForwardProp })({ display: "flex" }, space, flexbox)
export const Text  = styled("span", { shouldForwardProp })(space)
export const Button = styled("button", { shouldForwardProp })(space)
```

## 2. Behavioral primitive — Dropdown owns `isOpen`

Compound API, never a hook: a `useDropdown()` shape would leak `isOpen` into the consumer. (Internal implementation via Radix or hand-rolled — either way the state is invisible from outside.)

```tsx
// shared/ui/behavioral/Dropdown.tsx — public surface only
export const Dropdown = Object.assign(DropdownRoot, {
  Trigger: DropdownTrigger,   // renders children, wires aria
  Content: DropdownContent,   // focus trap + keyboard nav live here
  Item: DropdownItem,         // onSelect fires, then closes internally
})
```

## 3. Adapter — boring-avatars behind one clean prop surface

```tsx
// adapters/user-avatar/UserAvatarAdapter.tsx
import BoringAvatar from "boring-avatars"
import { Avatar, Text } from "@ui"

const SIZE_PX = { sm: 32, lg: 96 } as const   // token translation

export function UserAvatarAdapter({ name, size }: { name: string; size: "sm" | "lg" }) {
  // event translation + lifecycle are the library's problem, not the Blockiya's
  return <BoringAvatar name={name} size={SIZE_PX[size]} variant="beam" />
}
```

## 4. Types, data layer, deriver

```tsx
// entities/user.ts
export type User = { id: number; name: string; email: string; role: "admin" | "editor" | "viewer" }
export type DisplayUser = { fullName: string; email: string; roleBadge: string }

// features/users/queries/useUser.ts  — data only ever reaches the Blockiya via hooks
export function useUser(id: number) { /* React Query: queryKey ["user", id] */ }
export function useSaveUser()      { /* mutation hook, invalidates ["user"] */ }

// features/users/blockiyas/UserProfileBlock/derivers.ts — module scope, stable ref
export function deriveDisplayUser(user: User): DisplayUser {
  const badge = { admin: "Admin", editor: "Editor", viewer: "Viewer (read only)" }
  return { fullName: user.name, email: user.email, roleBadge: badge[user.role] }
}
```

## 5. Presentational children (Dumb views)

No state, no data calls, derived props in, intents out.

```tsx
// children/ProfileDisplayView.tsx
import { If, For } from "@/shared/blockiya-core"
import { Box, Flex, Text, Button, Dropdown } from "@ui"
import { UserAvatarAdapter } from "@/adapters/user-avatar/UserAvatarAdapter"
import type { DisplayUser } from "../../entities/user"

type Props = {
  user: DisplayUser
  actions: Array<{ id: string; label: string; danger?: boolean }>
  onEditIntent: () => void
  onDeleteIntent: () => void
}

export function ProfileDisplayView({ user, actions, onEditIntent, onDeleteIntent }: Props) {
  const onSelect = (id: string) => id === "delete" ? onDeleteIntent() : onEditIntent()
  return (
    <Flex direction="column" gap="md">
      <Flex align="center" gap="md">
        <UserAvatarAdapter name={user.fullName} size="lg" />
        <Flex direction="column" gap="xs">
          <Text as="h2">{user.fullName}</Text>
          <If condition={user.email}><Text tone="muted">{user.email}</Text></If>
        </Flex>
      </Flex>
      <Box><Text tone="label">Role</Text><Text>{user.roleBadge}</Text></Box>
      <Dropdown>
        <Dropdown.Trigger><Button>Actions</Button></Dropdown.Trigger>
        <Dropdown.Content>
          <For each={actions} keyExtractor={(a) => a.id}>
            {(a) => <Dropdown.Item onSelect={() => onSelect(a.id)}>{a.label}</Dropdown.Item>}
          </For>
        </Dropdown.Content>
      </Dropdown>
    </Flex>
  )
}
```

```tsx
// children/ProfileEditFormView.tsx — Context Object (#1) + Compound (#8) + Controlled (#3)
import { createContext, useContext } from "react"
import { Box, Flex, Text, Button } from "@ui"
import type { User } from "../../entities/user"

type EditContract = {
  draft: User
  isSaving: boolean
  onDraftChange: (field: keyof User, value: string) => void
  onSaveIntent: () => void
  onCancelIntent: () => void
}
const EditCtx = createContext<EditContract | null>(null)
const useEdit = () => {
  const ctx = useContext(EditCtx)
  if (!ctx) throw new Error("ProfileEditFormView fields must render inside the form")
  return ctx
}

export function ProfileEditFormView({ value, children }: EditContract & { children: React.ReactNode }) {
  return <EditCtx.Provider value={value}><Flex direction="column" gap="md">{children}</Flex></EditCtx.Provider>
}
ProfileEditFormView.NameField  = () => <Field label="Name"  field="name"  />
ProfileEditFormView.EmailField = () => <Field label="Email" field="email" />
ProfileEditFormView.Actions = () => {
  const { isSaving, onSaveIntent, onCancelIntent } = useEdit()
  return (
    <Flex gap="sm">
      <Button onClick={onSaveIntent} disabled={isSaving}>{isSaving ? "Saving…" : "Save"}</Button>
      <Button onClick={onCancelIntent} disabled={isSaving}>Cancel</Button>
    </Flex>
  )
}
function Field({ label, field }: { label: string; field: "name" | "email" }) {
  const { draft, onDraftChange } = useEdit()
  return (
    <Box>
      <Text tone="label">{label}</Text>
      <input value={draft[field]} onChange={(e) => onDraftChange(field, e.target.value)} />
    </Box>
  )
}
```

## 6. The Blockiya (Strict v2.1)

```tsx
// blockiyas/UserProfileBlock/index.tsx
import { If, useIntent, useDerivedState, useToggle } from "@/shared/blockiya-core"
import { useUser, useSaveUser } from "../../queries/useUser"
import { deriveDisplayUser } from "./derivers"
import { ProfileDisplayView } from "./children/ProfileDisplayView"
import { ProfileEditFormView } from "./children/ProfileEditFormView"
import type { User } from "../../entities/user"

type Props = {
  userId: number
  onSaveIntent: (user: User) => void
  onDeleteIntent: (userId: number) => void
}

export function UserProfileBlock({ userId, onSaveIntent, onDeleteIntent }: Props) {
  const { data: user, isPending, isError } = useUser(userId)
  const save = useSaveUser()

  // isEditing owned by useToggle; draft owned by useDerivedState:
  // resets automatically when the server user reference changes.
  const [isEditing, , startEditing, stopEditing] = useToggle(false)
  const [draft, setDraft] = useDerivedState(user ?? null, (u) => u ? { ...u } : null)

  // useIntent owns loading/error; the Blockiya body has no hand-rolled lifecycle.
  const saveIntent = useIntent(async () => {
    if (!draft) return
    const saved = await save.mutateAsync(draft)
    stopEditing()
    onSaveIntent(saved) // fires upward — job ends here
  })

  const onDraftChange = (field: keyof User, value: string) =>
    setDraft((prev) => prev && { ...prev, [field]: value })

  return (
    <If condition={isPending}  fallback={<Text tone="muted">Loading…</Text>}>
      <If condition={isError}   fallback={<Text tone="danger">Could not load user.</Text>}>
        <If condition={isEditing && draft} fallback={
          <If condition={user}>
            {(u) => <ProfileDisplayView
              user={deriveDisplayUser(u)}
              actions={[{ id: "edit", label: "Edit profile" }, { id: "delete", label: "Delete account", danger: true }]}
              onEditIntent={startEditing}
              onDeleteIntent={() => onDeleteIntent(userId)}
            />}
          </If>
        }>
          <ProfileEditFormView
            value={{ draft: draft!, isSaving: saveIntent.isLoading, onDraftChange,
                     onSaveIntent: () => saveIntent.fire(), onCancelIntent: stopEditing }}
          >
            <ProfileEditFormView.NameField />
            <ProfileEditFormView.EmailField />
            <ProfileEditFormView.Actions />
          </ProfileEditFormView>
        </If>
      </If>
    </If>
  )
}
```

## 7. Page — where post-intent decisions live

```tsx
// routes/user.page.tsx
export default function UserPage() {
  const { userId } = useParams()
  const [pendingDelete, setPendingDelete] = useState<number | null>(null)

  return (
    <>
      <UserProfileBlock
        userId={Number(userId)}
        onSaveIntent={() => toast.push({ message: "Profile saved" })}
        onDeleteIntent={(id) => setPendingDelete(id)} {/* page decides: confirm first */}
      />
      {/* Confirm modal is the page's call — the Blockiya only fired the intent */}
      <ConfirmDialog open={pendingDelete != null} onConfirm={() => { void api.deleteUser(pendingDelete); navigate("/users") }} />
    </>
  )
}
```

## What a port must preserve

Every rule above is framework-independent: hook-ownership of async lifecycle, module-scope deriver, compound encapsulation, intent-and-stop. The Vue port swaps hooks for composables and context for `provide/inject`; the MAUI port swaps components for `ContentView` + ViewModel and callbacks for events — **identically-shaped contracts**, different syntax.
