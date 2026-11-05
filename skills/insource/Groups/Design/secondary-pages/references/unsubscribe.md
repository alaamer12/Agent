# Unsubscribe / Email preferences

Needed the moment the product sends anything a user did not transact for: newsletters, digests,
product news, marketing. No non-transactional mail, no page (the filter stated in the report).

## Must include

1. **The instant route** - one-click unsubscribe ([RFC 8058] `List-Unsubscribe-Post` behavior in
   bulk mail) alongside the classic link; web recipients [do] see both in most mail clients.
2. **Effective time, truthfully** - "stopped immediately" or "within up to N business days": the
   honest number from the sending pipeline (ASK; the generator default "may take 10 business days"
   on a pipeline that stops instantly is just as wrong as the reverse).
3. **Preference granularity** [recommended] - the choices instead of one kill-switch: digest
   frequency, categories, product updates; per-category opt-out where the law splits them
   (marketing vs transactional-adjacent is the ASK).
4. **What unsubscribe does NOT stop** - the explicit list: receipts, security alerts, ToS-change
   notices - "account-related messages continue" is the sentence that prevents a support ticket.
5. **The logged-out path** - unsubscribe by email address with no login (a request form that
   requires signing up for an account to leave the mailing list is the classic broken door).
6. **The mail domain honesty** - the sender domains listed match the real ones (config-driven
   values - `engineering.md` §1; a wrong sender-domain claim teaches scammers to fake the right
   one).

## Writing professionally

- Zero guilt copy: no "you'll miss out", no five-step maze; the page's job is to make leaving as
  easy as joining was.
- A processed unsubscribes as a state change with a date; the confirmation page says what changed
  and shows the preferences center when it exists.

## Ask the user - never invent

Mail classes actually sent; pipeline stop behavior and timing; the preferences surface truth;
transactional vs marketing split per law frame; the one-click header reality.
