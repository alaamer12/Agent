# 00 — The anatomy of a ladder

A **ladder** is an ordered set of tests evaluated until one wins. Two rails, many rungs: the rails
are the flow (in, then out) and the rungs are conditions paired with outcomes. Every ladder in every
field — PLC rung logic, UX laddering, XACML policy combination, a routing table, an error-classifier —
is the same shape with different choices filled in.

The vocabulary is standard in one field and invented in another. Use these terms and the mapping
table when writing or reviewing one, so a reader in a new domain is not guessing.

## Vocabulary

| Term | Means |
|---|---|
| **rung** | One test and its outcome. The unit of the ladder. |
| **rail** | The fixed flow: entry, traversal, exit. Not a rung. |
| **facts / request** | The input the rungs are matched against. |
| **match** | A rung whose condition is satisfied by the facts. |
| **winner** | The single rung that produced the result. In "all matches" mode: the set of winners. |
| **fallback / fallthrough** | The result when no rung matches. Every ladder has one; name it explicitly. |
| **short-circuit** | Stop traversing once the outcome is decided. |
| **tier** | A named group of rungs whose relative order is fixed by the engine, not by the author. |
| **scope** | A named group of rungs whose relative order is author-controlled, and whose order among scopes is engine-controlled. |
| **specificity** | How narrow a rung is, used instead of or before position. |
| **audit trail** | Which rung won, plus which rule or record it came from. |

## The seven slots of any ladder

1. **Ordering key** — position, priority number, specificity, or a fixed tier. Pick one; mixing keys
   without stating precedence is the main source of "why did that win" bugs.
2. **Matching mode** — first match wins (short-circuit), all matches combined, or last match wins.
3. **Combining rule** — in all-match mode, how winners collapse: strictest wins (deny-overrides),
   most permissive wins (permit-overrides), most specific wins, or error on ambiguity.
4. **Scoping** — is there more than one set of rungs, and how do the sets order among themselves?
5. **Fallback** — the default outcome, and whether reaching it is normal or an error.
6. **Effects** — does a rung only return a value, or also act (mutate, call, log)? Actions inside
   predicates are where ladders go wrong, because matching is expected to be replayable.
7. **Audit** — what the result carries about the winner: rule id, scope, tier, source file, version.

## Semantics, with the canonical names

These are the same choices as XACML's policy/rule combining algorithms, so use those names in
security contexts and plain names elsewhere.

| Here | Standard name | Contract |
|---|---|---|
| First match wins | `first-applicable` | Stop at the first true rung. Order is total and author-controlled. |
| All matches, most restrictive | `deny-overrides` | Evaluate every rung; if any denies, deny. Order-independent. |
| All matches, most permissive | `permit-overrides` | Evaluate every rung; if any allows, allow. Order-independent. |
| All matches, exactly one allowed | `only-one-applicable` | More than one match is an error. Detects shadowed and overlapping rules. |
| Last match wins | (inverse of first-applicable) | Latest rule replaces earlier verdicts. Rewrite as first-applicable over a reversed list. |

## Invariants worth enforcing

Write these as tests, not as comments.

1. **Totality** — the ladder answers for every input. The fallback is a value, not "function returns
   None somewhere" or a crash.
2. **Determinism** — same facts, same winner, same result. Requires a tie-break beyond the sort key.
3. **No unreachable rung** — every rung can win for some input. Detect by shadow analysis or by
   requiring at least one test per rule id.
4. **No action in a condition** — matching is pure. Effects belong to the outcome, and outcomes
   happen once, after the winner is known.
5. **The fallback is a designed answer** — for safety ladders, the fallback is the restrictive one;
   a malformed rule is never a silent pass.
6. **Audit is never empty** — the result always names the winner. `result == fallback` without a
   rule id means you cannot answer "why".

## Anti-patterns

- **Shadowing**: a broad rung above a narrow one makes the narrow rung dead code. This is the single
  most common ladder defect. `15` gives the probe that reports it; `19` cites the same failure documented
  in production rule engines.
- **Implicit ordering**: relying on the order rules were appended, or on a map's iteration order, or
  on the order files load. Ordering must be data (priority, tier, explicit list), never an accident.
- **Order-as-security**: a flat first-match list where a broad `allow` sits above a specific `deny`.
  Correct only because nobody reordered the list. Use tiers (`13`) or strictest-wins (`14`).
- **The missing else**: a chain without a final branch, so "unknown" leaks as `None`, `undefined`, or
  an unhandled exception. Fails open.
- **Condition with a side effect**: a predicate that writes, calls, or mutates — the ladder may be
  re-evaluated (chaining, retry, replay), and the effect happens twice.
- **Two ordering keys in one list**: position for some rules, priority for others, unspecified
  between them. The engine picks; you did not.
- **Priority as a gap-toothed numbering** (`10, 20, 30`) *combined with* stable-sort-by-identity —
  gaps imply intent to insert, identity tie-break then makes insertion order meaningless. Choose one
  convention and document it.

## Reading order

Shapes to write by hand: `01` if-chain · `02` rules table · `03` scope chain · `04` guard
clauses · `05` match tree · `06` decision table in config · `07` priority numbers ·
`08` state/dispatch matrix · `09` pattern matching and switching · `10` chain of responsibility ·
`11` attempt and escalation · `12` statechart guards and visual builders.
Structures that order the shapes: `13` fixed tiers · `14` semantics and combining rules.
How to be sure it is right: `15` testing, shadows and audit · `16` selection guide.
Working on a real codebase rather than designing from scratch: `20` find the ladders that exist ·
`21` report findings, offer the shapes that fit with trade-offs, record the chosen decision ·
`22` express it as code without the nest.
Other meanings of the word: `17` PLC ladder logic and stepped layouts · `18` abstraction, inference and
research laddering. Where every claim came from: `19` sources.
