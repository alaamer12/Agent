# 07 — Capability vs. Policy Separation

> The foundational law of cross-platform decoupling: separating what an operating system can physically do (Capability) from what the application business rules permit (Policy).

---

## 1. The Architectural Boundary

The single most common source of coupling bugs in enterprise cross-platform software is mixing capability checks with business policy checks:

```
┌─────────────────────────────────────────────────────────────┐
│                       POLICY LAYER                          │
│  "Should this feature be permitted right now?"              │
│  Business rules, subscriptions, legal compliance, channels. │
│  e.g., IsUserPremium(), IsGDPRRestricted(), ChannelAllowsIAP│
└──────────────────────────────┬──────────────────────────────┘
                               │ Consumes / Orchestrates
┌──────────────────────────────▼──────────────────────────────┐
│                      CAPABILITY LAYER                       │
│  "Can this physical device execute this action?"            │
│  Hardware, OS APIs, runtime sandbox, permissions.           │
│  e.g., HasCameraSensor(), BiometricsAvailable(), CanSendSMS │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. The Dependency Direction Invariant

> **Rule:** Policy depends on Capability. Capability NEVER depends on Policy, knows nothing about business tiers, and has zero awareness of distribution channels.

```
       ✅ VALID FLOW:
       [ SubscriptionPolicy ] ──> reads ──> [ BiometricCapability ]

       ❌ PROHIBITED FLOW:
       [ BiometricCapability ] ──> checks ──> [ SubscriptionPolicy ]
```

---

## 3. Concrete Case: In-App Billing vs. Third-Party Subscription

### ❌ Coupled Anti-Pattern
```typescript
// ✘ DEFECT: Hardware/OS wrapper making business decisions
export class GooglePlayBillingAdapter {
  async purchasePremiumSubscription(userId: string) {
    // ✘ Checking business region and corporate tenant inside an OS billing adapter!
    if (AppConfig.region === 'EU' && AppConfig.tenant === 'Enterprise') {
      throw new Error("Enterprise users in EU must pay via invoice.");
    }
    return NativeBilling.launchPurchaseFlow("sku_premium");
  }
}
```

### ✅ Decoupled Architecture

#### 1. Pure Capability (Hardware / Store API)
```typescript
// capabilities/store/IInAppBillingCapability.ts
export interface IInAppBillingCapability {
  readonly isAvailable: boolean;
  launchBillingFlow(productId: string): Promise<PurchaseResult>;
}

// capabilities/store/GooglePlayBillingCapability.ts
export class GooglePlayBillingCapability implements IInAppBillingCapability {
  readonly isAvailable = true;
  async launchBillingFlow(productId: string): Promise<PurchaseResult> {
    return NativeGooglePlay.launchPurchaseFlow(productId);
  }
}
```

#### 2. Business Policy (Orchestrator)
```typescript
// policies/billing/SubscriptionCheckoutPolicy.ts
export class SubscriptionCheckoutPolicy {
  constructor(
    private readonly billingCap: IInAppBillingCapability,
    private readonly invoiceGateway: IInvoiceBillingGateway
  ) {}

  async checkout(user: UserProfile): Promise<PaymentReceipt> {
    // Business rule evaluated in the policy layer
    if (user.isEnterprise && user.region === 'EU') {
      return this.invoiceGateway.issueCorporateInvoice(user.id);
    }

    if (!this.billingCap.isAvailable) {
      throw new BusinessException("Store billing is not supported on this device. Please use web portal.");
    }

    return this.billingCap.launchBillingFlow("sku_premium");
  }
}
```
