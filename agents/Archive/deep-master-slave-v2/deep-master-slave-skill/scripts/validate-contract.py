#!/usr/bin/env python3
"""Validate task contract completeness."""

import sys
import re

REQUIRED_SECTIONS = [
    'GOAL:',
    'SCOPE',
    'OUT OF SCOPE',
    'ACCEPTANCE CRITERIA',
    'EXPECTED DELIVERABLE',
    'ISSUED BY:',
    'ASSIGNED TO:',
    'TASK ID:'
]

def validate_contract(filepath):
    """Check if a task contract file has all required sections."""
    with open(filepath, 'r') as f:
        content = f.read()

    missing = []
    for section in REQUIRED_SECTIONS:
        if section not in content:
            missing.append(section)

    if missing:
        print(f"❌ Missing sections: {', '.join(missing)}")
        return False
    else:
        print(f"✅ Contract is complete: {filepath}")
        return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python validate-contract.py <contract-file>")
        sys.exit(1)

    success = validate_contract(sys.argv[1])
    sys.exit(0 if success else 1)
