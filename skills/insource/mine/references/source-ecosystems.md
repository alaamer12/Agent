# /mine — source ecosystems

`workflow.md` says when to do what; this file says **what a source can be**.
`/mine` is not a GitHub skill that tolerates other inputs — it mines whatever
class of thing the task points at, and a topic about documentation, research,
or standards deserves the same professional reach-and-mine treatment that
codebases already get here.

Use it like this: find the ecosystem closest to the task, read its block, and
if nothing fits, use "The generic shape" at the bottom — then come back and
write the missing block once you've actually done the run. A block earns its
place by having been used, not by being imagined in advance.

Every block answers the same six questions, because those six are what the
four phases need from any domain:

1. **Candidate** — what counts as one source here?
2. **Discovery** — where the list of real, good ones comes from.
3. **Reach** — how to get the actual content, cheapest-first.
4. **Census** — what "how big / what is it made of" means for this kind.
5. **Why** — where rationale actually lives in this ecosystem.
6. **Dedup / traps** — how sources fake distinctness, and what silently lies.

And every checkpoint closes the same way, in every ecosystem, with a **source
ledger** — the URLs it actually touched, tagged `reached`/`read`/`searched`/
`partial`/`failed` (rules, pinning, and the scrub-before-you-write step are in
`search-and-mining-technique.md` → "The source ledger"). What legitimately
counts as one is ecosystem-specific, so each block's own ledger line says:

| Ecosystem | A ledger entry looks like |
|---|---|
| Codebase | commit-pinned `raw.githubusercontent.com/<o>/<r>/<sha>/<path>`; the tree/repos API call; the clone's remote + SHA |
| Visual/design | the reference tool's screen URL or image URL, plus the product page it was captured from |
| Documentation set | the sitemap or `--auto` start URL, then each page URL that produced a local file — and each page that `--verify` rejected |
| Research literature | the search-API query URL (with its returned total), then DOI / arXiv abs id **+ version** / PDF URL for each item opened |
| Spec / standard | the `rfc-editor.org`/body-index document URL, its `Obsoletes` neighbours, and the working-group archive thread you read |
| Package registry | the registry metadata endpoint, the tarball URL, and the linked repo — each separately, since the two disagree |
| Discussion corpus | the API query URL and the individual thread permalink (`…/issues/1234#issuecomment-…`), never just the search page |
| Postmortem / org writing | the article URL, its date, and the archive/wayback URL when the live one moved |
| Dataset / model | the hub card URL, the file listing API, and the specific sample rows/partition you actually opened |

A claim with no matching ledger entry is the tell that it wasn't really
checked — and a ledger entry you never opened is the tell that the census
overstated reach. Both are worth catching here rather than in the
distillation.

**Verification labels are mandatory in this file.** `verified` = run against a
live endpoint in this environment and it worked; `unverified` = plausible and
worth trying, but nobody has run it here. Do not upgrade one to the other from
memory — re-run it, and if it fails, fix or delete the line. This file is
useful exactly as far as it can be trusted.

---

## Codebases and repositories

See the two long sections on GitHub technique in
`search-and-mining-technique.md` — that's the worked example this whole file
generalizes from. Summary of the six:

- **Candidate:** a repo (or a product's 2–3 repos).
- **Discovery:** GitHub search with real qualifiers (`stars:>N`, `language:`,
  `pushed:>`), awesome-lists, cross-referenced against a second list.
- **Reach:** local clone (`scripts/fetch_repo.sh`) → else recursive tree API +
  targeted raw fetches, in that order of preference; disk budget decides.
- **Census:** files, code bytes/LOC, language split, top-level directory map,
  contributors, age.
- **Why:** ADRs, `CONTRIBUTING`, PR descriptions and review threads, closed
  issues, commit clusters, churn spikes, code comments.
- **Dedup/traps:** forks of each other; archived/mirror repos that are not the
  real home; a monorepo that quietly contains six of your "distinct"
  candidates.

## Visual and design references

- **Candidate:** one screen/flow/frame, not a whole site.
- **Discovery:** a design-reference tool's own search if connected, else image
  and gallery search (Dribbble, Behance, Awwwards) — prefer shipped products
  over concept work.
- **Reach:** the tool's image fetch, or direct download; keep every file
  available together, since dedup needs them side by side.
- **Census:** pixel dimensions and viewport class, screens in the set, distinct
  products behind them, recurring component kinds, palette.
- **Why:** almost always inferred from the artifact plus what you know about the
  product's audience; there is rarely a stated rationale next to a screenshot.
  Say so — the confidence label matters more here than anywhere.
- **Dedup/traps:** the same screen cropped twice, one template resold across
  listed "products," a marketing shot that isn't the real UI.

## Documentation sets and doc sites (HTML / Markdown)

For "how does everyone document X," "the guidance across these 8 frameworks,"
"what do the official docs actually say about Y."

- **Candidate:** a documentation *set* (a product's docs tree, one spec's
  chapter, a book) — one per source, not one page, unless the task is explicitly
  page-level.
- **Discovery:** the site's own `sitemap.xml` (check it first — it is the
  honest table of contents), generator-typical paths (`/docs/`, `/stable/`,
  `/vN/`), and the repo's `docs/` tree when the project is open.
- **Reach:** **use the sibling `scrape` skill rather than hand-fetching pages**
  — read its `SKILL.md` first. `<docs-skill>/scripts/scrape.py --auto
  <START_URL> --output <dir>` lands a whole set as local Markdown you can then
  Grep properly; `--verify` is the gate that proves the pages are
  server-rendered with real content instead of a JS shell. Registering
  `<url> --verify` before committing to a source is cheap insurance. If
  `--auto` discovers 0 or the wrong subtree, fall back to explicit `--url`
  pages and record that the set was only partially reached.
- **Census:** pages in the set, total Markdown bytes, the section breakdown
  (top-level nav → page counts per section), how much is reference vs
  explanation vs tutorial, and version currency (latest release vs what the
  docs cover — compare the two, it is frequently a finding).
- **Why:** rationale hides in the gaps — what a doc set *omits* about an
  obviously-available feature, which options it warns against, why a page
  exists at all, repeated "do not"/"prefer" phrasings. Cross-check docs
  against the implementation when one is public: the distance between them is
  usually the real story.
- **Dedup/traps:** one doc generated from one source file counted four times
  (per-language tabs), versioned copies of the same page presented as distinct
  guidance, and client-rendered content that never reached your Markdown —
  `--verify`'s `JS-RENDERED`/`THIN` outcomes exist for exactly this. **Never
  cite a doc page you did not successfully download.**

## Research literature and papers

- **Candidate:** one paper — but decide in the plan whether the unit is a paper,
  a research *line* (a paper plus its key replies), or a survey.
- **Discovery:** arXiv's Atom API `verified`, Crossref `verified` (better
  metadata + citation counts, covers non-arXiv work), OpenAlex and Semantic
  Scholar `unverified here` (Semantic Scholar returned HTTP 429 without a key in
  this environment — expect to need a key or to back off). Also chase
  references *out of* a good paper (`api.crossref.org/works/<DOI>` →
  `.reference`) and citations *forward from* it — one snowball pass beats three
  keyword queries.
- **Reach:** abstract from the API, then the full text: arXiv `/abs` and
  `/pdf`, Crossref `link[]` / Unpaywall for open copies (Unpaywall needs an
  email param), the authors' project pages, and openreview/PMC where they
  apply. `Read` accepts PDFs directly, which makes local PDFs greppable.
- **Census:** and this one is different in kind — **the honest denominator is
  how many papers you read in full versus skimmed versus only read the abstract
  of**, and it belongs in the checkpoint before any claim about the field.
  Also: corpus size from the search API's own total, venue, year spread,
  citation counts (with their age caveat), and how many of the corpus you
  actually opened.
- **Why:** the introduction's "prior work fails at…" sentence is the stated
  reason; the ablation section is the evidence for it; related-work sections
  name the alternatives that were rejected. Papers disagreeing is the finding —
  don't smooth it, and check whether they're using the same word for the same
  thing before calling it a disagreement.
- **Dedup/traps:** preprint and published version counted as two sources; the
  same result republished under a slightly different title; survey papers
  mined as primary evidence (they're secondary — that's commentary about the
  thing, not the thing, which Phase 1 already forbids for codebase tasks and
  applies identically here); and abstract-only claims reported as findings.

## Specifications, standards, and RFCs

- **Candidate:** one specification (or one RFC, one SEI/3GPP document, one
  W3C Recommendation).
- **Discovery:** the issuing body's own index — `rfc-editor.org`, IETF
  Datatracker, W3C `/TR`, IEEE/ISO catalogs, `openssf`, `whatwg`, ECMA —
  plus the `Obsoletes`/`Obsoleted-by` chain, which is a free list of what the
  field tried and replaced.
- **Reach:** plain text where it exists (`https://www.rfc-editor.org/rfc/rfcN.txt`
  `verified`, note the leading BOM), HTML from the same body otherwise, and
  `curl` + `pandoc`/`scrape` to turn either into greppable Markdown.
- **Census:** sections/pages, word count, and — genuinely useful here — the
  keyword profile: `grep -cE '\bMUST\b'`, `\bSHOULD\b`, `\bMAY\b` gives a real
  measurement of how prescriptive a document is, and comparing that across
  sources is exactly the quantitative cross-source observation Phase 4 wants.
  Status (Proposed Standard / Full Standard / Experimental / Historic), plus its
  version lineage.
- **Why:** never in the document — in the working-group mailing list archive,
  the minutes, the `Security Considerations` and `Changes` sections, and above
  all in what the previous version said that this one deleted. Diff two
  versions of the same spec when both are reachable; a removed sentence is
  usually a settled argument.
- **Dedup/traps:** informational and obsoleted documents mixed into a "current
  practice" list; a document's own examples implemented inconsistently by real
  parties; mining the marketing summary of a standard rather than the text.

## Package and service registries

For "what does the ecosystem converge on" — the dependency ecosystem around a
problem, not one project.

- **Candidate:** one package (or a family of alternatives solving one problem).
- **Discovery:** registry search plus reverse dependency listings; GitHub
  topic search; the download charts (`npm` trends, `pypistats`, crates.io
  downloads).
- **Reach:** `npm view <pkg> --json`, `https://pypi.org/pypi/<pkg>/json`,
  `https://crates.io/api/v1/crates/<name>` — all `unverified in this
  environment`; the point is that a registry API is usually one request, and
  the real artifact is on the registry tarball or in the linked repo.
- **Census:** weekly downloads, age and release cadence, dependency count
  (a strong proxy for how much it takes on), maintainers, license, and version
  count.
- **Why:** READMEs argue for themselves; the signal is comparative — why a
  smaller-downloaded package won a niche, what a package depends on instead of
  implementing, what its issue tracker's most-asked rejected feature is.
- **Dedup/traps:** abandoned-but-installed defaults (download counts lag
  reality), thin wrappers over each other, typosquats, and counting a package
  and its fork as independent choices.

## Discussion corpora (issue trackers, forums, mailing lists, Q&A, social)

For how a field actually reasons — proposals, rejections, and consensus,
including all the parts that never made it into documentation.

- **Candidate:** one thread / RFC proposal / dispute — its full chain of
  replies, not just the original post.
- **Discovery:** `gh api search/issues` `verified` for GitHub discussions; the
  HN Algolia API `verified` (`hn.algolia.com/api/v1/search?query=&tags=story`);
  Stack Overflow's API (works, rate-limited and needs a key at volume,
  `unverified here`); a project's mailing-list archive; Reddit's `*.json`
  endpoints (`unverified here` — commonly UA-blocked, expect to need a
  deliberate user agent or to skip it).
- **Reach:** the API's own pagination; keep raw JSON responses on disk in
  `sources/` so a claim can be re-checked without re-fetching.
- **Census:** threads read, replies per thread, how many threads were
  actually decided versus left open, participant counts and their standing
  (core maintainer? drive-by?), and the date span.
- **Why:** this ecosystem *is* the why — its whole value. The specific thing to
  record is the counterfactual: the alternative that was argued for and lost,
  and what the winner conceded. A thread that ends in "we'll do X for now"
  is a decision plus a known cost.
- **Dedup/traps:** one person's opinion surfacing in five cross-linked threads,
  consensus that's really just the loudest maintainer, and survivorship — the
  ideas that were never written down leave no thread to mine. Also: a
  discussion is a **secondary** source about the artifact; when the artifact is
  reachable, check the claim against it and say which you did.

## Companies, products, and postmortems

For "how do real teams operate this," where the source is an organization's own
writing rather than its code.

- **Candidate:** one document (an incident postmortem, a rearchitecture writeup,
  a changelog entry, a status page) or one product's whole corpus — say which
  in the plan.
- **Discovery:** engineering-blog aggregators and HN, `status.` /
  `<product>/blog` / `/changelog` conventions, RSS, sitemap probes, and vendor
  docs' "limitations" pages, which are postmortems in disguise.
- **Reach:** direct fetch, then `scrape --url` to turn HTML into Markdown when
  you'll need to grep it.
- **Census:** documents read per org, their date span (postmortem culture is
  recent — the year range is itself data), and how public the org's
  self-assessment is.
- **Why:** stated freely, which is the appeal and the trap. A published
  postmortem is a *narrative* the org chose; read it against what the code or
  the docs now do, and note where the account and the artifact diverge.
- **Dedup/traps:** conference-talk versions of the same story, vendor content
  marketing posing as engineering, and one loud company setting the vocabulary
  everyone else then repeats in their own postmortem.

## Datasets, benchmarks, and models

- **Candidate:** one dataset / benchmark suite / model release.
- **Discovery:** Hugging Face Hub and Dataset Card indexes, Papers-with-Code,
  Kaggle, a lab's own catalog. `unverified in this environment` across the
  board — check before relying on an endpoint.
- **Reach:** the model/dataset card and file listing first (`--verify` the size
  before any download — these are the largest disk hazards this skill meets;
  the run's disk budget outranks your curiosity). Sampling is legitimate:
  reading 50 rows and the schema honestly bounds "what this dataset is."
- **Census:** rows/size/split structure, label and feature inventory, license
  and any usage restriction, collection method stated by the authors, provenance
  and last update.
- **Why:** the card's "collection process" and "known limitations" sections are
  the rationale; benchmark numbers are the cost ledger. A dataset's
  composition bias is usually only visible from its own collection
  description — which is exactly what a what→why pass recovers.
- **Dedup/traps:** the same corpus repackaged under several names (check by
  size and row count, not title), a benchmark with leaked test data, and a
  derivative counted as an independent source.

## The generic shape (for anything not listed yet)

When the task points at an ecosystem with no block here, don't force it into
one of the above and don't declare `/mine` inapplicable. Ask, in order:

1. **What is one instance of the thing?** — the unit of a source, settled
   before discovery, stated in the plan.
2. **Who maintains an authoritative index of those instances?** — nearly every
   domain has a catalog, registry, archive, sitemap, listing API, or a curated
   list someone already keeps. Find it, and prefer it over general web search;
   that index is also where the honest *count* comes from.
3. **What tool reaches it in bulk?** — the "check for a fitting tool first"
   principle from `workflow.md`, applied without assuming manual is the only
   option. If you must hand-fetch, cache raw responses under `sources/`.
4. **What numbers describe the thing itself?** — these become the census. Any
   source can be counted on at least two axes; if you can't find two, you
   haven't looked at enough of them yet.
5. **Where does rationale live, and is it stated or only inferable?** — usually
   one of: a design doc, a changelog, a discussion, a diff between versions, a
   limitation section, or the artifact's own shape.
6. **How does a source fake being distinct?** — mirrors, derivatives, reboots,
   per-format copies of one underlying object.

Then write the checkpoint under the same floor as every other source type —
identity, magnitude, composition, arrangement, reach, why, cost — and add the
finished block to this file afterward, with commands labelled `verified` only
if you actually ran them.
