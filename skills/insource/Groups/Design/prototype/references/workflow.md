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
- **No answer is not "skip":** if none exists, design the full palette (brand ramp, neutrals,
  semantic tones, both theme blocks) and state the choice in one line before scaffolding —
  see the Palette Law in [`zero-duplication.md`](zero-duplication.md).

### F. Data & Vocabulary
- Real domain vocabulary (never Lorem ipsum or "Item 1 / Item 2").
- Realistic data schemas or sample rows.

---

## 2. Step-by-Step Implementation Flow

1. **Pin Viewports & Topologies:** Single-app uses Topology A; multi-app uses Topology B (`shared/` + `apps/<app>/`). Frameless viewports always ([`viewport-frames.md`](viewport-frames.md)).
2. **Scaffold:** Copy base structure from `assets/starter/` (or multi-app layout). Copy `assets/dev-dock/devdock.js` into the project (`js/` or `shared/js/`), set `window.DevDockInit` (apps list in suites), and load it on every page — it is the project's only chrome component ([`prototype-dock.md`](prototype-dock.md)). Wire `package.json` scripts and route rewrites in `serve.mjs`.
3. **Derive States Before Building:** Walk interactive components through condition axes (data, provider, in-flight, viewer, time) and enumerate the complete state tree in `specs.js` before writing DOM code. Include `filled: { default: null }` for seeded stress tests.
4. **Build Pages & Components:** Thin HTML entries + JS modules building the DOM. Keep files under ~300 lines by splitting renderer and data concerns. The second use of any class string or markup block goes into a token, a `components.css` class, or a `ui.js` builder — never a paste ([`zero-duplication.md`](zero-duplication.md)).
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
- **Guards:** `node scripts/guards.mjs all <project-dir>` is clean (or accepted one-offs are noted); flip `--strict` once the baseline passes — a repeated class string, off-token hex, inline `<svg>` next to an icon helper, or inline handler is a finding, not a style choice.
- **Palette:** the dock's Theme tab shows live swatches for every color token; the list must be non-empty and cover both `[data-theme]` blocks. Any color in use that is not in that list is a defect (same rule `guards.mjs tokens` measures).
- **Chrome:** no page template renders a prototype-meta control — toggles, toolbars, pickers and app switchers are dock tabs or bare URL params; the product-content test: *would this control exist in the shipped product?*
- **States by URL, both widths:** every page's empty/zero-result/loading/error state is reachable cold by URL and is a designed surface — recognition + path (CTA), skeleton loading, never white space ([`state-surfaces.md`](state-surfaces.md)); screenshot each state at the narrowest and widest pinned viewport (dock Viewport tab reports drift).
- **Content fidelity:** no "TODO"/Lorem/"Item 1" anywhere; every region of every state carries full plausible product content — real domain vocabulary, named entities, realistic amounts and dates. Sparse default means *few real rows*, not a blank screen. Stranger test per screenshot: could this app be believed to exist?
- **Responsive:** each route holds at every pinned width from the questionnaire — no horizontal scroll, no clipped CTAs, action rows survive 390px; mobile surfaces are *viewed* in device-width previews (gallery iframe / emulation), never by asking the person to resize a window ([`viewport-frames.md`](viewport-frames.md)).
- **Visual regression:** when migrating or restyling existing screens, screenshot-compare each route against its pre-change render via the `parity` skill (`/parity`) before moving to the next page.
