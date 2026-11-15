# US State Privacy Notices

The artifacts US state law (2026: ~20 comprehensive laws) adds **around** the Privacy Policy: the
Notice at Collection, the opt-out destination, and the GPC duty. Gate: only when the project is in
scope per state (thresholds below) — a small US-only site ships one honest Privacy Policy plus a
GPC-honoring line, not twenty state addenda. Rhode Island is the outlier: its standalone website
privacy-notice duty applies regardless of the usual thresholds.

## The artifact set (which page, which law)

1. **Notice at Collection** — categories collected, purposes, retention, sale/share status, third
   parties, contact — encountered *at or before* collection (site + every form + app download/
   settings), not buried in the policy; separate short page or per-surface card, linked from the
   footer. CCPA regs §7012: collection without the notice is the violation.
2. **"Do Not Sell or Share My Personal Information" / opt-out page** — required when selling or
   sharing (§7013); exact wording labels, the CPPA **opt-out icon** beside "Your Privacy Choices",
   a **working** mechanism on that page (a banner-only "opt-out" with no footer link is the
   enforcement pattern); the Alternative Opt-out Link form of §7015 exists for the frictionless-
   signal case — and even then the *notice* stays mandatory.
3. **Limit notice** for sensitive personal information used beyond permitted purposes (§7014) —
   or state truthfully in the policy that SPI is used only for permitted purposes and no link is
   needed.
4. **Financial-incentive notice** (rewards/referral/discount programs) — may be a policy section
   (§7016) with a direct link.
5. **GPC / opt-out preference signals** — detect, honor, **surface that you honored** (§7025 since
   1 Jan 2026; Sept 2025 multistate sweep; Tractor Supply $1.3M included an ineffective GPC path);
   Colorado's universal mechanism duty since Jul 2024. The cookie page states the same behavior —
   one owner for the mechanism description (this doc), the cookie page links.
6. **Authorized-agent instructions + request methods** — ≥2 methods incl. one online (2027: web
   form/portal + email for online-only businesses, SB 923); these blocks live **inside** the
   Privacy Policy's US-rights section.

## Thresholds (count per state, ASK the user their reach)

Typical triggers: ~100k residents of that state; CA adds $26.625M revenue or 50%-of-revenue-from-
selling tests; MT 25k; CT 35k (Jul 2026) **or any sensitive-data processing regardless of size**;
TX has no count but exempts SBA-defined small businesses (sensitive-data sale still needs
consent); RI 35k or 10k+20%. Data brokers: CA registration + DROP delete platform. Nonprofits and
governments largely out. The honest output of the check may be "you are outside these laws today;
this line about GPC is still worth shipping."

## Failure patterns

GDPR banner copied as the US answer; "we may sell data" text with no working mechanism; stale
"last updated"; assuming national headcount = exemption; claiming no-sale while ad trackers run
(the FedEx $2.975M, Nov 2026, fact pattern); recommending the whole set to a solo dev (scale gate
above).
