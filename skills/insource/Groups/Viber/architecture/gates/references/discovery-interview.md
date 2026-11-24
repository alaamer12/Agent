# Gates Architecture — discovery interview

Ask only what the codebase cannot answer. Recon has already read the architecture docs, the CI
workflows, the hook config, the checks, the baselines, the suppression count, and the recent commits
where an agent touched a gate. What remains is intent and risk ownership.

## A. What must never ship

1. Which failures are **unacceptable** rather than merely expensive? A data loss, a leaked secret, a
   wrong price, an auth bypass, a broken checkout, a legally wrong locale. These are the first
   blocking gates.
2. Which incidents or near-misses happened in the last year? Each one is a gate candidate; the
   postmortem question is "which gate would have caught it?"
3. Which of those can be detected **before** the change reaches production, and which can only be
   caught at runtime? The answer separates static gates from runtime guards and sentinels.
4. Is there a regulatory, contractual, or legal constraint that makes a rule non-negotiable? Name
   the jurisdiction and the obligation; it changes the exception policy.

## B. Current enforcement

5. What already runs, at which boundary, and with what measured duration? Do not accept "we have
   CI"; ask for the required checks and the p95.
6. Which checks are **advisory today but should block**, and which block but should warn? The second
   list is usually longer and more urgent.
7. What is the current suppression count, and where does it live? A high count is evidence that a
   rule or a gate is wrong.
8. Is there a baseline? Is it shrinking, growing, or regenerated automatically? An auto-refreshed
   baseline is not a baseline.
9. Who bypasses the gate today, how, and why? `--no-verify`, an admin merge, a skipped job, a
   `continue-on-error`, an editable workflow. The bypass path is the real policy.
10. What is the slowest required check, and what does it cost in waiting time per day? That number
    decides the tier design.

## C. Risk, ownership, and exceptions

11. Who owns the **risk** for each domain — security, payments, personal data, public contracts,
    migrations? The exception approver is the risk owner, not the author.
12. What is the acceptable exception lifetime for each domain? Default to 90 days for design and
    architecture, 30 days for security unless a compensating control justifies longer.
13. What compensating controls exist when a rule cannot be met? Runtime guard, monitoring, manual
    review, feature flag, sandbox. An exception without one is a wish.
14. Is there an emergency path for production incidents? Who can authorize it, and how is it
    recorded? A caller-set variable is not authorization.
15. Which rules are **taste** rather than contract? Those become advisory with a rubric, not fake
    gates.

## D. Agents and the completion contract

16. Which agents or harnesses write code here (terminal agent, IDE agent, CI bot, multiple agents in
    parallel)? The answer changes the completion hook and the merge strategy.
17. Can the agent edit the CI config, the checks, the baselines, or the tests in its environment? If
    yes, what prevents self-certification?
18. What is the agent's one-command fast gate, and how long does it take? If there is no single
    command, the agent will improvise.
19. Does the harness support a completion hook (for example, a Stop hook that blocks the turn while
    the gate fails)? If not, where does the written contract live, and who reruns it?
20. What is the token/latency budget for the agent's feedback loop? A 400-finding report is a budget
    problem, not just a UX problem.
21. How do parallel agents merge? A merge queue, a final full run, or neither? Green branches do not
    compose.

## E. Rollout and governance

22. How many legacy violations does the first rule find? That number decides observe → warn →
    baseline → block, and the baseline shape.
23. Who reviews the register, and how often? Name the role and the cadence; a register with no
    review is a snapshot.
24. Which gates are candidates for deprecation this quarter? A gate that no longer maps to a rule is
    an orphan.
25. Is there an audit or retention requirement for gate reports and approvals? If yes, the report
    schema and the retention period are part of the design.

## Hand-off

Conclude by restating five things in one block and getting confirmation:

- the **blocking five** (plus the project-specific gates that protect its actual failure modes);
- the **tier table** (trigger, scope, p95 budget, blocking, owner);
- the **register sample** (rule, rung, tier, command, exception, owner, evidence);
- the **exception and bypass policy** (who approves, time box, compensating control, record);
- the **agent contract** (command, protected paths, completion evidence, full-scan rule).

The template's sections 3, 4, 6, 7, and 8 become exactly that block (tiers, register, suppressions
and exceptions, agent contract, failure and bypass policy). Anything unanswered goes to Open
Decisions, never defaulted silently.
