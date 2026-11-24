# Case 04 — the payment gateway that lived in nine files

*Names, packages and numbers here are illustrative. The shape is what transfers. Backend instance of
the doctrine — the same audit, walls and ledger, with no widget in sight.*

## The setup

A subscription service on [Stripe or any gateway vendor]. Checkout, webhooks, refunds, invoices, and
the admin panel all worked. The billing module was the crown jewel of the codebase and the one thing
nobody could move. The contract seam rule said the swap must be a one-file edit; nobody had ever
tested that, because the price question was uncomfortable.

## The audit (the doctrine's §6 test, run mechanically)

The grep is the whole method: vendor package named in `package.json` / `pom.xml` / `go.mod`, then
search the tree for its import, excluding the one seam directory that should own it.

```
vendor import found in:  checkout/service.ts     webhook/handler.ts
                         refunds/service.ts      invoices/pdf.ts
                         admin/billing.ts        jobs/dunning.ts
                         reports/mrr.ts          tests/helpers/factories.ts
                         lib/stripe.ts           ← the one honest file
```

Nine files outside the seam knew the vendor. But the leak had three faces, and the import count was
the least of them:

| Leak | Where | Why the import wall alone misses it |
| --- | --- | --- |
| **type leak** | `checkout/dto.ts` exported `Stripe.Charge` upward; two API response types embedded it | type-only imports erase at build — no runtime import, no vendor name in `dist/` |
| **string leak** | `"Stripe"` written into the `payment_provider` column by checkout; the webhook replay job matched on it; an admin filter dropdown listed vendor names | data, not code — a rename of the constant is a migration, not a refactor |
| **idiom leak** | `charge.succeeded` event strings matched in three switch statements | the vendor's vocabulary wearing our enum's clothes |

## What the seam actually looked like after the fix

One file (plus its config rows) per capability. Every world names it differently, seals it identically.

```ts
// billing/gateway.ts — the seam. vendor knowledge ends here.
import Stripe from "stripe";
import { GATEWAY_SECRET, GATEWAY_WEBHOOK_SECRET } from "../config.js";

export interface PaymentGateway {
  authorize(order: Order): Promise<Charge>;
  capture(chargeId: ChargeId): Promise<Charge>;
  refund(chargeId: ChargeId, amount?: Money): Promise<Refund>;
  parseWebhook(raw: Request): Promise<GatewayEvent>; // our events, not charge.succeeded
}
// Charge, ChargeId, Money, GatewayEvent: OUR types, converted at this boundary — the contract seam.
```

```go
// billing/gateway/stripe.go
type Gateway interface {
	Authorize(ctx context.Context, o Order) (Charge, error)
	Capture(ctx context.Context, id ChargeID) (Charge, error)
	Refund(ctx context.Context, id ChargeID, amount *Money) (Refund, error)
	ParseWebhook(r *http.Request) (Event, error)
}
// the stripe import exists only in this package's stripe.go; cmd/ and domain/ never name it.
```

```csharp
// Billing/Gateway/IPaymentGateway.cs — interface is the seam location; registration is the pin.
builder.Services.AddScoped<IPaymentGateway, StripeGateway>();  // ← the one line that names the vendor
// domain services inject IPaymentGateway; none of them can compile against the SDK.
```

The webhook verifier's `replay_provider` column now stores **`gateway`**, an our-vocabulary value;
the vendor name lives in the seam's config table with a reason and an owner.

## The gates that made it stick

```
VENDOR_IMPORT_OUTSIDE_SEAM   hard-zero   scope: domain/**, api/**, jobs/**     fixture: planted fake import, must fire
VENDOR_TYPE_LEAK             hard-zero   scope: exported signatures            enforced at the type checker + audit code
GATEWAY_IDIOM_IN_CODE        hard-zero   vendor event strings outside the seam
PROVIDER_LITERAL_IN_DATA     ratcheted   own baseline, judgment attached: a legacy row that still says "stripe"
                                         is data archaeology, not a bug — shrink per migration batch, re-bless each drop
```

The ratchet earned its complexity exactly once: the existing rows. The hard-zeros stopped the tide the
day they landed, and the starting count of the ratchet (34, from `reports/mrr.ts` and two admin
screens) was stated in the same commit as the wall — nothing frozen silently.

## The swap, rehearsed

Quarterly drill: a throwaway branch replaces the gateway by adding `billing/gateway/other.ts`,
flipping one DI/config line, and running the suite. **Files touched: 1 added, 1 line changed.** That
number in the register's "Swap touches" column is the artifact the doctrine accepts as proof — not
an opinion about decoupling.

## The general form

Any backend capability answers this shape: the vendor is *convenient* at first (checkout worked!),
the leak is *three-part* (import, type, string), and the seam is only real when the swap is rehearsed.
A payment gateway, an LLM behind `complete(prompt)`, a mail provider, a storage driver, a clock —
same audit, same three walls, one number as proof: files touched on swap = 1.
