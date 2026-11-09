# Prototype Workflow & Lifecycle

> **What this owns:** The step-by-step authoring workflow, questionnaire, and verification discipline for creating and extending prototype projects.

---

## 1. Pre-build Questionnaire (Never-Rush Law)

Group these questions into one concise message before writing any files. Skip a question only when the user's prompt already answers it unambiguously:

### A. Screen Inventory
- Which screens/pages should the prototype include? (Propose a complete set if unstated).
- For each screen: primary purpose and target persona.

### B. Viewport & Responsiveness
- Desktop only (1280×800, default for dashboards / backoffice).
- Mobile only (390×844, for native-app or PWA flows).
- Tablet (~768px).
- Multiple viewports (shared responsive file vs. separate surface variants via Topology B).

### C. App Scope & Topology
- Single standalone app (Topology A) or multi-role system suite (Topology B: admin + operator + client)? See [`multi-app-scope.md`](multi-app-scope.md).

### D. Libraries & Dependencies
- Default: **CDN libraries for everything** (Lucide icons, Chart.js, Day.js, etc.). Hand-rolling requires explicit user opt-out. See [`libraries.md`](libraries.md).

### E. Design Language & Tokens
- Existing design system, brand guide, or color palette to follow?
- Dark mode, light mode, or both?

### F. Data & Vocabulary
- Real domain vocabulary (never Lorem ipsum or "Item 1 / Item 2").
- Realistic data schemas or sample rows.

---

## 2. Step-by-Step Implementation Flow

1. **Pin Viewports & Topologies:** Single-app uses Topology A; multi-app uses Topology B (`shared/` + `apps/<app>/`). Frameless viewports always ([`viewport-frames.md`](viewport-frames.md)).
2. **Scaffold:** Copy base structure from `assets/starter/` (or multi-app layout). Wire `package.json` scripts and route rewrites in `serve.mjs`.
3. **Derive States Before Building:** Walk interactive components through condition axes (data, provider, in-flight, viewer, time) and enumerate the complete state tree in `specs.js` before writing DOM code. Include `filled: { default: null }` for seeded stress tests.
4. **Build Pages & Components:** Thin HTML entries + JS modules building the DOM. Keep files under ~300 lines by splitting renderer and data concerns.
5. **Wire URL States & Story Isolation:** Central helper in `_app.js`. Every testable component carries `data-story="<id>"` and `data-testid="<id>"` to support in-page isolation via `?story_id=`.
6. **Gallery & Stories Catalog:**
   - 2+ screens: Root `index.html` showcases live iframe cards with state preview chips ([`gallery-index.md`](gallery-index.md)). Max 3 columns (`repeat(auto-fit, minmax(320px, 1fr))`).
   - Component stories catalog: `index.stories.html` showcases pure-data component registry across all states ([`component-registry-stories.md`](component-registry-stories.md)).
7. **Verify & Deliver:** Run structural, state, and gallery checks.

---

## 3. Verification Checklist (Mandatory)

Do not mark done until every item passes:

- **Structural:** Dev command starts cleanly; all clean routes work on direct entry and refresh; HTML entries remain thin.
- **State by URL:** Every state reachable cold by URL; `?filled` and `?filled=<seed>` produce full seeded datasets; composed params preserve unrelated keys; invalid values fall back safely to defaults.
- **Gallery Quality:** At most 3 columns; no scrollbars visible inside preview iframes (`scrollbar-width: none; &::-webkit-scrollbar { display:none }`); state strip has chips for all derived states + `Filled`.
- **Component Stories:** `scripts/stories_check.mjs` passes without undeclared states or duplicate card traps.
