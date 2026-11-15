# Typography & Spacing Systems

The `## Typography & Hierarchy` and `## Layout & Spacing System` sections define the mathematical and visual rhythm of the project.

---

## 1. Typography Hierarchy

### 1.1 Font Pairings
Choose no more than two font families:
- **Primary / Body**: System font stack (`system-ui, -apple-system, sans-serif`) or a neutral grotesque sans (e.g. *Inter*, *Geist*, *Plus Jakarta Sans*).
- **Secondary / Heading** (Optional): A high-character display font or editorial serif (e.g. *Instrument Serif*, *Cal Sans*, *Newsreader*).
- **Code / Tabular Data**: Monospaced font (*JetBrains Mono*, *Geist Mono*, *Fira Code*).

### 1.2 Fluid Rem Scale & Line Heights
Use a geometric type ladder based on an 8pt / 0.25rem baseline. Unitless line heights ensure proportional scaling:

```yaml
typography:
  fonts:
    body: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    heading: "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    mono: "'JetBrains Mono', ui-monospace, monospace"

  scale:
    xs:
      fontSize: "0.75rem"      # 12px
      lineHeight: 1.4
      letterSpacing: "0.01em"
    sm:
      fontSize: "0.875rem"     # 14px
      lineHeight: 1.5
      letterSpacing: "0em"
    base:
      fontSize: "1rem"         # 16px
      lineHeight: 1.6
      letterSpacing: "-0.01em"
    lg:
      fontSize: "1.125rem"     # 18px
      lineHeight: 1.5
      letterSpacing: "-0.015em"
    xl:
      fontSize: "1.25rem"      # 20px
      lineHeight: 1.4
      letterSpacing: "-0.02em"
    "2xl":
      fontSize: "1.5rem"       # 24px
      lineHeight: 1.3
      letterSpacing: "-0.025em"
    "3xl":
      fontSize: "2rem"         # 32px
      lineHeight: 1.2
      letterSpacing: "-0.03em"
    "4xl":
      fontSize: "2.5rem"       # 40px
      lineHeight: 1.15
      letterSpacing: "-0.035em"
```

### 1.3 Reading Widths
- Body prose: Max width **65 to 75 characters** (`max-w-prose` / `65ch`).
- Dense dashboard data: Width follows tabular grid alignment, not prose widths.

---

## 2. Spacing Architecture (4px / 8px Grid)

Never invent arbitrary margins or paddings (`margin: 13px;` is forbidden). Every spacing value must resolve to an explicit token:

```yaml
spacing:
  "1": "0.25rem"   # 4px  - Hairline gap, icon-to-label
  "2": "0.5rem"    # 8px  - Compact element padding
  "3": "0.75rem"   # 12px - Input field horizontal padding
  "4": "1rem"      # 16px - Standard container padding / card gap
  "6": "1.5rem"    # 24px - Section gap / card padding
  "8": "2rem"      # 32px - Module separation
  "12": "3rem"     # 48px - Major layout divide
  "16": "4rem"     # 64px - Hero and viewport padding
```

### Layout Invariants
- **Consistency**: The same gap value must mean the same relationship across the entire interface.
- **Card Spacing**: Internal card padding is typically `spacing.6` (24px) for desktop and `spacing.4` (16px) for compact mobile viewports.
