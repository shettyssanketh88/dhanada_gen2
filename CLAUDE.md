# Dhanada v2 — instructions for implementing agents

You are implementing an **AI-run investment firm** from its specification. Read in this order, every session:
1. `.specify/memory/constitution.md` — binding. Article I: agents decide, code never decides (outside `rails/`). Article X: specs precede code; CI is the only verifier.
2. `specs/README.md` — how features are specified, planned, tasked, implemented and traced.
3. The feature you are working on: `specs/NNN-<name>/{spec,plan,tasks}.md`. Its parent requirements live in `specs/000-platform/spec.md` (ids `DH2-<AREA>-<nnn>`); companions explain the design (`roles.md`, `memory.md`, `tools-and-rails.md`, `learning.md`, `operations.md`, `compliance.md`, `ui.md`, `scenario-walkthrough.md`).

## Non-negotiables (mechanically checked)
- No decision rule in code outside `rails/`. If a task would need one, stop and raise it as a spec defect.
- Nothing under `engine/` imports an LLM client (structural test).
- Every PR cites the requirement ids it implements and the acceptance scenarios it satisfies; `python3 scripts/spec_lint.py` must pass.
- Agents never touch secrets, `.env*`, broker endpoints or the production VPS. Hooks in `.claude/settings.json` deny it; do not work around them.
- Never run test suites on the laptop against OneDrive paths; work in a scratch clone, push, and let CI verify.

## Stack and conventions
Python 3.12, `ruff`, `mypy --strict`, pytest (unit ≥ 90 % for `engine/exec`, `engine/accounting`, `engine/rails`; ≥ 85 % elsewhere), Pydantic v2 contracts in `contracts/`, PostgreSQL 16 + Parquet/DuckDB, FastAPI, Claude Agent SDK for roles, Vite + React + TypeScript (pnpm, frozen lockfile) for `ui/`. Commit style: `type(scope): subject`.

## Workflow for a task
1. Read the task row in `specs/000-platform/tasks.md` and its feature spec. If the feature directory does not exist, scaffold it: `python3 .specify/scripts/new_feature.py NNN-name "Title"` and fill `spec.md` from the platform requirements it cites before writing code.
2. Write tests from the acceptance scenarios first; then the minimum code that passes them.
3. Run `python3 scripts/spec_lint.py`, `ruff`, `mypy --strict`, `pytest` in the scratch clone.
4. Open a PR citing requirement ids and scenarios. Trading-impact changes also need the Validation Reviewer role's verdict (recorded in the PR).

## Where things live
`engine/` code plane · `runtime/` agent plane glue · `agents/<role>/ROLE.md` · `skills/<name>/` · `rails/` (Principal-owned: `RAILS.md`, `ips.yaml`, `broker-confirmation.md`; `market_rules/` by Compliance Officers via PR) · `memory/` · `research/` · `contracts/` · `tests/{unit,integration,compliance,evals}` · `infra/` · `ui/`.

Operating facts: Hostinger VPS (same box as v1, to be reset by task `000-vps-reset`), static IPv4 whitelisted with Zerodha, Tailscale for the owner console, one daily manual Kite login. Live capital ₹1 lakh, `live_enabled: false` until the go-live procedure in `rails/ips.yaml` holds.
