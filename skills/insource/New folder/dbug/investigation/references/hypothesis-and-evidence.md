# Hypothesis-driven debugging and the evidence hierarchy

The research corpus (`data/user.txt` §22–23; `data/grok.txt` §1,6;
`data/gemini.txt` §17) converges on one discipline: debugging is the
hypothetico-deductive method, not improvisation.

## The loop

```
Observation   what exactly happened (expected vs actual, conditions, rate)
     ↓
Hypothesis    a falsifiable causal claim: "because <A>, we see <B>"
     ↓
Prediction    "if that's true, then <experiment> will show <result> —
     ↓        and if it's false, <result2>"
Experiment    the CHEAPEST procedure that distinguishes the hypotheses
     ↓
Result        confirm → localize further   refute → next hypothesis
     ↓
Updated model (loop). Negative results delete search-space regions —
              record them, they are the actual progress of debugging.
```

Rules:

- **Falsifiable or discard it.** "Something in the caching layer is off"
  tests nothing; "the `/x` response is served from cache older than the
  14:02 write" can be proven wrong in one request.
- **Rank hypotheses** by prior probability × cost-to-test; run the
  cheapest strong one first, not the most feared.
- **Change one variable at a time.** Multiple edits between runs destroy
  attribution — you no longer know which one mattered.
- **The forbidden loop:** guess → change code → run → hope. If you catch
  yourself doing it, stop; you have skipped Observation and Hypothesis.

## Two ways causality gets proven

- **Counterfactual** (deterministic bugs): change/omit A, hold everything
  else equal, B disappears — and returns when A is restored. This is what
  a bisect result, a minimal reproduction, and "revert the fix, the test
  goes red again" establish. Root-cause bar for reproducible bugs.
- **Statistical** (races, timing-, load-, GC-dependent bugs): A doesn't
  guarantee B, it raises the probability of B given A. Confirmation means
  measuring **both arms** — same workload with the suspect condition on
  vs off (flag, dataset size, injected delay, concurrency level), N runs
  each, and comparing rates. "It stopped happening after my change" over
  three runs is not evidence; a rate ratio is.

Every prediction in the loop should name which kind of confirmation it is
seeking — it decides the experiment's design (single run vs N-vs-N).

## Socratic ("rubber duck") pass — the zero-cost experiment

Force your mental model into explicit answers at each pipeline step:

```
What enters here, exactly (type, shape, constraints)?
What transformations run on it, and what SIDE EFFECTS (cache, writes, calls)?
What must leave, exactly?
What environment/global/flag/concurrency assumptions am I making?
```

Divergence between "what must be true" and "what is true" *is* the bug's
address. This costs minutes and frequently beats an hour of skimming code.

## The evidence hierarchy

Rank what you have before trusting a conclusion:

| Level | Evidence | What it proves |
|---|---|---|
| 1 | anecdote, assumption, "I think it's X" | nothing — prompt for an experiment |
| 2 | source-code reading suggests a flaw | a hypothesis, not a cause |
| 3 | logs/traces/telemetry show the failure path | correlation along the pipeline |
| 4 | an invariant breaks at exactly step k (first invalid state captured) | localization of the divergence |
| 5 | minimal automated reproduction: this input/state ⇒ this failure | causality — the root-cause bar |

"Reads wrong" is Level 2. Keep climbing. A fix justified only by Level 1–2
is allowed *only* as a documented temporary mitigation with a follow-up,
never as the close of the investigation.

## Meta-debugging — when you've been in the wrong subsystem for an hour

The investigation itself can have bugs. At a fixed time budget (≈30–60
min without new evidence), stop and write down:

```
What do I actually know?        (list Level 3+ evidence only)
What am I assuming?             (every belief not backed by evidence)
What evidence contradicts my current hypothesis? (if none — you're
                                                 cherry-picking)
What single observation would prove it wrong?
What is the cheapest experiment that distinguishes my top two hypotheses?
```

Then run that experiment, or re-classify the problem and return to the
classify step in `../SKILL.md`. Widening/narrowing in
[`pipeline-model.md`](pipeline-model.md) is what this unblocks.
