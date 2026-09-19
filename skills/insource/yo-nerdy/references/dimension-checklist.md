# Universal Dimension Checklist

These are the dimensions that apply to nearly any system component. For each one that's relevant to the component being analyzed, instantiate it into the component's own specific micro-questions — the generic prompt below is a starting point for your thinking, not something to paste into the output verbatim.

Not every dimension applies to every component. A rate limiter has little to say about "ranking"; a ranking algorithm has little to say about "triggering." Use judgment about which subset is relevant, but err toward covering a dimension briefly rather than skipping it silently — a one-line "not applicable here because..." is better than silence, since it shows the ground was actually considered.

## 1. Input handling & validation
What counts as valid input? What are the boundaries (min/max length, allowed characters, encoding)? What happens on empty input, null, whitespace-only, malformed, or oversized input? Is input trimmed/sanitized, and exactly how?

## 2. Parsing & normalization
How is raw input broken down before processing (tokenization, case folding, accent/diacritic stripping, punctuation handling, whitespace collapsing)? What order do normalization steps happen in — does order matter? Are numbers, dates, or units normalized to a canonical form?

## 3. Timing & triggering
What specific event causes each behavior to fire? Is there a threshold (characters typed, time elapsed, items accumulated) before something kicks in? Is there debouncing or throttling, and what's the delay? What happens if the triggering event repeats rapidly (e.g., user keeps typing) — is prior work cancelled, queued, or ignored?

## 4. Matching / core decision logic
What's the primary strategy (exact match, fuzzy match, rule-based, learned model)? If there's a fallback chain, what's the precedence order and what triggers falling back to the next strategy? What are the exact thresholds involved (edit distance, similarity score, confidence level) and why that number rather than another?

## 5. Ordering & ranking
If output is ordered, what determines the order — relevance, recency, popularity/trending, personalization, business rules, a blended score? How are ties broken? Is the ranking the same for every user, or does it vary by user, and if it varies, on what basis?

## 6. Personalization vs. universality
Does behavior differ per user or per session? What happens for a brand-new user with no history (cold start)? Is personalization based on explicit preferences, implicit behavior, or both? Is there a way to opt out?

## 7. Internationalization & localization
What languages/scripts are supported? What happens with mixed-language input in a single request/action? What happens when input is in a language the underlying content/data doesn't exist in — is there a fallback language, translation, or an honest "not available"? Are matching/parsing rules (case folding, fuzzy thresholds, word segmentation) the same across all languages, or do they need to differ (e.g., languages without whitespace word boundaries, right-to-left scripts, transliteration between scripts, units/date formats/currency)?

## 8. Performance & caching
What, if anything, is cached or precomputed? What invalidates the cache? Is there predictive/speculative work (e.g., prefetching a likely-next result) — and if a prediction is wrong, what's the cost, and is that cost worth the average-case speedup? What's the acceptable latency budget for this component, and does it change the earlier answers (e.g., a tighter budget might force cutting fuzzy matching)?

## 9. Failure modes & edge cases
What happens on zero results / empty output? On a tie between many equally-good options? On conflicting or contradictory input? On a downstream dependency failing or timing out? On concurrent/simultaneous requests that touch the same state?

## 10. State & memory
Does the component remember anything across a single session or across sessions (history, recent queries, prior choices)? How long is it remembered, and what resets it? Does remembered state change behavior transparently to the user, or invisibly?

## 11. Security & abuse resistance
Can this component be abused (scraping, injection, spoofed input, enumeration)? Is there rate limiting or anomaly detection specific to this component? Is any of the input/output sensitive enough to need special handling (PII, credentials)?

## 12. Configuration & tunability
Which of the thresholds and decisions above are hardcoded constants versus configurable knobs? Who is allowed to change them, and how (a config file, an admin panel, a feature flag, an A/B test)? Would you want these tunable in production, or is a fixed value fine?

## 13. Feedback loops & learning
Does usage of this component feed back into how it behaves later (learned ranking, adaptive thresholds, popularity-based boosting)? If so, what's the risk of the feedback loop reinforcing an early bias (e.g., an early popular result staying artificially popular because it's shown more)? Is there a mechanism to counteract that?

## 14. Observability
How would you know this component is behaving correctly in production versus silently misbehaving? What would you log or measure? What's the signal that a threshold picked in this analysis needs revisiting later?

## 15. Granularity & decomposition depth
How fine-grained should the component's categories, labels, rules, or decision set actually be? This is a distinct question from *what* the categories are — it's *how many* and *how precisely split*. A computer-vision annotation task can label a shoe with one box ("footwear") or with a dozen keypoints ("heel, toe-tip, laces, sole, ankle-collar..."); a permission system can have three coarse roles or hundreds of per-resource grants; a ranking algorithm can blend two signals or twenty. More granularity generally buys precision and flexibility at the cost of collection/labeling effort, consistency (more categories means more room for disagreement or drift between similar ones), and cognitive/maintenance load for whoever configures or reviews it. Is there a natural floor below which finer granularity stops adding real value? Is there a ceiling past which it adds noise or inter-rater disagreement rather than signal? This is usually a preference the user needs to state, not something inferable from the component alone — see Step 3 of the main skill.
