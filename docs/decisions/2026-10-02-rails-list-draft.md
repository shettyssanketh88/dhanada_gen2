# RAILS — the complete list of what code enforces

*Status: **draft for the Principal**, 2026-10-02. This file is the proposed content of `rails/RAILS.md` (DH2-RAIL-001). It adds no rail: it consolidates the rails already stated in `rails/ips.yaml` v0.2, `rails/broker-confirmation.md`, `specs/000-platform/tools-and-rails.md` §9–10 and `specs/000-platform/compliance.md` §5. It becomes the rail list only when the Principal moves it to `rails/RAILS.md`; from then on it grows only by the Principal's hand (constitution II.2).*

Rules for every rail (constitution II.3, DH2-RAIL-002): a rail rejects and explains with its id; it never alters a decision silently. Every rail event is recorded on the dossier or shift, sent to the acting role and the Risk Officer, and included in the Coach's next review. Anything not listed here is an agent decision.

## 1. IPS rails (`ips.*`) — values in `rails/ips.yaml`

The rail id is `ips.` followed by the key path in `rails/ips.yaml`; the values live only there.

| Rail group | Keys | What is enforced |
|---|---|---|
| `ips.capital` | `live_total_inr`, `live_enabled`, `paper_accounts` | No live order while `live_enabled` is false; capital in use never exceeds the stated totals |
| `ips.go_live_procedure` | all keys | `live_enabled` can be ratified only when every condition holds |
| `ips.capital_thresholds_inr` | all keys | A desk type trades live only at or above its capital threshold |
| `ips.firm_risk` | `max_daily_loss_pct`, `max_drawdown_pct`, `drawdown_restore_steps_pct`, `portfolio_heat_pct`, `target_vol_annual_pct` | Daily loss soft and hard limits; drawdown steps (half risk, halt, to paper); firm and desk heat |
| `ips.desk_risk` | `drawdown_pct`, `risk_per_trade_pct`, `min_risk_per_trade_inr`, `incubation_allocation_pct`, `allocation_ladder_pct`, `max_capital_per_desk_pct`, `intraday_capital_cap_pct` | Per-desk drawdown, risk per trade bounds, allocation caps (also cited as `desk.capital`) |
| `ips.concentration` | `max_single_name_pct`, `max_positions_positional`, `max_sector_pct`, `liquidity.*` | Single-name, sector and liquidity caps |
| `ips.permissions` | `products`, `segments`, `horizons_paper`, `horizons_live`, `desks_max_live` | Only permitted products, segments, horizons and number of live desks |
| `ips.prohibited` | each list entry | Each prohibited activity is rejected |
| `ips.operating_budget` | `llm_budget_usd_per_day`, `agent_watch_max_stocks_per_desk` | Firm LLM budget and Agent Watch concurrency cap (DH2-COST-003) |
| `ips.records` | `retention_years` | Record retention |

## 2. Regulator rails (`sebi.*`)

| Rail id | Constraint |
|---|---|
| `sebi.order_rate` | Order actions stay below 10 per second per exchange segment: token bucket 8/s sustained, hard ceiling 9; secondary cap 400/min (`rails/broker-confirmation.md`) |
| `sebi.session` | Orders only in permitted sessions and products; square-off and conversion windows per `tools-and-rails.md` §4 |
| `sebi.retention` | Tamper-evident records kept for the IPS retention period (DH2-CMP-007) |

## 3. Broker rails (`broker.*`)

| Rail id | Constraint |
|---|---|
| `broker.static_ip` | Every order request egresses from the whitelisted static IP; mismatch → no new orders, protective orders continue, Principal alerted |
| `broker.market_protection` | Every MARKET and SL-M order carries `market_protection` (never 0; default `-1`) |
| `broker.daily_auth` | Token only from the Principal's daily manual OAuth login with 2FA/TOTP; no automated login; without a token the firm is `awaiting_login` |
| `broker.terms_confirmed` | Live orders blocked while false (DH2-CMP-008) |
| `broker.freeze_qty` | Orders above the freeze quantity are sliced, never sent whole |
| `broker.lot_size` | F&O quantities are whole lots |
| `broker.conversion_window` | Product conversion only before 14:45 IST |
| `broker.gtt_limits` | GTT count and validity within the broker's limits |

## 4. Compliance rails (`compliance.*`, DH2-CMP-003)

Evaluated synchronously on every order from the Compliance Officers' rule catalogue (`rails/market_rules/`, rows A1–A19 and B1–B10), their clearance conditions and their holds. The catalogue rows are the officers' by PR; the rail ids below are the Principal's.

`compliance.ip` · `compliance.ops` · `compliance.tag` · `compliance.session` · `compliance.instrument` (lot, freeze, band, LPP, protection) · `compliance.surveillance_status` · `compliance.product` · `compliance.margin` · `compliance.self_match` · `compliance.ban_list` · `compliance.expiry_exposure` · `compliance.clearance_conditions` · `compliance.provenance` · `compliance.hold`

## 5. Books rail

| Rail id | Constraint |
|---|---|
| `books.clean` | New book approvals are held while a reconciliation break is unresolved (DH2-CTL-003) |

## 6. Kill switch (`kill.*`, DH2-RAIL-003)

| Rail id | Level | Who may fire |
|---|---|---|
| `kill.L1` | Desk pause | Risk Officer, CIO |
| `kill.L2` | Firm flat-and-halt | Risk Officer; automatically on an IPS hard breach |
| `kill.L3` | Gateway disconnect | Principal only |

All three are drilled on every release in paper.

## 7. Points for the Principal before ratifying

1. **Static IP id.** `tools-and-rails.md` §9 lists static IP under `sebi.*`; `rails/broker-confirmation.md` names it `broker.static_ip`. This draft follows the broker confirmation.
2. **`rails/health.yaml`.** `plan.md` §3 lists it as a Principal-owned file; nothing else defines it. Either define it or drop the mention.
3. **IPS status.** `rails/ips.yaml` is still `status: proposed` and unsigned; this list has force only once the IPS is ratified.
