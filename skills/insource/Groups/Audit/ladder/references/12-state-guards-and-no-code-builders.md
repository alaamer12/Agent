# 12 — State-transition guards and no-code branch builders

Two places where a ladder exists but nobody calls it a ladder: state machines (transitions guarded by
conditions, tried in order) and visual workflow builders (branches stacked top to bottom). Both inherit
every defect from `00`.

## Statechart guards: ordered transitions, first true wins

The spec-level behavior: for a given event, the transitions are tested **in declaration order** and the
first whose guard is true is taken; the rest are not evaluated. An unguarded transition for the same
event therefore must be declared last, or it swallows everything below it.

**TypeScript (XState-style)**

```ts
CLICK: [
  { guard: 'tooManyAttempts', target: 'locked' },
  { guard: 'authenticated',   target: 'detail' },
  { guard: 'guest',           target: 'login' },
  { target: 'login' },                       // terminal: no guard left unhandled
],
```

**Python (a minimal machine, same semantics)**

```python
def fire(table, event, ctx):
    for t in table[event]:
        if isinstance(t, Terminal) or eval_guard(t.guard, ctx):
            return (t.target, t.name)
    raise LookupError(f"{event} matched no guard and no terminal rung: the event is swallowed")
```

**Java/C#** - identical rule with different syntax: guard-then-target lists where the ordering is the
documentation. In C#, an attribute-ordered filter pipeline in ASP.NET Core does the same thing with
`Order` numbers (`07`), which is the version to prefer when filters come from different assemblies.

### Reachability probe (this is the whole point)

```python
def unreachable(table, event, space):
    names = {t.name for t in table[event] if isinstance(t, Transition)}
    hit = {fire(table, event, c)[1] for c in space} - {"no-transition"}
    return sorted(names - hit)
```

Run it over the cross product of the small context space. A broad guard placed early makes every later
transition unreachable; without the probe you learn this from a user.

### Guard-specific failure modes

- **Broad-first ordering**: `attempts >= 0` above `attempts >= 3` kills the specific rung. The probe
  finds it; nothing else does.
- **Impure guards**: a guard that mutates context. Machines re-evaluate transitions in devtools,
  simulations, and state re-entry, so the mutation happens twice.
- **No terminal transition**: the event is silently ignored and the UI hangs on a spinner. If ignoring
  is intended, say so with an explicit `Terminal()` rung - that also makes it visible in tests.
- **Per-event tables that drift**: the same guard spelled three ways in three states. Centralize named
  guards (`guards: { authenticated: (c) => ... }`).
- **Guards and entry/exit actions racing**: decide whether actions run before or after the guard and
  write it down; engines differ.

## No-code and low-code branch builders

Workflow tools, agent platforms, and rule UIs render the same ladder as stacked blocks, and their
guidance converges on the same three sentences: evaluate top to bottom, the first matching condition
wins, put the most specific or most likely branches first and the fallback last.

What a builder must provide, or it is a bug generator:

| Feature | Why it is load-bearing |
|---|---|
| Position = evaluation order, visibly | authors otherwise assume "more important first" means something structural |
| Reorder affordance with the order shown as data | reordering is the edit; if it is invisible, shadowing is invisible |
| Shadow/unreachable warning | "branch 3 matches everything branch 4 matches" is undetectable by looking |
| Forced final branch | an incomplete ladder in a UI produces "nothing happens" - unattributable |
| Test panel that shows which branch fired | the audit trail is the only way a non-programmer debugs |
| Preview of the compiled rule list | keeps the generated artifact diffable and reviewable |

### Failure modes specific to builders

- **Two sources of truth**: canvas plus generated rules. Compile on save, check the generated artifact
  in, and let the builder read its own output back.
- **Reordering by deletion-and-recreate** loses branch identity, so tests and analytics key on nothing.
  Give every branch a stable id the UI displays.
- **Copy-paste branches** that differ in one character of a condition string; without validation, both
  are "valid".
- **Depth explosion**: nested branches to express OR-of-ANDs. That is a decision table (`06`) wearing a
  tree costume; the flat form is reviewable.

## Seen in

XState and every UML-style statechart engine, SMIL/SCXML, ASP.NET Core filter pipelines, framework
route middleware, AWS Step Functions choice blocks, workflow automation platforms' condition blocks,
agent-permission prompt flows, and dialogue trees.
