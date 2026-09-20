# Dhanada v2 — Platform Specification (WHAT and WHY)

| Field | Value |
|---|---|
| Spec id | `000-platform` |
| Status | Draft v2.0 for Principal review (supersedes v1.0 of the same day) |
| Date | 2026-09-20 |
| Governed by | `.specify/memory/constitution.md` v2.0.0 |
| Inputs | `docs/lessons-from-v1.md`, `docs/research/*` (4 reports), the Principal's direction of 2026-09-20: all decisions are agent-driven |
| Companion documents | `plan.md`, `roles.md`, `memory.md`, `skills.md`, `tools-and-rails.md`, `learning.md`, `operations.md`, `tasks.md` |

Requirement ids are `DH2-<AREA>-<nnn>`. Areas: FIRM (organisation), DSK (desks and trades), MEM (memory), LRN (learning and research), RAIL (rails), TOOL (tools and execution service), DAT (data), OPS (operations), CMP (compliance), OBS (observability), COST (LLM cost), DEV (development). EARS phrasing. `[NC]` marks a clarification for the Principal.

---

## 1. Vision

Dhanada v2 is an **AI-run investment firm** for Indian markets, trading through Zerodha Kite. Agents hold every role that decides: they form views, build theses, plan and size trades, manage positions, review each other, allocate capital among desks, research new strategies, coach one another, and run operations. Code provides instruments (calculators, data, backtests), executes repeatable actions (orders, accounting), keeps memory, and enforces the short list of rails the owner wrote in the Investment Policy Statement.

The firm is organised as **desks**. Each desk is a small team of agents with a mandate (horizon, universe, style), a capital allocation and its own playbook. Desks compete for capital under a **Chief Investment Officer** agent. A **Research Lab** proposes new desks and improvements; a **Coach** measures every agent's decisions and improves their playbooks; a **Risk Office** reviews plans and watches the book. Every trade is a **dossier** that each role writes into and reads from, so that every agent continues its own work on that trade across sessions, days and restarts.

## 2. Goals

| # | Goal | Measure |
|---|---|---|
| G1 | The firm makes money after realised costs | Firm-level net expectancy > 0 and Deflated Sharpe > 0 on paper across ≥ 3 desks before real capital; then live |
| G2 | The firm is agentic end to end | No trading, allocation, promotion or exit decision is made by code; each is attributable to a role with reasoning |
| G3 | The firm learns | Every closed trade reviewed; every agent's calibration tracked; playbooks revised with evidence; measurable improvement in decision scores quarter over quarter |
| G4 | Breadth | ≥ 3 desks across ≥ 2 horizons on paper within 3 months; ≥ 5 within 12 months of first capital |
| G5 | Operational autonomy | Only the daily broker login, the IPS and rail changes involve the Principal |
| G6 | Honest measurement | Calibration, counterfactual baselines and trial counts on every performance claim |
| G7 | Bounded LLM spend | Firm budget enforced by the runtime and allocated by the CIO among desks |

## 3. Non-goals (v2.0)

- Multi-tenant SaaS, mobile apps, public API.
- Automated broker login (Zerodha terms).
- Kubernetes (single-VM Docker Compose retained).
- Any decision rule hard-coded outside the IPS rails.

## 4. The Investment Policy Statement (IPS) and rails

The Principal writes `ips.yaml` (`[NC-1: initial values]`), the only place where the owner's limits live:

| Field | Meaning |
|---|---|
| `total_capital_inr`, `paper_capital_inr` | Capital the firm may deploy; paper capital for desks in incubation |
| `max_daily_loss_pct`, `max_drawdown_pct` | Firm-level rails; breach → firm flat-and-halt |
| `max_single_name_pct`, `max_sector_pct` | Exposure rails |
| `permitted_products`, `permitted_segments` | e.g. equity CNC/MIS, index futures; options defined-risk only |
| `permitted_horizons` | e.g. intraday, swing, positional |
| `prohibited` | e.g. naked option selling, automated login, sub-5-minute holds |
| `max_desks_live`, `max_capital_per_desk_pct` | Concentration rails on the firm structure |
| `llm_budget_usd_per_day` | Firm-wide spend rail |

Rails (`tools-and-rails.md` §8) = IPS limits + regulator/broker mechanics + kill switch. Everything else is an agent decision.

## 5. The firm

```
                                   Principal (IPS, login, kill L3)
                                                │
   ┌────────────────────────────────────────────┴───────────────────────────────────────────┐
   │ FIRM LEADERSHIP                                                                         │
   │  CIO ── allocates capital and LLM budget among desks; charters / retires desks          │
   │  Risk Office ── reviews plans, watches the book, pauses/halts within the IPS            │
   │  Coach ── scores every agent's decisions, revises playbooks, runs evals                 │
   └─────────────┬──────────────────────────────┬───────────────────────────┬───────────────┘
                 │                              │                           │
   ┌─────────────▼───────────┐   ┌──────────────▼──────────────┐   ┌────────▼──────────────┐
   │ DESKS (N, chartered)    │   │ RESEARCH LAB                │   │ OPERATIONS            │
   │  Analysts (tech,        │   │  Quant Researcher           │   │  Operations Engineer  │
   │   catalyst, flow)       │   │  Data Steward               │   │  Compliance Auditor   │
   │  Strategist             │   │  Validation Reviewer        │   │  Skill Engineer       │
   │  Trader                 │   │  Desk Designer              │   │                       │
   │  Position Manager       │   └─────────────────────────────┘   └───────────────────────┘
   │  Desk Reviewer          │
   └─────────────────────────┘
   ═══════════════════════════ typed tools (MCP) ═══════════════════════════════════════════
   EXECUTION SERVICE & INSTRUMENTS (code): orders · reconciliation · accounting · market data ·
   calculators · backtest engine · trial ledger · dossier & memory stores · scheduler · rails
```

## 6. The trade dossier state machine (agent-owned)

| State | Owner (decides the exit) | Meaning |
|---|---|---|
| `idea` | Analyst | A view with evidence, filed to the desk |
| `thesis` | Strategist | Idea developed into a thesis: direction, horizon, catalyst, invalidation, conviction |
| `plan` | Trader | Instrument, entry, stop, target, size, timing, order type, cost per R, expected R and probability (the Trader's forecast, for calibration) |
| `risk_review` | Risk Office | Approve, modify (with the Trader's agreement), or reject with reasons |
| `working` | Trader | Orders placed by the execution tool; fills tracked |
| `open` | Position Manager | Position held; adjustments, scale, carry, exit are its decisions |
| `closed` | Execution service (facts) → Desk Reviewer | Both legs reconciled; accounting written |
| `reviewed` | Desk Reviewer + Coach | Per-role scores, lessons proposed |
| `archived` | — | Immutable |

Side exits: `dropped` (any owner, with reason), `rejected` (Risk Office), `expired`, `killed` (rail). Each role writes its own section of the dossier in its state and can be re-invoked on events while it owns the trade.

## 7. Requirements

### 7.1 Firm (FIRM)

- **DH2-FIRM-001** THE SYSTEM SHALL define every role as a versioned role definition (`agents/<role>/ROLE.md`: mandate, decision rights, model, tools, skills, memory scopes, budget) and SHALL run each role as its own agent session with its own memory.
- **DH2-FIRM-002** THE SYSTEM SHALL represent desks as chartered entities (`desks/<desk_id>/CHARTER.md` written by the CIO: mandate, universe, horizon, capital, LLM budget, team, playbook reference, review cadence) and SHALL allow the CIO to charter, resize, pause and retire desks through tools.
- **DH2-FIRM-003** THE SYSTEM SHALL record every decision (trading or organisational) with role, role version, reasoning, instruments used, expected outcome, and correlation ids, so that any decision can be replayed and scored.
- **DH2-FIRM-004** WHEN a role's structured output fails validation, THE SYSTEM SHALL return the validation errors to the same session for correction up to two times, then record `REVIEW` and notify the Coach; it SHALL NOT substitute a default decision.
- **DH2-FIRM-005** THE SYSTEM SHALL let roles convene: a desk meeting, a risk conference and an investment committee are multi-agent sessions with an agenda, a chair, recorded positions and a decision, capped in rounds by the chair's role definition.
- **DH2-FIRM-006** THE SYSTEM SHALL inform the Principal of every organisational decision (charter, allocation, promotion, retirement, playbook change) through the journal and digest, and SHALL require Principal approval only for IPS, rails and constitution changes.

### 7.2 Desks and trades (DSK)

- **DH2-DSK-001** THE SYSTEM SHALL implement the dossier state machine in §6 with a single owning role per state, a complete transition log, and per-role sections.
- **DH2-DSK-002** WHEN a Trader writes a plan, THE SYSTEM SHALL require it to reference the calculator outputs it used (volatility, structure, liquidity, cost, sizing) and to state expected R, probability of success and cost per R; the Trader's numbers are the plan.
- **DH2-DSK-003** THE SYSTEM SHALL validate a plan only for type, rails (IPS, product, session, exposure, margin, freeze limits) and internal consistency (stop on the correct side, size within the desk's capital); any other objection is the Risk Office's decision.
- **DH2-DSK-004** WHEN the Risk Office reviews a plan, THE SYSTEM SHALL accept `approve`, `modify` (proposed changes, requiring the Trader's acceptance or a chaired resolution) or `reject`, each with reasons, and SHALL record the review on the dossier.
- **DH2-DSK-005** WHILE a dossier is `open`, THE SYSTEM SHALL route every relevant event (fill, price milestone the Position Manager subscribed to, catalyst on the symbol, data anomaly, risk notice, session milestone) to the Position Manager, whose decision (hold, adjust stop/target, scale, carry, exit) is executed by tools.
- **DH2-DSK-006** THE SYSTEM SHALL let the Position Manager subscribe to price and time triggers so that it is invoked when they occur; between invocations the execution service holds the working stop and target orders the Position Manager last set.
- **DH2-DSK-007** THE SYSTEM SHALL compute counterfactual baselines for every closed trade (no-trade, plan-as-filed with mechanical bracket, un-modified plan where the Risk Office modified it) and attach them to the dossier for the reviewers.
- **DH2-DSK-008** THE SYSTEM SHALL allow a desk to define and revise its playbook (markdown plus skills) and SHALL version it; every dossier records the playbook version in force.
- **DH2-DSK-009** THE SYSTEM SHALL provide a paper environment with identical tools where new desks incubate, and SHALL let the CIO move a desk between paper and live within the IPS.

### 7.3 Memory (MEM)

- **DH2-MEM-001** THE SYSTEM SHALL give every role its own long-term memory (playbook, lessons, calibration record, notes) and every dossier a section per role; roles read before deciding and write after.
- **DH2-MEM-002** THE SYSTEM SHALL enforce time-aware retrieval: a decision at time T sees only items with `known_at ≤ T`.
- **DH2-MEM-003** THE SYSTEM SHALL store lessons with evidence references and a status (`proposed`, `adopted`, `retired`) decided by the Coach, and SHALL include adopted lessons in the owning role's context.
- **DH2-MEM-004** THE SYSTEM SHALL provide desk memory (shared by the desk team) and firm memory (shared by all), with write rights per role definition.
- **DH2-MEM-005** THE SYSTEM SHALL version every memory write and support point-in-time reads and replay.
- **DH2-MEM-006** THE SYSTEM SHALL run a nightly consolidation in which each role curates its own memory (index, decay, merges) with the Coach reviewing changes.

### 7.4 Learning and research (LRN)

- **DH2-LRN-001** THE SYSTEM SHALL score every decision after the fact: calibration (stated probability vs outcome), process adherence to the role's playbook, and counterfactual comparison; scores are written to the deciding role's calibration record.
- **DH2-LRN-002** THE SYSTEM SHALL provide the Coach with per-role, per-desk decision statistics with sample sizes and confidence intervals, and SHALL let the Coach revise playbooks, propose skill changes and adjust role prompts through versioned changes with evals.
- **DH2-LRN-003** THE SYSTEM SHALL let the Research Lab run backtests, replays and factor studies through a sandboxed engine, recording each run in the trial ledger with its pre-registration and the trial count N; the ledger tool SHALL require an experiment id and hypothesis on every run.
- **DH2-LRN-004** THE SYSTEM SHALL let the Desk Designer propose a desk charter and playbook to the CIO with evidence, and SHALL let the Validation Reviewer attach an adversarial review before the investment committee decides.
- **DH2-LRN-005** THE SYSTEM SHALL let the Skill Engineer create and modify skills and calculators through PRs that run the skill's evals and the test suite; a second agent reviews; the Principal is informed.
- **DH2-LRN-006** THE SYSTEM SHALL maintain point-in-time data, delisting-inclusive histories and masked identifiers for any LLM-touched historical study.

### 7.5 Rails (RAIL)

- **DH2-RAIL-001** THE SYSTEM SHALL enforce, in code, only: IPS limits, regulator rules (order rate < 10 per second per segment, static IP, product/session rules, retention), broker mechanics, and the kill switch; the rail list is `rails/RAILS.md` and changes only by the Principal.
- **DH2-RAIL-002** WHEN a rail blocks an action, THE SYSTEM SHALL record the event on the dossier or shift, notify the acting role and the Risk Office, and include it in the Coach's next review.
- **DH2-RAIL-003** THE SYSTEM SHALL provide kill levels: L1 desk pause (Risk Office, CIO), L2 firm flat-and-halt (Risk Office, IPS breach), L3 gateway disconnect (Principal); all drilled on every release.

### 7.6 Tools and execution service (TOOL)

- **DH2-TOOL-001** THE SYSTEM SHALL execute orders (place, modify, cancel, brackets, square-off, reconciliation) as deterministic code behind typed tools, with tag-before-call persistence, unknown-state polling, order-book-as-truth reconciliation and an order-rate governor.
- **DH2-TOOL-002** THE SYSTEM SHALL provide calculators as tools: volatility (ATR, realised vol), structure (swing levels, ranges, VWAP distance), liquidity (spread, depth, turnover class), cost (per product and date, cost per R for a given stop), sizing (risk-based quantity for a stated R), margin, correlation/exposure, and any calculator an agent commissions from the Skill Engineer.
- **DH2-TOOL-003** THE SYSTEM SHALL provide a backtest and replay engine with first-touch fills, honest limits and realised-cost models, usable by agents on paper and research data and returning the same accounting schema as live.
- **DH2-TOOL-004** THE SYSTEM SHALL record on every order the reference price and time, bid/ask at decision, fill price and time, and on every trade the costs, slippage, `risk_inr` and `r_multiple`.
- **DH2-TOOL-005** THE SYSTEM SHALL keep broker credentials in the execution service's secret store; no tool returns them; agent sessions cannot reach broker endpoints directly.
- **DH2-TOOL-006** WHEN authentication fails or the egress IP mismatches, THE SYSTEM SHALL halt new orders, keep protective orders working, notify the Principal and the Risk Office, and SHALL NOT attempt automated login.

### 7.7 Data (DAT)

- **DH2-DAT-001** THE SYSTEM SHALL ingest Kite ticks in `full` mode with depth, build 1-minute, 15-minute and daily bars, and persist bid/ask at decision times.
- **DH2-DAT-002** THE SYSTEM SHALL import v1's bar history, maintain daily bars for the research universe, a point-in-time universe table, delisting and corporate-action tables, and the instrument master with lot sizes, freeze quantities, expiries and holidays as dated data.
- **DH2-DAT-003** THE SYSTEM SHALL ingest NSE announcements, results calendar and corporate actions with `published_at` and expose them to agents with that timestamp.
- **DH2-DAT-004** THE SYSTEM SHALL test agent-visible features for degeneracy and SHALL tell the agent when a feature is withheld and why.
- **DH2-DAT-005** THE SYSTEM SHALL store research data as Parquet queried by DuckDB and transactional data in PostgreSQL.

### 7.8 Operations (OPS)

- **DH2-OPS-001** THE SYSTEM SHALL run a durable scheduler that triggers shifts and events, records runs, resumes after crashes, and lets desks set their own meeting and review cadence within firm hours.
- **DH2-OPS-002** THE SYSTEM SHALL deliver a daily journal and weekly digest to the Principal: desks, decisions of note, decision-quality scores, expectancy and cost per R, drawdown vs IPS, LLM spend, incidents, organisational changes.
- **DH2-OPS-003** THE SYSTEM SHALL provide an Operations Engineer with runbooks-as-skills, a Compliance Auditor with weekly audits, and deterministic health checks that remediate first and escalate second.
- **DH2-OPS-004** THE SYSTEM SHALL deploy only CI-built images; no source on the VM; configuration only through the declared environment file.

### 7.9 Compliance (CMP)

- **DH2-CMP-001** THE SYSTEM SHALL keep tamper-evident audit records (orders, fills, decisions, invocations, rail events) for at least five years.
- **DH2-CMP-002** THE SYSTEM SHALL encode market rules as dated data maintained by the Compliance Auditor via PR.
- **DH2-CMP-003** THE SYSTEM SHALL reconstruct, for any order, the chain of decisions and reasoning that produced it.

### 7.10 Observability (OBS), cost (COST), development (DEV)

- **DH2-OBS-001** Traces for every shift, session, tool call and order with correlation ids; metrics for feed freshness, reconciliation lag, rail events, order-rate usage, LLM cost by role and desk, decision scores by role, expectancy and cost per R by desk.
- **DH2-OBS-002** Alerts to the Principal on kill events, token failure, feed stall > 5 minutes, reconciliation mismatch, IPS proximity (80 % of any limit), budget exhaustion.
- **DH2-COST-001** Per-session budgets, per-desk daily budgets allocated by the CIO within the IPS budget; graceful stop at limits; cost per decision and per trade reported weekly.
- **DH2-COST-002** Model routing per role as declared in role definitions; stable prompt prefixes cached.
- **DH2-DEV-001** Feature specs with requirement ids; CI (ruff, mypy --strict, unit ≥ 90 % for execution/accounting/rails, ≥ 85 % elsewhere, integration on PostgreSQL, skill evals, kill drill on releases).
- **DH2-DEV-002** Pre-tool-use hooks in developer and runtime harnesses deny access to secrets, the production environment file and broker endpoints.

## 8. Acceptance scenarios (platform level)

**S1 — A desk takes a trade end to end, every decision by an agent.** Given the Positional Desk is chartered on paper, When the Technical Analyst files an idea at 09:40, Then the Strategist writes a thesis, the Trader writes a plan citing calculator outputs with expected R and probability, the Risk Office approves, the execution tool places the order with a persisted tag, the Position Manager's stop and target are working, and the dossier shows one owner per state with reasoning at each.

**S2 — The Position Manager decides the exit and is scored.** Given an open dossier, When the price crosses a milestone the Position Manager subscribed to, Then it is invoked, decides (hold/adjust/exit) with reasoning, the tool executes, and after close the dossier carries the mechanical-bracket counterfactual and the Position Manager's calibration record is updated.

**S3 — The Risk Office modifies a plan.** Given a plan sized beyond the Risk Office's comfort but inside the IPS, When it returns `modify`, Then the Trader accepts or a chaired resolution occurs, both positions are recorded, and the eventual outcome is scored against both versions.

**S4 — A rail fires and is explained.** Given a plan that would breach `max_single_name_pct`, When the Trader submits it, Then the tool rejects with the rail id, the dossier records it, the Risk Office is notified, and the Coach's next review includes it.

**S5 — Time-aware memory.** Given a lesson learned on D+1 from a trade closed on D, When any role decides at D 10:00 in replay, Then the lesson is absent.

**S6 — The CIO reallocates.** Given the monthly investment committee, When desk statistics are presented with sample sizes, Then the CIO's allocation decision with reasoning is recorded, applied by tool within the IPS, and reported to the Principal.

**S7 — The Coach improves a playbook.** Given a Trader whose stated probabilities are systematically overconfident over ≥ 50 trades, When the Coach runs its weekly review, Then it revises the Trader's playbook (versioned), adds an eval case, and the next sessions load the new version.

**S8 — The Skill Engineer ships a calculator.** Given a Trader requests a new liquidity-impact calculator, When the Skill Engineer opens a PR with tests and evals and the Validation Reviewer approves, Then CI merges it and the Trader's next session can call it; the Principal sees it in the digest.

**S9 — Broker timeout does not duplicate.** As in every version: tag persisted before the call; unknown state polled for two minutes; no duplicate.

**S10 — The Principal's only daily job.** Login reminder once; desk `awaiting_login`; arms automatically afterwards.

## 9. Glossary

| Term | Meaning |
|---|---|
| IPS | Investment Policy Statement: the Principal's limits and permissions |
| Rail | A limit enforced by code from the IPS, regulation or broker mechanics |
| Desk | A chartered team of agents with mandate, capital and playbook |
| Dossier | The durable per-trade entity with state, per-role sections and evidence |
| Playbook | A desk's or role's written procedure, versioned, revised by agents |
| Calibration record | Per-role history of stated expectations vs outcomes |
| Counterfactual baseline | Code-computed alternative outcome for a trade (no-trade, mechanical bracket, unmodified plan) |
| R, cost_R, DSR, MTRL, N, k | As in `learning.md` |
