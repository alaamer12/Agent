# Inquiry questions: examples

Use as calibration for tone and shape. Adapt the wording to what `/inquire` supports. All options come from investigation evidence.

## Q1. Which of these should become project rules? (select all that apply)

Code-level
- [ ] Silenced type errors: 14 `# type: ignore` and 6 `cast(Any, ...)`, 9 of them in `order_service.py`
- [ ] Swallowed exceptions: 5 `except Exception: pass` blocks, 3 in the payment client
- [ ] Single-implementation factory (`OrderProcessorFactory`)

Business-level
- [ ] Discount rule duplicated in two modules with different thresholds
- [ ] Money stored as `float` in `models.Order.total`

Resource-level
- [ ] Hand-written `parse_date` although `python-dateutil` is already a dependency

- [ ] None of these / other (describe)

## Q2. For the ones you selected, which are mandatory?

Required (agents must never do this) / Recommended (prefer to avoid, exceptions allowed). One choice per selected item.

## Q3. Which architectural concerns should the document cover? (select all that apply)

- [ ] `domain/` importing `infrastructure/` (3 imports found)
- [ ] Circular dependency between `billing` and `orders`
- [ ] Outbound calls without timeouts or retries (4 clients)
- [ ] None of these

## Q4. Do any of these constraints change the recommendations? (select all that apply, add detail below)

- [ ] `legacy/` is frozen and should be excluded
- [ ] A migration to Decimal money types is already planned
- [ ] Some suppressions are required by an unfixed upstream typing bug
- [ ] Other: ______

## Not worth asking

- Whether `any` casts are bad when the TypeScript config already sets `noExplicitAny` to error.
- Whether to document the monolith structure when an ADR records it as intentional.
