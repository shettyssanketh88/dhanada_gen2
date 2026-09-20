# Tools, execution service, watch modes and rails

*Companion to `spec.md` v2.1 (DH2-TOOL-*, DH2-EXEC-*, DH2-RAIL-*, DH2-DAT-*). The code half of the firm: it executes what agents decide, computes what agents ask, evaluates the Analyst's crisp conditions on the tape, keeps the books, and enforces the owner's rails. It decides nothing. Constraints from `docs/research/2026-09-20-kite-sebi-execution-constraints.md`.*

## 1. Division of labour

| Agents decide | Code does |
|---|---|
| Which stocks (Scanner); which data (Ingestor) | Fetch, store, serve data; compute features every minute; test feature health |
| Strategies, conditions, buy/stop/sell prices, sizes, priorities (Analyst) | Validate type, rails and consistency; version and store books |
| Approve/modify/reject (Risk Officer) | Record; auto-apply the Risk Officer's own auto-approval rules |
| Which strategy applies now, how to work the order, when to escalate (Execution Agent) | Rule Watch evaluates crisp conditions per tick; place/modify/cancel/track/reconcile orders; keep protective orders working; fire subscriptions |
| Retire/adjust/add strategies (Recalibration Agent) | Strategy-family statistics; counterfactuals per book version and watch mode |
| Capital, charters, watch-mode governance (CIO) | Apply allocations; keep accounts; statistics |
| Lessons, templates, playbooks, skills (Coach, Skill Engineer) | Store, version, index, retrieve memory; run evals and tests |
| Experiments and their interpretation (Lab) | Run backtests/replays; record trials with N and k |
| Pauses and halts within the IPS (Risk Officer) | Enforce IPS/regulatory rails; kill switch mechanics |

## 2. Feature service (`engine/features/`)

Computes, every minute for every watched stock (and every tick for the few tick-level features), the **named features** of the expression language:

| Family | Examples |
|---|---|
| Trend | `trend_1m`, `trend_5m`, `trend_15m`, `trend_1d` ∈ {up, down, sideways} by a documented method the Analyst can inspect; `higher_highs_15m`, `lower_lows_15m` |
| Volume | `volume_ratio_paced` (session-time-paced vs 20-day same-window), `rvol_first_5m`, `volume_profile_poc` |
| Levels | `close_1m`, `last_price`, `day_high`, `day_low`, `open`, `prev_close`, `opening_range_high/low`, `swing_high_15m`, `swing_low_15m`, `vwap`, `vwap_distance_pct`, `pullback_depth` |
| Volatility | `atr_1m`, `atr_15m`, `atr_1d`, `noise_band` |
| Market | `nifty_change_pct`, `nifty_break_day_low`, `breadth_pct`, `dispersion_z`, `vix_change` |
| Events | `results_within_days`, `expiry_today`, `announcement_flag`, `circuit_proximity_pct` |
| Time | `time_in(a, b)`, `minutes_since_open`, `minutes_to_close` |
| Position | `no_position_open(strategy_id)`, `minutes_since_fill(strategy_id)` |

Each feature has a definition file, unit tests, a health test (not constant, not stale, not structurally biased by time of day) and a version. The Skill Engineer adds features the Analyst asks for. The Analyst's calculators use the same service.

**Expression language**: boolean combinations (`AND`, `OR`, `NOT`), comparisons, arithmetic, `crosses_above(x, level)`, `crosses_below`, `touches(x, level, tolerance)`, `time_in`, and named features. Parsed and type-checked at book validation; evaluated deterministically by Rule Watch.

## 3. Watch modes (`engine/watch/` and the Execution Agent's skill)

### 3.1 Rule Watch (deterministic evaluator)
- Loads the governing book version; compiles each strategy's crisp `applies_when`, validity, priority and exclusivity; subscribes to the stock's feature stream.
- On every tick/minute: evaluates conditions; on a **match** (with priority/exclusivity resolved), an **order event**, an **escalation condition** (invalidation firing, conflict unresolved, feature withheld, judgment-only strategy pending, position facts inconsistent), or a **milestone** (open, carry window, square-off), it invokes the Execution Agent session with the event and context.
- Judgment conditions are marked `judgment_only` and handed to Agent Watch (or escalated if Agent Watch is not running for the desk).
- Reloads a new version within 5 s of approval; diffs protective orders and asks the Execution Agent to apply the diff.

### 3.2 Agent Watch (continuous session)
- One long-running Execution Agent session per stock (or per small group the CIO sets), fed 1-minute bar digests (OHLCV, features, position facts) and notable tick events (level touches, volume bursts, order events) by the feature service.
- The agent evaluates crisp and judgment conditions itself, acts through `exec:*`, records reasoning per action, and manages context with context editing and compaction; its cost per stock-day is recorded.
- Concurrency cap per desk set by the CIO within the IPS budget (`DH2-COST-003`).

### 3.3 Governing and shadow
- The CIO sets per desk which mode **governs** (places orders) and which **shadows** (paper-only; records would-be actions with timestamps and would-be fills from the sim engine).
- Both produce `ExecutionLog` entries; code computes fidelity (actions vs book), latency (condition met → order sent), slippage, cost, and outcome deltas per mode. Reports go to the Recalibration Agent weekly and to the investment committee (`learning.md` §5, ADR-008).

## 4. Execution service (`engine/exec/`)

Broker session (one token, manual login, no auto-login), static IP check, order-rate bucket (8/s sustained, ceiling 9), order lifecycle with tag-before-call and unknown-state polling, order book as truth with reconciliation on postbacks/reconnect/60 s/EOD, `market_protection = -1` on any market order, slicing above freeze limits, protective orders (MIS: SL-L + limit legs with OCO watchdog; CNC/NRML: two-leg GTT with daily verification and fallback), square-off from 15:15 IST with verification, product conversion before 15:00 IST, subscriptions and events — all as in v2.0 (`docs/ADR/ADR-005`, research constraints). The Execution Agent is the only agent role with `exec:*` tools; every `exec:*` call carries `book_version` and `strategy_id`.

## 5. Calculators (`calc:*`)

Volatility, structure, liquidity, cost (round trip and cost per R for a stop), size (quantity for a stated R, margin, slices), exposure, correlation, event window, regime inputs, stats (expectancy, t, Sharpe, DSR/PSR/MTRL with N and k). Pure, versioned, tested; results carry inputs and `calc_version`.

## 6. Books tools (`books:*`)

| Tool | Caller | Effect |
|---|---|---|
| `books:draft(symbol, period, book)` | Senior Analyst | Validates (type, rails, consistency, expression parse); stores version n |
| `books:revise(symbol, changes, rationale)` | Senior Analyst | New version; records which revision requests it answers |
| `books:review(book_version, per_strategy_decisions)` | Risk Officer | Records review; applies auto-approval rules the Risk Officer defined |
| `books:load(symbol)` | Execution Agent / watch | Governing version |
| `books:request_revision(symbol, strategy_id, change, evidence)` | Recalibration Agent | Queues a request to the Analyst |
| `books:retire(symbol, strategy_id, reason)` | Senior Analyst | Marks retired in a new version |

## 7. Sim/replay engine, accounting, market data

As v2.0 (`engine/sim/`, `engine/accounting/`, `engine/data/`), with: counterfactuals per **book version** (each version that governed during a trade is replayed over the trade's bars) and per **watch mode** (shadow actions simulated with first-touch fills); strategy-family statistics aggregated nightly.

## 8. Firm and desk tools

`firm:*`, `desks:*`, `dossiers:*`, `memory:*`, `ledger:*`, `learning:*`, `ops:*`, `watch:*`, `compliance:*` (preclear, decide, hold, dispose), `rules:*` (read, propose), `treasury:*` (read_funds/margins/collateral, plan, request_reduce), `recon:*` (run, read, dispose), `tca:*` (read_fills, report) — typed, annotated, scoped per role by a per-session capability token, logged to the audit chain. Write tools accept the agent's decision object and reasons; validation is type + rails + consistency only.

## 9. Rails (`rails/RAILS.md`, `rails/ips.yaml`, `rails/market_rules/`)

Unchanged from v2.0: `ips.*` (daily loss, drawdown, single name, sector, products, segments, horizons, prohibited, capital per desk, LLM budget), `sebi.*` (order rate, static IP, session, retention), `broker.*` (token, freeze qty, lot size, conversion window, GTT limits, market protection), `desk.capital`, `kill.L1/L2/L3`, plus (v2.2, `compliance.md`): `compliance.*` (ip, ops, tag, session, instrument, surveillance_status, product, margin, self_match, ban_list, expiry_exposure, clearance_conditions, provenance, hold) evaluated synchronously from the Compliance Officers' rule catalogue A1–A19/B1–B10 and their clearance conditions and holds; `broker.terms_confirmed` (live orders blocked until the Principal records Zerodha's written confirmation, NC-7); `books.clean` (new book approvals held while a reconciliation break is unresolved). A rail event is recorded on the dossier or shift, sent to the acting role and the Risk Officer, and included in the Coach's review. Rails reject and explain; they never alter a decision silently.

## 10. Kill switch

L1 desk pause (Risk Officer, CIO); L2 firm flat-and-halt (Risk Officer; IPS rails); L3 gateway disconnect (Principal). Drilled on every release in paper with `try/finally` semantics.

## 11. Acceptance scenarios

- **T1–T6** Execution mechanics as v2.0 (tag-before-call, unknown-then-adopt, rate ceiling, MIS leg re-placement, GTT re-creation, IP mismatch).
- **T7** Same-bar tie is a loss in the sim engine.
- **T8** No LLM client importable from `engine/`.
- **T9** The last protective orders stand across a service restart and across an `escalated` state.
- **T10** A rail rejection carries the rail id and reaches the Risk Officer.
- **T11** Rule Watch reloads a new book version within 5 s and produces the protective-order diff.
- **T12** A judgment condition under Rule Watch governance is marked `judgment_only` and handed to Agent Watch or escalated.
- **T13** Shadow mode never places a broker order (structural test on the shadow code path) and records would-be actions with timestamps.
- **T14** An expression with an unknown feature fails book validation with the feature name.
