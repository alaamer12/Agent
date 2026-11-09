# Worked Cross-Platform Directory Trees

> Concrete filesystem architectures demonstrating proper multi-platform code organization across escalating levels of project complexity.

---

## Tree 1: Level 1 Escalation — Single-Axis Platform Divergence (Standard Mobile App)

Appropriate when the only axis of variation is the operating system (e.g. React Native / Expo):

```
src/
├── app/
│   ├── NavigationShell.tsx              # PlatformConcept: Dispatches to Tabs on Phone, Drawer on Tablet
│   └── routes.ts
│
├── features/
│   └── funds/
│       ├── state/
│       │   └── useFundListState.ts      # Pure shared state (100% agnostic)
│       └── views/
│           └── FundCardView/
│               ├── FundCardView.tsx     # View Barrel (connects ViewModel to layout)
│               ├── _FundCardDesktop.tsx # Layout 1: Wide multi-column format
│               └── _FundCardPhone.tsx   # Layout 2: Compact vertical format
│
├── shared/
│   ├── capabilities/
│   │   ├── biometrics/
│   │   │   ├── IBiometrics.ts           # Contract
│   │   │   ├── Biometrics.android.ts    # Level 1 single-axis suffix
│   │   │   └── Biometrics.ios.ts        # Level 1 single-axis suffix
│   └── ui/
│       ├── primitives/
│       │   └── Button/
│       │       ├── Button.tsx           # Shared API
│       │       ├── _ButtonSurface.android.tsx
│       │       └── _ButtonSurface.ios.tsx
│       └── responsive/
│           └── BreakpointContainer.tsx  # Dynamic width resolver
```

---

## Tree 2: Level 2 Escalation — Two Orthogonal Axes (Platform × Distribution Channel)

Appropriate when variations exist across both OS targets and deployment channels (e.g., Google Play vs. F-Droid):

```
src/
├── channels/                            # Axis 2: Distribution Channel Overlays
│   ├── google-play/
│   │   ├── billing/
│   │   │   └── StoreBillingGateway.android.ts # Level 1 Platform suffix inside Channel overlay
│   │   └── updates/
│   │       └── InAppUpdateManager.ts
│   └── f-droid/
│       ├── billing/
│       │   └── StoreBillingGateway.ts         # Pure FOSS donation fallback
│       └── updates/
│           └── InAppUpdateManager.ts          # Checks GitHub releases / direct APK
│
├── core/
│   ├── billing/
│   │   └── IStoreBillingGateway.ts      # Abstract Contract
│   └── updates/
│       └── IInAppUpdateManager.ts       # Abstract Contract
│
└── features/
    └── checkout/
        └── CheckoutCoordinator.ts       # Depends purely on core/ contracts
```

---

## Tree 3: Level 3 Escalation — Enterprise Multi-Axis Layer Resolution

Appropriate for complex white-label products varying across Platform, Channel, Region, and Tenant:

```
src/
├── layers/
│   ├── specificity/
│   │   ├── LayerCriteria.ts             # Criteria interface (Platform, Channel, Region, Tenant)
│   │   ├── SpecificityResolver.ts       # Scoring engine
│   │   └── LayerRegistry.ts             # Global registry
│   │
│   ├── defaults/                        # Base layer (Specificity = 0)
│   │   ├── auth/
│   │   │   └── StandardAuthFlow.ts
│   │   └── branding/
│   │       └── DefaultThemeTokens.ts
│   │
│   ├── regions/                         # Region overlays (Specificity = 4)
│   │   ├── eu/
│   │   │   └── CookieConsentPolicy.ts
│   │   └── ksa/
│   │       └── HijriCalendarAdapter.ts
│   │
│   └── tenants/                         # Tenant overrides (Specificity = 8)
│       └── enterprise-corp/
│           ├── auth/
│           │   └── OktaSsoAuthFlow.ts
│           └── branding/
│               └── EnterpriseTokens.ts
│
└── main.ts                              # Resolves active configuration on app boot
```
