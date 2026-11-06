#!/usr/bin/env python3
"""Self-test: the verifier must PASS the clean template and FAIL each known-broken part.

  python scripts/selftest.py

Run it after changing verify_parts.py, the template, or the thresholds. Each file in
examples/broken-parts/<slot>/<id>.svg is dropped into a temporary copy of the template
and must be reported as an ERROR for exactly that part.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "assets" / "rig-template"
BROKEN = ROOT / "examples" / "broken-parts"
VERIFY = ROOT / "scripts" / "verify_parts.py"


def run(rig, out):
    p = subprocess.run([sys.executable, str(VERIFY), str(rig), "--combos", "3", "--out", str(out)],
                       capture_output=True, text=True)
    report = json.loads((Path(out) / "report.json").read_text()) if (Path(out) / "report.json").exists() else {}
    return p.returncode, report.get("errors", []), p.stdout + p.stderr


def main():
    tmp = Path(tempfile.mkdtemp(prefix="avatar-selftest-"))
    failures = []
    code, errs, text = run(TEMPLATE, tmp / "clean")
    print(f"clean template: {'PASS' if code == 0 else 'FAIL'}")
    if code != 0:
        failures.append("clean template should pass")
        print(text)

    rig = tmp / "rig"
    shutil.copytree(TEMPLATE, rig)
    expected = []
    for f in sorted(BROKEN.glob("*/*.svg")):
        (rig / "parts" / f.parent.name).mkdir(parents=True, exist_ok=True)
        shutil.copy(f, rig / "parts" / f.parent.name / f.name)
        expected.append(f"{f.parent.name}/{f.stem}")
    code, errs, text = run(rig, tmp / "broken")
    if code == 0:
        failures.append("broken rig should fail")
    for tag in expected:
        hit = any(e.startswith(tag + ":") for e in errs)
        print(f"  {tag:16s} {'caught' if hit else 'MISSED'}")
        if not hit:
            failures.append(f"{tag} not caught")
    shutil.rmtree(tmp, ignore_errors=True)
    print("selftest:", "PASS" if not failures else "FAIL - " + "; ".join(failures))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
