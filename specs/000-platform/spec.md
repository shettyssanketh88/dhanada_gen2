# Dhanada v2 — Platform Specification (WHAT and WHY)

| Field | Value |
|---|---|
| Spec id | `000-platform` |
| Status | Draft v1.0 for Principal review |
| Date | 2026-09-20 |
| Governed by | `.specify/memory/constitution.md` v1.0.0 |
| Inputs | `docs/lessons-from-v1.md`, `docs/research/*` (4 reports) |
| Companion documents | `plan.md`, `roles.md`, `memory.md`, `skills.md`, `execution.md`, `research.md`, `operations.md`, `tasks.md` |

Requirement ids are `DH2-<AREA>-<nnn>`. Areas: ORG (organisation), TRD (trade lifecycle), MEM (memory), RSH (research), RSK (risk and policy), EXE (execution), DAT (data), OPS (operations), CMP (compliance), OBS (observability), COST (LLM cost), DEV (development). Requirements use EARS phrasing. `[NC]` marks an open clarification the Principal must resolve before the feature spec that cites it is finalised.

---

## 1. Vision

Dhanada v2 is an **autonomous trading organisation** for Indian markets, operated through Zerodha Kite, in which AI agents hold named roles (research, intelligence, trade management, risk, review, operations, compliance) and deterministic code performs everything that must be exact (execution, accounting, risk enforcement, simulation, data). Its product is a governed **portfolio of sleeves**: independently accounted strategies, each of which entered production through a pre-registered gate and each of which can be paused, demoted or retired by measured evidence.

The organisation learns. Every trade is a durable **dossier** that each role reads before acting and writes to after acting. Every research result is a **trial** in a ledger. Every lesson has a status (hypothesis, validated, retired) and only validated lessons influence trading. The loop from review to hypothesis to trial to gate to deployment is owned end to end.

## 2. Goals

| # | Goal | Measure |
|---|---|---|
| G1 | Positive net expectancy after realised costs at the portfolio level | Portfolio Deflated Sharpe > 0 on paper across ≥ 3 sleeves before capital |
| G2 | Breadth | ≥ 3 sleeves across ≥ 2 horizons before capital; ≥ 5 within 12 months of first capital |
| G3 | A research loop that runs without the Principal | ≥ 4 pre-registered trials per week produced, reviewed and dispositioned by agents |
| G4 | Survivable drawdowns | Automatic governance at pre-declared sleeve and desk thresholds; no override without written approval |
| G5 | Operational autonomy | Only the daily broker login and capital/skill approvals require the Principal |
| G6 | Honest measurement | Every Sharpe reported with DSR, N, k and MTRL; realised cost per R on every trade |
| G7 | Bounded LLM spend | Daily budget per shift, enforced by the runtime, reported in the desk journal |

## 3. Non-goals (v2.0)

- Options selling as a P&L engine (India VRP is net negative after frictions; constitution V.3).
- Sub-15-minute holding periods or any strategy whose stop is inside one daily ATR (constitution III.3).
- LLM-proposed price levels, quantities or thresholds (constitution I.1).
- Multi-tenant SaaS, mobile apps, or a public API. One Principal, one broker account family.
- Automated broker login (Zerodha terms forbid it; see `docs/research/2026-09-20-kite-sebi-execution-constraints.md`).
- Kubernetes; the single-VM Docker Compose model from v1 ADR-005 is retained.

## 4. Users

| User | Interaction |
|---|---|
| **Principal** (owner, one person) | Daily broker login; reads the daily desk journal and weekly digest; approves capital gates, constitution changes and trading-behaviour skill changes; can invoke any kill level. |
| **Agents** (the roles in `roles.md`) | Operate the desk through skills and typed tools on schedules and events. |
| **Developer agents** (Claude Code specialists) | Implement feature specs via PRs; never touch production directly. |

## 5. The organisation at a glance

```
                          ┌────────────────────────── Principal ──────────────────────────┐
                          │  login · approvals · kill switch · weekly digest                │
                          └───────────────────────────────┬────────────────────────────────┘
                                                          │
   AGENT PLANE (skills, memory, typed tools; NO broker write credentials)
   ┌──────────────┐  ┌───────────────┐  ┌────────────────┐  ┌───────────────┐  ┌────────────────┐
   │ Desk Head    │  │ Market Intel  │  │ Quant          │  │ Validation    │  │ Portfolio      │
   │ (orchestrate)│  │ Analyst       │  │ Researcher     │  │ Reviewer      │  │ Manager        │
   └──────┬───────┘  └───────┬───────┘  └───────┬────────┘  └──────┬────────┘  └──────┬─────────┘
   ┌──────┴───────┐  ┌───────┴───────┐  ┌───────┴────────┐  ┌──────┴────────┐  ┌──────┴─────────┐
   │ Trade        │  │ Risk Officer  │  │ Post-Trade     │  │ Operations    │  │ Compliance     │
   │ Manager      │  │ (supervises)  │  │ Reviewer       │  │ Engineer      │  │ Auditor        │
   └──────┬───────┘  └───────┬───────┘  └───────┬────────┘  └──────┬────────┘  └──────┬─────────┘
          │  typed tools (MCP): candidates, dossiers, ledger, memory, health, pause_sleeve, …
   ═══════╪══════════════════╪══════════════════╪═════════════════╪═════════════════╪═══════════
   ENGINE (deterministic, tested, versioned; owns numbers and credentials)
   data ingest · feature store · signal engines · policy gate · OMS/execution · accounting
   simulation kernel · trial ledger + stats · governor · kill switch · dossier store · scheduler
   ═══════╪════════════════════════════════════════════════════════════════════════════════════
          │ Kite Connect (one static IP, one token)          PostgreSQL · Parquet/DuckDB
```

The two planes are separated by a **hard boundary**: agents call the engine through typed tools whose implementations enforce policy; the engine never calls a language model on the trading path.

## 6. Trade lifecycle (the dossier state machine)

| State | Owner | Entered when | Exits to |
|---|---|---|---|
| `candidate` | Engine (signal) | A sleeve's signal engine emits a candidate with entry zone, stop, target, horizon, sleeve risk budget | `vetted`, `vetoed`, `expired` |
| `vetted` | Trade Manager | Categorical checks pass (event veto, data sanity, liquidity class, exposure overlap); thesis recorded | `intent` |
| `vetoed` | Trade Manager | A categorical veto fires (reason enum recorded; A/B arm recorded) | terminal |
| `intent` | Engine | Quantity, prices, product and bracket computed from the sleeve budget and the candidate; policy gate evaluated | `submitted`, `rejected_policy` |
| `rejected_policy` | Engine | Policy gate denies (rule id recorded) | terminal |
| `submitted` | Engine (OMS) | Order sent; tag persisted before the HTTP call | `open`, `cancelled`, `expired` |
| `open` | Engine (OMS) / Trade Manager (narrative) | Fill confirmed by order-book reconciliation | `managing` |
| `managing` | Engine (bracket) / Trade Manager (categorical events only) | Bracket active; carry decision at the gated rule's time | `closing` |
| `closing` | Engine (OMS) | Exit order placed (stop, target, square-off, kill) | `closed` |
| `closed` | Engine (accounting) | Both legs reconciled; costs, slippage, R computed | `reviewed` |
| `reviewed` | Post-Trade Reviewer | Structured rubric written to the dossier; hypotheses queued | `archived` |
| `archived` | Engine | Retention rules applied; dossier immutable | terminal |

Only the owner of the current state may transition it, plus the Risk Officer's pause and the kill switch, which may force `closing` from any open state.

## 7. Requirements

### 7.1 Organisation (ORG)

- **DH2-ORG-001** THE SYSTEM SHALL define each agent role as a versioned role definition (mandate, model, allowed tools, skills, memory scopes, forbidden actions, budget) checked into the repository under `agents/<role>/`.
- **DH2-ORG-002** WHEN a role definition changes in a way that affects trading behaviour (tools, forbidden actions, decision skills), THE SYSTEM SHALL require the Principal's approval recorded in the PR before the change is deployable.
- **DH2-ORG-003** THE SYSTEM SHALL run roles as isolated agent sessions with their own context, tool allowlist and budget; roles SHALL communicate only through the dossier store, the research ledger, memory, and typed engine tools, never through shared conversation history.
- **DH2-ORG-004** THE SYSTEM SHALL provide a Desk Head orchestrator that starts every scheduled shift, records a shift run (start, end, cost, outcome) and escalates failures to the Principal channel.
- **DH2-ORG-005** WHEN any role's structured output fails schema validation, THE SYSTEM SHALL record a `REVIEW` sentinel on the affected entity and continue fail-safe (no trade, no promotion), never a silent default.
- **DH2-ORG-006** THE SYSTEM SHALL keep an append-only audit record of every agent invocation: role, role version, skill versions, model, prompt version, input references, output, cost, correlation ids.
- **DH2-ORG-007** WHERE a decision requires debate (promotion review, monthly allocation), THE SYSTEM SHALL limit debate to at most two rounds and record each round's structured position.

### 7.2 Trade lifecycle (TRD)

- **DH2-TRD-001** THE SYSTEM SHALL represent every trade as a dossier entity from `candidate` to `archived` with the state machine in §6, a single owner per state, and a complete transition log.
- **DH2-TRD-002** THE SYSTEM SHALL generate candidates only from versioned signal engines of sleeves whose status is `active` or `reduced`; agents SHALL NOT create candidates.
- **DH2-TRD-003** WHEN a candidate is created, THE SYSTEM SHALL compute entry zone, stop, target, horizon, product (MIS/CNC/NRML) and the sleeve risk budget in code and store them on the dossier before any agent sees it.
- **DH2-TRD-004** WHEN the Trade Manager vets a candidate, THE SYSTEM SHALL accept only a structured verdict `{decision: take|veto, veto_reason: enum|null, thesis, invalidation_conditions: enum[], confidence_bucket}` and SHALL ignore any numeric field.
- **DH2-TRD-005** THE SYSTEM SHALL run the Trade Manager's veto as an A/B arm: a deterministic fraction of candidates per sleeve is executed regardless of the veto (shadow), and the lift of the veto is reported weekly as expectancy difference with t-statistic. `[NC-1: shadow fraction; proposed 30 %]`
- **DH2-TRD-006** WHEN an open position exists for a symbol, THE SYSTEM SHALL NOT create a second candidate for that symbol in any sleeve until the position is closed.
- **DH2-TRD-007** THE SYSTEM SHALL define exits at entry (bracket) and SHALL change them only by rules that passed a gate; the Trade Manager MAY request `close_now` only for an enumerated invalidation condition that its role definition lists.
- **DH2-TRD-008** WHEN a trade closes, THE SYSTEM SHALL compute gross P&L, statutory costs, slippage against reference prices on both legs, `risk_inr` and `r_multiple`, and SHALL mark the dossier `closed` only after both legs reconcile with the broker order book.
- **DH2-TRD-009** THE SYSTEM SHALL expose a replay facility that reconstructs any dossier decision from stored inputs and reproduces the same engine outputs bit-for-bit.

### 7.3 Memory (MEM)

- **DH2-MEM-001** THE SYSTEM SHALL provide per-trade, per-role memory: each dossier has one section per role that touched it; a role reads its own and others' sections before acting.
- **DH2-MEM-002** THE SYSTEM SHALL enforce an outcome embargo: any retrieval of past dossiers or lessons for a decision at time T returns only facts whose `known_at ≤ T`.
- **DH2-MEM-003** THE SYSTEM SHALL classify every lesson with a status in `{hypothesis, validated, retired}`; only `validated` lessons (those tied to a passed gate id) may be injected into a trading-path prompt.
- **DH2-MEM-004** THE SYSTEM SHALL store lessons alongside verbatim evidence (the raw inputs and outputs they were derived from), never in place of it.
- **DH2-MEM-005** THE SYSTEM SHALL keep reference memory (cost model, instrument rules, gates, regulatory facts) read-only to agents; changes go through PRs.
- **DH2-MEM-006** THE SYSTEM SHALL run a nightly consolidation job that prunes or decays lessons past their validity window, and SHALL never delete evidence.
- **DH2-MEM-007** THE SYSTEM SHALL version every memory write (who, when, prior hash) and support point-in-time reads.

### 7.4 Research (RSH)

- **DH2-RSH-001** WHEN a backtest, replay or audit starts, THE SYSTEM SHALL first record a trial row containing hypothesis, universe, window, parameters, holdout flag, code SHA and the pre-registration id; a run without a trial row SHALL fail.
- **DH2-RSH-002** THE SYSTEM SHALL report, beside every Sharpe or expectancy, the Deflated Sharpe at the experiment's trial count N, the aggregation depth k, the Probabilistic Sharpe, and the Minimum Track Record Length.
- **DH2-RSH-003** THE SYSTEM SHALL require every pre-registration to be committed to the repository before the trial runs, and SHALL reject a trial whose parameters differ from its pre-registration without a new registration id.
- **DH2-RSH-004** THE SYSTEM SHALL use point-in-time universes, delisting-inclusive price histories and per-instrument cost models in every backtest.
- **DH2-RSH-005** THE SYSTEM SHALL provide a zero-alpha calibration: each research skill can rerun its pipeline on shuffled or synthetic zero-alpha data and report the distribution of best-of-N Sharpes for comparison.
- **DH2-RSH-006** WHEN a sleeve promotion is proposed, THE SYSTEM SHALL route it to the Validation Reviewer, whose structured verdict (accept, request holdout, reject with reason enum) is required before the gate can be evaluated.
- **DH2-RSH-007** THE SYSTEM SHALL maintain a hypothesis backlog fed by the Post-Trade Reviewer, the Market Intelligence Analyst and the Principal, with each item carrying source, date and disposition.
- **DH2-RSH-008** WHERE an LLM is used to generate features (catalyst enums, regime labels), THE SYSTEM SHALL evaluate the feature against a no-feature baseline on the same trades before it is enabled in any sleeve.

### 7.5 Risk and policy (RSK)

- **DH2-RSK-001** THE SYSTEM SHALL evaluate every trade intent against a policy-as-code rule set before submission; each rule has an id, and denials record the rule id on the dossier.
- **DH2-RSK-002** THE SYSTEM SHALL enforce, in code: single-stock exposure ≤ 15 % of desk equity, sector exposure ≤ 30 %, sleeve risk per trade ≤ the governor's current value, sleeve concurrency caps, desk daily loss cap, trading-hours window, blacklist, product rules, and margin availability. `[NC-2: initial desk daily loss cap; proposed 2 %]`
- **DH2-RSK-003** THE SYSTEM SHALL run a sleeve governor after each accounting close that applies, in order: drawdown reduction/pause, volatility targeting, fractional Kelly cap, decay pause, clamp; and a desk governor that engages the soft kill at the desk drawdown limit.
- **DH2-RSK-004** THE SYSTEM SHALL provide three kill levels (sleeve pause, desk flat-and-halt, gateway cancel-all-and-disconnect) invokable by the Principal, the Risk Officer (levels 1–2) and automatically by the governor (level 2), and SHALL drill all three on every release.
- **DH2-RSK-005** THE SYSTEM SHALL compute realised cost per R per sleeve weekly and SHALL pause any sleeve whose gross expectancy over the trailing window is below twice its realised cost.
- **DH2-RSK-006** THE SYSTEM SHALL size every position from the sleeve's allocated capital and risk fraction, never from account cash, and SHALL cap quantity by margin and freeze limits.
- **DH2-RSK-007** THE SYSTEM SHALL NOT allow any agent tool to change a governor threshold, a policy rule, or a sleeve's allocated capital; these change only through PRs with Principal approval.

### 7.6 Execution (EXE)

- **DH2-EXE-001** THE SYSTEM SHALL implement order placement, modification, cancellation, bracket management, square-off and reconciliation as deterministic code with no language-model call in the path.
- **DH2-EXE-002** THE SYSTEM SHALL persist an order intent with a unique client tag before any broker HTTP call and SHALL treat a timeout or non-4xx failure as "unknown" until the order book has been polled by tag for at least two minutes.
- **DH2-EXE-003** THE SYSTEM SHALL treat the broker order book as the source of truth and reconcile on every postback, on WebSocket reconnect, and every 60 seconds during market hours.
- **DH2-EXE-004** THE SYSTEM SHALL enforce an order-action rate below 10 per second per exchange segment and below the broker's per-minute and per-day limits with a token bucket that counts placements, modifications, cancellations and rejections.
- **DH2-EXE-005** THE SYSTEM SHALL egress order traffic only from the whitelisted static IP and SHALL halt order flow and alert when the observed egress IP differs.
- **DH2-EXE-006** THE SYSTEM SHALL manage intraday (MIS) brackets with system-side stop and target orders and a local watchdog, and positional (CNC/NRML) brackets with two-leg GTT plus a daily verification.
- **DH2-EXE-007** THE SYSTEM SHALL flatten all MIS positions by 15:15 IST with verification against broker positions, ahead of the broker's auto square-off.
- **DH2-EXE-008** WHEN a `TokenException` or an authentication failure occurs, THE SYSTEM SHALL halt new entries, keep managing exits with cached state, and notify the Principal; it SHALL NOT attempt automated login.
- **DH2-EXE-009** THE SYSTEM SHALL support paper and live environments with identical code paths, where paper fills come from the simulation kernel with honest limit semantics.
- **DH2-EXE-010** THE SYSTEM SHALL record reference price, reference time, fill price, fill time and spread at decision time on every order.

### 7.7 Data (DAT)

- **DH2-DAT-001** THE SYSTEM SHALL ingest Kite WebSocket ticks in `full` mode (5-level depth) for the active universe and persist bid/ask snapshots at decision times.
- **DH2-DAT-002** THE SYSTEM SHALL maintain 1-minute, 15-minute and daily bars for the research universe (NIFTY-500 liquid names plus index futures), importing v1's existing bar history rather than re-downloading it.
- **DH2-DAT-003** THE SYSTEM SHALL maintain a point-in-time universe table (constituents and liquidity rank as of each date) and a delisting table.
- **DH2-DAT-004** THE SYSTEM SHALL refresh the instrument master daily before 08:45 IST and store lot sizes, freeze quantities, expiry calendars and holidays as data.
- **DH2-DAT-005** THE SYSTEM SHALL ingest NSE corporate announcements, results calendar and corporate actions daily and expose them with `published_at` timestamps for embargo-safe use.
- **DH2-DAT-006** THE SYSTEM SHALL test every agent-visible feature for degeneracy (constant, stale beyond tolerance, or structurally biased by time of day) in CI and at runtime; a degenerate feature SHALL be withheld from prompts and alerted.
- **DH2-DAT-007** THE SYSTEM SHALL store research data as columnar files (Parquet) queried by DuckDB and transactional state in PostgreSQL.

### 7.8 Operations (OPS)

- **DH2-OPS-001** THE SYSTEM SHALL run the daily shift schedule in `operations.md` from a durable scheduler that records each shift run and resumes from the last completed step after a crash.
- **DH2-OPS-002** THE SYSTEM SHALL deliver a daily desk journal and a weekly digest to the Principal containing: sleeve status, expectancy in R, cost per R, drawdown vs limit, DSR/MTRL progress, LLM spend, incidents, pending approvals.
- **DH2-OPS-003** THE SYSTEM SHALL provide an Operations Engineer role with runbooks as skills for: morning checklist, token freshness, data-quality checks, feed stalls, reconciliation mismatches, deploy verification, and incident write-ups.
- **DH2-OPS-004** WHEN a health check fails, THE SYSTEM SHALL execute the deterministic remediation in the runbook first and invoke the Operations Engineer only for diagnosis or when remediation fails.
- **DH2-OPS-005** THE SYSTEM SHALL deploy only CI-built images tagged by release; no source, no hot-patching, and configuration only through the declared environment file.

### 7.9 Compliance (CMP)

- **DH2-CMP-001** THE SYSTEM SHALL keep audit records (orders, fills, decisions, agent invocations, policy outcomes) for at least five years with tamper evidence (hash chain).
- **DH2-CMP-002** THE SYSTEM SHALL encode market-hour, product, square-off, expiry and lot rules as versioned data with an effective-from date, updated by the Compliance Auditor via PR when circulars change.
- **DH2-CMP-003** THE SYSTEM SHALL run a weekly compliance audit (OPS histogram, static IP, token handling, retention, rule versions) whose report is part of the weekly digest.
- **DH2-CMP-004** THE SYSTEM SHALL log every trade decision with its reasoning references so that a regulator or the Principal can reconstruct why an order was placed.

### 7.10 Observability (OBS)

- **DH2-OBS-001** THE SYSTEM SHALL emit traces for every shift, agent invocation, tool call and order with correlation ids linking dossier, trial and shift.
- **DH2-OBS-002** THE SYSTEM SHALL expose metrics for: feed freshness, reconciliation lag, policy denials by rule, OPS usage, LLM cost by role, expectancy and cost per R by sleeve, governor actions.
- **DH2-OBS-003** THE SYSTEM SHALL alert the Principal channel on: kill-switch engagement, token failure, feed stall > 5 minutes in market hours, reconciliation mismatch, budget exhaustion, and any policy denial of an exit order.

### 7.11 LLM cost (COST)

- **DH2-COST-001** THE SYSTEM SHALL enforce a per-shift budget and a daily desk budget on agent sessions via the runtime's budget controls, and SHALL stop the shift gracefully at the limit. `[NC-3: daily budget; proposed USD 25/day, research shift USD 10]`
- **DH2-COST-002** THE SYSTEM SHALL route work to the cheapest adequate model tier per role as declared in the role definition, and SHALL cache stable prompt prefixes.
- **DH2-COST-003** THE SYSTEM SHALL record cost per invocation and per dossier, and report cost per trade and cost per trial in the weekly digest.

### 7.12 Development (DEV)

- **DH2-DEV-001** THE SYSTEM SHALL be developed as feature specs under `specs/NNN-<feature>/` with `spec.md`, `plan.md`, `tasks.md` and contracts, each requirement traceable to tests.
- **DH2-DEV-002** THE SYSTEM SHALL gate merges on: ruff, mypy --strict, unit tests with coverage floors (engine execution/accounting/policy ≥ 90 %, other new modules ≥ 85 %), integration tests on a real PostgreSQL, skill evals, and the kill-switch drill for release tags.
- **DH2-DEV-003** THE SYSTEM SHALL keep acceptance scenarios in specs in Given/When/Then form and SHALL generate agent eval tasks from the scenarios that involve a role.
- **DH2-DEV-004** THE SYSTEM SHALL enforce, with pre-tool-use hooks in the developer and runtime harnesses, that no agent session can read broker secrets, write to the production environment file, or call broker order endpoints.

## 8. Acceptance scenarios (platform level)

**S1 — A candidate becomes a paper trade with a full dossier.**
Given sleeve `mom_core` is active with a risk budget, When its signal engine emits a candidate at 09:35 IST, Then a dossier exists in `candidate` with engine-computed levels; the Trade Manager is invoked with only categorical context; on `take`, the engine computes quantity and places a paper order with a persisted tag; on fill, the dossier is `open` with reference and fill prices; and every step has a transition log entry with correlation ids.

**S2 — The veto is measured.**
Given 30 % of candidates are shadow-executed regardless of veto, When the weekly review runs, Then the digest shows the veto arm's expectancy minus the shadow arm's with a t-statistic and sample sizes, and the Trade Manager's veto stays enabled only while the gate criteria hold.

**S3 — A research result without a ledger row is impossible.**
Given the Quant Researcher invokes the backtest skill without a pre-registration id, When the script runs, Then it exits non-zero before loading data and the shift log records the refusal.

**S4 — Outcome embargo.**
Given a dossier closed on 2026-10-03 with a lesson written on 2026-10-04, When the Trade Manager recalls similar trades for a decision timestamped 2026-10-03 10:00, Then the lesson is not returned and the dossier is returned without its outcome fields.

**S5 — Governor pauses a sleeve.**
Given sleeve `sip_orb` has a drawdown of 6.2 % against a pause threshold of 6 %, When the accounting close runs, Then the sleeve status is `paused`, the reason is `dd_pause`, a Principal alert is sent, existing positions keep their brackets, and no new candidates are generated for that sleeve.

**S6 — Broker timeout does not duplicate.**
Given an order placement HTTP call times out, When the OMS handles it, Then no retry is sent until the order book has been polled by tag for two minutes, and the dossier shows `submitted` with `ack_state=unknown` during that window.

**S7 — Kill drill on release.**
Given a release tag is pushed, When CI runs, Then it executes the three-level kill drill against a paper environment and blocks the release on any failure.

**S8 — Agent cannot touch money.**
Given any agent session, When it attempts a Bash command or tool call matching broker order endpoints, the production environment file, or secrets paths, Then the pre-tool-use hook denies it, the denial is logged with the role and shift, and the shift continues.

**S9 — The Principal's only daily job.**
Given a trading day, When the Operations Engineer's morning checklist finds no valid token at 08:30 IST, Then the Principal receives one reminder with the login link, the desk stays in `awaiting_login`, and after login the checklist completes without further human action.

**S10 — Promotion is adversarial.**
Given the Quant Researcher proposes promoting a sleeve from harness to paper, When the Validation Reviewer runs, Then its structured verdict lists leakage, survivorship, cost and multiple-testing checks with pass/fail each, and a `request_holdout` verdict creates a new pre-registration with an untouched window before any gate evaluation.

## 9. Gate register (adopted from v1 EDGE spec, amended)

| Gate | Decides | Criteria (summary; normative detail in `research.md`) |
|---|---|---|
| G0 | hypothesis → pre-registered trial | Backlog item has source, falsifiable statement, universe, window, cost model, kill criteria |
| G1 | harness → paper (positional sleeve) | Survivorship-free net alpha > 0 in ≥ 4 of 5 years; DSR > 0.5 at ledger N; drawdown accepted in writing |
| G2 | harness → paper (intraday/swing sleeve) | Net expR > 0 in every holdout window; pooled t > 2.5; n ≥ 300; cost_R ≤ 0.10; filtered beats unfiltered where a filter is the thesis |
| G3 | paper → keep | ≥ 100 trades (or ≥ 6 rebalances) across ≥ 2 regimes; net expR > 0, t > 1; median cost_R ≤ 0.5 × gross expR; bracket exits ≥ 95 % |
| G4 | enable an LLM feature | with-arm minus without-arm > 0.03R, t > 2 on the difference, ≥ 300 trades each |
| G5 | any sleeve → real capital | All of: G3 held; sleeve DSR > 0.5; governor never bypassed; kill drill passed on current release; ≥ 3 sleeves at G3 across ≥ 2 horizons; portfolio DSR > 0; Principal signature; initial allocation ≤ min(₹100,000, 10 % of paper capital) |
| G6 | keep a validated lesson | Lesson's implied rule improves expectancy on a pre-registered holdout; otherwise `retired` |

## 10. Glossary

| Term | Meaning |
|---|---|
| Sleeve | A named, independently accounted strategy with its own status, capital, risk fraction and gates |
| Dossier | The durable per-trade entity with state, engine data, per-role memory sections and evidence |
| Candidate | An engine-generated trade opportunity with computed levels, before vetting |
| Intent | A sized, priced, policy-checked order request |
| R | Rupees at risk at entry: `qty × |entry_reference − stop|`; R-multiple = net P&L / R |
| cost_R | Realised (statutory + slippage) cost per trade divided by R |
| DSR / PSR / MTRL | Deflated Sharpe, Probabilistic Sharpe, Minimum Track Record Length (Bailey & López de Prado) |
| N, k | Trial count under an experiment; number of winners blended into a reported result |
| Outcome embargo | Retrieval rule: only facts known at the decision time are visible |
| Shift | A scheduled unit of agent work with a budget and a run record |
| Principal | The human owner |
