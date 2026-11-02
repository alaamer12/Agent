# Finding: worked example

Project: a Python order service. Shows a well-formed finding, a pointer to the rule derived from it, and a weak finding with annotations.

## Good finding

**F-03: Duplicated discount rule with divergent thresholds**

- **Description:** The bulk-discount rule is implemented twice and the copies disagree.
- **Affected:** `app/pricing.py::apply_discount`, `app/billing.py::compute_total_with_discount`
- **Evidence:**
  - Measured: `pricing.py:12` applies 10% at quantity >= 10. `billing.py:31` applies 10% at quantity > 10. Both are called on the checkout path (`order_service.py:54`, `:61`).
  - Interpreted: An order of exactly 10 units is priced differently depending on the code path.
- **Why it matters here:** Invoices and displayed totals can differ for the same cart, which creates customer-visible billing disputes.
- **Consequences:** Incorrect charges, reconciliation work, rule changes applied in only one place.
- **Impact:** High. A wrong total is charged to a real customer and reconciled by hand; the checkout path is the
  service's main job.
- **Confidence:** High. Both call sites verified by reading the checkout path. Would drop to Medium if one function is shown to be dead code (no caller found in tests or scripts either).

## Rule derived from it

See AP-003 in [ANTIPATTERN.example.md](ANTIPATTERN.example.md). It turns this finding into an imperative, checkable rule and drops the evidence, which stays in the report.

## Weak finding (do not write like this)

> **Overengineering in services layer.** The code is too complex and probably written by AI. Should be simplified.

What is wrong:
- No location, so it cannot be verified or acted on.
- No measurement, and "probably written by AI" is speculation about authorship rather than a defect.
- No consequence in this project and no confidence statement.
- The implied rule ("simplify") is not checkable.

## Same defect, correct framing

> **Single-implementation factory.** `app/services/factory.py::OrderProcessorFactory` builds `DefaultOrderProcessor` and is the only implementation of `OrderProcessor` (grep: 1 subclass, 1 call site). Measured: 58 lines, 2 abstract classes. Interpreted: indirection without a second consumer. Confidence: Medium. A planned second processor in the roadmap would justify it.
