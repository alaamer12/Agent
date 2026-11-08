# Multi-Axis Layer Resolution Walkthrough

> A step-by-step trace of how the Specificity Resolver evaluates conflicting registrations and selects the exact winning implementation across four intersecting dimensions: Platform, Distribution Channel, Geographic Region, and Corporate Tenant.

---

## 1. The Multi-Axis Collision Context

Consider an enterprise cross-platform banking client:
- **Platform:** Android
- **Channel:** Google Play Store
- **Region:** European Union (EU)
- **Tenant:** EnterpriseAlpha (VIP Enterprise Customer)

Each dimension provides its own variation for `IAuthenticationFlow`:

| Registration | Target Dimensions | Provided Implementation |
| :--- | :--- | :--- |
| **Registration A** (Default Base) | `{}` | `StandardUsernamePasswordAuth` |
| **Registration B** (Channel Overlay) | `{ channel: 'google-play' }` | `GoogleSmartLockAuth` |
| **Registration C** (Regional Compliance) | `{ region: 'EU' }` | `EUSCAStrongCustomerAuth` |
| **Registration D** (Tenant Customization) | `{ tenant: 'EnterpriseAlpha' }` | `CustomSsoAuth` |
| **Registration E** (Tenant + Platform) | `{ tenant: 'EnterpriseAlpha', platform: 'android' }` | `CustomAndroidSsoAuth` |

Which implementation should be instantiated at runtime? If resolved ad-hoc, bugs arise where regional security overrides corporate SSO, or channel defaults overwrite tenant branding.

---

## 2. The Specificity Weight Formula

Specificity follows the law of constraint closeness:

$$\text{Score} = (W_{\text{tenant}} \times 8) + (W_{\text{region}} \times 4) + (W_{\text{channel}} \times 2) + (W_{\text{platform}} \times 1)$$

Where:
- If a declared criterion fails to match the runtime environment, the registration is **disqualified** ($\text{Score} = -1$).
- If a declared criterion matches, it adds its weight to the total score.

---

## 3. Step-by-Step Resolution Trace

```typescript
import { SpecificityResolver } from '@/architecture/layers/SpecificityResolver';
import { IAuthenticationFlow } from './IAuthenticationFlow';

const resolver = new SpecificityResolver<IAuthenticationFlow>();

// 1. Register all variants
resolver.register({}, new StandardUsernamePasswordAuth()); // Score = 0
resolver.register({ channel: 'google-play' }, new GoogleSmartLockAuth()); // Score = 2
resolver.register({ region: 'EU' }, new EUSCAStrongCustomerAuth()); // Score = 4
resolver.register({ tenant: 'EnterpriseAlpha' }, new CustomSsoAuth()); // Score = 8
resolver.register({ tenant: 'EnterpriseAlpha', platform: 'android' }, new CustomAndroidSsoAuth()); // Score = 8 + 1 = 9

// 2. Runtime Context
const runtimeContext = {
  platform: 'android',
  channel: 'google-play',
  region: 'EU',
  tenant: 'EnterpriseAlpha'
};

// 3. Execution Trace:
// - StandardUsernamePasswordAuth: matches (Score = 0)
// - GoogleSmartLockAuth: channel matches (Score = 2)
// - EUSCAStrongCustomerAuth: region matches (Score = 4)
// - CustomSsoAuth: tenant matches (Score = 8)
// - CustomAndroidSsoAuth: tenant matches (+8) AND platform matches (+1) (Total Score = 9)

const activeAuthFlow = resolver.resolve(runtimeContext);
// --> Yields CustomAndroidSsoAuth (Score 9 wins unequivocally)
```

---

## 4. Conflict Handling & Strict Disqualification

What happens if an implementation declares `{ region: 'US' }` when the app runs in the EU?
```typescript
// Score calculation:
if (criteria.region !== current.region) {
  return -1; // IMMEDIATE DISQUALIFICATION
}
```
Even if that registration had matched on Tenant, Platform, and Channel, a single mismatch on any declared dimension immediately disqualifies it, preventing invalid cross-border or incompatible deployments.
