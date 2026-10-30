# ANTIPATTERN

Anti-patterns agents and contributors must avoid in this project. Each rule says what to avoid, what to do instead, and how to check compliance. Evidence and background are in the investigation report.

## How to use

Before changing code, check the rules whose "Applies when" matches your change. If you must make an exception, state which rule and why in the change description.

## Superficial compliance

### AP-001: Silencing the type checker
- **Avoid:** Adding `# type: ignore`, `cast(Any, ...)`, or widening a type to `Any` to make `mypy` pass.
- **Instead:** Fix the type or the contract. If an upstream typing gap forces an ignore, scope it to one line with the error code and a comment linking the upstream issue.
- **Applies when:** Any Python change that touches typed modules under `app/`.
- **Why it matters:** `order_service.py` already holds 9 suppressions that hide a real mismatch between `OrderDTO` and `Order`, so the checker no longer protects the checkout path.
- **Exceptions:** Third-party libraries without stubs, with a linked issue and a narrow error code.
- **Compliance check:** `rg -n "type: ignore(?!\[)" app/` finds no bare ignores; `rg -n "cast\(Any" app/` finds none.
- **Level:** Required

### AP-002: Catch-and-ignore
- **Avoid:** `except Exception: pass` (or logging and continuing) around operations whose failure changes results.
- **Instead:** Catch the narrowest exception, handle or convert it to the project's `IntegrationError`, and let unexpected errors propagate.
- **Applies when:** Payment, inventory, and any outbound client code.
- **Why it matters:** Failed payment calls currently look like successes to the order flow.
- **Exceptions:** Best-effort telemetry, with a comment saying so.
- **Compliance check:** `rg -nU "except Exception:\s*\n\s*pass" app/` returns nothing outside `app/telemetry/`.
- **Level:** Required

## Business rules

### AP-003: Duplicated business rules
- **Avoid:** Re-implementing pricing or discount rules outside `app/pricing.py`.
- **Instead:** Call the function in `app/pricing.py`; change thresholds there only.
- **Applies when:** Any code computing totals, discounts, taxes, or fees.
- **Why it matters:** Two copies already disagree at the quantity boundary, producing different totals for the same cart.
- **Exceptions:** Display-only formatting of an already computed amount.
- **Compliance check:** `rg -n "quantity\s*(>=|>)\s*\d+" app/` matches only `app/pricing.py`.
- **Example:** Before/after, from the checkout path.

  ```diff
  # app/billing.py
  -    if quantity > 10:
  -        total *= 0.90
  +    total = apply_discount(total, quantity)   # the single rule, in app/pricing.py
  ```
- **Level:** Required

## Resources

### AP-004: Re-creating existing library functionality
- **Avoid:** Writing date parsing, retry, or validation helpers when a dependency already provides them.
- **Instead:** Use `python-dateutil` for parsing and the shared `retry` decorator in `app/utils/retry.py`.
- **Applies when:** Adding a helper under `app/utils/` or an inline equivalent.
- **Why it matters:** The hand-written `parse_date` handles three formats while the dependency handles the formats production data already contains.
- **Exceptions:** The dependency is demonstrably unsuitable (licence, security, missing feature); record the reason in the PR.
- **Compliance check:** Review question: "Does a dependency in `requirements.txt` already do this?" and `rg -n "def parse_date" app/` finds nothing.
- **Level:** Recommended
