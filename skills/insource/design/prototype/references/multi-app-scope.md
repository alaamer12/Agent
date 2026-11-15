# Multi-App & System Scope Discovery Guide

> **What this owns:** Step 1 of `prototype` — how an agent determines whether a prototype request is a **Single App**, a **Multi-App Suite**, or a **Multi-Surface / Adaptive Experience (e.g. mobile-device viewport alongside desktop web)**, how to conduct the Scope Alignment Interview without rushing into code, and how to structure shared design systems.

---

## The "Never-Rush" Law

An agent that generates a prototype without clarifying system boundaries builds the wrong architecture:
- If it assumes a single app when the product requires an `admin-portal` + `operator-console` + `customer-web-app`, it creates messy mega-pages or tangles distinct permissions, layouts, and mental models into one bundle.
- If it assumes multiple separate repos/apps when the user just wanted a responsive multi-viewport preview of a single product, it over-engineers directories and loses shared state.
- If it builds without agreeing on how design tokens/styles are shared, it duplicates CSS, drifts colors, and breaks theme coherence.

**Do not write code or create directories until the Scope and Architecture Topology are established.**

---

## 1. Scope Topology Archetypes

Every request maps to one of three archetypes:

### Archetype 1: Single App
- **Examples:** A dedicated analytics dashboard, a single checkout flow, a settings manager.
- **Topology:** Root-level `pages/`, `js/`, `css/`, `_app.js`, `_app.css`.
- **URLs:** Direct clean routes: `/`, `/overview`, `/settings`.

### Archetype 2: Multi-App System Suite
- **Examples:** A platform with distinct roles/personas: an admin portal (governance, billing, users), an operator console (real-time queues, high-density incident response), and a client/consumer web app (onboarding, self-service).
- **Topology:** Monorepo-style `shared/` (design system tokens, common glyphs, state primitives) + `apps/<app-slug>/` (own thin pages, modules, role-specific CSS).
- **URLs:** App-namespaced clean routes: `/admin/overview`, `/operator/queue`, `/web/home`.
- **Theme sharing:** Base tokens in `shared/css/theme.css`. Each app imports the base tokens, then optionally layers an app theme override (e.g. `apps/operator/css/operator-theme.css` for high-density dark mode).

### Archetype 3: Multi-Surface / Viewport Variations
- **Examples:** An application that must demonstrate both:
  1. A **Native Mobile / Touch Viewport** experience (handheld aspect ratio, safe areas, bottom navigation, sheet gestures).
  2. A **Desktop / Wide Screen** experience (sidebar navigation, multi-column density, expanded data tables).
  3. A **Multi-Surface Previewer** (showing how shared business logic and components adapt to mobile frames vs wide windows).
- **Topology:** Either an app with dual viewport shells (`?surface=mobile|desktop` via URL state), or two sibling entries (`apps/mobile/` and `apps/web/`) sharing the core component modules in `shared/`.

### Archetype 4: Multi-Tenant & Dual-Realm Routing (Subdomains & Marketing vs In-App)
- **Examples:**
  1. **Dual-Realm / Marketing vs App Partitioning:** The unauthenticated public marketing website (`example.com`) vs the authenticated product workspace (`app.example.com`).
  2. **Multi-Tenant / Subdomain Branching:** Enterprise branching (`enterprise.example.com`), organization subdomains (`acme.example.com`), or documentation hubs (`docs.example.com`).
- **Topology:** Subdomain realms can be modeled either as distinct app folders under `apps/` (`apps/marketing/`, `apps/workspace/`, `apps/enterprise/`) sharing `shared/`, or via the central URL-state param **`?subdomain=<name>`** (or `?realm=marketing|app`).
- **Dev Server Routing:** `serve.mjs` cleanly recognizes both paths (`/<subdomain>/<page>`) and query params (`?subdomain=app&page=overview`). In local review, reviewers can switch between realms with a single query parameter or gallery chip without needing custom DNS/hosts configuration.

---

## 2. The Scope Alignment Interview

When the user's prompt mentions multiple portals, roles, or hybrid web/mobile targets (or is ambiguous about whether an ecosystem exists), pause and ask the **Scope Alignment Questions** before scaffolding:

### Round 1: Topology & Roles
```text
1. Scope Type:
   - Is this a standalone Single Application, or a Multi-App System Suite (e.g., admin + operator + consumer portals)?
   - If multi-surface/cross-device: Do you want a single responsive app, or distinct surfaces (e.g., dedicated mobile-device preview alongside a desktop web view)?

2. Apps / Surfaces Inventory:
   - What are the distinct apps, portals, or surfaces? (e.g., "admin", "operator", "consumer")
   - Who is the user/persona for each?
```

### Round 2: Design System & Styling Sharing
```text
3. Design System & Theme:
   - Do all apps share the exact same brand tokens (colors, typography, radii), or does each app have a persona-specific theme (e.g., Operator is high-density dark mode, Consumer is brand light mode)?
   - Are there shared component patterns (navigation header, tables, modal dialogs) or does each app have its own shell?
```

### Round 3: Unified Review Experience
```text
4. Gallery & Review:
   - The prototype includes a zero-dependency local dev server. For multi-app suites, a single root System Gallery (`/`) previews all screens across all apps, with direct clean URLs for every screen and state. Does this match your review flow?
```

*Rule:* If the user's initial prompt is already explicit and unambiguous (e.g., "Build a multi-app prototype with an admin portal and an operator dispatch board sharing the same design system"), state your architectural plan back to them in one concise paragraph and confirm before building.

---

## 3. Structural Contracts

### Multi-App Layout (`apps/` + `shared/`)

```text
prototype/
├── package.json              # scripts to run and test the entire suite
├── serve.mjs                 # zero-dep multi-app clean routing
├── index.html                # System Suite Gallery (all apps, screens, state chips)
├── shared/                   # The Design System & Core Primitives
│   ├── css/
│   │   ├── theme.css         # Global tokens: palette, type scale, spacing, elevation
│   │   └── _base.css         # Base resets, typography, shared utility classes
│   └── js/
│       ├── _app_core.js      # Pure state helper (mountState, parse, patch, toQuery)
│       ├── glyphs.js         # Shared icon set / SVG glyphs
│       └── utils.js          # Shared formatting, seeded PRNG for ?filled
└── apps/
    ├── <app-1>/              # e.g., admin
    │   ├── pages/
    │   │   └── <page>.html   # Thin HTML entry
    │   ├── js/
    │   │   ├── _app.js       # App shell + imports _app_core.js
    │   │   ├── specs.js      # Component state trees for this app's pages
    │   │   └── <page>.js     # Page DOM builder
    │   └── css/
    │       ├── _app.css      # App-level layout, nav shell, theme overrides
    │       └── <page>.css    # Page-scoped styles
    └── <app-2>/              # e.g., operator or mobile
        ├── pages/
        ├── js/
        └── css/
```

### Clean URL Routing for Multi-App

`serve.mjs` maps clean paths directly by prefix:
- `http://localhost:5173/` → Root System Gallery (`index.html`)
- `http://localhost:5173/admin/overview` → `apps/admin/pages/overview.html`
- `http://localhost:5173/operator/queue` → `apps/operator/pages/queue.html`
- `http://localhost:5173/shared/...` → Serves shared CSS, JS, and asset statics
- Query strings (`?tab=active&open=modal&filled=42`) pass through untouched to the page module.

---

## 4. Multi-Surface & Multi-Viewport Nuances

When modeling multi-surface applications (e.g. mobile vs desktop):

1. **Dual-Surface via Query Param (`?surface=mobile|desktop`)**:
   - Best when the codebase represents a single adaptive product.
   - The shell adapts: `mobile` injects a simulated status bar, bottom navigation tab strip, and gesture handles; `desktop` expands into a sidebar navigation and wide data grid.
2. **Dedicated Surface Apps (`apps/mobile` vs `apps/web`)**:
   - Best when mobile and desktop are conceptually distinct user experiences (e.g. Mobile Field Worker vs Desktop Backoffice).
   - In the System Gallery, mobile screens render inside a mobile aspect-ratio viewport (`aspect-ratio: 390 / 844` or `412 / 915`), while desktop screens render in `1280 / 800`.

---

## 5. Dual-Realm & Subdomain Simulation (`?subdomain=`)

In production, multi-realm systems rely on DNS subdomains (e.g., `notion.so` for landing/pricing vs `app.notion.so` for workspace; `acme.platform.com` for tenant workspaces). During prototype review on a local dev server (`http://localhost:5173`), configuring local `/etc/hosts` or local DNS wildcards is friction that reviewers shouldn't have to bear.

The `prototype` skill standardizes two compatible mechanisms for dual-realm and subdomain branching:

### 1. Simulated Subdomains via Query Parameter (`?subdomain=<name>`)
- A single page or app shell inspects `?subdomain=`:
  - `/?subdomain=marketing` (or default): Shows the public marketing landing page, feature highlights, and "Sign in" call-to-actions.
  - `/?subdomain=app`: Swaps the shell to the authenticated workspace (sidebar, recent documents, team switcher).
  - `/?subdomain=enterprise`: Demonstrates the enterprise tier variations (SSO login prompt, custom tenant branding, compliance widgets).
- **Navigation Handoff:**
  - Clicking "Log in" on the marketing page executes `sync({ subdomain: "app" })` or links to `<a href="/?subdomain=app">`, seamlessly transitioning the reviewer across realms without page unloads.

### 2. Path-Mapped Subdomain Namespaces
In `apps/` multi-app mode, `serve.mjs` maps subdomain names to their app folders:
- `http://localhost:5173/app/overview` → `apps/app/pages/overview.html` (the workspace)
- `http://localhost:5173/marketing/pricing` → `apps/marketing/pages/pricing.html` (the landing site)
- Both realms share `/shared/css/theme.css` for brand design tokens, but the marketing realm uses brand-expressive display typography while the app realm uses high-density UI typography.

---

## 6. Cross-App Navigation — the Dev Dock's Apps tab

**THE INVIOLABLE RULE: NEVER INJECT CROSS-APP NAVIGATION BUTTONS INTO THE PAGE'S MAIN CONTENT.**

A page's header, sidebar, and body must strictly represent **the real product's authentic interface**. In a multi-app suite (e.g. `admin`, `operator`, `customer`), putting a button labeled "Go to Admin App" inside the customer portal's main navbar or card content corrupts the design and renders screenshots invalid.

The rule generalizes beyond cross-app nav: **every** control about the prototype — app switching, data-state toggles, inspection tools, pickers — is dock or URL content, never page content ([`prototype-dock.md`](prototype-dock.md)).

### The dock as the single chrome, per suite

1. **One `devdock.js`, shared.** It lives in `shared/js/`, every app's pages load it, and every page sets the same `window.DevDockInit = { apps: [...] }` list (name, url, `current: true` on the app being viewed) before the script tag. One configuration, N apps — never a per-app switcher implementation.
2. **The Apps tab lists the suite.** Current-app badge at top; one row per app/subdomain/surface variant, direct clean links.
3. **Removal for capture:** `?dock=hide` removes the dock entirely for screenshot capture and video recording — including the Apps tab, so gallery iframes and visual-regression runs see pure product UI.

Legacy note: pre-dock projects carried a bottom-right floating trigger for this (`?apps_toolbar=hide`, implemented by `mountAppsToolbar()` in the shared layer) and a separate bottom-left story toolbox (`sy_toolbar`). Both are superseded by the dock; the `assets/starter/` helpers still work, and the old split placement (bottom-left tools vs. bottom-right switcher) is retired — do not build new chrome in that shape.
