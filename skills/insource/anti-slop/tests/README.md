# Test suites

Run from the repository root:

```text
python anti-slop/scripts/build_registry.py
python anti-slop/scripts/validate_registry.py
python -m unittest discover -s anti-slop/tests -p "test_*.py" -v
python -m unittest discover -s anti-slop/tests/structural -p "test_*.py" -v
python -m unittest discover -s anti-slop/tests/visual -p "test_*.py" -v
python -m unittest discover -s anti-slop/tests/integration -p "test_*.py" -v
```

The structural suite checks positive, negative, and exception cases for every implemented source candidate detector. The visual suite validates its rendered screenshot fixtures and the independently reviewed expected classifications; visual judgment itself remains contextual. The integration suite verifies evidence preservation and non-overriding reconciliation outcomes. Registry checks require a knowledge/detection disposition and evidence links for every official catalog entry.

The skill-level prompt evaluations live in `../evals/evals.json`; see `../evals/README.md` for running them in a compatible agent host. Local unit tests validate the eval manifest and its input files, but do not invoke a model or claim behavioral benchmark results.