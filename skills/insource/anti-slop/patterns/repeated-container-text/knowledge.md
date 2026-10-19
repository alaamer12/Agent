# Same text repeated inside one container

**ID:** `repeated-container-text`  
**Catalog section:** Copy  
**Official modality:** Source

## Definition and empirical evidence

This pattern concerns the same or near-identical wording appearing more than once inside one container. Repetition can help users find information, but wording that adds no context/action/reassurance may add clutter and interaction/cognitive cost. Repetition alone is not automatically a defect.

## Underlying principle and potential harm

Every visible text element should contribute to the task. Redundancy can slow scanning or obscure what actually differs; however, duplicate-sounding copy may serve distinct roles at different points in a task.

## Recognition signals

- A heading, label, helper text, button, status, or error message repeats the same information in the same context.
- Repeated wording adds no new action, instruction, or reassurance.
- Removing one instance does not make the task harder or the information less available.
- Multiple visible copy elements or duplicated strings in source are clues; inspect associated labels/descriptions and component boundaries.

## Causes to investigate

Possible causes include child components repeating parent copy; headings restating labels/buttons; instructions copied into helper/error states; or repeated wording compensating for unclear hierarchy.

## Exceptions and false positives

- Form controls need clear labels/instructions, including input restrictions; do not remove an associated label because it sounds similar.
- Inline and overall validation messages may intentionally provide feedback at different task locations.
- Point-of-use help can spare users from remembering/looking elsewhere for instructions.
- Repeated navigation/action cues may support distinct routes or contexts; evaluate whether the second instance helps.
- Identical phrase strings may serve different users/states; different wording may still repeat the same meaning.

## Correction guidance

Establish each text element’s purpose before editing. If two instances do the same job in the same context, keep the clearest and remove the duplicate. If each serves a distinct point of use, clarify the roles and keep them concise. Preserve associated form labels, format instructions, and actionable validation; test with keyboard/screen reader and, where unclear, observe users completing the task.

## Independent research references

- [Nielsen Norman Group — Duplicate links](https://www.nngroup.com/articles/duplicate-links) — redundancy can aid wayfinding but often adds interaction/cognitive cost.
- [GOV.UK — Writing for user interfaces](https://www.gov.uk/service-manual/design/writing-for-user-interfaces) — concise wording and removing unnecessary copy.
- [W3C WAI WCAG 2.2 labels or instructions](https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html) — necessary input labels/instructions and format guidance.
- [W3C WAI — User notification](https://www.w3.org/WAI/tutorials/forms/notifications) — inline/overall validation and actionable feedback.