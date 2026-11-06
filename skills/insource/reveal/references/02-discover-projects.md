# Phase 2 - discover what already exists, widely and in the dark

Discovery is where Reveal earns or loses its honesty. The famous names are the *starting* set; the skill is
judged on whether it found the obscure, the regional, the defunct, and the open-source ones. Work the axis
list from Phase 1 across as many independent source families as the project makes relevant.

## The source map

Not a checklist to run blindly - a map of *where different kinds of competitor live*. Pick the families that
fit the project (a dev tool barely lives on Instagram; a consumer app barely lives on SourceForge), but do
not skip a family just because the leader was already found elsewhere.

| Family | Sources | What it finds that others miss |
|---|---|---|
| General search | Google, Bing, DuckDuckGo, Brave, regional engines (Yandex, Naver, Baidu) | the plain-language and local-language players |
| Developer platforms | GitHub, GitLab, Bitbucket, SourceForge | open-source and abandoned implementations; the exact feature set, in code |
| App stores | Google Play, Apple App Store, Microsoft Store, Samsung Galaxy Store, Huawei AppGallery, regional stores | shipped mobile products with download/review counts; regional stores reveal local-only apps |
| Startup & product directories | Product Hunt, BetaList, AlternativeTo, G2, Capterra, Crunchbase, Wellfound, Dealroom, GetApp, SaaSHub | the long tail, "alternatives to X" lists, funding status, team size |
| Communities & social | Reddit, Hacker News, X, LinkedIn, Facebook groups, public Discords, niche forums, Quora, Stack Exchange | what people actually use and complain about; unmarketed tools; the "how do you handle X" threads |
| Company & product primary sources | official sites, docs, pricing pages, changelogs, press/launch announcements | the verified facts for the dimensions in Phase 3 |
| Archives & dead projects | Wayback Machine, app-store version histories, GitHub archived repos, "shut down" lists | who tried this and why they stopped - the most instructive competitors are often corpses |
| Native-language & regional web | searches in the target market's languages, local directories, local tech press | the regional players invisible to English search - often the *actual* competition for a regional idea |
| Cross-references | backlinks, "compare with" pages, review-site alternatives, competitor's own integration lists | competitors found by other competitors |

The list is not exhaustive: when a family clearly exists that this table does not name for this kind of
project, use it and note it. Discovery quality is measured by what turned up that was not obvious.

## Search technique that actually finds the obscure

- **Rephrase constantly.** Each axis gets several natural phrasings, in each relevant language; the competitor
  does not describe itself in your words.
- **Search the problem, not the product.** "how do freelancers in egypt collect payments" finds tools that
  never call themselves what you would.
- **Mine the leader's edges.** AlternativeTo/G2 "alternatives to <leader>", the leader's integration partners,
  its comparison pages, the review-site "people also consider" rails - each is a curated competitor list.
- **Follow people.** HN/Reddit/X threads where the category is debated name the small ones; a founder's
  "we built X" launch post is a discovery event.
- **Search for the graveyard.** "<category> shut down", "RIP <leader>", Wayback captures of dead startups -
  discontinued implementations prove prior art and sometimes reveal the exact reason the market was hard.
- **Vary the year and the freshness.** Old results are prior art; brand-new ones are emerging threats. A
  two-year-old Product Hunt launch with no updates is a different competitor than a funded one.
- **Go native.** For any target market, search in its language(s) on its engines and its stores; RTL and
  regional-market players are systematically invisible to English-only work.
- **Snowball until quiet.** Every competitor found is a source of new candidates (its alternatives list, its
  comparators, its community mentions). Keep expanding the frontier until it stops yielding.

## The stopping rule: diminishing returns, not a comfortable count

Discovery ends when a *full additional pass* - new phrasings, new languages, new families, snowballing the
newest finds - produces no competitor not already on the list. Operationally: keep a running frontier of
"candidates to investigate"; when two consecutive expansion rounds add nothing new across at least three
axes, discovery is done. Stopping after the first page of results, or after N names, or as soon as the list
"looks respectable", is the failure the never-list forbids. Record how many rounds it took and what the last
round found - that is the evidence the stopping was honest.

## Access honesty

Search only what is publicly reachable. Respect robots/access rules, authentication walls, and terms of
service; do not scrape gated content, do not fabricate "I checked the private Discord." When a relevant
source is inaccessible (a login-walled community, a regional store not reachable from here), **name it as a
gap in the limitations section** - an unsearched source is a known blind spot, and reporting it is part of
the deliverable. Never pretend coverage you did not get.

## What Phase 2 produces

A candidate competitor list with, for each entry: name, URL(s), where it was found (which axis, which
family), and a one-line "why it might be relevant." This list feeds Phase 3; nothing is scored yet. Merge
obvious duplicates now (same product, four directory listings), but do not prune aggressively - the
"probably not relevant" call belongs after the dimensions are filled, not before.
