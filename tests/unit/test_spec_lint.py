"""DH2-DEV-001.4, DH2-DEV-001.5 — spec lint (specs/001-repo-and-ci, scenario F4)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "spec_lint.py"

SPEC = (
    "# Spec\n\n- **DH2-DEV-001** THE SYSTEM SHALL be verified by CI.\n- **DH2-DEV-002** THE SYSTEM SHALL use hooks.\n"
)
TASKS = "| Task | Feature spec | Requirements | Verification |\n|---|---|---|---|\n| 0.1 Repo and CI | `001-repo-and-ci` | DH2-DEV-001/002 | CI green |\n"


def make_tree(tmp_path: Path, *, tasks: str = TASKS, feature_spec: str | None = None) -> Path:
    platform = tmp_path / "specs" / "000-platform"
    platform.mkdir(parents=True)
    (platform / "spec.md").write_text(SPEC, encoding="utf-8")
    (platform / "tasks.md").write_text(tasks, encoding="utf-8")
    (tmp_path / ".specify" / "memory").mkdir(parents=True)
    (tmp_path / ".specify" / "memory" / "constitution.md").write_text("# Constitution\n", encoding="utf-8")
    (tmp_path / "rails").mkdir()
    if feature_spec is not None:
        feature = tmp_path / "specs" / "001-repo-and-ci"
        feature.mkdir()
        (feature / "spec.md").write_text(feature_spec, encoding="utf-8")
    return tmp_path


def run_lint(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), str(root)], capture_output=True, text=True, check=False)


def test_clean_tree_passes_and_writes_traceability(tmp_path: Path) -> None:
    root = make_tree(tmp_path, feature_spec="- **DH2-DEV-001.1** WHEN a PR opens THE SYSTEM SHALL run CI.\n")
    result = run_lint(root)
    assert result.returncode == 0, result.stdout
    assert "2 requirements defined, 0 uncovered by tasks: none" in result.stdout
    trace = (root / "specs" / "000-platform" / "traceability.md").read_text(encoding="utf-8")
    assert "| DH2-DEV-001 | specs/000-platform/spec.md:3 | 0.1 |" in trace
    assert "| DH2-DEV-002 | specs/000-platform/spec.md:4 | 0.1 |" in trace


def test_f4_feature_spec_citing_undefined_id_fails(tmp_path: Path) -> None:
    root = make_tree(tmp_path, feature_spec="Parent requirements: DH2-DEV-001, DH2-OPS-099\n")
    result = run_lint(root)
    assert result.returncode == 1
    assert "undefined requirement referenced: DH2-OPS-099 in specs/001-repo-and-ci/spec.md" in result.stdout


def test_f4_task_without_requirement_id_fails(tmp_path: Path) -> None:
    tasks = TASKS + "| 0.2 Contracts | `002-contracts` | — | Schema tests |\n"
    result = run_lint(make_tree(tmp_path, tasks=tasks))
    assert result.returncode == 1
    assert "task 0.2 (tasks.md:4) cites no requirement id" in result.stdout


def test_duplicate_definition_fails(tmp_path: Path) -> None:
    root = make_tree(tmp_path)
    (root / "specs" / "000-platform" / "extra.md").write_text("- **DH2-DEV-001** again\n", encoding="utf-8")
    result = run_lint(root)
    assert result.returncode == 1
    assert "duplicate definition DH2-DEV-001" in result.stdout


def test_open_clarification_in_feature_spec_is_listed_as_warning(tmp_path: Path) -> None:
    root = make_tree(tmp_path, feature_spec="- [NEEDS CLARIFICATION: which runner?] DH2-DEV-001\n")
    result = run_lint(root)
    assert result.returncode == 0
    assert "WARN    open clarification specs/001-repo-and-ci/spec.md:1" in result.stdout


def test_repository_specs_lint_clean_and_traceability_is_current() -> None:
    path = ROOT / "specs" / "000-platform" / "traceability.md"
    before = path.read_text(encoding="utf-8")
    result = run_lint(ROOT)
    assert result.returncode == 0, result.stdout
    assert path.read_text(encoding="utf-8") == before
