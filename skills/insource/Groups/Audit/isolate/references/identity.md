# Isolating variants that run together

Contents: when this applies, one identity source, collision checklist, which axes feed identity, enforcement.

Apply this only when variants must be installed and run on one machine at the same time (for example so testers can run stable and several experimental variants together). Otherwise skip it. Everything named below is an example, so adapt it to the platform.

## One identity source

Every identifier two variants might share is a collision. Derive identity from one generated source, keyed by the variant id, instead of typing names in many places. Stable has an empty id and the plain product name. An experimental variant gets the name plus its id. An open set of variants then costs no new hand-written table.

## Collision checklist

- Install location and executable name
- Single-instance locks and watchdog locks
- OS registrations: `[shortcut identity]`, `[URL scheme handlers]`, `[file associations]`, `[autostart entry]`, `[notification ids]`
- Databases, settings, logs, and caches
- Local IPC endpoints: `[named pipes]`, `[sockets]`, `[local ports]`, `[shared memory]`
- Embedded web view data folders
- Update feed and update target, so one variant can never update another
- Mobile identifiers: `[application id]`, `[bundle id]`; without distinct ones the new variant overwrites the old on the device
- Telemetry and crash reports, tagged by variant so test noise does not pollute production numbers
- Database schema: migrations must be additive, or each variant keeps a separate store

## Which axes feed identity

Only axes whose values must coexist should feed identity. Others are metadata stamped into build info and telemetry.

| Axis (examples) | Feeds identity? | Reason |
|---|---|---|
| `[release channel]` | yes | variants must run side by side |
| `[audience or region]` | no, metadata by default | a real user installs the plain product, not a regional copy |
| `[promotion ring]` | no, metadata | the candidate and the stable release are the same bytes |

If testers need audiences side by side, they opt in with an explicit identity suffix. It is not the default.

## Enforcement

Add a lint rule, static analyzer, or test that fails the build when the product name appears as a literal anywhere outside the single identity source. `scripts/scan_axes.py --product NAME` counts such literals and lists the files, which gives the starting list for the migration. Isolation then becomes a build error instead of a discovery during testing.

## Behavior differences between variants

A variant that changes behavior (not just identity) goes through the layer mechanism, never through `if (isCanary)` checks spread across code. The composition root registers implementations by key, and no component asks which variant it is in.
