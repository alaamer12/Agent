# /mine — noise and density: spend reading budget only where signal lives

A long artifact — a 600-page book, a 90-page spec, a transcript, a scraped
doc set — is far less content than its page count suggests. The first fifty
pages of a typical book are front matter: half-titles, a copyright page,
a list of figures, a table of contents. The last sixty are often an index.
Old scans carry blank verso pages and advertiser pages between chapters.
Web captures carry nav bars and cookie banners repeated two hundred times.
None of that is understanding, and an agent that reads it page-by-page —
especially a subagent handed "pages 1–100" as its assignment — burns its
whole budget on furniture.

**The rule: profile before you read, skip with evidence, and never skip
silently.** The profile is mechanical and cheap (seconds of extraction and
counting). Reading is the expensive resource. So the shape of every
document/media pass is: extract → measure where words actually live →
classify regions → sample-check the classification → read proportionally →
record what was read, skimmed, and skipped, with the evidence behind each
skipping decision. This applies to **every** artifact bigger than a screen
or two, and it is mandatory whenever page ranges are being handed to
subagents — a page-range assignment made before the noise map is a guess
about where the book's content is.

Where the general census discipline lives (`search-and-mining-technique.md`
→ "The ground census"), this file is its document-shaped extension: the
**structure split** is a census field here, not optional garnish.

## The taxonomy of noise

| Region | What it is | How to treat it |
|---|---|---|
| **Front matter** | Half-title, title page, copyright/colophon, dedication, list of figures/tables, TOC | Skim at most. **Exception that overrides the skip: the preface, foreword, and "why this book exists" introduction are primary *why* evidence** — the author's stated rationale and audience. Never let a noise filter drop them; downgrade them to a skim pass, not a skip. |
| **Table of contents** | Structure map with page numbers | **Read it once, carefully — it is the cheapest map of the artifact's arrangement the census asks for.** Then never treat it as content. It tells you where chapters start, which is exactly what the noise map and any page-range split need. |
| **Running furniture** | Headers, footers, page numbers, repeating disclaimers | Detect by repetition (recipes below), strip at extraction time, never read. |
| **Back matter** | Index, bibliography, list of references | Index: skip after sampling — but glance at its entries once; an index's term list is honest evidence of what the artifact considers important. Bibliography: don't read, *harvest* — it's a free candidate list for the next discovery pass. |
| **Scanned-document artifacts** | Blank verso pages, separator pages, ad pages in old scans, OCR garbage from bad scans | Near-zero word count per page flags them mechanically. A page that OCRs to 3 words is not content. |
| **Web-capture boilerplate** | Nav, sidebars, cookie banners, "related articles", comment sections | Use a converter that strips them (a docs scraper like the sibling `scrape` skill, pandoc, readability) rather than raw HTML; then grep for the tell — a line appearing on >20% of pages is boilerplate, not prose. |
| **Media filler** | Silence, ad rolls, intro/outro jingles, "before we get started" chatter | Profile by timestamps before transcribing/reading; segment selectively (see "Media below"). |

## Profile it, don't assume it

The trap in the other direction is just as expensive as reading the noise:
**heuristics about where front matter ends are guesses.** A "50 pages of
junk" assumption deletes the 40-page author's preface that carried the whole
rationale; a "this region looks like an appendix" assumption skips the
appendix that contains the actual protocol table. So the map is built from
measurements on *this* artifact, and no region gets dropped on a
classification alone.

Sample-extraction recipes — text with page boundaries preserved (a form feed
`\f` per page is what `pdftotext` produces), then count per page:

```bash
# text layer present? (empty/near-empty output on a "PDF" ⇒ scanned image —
# the OCR route instead, or declare reach partial; this check itself is the
# detector)
pdftotext -layout book.pdf book.txt

# words per page + near-blank tally
awk 'BEGIN{RS="\f"} {print NR"\t"NF}' book.txt | awk '{t+=$2; if($2<15)b++} END{print "pages",NR,"words",t,"near-blank",b+0}'

# running header/footer candidates: lines repeated across many pages
awk 'NR%40==1' book.txt | sort | uniq -c | sort -rn | head   # sample first lines; or all lines with sort|uniq -c|awk '$1>20'

# index/TOC tell: what fraction of a page's lines end in a number
# (high ⇒ listing-like: TOC, index, table corpus — verify before classifying)

# per-page density profile to find the content boundary
awk 'BEGIN{RS="\f"} {print NR": "NF}' book.txt | sort -t: -k2 -n | tail -40  # densest pages; content usually starts where density jumps
```

Then **sample-verify every skip**: open 2–3 items from any region about to
be dropped — two random index pages, the three pages straddling the
front-matter/content boundary, one repeated-header line in context. The
boundary pages of a region are where a wrong classification shows itself.
Record the evidence ("index 452–512: sampled 461/488/503, all alphabetical
entry lists, no prose"). These recipes are starting points, verified on
none of them being perfect — same rule as `source-ecosystems.md`: run the
command, check the output makes sense, adapt. Where the standard tools are
missing, the bootstrap in `search-and-mining-technique.md` → "The extraction
bootstrap" is how you get a pipeline; the noise map runs on whatever text
extraction lands in `cache/`.

For paginated readers with no text layer to grep (this environment's `Read`
tool takes PDF page ranges directly): sample pages at a stride — every 10th
page from the start until prose density stabilizes, every 10th from the end
until it stops being index-like — and interpolate the boundaries, labelled
as interpolation in the census.

## Report the split — in the census and in the ledger

Every document checkpoint carries a **structure split** line, the document
analogue of "read 15 files of 32,818":

> 512 pages: front 1–23 (skimmed 1–3, TOC read as structure map),
> body 24–451 (read closely, incl. preface 12–22 — stated rationale lives
> there), back 452–512 index (3 pages sampled, skipped). Blanks: 31
> verso pages stripped at extraction. **Read: ~380 of 512.**

Three failure modes this line prevents, each of which otherwise quietly
poisons a run:

- **An agent reporting findings from pages it skipped** — the ledger's
  `skipped:<region> <range> (<evidence>)` entries vs the checkpoint's
  claims make the contradiction visible to the parent's spot-check.
- **A TOC mistaken for structure read** — "arrangement: 14 chapters"
  derived from contents is fine *if labelled* "from TOC, not from reading
  each chapter opening".
- **Page-range fanout assigned against raw page counts** — split by the
  noise map's body range (and chapter boundaries from the TOC), not by
  uniform 100-page blocks that hand one subagent fifty pages of index and
  another the actual core argument.

## Media below: audio and video

Same discipline, different meter: the scarce resource is transcript tokens
and your attention, not pages. Profile before transcribing — duration,
chapter/segment markers if the platform exposes them, silence-dense ranges;
transcribe selectively rather than wholesale (the Q&A of a conference talk
is signal; the 20-minute sponsor read is not). Always census the
**transcript source** — official captions, creator-published transcript, or
your own ASR pass — auto-generated captions are usable but their errors are
yours to inherit; label quotes taken from them as ASR-approximate, and
re-check any quoted passage that will carry a load-bearing claim against a
timestamp in the original.

## Run directory placements

The raw artifact goes in `sources/`; the extracted text, per-page profile,
and cleaned markdown go in `cache/` (derived, re-buildable, subagents read
from here); the noise-map outputs and sample-check evidence that back a
skip go in `witness/`; any profiling loop you formalized goes in `tools/`
so the next source — and every subagent — reuses it instead of re-deriving.
