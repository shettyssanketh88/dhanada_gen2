# Execution layer — the deterministic engine

*Companion to `spec.md` (DH2-EXE-*, DH2-RSK-*, DH2-DAT-*). This is the "static scripts" half of the design: everything here is versioned, unit-tested Python with no language-model call. Constraints come from `docs/research/2026-09-20-kite-sebi-execution-constraints.md`; lessons F7, F10, F12, F13 from `docs/lessons-from-v1.md`.*

## 1. Components

| Component | Responsibility | Exposed to agents as |
|---|---|---|
| **Broker adapter** (`engine/broker/kite/`) | Kite Connect REST + WebSocket; one token; static-IP check; rate limiting; instrument master | nothing directly (read-only Kite MCP is a separate sidecar for agents) |
| **Market data** (`engine/data/`) | Tick ingest (`full` mode), bar building (1m/15m/1d), REST quote fallback, historical backfill, NSE feeds (bhavcopy, announcements, corporate actions, results calendar), instrument/rule tables | `data:*` read tools |
| **Feature store** (`engine/features/`) | ATR, RVOL by session window, breadth/dispersion/vol z-scores, regime inputs, liquidity class; degeneracy tests | `features:read` |
| **Signal engines** (`engine/sleeves/<sleeve_id>/`) | Pure functions from features to `Candidate`s; one module per sleeve; parameters from versioned config | none (candidates appear as dossiers) |
| **Policy gate** (`engine/policy/`) | Rule set evaluated on every `TradeIntent` and on exits; rule ids; deny reasons | `engine:read_policy_outcomes` |
| **OMS** (`engine/oms/`) | Order state machine, tags, reconciliation, brackets, square-off watchdog, OPS governor | `engine:accept_candidate`, `engine:veto_candidate`, `engine:request_close` (via Trade Manager tools only) |
| **Accounting** (`engine/accounting/`) | Positions, cash, costs, slippage, R, sleeve metrics, daily rollups | `engine:read_sleeves`, `engine:read_risk` |
| **Simulation kernel** (`engine/sim/`) | First-touch fills, honest limits, cost model; used by research, replay and paper | `research:run_backtest` (sandboxed) |
| **Governor** (`engine/governor/`) | Sleeve and desk rules (drawdown, vol target, Kelly, decay, clamp) | `engine:feasible_allocations`, `engine:set_allocation_tier` (bounded) |
| **Kill switch** (`engine/kill/`) | Three levels; drill | `engine:pause_sleeve`, `engine:kill(level ≤ 2)` |
| **Dossier store** (`engine/dossiers/`) | State machine, sections, evidence, projection | `dossiers:*` |
| **Scheduler** (`engine/scheduler/`) | Shift runs, durable steps, agent session launcher, budgets | `ops:*` |

## 2. Broker adapter

### 2.1 Session and token

- One Kite Connect app key. One access token per day, obtained by the Principal's manual login (request token → session exchange in the engine). Stored in the secret store; agents never see it (constitution VIII.4).
- The WebSocket ticker and every REST call use the same token. No second consumer, no sidecar login (v1 lesson: token collision).
- `TokenException` or HTTP 403 on any call: set `broker_state = token_invalid`, halt entries, continue exits from cached state, notify Principal. No automated re-login (Zerodha terms).
- Token freshness check every 5 minutes in market hours; the morning checklist verifies a token exists before 08:45 IST.

### 2.2 Static IP

- Order endpoints must egress from the whitelisted IP (SEBI, 1 Apr 2026). The adapter checks the observed egress IP at startup and hourly; mismatch → `broker_state = ip_mismatch`, entries halted, alert.
- Data endpoints are unaffected; the ticker keeps running.

### 2.3 Rate limiting

- Token bucket on order actions (place, modify, cancel; rejections count): 8 per second sustained, burst 8, per exchange segment; hard ceiling 9 (below the 10 OPS SEBI threshold so the generic Algo-ID path applies). Minute (400) and day (5,000) counters as secondary limits.
- Quote REST ≤ 1 request/s (500 instruments per call); historical ≤ 3 request/s with per-interval span caps.
- HTTP 429 is back-pressure: the action is queued and retried; it is never interpreted as "not placed".

### 2.4 Instrument master and rule data

- Instrument CSV fetched daily at 08:30 IST; stored with `as_of`.
- Rule tables (`rules/`): lot sizes, freeze quantities, expiry calendar, holidays, square-off times, cost rates — each row with `effective_from`. Loaded by date, never hard-coded.

## 3. Order lifecycle

### 3.1 Intent → order

```
Candidate ──(Trade Manager: take)──► TradeIntent (engine computes qty, prices, product, bracket)
        ──(policy gate)──► allowed | denied(rule_id)
        ──(OMS)──► OrderIntent persisted {client_tag, idempotency_key, state=created}
        ──► HTTP place ──► state=sent ──► ack(order_id) | unknown
```

- `client_tag`: ≤ 20 alphanumeric chars, base36 of the order intent id; persisted **before** the HTTP call.
- Idempotency: `(dossier_id, leg, attempt)` unique; the OMS never places a second order for the same leg while any prior attempt is `sent` or `unknown`.

### 3.2 Unknown-state handling

- A timeout or any non-4xx failure sets `state=unknown`. The OMS polls `/orders` filtered by `client_tag` every 10 s for ≥ 120 s. If found → adopt `order_id` and continue; if not found after the window → `state=failed`, a new attempt may be created.
- A 4xx with a broker rejection message → `state=rejected` immediately, with the message stored.

### 3.3 Reconciliation

- Sources, in order of authority: `/orders` and `/orders/:id/trades` (truth) > WebSocket order postbacks (hints) > HTTP postbacks (hints).
- Reconcile: on every postback for our tag, on WebSocket reconnect, every 60 s during market hours, and at 15:35 IST end-of-day. Positions are reconciled against `/positions` at the same cadence; mismatches raise `reconciliation_mismatch` (Risk Officer + alert).

### 3.4 Order types

- Entries: marketable limit (limit at reference ± buffer from the sleeve config), validity DAY or TTL as configured, `market_protection = -1` if a market order is ever used. Non-marketable limits are allowed only for sleeves whose thesis is passive entry, and paper fills honour them (no fill unless touched).
- Exits: stop as SL-L with trigger and limit computed by code; target as limit; square-off as marketable limit with `market_protection = -1` fallback.
- Slicing: quantities above freeze limits are sliced (`autoslice` or manual) as separate legs sharing the dossier.

### 3.5 Brackets

| Product | Mechanism | Verification |
|---|---|---|
| MIS (intraday) | System-side SL and target orders placed immediately after entry fill; local watchdog re-places a missing leg within 5 s; OCO handled by the OMS (cancel the other on fill) | Every 60 s reconcile; missing bracket for > 30 s → `bracket_missing` incident and immediate re-placement |
| CNC / NRML (positional) | Two-leg GTT (OCO) placed after fill; daily verification that the GTT exists and matches the dossier; GTT triggers a LIMIT order, so a fallback marketable limit is placed if the GTT-triggered order is rejected or unfilled beyond a tolerance | Daily 09:20 and 15:00 IST checks; ≤ 500 active GTTs enforced |

Trailing stops and time stops are **off** by default and can be enabled per sleeve only by a passed gate (three independent v1 audits found they subtract value).

### 3.6 Square-off watchdog

- MIS flatten starts 15:15 IST (equity and F&O), verifies via `/positions` at 15:20 and 15:23, and escalates to level-2 kill semantics (cancel-all, marketable exits) if any MIS quantity remains at 15:23. The broker's own square-off (15:25 equity, 15:26 F&O) is a backstop, never the plan.
- Intraday-to-overnight carries (a gated sleeve rule) convert the product before 15:00 IST; the conversion is an engine action recorded on the dossier.

## 4. Policy gate (policy-as-code)

Rules are pure functions `rule(ctx) -> Denial | None` with stable ids, evaluated in order; all denials are recorded (not just the first). Initial rule set:

| Rule id | Check |
|---|---|
| `mkt.hours` | Entry only 09:15–15:00 IST (configurable per sleeve; exits exempt) |
| `mkt.holiday` | Exchange holiday table |
| `mkt.product_allowed` | Product allowed for sleeve and instrument |
| `mkt.circuit_proximity` | Price within X % of circuit limit → deny entry |
| `risk.single_stock` | Post-trade single-name exposure ≤ 15 % of desk equity |
| `risk.sector` | Sector exposure ≤ 30 % |
| `risk.sleeve_risk` | Trade R ≤ sleeve allocated capital × current risk fraction |
| `risk.sleeve_concurrency` | Open positions in sleeve < cap |
| `risk.desk_daily_loss` | Desk realised + unrealised loss today < cap → else no entries |
| `risk.margin` | `/margins/basket` shows sufficient margin with headroom |
| `risk.freeze_qty` | Quantity per leg ≤ freeze limit (else sliced upstream) |
| `sebi.ops` | Token bucket has capacity (secondary guard) |
| `sebi.static_ip` | `broker_state != ip_mismatch` |
| `sebi.token` | `broker_state == ok` for entries |
| `desk.kill_state` | No kill level engaged (exits always allowed) |
| `desk.blacklist` | Symbol not on blacklist (regulatory, ASM/GSM stages configurable) |
| `sleeve.status` | Sleeve `active` or `reduced` |
| `sleeve.one_per_symbol` | No open position or pending entry in the symbol across sleeves |

Thresholds live in `rules/policy.yaml` with `effective_from`; changing them is a PR with Principal approval (DH2-RSK-007). Exits are evaluated only against `mkt.holiday`, `sebi.*` and technical checks; a policy denial of an exit is itself an alert (DH2-OBS-003).

## 5. Accounting

- Positions and cash per (account, environment, sleeve). Fills apply atomically with costs computed from the rule tables by product and date.
- On every order: `reference_price`, `reference_at` (decision time), best bid/ask at decision time, fill price and time, `slippage_inr` (signed).
- On close: `gross_pnl_inr`, `costs_inr`, `slippage_inr` (both legs, positive = cost), `risk_inr = qty × |entry_reference − stop_at_entry|`, `r_multiple = net / risk`.
- Daily rollup per sleeve: trades, wins, gross, costs, slippage, net, sum R, equity start, daily return, peak, drawdown. Idempotent upsert.
- Weekly cost calibration: median and mean `cost_R` per sleeve, statutory vs slippage split, spread statistics, edge-to-cost ratio; feeds DH2-RSK-005.

## 6. Simulation kernel

One kernel for research, replay and paper:

- Bar-driven (1-minute for intraday sleeves, daily for positional) with first-touch fills: an entry limit fills when the bar's range touches it; stop and target on the same bar resolve as a **loss** (conservative tie).
- Cost model by product and date from the rule tables; slippage model calibrated from live spread samples (default: half-spread + impact parameter per liquidity class).
- Honest limits: non-marketable limits do not fill until touched; marketable limits fill at the touch price plus modelled slippage.
- Deterministic given inputs and seed; outputs a trade list with the same schema as live accounting.
- Paper environment = the kernel driven by live bars, producing fills into the same accounting tables.

## 7. Governor

Adopted from v1 WP5.1, deterministic, run after the accounting close (16:10 IST) and never intra-session:

1. Drawdown: ≥ `dd_pause_pct` → `paused`; ≥ `dd_reduce_pct` → `reduced` (risk × 0.5); recovery below half the reduce threshold → `active`. `halted` is operator-only.
2. Volatility targeting: scale risk by `min(1, vol_target / realised_20d_annualised)`.
3. Fractional Kelly cap with ≥ 30 trades; `f* ≤ 0` → `paused (kelly_negative)`.
4. Decay: mean of last N R-multiples < `decay_fraction × validated_exp_r` → `paused (decay)`.
5. Clamp to `[min_risk, max_risk]`.
6. Desk: drawdown across active sleeves ≥ `desk_halt_pct` → soft kill (level 2), Principal clears.

The Portfolio Manager chooses an allocation **tier** per sleeve from the feasible set the governor computes (`full | half | quarter | off`); it cannot exceed the governor's ceiling.

## 8. Kill switch

| Level | Action | Who |
|---|---|---|
| 1 `sleeve_pause` | No new entries for the sleeve; brackets continue | Risk Officer, governor, Principal |
| 2 `desk_halt` | Cancel all open entry orders; flatten all positions with marketable limits; no entries until cleared | Risk Officer, governor (desk drawdown), Principal |
| 3 `gateway_disconnect` | Cancel all orders, flatten, disconnect broker session, disable scheduler | Principal only |

Drill on every release in the paper environment: engage → verify no entries and full flatten → disengage; a failed drill blocks the release. The drill must have `try/finally` semantics so a failure never leaves the switch engaged (v1 bug).

## 9. Data ingest

- Ticker: `full` mode, ≤ 3,000 instruments per connection, up to 3 connections; ticks outside 09:15–15:30 IST dropped by tick timestamp; reconnect with backoff; a stall > 60 s triggers REST quote fallback and a `feed_stall` incident at 5 minutes.
- Bars: built from ticks with real volume; 15-minute and daily bars derived; v1's historical bars (12.9M 1-minute rows, 507k daily rows) imported once via Parquet export.
- NSE feeds: bhavcopy nightly; announcements every 15 minutes in market hours and hourly otherwise, stored with `published_at`; results calendar and corporate actions daily.
- Point-in-time universe: constituents from NSE inclusion/exclusion archives to 2020 and niftyindices monthly reports after; liquidity rank by 20-day turnover as of each rebalance date; delisting table maintained.
- Storage: Parquet partitioned by symbol/month for bars (DuckDB queries); PostgreSQL for everything transactional.

## 10. Engine tools exposed to agents (MCP server `dhanada-engine`)

All tools are typed (JSON schema), annotated (`readOnlyHint`, `destructiveHint`), scoped per role by the runtime, and logged. Write tools take reason enums, never numbers.

| Tool | Scope | Effect |
|---|---|---|
| `engine:read_sleeves`, `engine:read_risk`, `engine:read_policy_outcomes`, `engine:read_health` | read | Structured snapshots |
| `dossiers:get`, `dossiers:list`, `dossiers:write_section` | per role | Own section only |
| `engine:accept_candidate(dossier_id, verdict)` | Trade Manager | Moves `candidate → vetted`; engine then builds the intent |
| `engine:veto_candidate(dossier_id, reason)` | Trade Manager | Moves to `vetoed`; shadow arm may still execute |
| `engine:request_close(dossier_id, reason)` | Trade Manager | Allowed only for enumerated reasons in the sleeve's gate |
| `engine:pause_sleeve(sleeve_id, reason)` | Risk Officer | Level-1 kill |
| `engine:kill(level ≤ 2, reason)` | Risk Officer | Level-2 kill |
| `engine:feasible_allocations()`, `engine:set_allocation_tier(sleeve_id, tier, review_id)` | Portfolio Manager | Bounded by governor |
| `features:read`, `data:*`, `ledger:*`, `research:*`, `memory:*`, `ops:*`, `notify:principal` | as per role | see `skills.md` |

A separate read-only Kite MCP sidecar (`zerodha/kite-mcp-server` with all order and GTT tools excluded) may be exposed to the Operations Engineer and Risk Officer for independent verification of positions and orders; it uses its own Kite app key and login so it cannot invalidate the engine's token. `[NC-4: whether to fund a second Kite app key for the sidecar]`

## 11. Acceptance scenarios

- **E1 Tag before call.** Given an intent, When placement starts, Then an `OrderIntent` row with `client_tag` exists before the HTTP request is issued (verified by a fault-injection test that kills the process between persist and send, and by the recovery poll finding the order).
- **E2 Unknown then adopt.** Given a placement timeout, When the order appears in `/orders` with our tag 40 s later, Then the OMS adopts it and no duplicate is sent.
- **E3 OPS ceiling.** Given 20 immediate order actions, When the bucket allows 8/s, Then ≤ 9 reach the broker in any second and the rest queue.
- **E4 Bracket watchdog.** Given an MIS entry fill with a failed stop placement, When 5 s pass, Then the stop is re-placed and an incident is recorded.
- **E5 GTT verification.** Given a CNC position whose GTT was deleted externally, When the 09:20 check runs, Then the GTT is re-created and the dossier logs it.
- **E6 IP mismatch.** Given the observed egress IP differs, When the hourly check runs, Then `broker_state = ip_mismatch`, entries are denied by `sebi.static_ip`, exits still work, and the Principal is alerted.
- **E7 Same-bar tie is a loss.** Given a simulated bar touching both stop and target, When the kernel resolves it, Then the trade is recorded as a stop-out.
- **E8 No LLM in the path.** Given static analysis of `engine/`, When CI runs, Then no import of any LLM client is present (structural test).
