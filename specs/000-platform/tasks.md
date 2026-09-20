# Tasks — phased implementation roadmap

*Feature specs under `specs/NNN-<name>/` precede code. Tasks cite requirement ids; `[P]` = parallelisable. The firm trades paper first; the CIO moves desks to live within the IPS; the Principal is informed.*

## Phase 0 — Instruments and execution service (code only) · ~3 weeks

| Task | Feature spec | Requirements | Verification |
|---|---|---|---|
| 0.1 Repo, CI, release workflow, structural no-LLM test, hooks scaffolding | `001-repo-and-ci` | DH2-DEV-001/002 | CI green; release blocked on failing tests |
| 0.2 Contracts: all decision objects and runtime records | `002-contracts` | DH2-FIRM-003/004 | Schema tests |
| 0.3 Rails: `rails/RAILS.md`, `ips.yaml` loader, market rules with `effective_from`, rail evaluation library | `003-rails` | DH2-RAIL-001/002 | Every rail unit-tested; rail event recorded with id |
| 0.4 [P] Market data: Kite adapter (token, static IP, order-rate bucket), `full` ticker, bars, REST fallback, instrument master | `004-market-data` | DH2-DAT-001, DH2-TOOL-006 | Recorded ticks → bars; IP mismatch → state |
| 0.5 [P] Historical import and point-in-time universe, delistings, NSE feeds with `published_at` | `005-historical-data` | DH2-DAT-002/003 | Universe as-of differs by date; delisted present |
| 0.6 [P] Calculators `calc:*` with versioning and pinned tests | `006-calculators` | DH2-TOOL-002 | Each calculator reproducible from stored inputs |
| 0.7 [P] Accounting + counterfactual baselines + cost calibration | `007-accounting` | DH2-TOOL-004, DH2-DSK-007 | Worked examples; baselines on a synthetic trade |
| 0.8 [P] Sim/replay engine (rule mode) with parity harness | `008-sim-engine` | DH2-TOOL-003 | T7; parity passes |
| 0.9 Trial ledger + stats + zero-alpha calibration tool | `009-ledger` | DH2-LRN-003 | L3; pinned DSR/PSR/MTRL |
| 0.10 Dossier store: states, sections, events, evidence, counterfactual slots, projection, time-aware retrieval | `010-dossiers` | DH2-DSK-001, DH2-MEM-001/002/005 | M1, M2, M5 |
| 0.11 Execution service: order intents, tags, unknown-state, reconciliation, protective orders (MIS OCO watchdog, GTT), square-off, subscriptions — paper first | `011-execution-service` | DH2-TOOL-001, DH2-DSK-006 | T1–T5, T9 in paper |
| 0.12 Audit chain, observability, notifications | `012-audit-observability` | DH2-CMP-001, DH2-OBS-001/002 | Chain verifies; spans present |

## Phase 1 — The firm runs (paper), one desk end to end · ~4 weeks

| Task | Feature spec | Requirements | Verification |
|---|---|---|---|
| 1.1 Runtime: roles → AgentDefinitions, launcher, prompt assembly (no anchoring numbers), structured decisions with correction rounds, budgets, hooks, sandbox, invocation audit | `013-agent-runtime` | DH2-FIRM-001/004, DH2-DEV-002, DH2-COST-001/002 | S8-style denial logged; budget stop |
| 1.2 Firm MCP tools with per-role scopes (`firm:*`, `desks:*`, `dossiers:*`, `calc:*`, `exec:*`, `memory:*`, `ledger:*`, `learning:*`, `ops:*`) | `014-firm-tools` | DH2-TOOL-*, DH2-MEM-* | Out-of-scope tool denied |
| 1.3 Memory service: role/desk/firm memory, lessons with status, retrieval, consolidation, linter | `015-memory` | DH2-MEM-003/004/006 | M3, M4, M6 |
| 1.4 Scheduler + events + meetings orchestration + journal/digest delivery | `016-scheduler-meetings` | DH2-FIRM-005, DH2-OPS-001/002 | O1, O2, O5; a meeting produces minutes with positions |
| 1.5 Skills framework + shared skills + eval runner in CI | `017-skills-framework` | DH2-DEV-001 | State-graded evals run |
| 1.6 [P] Operations Engineer + Compliance Auditor roles and skills | `018-operations-roles` | DH2-OPS-003, DH2-CMP-002/003 | O3; weekly audit produced |
| 1.7 [P] Desk roles: Analysts, Strategist, Trader, Position Manager, Desk Reviewer + skills | `019-desk-roles` | DH2-DSK-002…008 | S1, S2 on paper |
| 1.8 [P] Risk Office role + skills (plan review, sweeps, guidance, conference, drill) | `020-risk-office` | DH2-DSK-003/004, DH2-RAIL-003 | S3, S4; drill passes |
| 1.9 Decision scoring service + calibration records | `021-decision-scoring` | DH2-LRN-001 | L1 |
| 1.10 CIO role (charters, allocations, committee, journal) — first desk chartered on paper: Positional Momentum Desk `[NC-5]` | `022-cio-and-first-desk` | DH2-FIRM-002/006 | Charter applied; desk trades paper end to end |

Exit criterion: one desk trading paper for two weeks with every decision attributable to a role, every trade reviewed and scored, journal and digest delivered, spend within budget.

## Phase 2 — Learning and research loops · ~3 weeks

| Task | Feature spec | Requirements | Verification |
|---|---|---|---|
| 2.1 Coach role + skills (scoring, coaching, playbook revision with evals, lesson curation) | `023-coach` | DH2-LRN-002, DH2-MEM-003 | S7, L2 |
| 2.2 Research Lab roles: Quant Researcher, Data Steward, Validation Reviewer, Desk Designer + agentic replay mode | `024-research-lab` | DH2-LRN-003/004/006 | L4; agentic replay report for the first desk |
| 2.3 Skill Engineer role + PR flow with agent review + CI | `025-skill-engineer` | DH2-LRN-005 | S8, L5 |
| 2.4 Second and third desks chartered on paper from Lab proposals (Event/Catalyst, Intraday Breakout `[NC-5]`) | — | DH2-FIRM-002 | Committee minutes; desks trading paper |
| 2.5 Dashboard v0 | `026-dashboard` | DH2-OPS-002 | No win-rate headline |

Exit criterion: three desks on paper across ≥ 2 horizons; weekly coaching revisions with evals; monthly committee held with minutes.

## Phase 3 — Live execution path · ~3 weeks

| Task | Feature spec | Requirements | Verification |
|---|---|---|---|
| 3.1 Live Kite execution (place/modify/cancel, MIS and GTT protective orders, square-off, reconciliation, fault-injection suite) | `027-live-execution` | DH2-TOOL-001/005/006 | T1–T6 against a live account with quantity 1 during a supervised session |
| 3.2 Live hardening: separate DB/accounts, secrets audit, backup/restore drill, static-IP monitoring, Principal 2FA | `028-live-hardening` | DH2-CMP-001, plan.md §8 | Restore drill; secrets scan clean |
| 3.3 IPS live section and rails verification; kill drill on release | `029-ips-live` | DH2-RAIL-* | O4 |

## Phase 4 — First capital and firm growth · ongoing

| Task | Notes |
|---|---|
| 4.1 The CIO moves the first desk to live within the IPS (initial allocation cap in `ips.yaml`); the Principal is informed via the digest | DH2-FIRM-006 |
| 4.2 NFO adapter and index-futures desk proposals | Lab backlog |
| 4.3 pgvector retrieval if recall proves insufficient (ADR) | measure first |
| 4.4 Managed Agents for Lab shifts if VM compute limits (ADR-001 revisit) | trading roles stay on the VM |

## Definition of done (every task)

Feature spec with ids and scenarios; tests in CI with coverage floors; skill evals passing; docs and memory updated; PR cites ids; agent review recorded; Principal informed in the digest.
