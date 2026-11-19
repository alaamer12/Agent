# /mine — search, mining, and writing technique

`references/workflow.md` covers *when* to do what (plan → mine → track
budget → distill). This file covers *how* to actually execute each of
those well — concrete technique, not policy. Read this alongside
`workflow.md`, not instead of it.

This file holds the long-form technique for the ecosystems where digging
needs more room than a summary block: codebase/GitHub and visual/design.
`references/source-ecosystems.md` is the index of every ecosystem this skill
reaches (documentation sets, research literature, specs, registries,
discussion corpora, postmortems, datasets) and where its candidates, tools
and census numbers come from — start there to identify the ecosystem, then
read the corresponding section here if one exists. These sections
are worked examples of applying the same underlying discipline (search
deliberately, prefer a purpose-built tool over manual work when one
exists, chase what → why → cost) to a specific domain — they're not a
closed list. A task pointing at a source type with no section here yet
still follows that same discipline; write a new section here — or a block in
`source-ecosystems.md` — afterward if the technique that worked is worth
keeping for next time (see
`workflow.md` for when this skill accumulates a new domain's technique).
"The ground census", "The source ledger", "The vintage gate", "The extraction
bootstrap", "Mining technique — going from 'what' to 'why'" and "Writing the
final document" are fully general and apply
regardless of source type — read the census section even for a source you
think you already know the shape of, and write the ledger even when the run
felt entirely local. For any artifact too big to read in one pass (book,
scan, transcript, scraped corpus), also read
`references/noise-and-density.md` before spending reading budget on it.

## The ground census — establish what a source IS before arguing why

Before interpreting anything, pin the source down in countable terms, and put
those numbers in the checkpoint. This is the one part of a checkpoint that is
not free-form, and the reason is load-bearing:

- **A "why" claim has no weight without a scale reference.** "They hand-rolled
  their own ORM instead of using the standard one" reads as principled minimalism
  at 20 contributors and a 40k-file repo, and as a plausible-looking accident at
  460 contributors and 33k tracked files. The reader cannot judge any
  decision — or judge whether *you* judged it — without knowing the size and
  shape of the thing the decision was made inside.
- **Absence claims are unprovable without it.** "There is no `search_path`
  anywhere in the ORM" only means something if the file says how many files
  existed and how many you could actually read. See the traps below.
- **The final document needs a shared spine.** Cross-source synthesis usually
  turns on a quantitative comparison ("every product past ~1M LOC grew a
  codegen layer; the two under 200k didn't") — that sentence is unwriteable
  if no checkpoint recorded the numbers, and unrecoverable after the run.

### The six ground-census fields (presence is mandatory, order and voice are not)

| Field | Codebase source | Visual/design source | Any other source type |
|---|---|---|---|
| **Identity** | owner/repo, branch or commit, release/version, license | product, screen or flow name, where it was captured, capture date | the exact named instance, plus its version/datum |
| **Magnitude** | tracked files, code bytes or LOC, number of repos/packages | pixel dimensions, viewport class, screens in the set | whatever number answers "how big is this one" |
| **Composition** | language/extension split, runtime split (client vs server vs build vs docs) | palette, type families, recurring component kinds | what the thing is made of |
| **Arrangement** | top-level directory map with a file count per entry, workspace/package manifest | layout regions and what sits in each | its sectioning or division |
| **Reach** | which method got you here, and what that method therefore could not show you | which tool, and whether you viewed the full screen or a crop | same — always stated |
| **Vintage** | when it was written and when it last moved (first/last commit, the release the README describes), plus **how you found that out** | when it was captured, and whether the product still ships that screen | its publication/last-update date with its evidence, or the honest "undated — here is what I checked" |

Write them as a table, a paragraph, or a few scattered lines — whatever suits
the source. What is not acceptable is a checkpoint that never says what the
source physically is, or that reports a number you did not actually measure.

**Reach is three numbers, not one.** Conflating them is what makes an
over-confident checkpoint, so keep them separate wherever you state them:
the *instances you could see* (paths in a tree listing, pages in a sitemap,
papers in an API's own total), the *content you could search* (the subset
actually on disk after a sparse checkout, the pages you successfully
downloaded, the PDFs you opened), and the *content you read closely* (files
you actually opened and reasoned over). "No code calls X" is a claim over the
second; "we never found a stated reason for X" is a claim over the third.
Name the denominator with the claim, and never let the first stand in for
the others.

**Name the measure whenever more than one exists.** File counts by extension,
linguist bytes, and raw `wc -l` will disagree on the same repo and any of the
three is defensible — what isn't defensible is a bare "the project is mostly
TypeScript" that could be any of them. Say which you used, once, at the top.
An extension split is also an approximation that quietly merges things:
`foo.test.ts` counts as `ts`, so a large test suite disappears into the
production-language tally — call out the split when tests, generated code, or
vendored paths are a big share of it.

For an ecosystem outside code and design, the six fields stay identical and
only what fills them changes — `source-ecosystems.md` names the numbers worth
taking per ecosystem (pages, version currency, and reference-vs-tutorial mix
for a documentation set; sections and MUST/SHOULD counts for a specification;
full-text-read versus skimmed versus abstract-only for a paper; downloads,
release cadence, and dependency count for a package). Census fields are a
contract with the reader, not a code-specific ritual.

### Census recipes that work (verified against real repos)

With a local checkout — any kind of checkout, including shallow, sparse, or
partial, since these all read the *index*:

```bash
git ls-files | wc -l                          # tracked files
git ls-files | sed -n 's/.*\.\([A-Za-z0-9]\{1,8\}\)$/\1/p' | sort | uniq -c | sort -rn | head -15
git ls-files | awk -F/ 'NF>1{print $1} NF==1{print "(root)"}' | sort | uniq -c | sort -rn | head -15
git ls-files -z '*.ts' '*.tsx' | xargs -0 wc -l | tail -1   # LOC for a language you care about
git rev-list --count HEAD                     # history depth — read the traps
```

Roughly 1–3 seconds on a 120 MB checkout; there's no excuse to skip it. For
LOC by language, prefer a real counter (`cloc`, `tokei`, `scc`) when the
environment has one — check first, because many do not, and the fallbacks
above are extension- and path-based approximations, not linguist-accurate.

Without a clone, the recursive tree API returns the same census in one request:

```bash
gh api "repos/<owner>/<repo>/git/trees/<branch>?recursive=1" \
  --jq '{truncated, entries:(.tree|length), blobs:([.tree[]|select(.type=="blob")]|length), bytes:([.tree[]|select(.type=="blob")|.size//0]|add)}'
gh api "repos/<owner>/<repo>/git/trees/<branch>?recursive=1" \
  --jq '.tree[]|select(.type=="blob")|.path' | sed -n 's/.*\.\([A-Za-z0-9]\{1,8\}\)$/\1/p' | sort | uniq -c | sort -rn | head
gh api repos/<owner>/<repo> --jq '{size_kb:.size,lang:.language,stars:.stargazers_count,license:.license.spdx_id,created:.created_at,pushed:.pushed_at}'
gh api repos/<owner>/<repo>/languages        # per-language byte split
gh api "repos/<owner>/<repo>/contributors?per_page=1" -i 2>/dev/null | grep -io 'page=[0-9]*>; rel="last"'
```

Cache the tree JSON once (`> cache/<repo>_tree.json` in the run directory) and
re-cut it with `jq`
locally instead of re-hitting the API per question — it's also the cheapest way
to answer "does path X exist anywhere" at whole-repo scale.

Cross-checked: on one repo, the tree API and a real clone produced *identical*
extension splits, so a disk-blocked run loses nothing on the census itself —
only on reading file contents. Contributor headcount comes free from the last
page number of that `Link` header. Cache count matters more than it looks:
team size is what tells a reader whether a decision was made by a design or by
an accident of staffing.

For visual/design sources the census is mostly manual and short: dimensions
(`identify`/`file`, or the tool's own metadata), how many screens in the set
and how many distinct products, which viewports, the recurring component kinds
you can actually enumerate by looking, and the dominant colors if you can
sample them. Estimate nothing you can count; count nothing that needs a claim
about the product's internals you cannot see.

### Traps that make a census wrong (all of these are real)

- **Shallow clones silently report one commit.** `git rev-list --count HEAD`
  returns `1` at depth 1. Never state a commit count, author count, or churn
  timeline from a shallow clone without deepening (`git fetch --deepen N`) or
  using the API — and if you can't, write "history not available (depth 1)".
- **The repos API `.size` is not the code.** It's KiB of the packed repo
  *including full history* — observed at ~324 MB on a repo whose tracked code
  is 17.9 MB, an 18x difference. Label it "repo incl. history" or don't quote it.
- **`/languages` is linguist, and linguist excludes things.** Vendored,
  generated, and `.gitattributes`-marked paths are dropped, so its byte split
  will not match either your extension count or your raw byte total. It also
  counts a docs site's MDX as part of the product. Say which measure you're
  quoting.
- **The tree API truncates without warning.** `truncated: true` means the path
  list stops early — observed cutting off mid-directory on a very large repo at
  ~58k entries. Report the flag; a truncated tree cannot support any
  "this doesn't exist in the repo" claim.
- **`git ls-files` reads the index, not the disk.** On a sparse checkout it
  lists files you never downloaded — observed 13,084 indexed against 6,859
  actually on disk. Great for the census; fatal for grep claims. Any
  "no code does X" must state it's a content grep over the checked-out subset
  (`find . -path ./.git -prune -o -type f -print | wc -l` to get that
  denominator), and a *path*-level claim ("no file named Y") should say it came
  from the full index or full tree.
- **Raw-fetch-only measures nothing.** If you fetched N individual files, you
  have no file/language census at all. That is a legitimate outcome — but write
  "not measured: method was N raw fetches against one branch", never a blank.
  Silent omission and honest unavailability look identical to the parent and
  read very differently later.

### What this changes in the opening of a checkpoint

Thin (method bounds present, ground absent — how most of these files actually
start):

> **Repo:** `<owner>/<name>`, `main`, ~2.42, NestJS + GraphQL + Postgres + React.
> **Method (disk-bound).** Full recursive tree + ~15 raw fetches + DeepWiki.

Grounded (same length, now comparable to the other 29 sources):

> **Repo:** `<owner>/<name>`, `main`, package version 2.42, AGPLv3 + file-level
> Enterprise headers, 57.2k stars, created 2022-12, 463 listed contributors.
> **Scale:** 41,294 tree entries (`truncated:false`) → 32,818 files, 317 MB
> tracked, 99.6% of paths under `packages/` (20 `twenty-*` packages +
> `create-twenty-app`). **Language:** linguist puts TypeScript at 91.5 MB of
> 114 MB total — 22,878 `.ts` + 4,822 `.tsx` files — i.e. a single-language
> monorepo with one server tier and one web client, no native tier.
> **Method (bounds this):** whole-tree *path* visibility, but file *contents*
> for ~15 of those 32,818 files. Every absence claim below is therefore a
> path-level or targeted-search claim, not a content grep — flagged per claim.

Same move for a design source: name the product and screen, its dimensions and
viewport class, what's on it, and how much of the flow you actually saw versus
this one frame.

## The source ledger — every URL you actually touched

Every checkpoint **ends** with a list of the endpoints it really used. This is
the one more structural requirement the floor makes, and it exists because of
what happens after a run: checkouts get deleted, sandboxes reset, pages move,
and the parent's spot-check has to click something. A file path quoted in prose
is a claim; a file path with the URL it came from is a citation.

It is a **receipt list, not a bibliography** — record only what you actually
fetched or opened. That includes the things that failed: a 404 you aimed at is
evidence about the source and saves the next agent the same dead request. It
excludes the search-result page you glanced at and dismissed, and anything you
merely know exists.

Tag each entry with what it did, then one clause of context. Roles, grouped or
in order used — your choice, same rule as the rest of the file:

- `reached` — got bytes; may never have been opened.
- `read` — opened and reasoned over; these are the ones that back claims.
- `searched` — a query endpoint whose *result list* you used (note the query
  and what it returned, including zero hits — a negative result is a finding).
- `partial` — got some of it (truncated tree, paywalled section, JS shell).
- `failed` — 404/403/timeout/empty; keep it, and say which.

**Pin what you cite.** A URL to a mutable branch is a URL that will lie later:
cite code by commit (`raw.githubusercontent.com/<o>/<r>/<sha>/path#L10-L20`, not
`/main/`), papers by DOI or arXiv id **with version** (`v2`), and any web page by
its exact URL plus the date you fetched it. If all you have is `main`, say so in
that entry — it means the line numbers may not survive the day.

**The fetch date is not the source's date, and writing only the first is how a
2014 page gets cited as if it were this year's.** `fetched 2026-11-18` records
when *you* arrived; it says nothing about when the thing was written, and placed
alone at the top of a ledger it reads as currency. Every ledger block therefore
carries both, on separate terms: `fetched <date>` for the visit, and
`published <date> (<how>)` / `updated <date> (<how>)` for the source — where
`<how>` is the evidence the next agent could re-check, not a bare year. An
undated page says `undated (no byline date, no metadata; earliest Wayback
snapshot 2019-04)` rather than going quiet. How to get a date that honest is
the next section.

**Log while you fetch; never reconstruct afterwards.** Rebuilding a URL list
from memory at write-up time reliably produces confident, invented links, which
is the fastest way to poison a run — the parent spot-checks exactly these.
Appending as you go is nearly free: `curl … | tee -a scratch/<slug>-urls.txt`, or
paste the source URL into the header of every raw response you cache under
`sources/`, and the ledger is then a one-line `grep` away.

**Scrub before you write it down.** Strip credentials and signed-URL query
strings — `?sig=`, `X-Amz-Credential`, `X-Amz-Signature`, SAS tokens, `access_token`,
private-repository tokens, session params. A signed URL *is* a bearer secret:
anyone holding it holds the object until it expires. This list is a log, and the
rule against secrets in logs is absolute (see the repo's own
`Docs/base/security-and-privacy.md` when working in this project). Keep the path,
drop the query, and note "query string redacted (signed URL)" so the omission is
visible rather than silent.

**The ledger is the audit trail for your reach numbers.** If the census says
"read 15 files of 32,818", there should be roughly 15 `read` entries; if it says
4 of 20 doc pages downloaded, 4 entries should be `partial`/`failed`. A mismatch
means one of the two is wrong — fix it before closing the file, not in the
distillation.

Shape of the closing block, with the tags doing the work:

```markdown
## Sources touched — fetched 2026-09-21, commit-pinned at 58e3976

- reached  https://api.github.com/repos/<owner>/<repo>/git/trees/58e3976?recursive=1
           → cached at sources/<slug>/tree.json (truncated:false, 41,294 entries)
- read     https://raw.githubusercontent.com/<owner>/<repo>/58e3976/src/vs/base/parts/ipc/common/ipc.ts
           → file last touched 2023-07-14 (`git log -1 --format=%ad -- <path>`)
- searched https://github.com/search?q=repo%3A<owner>%2F<repo>+path%3Adocs%2Fadr&type=code
           → 0 hits: no ADR directory (a negative result — the checkpoint's
           "the project keeps no ADRs" claim rests on this line)
- partial  https://www.<vendor>.com/blog/why-we-chose-x → 1,200 chars then a signup wall
           → published 2014-03-11 (JSON-LD `datePublished`, no `dateModified`):
           eleven years old, and it argues for the v2 API the project deprecated
           in 2021, so under this run's time-critical reading it backs the
           "they chose X" claim only, not the "so X is the right call" one
- failed   https://objects.<cdn>.githubcontent.com/<signed-path> → 403 after pin expiry;
           query string redacted
```

## The vintage gate — how old is this source, and how do you actually know

This exists because of a specific hole. A dig for database guidance accepted a
2014 blog post. The post resolved, so link verification passed; it was a real
source, so the plan accepted it; the agent genuinely read it, so the checkpoint
and ledger were honest; and the ledger stamped it `fetched 2026`, which made it
*look* current in the run record. Every check `/mine` has asks whether a source
is **real** and whether you **actually read it**. None of them asked whether it
is **still true** — because nothing in the run ever recorded the one fact that
would have raised the question. A missing field can't be spot-checked: the
parent verifies the dates a checkpoint states, and there was none to verify.

**The gate is not a year.** Age is only a defect relative to what the run is
for, and the three readings are settled per task in Phase 1, before discovery
(`workflow.md` → "Settle the run's time-sensitivity before discovery"):

- **Time-critical** — the field moved under the source, so an old page
  misleads rather than merely pre-dating you. Tooling and library guidance,
  framework and API usage, security practice, pricing, "which library should I
  use", anything where the honest answer depends on what shipped this year.
  Here an old source needs an affirmative reason to stay, not a pass by default.
- **Time-anchored** — the date *is* the datum. "What did people believe about
  X in 2014", the history of a decision, a postmortem of a named incident.
  Filtering for recency here deletes the only sources that answer the question.
- **Timeless** — age carries no penalty, and the oldest source is often the
  best one: algorithms and theory, the classic papers, the founding spec, the
  reasoning that still holds. A 1979 paper on B-trees is not a stale source; it
  is the primary source, and a recency filter applied to research literature is
  a bug, not a safeguard.

So the run declares its reading once, the sources each carry their date, and the
judgment happens against the declared reading — never against an inherited
reflex that 2014 means obsolete or 2026 means current.

### Getting a date is a reach problem, and reaches get the same rule as everything else

A publish date is almost never in a search snippet, so this is not fixable by
searching harder. The principle is the one `workflow.md` already states for
every other reach: **manual inspection is the fallback, not the default —
check for a purpose-built tool first**, and stay general about which tool that
is, because the landscape turns over faster than this file does.

1. **Use what this environment already has.** Some harnesses ship a professional
   reader or search tool internally (one that returns cleaned content with its
   structured metadata rather than a snippet), and some have a connector on
   offer — a Firecrawl/Jina-class reader, a docs-extraction endpoint, or an MCP
   tool for the specific platform. If one is connected, use it for dates the way
   you'd use it for content, and note it in the plan's "Mining tool".
2. **If none is connected, look for one, and ask.** Same sequence as the
   reach-tool check (`workflow.md` → step 2 and step 4): search the current
   landscape for a fitting tool, then fold the offer into the message that
   presents the plan — connect it, or proceed manually — and say plainly if it
   needs a paid plan or the user's own API key, so the choice is informed. A run
   that will read forty pages has a real reason to ask; a three-source run does
   not, and you're the one who knows which this is.
3. **Then read what the source itself offers, strongest-as-a-*publication*
   date first.** Stop at the first rung that answers, and record which one gave
   it. The order below is by how well each signal supports *"this is when it was
   written"* — which is not the same as how easy each is to find, and the two
   get conflated into wrong dates:

   - **The platform's own API or registry fields**, where one exists: registries
     carry a per-version `time` map, arXiv carries v1 and every revision's date,
     GitHub gives first-commit / last-push / release dates, forum and Q&A APIs
     give `creation_date` and `last_edit_date` per post. Structured, typed, and
     about *the object* rather than the page rendering it — nothing in HTML beats
     these, so check for one before scraping markup.
   - **The dateline printed on the page** — a `<time datetime="…">` element, an
     "18 November 2026" byline, a running `29 May 2019: published` changelog the
     author keeps in the body. This is often the **only** publication date that
     exists, and it is the normal case for hand-authored writing: probed
     2026-11-18 against a long-running individual engineering blog, which served
     **no JSON-LD at all** and exposed only a *modified* stamp, while its real
     date sat in a visible `<p class='date'>` and in the entry `<id>` URI.
     Read the rendered page, not just its head.
   - **Structured metadata in the document head**: JSON-LD `datePublished` /
     `dateModified`, `<meta property="article:published_time">`,
     `og:updated_time`. Reliable where present and typical of CMS-generated
     sites; frequently absent where an author writes their own HTML — so its
     absence is a finding about the source, not a licence to guess.
   - **Feeds and sitemaps**: RSS `pubDate`, Atom `published` / `updated`,
     `sitemap.xml <lastmod>`. All three are weaker than they look: an Atom feed
     commonly carries **only** `<updated>` (verified on the same blog), the
     sitemap's `<lastmod>` is a *touch* date the CMS sets on deploys, and the
     conventional paths 404 more often than documentation admits (that same
     blog has no `/sitemap.xml`; the Cloudflare blog does, with `<lastmod>` on
     every entry). Try to *find* them via a `robots.txt` `Sitemap:` line or a
     `<link rel="alternate">` in the head — but only where the site offers them,
     since the tested blog offered neither: its robots.txt declares no sitemap
     and its articles link no feed, so probing conventional paths is a
     legitimate fallback before concluding the source publishes no dates at all.
   - **Dates the prose implies**: a version number with its own release date, a
     named incident, "we migrated in 2019 after…". Inference — label it — but a
     page describing API v2 *is* datable when nothing on it says so.
   - **An archival floor**: the earliest Wayback snapshot bounds the age from
     above (a page captured in 2014 was not written in 2026) and the latest
     bounds its *silence* — no snapshot since 2019 is evidence nobody kept it
     current.
   - **Nothing found** → write `undated`, list what you checked, and treat the
     date as unknown rather than as no-date-means-new.

**A modified date is not a published date, and reporting it as one is the
specific way a machine-readable date goes wrong.** Sites publish `dateModified`
/ `article:modified_time` / `<updated>` far more often than they publish the
original, and a 2014 post whose typo was fixed in 2025 will hand you
`2025-05-01` from a field you trusted because it was structured. Take the
*earliest* defensible birth signal, name the field it came from, and when only a
modified date exists, write it as `updated 2025-05 (article:modified_time;
published date not stated)` — which is a real answer to a different question.

**Parse, don't grep the head.** Metadata does not have one spelling: the same
property appears as `content="…"`, `content = '…'`, with `property=` or `name=`,
or only inside a JSON-LD block, and a pattern written for one convention misses
the others *silently* and returns "no date found" for a page that is fully
tagged. Ask a reader tool or an HTML parser for it; if you must scan by hand,
scan case-insensitively for the value shape (`20\d\d-\d\d-\d\d`) across the whole
document and then work out which field each hit came from.

**What never counts as a date**: the year in the URL slug (archives get
re-hosted, and `/2014/03/` may be a CMS path the platform chose, not a
publication), the footer copyright range (that is the site's build year, updated
on schedule for content nobody has touched in a decade), a search-result
snippet's date, the domain's registration age, and your own memory of when
something was written. Nor does HTTP `Last-Modified`: probed 2026-11-18, a page
whose own dateline and `og:article:modified_time` both read `2019-05-29` was
served with `Last-Modified: Thu, 12 Nov 2026` — a deploy artifact seven years and
six months after the writing, which would date a 2019 article to six weeks ago.
Of everything on this list, memory is the quietest
failure: it is indistinguishable in the checkpoint from a real finding, which is
exactly the disease the ledger was written against.

**Mark the date's status the way this file marks its endpoints.** `published
2014-03-11 (JSON-LD datePublished)` is re-checkable fact; `~2014 (earliest
Wayback snapshot; page states no date — inferred)` is a judgment with its
reasoning attached; a bare `2014` is neither, and reads as the first while being
the second.

### Age is not the only way a source goes stale — check whether what it describes still exists

Two 2014 pages are not the same risk. One describes how to shard a database the
project deleted in 2021; the other describes why sharding is hard, which is not
a thing that expired. The cheap test is not the date but the **object**: name
what the source is *about* — the version, API, product, library, standard
revision — and check whether that thing is still current, deprecated, or gone.
Where the object is verifiably superseded, the source's *date* stops mattering
and its *subject* decides; where the object is stable, an old date costs you
nothing. This is also why "actively-maintained" alone was never enough: a
well-maintained repo can document a dead convention, and an abandoned one can
contain the only correct explanation of how something works.

### When age and authority disagree, the user decides — not the file

The 2×2 has two corners the skill must not silently resolve. **Old and
authoritative** — the engineer who built the feature writing it up in 2014, a
commitfest thread, the original spec — often outranks anything recent, because
recency is a proxy for relevance and authority is the thing the proxy was for.
**New and thin** — this year's SEO listicle — passes a date filter and carries no
knowledge at all. So judge the pair together, with the reason on the page: who
wrote it, what gives them the standing, is it self-promotion, does it describe
the thing or merely mention it, and what its date costs *under this run's
reading*.

Then, when the call is genuinely contestable — a source the plan's reading
disqualifies that looks authoritative, an authoritative source you suspect is
obsolete, or a load-bearing claim that would rest on either — **ask the user,
with the date, the evidence for the date, and the venue in the question**, and
let them drop it, keep it, or narrow what it may support. Don't open a separate
round-trip per source: fold the question into the next message the run was
sending anyway (the same batching rule the tool-offer step uses), and raise the
whole batch once rather than interrupting mining for each page.

A **subagent cannot ask.** It records the conflict in its checkpoint — source,
date + evidence, authority read, what it would be used for, what's contestable —
and keeps mining within whatever the plan approved; the parent collects these and
raises them as one question, exactly as it spot-checks their ledgers. An agent
that quietly drops a source has destroyed the only signal that the run's plan was
wrong.

### The other two modes, where vintage means something different

In **run-mining** you measure the candidate today, so its *behavior* can't go
stale — but the docs you read to write its adapter can, and the mode's known
trap is precisely a stale favorite: abandoned-but-installed, download counts
that lag reality (`source-ecosystems.md`). Record last release and last commit
as census, note an unmaintained-but-winning candidate as a *result* with its
date rather than dropping it, and prefer the current docs of the thing over any
write-up about it.

In **case-mining**, a case's date is when the incident happened and it never
expires — a 2014 postmortem is not outdated about a 2014 failure, and filtering
cases for recency throws away the corpus. What can expire is the **handling**:
the remedy may name a tool that no longer exists. Date the event and the
handling separately, and where a handling is superseded, mine what replaced it
as the case's current form rather than quietly keeping the obsolete advice.

## The extraction bootstrap — prove the reach pipeline once, then hand it to every subagent

Most source types beyond repos-and-screens are not directly readable: a PDF
must become text, a scan must be OCR'd, an HTML tree must become Markdown, an
episode must become a transcript, a dataset must become sampled rows. That
conversion step — *reach* in the six-question sense — is where runs quietly
die, in two distinct ways: each agent redoes it differently (or one agent
redoes it N times), **or the whole run is built on a converter that produces
confident garbage.** The second failure is the expensive one, because of the
chain it starts: a weak converter produces weak experiences (every agent reads
the same garbled page), weak experiences produce a weak essence (the
distillation is only as true as what actually reached it), and a tidy ledger
makes the garbage look *sourced* — receipts certify that a URL was fetched,
not that the tool parsing it was right, so nothing downstream can smell the
error. The bootstrap exists to break that chain at its root, before fan-out.

The sequence, in order of cheapness:

1. **Search for the current tool landscape — never pick a converter from
   memory.** This is a fast-moving field: a new open-source model released
   last month may already beat the established names on OCR, ASR, or PDF
   parsing, and whichever list is in your weights is stale by construction.
   So before choosing any conversion tool, run the discovery like any other
   discovery question — search "best open source [PDF extraction / OCR /
   speech-to-text] <this year>", check what's recently changed (a tool's repo
   activity, a benchmark leaderboard, a release announcement), and treat the
   agent's own memory of tool names and standings as a *hypothesis to verify*,
   never a source. The same rule applies in both directions: don't assume the
   famous tool is still best, and don't assume the new thing on the leaderboard
   is — verify both against the next two steps.
2. **Enumerate the candidates — open source *and* paid — and refuse to assume
   which category wins.** For every conversion job there is usually a
   professional/hosted option and a free/library option (hosted ASR vs open
   ASR models, commercial document-OCR vs `tesseract` vs a parsing library).
   Neither category holds the quality crown by default: open implementations
   currently lead some benchmarks for some languages, accents, and document
   types, and hosted products lead others — and standings move. Pick by the
   actual axes: accuracy *on this kind of content* (see step 3), cost and
   rate limits, what this environment can actually run, credentials the user
   has, and whether the output shape is greppable.
3. **Run the accuracy gate before the run commits to a tool.** Take ONE real
   sample of the actual content — one page of this scan, a two-minute stretch
   of this audio, one two-column page — convert it with the leading candidate,
   and *personally verify the output against ground truth*: read the rendered
   page next to the extracted text; listen to the segment next to the
   transcript. Count errors where it matters: a small character-error rate is
   harmless for skimming structure and quietly lethal for verbatim quotes.
   The gate decides "accurate enough for what this run will *do* with the
   output" — skim vs cite vs measure are different quality bars. When free and
   paid are both viable and the choice has real consequences (spend, or the
   accuracy claims depend on), present both to the user *with what you just
   measured on their content*, not with brand reputation — in the plan-approval
   message, same fold-in as the connector choice. "The open model beat the
   hosted one on this clip and costs nothing" and "the hosted one is worth $N
   because the open one mangles this domain's jargon" are both legitimate
   findings; an unmeasured assumption in either direction is not.
4. **Look for what's already installed and shipped.** Sibling skills first
   (in this repo, `scrape` for docs sites), then installed binaries
   (`pdftotext`, `pandoc`, `tesseract`, `gs`, `ffmpeg`, an ASR model), then
   language libraries (`pypdf`, `pdfplumber`, `pdfminer`), then platform APIs
   that return the converted form directly (provider-hosted transcripts,
   arXiv source, RFC `.txt`). Check what *this* environment actually has — do
   not assume a tool exists because it is famous, and do not assume it's
   missing because one check failed. A tool behind a paid API the user hasn't
   opted into is not "available."
5. **If nothing exists or nothing passes the gate, adapt rather than
   downgrade the source.** Hand-roll the minimum that makes the content
   greppable or readable: a loop over page-range reads via a PDF-capable
   reader; `curl` + a HTML→text filter; rendering pages to images and reading
   them visually. Label the method honestly in the census Reach field —
   "OCR'd, 2018 scan, expect character errors in quotes" is a usable census
   fact; an undetectable pipeline is a lie waiting to be quoted.
6. **The main agent mines the pipeline once, by hand, on ONE sample
   artifact** — before any subagent spawns. Not "verify the tool runs" but
   actually run the full chain end-to-end: fetch → convert → noise-profile →
   read a slice, so every failure mode shows itself while it still only
   costs one artifact's budget (wrong tool for scanned PDFs, encoding junk,
   missing fonts, rate limits, the 400-page file that isn't what its name
   claimed).
7. **Codify the proven sequence into a script under the run's `tools/`
   directory — every mining task generates its scripts.** Not only fan-out
   runs: per-task jobs are what the run's toolset is made of — split a PDF
   by page range, cut an audio segment, sample frames at a stride, profile
   page density, dedup images by perceptual hash, harvest table pages. A
   sequence worth running twice is a script. Each takes the artifact (path
   or URL) and emits the standard products: extracted text and/or per-page
   word profile into `cache/`, the noise map into `witness/`, and URL/version
   lines ready for the ledger. Required properties: a `--help` that states
   inputs and outputs; a fixed output-location convention so every consumer
   knows where results land; a one-line header recording the tool + version
   it wrapped — *including which ASR/OCR tool produced which transcript, so
   the accuracy provenance travels with the citation* — and an explicit
   "this artifact is scanned/empty/failed" outcome, because a pipeline that
   silently produces empty text is worse than one that errors: an agent will
   summarize nothing as content.
8. **Test the script once on a second, different artifact** (a second book,
   a differently-generated PDF) before distribution — the one-sample proof
   overfits to the first file, and a bug found after twelve subagents shipped
   is twelve runs poisoned.
9. **Every mining brief then points at the script, not at prose.** "Read
   `<run>/tools/extract.sh --help` and call it on your assigned artifact;
   consume `cache/` output; do not re-derive extraction" beats explaining the
   pipeline in words in six different briefs. This is the same argument the
   shared brief already makes — a dozen agents with one definition of the
   work — applied to the *tool* instead of the *checklist*.

This is strictly beneficial whenever fanout is involved — N agents re-deriving
an extraction pipeline by hand is N× the cost and N× the variance — but the
script is worth writing even for a solo run mining ten PDFs, for the same
reason the checkpoint files are: the third one reuses what the first one
proved, and a re-run of the whole job months later is `tools/` + `sources/`
already on disk.

## Searching professionally — codebase/GitHub sources

### Discovery search (finding candidates for the plan)

A single query like `"best 20 enterprise projects github"` is a starting
point, not a finished search. Vary the angle across a few queries rather
than trusting one phrasing:

- **By ranking signal**: `"most starred <topic> repositories github <year>"`,
  `"awesome-<topic>"` (GitHub's "awesome list" convention curates
  high-quality project lists by domain — searching for the awesome-list
  itself is often higher-signal than searching for projects directly)
- **By authority**: `"<topic> github trending"`, or asking who the
  acknowledged reference implementations are (`"canonical <topic>
  implementation open source"`)
- **By recency, if it matters**: append a year when the plan settled this run as
  time-critical (a fast-moving ecosystem's "best" list from three years ago may
  no longer reflect the current landscape). This shapes *which candidates you
  find*; it is not a source's date and never excuses one — a 2014 post still
  reaches your candidate list through a stale link, a quote, or a search that
  returned it anyway. Dating and judging the sources you end up with is
  "The vintage gate", and it runs per source on top of whatever discovery did —
  on the candidates at plan time, and on every source actually read in Phase 2.

Cross-reference at least two independent lists/sources before finalizing
candidates — a single "top 20" blog post reflects one author's opinion,
not a verified ranking. Where the user gave an explicit ranking criterion
("by stars 2026"), search GitHub directly rather than trusting a
third-party list: GitHub's own search supports `stars:>N`, `language:`,
`pushed:>YYYY-MM-DD` (for activity recency) as real filterable qualifiers,
not just prose to include in a query.

### Mining search — digging into why, once a repo is selected

This is where most of the actual "why" lives, and it's a different search
problem than discovery — you're now searching *inside and around* one
specific project, not comparing many.

DeepWiki is used as the concrete example below because it's a real,
currently-available tool that fits this domain well — not the only or
permanent answer; the same "check for a fitting tool first" principle
from `workflow.md` applies to codebase sources as to any other, so if a
different or better tool turns out to be in play for this run, use it the
same way DeepWiki is described here.

**If DeepWiki was chosen for this run (see workflow.md → "Identify the
source type and check for the best tool first"), query it before falling
back to manual search for any candidate it covers.** It's pre-indexed
specifically for this kind of deep, structural, rationale-level question
about a repository, so it often answers a "why" question directly where
manual search would need several rounds of fetch-and-read to piece
together the same answer. Fall back to the manual techniques below when a
candidate isn't covered, or when DeepWiki's answer to a specific question
is thin or unconvincing — the two are complementary, not exclusive.

But it is an *index of* the repo, not the repo. When you have a real
checkout on disk, the project's own `docs/`, architecture notes,
`CONTRIBUTING`, lint configs and code comments are primary evidence and
outrank any summary of them — use the index to aim your reading and to
generate candidates for a question, never as a substitute for it. Re-verify
its concrete claims before writing them down: an index can lag `HEAD`, and
it will happily name a file that no longer exists. (A stale name that
survives into a checkpoint becomes a citation to something a reader cannot
find, which is the worst kind of error to ship.)

**Use GitHub's own search operators, not just prose queries, once you're
inside a specific repo:**
- `repo:<owner>/<name> path:docs/adr` — architecture decision records, if
  the project keeps them (not all do; don't force this if a repo clearly
  has none)
- `repo:<owner>/<name> "why we" OR "we chose" OR "instead of" OR "decided
  to"` — searches issue/PR/discussion text for the actual language
  maintainers use when explaining a decision, which surfaces rationale
  that a README summary strips out
- `repo:<owner>/<name> path:CONTRIBUTING.md` — often states conventions
  and *why* they're enforced, more candidly than user-facing docs
- `language:<lang> path:<module>` scoped to the repo — for tracing how a
  specific concern (auth, state, rendering) is actually organized, rather
  than reading the whole tree

**Chase the discussion, not just the code.** A merged PR's diff shows
*what* changed; the PR description and review comments above it usually
show *why*, including alternatives that were considered and rejected —
which is exactly the kind of implicit-to-explicit information this skill
exists to surface. Closed issues linked from a PR often contain the actual
motivating pain point.

**Read commit history and churn as evidence when nothing is written down.**
Many real architectural decisions are never documented in prose at all —
they're only visible as a pattern in how the code changed over time. A
cluster of commits migrating files from one directory pattern to another,
or a spike in changes to one module right before a version bump, is a
signal of a decision even with zero accompanying explanation. When
mining a project with sparse documentation, this is often the only way to
recover "why" at all — note explicitly when a conclusion comes from this
kind of inference rather than a stated source, so the final document can
reflect that distinction (see workflow.md's Origin-query framing: stated
vs. only inferable is a real, worth-preserving distinction).

**Trace a concrete path through the system**, not just its file layout.
For anything request/event-driven, follow one real flow end to end (e.g.
a single HTTP request from entry point through middleware to response) —
this surfaces structural decisions that a directory listing alone won't,
because the *reasons* for a layer boundary often only make sense once you
see what actually has to cross it.

## Searching and analyzing — visual/design sources

Applies when the task points at visual references rather than code — UI
screens, dashboard designs, app flows, marketing pages, and similar.
Mobbin is used as the concrete example throughout this section because
it's a real, currently-available tool that fits this domain well — not
because it's the only or permanent answer. If a different or better tool
for this domain is connected or found (see `workflow.md` → "Identify the
source type and check for the best tool first"), use it the same way:
prefer it for candidates it covers, fall back to manual search/fetch for
anything it doesn't.

### Finding and collecting candidates

**If Mobbin was chosen for this run** (see `workflow.md` → "Identify the
source type and check for the best tool first"), use its search tools
directly — natural-language queries against its screen library (e.g.
"dashboard layouts with sidebar navigation," "SaaS analytics screens")
rather than general web search, since it's a curated, purpose-built
library and returns real, current product screens with metadata (app
name, category) attached. Its "deep" search mode is worth using over
"fast" when the query is nuanced rather than a simple keyword match — it
interprets intent and scores relevance rather than doing plain keyword
retrieval.

**Without Mobbin** (not connected, or the user doesn't have access),
fall back to general image/web search against design gallery sources —
Dribbble, Behance, Awwwards, or a plain image search scoped to the topic
(`"dashboard website design examples"`, `"SaaS dashboard UI screenshot"`).
Prefer sources that show real, shipped products over speculative concept
art or AI-generated mockups where the task is about how real designs are
actually built — concept work optimizes for looking striking in a
portfolio, not for the real constraints (data density, error states,
responsive behavior) that shape production designs.

### Per-image analysis — what to actually look at

For each image, once collected (and past the dedup step — see
`workflow.md` → Phase 2 → "Dedup after collection"), look
at it closely enough to describe, concretely:

- **Layout structure** — grid/column structure, where primary navigation
  lives, how content areas are proportioned relative to each other, what's
  above the fold vs. requires scrolling.
- **Information hierarchy** — what draws the eye first, second, third;
  how that's achieved (size, color, whitespace, position) rather than
  just naming that a hierarchy exists.
- **Color scheme** — the actual palette in use (base/neutral colors vs.
  accent/action colors), and where accent color is deployed (is it
  reserved for primary actions only, or used more broadly) — this is
  often a deliberate signal of what the design wants the user to notice.
- **Spacing and density** — tight/dense vs. generous whitespace, and
  whether that varies by section (e.g. dense in a data table, generous
  around a primary CTA).
- **Typography** — how many distinct type sizes/weights are in use, and
  what each is doing (labels vs. data vs. headings vs. body).
- **Specific components and patterns** — what recurring UI patterns are
  present (cards, tabs, a specific chart type, a particular nav pattern)
  and how they're specifically styled here versus a generic version of
  that pattern.

This description is the "what." The "why" chase (see "Mining technique"
below) applies the same way it does for code: what's the obvious
alternative to this layout/color/spacing choice, why might this one have
been chosen instead, and what did it cost (e.g. a dense data table trades
scannability for information density; heavy whitespace trades information
density for a calmer, more premium feel). For visual sources, "why" is
almost always inferred from the design itself and cross-referenced
against what's known about the product/audience (a fintech dashboard's
density choices likely serve a different user than a consumer wellness
app's) rather than found in an explicit stated source the way a GitHub
PR discussion might state a reason directly — note this lower certainty
explicitly in the checkpoint file and the final document, the same way an
inferred-from-commit-history conclusion gets flagged in the codebase
track.

## Mining technique — going from "what" to "why"

For each notable thing found — a module boundary or dependency choice in
a codebase, a layout or color decision in a design — ask, in order:

1. **What is this** — plainly, so you're not skipping straight to
   interpretation of something misread.
2. **What's the obvious alternative** — the thing most projects in this
   space do instead, or the "default" choice a newcomer might expect.
3. **Why this instead of that** — search for the answer (via the
   techniques above) before guessing. If a stated reason exists, use it.
   If not, look for indirect evidence (commit timing, an issue thread, a
   maintainer comment elsewhere) before concluding it's genuinely
   undocumented.
4. **What did that decision cost** — every real architectural choice
   trades something away. If the "why" surfaced in step 3 doesn't include
   a cost or tradeoff, that's often a sign the stated reason is a
   simplification (marketing-flavored) rather than the full picture — dig
   one level further before accepting it.

This four-step chase is what separates "the auth module is separate from
the API layer" (a fact) from "the auth module was pulled out after two
incidents where API changes accidentally altered session validation,
which cost them a decoupled-but-more-verbose call pattern they still
consider worth it" (the actual understanding this skill exists to
produce).

## Writing the final document

The core distinction to hold onto: **summary restates a source; synthesis
draws a conclusion that only exists because multiple sources were
considered together.** A paragraph that could have been written after
reading one project's README is a summary, no matter how well-written.
A paragraph that could only have been written after seeing the same
tension resolved differently across several real projects is synthesis —
that's the target.

Concretely, this means:

- **Organize around ideas, not around sources.** If a paragraph starts
  "Project A does X, Project B does Y, Project C does Z" (or "Design A
  does X, Design B does Y"), that's a structure imposed by the source
  list, not by the idea. Instead, lead with the idea itself ("teams
  converge on X once scale forces Y," or "dashboards aimed at expert users
  consistently trade whitespace for density") and let specific sources
  appear as evidence inside that idea, not as the organizing unit.
- **State what a comparison actually reveals, not just that a comparison
  exists.** "Both approaches handle this differently" is not synthesis —
  it's an observation waiting to become one. Push to the actual
  conclusion: differently *how*, and what does the difference imply about
  what each team was optimizing for.
- **Reach for the census numbers when they carry the argument.** The
  ground facts from each checkpoint are comparison fuel, not decoration: a
  threshold that several sources cross together ("every product past ~1M
  LOC grew a codegen layer; the two under 200k never did"), or a source
  that's an outlier on one count while agreeing on the rest, is exactly the
  kind of conclusion that could only exist because many sources were
  measured the same way. Report the threshold as an observation about these
  sources, never as a universal law — the sample is the sample.
- **Let genuine uncertainty stay uncertain.** Where a "why" was only
  reached through inference (commit-history reading, not a stated source),
  say so plainly rather than writing it with the same confidence as a
  documented decision. Distilled understanding that's honest about its own
  confidence is more useful than understanding that reads as more certain
  than it is.
- **Make every specific claim trace back to a ledger entry.** The
  distillation reads as understanding, not as footnotes — but a concrete
  assertion ("keeps no ADRs", "one pool shared by every tenant", "the docs
  never mention the timeout") should correspond to something some source's
  checkpoint actually *read* or *searched*, not to something that felt true by
  Phase 4. If you can't locate which, that's a signal: either the claim was
  never checked, or it's the kind that belongs in the run's stated-uncertainty
  column. Say which, in the journey document, rather than letting a reader
  discover it.
- **Don't perform completeness.** A distillation that mentions every
  candidate evenly, in the order they were mined, reads as a report with
  the headers removed — not as understanding. If three projects turned out
  to be the real source of insight and the rest confirmed what was already
  clear, the writing should reflect that imbalance honestly rather than
  smoothing it out for the appearance of thoroughness.
