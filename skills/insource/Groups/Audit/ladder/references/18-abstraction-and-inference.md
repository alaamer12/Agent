# 05 — Ladders of thinking: abstraction, inference, and research laddering

Three ladders that are not code but shape code decisions. They are the reason a skill about ladders
should not be only about `if` chains: they decide *where* your rungs live and *why* a fix keeps
missing.

## The ladder of abstraction

Moving between concrete detail and general concept to find the level where a problem is solvable.
Levels of abstraction is a design-school term (Stanford d.school; also "the ladder of inference"
adjacent literature); the practical move is: a complaint that arrives at the rung of a widget is
usually a fix at the rung of a flow.

```
values / intent        "onboarding should build confidence"      ← the fix often belongs here
flows                  "the first 3 screens ask for account setup"
components             "the 'skip' link is below the fold"
details / CSS          "the button is grey on grey"               ← where the bug was reported
```

Using it as a ladder (first-match-wins thinking applied to problem framing):

1. Take the report at its stated level; do not silently re-level it.
2. Walk **up** by asking what the object is *for* (function → flow → intent).
3. Walk **down** by asking what the chosen intent requires *concretely* (never stay at the slogan).
4. Stop at the level where a single change removes the class of problem, not the instance.
   "Disable the button" fixes a rung; "route unauthenticated users to a read-only view" removes the rung.

Where it plugs into this skill: the **level you choose sets the facts your decision ladder reads**.
A UI-state ladder keyed on `isLoading` is one abstraction level below one keyed on `fetchState`;
the second admits error, stale, partial and cancelled, and the first cannot express them. The most
common cause of an unmaintainable if-chain is that its rungs were cut at the wrong abstraction level.

## The ladder of inference (Argyris; Seven Steps)

The rungs are mental, and each one discards data:

```
7 actions            we act on beliefs
6 beliefs            beliefs are adapted from conclusions
5 conclusions        we draw conclusions from assumptions
4 assumptions        we make assumptions to fill gaps
3 meanings           we add meaning to what we select
2 selection          we select a subset of what we observe
1 observable data    what is actually available
```

The failure mode is a reflex loop: beliefs select the data we notice next, so the climb accelerates.
In engineering terms, this is why "the flaky test is a Docker issue" survives to Friday — a belief
set selected the observation.

Using it: when two people (or two agents) disagree about a cause, descend the ladder until you reach
a rung where you agree — usually step 1 or 2 — and re-climb from shared data. In practice that means:
name the observable, then the interpretation, then the assumption, then the conclusion, then the
action you're proposing. Every rung above the observable gets a "verified / inferred / assumed" label,
which is exactly the discipline the `stateful` skill demands of its rows and the `senior-refactor`
"evidence first" rule.

## Laddering interviews (means-end chain, Reynolds & Gutman)

A qualitative technique that climbs a hierarchy of *meaning* with the same probe, repeatedly:

```
attribute            "it has a quick-dry fabric"
  ↓ "why is that important to you?"
functional consequence   "I don't have to iron it"
  ↓ "and why does that matter?"
psychosocial consequence "I look put-together at work"
  ↓ "what does that say about you / get you?"
value                "competence", "self-respect"
```

Field notes that generalize to any interview-driven requirement gathering:

- The default probe is the up-probe ("why is that important to you?"); vary it ("what does that let
  you do?", "what would it mean if you couldn't?") to avoid the three-year-old effect, which is the
  documented failure mode — participants exhaust and give empty answers at the top.
- Stop when answers become abstract nouns that are not actionable *for your decision*; a chain that
  ends at "happiness" tells you nothing to build.
- Represent results as chains (attribute → consequence → value), not as isolated quotes, so you can
  see which values recur; the standard artifact is the hierarchical value map.
- Requirement → feature mapping is then a ladder of its own: the values select which consequences are
  in scope, which select which features are worth building.

## How the three feed the code ladders in this skill

| Thinking ladder | Code-ladder consequence |
|---|---|
| Abstraction | Sets the *facts* a decision ladder reads and the level its rungs live at. Wrong level = unmaintainable chain. |
| Inference | Labels which rung conditions are verified vs assumed, before they become rules in production. |
| Research laddering | Turns user statements into the criteria (values) that tier ordering should encode — e.g. a deny tier standing for "don't destroy trust". |

## Sketches: the rungs as something you can hold

**Abstraction ladder** — climb until the level explains the class, descend until it is buildable. This is
the version to run against a bug report before designing a ladder's facts.

```python
LEVELS = ["detail", "component", "flow", "function", "intent"]

def climb(report, explains_class):
    """Returns the highest level whose statement still implies every symptom."""
    for level in reversed(LEVELS):
        statement = reframe(report, level)
        if explains_class(report.symptoms, statement):
            return level, statement
    return LEVELS[0], report


def descend(level, statement, depth=3):
    """Walks back down to a concrete change; a slogan at the top is not a fix."""
    return [reframe(statement, l) for l in LEVELS[: LEVELS.index(level) + 1][::-1]][:depth]
```

The consequence for the code ladders in this skill: **the level you stop at decides the fields your rungs
read**. `isLoading: bool` is a `detail`-level fact; `fetchState` is a `function`-level fact, and only the
second can express `stale`, `partial` or `cancelled` without inventing a second boolean that lies
(`08`).

**Inference ladder** — label each rung, and let only verified rungs become rules.

```python
CHAIN = [
    ("observable",  "contrast 1.05:1 on the Skip link",            "verified"),
    ("selected",    "measured that link, not the other 12 elements", "verified"),
    ("interpreted", "the user does not see the escape hatch",       "inferred"),
    ("assumed",     "they want to leave rather than finish",        "assumed"),
    ("concluded",   "the button needs more contrast",               "assumed"),
    ("acted",       "raise the contrast of the Skip link",          "verified"),
]

def safe_to_encode(chain):
    """A rung may become a decision rule only when nothing above it is an assumption."""
    return all(kind == "verified" for _, _, kind in chain)

def first_unverified(chain):
    return next(((step, kind) for step, _, kind in chain if kind != "verified"), None)
```

`first_unverified` is the debugging version of this ladder: when a diagnosis is wrong, it is almost never
the observable that was wrong, it is the third or fourth rung. Descent means going back to the observable
with the assumption written next to it and re-deriving - which is the same discipline the `stateful`
skill asks for when a state is labeled `assumed` and must not be implemented unchecked.

**Laddering an interview** — one probe, varied, with a stop rule; the output is a chain, not a quote.

```
attribute   "it dries fast"
  up-probe  "so what does that let you do?"       -> "I never iron it"        (functional)
  up-probe  "and why does that matter to you?"    -> "I look put-together"     (psychosocial)
  up-probe  "what does that say about you?"       -> "competent"               (value)
stop        when the next answer cannot change a build decision ("happiness")
```

```python
def ladder_answer(answer, probe=lambda a: ask("why is that important to you?", a), max_rungs=4):
    chain = [categorize(answer)]
    while len(chain) < max_rungs and actionable(chain[-1]):
        chain.append(categorize(probe(chain[-1])))
    return chain          # attribute -> consequence -> value; empty answers stop the climb
```

Field notes that transfer to any requirements interview: vary the wording or the participant goes
flat ("the three-year-old why"), a value that no build decision depends on is too high a rung, and the
chains are the artifact - isolated quotes cannot be compared for frequency.

## Where the three connect to a decision ladder

| Thinking ladder | What it changes in the code |
|---|---|
| Abstraction | The fact schema. Wrong level, and the rungs cannot express the states that exist. |
| Inference | Which conditions are allowed to become rules, and which stay behind a flag until measured. |
| Laddering | The criteria a tier ordering encodes: "don't destroy trust" is why the deny tier exists. |
