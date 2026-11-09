# Anti-Patterns & Explicit Don'ts

The `## Do's and Don'ts` section is the highest-value guardrail for AI coding agents. When models generate UI from scratch, they default to common "AI slop" patterns. Explicit negative constraints prevent these defaults.

---

## 1. Catalog of Common AI Slop Anti-Patterns

### 1.1 The "Pastel Pill" Syndrome
- **The Slop**: Putting 9999px pill radii and pastel gradient fills on every button, badge, and card.
- **The Rule**: Corner radii must match the defined `radius` token scale. Primary buttons are solid, never multi-stop rainbow gradients.

### 1.2 The Floating Card Trap
- **The Slop**: Nesting cards inside cards inside dialogs, each with heavy, muddy black box-shadows.
- **The Rule**: Use borders (`1px solid var(--border-subtle)`) and background lightness steps to separate surfaces. Max 1 card nesting level.

### 1.3 Random Spacing & Magic Numbers
- **The Slop**: Hardcoding arbitrary margins like `margin-top: 17px;` or `padding: 13px 21px;`.
- **The Rule**: Spacing values must strictly resolve to the `spacing` tokens (4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px).

### 1.4 Low-Contrast Ghost Text
- **The Slop**: Light gray text (`#9ca3af` / `oklch(75% 0 0)`) on white backgrounds for secondary labels, failing WCAG AA.
- **The Rule**: Secondary text must maintain at least 4.5:1 contrast against its immediate background.

### 1.5 Decorative Non-Functional Badges
- **The Slop**: Scattering non-clickable colorful pill badges across tables and cards as visual filler.
- **The Rule**: Every badge must communicate real state (status, count, role).

---

## 2. Formatting the Do's and Don'ts Section

A compliant `DESIGN.md` must conclude with this balanced two-column table:

```markdown
## Do's and Don'ts

| Do | Don't |
|---|---|
| **Use 1px hairline borders** with subtle neutral tokens to delineate surfaces and cards. | **Don't use heavy, dark drop shadows** to separate UI layers. |
| **Limit primary accent color** to the single most important call-to-action per screen. | **Don't use primary brand color** on multiple competing buttons in the same view. |
| **Maintain strict 4.5:1 text contrast** for all body and secondary labels. | **Don't use low-contrast muted gray text** that fails WCAG AA readability. |
| **Align tabular numerical data to the right** with tabular numbers (`font-variant-numeric: tabular-nums`). | **Don't center-align financial or metric data** in tables. |
| **Use sentence case** for button labels, headings, and table columns. | **Don't use Title Case** or ALL CAPS for standard body labels and dialog titles. |
| **Use consistent 4px/8px incremental spacing** from the spacing token scale. | **Don't invent arbitrary pixel values** (`margin: 15px`) outside the design tokens. |
| **Provide explicit hover, focus-visible, and disabled states** for all interactive elements. | **Don't remove focus rings** (`outline: none`) without an explicit focus indicator. |
```
