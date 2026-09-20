# Skills catalogue

*Companion to `roles.md`. Skills follow the open Agent Skills specification (`SKILL.md` with frontmatter; `scripts/`, `references/`, `assets/`; progressive disclosure) and Anthropic's best practices: third-person descriptions with trigger words, gerund names, SKILL.md under 500 lines, deterministic work in scripts, evaluations written before documentation, `disable-model-invocation: true` on anything money-adjacent. Source: `docs/research/2026-09-20-agent-engineering-state-of-the-art.md` §1.*

## 1. Conventions

```
skills/<name>/
  SKILL.md              # frontmatter + workflow (checklist form), ≤ 500 lines
  scripts/              # deterministic Python; each script has --help, typed args, JSON out, unit tests
  references/           # gate register excerpts, schemas, enum lists (one level deep)
  evals/                # ≥ 3 eval cases: {query, files, expected_behavior[], grader}
```

Frontmatter fields used: `name`, `description`, `allowed-tools`, `disable-model-invocation`, `user-invocable`, `model`, `effort`, `hooks`, `metadata: {role, version, trading_impact: none|indirect|direct}`.

Rules:

1. A skill with `trading_impact: direct` changes only with Principal approval (DH2-ORG-002) and carries `disable-model-invocation: true` unless it is the role's core workflow, in which case the role's tool allowlist is the guard.
2. Every numeric computation lives in a script. SKILL.md may say "run `scripts/size_check.py`", never "compute the stop as …".
3. Every skill's evals run in CI (promptfoo with the Claude Agent SDK provider, or the SDK's own harness) and grade **state** (a ledger row exists, a section was written, no order was placed), not the transcript.
4. Prompts assembled by skills contain no anchoring numbers; features are passed as z-scores, buckets or enums produced by scripts.
5. Scripts that read external text (announcements) treat it as data and never as instructions; SKILL.md says so explicitly.

## 2. Desk Head

| Skill | Purpose | Scripts | Trading impact |
|---|---|---|---|
| `running-shifts` | Execute a shift definition: check preconditions, invoke roles, collect structured results, record the shift run | `shift_preflight.py`, `record_shift.py` | none |
| `writing-desk-journal` | Compose the daily journal from structured inputs (sleeve metrics, incidents, costs, approvals) | `journal_data.py` (assembles numbers), `journal_lint.py` (no unapproved claims) | none |
| `escalating-incidents` | Decide escalation tier from enumerated severity; notify Principal | `notify.py` | none |

## 3. Market Intelligence Analyst

| Skill | Purpose | Scripts | Trading impact |
|---|---|---|---|
| `briefing-market` | Produce `MarketBrief` from code-computed regime inputs and the event calendar | `regime_inputs.py` (breadth, dispersion, vol z-scores), `calendar.py` | indirect (feature) |
| `tagging-catalysts` | Batch-classify NSE announcements into `CatalystTag` enums with `published_at`; masked symbol ids during historical runs | `fetch_announcements.py`, `tag_batch.py` (calls the classification model with a fixed prompt version; validates against the enum schema), `feature_health.py` | indirect (feature, G4-gated) |

## 4. Quant Researcher

| Skill | Purpose | Scripts | Trading impact |
|---|---|---|---|
| `researching-hypotheses` | Pick backlog items, consult the idea forest, draft a falsifiable plan | `backlog.py`, `idea_forest.py` | none |
| `preregistering-trials` | Write and commit `preregistration.md`; validate against schema; compute grid size N | `prereg.py validate|commit` | none |
| `running-backtests` | Run the simulation kernel for a registered experiment in the sandbox; open/complete ledger rows; fail closed | `backtest.py --experiment` (refuses without registration), `ledger.py open|complete|fail` | none |
| `reporting-trials` | Produce `TrialReport` with DSR/PSR/MTRL, N, k, cost_R, zero-alpha percentile, stability table | `stats.py`, `calibrate_zero_alpha.py`, `report.py` | none |
| `proposing-promotion` | Assemble a `PromotionProposal` with evidence refs and the sleeve spec draft | `proposal.py validate` | indirect (enters review) |

## 5. Validation Reviewer

| Skill | Purpose | Scripts | Trading impact |
|---|---|---|---|
| `reviewing-promotions` | Run the 12-check checklist (`research.md` §8); produce `ReviewVerdict` | `checks.py` (each check is a function returning pass/fail + evidence), `lookahead_shift.py`, `attribution.py` | indirect (gate input) |
| `auditing-ledger` | Weekly ledger audit: trials left `running`, registrations without runs, N/k anomalies | `ledger_audit.py` | none |

## 6. Portfolio Manager

| Skill | Purpose | Scripts | Trading impact |
|---|---|---|---|
| `allocating-risk` | Choose allocation tiers from the governor's feasible set with correlation and MTRL context | `feasible_set.py`, `apply_tiers.py` (bounded engine tool) | direct (bounded) |
| `reviewing-portfolio` | Monthly and emergency review: correlation matrix, DSR progress, capacity, decay flags | `portfolio_report.py` | indirect |

## 7. Trade Manager

| Skill | Purpose | Scripts | Trading impact |
|---|---|---|---|
| `vetting-candidates` | Read the dossier (engine section, similar trades embargo-safe, brief, catalyst tags for the symbol, exposure overlap enum); output `VetVerdict` | `dossier_context.py` (assembles the categorical context; strips numbers), `verdict.py validate` | direct (A/B-measured) |
| `managing-open-trades` | Respond to invalidation events with `HoldAction`; record hold notes | `event_context.py`, `hold_action.py validate` | direct (enumerated reasons only) |
| `writing-dossier-narrative` | Append thesis/notes to own section; summarise for the reviewer at close | `write_section.py` | none |

`vetting-candidates` SKILL.md contains the veto-reason enum and the explicit instruction that a `take` is the default when no enumerated veto applies (v1 lesson: structural "don't trade" biases). It never shows day P&L, rankings, or prices.

## 8. Risk Officer

| Skill | Purpose | Scripts | Trading impact |
|---|---|---|---|
| `supervising-risk` | Sweep policy outcomes, exposures, governor actions, reconciliation state; produce `RiskAssessment`; act within enumerated authority | `risk_snapshot.py`, `act.py pause|kill` (calls bounded engine tools) | direct (pause/kill) |
| `drilling-kill-switch` | Run the three-level drill in paper; verify flatten; record | `drill.py` | direct; `disable-model-invocation: true` (CI and Principal only) |
| `reviewing-cost-calibration` | Weekly cost_R per sleeve, edge-to-cost ratios, spread statistics | `cost_report.py` | indirect (feeds DH2-RSK-005 auto-pause) |
| `reviewing-veto-arm` | Weekly veto vs shadow expectancy difference with t-stat | `veto_ab.py` | indirect (G4 evidence) |

## 9. Post-Trade Reviewer

| Skill | Purpose | Scripts | Trading impact |
|---|---|---|---|
| `reviewing-trades` | Per closed dossier: rubric (thesis, execution, process, luck vs skill), lesson candidate | `review_context.py`, `rubric.py validate` | none |
| `reviewing-week` | Aggregate reviews; propose hypotheses to the backlog and lessons (status `hypothesis`) | `week_aggregate.py`, `backlog.py add`, `propose_lesson.py` | none |

## 10. Operations Engineer

| Skill | Purpose | Scripts | Trading impact |
|---|---|---|---|
| `running-morning-checklist` | Token present, egress IP matches, instrument master fresh, feeds healthy, rule tables valid for today, disk/DB health; remind Principal to log in | `checklist.py` (each check deterministic), `notify.py` | indirect |
| `checking-data-quality` | Feature degeneracy tests, bar completeness, announcement feed freshness, universe as-of consistency | `dq.py` | indirect (withholds degenerate features) |
| `diagnosing-incidents` | Bounded log/metric reads; runbook selection; escalation | `logs.py --window --filter`, `runbook.py list|run <allowlisted>` | none |
| `verifying-deploys` | Post-deploy: image tag, migrations applied, health, kill drill result | `verify_deploy.py` | none |
| `writing-incident-reports` | Structured incident write-up into ops memory; open follow-up PR | `incident.py` | none |

Runbooks are scripts under `skills/diagnosing-incidents/scripts/runbooks/` with an allowlist in the role definition (restart a stalled ticker, re-run instrument fetch, re-run reconciliation, rotate logs). Anything else escalates.

## 11. Compliance Auditor

| Skill | Purpose | Scripts | Trading impact |
|---|---|---|---|
| `auditing-compliance` | OPS histogram, static IP log, single-session check, audit-chain verification, retention, rule-table versions | `ops_histogram.py`, `audit_chain_verify.py`, `rules_check.py` | none |
| `tracking-circulars` | Read new SEBI/NSE/Zerodha circulars; propose rule-table changes with effective dates as a PR | `circulars.py fetch`, `rules_pr.py` | indirect (rules via PR) |

## 12. Shared skills

| Skill | Purpose | Scripts |
|---|---|---|
| `recalling-memory` | Embargo-safe retrieval of similar trades and in-scope lessons; logs the retrieval | `recall.py --as-of` |
| `writing-memory` | Append to own role memory; propose lessons; lint for secrets and numbers | `memory_write.py`, `memory_lint.py` |
| `reading-desk-knowledge` | Locate reference documents and rule tables | `desk_index.py` |
| `using-engine-tools` | Reference for the typed engine tools and their reason enums (background knowledge, `user-invocable: false`) | — |

## 13. Developer-side skills (design time)

| Skill | Purpose |
|---|---|
| `implementing-feature-spec` | Read `specs/NNN/`, create tasks, implement with tests, cite requirement ids in the PR |
| `writing-feature-spec` | Create `specs/NNN-<name>/` from a backlog item with EARS requirements and acceptance scenarios |
| `authoring-skill` | Scaffold a skill with evals first (wraps `skill-creator`) |
| `releasing` | Tag, CI verification, deploy runbook, kill drill evidence; `disable-model-invocation: true` |

## 14. Skill evaluation standard

Each skill ships ≥ 3 evals derived from real v1 failures where possible:

- `vetting-candidates`: (a) results announcement in 45 minutes → `veto: results_within_window`; (b) quiet market, no catalyst, clean data → `take` (guards against "decline everything"); (c) unparseable engine payload → `REVIEW`, no tool call.
- `running-backtests`: (a) missing registration → exit non-zero before data load; (b) extra parameter → refused; (c) crash mid-run → trial marked `failed`.
- `running-morning-checklist`: (a) no token → one Principal reminder, desk `awaiting_login`; (b) IP mismatch → `broker_state` set, alert; (c) all green → checklist complete, no notification.
- `supervising-risk`: (a) desk drawdown at limit → level-2 kill via tool with reason; (b) exit denied by policy → alert, no other action; (c) normal sweep → no action, assessment written.

Evals grade environment state; pass^k (k = 5) is required for ops and risk skills.
