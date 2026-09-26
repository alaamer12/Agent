# Structure, Stereotypes & Growth (Full)

## Recommended project structure (adaptable)

Vertical feature slices keep related concerns together. Adapt depth to team size and domain complexity; the structure is recommended, not forced.

```
src/
  shared/
    ui/
      primitives/              ← <<Primitive>> (Box, Text, Flex, Button, …)
      behavioral/              ← <<Behavioral>> (Dropdown, Modal, Tooltip, …)
    blockiya-core/             ← <<Utility>>
  entities/                    ← domain models shared across features
  features/
    projects/
      blockiyas/
        ProjectListBlock/
          index.tsx            ← pure orchestrator, zero styling
          context.ts           ← optional Context Object
          children/            ← private presentational views
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
    charts/
  app/
    layout.tsx
    page.tsx
```

### Placement rules

- A feature's Blockiyas live only under `features/<feature>/blockiyas/`.
- `queries/` contains only hooks — no direct API calls inside Blockiyas.
- `children/` are private to their parent. Promote when a second consumer appears.
- `adapters/` is always top-level. An adapter is never a feature concern.
- Global stores live outside `features/`.

### Key rules from original

- A feature's Blockiyas live in `features/<n>/blockiyas/` — never inside another feature's folder.
- `queries/` contains only hooks. No `invoke()` or `fetch()` calls directly in Blockiyas.
- `children/` holds presentational components private to their parent Blockiya. If reused across two Blockiyas, it moves up or becomes its own Blockiya.
- `adapters/` is its own top-level folder. An adapter is not a feature concern.
- For `blockiya-core/` full directory tree, see the implementation reference.

## Stereotypes in depth

Stereotypes are a shared vocabulary that appears in UML and in code comments as `<<Stereotype>>`. They are not compiler-enforced; they make intent visible.

| Stereotype | Meaning | Growth signal |
| --- | --- | --- |
| `<<Page>>` | Top-level route component | — |
| `<<Feature>>` | Large workflow orchestrator (wizards, multi-step) | Becomes the owner of several Compounds |
| `<<Compound>>` | Combines 2–5 child blocks | May later be extracted into a Feature |
| `<<Atomic>>` | Single-purpose leaf | Accumulating children → promote to Compound |
| `<<Primitive>>` | Visual token only | — |
| `<<Behavioral>>` | Owns interaction state via compound components | — |
| `<<Adapter>>` | Third-party isolation (token/event/lifecycle) | Never owns domain state |
| `<<Utility>>` | Pattern-native helper with zero domain knowledge | — |
| `<<Context>>` | Scoped provider for deep trees | — |
| `<<Hook/Query>>` | Data access | Lives exclusively in `queries/` |

**Primitive vs Behavioral:** both live in the design system and are consumed identically by Blockiyas. The distinction matters for how they are built and constrained. Behavioral units must use the compound-component API so that interaction state never leaks upward.

**Utility test:** remove every domain word; if the helper still makes complete sense, it is a `<<Utility>>`.

## How a Blockiya grows

### Growth signals

- **Props or intents > 7** — two concerns have merged. Extract one into a child Blockiya.
- **Two different domains in one component** — e.g. profile editing + avatar management. Extract the second domain.
- **Private child starts being reused** — promote to public Blockiya, primitive, or utility depending on whether it carries domain logic.
- **Stereotype mismatch** — label says `<<Atomic>>` but reality has children. Update the stereotype and structure.

### Atomic → Compound transition

```
UserProfileBlock <<Atomic>>              UserProfileBlock <<Compound>>
  - fetches user                           - fetches user
  - owns isEditing                         - owns isEditing, draft, errors
  - renders everything inline      →       - renders ProfileDisplayView
                                           - renders ProfileEditView
                                           - renders AvatarManagerBlock (child)
```

### When to extract

- **Presentational child** — no state, no API calls, used only by this Blockiya.
- **Child Blockiya** — has its own domain state, its own data calls, or is reused across parents.

## UML notation reminders

- Stereotypes appear as `<<Stereotype>>`.
- Hierarchy: Page → Blockiya (props down / events up).
- Ownership: Blockiya `*--` child blocks.
- Usage: Blockiya `..>` primitives / adapters / hooks.

When generating diagrams or reviewing architecture, always annotate with the correct stereotype and show the intent direction (▲) and prop direction (▼).
