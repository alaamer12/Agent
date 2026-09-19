# Canonical Example — Focused Roles (React + Vue)

Shows the same architectural roles across frameworks. Full copyable templates live in `assets/templates/`.

## Roles demonstrated

| Role | Responsibility |
|------|----------------|
| Blockiya | Owns domain state, derives, fires intents upward, zero visual concerns |
| Presentational child | Receives derived data, fires intents, owns no domain state |
| Adapter | Token + event + lifecycle translation only |
| Behavioral primitive | Interaction state stays internal (compound / headless shape) |
| Page | Owns what happens after each intent |

## React — focused skeleton

```tsx
// derive (module scope, pure)
function deriveDisplayUser(user: User): DisplayUser { /* ... */ }

// Adapter — no domain state
function UserAvatarAdapter({ name, size }) {
  return <Avatar name={name} size={size} />
}

// Presentational — derived props in, intents out
function ProfileDisplay({ user, onEditIntent, onDeleteIntent }) {
  return (
    <Flex>
      <UserAvatarAdapter name={user.fullName} size="lg" />
      <Text>{user.roleBadge}</Text>
      <Dropdown>
        <Dropdown.Trigger><Button>Actions</Button></Dropdown.Trigger>
        <Dropdown.Content>
          <Dropdown.Item onSelect={onEditIntent}>Edit</Dropdown.Item>
          <Dropdown.Item onSelect={onDeleteIntent}>Delete</Dropdown.Item>
        </Dropdown.Content>
      </Dropdown>
    </Flex>
  )
}

// Blockiya — orchestrator
function UserProfileBlock({ userId, onSaveIntent, onDeleteIntent }) {
  // domain state + data access via queries/
  // derive before pass
  const displayUser = useDerive(user, deriveDisplayUser)
  const save = useIntent(async (draft) => {
    const saved = await saveUser(draft)
    onSaveIntent(saved) // fire and stop
  })
  // render presentational children only — zero className/style
}
```

## Vue — focused skeleton

```vue
<script setup lang="ts">
const props = defineProps<{ userId: number }>()
const emit = defineEmits<{
  (e: 'save-intent', user: User): void
  (e: 'delete-intent', id: number): void
}>()

function deriveDisplayUser(user: User): DisplayUser { /* ... */ }

const user = ref<User | null>(null)
const displayUser = useDerive(user, (u) => u ? deriveDisplayUser(u) : null)

const save = useIntent(async (draft: User) => {
  const saved = await saveUser(draft)
  emit('save-intent', saved) // fire and stop
})
</script>

<template>
  <!-- presentational children only; no class/style on the Blockiya itself -->
  <ProfileDisplay
    v-if="displayUser"
    :user="displayUser"
    @edit-intent="startEdit"
    @delete-intent="emit('delete-intent', userId)"
  />
</template>
```

## Mapping

| Concept | React | Vue |
|---------|-------|-----|
| Upward intent | `onSaveIntent` callback prop | `emit('save-intent')` |
| Derive | `useDerive` / pure fn | `useDerive` + `computed` |
| Async lifecycle | `useIntent` | `useIntent` composable |
| Zero visual concerns | no className / style | no class / style on Blockiya |
| Data access | queries hooks | composables / stores |

Full runnable templates: `assets/templates/user-profile-react.tsx`, `assets/templates/user-profile-vue.vue`.
