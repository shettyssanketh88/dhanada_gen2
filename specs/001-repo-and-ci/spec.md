# Feature 001 — Repo and CI

| Field | Value |
|---|---|
| Feature id | `001-repo-and-ci` |
| Phase / task | `0.1` in `specs/000-platform/tasks.md` |
| Parent requirements | DH2-DEV-001, DH2-DEV-002 |
| Status | implementing |
| Companion docs | `000-platform/plan.md` §2, §3, §9; constitution Article X |

## 1. Purpose
Give every later feature a verifier. v1 shipped images that were built without tests and changed production by hand (`docs/lessons-from-v1.md` F13); its development environment could not run checks reliably (F15). This feature makes CI the only verifier (constitution X.2): one workflow runs the linters, the type checker, the tests with coverage floors, the spec lint and the structural "no LLM client in `engine/`" test, and a release cannot be published unless that workflow passed. It also makes the developer guard hook do what DH2-DEV-002 says.

## 2. Scope
**In scope (all deterministic developer tooling; no role is touched and no trading decision exists here):**
- Python project definition (`pyproject.toml`, locked dependencies) and the empty top-level packages `engine/`, `runtime/`, `contracts/` and `tests/{unit,integration,compliance,evals}`.
- CI workflow on every pull request and on pushes to `main`.
- Release workflow on version tags, gated on the CI workflow.
- Coverage floors per path, the structural no-LLM test, spec lint in CI (extended to feature specs), tests for the developer guard hook and a fix for the gaps those tests expose.

**Out of scope:** see §8.

## 3. Requirements (EARS)
- **DH2-DEV-001.1** WHEN a pull request is opened or updated, or a commit lands on `main`, THE SYSTEM SHALL run `ruff check`, `ruff format --check`, `mypy --strict`, `pytest` and `scripts/spec_lint.py`, and SHALL report failure if any of them fails.
- **DH2-DEV-001.2** WHEN the tests have run, THE SYSTEM SHALL fail the build if statement coverage is below 90 % for `engine/exec`, `engine/accounting` or `engine/rails`, or below 85 % for the rest of `engine/`, `runtime/` and `contracts/`; a path with no statements yet passes.
- **DH2-DEV-001.3** THE SYSTEM SHALL fail the build if any Python file under `engine/` imports an LLM client library, statically or through `importlib.import_module` / `__import__` with a literal name.
- **DH2-DEV-001.4** THE SYSTEM SHALL lint feature specs (`specs/NNN-<name>/*.md`) as well as the platform spec: every requirement id they cite must be defined in the platform spec, and open clarification markers are listed.
- **DH2-DEV-001.5** IF `specs/000-platform/traceability.md` in the commit differs from what `scripts/spec_lint.py` generates, THEN THE SYSTEM SHALL fail the build.
- **DH2-DEV-001.6** WHEN a tag `v*` is pushed, THE SYSTEM SHALL run the full CI workflow on that commit and SHALL publish the release only if it passed.
- **DH2-DEV-002.1** WHEN a developer-session Bash command references a secret location (`.env` files other than `.env.example`, `/etc/dhanada*`, a `secrets/` directory), THE SYSTEM SHALL deny it, including read-only commands.
- **DH2-DEV-002.2** WHEN a developer-session Bash command references a broker endpoint, a production tool (`ssh`, `scp`, `docker`, `psql`) or a Principal-owned file (`rails/ips.yaml`, `rails/RAILS.md`, `rails/broker-confirmation.md`, the constitution), THE SYSTEM SHALL deny it unless every command in the line is a read-only command (`cat`, `sed -n`, `grep`, `head`, `tail`, `ls`, `git diff|log|show|status`) with no output redirection or command substitution.
- **DH2-DEV-002.3** WHEN the hook denies a command, THE SYSTEM SHALL exit with status 2 and name the requirement and the matched patterns on standard error.

## 4. Acceptance scenarios
- **F1** Given a clean checkout, When the CI workflow runs, Then lint, format check, type check, tests, coverage floors, spec lint and the traceability check all pass.
- **F2** Given a file under `engine/` containing `import anthropic` (or `from openai import …`, or `importlib.import_module("claude_agent_sdk")`), When the structural test scans it, Then it is reported with file and module name; Given the same import under `runtime/`, Then it is not reported.
- **F3** Given a coverage report where `engine/rails` is at 89 % and everything else at 100 %, When the floor check runs, Then it fails naming `engine/rails`, 89 % and the 90 % floor; at 90 % it passes; Given `engine/features` at 85 % it passes and at 84 % it fails; Given no statements under a path, it passes.
- **F4** Given a spec tree where a feature spec cites an id that the platform spec does not define, When the spec lint runs, Then it exits 1 and names the id and the file; Given a task row with no requirement id, Then it exits 1 naming the task.
- **F5** Given the command `cat .env`, When the guard hook evaluates it, Then it is denied with exit status 2; Given `cat .env.example`, Then it is allowed.
- **F6** Given `cat rails/ips.yaml`, Then allowed; Given `ls; curl https://api.kite.trade/orders`, `cat rails/ips.yaml > /tmp/x`, `grep x rails/ips.yaml | ssh host`, or `echo x >> rails/ips.yaml`, Then each is denied with exit status 2 and the message names DH2-DEV-002.
- **F7** Given a command that references none of the guarded patterns, Then the hook exits 0 with no output.
- **F8** Given a tag `v*` on a commit whose CI workflow fails, When the release workflow runs, Then the publish job does not run (it depends on the CI job).

## 5. Contracts and data
None. No Pydantic models, tables, events or agent tools. Files added: `pyproject.toml`, `uv.lock`, `.github/workflows/{ci,release}.yml`, `scripts/check_coverage.py`, package and test directories.

## 6. Rails and compliance touchpoints
No rail is evaluated. The guard hook protects the Principal-owned rail files and the constitution from developer sessions (reads allowed, writes denied); it does not change them. The structural no-LLM test enforces constitution VI.1 for `engine/`.

## 7. Clarifications
None open.

## 8. Non-goals
Each item below is part of DH2-DEV-001 or DH2-DEV-002 but has nothing to verify yet; the named feature adds it to CI.
- Integration tests on PostgreSQL — added by `010-dossiers`, the first feature with database tests.
- Skill evals in CI — `017-skills-framework`.
- Kill drill on release tags — `020-risk-office`.
- Building and publishing container images on release — `011-execution-service`, the first deployable service (DH2-OPS-004).
- Runtime-harness hooks for agent sessions — `013-agent-runtime`.
- UI lockfile and Playwright checks — `026-owner-console`.
- Branch protection on `main` is a repository setting for the Principal, not code.
