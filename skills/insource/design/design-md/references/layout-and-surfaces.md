# Layout & Surface Architecture

The `## Layout & Spacing System` and `## Elevation, Depth & Shapes` sections define how elements sit in space, group together, and elevate above surfaces.

---

## 1. Container Widths & Responsive Breakpoints

Standardize major layout containers so agents do not produce erratic view widths:

```yaml
layout:
  containers:
    sm: "640px"      # Focused forms / Auth modals
    md: "768px"      # Reading / Article view
    lg: "1024px"     # Standard settings & single-pane dashboards
    xl: "1280px"     # High-density operational dashboards
    "2xl": "1536px"  # Data grids & multi-column canvas

  breakpoints:
    mobile: "max-width: 639px"
    tablet: "640px - 1023px"
    desktop: "min-width: 1024px"
```

---

## 2. Surface Hierarchy & Borders Over Shadows

Modern, calm UI relies on **subtle hairline borders** and **lightness stepping** rather than muddy drop shadows.

### 2.1 The Elevation Ladder
- **Surface 0 (App Canvas)**: The base background (`semantic.bg-app`, e.g. `neutral.50` in light, `neutral.950` in dark).
- **Surface 1 (Card / Sidebar)**: Base white or dark-tinted card (`semantic.bg-surface`). Separated from Surface 0 by a 1px border (`border-subtle`).
- **Surface 2 (Popover / Dropdown)**: Floats above canvas. Uses a delicate 1px border and low-opacity shadow (`shadow.sm`).
- **Surface 3 (Modal / Dialog)**: Overlays entire viewport. Backed by a semi-transparent scrim (`backdrop-blur-sm`).

```yaml
elevation:
  shadows:
    none: "none"
    sm: "0 1px 2px 0 oklch(0% 0 0 / 0.05)"
    md: "0 4px 6px -1px oklch(0% 0 0 / 0.08), 0 2px 4px -2px oklch(0% 0 0 / 0.04)"
    lg: "0 10px 15px -3px oklch(0% 0 0 / 0.10), 0 4px 6px -4px oklch(0% 0 0 / 0.05)"
```

### 2.2 Corner Radii Philosophy
State a clear, unified corner radius rule:
- **Sharp / Architectural**: 4px (`0.25rem`) on buttons, cards, and inputs. Best for developer tools and financial terminals.
- **Modern Soft**: 8px (`0.5rem`) on buttons/inputs, 12px (`0.75rem`) on cards. Best for B2B SaaS and productivity.
- **Fluid / Playful**: 12px on inputs, 16px–24px on cards, full pill (`9999px`) on badges. Best for consumer apps.

```yaml
radius:
  none: "0px"
  sm: "0.25rem"   # 4px  - Hairline badges, inner controls
  md: "0.5rem"    # 8px  - Inputs, buttons, dropdown items
  lg: "0.75rem"   # 12px - Cards, dialogs, containers
  full: "9999px"  # Avatar circles, status pills
```
