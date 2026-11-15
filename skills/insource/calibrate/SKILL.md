---
name: calibrate
description: "Universal framework for extracting the complete design, visual, and interaction DNA of a confirmed 'North Star' reference implementation and systematically propagating it across all sibling pages, components, or screens. Operates across any UI stack (Web, React, Vue, Svelte, Mobile Flutter/React Native/SwiftUI, Desktop, HTML/Tailwind) without loss of subtle layers like atmosphere, iconography, micro-visualizations, typography hierarchy, or data simulation contracts. Triggers: calibrate, /calibrate, make all pages match this one, spread the design, North Star alignment, propagate design system."
---

# Calibrate — Universal North Star Design Extraction & Propagation

A universal engineering framework for extracting the complete visual and interactive DNA of a verified reference implementation (the **"North Star"**) and propagating it across sibling pages, views, or components with zero loss of subtlety.

Calibrate solves the **Partial Adoption Defect** — the recurring failure where an agent ports basic typography and surface colors from a reference screen, but silently omits subtle layers: atmospheric gradients, decorative patterns, micro-visualizations, icon badge geometry, responsive breathing room, deterministic mock simulation contracts, and empty states.

---

## The 6 Universal Extraction Dimensions

When calibrating from a North Star reference, the agent must treat the interface as an interconnected 6-dimensional system, regardless of the underlying stack (React, Vue, Svelte, Flutter, SwiftUI, Blade, or Vanilla):

```
┌────────────────────────────────────────────────────────────────────────┐
│                   UNIVERSAL CALIBRATION CONTRACT (UCC)                 │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Canvas & Atmosphere   │ Ambient glows, background mesh, organic SVGs│
│ 2. Spatial & Surface     │ Radius scale, elevation, border token, gap  │
│ 3. Iconographic System   │ Vector source, badge framing, tint pairing  │
│ 4. Data & Visual Rhythm  │ Micro-charts, sparklines, progress bars     │
│ 5. Typographic Hierarchy │ Headings, body weights, tabular/monospace   │
│ 6. Lifecycle & Mock Data │ Full-fidelity data state vs honest baseline │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Workflow

### Step 1: Dissect the North Star (Ground Truth Extraction)

Never edit sibling files before completing the extraction phase. Read the North Star file completely and build a formal **Calibration Contract**:

1. **Dimension 1 — Canvas & Atmosphere**:
   - Inspect the viewport background. Is it a flat solid, or does it include subtle organic SVG paths, radial glow blur discs, noise textures, or dot/grid matrices?
   - Record exact layer positioning: z-indexing, overflow bounding, absolute pinning, and opacity multipliers.
   - *Collisions Check*: If SVG patterns or CSS clip-paths use IDs (e.g., `<pattern id="...">`), require unique instance keys per sibling to prevent cross-view cache pollution.

2. **Dimension 2 — Spatial & Surface Architecture**:
   - Inspect component enclosures: border-radius scale, border opacity, background tints, and shadow tiers (rest vs hover).
   - Measure internal card padding (`p-4`, `p-5`, `p-6`) and vertical flow spacing (`gap-5`, `space-y-6`, `space-y-8`).
   - Identify containment requirements (e.g., `overflow: hidden` on cards containing bleeding charts or decorative ribbons).

3. **Dimension 3 — Iconographic System**:
   - Identify how icons are authored: inline SVG paths, component icon library (Lucide, Heroicons, Phosphor), or font glyphs.
   - **Crucial verification**: Check that icon keys actually exist in the project registry. Never blindly invoke icon helper functions that return empty fallbacks.
   - Inspect badge architecture: shape (circle vs squircle), dimensions, background pastel tint, and icon contrast.

4. **Dimension 4 — Data & Micro-Visualizations**:
   - Do KPI cards or list items host mini charts, sparklines, or progress rings?
   - Identify the rendering engine (Chart.js, Canvas, SVG bezier curves, D3, or CSS bars).
   - Note layout positioning inside cards (e.g., anchored to bottom-left with fixed width/height vs centered).

5. **Dimension 5 — Typographic Hierarchy**:
   - Map font families: primary UI font, headline font, and monospace/tabular figures font for numbers.
   - Map metric scales: label size/weight, value size/weight, and trend/status badge geometry.

6. **Dimension 6 — Lifecycle & Mock Simulation Contract**:
   - How does the reference handle sparse vs rich data? (e.g., URL parameters like `?filled`, local storage flags, or mock state switches).
   - Ensure sibling pages mirror the exact same contract: deterministic mock data when active, and honest zero/empty state when inactive.

---

### Step 2: Audit Target Sibling Pages (Gap Analysis Ledger)

Before applying edits, author a concise Audit Ledger showing exactly what is missing from each target page:

| Target Surface | Dim 1 (Atmosphere) | Dim 2 (Surface) | Dim 3 (Icons/Badges) | Dim 4 (Micro-Charts) | Dim 5 (Typography) | Dim 6 (State Contract) |
|---|---|---|---|---|---|---|
| *Target A* | ❌ Missing | ⚠️ Partial | ❌ Broken / Missing | ❌ Missing | ⚠️ Inconsistent | ❌ Lacks mock data |
| *Target B* | ❌ Missing | ✅ Matches | ⚠️ Inconsistent badge | ❌ Missing | ✅ Matches | ✅ Implemented |

---

### Step 3: Systematic Propagation & Architectural Parity

Execute changes iteratively across all target files:

1. **Verify Shell & Dependency Parity**:
   - Ensure the parent HTML template, layout wrapper, or bundler imports all dependencies required by the North Star (e.g., chart libraries, web fonts, CSS utilities).
2. **Propagate Atmosphere**:
   - Replicate the ambient background layer, adjusting theme tints appropriately for the page's functional role while keeping structural geometry consistent.
3. **Propagate Cards & Surfaces**:
   - Apply identical surface tokens, hover states, and card structures.
4. **Propagate Iconography & Badges**:
   - Enforce the North Star's icon badge geometry and valid SVG vector sources.
5. **Propagate Micro-Visualizations**:
   - Wire identical sparkline or micro-chart containers, fed by the page's domain metrics.
6. **Harmonize State & Edge Cases**:
   - Implement both the simulated rich state and the clean empty/zero baseline state.

---

### Step 4: Verification & Anti-Pattern Checklist

Before marking the task complete:

- [ ] **No Phantom Icons**: Every icon renders a real vector graphic, not an empty square or fallback dot.
- [ ] **Zero Canvas Bleed**: Charts and sparklines respect card bounds and never spill across borders.
- [ ] **RTL / LTR Symmetry**: Text alignment, badge positions, and sparkline coordinates respect the locale layout direction.
- [ ] **Deterministic Data**: With the mock flag enabled, numbers, charts, and lists render populated; with the flag disabled, the page displays a clean, honest baseline.
- [ ] **Visual Proof**: Capture or inspect the output in both states to confirm pixel-level harmony with the North Star.

---

For in-depth layer standards, see `references/calibration-contract.md`.
For framework-agnostic architectural examples, see `examples/walkthrough.md`.
