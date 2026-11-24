# Blockiya — Vue 3 + TypeScript (Composables)

The same `UserProfileBlock` scenario, ported file-for-file from [react.md](react.md). This port shows why Vue is the closest natural fit: Vue already encourages **modular files** — one concern per `.vue`/`.ts` file, composables for stateful logic — which maps one-to-one onto the Blockiya folder shape. Only the mechanism changes: hooks become composables, Context becomes `provide/inject`, callback props become `emits`, and JSX becomes the template.

## 1. Primitives and tokens

Zero-styling rule identical: styles live **inside** the primitives (scoped `<style>` there is fine — it's the Blockiya that must stay clean).

```vue
<!-- shared/ui/Flex.vue -->
<script setup lang="ts">
const props = defineProps<{ gap?: "xs" | "sm" | "md" | "lg"; align?: string; dir?: "row" | "col" }>()
</script>
<template>
  <div class="flex" :data-gap="props.gap" :data-align="props.align" :data-dir="props.dir">
    <slot />
  </div>
</template>
<style scoped>
/* token scale resolved from CSS custom properties — the token system, enforced here */
.flex { display: flex; flex-direction: var(--dir, row); }
.flex[data-gap="md"] { gap: var(--space-md); }
/* …one rule per token stop, nothing else */
</style>
```

## 2. Behavioral — Dropdown owns `isOpen` internally

```vue
<!-- shared/ui/behavioral/Dropdown.vue (root) -->
<script setup lang="ts">
import { provide, ref } from "vue"
import { DROPDOWN_KEY } from "./dropdownKeys"     // plain .ts: export const DROPDOWN_KEY = Symbol("dropdown")
const isOpen = ref(false)                          // ← the state never leaves this component
provide(DROPDOWN_KEY, {                         // compound children inject from here
  isOpen,
  close: () => (isOpen.value = false),
  registerItem: (onSelect: () => void) => onSelect,
})
</script>
<template>
  <div class="dropdown" v-on-click-outside="() => (isOpen.value = false)">
    <slot name="trigger" />
    <slot v-if="isOpen" />                      <!-- Dropdown.Content -->
  </div>
</template>
```

```vue
<!-- shared/ui/behavioral/DropdownItem.vue -->
<script setup lang="ts">
const { close } = inject(DROPDOWN_KEY)!         // still zero isOpen outside the primitive
defineProps<{ onSelect: () => void }>()
</script>
<template><button class="item" @click="() => { onSelect(); close() }"><slot /></button></template>
```

## 3. Adapter

```ts
// adapters/user-avatar/useAvatarProps.ts — token + lifecycle translation only
const SIZE_PX = { sm: 32, lg: 96 } as const
export function useAvatarProps(name: Ref<string>, size: Ref<"sm" | "lg">) {
  return { name, sizePx: computed(() => SIZE_PX[size.value]), variant: "beam" }
}
```

```vue
<!-- adapters/user-avatar/UserAvatarAdapter.vue -->
<script setup lang="ts">
import BoringAvatar from "boring-avatar-vue"    // third party known ONLY here
const props = defineProps<{ name: string; size: "sm" | "lg" }>()
const avatar = useAvatarProps(toRef(props, "name"), toRef(props, "size"))
</script>
<template><BoringAvatar :name="avatar.name" :size="avatar.sizePx" :variant="avatar.variant" /></template>
```

## 4. Data layer and deriver — Vue's modular files ARE the Blockiya shape

```ts
// features/users/composables/useUser.ts     ← queries/ equivalent
export function useUser(id: Ref<number>) {
  const data = ref<User | null>(null), isPending = ref(true), isError = ref(false)
  watch(id, async (uid) => { /* fetch/refresh, set refs */ }, { immediate: true })
  return { data, isPending, isError }
}

// features/users/blockiyas/UserProfileBlock/derivers.ts  — module scope, like React
export function deriveDisplayUser(user: User): DisplayUser {
  const badge = { admin: "Admin", editor: "Editor", viewer: "Viewer (read only)" } as const
  return { fullName: user.name, email: user.email, roleBadge: badge[user.role] }
}
```

Strict-blockiya-core, Vue edition — same contracts, composable syntax:

```ts
// shared/blockiya-core/intents/useIntent.ts  (port of the React hook, same semantics)
export function useIntent<A extends unknown[]>(handler: (...args: A) => Promise<void>) {
  const isLoading = ref(false), error = ref<Error | null>(null)
  async function fire(...args: A) {
    isLoading.value = true; error.value = null
    try { await handler(...args) } catch (e) { error.value = e instanceof Error ? e : new Error(String(e)) }
    finally { isLoading.value = false }
  }
  return { fire, isLoading, error, reset: () => { isLoading.value = false; error.value = null } }
}

// shared/blockiya-core/derivation/useDerivedState.ts — source-change reset, via watch
export function useDerivedState<S, T>(source: Ref<S>, transform: (s: S) => T) {
  const state = ref(transform(source.value)) as Ref<T>
  watch(source, (s) => { state.value = transform(s) })   // ← auto-reset of the draft
  return [state, (v: T) => (state.value = v)] as const
}
```

## 5. Presentational children

```ts
// children/editContext.ts — the Vue form of the Context Object: one typed InjectionKey
export type EditContract = {
  draft: User
  isSaving: boolean
  onDraftChange: (field: keyof User, value: string) => void
  onSaveIntent: () => void
  onCancelIntent: () => void
}
export const EDIT_KEY: InjectionKey<EditContract> = Symbol("profile-edit")
```

```vue
<!-- children/ProfileEditFormView.vue — Context Object (#1) via provide -->
<script setup lang="ts">
import { provide } from "vue"
import { EDIT_KEY, type EditContract } from "./editContext"
const props = defineProps<{ contract: EditContract }>()
provide(EDIT_KEY, props.contract)
</script>
<template>
  <Flex dir="col" gap="md"><slot /></Flex>
</template>
```

```vue
<!-- children/NameField.vue — sibling file (Vue's one-concern-per-file idiom), Controlled (#3) -->
<script setup lang="ts">
import { inject } from "vue"
import { EDIT_KEY } from "./editContext"
const { draft, onDraftChange } = inject(EDIT_KEY)!   // typed by EDIT_KEY's InjectionKey
</script>
<template>
  <Box><Text tone="label">Name</Text>
    <input :value="draft.name" @input="onDraftChange('name', ($event.target as HTMLInputElement).value)" />
  </Box>
</template>
```

```vue
<!-- children/ProfileDisplayView.vue -->
<script setup lang="ts">
defineProps<{ user: DisplayUser }>()
defineEmits<{ editIntent: []; deleteIntent: [] }>()   // intents out, ▼/▲ preserved
</script>
<template>
  <Flex dir="col" gap="md">
    <Flex align="center" gap="md">
      <UserAvatarAdapter :name="user.fullName" size="lg" />
      <Flex dir="col" gap="xs">
        <Text as="h2">{{ user.fullName }}</Text>
        <Text v-if="user.email" tone="muted">{{ user.email }}</Text>   <!-- If → v-if -->
      </Flex>
    </Flex>
    <Dropdown>
      <template #trigger><Button>Actions</Button></template>
      <DropdownItem :onSelect="() => emit('editIntent')">Edit profile</DropdownItem>
      <DropdownItem :onSelect="() => emit('deleteIntent')">Delete account</DropdownItem>
    </Dropdown>
  </Flex>
</template>
```

## 6. The Blockiya

```vue
<!-- features/users/blockiyas/UserProfileBlock/index.vue -->
<script setup lang="ts">
import { useUser } from "../../composables/useUser"
import { useIntent, useDerivedState } from "@/shared/blockiya-core"
import { deriveDisplayUser } from "./derivers"

const props = defineProps<{ userId: number }>()
const emit = defineEmits<{ saveIntent: [user: User]; deleteIntent: [id: number] }>()

const userId = toRef(props, "userId")
const { data: user, isPending, isError } = useUser(userId)

const isEditing = ref(false)
const [draft, setDraft] = useDerivedState(user, (u) => (u ? { ...u } : null))

const saveIntent = useIntent(async () => {
  if (!draft.value) return
  const saved = await api.saveUser(draft.value)
  isEditing.value = false
  emit("saveIntent", saved)        // fires upward — stops here, same as React
})

const onDraftChange = (field: keyof User, value: string) =>
  setDraft(draft.value && { ...draft.value, [field]: value })
</script>

<template>
  <Text v-if="isPending" tone="muted">Loading…</Text>
  <Text v-else-if="isError" tone="danger">Could not load user.</Text>
  <template v-else-if="user">
    <ProfileEditFormView v-if="isEditing && draft"
      :contract="{ draft, isSaving: saveIntent.isLoading, onDraftChange,
                   onSaveIntent: saveIntent.fire, onCancelIntent: () => (isEditing = false) }">
      <NameField /><EmailField /><FormActions />
    </ProfileEditFormView>
    <ProfileDisplayView v-else :user="deriveDisplayUser(user)"
      @edit-intent="isEditing = true" @delete-intent="emit('deleteIntent', props.userId)" />
  </template>
</template>
```

## 7. Page

```vue
<!-- routes/user.page.vue — post-intent decisions belong here -->
<script setup lang="ts">
const pendingDelete = ref<number | null>(null)
</script>
<template>
  <UserProfileBlock :user-id="Number(route.params.id)"
    @save-intent="toast.push('Profile saved')"
    @delete-intent="pendingDelete = $event" />
  <ConfirmDialog :open="pendingDelete != null"
    @confirm="api.deleteUser(pendingDelete); router.push('/users')" />
</template>
```

## Port notes

- `ref`/`computed`/`watch` are reactive primitives — the `useDerivedState` auto-reset is a `watch`, not a memo cache: **same contract, cleaner mechanism** in Vue.
- The user's point stands: Vue's modular-file culture means a Blockiya folder (`index.vue`, `derivers.ts`, `children/*.vue`, `composables/*.ts`) is *already idiomatic Vue* — the pattern adds rules, not structure.
- `v-if` in a **template** is the framework's own structural rendering — Strict Blockiya's `<If>` exists to tame JSX expressions; templates already keep shape visible, so `v-if`/`v-for` satisfy the rule.
- Emits are typed contracts: 3–7 emits out, 3–7 props in — same ceiling, `defineEmits` instead of callback props.
