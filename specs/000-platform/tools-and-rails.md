# Tools, execution service and rails

*Companion to `spec.md` v2.0 (DH2-TOOL-*, DH2-RAIL-*, DH2-DAT-*). This is the code half of the firm: it executes what agents decide, computes what agents ask, keeps the books, and enforces the owner's rails. It decides nothing. Constraints from `docs/research/2026-09-20-kite-sebi-execution-constraints.md`.*

## 1. Division of labour

| Agents decide | Code does |
|---|---|
| What to trade, direction, horizon | Fetch and serve data; build bars and features; test feature health |
| Entry, stop, target, size, timing, order type | Compute calculator outputs on request; validate types and rails; place, modify, cancel, track and reconcile orders |
| Adjust, scale, carry, exit | Keep the last stop/target working between agent invocations; fire subscribed triggers |
| Capital allocation, charters, promotions | Apply allocations; keep accounts and sleeve books; compute statistics |
| Lessons, playbook changes, skills | Store, version, index, retrieve memory; run evals and tests in CI |
| Experiment design and interpretation | Run backtests/replays; record trials with N and k |
| Risk approval, pauses | Enforce IPS/regulatory rails; kill switch mechanics |

## 2. Execution service (`engine/exec/`)

### 2.1 Broker session
- One Kite Connect app key; one daily token from the Principal's manual login (request token exchanged by the service). Stored in the secret store; no tool returns it.
- Ticker and REST share the token; no second consumer.
- `TokenException`/403 → `broker_state = token_invalid`: new orders refused by rail `broker.token`, protective orders remain, Principal and Risk Office notified. No automated login.

### 2.2 Static IP and rate
- Egress IP checked at start and hourly; mismatch → `broker_state = ip_mismatch`, rail `sebi.static_ip` blocks new orders.
- Order-action token bucket: 8/s sustained, burst 8, ceiling 9 per exchange segment (below SEBI's 10); 400/min and 5,000/day secondary counters; 429 = back-pressure, never "not placed".

### 2.3 Order lifecycle
```
OrderAction (agent) ─► type + rail validation ─► OrderIntent persisted {client_tag} ─► HTTP ─► ack | unknown
```
- `client_tag` (≤ 20 alphanumerics) persisted before the call; idempotency key `(dossier_id, leg, attempt)`; no second attempt while one is `sent`/`unknown`.
- Unknown (timeout, non-4xx): poll `/orders` by tag every 10 s for ≥ 120 s; adopt if found; else `failed`, agent informed and may act again.
- Order book is truth; reconcile on postbacks (WebSocket and HTTP, treated as hints), on reconnect, every 60 s in market hours, and at 15:35 IST.
- MARKET/SL-M always carry `market_protection = -1`; the Trader chooses the order type; the tool applies the mechanics.
- Slicing above freeze limits automatic (`autoslice`) with legs on the same dossier.

### 2.4 Working protective orders
- After a fill, the service places the stop and target the Trader's plan specified (or the Position Manager's latest) as broker orders: MIS → SL-L and limit legs with a local OCO watchdog (re-place a missing leg within 5 s); CNC/NRML → two-leg GTT with daily verification and a fallback marketable exit if a triggered GTT order fails.
- The Position Manager changes them through `exec:modify`; between its invocations the last instructions stand. There is no code-side trailing or time stop; if a Position Manager wants one, it subscribes to triggers and decides at each.

### 2.5 Square-off
- MIS flatten by the service starts 15:15 IST unless the Position Manager has already exited or converted (carry). Verification at 15:20 and 15:23; escalation to L2 mechanics at 15:23 if MIS quantity remains. The broker's 15:25/15:26 square-off is a backstop only.
- Product conversion (`exec:convert_product`) is a Position Manager decision executed before 15:00 IST (rail `broker.conversion_window`).

### 2.6 Subscriptions and events
`subscribe:price(dossier_id, level, side)`, `subscribe:time(dossier_id, at)`; events delivered to the owning role via the scheduler with a per-event deadline. Also delivered without subscription: fill, partial fill, rejection, catalyst tag on the symbol, data anomaly, risk notice, session milestones, rail events.

## 3. Calculators (`engine/calc/`, exposed as `calc:*`)

| Tool | Returns |
|---|---|
| `calc:volatility(symbol, window, interval)` | ATR (daily, 15m, 1m), realised vol, noise band estimates |
| `calc:structure(symbol, as_of)` | swing highs/lows, day range, opening range, VWAP and distance, gap, multi-day ranges |
| `calc:liquidity(symbol, as_of)` | spread (bps), depth at 5 levels, 20-day turnover, liquidity class, impact estimate for a notional |
| `calc:cost(product, notional, stop_pct, as_of)` | statutory round trip, modelled slippage, cost per R for the given stop |
| `calc:size(risk_inr, entry, stop, product, symbol)` | quantity for a stated R; margin required; freeze-limit slices |
| `calc:exposure(desk_id?, symbol?, sector?)` | current and pro-forma exposures vs IPS |
| `calc:correlation(symbols|desks, window)` | correlation matrix |
| `calc:event_window(symbol, as_of)` | upcoming results/corporate actions/expiry within horizon |
| `calc:regime_inputs(as_of)` | breadth, dispersion, vol z-scores (the agent labels the regime) |
| `calc:stats(series)` | expectancy, t, Sharpe, DSR/PSR/MTRL given N and k |

Calculators are pure, tested, versioned; every result carries `calc_version` and inputs so plans can be replayed. Agents may commission new calculators from the Skill Engineer.

## 4. Backtest and replay engine (`engine/sim/`)

- One engine for research, replay and paper: bar-driven, first-touch fills, same-bar stop/target tie counted as a loss, honest limits, cost and slippage models from rule tables and live calibration.
- Agents drive it in two modes: **rule mode** (a playbook expressed as code by the Skill Engineer, for large-sample studies) and **agent mode** (the desk's roles replayed over history with masked identifiers and time-aware memory, for evaluating agentic playbooks on a sampled set of days — cost-bounded).
- Every run opens a ledger trial (`ledger:open` requires `experiment_id`, `hypothesis`, pre-registration reference) and closes it with results, N and k.
- Paper environment = the engine driven by live bars, writing to the same accounting tables as live.

## 5. Accounting (`engine/accounting/`)

Positions, cash, costs by product and date, slippage against reference prices, `risk_inr`, `r_multiple`, desk daily rollups (equity, return, peak, drawdown), firm rollups, weekly realised cost per R per desk. Counterfactual baselines computed at close: no-trade, plan-as-filed with mechanical bracket, unmodified plan (if the Risk Office modified), and any baseline a desk's playbook registers.

## 6. Market data (`engine/data/`)

Ticker in `full` mode (≤ 3,000 instruments per connection, 3 connections), ticks outside 09:15–15:30 IST dropped by timestamp, REST quote fallback, bars 1m/15m/1d with real volume, v1 history imported to Parquet, NSE bhavcopy nightly, announcements every 15 minutes in market hours with `published_at`, results calendar and corporate actions daily, point-in-time universe (NSE inclusion/exclusion archives to 2020, niftyindices reports after), delisting table, instrument master 08:30 IST, rule tables with `effective_from`. Feature health tests run in CI and at runtime; a withheld feature is reported to the requesting agent with the reason.

## 7. Firm and desk tools (`firm:*`, `desks:*`, `dossiers:*`, `memory:*`, `ledger:*`, `learning:*`, `ops:*`)

All typed, annotated (`readOnlyHint`, `destructiveHint`), scoped per role by a per-session capability token, logged to the audit chain. Write tools accept the agent's decision object and reasons; validation is type + rails + consistency only.

## 8. Rails (`rails/RAILS.md`, `rails/ips.yaml`, `rails/market_rules/`)

The complete list of what code enforces. Grows only by the Principal's PR.

| Rail id | Source | Check |
|---|---|---|
| `ips.max_daily_loss` | IPS | Firm realised + unrealised loss today ≥ limit → L2 flat-and-halt |
| `ips.max_drawdown` | IPS | Firm drawdown from peak ≥ limit → L2 |
| `ips.single_name` | IPS | Pro-forma single-name exposure > limit → reject order |
| `ips.sector` | IPS | Pro-forma sector exposure > limit → reject |
| `ips.products`, `ips.segments`, `ips.horizons` | IPS | Not permitted → reject |
| `ips.prohibited` | IPS | Listed activity (e.g., naked option sale) → reject |
| `ips.capital_per_desk` | IPS | Allocation above cap → reject allocation |
| `ips.llm_budget` | IPS | Firm daily spend cap → stop non-essential sessions |
| `sebi.order_rate` | Regulation | Token bucket as §2.2 |
| `sebi.static_ip` | Regulation | Egress mismatch → no new orders |
| `sebi.session` | Exchange | Orders only in session; product-specific windows |
| `sebi.retention` | Regulation | Audit chain retention ≥ 5 years |
| `broker.token` | Broker | Invalid token → no new orders |
| `broker.freeze_qty`, `broker.lot_size`, `broker.conversion_window`, `broker.gtt_limits`, `broker.market_protection` | Broker mechanics | Enforced on order construction |
| `desk.capital` | Charter (CIO) | Plan size within desk capital; desk paused → no new plans |
| `kill.L1/L2/L3` | Kill switch | As spec DH2-RAIL-003 |

A rail event is recorded on the dossier or shift, sent to the acting role and the Risk Office, and included in the Coach's review. Rails never modify an agent's decision silently; they reject and explain.

## 9. Kill switch

L1 desk pause (Risk Office, CIO): no new plans for the desk; positions managed as usual. L2 firm flat-and-halt (Risk Office; IPS rails): cancel entries, exit all positions with marketable limits, no new plans until the Risk Office and Principal clear. L3 gateway disconnect (Principal): cancel, flatten, disconnect, scheduler off. Drill on every release in paper with `try/finally` semantics.

## 10. Acceptance scenarios

- **T1** Tag persisted before the HTTP call (fault-injection test kills the process between persist and send; recovery poll finds the order).
- **T2** Timeout then adopt: no duplicate.
- **T3** Order-rate ceiling: ≤ 9 actions per second reach the broker.
- **T4** Missing MIS leg re-placed within 5 s.
- **T5** GTT deleted externally is re-created at the 09:20 check.
- **T6** IP mismatch blocks new orders, keeps exits, alerts.
- **T7** Same-bar tie is a loss in the sim engine.
- **T8** No LLM client importable from `engine/` (structural test).
- **T9** A Position Manager's last stop stands across a service restart.
- **T10** A rail rejection carries the rail id, is on the dossier, and reaches the Risk Office.
