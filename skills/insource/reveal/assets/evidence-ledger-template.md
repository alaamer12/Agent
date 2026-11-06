# Evidence ledger - <project name>

One row per finding. This is the artifact the report is written *from*, and the thing the final defect audit
in [`06`](../references/06-research-quality-and-evidence.md) runs against. A claim with no row is a claim
that does not go in the report.

Columns: `competitor | dimension | claim | value | label | source_url | date | method`

- **dimension:** A-J (name, features, market, language, history, users, business, tech, positioning, status)
- **label:** `fact` (primary/corroborated source states it) · `estimate` (inferred - `method` required) ·
  `assumption` (reasoned, no direct evidence - low confidence, never load-bearing)
- **date:** the publication date if known, else the access date (YYYY-MM-DD)
- **method:** required for every `estimate`; empty for `fact`/`assumption`

## Competitor registry (deduped)

| id | name | website | found via (axis / source family) | class | similarity | notes |
|---|---|---|---|---|---|---|
| c1 | <name> | <url> | problem-axis / GitHub | direct | 82 | |
| c2 | ... | | | | | |

## Findings

| competitor | dimension | claim | value | label | source_url | date | method |
|---|---|---|---|---|---|---|---|
| c1 | E history | founded | 2019 | fact | https://.../about | 2025-11-06 | |
| c1 | E history | first public launch | 2021 | fact | https://web.archive.org/.../2021... | 2021-04-02 | |
| c1 | F users | monthly active users | ~50,000 | estimate | https://play.google.com/... | 2025-11-06 | 500k+ downloads × ~10% typical retention |
| c1 | F users | play store installs | 500,000+ | fact | https://play.google.com/... | 2025-11-06 | |
| c1 | D language | supports Arabic UI | no | fact | https://.../languages | 2025-11-06 | |
| c1 | I positioning | top user complaint | sync is unreliable | fact | https://.../reviews?page=3 | 2025-11-06 | |
| c1 | J status | last product update | 14 months ago | fact | https://.../changelog | 2025-11-06 | |
| c1 | J status | likely winding down | — | assumption | (reasoning: dead changelog + unanswered support) | 2025-11-06 | |

## Similarity reasoning (one per scored competitor)

| competitor | overall | per-axis (idea/problem/audience/features/workflow/model/market/ux/tech/value) | why this score, not higher/lower |
|---|---|---|---|
| c1 | 82 | 90/85/80/75/70/60/40/70/50/85 | same idea+audience+value, but English-only and no local payments → market axis 40 pulls it below 90 |

## Conflicts & corroboration

| claim | sources that disagree / corroborate | resolution |
|---|---|---|
| c1 user count | company PR "100k users" (2022) vs traffic estimate | kept 50k MAU estimate; PR figure is registered-users-since-inception, different metric - noted |

## Search frontier log (proves diminishing returns)

| round | axes/languages/sources newly tried | new competitors found |
|---|---|---|
| 1 | core-concept × EN × Google/PH | c1, c2, c3 |
| 2 | problem-axis × AR × native web + Play KSA | c4, c5 |
| 3 | snowball c1's AlternativeTo + HN threads | c6 |
| 4 | feature-axis × DE × G2/Capterra + Wayback graveyard | none new |
| 5 | audience+model × TR × local directories | none new → **two quiet rounds, stop** |

## Gaps / limitations (carried into the report)

- <source> not reachable from this environment (login-walled / regional store / paid DB) - may hide <what>.
