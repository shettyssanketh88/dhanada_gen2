# Specifications — index and method

This repository is developed with Spec-Driven Development. The platform specification (`000-platform/`) is the source of truth; each feature is a directory `NNN-<name>/` created from `000-platform/tasks.md` with the scaffolder below.

## Layers
| Layer | File | Owner | Changes by |
|---|---|---|---|
| Constitution | `.specify/memory/constitution.md` | Principal | signed amendment |
| Platform spec | `000-platform/spec.md` (requirements `DH2-<AREA>-<nnn>`, scenarios) + companions | Principal and Claude in review | PR + spec lint |
| Feature specs | `NNN-<name>/spec.md`, `plan.md`, `tasks.md`, `contracts/`, optional `research.md`, `data-model.md`, `quickstart.md` | implementing agents | PR + spec lint |
| Traceability | `000-platform/traceability.md` | generated | `scripts/spec_lint.py` |

## Writing a feature spec
- Start from the task row: copy its requirement ids into the feature `spec.md` and restate each as a feature-level requirement `DH2-<AREA>-<nnn>.<k>` with EARS phrasing (WHEN/WHILE/IF … THE SYSTEM SHALL …).
- Acceptance scenarios in Given/When/Then; each becomes a test (and an eval for anything a role does).
- Unknowns are written as `[NEEDS CLARIFICATION: question]` and must be resolved (or explicitly deferred with an owner) before `tasks.md` is written.
- `plan.md` names modules, contracts, data model, migrations, tests, and the structural checks that apply (no LLM import in `engine/`, read-only tool registries, hooks).
- `tasks.md` lists ordered, independently verifiable tasks with `[P]` for parallelisable ones; each cites requirement ids and scenario ids.

## Definition of done
Spec, plan and tasks exist and lint clean; tests from scenarios pass in CI with the coverage floors; skill evals pass; `traceability.md` regenerated; docs and memory updated; PR cites ids; trading-impact changes carry a Validation Reviewer verdict; the Principal is informed in the digest.

## Features
| Id | Name | Phase | Status |
|---|---|---|---|
| 000 | platform | — | specified (v2.3) |
| 001 | repo-and-ci | 0 | implementing |
| 000-vps-reset, 002 … 033 | see `000-platform/tasks.md` | 0–4 | not started |
