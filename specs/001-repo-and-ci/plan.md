# Plan — 001 Repo and CI

## Approach
One GitHub Actions workflow (`ci.yml`) is the verifier; it is also callable (`workflow_call`) so the release workflow reuses it rather than duplicating steps. Dependencies are managed with `uv` and a committed `uv.lock`; CI installs with `--locked` so the lock is the only source of versions. Actions are pinned to commit SHAs. The project is not built as a wheel (`tool.uv.package = false`); packages are imported from the repository root.

Alternatives considered: a separate job per tool (slower, no benefit at this size); `coverage --fail-under` (one global floor only, cannot express the 90 % paths); pre-commit (adds a second verifier, against constitution X.2).

## Modules
| Path | Responsibility | Tests |
|---|---|---|
| `pyproject.toml`, `uv.lock` | Python 3.12, dev dependencies, ruff, mypy strict, pytest and coverage configuration | exercised by CI (F1) |
| `engine/`, `runtime/`, `contracts/` | Empty packages so later features have a home and the checks have a target | `tests/unit/test_packages.py` |
| `.github/workflows/ci.yml` | DH2-DEV-001.1, .2, .3, .5 | F1 (the PR's own run) |
| `.github/workflows/release.yml` | DH2-DEV-001.6: `publish` job `needs` the CI job | F8 (structure asserted in `tests/unit/test_workflows.py`) |
| `scripts/check_coverage.py` | Per-path floors from `coverage.json` | `tests/unit/test_check_coverage.py` (F3) |
| `tests/compliance/test_no_llm_in_engine.py` | AST scan of `engine/` for LLM client imports | same file (F2) |
| `scripts/spec_lint.py` | Typed; optional root argument for tests; also reads feature specs | `tests/unit/test_spec_lint.py` (F4) |
| `.specify/scripts/guard_bash.py` | DH2-DEV-002.1–.3 | `tests/unit/test_guard_bash.py` (F5–F7) |

## Contracts
None.

## Data model and migrations
None.

## Runtime (if roles are involved)
None.

## Structural checks
- No LLM import under `engine/`: forbidden top-level modules are `anthropic`, `claude_agent_sdk`, `openai`, `litellm`, `langchain*`, `google.generativeai`, `google.genai`, `mistralai`, `cohere`, `ollama`, `groq`. The scanner is proven against fixture files, then run on the real tree.
- Spec lint and regenerated `traceability.md` must leave the tree unchanged (`git diff --exit-code`).

## Test plan
The three scripts are command-line programs, so they are tested as programs (subprocess, real exit codes). Coverage is measured on `engine`, `runtime`, `contracts` only.

| Scenario | Test |
|---|---|
| F1 | CI run on the pull request |
| F2 | `tests/compliance/test_no_llm_in_engine.py` |
| F3 | `tests/unit/test_check_coverage.py` |
| F4 | `tests/unit/test_spec_lint.py` |
| F5, F6, F7 | `tests/unit/test_guard_bash.py` |
| F8 | `tests/unit/test_workflows.py` |

## Risks and rollback
- The guard hook becomes stricter: chained commands that mention a guarded word are now denied even when they start with a read-only command. A developer session that hits this rewrites the command as a single read; nothing is lost.
- The guard matches text, so it is best-effort: a glob or an indirect path (a wildcard, a variable) that never spells a guarded name is not caught. The controls behind it are the `Edit` deny rules in `.claude/settings.json` and review of the PR diff.
- The release workflow cannot be exercised without pushing a tag; its gating is asserted structurally and by the first real release.
- Rollback: revert the PR; nothing outside the repository changes.
