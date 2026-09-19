# Example Judgments

These show the difference between the stressed impulse and the calm engineering decision.

---

## Example 1 — Retry / Backoff Logic

**Stressed impulse**  
“I’ll just write a small retry helper with exponential backoff myself. It’s only 30 lines.”

**Take-a-breath decision**  
Mature, battle-tested retry libraries already exist in almost every ecosystem and correctly handle jitter, cancellation, budget, and observability.  
In this project the cost of a well-maintained dependency is lower than the risk of subtle bugs in a hand-rolled version.  
→ **Use existing solution**.

---

## Example 2 — Simple Internal Utility

**Stressed impulse**  
“There’s a library for this, but I don’t want another dependency for something so small.”

**Take-a-breath decision**  
The required behavior is 8 lines of pure logic with no edge cases that libraries solve better. Adding a dependency would increase surface area for no meaningful gain.  
→ **Build custom** (and keep it tiny and well-tested).

---

## Example 3 — Authentication

**Stressed impulse**  
“I can implement JWT + refresh tokens + session store myself. I’ve done it before.”

**Take-a-breath decision**  
Authentication is a high-stakes domain full of subtle security and correctness traps. Production-proven libraries and platform features exist and are actively maintained by people who specialize in this. Reinventing it here would be high risk for little benefit.  
→ **Use existing solution** (or platform feature).

---

## Example 4 — Domain-Specific Mapping Layer

**Stressed impulse**  
“There’s an ORM / mapper library, so I should use it.”

**Take-a-breath decision**  
The mapping is highly specific to our internal domain model and the library would force awkward workarounds and extra abstraction. A thin, focused custom mapper is clearer and cheaper to maintain.  
→ **Build custom** (or Hybrid: use the library only for the generic persistence parts).

---

## Example 5 — Rate Limiting

**Stressed impulse**  
“I’ll implement a token-bucket rate limiter in Redis myself.”

**Take-a-breath decision**  
Reliable distributed rate-limiting is a solved problem with mature libraries and infrastructure tools. The cost of getting the edge cases (clock skew, atomicity, fairness) wrong is higher than the cost of adopting a proven solution.  
→ **Use existing solution**.

---

## Pattern to Notice

The stressed engineer optimizes for “I can build it.”  
The calm engineer optimizes for “What is the most appropriate engineering solution for this project right now?”
---
