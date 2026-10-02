"""DH2-DEV-001.2 — coverage floors per path (specs/001-repo-and-ci, scenario F3)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_coverage.py"


def run_check(tmp_path: Path, files: dict[str, tuple[int, int]]) -> subprocess.CompletedProcess[str]:
    report = {
        "files": {
            name: {"summary": {"covered_lines": covered, "num_statements": statements}}
            for name, (covered, statements) in files.items()
        }
    }
    path = tmp_path / "coverage.json"
    path.write_text(json.dumps(report))
    return subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True, check=False)


def test_f3_strict_path_below_90_fails_and_is_named(tmp_path: Path) -> None:
    result = run_check(
        tmp_path,
        {"engine/rails/ips.py": (89, 100), "engine/exec/orders.py": (100, 100), "runtime/launcher.py": (10, 10)},
    )
    assert result.returncode == 1
    assert "FAIL engine/rails: 89.00 % of 100 statements (floor 90 %)" in result.stdout
    assert "ok   engine/exec: 100.00 %" in result.stdout


def test_f3_strict_path_at_90_passes(tmp_path: Path) -> None:
    result = run_check(tmp_path, {"engine/rails/a.py": (50, 50), "engine/rails/b.py": (40, 50)})
    assert result.returncode == 0, result.stdout


def test_f3_strict_floor_applies_to_each_strict_path_separately(tmp_path: Path) -> None:
    result = run_check(tmp_path, {"engine/accounting/a.py": (80, 100), "engine/exec/b.py": (100, 100)})
    assert result.returncode == 1
    assert "FAIL engine/accounting" in result.stdout


def test_f3_elsewhere_at_85_passes_and_at_84_fails(tmp_path: Path) -> None:
    assert run_check(tmp_path, {"engine/features/a.py": (85, 100)}).returncode == 0
    result = run_check(tmp_path, {"engine/features/a.py": (84, 100), "contracts/b.py": (0, 0)})
    assert result.returncode == 1
    assert "FAIL elsewhere: 84.00 %" in result.stdout


def test_f3_no_statements_passes(tmp_path: Path) -> None:
    result = run_check(tmp_path, {"engine/__init__.py": (0, 0), "engine/rails/__init__.py": (0, 0)})
    assert result.returncode == 0
    assert run_check(tmp_path, {}).returncode == 0
