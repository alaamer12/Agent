# Decision Checklist (Use during the pause)

Copy or mentally run through this every time the skill activates.

## 1. Problem Statement
- [ ] I can state the exact capability in 1–2 clear sentences.

## 2. Existing Solution Scan
- [ ] I checked for mature, production-proven options (libraries, frameworks, platform features, established patterns, infrastructure tools).
- [ ] I noted the strongest candidate(s), if any.

## 3. Trade-off Evaluation (Existing Solution)
- [ ] Dependency / size / license cost is understood.
- [ ] Maintenance and security posture of the candidate is acceptable.
- [ ] Fit with the current project stack and constraints is evaluated.
- [ ] Learning curve and operational complexity are considered.

## 4. Trade-off Evaluation (Custom Build)
- [ ] Time and complexity of a correct custom implementation are realistic.
- [ ] Ongoing maintenance burden is acknowledged.
- [ ] Risk of missing solved edge cases is considered.
- [ ] “Because I can” is not used as justification.

## 5. Fair Judgment & Decision
- [ ] I judged the options fairly — no bias toward custom code, no bias toward any particular library or trend.
- [ ] One of the three outcomes is chosen and written:
  - Use existing solution (named + justified)
  - Build custom (justified by real advantage)
  - Hybrid (proven core + thin custom layer)
- [ ] The decision is grounded in the actual requirements of *this* project, not abstract preference or personal habit.

## 6. Ask When Unsure
- [ ] If the choice involves a new dependency, tool, or significant architectural direction and I am not confident, I asked the user instead of deciding alone.

## 7. Proceed
- [ ] Only after the above is complete (and any needed user confirmation is obtained) do I start writing implementation code.
---
