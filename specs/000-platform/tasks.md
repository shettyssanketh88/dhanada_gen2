# Tasks — phased implementation roadmap

*Each phase produces feature specs under `specs/NNN-<name>/` (spec.md, plan.md, tasks.md, contracts/) before code. Tasks cite requirement ids; `[P]` marks tasks that can run in parallel. Verification is stated per task. Nothing trades real money before Phase 5's G5 gate.*

## Phase 0 — Foundation (no agents, no trading) · target 3 weeks

Goal: a tested engine skeleton that can ingest data, simulate, account and refuse unregistered research.

| Task | Feature spec | Requirements | Verification |
|---|---|---|---|
| 0.1 Repo bootstrap: layout (`plan.md` §3), CI (ruff, mypy --strict, pytest, testcontainers Postgres, structural no-LLM test), release workflow that runs tests before building | `001-repo-and-ci` | DH2-DEV-001/002, E8 | CI green on an empty engine; release blocked when a test fails |
| 0.2 Contracts package: all Pydantic models in `plan.md` §6 with JSON schemas, `additionalProperties: false`, range validators | `002-contracts` | DH2-ORG-005, DH2-TRD-004 | Schema tests; agent-output schemas contain no numeric fields |
| 0.3 Rule tables: instruments, lot/freeze, expiry, holidays, square-off, cost rates with `effective_from`; loader by date | `003-rule-tables` | DH2-DAT-004, DH2-CMP-002 | Rates for 2026-04-01 reproduce the research cost table |
| 0.4 [P] Market data: Kite adapter (token store, static-IP check, rate limiter), `full`-mode ticker, bar builder, REST quote fallback, instrument master | `004-market-data` | DH2-DAT-001, DH2-EXE-004/005/008 | Replay a recorded tick file → bars; IP mismatch → halted state |
| 0.5 [P] Historical import: v1 bars → Parquet; daily backfill; NSE bhavcopy; point-in-time universe and delisting tables | `005-historical-data` | DH2-DAT-002/003 | Universe as-of 2021-04-01 differs from 2026-08-01; delisted names present |
| 0.6 [P] Accounting: positions, cash, costs, slippage, R, sleeve rollups, cost calibration report | `006-accounting` | DH2-TRD-008, DH2-EXE-010, DH2-RSK-005 | v1 WP0.2/0.3 worked examples reproduce |
| 0.7 [P] Simulation kernel: first-touch, honest limits, cost/slippage models, deterministic seeds; parity harness with accounting | `007-sim-kernel` | DH2-EXE-009, E7 | Same-bar tie = loss; parity test passes |
| 0.8 Trial ledger + stats + pre-registration enforcement + zero-alpha calibration | `008-research-ledger` | DH2-RSH-001/002/003/005 | R1–R3 scenarios; pinned DSR/PSR/MTRL numerics |
| 0.9 Dossier store: state machine, sections, events, evidence, filesystem projection, embargo-safe retrieval | `009-dossiers` | DH2-TRD-001, DH2-MEM-001/002/007 | M1, M2, M5 scenarios |
| 0.10 Audit chain + observability skeleton (OTel, metrics, structured logs) | `010-audit-observability` | DH2-CMP-001, DH2-OBS-001/002 | Chain verifies; spans visible for a simulated order |

## Phase 1 — Agent plane and the research loop · target 3 weeks

Goal: agents research, review, remember and operate — with no execution path yet.

| Task | Feature spec | Requirements | Verification |
|---|---|---|---|
| 1.1 Runtime: role definitions → AgentDefinitions, launcher, budgets, structured outputs, invocation audit, hooks (deny broker/secrets/env), sandbox | `011-agent-runtime` | DH2-ORG-001/003/006, DH2-DEV-004, DH2-COST-001/002 | S8 scenario; budget stop test; hook denial logged |
| 1.2 Engine MCP server with per-role capability tokens; read tools; `ledger:*`, `dossiers:*`, `memory:*` | `012-engine-mcp` | DH2-ORG-003 | Tool called outside role scope is denied |
| 1.3 Memory service: role memory layout, lesson schema/status, injection policy, consolidation job, secrets linter | `013-memory` | DH2-MEM-003/004/005/006 | M3, M4 scenarios |
| 1.4 Scheduler: shift runs/steps, resume, event queue, budgets, notifications (email + Telegram) | `014-scheduler` | DH2-OPS-001, DH2-OBS-003 | O1, O2 scenarios |
| 1.5 Skills framework + shared skills (`recalling-memory`, `writing-memory`, `using-engine-tools`) + eval runner in CI | `015-skills-framework` | DH2-DEV-003 | Eval runner grades state; 3 evals per shared skill |
| 1.6 [P] Quant Researcher + skills (`researching-hypotheses`, `preregistering-trials`, `running-backtests`, `reporting-trials`, `proposing-promotion`) with sandboxed backtest | `016-quant-researcher` | DH2-RSH-004/007 | Nightly shift runs B-001 in-sample and produces a report with DSR/N/k |
| 1.7 [P] Validation Reviewer + `reviewing-promotions`, `auditing-ledger` | `017-validation-reviewer` | DH2-RSH-006 | R4 scenario; Researcher and Reviewer are distinct sessions |
| 1.8 [P] Operations Engineer + morning checklist, data quality, incidents, deploy verification | `018-operations-engineer` | DH2-OPS-003/004, DH2-DAT-006 | O3 scenario; degenerate feature withheld |
| 1.9 [P] Market Intelligence Analyst + `briefing-market`, `tagging-catalysts`; feature health tests | `019-market-intel` | DH2-DAT-005/006, DH2-RSH-008 | Tags carry `published_at`; historical tagging is masked |
| 1.10 Desk Head + `running-shifts`, `writing-desk-journal`, `escalating-incidents`; daily journal delivered | `020-desk-head` | DH2-ORG-004, DH2-OPS-002 | A full non-trading day runs end to end within budget |
| 1.11 Research backlog seeded (B-001…B-010) and first weekly research committee held | — | DH2-RSH-007 | Committee record with verdicts exists |

Exit criterion: two consecutive weeks of nightly research shifts producing pre-registered trials, reviewed by the Validation Reviewer, with the desk journal and weekly digest delivered and LLM cost within budget.

## Phase 2 — First sleeve on paper (positional momentum core) · target 3 weeks

| Task | Feature spec | Requirements | Verification |
|---|---|---|---|
| 2.1 Signal engine `mom_core` (PIT universe, formation/hold, quality screen, MA overlay) + config schema + evals | `021-sleeve-mom-core` | DH2-TRD-002/003 | Harness trial registered; G1 evaluated by code from ledger rows |
| 2.2 Policy gate with the initial rule set and `rules/policy.yaml` | `022-policy-gate` | DH2-RSK-001/002/006/007 | Every rule has unit tests; denial records rule ids |
| 2.3 Paper OMS: order intents, tags, unknown-state handling, reconciliation against the sim kernel, positional GTT-equivalent brackets in paper | `023-paper-oms` | DH2-EXE-001/002/003/006 | E1–E5 in paper mode |
| 2.4 Governor + kill switch (levels 1–3) + drill in CI | `024-governor-kill` | DH2-RSK-003/004 | S5, S7, O4 scenarios |
| 2.5 Trade Manager (vetting, hold events, narrative) + shadow A/B arm + Risk Officer (sweep, pause/kill, cost calibration, veto-arm review) + Post-Trade Reviewer (per-trade, weekly) | `025-trading-roles` | DH2-TRD-004/005/006/007, DH2-MEM-001 | S1, S2, M1 scenarios in paper |
| 2.6 Portfolio Manager + feasible-set tool + monthly review | `026-portfolio-manager` | DH2-RSK-003 | Tier cannot exceed governor ceiling |
| 2.7 Dashboard v0 (desk, research, ops, Principal actions) | `027-dashboard` | DH2-OPS-002 | No win-rate anywhere |
| 2.8 `mom_core` first paper rebalance through the full dossier path | — | G1 → paper | Dossiers for every rebalance order; journal reports it |

Exit criterion: `mom_core` on paper with G1 passed; two monthly rebalances executed by the engine; every dossier reviewed.

## Phase 3 — Live execution path and intraday/swing sleeves · target 5 weeks

| Task | Feature spec | Requirements | Verification |
|---|---|---|---|
| 3.1 Live Kite OMS: placement, modification, cancellation, MIS brackets with watchdog, GTT brackets, square-off, reconciliation, OPS governor, fault-injection suite | `028-live-oms` | DH2-EXE-001…010, DH2-EXE-007 | E1–E6 against a live account with quantity 1 on a liquid name during a supervised session `[Principal present]` |
| 3.2 Compliance Auditor + audit chain verification + circular tracking + rules PR flow | `029-compliance-auditor` | DH2-CMP-003/004 | Weekly report produced; a synthetic circular yields a rule PR with effective date |
| 3.3 [P] Sleeve `sip_orb` (stocks-in-play ORB) research → G2 → paper | `030-sleeve-sip-orb` | G2, G3 | Pre-registered holdouts; paper with ≥ 100 trades |
| 3.4 [P] Sleeve `hod_pm_dailyatr` research (re-validation with ≥ 1× daily ATR stop, realised costs) → G2 → paper | `031-sleeve-hod-pm` | G2, G3 | As above |
| 3.5 [P] Sleeve `overnight_hybrid` (carry rule, CNC conversion) research → paper | `032-sleeve-overnight-hybrid` | G2, G3 | Carry conversions executed in paper |
| 3.6 Catalyst veto feature G4 test on `sip_orb` (with-arm vs without-arm) | — | DH2-RSH-008, G4 | Difference with t-stat in the digest |
| 3.7 Swing-horizon research (B-006) → sleeve spec if G2 passes | `033-sleeve-swing` | G2 | Ledger evidence |

Exit criterion: ≥ 3 sleeves on paper across ≥ 2 horizons; live OMS proven with supervised quantity-1 orders; kill drill passing on every release.

## Phase 4 — Portfolio layer and capital gate · target 3 weeks

| Task | Feature spec | Requirements | Verification |
|---|---|---|---|
| 4.1 Correlation matrix, portfolio DSR, vol targeting across sleeves, capacity estimates | `034-portfolio-layer` | G5 inputs | Weekly digest shows the matrix and portfolio DSR |
| 4.2 Capital gate procedure as a skill + signed approval flow + live sleeve creation with reduced risk | `035-capital-gate` | G5, DH2-ORG-002 | Dry run produces the full evidence bundle |
| 4.3 Live environment hardening: separate DB/accounts, secret handling audit, backup/restore drill, static IP monitoring, Principal 2FA on dashboard actions | `036-live-hardening` | DH2-CMP-001, DH2-EXE-005, plan.md §8 | Restore drill passes; secrets scan clean |
| 4.4 First capital on the positional core (≤ ₹100,000), intraday last | — | G5 | Principal signature file; journal records first live dossier |

## Phase 5 — Expansion (after first capital) · ongoing

| Task | Feature spec | Notes |
|---|---|---|
| 5.1 NFO adapter + NIFTY futures sleeves (`nifty_last30`, trend overlay) | `037-nfo-futures` | B-007, B-008 |
| 5.2 Optional embeddings for memory retrieval (pgvector) if BM25 recall proves insufficient (ADR) | `038-memory-retrieval-v2` | Measure first |
| 5.3 Managed Agents for research shifts (cloud sandbox, scheduled deployments) if VM compute or isolation becomes the bottleneck (ADR-001 revisit) | `039-research-runtime-v2` | Keep trading roles on the VM |
| 5.4 PEAD / low-vol tilt sleeves | `040-…` | B-002, B-010 |

## Definition of done (every task)

1. Feature spec exists with requirement ids and acceptance scenarios; `[NC]` markers resolved.
2. Tests cited in the spec pass in CI; coverage floors met; structural tests pass.
3. Skill evals (if any) pass; state-graded.
4. Docs updated: `memory/desk/` where applicable, ADR if a decision changed.
5. PR cites requirement ids and (if applicable) the gate id; Principal approval recorded for trading-impact changes.
