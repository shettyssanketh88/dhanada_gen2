"""DH2-DEV-001.3 — nothing under engine/ imports an LLM client (constitution VI.1; scenario F2, platform T8)."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = (
    "anthropic",
    "claude_agent_sdk",
    "openai",
    "litellm",
    "langchain",
    "langchain_core",
    "langchain_anthropic",
    "langchain_openai",
    "google.generativeai",
    "google.genai",
    "mistralai",
    "cohere",
    "ollama",
    "groq",
)
DYNAMIC_IMPORTERS = {"import_module", "__import__"}


def forbidden_name(module: str) -> str | None:
    return next((n for n in FORBIDDEN if module == n or module.startswith(n + ".")), None)


def imported_modules(tree: ast.AST) -> list[str]:
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            modules.append(node.module)
            modules += [f"{node.module}.{alias.name}" for alias in node.names]
        elif isinstance(node, ast.Call) and node.args:
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            first = node.args[0]
            if name in DYNAMIC_IMPORTERS and isinstance(first, ast.Constant) and isinstance(first.value, str):
                modules.append(first.value)
    return modules


def llm_imports(directory: Path) -> list[tuple[str, str]]:
    found: set[tuple[str, str]] = set()
    for path in directory.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for module in imported_modules(tree):
            name = forbidden_name(module)
            if name:
                found.add((path.relative_to(directory).as_posix(), name))
    return sorted(found)


def test_f2_scanner_reports_static_and_dynamic_llm_imports(tmp_path: Path) -> None:
    engine = tmp_path / "engine"
    (engine / "exec").mkdir(parents=True)
    (engine / "a.py").write_text("import anthropic\n")
    (engine / "exec" / "b.py").write_text("from openai import OpenAI\n")
    (engine / "c.py").write_text("import importlib\nimportlib.import_module('claude_agent_sdk')\n")
    (engine / "d.py").write_text("from google import generativeai\n")
    (engine / "e.py").write_text("def f():\n    import anthropic.types\n    __import__('litellm')\n")
    (engine / "ok.py").write_text("import json\nfrom decimal import Decimal\nimport anthropic_free_name\n")

    assert llm_imports(engine) == [
        ("a.py", "anthropic"),
        ("c.py", "claude_agent_sdk"),
        ("d.py", "google.generativeai"),
        ("e.py", "anthropic"),
        ("e.py", "litellm"),
        ("exec/b.py", "openai"),
    ]


def test_f2_same_import_outside_engine_is_not_scanned(tmp_path: Path) -> None:
    (tmp_path / "engine").mkdir()
    (tmp_path / "runtime").mkdir()
    (tmp_path / "runtime" / "launcher.py").write_text("import claude_agent_sdk\n")

    assert llm_imports(tmp_path / "engine") == []


def test_engine_has_no_llm_client_import() -> None:
    assert (ROOT / "engine").is_dir()
    assert llm_imports(ROOT / "engine") == []
