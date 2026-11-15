# Universal Calibration Contract (UCC) — Architectural Reference

The Universal Calibration Contract provides platform-agnostic definitions for the 6 extraction dimensions.

---

## 1. Canvas & Atmosphere (Background System)

A polished UI is rarely a flat monochromatic canvas. It typically incorporates an atmospheric layer consisting of:
- **Atmospheric Glows / Mesh Gradients**: Radial blur patches (`blur-3xl`, opacity 0.2–0.5) positioned out-of-flow behind the main content (`pointer-events: none; z-index: -1`).
- **Texture / Grid Patterns**: Dot matrices, subtle grid lines, or SVG noise patterns giving depth to large viewports.
- **Organic Flow Elements**: Curvature waves, contour paths, or brand ribbons with low-opacity gradients.

### Platform Independence:
- **Web / CSS**: `position: absolute; overflow: hidden; pointer-events: none; -z-10; filter: blur(...)`.
- **Flutter**: Stack with `Positioned` containers, `BackdropFilter`, or custom `CustomPainter`.
- **SwiftUI**: `ZStack` background with `.blur(radius: ...)` and `.clipped()`.

---

## 2. Spatial & Surface Architecture

Defines how containers segment data and react to ergonomics:
- **Surface Elevation**: Consistent border-radius (e.g. `16px` / `rounded-2xl`), border styling (e.g. `1px solid rgba(..., 0.08)`), and soft drop shadows (`0 1px 3px rgba(0,0,0,0.05)`).
- **Internal Density**: Generous breathing room (`padding: 20px–24px` on desktop, `16px` on mobile) ensuring components never feel cramped.
- **Hover & Interaction Feedback**: Smooth transition for elevation or border highlight on hover/focus.
- **Strict Containment**: Any surface hosting dynamic charts, gradients, or watermarks must strictly enforce `overflow: hidden` to prevent visual spillover.

---

## 3. Iconographic System & Badge Geometry

Icons should never float unanchored or rely on fragile unverified keys:
- **Framing & Geometry**: Icons are housed in consistent badges (e.g., circular `44x44px`, rounded squircle `48x48px`).
- **Semantic Tint Pairing**: A distinct background-to-foreground color pair matching the domain meaning:
  - Positive / Growth: Mint/Emerald background with deep green vector.
  - Informational / Primary: Soft blue background with royal blue vector.
  - Attention / Activity: Warm amber background with deep orange vector.
  - Premium / Tier: Pastel lavender background with rich purple vector.
- **Reliable Vectors**: Always verify icon availability in the project registry before rendering. If an icon helper returns fallback dots or nulls, provide direct inline SVG vectors from a standard library (Heroicons, Lucide, Phosphor).

---

## 4. Micro-Visualizations & Visual Rhythm

Cards and summary panels communicate trend velocity using micro-visualizations:
- **Sparklines & Trend Ribbons**: Small linear spline charts (height 32–40px) integrated directly into cards.
- **Progress & Ring Gauges**: Compact circular or radial gauges for percentage completion.
- **Zero-Bleed Geometry**: Positioned in an absolute or bounded container at card edges with fixed dimensions and hidden overflow.

---

## 5. Typographic Hierarchy & Monospace Numbers

- **Distinct Metric Typography**: Key numerical indicators use monospace or tabular figures (`font-mono`, `font-variant-numeric: tabular-nums`) to maintain visual alignment and prevent jitter during updates.
- **Visual Contrast**: Major numerical values stand out prominently (`28px–36px`, extra-bold/black weight) paired with subdued, descriptive labels (`13px–14px`, medium weight).

---

## 6. Lifecycle & Data Simulation Contract

High-fidelity design reviews require realistic data. The system must support:
- **Rich State**: Realistic, deterministic mock data populated via seed parameters (`?filled=1`, debug props, or mock stores).
- **Honest Baseline**: A clean zero/empty state showing proper placeholders and helpful empty-state UI when mock flags are disabled.
