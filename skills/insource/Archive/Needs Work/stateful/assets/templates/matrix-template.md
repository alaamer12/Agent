# Coverage matrix — the consult format

Show this in chat, exactly this shape, before implementing anything. One table for a single screen;
two tables in sweep mode. Keep the prose around it to the summary line and the questions.

Every example below is illustrative — the shape is the contract, the vocabulary is whatever the
platform in front of you actually uses.

## Severity — score it, don't feel it

`reach × consequence ÷ recoverability`, bucketed. It exists so a forty-row ledger sorts itself instead of
being argued from, and so the depth budget lands on the rows that earn it.

| Sev | Meaning |
|---|---|
| **S1** | someone loses data, takes an irreversible action on a wrong belief, or sees another viewer's data |
| **S2** | the screen defeats its own purpose, or misrepresents an outcome the viewer will act on |
| **S3** | survivable but unhelpful — dead activity marker, no recovery control, several causes mushed into one |
| **S4** | informational only, rare, nothing to undo |

**S1 rows never sit below D1, whatever the budget.** If a row outranks this ordering because the user says
so, upgrade it in plain sight and record that it was their call, not yours.

---

## Single screen

The block between the fences is the template. Fill it; do not re-shape it.

```markdown
## State coverage — <screen> · <mode: static-prototype | real source> · <posture: offline-first | …>

**Facts:** <n> providers (<cacheable?>) · writes: <yes — which, irreversible? | none, read-only> ·
gates: <…> · lifecycle enum `<field>` = <values + unknown case> · regions: <n> · empties:
<collections + which causes> · host: <connectivity / lifecycle / storage / permissions>

**Axes walked:** A1 A2 A3 A4 A6 A7 A9 (A5 by enum, A8 by posture) — <n> candidates considered,
<n> survived the gates, <n> merged, <n> rejected (listed below). Ceiling if every axis met every
value: ≈<n> conditions; this table is the <slice> slice (`derivation-axes.md`).

Precedence I propose: <order> — contested: <which positions, and what each answer implies>.
Fail-closed list (irreversible actions on this screen): <…>
Three states no checklist would have produced: <…> · failure the code swallows: <where, and what the
viewer is left staring at>

| # | State | Fam | Evidence | R | Sev | Now | Verdict | Depth | Recovery |
|---|---|---|---|---|---|---|---|---|---|
| 1 | pending, first read | A | provider call at `<file:line>` (v) | always | S3 | busy marker, no reserved height | upgrade | D2 | — (placeholder) |
| 2 | high-latency-but-working | B | no request budget anywhere (v) | yes, slow links | S2 | indistinguishable from stuck | **add** | D2 | elapsed + real cancel |
| 3 | no-connection-at-entry | B | no connectivity signal read anywhere (v) | yes | S2 | renders as `empty-never` | **add** | D1 | resume on reconnect |
| 4 | no-connection-with-cache | B | cache exists at `<file:line>` (v) | yes | S3 | falls through to failed | **add** | D2 | read-only + stale line |
| 5 | failed (retryable) | A | handler at `:51` only logs (v) | yes | S2 | busy marker forever | **add** | D2 | retry (transient only) |
| 6 | absent | A | `absent` outcome unhandled; screen takes an id (v) | yes | S3 | busy marker forever | **add** | D1 | back to the list |
| 7 | `empty-never` | A | list at `:88` (v) | first run | S3 | "No data" | upgrade | D2 | create the first |
| 8 | `empty-filtered` | A | filter state at `:23` (v) | yes | S3 | same "No data" + a create action | **add** | D1 | clear filters |
| 9 | unknown lifecycle value | E/A8 | `<status>` has 5 values, 2 handled (v) | on contract change | **S1** | renders as ready | **add** | D1 | render as unknown, don't act |
| 10 | write in flight | C | mutation at `:140` (v) | yes | **S1** | no duplicate guard | **add** | D2 | disable + idempotency key |
| 11 | lost-in-transit | C | no ack check after send (v) | yes | **S1** | reported as success | **add (fail-closed)** | D2 | verify, then offer resend |
| 12 | restored-after-kill | G | no state save on suspend (v) | yes (OS reclaims) | **S1** | returns to the list, work lost | **add** | D2 | restore position + draft |
| 13 | session expired mid-write | D×C | refused-on-write path (i) — store read, branch not traced | yes | **S1** | silent failure | **add** | D1 | re-auth, draft intact |
| 14 | write blocked by policy | C | — | no | — | — | n/a | — | no policy gate on writes |

Dropped by the gates (so you can see the net was cast, and what the ceiling is): `throttled` — no
quota on these providers; `integrity-failed` — nothing signed, no local crypto; `too-large` —
provider caps the collection server-side; `maintenance`/`incident` — **cross-cutting, see below**;
multi-display, capture-mode, `absent-vs-refused` leak check — no surface here.

**Decide:** (a) cut/add rows (b) depth budget (c) may rows 3, 5, 13 be handled in the shared
transport/shell rather than here? (d) row 9's unknown-value rendering — hide, or show "unsupported"?
```

### Reading the columns

`R` = reachable without doing something absurd (yes / yes-on-slow-links / rare / no). `Now` = what a
viewer actually sees today — "busy marker forever", "renders as empty", "silent", "reported as
success" are findings and belong in the table. `(fail-closed)` marks a row where the safe default is
non-negotiable (`hostile-and-unknown-conditions.md` §1).

**Confidence marks** (`persona.md`) sit on every `Evidence` cell: `(v)` verified — you read the path;
`(i)` inferred — the mechanism is real, that branch is untraced; `(a)` assumed — unchecked. A row may be
*consulted* at `(i)` or `(a)`; **no row is implemented at `(a)` until it has been checked.** Unmarked
evidence reads as `(a)`, so mark all of it.

## Sweep mode

Table 1 — one row per state, applied to **all** screens that can have it, no exceptions:

```markdown
## 1. Cross-cutting — handled once, everywhere (<n> screens)

| # | State | Screens that can have it | Owner layer | Now | Verdict | Sev | Depth |
|---|---|---|---|---|---|---|---|
| X1 | no-connection-at-entry | 12/12 | connectivity service + app shell | 3 variants across 12 | add | S2 | D2 |
| X2 | failed (transport outcome) | 12/12 | provider wrapper → screen condition | none | add | S2 | D2 |
| X3 | not-signed-in | 9/12 | entry guard (redirect, not UI) | handled elsewhere | keep | — | — |
| X4 | unknown-value / contract drift | 12/12 | deserialisation boundary | renders as ready | **add** | S1 | D1 |

Global precedence: <order> — written once at <resolver location>. Contested positions: <list>.
Forcing hook for every screen: <param / arg / dev menu / env var>.
```

Table 2 — what stays screen-local:

```markdown
## 2. Screen-specific residue

| # | Screen | State | Fam | Evidence | Now | Verdict | Sev | Depth |
|---|---|---|---|---|---|---|---|---|
| P1 | `<library>` | `empty-filtered` | A | `:88` (v) | create action shown | upgrade | S3 | D2 |
| P2 | `<upload>` | write in flight / queued | C | 3 sequential sends (v) | partial success silent | add | S1 | D2 |

Sampled <a,b,c> for derivation; inferred the other <n> against this set — say the word to run them.
Scope: <shells+all screens | shells+5 worst | audit only> ≈ <n> files.
```

## Rules for the table

- Every `Evidence` cell is a real `file:line`, or "no <signal> anywhere" — plus its confidence mark.
  Never "typically needed".
- A row without a `Recovery` cell is not a state, it's a dead end — fix it before showing the table.
- **Always show the axis line, the rejected list and the ceiling.** They are the only proof the coverage
  came from a walk rather than a memory of a list, and the only honest statement of what is unbuilt.
- **Fill the "three states no checklist would have produced" line.** If it is empty, the derivation did
  not happen: go back to the edge pass (`derivation-axes.md`) before sending this.
- `n/a` rows survive only when the reason is structural (read-only screen, no such gate). They prove
  the net was cast; they are not padding.
- Merge visible causes into one row only when message *and* recovery match — then name both causes
  (`failed — unreachable / timed-out / provider`).
- Flag `policy` on any row from `hostile-and-unknown-conditions.md` §3–§6: those answers belong to the
  product's risk owner, not to the implementer.
- 8–20 rows for a screen is normal; over ~25 means the distinctness gate is being skipped.

## Questions worth asking

Batch into the environment's structured-question tool if present; otherwise the numbered list above.
Only these: rows to cut/add, depth budget, shared-layer permission, contested precedence positions,
and (sweep) scope. Never ask about styling, copy tone, or which states "matter" — the matrix already
answers those, and a viewer who wanted a subset will say so.
