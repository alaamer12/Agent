# Case 4 - a file format whose vendor vanished

**The ask:** "read these exports from a system that died in 2011, and migrate the archive into our current
store."

## Goal, separated

```text
GOAL  : the contents of these files available to search and browse in our current system
VALUE : the records inside - text, dates, attachments, relationships
TEST  : every record in a known sample of files appears in the new store, field for field
```

## Block verification

No service to call, no vendor to ask, no official reader shipped since then. Confirmed by three signals: the
product is discontinued and its domain is dark; the last SDK release predates the file version present; the
support forum's final answers are "export before we shut down". Class: blocker, high confidence.

Note what is *not* blocked: these are the user's own files, already in their hands. Ordinary-user access is
complete - nothing here needs unlocking.

## Routes

- **rebuild from the pattern** - characterize the container and write a reader. Chosen.
- **replace** - a surviving open implementation of the same format, used as the oracle for field meanings.
  Actually the first step of the rebuild, not a separate route.
- **reroute** - any desktop copy still installed in the office could open and export them; slow, but it is a
  door. Kept as the fallback if the reader disagrees with the real thing.
- **reduce** - import only the plain-text body, keep originals untouched as the system of record. Legitimate
  and cheap; chosen *as the interim state*, not as the destination.

## How the rebuild was done honestly

1. Magic bytes and envelope first, before guessing at fields.
2. Version variants enumerated from the corpus itself, not from a single lucky file.
3. Unknown fields preserved verbatim rather than decoded by intuition - a guessed field is a silent
   corruption.
4. A golden set of files whose contents the user could confirm by eye; the reader had to reproduce those
   exactly.
5. **Nothing deleted or rewritten until the golden set passed** - this is the obligation that turns a clever
   parser into a safe migration.

## Failure mode it avoided

A reader that quietly drops one rarely-used field nobody noticed missing, discovered a year later when the
originals were already converted and gone. The acceptance test is what makes that impossible, and the test
was written before the parser.

## Said out loud

The mapping from their fields to ours is inferred from behavior and surviving documentation, so it is labelled
inferred, the fragile spot is named, and the re-check condition is "if a surviving copy of the old client is
found, re-export one folder and diff".
