# Research quality and the evidence ledger

The report is only as trustworthy as the sourcing under it. These are the standards every run holds to, and
the ledger that makes them checkable.

## The fifteen standards

1. **Search broadly before concluding.** No verdict after a thin pass.
2. **Multiple queries and phrasings per axis**, not one.
3. **Search in other languages** wherever the target market is not English-only - the local competitors are
   invisible otherwise.
4. **Search individual features and problems**, not only the whole concept.
5. **Investigate competitors found by competitors** - alternatives lists, comparison pages, integration
   partners.
6. **Follow references, backlinks, discussions, and "alternatives to" recommendations.**
7. **Search old, discontinued, abandoned, and open-source implementations** - prior art and cautionary tales.
8. **Prefer primary sources**: official site, repo, docs, pricing page, app-store listing, company
   announcements, over third-party commentary about them.
9. **Validate important claims with independent sources** - a user count from the company's own PR is weaker
   than the same figure triangulated from a traffic estimate and a review count.
10. **Attach a source URL to every finding.**
11. **Record publication or access dates** - a 2021 funding figure and a 2025 one are different facts.
12. **Label every claim**: verified fact / estimate (with method) / assumption. No unlabeled numbers.
13. **Never fabricate competitor information or statistics.** An unknown is an unknown.
14. **Report inaccessible platforms and limitations honestly** - name what could not be reached.
15. **Continue to diminishing returns**, not to a satisfying count.

## The three labels, used exactly

| Label | Means | Rule |
|---|---|---|
| **fact** | a primary or independently corroborated source states it | cite URL + date |
| **estimate** | inferred from public indicators | cite the indicators **and the method** ("~50k MAU est., from 500k downloads × typical 10% retention") |
| **assumption** | reasoned without direct evidence | mark as low-confidence; never load-bearing in the verdict |

A number with no label is a defect. Before the report is written, the ledger is audited against the defect
list - unlabeled findings, estimates without a method, facts without source or date, store/proxy figures
presented as verified user counts, similarity scores without reasoning or per-axis breakdown - and every hit
is fixed or downgraded to its honest label. The distinction the report
must never blur: **website visits, app downloads, followers, and GitHub stars are not active users** - they
are proxies that feed estimates, with the method shown.

## The evidence ledger

Every finding, from the first competitor to the last, is recorded in the ledger
(`assets/evidence-ledger-template.md`) as one row:

`competitor | dimension | claim | value | label (fact/estimate/assumption) | source URL | date | method (if estimate)`

The ledger, not memory, is what the report is written from. Its jobs:

- **Traceability** - any sentence in the report can be pointed at the row that earned it, and a reader can
  re-open the URL.
- **Consistency** - the same competitor's "founded 2019" cannot quietly become "founded 2021" in a later
  section, because both cite the same row.
- **Gap visibility** - empty cells are visible as empty cells, which is what makes "we could not find X" a
  reportable finding rather than an accidental omission.
- **Anti-fabrication** - a claim with nowhere to put a URL is a claim that does not go in the report.

## Cross-source validation before synthesis

Before scoring, reconcile: merge duplicate competitor entries (same product across four directories), resolve
conflicting facts by preferring the dated primary source and noting the conflict when it survives, and flag
any single-source load-bearing claim as needing a second source or a lower confidence. This is the same
"spot-check a sample of claims before writing" discipline `mine` applies - a plausible URL that 404s, or a
cited page that does not contain the claim, is how an invented finding surfaces, and it is cheapest to catch
before the verdict is built on it.
