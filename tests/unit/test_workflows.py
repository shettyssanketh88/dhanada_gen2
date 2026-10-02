"""DH2-DEV-001.1, DH2-DEV-001.6 — workflow structure (specs/001-repo-and-ci, scenarios F1, F8)."""

from __future__ import annotations

import re
from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parents[2] / ".github" / "workflows"


def test_ci_runs_every_required_check() -> None:
    ci = (WORKFLOWS / "ci.yml").read_text(encoding="utf-8")
    for command in (
        "uv sync --locked",
        "ruff check",
        "ruff format --check",
        "mypy",
        "pytest",
        "scripts/check_coverage.py",
        "scripts/spec_lint.py",
        "git diff --exit-code",
    ):
        assert command in ci, command
    assert "pull_request:" in ci
    assert "workflow_call:" in ci


def test_f8_release_publishes_only_after_ci() -> None:
    release = (WORKFLOWS / "release.yml").read_text(encoding="utf-8")
    assert re.search(r"^  ci:\n    uses: \./\.github/workflows/ci\.yml$", release, re.MULTILINE)
    assert re.search(r"^  publish:\n    needs: ci$", release, re.MULTILINE)
    assert re.search(r"tags:\s*\n\s*- ['\"]v\*['\"]", release)


def test_actions_are_pinned_to_commit_shas() -> None:
    for workflow in WORKFLOWS.glob("*.yml"):
        for ref in re.findall(r"uses: (\S+@\S+)", workflow.read_text(encoding="utf-8")):
            assert re.fullmatch(r"[\w./-]+@[0-9a-f]{40}", ref), f"{workflow.name}: {ref}"
