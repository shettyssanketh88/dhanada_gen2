# Dhanada: why it is not profitable yet, and what the evidence says to build

*Research date: 2026-09-07. Five parallel web-research streams (~300 searches/fetches across academic papers, SEBI studies, framework docs, fund statements, and practitioner replications), cross-checked against Dhanada's own measured results (memory notes, replay harness, strategy audit, hod_pm holdouts, LLM A/B).*

---

## 0. The answer in one page

**What a trader is.** A trader is someone who repeatedly takes risk for an expected payoff. The population base rate in India is brutal: SEBI's FY22–FY26 studies show roughly nine in ten individual F&O traders lose every year, only **0.5% of traders active all five years were profitable every year**, loss rates *rise* with experience (91% in year 1 → 95% in year 5), and individuals using algos lost ₹27,700 crore in FY24 while proprietary desks and FPIs made ₹61,000 crore, 96–97% of it algorithmically. Seven in ten equity-cash intraday traders lose, eight in ten among frequent ones.

**What the exceptional trader actually is.** Every verified "does not lose" record (Medallion, Jane Street, Citadel Securities, Graviton, AlphaGrep) is market making, arbitrage, or thousands of tiny bets with a barely-above-coin-flip hit rate. Medallion is right **50.75%** of the time. Seykota, Tudor Jones and the Market Wizards win 20–55% of trades. Systems with 95% win rates are short-tail payoff profiles (option selling, martingale, grid) and they blow up: LJM (−82% in a week), OptionSellers.com (−100% and negative equity). Nobody exceptional "does not lose trades". They do not lose *the account*, because expectancy, breadth, sizing and drawdown governance are engineered.

**So the goal must be restated.** "95% success" is achievable only as: *a diversified, cost-disciplined, risk-governed portfolio of small real edges that is ~95% likely to finish any given year net positive*, with a 40–60% trade win rate, net Sharpe 0.8–1.5, drawdowns of 15–25%, and 12–25% annual return in good years. That would put Dhanada in the top ~1% of SEBI's population. A system designed to "never lose" hides its losses in a tail.

**Why Dhanada is not there. Five blockers, all now evidenced:**

| # | Blocker | Evidence (external) | Evidence (Dhanada's own) |
|---|---|---|---|
| 1 | **It trades in the one arena where retail cannot win**: 1-minute to intraday, cash equity, tight stops. | 5-min falsification study of 14 signal families: gross edge 0.07–1.5 pts vs 2 pt friction, nothing passes. Zarattini QQQ ORB dies at 2¢ slippage. Nothing peer-reviewed supports sub-15-min holds for a cost-paying participant. | 1-min families all negative; hod_pm +0.05R gross vs ~0.19R cost; entry audit: intraday median R:R 0.71 vs 3.05 at 5-day hold, identical entries. |
| 2 | **No breadth.** One family, one horizon, one asset class, long/short single names. | Grinold: IR = IC × √breadth. Medallion = tiny IC × huge breadth. Retail Sharpe 0.8–1.5 comes from ≥5 uncorrelated sleeves across ≥2 horizons. | One live mechanical trigger (hod_pm). Beta-core book is separate and passive. F&O execution is a stub. |
| 3 | **The proven edge was found and not built.** | Momentum in Indian mid/small caps is the best evidence-to-effort strategy for a ₹10L–₹1Cr account: survivorship-adjusted net CAGR 14% vs Nifty 10.4%, Raju et al. long-only alpha survives costs, small-cap WML 0.9%/month. | 3-month momentum in 354 liquid non-NIFTY-100 names: +3.3%/month excess, 64% hit (survivorship-caveated). Flagged as "the direction" on 2026-07-07. Not built. |
| 4 | **AI is in the wrong seat.** LLM as trade planner / take-skip gate. | KTD-Fin: 9 of 10 frontier LLMs have negative stock-selection alpha once memorisation is masked. StockBench: 3/12 beat buy-and-hold over 82 days. Alpha Arena real money: GPT-5 −63%. Anchoring is measured, not prompt-fixable; Haiku among the worst. Where AI works: text → categorical features (grade B), cross-sectional GBDT with purged CV (grade A), research throughput (2–4×). | Terra take/skip A/B: +0.001R. Prompt anchoring flipped stops from 5.1% to 0.6% by changing one number. 4o-mini proposed 0/24. |
| 5 | **Validation and portfolio discipline are partial.** | Harvey-Liu-Zhu t>3; Deflated Sharpe; PBO/CPCV; Minimum Track Record Length; Millennium DD governance; realised-cost calibration. | Good: pre-registered holdouts for hod_pm, first-touch sim, A/B rig. Missing: trial ledger + DSR, realised slippage (no bid/ask, 'quote' mode), vol targeting, fractional Kelly, per-sleeve DD governance, correlation tracking. |

**What to build (summary).** Keep the plumbing (it is genuinely good). Change the product: a multi-sleeve book with a slow **cross-sectional momentum core** in mid/small caps, an **index-futures trend/last-30-min module**, a redesigned intraday sleeve limited to **stocks-in-play with wide ATR stops, one trade per name per day, hold to close, with an intraday-to-overnight hybrid**, all under a **portfolio layer** (vol targeting, fractional Kelly, automatic drawdown governance, realised-cost gate), with the **LLM moved to catalyst classification, research coding and post-trade review**. Full roadmap in §8.

---

## 1. What Dhanada is today (facts used for the gap analysis)

- **Platform**: Python/FastAPI, ~40k LOC, 139 test files, Kite REST+WS feeds, event-bus pipeline, MetaController, RiskEngine (pre-trade rails: 2% daily loss cap, 5 concurrent, 20 trades/day), compliance sentinel, kill switch service, paper OMS with marketable-limit fills, post-trade review consumer, learning-engine consumer (proposals only, never wired to live).
- **Live intraday desk (paper, ₹10L account)**: mechanical `hod_pm` trigger (afternoon break of morning high/low, 12:00–14:30 IST, 1.5×ATR15 stop, 1.5R target, bracket-only), planner OFF. Pre-registered holdouts: +0.05R gross over ~8,000 OOS trades on NIFTY-100 and ~11,000 on mid/small; real cost ~0.19R on a tight stop ⇒ net ≈ −0.13R.
- **Beta-core (paper, ₹20L)**: 100 equal-weight NIFTY-100, monthly rebalance. Passive.
- **Research tooling**: 12.9M 1-min bars, 208 symbols, 240 days; `strategy_audit` (8 families, first-touch sim, holdout switch), `plan_replay`, `llm_replay`, `hod_pm_ab`, Kite-historical factor backtests (monthly cross-sectional).
- **Findings already in hand**: 1-min technical families lose; mean-reversion worst; trailing stops and time stops subtract value (three independent confirmations); LLM selection adds nothing; the intraday horizon is the binding constraint; mid/small-cap momentum shows raw edge.
- **Missing capabilities**: F&O execution (`options_iv` is a stub), bid/ask depth (feed in 'quote' mode), realised-slippage measurement, point-in-time universe, trial ledger, vol targeting, drawdown governance per sleeve, overnight/delivery holds in the intraday path.

---

## 2. Question 1: what successful AI/automated trading frameworks do that Dhanada does not

Frameworks reviewed: QuantConnect LEAN, NautilusTrader, Freqtrade/FreqAI, Hummingbot, Jesse, Backtrader/Zipline/VectorBT, vn.py, Lumibot, FinRL, TradingAgents / ai-hedge-fund / FinMem, Alpha Arena, Composer, Trade Ideas Holly, Tickeron/Kavout, and Indian platforms (Tradetron, AlgoTest, Streak, uTrade, QuantMan, Stoxxo, AlgoBulls).

**Honest headline**: no open-source framework and no LLM-agent system has a verified profit record. TradingAgents (103k stars) needed two 2026 releases to fix look-ahead in four data sources; a 2026 survey of 77 LLM-trading studies found only one modelling transaction costs. What *is* verified is infrastructure success: parity, cost realism, risk engines, kill switches, barriers on every position.

| Pattern in durable frameworks | Dhanada status | Gap |
|---|---|---|
| Research-to-production parity is architectural (Nautilus one kernel; LEAN reality models) | Partial: `plan_replay` uses the real `interpret()`; `strategy_audit` is a separate sim | Unify: one sim path shared by audit, replay, paper |
| Model every friction per instrument, then assume you are still optimistic | Statutory costs correct (v0.51.x); slippage = 1bp assumption; no bid/ask | Switch feed to 'full' mode, log arrival vs fill, calibrate weekly |
| Signal → sizing → risk → execution as separate stages | Yes (planner/MetaController/RiskEngine/OMS) | Add a *portfolio construction* stage (vol target, Kelly fraction, correlation) |
| Risk engine with pre-trade vetoes and kill switch | Yes | Add per-sleeve drawdown governor and order-rate governor (<10 OPS) |
| Every position wrapped in barriers (triple barrier) | Yes, bracket-only; trailing/time stops proven harmful | Keep |
| Walk-forward + Monte Carlo as modes, with a recorded trial count | Holdouts yes; no trial ledger, no DSR/PBO | Build trial ledger; report DSR beside raw Sharpe |
| ML for adaptation/filtering inside rules, not end-to-end | LLM was end-to-end; now off | Reposition (see §5) |
| Point-in-time data discipline | Universe by today's liquidity (survivorship) | Point-in-time liquidity ranking per rebalance date |
| Edge from structure/execution, not prediction | Beta-core only | Add risk-premia sleeves (§3) |
| Fail closed | Yes (fail-open selector, crash-safe consumer) | Keep |
| Regulatory fit (SEBI Feb-2025 framework, enforced Apr-2026) | Static IP + OAuth present; <10 OPS not enforced as a governor | Add hard OPS cap, 5-yr audit retention check, algo-ID readiness |
| Verified adoption beats stars | n/a | Ignore star counts when picking tools |

**Nothing here is a reason to adopt a new framework.** Dhanada already has the parts that matter. The gap is what runs *on* the engine and the missing portfolio/validation layer.

---

## 3. Question 2: which strategies make money for automated systems, and what Dhanada lacks

Ranked by evidence × retail accessibility (₹10L–₹1Cr via Kite) × capacity:

| Rank | Strategy | Evidence | Net Sharpe (realistic) | Holding | Retail on Kite? | Dhanada has it? |
|---|---|---|---|---|---|---|
| 1 | Cross-sectional momentum, long-only, mid/small-cap tilt | A global, B+ India (Raju; Mandhyan; BacktestIndia survivorship-adjusted 14% vs 10.4% CAGR) | 0.35–0.6; alpha +3–5%/yr vs Nifty | 1–6 months | Yes; ₹1Cr is small enough to hold names funds cannot | **No** (raw research only) |
| 2 | Low-vol / quality tilt (core) | A / B | 0.5–0.7, mostly beta | Quarterly | Yes | Equal-weight beta only |
| 3 | Trend following on index futures (overlay) | A | 0.2–0.4 single market | Weeks–months | Yes, needs F&O | **No** (F&O stub) |
| 4 | Stocks-in-play intraday (RVOL-filtered ORB, wide stops, hold to close) | B (Zarattini 2024, QuantConnect replication Sharpe 2.4; gross of spreads) | Unknown net in India; +0.38R vs −0.02R unfiltered in US | Intraday | Yes | Scanner picks by price move only; no RVOL |
| 5 | Last-30-min index momentum (Gao et al.) | A US (Sharpe ~1 gross, ~0.7 net); India one unverified paper | ~0.5 est. | 30 min | Needs index futures | **No** |
| 6 | Intraday-to-overnight hybrid | A that overnight drift exists (India: 92% of gains overnight); C tradable | Overlay | Hold winners overnight | Yes (CNC/NRML) | **No** (forced 15:20 flatten) |
| 7 | PEAD in small caps | B− | 0.3–0.5 | 1–3 months | Needs surprise data | No |
| 8 | Pairs / stat-arb | A historic, declining; C India | 0.2–0.5 | Days–weeks | Stock futures only | No |
| 9 | ML cross-sectional ranker on top of #1 | A US academic (Gu-Kelly-Xiu), C India | Adds IC, kills turnover | Monthly | Feasible | No |
| 10 | Volatility risk premium (option selling, 9:20 straddle) | India net **negative** (Pillai 2026: all four variants lose after frictions; tail dominates) | −0.37 to deeply negative | Intraday–weekly | Mechanically easy, statistically worst | Not built; **do not build as P&L engine** |
| — | Market making | Closed to retail (colocation, OPS cap, OTR penalties) | — | — | No | — |

**Gap in one sentence**: Dhanada has built nothing from ranks 1–6 and everything from the unranked bottom (1-min technical intraday). The counterparty of Indian intraday retail is the ₹61,000-crore institutional algo profit pool.

---

## 4. Question 3: intraday methods that survive, and the cost arithmetic Dhanada must obey

**What survives replication and costs** shares four properties: a selection filter concentrating trades on abnormal-volume days; wide ATR-scaled stops with hold-to-close; low hit rate / high payoff; at most one trade per symbol per day.

- **Stocks-in-play ORB (Zarattini, Barbon, Aziz 2024)**: rank by relative volume in the first 5 minutes vs the 14-day average of the *same window*; top 20 with RVOL >100%; stop-entry beyond the 5-min range; exit at close; risk 1%; Sharpe 2.81 reported, 2.40 in an independent replication; unfiltered ORB was below the S&P. The filter *is* the edge.
- **Market intraday momentum (Gao, Han, Li, Zhou 2018; Baltussen et al. 2021)**: first-half-hour return predicts the last half-hour; mechanism = gamma hedging by option market makers; 54% hit, Sharpe ~1 gross, ~0.7 net; stronger on high-vol days. India has the world's largest index-option OI, so the mechanism is plausible on NIFTY.
- **"Beat the Market" intraday momentum (Zarattini, Aziz, Barbon 2024)**: noise-band breakout with vol-targeted sizing, one trade/day, flat at close; ES/NQ replication with real futures costs: Sharpe 0.9–1.7, +2–6 bp per trade. Marginal in NIFTY futures at ~7 bp round trip unless conditioned on vol.
- **Overnight vs intraday in India**: NIFTY gains accrue overnight; intraday drift is negative post-2010. A long-only intraday equity desk fights structural drift; a short-biased intraday rule and holding winners overnight have the drift on their side.
- **What fails**: VWAP reversion (bid-ask bounce, liquidity-taker), gap fades on ≥1% NIFTY gaps (29% fill), 9:20 straddle / 0DTE selling (only no-slippage vendor backtests, pre-Nov-2024 regime), anything sub-15-minute.

**Cost arithmetic (Zerodha, post-Budget-2026 STT):**

| Segment | Round-trip ex-slippage | All-in with slippage |
|---|---|---|
| Equity intraday | ~0.08–0.10% of notional | ~0.15% |
| Index/stock futures | ~0.06–0.07% | ~0.07% |
| Options | ~0.5% of premium + ₹40/lot | higher |

cost_R = round-trip cost % ÷ stop distance %. Equity at 0.15%: 0.75% stop ⇒ 0.20R (Dhanada's number); 2% stop ⇒ 0.075R; 3% stop ⇒ 0.05R. **A +0.05R gross rule needs a ≥3% stop in cash equities or ≥1.5% in NIFTY futures just to break even.** This single equation explains the whole intraday P&L history.

**Dhanada gap**: scanner has no RVOL (20-day volume feed unreliable, gate off); stops are 1.5×ATR15 (~0.6%); no futures; forced flatten at 15:20; no overnight path.

---

## 5. How AI is really used in trading, and where Dhanada's LLM should sit

| AI technique | Value-add | Evidence | Dhanada now | Should be |
|---|---|---|---|---|
| LLM proposing entry/stop/target | ≈0; anchors on any number | none | Built, off | **Removed from entry path** |
| LLM take/skip on mechanical trigger | ≈0 (+0.001R measured) | none | Built, off | Retire; at most a categorical veto ("results/regulatory event inside 60 min"), A/B-tested |
| LLM catalyst/event classification → enum feature | Small positive; small/mid caps; decays in days | B | Catalyst text prepended to prompt | Pre-market batch: ~10 enums + novelty flag, feeding scanner and stop-width model |
| LLM text embeddings into GBDT | Positive in 16 markets (Chen-Kelly-Xiu) | B | No | After a cross-sectional model exists |
| Cross-sectional GBDT/NN, era-normalised, purged CV, DSR | Real (AQR ~20% of signals; Numerai Sharpe 2.75 live, JPM $500M capacity) | **A** | No | Ranker on top of momentum sleeve, monthly |
| ML regime classifier gating size/stop | Modest, robust | B | Regime from RELIANCE proxy, degenerate | Breadth/vol/dispersion classifier for sizing, not direction |
| LLM as research coder / hypothesis generator | 2–4× throughput, zero alpha | A (productivity) | Ad hoc (this session) | Formalise with a trial ledger; every backtest is a logged trial |
| LLM as post-trade reviewer | Diagnostic, no P&L risk | C | post_trade_review_builder exists | Weekly batch producing categorical hypotheses → A/B tests |
| Deep RL for signals | ≈0 after seed control | none | No | Skip |
| Time-series foundation models for direction | ≈0 (2/10 tasks beat random walk) | none | No | Skip; optional vol forecast |

Design rules that survive the evidence: LLM emits categories never levels; strip numbers from prompts; temperature 0, three samples, disagreement = abstain; log every prompt/output for replay; A/B every LLM feature against the mechanical baseline exactly as `hod_pm_ab` already does.

---

## 6. What exceptional systematic traders do (design requirements)

1. Objective = positive expectancy in R after *realised* costs at a Sharpe that lets modest leverage produce the return. Win rate is a free parameter.
2. Breadth before signal quality: ≥5 low-correlation sleeves across ≥2 horizons; measure realised P&L correlation monthly.
3. Every trade sized in R from a fractional-Kelly budget (¼–½ on shaded edge); portfolio vol targeting 10–12% annualised.
4. Automatic drawdown governance per sleeve and desk (−3% halve, −6% stop and re-validate, desk −10% flat). No discretionary overrides.
5. Cost model calibrated from live fills weekly; pause any sleeve whose gross expectancy < 2× realised cost.
6. Pre-registered research: hypothesis, universe, params, costs, kill criteria written first; every trial logged; report Deflated Sharpe and PBO; walk-forward OOS ≥ 50% of in-sample.
7. Promotion gates in trades and regimes (≥100 trades spanning a trending and a choppy quarter), using Minimum Track Record Length.
8. Prefer daily/weekly horizons and risk-premia/structural edges; treat sub-5-minute signals as presumptively cost-dominated.
9. No naked short-tail exposure; any option selling is defined-risk, sized so a 3σ day ≤ 1R.
10. Regime and regulatory monitors as components (expiry rules, OPS limits, lot sizes change by circular).
11. Three-level kill switches (sleeve anomaly, desk P&L/exposure/OPS, gateway flat-and-cancel), drilled each release.
12. SEBI-2025 plumbing: OAuth+2FA, whitelisted static IP, hard <10 OPS governor, ≥5-year audit log, algo-ID readiness.
13. Learning loop adapts only within pre-declared bounds on rolling walk-forward; every change re-enters the gates.
14. Dashboard shows expectancy in R, DSR, realised cost/R, correlation matrix, drawdown vs limit, MTRL progress. Not win rate.
15. Track decay; auto-demote at 50% of validated expectancy; design for replacement.

Dhanada satisfies roughly 1 (partially), 6 (partially), 11 (partially), 12 (partially). The rest are the build.

---

## 7. Consolidated gap analysis

| Gap | Why it blocks profit | Fix | Effort |
|---|---|---|---|
| Intraday cash-equity with ~0.6% stops | cost 0.19R > edge 0.05R by construction | Wide ATR stops (≥2–3% or ≥1×daily ATR), one trade/name/day, hold to close; move market-level rules to index futures | M |
| No slow sleeves | All evidenced retail edge is at daily+ horizon | Momentum core + quality screen + trend overlay | M (reuse rebalancer, factor backtests) |
| Survivorship in universe | Inflates momentum by a lot | Point-in-time liquidity ranking per rebalance date | S |
| No F&O execution | Blocks trend overlay, last-30-min timing, cheap hedging | Kite NFO adapter for NIFTY futures (orders, margins, rollover) | L |
| Forced 15:20 flatten | Gives up the positive (overnight) component | CNC/NRML conversion path for winners meeting a condition; delivery margin budget | M |
| No RVOL | The stocks-in-play filter is the whole ORB edge | Real 20d per-window volume feed (backfill exists with real volume) | S |
| No bid/ask | Slippage unmeasured; cost model may still understate | Kite 'full' mode (parser exists); arrival-vs-fill logging | S |
| No portfolio layer | Sizing/DD/correlation are what separate survivors | Vol targeting, fractional Kelly, per-sleeve DD governor, correlation report | M |
| No trial ledger / DSR | Best-of-N selection already killed squeeze once | Ledger table + DSR/PBO in strategy_audit | S |
| LLM as decider | Zero alpha, anchoring, cost | Move to catalyst enums + research + review | S |
| Learning engine unwired | Adaptivity is a loss-limiter, not edge; must be bounded | Wire only bounded, walk-forward, pre-registered knobs (§6.13) | M |
| Regime degenerate | Single-symbol proxy cannot read "trending" | Breadth/dispersion/vol regime from the universe | S |
| OPS not governed | SEBI Apr-2026 enforcement | Hard governor <10 orders/sec/exchange | S |

---

## 8. Roadmap with verification gates

Principle: never test one thing per live day again. Every phase has a harness gate before a paper gate before capital.

**Phase 0 — Honesty and instrumentation (≈2 weeks)**
- Kite 'full' mode; log arrival price, fill price, spread; realised cost/R weekly report.
- Trial ledger (every backtest run: hypothesis, params, universe, dates, Sharpe, n); DSR and PBO in `strategy_audit`.
- OPS governor; per-sleeve accounts and P&L attribution; regime classifier from universe breadth/dispersion.
- Gate: realised slippage on hod_pm measured over ≥200 fills; cost model recalibrated.

**Phase 1 — Momentum core (≈4–6 weeks, parallel with 0)**
- Point-in-time universe (turnover rank as of each rebalance date); 3-month and 6-month formation, monthly/semi-monthly rebalance at close; top 30–50; quality/low-vol screen; NIFTY 10-month MA de-risk overlay; STCG-aware turnover.
- Reuse `rebalancer/core.py`, `tools/rebalance.py`, the factor backtest pipeline. New paper account.
- Gate (harness): survivorship-free net alpha > 0 in ≥4 of 5 years, DSR > 0 at the ledger's trial count, max DD documented. Gate (paper): 3 rebalances tracking the backtest within tolerance.

**Phase 2 — Intraday redesign (≈4 weeks)**
- hod_pm: widen stop to ≥1×daily ATR / ≥2% (accept fewer, larger trades); re-run the four holdouts with the new geometry and realised costs; keep only if net > 0.
- Stocks-in-play sleeve: RVOL top-20 at 09:20/09:30 across NIFTY-500 liquid names; stop-entry beyond opening range; 0.5–1.0×ATR14 stop; hold to 15:15; 1% risk; ≤1 trade/name/day. Gate: pre-registered holdouts as for hod_pm.
- Intraday-to-overnight hybrid: winners above +1R at 15:10 with positive day-move convert to CNC, exit next open or trailing daily stop; capped notional. Gate: harness on the 240-day bar set.
- Gate (paper): ≥100 trades per sleeve across ≥2 regimes, expectancy net of realised cost > 0 at 1σ.

**Phase 3 — Index futures module (≈6 weeks, needs F&O adapter)**
- NIFTY futures: last-30-min timing (sign of open→14:55 return scaled by noise band; skip inside band); trend overlay for the momentum core (10-month MA, vol-scaled).
- Gate: harness on NIFTY 1-min history with 0.07% costs; paper ≥60 sessions.

**Phase 4 — AI repositioned (≈3 weeks, parallel)**
- Pre-market catalyst classifier: enum event type, strength, novelty, direction; feeds scanner/stop-width. A/B against no-feature.
- Research assistant writes backtests only through the trial ledger.
- Weekly post-trade reviewer emits categorical hypotheses into a queue; each becomes a pre-registered test.
- Gate: catalyst feature lifts expectancy at DSR > 0; otherwise off.

**Phase 5 — Portfolio layer and capital gate (≈4 weeks)**
- Vol targeting 10–12%, fractional Kelly per sleeve, correlation matrix, per-sleeve DD governor (−3/−6/−10), decay monitor, dashboard in R/DSR/cost.
- Capital gate: ≥3 sleeves with paper net expectancy > 0, portfolio DSR > 0, MTRL progress reported, drills passed. Then small real capital on the slow core first, intraday last.

**Stop doing now**: 1-min entries of any kind; tight-stop intraday on cash equities without the cost equation; LLM in the entry path; trailing/time stops; reacting to daily P&L; any option-selling P&L engine.

---

## 9. Realistic targets (state these to yourself before building)

| Metric | Realistic for a well-built retail desk in India | "Exceptional" |
|---|---|---|
| Trade win rate | 40–60% momentum/trend; 55–70% daily mean reversion | Irrelevant; expectancy matters |
| Net Sharpe, diversified book | 0.8–1.5 | > 1.5 sustained is audit-worthy |
| Max drawdown at 10–12% vol | 15–25% | Momentum-only: −50% to −70% in crashes |
| Annual net return | 12–25% good years; flat/negative one year in three or four | Nifty + 3–8 pp over 5 years with lower DD = top 1% |
| Time to trust an edge | Sharpe 1 ⇒ ~2.5–3 years live; Sharpe 0.5 ⇒ a decade | Design capital deployment to survive the wait |

"95% success" translated honestly: 95% probability the desk survives and is net positive in a given year. That is what the exceptional 0.5% actually have.

---

## Sources (consolidated)

**Base rates and regulation**: SEBI PR 37/2024 (93% lose FY22–24); SEBI Aug-2026 FY25–26 study; SEBI Jul-2024 intraday cash study; SEBI circular 4 Feb 2025 (retail algo framework; Apr-2026 enforcement); Barber–Odean; Barber, Lee, Liu, Odean (Taiwan); Chague et al. (Brazil); Zerodha In the Money (overnight drift; HFT); Nithin Kamath statements.
**Exceptional performers**: Zuckerman (Medallion, 50.75%); Cornell (Medallion counterexample); Hedgeweek/Bloomberg (Jane Street, Citadel Securities 2025); SEBI Jane Street order; QuantInsti/Sanchety (Indian HFT); AQR Hurst-Ooi-Pedersen (century of trend); LJM and OptionSellers post-mortems.
**Strategies**: Raju & Chandrasekaran 2019; Raju & Teli 2022; Raju 2023/2024; Mandhyan 2025; BacktestIndia survivorship-adjusted momentum; Gatev-Goetzmann-Rouwenhorst; Do & Faff; Pillai 2026 (Nifty VRP with frictions); Lou-Polk-Skouras; Knuteson; Elm Wealth; Martineau (PEAD); Gu-Kelly-Xiu; Avramov-Cheng-Metzker.
**Intraday**: Zarattini & Aziz 2023 (QQQ ORB) and Brusco replication; Zarattini, Barbon & Aziz 2024 (stocks in play) and QuantConnect replication; Gao-Han-Li-Zhou 2018; Baltussen et al. 2021; Zarattini-Aziz-Barbon 2024 "Beat the Market" and Quantitativo ES/NQ replication; arXiv 2605.04004 (5-min falsification); Heston-Korajczyk-Sadka; IntradayLab NIFTY gap study; Zerodha charges; ICICI Direct Budget-2026 STT.
**AI**: arXiv 2412.20138 (TradingAgents); arXiv 2505.07078 (FinMem/FinAgent re-test); StockBench 2510.02209; KTD-Fin 2605.28359; TradeTrap 2512.02261; nof1 Alpha Arena; Lopez-Lira & Tang; Chen-Kelly-Xiu SSRN 4416687; Lookahead Propensity 2512.23847; FinCAD 2605.24564; Unstable Gains (DRL multiplicity); Noguer i Alonso & Franklin 2606.27100 (TSFMs); Kronos and Cornford & Cross test; Garcia SSRN 6366838 (LLM anchoring); Bailey & López de Prado (DSR, PBO); Two Sigma 2026 outlook; Man Group AlphaGPT; AQR/Bloomberg; Numerai.
**Frameworks**: QuantConnect LEAN docs; NautilusTrader architecture; Freqtrade/FreqAI; Hummingbot reporting; Jesse; Lumibot agents; FinRL-Meta 2211.03107; arXiv 2605.19337 (survey of 77 LLM-trading studies); arXiv 2608.27734 (leakage-safe certification); AlgoTest/Tradetron/Streak reviews; IBKR and Zerodha SEBI-framework summaries.
