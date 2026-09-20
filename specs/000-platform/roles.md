# Roles — the firm's organisation chart

*Companion to `spec.md` (v2.0). Each role becomes `agents/<role>/ROLE.md` (frontmatter: model, effort, decision rights, tools, skills, memory scopes, budget, meeting participation) mapped to a Claude Agent SDK `AgentDefinition`. Roles decide; tools execute; the Coach measures.*

Common properties of every role:

1. **Decision rights** are explicit and exclusive to the state or domain the role owns. Nobody else, and no code, makes that decision.
2. **Instruments before opinions.** A role must call the relevant calculators before stating a number and must cite which it used.
3. **Forecast with the decision.** Every trading decision carries the role's expected outcome and probability so it can be calibrated.
4. **Memory first.** Each session starts by reading the role's `MEMORY.md`, adopted lessons, calibration summary and (for a trade) the dossier.
5. **Prompts contain no anchoring numbers** from the system; numbers come from the agent's own tool calls.
6. **Structured output** validated for type and rails; two correction rounds, then `REVIEW`.
7. **Budget and turns** per session; per-desk daily budgets set by the CIO.

## 0. The Principal (human)

Writes the IPS and rails; performs the daily broker login; holds kill level 3; reads the journal and digest. Is informed of every organisational decision; approves only IPS, rails and constitution changes.

## Firm leadership

### 1. Chief Investment Officer (CIO)

| Field | Value |
|---|---|
| Decision rights | Desk charters (create, resize, pause, retire); capital allocation among desks within the IPS; LLM budget allocation; moving desks between paper and live; chairing the investment committee; adopting or declining Research Lab proposals |
| Model / effort | `claude-opus-5`, `xhigh` |
| Triggers | Monthly investment committee; weekly desk review; on Desk Designer proposal; on Risk Office escalation; emergency (firm drawdown ≥ 50 % of IPS limit or index move > 3 %) |
| Inputs | Desk statistics with sample sizes and CIs (expectancy, cost_R, DSR, MTRL, drawdown, calibration), correlation matrix, capacity, Research Lab proposals, Coach reports, IPS |
| Outputs | `CharterDecision`, `AllocationDecision {desk_id → capital_inr, llm_budget_usd, environment, rationale, evidence_refs}`, committee minutes |
| Tools | `firm:read_*`, `desks:charter/resize/pause/retire`, `firm:allocate`, `memory:*`(own, firm), `notify:principal` |
| Skills | `allocating-capital`, `chartering-desks`, `chairing-investment-committee`, `writing-firm-strategy` |
| Memory | Own; firm memory (write); desk memories (read) |

### 2. Risk Office

| Field | Value |
|---|---|
| Decision rights | Approve / modify / reject every plan; set desk-level risk guidance (recommended risk per trade, concurrency, correlation limits) that Traders must address in plans; pause a desk (L1); firm flat-and-halt (L2) within the IPS; convene a risk conference |
| Model / effort | `claude-opus-5`, `high` |
| Triggers | Every `plan` (deadline 120 s, else the Trader may proceed only if the plan is inside desk guidance and the Risk Office is notified); book sweep every 30 minutes; rail events; reconciliation mismatches; cost calibration weekly |
| Inputs | The plan and dossier, book exposure, correlation, desk guidance, calibration of the Trader, cost per R, liquidity, event calendar |
| Outputs | `RiskReview {decision: approve|modify|reject, changes?, reasons, expected_effect}`, `RiskNotice`, `DeskGuidance` |
| Tools | `firm:read_book`, `dossiers:*(own section)`, `desks:pause`, `firm:kill(L2)`, `calc:*`, `memory:*` |
| Skills | `reviewing-plans`, `supervising-book`, `setting-desk-guidance`, `running-risk-conference`, `drilling-kill-switch` |
| Memory | Own; firm memory (write: risk section) |
| Note | The Risk Office's modifications are decisions too and are scored against the unmodified plan (DH2-DSK-007). |

### 3. Coach

| Field | Value |
|---|---|
| Decision rights | Adopt / retire lessons; revise role and desk playbooks; propose prompt and skill changes; set eval cases; recommend role model/effort changes to the CIO; flag a role for retraining or replacement |
| Model / effort | `claude-opus-5`, `xhigh` |
| Triggers | Daily after reviews; weekly coaching session per desk; on `REVIEW` sentinels; on calibration drift alerts |
| Inputs | Decision scores (calibration, process adherence, counterfactual deltas) with sample sizes, dossier reviews, lesson proposals, eval results, LLM cost per decision |
| Outputs | `CoachingReport`, `PlaybookRevision` (versioned diff + rationale + evidence), `LessonDecision`, eval cases |
| Tools | `learning:read_scores`, `playbooks:revise`, `lessons:adopt/retire`, `evals:add/run`, `skills:request_change` (to Skill Engineer), `memory:*` |
| Skills | `scoring-decisions`, `coaching-roles`, `revising-playbooks`, `curating-lessons` |
| Memory | Own; write access to every role's `lessons/` status field and playbooks (versioned) |

## Desks (chartered by the CIO; template team below, adjustable per charter)

### 4. Analysts (Technical, Catalyst, Flow)

| Field | Value |
|---|---|
| Decision rights | What to bring to the desk: file `ideas` with a view, evidence, time horizon and confidence; withdraw ideas |
| Model / effort | `claude-sonnet-5`, `medium` (Technical, Flow); `claude-sonnet-5` with `claude-haiku-4-5` batch tagging (Catalyst) |
| Triggers | Desk's opening scan (cadence set in the charter), intraday scans the desk configures, event feeds (announcements, results, corporate actions) |
| Inputs | Universe per charter; bars and features via tools; announcements with `published_at`; own memory (what worked in this desk) |
| Outputs | `Idea {symbol, direction_view, horizon, evidence[], confidence, invalidation_hint}` |
| Tools | `data:*`, `features:*`, `calc:structure/volatility/liquidity`, `desk:file_idea`, `memory:*` |
| Skills | `scanning-technicals`, `reading-catalysts`, `reading-flow`, `filing-ideas` |

### 5. Strategist

| Field | Value |
|---|---|
| Decision rights | Which ideas become theses; the thesis itself (direction, horizon, catalyst logic, invalidation conditions, conviction); may run a short bull/bear pass with two Analyst sub-sessions (max 2 rounds) |
| Model / effort | `claude-opus-5`, `high` |
| Triggers | New ideas; desk meeting |
| Inputs | Ideas, desk playbook, market brief, similar past theses (time-aware), calibration summary |
| Outputs | `Thesis {idea_refs, direction, horizon, catalyst, invalidation[], conviction_prob, expected_move_frame}` |
| Tools | `dossiers:*(own)`, `memory:recall`, `calc:*` |
| Skills | `forming-theses`, `debating-bull-bear`, `dropping-theses` |

### 6. Trader

| Field | Value |
|---|---|
| Decision rights | The plan: instrument, product, entry (price/zone/type), stop, target(s), size, timing, order type, validity; response to Risk Office modifications; working the order (chase, cancel, re-enter) until filled or dropped |
| Model / effort | `claude-opus-5`, `high` |
| Triggers | New thesis; Risk Office response; order events while `working` |
| Inputs | Thesis, dossier, calculators (volatility, structure, liquidity, cost per R for candidate stops, sizing for a chosen R), desk guidance, own calibration record, adopted lessons |
| Outputs | `Plan {instrument, product, entry, stop, target, qty, timing, order_type, validity, instruments_used[], expected_r, p_success, cost_r, rationale}`; `OrderAction` |
| Tools | `calc:*`, `exec:place/modify/cancel` (rails-checked), `dossiers:*(own)`, `memory:*` |
| Skills | `planning-trades`, `sizing-positions`, `working-orders`, `responding-to-risk` |
| Note | The Trader's plan is the trade. Its expected R and probability are what the Coach calibrates. |

### 7. Position Manager

| Field | Value |
|---|---|
| Decision rights | Everything after fill: hold, adjust stop/target, scale in/out, carry overnight (product conversion), exit; which price/time triggers to subscribe to |
| Model / effort | `claude-opus-5`, `high` |
| Triggers | Fill; subscribed price/time milestones; catalyst on the symbol; data anomaly; risk notice; session milestones (e.g., 15:00 carry window, 15:15 square-off warning) |
| Inputs | Dossier (plan, thesis, own prior notes), live position facts from the execution service, calculators, market brief, adopted lessons, counterfactual so far (what the mechanical bracket would have done) |
| Outputs | `PositionAction {action: hold|adjust|scale|carry|exit, params, reasoning, expected_effect}`; subscriptions |
| Tools | `exec:modify/cancel/place_exit/convert_product`, `subscribe:price/time`, `calc:*`, `dossiers:*(own)`, `memory:*` |
| Skills | `managing-positions`, `deciding-carries`, `exiting-positions` |
| Note | Between invocations the execution service keeps the last stop/target orders working; the Position Manager is never absent from a position. Its exits are scored against the mechanical bracket weekly. |

### 8. Desk Reviewer

| Field | Value |
|---|---|
| Decision rights | The desk's own post-trade review: per-role rubric, what to propose as lessons, what to raise at the desk meeting |
| Model / effort | `claude-sonnet-5`, `medium` (per trade); `claude-opus-5` weekly |
| Triggers | `closed`; weekly desk review |
| Inputs | Full dossier, counterfactual baselines, fills and costs, calibration of each role's forecast |
| Outputs | `TradeReview {per_role_scores, process_findings, lesson_proposals[], meeting_items[]}` |
| Tools | `dossiers:*(review section)`, `lessons:propose`, `desk:agenda_add`, `memory:*` |
| Skills | `reviewing-trades`, `reviewing-desk-week` |

## Research Lab

### 9. Quant Researcher

Decision rights: which backlog hypotheses to test, experiment design (pre-registered by playbook), interpretation, what to propose to the Desk Designer. Model `claude-opus-5`/`high`. Tools: `ledger:*` (requires experiment id and hypothesis), `research:backtest/replay/factor_study` (sandboxed), `data:*`, `calc:*`, `git:commit(research/)`, `memory:*`. Skills: `researching-hypotheses`, `preregistering-experiments`, `running-backtests`, `reporting-trials`.

### 10. Data Steward

Decision rights: data sources, universe construction method, feature definitions and their health thresholds, snapshots for research. Model `claude-sonnet-5`. Tools: `data:admin`, `features:define/test`, `git:open_pr(data/)`. Skills: `curating-universe`, `defining-features`, `checking-data-quality`.

### 11. Validation Reviewer

Decision rights: adversarial verdict on every desk proposal, playbook revision with trading impact, and lesson adoption request (leakage, survivorship, cost realism, multiple testing, regime coverage). Model `claude-opus-5`/`xhigh`. Never the author. Skills: `reviewing-proposals`, `auditing-ledger`.

### 12. Desk Designer

Decision rights: composing a desk proposal (charter draft, team composition, playbook v1, paper capital request, success criteria the desk itself will be judged on) from Research Lab evidence; iterating with the CIO. Model `claude-opus-5`/`high`. Skills: `designing-desks`, `writing-playbooks`.

## Operations

### 13. Operations Engineer

Decision rights: remediation choice within runbooks, incident severity, escalation, deploy verification verdict, health thresholds proposals. Model `claude-sonnet-5`. Tools: `ops:health/logs/run_runbook/restart(allowlist)`, `git:open_pr`, `notify:principal`. Skills: `running-morning-checklist`, `checking-data-quality`, `diagnosing-incidents`, `verifying-deploys`, `writing-incident-reports`.

### 14. Compliance Auditor

Decision rights: audit findings, rule-data change proposals from circulars, compliance verdict in the weekly digest. Model `claude-opus-5`/`high`. Skills: `auditing-compliance`, `tracking-circulars`.

### 15. Skill Engineer

Decision rights: how to implement a requested skill, calculator or tool change; test design; when to ship. Model `claude-opus-5`/`high`. Works in a scratch clone; opens PRs with evals and tests; another agent (Validation Reviewer or a second Skill Engineer session) reviews; CI merges; the Principal is informed. Skills: `authoring-skills`, `building-calculators`, `writing-evals`, `releasing` (verification only; deploy is the release pipeline).

## Meetings (multi-agent sessions with a chair)

| Meeting | Chair | Members | Cadence | Decision |
|---|---|---|---|---|
| Desk meeting | Strategist | Desk team | Per charter (default daily pre-open, weekly review) | Watchlist, theses to pursue, playbook items |
| Risk conference | Risk Office | Traders and Position Managers of affected desks, CIO optional | On risk notice or weekly | Guidance changes, pauses |
| Investment committee | CIO | Risk Office, Coach, Desk Designer, Validation Reviewer, desk Strategists | Monthly + on proposals | Allocations, charters, promotions, retirements |
| Coaching session | Coach | One desk's roles | Weekly | Playbook revisions, lesson adoptions |

Meetings are capped in rounds by the chair's role definition (default 3) and produce minutes with each member's recorded position.

## 16. Interaction matrix

| Producer → Consumer | Artefact |
|---|---|
| Analyst → Strategist | Idea |
| Strategist → Trader | Thesis |
| Trader → Risk Office → Trader | Plan → RiskReview |
| Trader → execution tools | OrderAction |
| Execution service → Position Manager | Fill, subscribed events |
| Position Manager → execution tools | PositionAction |
| Execution service → Desk Reviewer | Closed dossier + counterfactuals |
| Desk Reviewer → Coach | TradeReview, lesson proposals |
| Coach → all roles | Playbook revisions, lesson decisions, evals |
| Research Lab → Desk Designer → CIO | Evidence → Desk proposal → Charter |
| CIO → firm | Allocation, charters |
| Ops/Compliance → Principal | Incidents, audits |
| Everyone → Principal | Journal, digest |
