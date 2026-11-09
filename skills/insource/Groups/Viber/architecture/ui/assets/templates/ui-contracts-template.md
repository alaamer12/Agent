# Universal UI & Design System Contracts Template

Use this universal template when drafting UI rules and visual interaction contracts for an application with a frontend. Adapt the sections based on the application's actual platform and design requirements.

```markdown
# UI Rules & Design System Contracts — <Application Name>

> **Scope:** Visual design contracts, responsive behavior, typography, state indicators, and interaction conventions for `<Application Name>`.
> **Platforms:** `<e.g. Web (Desktop/Mobile), Native iOS/Android, Desktop Win/macOS>`

---

## 1. Data Fetching, State Preservation & Invalidation Contract

- **Client Caching Strategy:** `<e.g. Stale-While-Revalidate / Memory cache / Local client DB (SQLite/IndexedDB)>`
- **State Preservation Across Navigation:**
  - View models / components preserve scroll position and query parameters when switching views or tabs.
  - Initial load presents cached data immediately; background sync updates view without full layout remount.
- **Cache Invalidation Triggers:**
  - *On Mutation:* `<Specify which queries or collections are invalidated on create/update/delete>`
  - *On Window/App Focus:* `<e.g. silent refetch if cache older than N minutes>`
  - *On Network Reconnect:* `<automatic queue flush & fresh sync>`
- **Optimistic Updates:** `<Define actions using optimistic local UI updates with rollback on failure>`

---

## 2. Responsiveness & Screen Geometry Contract

- **Breakpoints / Form Factors:**
  | Breakpoint / Tier | Dimension Range | Target Experience |
  |---|---|---|
  | `<Compact / Mobile>` | `<0px – 599px>` | `<Single-column, bottom navigation, full-width cards>` |
  | `<Medium / Tablet>` | `<600px – 1023px>` | `<Two-column split view, collapsed sidebar>` |
  | `<Expanded / Desktop>` | `<1024px+>` | `<Multi-pane layout, persistent rail/sidebar>` |

- **Layout Switching Discipline:** `<e.g. Responsive fluid CSS / Adaptive block swapping PlatformSelect>`
- **Safe Area Insets:** `<Handling strategy for notches, navigation bars, and status bars>`

---

## 2. Skeleton Loading & Asynchronous Feedback

- **CLS Invariant:** Loading skeleton placeholders must strictly mirror the final rendered geometry (aspect ratio, padding, height).
- **Feedback Hierarchy:**
  - *Full View Load:* Skeleton screens matching target layout.
  - *Inline Mutation / Refresh:* Subtle spinners or shimmer overlays without unmounting existing content.
  - *Optimistic Updates:* Instant UI state reflection with graceful rollback on failure.

---

## 3. Typography, Text Clamping & Slot System

- **Text Truncation Rules:**
  - Primary Titles: Max `<N>` lines with ellipsis (`line-clamp-<N>`).
  - Secondary Metadata: Single line with ellipsis; full content viewable on hover/tooltip.
- **Slot System:** Components provide fixed-height metadata slots (e.g. tags, badges, relative timestamps) to prevent layout shifting between list items.
- **Linguistic Expansion:** Design containers must withstand a 30% expansion in text length for internationalization.

---

## 4. Icon System & Visual Assets

- **Icon Hierarchy:**
  - *Tier 1 (Interactive / Navigation):* Standardized vector glyphs with minimum touch target `<e.g. 44x44px>`.
  - *Tier 2 (Informational Badges / Inline):* Compact semantic icons (`16x16px` or `20x20px`).
  - *Tier 3 (Hero / Empty-State Illustrations):* Vector illustrations centered in dedicated letterbox panels.
- **Format:** `<SVG / Font Glyphs / Canvas>` (Bitmap PNG/JPEG prohibited for icons).

---

## 5. Internationalization (i18n), Localization & Text Directionality

<!-- If the application supports multi-lingual, international, or bidirectional (RTL) locales, define the rules below. If English/single-locale only, document as single-locale LTR. -->

- **Locale & Direction Scope:** `<e.g. Single-locale LTR (English) / Multi-lingual LTR / Bi-directional (LTR + RTL Arabic/Hebrew)>`
- **Directionality Strategy:**
  - *Logical Layout Properties:* `<Enforce logical spacing (margin-inline-start, padding-inline-end) if multi-direction; standard spacing if single-locale>`
  - *Mirroring Rules:* `<Define navigation mirroring rules if RTL supported; N/A if single-locale LTR>`
  - *Mixed Direction Isolation:* `<Unicode bidi isolation markers (\u2068...\u2069) for numbers/currencies/handles in mixed text, if applicable>`
- **Font Stacks & Script Fallbacks:**
  - Primary Font: `<e.g. Inter, system-ui, Roboto>`
  - Script Fallbacks (if internationalized): `<e.g. Arabic (Tajawal/Cairo), CJK (Noto Sans), etc.>`
- **String Extraction & Resource Keys:** `<e.g. i18next JSON, Resx, Flutter intl>`

---

## 6. Theming, Contrast & Accessibility

- **Semantic Color Tokens:** Component styles reference semantic tokens (`bg-surface`, `text-primary`, `border-subtle`), never raw hex codes.
- **Contrast Ratios:** Minimum contrast ratio `<4.5:1 (WCAG AA) / 7:1 (WCAG AAA)>`.
- **Keyboard & Focus State:** Visible high-contrast focus rings on all interactive elements.
```
