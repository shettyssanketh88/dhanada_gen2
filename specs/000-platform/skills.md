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
| Risk Officer | `supervising-book` | 30-minute sweep: book, rails proximity, reconciliation, notices | `book_snapshot.py`, `notice.py` |
| Risk Officer | `setting-desk-guidance` | Standing guidance per desk (recommended risk per trade, concurrency, correlation limits) | `guidance.py` |
| Risk Officer | `running-risk-conference` | Convene affected roles; decide pauses/guidance changes; minutes | `minutes.py` |
| Risk Officer | `drilling-kill-switch` | Release drill in paper; `disable-model-invocation: true` outside CI/Principal | `drill.py` |
| Coach | `scoring-decisions` | Read scores; LLM-judge process adherence calibrated against spot checks; write coaching notes | `scores.py`, `judge.py` |
| Coach | `coaching-roles` | Weekly per-desk session: findings, playbook revisions, eval cases, change requests | `coaching_report.py` |
| Coach | `revising-playbooks` | Versioned playbook diff with rationale and evidence; run evals before publish | `playbook.py diff|publish`, `evals.py run` |
| Coach | `curating-lessons` | Adopt/retire lessons with evidence; maintain firm lessons index | `lessons.py` |

## 3. Pipeline roles (per desk)

| Role | Skill | Purpose | Scripts |
|---|---|---|---|
| Stock Scanner | `scanning-market` | Scan the desk universe with structure/volatility/liquidity/catalyst/flow tools; pick stocks with reasons | `scan_context.py`, `watchlist.py validate|set` |
| Stock Scanner | `requesting-screens` | Read the universe screen output; ask the Skill Engineer for a new or modified screen with evidence from scan-quality scores | `screen_output.py`, `screen_request.py` |
| Stock Scanner | `prioritising-watchlist` | Priority and horizon hints; intraday additions/removals | `watchlist.py` |
| Data Ingestor | `building-data-packs` | Select sources and granularity; assemble the pack; flag quality issues and excluded windows | `datapack.py build|validate`, `dq.py` |
| Data Ingestor | `checking-data-quality` | Nightly DQ for the research universe; feature health; withheld-feature notices | `dq.py` |
| Data Ingestor | `commissioning-data-sources` | Propose a new source via PR to the Skill Engineer | `source_request.py` |
| Senior Analyst | `writing-strategy-books` | Read the pack, templates, calibration, prior books; call calculators; write the book with crisp/judgment conditions, levels, sizes, priorities, rules, expected R and p | `book_context.py`, `book.py validate|draft`, `expr_check.py` |
| Senior Analyst | `resolving-escalations` | Decide the uncovered situation; issue a new version within deadline | `escalation_context.py`, `book.py revise` |
| Senior Analyst | `revising-books` | Accept/amend/decline recalibration requests with reasons | `revision.py` |
| Risk Officer | `reviewing-strategy-books` | Per-strategy approve/modify/reject; cost per R, exposure, correlation, event windows; auto-approval rules | `book_review_context.py`, `review.py validate` |
| Execution Agent | `watching-and-executing` | On watch events: confirm the match against the book, resolve priority/exclusivity, place/modify orders exactly as specified, record reasoning; Agent Watch mode: evaluate digests and judgment conditions continuously | `event_context.py`, `action.py validate`, `digest_reader.py` |
| Execution Agent | `working-orders` | Partials, chases within book instructions, cancellations, protective-order diffs on version reload | `order_action.py` |
| Execution Agent | `escalating-to-analyst` | Recognise uncovered situations; escalate with context; keep protection working | `escalate.py` |
| Recalibration Agent | `recalibrating-strategies` | Intraday and nightly: strategy-family stats vs expectation; regime assessment; revision requests with evidence | `family_stats.py`, `request.py validate` |
| Recalibration Agent | `assessing-regime` | Regime assessment from code-computed inputs | `regime_context.py` |
| Recalibration Agent | `reporting-strategy-families` | Nightly template recommendations to the Coach; watch-mode report reading | `family_report.py`, `watch_report.py` |
| Trade Reviewer | `reviewing-pipeline-trades` | Per-agent rubric with counterfactuals per version and mode; lesson proposals | `review_context.py`, `rubric.py validate` |
| Trade Reviewer | `reviewing-desk-week` | Weekly desk review; meeting items | `week_aggregate.py` |

## 4. Research Lab

| Role | Skill | Purpose | Scripts |
|---|---|---|---|
| Quant Researcher | `researching-hypotheses` | Choose backlog items; consult idea forest; design | `backlog.py`, `idea_forest.py` |
| Quant Researcher | `preregistering-experiments` | Commit registration before running | `prereg.py validate|commit` |
| Quant Researcher | `running-backtests` | Rule studies and agentic replays through the engine; ledger open/complete | `backtest.py`, `replay_agentic.py`, `ledger.py` |
| Quant Researcher | `reporting-trials` | DSR/PSR/MTRL, N, k, zero-alpha percentile, stability | `stats.py`, `calibrate_zero_alpha.py`, `report.py` |
| Data Ingestor (research universe) | `curating-universe` | Point-in-time universe, delistings, snapshots | `universe.py`, `snapshot.py` |
| Data Ingestor (research universe) | `defining-features` | Feature definitions and health thresholds | `feature.py define|test` |
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
| Operations Engineer | `owning-security-and-kill-switch` | Secrets/token lifecycle, static-IP health, prompt-injection filtering on ingested text, drill and restart procedure | `secrets_audit.py`, `ip_health.py`, `injection_filter.py` |
| Skill Engineer | `authoring-skills` | Scaffold with evals first; implement; open PR | wraps `skill-creator` |
| Skill Engineer | `building-calculators` | New `calc:*` with tests and versioning | `calc_scaffold.py` |
| Skill Engineer | `writing-evals` | Eval cases from real failures; state graders | `eval_scaffold.py` |
| Skill Engineer | `releasing` | Release verification checklist; `disable-model-invocation: true` | `release_check.py` |

## 5a. Compliance and control (see `compliance.md`)

| Role | Skill | Purpose | Scripts |
|---|---|---|---|
| Regulatory Compliance Officer | `preclearing-books-regulatory` | Per-strategy clear/conditions/block on A1–A19 grounds from `compliance:preclear` findings | `preclear_context.py`, `decision.py validate` |
| Regulatory Compliance Officer | `surveilling-trading` | Dispose detector alerts (OTR, cancel ratios, self-match, volume share, closing window, position limits); holds | `alerts.py`, `hold.py` |
| Regulatory Compliance Officer | `closing-compliance-day` | EOD close report: tags, OTR, penalties, obligations, E-4, disclosures, retention | `eod_close.py` |
| Regulatory Compliance Officer | `auditing-compliance` | Weekly and half-yearly self-audit; evidence bundle | `audit_chain_verify.py`, `rules_check.py`, `evidence_bundle.py` |
| Regulatory Compliance Officer | `tracking-circulars` | Poll SEBI/NSE/BSE; diff catalogue; PR with effective dates | `circulars.py`, `rules_pr.py` |
| Regulatory Compliance Officer | `classifying-tax-ledger` | Income classification rules, STT rates, turnover method | `tax_rules.py` |
| Both officers | `maintaining-rule-catalogue` | Catalogue schema, sources, effective dates, verification-status resolution | `catalogue.py validate|diff` |
| Broker Compliance Officer | `preclearing-books-broker` | Per-strategy decision on B1–B10 grounds (products, RMS, API, terms) | `preclear_context.py`, `decision.py validate` |
| Broker Compliance Officer | `handling-rms-rejections` | Classify rejection bursts; hold; catalogue update | `rejections.py` |
| Broker Compliance Officer | `refreshing-broker-feeds` | MIS list, haircuts, freeze quantities, timings, lot sizes weekly | `feeds.py refresh` |
| Broker Compliance Officer | `tracking-broker-updates` | Bulletin, Z-Connect, Kite forum; terms-of-use watch (NC-7) | `broker_updates.py` |
| Treasury & Settlement Manager | `planning-margin-and-cash` | Daily plan per desk; funds/pledge actions; expected penalties | `margin_plan.py`, `basket_margin.py` |
| Treasury & Settlement Manager | `monitoring-peak-margin` | 5-minute headroom incl. MTM; reduce requests | `peak_margin.py` |
| Treasury & Settlement Manager | `managing-settlement-obligations` | T+1 pay-in, short-delivery, E-4 ramps, quarterly settlement pre-funding | `settlement.py` |
| Treasury & Settlement Manager | `managing-collateral` | Pledge/unpledge within the 50 % cash rule and haircuts | `collateral.py` |
| Books & Records Agent | `reconciling-books` | Start-of-day, 15:35, 16:05 and contract-note reconciliation; break classification and disposition; hold requests | `recon.py run|dispose` |
| Books & Records Agent | `attributing-pnl` | Daily attribution per desk | `attribution.py` |
| Books & Records Agent | `keeping-tax-ledger` | STT, classification, turnover, 44AB alarm | `tax_ledger.py` |
| Execution Quality Analyst | `analysing-execution-quality` | Implementation shortfall vs arrival/quote/VWAP per fill; per desk and family | `tca.py` |
| Execution Quality Analyst | `calibrating-cost-model` | Versioned cost/slippage model from realised fills; PR to Skill Engineer | `cost_calibration.py` |

## 6. Shared

| Skill | Purpose |
|---|---|
| `recalling-memory` | Time-aware recall of similar trades/theses/lessons; logs retrieval |
| `writing-memory` | Append to own memory; propose lessons; secrets/anchoring linter |
| `attending-meetings` | Meeting protocol: stating a position, rounds, minutes |
| `using-firm-tools` | Reference for typed tools and decision schemas (`user-invocable: false`) |

## 7. Evaluation standard

Each skill ships ≥ 3 evals graded on environment state, several from v1 failures:

- `writing-strategy-books`: (a) calculators called and cited; every strategy has crisp or judgment condition, levels, size, priority, expected R and p; (b) book inside IPS and desk capital; expressions parse; (c) unusable data pack → `REVIEW`, no book.
- `reviewing-strategy-books`: (a) cost per R below floor → `modify` with reasons; (b) inside guidance → `approve` within deadline; (c) auto-approval rule applied and recorded.
- `watching-and-executing`: (a) match → order exactly per book, reasoning recorded; (b) conflict unresolved by priority → escalate, no order; (c) version reload → protective-order diff applied; (d) Agent Watch digest with a judgment condition → decision with reasoning; (e) shadow mode → no broker order.
- `recalibrating-strategies`: (a) family failing with n ≥ threshold in its playbook → revision request with evidence; (b) small n → no request, note recorded; (c) regime shift → assessment written.
- `running-backtests`: (a) no experiment id → refused; (b) crash → trial `failed`; (c) result carries N and k.
- `running-morning-checklist`: (a) no token → one reminder; (b) IP mismatch → state and alert; (c) all green → no notification.

pass^5 required for operations, risk, compliance, treasury, reconciliation and execution-adjacent skills.

- `preclearing-books-regulatory` / `-broker`: (a) ASM-listed stock with MIS → `block` with rule ids; (b) CNC with 100 % margin → `clear_with_conditions`; (c) findings empty → `clear` within deadline.
- `reconciling-books`: (a) broker shows a position the ledger lacks → break, hold request; (b) clean → `clean: true`; (c) contract-note cost mismatch → journal adjustment with reason, never a fill rewrite.
- `planning-margin-and-cash`: (a) E-4 stock futures → reduce/fund request; (b) headroom < 20 % → reduce request to the desk with the smallest expectancy; (c) quarterly settlement in 3 days → pre-fund note to the Principal.
