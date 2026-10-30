# Example: a discovery report

Command: `life component src/features/settings/` (a directory, so discovery runs automatically)

Recon: React with Motion, no token file, dense settings UI, reduced-motion handling absent in code.

### Opportunities

| # | Location | Today | Purpose | Frequency | Proposed command | Suggested direction |
|---|---|---|---|---|---|---|
| 1 | `SaveBar.tsx:42` | Appears with no motion | Spatial consistency | Occasional | component | Rises 8px with opacity, 200ms, enter curve; exits 140ms; reduced motion: opacity only |
| 2 | `ProfileForm.tsx:88` | Success text appears abruptly | State indication | Occasional | micro | In-place check on the Save button, 300ms, no toast |
| 3 | `ThemePicker.tsx:15` | Choosing a theme swaps instantly | Preventing a jarring change | Rare | transition | Crossfade with 3px blur bridge, 240ms; reverse identical |

### Rejected candidates

- `CommandMenu.tsx:12` open and close. Rejected: keyboard-initiated and very frequent.
- `DataTable.tsx:60` row highlight on hover. Rejected: functional data the user scans; the existing instant highlight is correct.
- `Sidebar.tsx:30` item hover scale. Rejected: tens of times a day; color change only.

### Verdict

This interface needs very little motion. The highest-leverage change is the save bar (1). Reduced-motion handling is missing everywhere, which is a bigger gap than any missing animation.

The user picks 1; the run continues from the gate with `life component SaveBar.tsx`. Items 2 and 3 are recorded as follow-ups.
