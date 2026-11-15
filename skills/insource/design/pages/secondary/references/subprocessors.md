# Sub-processor List

The named third parties a processor's service depends on, with change-notice rights — GDPR Art.
28(2) made visible. Gate: pointless for hobby/B2C-only projects; *expected the moment EU business
customers arrive* (procurement asks, and a sales team without this page improvises one badly); a
small SaaS may start with the list as a DPA annex and split the page once changes make that
annex lie.

## Must include

1. **The table** — entity name + address/contact, what it processes (role), data categories
   touched, processing location (incl. cloud region), transfer/safeguard mechanism (SCC module,
   adequacy, DPF, certification). A name-only row satisfies neither Art. 28(2) nor a security
   questionnaire.
2. **The dating** — visible "Last updated / Effective"; **versioned prior lists** (dated entries,
   superseded list linked) — an undated in-place PDF overwrite hides the very change the notice
   duty exists for.
3. **Notification mechanics** — subscribe route (the EDPB's Opinion 22/2024 says a webpage alone
   is not "informing": pair the list with active alerts), stated notice period, objection window
   (ICO: state the date by which objections must come), and the objection's consequence — good-
   faith fix, else terminate **the affected services** without penalty (Supabase-style 30/5-day
   windows are the common shape).
4. **Plan/region carve-outs** — EU-residency lists, HIPAA/BAA exclusions, "applies to plans X";
   marked, not implied.
5. **The DPA cross-link** — the list is incorporated by reference and lives at its own URL so the
   DPA annex never goes stale (frozen-annex lists are a common mistake).

## Writing professionally

- Keep the list literally current: adding an AI model vendor or a new CDN is a catalog event in
  the same change as the contract, not a quarterly cleanup.
- Silence ≠ consent under *specific* authorisation; under general authorisation the page + notice
  route *is* the consent machinery — describe it as such, in one line.

## Ask the user - never invent

Every actual sub-processor (audit the stack: hosting, email, payments, analytics, error tracking,
model providers), each role/location/data mix, the notice channel, objection terms.

## Failure patterns

Login-gating the list; "we add vendors and update this page" with no dates or alert route;
missing the sub-sub-processors; list contradicting the DPA annex or the Privacy Policy's vendor
section; copying big-tech fields the project cannot source.
