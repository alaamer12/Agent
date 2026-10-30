# Broken or placeholder image

**ID:** `broken-image`  
**Catalog section:** Imagery  
**Official modality:** Source

## Definition and empirical evidence

This pattern is a signal for an image that fails to appear or a placeholder that remains after content should load. An image may legitimately be absent while its request is pending; lazy loading can defer offscreen images until they are expected to be needed.

## Underlying principle and potential harm

Distinguish temporary loading from failed resources and preserve the image’s meaning/function if it cannot display. Persistent failure can remove useful visual information, product identification, or task context. Informative images need alternatives conveying essential information; functional images need alternatives describing their action; decorative images should generally use an empty alternative.

## Recognition signals

- A placeholder remains after the image is expected to load or an error state appears without useful fallback.
- An offscreen lazy image is falsely treated as broken before it enters the loading range.
- Network/resource request fails, an unsupported type is used, or a stale path/content blocker prevents display.
- A screenshot alone cannot show whether the request is pending, deferred, blocked, or failed.

## Causes to investigate

Potential causes include invalid/changed paths, inaccessible CDN/resource, unsupported format, network error/content blocking, lazy-loading delay, or failure handling that never replaces a placeholder. Verify runtime conditions rather than inferring from appearance.

## Exceptions and false positives

- A skeleton/placeholder is valid temporary feedback when it gives way to content.
- Lazy-loaded offscreen images may not yet have been requested; scroll into view and wait.
- Failure of a decorative image may not remove meaningful content, though it should not leave misleading UI.
- A designed error/fallback state can be intentional, especially with retry or an alternate access path.
- An image can load successfully yet still have missing/misleading alternative text.

## Correction guidance

Confirm whether the request is pending or failed using the runtime request/state. Fix the resource path/format/access problem where possible; otherwise show a stable fallback rather than an endless loading state and provide retry where useful. Supply appropriate text alternatives by image purpose and avoid duplicate announcements. For lazy images, test after entering the loading range; reserve space to avoid layout shift and do not defer critical initial-viewport images.

## Independent research references

- [MDN `<img>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/img) — display failures and browser alternative-text fallback.
- [MDN `HTMLImageElement.loading`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLImageElement/loading) — deferred offscreen lazy-loading behavior.
- [W3C WAI — Images Tutorial](https://www.w3.org/WAI/tutorials/images/) — informative/functional/decorative/complex image alternatives.
- [WHATWG HTML — Images](https://html.spec.whatwg.org/multipage/images.html) — image request state and failed-load `error` event.
- [eBay Playbook — Skeleton loader](https://playbook.ebay.com/design-system/components/loading-skeleton) — temporary skeleton behavior and resolution when content arrives.