# Building the page

One self-contained `.html` file. No build step. The structure is chosen for this task so the user can decide as easily as possible. `examples/ui-frameworks-example.html` shows one good result for one domain (web UI frameworks). Read it for working code, then design your own. It is not a template and your page may look very different. `examples/domain-walkthroughs.md` shows how the same method changes shape across other domains. Options listed in this file are illustrative, not exhaustive, and hybrids are always acceptable.

## Page order

1. **Title** (what is being decided).
2. **Candidate chips**: name + version, a color dot, and the rating (`4.3/5`). Chips are buttons that turn on focus mode (below). Under them, one hint line: how the rating is computed.
3. **Caption**: one or two sentences with the goal and the data date.
4. **Freshness section** (required, its own visible block with `data-section="freshness"`): three fields, **Compared on** (the date the comparison was done), **Data covers** (the period of the data) and **Re-check by** (a date or event after which the page should be treated as out of date), plus one sentence saying why. Do not fold the date into the caption. The date also prints in the PDF footer. When the page is changed in a later turn, add an **Updated** line with the date and what changed (see `iteration.md`).
5. **Intro note** (optional): the one caveat that frames everything (for example "no candidate is universally best").
6. **Tabs** and an **Export PDF** button.
7. **Tab content.**

## Tabs

- Default is two tabs: **Compare** and **Showcase**.
- Add tabs when the task needs them (Migration, Cost, Risks, Decision matrix, Timeline). Keep each tab to one purpose. A tab with nothing useful is not created.
- Tabs are buttons with `role="tab"`; panes are sections. Next and Back buttons at the bottom of each pane move between tabs.
- Render panes from JS data arrays (candidates, dimensions, examples) so content and layout stay separate.

## Compare tab: choose blocks by the data

| Block | Use when | Notes |
|---|---|---|
| Dimension section | always | Heading, winner line, optional chart, points, sources, "why it matters" |
| Winner line | always | Names co-winners when tied. Margin text says how clear the lead is |
| Main point + subtext | every point | See below |
| Bar chart | at least 2 candidates have numbers on the same measure | Say the direction (lower or higher is better). If bars start above zero, say so. List candidates with no figure in the note |
| Table or heatmap | many candidates x many dimensions, or tiers to show | Rows are dimensions, columns are candidates, notes column last, rating row at the end |
| Co-located sources | always | A "Related sources" line per dimension with links. If a claim has no source, say so |
| Verdict | always | One row per use case with colored picks. Ends with the dominant constraint |
| Caveat note | when sources conflict or data is thin | Amber box at the end |

Do not draw a chart or table when the data does not support it. Prefer prose points over a weak chart.

### Main point and subtext

Each candidate point has two layers:
- **Main point**: one short line that carries the finding, with numbers highlighted (a colored chip style).
- **Subtext**: smaller, muted text under it with the reason, the context, or the caveat. Skip the subtext when the main point says it all.

Never drop supporting detail from the research just to be short. Move it to subtext.

### Focus mode

Clicking a chip focuses that candidate. Elements that mention a candidate carry `data-ks="react vue"` (space-separated keys). On focus:
- matching elements get a highlight (tinted background + outline in the candidate color)
- other elements are dimmed (opacity about .3, slight grayscale) but stay visible
- clicking the chip again clears focus
This covers points, bars, table columns, winner lines and verdict rows. Use the same keys everywhere.

## Showcase tab

The Showcase shows the candidates in use. Its content follows the domain and what the user asked for: [code] [terminal sessions] [screenshots] [product photos] [audio samples] [video clips] [PDFs] [3D model views] [spec sheets] [sample outputs or reports] [step lists] [a worked scenario]. Mix types when that helps the decision. Skip the tab and say why if it would add nothing.

- One block per type the user chose. Each block: number, title, one-line description.
- Inside the block a toggle bar lists the candidates as tabs. Each block's toggle is independent (do not sync blocks).
- A candidate can have inner tabs for sub-items: files, or views such as [front] [side] [in use].
- Everything shown comes from sources found in this session or from files the user uploaded. Cite the source in the caption. If nothing supports an example, leave it out and say so.
- For print, render every candidate and every sub-item as its own labeled block (see `pdf-export.md`).

### Code and text examples

- Real, runnable code from official docs, for example [`main.go`, `go.mod`], [`app.py`, `requirements.txt`], [`Cargo.toml`, `src/main.rs`] or [`app.js`, `main.js`, `counter.js`]. Show the file name on the inner tab and a copy button for the visible file.
- Syntax highlight every code block (see snippet below). Code panels are dark in both themes.

### Images

Images are one medium. For audio, video, documents, 3D models, fonts or any other medium, follow `media.md`. Use images for products, screenshots, hardware, dashboards, anything judged by looking.

- **Sourcing.** Take images from official product or project pages, documentation, press kits, or files the user uploaded. Never invent or guess an image URL. Keep each full URL as a plain string literal in the data array so `scripts/check_images.py` can find it.
- **Markup.** Each image is a figure with alt text, reserved space and a credited caption:
  ```html
  <figure class="shot" style="--r:4/3">
    <img src="URL-OR-DATA-URI" alt="Laptop A, lid closed, top view" loading="lazy" decoding="async" width="1200" height="900">
    <figcaption>Top view. <a href="PAGE-URL" rel="noopener">Source: maker's product page</a></figcaption>
  </figure>
  ```
  CSS: `.shot img{display:block;width:100%;aspect-ratio:var(--r,4/3);object-fit:contain;background:#fff}` (a white panel keeps product photos readable in dark theme).
- **Never leave a broken image.** Add one capture-phase error handler that swaps a failed image for a placeholder showing the alt text:
  ```js
  document.addEventListener("error",function(e){var i=e.target;if(i.tagName==="IMG"){var d=document.createElement("div");d.className="shot-missing";d.textContent="Image unavailable: "+i.alt;i.replaceWith(d);}},true);
  ```
- **Where the page runs decides how images are stored.** Opened as a local file, remote URLs work. Some hosted or published viewers block remote and local-file images (check the environment's rules, since they change). Then embed each image as a `data:` URI: download it, resize to a sensible width such as 1200px, compress it, base64 it, and stay within the host's page-size limit. If an image cannot be fetched (network limits, no permission), say so, ask the user to upload it, or use a spec table instead.
- **Rights.** Prefer images the source allows to be shown. Credit the source in the caption.
- **Verify.** Run `python scripts/check_images.py page.html` (add `--hosted` when publishing, `--browser` to test in a real renderer). Fix every PROBLEM. For each WARN (could not confirm from this environment) tell the user to open the page and look.

## Visual rules

These are defaults, not requirements. Change them when the user asks (palette, fonts, size) or the content calls for it. Check the environment's rules for hosted pages before relying on any external resource.

- **Full width**, fluid: `padding: clamp(16px, 4vw, 72px)`, cards in `grid-template-columns: repeat(auto-fit, minmax(min(100%, 34rem), 1fr))` with a generous gap (`clamp(28px, 3.5vw, 56px)`).
- **Type** (defaults): a fluid base size such as `html{font-size: clamp(17px, .55vw + 15px, 22px)}`, rem everywhere, line-height about 1.7. Choose a font made for comfortable long-form reading (for example Lexend or Atkinson Hyperlegible) and a clear monospace font for code, each with a system fallback stack. Larger is better than smaller.
- **Color carries meaning**, not decoration:
  - one color per candidate (dot, chip border, names, bars, code tabs)
  - winner = green, "why it matters" = blue, caveat = amber, numbers = purple chip, accents = one brand color
  - heatmap tiers: green (best) to red (worst)
  - define as CSS variables on `:root` and override in `:root[data-theme=dark]`. If the user gives a palette, map it onto these tokens and keep candidate colors distinguishable.
- **Theme**: light by default. `?theme=dark` switches: `document.documentElement.dataset.theme = new URLSearchParams(location.search).get("theme") === "dark" ? "dark" : "light"`. A `?theme=light` value is the same as the default.
- **Responsive**: check phone, tablet, desktop. Tab bars and tables scroll sideways inside their own container. Tap targets at least 44px. Keep `viewport-fit=cover` and safe-area padding.
- **Accessibility**: visible `:focus-visible`, `aria-selected` on tabs, `aria-pressed` on chips, never rely on color alone (text labels beside colors).
- **Colored left borders on list items** are avoided by default (user preference). Use a small colored dot before the candidate name.

## Syntax highlighting snippet

Code blocks can be in any language. Build one highlighter per language from a keyword list and a comment pattern. Strings, numbers, function calls and tags are shared. Unknown languages fall back to plain text with strings and numbers only.

```js
function makeHL(kw, comment, flags){
  var rx=new RegExp("("+comment+")|(\"[^\"\\n]*\"|'[^'\\n]*'|`[^`]*`)|(\\b(?:"+kw.replace(/ /g,"|")+")\\b)|(<\\/?[A-Za-z][\\w.-]*)|([@:]?[\\w-]+\\$?(?==))|([\\w$]+(?=\\())|(\\b\\d+(?:\\.\\d+)?\\b)",flags||"g");
  var K=["","cm","st","kw","tg","at","fn","nu"],E=function(s){return s.replace(/&/g,"&amp;").replace(/</g,"&lt;")};
  return function(s){var o="",l=0,m;rx.lastIndex=0;
    while((m=rx.exec(s))){var g=1;while(!m[g])g++;
      o+=E(s.slice(l,m.index))+'<span class="'+K[g]+'">'+E(m[0])+'</span>';l=rx.lastIndex;}
    return o+E(s.slice(l));};
}
var HL={ // examples; add the languages the showcase needs
  js:makeHL("import from export default function const let return async await","\\/\\/[^\\n]*|<\\!--[\\s\\S]*?-->"),
  py:makeHL("def class import from return if elif else for in with as async await lambda","#[^\\n]*"),
  go:makeHL("package import func return if else for range struct interface go defer var const type","\\/\\/[^\\n]*|\\/\\*[\\s\\S]*?\\*\\/"),
  rust:makeHL("fn let mut pub use mod struct enum impl trait match return if else for in async await","\\/\\/[^\\n]*"),
  sql:makeHL("select from where join group by order insert into values update delete create table","--[^\\n]*","gi"),
  sh:makeHL("if then fi for do done echo export","#[^\\n]*")
};
```
Highlight classes: comment `cm`, string `st`, keyword `kw`, tag `tg`, attribute `at`, function `fn`, number `nu`. Give each class a color that reads on the dark code panel.

## Gotchas (these have broken pages before)

- **Unclosed script tag bug.** Inside the inline `<script>`, never write a literal `<!--` or `</script>`. Write `<\!--` and `<\/script>` in JS strings. A literal `<!--` followed by `<script` makes the browser swallow the rest of the page, so buttons stop working with no visible error. `scripts/check_page.py` detects this.
- In template literals, avoid `${` unless you mean interpolation. Code samples with `$state` or `component$` are fine.
- No `localStorage` dependency. State lives in memory.
- Prefer no external scripts. Web fonts are the only external resource by default, and every font needs a full fallback stack so the page still reads well if the font host is blocked. Whether remote images and scripts load depends on where the page runs (see Images).
- Escape `&` and `<` before inserting code into the DOM (`textContent` or the `E` helper above).
