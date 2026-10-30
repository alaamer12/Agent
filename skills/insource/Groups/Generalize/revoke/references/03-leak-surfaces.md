# Leak surfaces - where the data hides outside the prose

Revokers scrub paragraphs and then ship a document whose file properties name the author. This list is the
part people skip.

## Inside the file, outside the body

- **Document metadata** - title, author, company, last-modified-by, comments, keywords, revision history,
  tracked changes and their forgotten deleted-but-present edits, embedded thumbnails.
- **Filename and path** - `acme-incident-2025-03-03.md`, an export from `/Users/marta/Desktop/…`.
- **PDF and Office internals** - producer strings, embedded fonts named after a client, XMP blocks, form-field
  default values, print headers and footers that carry a client name and an internal page number.
- **Images** - what is visible inside them (mailbox headers, browser tabs, Slack sidebars, terminal prompts,
  the customer logo on a slide), plus EXIF/PNG text chunks, GPS tags, software and host names, and the
  screenshot's own window title.
- **Video and audio** - spoken names, visible whiteboards, chat overlays, burned-in timestamps.

## Inside the text, outside the sentence

- **Code blocks and config samples** - example values that were never examples, seed data, internal package
  names, host strings in comments, license headers with a company name.
- **Links and references** - URLs to internal wikis and dashboards (the hostname is the disclosure even when
  the link is dead), citation entries, bibliography DOIs that point at your paper, image URLs hosted on your
  CDN, tracking parameters.
- **Structure** - headings that name the client, table column headers, footnotes, appendices, changelog
  entries, "prepared for" lines, letterheads, page-numbered watermarks, an email quote chain at the bottom.
- **VCS and tooling residue** - commit hashes, branch names, PR numbers, ticket IDs with your prefix, CI log
  URLs, `Co-authored-by:` trailers, generated-file headers with a path.

## Inside the shape of the redaction

- **Partial masks** - `a**@acme.com`, `+44 7*** ***412`, `$2b$...9f3`. Length, domain, and prefix are usually
  enough to confirm a guess.
- **Countable redactions** - "the 14 [REDACTED] accounts" states a fact you meant to hide.
- **Ordering** - alphabetical lists, chronological timelines, or a table sorted by revenue keep identity
  structure even after the names go.
- **Whitespace and casing residue** - a variable renamed to `[CUSTOMER]` inside a snippet whose length still
  matches the original name.

## Inside the writing itself

- **Narrative fingerprint** - an unusually specific incident sequence, an internal tool with no public name, a
  company-specific acronym, an in-joke, a location reference ("the Austin office").
- **Register** - writing voice identifies within a small community; an executive-summary style plus a specific
  metric obsession plus a quarter names a company to someone who was in the room.
- **Dates as events** - "the day after our launch announcement" is searchable in public news.

## The check that catches these

Do not eyeball. Run, in order:

1. `python scripts/revoke.py scan sanitized.md` - mechanical candidates: emails, URLs, IPs, key-shaped
   strings, UUIDs, private-key headers, paths, precise dates and money.
2. `python scripts/revoke.py verify --map map.yaml --out sanitized.md` - every original token, all case and
   split variants, collisions, placeholder hygiene.
3. Metadata sweep by hand or with the tools you have: dump the file's properties, strings in the binary
   container, and any image's text chunks. A `strings` pass over a PDF catches more than any reader will.
4. **Zoom into every image** at 100% and read the pixels: browser chrome, terminal prompts, sidebars.
5. Open every link: does the URL itself disclose, even after the anchor text is generic?
6. Read the document once as a stranger, asking at each element *"could this confirm who wrote this?"*

Surfaces 1 and 2 are cheap and repeatable; 3 through 6 are where the real leaks are found.
