# Universal UI & Design System Engineering Reference

This reference guide establishes the principles and contract options for defining UI rules, interaction behaviors, and design system constraints across frontend applications (Web, Mobile, Desktop).

---

## 1. UI Activation Gate & Tooling Discovery

Before applying UI rules to an application, the agent must verify that the confirmed application actually possesses a visual user interface:
- **CLI, Headless Daemons, Background Workers, RPC Services:** UI rules skill must be bypassed completely.
- **Visual Frontend Applications:** UI rules skill triggers. The agent uses available search or documentation tools to investigate the target platform's latest framework tools, libraries, and major version conventions to avoid version mismatch traps or outdated APIs.

---

## 2. Core UI Architectural Contracts

UI rules govern the operational and visual behavior of components across 8 fundamental dimensions:

### 2.1 Data Fetching, Preservation & Invalidation Contract
- **State Preservation Across Navigation:** Screen and component states (scroll positions, loaded lists, search filters) must be preserved in memory or client caches when navigating back and forth; users must never be forced to re-fetch identical data upon returning to a view.
- **Cache Strategy:** Implement explicit caching lifecycles (e.g. *Stale-While-Revalidate*). Show existing cached data immediately on view entry while checking for background updates silently.
- **Deterministic Invalidation:** Define targeted invalidation rules:
  - *Mutation Triggers:* Successful write operations (create, update, delete) selectively invalidate relevant query keys/collections.
  - *Lifecycle Triggers:* When the app returns from background or regains network connectivity after an outage, trigger focused refetches.
- **Optimistic UI with Rollback:** User actions reflect immediately in the UI state; if the background persistence fails, revert gracefully and present the error via the sub-text slot or toast.

### 2.2 Responsiveness Contract
- **No Fixed Heights on Text Containers:** Every container holding text must size to its content (`auto`). Fixed heights on text elements cause severe text clipping across different languages or dynamic text scaling.
- **Fluid Grid & List Row Sizing:** List items and grid cells must use automatic row sizing; avoid measure-first-item optimizations when content heights vary.
- **Overflow-Safe Text:** Unbroken strings (URLs, hash IDs, long alphanumeric tokens) must break gracefully (`line-break: anywhere` or `CharacterWrap`).
- **Density-Independent Sizing:** All dimensions must use density-independent units (`dp`, `rem`), referencing tokenized spacing scales rather than hardcoded magic numbers.

### 2.2 Skeleton Loading System (The Pairing Rule)
- **Sibling Pairing Rule:** Every content container has a sibling Skeleton component matching its exact visual footprint (aspect ratio, height, corner radius). They toggle via visibility bindings without unmounting or shifting surrounding layout.
- **Atomic Skeletons:** One content element = one skeleton element. Avoid giant generic rectangles that hide real layout structure.
- **Shimmer Animation Standards:** Shimmer sweeps must be smooth, constant-speed, and lighter than the skeleton base color to provide clear asynchronous feedback.

### 2.3 Text Display & Smart Truncation Rules
- **Two Canonical Modes:**
  - *Mode 1 (Wrapping):* Unlimited lines (`WordWrap`) for primary feed titles, descriptions, and error banners.
  - *Mode 2 (Truncation + Ellipsis):* Capped lines (1–2 lines) with tail truncation for metadata chips, badges, and breadcrumbs.
- **Truncation Thresholds:** Support both line-count caps and character-count thresholds with clean ellipsis appending (`…`).

### 2.4 Sub-Text Slot System
- **Empty-Safe Metadata Slot:** Primary text and card components provide a dedicated `SubText` slot that renders with zero footprint when empty.
- **Error Binding Target:** Standardized binding point for user-facing error explanations (`ExternalMessage`) and actionable resolution hints (`FixMessage`).
- **Multi-Level Slots:** Compound components (e.g. project cards) expose primary title, secondary metadata, and tertiary sub-text slots cleanly.

### 2.5 Icon System — Three Tiers
- **Tier 1 (Neutral):** Inactive navigation items, secondary actions, disabled controls.
- **Tier 2 (Brand / Positive):** The single primary action per view, active states, success badges.
- **Tier 3 (Conceptual):** Distinct semantic hues assigned per row concept (e.g., settings categories, status indicators).
- **Three Required States:** Every interactive icon defines distinct visual states for Normal (100% opacity), PointerOver/Hover (80% opacity), and Disabled (38% opacity, falling back to neutral color).

### 2.6 Illustrations & Letterbox Panels
- **Letterbox Panels:** Full-width hero illustrations on a fixed, non-theme-reactive dark canvas for onboarding and feature splash screens.
- **Sticker Assets:** Compact vector illustrations for empty states (empty feed, empty search), success dialogs, and error recovery screens, provided with light/dark theme variants.

### 2.7 Internationalization (i18n), Localization & Text Directionality
- **Locale & Direction Scoping:** Determine whether the application is single-locale (e.g. English-only LTR), multi-lingual LTR, or bidirectional (incorporating RTL scripts like Arabic, Hebrew, Urdu, or Persian).
- **Single Root FlowDirection:** For bidirectional apps, directionality (`RightToLeft` vs `LeftToRight`) is declared at the root container/shell level, never duplicated per control.
- **Unicode Bidi Isolation:** Mixed directional content (e.g. numbers, currencies, foreign tokens inside RTL sentences) must be wrapped in directional isolate markers (e.g. `\u2068` ... `\u2069`) to prevent number and punctuation re-ordering bugs.
- **Logical Properties:** When internationalized across directions, physical spacing (`left`/`right`) is prohibited; use logical start/end properties (`margin-inline-start`, `start` alignment) so layouts mirror correctly.
- **Script Font Fallbacks:** Choose typography stacks that include legible, native typeface fallbacks for the application's supported language scripts.
