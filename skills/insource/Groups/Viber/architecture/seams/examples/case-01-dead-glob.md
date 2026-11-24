# Case 01 — the wall that policed a directory that no longer existed

*Names, paths and numbers here are illustrative. The shape is what transfers.*

## The setup

A tree with a boundary rule: the third party may be named in one tier only. The auditor was real, the
registry was real, the rule codes were documented, and the gate ran on every change. For months it
reported zero offences, and people correctly described the boundary as "held".

## The rule as configured

```
code:   VENDOR_TAG_IN_MARKUP  (hard-zero)
scope:  src/features/**/*.tmpl
```

`src/features/**` had been renamed in a reorganisation — files moved to a sibling directory, the old
name deleted. The auditor's scope string was not part of that change, because the change was about
where screens live, not about the wall.

## What green meant

Nothing was wrong with the auditor's matching logic; it matched its pattern faithfully and found no
files, so it reported no offences. Zero offences from an empty scope is arithmetically identical to
zero offences from a clean tree, and the output did not distinguish them. Two files that used the
vendor tag directly, in the new location, were reviewed, approved, and shipped — with three separate
reviewers looking at markup that the rule existed to refuse.

## How it surfaced

Not through the gate. Through an unrelated question: "how many files does this rule actually scan?"
Nobody could answer, so someone printed the match count per scope entry. One entry: **0 files**.

## What was added

1. A liveness assertion in the gate: **every configured path/glob must match at least one real
   file**, else fail. (`scripts/glob-liveness.mjs`, pointed at the same config the auditor reads.)
2. The match count printed per rule on every run, so "0 files scanned" is visible even when the
   liveness check is not what fails.
3. The rule's reason moved out of its message into the doc the code names, so a stale scope string
   could be spotted by a reviewer without reading the matcher.

## The general form

Any rule whose *scope* is data, and whose scope is not part of the change that moves the files. A
rename, a folder split, a tier promoted into its own package, a directory that becomes generated — all
of them take an existing wall out of scope without touching the wall. The wall does not complain,
because complaining is what it does when it finds something, and it finds nothing.

Severity note: this failure mode is invisible precisely for **hard-zero** rules. A ratcheted rule
carries a count, and a count that suddenly has no keys is a smell. A hard-zero rule carries absence,
and absence is its own alibi.
