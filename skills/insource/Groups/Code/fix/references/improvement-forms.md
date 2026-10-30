# Forms of Improvement

The Fix skill does not prescribe a single technique. Choose the highest-leverage improvement that makes the next similar problem cheaper to diagnose or prevent.

## Possible forms

- **Precision of failure information**  
  Custom errors / exceptions that name the exact step, the responsible component, and the data that failed. Prefer when the original error was generic (“Database insertion failed”).

- **Observability**  
  Targeted logging, structured context, or better validation messages that surface the failure point without requiring re-investigation.

- **Structural clarity**  
  Clearer naming, extraction of a shared helper, or separation of concerns inside the affected block so the same class of defect is harder to re-introduce.

- **Making the bug impossible**  
  Moving a check to the source of truth, adding a type or invariant, or changing the data model so the invalid state cannot arise.

- **Consistency of values**  
  Extracting or consolidating duplicated hard-coded values when they represent the same concept (magic numbers are a common example that linters often flag).

- **Downstream artifacts**  
  Updating documentation, terms, privacy statements, configuration, or user-facing copy that would otherwise become false after the change.

## What is not required

- Adding a custom exception for every problem.
- Expanding scope into unrelated modules.
- Performing a broad cleanup that is not a direct consequence of the fix.

The improvement is successful when a future engineer (or the agent) can identify, understand, or prevent the same class of problem with less effort than was required this time.