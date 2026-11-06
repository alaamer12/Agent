# Phase 1 - understand the project, then break it into axes

You cannot find competitors for an idea you have not understood. The first move is not searching; it is
turning the user's idea into a structured set of *things to search on*. A single query - the project's own
one-line pitch - finds the top result and nothing else, which is precisely the failure the never-list warns
against.

## Extract first

Build the project brief from what the user gave, filling each line or marking it *unknown*:

| Field | Why it matters for discovery |
|---|---|
| Name + alternative names/spellings/translations | seeds the Name dimension, and its near-misses |
| Core concept and purpose | the idea-level similarity axis |
| Problems it solves (each one separately) | each problem is its own search axis - competitors often solve one and not the rest |
| Target audience(s), by segment | audience-level similarity; same product, different audience = different market |
| Main features/functionalities (enumerated) | the feature matrix rows; each feature can be a query |
| Claimed USPs | what the user *thinks* is different - Reveal tests it |
| Business model / monetization | model-level similarity and differentiation |
| Target countries / regions | the geographical axis, and the local-gap hunt |
| Supported languages (incl. RTL) | the localization axis |
| Platforms (web/Android/iOS/desktop/…) | where to look (app stores vs web vs repos) |
| Intended UX / how the workflow runs | workflow-level similarity, which survives feature-count differences |
| Distinctive technical or business approaches | the implementation-uniqueness axis |

If the user handed over a repo, README, spec, or landing page, read it and populate the brief from it. If a
path is given, that is an `investigate`-style read of local material feeding this brief - Reveal's subject is
still the outside world.

## Ask before assuming - the gate

Some unknowns change the entire investigation. Before spending a deep search on a wrong premise, ask the
user about the ones that would *materially* alter the findings:

- **Target market/geography** if unstated - "global" vs "Egypt and the Gulf" is a different search and often a
  different verdict.
- **Target audience** if vague - "everyone" gives no axis to differentiate on.
- **Business model** if it swings the competitive set (a free consumer app and a paid B2B platform have almost
  disjoint competitors under the same feature list).
- **The one or two things the user believes are novel** - so Reveal can test those specifically rather than
  guess which claims matter.

Do not interrogate on everything. State the assumptions you *are* making for the rest, plainly, in the plan,
so the user can correct them the way they correct a plan.

## Break the idea into search axes - the actual output of Phase 1

This is the deliverable of Phase 1 and the input to Phase 2: **a list of independent search axes**, not one
query. For each of these, generate several phrasings, in every relevant language:

- the core concept, stated 3-5 ways (the jargon term, the plain-English description, the "X for Y" framing,
  the competitor-category name);
- **each problem** it solves, as its own query ("how do people solve <problem>");
- **each major feature**, especially the ones the user thinks are unique;
- the **audience + need** combination ("<audience> tool for <need>");
- the **business model + domain** combination ("<domain> marketplace", "<domain> subscription", "freemium
  <domain>");
- the **name** and its near-collisions, translations, and alternate spellings;
- the **category** it belongs to ("alternatives to <known leader>", "<category> apps", "best <category> for
  <region>");
- the **adjacent** categories that solve the same job differently (a spreadsheet competes with an app for
  some jobs).

Each axis is a separate line of search in Phase 2. The number of axes, not the cleverness of one query, is
what determines whether the obscure competitor gets found. Write the axis list into the plan and get it
approved before searching, exactly as `mine` approves a source plan - so the user sees what will be searched
for and can add the axis they know matters.

## Anti-pattern

- **One query, the pitch verbatim.** Finds the leader, misses everyone else.
- **English-only search for a product aimed at Arabic/RTL users.** The local competitors are invisible.
- **Treating "no results for my exact phrase" as "no competitors."** The competitor does not describe itself
  the way you do.
- **Skipping the brief.** Without enumerated features/audience/markets there is nothing to score similarity
  *against* in Phase 3.
