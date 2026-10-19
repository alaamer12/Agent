# Example: a micro run

Command: `animate micro CheckoutButton.tsx "feels dead, make it premium"`

**0 Understand.** "Premium" maps to restraint, light and depth cues, soft press, no bounce, one slower beat. Restated: "I read this as: reflection or sheen plus a settled press · scope=micro, interaction=interactive, sync=instant · feel=premium, restrained. Proceeding unless you meant a more playful feel."

**1 Survey and classify.** Stack: React with Motion; no tokens file; the button already has `transition: all 300ms`. Existing animation is reviewed first: `ease` default, layout property in the transition. Classification: `scope=micro · interaction=interactive (press), non-interactive (success) · sync=domino (label then check) · direction=press/release`.

**2 Gate.** Frequency: a checkout button is seen occasionally (not 100 times a day). Purpose: feedback and state indication. Speed: press 140ms; success within 360ms. Function: helps. Outcome: animate, tier rare.

**3 Style.** Asked one question: creative or traditional, recommending creative because the tier is rare and the brief says premium.

**4 Options.** Three options from different lanes: A label rolls into a check (self-transformation), B sheen sweep (light and material, needs a live demo), C magnetic press (physics). The agent wrote the spec (see `prototype-spec.json`), validated it, and built the page. B is marked `needs_html`, so it asked: "Light cannot be shown in ASCII. Keep ASCII for A and C, and build a live demo for B?" The user said yes and picked A.

**5 Build.** Pressed state with `scale(0.97)` at 140ms using the press curve; label slides up through a clipped window; check draws using `getTotalLength()`; fixed width to avoid layout shift; reverse crossfades back in 180ms; disabled state static.

**6 Review.** The audit script flagged the old `transition: all` and a missing reduced-motion variant; both fixed; second run clean. Verdict: Approve. Needs a human: how the check draw feels on a real phone.

**7 Report** (contract format): classification line, decision, files, values, review result, human checks, follow-up: "the success toast could become an in-place confirmation too (component)".
