# Explicit and Implicit References

## Explicit search

After identifying the changed concept, search for:

- Exact names and identifiers
- Related keywords
- The literal value itself (when a hard-coded number or string is meaningful)
- Regular expressions and symbol searches appropriate to the language and tools

Inspect every hit that could reasonably be affected by the semantic change.

## Implicit / conceptual search

Not every dependency contains the exact string that was changed. Use understanding of the system to locate:

- Policy and legal files (Terms of Service, Privacy Policy)
- User-facing copy and help text
- Configuration and feature flags that encode the old assumption
- Documentation and README sections that describe the old behavior
- Related domain modules that consume the changed contract

Treat these as first-class consequences of the fix when the conceptual link is clear.

## Example: hard-coded values

Hard-coded values (often called “magic numbers”) are a frequent illustration of incomplete-fix risk, and many linters flag them. When a fix touches a meaningful value:

1. Search by the constant name **and** by the raw value.
2. Look for the same concept under different names.
3. Decide whether the occurrences should share a single definition or are intentionally separate.
4. Prefer consolidation when future changes would otherwise require coordinated edits in multiple places.

This is one common consistency check, not a mandatory ritual for every fix.
