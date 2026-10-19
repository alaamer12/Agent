# Text covered by another element

**ID:** `text-occlusion`  
**Catalog section:** Layout & Space  
**Official modality:** Browser

## Definition and empirical evidence

The catalog defines this as an opaque layer covering otherwise readable text and suggests moving the layer or giving the text clear space. CSS permits intentional overlaps; the question is whether meaningful text remains readable and whether the interaction is purposeful.

## Underlying principle and potential harm

Keep important text perceivable as users read, resize, and interact with a page. Accidental occlusion can hide words, instructions, values, or controls. Accessibility impact depends on actual behavior and criteria; overlap alone does not prove nonconformance.

## Recognition signals

- Words are fully or partly covered/clipped at normal, narrow, or zoomed layouts.
- Overlap blocks reading or interaction, including after text wraps, localizes, or enlarges.
- Positioning, transforms, fixed dimensions, overflow/clipping, or stacking contexts may contribute.
- A hover/focus overlay covers content without suitable dismiss/hover/persistence behavior.

## Causes to investigate

Possible causes include absolute/fixed positioning over normal-flow text; misunderstanding nested stacking contexts; fixed sizing/overflow that fails when copy wraps/scales; or a badge/tooltip/label placed without checking nearby content.

## Exceptions and false positives

- A badge can intentionally overlap an icon/control to show a meaningful count/status.
- Tooltips/popovers intentionally overlay adjacent content when their behavior supports access and dismissal.
- Selection highlights/floating labels can be intentional if text remains readable and necessary information is not obscured.
- An overlay may cover decoration or be temporary and controllable; visible text in the DOM does not make visually unreadable text acceptable.

## Correction guidance

Confirm the overlay’s purpose and text role. If coverage is accidental, reposition/constrain the overlay, allow reflow, or reserve clear space; do not blindly increase `z-index` where stacking contexts are involved. If intentional, keep scope/duration clear, preserve readability/interaction, and provide expected hover/focus dismissal behavior. Retest narrow layouts, long/localized text, and increased zoom/text size.

## Independent research references

- [Impeccable Slop catalog](https://impeccable.style/slop) — opaque coverage signal and concise correction.
- [MDN — Stacking context](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Positioned_layout/Stacking_context) — nested layers and `z-index` behavior.
- [W3C WAI WCAG 2.2 reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) — reflow/text enlargement and overlap outcomes.
- [W3C WAI WCAG 2.2 content on hover/focus](https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html) — dismissible, hoverable, and persistent overlay conditions.
- [ServiceNow Horizon Badge](https://horizon.servicenow.com/workspace/components/now-badge) — purposeful count/status badges over other UI.