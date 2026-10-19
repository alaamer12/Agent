# Content overflowing its container

**ID:** `text-overflow`  
**Catalog section:** Layout & Space  
**Official modality:** Browser

## Definition and empirical evidence

The catalog flags content spilling outside its container or making the page scroll sideways; it suggests wrapping/shrinking or a scrolling region when needed. CSS overflow may expose, clip, or scroll excess content. Visible overflow is a signal to check access/usability, not proof of failure.

## Underlying principle and potential harm

Ordinary reading content should generally reflow; intended overflow should have a clear purpose and a way to reach all content. Accidental clipping may hide text/controls, while page-wide horizontal scroll can force two-dimensional navigation for ordinary content. A scrollable region that keyboard users cannot operate may hide its contents.

WCAG 2.2 reflow permits a limited exception for content that genuinely needs two-dimensional layout (e.g. data tables); this does not automatically exempt adjacent headings, instructions, or controls.

## Recognition signals

- Ordinary text/controls are clipped or extend beyond the viewport at narrow widths/increased zoom.
- The page, rather than a meaningful bounded region, scrolls horizontally.
- Long URLs/identifiers/localized labels do not wrap.
- A scroll region cannot be discovered or traversed by touch, pointer, or keyboard; focus can disappear behind clipping.
- Source clues include fixed/minimum widths, `white-space: nowrap`, overflow clipping, and oversized media/children.

## Causes to investigate

Possible causes include fixed dimensions; unbreakable strings; non-wrapping text; flex/grid children refusing to shrink; oversized media/tables; or clipping applied to meaningful content.

## Exceptions and false positives

- Data tables may need two-dimensional layout; confine scrolling to the table where possible.
- Code, carousels, and other intentionally navigable regions may scroll horizontally when usable.
- A preview may be intentionally truncated if the full content is available through a clear, operable path.
- A region’s scrollbar is not necessarily page-wide overflow; absence of a visible scrollbar does not prove content is not clipped.

## Correction guidance

Identify what overflows and whether its width is necessary. For prose/labels, remove unnecessary fixed constraints, allow wrapping (including long tokens where appropriate), and let layout children shrink/reflow. For essential two-dimensional content, confine scrolling to that region, preserve semantics, and make it keyboard-operable with visible focus. Do not add `overflow: hidden`/`clip` as a cosmetic fix until confirming no meaningful content is lost.

## Independent research references

- [Impeccable Slop catalog](https://impeccable.style/slop) — content escaping its container/page-wide sideways scroll and candidate responses.
- [MDN `overflow`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/overflow) — visible, clipped, and scrollable overflow and accessibility cautions.
- [W3C WAI WCAG 2.2 reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) — reflow and limited two-dimensional content exception.
- [MDN `overflow-wrap`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/overflow-wrap) and [`text-overflow`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/text-overflow) — long-token wrapping and the fact text-overflow alone does not create overflow.
- [W3C WAI ACT — Scrollable content keyboard reachability](https://www.w3.org/WAI/standards-guidelines/act/rules/0ssw9k) — scroll-region sequential focus access.