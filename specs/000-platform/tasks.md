# Tasks — phased implementation roadmap

*Feature specs under `specs/NNN-<name>/` precede code. Tasks cite requirement ids; `[P]` = parallelisable. The firm trades paper first; the CIO moves desks to live within the IPS; the Principal is informed.*

## Phase 0 — Instruments and execution service (code only) · ~3 weeks

| Task | Feature spec | Requirements | Verification |
|---|---|---|---|
| 0.0 VPS reset (same Hostinger VPS as v1; Principal's decision 2026-10-02): **export and verify first** — PostgreSQL dump of v1 bars (1m/15m/daily), trial ledger, cost calibration, fills with reference prices; Kite app credentials and static-IP registration (unchanged, same box); `age` backup keys; monitor-bot email credentials. Then stop and remove all v1 containers, images, crons, `/opt/dhanada-prod`, `/etc/dhanada-prod`, stale source trees and logs; rebuild the baseline (Docker, native PostgreSQL 16, Caddy, Tailscale); re-create the deploy user and firewall; restore only the exported data into the v2 schema when `005-historical-data` lands. Executed only on the Principal's explicit go, outside market hours, with a Hostinger snapshot taken first | `000-vps-reset` | DH2-OPS-004, DH2-DAT-002 | Snapshot exists; export checksums recorded; box boots clean with only the baseline; Tailscale and static IP verified |
| 0.1 Repo, CI, release workflow, structural no-LLM test, hooks scaffolding | `001-repo-and-ci` | DH2-DEV-001/002 | CI green; release blocked on failing tests |
| 0.2 Contracts: all decision objects and runtime records | `002-contracts` | DH2-FIRM-003/004 | Schema tests |
| 0.3 Rails: `rails/RAILS.md`, `ips.yaml` loader, rail evaluation library | `003-rails` | DH2-RAIL-001/002 | Every rail unit-tested; rail event recorded with id |
| 0.3a [P] Rule catalogue and feeds: `rails/market_rules/` schema (A1–A19, B1–B10 with sources, effective dates, `[verify]` flags), feed pollers (surveillance lists, ban list, price bands, MIS list, haircuts, freeze quantities, calendar, circulars), compliance rails (`rails.compliance.*`) | `003a-rule-catalogue` | DH2-CMP-001/003/009 | Rails reproduce catalogue rows on dated fixtures; feeds refresh idempotently |
| 0.4 [P] Market data: Kite adapter (token, static IP, order-rate bucket), `full` ticker, bars, REST fallback, instrument master | `004-market-data` | DH2-DAT-001, DH2-TOOL-006 | Recorded ticks → bars; IP mismatch → state |
| 0.5 [P] Historical import and point-in-time universe, delistings, NSE feeds with `published_at` | `005-historical-data` | DH2-DAT-002/003 | Universe as-of differs by date; delisted present |
| 0.6 [P] Calculators `calc:*` with versioning and pinned tests | `006-calculators` | DH2-TOOL-002 | Each calculator reproducible from stored inputs |
| 0.7 [P] Accounting + counterfactual baselines + cost calibration + reconciliation engine (ledger vs broker snapshots, contract notes) + P&L attribution + tax ledger | `007-accounting-and-books` | DH2-TOOL-004, DH2-PIPE-009, DH2-CTL-003/004 | Worked examples; synthetic break detected; attribution sums to net P&L; STT per A18 |
| 0.7a [P] Treasury instruments: margin/basket-margin readers, peak-margin snapshot simulator, settlement calendar, collateral haircuts; TCA instruments: implementation shortfall per fill | `007a-treasury-tca-instruments` | DH2-CTL-001/002/005 | Margin plan reproduces a worked expiry-week example; shortfall computed on fixture fills |
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
| 1.6 [P] Operations Engineer role and skills incl. security/kill-switch ownership | `018-operations-role` | DH2-OPS-003 | O3 |
| 1.6a [P] Compliance Officers (Regulatory, Broker): pre-clearance flow, surveillance detectors and dispositions, holds, EOD close, circular tracking, self-audit | `018a-compliance-officers` | DH2-CMP-002/004/005/006/009 | S12, C1–C5 |
| 1.6b [P] Treasury & Settlement Manager, Books & Records Agent, Execution Quality Analyst roles and skills | `018b-control-roles` | DH2-CTL-001…005 | S13, S14; first TCA report |
| 1.7 [P] Feature service + expression language + strategy-book store and validation (`books:*`) | `019-features-and-books` | DH2-PIPE-003/004/005, DH2-TOOL-007/008 | T11, T14; a book validates and versions |
| 1.7a [P] Rule Watch + shadow recorder + execution log | `019a-rule-watch` | DH2-EXEC-001/002/006 | T11, T13 |
| 1.7b [P] Pipeline roles: Stock Scanner, Data Ingestor, Senior Analyst, Execution Agent (event mode), Recalibration Agent, Trade Reviewer + skills | `019b-pipeline-roles` | DH2-PIPE-001/002/006/008, DH2-EXEC-003/004/005 | S1, S3, S4, S5 on paper |
| 1.7c Agent Watch (continuous sessions, digests, concurrency cap, cost recording) | `019c-agent-watch` | DH2-EXEC-001, DH2-COST-003 | S2, S3; cost per stock-day recorded |
| 1.8 [P] Risk Officer role + skills (book review, auto-approval rules, sweeps, guidance, conference, drill) | `020-risk-office` | DH2-PIPE-006/007, DH2-RAIL-003 | S6; drill passes |
| 1.9 Decision scoring service + calibration records + counterfactuals per book version and watch mode + watch-mode report | `021-decision-scoring` | DH2-LRN-001/007, DH2-PIPE-009/010, DH2-EXEC-007 | L1; S5; first watch-mode report |
| 1.10 CIO role (charters, allocations, committee, journal) — first desk chartered on paper: Positional Momentum Desk `[NC-5]` | `022-cio-and-first-desk` | DH2-FIRM-002/006 | Charter applied; desk trades paper end to end |

Exit criterion: one desk trading paper for two weeks with both watch modes running (one governing, one shadow), every decision attributable to a role, every trade reviewed and scored with counterfactuals per version and mode, journal and digest delivered, spend within budget.

## Phase 2 — Learning and research loops · ~3 weeks

| Task | Feature spec | Requirements | Verification |
|---|---|---|---|
| 2.1 Coach role + skills (scoring, coaching, playbook revision with evals, lesson curation) | `023-coach` | DH2-LRN-002, DH2-MEM-003 | S7, L2 |
| 2.2 Research Lab roles: Quant Researcher, Data Steward, Validation Reviewer, Desk Designer + agentic replay mode | `024-research-lab` | DH2-LRN-003/004/006 | L4; agentic replay report for the first desk |
| 2.3 Skill Engineer role + PR flow with agent review + CI | `025-skill-engineer` | DH2-LRN-005 | S8, L5 |
| 2.4 Second and third desks chartered on paper from Lab proposals (Event/Catalyst, Intraday Breakout `[NC-5]`) | — | DH2-FIRM-002 | Committee minutes; desks trading paper |
| 2.5 Owner console v0 (Today, Inbox, Desk, Dossiers, Books, Agents, Journal, Governance, Compliance, Research), SSE bus, passkeys/TOTP over Tailscale (tailnet setup: VM package, laptop and phone apps; console bound to tailnet address; public vhost only for `/tg/*` and `/api/health`), pnpm lockfile CI, Playwright | `026-owner-console` | DH2-UI-001…007, 010…012 | U1, U2, U4, U6, U7, U8 |
| 2.5a [P] Telegram companion (8 verbs, notification matrix, signed one-time codes) | `026a-telegram-companion` | DH2-UI-003/004/008 | U1, U3 |
| 2.5b [P] Ask the firm (read-only tools, citations, widget catalogue, structural test) | `026b-ask-the-firm` | DH2-UI-009 | U5 |

Exit criterion: three desks on paper across ≥ 2 horizons; weekly coaching revisions with evals; monthly committee held with minutes.

## Phase 3 — Live execution path · ~3 weeks

| Task | Feature spec | Requirements | Verification |
|---|---|---|---|
| 3.1 Live Kite execution (place/modify/cancel, MIS and GTT protective orders, square-off, reconciliation, fault-injection suite) | `027-live-execution` | DH2-TOOL-001/005/006 | T1–T6 against a live account with quantity 1 during a supervised session |
| 3.2 Live hardening: separate DB/accounts, secrets audit, backup/restore drill, static-IP monitoring, Principal 2FA | `028-live-hardening` | DH2-CMP-001, plan.md §8 | Restore drill; secrets scan clean |
| 3.3 IPS live section and rails verification; kill drill on release; broker operating-model rails verified against `rails/broker-confirmation.md` (static IP, market protection, < 10 OPS, daily 2FA login); `[verify]` catalogue items resolved (NC-8) | `029-ips-live` | DH2-RAIL-*, DH2-CMP-008 | O4, C6, C7 |

## Phase 4 — First capital and firm growth · ongoing

| Task | Notes |
|---|---|
| 4.1 The CIO moves the first desk to live within the IPS (initial allocation cap in `ips.yaml`); the Principal is informed via the digest | DH2-FIRM-006 |
| 4.2 NFO adapter and index-futures desk proposals | Lab backlog |
| 4.3 pgvector retrieval if recall proves insufficient (ADR) | measure first |
| 4.4 Managed Agents for Lab shifts if VM compute limits (ADR-001 revisit) | trading roles stay on the VM |

## Definition of done (every task)

Feature spec with ids and scenarios; tests in CI with coverage floors; skill evals passing; docs and memory updated; PR cites ids; agent review recorded; Principal informed in the digest.
