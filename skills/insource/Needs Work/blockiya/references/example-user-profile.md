# Canonical Example (React)

Focused role demonstration. Full template: `assets/templates/user-profile-react.tsx`.

See also the polyglot side-by-side: `example-user-profile-polyglot.md`.

## Key snippets

**Derive (module scope):**
```tsx
function deriveDisplayUser(user: User): DisplayUser {
  return {
    fullName: user.name,
    email: user.email,
    roleBadge: { admin: 'Admin', editor: 'Editor', viewer: 'Viewer' }[user.role],
  }
}
```

**Blockiya intent (fire and stop):**
```tsx
const save = useIntent(async (draft: User) => {
  const saved = await saveUser(draft)
  onSaveIntent(saved) // job ends here
})
```

**Presentational child receives derived data only:**
```tsx
<ProfileDisplay
  user={displayUser}
  onEditIntent={startEdit}
  onDeleteIntent={() => onDeleteIntent(userId)}
/>
```

**Page owns post-intent decisions:**
```tsx
<UserProfileBlock
  userId={1}
  onSaveIntent={(u) => { /* navigate / toast / refresh */ }}
  onDeleteIntent={(id) => { /* confirm modal? */ }}
/>
```
