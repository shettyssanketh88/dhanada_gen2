# Skills catalogue

*Companion to `roles.md` v2.0. Skills follow the open Agent Skills specification (`SKILL.md` frontmatter; `scripts/`, `references/`, `evals/`; progressive disclosure). Skills are the firm's procedures: they tell a role how to do its job and bundle the deterministic scripts that fetch, compute and record. Skills are written and revised by agents (the Coach and the Skill Engineer) through PRs with evals; the Principal is informed.*

## 1. Conventions

```
skills/<name>/
  SKILL.md        # frontmatter (name, description, allowed-tools, model, effort, metadata{role, version, trading_impact}) + workflow as a checklist, ≤ 500 lines
  scripts/        # deterministic helpers (context assembly, validation, recording); typed args; JSON out; unit tests
  references/     # enums, schemas, playbook excerpts, one level deep
  evals/          # ≥ 3 cases {query, files, expected_behavior[], grader}; graded on state
```

Rules: prompts assembled by scripts contain no anchoring numbers from the system (numbers come from the agent's own calculator calls); external text is labelled as data; every decision skill ends by writing the decision, the instruments used and the forecast to the dossier or memory; every skill's evals run in CI; a skill with `trading_impact: direct` changes only with the Validation Reviewer's verdict.

## 2. Leadership

| Role | Skill | Purpose | Scripts |
|---|---|---|---|
| CIO | `allocating-capital` | Decide desk allocations within the IPS from desk statistics with n/CIs, correlation, capacity | `desk_stats.py`, `apply_allocation.py` |
| CIO | `chartering-desks` | Write/resize/pause/retire a charter from a proposal and committee minutes | `charter.py validate|apply` |
| CIO | `chairing-investment-committee` | Run the meeting: agenda, positions, rounds cap, minutes, decisions | `minutes.py` |
| CIO | `writing-firm-strategy` | Maintain `memory/firm/strategy.md` and the digest's strategy section | — |
| Risk Office | `reviewing-plans` | Assess a plan: exposure, correlation, liquidity, cost per R, Trader calibration, event window; decide approve/modify/reject with expected effect | `plan_context.py`, `review.py validate` |
| Risk Office | `supervising-book` | 30-minute sweep: book, rails proximity, reconciliation, notices | `book_snapshot.py`, `notice.py` |
| Risk Office | `setting-desk-guidance` | Standing guidance per desk (recommended risk per trade, concurrency, correlation limits) | `guidance.py` |
| Risk Office | `running-risk-conference` | Convene affected roles; decide pauses/guidance changes; minutes | `minutes.py` |
| Risk Office | `drilling-kill-switch` | Release drill in paper; `disable-model-invocation: true` outside CI/Principal | `drill.py` |
| Coach | `scoring-decisions` | Read scores; LLM-judge process adherence calibrated against spot checks; write coaching notes | `scores.py`, `judge.py` |
| Coach | `coaching-roles` | Weekly per-desk session: findings, playbook revisions, eval cases, change requests | `coaching_report.py` |
| Coach | `revising-playbooks` | Versioned playbook diff with rationale and evidence; run evals before publish | `playbook.py diff|publish`, `evals.py run` |
| Coach | `curating-lessons` | Adopt/retire lessons with evidence; maintain firm lessons index | `lessons.py` |

## 3. Desk roles

| Role | Skill | Purpose | Scripts |
|---|---|---|---|
| Analyst (Technical) | `scanning-technicals` | Scan the desk universe with structure/volatility/liquidity calculators; file ideas with evidence | `scan_context.py`, `file_idea.py` |
| Analyst (Catalyst) | `reading-catalysts` | Tag announcements/results/corporate actions (batch model), assess relevance to the desk, file ideas | `fetch_announcements.py`, `tag_batch.py`, `file_idea.py` |
| Analyst (Flow) | `reading-flow` | Depth, turnover, relative volume, index/futures context; file ideas | `flow_context.py`, `file_idea.py` |
| Analyst (all) | `filing-ideas` | Idea schema, evidence standards, withdrawal | `file_idea.py validate` |
| Strategist | `forming-theses` | Turn ideas into theses with invalidation and conviction; recall similar theses time-aware | `thesis_context.py`, `thesis.py validate` |
| Strategist | `debating-bull-bear` | Optional two-round bull/bear pass with Analyst sub-sessions; record both | `debate.py` |
| Strategist | `dropping-theses` | Drop with reasons; memory note | — |
| Trader | `planning-trades` | Build the plan: call calculators for candidate stops/targets, cost per R, liquidity; choose; state expected R and probability; cite instruments | `plan_context.py`, `plan.py validate` |
| Trader | `sizing-positions` | Choose R and quantity with `calc:size`, margin, freeze slices, desk guidance | `size_check.py` |
| Trader | `working-orders` | Place and work orders through `exec:*`; handle partials, chases, drops | `order_action.py validate` |
| Trader | `responding-to-risk` | Accept/contest Risk Office modifications; request a chaired resolution | — |
| Position Manager | `managing-positions` | On each event: hold/adjust/scale with reasoning; set subscriptions; keep the dossier current | `position_context.py`, `action.py validate` |
| Position Manager | `deciding-carries` | Carry window: convert or exit, with expected overnight effect stated | `carry_context.py` |
| Position Manager | `exiting-positions` | Exit decisions with reasoning; expected vs mechanical bracket noted | — |
| Desk Reviewer | `reviewing-trades` | Per-role rubric with counterfactuals; lesson proposals | `review_context.py`, `rubric.py validate` |
| Desk Reviewer | `reviewing-desk-week` | Weekly desk review; meeting items; playbook suggestions | `week_aggregate.py` |

## 4. Research Lab

| Role | Skill | Purpose | Scripts |
|---|---|---|---|
| Quant Researcher | `researching-hypotheses` | Choose backlog items; consult idea forest; design | `backlog.py`, `idea_forest.py` |
| Quant Researcher | `preregistering-experiments` | Commit registration before running | `prereg.py validate|commit` |
| Quant Researcher | `running-backtests` | Rule studies and agentic replays through the engine; ledger open/complete | `backtest.py`, `replay_agentic.py`, `ledger.py` |
| Quant Researcher | `reporting-trials` | DSR/PSR/MTRL, N, k, zero-alpha percentile, stability | `stats.py`, `calibrate_zero_alpha.py`, `report.py` |
| Data Steward | `curating-universe` | Point-in-time universe, delistings, snapshots | `universe.py`, `snapshot.py` |
| Data Steward | `defining-features` | Feature definitions and health thresholds | `feature.py define|test` |
| Data Steward | `checking-data-quality` | Nightly DQ; withheld-feature notices | `dq.py` |
| Validation Reviewer | `reviewing-proposals` | Adversarial checklist on desk proposals, playbook revisions, lesson adoptions | `checks.py`, `lookahead_shift.py`, `attribution.py` |
| Validation Reviewer | `auditing-ledger` | Weekly ledger audit | `ledger_audit.py` |
| Desk Designer | `designing-desks` | Compose a proposal with charter, team, playbook v1, self-declared success criteria | `proposal.py validate` |
| Desk Designer | `writing-playbooks` | Playbook structure and standards | — |

## 5. Operations

| Role | Skill | Purpose | Scripts |
|---|---|---|---|
| Operations Engineer | `running-morning-checklist` | Token, egress IP, instrument master, rule tables, feeds, DB/disk; one Principal reminder if no token | `checklist.py`, `notify.py` |
| Operations Engineer | `diagnosing-incidents` | Bounded logs/metrics; runbook selection from allowlist; escalation | `logs.py`, `runbook.py list|run` |
| Operations Engineer | `verifying-deploys` | Image tag, migrations, health, drill result | `verify_deploy.py` |
| Operations Engineer | `writing-incident-reports` | Incident file in ops memory; follow-up PR | `incident.py` |
| Compliance Auditor | `auditing-compliance` | Order-rate histogram, static IP log, token handling, audit chain, retention, rule versions | `ops_histogram.py`, `audit_chain_verify.py`, `rules_check.py` |
| Compliance Auditor | `tracking-circulars` | Read circulars; propose dated rule changes as PRs | `circulars.py`, `rules_pr.py` |
| Skill Engineer | `authoring-skills` | Scaffold with evals first; implement; open PR | wraps `skill-creator` |
| Skill Engineer | `building-calculators` | New `calc:*` with tests and versioning | `calc_scaffold.py` |
| Skill Engineer | `writing-evals` | Eval cases from real failures; state graders | `eval_scaffold.py` |
| Skill Engineer | `releasing` | Release verification checklist; `disable-model-invocation: true` | `release_check.py` |

## 6. Shared

| Skill | Purpose |
|---|---|
| `recalling-memory` | Time-aware recall of similar trades/theses/lessons; logs retrieval |
| `writing-memory` | Append to own memory; propose lessons; secrets/anchoring linter |
| `attending-meetings` | Meeting protocol: stating a position, rounds, minutes |
| `using-firm-tools` | Reference for typed tools and decision schemas (`user-invocable: false`) |

## 7. Evaluation standard

Each skill ships ≥ 3 evals graded on environment state, several from v1 failures:

- `planning-trades`: (a) calculators called and cited, expected R and probability present; (b) plan inside IPS and desk capital; (c) unparseable thesis → `REVIEW`, no order.
- `reviewing-plans`: (a) exposure over guidance → `modify` with reasons; (b) inside guidance → `approve` within deadline; (c) rail-proximity → notice issued.
- `managing-positions`: (a) subscribed milestone → decision with reasoning and expected effect; (b) catalyst event → decision recorded; (c) service restart → prior actions in context.
- `running-backtests`: (a) no experiment id → refused; (b) crash → trial `failed`; (c) result carries N and k.
- `running-morning-checklist`: (a) no token → one reminder; (b) IP mismatch → state and alert; (c) all green → no notification.

pass^5 required for operations, risk and execution-adjacent skills.
