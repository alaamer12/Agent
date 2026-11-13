# Screen Inventory Planning: Professional Methodology Research

> Research compiled for the agent skill: **page/screen inventory planning for software products**.
> Seven research areas covering IA methodology, format standards, signal catalogues, common mistakes, platform conventions, multi-role IA, and versioning.

---

## Research Area A: Information Architecture Methodology

### The professional workflow for deriving a screen inventory

Professional UX teams do not begin with screens. They begin with users, content, and context — and derive screens as a byproduct of that work. The industry-standard progression is:

#### Phase 1: Research & Discovery

Before listing a single screen, practitioners gather:

- **Stakeholder interviews** — business goals, KPIs, constraints, non-negotiables
- **User research** — support tickets, analytics, session recordings, interviews to understand *actual* top tasks (not assumed ones)
- **Mental model mapping** — how do users think about the domain? What words do they use? What groups do they expect?
- **Jobs-to-be-done (JTBD) analysis** — what outcome is the user trying to achieve, in what situation, with what emotional context?
- **User journey maps** — the full arc of a user's experience across time (touchpoints before, during, and after using the product)
- **Entity-relationship analysis** — what are the core nouns in the system (User, Document, Project, Invoice)? Each entity often implies at minimum a list screen and a detail screen.
- **Competitor analysis** — what screen conventions has the market already established? Users carry mental models from tools they already know.
- **User stories** — "As a [role], I want to [action] so that [outcome]" — each story is a candidate screen trigger

#### Phase 2: Content Inventory (the precursor to screen inventory)

A **content inventory** is a catalogue of every piece of content that must exist in the product — text, media, data fields, user-generated content, system messages. It answers: *what must be communicated or displayed?*

A **screen inventory** answers: *where does that content live, and how is it navigated to?*

The content inventory feeds the screen inventory. If you know you need to display 12 categories of account settings, you can reason about whether that's one screen with tabs, or 12 separate screens. Without the content inventory, the screen inventory is guesswork.

#### Phase 3: Card Sorting

Card sorting is used to discover how users mentally organize the content and features of a product.

- **Open card sort**: Users are given cards (representing features, content types, or screens) and asked to group them and name the groups. Used to discover natural categories — drives nomenclature and primary navigation structure.
- **Closed card sort**: Users sort cards into pre-defined categories. Used to validate a proposed structure before committing to it.
- **Hybrid card sort**: Categories are pre-defined but users can create new ones. Balances discovery with validation.

Card sorting outputs directly inform the navigation structure, which defines which screens live at which level.

#### Phase 4: Sitemap / Screen Map drafting

The sitemap is the first structural artefact — a hierarchical diagram of screens and their parent-child relationships. It is not a wireframe; it contains no layout details. It answers: *what screens exist and how are they related?*

At this stage, screens are nodes. Each node gets a name, an ID, and a rough description of purpose.

#### Phase 5: Tree Testing

Tree testing validates the proposed IA *before* visual design begins. Users are given real tasks ("Where would you go to change your password?") and must navigate a text-only tree structure. No visual design, no icons — just hierarchy. This isolates whether the structure itself works.

Nielsen Norman Group research shows tree testing catches structural problems that card sorting misses, because card sorting is about grouping but tree testing is about findability in a real sequence.

#### Phase 6: Wireframing and flow mapping

Each node in the sitemap becomes a wireframe. At this stage, states and variants are designed. User flow diagrams show the transitions between screens.

---

### Screen vs State: The core distinction

This is one of the most consequential decisions in IA planning and one of the most frequently gotten wrong.

**A screen is:**
- A distinct destination in a navigation stack or routing system
- Something that gets its own URL (or its own named route in a mobile app)
- Something the Back button navigates away from
- Something that could be deep-linked to or bookmarked
- Something that loads a substantially different dataset or layout

**A state is:**
- A variation of a screen that exists at the same URL/route
- A change in content caused by user interaction without a navigation event
- Something that the Back button does *not* exit (closing a modal, collapsing an accordion, switching a tab within a page)
- Something ephemeral — it doesn't need to be shareable or bookmarkable

#### The four decision tests (in order)

1. **The Back button test**: If the user presses Back, should they return to the previous location or close a UI element within the current location? If previous location → it's a screen. If close UI element → it's a state.

2. **The URL/deep-link test**: Does this variation need a unique URL so it can be bookmarked, shared, or linked to from an email? If yes → screen. If no → state (or query param on the same screen).

3. **The mental model test**: Does the user feel they have *navigated somewhere new*, or are they *exploring the same space*? New destination → screen. Same space → state.

4. **The data complexity test**: Does this variation require loading a substantially different or heavier dataset? If yes → screen (for performance and architectural clarity). If it's a filtered view of the same data → state (or query param).

#### Common specific cases

| Scenario | Decision | Reasoning |
|---|---|---|
| Empty state (no data yet) | State | Same screen, different content fill |
| Loading state (skeleton) | State | Transient, same route |
| Error state (fetch failed) | State | Same route, different render |
| Edit mode for a detail view | Context-dependent | On mobile: usually a separate screen. On web with a few fields: modal or inline state. With many fields/validation: separate screen. |
| Modal confirmation dialog | State | Overlay on current screen, no URL change |
| A settings sub-section | Screen | Has its own URL, is navigated to |
| A tab within a settings page | State (usually) | Same URL, tab selection may be a query param |
| Search results filtered by category | State (query param) | Same screen, same URL with `?category=X` |
| A specific product detail | Screen | Has its own URL, requires separate data fetch |
| Master-detail on desktop (side panel) | State | The panel is a component within the screen |
| Master-detail on mobile | Screen | The detail view is pushed onto the navigation stack |

#### When a variation becomes a separate screen

A variation should be promoted to a full screen when **any two or more** of the following are true:
- It requires unique URL/deep-link support
- It has meaningfully different navigation controls (different back behaviour, different header)
- It is reachable from more than one entry point (requires routing)
- Its content is loaded independently (separate API call)
- It has its own empty state, error state, and loading state that are distinct from the parent
- Platform conventions dictate it (iOS pushes detail views as screens; web can use modals more freely)

---

### The screen → route → component hierarchy

```
Information Architecture (structural model)
  └── Screen (a distinct destination / view)
        ├── Route (the URL or named navigation target that maps to this screen)
        │     └── Example: /dashboard/projects/:projectId
        └── Component tree (the UI rendered at that route)
              ├── Layout component (shell, nav, sidebar — persistent)
              │     └── Shared across multiple routes; does not re-render on navigation
              └── Page component (the smart/container component for this route)
                    ├── Loads data for this specific route
                    ├── Handles loading / error / empty states
                    └── Renders presentational child components
                          ├── Organism (complex UI block, e.g. ProjectCard)
                          │     └── Molecule (grouped elements, e.g. StatusBadge + Title)
                          │           └── Atom (smallest unit, e.g. Button, Icon)
                          └── State-dependent renders (empty state, error boundary, skeleton)
```

Modern file-based routing frameworks (Next.js App Router, Remix, Nuxt, Expo Router) make this hierarchy explicit in the file system:

```
app/
├── layout.tsx              ← Root layout (persistent shell)
├── page.tsx                ← Route: /
├── dashboard/
│   ├── layout.tsx          ← Dashboard layout (sidebar, etc.)
│   ├── page.tsx            ← Route: /dashboard
│   └── projects/
│       ├── page.tsx        ← Route: /dashboard/projects (list screen)
│       └── [id]/
│           └── page.tsx    ← Route: /dashboard/projects/:id (detail screen)
```

Each `page.tsx` file = one screen in the inventory.

---

### Inputs used in professional IA planning

| Input | What it contributes |
|---|---|
| User stories | Direct trigger signals for screens ("As a user, I can reset my password" → at least 2 screens) |
| Jobs-to-be-done | Reveals the *why* behind screens; helps de-duplicate overlapping screens |
| Entity-relationship diagram | Each entity implies list + detail screens; relationships imply association screens |
| User journey maps | Reveals transitional screens that fall between features (confirmation pages, waiting states) |
| Competitor analysis | Establishes conventions users expect; prevents reinventing screen patterns that already work |
| Analytics / support data | Shows which paths users actually take (for redesigns); reveals where screens are missing |
| Technical constraints | Affects whether something is a screen or a system-handled flow (e.g., OAuth redirects) |

---

## Research Area B: Sitemap / Screen Map Formats

### Format 1: Traditional XML Sitemap (web SEO)

The XML sitemap (sitemaps.org protocol) is **not** a screen inventory tool. It is a machine-readable file submitted to search engines.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2024-01-15</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
```

Captures: URL, last modified date, change frequency, relative priority.
Does NOT capture: screen name, purpose, design status, component info, auth requirements.
Relationship to screen inventory: Every public screen should eventually have a URL in the XML sitemap, but the XML sitemap is a subset (auth-gated screens are excluded) and contains none of the planning metadata.

### Format 2: UX Sitemap / Visual Sitemap (boxes and arrows)

The UX sitemap is the primary planning artefact for IA. It is a hierarchical diagram where each node represents a screen.

**Node fields (minimum):**
- Screen name (human-readable label)
- Screen ID (e.g., `2.1.3` or `AUTH-03`)
- Hierarchy level (depth in the tree)
- Connection type (navigation arrow, conditional arrow, back arrow)

**Node fields (extended):**
- Screen description (1–2 sentences of purpose)
- Route / URL path
- Design status (colour-coded)
- Platform (web / iOS / Android)
- Auth requirement (public / auth-required / admin-only)
- Notes / annotations

**Common tools:** Figma/FigJam, Miro, Whimsical, Lucidchart, Slickplan, OmniGraffle, Overflow

**Conventions:**
- Colour coding by section or status
- Dashed lines for conditional/alternative paths
- Double borders for modal/overlay screens (they don't sit in the hierarchy like full screens)
- Numbered levels (1.0, 1.1, 1.1.1) to reflect depth

### Format 3: Screen inventory spreadsheet

The spreadsheet format is the operational backbone for large projects. It holds metadata that the visual diagram cannot.

**Complete column set:**

| Column | Description | Example |
|---|---|---|
| `ID` | Unique alphanumeric identifier | `PROJ-04`, `2.1.3`, `AUTH-02` |
| `Screen Name` | Human-readable label | "Forgot Password" |
| `Route / URL Path` | The URL slug or named route | `/auth/forgot-password` |
| `Hierarchy Level` | Depth: L1 (top nav), L2 (sub-nav), L3 (modal/overlay) | L2 |
| `Parent Screen` | The screen this is navigated from | "Login" (AUTH-01) |
| `Section / Group` | Logical grouping (Auth, Billing, Settings) | Auth |
| `Platform` | Web, iOS, Android, All | Web + iOS |
| `Auth Requirement` | Public / Authenticated / Role-restricted | Public |
| `Role(s)` | Which user roles can access | All |
| `Description` | Purpose of this screen in 1–3 sentences | "Allows unauthenticated users to request a password reset email" |
| `Primary User Goal` | The JTBD or user story this screen serves | "Regain access to my account after forgetting my password" |
| `Key Interactions` | Main actions available on this screen | "Enter email, submit form, link to login" |
| `Entry Points` | How users reach this screen | "Login page 'Forgot password?' link, session-expired redirect" |
| `Exit Points` | Where users go after this screen | "Check Your Email confirmation screen" |
| `Design Status` | Backlog / In Design / Ready for Dev / In Dev / QA / Shipped | In Design |
| `Dev Status` | Not Started / In Dev / Staging / Shipped / Deprecated | Not Started |
| `v1 / v2` | Whether this screen is in-scope for v1 or deferred | v1 |
| `Priority` | P1 (must-have) / P2 (should-have) / P3 (nice-to-have) | P1 |
| `Figma Link` | Direct link to the design frame | [url] |
| `Notes / Dependencies` | Edge cases, blockers, tech constraints | "Token expires after 24h; expired token variant needed" |
| `Exclusion Reason` | If deliberately excluded, why | — |
| `Owner` | Designer or PM responsible | @alice |
| `Last Updated` | Date of last change to this row | 2024-03-10 |

**Minimum viable set** (for a lightweight planning doc):

`ID | Screen Name | Route | Platform | Auth Requirement | Design Status | Notes`

### Format 4: Figma / FigJam page map

In Figma, screens are typically organised as:
- **Pages** = product areas or platform (e.g., "iOS Screens", "Web — Auth", "Web — Dashboard")
- **Frames** = individual screens (each named after the screen)
- **Sections** (Figma 2023+) = groupings within a page by feature or user flow

FigJam sitemaps use sticky notes or rectangles connected by arrows. Groups are indicated by background colour. Numbers or labels indicate hierarchy.

Naming conventions in professional Figma files:
```
[Platform] / [Section] / [Screen Name] / [State]
iOS / Auth / Login / Default
iOS / Auth / Login / Error — Wrong Password
Web / Dashboard / Projects / Empty State
```

### Format 5: Linear / Jira epic → story hierarchy

Product management tools often serve as a de-facto screen inventory:
- **Epic** = a feature area or screen group (e.g., "Authentication", "Billing")
- **Story** = an individual screen or screen state (e.g., "Login screen", "Forgot password flow")
- **Sub-task** = a specific design or engineering task for that screen

This format lacks visual hierarchy but integrates with engineering workflow. Teams often cross-reference it with the spreadsheet or Figma sitemap.

### Format 6: Markdown-based screen maps

Used in documentation-driven teams (open-source projects, developer tools, monorepos). Stored alongside code in the repository. Format typically looks like:

```markdown
# Screen Inventory — [Product Name]

## Auth

| ID | Screen | Route | Status | Notes |
|----|--------|-------|--------|-------|
| AUTH-01 | Login | `/login` | Shipped | Supports Google OAuth |
| AUTH-02 | Register | `/register` | Shipped | Email + password only |
| AUTH-03 | Forgot Password | `/forgot-password` | Shipped | |
| AUTH-04 | Reset Password | `/reset-password?token=` | Shipped | Token expires 24h |
| AUTH-05 | Email Verification Pending | `/verify-email` | Shipped | |
| AUTH-06 | Accept Invitation | `/invite/accept?token=` | In Dev | |
| AUTH-07 | Expired Invitation | `/invite/expired` | Backlog | |

## Dashboard

| ID | Screen | Route | Status | Notes |
|----|--------|-------|--------|-------|
| DASH-01 | Dashboard (data loaded) | `/dashboard` | Shipped | |
| DASH-02 | Dashboard (empty — first run) | `/dashboard` | In Design | Conditional render |
```

Projects that use this format: documentation-heavy SaaS tools, design systems with a companion `screens.md` or `routes.md`, and codebases following Architecture Decision Records (ADR) conventions.

---

## Research Area C: Signals That Imply Screens

The following is a comprehensive catalogue of signals in a product brief/spec and the screens they imply. Each entry follows: **[Signal in the brief] → [screens implied]**.

---

### Auth signals

| Signal | Screens implied |
|---|---|
| "Users can sign up" | Registration screen; Email verification pending/confirmation screen |
| "Users can log in" | Login screen |
| "Users can log in with Google/GitHub/Apple" | OAuth callback/redirect handler (may be silent, but needs error handling); Account linking screen (if social + email accounts can merge) |
| "Users can reset their password" | Forgot password screen; "Check your email" confirmation screen; Reset password screen (token-based); Password changed confirmation (or redirect) |
| "Users must verify their email" | Email verification pending screen; Email verified success screen; Expired/invalid verification link screen |
| "2FA / MFA is supported" | 2FA setup screen (choose method); 2FA verify screen (enter code at login); 2FA recovery codes screen; Backup code entry screen; 2FA disable confirmation screen |
| "SSO / SAML is supported" | SSO login entry screen; SAML callback handler; SSO error screen (misconfigured, domain not found) |
| "Users can be invited" | Accept invitation screen (set password / join); Invitation already accepted screen; Expired invitation screen; "Wrong account logged in" collision screen |
| "Sessions expire" | Session expired modal overlay OR full session expired screen with redirect-back-to-destination |
| "Users can log out" | (Usually not a screen, but: ) Logged out confirmation screen if the product uses it; Multi-device logout confirmation |
| "Account deletion is supported" | Delete account confirmation screen; Account deleted / goodbye screen |
| "Users can be suspended / banned" | Account suspended screen (shown on login attempt); Account banned screen |
| "Passkeys / biometrics are supported" | Passkey registration screen; Passkey sign-in prompt |

---

### Payment and billing signals

| Signal | Screens implied |
|---|---|
| "Users pay monthly or annually" | Pricing / plan selection screen; Checkout / payment screen; Subscription confirmation screen; Billing settings screen (manage subscription); Plan change (upgrade/downgrade) confirmation screen |
| "Credit card is required" | Add payment method screen; Edit payment method screen; Payment method list screen |
| "Users receive invoices" | Invoice history / billing history screen; Invoice detail / download screen |
| "Free trial is offered" | Trial started / welcome screen; Trial expiring warning (can be a banner, but sometimes a modal/screen); Trial ended / upgrade required gate screen |
| "Users can cancel" | Cancel subscription flow screen; Cancellation confirmation screen; Reactivation screen |
| "Payment can fail" | Payment failed / card declined screen (or in-app notification leading to this screen); Update payment method prompt screen |
| "Usage-based billing / metered plan" | Usage dashboard screen; Usage limit approaching warning screen; Usage limit reached / blocked screen |
| "Promo codes / coupons are supported" | Promo code entry (usually part of checkout, but may be standalone redemption screen) |
| "Refunds are supported" | (Admin-side) Refund processing screen; (User-side) Refund request screen or confirmation |
| "Tax receipts / VAT invoices" | Tax settings screen (input VAT number, company details); Invoice detail with tax breakdown |
| "Enterprise / custom pricing" | Contact sales screen; Quote request screen |

---

### Collaboration and team signals

| Signal | Screens implied |
|---|---|
| "Users can invite teammates" | Invite members screen; Pending invitations list (admin view); Invitation sent confirmation |
| "Teams / organisations exist" | Team/org settings screen; Team member list screen; Member role management screen; Remove member confirmation screen |
| "Roles and permissions exist" | Role assignment screen; Permissions overview screen (what each role can do) |
| "Users can transfer ownership" | Transfer ownership confirmation screen |
| "Real-time collaboration is supported" | Presence indicators (component-level, not a screen), but: Collaboration conflict / version mismatch screen |
| "Comments or @mentions" | Notification / mentions inbox screen; Comment thread view (may be part of content screen) |
| "Activity feed / audit trail" | Activity / history screen (team-level or item-level) |
| "Guest access / view-only links" | Guest/viewer access landing screen; Link sharing settings screen |
| "Organisations can have multiple workspaces" | Workspace switcher screen; Create workspace screen; Workspace settings screen |
| "Impersonation / 'view as' for support" | (Admin-only) Impersonation mode banner + exit impersonation control; Impersonation confirmation screen |

---

### Content creation signals

| Signal | Screens implied |
|---|---|
| "Users can create [items]" | Create item screen (form or blank canvas); Item saved / created confirmation (or redirect to item) |
| "Users can upload files / media" | Media picker / file upload screen (mobile: media library picker); Upload progress screen or modal; Upload error screen |
| "Users can edit [items]" | Edit screen (may be same route as detail with edit mode, or separate `/edit` route) |
| "Users can delete [items]" | Delete confirmation dialog (state) or screen; Deleted / undo confirmation |
| "Drafts are supported" | Drafts list screen; Draft recovery screen (after session expiry or crash) |
| "Publishing / approval workflow" | Submit for review screen; Review queue screen (reviewer role); Approve/reject confirmation screen; Published confirmation screen |
| "Templates are supported" | Template library / gallery screen; Template detail / preview screen; Create from template screen |
| "Versioning / revision history" | Version history screen; Version diff / compare screen; Restore version confirmation screen |
| "Export is supported" | Export settings / format picker screen; Export progress screen; Export ready / download screen |
| "Search is supported" | Search results screen; No results / empty search screen; Search with filters screen |
| "Content can be organised into folders/collections" | Folder / collection list screen; Folder contents screen; Move item screen |

---

### Notification signals

| Signal | Screens implied |
|---|---|
| "Users receive in-app notifications" | Notifications inbox / centre screen; Notification detail screen (if notifications are actionable) |
| "Users can configure notification preferences" | Notification settings screen (per channel: email, push, SMS, in-app) |
| "Users receive email notifications" | (Not a UI screen, but:) Email preference management screen (often part of notification settings) |
| "Push notifications are sent (mobile)" | Push notification permission primer screen; Push notification settings screen |
| "Users receive SMS alerts" | Phone number entry/verification screen; SMS notification settings screen |
| "Digest / summary emails exist" | Digest frequency settings screen |
| "Webhooks are supported" | Webhook endpoint management screen; Webhook event log screen; Webhook test screen |

---

### Mobile-specific signals

| Signal | Screens implied |
|---|---|
| "Camera access is needed" | Camera permission primer screen (pre-permission education); Camera capture screen; Photo preview / confirm screen |
| "Location is used" | Location permission primer screen; Location denied / fallback screen |
| "Push notifications are sent" | Push permission primer screen; Notification settings screen |
| "Contacts access is needed" | Contacts permission primer screen |
| "Users can share content from the app" | Share sheet integration (system-level, but may need a share preview screen); Share target selection (if custom sharing screen) |
| "Deep links are used" | Deep link error screen (link expired/invalid); Universal link fallback screen (web → app redirect) |
| "Share extension is supported" | Share extension mini-UI (runs in host app context — separate UI module) |
| "Widget is supported" | Widget configuration screen (in-app); Widget preview screen |
| "App Clip / Instant App" | App Clip entry screen (lightweight onboarding in clip context) |
| "Offline mode is supported" | Offline mode indicator (component); Offline / no connection screen; Sync in progress screen |
| "Biometric login (Face ID / fingerprint)" | Biometric auth setup screen; Biometric auth prompt (system-level, but: ) Biometric failed / fallback screen |

---

### Admin and moderation signals

| Signal | Screens implied |
|---|---|
| "An admin can manage users" | User list / management screen; User detail screen (admin view); User edit screen; Suspend/ban user confirmation screen; Impersonate user screen |
| "Content moderation is needed" | Content moderation queue screen; Content detail screen (review context); Approve / reject action confirmation |
| "An admin dashboard exists" | Admin dashboard / overview screen |
| "Feature flags / toggles exist" | Feature flag management screen |
| "Audit logs are required" | Audit log / event log screen; Audit log filter / search screen |
| "System health monitoring" | System status / health screen (admin-only); Maintenance mode management screen |
| "Announcements / broadcast messages" | Announcement composer screen (admin); Announcement list (admin); Announcement banner (user-facing — component, not screen) |
| "Support / ticketing integration" | Help / support screen (user-facing); Ticket submission screen; Ticket history screen |
| "Rate limiting or abuse detection" | Rate limit hit screen (user-facing error); Abuse report screen (user reports other users) |

---

### API and developer signals

| Signal | Screens implied |
|---|---|
| "API access is provided" | API keys / credentials screen; Create API key screen; API key detail (permissions, last used); Revoke API key confirmation screen |
| "Webhooks are configurable" | Webhook list screen; Create/edit webhook screen; Webhook delivery log screen; Webhook test screen |
| "OAuth apps can be created" | OAuth app list screen; Create OAuth app screen; OAuth app detail / settings screen; OAuth authorization screen (the consent screen shown to users) |
| "Developer documentation is available" | Developer docs section (may be external, but: ) Interactive API explorer / sandbox screen |
| "SDK or CLI is downloadable" | Downloads / SDK screen |
| "Zapier / integration marketplace" | Integrations / marketplace screen; Integration detail screen; Connected integration management screen; OAuth connect flow screen |

---

### Onboarding signals

| Signal | Screens implied |
|---|---|
| "New users are onboarded" | Welcome / onboarding start screen; Onboarding step N (profile setup, preferences, tour); Onboarding complete / get started screen |
| "Users set up their profile" | Profile setup screen (name, avatar, etc.) |
| "Users choose a plan at signup" | Plan selection screen (during onboarding) |
| "Users invite their team during onboarding" | Invite team screen (onboarding step); Skip / do later option (component, not screen) |
| "A product tour is offered" | Product tour overlay / coach marks (component-level, not a screen, but requires design) |
| "Users can skip onboarding" | Skipped onboarding → first empty dashboard state (requires distinct design from onboarding-complete) |
| "Onboarding checklist / progress tracker" | Onboarding checklist widget (component on dashboard); Checklist item detail / help screen |
| "Role-specific onboarding" | Separate onboarding flow per role (each role's path may have different screens) |

---

### Settings signals

| Signal | Screens implied |
|---|---|
| "Users can update their profile" | Profile settings screen |
| "Users can change their email" | Change email screen; Confirm new email screen (email verification step) |
| "Users can change their password" | Change password screen |
| "Users can manage connected accounts" | Connected accounts / integrations screen (social logins, OAuth apps) |
| "Privacy settings exist" | Privacy settings screen |
| "Data export is available" | Export my data screen; Export in progress / download ready screen |
| "Account deletion is available" | Delete account screen; Deletion confirmation screen; Grace period / account recovery screen |
| "Language / locale preferences" | Language settings screen |
| "Theme / appearance preferences" | Appearance settings screen |
| "Keyboard shortcuts reference" | Keyboard shortcuts screen / modal |
| "API access is self-service" | API settings screen (sub-section of settings) |
| "Team / org settings are separate from personal settings" | Personal settings section; Team/org settings section (separate screens or top-level tab split) |

---

## Research Area D: Common Screen Planning Mistakes

### Screens that are almost always missed

These are systematically overlooked in screen inventories because they appear only in edge-case or error flows, which are considered "later" and then never adequately designed.

**Auth and identity edge cases:**
- Email verification pending screen ("Check your inbox")
- Email verification expired / link already used screen
- Verification resend confirmation screen
- Invitation acceptance screen (token-valid path)
- Invitation expired / invalid token screen (always missed)
- Invitation → account already exists collision screen ("You have an account, want to log in instead?")
- 2FA setup screen (teams plan the 2FA *login prompt* but forget the *setup flow*)
- 2FA recovery code display screen (shown once at setup time)
- 2FA recovery code entry screen (when device is lost)
- Password changed confirmation screen
- Account suspended screen (shown on login, not just in email)
- Account deleted / goodbye screen
- Session expired re-auth overlay (not just a redirect — the overlay that lets users re-authenticate without losing work)

**System and infrastructure states:**
- 404 Not Found page
- 403 Forbidden / access denied page
- 500 Internal Server Error page
- 503 Service Unavailable / maintenance page
- Rate limit reached page
- Offline / no connection screen (PWA, mobile)
- Update required screen (mobile apps, desktop apps)

**Billing and plan gates:**
- Trial expired / upgrade required gate (the wall screen, not just an email)
- Plan limit reached gate (e.g., "You've reached 3/3 projects on the free plan")
- Payment failed / card declined screen
- Account downgraded / features lost notification screen

**Operational flows:**
- Empty states for *every* list screen (a list screen with data and a list screen with no data are two different designs; both must be planned)
- First-run / onboarding variant of the dashboard (different from the data-loaded dashboard)
- "You need to verify your email to do this" gate (users who skipped verification and hit a feature gate)
- Accept terms of service / privacy policy update screen (required when T&C change)
- "New feature / what's new" announcement screen or modal

---

### Screens that are over-built when they should be states

The opposite error — promoting a state to a full screen — creates unnecessary routing complexity, breaks back-button expectations, and bloats the navigation stack.

**Things that are almost always states, not screens:**
- Loading / skeleton state (this is a render state of the page, not a destination)
- Empty state (same route, different content fill — no separate URL)
- Hover state (component-level, never a screen)
- Error state for a failed fetch (same route, different render — not a navigation target)
- Filter / sort panel (a drawer or inline panel, not a full page navigation)
- Delete confirmation dialog (a modal overlay, not a pushed screen on web)
- Success confirmation for small actions ("Saved!" toast — never a screen)
- Dropdown menus, context menus (component-level)
- Tab switching within a section (unless tabs have distinct routes, this is state)

**The specific trap: multi-step forms**

Teams often make multi-step forms into separate screens when they should be one screen with step state. The right decision depends on:
- Length/complexity of each step (more complex = more justification for separate screens)
- Whether users need to navigate between steps freely (non-linear = URL-per-step helps)
- Whether the browser Back button should go to the previous step (yes → URL-per-step)
- Mobile vs web (mobile apps routinely push form steps as separate screens; web can use inline state)

---

### The dashboard problem

One of the most systematically under-designed areas in screen inventories.

Teams plan: `Dashboard`

They should plan:
- `Dashboard — loading state` (skeleton)
- `Dashboard — first-run / empty state` (zero data, user has just signed up — CTA to add first item)
- `Dashboard — data loaded state` (normal state with real data)
- `Dashboard — error state` (data fetch failed)
- `Dashboard — admin view` (if admins see different widgets)
- `Dashboard — mobile layout` (may require distinct planning from desktop)
- `Dashboard — empty after filtering` (filtered view with no results)

Each of these is a different design. Teams discover them in development and scramble to design them under deadline.

---

### Platform differences that trip up screen planning

| Pattern | Web | iOS | Android |
|---|---|---|---|
| Confirmation dialogs | Modal overlay (state, no nav) | UIAlertController (system sheet — no custom design needed) | MaterialAlertDialog (system-managed) |
| Master-detail navigation | Side panel (state) or separate page | Push onto navigation stack (screen) | Activity push (screen) or NavigationComponent |
| Bottom sheet / action sheet | Custom modal sheet | UIActionSheet (system) or custom | ModalBottomSheet (Material) |
| Permissions | No prompt — just works (browser media APIs have their own flow) | One-time system dialog (no custom design, but need primer screen) | Runtime dialog (can be re-triggered; needs rationale design) |
| File picker | Browser file input (no custom screen needed) | UIImagePickerController / PHPickerViewController (system) | Intent-based picker (system) |
| Share | Web Share API (system sheet on mobile browser) | UIActivityViewController (system sheet) | Intent chooser (system) |
| App update | No concept (web is always current) | App Store update banner (no in-app screen, but: ) Update required gate if API version is deprecated | In-app update API: flexible (banner) or immediate (forced screen) |
| Deep link handling | URL-based routing (standard) | Universal Links + URL Schemes — may need a redirect/loading screen | App Links + Intent filters — may need loading/redirect screen |
| Onboarding | Multi-page or single page (design freedom) | Prefer interactive/contextual (HIG); skip must be available | Structured flows with steppers/progress (Material guidelines) |

---

### Screens discovered late causing rework

Ranked by frequency and rework severity:

1. **Account suspended / banned screen** — discovered when ops says "we need to be able to suspend users"
2. **Plan limit reached / upgrade gate** — discovered when the product actually goes freemium and someone realises there's no wall
3. **Email verification gate** — "What happens if they access feature X before verifying their email?" — often discovered in QA
4. **Invitation flow edge cases** — expired tokens, wrong account — always late discoveries
5. **Session expired overlay** — teams implement a redirect to login; then users complain about losing form data; overlay gets retrofitted
6. **Maintenance / 503 page** — discovered during the first production incident
7. **Role-specific empty states** — "The admin sees no users; the regular user sees no projects. These need different copy and CTAs."
8. **Data export / GDPR download screen** — discovered when legal raises compliance requirements
9. **Print view / PDF export** — discovered when enterprise customers ask for it
10. **Webhook failure / retry screen** — discovered when developers start integrating

---

### Multi-role screen split problems

The hardest question in multi-role IA: **is this one screen with conditional rendering, or two separate screens?**

**Rule**: Use a single screen with conditional rendering when:
- The route/URL is the same for both roles
- The majority of the screen's content is shared (>60%)
- The difference is in what actions are available, not what data is shown
- The role difference is about *capability* not *content domain*

**Rule**: Create separate screens (or separate route namespaces) when:
- The URL should differ (e.g., `/admin/users` vs `/account`)
- The majority of content differs between roles
- The layout or navigation structure is fundamentally different
- The role difference is about a completely different *job to be done*

**The ambiguous middle ground** — one dashboard URL, two very different experiences:
Best practice is a **role-aware component architecture**: the route is the same, but the page component reads the user's role and renders completely different child component trees. Document this in the screen inventory as a single screen entry with a "role variants" column listing both designs.

---

## Research Area E: Platform-Specific Screen Conventions

### iOS / iPadOS

**LaunchScreen (Splash)**
- Implemented as a static storyboard (`LaunchScreen.storyboard`), not a view controller
- Apple HIG strictly forbids logos, marketing copy, or animations on the launch screen
- Must mirror the app's initial UI layout (placeholder nav bar, tab bar, blank content areas) so the app feels instant
- The launch screen is NOT a screen in the navigable sense — it cannot receive events or run code
- Implication for screen inventory: list it as `iOS-SYS-01 Launch Screen` with note "static storyboard; no interaction; no data"

**Permission prompts**
- iOS grants **one single irreversible chance** to show a system permission dialog per permission type
- If user taps "Don't Allow", the app can NEVER trigger the system dialog again — user must go to Settings manually
- **Primer screens are therefore mandatory**, not optional. The primer screen is a custom in-app screen shown *before* `requestAuthorization()` is called, explaining why the permission matters and what the user gains
- Required primer screens for each permission type: Camera primer, Microphone primer, Location primer (with why location is needed and which accuracy level), Contacts primer, Photos primer, Notifications primer (shown at the right contextual moment, not on first launch)
- The permission dialog itself is system-controlled — no custom design — but the primer screen IS a full custom UI screen that belongs in the inventory

**Share Extension**
- A separate app target that runs in the context of the host app (Safari, Photos, etc.)
- Has its own UI: at minimum, a share sheet with a compose area and a post button
- Needs its own login/auth check (the extension has a separate process from the main app)
- Must be planned as a separate mini screen-set: `Share Extension — Compose`, `Share Extension — Auth Required` (redirects to main app), `Share Extension — Success`

**Widget configuration screen**
- Widgets added in iOS 14+ can have a configuration UI called an Intent configuration
- The configuration screen is a separate `INUIEditIntentViewController` that appears when the user long-presses the widget and taps "Edit Widget"
- Must be listed in the screen inventory: `Widget — Configure [Widget Name]`

**iPad split-view**
- iPadOS allows two apps side by side; your app needs to handle compact, regular, and large size classes
- Many screens that are separate on iPhone collapse to a single master-detail view on iPad
- Implication: document screen pairs that merge on iPad: `[iPhone] Project List + Project Detail → [iPad] Split View: Projects`

**App Clip**
- A lightweight version of the app that can be launched from NFC tags, QR codes, Safari, Maps, Messages
- Has a maximum binary size limit and a constrained feature set
- Needs its own screen-set: `App Clip — Entry Point / Mini Onboarding`, `App Clip — Core Action Screen`, `App Clip — Full App CTA`

---

### Android

**SplashScreen API (Android 12+)**
- System-managed via the `SplashScreen` API — not a traditional Activity
- Anatomy: window background + optional branding image at bottom + centered app icon (static vector or animated up to 1,000ms)
- Developers should NOT manually extend the splash screen (it's an anti-pattern)
- In the screen inventory: `Android-SYS-01 Splash Screen` — note "system-managed via SplashScreen API"

**Permission rationale dialogs**
- Android allows the app to show rationale (`shouldShowRequestPermissionRationale()`) between the first denial and a "Don't ask again" lockout
- Design pattern: a contextual bottom sheet or dialog explaining why the permission is needed, shown *after* first denial, before triggering the system prompt again
- These are custom-designed UI states: `Permission Rationale — Camera`, `Permission Rationale — Location`, etc.
- After "Don't ask again": app must redirect user to system Settings — needs a screen/dialog with a "Open Settings" button

**Notification channel setup**
- Android 8+ requires notification channels to be created in code, but users manage them in system Settings
- Some apps have an in-app notification settings screen that links to or explains channel settings
- Not a system screen, but a custom one: `Notification Channel Explanation Screen`

**In-app review prompt (Play Store)**
- Google Play In-App Review API allows apps to prompt users to leave a review without leaving the app
- The review sheet is system-controlled — no custom design — but the app decides *when* to trigger it
- Plan the trigger logic (not a screen), but note in the inventory where it fires: `After completing [milestone action]`

**Back stack and deep link handling**
- Android deep links can drop users into the middle of the app without the normal back stack
- Must plan: what happens when a deep link opens a screen and the user presses Back? Options: synthetic back stack, go to home, exit app
- For each deep-linkable screen, document the "Back pressed" behavior

**App shortcuts (long-press home screen)**
- Static shortcuts: defined in XML, appear on long-press immediately
- Dynamic shortcuts: added in code based on user behavior
- Each shortcut destination must be a screen in the inventory (or confirm it maps to an existing one)

---

### Web

**Error pages**
Essential screens that must be explicitly designed (not left to framework defaults):

| Screen | Route | When shown |
|---|---|---|
| 404 Not Found | `/404` | URL doesn't match any route |
| 403 Forbidden | `/403` | User lacks permission for this resource |
| 500 Internal Server Error | `/500` | Unhandled server error |
| 503 Service Unavailable | `/503` or `/maintenance` | Planned maintenance or overload |
| Rate limit exceeded | — | Too many requests (429) |

**Non-screen routes that affect planning**
These are not screens but are URL routes that must be listed in the route inventory:
- `GET /robots.txt` — search engine crawling rules (not a screen)
- `GET /sitemap.xml` — SEO sitemap (not a screen)
- `GET /health` — health check endpoint (not a screen)
- `GET /.well-known/apple-app-site-association` — Universal Links config (not a screen)
- `GET /manifest.json` — PWA manifest (not a screen)

**OpenGraph / social sharing**
Not a screen, but affects route metadata. Every public screen should have its own OG title, description, and image. Some products have a dynamic OG image route: `GET /og?title=X&description=Y` — this is a route that generates images, not a user-navigable screen.

**Print view**
Some enterprise or document-focused products have print-optimised views. These may be separate routes (`/invoice/:id/print`) or CSS print stylesheets on the same route. If a separate route exists, it belongs in the inventory.

**PWA offline fallback**
Progressive Web Apps register a service worker that can serve a fallback page when offline. This is a real screen: `Offline Fallback Page` — appears when the user is offline and navigates to a URL not in the cache. Must be designed; often forgotten.

---

### Desktop (Electron / Tauri)

**Onboarding / welcome window**
Desktop apps often have a first-run experience that is a separate window, not a screen within the main window. Must be in the inventory: `Welcome / Setup Window`.

**Update available notification**
- Soft update: a banner or toast in the app UI with "Update available — Restart to update" CTA
- Forced update: a blocking modal or separate window that prevents use until updated
- Both require design: `Update Available Dialog`, `Update Required Gate Window`

**Crash reporter**
When the app crashes and restarts, some desktop apps show a crash report dialog: "The app quit unexpectedly. Send crash report?" This is a system-adjacent screen that needs design: `Crash Reporter Dialog`.

**System tray menu**
Not a screen, but a menu that appears on right-click of the system tray icon. Each menu item must be catalogued: quick actions, open main window, quit, status indicator. Plan the tray menu as part of the screen inventory under a `System Tray` section.

**Preferences window**
macOS and Windows conventions expect a dedicated Preferences/Settings window (Cmd+, on Mac). This is a separate window, not a screen within the main app window, and may have its own tab structure.

**Multiple window support**
Some desktop apps support opening multiple windows (documents, panels). Each window type must be inventoried: `Main Window`, `Document Window`, `Quick Look / Preview Window`, `Settings Window`.

---

## Research Area F: Multi-Role / Multi-Persona IA

### When does a role difference create a separate screen vs conditional rendering?

**Separate screen (separate route)** when:
- The URL/route differs by role (e.g., `/admin/*` vs `/app/*`)
- The navigation structure is fundamentally different (admin has a different sidebar/nav)
- The primary job-to-be-done is entirely different (admin's goal is oversight; user's goal is task execution)
- The page content overlap is under ~40%
- The role needs to be reflected in audit logs or analytics separately

**Conditional rendering on the same screen** when:
- The URL is identical for all roles
- The majority of content (>60%) is shared
- The difference is in what actions/buttons are available (hide/show permissions)
- The role difference is about capability on the same content (e.g., user can view, admin can edit)

**Hybrid approach** (most common in real products):
- Shared base route and layout
- Role-specific tabs, sections, or action sets rendered conditionally
- Documented in the screen inventory as one entry with a "role variants" note and separate Figma frames per role

### Role-specific nav documentation

In the screen inventory, role-specific navigation items are best documented as:
1. A single nav structure table with a "Visible to" column per item
2. Separate "Nav — [Role]" sections in the sitemap diagram (colour-coded by role)
3. A role matrix: rows = nav items, columns = roles, cells = visible/hidden/modified

### Operator + end-user products (e.g., Shopify merchant vs buyer)

These products require fully separate screen inventories with their own hierarchies:

**Merchant/Operator portal:**
- `/admin/*` namespace
- Dense data tables, management workflows, settings
- Different design system tone (utilitarian, information-dense)
- Separate navigation, separate auth, separate session

**End-user / buyer portal:**
- `/app/*` or root namespace
- Consumer-grade UX, simplified navigation
- Optimised for conversion or task completion
- Separate auth (may share identity provider, but separate session context)

The two inventories are cross-referenced at integration points: "Merchant configures X → End-user sees Y on screen Z."

### Admin portal IA vs consumer app IA

Admin portals have distinct IA conventions:
- **Global search** that spans all entities (users, orders, content) — a screen often forgotten
- **Entity detail + action panel** pattern: user detail + "Suspend / Reset Password / Impersonate" actions sidebar
- **Audit log / event stream** screen: global or per-entity
- **Bulk action confirmation screen**: "You are about to delete 1,247 records. Are you sure?"
- **Data export** at the admin level: different from user-level export
- **System configuration screens**: feature flags, rate limits, email templates, global settings

### The "view as" / impersonation pattern

When admins can impersonate users (for support), the following screens are required:
- **Admin-side**: Impersonate User trigger (button on user detail screen, plus confirmation modal)
- **Active impersonation indicator**: A persistent banner in the impersonated user's UI: "You are viewing as [User Name]. [Exit impersonation]"
- **Impersonation session boundary**: The impersonated user's screens should not allow destructive admin-only actions
- **Exit impersonation**: Confirmation or automatic redirect back to admin context
- **Audit log entry**: Each impersonation event must be logged — this is a backend requirement but affects the admin's audit log screen design

Inventory entries:
- `Admin — Impersonate User Confirmation` (modal/screen)
- `Impersonation Active Banner` (persistent component, not a screen, but requires design)
- `Admin — Impersonation Audit Log` (screen)

### Documenting role-specific nav in a screen inventory

Recommended approach: add a `Roles` column to the inventory spreadsheet and use a nav visibility matrix as an appendix.

```markdown
## Navigation Visibility Matrix

| Nav Item         | Guest | User | Admin | Super Admin |
|------------------|-------|------|-------|-------------|
| Dashboard        | ✗     | ✓    | ✓     | ✓           |
| Projects         | ✗     | ✓    | ✓     | ✓           |
| Team Members     | ✗     | ✓    | ✓     | ✓           |
| Billing          | ✗     | ✓    | ✓     | ✓           |
| Admin Panel      | ✗     | ✗    | ✓     | ✓           |
| System Settings  | ✗     | ✗    | ✗     | ✓           |
```

---

## Research Area G: Versioning and Evolution of Screen Inventories

### Screen lifecycle status model

Each screen in the inventory should carry a lifecycle status. The recommended status vocabulary (compatible with Linear, Jira, and Notion):

**Design lifecycle:**
- `Identified` — the screen has been named and is known to need design; no design work started
- `Backlog` — prioritised for a future sprint but not yet actively designed
- `In Design` — a designer is actively working on wireframes or high-fidelity mockups
- `Design Review` — design is complete and in review with stakeholders
- `Design Approved` — ready to hand off to engineering

**Engineering lifecycle:**
- `Dev Backlog` — design approved; waiting for engineering sprint
- `In Development` — engineering is actively implementing
- `In QA` — implemented; in quality assurance testing
- `Staging` — deployed to staging environment
- `Shipped` — live in production

**Post-ship:**
- `Deprecated` — scheduled for removal; existing users may still see it
- `Removed` — no longer in the product; retained in the inventory for historical reference

**Special statuses:**
- `Deferred — v2` — intentionally out of scope for the current version; must be noted with reason
- `Blocked` — cannot proceed due to a dependency (note what the blocker is)
- `Cancelled` — will not be built; retained with a cancellation reason

### v1 vs v2 scope tracking

In the screen inventory, add a `Version` column:
- `v1` — in scope for the current release
- `v2` — deliberately deferred to the next major version
- `v3+` — longer-term backlog
- `Icebox` — no committed timeline

For `v2` and later entries, add a `Deferral Reason` column:
- Complexity too high for v1 timeline
- Dependency on a feature not yet built
- Insufficient user research to design confidently
- Not in the initial business model

This prevents deferred screens from being lost. The v2 backlog in the screen inventory feeds the v2 planning process directly.

### Recording deferral decisions

Each deferral should be recorded as a brief decision note, following the Architecture Decision Record (ADR) format:

```
Screen: 2FA Setup Flow
Decision: Defer to v2
Date: 2024-03-15
Reason: v1 targets a closed beta with known users; full 2FA is a compliance
        requirement for enterprise tier which launches in v2.
Revisit trigger: When first enterprise prospect signs LOI.
Owner: @alice
```

Storing these in a `deferred-screens.md` file alongside the main inventory prevents them from being forgotten.

### Triggers for a screen inventory review

A screen inventory review should be triggered by:
- **Major feature addition**: any new feature that adds more than 3 screens
- **Navigation restructure**: changes to global nav or primary routing
- **New user role or persona**: a new role may require new screens or change existing ones
- **Platform addition**: adding iOS to a web-only product (or vice versa) requires a new inventory section
- **Rebrand or design system update**: screens may be renamed, merged, or split
- **Quarterly planning cycle**: at the start of each quarter, review for status accuracy
- **Post-launch audit**: after a release, update all screen statuses based on what actually shipped
- **User research findings**: research that reveals users expect a screen that doesn't exist

### How design systems relate to screen inventories

Design systems (Storybook, Zeroheight, Supernova) are **component-level** documentation. Screen inventories are **screen-level** documentation. They are complementary and cross-reference each other.

**Integration points:**
- Each screen entry in the inventory references the components used (from the design system)
- Each component in the design system references the screens it appears on
- When a component is deprecated in the design system, check the screen inventory for all screens that use it — those screens need an update

**Storybook and screen inventories:**
- Storybook documents component states, not screen-level compositions
- Some teams add a "Pages" or "Screens" category in Storybook where full-page compositions are shown — this bridges the gap
- Chromatic (Storybook's visual testing tool) can run visual regression on screen-level compositions when configured

**Component lifecycle → screen lifecycle impact:**
- When a component moves from `Beta` to `Stable` in the design system, screens using it can be unblocked
- When a component is `Deprecated`, all screens using it must be updated — the screen inventory is the authoritative list of where the component is used

**Zeroheight / Supernova and screen inventories:**
- These tools document design tokens and components with usage guidelines
- Some teams embed screen inventory tables directly in these tools to create a single source of truth
- The screen inventory then links to the design system documentation for each component used on that screen

### Keeping the inventory accurate over time

Best practices for long-term accuracy:
1. **Assign ownership**: every screen has a named owner (designer or PM) responsible for keeping its entry current
2. **Link to code**: the inventory entry for a shipped screen should reference the actual component file and route definition in the codebase
3. **Automate what you can**: in route-file-based frameworks (Next.js, Expo Router), the route file structure can be automatically diffed against the inventory to catch missing or undocumented screens
4. **Review in sprint ceremonies**: during sprint planning, check if new stories require new screens to be added to the inventory; during sprint review, update statuses of completed screens
5. **Don't delete — archive**: never delete a deprecated screen from the inventory; mark it `Deprecated` with a date and reason; it's historical record and may be needed for audits or rollbacks
6. **Changelogs**: maintain a `CHANGELOG` section in the inventory document noting when screens were added, changed status, or deprecated

---

## Appendix: Minimum Viable Screen Inventory Format

For teams that want a lightweight, low-overhead screen inventory in a markdown file:

```markdown
# Screen Inventory

_Last updated: YYYY-MM-DD | v1 scope | [Platform: Web + iOS]_

## Legend
Status: `🔲 Backlog` | `🎨 In Design` | `🔨 In Dev` | `✅ Shipped` | `⏸ Deferred` | `❌ Cancelled`
Auth: `🌐 Public` | `🔒 Auth required` | `👑 Admin only`

---

## Auth

| ID | Screen | Route | Platform | Auth | Status | Notes |
|----|--------|-------|----------|------|--------|-------|
| AUTH-01 | Login | `/login` | Web+iOS | 🌐 | ✅ | |
| AUTH-02 | Register | `/register` | Web+iOS | 🌐 | ✅ | |
| AUTH-03 | Forgot Password | `/forgot-password` | Web | 🌐 | ✅ | |
| AUTH-04 | Check Your Email | `/check-email` | Web | 🌐 | ✅ | Post-forgot-password |
| AUTH-05 | Reset Password | `/reset-password` | Web | 🌐 | ✅ | Token in query param |
| AUTH-06 | Email Verification Pending | `/verify-email` | Web+iOS | 🔒 | ✅ | |
| AUTH-07 | Accept Invitation | `/invite/accept` | Web | 🌐 | 🔨 | |
| AUTH-08 | Expired Invitation | `/invite/expired` | Web | 🌐 | 🔲 | |
| AUTH-09 | 2FA Setup | `/settings/2fa/setup` | Web | 🔒 | ⏸ | Deferred to v2 |
| AUTH-10 | Session Expired Overlay | — | Web | 🔒 | 🎨 | Modal overlay, no route |

## Dashboard

| ID | Screen | Route | Platform | Auth | Status | Notes |
|----|--------|-------|----------|------|--------|-------|
| DASH-01 | Dashboard (data loaded) | `/dashboard` | Web+iOS | 🔒 | 🔨 | |
| DASH-02 | Dashboard (first run / empty) | `/dashboard` | Web+iOS | 🔒 | 🎨 | Conditional render |
```

This format is version-controllable, diff-able, and works in any project that uses a repository.
