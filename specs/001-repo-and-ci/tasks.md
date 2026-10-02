# Tasks — 001 Repo and CI

| # | Task | Requirements | Scenarios | Verification | Parallel |
|---|---|---|---|---|---|
| 1 | Project definition: `pyproject.toml`, `uv.lock`, empty packages and test directories | DH2-DEV-001.1 | F1 | `uv sync --locked` succeeds; packages import | |
| 2 | Structural no-LLM test | DH2-DEV-001.3 | F2 | Fixture imports detected; real `engine/` clean | [P] |
| 3 | Coverage floors script | DH2-DEV-001.2 | F3 | Boundary cases at 89/90 and 84/85 | [P] |
| 4 | Spec lint: typed, root argument, feature specs | DH2-DEV-001.4, DH2-DEV-001.5 | F4 | Undefined id and uncited task fail; repository lints clean | [P] |
| 5 | Guard hook: secrets always denied; reads only as a single read-only line | DH2-DEV-002.1, DH2-DEV-002.2, DH2-DEV-002.3 | F5, F6, F7 | Allow and deny cases with exit codes | [P] |
| 6 | CI workflow | DH2-DEV-001.1, DH2-DEV-001.2, DH2-DEV-001.5 | F1 | Green run on the pull request | |
| 7 | Release workflow gated on CI | DH2-DEV-001.6 | F8 | `publish` needs `ci`; structure test | |

Order is dependency order. Every task is independently verifiable. Definition of done: `specs/README.md`.
