# 20 — Finding the ladders already in a codebase

The usual ask is not "write me a ladder" but *"do we have tiers/layers/fallbacks here, and are they
holding?"* — or *"make this robust so the guarantee is always met."* That is an audit job: find the
ordered decisions that already exist, name the shape, and report the defects with evidence. Never
propose a strategy before you have looked.

## Audit modes, by what was asked

| They asked | Audit for | Likely shapes |
|---|---|---|
| "find/understand if there are tiers, ladders, layers between our code" | precedence chains: config merge order, middleware/filter order, resolver chains, CSS-like cascade, registry lookup, override layers | `03` scopes, `07` priorities, `10` chain, `12` |
| "make it more robust with tiers or fallback" | every single-source path: model/provider/disk/network/cache calls, retries with no backoff ladder, "one attempt then throw" | `11` attempts, `13` tiers |
| "escalate errors or information, not swallow them" | every `catch`, `?? default`, `.catch(() => )`, `except: pass`, silent empty return, and any place a severity is dropped | `04` guards, `13` tiers, `14` modes |
| "ensure guarantees are always met" | the invariant the code asserts or implies, then every path that can reach it without passing a check | `08` dispatch, `13` tiers, `15` tests |

## Where ladders hide

Look for a place where **more than one candidate answer exists and something picks one**. In practice:

```bash
# ordered/precedence structures already declared somewhere
rg -n --glob '!**/{dist,build,node_modules,vendor}/**' \
   -g '*.{ts,tsx,js,jsx,py,go,rs,java,kt,cs,rb,php,swift,c,cpp,mjs}' \
   'middleware|use\(|addFilter|register\(|interceptor|pipe\(|compose\(|chain\.|next\(|\bprecedence\b|\bfallback\b|\bresolve(Chain|Order)?\(|mergeConfig|overrides?\b'

# implicit ladders: maps and switch-style dispatch
rg -n 'switch *\(|match *\(|\.get\([^)]*\) *\?\?|case .*:\s*(return|break)|\bwhen\s*\(.*\)\s*\{'

# swallowed failures: the ladder with no terminal rung
rg -n -B1 -A3 'catch\s*(\([^)]*\))?\s*\{\s*[}]|except[^:]*:\s*(pass|\.\.\.)|\.catch\(\s*\(\s*\)\s*=>\s*(undefined|null|\{\}\)|false)\s*\)|\?\?\s*(null|undefined|false|\{\}|\[\])\s*[;,]'
```

Then read, don't trust greps: a match is a candidate, `file:line` is evidence.

Also inventory the **non-obvious** ladders, which greps miss:

- **Layer precedence.** Config: env > file > defaults; policy: org > team > user; DI: last registration
  wins. Write the order down in one line and check it matches the code's behaviour (`03`).
- **Registration order as policy.** A list built by appending across modules is a ladder whose order is
  decided by import order and test suite runs.
- **Loop-with-break.** A `for` over candidates with an early `return` is a first-match ladder.
- **Query/UI defaults.** `WHERE ... ORDER BY priority LIMIT 1`, a CSS cascade, a component picking the
  first matching breakpoint.

## What to report per finding

One row, one site, evidence-anchored. No adjectives without a line number.

| Field | Content |
|---|---|
| Site | `path/file.ext:120-148` |
| Shape today | nested ifs · switch · map lookup · try/catch fallback chain · config merge |
| Order source | written position · insertion/registration order · priority field · engine (tier) |
| Terminal rung? | name and value, or **"none — falls through as X"** |
| Defect | shadow / severity inversion / swallow / non-total / impure predicate / unbounded chain |
| Reachability | which rung can never fire, and the input that would have needed it |
| Guarantee at stake | the invariant the site is supposed to protect ("no write without consent") |
| Blast radius | what a wrong pick costs here (money, data loss, trust, one bad render) |

Two counts to finish with, because they change the recommendation more than any single finding:

- **N sites** and how many share one concern — three ladders deciding the same question in three layers
  is a consolidation candidate, not three fixes.
- **Rung count and depth** per site. ≤4 rungs and depth 1 is fine as a chain (`01`); depth ≥3 or
  ≥6 rungs is where a table or a closed-set dispatch pays (`02`, `08`).

## Reading the guarantee, not the code

For "make sure the guarantee always holds", state it first as a sentence with no `if` in it: *"every
destructive action carries an explicit yes"*, *"every request is answered with either data or a stated
failure"*. Then check the ladder against it structurally:

1. Enumerate every path to the effect. Each must cross a rung that can refuse it.
2. Ask what happens on input nobody enumerated. It must land on a named rung (`15`'s totality check),
   ideally the strictest one, never on the happy path.
3. Ask what happens when the check itself fails (timeout, missing flag, unparseable config). A rung
   whose guard threw an exception usually means "allowed" — that is fail-open by accident.
4. Ask who can add a rung and where. If the answer is "anyone, anywhere", make ordering data with a
   tie-break (`07`) and the strict verdict a tier (`13`).

A guarantee expressed only in prose, tests, or a code comment is a hope. The shape that turns it into a
type-level or engine-level fact is a closed-set dispatch (`08`) or a tier whose order the engine owns
(`13`) — those are the two options worth recommending when the ask is about guarantees.

## Before proposing anything

Read the project's own conventions — instruction files (`AGENTS.md` and friends), docs index, lint and
formatter config, an ADR/conventions folder, and the shape of neighbouring code. If the repo already
writes ladders as a rules table with ids, propose a rules table with ids; the fifth dialect in one
codebase is a cost, not a cleanup. Report findings first, strategies with trade-offs second, and let the
user pick (`21`).
