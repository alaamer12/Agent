# /mine — search, mining, and writing technique

`references/workflow.md` covers *when* to do what (plan → mine → track
budget → distill). This file covers *how* to actually execute each of
those well — concrete technique, not policy. Read this alongside
`workflow.md`, not instead of it.

This file has parallel sections for source types encountered so far —
read whichever matches the current task's source type (see `workflow.md`
→ "Identify the source type"), not all of them by default. These sections
are worked examples of applying the same underlying discipline (search
deliberately, prefer a purpose-built tool over manual work when one
exists, chase what → why → cost) to a specific domain — they're not a
closed list. A task pointing at a source type with no section here yet
still follows that same discipline; write a new section here afterward if
the technique that worked is worth keeping for next time (see
`workflow.md` for when this skill accumulates a new domain's technique).
"Mining technique — going from 'what' to 'why'" and "Writing the final
document" are fully general and apply regardless of source type.

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
- **By recency, if it matters**: append a year when freshness matters to
  the topic (a fast-moving ecosystem's "best" list from three years ago
  may no longer reflect the current landscape)

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
`workflow.md` → "Visual/design-specific: dedup after collection"), look
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
- **Let genuine uncertainty stay uncertain.** Where a "why" was only
  reached through inference (commit-history reading, not a stated source),
  say so plainly rather than writing it with the same confidence as a
  documented decision. Distilled understanding that's honest about its own
  confidence is more useful than understanding that reads as more certain
  than it is.
- **Don't perform completeness.** A distillation that mentions every
  candidate evenly, in the order they were mined, reads as a report with
  the headers removed — not as understanding. If three projects turned out
  to be the real source of insight and the rest confirmed what was already
  clear, the writing should reflect that imbalance honestly rather than
  smoothing it out for the appearance of thoroughness.
