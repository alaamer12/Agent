# Domain-Specific Patterns

Pre-built question sets for common component types. These supplement the generic checklist in `dimension-checklist.md` — they exist because certain component types have well-known, easy-to-overlook edge cases that a purely generic pass tends to miss. Use whichever pattern matches; skip the rest.

**How to read the bullets below**: each one names a micro-decision, followed by a few `[bracketed]` example options separated by "vs." The bracketed items are illustrative possibilities to jog thinking, not a mandatory menu and not a requirement that the real answer be one of them exactly as worded — the actual right answer for a specific component might be one of these, a hybrid of two, a variant not listed, or something the options don't anticipate at all. Don't treat "[option A] vs [option B]" as "the agent must force this component into A or B" — treat it as "here's the shape of the decision; go find the actual answer for this component." When you write the real analysis (in Steps 3-8 of the main skill), state the option actually chosen, the reasoning, and feel free to describe an answer that isn't any bracketed option at all.

Every pattern below gets roughly the same treatment: a one-line framing and 5-6 bullets, alphabetical order, no domain used as a "fuller" template than any other — none of these problem categories is more central to this skill than the rest.

## Authentication / session flows
Governs how identity is established and maintained across requests.
- **Credential comparison**: [constant-time comparison to avoid timing side-channels] vs [a simpler direct comparison] — the former matters once credentials are security-sensitive at all.
- **Lockout policy**: scoped [per-account] vs [per-IP] vs [both]; unlocks via [a timed cooldown] vs [admin action] vs [a secondary verification step].
- **Session duration & renewal**: [fixed expiry regardless of activity] vs [sliding expiry extended by activity] vs [indefinite until explicit logout]; invalidated early by [password change] vs [suspicious-activity detection] vs [manual logout elsewhere].
- **Concurrent sessions**: [unlimited across devices] vs [capped at N] vs [single-session-only, new login evicts the old one]; user-visible and revocable, or not.
- **Failure signaling**: [identical response for "wrong password" and "no such account"] vs [a distinguishing response] — the latter is more informative to the user but leaks account existence.
- **Step-up for sensitive actions**: [none — active session is enough] vs [fresh re-authentication required within the last few minutes] vs [full re-login required].

## Caching layers
Governs trading memory/staleness for speed.
- **Cache key scope**: [captures every input that affects the output] vs [a coarser key that risks two different requests sharing an entry].
- **Invalidation**: [pure TTL-based expiry] vs [explicit invalidation on write] vs [both, with a stated tie-break for the race between them].
- **Miss behavior**: [synchronous fetch-and-populate, caller waits] vs [serve-stale-while-revalidating in the background].
- **Stampede handling**: [no special handling — misses can pile onto the backend simultaneously] vs [request coalescing, one fetch serves all waiters] vs [probabilistic early expiration to spread refreshes out].
- **Eviction policy**: [LRU] vs [LFU] vs [pure TTL, no size-based eviction] — the right one depends on whether access is recency-driven, long-tail-stable, or has a known staleness tolerance.

## Classification, labeling & annotation systems
Governs assigning categories, labels, or structured markup to raw input — image/video annotation, content moderation tagging, document classification, medical coding, and similar.
- **Label granularity**: [a single coarse tag per item] vs [a bounding region] vs [a full segmentation mask] vs [fine-grained keypoints, e.g. heel/toe-tip/laces/sole on a shoe] (`dimension-checklist.md` #15 — this is a cost/precision tradeoff to settle with whoever consumes the labels, not something inferable from the task alone).
- **Taxonomy shape**: [flat label set] vs [hierarchical, coarse label with optional finer sub-labels beneath it].
- **Ambiguity & overlap**: [an explicit "uncertain/needs review" label] vs [a forced single choice even at a boundary case].
- **Inter-annotator consistency**: [averaging across annotators] vs [adjudication by a third reviewer] vs [discarding disagreements] when two annotations of the same item conflict.
- **Cost/precision tradeoff**: [the coarser, cheaper scheme is enough for the stated downstream use] vs [the finer scheme's extra precision is actually consumed by the downstream model/use case].

## Distributed messaging / event pipelines
Governs how independent services exchange events reliably.
- **Delivery semantics**: [at-least-once with idempotent consumers] vs [at-most-once, tolerating occasional loss] vs [true exactly-once, generally hard to achieve end-to-end].
- **Ordering guarantee**: [global order] vs [per-key order only, e.g. per-user] vs [no ordering guarantee at all].
- **Poison-message handling**: [infinite retry] vs [a dead-letter queue after N attempts] vs [drop and log].
- **Backpressure**: [unbounded buffering] vs [dropping excess] vs [slowing the producer down to match consumer capacity].
- **Consumer restart**: [resumes from a tracked offset/checkpoint] vs [replays from the beginning] vs [starts fresh, accepting gaps].

## File upload / storage
Governs accepting, storing, and serving user-supplied files.
- **Validation timing**: [validated before being durably stored] vs [stored first, validated asynchronously after] — the latter needs an explicit cleanup path for files that fail validation.
- **Deduplication**: [content-hash-based, identical uploads share storage] vs [every upload gets its own independent copy].
- **Resumability**: [restarts from zero on interruption] vs [resumes from the last confirmed chunk].
- **Retention**: [files expire/delete automatically after a period] vs [retained indefinitely until explicit deletion] — and what happens when another part of the system still references a file being deleted.
- **Access control enforcement point**: [checked at storage/write time] vs [checked only at serving/read time].

## Machine learning / recommendation pipelines
Governs components whose behavior is learned from data rather than fully hand-specified.
- **Feedback-loop risk**: [no correction — early exposure can self-reinforce via position/popularity bias] vs [an explicit exploration or de-biasing mechanism].
- **Cold start**: [a generic/popularity-based default for new users or items] vs [a content-based default using item/user features] vs [showing nothing distinctive until enough data accumulates].
- **Staleness tolerance**: [serving from a snapshot that's minutes old] vs [hours old] vs [days old] — how much does that matter for this specific use case?
- **Serving fallback**: [a simpler rule-based ranking] vs [cached previous results] vs [the feature going blank] if the model service is unavailable.
- **Drift monitoring**: [no explicit monitoring] vs [tracking a proxy metric that signals when retraining is needed].

## Notifications
Governs when and how a user is interrupted about an event.
- **Triggering & batching**: [one notification per event, no matter how frequent] vs [batched/debounced, e.g. 5 events in a minute become 1].
- **Priority model**: [all notifications interrupt the same way] vs [tiered — some are silent/badge-only, others alert immediately].
- **Repeat-trigger handling**: [a new notification each time the condition fires again] vs [suppressed until the user acts on the existing one].
- **Quiet hours**: [none — notifications fire any time] vs [a do-not-disturb window] vs [a window that still lets through anything flagged urgent].
- **Channel fallback**: [single channel only, no fallback] vs [falls back to another channel, e.g. email, if the primary goes undelivered after some period].

## Pagination / infinite scroll
Governs presenting a large result set in pieces.
- **Paging mechanism**: [offset-based, simple but breaks under concurrent inserts/deletes] vs [cursor-based, more robust to concurrent changes].
- **Data drift mid-scroll**: [a consistent snapshot taken at the first request] vs [live data, risking duplicate or skipped items as the underlying set changes].
- **End of results**: [a clear, communicated end] vs [degrades into an infinite/repeating feed] — and whether that's disclosed or deliberately hidden.
- **Page size**: [small pages, more round-trips, lower latency per request] vs [larger pages, fewer round-trips, higher latency per request].
- **Ordering stability**: [a fixed sort order across page loads] vs [a dynamic ranking that can reorder previously-seen items between loads].

## Payment / checkout flows
Governs the exchange of money for goods/services.
- **Charge timing**: [charged at order confirmation] vs [charged only after inventory is confirmed available] vs [charged, then reversed if a later step fails].
- **Duplicate-submission prevention**: [an idempotency key so a retried/double-clicked request can't double-charge] vs [no explicit protection, relying on the client not to retry].
- **Decline messaging**: [generic "payment failed" regardless of reason] vs [reason-specific messaging, e.g. insufficient funds vs. expired card vs. fraud flag].
- **Inventory/price hold**: [held for a fixed window during checkout] vs [not held at all, re-validated at the final confirm step].
- **Partial-failure rollback**: [automatic compensating refund/release if a later step fails after charging] vs [manual/ops intervention required].

## Ranking / recommendation
Governs producing an ordered list from many candidates.
- **Optimization target**: [engagement] vs [stated-intent relevance] vs [revenue] vs [result diversity] vs [some explicit blend of these].
- **Cold start**: [a popularity-based default for new items] vs [a content-based default using item features] vs [de-prioritized until enough signal accumulates].
- **Feedback-loop mitigation**: [none — popular items simply get shown more and stay popular] vs [an explicit mechanism, e.g. periodic exploration, to counteract that].
- **Explore/exploit mix**: [pure best-score-wins, no exploration] vs [a small deliberate share of lower-ranked items shown to keep learning true performance].
- **Tie-breaking**: [recency] vs [a secondary signal] vs [random] when scores are near-identical.

## Rate limiting
Governs bounding how often a caller can act.
- **Limit scope**: [per user] vs [per IP] vs [per API key] vs [a combination] — and how a legitimate shared-IP situation (office, NAT) is handled.
- **Algorithm**: [fixed window, simple but allows a burst at the window boundary] vs [sliding window, avoids that at some memory cost] vs [token bucket, allows controlled bursts while enforcing a steady average].
- **Limited-caller response**: [a hard error] vs [an artificial delay] vs [silent dropping] — and whether a retry-after signal is given.
- **Burst tolerance**: [strictly uniform rate, no bursts allowed] vs [bursts allowed up to a cap above the steady-state rate].
- **Abuse vs. legitimate-spike distinction**: [none — any caller hitting the limit is treated the same] vs [an anomaly-detection layer that distinguishes a genuine high-volume legitimate user from distributed abuse].

## Real-time collaboration / multiplayer state sync
Governs multiple clients editing shared state concurrently.
- **Conflict resolution**: [last-write-wins, simple but silently discards one edit] vs [operational transformation] vs [a CRDT, guarantees convergence without a central arbiter].
- **Partition behavior**: [optimistic — the client keeps editing during a network partition and reconciles later] vs [blocked — editing is disabled until reconnected].
- **Presence accuracy**: [a heartbeat/timeout mechanism that eventually detects silent disconnects] vs [presence only updates on clean disconnect events, risking stale "still here" state].
- **Ordering guarantee**: [a defined order concurrent edits are applied in] vs [no ordering guarantee, only eventual convergence].
- **Reconciliation UX**: [the user sees what changed when a conflict resolves] vs [it happens invisibly].

## Search / query matching / autocomplete
Governs finding and ordering matches for a user-supplied query.
- **Matching strategy**: [exact match only] vs [fuzzy match with a fixed edit-distance tolerance] vs [fuzzy match with a tolerance that scales with word length].
- **Triggering timing**: [fires on every keystroke] vs [fires after a debounce delay] vs [fires on a specific trigger, e.g. a trailing space or N characters of a new word].
- **Multi-word handling**: [all words required] vs [any word may be dropped for a partial match]; word order treated as [significant, e.g. "computer vision" ranks above a reordered match] vs [insignificant, reordered matches rank equally].
- **Ranking blend**: [pure textual relevance] vs [relevance blended with personalization] vs [relevance blended with popularity/trending] — and whether a brand-new user with no history gets a different blend.
- **Language handling**: [single-language only] vs [multi-language with automatic query-language detection] vs [multi-language with no detection, tried against all indexed languages]; a query in a language with no matching content gets [translation/transliteration attempted] vs [an honest "no results"].
- **Zero-result behavior**: [an honest empty state] vs [a "did you mean" suggestion] vs [related/popular items shown instead].
