# Child Privacy

What changes for users under the threshold age (13 in US COPPA terms; 13-16 varies under GDPR
countries - which threshold applies is a jurisdiction question, never a guess).

## The filter first

- The product does not target children and gates by self-declared age: the honest scope is
  **one accurate paragraph** - usually inside the Privacy Policy or ToS ("not directed to children
  under N; we do not knowingly collect; if we learn otherwise we delete - here's how to tell us").
  A full page only when: children CAN plausibly arrive (games, education, consumer social), or
  an app-store/audience category forces it.
- The product IS for children: this becomes the most important document in the set.

## Must include (full page)

1. **What data we collect from a child account** - the minimum, stated per class; child accounts
   collect LESS by design, and the page should prove it.
2. **Age assurance, not age declaration** - where law now demands a method: UK Online Safety Act
   (since 25 Jul 2025, porn and services likely accessed by children need *highly effective*
   age assurance - Ofcom is fining and explicitly rejects birthday self-declaration and paywall
   tricks); EU DSA Art. 28 (minor protection + no profiling ads to minors); app-store age
   **signals** the developer must read and act on (US state store-accountability laws: UT, TX,
   LA, AL, 2025-26; Australia's under-16 platform duty live Dec 2025). The page names the method
   actually deployed, what the assurance data is used for and **when it is deleted** (verification
   artifacts reused or retained are a separate scandal waiting to happen).
3. **Parental consent** - the mechanism (verified email, payment card, in-person) named truthfully;
   COPPA's amended rule (effective 2025, full compliance Apr 2026): biometrics are now personal
   information, third-party targeted ads need separate opt-in, retention has limits, mixed-
   audience services cannot hide behind "not directed at children". COPPA-shaped consent flows
   have a defined list of acceptable verification methods - ASK which the product implements.
4. **No behavioral ads / no selling** - the promise, if true, in one sentence.
5. **Parent rights** - access, correct, delete, revoke; the route to exercise.
6. **What the child sees** - default-private settings, contact restrictions, and a reporting route
   a child can actually use.

## Writing professionally

- A parent reads this once, scared, in a hurry: short sections, first sentence = what data does my
  kid generate and who can see it.
- The claim must match the product's real settings - a child-privacy page promising "profiles are
  private by default" while the app defaults to public is the worst document this skill can ship.

## Ask the user - never invent

Whether minors arrive; the age threshold(s) by market; the **age-assurance method actually
deployed** where law demands one (and its data's lifecycle); consent verification actually
implemented; data classes for child accounts; the delete-on-discovery path; which store age
signals the product reads.

## Failure patterns

Birthday self-declaration presented as compliance (explicitly rejected by Ofcom enforcement);
"not directed at children" on a mixed-audience service (the amended COPPA definition closes that
door); reusing verification artifacts for other purposes; promising store-grade defaults the app
does not set; silence on behavioral ads while the analytics SDK serves them.
