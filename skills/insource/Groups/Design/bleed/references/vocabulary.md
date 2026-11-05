# Vocabulary — what people actually say

Register problems are hard to ask for. Nobody says "this is the wrong layout register"; they say the
page looks wrong. Match on the **structural nouns** — page, section, card, box, margins, width, whole,
full, like the other files — not on the verb, which is usually "make" or "fix".

## Direct → act

| Phrase shape | Means | Action |
|---|---|---|
| "make it the whole page, not sections inside a page" | framed-inside-page → page | delete cap + outer card, hoist sections |
| "don't make it like main-section inside a page" | same | same |
| "it looks like a section inside a page" / "a page inside a page" | nested frames | remove the inner one |
| "make it take full page dimensions" | capped column | drop the cap |
| "full width" / "edge to edge" / "full bleed" | page | as above |
| "remove the box around it" / "stop wrapping everything in a card" | outer card | delete the card, keep the children |
| "use section headers and dividers instead" | page grammar named explicitly | swap card chrome for sticky head + hairline |
| "make it consistent with the other files" / "like the other files" | register drift | read siblings first, adopt their grammar verbatim |
| "this doesn't look like the rest of the app" | register drift | same |
| "why are there empty margins here" | cap at wide viewport | drop the cap or widen it deliberately |
| "put it in cards" / "make it a dashboard" / "group these into panels" | page → framed | add cap + cards |
| "each of these is its own thing, let me pick one" | framed or hybrid | wrap the objects, keep the page |
| "only this one block should feel like an object" | hybrid | one card, everything else full-bleed |
| "match the layout of `X.html`" | reference given | extract that file's grammar and apply |

Mixed-language phrasing is common and still lands on the same nouns. Look for the structural word
wherever it appears; do not require an English keyword to trigger.

## Near-miss → do NOT do a register pass

These sound like framing complaints and are not. Doing a register pass for them changes the wrong
thing and burns a round trip.

| Phrase | Actually means | Test that tells you |
|---|---|---|
| "it is very long" | density / vertical rhythm | measure document height before touching structure; if blocks already reach the edges, it is not framing |
| "not eye-conforming" / "too crowded" / "raw data dumped into a UI" | information hierarchy and component craft | are the sections already full-bleed? then the problem is inside them |
| "organized in a good way" | grouping and ordering | count sections; a well-framed page with bad grouping still reads wrong |
| "make it stunning / sleek / premium" | visual treatment, emphasis, whitespace | register is usually already correct |
| "this number is wrong" | data or computation | never a layout issue |
| "the chart looks amateur" | chart quality, labels, legend | fix the chart, not the container |

The disambiguating question, asked internally before acting: **does the content already reach its
container's edges?** If yes, framing is solved and the complaint is about something else.

## When the phrase is ambiguous

"Clean it up", "make it look right", "this is wrong" do not name a register. Ask one question, three
options, one consequence line each:

- **page** — content runs to the edge, sections separated by hairlines and sticky heads.
- **framed** — a capped column of cards, each block an object you can point at.
- **hybrid** — full-bleed page with one framed object where a real object exists.

Never guess between registers; it is the one decision the whole pass turns on.
