# Move 8 (regional half): color weighted by where attention accumulates

## The shape of the "before"

One color/theme decision is applied uniformly across the whole interface, driven by a single source of truth — usually "the brand's identity color" or "the app's overall theme setting" — rather than by how each region is actually used. A permanently-visible navigation rail and a continuously-read work surface end up sharing the exact same background treatment, because both simply inherited the one global theme value, with no separate reasoning applied to either.

Diagnostic question: does more than one region of this interface currently pull from the same single global color/theme token, despite being used completely differently — one glanced at briefly to navigate, another stared at for extended reading or data entry?

## The shape of the "after"

Identify, region by region, how long and how continuously a user's eyes actually rest there during real use — not how prominent the brand wants that region to be. Chrome that's glanced at once per navigation action can carry the boldest, most saturated, most identity-forward treatment, including the brand's strongest signature color as its *dominant* surface color rather than a mere accent on a neutral background, because brief glances don't accumulate the fatigue that sustained reading does. The region where real work happens — reading a table for minutes, filling in a form, reviewing a document — gets whatever treatment reduces strain over that sustained use, independent of what the brand's primary color happens to be.

Critically, "reduces strain" doesn't universally mean "goes light" — for a genuinely dark-context tool (a code editor, a media/video tool, anything meant to be used in low ambient light) the calmer choice for the high-dwell-time region may be a softened dark tone, while the brand's boldest, brightest color gets concentrated in chrome instead. The direction of the shift depends on the surface; the *mechanism* — decide per region by dwell time, not by one global token — is what transfers.

This split covers *where the brand's color lives*, but chrome carries two further, independent calls that are easy to collapse into one by habit:

- **Position.** "Chrome" means whatever region is glanced at rather than read — a side rail, a top bar, a bottom bar (common on mobile), or a floating/collapsible panel are all legitimate instances, not variations on one canonical "sidebar" answer. Which one fits depends on navigation depth, item count, and screen proportions, not on which is most commonly seen in admin-tool examples.
- **Color identity.** Once chrome's role (bold, identity-forward, low-fatigue-cost) is established, its actual hue is a separate decision from the working surface's light/dark direction. Chrome can be the brand's full, saturated hue as its base color (a genuinely green chrome, not a dark-neutral chrome with a green accent stripe); it can be dark-neutral; it can be light-neutral. None of these is the default — each is a real option whose fit depends on what actually reads as "the brand" for this product.

What makes this reasoning-driven rather than a fixed palette rule:
- There's no universal answer to "should chrome be a dark sidebar and content be light" — that's one instance of the pattern, observed in one case, not the rule. The rule is: separate "where does the brand show up boldest," "what color and how saturated is that," and "where does the user's attention actually live" into three independent decisions instead of one inherited value that answers all three at once.
- The technical mechanism for this split (a fixed, non-themeable value on the low-dwell-time region vs. a token-driven value on the high-dwell-time region; or two independently-configurable theme scopes; or a design-system layer with per-region overrides) depends entirely on how the codebase already manages styling — there is no single correct implementation to reach for.

## A minimal, illustrative sketch (not a template to copy)

```
[low-dwell-time chrome region: position chosen for this product's nav depth
 and screen proportions (side rail / top bar / bottom bar / floating panel —
 not defaulted to "sidebar"); color/theme value fixed to the brand's boldest,
 most identity-forward choice — which may be the brand's full saturated hue
 as the base color, not just a neutral with an accent — independent of the
 main content's theme]
[high-dwell-time work region: color/theme value chosen for lowest fatigue
 over sustained reading — the specific direction (lighter or darker, warmer
 or cooler) depends on what this surface is actually used for, and is decided
 independently of whatever color/position chrome landed on]
```
