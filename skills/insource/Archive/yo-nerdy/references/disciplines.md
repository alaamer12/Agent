# Governing Disciplines

Every component this skill analyzes belongs to at least one established discipline that already has decades of vocabulary, metrics, and hard-won frameworks for exactly this kind of problem. Naming the discipline explicitly matters for two reasons: it tells you which canonical concepts and metrics you'd be embarrassed to have missed, and it tells you what to search for in Step 8 (production verification) — "how does BM25 handle short queries" finds real answers; "how does search handle short queries" mostly finds blog spam.

Identify the 1-2 disciplines that actually govern the component (most components are primarily one discipline with a secondary one at the edges — a search bar is primarily Information Retrieval but touches HCI at the UI layer) and use that discipline's own vocabulary and metrics throughout the analysis instead of reinventing generic-sounding equivalents. The list below is alphabetical — order carries no signal about which discipline is more common or more important; scan for the one that actually fits.

## Computer Vision / Perception
**Covers**: image/video annotation and labeling, object detection, segmentation, pose/keypoint estimation, any component that extracts structured information from visual input.
**Canonical metrics**: IoU (intersection-over-union — how well a predicted region overlaps the true one), mAP (mean average precision, the standard detection-quality summary), per-keypoint localization error.
**Canonical concepts**: the label-granularity spectrum itself (whole-image tag → bounding box → segmentation mask → per-keypoint landmarks — this is the formal version of the "few labels vs. many labels" question), occlusion handling, anchor boxes, inter-annotator agreement as a formal reliability metric.
**A pivotal, discipline-native preference axis**: annotation granularity — a single coarse label per item vs. fine-grained keypoints/segments (e.g., a shoe labeled just "footwear" vs. labeled at heel/toe-tip/laces/sole level). See `dimension-checklist.md` #15 and the Classification/Labeling pattern in `domain-patterns.md` — this axis multiplies annotation cost and inter-rater disagreement risk as it gets finer, so it needs to be settled with whoever consumes the labels, not assumed.

## Control Theory
**Covers**: any component that continuously adjusts its own behavior based on feedback — autoscalers, rate limiters that adapt, robotics, thermostats, PID-style throughput controllers.
**Canonical concepts**: feedback loops, stability (does the system settle or oscillate/diverge), a PID controller's three terms (proportional — react to current error; integral — react to accumulated past error; derivative — react to the rate of change), overshoot and damping.

## Database Systems
**Covers**: anything about how data is stored, queried, and kept consistent.
**Canonical concepts**: ACID properties (atomicity, consistency, isolation, durability), normalization vs. denormalization, indexing strategies, isolation levels (read committed, repeatable read, serializable) and the anomalies each one prevents or allows.

## Distributed Systems
**Covers**: anything spanning multiple machines/services — messaging pipelines, replicated caches, multi-region deployments, consensus-dependent state.
**Canonical concepts**: the CAP theorem (consistency/availability/partition-tolerance — pick two), consensus algorithms (Raft, Paxos) for agreeing on a single value across nodes, replication (leader-follower vs. leaderless/quorum-based), eventual vs. strong consistency, vector clocks / logical clocks for ordering events without a global clock.
**A pivotal preference axis**: strong consistency (every read sees the latest write, at the cost of availability/latency during partitions) vs. eventual consistency (always available and fast, but reads can be briefly stale).

## Human-Computer Interaction (HCI) / UX
**Covers**: anything where a human directly perceives and reacts to the component's behavior — how results are presented, how errors are communicated, timing that affects perceived responsiveness.
**Canonical concepts**: Nielsen's usability heuristics (visibility of system status, error prevention, recognition over recall), Fitts's law (time to reach a target depends on distance and size — relevant to any UI timing/placement decision), the perceived-performance principle that showing partial results fast often beats a complete result that's slow.

## Information Retrieval (IR)
**Covers**: search, matching, autocomplete, query understanding, ranking of any kind.
**Canonical metrics**: precision (of what's returned, how much is relevant), recall (of what's relevant, how much was found), F1 (their harmonic mean), nDCG (normalized discounted cumulative gain — rewards relevant results appearing higher, not just present), mean reciprocal rank.
**Canonical concepts**: the precision/recall tradeoff itself (this is the formal name for "exact vs. fuzzy" and "strict vs. permissive" matching tensions), the vector space model, query expansion, relevance feedback (implicit — clicks; explicit — thumbs up/down), stemming/lemmatization, inverted indexes, TF-IDF/BM25 (see cs-toolkit.md).
**A pivotal, discipline-native preference axis**: precision-oriented (fewer results, all highly relevant — favors expert/power users who know what they want) vs. recall-oriented (more results, willing to include marginal matches — favors casual users who might not phrase things precisely). This is IR's version of "should this feel more like a strict database query or more like Google reading your mind."

## Machine Learning / Recommender Systems
**Covers**: any component whose behavior is learned from data rather than fully hand-specified — ranking models, personalization, classification/filtering.
**Canonical concepts**: the bias-variance tradeoff, overfitting to training data vs. generalizing, cold-start problem (new user/item with no history), exploration vs. exploitation (try something new and possibly worse to learn more, vs. always serving the currently-best-known option), feedback loops that reinforce early exposure (a formal ML concern, not just a general worry).
**A pivotal preference axis**: this is exactly where "should ranking reflect what's generically popular/trending, or what this specific user's history suggests, or the literal query relevance" lives formally — it's the explore/exploit and personalization-vs-generalization tension named above, not a vague taste question.

## Networking
**Covers**: anything about how data moves between systems over an unreliable network — protocols, retries, timeouts.
**Canonical concepts**: at-least-once/at-most-once/exactly-once delivery semantics, exponential backoff with jitter for retries, head-of-line blocking.

## Operations Research / Queueing Theory
**Covers**: scheduling, load balancing, capacity planning, anything about resources being allocated among competing demands over time.
**Canonical concepts**: queueing models (arrival rate vs. service rate, Little's Law relating queue length, wait time, and throughput), scheduling policies (FIFO, priority, shortest-job-first) and their fairness/starvation tradeoffs.

## Security & Cryptography
**Covers**: authentication, authorization, anything handling credentials or sensitive data, anything with an adversarial user in the threat model.
**Canonical concepts**: the CIA triad (confidentiality, integrity, availability), threat modeling frameworks (STRIDE: spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege), principle of least privilege, defense in depth (also a general axiom, but originates here), zero trust.
**A pivotal preference axis**: convenience vs. friction — every security control traded against user experience; naming exactly where on that spectrum a decision sits (e.g., "session lasts 30 days with no re-auth" vs. "re-auth every login") is more useful than calling it "secure."

## Notes on using this file
A component can straddle two disciplines cleanly — e.g., a recommendation feed is Machine Learning for the ranking model and Information Retrieval for how it handles a text query on top of it. Say so, and use each discipline's vocabulary for the part it actually governs, rather than picking one and forcing the whole analysis through it. If a component's discipline isn't listed here (robotics kinematics, compiler design, audio signal processing, and plenty of others aren't), that's a gap in this file's coverage, not a signal that the skill doesn't apply — name the real discipline anyway and use its actual vocabulary.
