# Open items — researched recommendations for the Principal

*2026-09-21. Sources: `docs/research/2026-09-21-ips-limits-and-capital.md`, `docs/research/2026-09-21-regulatory-verification.md`, the LLM budget model (`plan.md` §12 note), `docs/research/2026-09-20-*`. Each item states the recommendation, the evidence, and what the Principal must still supply. Values marked (J) are judgement calls on top of the evidence.*

## Summary

| Item | Recommendation | Status |
|---|---|---|
| NC-1 IPS values | Table in §1; encoded as `rails/ips.yaml` (draft) | Needs the Principal's capital figure and signature |
| NC-2 LLM budget | Lean configuration ≈ USD 15/day for two desks (≈ ₹2.7 lakh/yr); cap set as a rail; see the cost-versus-capital tension in §2 | Principal to choose tier |
| NC-3 second Kite key (read-only sidecar) | **No** for v2.0 | Decided by recommendation unless overridden |
| NC-4 notifications | Telegram (alerts, approvals, kill) + email (journal, digest, records) | Decided by recommendation unless overridden |
| NC-5 first desks | Positional Momentum (weekly books) first; Catalyst/Event Swing second; Intraday Breakout only as a paper-only evaluation desk; Index Futures deferred until capital ≥ ₹30 lakh | Principal to confirm |
| NC-6 Agent Watch concurrency | 3 stocks per desk on 15-minute digests plus event bursts during evaluation; one desk at a time | Decided by recommendation |
| NC-8 catalogue `[verify]` | Resolved from primary text; square-off schedule corrected | Done |
| NC-9 retention | 8 years | Decided by recommendation |

## 1. IPS values (NC-1)

The Principal must state **total capital** and **paper capital**. Every rail below is a percentage so it holds at any size; the desk permissions depend on size.

| Field | ₹25 lakh | ₹50 lakh | ₹1 crore | Why |
|---|---|---|---|---|
| `target_vol_annual_pct` | 10 | 11 | 12 | Vol targeting to ~10 % improves Sharpe and cuts tail severity (Harvey et al. 2018) |
| `max_daily_loss_pct` soft / hard | 1.25 / 2.0 | same | same | 2 % ≈ a 3σ day at 11 % vol; the prop-firm 5 % never binds at this vol |
| `max_drawdown_pct` half-risk / halt / to-paper | 5 / 10 / 15 | same | same | Pod-shop −5/−7.5–10 bands scaled for the firm's lower vol; a Sharpe-0.7 book touches −10 % about one year in three, so −10 % is "stop and review", −15 % is terminal |
| Per-desk drawdown half / stop (of desk allocation) | 6 / 10 | same | same | Millennium-style desk governance |
| Restore steps | at −3 % / −6 % recovery | same | same | Discrete step-ups beat continuous scaling under transaction costs |
| `risk_per_trade_pct` positional / catalyst / intraday | 0.5 / 0.5 / 0.4 | 0.5 / 0.5 / 0.4 | 0.5 / 0.5 / 0.3 | Risk-of-ruin at 1 % vs 2 %; ≤ 0.5 Kelly on estimated edges |
| Portfolio heat firm / desk (sum of open R) | 6 / 3 | same | same | Tharp < 6 % |
| `max_single_name_pct` at cost / hard | 7 / 10 | 7 / 10 | 5 / 10 | SEBI mutual-fund 10 % single-company limit as the prudential reference |
| `max_sector_pct` | 25 | 25 | 25 | SEBI 25 % reference; NIFTY financials > 30 % so it binds for benchmark-like books |
| Permitted desks | Positional + Catalyst | + Index Futures 1 lot (R 0.75 %) | all; futures 2 lots | One NIFTY lot ≈ ₹15.2 lakh notional, ≈ ₹1.72 lakh margin; a 1 % stop = ₹15.2k = 1R only at ≥ ₹20–30 lakh equity (lot granularity binds, not margin) |
| `max_capital_per_desk_pct` / intraday cap | 50 / 0 | 40 / 15 | 35 / 20 | Multi-strategy sleeve practice; intraday capped until 12 months live |
| Incubation allocation | 10 % of equity | 10 | 10 | Paper-to-live ladder: 10 % → 20 % → cap after ≥ 60 sessions and ≥ 30 trades with DSR > 0 |
| Liquidity: min ADV positional / intraday | ₹5 cr / n.a. | ₹5 cr / ₹25 cr | ₹10 cr / ₹50 cr | NSE impact-cost bar; 20 % of ADV sellable per day |
| Order / position vs 20-day ADV | 5 % / 25 % | same | same | SEC/MSCI practice |
| `permitted_products` | equity CNC, MIS; index futures NRML; options defined-risk only | | | |
| `prohibited` | naked or undefined-risk option writing; holds < 5 minutes; ASM/GSM/ESM, T2T, unsolicited-SMS names; stocks with ADV < ₹5 cr or price < ₹50; stock F&O; MIS on non-approved names; adding to losers; any order without a registered stop; gross leverage > 1.0× positional, > 2.0× intraday; any agent override of a rail | | | From the evidence ranking and the compliance catalogue |
| Opex cap per year (infra + data + LLM) | 4 % (₹1 lakh) | 3 % (₹1.5 lakh) | 2 % (₹2 lakh) | Small-shop IT spend; fixed floor ≈ ₹50–65k/yr (Kite Connect + VM) |

**Below ₹25 lakh**: positional desk only (12–15 names at 5–7 %, R 0.5 %); no futures, no intraday; six months of paper with DSR > 0 before live; reassess if net-of-tax-and-opex expectation falls under ~5 %.

Note on the drawdown rail: the previous draft proposed max drawdown 15 % as the only firm rail. The research supports a **three-step** rail (−5 % half risk, −10 % halt, −15 % to paper) because a single terminal rail gives the Risk Officer and CIO no graduated response.

## 2. LLM budget (NC-2) — and an honest tension

The session plan in `operations.md` was costed with Anthropic list prices (Opus 5 $5/$25 per MTok, Sonnet 5 $2/$10, Haiku 4.5 $1/$5; 50 % of input served from cache).

| Configuration | USD/day | ₹/month (21 days) | ₹/year |
|---|---|---|---|
| Full plan as first drafted, 3 desks, Rule Watch only | 35 | 62k | 7.4 lakh |
| Same + Agent Watch on 10 stocks/desk at 1-minute digests | 168 | 3.0 lakh | 35 lakh |
| **Lean**: batched books and reviews, Sonnet for pre-clearance/sweeps, Agent Watch on 3 stocks at 15-minute digests + event bursts — 1 desk | 7 | 13k | 1.5 lakh |
| Lean — 2 desks | 13 | 23k | 2.7 lakh |
| Lean — 3 desks | 19 | 33k | 3.9 lakh |

The risk research recommends LLM spend near **1 % of capital per year** (₹25k at ₹25 lakh; ₹1 lakh at ₹1 crore). The agentic firm cannot run at that level: even the lean single-desk configuration costs ≈ ₹1.5 lakh/yr, which is 6 % of ₹25 lakh, 3 % of ₹50 lakh, 1.5 % of ₹1 crore. Three choices:

1. **Treat year one as R&D.** Budget the paper phase at USD 15/day (≈ ₹2.7 lakh/yr for two lean desks) irrespective of capital, and decide on live scale only after the paper track record exists. Recommended.
2. **Scale capital to the firm.** At ₹1 crore the lean three-desk firm costs ≈ 4 % of capital; at ₹2 crore ≈ 2 %.
3. **Shrink the firm.** One positional desk (weekly books, few sessions) costs ≈ ₹1.5 lakh/yr and is the configuration that fits ₹25–50 lakh.

Proposed rails: `llm_budget_usd_per_day: 15` for the paper phase (firm-wide, CIO allocates), reviewed at the first monthly committee with actual spend; Agent Watch capped at 3 stocks per desk on 15-minute digests (NC-6) until its first evaluation report; Opus reserved for the roles that write or clear books and for the Coach; Sonnet for everything periodic; Haiku for batch classification and consolidation. The cost model assumed 50 % cache hits; the runtime should measure and report the real rate.

## 3. Second Kite key for a read-only sidecar (NC-3): no

The free Kite Connect Personal plan covers orders, positions, holdings and funds without market data, so the money cost is nil. The real cost is a **second daily manual login** (each API key needs its own token) and a second credential to guard. The Books & Records Agent's independence comes from reconciling the internal ledger against the broker's order book and positions, which the engine already reads with the one token; it does not need a separate token to be independent. Decision: no sidecar in v2.0; revisit only if the firm ever runs more than one broker account.

## 4. Notifications (NC-4)

Telegram bot for alerts, login reminders, approvals and kill confirmations (push, sub-second, supports inline actions with a signed one-time code); email for the daily journal, weekly digest, compliance evidence bundles and anything that must be archived. The existing v1 Gmail bot account can be reused for email.

## 5. First desks (NC-5)

| Order | Desk | Book period | Why |
|---|---|---|---|
| 1 | Positional Momentum (mid/small-cap, quality screen, trend overlay) | weekly | Zero delivery brokerage, capital-gains tax rather than slab, fewest orders, tolerant of latency; the only family where v1's research found real edge (+3.3 %/month raw, survivorship-caveated); rank 1 in the evidence table |
| 2 | Catalyst / Event Swing (results, corporate actions, announcements with `published_at`) | weekly with daily check-ins | Uses the Catalyst Analyst and provenance rules; 2–10 day holds where v1's audit showed R:R 2.5–3.0 at identical entries |
| 3 | Intraday Breakout (stocks-in-play, wide ATR stops, one trade per name per day) | session | Paper-only evaluation desk in v2.0: highest cost per R, speculative tax, 70 % base-rate losers; it exists to exercise Rule Watch/Agent Watch and the intraday compliance rails, and is capped at 0–20 % of capital by the IPS |
| later | Index Futures (last-30-minute momentum, trend overlay) | session/weekly | Deferred until equity ≥ ₹30 lakh so one lot ≈ 1R at 0.5 % |

## 6. Agent Watch concurrency (NC-6)

Three stocks per desk on 15-minute digests plus event bursts (≈ USD 2/desk-day on Sonnet), one desk at a time in the first month, alternating governance by session so both modes accumulate governing evidence. Raise only on the strength of the first watch-mode report.

## 7. Retention (NC-9): 8 years

NSE requires the algo audit trail for at least 5 years; SEBI's Stock Brokers Regulations 2026 set 8 years for brokers; the tax code needs 6. Storage cost is negligible; adopt 8.

## 8. Verification outcomes (NC-8)

Resolved from primary text (`docs/research/2026-09-21-regulatory-verification.md`). Two consequences already applied to the spec: the MIS square-off schedule (F&O-segment stocks auto-square at 15:12 and enter a closing auction at 15:15, so the firm flattens them by 15:05 and the carry window moved to 14:45), and the corrected attribution of the 10 OPS threshold, weekly IP-change limit and 5-year audit trail to NSE's standards rather than SEBI's circular.
