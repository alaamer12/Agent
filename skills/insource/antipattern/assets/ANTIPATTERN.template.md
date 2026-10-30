# ANTIPATTERN

<One paragraph: what this document is, which project it covers, and where the supporting investigation report lives.>

## How to use

Before changing code, check the rules whose "Applies when" matches your change. If you must make an exception, state which rule and why in the change description.

Rules need the fields below. Add `Example` only where the rule is easy to state but easy to misapply: a small
before/after pair, fenced as a diff or two short snippets, labelled **illustrative** when it is not the project's
own code, and free of angle-bracket placeholders — a finished spec is validated by `scripts/check_spec.py`.

## <Theme, e.g. Superficial compliance>

### AP-001: <Short anti-pattern name>
- **Avoid:** <The specific behavior to stop.>
- **Instead:** <The behavior to follow.>
- **Applies when:** <Scope: paths, layers, situations.>
- **Why it matters:** <The consequence in this project, with a pointer to evidence.>
- **Exceptions:** <Valid exceptions and trade-offs, or "None".>
- **Compliance check:** <A grep pattern, linter rule, review question, or test.>
- **Example:** <Optional before/after pair. Delete this line when the rule needs no example.>
- **Level:** <Required | Recommended>
