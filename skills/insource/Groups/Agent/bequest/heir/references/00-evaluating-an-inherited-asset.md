# Evaluating an inherited asset

The card is a claim; the tests are evidence; the environment is the judge. Work in that order.

## The fitness check (two minutes, not twenty)

| Question | Where the answer lives | If it fails |
|---|---|---|
| Does the task produce the input this asset expects? | card §Inputs | adapt the caller, or skip the asset |
| Are the dependencies present and compatible? | card §Dependencies | run it anyway only to see the error, then mark the gap |
| Do the assumptions match this project **now**? | card §Assumptions and limitations | adapt, or record the mismatch in the card |
| Was it ever verified, and how? | card §Verification | run the tests before trusting; otherwise status applies |
| Has anything drifted since? | card §Origin date, versions, paths | treat as untested here until you re-run it |

Drift signals worth checking explicitly, because they invalidate a card silently:

- **Version drift** — the card says a runtime, library or OS version you no longer have.
- **Schema drift** — the data shape it expected (column names, JSON keys) versus today's.
- **Path drift** — it references a file, service or host that moved or disappeared.
- **Policy drift** — permissions, network rules or credentials it assumed are no longer available.
- **Authority drift** — the project decision it encoded was superseded (check decisions/ADRs, not just code).

## Run before trust

```text
1. read the card's "How to use it" exactly as written
2. run its tests (tests/…), or the card's verification commands
3. compare the observed output with the card's recorded output
4. if they differ: stop. That difference is the finding - card is stale, asset is broken, or the environment moved
5. only then use it, adapt it, or record why you are not using it
```

A failing test does not mean "ignore the asset"; it means the card's claim is no longer true and you now own the
update if you proceed.

## The four outcomes, with their obligations

**Use as-is.** Cite it in the commit/PR/record. Nothing else changes.

**Extend in place.** Add the missing parameter or branch. Update the card's Inputs/Outputs, append to the
verification block (new cases, today's date), and adjust the index row only if the "What it does" sentence
changed. Keep the old behaviour working — an extension that breaks the original case is a new asset, not an
extension.

**Adapt in place.** The environment or data moved. Re-run the **full** case matrix, not just the new case, and
replace the verification block rather than appending: the old results no longer describe the asset. If the
adaptation changes what the asset means, say so in the Origin line.

**Supersede.** A genuinely different method. Write the new asset, then mark the old card's first line
`Superseded by <slug>` and keep it until the new one has passed its tests; deleting an asset that
someone may still be using mid-task is how a shared directory loses trust.

## When the card is simply wrong

Sometimes the inherited asset never worked, or worked only in a world that no longer exists. Then:

1. Say it in the current turn — the user needs to know the asset is a trap, not a tool.
2. Mark it: change the status to `unverified` with one line of what you observed (command + output).
3. Fix it only if the fix is cheap and belongs to the current task; otherwise leave the mark and move on.
4. Do not quietly delete it. A marked dead asset costs a reader ten seconds; a deleted one costs them a rebuild.

## Provenance you owe the next agent

- The reuse itself: `reuse: bequest/<slug>` in the commit or PR, with the parameters you supplied.
- Any change: the card's Origin line, dated, one sentence.
- Any non-use: if an asset *looked* right and was rejected, one line saying why — in the current work's notes or
  in the card itself if the reason is durable ("needs a 3-node cluster; this project is single-node").

That last one is the cheapest gift in the system: it stops the next agent from repeating your evaluation.
