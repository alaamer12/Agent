# PDF export

Use the browser's print function. It needs no library and works offline. Add an **Export PDF** button that calls `window.print()`.

## Behavior

- **Order**: all tabs print in tab order, each tab starting on a new page (Compare first, Showcase next, then any extra tabs). Give each tab a print-only heading.
- **Before printing** (`beforeprint`): save the current theme and switch to light, unhide every pane, fill the export date, and inject a page header (the page title, top left), the comparison date ("Compared on ...", bottom left) and "Page X of Y" (bottom right) with an `@page` margin-box rule.
- **After printing** (`afterprint`): restore the theme and the active tab.
- If a candidate is focused, the PDF keeps the highlighting. Mention this to the user.
- Margin-box headers and footers (`@page` boxes) are not supported by every browser. If they are missing nothing breaks, and the comparison date also appears on the first page. Never put essential information only there.
- Print dialogs can be blocked inside embedded previews. If the button does nothing there, tell the user to open the saved file directly in the browser.

## Print stylesheet rules

- `@page { size: A4; margin: 17mm 14mm 18mm }`. Use A4 by default and Letter when the user's region or request calls for it. Format dates in the user's locale. Use `pt` sizes: body 10pt, captions 8pt, code 7.5pt, headings 12 to 20pt.
- Keep colors: `-webkit-print-color-adjust: exact; print-color-adjust: exact`. White page background. No shadows or transitions.
- Hide interface: tabs, buttons, copy buttons, hints, next and back.
- **Do not leave flowing content in CSS grid.** Some browsers (Chrome at the time of writing) push whole grids to the next page and leaves big blank areas. In print set `.grid { display: block }`.
- **Do not make large containers unbreakable.** Mark small units unbreakable (`break-inside: avoid` on list items, charts, "why it matters" boxes, table rows, the verdict) and let sections flow. Flatten boxed cards into sections separated by hairlines.
- **Headings stay with their content**: `break-after: avoid` on headings, winner lines, captions and candidate subtitles.
- Repeat table headers: `thead { display: table-header-group }`. Table `min-width: 0`, font about 8pt.
- Code wraps: `white-space: pre-wrap; word-break: break-word; overflow: visible`.
- Showcase in print: keep the usage title and description, then for each candidate a colored subtitle and its own separate code block. With inner file tabs, print the file name above each file's block. Hide the interactive toggle bar.
- Code colors for print use a light background with darker syntax colors.
- Media that cannot print (audio, video, 3D, interactive): print a poster or key frame, the caption, the duration and the visible URL. Hide the player controls.
- Image showcases: print each candidate's subtitle followed by its images, two per row (`display:inline-block; width:48%`, not CSS grid). Images get `max-width:100%` and `break-inside:avoid`, and captions stay attached to their image. Keep image colors exact. Skip the interactive view tabs and print every view.

## Testing

`python scripts/check_page.py page.html --pdf out.pdf` renders the print view in a headless browser (the script uses Playwright with Chromium) and reports the page count and any page that is nearly empty. Open a few pages as images to check for orphaned headings and cut-off code.
