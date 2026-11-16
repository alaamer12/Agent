# Fix Types — Templates for the "Suggested Fix" Field

Every finding's fix must be **executable**, not descriptive. Pick the type that matches the
finding, and follow its template.

---

## Type A — Code/style fix

Use when the fix is achievable by changing code that already exists (color tokens, spacing
system, layout, CSS/JS-driven motion, component composition).

**Must include a real diff**, using syntax that matches the actual file (`diff`, `jsx`, `css`,
etc.), ready to paste into the file at the stated line range.

```markdown
### Suggested fix
Give each icon its own accent color from the existing palette rather than one flat gray:
```diff
- <LockIcon color="#888888" />
+ <LockIcon color="var(--accent-blue)" />
- <EyeIcon color="#888888" />
+ <EyeIcon color="var(--accent-teal)" />
```
```

---

## Type B — New asset needed

Use when the fix requires an image/icon/illustration that doesn't exist yet.

Two required parts:
1. How the asset should be wired into the code (a real snippet, path following the project's
   existing asset convention from `stack-detection.md`).
2. A ready-to-use **image-generation prompt** — built from the project's *actual* colors,
   brand tone, and existing asset style, pulled from real files (theme/tokens, other assets in
   the repo). Never invent generic placeholder brand language ("modern, clean, professional")
   without grounding it in something concrete found in the project.

```markdown
### Suggested fix
This bottom sheet is pure text with no visual anchor. Add a supporting illustration:
```jsx
<img src="/assets/illustrations/empty-cart.svg" alt="" />
```

**Image generation prompt:**
> Flat vector illustration, isometric style, primary color #4F46E5 (indigo, matches
> `--color-primary` in `src/styles/tokens.css`) with #FBBF24 (amber) accent, matching the
> playful-professional tone used in `src/assets/illustrations/onboarding-1.svg` and
> `onboarding-2.svg`. Subject: an empty shopping cart with a small floating checkmark.
> Transparent background, no text, no border.
```

If the project has **no existing visual style to ground the prompt in** (first visual asset in
the project), say so explicitly and build the prompt from whatever concrete signals exist
(framework name, copy tone, primary brand color if any is defined) — never fabricate details
with no basis in the project.

---

## Type C — Restructure/decompose

Use when the problem is too much visual information crammed into one view — long tables, dense
dashboards, cluttered CLI output, a screen that should be split across multiple views.

The fix must respect what `stack-detection.md` found:

```markdown
### Suggested fix
This CLI dumps 40+ rows in a flat table — hard to scan in a terminal. The project already uses
`ink` + `ink-tab` (see `src/cli/dashboard.tsx`), so decompose into tabs by category:
```tsx
[real ink/ink-tab code using the project's existing component patterns]
```
```

If the stack doesn't support a richer component (bare `console.log` CLI, no layout library):

```markdown
### Suggested fix
This CLI dumps 40+ rows in a flat table. No TUI/layout library is present in this project, so
rather than adding one, paginate the output — print 10 rows at a time with a
`--page`/`-p` flag, or group rows under printed category headers:
```js
[real chunking/pagination code using only what's already imported]
```
**Requires new dependency:** none — uses existing `console.log` approach.
```

---

## Choosing between types

- Ask: "Does this need new visual content (image/icon)?" → Type B.
- Ask: "Is there just too much crammed into one view?" → Type C.
- Otherwise, if it's a matter of adjusting how existing elements are coded/styled/arranged →
  Type A.

A single finding can combine types (e.g., decompose a view *and* add a missing icon within the
new structure) — in that case, include both parts under one "Suggested fix" section, clearly
separated.
