# Content stuck waiting to appear

**ID:** `content-hidden-at-rest`  
**Catalog section:** General quality  
**Official modality:** Browser

## Definition and empirical evidence

This is a review signal for meaningful content absent or visually hidden until interaction, script, or animation reveals it. Content can start hidden for a clear user-facing purpose; a user-controlled disclosure is not automatically a defect. Progressive enhancement favors core content/functionality being available before optional enhancements.

## Underlying principle and potential harm

Users should understand whether content is loading, intentionally collapsed, or unavailable. Important content hidden behind an unexplained delay/scroll/script failure may be missed or make a page appear empty. A reveal can also be undiscoverable to keyboard/assistive-technology users when visual visibility, focusability, and accessibility-tree exposure disagree.

`aria-hidden` removes content from the accessibility tree; `inert` also blocks focus/interaction. Neither should be mismatched with visible content.

## Recognition signals

- Meaningful content is absent on a cold render and appears only after hydration, timer, scroll, or animation.
- It remains invisible after the expected loading/reveal state or script/data failure.
- Opacity/visibility/hidden styles leave content focusable while invisible, or visible content is `aria-hidden`.
- A skeleton/loading indicator never resolves to content or an understandable error/retry.
- The DOM/CSS alone cannot establish the runtime state.

## Causes to investigate

Possible causes include a reveal class that never applies; an observer that never fires; component state initialized hidden then corrected client-side; delayed/failed hydration/data; a stuck loading flag; or hidden content without a reachable disclosure.

## Exceptions and false positives

- Accordions/disclosures are legitimate when a clear control reveals content and communicates expanded/collapsed state.
- Dialogs/steps may be inactive until a user action/prerequisite when users can understand and exit the state.
- Skeletons are valid temporary loading states if replaced by content or a recoverable error.
- Entrance animation can be an enhancement if content remains available without motion, script, or mouse-only interaction.
- Visible text can still be inaccessible if `aria-hidden`; opacity-only hidden content can remain focusable.

## Correction guidance

Keep essential content in the initial document/render where practical; otherwise provide meaningful fallback. Ensure loading states end in content or a clear error/retry. For deliberate hiding, use an appropriate disclosure control and synchronize state with visibility; ensure hidden descendants cannot be focused/interacted with. Do not use `aria-hidden` to conceal visible content; use `inert` only for genuinely inactive subtrees. Make non-essential animation optional and avoid stranding content if scripts/motion fail.

## Independent research references

- [web.dev — No fallback when JavaScript is unavailable](https://web.dev/without-javascript/index.html) — progressive enhancement and baseline content.
- [React `hydrateRoot`](https://react.dev/reference/react-dom/client/hydrateRoot) — server HTML visible before hydration and jarring mismatches.
- [MDN `aria-hidden`](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-hidden) — accessibility-tree behavior and visible-content caution.
- [MDN `inert`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/inert) — focus/interaction/tree effects for inactive subtrees.
- [W3C WAI-ARIA APG — Disclosure](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/) — user-controlled collapsed/expanded content semantics.