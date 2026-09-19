# Cross-Domain Algorithm & Technique Toolkit

The dimension checklist and domain patterns tell you *which questions* to ask. This file is about answering them like an engineer, not a blogger — naming the actual algorithm, data structure, or formula, with its complexity and known failure mode, instead of describing it in vague prose ("some kind of fuzzy matching" is not a recommendation; "Levenshtein distance ≤ 2, computed via a BK-tree" is).

**This toolkit is deliberately balanced across problem categories, not organized around any one domain.** It would be easy for a file like this to drift toward whichever domain the author thought about most (matching and ranking algorithms are the classic example — they're vivid and well-documented, so they crowd out everything else). Don't let the order below imply priority: a payment component will lean almost entirely on Sections 5-6 and barely touch 1-2; a robotics component will live in Section 8 and never touch 1-2 at all. Scan the section titles first and pick whichever ones actually describe the component's real behavior, the same way you wouldn't reach for a matching algorithm to specify a thermostat.

**On the `[bracketed]` alternatives below**: where a bullet lists several named techniques against each other (e.g. `[LRU]` vs `[LFU]` vs `[TTL]`), that's the same illustrative-options convention used in `domain-patterns.md` and `engineering-axioms.md` — a menu to choose from or deviate from, not a mandatory set. Where a bullet names a single technique with no alternatives listed, that's because it's close to a default (an exact-match hash lookup, an idempotency key) rather than because no other approach could ever apply.

## 1. Similarity, comparison & approximate matching

The abstract problem: deciding whether two things are "close enough" to count as the same, and how close is close enough. This shows up in search typo-tolerance, but equally in deduplicating customer records, detecting plagiarism, aligning DNA sequences, and flagging near-duplicate fraud transactions — the same handful of techniques serve all of them.

- **Exact match**: hash-based lookup, O(1) average. The default unless there's a stated reason for tolerance.
- **Edit-distance**: Levenshtein (substitutions/insertions/deletions) or Damerau-Levenshtein (also transpositions). Naively O(n·m) per pair; a **BK-tree** or **SymSpell**-style precomputed index avoids comparing against every candidate. The same family of algorithm (generalized as sequence alignment — Needleman-Wunsch, Smith-Waterman) is the standard tool in bioinformatics for aligning DNA/protein sequences, and in plagiarism detection for aligning passages.
- **Set/vector similarity**: Jaccard similarity (token sets) or cosine similarity (vectors/embeddings) — used for document similarity, but equally for image-feature comparison, recommendation similarity, and flagging structurally similar fraudulent transactions.
- **Locality-sensitive hashing (LSH)**: approximate nearest-neighbor at scale without comparing every pair — used for near-duplicate detection across large document or image sets, not just search embeddings.
- **Prefix structures**: a **trie** gives O(k) lookup for a k-length prefix — the standard structure behind autocomplete, but also IP routing tables (longest-prefix match) and predictive text input.
- **Inverted index**: token → list of containing items — the standard structure behind full-text search, but equally behind log search and tag-based filtering systems.

## 2. Scoring, ranking & prioritization

The abstract problem: given many candidates, producing an order, not just a yes/no. Search relevance is one instance; so is loan-risk scoring, support-ticket triage, ride-hailing driver-rider matching, and operating-system process scheduling.

- **Weighted signal combination**: a simple weighted sum of factors (relevance, recency, risk, priority) is the most explainable starting point for any scoring problem, in any domain.
- **TF-IDF / BM25**: weighting a signal by how *distinctive* it is, not just how present it is — the classical text-relevance formulas, but the same "distinctiveness weighting" idea generalizes to anomaly/fraud-signal scoring (a rare combination of features is more suspicious than a common one).
- **Priority queues / heaps**: the underlying data structure for any prioritization problem — Dijkstra's shortest-path algorithm, OS process scheduling, hospital triage, event-driven simulation, print-job queues.
- **Learned ranking**: a model trained on outcome data (clicks, approvals, resolutions) rather than a hand-tuned formula — the natural next step once there's enough labeled data, in ranking, credit scoring, or ticket triage alike. Needs explicit monitoring for feedback-loop bias (see Section 8's control-loop framing, or "Feedback loops" in `engineering-axioms.md`).
- **Exploration vs. exploitation (multi-armed bandits)**: occasionally trying a lower-scored option to keep learning true performance, rather than always serving the current best guess — used in recommendation, but equally in dynamic pricing, ad allocation, and adaptive A/B testing.

## 3. Consensus, coordination & distributed agreement

The abstract problem: getting multiple independent nodes to agree on one fact, or to hand off responsibility cleanly, when any of them might be slow or unreachable. Nothing here is search-specific — this is the backbone of any multi-node system.

- **Consensus algorithms (Raft, Paxos)**: how a cluster agrees on a single value (a leader, a log entry) despite failures — used by distributed databases and coordination services (etcd, ZooKeeper) for leader election and distributed locks.
- **Consistent hashing**: distributing keys across nodes so that adding/removing a node remaps only a small fraction of keys — used for cache sharding, but equally for CDN request routing and peer-to-peer distributed hash tables.
- **Two-phase commit / sagas**: coordinating a transaction that spans multiple services (e.g., reserve inventory, charge payment, schedule shipping) where a partial failure needs an explicit compensating rollback rather than an implicit one.
- **Vector clocks / CRDTs**: tracking causality or merging concurrent edits without a central arbiter — the basis of real-time collaborative editing and multi-region eventually-consistent stores.

## 4. Caching & memory management

The abstract problem: trading memory/staleness for speed, and knowing exactly when that trade goes wrong.

- **Eviction policy**: `[LRU, recency-based]` vs `[LFU, suits stable long-tail access patterns]` vs `[TTL-based expiry, suits data with a known staleness tolerance rather than a size bound]`.
- **Cache stampede prevention**: request coalescing (one request per key actually hits the backend, others wait on it) or probabilistic early expiration.
- **Predictive/speculative prefetching**: worth it only when predicted-accuracy × savings exceeds wasted-work cost — state this as an explicit cost-benefit, not an assumed win, whatever the domain (prefetching a next search page, preloading a video's next segment, warming a route cache before a predicted traffic spike).

## 5. Concurrency & correctness

The abstract problem: multiple things happening at once touching the same state, and what happens when their timing overlaps in an unlucky way. This is as central to a booking system or an inventory system as to any other kind of component.

- **Idempotency keys**: the standard fix for "don't double-charge/double-submit/double-book on retry" — the client sends a unique key, the server ignores a repeat with the same key.
- **Optimistic vs. pessimistic locking**: `[optimistic — check a version number at write time, reject on conflict, scales better under low contention]` vs `[pessimistic — lock before reading, simpler to reason about under high contention]`.
- **Naming the actual race**: "two requests both read '5 seats left' before either decrements" is a real, specific race condition; "handle concurrency" is a placeholder, not an answer, whatever the component is.

## 6. Security & reliability primitives

The abstract problem: resisting an adversarial or merely careless actor, and staying up when a dependency doesn't. Relevant to any component that touches credentials, money, or shared resources — not a search-only concern.

- **Password/secret storage**: slow, salted hashing (bcrypt, scrypt, Argon2) — never a fast general-purpose hash (SHA-256 alone), which is designed to be fast and is therefore weak against offline brute-force.
- **Integrity vs. confidentiality vs. authenticity**: an HMAC proves a message wasn't tampered with and came from someone holding the shared key; a digital signature proves authorship without a shared secret; encryption hides content but proves neither on its own — naming which property a given check actually provides avoids a common false sense of security.
- **Symmetric vs. asymmetric encryption**: `[symmetric — one shared key, fast, suits bulk data]` vs `[asymmetric — public/private key pair, suits key exchange and signatures where two parties haven't already shared a secret]`.
- **Rate limiting**: `[token bucket — allows bursts up to a cap while enforcing a steady average, usually the right default]` vs `[fixed window — simple, but allows a 2x burst at the window boundary]` vs `[sliding window — avoids that at some memory cost]`. Applies to API abuse resistance, login-attempt throttling, and infrastructure protection alike.

## 7. Optimization & scheduling

The abstract problem: allocating a limited resource (time, capacity, budget) among competing demands, in any domain from logistics to meeting rooms to compute clusters.

- **Greedy vs. dynamic programming vs. linear/integer programming**: `[greedy — fast but can miss the true optimum]` vs `[dynamic programming — finds the optimum when the problem has overlapping subproblems, e.g. resource allocation with a budget constraint]` vs `[linear/integer programming — handles complex multi-constraint optimization, e.g. delivery routing or staff scheduling, at the cost of solver complexity]`.
- **Queueing theory (Little's Law: average items in a queue = arrival rate × average time in the system)**: applies identically to call-center staffing, web-server capacity planning, and hospital emergency-room wait times — whenever there's an arrival process and a service process.
- **Scheduling policies**: `[FIFO]` vs `[priority-based]` vs `[shortest-job-first]` — each trades throughput against fairness and starvation risk differently; the same tradeoff shows up in CPU process scheduling, job queues, and customer-service ticket assignment.

## 8. Control & adaptive feedback systems

The abstract problem: a system that continuously measures its own output and adjusts itself — nothing to do with search at all, but central to autoscaling, robotics, and any adaptive-rate mechanism.

- **PID control** (proportional, integral, derivative terms reacting to current error, accumulated past error, and rate of change respectively): the standard model behind thermostats, cruise control, infrastructure autoscaling, and adaptive video-bitrate streaming.
- **Exponential backoff (with jitter)**: the standard retry strategy when a dependency is failing or a network is congested — increasing delay between retries to avoid pile-on, with randomized jitter so many clients don't retry in lockstep.
- **Exponential moving averages**: smoothing a noisy signal (sensor readings, request latency, load) to make control decisions on a trend rather than reacting to every spike.

## 9. Formal specification of core logic

Once the plain-language decisions are made, express genuinely tangled decision logic in a more rigorous form — this applies to a matching fallback chain exactly as much as to an order-status lifecycle, an elevator dispatch algorithm, or a traffic-light control sequence:

- **Decision table**: rows are conditions, columns are rules, cells show which combinations trigger which action — good for "if these several boolean-ish conditions combine, do X."
- **Finite state machine**: states + transitions + triggering events — good for anything with a lifecycle (session states, order states, an elevator's states, a traffic light's phases).
- **Pseudocode**: plain imperative steps with IF/ELSE and loops — good for a control-flow-heavy algorithm when prose would tangle in nested conditionals.

Include one of these alongside prose, not instead of it, once more than 2-3 conditions interact — that's usually where natural language stops being unambiguous, regardless of domain.

## 10. Testing & edge-case discovery techniques

When double-checking that a "failure modes & edge cases" section is actually exhaustive, borrow from software testing theory rather than relying on brainstorming alone — these apply to any numeric or categorical boundary, whether it's a fuzzy-match distance, a rate limit, a payment amount, or a temperature threshold in an HVAC controller:

- **Boundary value analysis**: for any numeric or length-based threshold, explicitly check behavior at the boundary, one below it, and one above it.
- **Equivalence partitioning**: group possible inputs into classes that should behave identically, and make sure every class — not just the common ones — has a stated behavior.
