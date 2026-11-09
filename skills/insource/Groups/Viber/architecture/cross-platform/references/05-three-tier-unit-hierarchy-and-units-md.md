# 05 — Three-Tier Unit Hierarchy & UNITS.md Governance

> Structured unit classification for cross-platform components. Eradicating parallel reinvention through strict tier specialization and mandatory indexing in `UNITS.md`.

---

## 1. The Three-Tier Architecture

To maintain a scalable cross-platform codebase, every reusable visual unit belongs to exactly one of three structural tiers:

```
┌─────────────────────────────────────────────────────────────┐
│  Tier 3: Domain Specialization                              │
│  Context-aware, feature-bound, platform-customized views.   │
│  e.g., FundDetailCard.phone.tsx, DesktopProjectSidebar.xaml │
└──────────────────────────────┬──────────────────────────────┘
                               │ Specializes / Composes
┌──────────────────────────────▼──────────────────────────────┐
│  Tier 2: Base Unit (The Architectural Contract)              │
│  Abstract composition, standard layouts, neutral APIs.      │
│  e.g., CardBase, MasterDetailLayout, NavigationShellBase    │
└──────────────────────────────┬──────────────────────────────┘
                               │ Built From
┌──────────────────────────────▼──────────────────────────────┐
│  Tier 1: Core Primitive                                     │
│  Feature-blind, atomic building blocks.                     │
│  e.g., RawText, BaseButton, Surface, Divider, IconContainer │
└─────────────────────────────────────────────────────────────┘
```

### Tier Definitions & Rules

| Tier | Name | Dependency Constraint | Rule |
| :--- | :--- | :--- | :--- |
| **Tier 1** | **Core Primitive** | No dependencies on features, business logic, or app domains. | Pure visual/input primitives. Framework wrappers with zero domain knowledge. |
| **Tier 2** | **Base Unit** | May consume Tier 1 primitives; zero knowledge of concrete features. | Reusable structural patterns (e.g. Card layouts, Dialog shells). Declares extension slots. |
| **Tier 3** | **Domain Specialization** | Consumes Tier 2 and Tier 1; bound to domain models and platforms. | The final assembled unit. Specific to a feature (e.g., `CryptoWalletBalanceCard`). |

---

## 2. The UNITS.md Governance Mandate

Before authoring a new visual component or layout unit, an agent or engineer is **strictly obligated** to consult the project's `UNITS.md` catalog:

```
               Incoming Request: "Create a User Profile Card"
                                      │
                        ┌─────────────▼─────────────┐
                        │   Check UNITS.md Index    │
                        └─────────────┬─────────────┘
                                      │
                 ┌────────────────────┴────────────────────┐
                 ▼                                         ▼
         Unit already exists?                     Unit does not exist?
                 │                                         │
       ┌─────────▼─────────┐                     ┌─────────▼─────────┐
       │ REUSE OR EXTEND   │                     │ AUTHOR NEW UNIT   │
       │ Do NOT build a    │                     │ Must register in  │
       │ parallel copy.    │                     │ UNITS.md in same  │
       └───────────────────┘                     │ pull request.     │
                                                 └───────────────────┘
```

### UNITS.md Entry Schema

Every registered unit must declare its exact lineage and responsibility:

```markdown
| Unit Name | Tier | Path | Responsibilities | Extends / Depends On | Replaces / Deprecates |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CardBase` | Tier 2 | `shared/ui/containers/CardBase.tsx` | Standard elevated card container with header/body/footer slots | `Surface` (Tier 1) | `LegacyBox` |
| `FundCard` | Tier 3 | `features/funds/views/FundCardView/` | Renders mutual fund metrics with responsive mobile/desktop renditions | `CardBase` (Tier 2) | N/A |
```

---

## 3. The Reinvention Defect (Anti-Pattern)

```tsx
// ✘ DEFECT: Creating a parallel Card container inside a feature folder
// features/checkout/views/CheckoutSummaryCard.tsx
export function CheckoutSummaryCard({ title, total }: Props) {
  // ✘ Reinventing shadow, border radius, background, and padding 
  // already standardized inside shared/ui/containers/CardBase.tsx
  return (
    <div style={{ background: '#fff', borderRadius: 8, boxShadow: '0 2px 4px rgba(0,0,0,0.1)', padding: 16 }}>
      <h3>{title}</h3>
      <p>{total}</p>
    </div>
  );
}
```

#### Correct Specialization:
```tsx
// ✅ Composes the Tier 2 Base Unit and injects domain-specific children
import { CardBase } from '@/shared/ui/containers/CardBase';

export function CheckoutSummaryCard({ title, total }: Props) {
  return (
    <CardBase title={title} variant="outlined">
      <Typography variant="headline">{total}</Typography>
    </CardBase>
  );
}
```
