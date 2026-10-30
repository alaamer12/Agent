# Generalization — same behaviour, none of this conversation's gravity

The rule: **the behaviour that was useful must survive; every dependency on this task must not.**
Generalizing is subtraction plus a small amount of input design — not a rewrite into a product.

It applies to every asset form, not just scripts. For a procedure, the "inputs" are the names, hosts and values
inlined in the steps — turn them into `<placeholders>` with a "fill these first" list. For a config template, the
couplings are baked values — promote them to obvious placeholders with valid examples. For a query, they are the
hardcoded table, date range and tenant — make them parameters. For a documented constraint, the coupling is the
one file where it was discovered — generalize to the condition that triggers it, not to that file.

## The four couplings to remove

| Coupling | Looks like | Becomes |
|---|---|---|
| **Path** | `/tmp/repro.py`, `C:\Users\me\proj\data.json`, `./scratch/out` | an argument with a sensible default (`--input`, `--out`), never an absolute path |
| **Identity** | `acme-billing`, `user_1841`, `staging-3`, a tenant id, a host name | an argument, or a documented placeholder the caller must supply |
| **Assumption** | Python 3.11, Bash 5, a CSV with those exact columns, a 10k-row table | a documented precondition + a check that fails with a clear message |
| **State** | reads a file the session created, relies on env vars the session exported | explicit inputs, or the script creates its own temp workspace |

Anything you cannot remove is a **documented limitation**, not something to hide.

## Input design — the smallest thing that works

```text
one script, one job
  args: 2-4 meaningful flags, no positional magic        --input FILE  --since 2026-10-01  --out DIR
  --help: the same text as the asset card's "How to use"
  exit codes: 0 ok · 1 findings/expected failure · 2 usage error
  output: human lines by default; --json when another program consumes it
  defaults: safe (read-only, dry-run) - destructive behaviour requires an explicit flag
```

In any stack the shape is identical — `argparse` in [Python], `flag` in [Go], `clap` in [Rust], `commander` in
[Node], a `param()` block in [PowerShell], `getopts` in POSIX shell. The point is not the library, it is that a
future agent learns the contract from `--help` without reading the code.

Prefer in this order: **flag → environment variable → config file**. A config file is only justified when the
value is stable across runs and shared by several assets; otherwise it is a new file to forget to create.

## Before → after, three shapes

**1. A throwaway command sequence → a documented procedure**

```text
before: kubectl delete pod api-… (hand-picked); sleep 20; curl health; repeat until green
after:  "Restart one API pod at a time: wait for Ready, then health, then the next.
         Never restarts two at once - the second one lands on an unready node.
         Preconditions: 2+ replicas, PDB allows one eviction. Verify: `kubectl get pods` all Ready,
         and `curl /health` 200 twice. Abort if a second pod goes NotReady."
```

A procedure is often the right answer when the steps are judgment calls; forcing them into a script produces a
script nobody dares run.

**2. A script welded to the session → a script with inputs**

```python
# before
rows = json.load(open("/tmp/session/events.json"))
bad = [r for r in rows if r["latency_ms"] > 800]

# after
def find_slow(rows, threshold_ms=800):
    """Rows whose latency exceeds the threshold. Accepts a list of dicts with 'latency_ms'."""
    return [r for r in rows if r.get("latency_ms", 0) > threshold_ms]
# CLI: python find_slow.py --input events.json --threshold-ms 800 [--json]
```

The function is testable, the CLI is trivial, and the threshold is no longer a fact about one incident.

**3. A dead end → a check**

```python
# "sync params silently return undefined on Next 15.2"
if NEXT_MAJOR >= 15 and "params" in page_source and "await params" not in page_source:
    print("FAIL: params is a Promise in Next 15; use `await params`")
```

A constraint that cost an afternoon is worth more as a 5-line check than as a paragraph of prose.

## The overengineering guard

Do not turn an approved candidate into:

- a package with a `src/` layout for 60 lines of logic;
- a plugin/config system the original never needed;
- a retry/cache/logging layer "for robustness" that was never tested;
- an abstraction over two similar lines — three similar lines beat a premature helper.

If the generalization has grown beyond what the behaviour requires, you are building a product, not bequeathing
an asset. Return to the simplest form that is genuinely reusable and testable.

## Naming

- Directory: kebab-case, verb-led for scripts (`find-slow-requests`), noun-led for data assets
  (`pg-lock-check`), short and specific — `utils` is not a name.
- Files inside keep their natural names; the card is always `README.md`.
- The card's first line states the behaviour in one sentence, because that line becomes the index row.

## What must NOT change

- The output that made the asset useful (same structure, same meaning). If you must change it, bump the asset
  and say so in the final report.
- The failure behaviour: what used to fail now still fails, with a better message.
- The evidence: if the asset encodes a measured threshold or a proven constraint, keep the number — moving it
  into a default is how a hard-won fact becomes a guess.
