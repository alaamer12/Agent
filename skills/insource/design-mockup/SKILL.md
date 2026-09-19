---
name: design-mockup
description: Build static HTML/CSS mockups of app/website screens as standalone, frameless files sized for a viewport (desktop/tablet/mobile). Use for "mockup", "wireframe", or seeing what a screen "would look like" as static HTML. Every interactive element (sheets, drawers, modals, dropdowns, tabs, toggles, accordions, steppers, toasts) must be drivable via URL query params so a state can be linked/screenshotted without clicking through. Also covers an opt-in command — auditing an already-built HTML file for dead controls (kebab/ellipsis menus, chevrons, bells) that look clickable but do nothing, wiring each to the expected feedback (dropdown, toast, panel, inline toggle). Trigger that for "this does nothing when clicked", "add feedback to interactive elements", "make this feel real", "audit for dead clicks", "wire up the kebab menu", or "opt in" feedback. Not for real interactive apps or React components (use frontend-design).
---

# Design Mockup

A static HTML mockup of a UI — a screen, a short flow, or one component in context. It looks real and can be screenshotted in any state, but has no backend and no real logic: every dynamic-looking bit of state is faked with placeholder content or exposed as a URL query parameter.

**Two entry points.** Build a new mockup — the default, the Workflow below. Or audit an **existing** HTML file whose controls look clickable and do nothing — a separate opt-in command, triggered by "this does nothing when clicked", "add feedback to the interactive elements", "make this feel real", "audit for dead clicks", "wire up X". That procedure is [`references/dead-control-audit.md`](references/dead-control-audit.md); never run it on a mockup you just built.

## Workflow

### 1. Understand the request

Work out what screen(s) to build from the description, an attached reference, or both. Ask only when the request is genuinely ambiguous about **what** the screen is or does — never about details a screenshot already answers, and never about styling you can reasonably assume. Describe back in one line what you're building rather than interrogating.

Ground every label in the real subject matter: realistic copy, plausible data. Never Lorem ipsum or "Item 1 / Item 2". For visual and typographic distinctiveness, the `frontend-design` skill's principles apply on top of this skill's mechanics.

### 2. Pin down viewport(s), then file count

Ask only if the subject doesn't imply an answer (a landing page implies desktop; a bottom sheet or app screen implies mobile). Default is **desktop**, meaning the plain browser webview — not a browser-chrome mockup. Supported: `desktop`, `tablet`, `mobile`; per-viewport dimensions and the frameless rules are in [`references/viewport-frames.md`](references/viewport-frames.md).

- **Viewports are one axis:** one file per viewport by default (`desktop.html`, `mobile.html`). Only write a single responsive file if the user explicitly asks for one — three separately laid-out files are less code and far fewer layout bugs than forcing one DOM to reflow.
- **Screens are a separate axis, and it is not negotiable:** see 2.5. Never read "default to a single file" as licence to merge distinct screens behind a `?tab=` param — that conflates the two axes.

### 2.5 One file per distinct screen — always

More than one distinct screen (a flow, an app's tabs, a multi-step process shown as full screens) means **one file per screen**, linked by real `<a href="next-screen.html">` navigation, regardless of how many viewports are involved.

**The test:** if two "states" have different headers, different primary content structure, and would reasonably be called different pages by the person who asked for them, they are separate files. If they're two visibility states of one component on one page (sheet open vs. closed, tab A vs. B of content inside the same layout), a query param on a single file is correct. A `?tab=home|search|lists|more` where each value swaps an entire screen with its own header is a page router in disguise — stop and split.

A modal or sheet that overlays several screens still gets query-param treatment (`?sheet=create`) — the same markup and param convention repeated identically in each screen's file. Shared nav markup being duplicated across files is the expected cost of keeping screens separate, not a reason to merge them.

### 2.6 Two or more screens ⇒ also deliver a gallery `index.html`

Ship `index.html` in the same folder: every screen live, every state of every screen, and the notes on what each screen decides. Skip it for a single screen — one card is not a gallery. Anatomy, the three rules that make it work, and the acceptance test are in [`references/gallery-index.md`](references/gallery-index.md); a working starting point is [`assets/gallery.html`](assets/gallery.html).

### 3. Query-param-controlled state — the core requirement

Every interactive component with a visibility or selection state reads its initial state from `location.search` on load **and** keeps working normally via clicks afterward, so any state is reachable by URL alone (`?sheet=filters`, `?drawer=open`) — the contract in [`references/query-param-states.md`](references/query-param-states.md), which owns the naming convention, the bootstrap pattern and the per-component code patterns. Read it before writing interactive markup.

Separately, every screen that reads data gets `?state=<id>` for its own lifecycle (`loading`, `empty`, `error`, …). That param, the set of states, and the rules about what may and may not be faked are in the same reference — do not invent a per-screen variant of either.

### 4. Write lean code

- **Tailwind via the CDN script** (`https://cdn.tailwindcss.com`) for all styling. Don't hand-write utility-equivalent CSS; inline classes beat a stylesheet for size and clarity.
- Drop to a `<style>` block only for what Tailwind can't express directly: custom properties for a colour system, keyframes, RTL tweaks, safe-area insets. Keep it minimal.
- One `<script>` block at the end of `<body>` for all behaviour — the query-param bootstrap plus the click handlers. Keep functions short and shared across components of the same type rather than duplicated per instance.
- **Don't build a component library or templating layer.** This is a few concrete HTML files, not a system; repeat small markup patterns directly. **One exception:** if the set has a gallery, the `?state=` id/label table lives in one shared file both the screens and the gallery load — that is data with a single owner, not an abstraction, and without it the gallery's chip list silently drifts from the screens it claims to show.
- **If the user says "minimal tokens"**: drop indentation and line breaks, write dense/minified HTML. The query-param contract is not optional in that mode; only formatting is sacrificed.

### 5. Frameless output

The HTML *is* the deliverable — what renders in a browser tab, not a picture of a device. Frameless means no device depiction, and it does not mean skipping the native affordances the target platform needs; the enumerated rules and metrics are in [`references/viewport-frames.md`](references/viewport-frames.md) §Frameless.

### 6. Deliver

Save under `design/` in the working directory (`design/mockup.html`, or `design/desktop.html` + `design/mobile.html`), creating it if needed, unless the user names a different path. For 2+ screens, `design/index.html` is part of the deliverable, and any shared state kit goes in `design/assets/` so the gallery and the screens load the exact same file.

If the environment offers a file-presentation mechanism beyond the working directory (`present_files` or equivalent), use it after saving — check what's actually available rather than assuming. Don't also duplicate the content as a chat artifact: the file, opened in a browser, *is* the deliverable.

## Quick defaults reference

| Axis | Default when unstated |
|---|---|
| Viewport | desktop |
| Number of files (viewports) | one file (single, not split per viewport) |
| Number of files (screens/pages) | one file **per distinct screen**, always — never merged via a query param, regardless of viewport count |
| Gallery | `index.html` in the same folder for any set of 2+ screens |
| Output location | `design/` in the current working directory |
| Styling approach | Tailwind CDN utility classes |
| Code density | normal formatting (only minify if the user says "minimal tokens") |
| Device chrome | none — frameless always |
| Placeholder content | realistic, subject-grounded copy, never "Lorem ipsum" / "Item 1" |

## References

Read the one whose trigger matches what you're about to write; nothing here needs reading up front.

| File | Owns | Read it when |
|---|---|---|
| [`references/query-param-states.md`](references/query-param-states.md) | The URL-state contract: param naming, the bootstrap pattern, per-component patterns, screen-level `?state=`, what may not be faked | Before writing any interactive markup |
| [`references/viewport-frames.md`](references/viewport-frames.md) | Per-viewport dimensions, the frameless rules and native affordances, single vs. multi-file responsive | Before writing the outer `<body>`/`.app` wrapper |
| [`references/gallery-index.md`](references/gallery-index.md) | The `index.html` gallery: anatomy, the one-owner state table, preview scaling, acceptance test | Before writing any set of 2+ screens |
| [`references/dead-control-audit.md`](references/dead-control-audit.md) | The opt-in audit procedure: detect platform → inventory → classify → wire → report | Only when asked to fix dead controls in an existing file |
| [`references/feedback-heuristics.md`](references/feedback-heuristics.md) | The affordance→component mapping per platform, and the dropdown/toast code patterns | During step 3 of that audit |
| [`assets/template.html`](assets/template.html) | A runnable starting point for one screen | Starting a new mockup file |
| [`assets/gallery.html`](assets/gallery.html) | A runnable starting point for the gallery | Starting a multi-screen set |

**You must update this table whenever a reference or asset is added, removed or renamed** — the routing table is the only map of this skill, and a stale one is worse than none.
