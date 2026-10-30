# Case 9 - the operating system says no

**The ask:** "the app should keep syncing in the background so nothing is ever stale when you open it."

## Goal, separated

```text
GOAL  : when the user opens the app, the data on screen is current enough to act on
VALUE : freshness at the moment of use - not continuous work while nobody is looking
TEST  : time between opening the app and the data being usable, measured on a low-end device
        on a cellular connection
```

"Background sync forever" is the method someone reached for. The value is *fresh when I look*.

## Block verification

Not a bug. Both mobile platforms restrict background execution to sanctioned patterns, with battery and data
as the stated reason, and the OS kills long-lived background work under pressure. Confirmed by the platform
docs plus observed kill behavior on a real device at two usage profiles. Class: blocker, high confidence -
this one is a policy of a system the user does not control.

Is any route here a protection defeat? The OS restriction is a platform policy that applies to every app
equally, not an access-control measure guarding someone's data. Using a *sanctioned* mechanism that fits the
need is not defeating it; disguising continuous work as something else to dodge the policy would be, and it
also gets the app removed from the store. The distinction matters and goes in the record.

## Routes

| Route | Family | Note |
|---|---|---|
| Sync on open, with the last snapshot rendered instantly and refreshed underneath | reshape | satisfies "fresh when I look" and feels faster than the original plan |
| The platform's sanctioned background fetch, budgeted by the OS | reroute | you get some background windows; you do not get to choose them |
| Push messages wake the app when server data changes | reroute | the only real-time-ish door both platforms allow |
| A foreground session that keeps working while the app is open | reshape | covers the case that actually matters: user is looking |
| Local cache plus delta fetches so open-time sync costs 200ms not 4s | reshape | makes the chosen route cheap enough to be instant |
| A persistent service that never dies, disguised as media playback | rejected | circumvention, store removal risk, and battery abuse on the user's device |

## Chosen

Render-then-refresh on open, push-triggered wake for changes that must arrive while closed, delta fetches to
make it quick. The word "background" disappears from the design; "fresh when opened" replaces it, which is
what the user wanted.

## What gets said out loud

If the user was promised "always syncing", that phrase is now wrong and is corrected in the product copy, not
silently reinterpreted. That is the Reduce discipline: name the cut.

## What this case teaches

Platform limits are usually a shape mismatch. Once the goal is stated as freshness-at-moment-of-use, the
blocked method stops being the only answer and the sanctioned one is often strictly better on the metric the
user cares about.
