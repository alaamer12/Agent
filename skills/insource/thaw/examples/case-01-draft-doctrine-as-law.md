# Case 01 — a draft doctrine used as law

## The situation

An agent is helping design the backend for an app that tracks virtual balances in a ledger. The project
has a draft balance-safety doctrine that reads: *"Wallet mutations must use row-level locking in a
specific relational engine."* The user asks whether a BaaS could replace the custom backend, to write
less code. Three candidates are on the table: an embedded-engine BaaS, an abstraction-layer BaaS, and a
managed-relational BaaS.

## The freeze

The agent answers: *"The embedded-engine option and the abstraction-layer option don't support row-level
locking, so both are eliminated by your doctrine. The real choice is the managed-relational BaaS vs a
plain relational database."*

It cited a **draft doctrine** as if it were a law of nature, and pruned two candidates with it. It also
narrowed the field before understanding why the user wanted a BaaS.

## The thaw

The user pushes back: *"We're drafting. The docs aren't rigid. Don't take them as law — aim for better,
re-validate yourself."*

The agent runs the move:

1. **Notice the freeze.** "I treated the balance doctrine as law and used it to eliminate options."
2. **Split invariant from mechanism.** Tier test: *if the stack were rewritten, would this still be
   true?*
   - Invariant (keep): *a balance never goes negative; concurrent mutations must not desync it.*
   - Mechanism (draft): *row-level locking in a specific engine.* The doctrine even violates its own
     convention — "describe behavior, not fragile mechanism."
3. **Re-open the option set.** The embedded engine cannot do row locks, but it *can* enforce the
   invariant via serialized transactions + a non-negative CHECK constraint. The abstraction-layer
   option can via transactions + atomic ops. Neither is eliminated by the invariant — only by the draft
   mechanism. Both back on the table.
4. **Question both sides.** The agent's earlier "managed-relational vs plain database" framing assumed the
   custom backend was settled; the user's less-code goal actually questions that too. Re-derive from the
   goal.
5. **Aim for better.** Evaluate all candidates against the *invariant* and the real priorities (less
   code, maturity, the user's experience), not the draft locking mechanism.
6. **Re-close provisionally.** The user picks a BaaS. The decision is written down with alternatives and
   trade-offs; the doctrine is flagged for revision (mechanism → serialized transactions), the invariant
   untouched.

## What it settles

The requirement was the **invariant** (non-negative, desync-free balance). The row-locking doctrine was
a **mechanism** — draft, revisable, and powerless to eliminate an option that satisfies the invariant
another way. Citing the draft as law both narrowed the design and hid a better fit. The thaw restored
the real option set and let the better design win.