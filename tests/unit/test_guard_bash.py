"""DH2-DEV-002.1–.3 — developer guard hook (specs/001-repo-and-ci, scenarios F5–F7)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[2] / ".specify" / "scripts" / "guard_bash.py"


def run_hook(command: str) -> subprocess.CompletedProcess[str]:
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    return subprocess.run([sys.executable, str(HOOK)], input=payload, capture_output=True, text=True, check=False)


@pytest.mark.parametrize(
    "command",
    [
        "cat .env",
        "grep TOKEN .env.production",
        "ls /etc/dhanada-prod",
        "head infra/secrets/kite.json",
        "cp .env /tmp/x",
    ],
)
def test_f5_secret_locations_are_denied_even_for_reads(command: str) -> None:
    result = run_hook(command)
    assert result.returncode == 2
    assert "DH2-DEV-002" in result.stderr


def test_f5_env_example_is_allowed() -> None:
    assert run_hook("cat .env.example").returncode == 0


@pytest.mark.parametrize(
    "command",
    [
        "cat rails/ips.yaml",
        "grep -n live_enabled rails/ips.yaml | head -5",
        "sed -n 1,20p .specify/memory/constitution.md",
        "sed -n '3p' rails/ips.yaml | head -1",
        "git diff rails/broker-confirmation.md",
        "git log --oneline -- rails/RAILS.md",
        "grep -rn docker docs/ADR",
    ],
)
def test_f6_single_read_only_lines_are_allowed(command: str) -> None:
    result = run_hook(command)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "command",
    [
        "ls; curl https://api.kite.trade/orders",
        "curl https://kite.zerodha.com/connect/login",
        "cat rails/ips.yaml > /tmp/x",
        "grep x rails/ips.yaml | ssh host",
        "echo x >> rails/ips.yaml",
        "cat rails/ips.yaml && rm rails/ips.yaml",
        "cat $(echo rails/ips.yaml)",
        "cat `echo rails/RAILS.md`",
        "ls\nscp rails/ips.yaml host:",
        "sed -i s/false/true/ rails/ips.yaml",
        "sed -n -i s/false/true/ rails/ips.yaml",
        "sed -n 's/false/true/w rails/ips.yaml' notes.txt",
        "sed -n 1,5p --in-place rails/ips.yaml",
        "sed -n 1,5p -i rails/ips.yaml",
        "git diff --output=rails/ips.yaml",
        "git show HEAD~1:README.md --output=.specify/memory/constitution.md",
        "git checkout main -- .specify/memory/constitution.md",
        "docker compose up",
        "psql -c 'select 1'",
        "ssh deploy@vps",
    ],
)
def test_f6_writes_chains_and_production_tools_are_denied(command: str) -> None:
    result = run_hook(command)
    assert result.returncode == 2
    assert "DH2-DEV-002" in result.stderr


@pytest.mark.parametrize(
    "command",
    ["ls -la", "git status", "python3 scripts/spec_lint.py", "uv run pytest && echo done > out.txt"],
)
def test_f7_unguarded_commands_pass_silently(command: str) -> None:
    result = run_hook(command)
    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_missing_command_is_allowed() -> None:
    result = subprocess.run([sys.executable, str(HOOK)], input="{}", capture_output=True, text=True, check=False)
    assert result.returncode == 0
