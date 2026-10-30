# Substitution discipline

One map, applied everywhere, with the map kept out of the artifact. Most leaks are not missed categories -
they are the same entity spelled two ways in two places.

## Build the map before editing

Write the whole inventory table first, then apply it in one pass. Editing while inventing stand-ins produces
`[customer-1]`, `[customer A]` and `[acme]` in the same document - and `[acme]` is worse than no map at all,
because it reads like a placeholder while carrying the original first syllable.

Consistency requirements the script checks:

- one original → exactly one replacement, everywhere, including code blocks and captions;
- one replacement → exactly one original (two entities sharing a placeholder collapses distinctness);
- no replacement that is a prefix, substring, or abbreviation of the original;
- no original surviving in any case, spacing, or split form (`Acme Corp`, `acme_corp`, `ACME-CORP`,
  `Acme-Corp`, `acme.corp`).

## Naming placeholders so the document still reads

A good placeholder carries *role* and *kind*, not the original sound:

| Bad | Why | Good |
|---|---|---|
| `XXX`, `TODO`, `████` | reads as vandalism; tells the reader nothing | `[payment-provider]` |
| `REDACTED` for everything | six different entities, one name, causality lost | `[customer-1]`, `[customer-2]` |
| `[acme-corp-redacted]` | leaks the token it means to hide | `[customer-1]` |
| `[company]` (one, for many) | distinctness dies | `[vendor-a]`, `[vendor-b]` |
| `[REDACTED-KEY-abc123]` | the last four characters are the leak | `[REDACTED-SECRET]` |

Two rules inside the naming:

- **Distinct things stay distinct.** Number them if the role repeats: `[worker-1]`, `[worker-2]`. If the
  distinction between them is what the document teaches, label by role instead: `[writer]`, `[reader]`.
- **Do not decorate with false specificity.** `[some-random-host.example.com]` looks like a real host and
  invites a reader to pattern-match on it. Bracketed role words read as deliberate.

## Code, config and command samples

The hardest surface, because the artifact's usefulness depends on the code still compiling and reading
truthfully:

- Replace the secret in the value, not the whole line: `DB_PASSWORD=[REDACTED-SECRET]` keeps the shape a
  reader needs; deleting the line removes the lesson.
- Hostnames in example commands become `[internal-host]`, and the port stays if the port was the point.
- Stack traces: keep the frame structure and the error class, generalize the paths and user names.
  `/home/marta/projects/billing/…` → `/home/[user]/projects/[app]/…`.
- Sample data in fixtures gets the same map as prose. A fixture named `acme_prod_seed.sql` is a disclosure.
- Never let a placeholder be valid-but-wrong in a way that changes behavior: `[app]` inside a SQL string that
  the reader might paste is a trap; mark examples as examples.

## Protecting the map

The map is the re-identification key. Keep it out of the artifact and out of its neighborhood:

- not in a footnote, appendix, or "editor's note";
- not in the same repo path, commit message, branch name, PR description, or ticket comment;
- not in the sanitized file's own metadata (`title`, `author`, `comments`, tracked changes, revision history);
- not in the filename (`acme-postmortem-sanitized.md` still names acme).

Where the map must be retained for auditability, store it with the original under its existing access
controls, and reference it in the record as "map retained with source" rather than linking to it.

## Doing the edit

Replace longest tokens first so a substring cannot survive inside a compound name (`acme-billing-eu` replaced
after `acme` would leave `[customer-1]-billing-eu`). Then re-run the scan rather than trusting that you
caught every variant, and keep the diff of the pass - reviewing a small diff is easier than reviewing a
rewritten document, and it is the artifact that proves what changed.
