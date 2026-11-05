# Verification — measure, then look

A register change is structural, so verify it structurally. A screenshot catches rhythm; it will not
tell you a wrapper survived.

## Probe

Run against the rendered file (Playwright/Puppeteer `page.evaluate`). Rename the selectors to the
project's own — the assertions are the point, not the selectors.

```js
() => {
  const chrome = document.querySelector('[data-purpose=icon-rail]');   // fixed side chrome, if any
  const blocks = [...document.querySelectorAll('.section-block')];
  const capped = [...document.querySelectorAll('div')].filter(d => {
    const mw = getComputedStyle(d).maxWidth;
    return mw !== 'none' && parseFloat(mw) > 0 && parseFloat(mw) < window.innerWidth;
  });
  return {
    viewport: window.innerWidth,
    expected: Math.round(window.innerWidth - (chrome ? chrome.getBoundingClientRect().width : 0)),
    blockWidths: blocks.map(b => Math.round(b.getBoundingClientRect().width)),

    // page-level caps only: an element counts if it wraps a section block.
    // A component cap (a chip row, a tooltip, a form field) is legitimate and must NOT be flagged.
    pageCaps: capped.filter(d => !!d.querySelector('.section-block'))
                   .map(d => (d.className || d.id) + ':' + getComputedStyle(d).maxWidth),

    sections: document.querySelectorAll('main section').length,
    heads: document.querySelectorAll('.section-head').length,
    stickyHeads: [...document.querySelectorAll('.section-head')]
      .filter(h => getComputedStyle(h).position === 'sticky').length,

    docHeight: document.body.scrollHeight,
    overflowX: document.documentElement.scrollWidth > window.innerWidth
  };
}
```

## Assertions by target register

| Target | Must hold |
|---|---|
| page | every `blockWidth === expected`; `pageCaps` empty; `heads === sections` (or `sections − 1` when the first block is a hero with no head); `stickyHeads === heads`; `overflowX === false`; no console errors |
| framed | exactly one page-level cap; card count equals object count; `stickyHeads === 0`; no overflow at the narrowest supported width |
| hybrid | all page assertions hold **and** one card element is a direct child of a block |

Run the probe at **two widths** (e.g. 1440 and 900). A surviving wrapper hides at desktop width and
shows up as dead margins at tablet width.

## Reading the numbers honestly

- `pageCaps` non-empty is only a failure if the capped element wraps sections. Verify which element it
  is before deleting anything — component caps are correct code, and a probe that flags them trains
  the next pass to break them.
- **Document height usually rises** after a framed→page conversion. One compressed multi-column card
  becomes several stacked full-width sections. Taller is not worse; do not "fix" it by re-adding a cap.
- Report measurements, not feelings: "five blocks at 1376 = 1440 − 64 rail; zero page-level caps;
  four sticky heads for four headed sections; no overflow at 1440 or 900." A register claim without a
  number is a style opinion.

## The eye pass

One screenshot per state the file claims. Look only for what measurement cannot see:

- dead margins that are not responsive behaviour;
- a border duplicating the page edge;
- rhythm: consistent block padding, hairlines not colliding with sticky heads;
- inline elements colliding — a value and its unit rendering on one line is invisible to every probe;
- class-name collisions with a utility framework (`ring`, `grid`, `container`, `stack`, `card`, `col`)
  silently applying framework styles;
- inner components unharmed: charts labelled, tooltips positioned, tokens intact;
- every documented state parameter rendering something *different* — a parameter that renders the same
  output twice is a false claim in the file's own footer.
