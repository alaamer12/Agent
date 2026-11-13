# Verification — proving a redesign broke nothing

Everything else in this skill is about making a UI better. This is about proving it didn't
make a UI *wrong*, which is a different claim and needs different instruments.

It matters most for the whole-project cases — any pass over an
existing app with real data behind it — where "every data point preserved, all interactive
affordances intact" is a promise about 40 screens you did not look at one at a time.

The short version: **a claim you cannot demonstrate is not verified, and saying "I preserved
everything" after reading the diff is not demonstrating it.**

---

## Four separate claims, four separate pieces of evidence

They do not substitute for each other. Passing one says nothing about the others, and the
usual failure is presenting the easiest one as if it covered the rest.

| claim | question | evidence |
|---|---|---|
| **render** | does every page still mount a page? | a route walk with a render guard |
| **route** | does every page still mount the *right* page, rather than the app's own 404? | the same walk, fingerprinting the not-found screen |
| **runtime** | does any page now produce console output it didn't before? | the same walk, diffed against the original build |
| **value** | are the figures a person reads off the screen the same numbers? | extract label→figure pairs from both builds and compare |
| **behaviour** | is the logic that produces all of that still the logic that was there? | diff the script/setup bodies, not the templates |

`scripts/verify/` covers the first four. The last is a source-level read and is described
below, because it is where the damage actually hides.

---

## The control has to be the real original

A "before" that isn't the actual pre-redesign app is worse than no before, because it looks
like evidence.

The failure to avoid: taking the old page markup and mounting it inside the *new* shell,
with the *new* theme and stubbed data, then declaring the comparison valid because the files
came from the old commit. Nothing about that is the old product. It will differ from the
original in exactly the ways you are trying to measure, and agree with it in the ways you
need it to.

What a real control is:

- **A separate checkout of the pre-redesign state, running as its own app.** In git that is
  `git worktree add ../app-before <commit>` — a real tree, its own install, its own dev
  server. Not a copy of some files. Not a stub.
- **The same routes, the same data, the same account, both sides.** One route list, used
  twice. A page that exists on only one side is not a comparison.
- **Real data, not fixtures**, if the app has a working environment. A stub reproduces the
  shape of the API, never its edge cases, and the edge cases are the whole point.

If none of that is available — the app won't run, the database isn't reachable, there's no
way in — **say so, and label the pass as unverified** rather than quietly substituting a
weaker control. "I checked the markup carefully" is honest; "verified against the original"
is not, and will be believed.

---

## Your verification tooling can break the thing under test

This is the trap with the worst payoff, because it produces a confident false positive about
someone else's code.

What happened once: a control harness page was added inside the app's own root directory so
it could import the app's modules. The dev server treated every HTML file in that root as a
dependency-scan entry, so the new page pulled the *old* tree into the scan, the scan hit a
path that only resolved in the new tree, and the server skipped dependency pre-bundling for
the whole app. The redesigned dashboard then rendered zeros. The conclusion drawn — "the
redesign broke the data" — was true of the harness, not the redesign.

Rules that fall out of it:

- Keep control harnesses **outside** anything the app's build scans. A separate checkout is
  immune to this by construction.
- After adding any tooling file, **re-run the check against the app without your file** and
  confirm the result didn't move. If the number changed, you changed the experiment.
- When a verification result says the redesign is broken, **first try to break the
  verification.** Assume the harness is guilty until it is not. It usually is.

---

## Getting in: credentials, in this order

An unauthenticated sweep proves nothing — every page bounces to the login and reports a
clean console. `scripts/verify/auth.mjs` handles the mechanics; the ordering is the judgment
part, and it is a judgment call you should make out loud.

1. **Given to you now** — a flag or an environment variable. Use it and move on.
2. **Ask the person.** This is the default when (1) is empty, and it is one sentence:
   > I need a way into the running app to verify nothing broke. Is there a dev login I can
   > use, or a seeded test account? I'll pass it through the environment, not into any file.
   They almost always have one, and asking costs nothing compared to guessing wrong.
3. **Find it in the project** — seeds, fixtures, factories, `.env`, a testing README, docs.
   `auth.mjs --discover` prints candidate *locations* with values redacted, so nothing secret
   reaches a transcript while you look. Read the file yourself; never paste the secret back.
4. **Create a throwaway test user.** Last, because it writes to someone's database. Say that
   explicitly before doing it, and clean up after:
   > Nothing usable for auth, and I'd rather not guess. Can I create a temporary test user
   > (`verify-tmp@local`) to run the sweep, and delete it when I'm done?

Never write a credential into a tracked file. Never guess one. Never leave a created account
behind without saying you made it.

Two mechanics worth knowing regardless of framework:

- **A form bound to a model ignores a plain assignment.** Setting `el.value = 'x'` fires
  nothing; the framework's model stays empty and the form submits blank, which reads exactly
  like a broken login. Use the native prototype setter and then dispatch `input` — what a
  real keystroke produces.
- **Prove you got in, and treat a bounce as its own failure class.** Check the URL after
  submit. A page that redirected back to `/login` is not "no console errors"; it is an
  untested page. The sweep labels these `AUTH` separately so they can't inflate a clean run.

---

## Environment traps, each of which already produced one wrong conclusion

**The state that breaks may not be in your codebase.** Grepping the repo finds every *reference*
to a name; it cannot find the data that holds the name. Renaming an identifier — a route, a
permission, a feature key, a plan code — silently revokes or disables anything an external
system stored under the old spelling: auth-provider user metadata, a SaaS record, a cache key, a
queue name, a row in a table your migrations don't own. There is often no error and nothing to
diff. Before renaming anything that could have been *granted* rather than merely *written down*,
find where the value is persisted, and ship a forward alias so existing holders keep resolving.
The cheap version of this check: ask who else has ever seen this string.

**A scripted edit that reports success may have applied nothing.** Rewriting source with a
find-and-replace script is normal at rollout scale, and the failure is invisible: the patterns
are matched against text with `\r\n` line endings, so every multi-line replacement misses, the
script prints its summary line, and four intended edits became zero. Two rules: normalise line
endings before matching and restore them on write, and have the script **count what it applied
and abort if the number is not what it expected**. A tool that prints "done" without a count is
not reporting a result.

**One allowed origin.** If the API's CORS allowlist names a single origin, running two builds
on two ports means one of them gets *no data at all* and no visible error — just preflight
`OPTIONS` requests and a page of zeros. Run the two sides **one at a time on the allowed
origin**, save each record, and diff the files.

**The data moves.** Live databases change between captures; a real pair measured hours apart
went 241 → 243 funds and 11739 → 11800 users, which is a 100% "value parity failure" caused
by nobody. Capture both sides inside one window, or compare *structure* (which figures appear,
in what form) rather than the numbers themselves, and say which you did.

**When a figure looks wrong, go to the source of truth rather than adjudicating between two
UIs.** Both builds can agree and both be wrong, and neither can tell you which. Query the
database the page reads from and compare the raw count — that one step is what separates "the
redesign changed a number" from "the number was always that". Two mechanics: read connection
details from the environment rather than hardcoding them, and if the env file has CRLF
endings, sourcing it from a shell silently yields a value with a trailing carriage return —
parse it in the script instead.

**Zero is a digit.** "Every stat card now contains a number" is satisfied by a loading
skeleton. Require at least one non-zero figure *and* a reading that has stopped changing.
`--values` flags an all-zero capture for exactly this reason. This trap once made two healthy
builds look identically broken.

**Fixed sleeps are wrong in both directions.** Too short and you capture a skeleton; too long
and the walk takes ten times as long, so you sample fewer pages and feel falsely thorough.
Poll for stability with a ceiling instead.

**"No console errors" is also what a dead server says.** A page that never mounted produces no
errors, so every route needs a render guard before its clean console means anything — and one
guard is not enough. A mounted-node floor sounds sufficient and is not: a browser's own
connection-refused page has a heading, several paragraphs and dozens of nodes, and cleared a
25-node threshold on all five routes of a walk pointed at a port with nothing listening on it.
Check the navigation's own failure signal *and* that something resembling the application root
mounted. Then prove the guard works by pointing the walk at a dead port once per environment
and watching it go red.

**A deleted route can pass the render guard, because the app has a page for that.** The dead port
says `NOT RENDERED`; a route the router no longer knows about says nothing at all — it renders the
application's *own* not-found screen, inside the real shell, with a real `<h1>`, dozens of nodes and
a spotless console. That asymmetry is what let six routes which had been removed from the router
come back "ok" in a documented sweep of 73 whose headline was "0 failed to render". The claim the
sweep was being used to support was *every page still exists*, and the render guard was only ever
answering *every page still paints something*.

So the walk records both the route it asked for and the route the app says it is on
(`landed`), and classifies a route answered with the not-found screen as `NOT-FOUND` — a third
kind, kept apart from `NOT RENDERED` and from console errors, since each is a different thing to
fix. The detection is **on by default**, because a guard somebody has to remember to pass is a
guard that does not fire: the sweep navigates once to a path that cannot exist, learns what *this*
app's not-found page says, and then recognises that page wherever it turns up. It has to, because
a catch-all route (`/:pathMatch(.*)*`, or `path="*"` in React Router) renders the 404 component
*in place* — `location.pathname` still looks exactly like the route you asked for, so the URL alone
cannot tell you. Asking for the app's 404 path directly is not a failure, and the sweep says so
rather than padding the count.

Two honest limits. It reports `NOT-FOUND` and does not make the run exit non-zero, so an existing
green pipeline stays green — which means somebody has to read the line rather than trust the exit
code, and the parity report gives it a section of its own for that reason. And the fingerprint
matches on the not-found page's *sentences and heading*: an app whose 404 screen renders nothing but
a shell heading gives a weak signal, which the sweep admits in its output rather than reporting a
clean sweep. Point it at a deliberately dead route once per environment and confirm it says
`NOT-FOUND` — the same way you prove the render guard by pointing it at a dead port.

**An unbounded browser call hangs the whole walk.** One page that stops answering JavaScript
should be recorded as one failed page and the sweep should continue. Without a timeout on
every evaluation, the run stalls silently with no output, which looks like a broken app.

**A fixed debug port makes you drive a stranger's browser.** If a leftover instance holds the
port, the new one fails to bind, the endpoint answers anyway from the old process, and every
command goes to a wedged tab. Launch with port 0 and read the real one back from the profile.

**Killing processes by name pattern kills your own shell.** `pkill -f vite` matches the command
line of the shell running it. Kill by PID read from the listening socket, scoped to the port.

**Dev-server dependency caches go stale across restarts.** Symptom: "Failed to fetch
dynamically imported module" on pages that are perfectly fine, on both sides of the
comparison. Restart forced, then re-check the route before calling it a regression.

**Canvas and chart initialisation races are intermittent on both sides.** The same route can
error on one walk and pass on the next. Re-run the single route on *both* builds before
believing a one-sided error.

---

## Behaviour: markup is free, logic is frozen

The three machine checks above can all pass on a redesign that is broken, because they only
look at what the page renders. The remaining risk is in the source, and it has a specific
shape: **a design pass changes a component, and the component swap quietly drops behaviour
that still compiles.**

Read the diff with that in mind. Concretely, from passes that looked clean and were not:

- A control replaced by a hand-built primitive lost its `:loading` binding. The library it
  replaced derived `disabled` from `loading`, so the button became re-clickable while its own
  mutation was in flight — a double-submit bug, invisible in every screenshot.
- A renamed CSS class meant a grid never applied, so a stat strip stacked vertically and the
  page grew from 1.4 to 2 screens. Nothing errored; the layout was just wrong.
- A `v-if` moved from a wrapper onto its inner element, leaving a permanently rendered empty
  band where a dismissible banner used to collapse.
- A conditional that was *false* at runtime had been deleted along with the code it guarded —
  removing nothing observable, and breaking every future case where it turns true.

So, on the source side:

- **Diff the script/setup bodies, not the templates.** Templates are what you are allowed to
  rewrite; if the logic block changed, that is a finding to justify, not a detail.
- **Additions are fine, removals are not.** New imports and new presentational props are
  normal. A dropped binding, watcher, handler, guard, or computed is a behaviour change.
  Bindings that carry behaviour *and* look decorative are the dangerous ones: loading,
  disabled, options, rules, item-disabled.
- **Renamed or split routes must be re-granted.** If the app gates navigation by permission,
  a new route that isn't in the permission chain is unreachable to everyone except a
  super-admin — and it will look fine in a harness that bypasses auth. Enumerate every place
  a route name appears before renaming one.
- **A repeated colour is not always one colour.** If the original used the same hex for two
  meanings, a mechanical swap merges them; deciding they are now two tokens is a design call
  and should be written down where it can be reviewed.

---

## The most dangerous tool is the one that passes while comparing nothing

Every instrument in this directory failed silently at least once before it failed loudly. The
shapes they all share:

- a baseline generated from your own output, so it freezes the redesign instead of the original
- a key mismatch between two sides, so every item is "new" and every check is "not applicable"
  — reported as zero failures
- a regex that matches one framework's syntax, run against a project written in another, so
  every file looks "identical"
- a log filter on the wrong field value, so the errors you were hunting are dropped and the
  run is clean
- a render guard that asks *did something paint* when the claim being cited was *does this page
  still exist* — so a deleted route passes by painting the app's own 404 page
- a reviewer note that was never checked against the file it describes, so the ledger reports
  coverage rather than coverage-of-something

**Test each tool against a deliberately broken input at least once.** Inject an error you know
is there and confirm the tool reports it. If you cannot make it fail, it is not measuring —
and a green light from a tool that cannot go red is worse than no tool, because it gets cited.

---

## Report what you found but did not cause

A walk over a real app finds pre-existing defects: endpoints that 500, a null in one row that
crashes a computed, a chart that races. Those are not yours to fix inside a design pass — and
if you don't separate them, they will be attributed to you, or they will quietly get fixed in
a commit labelled "redesign" and nobody will know where the behaviour change came from.

So the report has three sections, always: **regressions** (yours), **pre-existing** (found,
not caused, not fixed — here's the evidence it fails on both sides), and **not tested** (what
you never touched). Write the record into the repository next to whatever system you built,
not into a chat log, or the next person re-runs the whole investigation.

---

## Then ask a human for the functional pass

Machine parity is a floor, not a verdict. The things that actually break in a redesign — a
filter that returns the wrong rows, a permission that no longer grants, a save that writes
half the fields — are invisible to a walk of first-load states. Hand over something concrete
rather than asking "want to check it?":

> Verified automatically: 73 routes render, each one a page rather than the app's own not-found
> screen, no console errors the old build doesn't also have, and the figures on every screen
> match. I did **not** test mutations, permissions on
> non-admin roles, or real devices.
>
> Could you click through these and tell me if anything is off?
> 1. The numbers on the main screens — do they match what you expect?
> 2. `<route>`, `<route>`, `<route>` — the pages that changed most.
> 3. Every filter, sort, page-size control, row action and bulk action.
> 4. Anything that writes: forms, saves, deletes, exports.
> 5. The browser console while you work — that catches paths I can't reach.

Item 4 matters more than the rest. A read-only sweep of a write-heavy app verifies the least
interesting half of it.

---

## When to stop and say so

If you cannot run the app, cannot get a session, cannot reach the data, or cannot compare
against a real original — report that as the finding, in one line, and deliver the pass
labelled as visually verified but not behaviourally verified. That is a useful answer. A quiet
narrowing of "nothing broke" to "the markup still contains the same fields" is not.

---

## Prove nothing broke — the second loop, for passes over a real app

"Verify by rendering" answers *is this screen calmer*. It cannot answer *did the app stop working* — and on a pass over a running application with real data behind it, that is the question the person actually cares about, because the preservation promises ("every data point", "all interactive affordances") are claims about screens you did not open.

So when the input is a real app rather than a single file or a mockup, run a second loop alongside the render loop:

1. **Get a real control.** The pre-redesign app, running as its own checkout (`git worktree add ../app-before <commit>`). Not old markup mounted inside the new shell with the new theme and stubbed data — that is not a before, and it will differ from the original in exactly the ways you are measuring. If the app cannot be run, say so and label the pass unverified rather than quietly substituting a weaker control.
2. **Get in, and prove you are in.** An unauthenticated sweep bounces every route to the login page and reports a spotless console, which is worth nothing. If you have no credentials, **ask** — it is a one-sentence question and they usually have a dev account; failing that, look for one in the project's seeds or env (`scripts/verify/auth.mjs --discover` prints locations, never values), and only then offer to create a throwaway test user, saying so first because it writes to their database. Never guess a password, never put one in a tracked file.
3. **Walk both builds over the same route list and diff.** `scripts/verify/sweep.mjs` then `parity.mjs`. Four separate claims, four separate answers: does every page still mount, does every page still mount *its own* page rather than the not-found screen, does any page now produce console output the other side doesn't, and are the figures a person reads off the screen the same numbers. Report each separately, because a pass on the first one is what hides a failure on the second.
4. **Read the source diff for behaviour.** Markup is free; logic is frozen. This is the damage that survives all three machine checks: a component swapped for a hand-built equivalent drops a binding that still compiles — a lost `loading`, and the button is re-clickable mid-mutation; a renamed class, and a grid never applied; a `v-if` moved inward, and a collapsed banner leaves an empty band. Diff the script bodies, not the templates. Additions are fine; a dropped binding, watcher, guard, or computed is a finding to justify.
5. **Walk the writing surfaces, in every state, at both ends of the range.** This is the half that a route sweep structurally cannot reach, because a crawler opens a page and reads it — it does not create a fund, submit a filter that returns nothing, break a validation rule, or lose a save. So: perform the three most common *tasks* end to end on both builds, and compare what it cost (clicks, keystrokes, screens, whether the thing you were comparing stayed on screen while you compared it). Force each state you can — empty, zero-result, forbidden, mid-save failure — and look at what renders. Shrink the viewport to the narrowest the product claims to support and do it again. Then do the whole thing with the keyboard only, and read the heading outline and the control names aloud, because nothing on a screenshot shows you that the screen went silent for someone who is not looking at it. **Redesign is where these regress, and a parity check is where you find out you caused it** — a dialog whose container changed width can now clip its own buttons, a restyled primitive can lose the binding that disabled the submit mid-save, and the render still photographs beautifully.
6. **Hand the person a functional checklist**, not "want to check it?". The numbers on the main screens; the routes that changed most; every filter, sort, page-size, row action and bulk action; **everything that writes** — forms, saves, deletes, exports; the states above; and the console while they click. A read-only walk of first-load states verifies the least interesting half of an app, and permissions on non-admin roles are entirely out of its reach.

Then report in three named parts: **regressions** (yours), **pre-existing** (found, not caused, not fixed — with the evidence that they fail on both builds too), and **not tested**. Commit the parity record next to the design system you built, or the next person repeats the whole investigation.

**Two warnings here are load-bearing.** First, your own verification tooling can break the thing under test: a harness page added inside the app's served root became a build entry, killed dependency pre-bundling for the whole app, and made a perfectly healthy redesign look data-broken — so when a check says the redesign is broken, try to break the check first, and re-run without your file before believing it. Second, every one of these instruments has at least once passed while comparing nothing: a baseline generated from your own output rather than the original, a key mismatch that made every page "new" and every check "not applicable", a log filter on the wrong field value. **Make each tool fail against a deliberately broken input at least once; if you cannot make it fail, it is not measuring, and a green light from it is worse than no check at all.**

Full method — the credential order, the environment traps (one allowed CORS origin, live data drifting between captures, "0 is a digit", dead servers that report clean consoles), and the behaviour-diff list: `references/verification.md`.


