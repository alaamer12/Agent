# Case: the bot wall that ended a task that should not have ended

## The stop that was actually a pivot

A task: "collect the job postings from [example boards] into our dataset." The agent built a
fetch loop, hit page two, and met an anti-bot challenge wall — 403s, JS challenges. It wrote:
**"Scraping blocked by bot protection; task cannot continue."** and stopped. Every line of that
report was true except the last one. The route was closed. The goal was not.

## What the pivot sweep looks like on the same task

Restate the outcome without the route: *"the user needs current listings in this category, as
structured rows"* — nothing in that sentence says "via HTML fetches of board X."

Sweep the families, in order, with results recorded:

1. **Same source, different door.** Check the board's own low-friction surfaces:
   `robots.txt` allowances, sitemap index, RSS feeds for saved searches, the JSON endpoint the
   board's own web app calls with modest headers, its public API-with-free-tier. → Two saved
   searches had RSS; the structured endpoint answered with proper attribution headers and a
   polite crawl delay. Partial coverage obtained, no wall touched.
2. **Different source, equivalent content.** The same listings category is published by three
   aggregators, a government labor-board export, and the union's monthly PDF. → The government
   CSV covered 70% of fields with better structure; the aggregators' public search pages
   filled the rest at a respectful volume.
3. **Different method, same objective.** Where breadth was impossible, depth was not: daily
   delta collection of the obtainable slice instead of one bulk harvest.
4. **Reduced but honest deliverable.** Assemble rows from families 1-3; mark the two fields
   that would have come only from the walled board (`internal_ref`, `apply_deadline`) with
   their would-have-been source and the reason they are absent — visible in the dataset, not
   hidden.

## The two reports, side by side

**Illegitimate stop:**
> Blocked by anti-bot protection. Task failed.

**Legitimate completion of a pivoted goal:**
> The HTML route is bot-protected (I did not attempt to defeat it — that would need your
> explicit order). Sweep result: RSS + official free endpoints gave 4 of 6 boards; the
> government export plus two aggregators covered 93% of rows with the fields that matter for
> your downstream use; `internal_ref` is absent (exists only behind the wall). Dataset built
> and validated; daily-delta script scheduled for the obtainable slice. To get the last 7%: a
> paid API key for the walled board — a 10-line adapter I stubbed and left ready.

Only that last line meets the real stop condition: an outside-world supply, named, with
everything else finished and the swap made trivial.

## The lesson, generalized

Obstacle encountered → the implicit syllogism *"goal = this route, route dead, goal dead"* is
**a false premise you invented at planning time, not a fact the world owes you**. The
impossibility claim the skill permits requires a written sweep list — a claim without the list
is "I gave up," which is not on the list of valid stop reasons.