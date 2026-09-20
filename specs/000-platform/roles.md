# Roles — the agent organisation

*Companion to `spec.md`. Each role below becomes a versioned role definition under `agents/<role>/` (`ROLE.md` with frontmatter: model, effort, tools, skills, memory scopes, budget, forbidden actions). The runtime maps a role definition to a Claude Agent SDK `AgentDefinition` (see `plan.md` §4).*

Design rules applied to every role (from `docs/research/2026-09-20-multi-agent-llm-trading-systems.md` and the constitution):

1. A role decides categories, never numbers (constitution I).
2. A role sees only tested, non-degenerate features; never rankings, leaderboards or "top movers" lists (DXRG finding: leaderboards routed 46.5 % of entries).
3. A role's outputs are typed structured objects; an unparseable output becomes a `REVIEW` sentinel.
4. A role has a budget per invocation and per day, a `max_turns`, and a tool allowlist enforced by hooks.
5. A role reads its memory scopes before acting and writes to them after acting.
6. Fine-grained, well-aligned roles beat persona crowds (arXiv 2602.23330); debate is capped at two rounds.

## 0. The Principal (human)

Not an agent. Approves capital gates (G5), constitution amendments, and trading-behaviour changes to roles and skills; performs the daily broker login; reads the daily journal and weekly digest; can invoke any kill level from a signed CLI or the dashboard.

## 1. Desk Head (orchestrator)

| Field | Value |
|---|---|
| Mandate | Run the shift schedule; delegate to roles; collect their structured results; write the daily desk journal; escalate. Never trades, never researches. |
| Model / effort | `claude-sonnet-5`, effort `medium` |
| Triggers | Every scheduled shift (see `operations.md`) |
| Inputs | Shift definition, sleeve registry, governor state, health summary, pending approvals |
| Outputs | `ShiftRun` record; `DeskJournal` entry (markdown + structured summary); escalation messages |
| Tools | `engine:read_*`, `dossiers:list`, `ledger:list`, `memory:read`, `journal:write`, `notify:principal` |
| Skills | `running-shifts`, `writing-desk-journal`, `escalating-incidents` |
| Memory scopes | Read: all role indexes, desk knowledge. Write: desk journal only. |
| Forbidden | Any engine write tool; invoking the Trade Manager outside a candidate event; editing memory of other roles |
| Budget | USD 2 per shift, `max_turns` 30 |

## 2. Market Intelligence Analyst

| Field | Value |
|---|---|
| Mandate | Turn text and calendars into categorical features and a daily brief: catalysts per symbol (event type, direction, novelty, strength bucket), scheduled events (results, expiry, holidays, policy days), regime label derived from code-computed breadth/dispersion/volatility inputs. |
| Model / effort | `claude-haiku-4-5` for bulk catalyst tagging (batch); `claude-sonnet-5` for the brief |
| Triggers | Pre-market shift 08:45 IST; intraday refresh at 12:30 IST; ad hoc on `announcement_burst` event |
| Inputs | NSE announcements (with `published_at`), results calendar, corporate actions, code-computed breadth/dispersion/vol z-scores, prior briefs (embargo-safe) |
| Outputs | `MarketBrief {as_of, regime_label, regime_inputs_ref, event_calendar[], notes}`; `CatalystTag[] {symbol, event_type, direction, novelty, strength_bucket, published_at, source_ref}` |
| Tools | `data:announcements`, `data:calendar`, `features:read`, `brief:write`, `memory:read/write(own)` |
| Skills | `briefing-market`, `tagging-catalysts` |
| Memory scopes | Own role memory; desk knowledge (read) |
| Forbidden | Any mention of a price target, direction call on a symbol beyond the enum, or trade suggestion. Reading dossiers of open trades. |
| Notes | Catalyst tags are features. They enter a sleeve only after passing G4 (`DH2-RSH-008`). The regime label is used for sizing and gating by code, never for direction. |

## 3. Quant Researcher

| Field | Value |
|---|---|
| Mandate | Convert backlog hypotheses into pre-registered trials; run them through the deterministic backtest skill; write trial reports with DSR/N/k/MTRL; propose promotions; maintain the "idea forest" of what has been tried (RD-Agent(Q) pattern). |
| Model / effort | `claude-opus-5`, effort `high` |
| Triggers | Nightly research shift 20:00 IST; weekend long shift; on backlog item assignment |
| Inputs | Hypothesis backlog, trial ledger, desk knowledge (cost model, universe, data catalogue), research memory |
| Outputs | `PreRegistration` (committed file), `TrialReport`, `PromotionProposal {sleeve_spec_ref, gate_id, evidence_refs}`; backlog dispositions |
| Tools | `ledger:*`, `research:run_backtest` (sandboxed), `research:calibrate_zero_alpha`, `data:read`, `git:commit(research/ only)`, `memory:read/write(own)` |
| Skills | `researching-hypotheses`, `preregistering-trials`, `running-backtests`, `reporting-trials`, `proposing-promotion` |
| Memory scopes | Research memory (read/write); desk knowledge (read); dossier reviews (read, embargo-safe) |
| Forbidden | Changing a trial after registration; touching sleeve config; running anything on the trading process; reporting a Sharpe without N and k |
| Budget | USD 10 per shift |

## 4. Validation Reviewer (red team)

| Field | Value |
|---|---|
| Mandate | Adversarially review every promotion proposal and every proposed lesson validation: leakage (look-ahead, vintage), survivorship, cost realism, multiple testing (N, k, zero-alpha comparison), regime coverage, fill assumptions. Can demand a fresh holdout. Signs off or rejects with reason enums. |
| Model / effort | `claude-opus-5`, effort `xhigh` |
| Triggers | On `PromotionProposal`; on `LessonValidationRequest`; weekly audit of the ledger |
| Inputs | Proposal, trial rows, pre-registration files, backtest artefacts, data lineage |
| Outputs | `ReviewVerdict {decision: accept|request_holdout|reject, checks[] {name, pass, evidence_ref}, holdout_window?, reasons: enum[]}` |
| Tools | `ledger:read`, `research:rerun_readonly`, `data:lineage`, `memory:read` |
| Skills | `reviewing-promotions`, `auditing-ledger` |
| Memory scopes | Own role memory; research memory (read) |
| Forbidden | Proposing strategies; editing trials; approving a proposal it authored in any session |
| Notes | The Researcher and Reviewer are never the same session (Anthropic adversarial-verification pattern). Two rounds maximum; the second round is the Researcher's response to the checklist. |

## 5. Portfolio Manager

| Field | Value |
|---|---|
| Mandate | Decide categorical allocation among sleeves within governor bounds: allocation tier per sleeve (`full`, `half`, `quarter`, `off`) chosen from the code-computed feasible set given vol target, correlation matrix, DSR/MTRL progress and capacity. Run the monthly allocation review and the volatility-triggered emergency review (HedgeAgents cadence). |
| Model / effort | `claude-opus-5`, effort `high` |
| Triggers | Monthly (first trading day); emergency when desk realised vol > 2× target or index moves > 3 % in a day; on sleeve promotion to paper |
| Inputs | Sleeve metrics (expectancy, DSR, MTRL, drawdown, correlation), governor outputs, feasible allocation set computed by code |
| Outputs | `AllocationDecision {sleeve_id → tier, rationale, review_id}`; risk-budget request to Principal when exceeding bounds |
| Tools | `engine:read_sleeves`, `engine:feasible_allocations`, `engine:set_allocation_tier` (bounded), `memory:read/write(own)` |
| Skills | `allocating-risk`, `reviewing-portfolio` |
| Memory scopes | Own role memory; desk knowledge |
| Forbidden | Setting any number (capital, risk fraction); changing thresholds; acting between reviews except on the emergency trigger |

## 6. Trade Manager

| Field | Value |
|---|---|
| Mandate | Own every dossier from `candidate` to `closed`. Vet candidates on categorical grounds only; record the thesis and the invalidation conditions from the enumerated list; during the hold, respond to enumerated invalidation events with `close_now` requests where the sleeve's gate allows; keep the dossier narrative complete for the reviewer. |
| Model / effort | `claude-sonnet-5`, effort `medium` (vetting); `claude-opus-5` for `close_now` requests |
| Triggers | `candidate_created` event; `invalidation_event` (catalyst tag on an open symbol, data anomaly, sleeve pause); carry-decision window 15:00 IST |
| Inputs | The dossier (engine section + own past sections + embargo-safe similar trades), the market brief, catalyst tags for the symbol, exposure overlap summary (categorical), data-quality flags. **No prices, no levels, no rankings.** |
| Outputs | `VetVerdict {decision: take|veto, veto_reason: enum|null, thesis, invalidation_conditions: enum[], confidence_bucket}`; `HoldAction {action: hold|close_now, reason: enum}`; dossier section text |
| Tools | `dossiers:read/write(own section)`, `memory:recall_similar_trades`, `engine:accept_candidate`, `engine:veto_candidate`, `engine:request_close(reason enum)` |
| Skills | `vetting-candidates`, `managing-open-trades`, `writing-dossier-narrative` |
| Memory scopes | Dossier sections (own); role memory (validated lessons only in the trading path); desk knowledge |
| Forbidden | Any number; creating candidates; overriding brackets; reading account cash or P&L for the day (constitution II.4); more than one vet per candidate |
| A/B | Its veto is shadow-tested (`DH2-TRD-005`). If the veto fails G4 for a sleeve, the Trade Manager still writes the thesis and narrative but its veto is advisory for that sleeve. |
| Veto reason enum | `results_within_window`, `regulatory_event`, `corporate_action_pending`, `data_anomaly`, `liquidity_class_too_low`, `exposure_overlap`, `sleeve_paused`, `circuit_limit_risk`, `other_documented` |
| Invalidation enum | `adverse_catalyst`, `data_feed_anomaly`, `regulatory_halt`, `sleeve_paused_by_governor`, `principal_instruction` |

## 7. Risk Officer

| Field | Value |
|---|---|
| Mandate | Independent supervision. Reads policy-gate outcomes, governor actions, exposure and correlation reports; explains breaches; may pause a sleeve (level 1) or trigger the desk flat-and-halt (level 2) on enumerated grounds; runs the release kill drill; monitors cost per R and edge-to-cost ratios; reviews the Trade Manager's veto arm statistics. |
| Model / effort | `claude-opus-5`, effort `high` |
| Triggers | Every 30 minutes in market hours (sweep); on `policy_denied_exit`, `reconciliation_mismatch`, `governor_action`, `cost_ratio_breach`; weekly risk review |
| Inputs | Policy outcomes, sleeve metrics, exposure matrix, cost calibration, kill-switch state, incident log |
| Outputs | `RiskAssessment {findings[], actions[] {type: pause_sleeve|desk_halt|none, reason enum}}`; weekly risk section of the digest |
| Tools | `engine:read_risk`, `engine:pause_sleeve(reason)`, `engine:kill(level ≤ 2, reason)`, `engine:drill_kill`, `memory:read/write(own)`, `notify:principal` |
| Skills | `supervising-risk`, `drilling-kill-switch` (`disable-model-invocation: true` outside CI), `reviewing-cost-calibration` |
| Memory scopes | Own role memory; desk knowledge; dossiers (read) |
| Forbidden | Resuming a paused sleeve (operator/Principal only); changing thresholds; sizing decisions |

## 8. Post-Trade Reviewer

| Field | Value |
|---|---|
| Mandate | After each dossier closes, write a structured reflection (rubric) into the dossier; weekly, aggregate reviews into categorical hypotheses for the research backlog and lesson proposals with evidence links. Never changes anything live. |
| Model / effort | `claude-sonnet-5` per-trade; `claude-opus-5` weekly |
| Triggers | `dossier_closed` (batched at 16:30 IST); weekly Saturday shift |
| Inputs | Closed dossier (all sections, engine data, fills, costs, R), sleeve context, prior reviews (embargo-safe) |
| Outputs | `TradeReview {rubric: {thesis_quality, execution_quality, process_adherence, outcome_luck_vs_skill} each 1–5, lesson_candidate?, tags[]}`; `WeeklyReview {hypotheses[] {statement, source_dossiers[], suggested_test}, lesson_proposals[]}` |
| Tools | `dossiers:read/write(review section)`, `backlog:add`, `memory:propose_lesson`, `ledger:read` |
| Skills | `reviewing-trades`, `reviewing-week` |
| Memory scopes | Dossier review sections; role memory (propose only) |
| Forbidden | Proposing parameter values; rating outcome by P&L alone (rubric requires process separation); writing `validated` lessons |

## 9. Operations Engineer

| Field | Value |
|---|---|
| Mandate | Keep the desk running: morning checklist, token freshness and the Principal login reminder, data-quality checks, feed and reconciliation incidents, deploy verification, incident write-ups, health baselines. Executes runbooks; proposes fixes as PRs. |
| Model / effort | `claude-sonnet-5`, effort `medium` |
| Triggers | 07:30 IST checklist; health-check failure after deterministic remediation failed; post-deploy; nightly data QA |
| Inputs | Health endpoints, logs (filtered), metrics, runbooks, incident memory |
| Outputs | `ChecklistResult`, `IncidentReport {symptom, cause_hypothesis, actions_taken, follow_up_pr?}`, Principal notifications |
| Tools | `ops:health`, `ops:logs(read, bounded)`, `ops:run_runbook(name)` (only runbooks listed in the role), `ops:restart_service(allowlist)`, `git:open_pr`, `notify:principal`, `memory:read/write(own)` |
| Skills | `running-morning-checklist`, `checking-data-quality`, `diagnosing-incidents`, `verifying-deploys`, `writing-incident-reports` |
| Memory scopes | Ops memory; desk knowledge |
| Forbidden | Touching orders or positions; editing environment files; deploying (only verifying); any broker login automation |

## 10. Compliance Auditor

| Field | Value |
|---|---|
| Mandate | Weekly audit of SEBI and broker compliance: OPS histogram, static IP, single-session token handling, audit-chain integrity, retention, rule data versions; read new circulars and propose data updates (lot sizes, expiries, freeze limits, square-off times) as PRs with effective dates. |
| Model / effort | `claude-opus-5`, effort `high` |
| Triggers | Weekly Saturday; on `circular_published` feed item |
| Inputs | Audit chain, OPS metrics, rule data tables, circular text |
| Outputs | `ComplianceReport {checks[], findings[], proposed_rule_changes[]}` |
| Tools | `audit:read`, `rules:read`, `git:open_pr(rules/ only)`, `memory:read/write(own)` |
| Skills | `auditing-compliance`, `tracking-circulars` |
| Forbidden | Changing rules directly; any trading tool |

## 11. Developer agents (design-time, not runtime)

The existing Claude Code specialists (system architect, backend, ML, DevOps, QA) implement feature specs. They run on the laptop or in CI, never on the VM, and never hold runtime credentials. Their definitions live in `.claude/agents/` and are outside this organisation chart.

## 12. Interaction matrix

| Producer → Consumer | Artefact | Channel |
|---|---|---|
| Engine → Trade Manager | Candidate (dossier in `candidate`) | `candidate_created` event |
| Market Intel → Trade Manager, Engine | MarketBrief, CatalystTags | Feature store (embargo-safe) |
| Trade Manager → Engine | VetVerdict, HoldAction | Typed tools |
| Engine → Post-Trade Reviewer | Closed dossier | `dossier_closed` event |
| Post-Trade Reviewer → Quant Researcher | Hypotheses | Backlog |
| Quant Researcher → Validation Reviewer | PromotionProposal | Ledger + PR |
| Validation Reviewer → Engine/PM | ReviewVerdict, gate evaluation | Ledger |
| Portfolio Manager → Engine | AllocationDecision (tiers) | Bounded tool |
| Risk Officer → Engine | pause/kill | Tools with reason enums |
| Governor (engine) → Risk Officer, PM, Principal | GovernorAction | Event + alert |
| Operations Engineer → Principal | Login reminder, incidents | Notification channel |
| Desk Head → Principal | Daily journal, weekly digest | Notification channel + dashboard |

## 13. What is deliberately absent

- No "Trader" role that picks entries: entries come from gated signal engines (constitution I, lessons F4).
- No bull/bear debate per trade: debate is reserved for promotion review and allocation, where it is cheap and auditable.
- No persona agents (Buffett, Lynch, …): personas add tokens, not alpha.
- No role can read the day's P&L while making a trading decision (lessons F6).
