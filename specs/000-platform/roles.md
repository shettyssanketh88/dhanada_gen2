# Roles — the firm's organisation chart

*Companion to `spec.md` v2.1. Each role becomes `agents/<role>/ROLE.md` (frontmatter: model, effort, decision rights, tools, skills, memory scopes, budget, meeting participation) mapped to a Claude Agent SDK `AgentDefinition`. Roles decide; tools execute; the Coach and the Recalibration Agent measure and revise. The trading pipeline follows the Principal's scenario (`scenario-walkthrough.md`).*

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
| Triggers | After every scan; on data-quality alerts; nightly for the research universe |
| Inputs | Watchlist; data catalogue; feature health; own memory of source reliability |
| Outputs | `DataPack {symbol, as_of, bars[1m,15m,1d] refs, depth, volume_profile, fundamentals, announcements(published_at), results_calendar, corporate_actions, sector_index_context, derivatives_context, quality_flags[], excluded_windows[]}` |
| Tools | `data:*` (read and ingest jobs), `features:test`, `desk:attach_datapack`, `git:open_pr(data/)` for new sources, `memory:*` |
| Skills | `building-data-packs`, `checking-data-quality`, `commissioning-data-sources` |

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
| Decision rights | Approve / modify / reject each strategy in each book version; standing desk guidance (risk per strategy, concurrency, correlation, cost-per-R floor); pause a desk (L1); firm flat-and-halt (L2) within the IPS; auto-approval rules for minor revisions within guidance |
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
Adversarial verdict on desk proposals, template/playbook revisions with trading impact, lesson adoptions, and watch-mode evaluation reports. `claude-opus-5`/`xhigh`. Never the author. Skills: `reviewing-proposals`, `auditing-ledger`.

### 12. Desk Designer
Composes desk proposals (charter, pipeline configuration, Analyst templates v1, self-declared success criteria, paper capital) from evidence; iterates with the CIO. `claude-opus-5`/`high`. Skills: `designing-desks`, `writing-templates`.

(The Data Ingestor covers the Data Steward duties for the research universe at night.)

---

## D. Operations

### 13. Operations Engineer — morning checklist, incidents, deploy verification, runbooks. `claude-sonnet-5`.
### 14. Compliance Auditor — weekly audits, circulars → dated rule PRs. `claude-opus-5`/`high`.
### 15. Skill Engineer — new skills, calculators, features for the expression language, watch improvements; PRs with evals; agent review; Principal informed. `claude-opus-5`/`high`.

---

## Meetings

| Meeting | Chair | Members | Cadence | Decision |
|---|---|---|---|---|
| Desk meeting | Senior Analyst | Scanner, Ingestor, Execution, Recalibration, Reviewer | Per charter (default daily pre-open + weekly) | Watchlist emphasis, template changes, escalation policy |
| Risk conference | Risk Officer | Analysts and Execution Agents of affected desks; CIO optional | On notice or weekly | Guidance, pauses |
| Investment committee | CIO | Risk Officer, Coach, Desk Designer, Validation Reviewer, desk Analysts | Monthly + proposals | Allocations, charters, promotions, retirements, watch-mode governance |
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
| Ops/Compliance → Principal | Incidents, audits |
| Everyone → Principal | Journal, digest |
