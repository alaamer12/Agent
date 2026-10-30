# Goal and value extraction - the step that decides everything

Most failed workarounds are not failures of imagination. They are failures of framing: the agent takes the
proposed method as the requirement, so when the method is blocked it declares the requirement blocked.

> The proposed method is a means, not a mandate.

## The three-line form

Before generating any route, write these three lines. If line 1 mentions the blocked thing by name, redo it.

```text
GOAL    : what the user's product or task must be able to claim, in their language
VALUE   : the specific thing needed from the blocked source (a datum, a behavior, a guarantee, an affordance)
TEST    : the observation that would prove the value was captured, without the blocked thing
```

Example - the user asks for "the vendor's live stock-availability API, so we show what can ship today":

```text
GOAL : our storefront never shows an item as shippable this week when it is not
VALUE: a per-item availability signal, current enough for the promise we make at checkout
TEST : over a week of real orders, items bought and then rejected as unavailable stay under the
       tolerance the shipping promise allows
```

Notice the rewrite: the goal is not "access to their availability endpoint", it is *not promising what we
cannot ship*. The vendor's live feed is one way to get that signal; freshness tolerance, our own order
outcome data, and a supplier report that already arrives nightly are others. The value can be taken without
taking the access.

Concrete worked examples - including a closed personalization behavior, where the framing fight is hardest -
live in `../examples/`. Read one only after you have written your own three lines; examples are calibration,
and borrowing someone else's framing is how a hunt ends up solving the wrong problem.

## Extraction drill - four questions

1. **Whose need does this serve?** Name the end user and what they can do afterwards that they cannot do
   now. Abstract one level away from the implementation.
2. **What would still satisfy them?** If the blocked thing vanished tomorrow and they never knew, what
   alternative outcome would they accept? Whatever you listed is the value; the blocked thing was packaging.
3. **What is the smallest unit of the need?** A whole platform is rarely needed - usually it is a number, a
   ranking, a notification, a file, an identity claim, a permission decision, a rendering.
4. **What is being *observed* vs *controlled*?** Blocked reads and blocked writes need different families;
   conflating them produces routes that cannot work.

## The trap list

| Trap | What it looks like | Fix |
|---|---|---|
| Method worship | "we can't do it because service X has no API for it" | Restate the goal without naming X |
| Substituted scope | the user's example is treated as the full requirement | Ask what else the need covers, or list the assumption |
| Precision theater | needing the exact same numbers as the blocked system | Ask what accuracy actually changes for the user - usually far less |
| Real-time reflex | assuming live is required when the need is "current enough" | Check whether hourly, per-session, or on-demand is the real bar |
| Symmetric block | assuming a block on one side blocks both | Reads and writes are separate problems |
| Feature-shaped need | the requirement is phrased as a UI feature, not an outcome | Name the user decision the feature supports |

## When the goal is genuinely the access

Sometimes the user truly needs the specific thing and nothing else - a signed legal document, a licensed
asset, an entitlement only the owner can grant, a live feed that exists in one place. Say so plainly, and
then the honest route set is: request it, buy it, wait for it, or reduce. Inventing an indirect route to a
goal that is *defined* by direct access is the failure mode the boundary file
[`04`](04-access-parity.md) exists to stop.

## Handoff

The three lines go into the route plan the audit script reads (`scripts/routes.py` requires them) and into
the decision record, so a reviewer three months from now can see why the chosen route was judged adequate.
