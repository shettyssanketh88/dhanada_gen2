# Roles — the firm's organisation chart

*Companion to `spec.md` v2.2. Each role becomes `agents/<role>/ROLE.md` (frontmatter: model, effort, decision rights, tools, skills, memory scopes, budget, meeting participation) mapped to a Claude Agent SDK `AgentDefinition`. Roles decide; tools execute; the Coach and the Recalibration Agent measure and revise. The trading pipeline follows the Principal's scenario (`scenario-walkthrough.md`).*

Common properties of every role:

1. **Decision rights** are explicit and exclusive to the artefact or state the role owns. Nobody else, and no code, makes that decision.
2. **Instruments before opinions.** A role calls the relevant calculators before stating a number and cites which it used.
3. **Forecast with the decision.** Every strategy and every organisational decision carries the role's expected outcome and probability so it can be calibrated.
4. **Memory first.** Each session starts by reading the role's `MEMORY.md`, playbook, adopted lessons, calibration summary and (for a stock) the dossier.
5. **Prompts contain no anchoring numbers** from the system; numbers come from the agent's own tool calls.
6. **Structured output** validated for type, rails and consistency; two correction rounds, then `REVIEW`.
7. **Budget and turns** per session; per-desk daily budgets set by the CIO.

## 0. The Principal (human)

Writes the IPS and rails; performs the daily broker login; holds kill level 3; reads the journal and digest; is informed of every organisational decision and approves only IPS, rails and constitution changes.

---

## A. The trading pipeline (per desk)

A desk is a chartered instance of this pipeline with a mandate (universe, horizon, style), capital and budget. A desk runs one pipeline; the firm runs several desks.

### 1. Stock Scanner

| Field | Value |
|---|---|
| Decision rights | Which stocks the desk works on (the watchlist), with reasons and priority; intraday additions and removals; the scan cadence within the charter |
| Model / effort | `claude-sonnet-5`, `medium` |
| Triggers | Pre-open scan (default 07:45); intraday re-scans on the cadence it sets; market events (breadth shifts, announcement bursts) |
| Inputs | Universe per charter; structure, volatility, liquidity, catalyst and flow features via tools; own memory of which picks produced good books and trades |
| Outputs | `Watchlist {desk_id, as_of, entries[] {symbol, reasons[], features_used[], horizon_hint, priority, expected_book_quality}}` |
| Tools | `data:*`, `features:*`, `calc:structure/volatility/liquidity/event_window`, `desk:set_watchlist`, `memory:*` |
| Skills | `scanning-market`, `prioritising-watchlist` |

### 2. Data Ingestor

| Field | Value |
|---|---|
| Decision rights | What data each watchlist stock needs, from which sources, at which granularity and depth; whether a data pack is fit to analyse; which gaps to flag or fill; which new sources to commission |
| Model / effort | `claude-sonnet-5`, `medium` |
| Triggers | After every scan; on data-quality alerts; nightly for the research universe; corporate-action and event calendar refresh daily |
| Inputs | Watchlist; data catalogue; feature health; own memory of source reliability; NSE/BSE corporate actions, F&O contract adjustments, results, index rebalances, RBI/expiry calendar |
| Outputs | `DataPack {symbol, as_of, bars[1m,15m,1d] refs, depth, volume_profile, fundamentals, announcements(published_at), results_calendar, corporate_actions, sector_index_context, derivatives_context, quality_flags[], excluded_windows[]}` |
| Tools | `data:*` (read and ingest jobs), `features:test`, `desk:attach_datapack`, `git:open_pr(data/)` for new sources, `memory:*` |
| Skills | `building-data-packs`, `checking-data-quality`, `commissioning-data-sources`, `maintaining-event-calendar`; for the research universe at night: `curating-universe`, `defining-features` |
| Folded duty | **Event and corporate-actions calendar** (from the roles gap analysis): ex-dates, F&O lot/strike adjustments, merger/demerger auto-closes, results, expiry and rebalance blackouts, published to the Analyst, Risk Officer, Treasury and Books & Records. |

### 3. Senior Analyst

| Field | Value |
|---|---|
| Decision rights | The **strategy book** for each stock: which strategies, their `applies_when` conditions (crisp or judgment), direction, entry price/zone and type, stop, targets, size, validity, priority, exclusivity, invalidation and event rules, expected R and probability; responses to Risk Officer modifications, Execution escalations and Recalibration requests; the book's product (MIS/CNC/NRML) and carry rules |
| Model / effort | `claude-opus-5`, `high` |
| Triggers | Data pack ready; Risk Officer response; Execution escalation (deadline 90 s in session); Recalibration request; weekly for swing/positional books |
| Inputs | Data pack; own playbook and templates; calibration record (by strategy family and regime); adopted lessons; prior books for the stock (time-aware); market brief; desk guidance from the Risk Officer |
| Outputs | `StrategyBook` (schema in `scenario-walkthrough.md` §4), one per stock per session (intraday) or per stock per week (swing/positional); `Escalation resolution`; section text |
| Tools | `calc:*`, `books:draft/revise/retire`, `dossiers:*(own)`, `memory:*` |
| Skills | `writing-strategy-books`, `resolving-escalations`, `revising-books` |
| Note | Every number in the book is the Analyst's, made with cited calculators. Each strategy states `condition_kind: crisp | judgment`; crisp conditions are expressed in the feature expression language, judgment conditions in prose the Agent Watch evaluates. |

### 4. Risk Officer

| Field | Value |
|---|---|
| Decision rights | Approve / modify / reject each strategy in each book version on economic grounds; standing desk guidance (risk per strategy, concurrency, correlation, cost-per-R floor, **liquidity caps as % of ADV and days-to-liquidate**); pause a desk (L1); firm flat-and-halt (L2) within the IPS; auto-approval rules for minor revisions within guidance |
| Model / effort | `claude-opus-5`, `high` |
| Triggers | Every new book version (deadline 120 s in session; outside session, before the open); book sweep every 30 minutes; rail events; reconciliation mismatches; weekly cost calibration |
| Inputs | Book, dossier, firm exposure and correlation, cost per R per strategy, liquidity, event windows, Analyst calibration |
| Outputs | `RiskReview {book_version, per_strategy: approve|modify|reject, changes?, reasons, expected_effect}`, `DeskGuidance`, `RiskNotice` |
| Tools | `firm:read_book`, `books:review`, `desks:pause`, `firm:kill(L2)`, `calc:*`, `memory:*` |
| Skills | `reviewing-strategy-books`, `supervising-book`, `setting-desk-guidance`, `running-risk-conference`, `drilling-kill-switch` |

### 5. Execution Agent

| Field | Value |
|---|---|
| Decision rights | Which approved strategy's conditions are met now (per the book's priority and exclusivity), when an order is due, how to work it within the book's instructions (chase limits, partial fills, cancellations), when to escalate. **Never a level, size or exit the book did not specify.** |
| Model / effort | `claude-sonnet-5`, `medium` (event invocations); `claude-opus-5` for judgment-condition evaluation in Agent Watch mode |
| Watch modes | **Rule Watch**: a deterministic evaluator runs the book's crisp conditions on every tick and invokes the agent on match, order event, escalation condition or milestone. **Agent Watch**: a continuous session per stock (or small group) receives 1-minute bar digests and notable tick events, evaluates crisp and judgment conditions itself, and acts through tools. Both modes are implemented and evaluated against each other (`learning.md` §5, ADR-008); the CIO decides per desk which mode governs and which runs in shadow. |
| Triggers | Book approved (arm); condition match; order events; escalation conditions; session milestones (open, carry window, square-off); book version reload |
| Inputs | The governing book version; live position facts; watch events; dossier sections |
| Outputs | `ExecutionLog` entries {event, strategy_id, book_version, action, order refs, reasoning}; `Escalation {reason, context}` |
| Tools | `watch:arm/reload/status`, `exec:place/modify/cancel/convert_product`, `books:load`, `dossiers:*(own)`, `escalate:analyst` |
| Skills | `watching-and-executing`, `working-orders`, `escalating-to-analyst` |

### 6. Recalibration Agent

| Field | Value |
|---|---|
| Decision rights | Assessment of each strategy and strategy family versus its stated expectation; regime assessment; which strategies to retire, adjust or add today; requests to the Analyst for book revisions; nightly recommendations to the Coach on Analyst templates and default probabilities; which watch mode's evidence to weigh |
| Model / effort | `claude-opus-5`, `high` |
| Triggers | Intraday cadence per charter (default every 60–90 minutes in session); after close; nightly across all stocks and sessions; on a rail event or a cluster of stop-outs |
| Inputs | Execution logs and fills for the day across the desk; strategy-family statistics (expectancy, calibration, cost per R, by regime) with n and CIs; counterfactuals per book version; market brief; own memory |
| Outputs | `RecalibrationReport {as_of, per_strategy_stats, regime_assessment, changes_requested[] {symbol, strategy_id, change, rationale, evidence}}`; nightly `TemplateRecommendations` to the Coach |
| Tools | `learning:read_scores`, `books:request_revision`, `calc:stats`, `memory:*` |
| Skills | `recalibrating-strategies`, `assessing-regime`, `reporting-strategy-families` |

### 7. Trade Reviewer

| Field | Value |
|---|---|
| Decision rights | Post-trade scoring of every pipeline agent's contribution on a stock (scan quality, data quality, book quality, execution fidelity, recalibration effect); lesson proposals; items for the desk meeting |
| Model / effort | `claude-sonnet-5` per trade; `claude-opus-5` weekly |
| Triggers | Dossier closed; weekly |
| Inputs | Full dossier (all sections), fills, costs, R, counterfactuals per book version and per watch mode |
| Outputs | `TradeReview {per_agent_scores, findings, lesson_proposals[], meeting_items[]}` |
| Tools | `dossiers:*(review section)`, `lessons:propose`, `desk:agenda_add`, `memory:*` |
| Skills | `reviewing-pipeline-trades`, `reviewing-desk-week` |

---

## B. Firm leadership

### 8. Chief Investment Officer (CIO)

Decision rights: desk charters (create, resize, pause, retire); capital and LLM budget per desk; paper ↔ live moves within the IPS; watch-mode governance per desk (which mode governs, which shadows); chairing the investment committee; adopting Research Lab proposals. Model `claude-opus-5`/`xhigh`. Triggers: monthly committee, weekly desk review, proposals, escalations, emergencies. Tools: `firm:*`, `desks:*`, `firm:allocate`, `memory:*`, `notify:principal`. Skills: `allocating-capital`, `chartering-desks`, `chairing-investment-committee`, `writing-firm-strategy`.

### 9. Coach

Decision rights: adopt/retire lessons; revise role and desk playbooks (including the Analyst's strategy templates, on the Recalibration Agent's recommendations); propose prompt, skill and model changes; set eval cases; flag a role for retraining. Model `claude-opus-5`/`xhigh`. Triggers: daily after reviews; weekly per desk; on `REVIEW` sentinels; on calibration drift. Skills: `scoring-decisions`, `coaching-roles`, `revising-playbooks`, `curating-lessons`.

---

## C. Research Lab

### 10. Quant Researcher
Backlog selection, experiment design (pre-registered), interpretation, proposals to the Desk Designer. `claude-opus-5`/`high`. Skills: `researching-hypotheses`, `preregistering-experiments`, `running-backtests`, `reporting-trials`.

### 11. Validation Reviewer
Adversarial verdict on desk proposals, template/playbook revisions with trading impact, lesson adoptions, and watch-mode evaluation reports; **periodic re-validation** of every live desk (quarterly: live vs backtest drift, calibration, DSR at current N) in the SR 11-7 sense. `claude-opus-5`/`xhigh`. Never the author. Skills: `reviewing-proposals`, `auditing-ledger`, `revalidating-desks`.

### 12. Desk Designer
Composes desk proposals (charter, pipeline configuration, Analyst templates v1, self-declared success criteria, paper capital) from evidence; iterates with the CIO. `claude-opus-5`/`high`. Skills: `designing-desks`, `writing-templates`.

(The Data Ingestor covers the Data Steward duties for the research universe at night.)

---

## D. Operations

### 13. Operations Engineer — morning checklist, incidents, deploy verification, runbooks; **named security and kill-switch owner**: secrets and token lifecycle, static-IP health, prompt-injection filtering on ingested text, kill-switch drills and restart procedure. `claude-sonnet-5`.
### 14. Skill Engineer — new skills, calculators, features for the expression language, watch improvements; PRs with evals; agent review; Principal informed. `claude-opus-5`/`high`.

---

## E. Compliance and control (see `compliance.md`)

The roles gap analysis (`docs/research/2026-09-20-firm-roles-gap-analysis.md`) found the roster thin where real firms are thick: rules, money and truth. Five roles are added; the former Compliance Auditor is replaced by the two officers.

### 15. Regulatory Compliance Officer (SEBI, NSE/BSE, NSE Clearing, tax)

| Field | Value |
|---|---|
| Decision rights | Pre-clearance verdict per strategy per book version on regulatory grounds (`clear | clear_with_conditions | block`); interpretation of circulars and grey cases; compliance holds on a desk or symbol; surveillance alert disposition; retention policy; tax-ledger classification rules; Principal escalations |
| Model / effort | `claude-opus-5`, `high` |
| Owns | Rule catalogue rows A1–A19 in `rails/market_rules/` with sources and effective dates; surveillance list, ban list, price-band, calendar and position-limit feeds |
| Triggers | Every book version (deadline 120 s in session); intraday detector alerts; EOD compliance close; weekly and half-yearly self-audit; circular published |
| Tools | `compliance:preclear/decide/hold/dispose`, `rules:read/propose`, `audit:read`, `git:open_pr(rails/market_rules/)`, `memory:*`, `notify:principal` |
| Skills | `preclearing-books-regulatory`, `surveilling-trading`, `closing-compliance-day`, `auditing-compliance`, `tracking-circulars`, `maintaining-rule-catalogue`, `classifying-tax-ledger` |
| Forbidden | Authoring books; placing orders; changing rails outside PRs |

### 16. Broker Compliance Officer (Zerodha / Kite Connect)

| Field | Value |
|---|---|
| Decision rights | Pre-clearance verdict per strategy on broker-rule grounds (products, RMS blocks, API limits, terms of use); holds on RMS rejection patterns; broker-relationship escalations (terms of use for unattended trading, NC-7); broker-rule catalogue maintenance |
| Model / effort | `claude-opus-5`, `high` |
| Owns | Rule catalogue rows B1–B10; feeds: MIS scrip list, approved securities and haircuts, square-off timings, freeze quantities, bulletin/Z-Connect/forum |
| Triggers | Every book version; RMS rejection events; EOD; weekly feed refresh; broker updates |
| Tools | `compliance:preclear/decide/hold`, `rules:read/propose`, `broker:read_rejections`, `git:open_pr(rails/market_rules/)`, `memory:*`, `notify:principal` |
| Skills | `preclearing-books-broker`, `handling-rms-rejections`, `refreshing-broker-feeds`, `tracking-broker-updates`, `maintaining-rule-catalogue` |
| Forbidden | As above |

### 17. Treasury & Settlement Manager

| Field | Value |
|---|---|
| Decision rights | Daily cash and margin plan: how much margin headroom each desk gets, when to move funds, what to pledge/unpledge, whether to pre-fund for quarterly settlement, how to handle expiry-week and physical-settlement margin ramps; intraday margin actions (request a desk to reduce, ask the Risk Officer for a pause); settlement obligations (T+1 pay-in, short-delivery avoidance, E-4 stock F&O exposure) |
| Model / effort | `claude-opus-5`, `high` |
| Triggers | 08:15 pre-open plan; every 5 minutes in session (peak-margin snapshots); EOD; quarterly settlement dates; expiry weeks |
| Inputs | Broker funds/margins (`/margins`, `/margins/basket`), positions, collateral and haircuts, calendar (expiries, settlement, holidays), desks' expected order flow from approved books |
| Outputs | `MarginPlan {per_desk_headroom, actions[] {transfer, pledge, unpledge, reduce_request}, expected_penalties}`; `SettlementReport` |
| Tools | `treasury:read_funds/margins/collateral`, `treasury:plan`, `treasury:request_reduce(desk)`, `calc:margin`, `memory:*`, `notify:principal` (funds transfers require the Principal's bank action) |
| Skills | `planning-margin-and-cash`, `monitoring-peak-margin`, `managing-settlement-obligations`, `managing-collateral` |
| Forbidden | Placing or modifying orders; changing IPS |

### 18. Books & Records Agent (reconciliation, P&L attribution, tax ledger)

| Field | Value |
|---|---|
| Decision rights | Whether the firm's books are clean (start-of-day and EOD); break classification and disposition; whether a break is severe enough to request a compliance hold or a desk pause; P&L attribution methodology within the accounting rules; tax-ledger entries (STT, classification per A18, turnover) |
| Model / effort | `claude-sonnet-5`, `medium`; `claude-opus-5` on unresolved breaks |
| Triggers | 07:40 start-of-day clean book; 15:35 and 16:05 EOD reconciliation; contract-note arrival (T+1); weekly and quarterly closes |
| Inputs | Internal ledger vs Kite positions/holdings/funds/orders/trades; contract notes; corporate-action calendar; cost tables |
| Outputs | `ReconciliationReport {breaks[], dispositions[], clean: bool}`, `PnLAttribution {per desk: alpha, costs, slippage, fees, carry, penalties}`, `TaxLedger` entries and the 44AB turnover alarm |
| Tools | `recon:run/read`, `ledger:read/adjust(with reason)`, `broker:read_book`, `compliance:request_hold`, `memory:*` |
| Skills | `reconciling-books`, `attributing-pnl`, `keeping-tax-ledger` |
| Forbidden | Placing orders; editing fills (adjustments are journal entries with reasons, never rewrites) |
| Note | This is the independent truth check the TradeTrap evidence calls for: a break between the internal ledger and the broker halts new books until disposed. |

### 19. Execution Quality Analyst (TCA)

| Field | Value |
|---|---|
| Decision rights | Execution-quality assessment per desk and per strategy family (implementation shortfall vs arrival price, vs quote at send, vs VWAP; market-impact estimates); recommendations to Analysts (order types, zones, timing) and to the Coach; calibration of the firm's cost and slippage model used by calculators and the sim engine |
| Model / effort | `claude-sonnet-5`, `medium`; `claude-opus-5` weekly |
| Triggers | 16:20 daily; weekly; on request from the Recalibration Agent or Risk Officer |
| Inputs | Fills with reference prices, bid/ask at decision, order working logs, feature snapshots, shadow-mode would-be fills |
| Outputs | `TCAReport {per desk/family: shortfall_bps, slippage_r, impact, order-type breakdown, recommendations}`, `CostModelCalibration` (versioned, adopted by the Skill Engineer via PR) |
| Tools | `tca:read_fills`, `tca:report`, `calc:cost`, `skills:request_change`, `memory:*` |
| Skills | `analysing-execution-quality`, `calibrating-cost-model` |
| Forbidden | Placing orders; changing books |


---

## Meetings

| Meeting | Chair | Members | Cadence | Decision |
|---|---|---|---|---|
| Desk meeting | Senior Analyst | Scanner, Ingestor, Execution, Recalibration, Reviewer | Per charter (default daily pre-open + weekly) | Watchlist emphasis, template changes, escalation policy |
| Risk conference | Risk Officer | Analysts and Execution Agents of affected desks; CIO optional | On notice or weekly | Guidance, pauses |
| Investment committee | CIO | Risk Officer, both Compliance Officers, Treasury, Coach, Desk Designer, Validation Reviewer, desk Analysts | Monthly + proposals | Allocations, charters, promotions, retirements, watch-mode governance; compliance officers can block a charter on record |
| Compliance self-audit | CIO (principal officer) | Both Compliance Officers, Books & Records, Operations Engineer | Half-yearly | Audit evidence bundle to the Principal |
| Coaching session | Coach | One desk's roles + Recalibration Agent | Weekly | Playbook and template revisions, lesson adoptions |

## Interaction matrix

| Producer → Consumer | Artefact |
|---|---|
| Stock Scanner → Data Ingestor | Watchlist |
| Data Ingestor → Senior Analyst | DataPack |
| Senior Analyst → Risk Officer → Senior Analyst | StrategyBook → RiskReview |
| Senior Analyst → Execution Agent | Approved StrategyBook (versioned) |
| Execution Agent → tools → broker | OrderAction |
| Execution Agent → Senior Analyst | Escalation |
| Recalibration Agent → Senior Analyst | RevisionRequest |
| Recalibration Agent → Coach | TemplateRecommendations |
| Execution service → Trade Reviewer | Closed dossier + counterfactuals |
| Trade Reviewer → Coach / Recalibration Agent | TradeReview, lessons |
| Coach → all roles | Playbook/template revisions, lesson decisions, evals |
| Research Lab → Desk Designer → CIO | Evidence → Desk proposal → Charter |
| CIO → firm | Allocation, charters, watch-mode governance |
| Senior Analyst → Compliance Officers → Senior Analyst | StrategyBook → ComplianceClearance (per strategy) |
| Detectors → Regulatory Compliance Officer | Surveillance alerts → dispositions/holds |
| Broker → Broker Compliance Officer | RMS rejections → holds/catalogue updates |
| Treasury → desks / Risk Officer | MarginPlan, reduce requests |
| Books & Records → Compliance / CIO | ReconciliationReport (breaks halt new books), PnLAttribution, TaxLedger |
| Execution Quality Analyst → Analysts, Coach, Skill Engineer | TCAReport, CostModelCalibration |
| Ops/Compliance → Principal | Incidents, audits |
| Everyone → Principal | Journal, digest |
