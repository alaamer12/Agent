---
name: visual-parity-testing
description: "Framework for closing the gap between a design mockup (HTML/CSS, Figma export, or reference image) and what actually renders on a real device/emulator, for any UI framework. Covers the full pipeline (mockup + on-device capture, frame/chrome-noise normalization, similarity scoring, regional diagnosis) and an autonomous convergence loop that iterates capture→compare→diagnose→fix→rebuild without pausing for check-ins until threshold is met. Also covers: inventorying ItC (interact-to-change) components like dropdowns/drawers/modals and forcing their states via query params; dummy/placeholder mockup data needing fixtures so content mismatches don't masquerade as layout bugs; transition/animation ('smoothing') parity beyond static screenshots; and navigating past obstacle screens (splash/onboarding/permissions) without getting stuck. Use when the user wants pixel/visual parity with a design, an automated visual regression pipeline, or an agent that autonomously iterates toward a similarity score."
---

# Visual Parity Testing & Autonomous Convergence

A framework for measuring — and then autonomously closing — the gap between a design reference and what a real device actually renders. This is not a one-shot "take a screenshot and diff it" tool; it's built around a **loop an agent runs to convergence on its own**, the same way a human would iterate, but without needing to be prompted after every attempt.

## Why this is a loop, not a single pass

A single capture-compare-report cycle tells you a score is low. It doesn't fix anything, and handing the result back to a human after every single iteration turns what could be an unattended multi-hour convergence run into a slow back-and-forth. The whole point of this skill is that **the loop closes itself**: diagnose *where* the mismatch is (regional grid), form a hypothesis for *why* (the rendering-gotchas catalog), apply a real fix, rebuild, recapture, and check again — repeatedly, autonomously — reporting to the human only at genuine decision points (see "When to stop and ask" below), not after every attempt.

## Reference files

- **`references/pipeline.md`** — the end-to-end architecture: mockup capture at a fixed viewport/DPR, on-device/emulator capture, and the mathematical comparison techniques (SSIM, palette similarity, regional grid scoring) with what each one is actually good at diagnosing.
- **`references/frame-normalization.md`** — the single most common cause of a *false* low score: coordinate-space misalignment (status bars, nav chrome, browser scrollbars, DPI mismatches) and chrome/frame noise that has nothing to do with real layout differences. Read this before trusting any similarity number that comes back surprisingly low.
- **`references/debug-state-simulation.md`** — how to reach a specific deep UI state on demand: the ItC-component inventory method, instrumenting a static mockup with query-param-driven state forcing, hosting it correctly (not over `file://`), the dummy-data fixture plan, and bypassing obstacle screens — everything needed so the loop can capture any screen/state/theme/language combination unattended.
- **`references/rendering-gotchas.md`** — a categorized catalog of *why* a pixel-accurate-looking implementation still scores low: native input decorations, spacing double-counting, font-metric divergence, chrome elements that don't auto-hide, asset-path resolution differences, dummy-data mismatches, and capture-reliability failures. Each category includes the general symptom pattern plus one concrete worked fix, from a real MAUI/Android project, to show what "root cause → fix" actually looks like end to end.
- **`references/motion-parity.md`** — why a passing still-frame score doesn't mean parity: transitions, easing, and coupled state changes (a chevron that should flip, a drawer that should slide rather than snap) that only show up in motion, plus how to check for them separately from the main still-image loop.

## The workflow

### Step 0 — Establish ground truth before the loop starts

- Confirm the mockup source (HTML/CSS, Figma export, static reference images) and the target platform(s)/device(s)/emulator(s).
- Confirm the similarity metric(s) and the **threshold that defines "done"** — don't assume 90%; ask if it's not stated, since this determines when the loop is allowed to stop.
- **Inventory every ItC (Interact-to-Change) component** — anything that looks different depending on interaction: dropdowns, drawers/side-menus, modals, tooltips, accordions, tabs, toggles, hover/focus/pressed states. For each one, list its distinct visual states. This inventory is what determines the true scope of the capture matrix — see `references/debug-state-simulation.md` for how to force each state deterministically instead of guessing at it manually per run.
- **Compute the full capture matrix before starting**, and state the number out loud: `base screens × ItC-state combinations × theme variants × language variants`. If the product supports dark mode, that's ×2. If it supports more than two languages, cap the audit at two (pick the two that matter most, e.g. the default plus one RTL/LTR-opposite language if relevant) rather than multiplying the matrix by every supported locale — full locale coverage is a separate, later concern, not part of this loop's scope.
- **Build the dummy-data fixture plan.** Mockups almost always contain fake/placeholder content (names, numbers, lorem ipsum). Comparing a mockup against the real app's real data will never converge — the loop will keep "fixing" a content mismatch that isn't a layout bug. Extract the mockup's literal dummy content and create a matching fixture/seed dataset the real app can be forced into via the debug/launch-flag mechanism (see `references/debug-state-simulation.md`). This fixture must only be reachable through the debug flag — never something that could leak into a production build.
- **Inventory obstacle screens** — splash screens, onboarding flows, permission prompts, login walls, or anything else that sits between app launch and the target screen. The loop must never depend on manually clicking through these each run; build a debug-flag bypass straight to the target screen/state for each one (see `references/debug-state-simulation.md`).
- Set up (or confirm the existence of) the deep-link/launch-flag mechanism per `references/debug-state-simulation.md` — the loop cannot capture the full matrix unattended if reaching each state requires manual navigation.
- Confirm frame-normalization is correct *before* the first real comparison (see `references/frame-normalization.md`) — running dozens of loop iterations against a miscropped baseline, or against browser/native chrome noise that was never cropped out, wastes the entire run chasing a score ceiling that normalization would have fixed in one step.
- Note which ItC components involve a **transition/animation**, not just a static open/closed state — these need separate handling per `references/motion-parity.md`, since a still-frame comparison of the end state can pass while the motion itself (easing, duration, a chevron that should flip and doesn't) is still wrong.

### Step 1 — Capture baseline pair

- Capture the mockup reference at a fixed, documented viewport and device-scale-factor.
- Capture the current on-device/emulator render of the same screen/state, using the deep-link mechanism from Step 0 so this is scriptable and repeatable.
- Normalize both to the same coordinate space (crop OS chrome, align dimensions) per `references/frame-normalization.md`.

### Step 2 — Score and diagnose (don't just get a number — localize it)

- Run the full comparison suite from `references/pipeline.md`: an overall similarity score, a palette/color-fidelity score, and a **regional grid breakdown** (e.g. 4×4) — the regional grid is what turns "72%, not sure why" into "the bottom row is 30%, everything else is 90%+," which is what makes autonomous diagnosis possible at all. A single global number is not enough signal to act on without a human manually inspecting the image every time.
- If already at or above the agreed threshold for this screen/state: record it as done, move to the next screen/state in scope, don't keep iterating on something that's already passing.

### Step 3 — Form a root-cause hypothesis from the regional signal

- Map the lowest-scoring region(s) to the actual UI elements that live there (a bottom row failing usually means a bottom bar/CTA/nav chrome issue; a top row failing usually means a header/status-bar issue).
- Check the failure pattern against `references/rendering-gotchas.md`'s categories first — most low-scoring regions turn out to be one of a small number of recurring causes (a native decoration bleeding through, a spacing/margin double-count, a chrome element that didn't auto-hide, a font-metric mismatch), not a novel one-off bug.
- If the heatmap shows a **structural shift** (bright red/magenta — things in the wrong place) that's a different fix category than **texture/softness** (yellow — minor anti-aliasing or shadow softness, often not worth chasing below a certain point of diminishing returns).

### Step 4 — Apply the fix, rebuild, recapture — without stopping to ask

This is the step that makes the loop autonomous rather than a human-mediated back-and-forth: apply the concrete code fix for the diagnosed cause, rebuild/redeploy to the device or emulator, recapture, rescore. If the score improved and is at/above threshold, mark done and move to the next screen/state. If it improved but isn't at threshold yet, repeat Step 3 with the new heatmap — the diagnosis at 85% is often different from the diagnosis at 60%, so re-diagnose fresh each time rather than assuming the first hypothesis explains the rest of the gap.

**Before trusting any capture, confirm the window/app had actually finished rendering when the screenshot was taken.** A capture fired before the first frame settles produces a black or blank screenshot that will score near-zero for reasons that have nothing to do with visual parity — this is a capture-reliability bug, not a design mismatch, and re-diagnosing against it wastes a cycle. Wait for a positive signal that rendering is stable (a known element present, a fixed settle delay after navigation, or a framework-specific "rendered" hook if one exists) before capturing, and if a capture comes back suspiciously blank/black/near-uniform in color, treat that as a capture failure to retry — not a real score — before it ever reaches the diagnosis step.

**Never pause the loop to report routine progress.** Run continuously through Step 1–4 across the full scope from Step 0 until the assignment is actually fulfilled (every screen/state at or above threshold) or one of the stop conditions below is genuinely hit. There is no "checkpoint" pause in between — the entire value of this loop is that it runs unattended for as long as it takes.

### Step 5 — Move through the full scope, then summarize

Repeat Steps 1–4 across every screen/state combination in scope (every screen × every theme/mode × every deep-linked state that matters) before reporting a final summary. Track a running table (screen/state, starting score, ending score, iterations taken, fixes applied) so the final report shows the whole run, not just the last thing touched.

## When to stop and ask (the loop is autonomous, not reckless)

Autonomy here means something specific: **the loop does not pause for routine check-ins, ever.** It only stops for one of three reasons:

1. **The assignment is fulfilled** — every screen/state in the Step 0 matrix is at or above the agreed threshold. This is the normal, expected exit. Report the full run summary (Step 5) at this point, not before.
2. **A genuine external blocker makes further work impossible** — a required tool/environment isn't available (an emulator image isn't installed, a required SDK is missing, a device isn't connected) and the loop cannot proceed at all without it. This isn't a design/code problem the loop can fix by iterating; it needs a human to resolve the environment, so stop and say exactly what's missing and what would unblock it.
3. **A genuine emergency/ambiguous decision point** — something broke in a way that has more than one reasonable resolution and no way to infer which the human wants (e.g. the emulator crashes on startup: attempt to diagnose and fix the emulator itself, or stop and let the human handle the environment?). Ask the specific question, don't guess and don't stall.

**Explicitly not a stop condition**: diminishing returns on a single region, a fix that needs a few attempts, a large capture matrix, a long expected runtime, or the loop simply taking hours. If a region isn't improving after several distinct fix attempts, that itself becomes an instance of reason 3 above — frame it as a specific decision for the human ("tried A/B/C on this region, none moved the score — keep trying alternate approaches, treat it as a platform/design limit and move on, or something else?") rather than silently giving up *or* silently looping forever on the same failing hypothesis.

### Obstacles are not stop conditions either — handle them, don't get stuck in them

Splash screens, onboarding flows, permission prompts, and similar gating screens are not emergencies and not ambiguous — they're an expected part of the app's boot sequence, and getting stuck inside one (repeatedly capturing a splash screen, or failing to advance past an onboarding step) is a loop bug, not a legitimate reason to stop. This is exactly what the Step 0 obstacle inventory and debug-flag bypasses are for: if the loop finds itself unable to get past a gating screen using the bypass that was supposed to handle it, that's a signal the bypass itself is incomplete or broken — fix the bypass (or note it as a genuine blocker per reason 2 above if the app truly has no way to skip it) rather than repeatedly attempting the same manual navigation and burning cycles stuck on the same screen.
