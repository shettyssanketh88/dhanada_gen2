# Dhanada v2 — an agentic trading organisation

Dhanada v2 is a rebuild of the Dhanada trading platform as an **AI-run investment firm**: agents in named roles make every trading and organisational decision, remember and improve; code provides instruments, executes orders, keeps memory and enforces the owner's rails. Developed with **Spec-Driven Development (SDD)**.

The first attempt (v1, May–Sep 2026) built a complete platform and never found an edge. Its post-mortem is in [docs/lessons-from-v1.md](docs/lessons-from-v1.md) and it is normative here: every v2 design decision must answer "which v1 failure does this prevent?".

## How this repository is organised (SDD)

Nothing in this repository is code yet. Everything is specification, and the specification is the source of truth from which agents implement.

```
.specify/memory/constitution.md   Non-negotiable principles. Highest authority. Read first.
docs/lessons-from-v1.md           Why v1 failed; rules v2 must satisfy.
docs/research/                    Evidence: v1 research report + 2026-09-20 research on agentic systems.
docs/ADR/                         Architecture decision records (numbered, immutable once accepted).
specs/000-platform/               The platform-level specification:
    spec.md                         WHAT and WHY: vision, roles, workflows, requirements (DH2-* ids), acceptance scenarios.
    plan.md                         HOW: architecture, runtime, contracts, data model, security, deployment.
    roles.md                        The firm: CIO, Risk Office, Coach, desks (Analysts, Strategist, Trader, Position Manager, Reviewer), Research Lab, Operations.
    memory.md                       Memory: per-trade per-role dossiers, role/desk/firm memory, time-aware retrieval, consolidation.
    skills.md                       Skill catalogue: every role's procedures, scripts, evals.
    tools-and-rails.md              The code plane: execution service, calculators, sim engine, data, and the owner's rails.
    learning.md                     Decision scoring, coaching, research lab, desk proposals, investment committee.
    operations.md                   Firm hours, cadence, monitoring, incidents, human touchpoints, cost.
    tasks.md                        Ordered, verifiable implementation phases and tasks.
specs/NNN-<feature>/              One directory per feature, created from tasks.md when implementation starts.
```

## The SDD workflow

1. **Constitution** governs. Any conflict between a spec and the constitution is a spec bug.
2. **Specify** — a feature gets `specs/NNN-<name>/spec.md` with requirement ids `DH2-<AREA>-<nnn>`, EARS-style statements ("WHEN … THE SYSTEM SHALL …"), and acceptance scenarios (Given/When/Then).
3. **Plan** — `plan.md` records the technical approach, contracts, data model and the tests that prove each requirement.
4. **Tasks** — `tasks.md` lists ordered, independently verifiable tasks, each citing requirement ids.
5. **Implement** — agents implement from tasks, in a scratch clone (never on the OneDrive path), open a PR, and CI is the only verifier.
6. **Review** — anything with trading impact carries a Validation Reviewer verdict and the Coach's evals before it is published; rails and the IPS change only by the Principal.

The workflow is compatible with GitHub `spec-kit` conventions (`/speckit.constitution`, `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`); this repository pre-populates the platform-level artefacts so the feature-level commands start from a solid base.

## Ground rules for anyone (human or agent) working here

- The Git object database lives in `~/git-repos/dhanada-v2.git` (this directory holds only a `gitdir:` pointer). Never move it onto OneDrive.
- Work in a scratch clone; sync back; push; let CI verify. Never run suites on the laptop, never put source on the VM.
- Every PR cites the requirement ids it implements and the gate (if any) it is subject to.
- Read `docs/lessons-from-v1.md` before proposing anything about intraday trading, agent decisions, or exits.
- Agents decide; code never decides. If a task would put a decision rule in code outside `rails/`, it is a spec bug.
