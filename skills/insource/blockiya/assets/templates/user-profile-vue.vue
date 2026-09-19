<!--
  Blockiya template — UserProfileBlock (Vue Composition API)
  Copy into features/<feature>/blockiyas/UserProfileBlock/UserProfileBlock.vue
  Zero visual concerns. Derive before pass. Fire intents and stop.
-->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Text, Box, Flex, Button, Avatar, Dropdown } from '@ui'
// import { useIntent, useDerive } from '@/shared/blockiya-core' // Strict

type User = {
  id: number
  name: string
  email: string
  role: 'admin' | 'editor' | 'viewer'
}

type DisplayUser = {
  fullName: string
  email: string
  roleBadge: string
}

const props = defineProps<{ userId: number }>()
const emit = defineEmits<{
  (e: 'save-intent', user: User): void
  (e: 'delete-intent', userId: number): void
}>()

function deriveDisplayUser(user: User): DisplayUser {
  const map = { admin: 'Admin', editor: 'Editor', viewer: 'Viewer (read only)' }
  return { fullName: user.name, email: user.email, roleBadge: map[user.role] }
}

const user = ref<User | null>(null)
const draft = ref<User | null>(null)
const isEditing = ref(false)
const isLoading = ref(true)
const isSaving = ref(false)

onMounted(async () => {
  isLoading.value = true
  // replace with queries/useUser(props.userId)
  user.value = await fetchUser(props.userId)
  isLoading.value = false
})

const displayUser = computed(() =>
  user.value ? deriveDisplayUser(user.value) : null
)

async function handleSave() {
  if (!draft.value) return
  isSaving.value = true
  const saved = await saveUser(draft.value)
  user.value = saved
  isEditing.value = false
  isSaving.value = false
  emit('save-intent', saved) // fire and stop
}

function startEdit() {
  draft.value = user.value ? { ...user.value } : null
  isEditing.value = true
}

// stubs
declare function fetchUser(id: number): Promise<User>
declare function saveUser(user: User): Promise<User>
import { computed } from 'vue'
</script>

<template>
  <Text v-if="isLoading" variant="muted">Loading...</Text>
  <Text v-else-if="!user" variant="danger">Could not load user.</Text>

  <Box v-else p="4" radius="lg" border>
    <Flex v-if="isEditing && draft" direction="column" gap="3">
      <input v-model="draft.name" />
      <input v-model="draft.email" />
      <Button :disabled="isSaving" @click="handleSave">
        {{ isSaving ? 'Saving…' : 'Save' }}
      </Button>
      <Button variant="ghost" @click="isEditing = false">Cancel</Button>
    </Flex>

    <Flex v-else direction="column" gap="3">
      <Flex align="center" gap="3">
        <Avatar :name="displayUser?.fullName" size="lg" />
        <Flex direction="column" gap="1">
          <Text variant="heading">{{ displayUser?.fullName }}</Text>
          <Text variant="muted">{{ displayUser?.email }}</Text>
        </Flex>
      </Flex>
      <Box>
        <Text variant="label">Role</Text>
        <Text>{{ displayUser?.roleBadge }}</Text>
      </Box>
      <Dropdown>
        <Dropdown.Trigger>
          <Button variant="secondary">Actions</Button>
        </Dropdown.Trigger>
        <Dropdown.Content>
          <Dropdown.Item @select="startEdit">Edit profile</Dropdown.Item>
          <Dropdown.Item variant="danger" @select="emit('delete-intent', userId)">
            Delete account
          </Dropdown.Item>
        </Dropdown.Content>
      </Dropdown>
    </Flex>
  </Box>
</template>
