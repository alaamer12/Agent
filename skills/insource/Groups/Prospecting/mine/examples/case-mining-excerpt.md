<!--
  A short excerpt illustrating the TONE and SHAPE of a case-mining Phase 4
  output — the counterpart to distillation-excerpt.md (read-mining) and
  run-mining-excerpt.md (run-mining). Not a template to fill and not a complete
  example (a real run's catalog would carry the full case list and its coverage
  map). The point: like a run-mining verdict, ONE thing here is deliberately
  structured — the per-case card fields — because a browsable, individually
  actionable entry IS the deliverable. Everything before the cards is the same
  free-form reasoning as any distillation: it leads with the honest shape of the
  list, not a count dressed up as coverage. Carry over the honesty markers a
  read checkpoint uses: `attested@` (documented in a source you actually reached),
  `derived` (reasoned out of the scenario space, nothing vouches for it),
  `inferred` (handling reasoned from a source that shows the symptom but not the
  remedy), a stated thin family, and the dedup collapse that turned a padded
  target into the real number. Debugging is the worked example; the shape is
  topic-agnostic.
-->

**Coverage:** I mapped the space onto four axes — *phase* (repro / localize /
inspect / confirm), *artifact* (live process · core `.dmp` · log stream ·
distributed trace), *trigger shape* (deterministic · intermittent · after-N-hours
· race · clock), and *environment* (dev · prod-only · under load · offline). The
request was "50 cases"; the honest set is **34** after dedup, because four of the
attach-related cards I'd started all prescribed the same non-invasive attach +
snapshot handling and merged into one — a family with four names and one remedy
is one case. **21 attested** across 9 sources (a book, three postmortems, two
bug-tracker threads, a vendor troubleshooting guide, a conference talk, and the
protocol spec's error section), **13 derived** — situations the grid says must
occur that nobody had bothered to write up. The **offline-artifact family is
thin** (2 cases) and I did not manufacture a third to round it out.

---

**Case 07 — Attach to a live process without stopping it**
*Situation:* prod service is degraded but still serving; a debugger that pauses
or restarts it is itself an outage, so the reproduction is off the table.
*How you recognize it:* you can only get a *snapshot*, not a stop-the-world —
the moment you attach destructively the latency/health check you're chasing
clears. That's the tell it's this case and not a local repro.
*Handling path:* read-only / non-stop attach → dump thread stacks + a heap
sample → detach before touching breakpoints; treat the snapshot as the artifact
and reason against it offline (folds into case 09). Reproduce only after you've
harvested prod state.
*Tools/techniques:* `perf`/`py-spy`-style sampling, language non-stop debug
mode, eBPF for kernel-level without halting. `attested@` (book §"production
debugging" + vendor troubleshooting guide).
*Pitfalls & cost:* sampling at too high a frequency perturbs the very latency
you measure; a "read-only" attach on some runtimes still safepoints the process.
The cost is you get *aggregate* state, not a stepped view — confirmation still
needs a repro.

**Case 12 — The failure that appears only after ~100 hours**
*Situation:* service runs clean for four days, then degrades and won't recover
without a restart — no code deploy in between.
*How you recognize it:* the trigger is *elapsed state*, not an input — a leak,
fragmentation, a rotating credential/cert expiring, log/temp accumulation,
a counter wrap. If restarting fixes it and a fresh instance never shows it,
suspect this family.
*Handling path:* don't try to reproduce at 100 h — compress the axis. Force the
slow variable to turn over fast (shorten the cert TTL, shrink the heap so GC
pressure arrives in minutes, seed the cache to its four-day size) and watch the
resource curve, not the wall clock. Bisect on *state accumulation*, not commits.
*Tools/techniques:* resource-over-time telemetry as the primary lens (a single
snapshot can't show a trend); `inferred` from the postmortem that described the
symptom curve but not this compression trick.
*Pitfalls & cost:* compression changes concurrency timing, so a race you *were*
chasing may hide — confirm the resource story before ruling a race in.

**Case 21 — Offline `.dmp` / core dump, no matching symbols**
*Situation:* all you have is a crash dump (or a captured core) and the build
that produced it is gone; you never saw the process live.
*How you recognize it:* the artifact is a dead snapshot; symbols/source don't
line up, stack frames resolve to addresses.
*Handling path:* pin the artifact to its exact build (hash → CI record) before
debugging anything — a dump analysed against the wrong binary lies confidently.
Recover or relocate symbols, load the dump as read-only, walk the managed/native
transition carefully; when symbols can't be recovered, read the dump like a
`live-process` forensic artifact (case 07's offline half).
*Tools/techniques:* debugger `!analyze`/symbol-path, matching-core checks,
`attested@` vendor guide (steps) + `inferred@` talk (what to do when the build
record itself is missing).
*Pitfalls & cost:* the whole case is bounded by provenance — if you can't tie
the dump to a build, every conclusion is `inferred`, not `attested`, and the
catalog should say so.

*… 31 more cards …*

The two things to actually take from this list: the hard debugging cases cluster
around **compressing an axis you can't wait on in real time** (time, load, the
four-day state) and **treating a snapshot as the artifact** when the live
process is off-limits — those two moves reappear under six different names,
which is itself the finding, not six cases. And the thin offline-artifact family
is a real gap in the sources, not in the space: I'd expect ~6 cases there if
more crash-analysis writeups existed; the 2 shown are 2 attested and I refused
to pad the rest as derived.
