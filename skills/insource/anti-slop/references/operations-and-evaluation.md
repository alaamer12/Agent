# Operations, scripts, tests, and evaluations

## Requirements and safety

Bundled scripts and tests use Python 3.10+ and the standard library. The structural scanner is read-only and accepts selected files/directories. Browser capture tooling is optional and requires Playwright plus a browser runtime; it is not required for project reviews that already have screenshots or a running browser.

Use the product repository as the working directory for the commands below. Do not run `scripts/build_registry.py` as a review command: it regenerates the skill’s canonical registry from captured local catalog data.

## Validation commands

```text
python anti-slop/scripts/validate_registry.py
python -m unittest discover -s anti-slop/tests -p "test_*.py" -v
python -m unittest discover -s anti-slop/tests/structural -p "test_*.py" -v
python -m unittest discover -s anti-slop/tests/visual -p "test_*.py" -v
python -m unittest discover -s anti-slop/tests/integration -p "test_*.py" -v
```

`tests/README.md` describes suite responsibilities. Structural fixtures test candidate precision/recall on positive, negative, and exception inputs. Visual results are an independently reviewed calibration set, not an automated visual model; integration cases protect disagreement and evidence boundaries. Passing manifest tests does not constitute a live product audit.

## Skill-level evals

`evals/evals.json` keeps the three host prompts in `evals` and defines three local HTML review cases in `html_impact_evals`, tiered high/medium/low by fixture-specific user impact. The local runner `evals/run_html_evals.py` requires Playwright and a working Chromium browser; it renders screenshots, records narrow runtime observations, and runs the structural candidate scanner against each fixture. It writes reproducible metrics and evidence to `evals/results.json` and screenshots to `evals/screenshots/`.

Run the local HTML cases from the repository root with `python anti-slop/evals/run_html_evals.py`. Its precision/recall/F1 score covers only expected structural candidate pattern IDs; it is not a visual-quality, final-finding, or LLM skill score. Record independent visual/contextual and structural reviewer outputs in `evals/agent-review-observations.json`, then run `python anti-slop/evals/score_agent_reviews.py` to write `evals/agent-review-score.json`. The scorer reports modality precision/recall, false-positive calibration, and combined status accuracy against the case annotations. The repository does not bundle or invoke a compatible model runtime, so do not claim host-level agent performance from the local run.

To execute the original host prompts, use a host that can load the skill and provide the listed screenshot/source files. Run each prompt in an isolated with-skill session; if benchmarking skill benefit, run the same prompt in a comparable without-skill session and grade both against the same expectations. Preserve outputs and timing in the host’s eval workspace.

## Optional capture helper

`scripts/capture_inner_scroll.py` is an evidence-acquisition utility for pages with internally scrollable panels. It requires Playwright, a working Chromium installation, and network access to the supplied URL. Use it only when authorized to capture the target; it creates screenshot outputs in the requested directory. It is not part of the regular test suite.