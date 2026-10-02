#!/usr/bin/env python3
"""Coverage floors per path (DH2-DEV-001): 90 % for engine/exec, engine/accounting, engine/rails; 85 % elsewhere.

Usage: check_coverage.py [coverage.json]   (as written by `coverage json` / `pytest --cov-report=json`)
A path with no statements passes. Exit code 1 if any group is under its floor. Stdlib only.
"""

from __future__ import annotations

import json
import pathlib
import sys

STRICT = ("engine/exec/", "engine/accounting/", "engine/rails/")
STRICT_FLOOR, DEFAULT_FLOOR = 90.0, 85.0
ELSEWHERE = "elsewhere"


def group_of(filename: str) -> str:
    name = filename.replace("\\", "/")
    return next((prefix.rstrip("/") for prefix in STRICT if name.startswith(prefix)), ELSEWHERE)


def main(argv: list[str]) -> int:
    report = json.loads(pathlib.Path(argv[1] if len(argv) > 1 else "coverage.json").read_text())
    totals: dict[str, list[int]] = {}
    for filename, data in report["files"].items():
        summary = data["summary"]
        group = totals.setdefault(group_of(filename), [0, 0])
        group[0] += summary["covered_lines"]
        group[1] += summary["num_statements"]

    failed = False
    for name, (covered, statements) in sorted(totals.items()):
        floor = DEFAULT_FLOOR if name == ELSEWHERE else STRICT_FLOOR
        percent = 100.0 if statements == 0 else 100.0 * covered / statements
        ok = percent >= floor
        failed = failed or not ok
        print(f"{'ok  ' if ok else 'FAIL'} {name}: {percent:.2f} % of {statements} statements (floor {floor:.0f} %)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
