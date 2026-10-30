# Visual calibration suite

`cases.json` is the expected classification rubric for obvious slop, subtle cross-page repetition, and legitimate lookalikes. `results.json` records an independent screenshot-only assessment; it preserves candidates and false positives rather than interpreting visual similarity as proof.

The rendered fixtures are under `fixtures/`; their screenshots are under `screenshots/`. Re-capture after changing a fixture. For each review, record the screenshot/viewport, observed region, relevant context, counterevidence, exceptions considered, and any missing state/brand information. The visual scout is qualitative: a manifest test can verify artifact/ID/result consistency, but it cannot replace a visual reviewer.