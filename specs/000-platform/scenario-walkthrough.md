# Scenario walkthrough — the strategy-book pipeline

*Written 2026-09-20 from the Principal's scenario: a Stock Scanning agent, a Data Ingesting agent, a Senior Analyst agent that defines several strategies per stock with buy and sell prices, an Execution agent that watches ticks and applies the matching strategy, and a Recalibration agent that revises strategies from the data. This document walks one stock through one day, names the agents and the artefacts between them, and states what the pipeline implies for `roles.md`, `memory.md` and `tools-and-rails.md`.*

## 1. The pipeline

```
 Stock Scanner ──► Data Ingestor ──► Senior Analyst ──► Risk Officer ──► Execution Agent ──► (fills, positions)
      ▲                 ▲                  ▲                                   │
      │                 │                  │                                   ▼
      └───────── Recalibration Agent ◄─────┴──────────── Trade Reviewer ◄──────┘
                        │
                        ▼
                 Capital Allocator (CIO) · Operations · Compliance · Skill Engineer
```

Every agent writes its own section of the stock's **dossier** and reads everyone else's before acting, so each continues its own work on that stock across the day and across days.

## 2. The agents

| # | Agent | Decides | Produces | Invoked |
|---|---|---|---|---|
| 1 | **Stock Scanner** | Which stocks the firm works on today (and intraday additions/removals), and why | `Watchlist {symbol, reasons[], scan_features_used[], horizon_hint, priority}` | Pre-open scan; intraday re-scans on a cadence it sets; on market events |
| 2 | **Data Ingestor** | What data each watchlist stock needs, from which sources, at which granularity; whether the data is fit to analyse | `DataPack {symbol, bars[1m,15m,1d], depth, volume profile, fundamentals, announcements(published_at), results calendar, corporate actions, sector/index context, futures/options context, quality_flags[]}` | After every scan; on data-quality alerts; nightly for the research universe |
| 3 | **Senior Analyst** | The **strategy book** for each stock: several strategies, each with the conditions under which it applies, buy price/zone, sell (target) price, stop, size guidance, validity, invalidation, priority among strategies, expected R and probability | `StrategyBook {symbol, version, strategies[]}` (schema in §4) | After data packs; on Recalibration requests; on Execution escalations |
| 4 | **Risk Officer** (added) | Whether a strategy book is acceptable for the firm's book: exposure, correlation, size, cost per R, event windows; approve / modify / reject per strategy | `RiskReview` attached to the book version | On every new book version |
| 5 | **Execution Agent** | Nothing about levels. Which strategy's conditions are currently met (per the Analyst's priority rules), when an order is due, how to work it within the book's instructions, when to escalate | `ExecutionLog` entries: condition matches, orders, fills, escalations | Continuously: its **watch** evaluates every tick deterministically; the agent session is invoked on a match, an order event, an escalation condition, or a session milestone |
| 6 | **Recalibration Agent** | How each strategy is performing versus its stated expectation; which strategies to retire, adjust or add; whether the regime has shifted; what to change in the Analyst's templates | `RecalibrationReport {per_strategy_stats, regime_assessment, changes_requested[]}` and revised book versions co-signed with the Analyst | Intraday on a cadence (e.g., every 60–90 minutes) and after close; nightly across all stocks and days |
| 7 | **Trade Reviewer** (added) | Post-trade scoring of every agent's contribution on this stock (scan quality, data quality, strategy quality, execution fidelity, recalibration effect) | `TradeReview` with per-agent scores and lesson proposals | After each close; weekly |
| 8 | **Capital Allocator / CIO** (added) | Capital and LLM budget per stock/desk; which pipelines run live | `AllocationDecision` | Daily pre-open; monthly committee |
| 9 | **Operations Engineer, Compliance Auditor, Skill Engineer** (added) | As in `roles.md`: keep the firm running, compliant, and able to grow its own tools | — | Schedules and events |

The Recalibration Agent is the "monitor and recalibrate" role the Principal asked for; the Trade Reviewer and the Coach function from `roles.md` feed it with scores so that recalibration is evidence-based rather than reactive.

## 3. One stock, one day (RELIANCE, a Tuesday)

**07:45 — Stock Scanner.** Scans the NIFTY-500 with structure, volatility, liquidity and catalyst tools. Picks 12 names. For RELIANCE it records: "15-minute trend up for three sessions; consolidating under 2,960 (20-day high); relative volume 1.4× yesterday; Q2 results on Thursday (event inside horizon); options OI building at 3,000." Priority: high. Writes `sections/scanner.md` on a new dossier for RELIANCE/today.

**08:00 — Data Ingestor.** Builds the data pack: 1-minute, 15-minute and daily bars (with real volume), depth snapshot, volume profile for the last 20 sessions, sector and NIFTY context, futures basis, options OI by strike, the results date, last three announcements with `published_at`, corporate actions (none). Runs quality checks: flags that 1-minute bars for 2026-09-12 have a gap (holiday? no — feed outage); marks the gap and excludes that day from any intraday statistic. Writes `sections/data_ingestor.md` and links the pack.

**08:35 — Senior Analyst.** Reads the pack and its own memory: its playbook, its calibration (it has been over-optimistic on breakout targets in this regime, per the Coach), adopted lessons, and the last two books it wrote for RELIANCE. Calls calculators: ATR(15m) = 11.8, ATR(1d) = 48, spread 2 bps, liquidity class A, cost per R for a 35-point stop ≈ 0.04R. Writes **StrategyBook v1** with three strategies:

| id | name | applies_when (machine-checkable) | direction | entry | stop | target | size | validity | priority |
|---|---|---|---|---|---|---|---|---|---|
| S1 | Breakout continuation | `trend_15m == up` AND `close_1m > 2960` AND `volume_ratio_paced >= 1.3` AND `time in 09:30–14:30` | long | zone 2,961–2,968, marketable limit | 2,925 | 3,010 (T1), 3,040 (T2, half) | 1R = ₹6,000 | today | 1 |
| S2 | Open-drive fade | `gap_open_pct >= 1.2` AND `first_15m_close < open` AND `trend_15m != up` | short | zone 2,985–2,995 | 3,012 | 2,945 | 1R = ₹4,000 | 09:30–11:00 | 2 |
| S3 | Pullback to value | `trend_15m == up` AND `price touches VWAP ± 0.1 %` AND `pullback_depth <= 0.6 × ATR15` AND `no S1 position open` | long | zone 2,931–2,938, limit | 2,905 | 2,975 | 1R = ₹4,000 | 10:30–14:00 | 3 |

Each strategy carries: thesis (two lines), invalidation ("if NIFTY breaks the day's low with breadth < 30 %, cancel all long strategies"), expected R and probability (S1: +1.6R at 0.42), and the exclusivity rule ("S1 and S3 never both open; S2 excludes S1 for 30 minutes after a fill"). Also an **event rule** for Thursday's results: "no positional carry into results; all strategies are MIS today". Writes `sections/analyst.md` with the reasoning and the instruments used.

**08:50 — Risk Officer.** Reviews v1 against the firm book: RELIANCE would be the firm's third energy-sector position; pro-forma sector exposure 22 % (IPS cap 30 %) — fine. S1 size acceptable; S2's stop is 17 points (0.57 %) against a 0.06 % round-trip cost ⇒ cost per R ≈ 0.10R — flags it and returns `modify: widen S2 stop to ≥ 25 points or drop`. Analyst accepts: S2 stop → 3,020, size → 1R = ₹3,500. Book **v2** approved.

**09:15 — Execution Agent arms the watch.** Its deterministic watch script loads v2, subscribes to ticks and evaluates every strategy's `applies_when` on each tick (trend and volume features are recomputed by the feature service every minute). No LLM call per tick. The agent session is invoked only on: a condition match, an order event, an escalation condition, or a session milestone.

**09:31 — S2 evaluation.** Gap open 0.4 %, so S2 never applies. Logged.

**10:42 — S1 matches.** Close of the 10:41 bar 2,962, trend up, paced volume 1.5×. The watch raises `match(S1)`. The Execution Agent session opens, reads the book, checks exclusivity (nothing open), places a marketable limit at 2,966 for the computed quantity (₹6,000 / 37 points = 162 shares), records the reason. Fill at 2,964. It immediately places the stop (SL-L 2,925) and T1 (3,010, half) as protective orders. Writes `sections/execution.md`.

**11:20 — Escalation.** NIFTY breaks the day's low and breadth reads 28 %: the book's invalidation rule fires. The rule says "cancel all long strategies" but does not say what to do with an *open* S1 position. The watch raises `escalate(invalidation_open_position)`. The Execution Agent does not invent an answer: it re-invokes the **Senior Analyst** with the dossier. The Analyst decides: "hold S1 with stop raised to 2,940; its own structure is intact; cancel S3". Book **v3** (Risk Officer notified; within guidance, auto-approved by its standing rule). The Execution Agent modifies the stop. All of this is on the dossier.

**12:30 — Recalibration Agent (intraday pass).** Reads the day so far across all 12 stocks: three "pullback to value" strategies were stopped in 20 minutes; regime assessment: "trend day with shallow pullbacks failing; open-drive fades never triggered". Requests: retire all S3-type strategies for today; raise T1 on breakout-continuation strategies where the 15-minute trend is still up, since they are running further than the books expected. The Analyst updates RELIANCE to **v4**: S3 retired, T1 → 3,025. Risk Officer approves. Execution reloads v4 (the T1 order is modified).

**13:55 — T1 hits at 3,025** for half the position. Remaining half's stop moves to 2,964 (breakeven) *because the book says so* (S1's rule: "after T1, stop to entry"). The Execution Agent applies it; it would not have done so on its own initiative.

**15:00 — Carry window.** The book says MIS only today (results Thursday). No carry decision needed. **15:15** the remaining half is squared off at 3,018 by the Execution Agent per the book's "exit at 15:15" rule. Closed. Accounting writes gross, costs, slippage, R (+1.45R blended).

**16:30 — Trade Reviewer.** Scores each agent's contribution: Scanner (good pick, priority justified), Data Ingestor (gap flagged correctly), Analyst (S1 well specified; S2's original stop was cost-inefficient — a calibration mark; the invalidation rule lacked an open-position clause — a playbook gap), Risk Officer (the S2 modification was right; the S2 never triggered so no counterfactual), Execution (fidelity 100 %; escalation correct), Recalibration (the T1 raise added +0.4R versus the v2 book — counterfactual computed by code). Lesson proposals: "invalidation rules must specify the open-position action"; "in trend days, pullback-to-value strategies underperform — encode a regime condition".

**20:00 — Recalibration Agent (nightly).** Aggregates every strategy type across the last 20 sessions: breakout-continuation +0.31R mean over 46 trades (stated p 0.42, realised 0.46 — calibrated); pullback-to-value −0.22R over 38 (stated p 0.55, realised 0.37 — over-optimistic); open-drive fade 6 triggers only. Recommends to the Coach: revise the Analyst's template for pullback strategies (add a regime condition and a shallower entry), and lower the Analyst's default probability for that family. The Coach adopts the lesson, revises the Analyst's playbook (v18), adds an eval case. Tomorrow's books are written with the new template.

## 4. The strategy book (the central artefact)

```yaml
symbol: RELIANCE
version: 4
author: senior_analyst@v18
approved_by: risk_officer            # per version
valid_for: 2026-09-22 (session)      # or a date range for positional books
global_rules:
  invalidation:
    - when: "nifty_break_day_low AND breadth_pct < 30"
      then: {cancel_strategies: [long], open_positions: escalate_to_analyst}
  event_rules:
    - when: "results_within_days <= 2"
      then: {product: MIS_only, carry: forbidden}
  exclusivity:
    - never_both_open: [S1, S3]
    - after_fill: {S2: {excludes: [S1], minutes: 30}}
strategies:
  - id: S1
    name: breakout_continuation
    thesis: "…"
    applies_when: "trend_15m == up AND close_1m > 2960 AND volume_ratio_paced >= 1.3 AND time_in('09:30','14:30')"
    direction: long
    entry: {type: marketable_limit, zone: [2961, 2968]}
    stop: 2925
    targets: [{price: 3025, fraction: 0.5}, {price: 3040, fraction: 0.5}]
    after_target_1: {stop_to: entry}
    size: {risk_inr: 6000}
    validity: {start: "09:30", end: "14:30"}
    priority: 1
    expected_r: 1.6
    p_success: 0.42
    instruments_used: [calc:volatility, calc:structure, calc:liquidity, calc:cost]
    status: active
```

Properties the pipeline needs from the book:

- **Conditions are machine-checkable.** `applies_when` uses a small expression language over named features the feature service computes every minute (trend labels, volume ratios, levels, time windows, breadth). The Analyst chooses the features and thresholds; the watch evaluates them. The Skill Engineer can add features the Analyst asks for.
- **Every number is the Analyst's**, produced with calculators and cited.
- **Priority and exclusivity** resolve conflicts when several strategies match.
- **Escalation is explicit**: any situation the book does not cover is escalated to the Analyst, never improvised by the executor.
- **Versions are immutable**; the dossier records which version governed each order.

## 5. What the walkthrough implies for the spec

| Area | Change |
|---|---|
| `roles.md` | Replace the desk team (Analysts, Strategist, Trader, Position Manager) with the pipeline roles: Stock Scanner, Data Ingestor, Senior Analyst, Execution Agent, Recalibration Agent, Trade Reviewer; keep Risk Officer, CIO, Coach, Research Lab, Operations, Compliance, Skill Engineer. The Coach remains the owner of playbook revisions; the Recalibration Agent owns strategy-level revisions. |
| `spec.md` §6 | Dossier states become: `scanned → data_ready → book_drafted → book_approved → watching → working → open → closed → reviewed → archived`, with `escalated` as a transient state owned by the Analyst. |
| `tools-and-rails.md` | Add the **watch** (condition evaluator over the feature stream, deterministic, part of the Execution Agent's skill) and the **feature service** (named features recomputed every minute, extensible by the Skill Engineer). Add `books:*` tools (draft, approve, load, retire). |
| `memory.md` | Dossier sections per pipeline agent; strategy-family statistics as Recalibration memory; Analyst templates as playbook. |
| `learning.md` | Counterfactuals per book version (v2 vs v4) so recalibration is scored; strategy-family calibration tables. |
| `skills.md` | `scanning-market`, `building-data-packs`, `writing-strategy-books`, `watching-and-executing`, `recalibrating-strategies`, `reviewing-pipeline-trades`. |

## 6. Two design choices to confirm

1. **How the Execution Agent watches ticks.** Proposed: a deterministic watch script evaluates the book's conditions on every tick and invokes the agent only on matches, order events, escalations and milestones. The alternative, an LLM session reading ticks continuously, costs roughly two to three orders of magnitude more per stock-day and adds seconds of latency per decision. The proposal keeps the executor "rules only", as specified, while the rules themselves are entirely the Analyst's.
2. **Granularity of strategy books.** Proposed: one book per stock per session for intraday strategies, and one book per stock per week for swing and positional strategies, both revisable by recalibration. The alternative is one book per strategy family applied across many stocks; it is cheaper but loses the per-stock levels the scenario asks for. Both can coexist later.
