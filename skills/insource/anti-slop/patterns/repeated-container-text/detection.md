# Detection: Same text repeated inside one container

## Catalog route

The official catalog classifies this as a **source** rule. Duplicate strings locate candidates; copy purpose and form/accessibility context determine whether repetition is unnecessary.

## Candidate signals

1. Find identical/near-identical visible text within a card, panel, or form group.
2. Classify each instance as heading, label, help, action, status, validation, or navigation.
3. Determine whether each instance contributes distinct point-of-use context or merely repeats the same job.
4. Check associations for labels/descriptions and inline/global validation before removal.

## False-positive controls

- Do not remove a field label or useful input instruction just because related wording appears nearby.
- Do not equate matching strings with redundant meaning or purpose.
- Do not infer usefulness solely from distinct wording; paraphrases can still duplicate information.

## Test disposition

Source fixtures should include a true repeated phrase and legitimate label/help/error or point-of-use repetition. Tests must retain necessary accessible associations; regex alone cannot determine copy purpose.