"""DH2-DEV-001.1 — the top-level packages exist and import (specs/001-repo-and-ci, scenario F1)."""

from __future__ import annotations

import importlib

import pytest


@pytest.mark.parametrize("package", ["engine", "runtime", "contracts"])
def test_package_imports(package: str) -> None:
    assert importlib.import_module(package).__name__ == package
