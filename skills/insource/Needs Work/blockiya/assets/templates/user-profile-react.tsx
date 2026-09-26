/**
 * Blockiya template — UserProfileBlock (React)
 * Copy into features/<feature>/blockiyas/UserProfileBlock/index.tsx
 * Zero visual concerns. Derive before pass. Fire intents and stop.
 */
import { useState, useEffect } from 'react'
import { Text, Box, Flex, Button, Avatar, Dropdown } from '@ui'
// import { useIntent, useDerive, If } from '@/shared/blockiya-core' // Strict

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

function deriveDisplayUser(user: User): DisplayUser {
  const map = { admin: 'Admin', editor: 'Editor', viewer: 'Viewer (read only)' }
  return { fullName: user.name, email: user.email, roleBadge: map[user.role] }
}

function UserAvatarAdapter({ name, size }: { name: string; size: 'sm' | 'lg' }) {
  return <Avatar name={name} size={size} />
}

type ProfileDisplayProps = {
  user: DisplayUser
  onEditIntent: () => void
  onDeleteIntent: () => void
}

function ProfileDisplay({ user, onEditIntent, onDeleteIntent }: ProfileDisplayProps) {
  return (
    <Flex direction="column" gap={3}>
      <Flex align="center" gap={3}>
        <UserAvatarAdapter name={user.fullName} size="lg" />
        <Flex direction="column" gap={1}>
          <Text variant="heading">{user.fullName}</Text>
          <Text variant="muted">{user.email}</Text>
        </Flex>
      </Flex>
      <Box>
        <Text variant="label">Role</Text>
        <Text>{user.roleBadge}</Text>
      </Box>
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

type Props = {
  userId: number
  onSaveIntent: (user: User) => void
  onDeleteIntent: (userId: number) => void
}

export function UserProfileBlock({ userId, onSaveIntent, onDeleteIntent }: Props) {
  const [user, setUser] = useState<User | null>(null)
  const [draft, setDraft] = useState<User | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    setIsLoading(true)
    // replace with queries/useUser(userId)
    fetchUser(userId).then((data) => {
      setUser(data)
      setIsLoading(false)
    })
  }, [userId])

  const handleSave = async () => {
    if (!draft) return
    setIsSaving(true)
    const saved = await saveUser(draft)
    setUser(saved)
    setIsEditing(false)
    setIsSaving(false)
    onSaveIntent(saved) // fire and stop
  }

  if (isLoading) return <Text variant="muted">Loading...</Text>
  if (!user) return <Text variant="danger">Could not load user.</Text>

  const displayUser = deriveDisplayUser(user)

  return (
    <Box p={4} radius="lg" border>
      {isEditing && draft ? (
        <Flex direction="column" gap={3}>
          <input
            value={draft.name}
            onChange={(e) => setDraft({ ...draft, name: e.target.value })}
          />
          <input
            value={draft.email}
            onChange={(e) => setDraft({ ...draft, email: e.target.value })}
          />
          <Button onClick={handleSave} disabled={isSaving}>
            {isSaving ? 'Saving…' : 'Save'}
          </Button>
          <Button variant="ghost" onClick={() => setIsEditing(false)}>
            Cancel
          </Button>
        </Flex>
      ) : (
        <ProfileDisplay
          user={displayUser}
          onEditIntent={() => {
            setDraft(user)
            setIsEditing(true)
          }}
          onDeleteIntent={() => onDeleteIntent(userId)}
        />
      )}
    </Box>
  )
}

// stubs — replace with real queries/
declare function fetchUser(id: number): Promise<User>
declare function saveUser(user: User): Promise<User>
