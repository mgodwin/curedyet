#!/usr/bin/env python3
"""Check every disease, pipeline stage and tracker file. Exits 1 on any problem.

Run it before opening a pull request:  python scripts/validate.py
"""
import sys

from curedata import load_all, validate

errors = validate(load_all())
if errors:
    print(f"Found {len(errors)} problem(s):\n")
    for e in errors:
        print(f"  - {e}")
    print("\nField guide: CONTRIBUTING.md. Ladder and forecast rules: METHODOLOGY.md.")
    sys.exit(1)
print("All good: every record passed validation.")
