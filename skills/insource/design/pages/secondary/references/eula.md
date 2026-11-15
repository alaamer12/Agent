# EULA / Software License

The license grant for software the customer *installs and runs*. Gate hard: apps distributed only
through Apple/Google stores mostly do **not** need one (the stores' standard EULA/terms apply;
Apple custom licenses must carry its Minimum Terms — contract with the developer, store terms
prevail, refunds through Apple); hosted SaaS is ToS + DPA territory, not a EULA. The real need:
direct desktop/on-prem installers, SDKs/firmware/embedded, enterprise and volume licensing.

## Must include

1. **Grant, bounded** — what is licensed (versions? environments?), seats/devices/entities, term
   vs perpetual, sublicensing stance.
2. **Restrictions that matter** — reverse engineering, benchmarking/publishing performance, key
   sharing, circumvention of license checks — each a deliberate choice, not a wall of boilerplate.
3. **Updates and versions** — what the license covers across versions; forced-update truth
   (does it phone home: activation/telemetry gets its own disclosure line and a privacy-policy
   link, never silence).
4. **Ownership and third-party notices** — binary OSS attribution route.
5. **Warranty disclaimer + liability cap** — honest "AS IS where law allows"; consumer law (EU,
   some US states) caps what a EULA can disclaim for consumers — say "to the extent permitted by
   law" and mean it.
6. **Termination** — what ends the license, delete-copies duty, what survives.

## Writing professionally

- One license per distribution shape; the page names which applies where both exist (store vs
  direct build).
- A EULA is not a privacy policy, not a refund policy — link, per `catalog.md` ownership.

## Ask the user - never invent

Distribution channels per artifact; telemetry/activation reality; version/upgrade promise;
enterprise/volume options; OSS mix.

## Failure patterns

A bespoke EULA on an app-store-only mobile app (unenforceable past store terms, template bloat);
installed-software EULA language pasted onto a hosted product; conflicting refund promises between
EULA and store; license checks described as "cracking" to ordinary users.
