# Anatomy — the contract every conditional page signs

Every page in this family is described by the same six fields before a pixel is designed. They
are the page's contract; the page file carries them, the map marks the family, the audit checks
them.

1. **Trigger** — the exact condition that produces this page, stated as a predicate on real
   state: "backend returns `status=settled` for order X", not "after payment". If the trigger
   cannot be written precisely, the page is not ready to design.
2. **Condition source** — who answers whether the trigger holds *right now*, at render.
   Server endpoints, verified token payloads, feature-flag reads. Never: the URL, a query
   param the client set, a `sessionStorage` flag from a previous visit (freshness rule: the
   page re-checks; a stale success page lying three days later is a defect of this field).
3. **Reachability states** — the page is designed for arriving in ways its journey never
   planned: deep-linked cold, bookmarked and reopened, back-button replay after the moment is
   gone, logged-out visit, *and* fresh in-flow arrival. Each state gets an answer — usually
   "re-check, then redirect or explain" — decided here, not discovered in QA.
4. **Exits** — primary way forward + at least one fallback for when the primary is impossible.
   No dead ends. An exit that returns the user into the flow is a route, not "history back".
5. **Continuation ownership** — what the page is allowed to *cause*: navigating onward, firing
   nothing. A success page never re-captures, a failure page never auto-retries on its own
   authority (retry policy = `contract` skill's `automatic_retry`/`manual_retry` when those
   exist — this page only renders the affordance the contract permits).
6. **Announcement** — how the page tells the person where they are, in every sense: heading
   hierarchy that names the state, screen-reader announcement on arrival (these pages mount
   mid-Journey, often from client redirects that fire no native announcement), and a message
   that survives translation — this family's text is quoted in support tickets more than any
   other.

## How the anatomy lands in the tree

The six fields are decided here, then recorded in the page file under `<docs>/pages/` at the
depth the page needs — a complementary page's sketch and notes carry its trigger, condition
source, reachability states, exits, continuation ownership and announcement. The root index
map marks the page kind=complementary and its family; the file shape is
`../../references/pages-tree-format.md`'s. Depth is opt-in (the format's guideline), but a
conditional page that cannot state its trigger and exits is not ready to design.

Exclusions are recorded like in `/pages main` — an outage page *deliberately absent because the
product has none of that operational story yet* is a decision that must survive the next
agent, not a gap it "helpfully" fills.