# Example: page-level review

This is an illustrative workflow, not a report about a real application.

## Request and routing

**Request:** “Review the account sign-up page for usability and visual slop.”  
**Scope:** one rendered page plus the related form component.

After identifying the page’s form/task and available source, consult the registry. Load only relevant records, for example:

- `repeated-container-text` if headings, labels, help, and submit copy appear duplicated;
- `low-contrast` if form text or controls look difficult to distinguish;
- `text-overflow` or `content-hidden-at-rest` only when rendered behavior shows clipping or content that fails to appear;
- `marketing-buzzword` only if the actual offer copy is vague or unsupported.

Do not load all 67 knowledge files or run unrelated detectors.

## Independent passes

- `impeccable-scout`: inspect the rendered page at desktop and a narrow viewport; assess whether hierarchy, instructions, status, and visual treatments fit the sign-up task. Record the screenshot/region and exceptions.
- `structural-scout`: scan only the form source for registry-selected source candidate detectors (for example, duplicate visible strings). Preserve file/line/snippet and candidate status. Browser-only overflow/contrast observations are not inferred from source.

Run both passes independently, then reconcile their stable pattern IDs.

## Illustrative synthesis

```text
repeated-container-text — candidate
Structural: “Create your account” occurs as a panel title, helper paragraph, and submit copy in SignupForm.tsx; source locations retained.
Visual/context: the heading states the task, while the helper text adds account requirements; the submit label identifies the action.
Resolution: do not delete the label or button. Candidate only; remove or rewrite only copy that adds no distinct instruction.

low-contrast — not observed
Visual: text and controls remain distinguishable at the reviewed states; no ratio was inferred from color names.

text-overflow — not observed
Visual: no clipping at the tested widths. The report is limited to those viewports.
```

The example keeps the structural string match as evidence without letting it silently overrule the contextual review.