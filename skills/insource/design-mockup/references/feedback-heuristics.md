# Feedback Heuristics — Affordance → Expected Reaction

> **What this owns:** the lookup from a visual affordance to the component that correctly answers it, per platform, plus the two code patterns (`anchored dropdown`, `toast`) that `query-param-states.md` doesn't already cover. The order of operations for auditing a file — and the reuse-before-inventing rule that governs it — is [`dead-control-audit.md`](dead-control-audit.md)'s concern, not this file's.

Used during step 3 of the dead-control audit. When auditing an existing file, first note the platform it targets (see [`viewport-frames.md`](viewport-frames.md) for the desktop/tablet/mobile categories), then match each dead-looking control against the table below to decide what to wire, then use the matching code pattern. Everything here still follows the main query-param-state convention in [`query-param-states.md`](query-param-states.md).

## Platform changes the answer, not just the affordance

The trigger icon alone (kebab, share arrow, bell) doesn't fully determine the right component — what that trigger *should* produce is a platform convention as much as an icon-shape convention. The same "share" affordance is correctly a small anchored dropdown on a desktop site and incorrectly the same thing on a mobile app, where the OS-native pattern for share/export and for multi-option pickers is a bottom sheet or action sheet, not a compact dropdown. Work out the platform first, then read the table below with that context — don't pick a component name in isolation and stop there.

General native idioms to reason from, not a rigid lookup:
- **Mobile/tablet (touch-first):** a share action, an action offering several external destinations, or a long list of options to choose one from (sort, filter values, a picker) reads natively as a **bottom sheet** — the same sheet this skill already builds for other flows (see `query-param-states.md`'s bottom-sheet pattern). A short, single-column, text-only menu anchored to a specific icon (settings kebab in a top bar, a row's "..." for 2–4 short actions) still reads natively as a small **anchored dropdown/context menu** — mobile OSes render overflow menus this way too, it's not exclusively a desktop pattern.
- **Desktop (pointer-first):** almost everything in this category is an **anchored dropdown/popover** near the trigger, or a centered **modal/dialog** for share (with a copy-link field) or for a long picker. Bottom sheets are not a desktop idiom — never place one in a file detected as desktop.
- **Either platform:** a toggle-style icon (like, save, follow, subscribe) is an **inline state change**, not a menu, regardless of platform. A confirmation **toast** after an action is also platform-agnostic in kind, just anchored differently (above a bottom nav on mobile, a bottom corner on desktop).

## The mapping

| Visual affordance | What a user's mental model expects | Mobile/tablet component | Desktop component | Param |
|---|---|---|---|---|
| Kebab / ellipsis / "more_vert" (⋮ or ⋯) with a short, single-column list of text actions (settings, "not interested", report) | A small menu of contextual actions appears near the button | Anchored context/dropdown menu (see pattern below) | Anchored context/dropdown menu | `?dropdown=<id>` |
| Share icon, or a "..." that surfaces several external destinations/apps | The platform's native share flow appears | Bottom sheet (reuse `query-param-states.md`'s sheet pattern; list destinations as rows, not a compact dropdown) | Small popover, or a modal with a copy-link field — never a bottom sheet | `?sheet=<id>` (mobile) or `?dropdown=<id>` / `?modal=<id>` (desktop) |
| Chevron / caret on a row, or a "Filters" / "Sort by" control offering several values to pick one from | A picker of options opens | Bottom sheet (full-width picker list) | Dropdown/select or popover | `?sheet=<id>` (mobile) or `?dropdown=<id>` (desktop) |
| Chevron / caret that's expanding in-place detail on the same row (not offering a picker) | The row expands to show more of itself | Accordion expand | Accordion expand | `?accordion=<id>` |
| Bell / notification icon | A panel of recent notifications appears | Bottom sheet if items are rich/multi-line; anchored dropdown panel if short — match whatever density the rest of the file already uses | Anchored dropdown panel | `?sheet=notifications` or `?dropdown=notifications` |
| Heart/like, bookmark/save, follow, subscribe "+" badge, thumbs up/down | Immediate visible state change on the icon itself (filled vs. outline, count increments), sometimes with a brief confirmation | Inline toggle (platform-agnostic) | Inline toggle (platform-agnostic) | inline toggle fn; optional `?toast=<id>` |
| Primary CTA verb button — "Submit", "Save", "Post", "Send", "Review", "Add", "Follow up", "Create" | Some acknowledgment that the click did something | Toast, anchored above any bottom nav | Toast, anchored bottom corner or bottom center | `?toast=<id>` |
| Icon-only button with no label, no obvious menu semantics, sitting where a settings/options affordance would go | Treat as a kebab (opens a small menu) — the most common intent for an unlabeled icon button that isn't a like/save/share glyph | Anchored context/dropdown menu | Anchored context/dropdown menu | `?dropdown=<id>` |
| Row or card that's entirely clickable but has no `href`/handler | Navigates somewhere or opens a detail view | If this skill built the surrounding flow as multiple files, link it for real (`<a href="...">`); otherwise a toast ("Opens video detail") is an acceptable stand-in — say so in the report | same | real `href`, or `?toast=<id>` as a documented stand-in |
| Search icon glued to a search input | Not an independent affordance — leave alone unless visually separated and clearly its own button | — (skip) | — (skip) | — |
| Tabs, toggles/switches, steppers | Already covered by the main `query-param-states.md` patterns — use those directly | — | — | see `query-param-states.md` |

Skip anything that already reacts (real `href`, existing `onclick` that changes visible state, or an existing query param) and anything genuinely decorative that no reasonable user would expect to click (a static logo mark, a divider, a label-only badge).

## Pattern: anchored context/dropdown menu (kebab, bell, overflow)

Use this for the "anchored dropdown/popover" cells in the table above — short, single-column text menus anchored to their trigger, on either platform. For anything the table assigns to a bottom sheet instead (mobile share, mobile pickers), use the bottom-sheet pattern already documented in `query-param-states.md` — don't build a second sheet implementation here, reuse that one.

This is the one pattern not already spelled out in `query-param-states.md`. Unlike a full-width sheet, this menu is small and anchored to its trigger button — position it with a `relative` wrapper around the trigger, not centered on the viewport.

```html
<div class="relative inline-block">
  <button onclick="toggleDropdown('video-1-menu')" class="icon-btn" title="More options" aria-haspopup="true">
    <!-- kebab svg -->
  </button>
  <div id="video-1-menu" class="dropdown-menu hidden absolute right-0 top-full mt-1 w-56 rounded-lg bg-[var(--surface,#272727)] border border-white/10 shadow-lg py-1 z-40">
    <button class="dropdown-item w-full text-left px-3 py-2 text-[13px] hover:bg-white/10" onclick="closeDropdown('video-1-menu')">Not interested</button>
    <button class="dropdown-item w-full text-left px-3 py-2 text-[13px] hover:bg-white/10" onclick="closeDropdown('video-1-menu')">Save to Watch Later</button>
    <button class="dropdown-item w-full text-left px-3 py-2 text-[13px] hover:bg-white/10 text-red-400" onclick="closeDropdown('video-1-menu')">Report</button>
  </div>
</div>
```

```js
function toggleDropdown(id) {
  document.querySelectorAll('.dropdown-menu').forEach(el => { if (el.id !== id) el.classList.add('hidden'); });
  document.getElementById(id)?.classList.toggle('hidden');
}
function closeDropdown(id) {
  document.getElementById(id)?.classList.add('hidden');
}
// Click-outside dismiss — one listener handles every menu on the page.
document.addEventListener('click', (e) => {
  document.querySelectorAll('.dropdown-menu:not(.hidden)').forEach(el => {
    const trigger = el.parentElement?.querySelector('button');
    if (!el.contains(e.target) && trigger && !trigger.contains(e.target)) el.classList.add('hidden');
  });
});
```

Bootstrap addition (in the same `applyInitialState()` the rest of the file already has, or a new one if the file has none yet):

```js
const dropdown = params.get('dropdown');
if (dropdown) document.getElementById(dropdown)?.classList.remove('hidden');
```

If the file is hand-rolled CSS rather than Tailwind, translate the classes above into that file's own conventions (e.g. a `.dropdown-menu { display: none; }` / `.dropdown-menu.open { display: block; }` pair matching how the file already toggles visibility elsewhere) rather than pulling in Tailwind just for this menu.

## Pattern: toast, when the file doesn't already have one

If the audited file has no toast/snackbar element yet and a candidate needs one, add a single shared toast (one element, reused for every action) rather than one per trigger:

```html
<div id="toast" class="fixed left-1/2 -translate-x-1/2 bottom-20 z-50 opacity-0 pointer-events-none translate-y-2 transition-all duration-200 bg-[var(--surface-strong,#3f3f3f)] text-white text-[13px] font-medium px-4 py-3 rounded shadow-lg">
  <span id="toast-text">Saved</span>
</div>
```

```js
let toastTimer;
function showToast(id) {
  const copy = { /* fill in with the real per-action copy for this file */ };
  const el = document.getElementById('toast');
  document.getElementById('toast-text').textContent = copy[id] || 'Done';
  el.classList.remove('opacity-0', 'pointer-events-none', 'translate-y-2');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    el.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => el.classList.add('pointer-events-none'), 200);
  }, 2400);
}
```

## Reporting the fix

Keep Step 4's report short and concrete: name the control, name what it now does, and give the param to preview it. Don't narrate the whole audit process — the user wants the findings, not the method.
