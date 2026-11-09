# 06 — Multi-Axis Isolation & The Escalation Ladder

> Managing orthogonal variability across Platform, Distribution Channel, Audience/Region, and Multi-Tenant dimensions. The Single-Axis Filename Law and the three-level architectural escalation ladder.

---

## 1. Orthogonal Axes of Variation

In enterprise-scale cross-platform applications, variability extends beyond the operating system. Codebases frequently vary along four independent, orthogonal axes:

```
                      ┌──────────────────────┐
                      │    AXIS 1: PLATFORM   │
                      │  iOS, Android, macOS,│
                      │  Windows, Web, Linux │
                      └──────────┬───────────┘
                                 │
     ┌───────────────────────────┼───────────────────────────┐
     ▼                           ▼                           ▼
┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│AXIS 2: CHANNEL│          │AXIS 3: REGION│          │AXIS 4: TENANT│
│PlayStore, F- │          │US, EU (GDPR),│          │Enterprise A, │
│Droid, AppStore│          │KSA, China    │          │White-Label B │
└──────────────┘          └──────────────┘          └──────────────┘
```

---

## 2. The Single-Axis Filename Law

> **A filename may express at most ONE axis of variation. Compounding multiple axes into a single file suffix is strictly prohibited.**

```
❌ PROHIBITED COMPOUNDING:
  PaymentService.android.playstore.eu.ts
  AuthView.ios.enterprise.xaml

✅ ORTHOGONAL DISPATCH:
  Separate axes using directory overlays or a Layer Registry.
```

---

## 3. The 3-Level Escalation Ladder

Choose the simplest isolation mechanism that satisfies project complexity. Escalate strictly when complexity forces it:

```
[ Complexity Escalates ]
        ▲
        │  Level 3: Layer Registry with Specificity Resolver
        │  (Dynamic multi-dimensional resolution for 3+ intersecting axes)
        │
        │  Level 2: Directory Overlays
        │  (Isolated directory trees mirrored per axis)
        │
        │  Level 1: File Suffixes
        │  (Single-axis differentiation via toolchain naming)
```

### Level 1: File Suffixes (Single-Axis Divergence)
For simple divergence along one axis (usually the OS platform). Supported natively by bundlers (React Native Metro, C# MSBuild):
```
src/
└── features/
    └── biometric/
        ├── BiometricAuth.ts          # Shared Interface / Fallback
        ├── BiometricAuth.android.ts  # Android implementation
        └── BiometricAuth.ios.ts      # iOS implementation
```

### Level 2: Directory Overlays (Two Orthogonal Axes)
When two axes intersect (e.g. Platform × Channel), isolate variations into clean directory mirrors rather than mangled filenames:
```
src/
├── channels/
│   ├── google-play/
│   │   ├── BillingService.ts
│   │   └── AppUpdatePrompt.tsx
│   └── f-droid/
│       ├── BillingService.ts        # FOSS donation fallback
│       └── AppUpdatePrompt.tsx      # In-app APK update checker
└── shared/
    └── billing/
        └── IBillingService.ts
```

### Level 3: Layer Registry & Specificity Resolver (Three+ Axes)
When 3 or more axes intersect (e.g. Platform + Channel + Region + Tenant), static file naming collapses. Use a dynamic registry with a specificity-weight scoring engine:

```typescript
// architecture/layers/SpecificityResolver.ts
export interface LayerCriteria {
  platform?: string;
  channel?: string;
  region?: string;
  tenant?: string;
}

export interface LayerRegistration<T> {
  criteria: LayerCriteria;
  implementation: T;
}

export class SpecificityResolver<T> {
  private readonly registrations: LayerRegistration<T>[] = [];

  register(criteria: LayerCriteria, implementation: T): void {
    this.registrations.push({ criteria, implementation });
  }

  resolve(current: Required<LayerCriteria>): T {
    let bestMatch: T | null = null;
    let highestScore = -1;

    for (const reg of this.registrations) {
      const score = this.calculateScore(reg.criteria, current);
      if (score > highestScore) {
        highestScore = score;
        bestMatch = reg.implementation;
      }
    }

    if (!bestMatch) throw new Error("No matching implementation found for current context.");
    return bestMatch;
  }

  private calculateScore(criteria: LayerCriteria, current: Required<LayerCriteria>): number {
    let score = 0;
    // Specificity Weights: Tenant (8) > Region (4) > Channel (2) > Platform (1)
    if (criteria.tenant) {
      if (criteria.tenant !== current.tenant) return -1;
      score += 8;
    }
    if (criteria.region) {
      if (criteria.region !== current.region) return -1;
      score += 4;
    }
    if (criteria.channel) {
      if (criteria.channel !== current.channel) return -1;
      score += 2;
    }
    if (criteria.platform) {
      if (criteria.platform !== current.platform) return -1;
      score += 1;
    }
    return score;
  }
}
```
