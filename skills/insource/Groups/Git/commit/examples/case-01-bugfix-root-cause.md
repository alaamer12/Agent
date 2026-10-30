# Case 1 - a bug fix, told by its cause

**Situation:** customers were charged twice when a payment processor returned a 503. The retry loop kept
re-sending, and delivery ids were regenerated per attempt so upstream dedup could not help.

## The message a hurried pass produces

```text
fix: payment bug
```

Nothing here survives contact with `git blame` in six months. A reader learns that something was wrong, that
this commit is somehow related, and nothing else - and the person bisecting a payment incident cannot tell
whether this commit is the cause or the cure.

## What got staged

```bash
git status --short
 M src/payments/webhook_retry.ts
 M src/payments/delivery_id.ts
?? scratch/replay-503.ts          # left uncommitted - a probe, not part of the fix
?? .env.local                     # never staged
git add src/payments/webhook_retry.ts src/payments/delivery_id.ts \
        test/payments/retry_503.spec.ts
git diff --cached --stat          # three files: the fix and its regression test, nothing else
```

Note the test file appears in staging but not in `status --short` above because it was added earlier in the
session; the point is the check, not the assumption.

## The message that got written

```text
fix(orders): stop double-charging retried payment webhooks

The retry loop re-sent payloads on every 5xx, including 501/503 which the
processor treats as permanent failures. Those retries kept the queue hot and,
because delivery ids were regenerated per attempt, the processor could not
deduplicate - so a customer could be charged twice.

Retries are now limited to 429, 502 and 504 with Retry-After honored, and the
delivery id is derived from the order id, so a duplicate attempt deduplicates
upstream. Adds a regression test replaying a recorded 503 sequence.

Fixes #4821
Reported-by: Support <support@example.com>
```

## Why each line is there

| Element | Job it does later |
|---|---|
| `fix(orders):` | release tooling counts it as a patch; scope tells the reader which area |
| subject states the effect, not the file | readable in `git log --oneline` across a 40-commit branch |
| body paragraph 1 - the cause | the next reader can judge whether the fix actually addresses it |
| body paragraph 2 - what changed behaviorally | support can answer "which retries still happen?" without reading code |
| regression test named | reviewer knows the claim is covered, and where |
| `Fixes #4821` | links the ticket when it merges to the default branch |
| `Reported-by:` | credits who found it, which matters for the security and support processes |

## Verification run before reporting

```bash
git show --stat --no-patch HEAD
git log --oneline -3
```

The test suite was **not** re-run in this session (the project's instructions say not to run typecheck or
full builds by default), so that was reported as "regression test added; suite not run locally" instead of an
implied green.
