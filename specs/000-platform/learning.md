# Learning and research — how the firm gets better

*Companion to `spec.md` v2.0 (DH2-LRN-*). The loop is owned by roles (Desk Reviewer, Coach, Research Lab, Skill Engineer) and instrumented by code (decision scores, counterfactuals, trial ledger). Nothing here is a static gate that decides; the CIO and Coach decide, with the evidence the instruments provide and the Validation Reviewer's adversarial verdict on record.*

## 1. Three loops

| Loop | Cadence | Owner | What changes |
|---|---|---|---|
| **Trade loop** | per trade | Desk Reviewer → Coach | Role calibration records; lesson proposals; per-role coaching notes |
| **Playbook loop** | weekly per desk | Coach (with desk) | Desk and role playbooks (versioned); lesson adoption/retirement; eval cases; prompt/skill change requests |
| **Firm loop** | monthly + on proposal | Research Lab → Desk Designer → Validation Reviewer → investment committee (CIO) | Desk charters, allocations, promotions to live, retirements; new calculators/skills |

## 2. Decision scoring (code-computed instruments)

For every decision recorded on a dossier:

| Score | Definition |
|---|---|
| Calibration | Stated probability vs outcome (Brier, reliability by bucket) and expected R vs realised R, per role, desk, regime, horizon, with n and CIs |
| Counterfactual delta | Realised R minus each baseline: `no_trade` (0), `per_book_version` (each version that governed, replayed over the trade's bars — scores recalibration and escalation resolutions), `per_watch_mode` (the shadow mode's would-be actions simulated), `unmodified_by_risk` (where the Risk Officer modified), `desk_registered` baselines |
| Process adherence | Playbook checklist items evidenced in the section (instruments cited, invalidation stated, forecast given) — computed by a deterministic checker plus an LLM-judge pass (Coach) calibrated against the Principal's spot checks |
| Cost discipline | Plan's stated cost per R vs realised |
| Timeliness | Response latency to events while owning a state |

Scores are appended to `decision_scores` and summarised into each role's `calibration.md` nightly. The Coach sees them with sample sizes; a role sees its own.

## 3. The Coach's protocol (playbook loop)

1. Read the desk's week: scores by role, reviews, lesson proposals, rail events, `REVIEW` sentinels, cost per decision.
2. Decide lesson statuses (`adopted` requires evidence references and, for trading impact, the Validation Reviewer's verdict).
3. Revise playbooks where a pattern has enough support (the Coach states n and the evidence in the revision rationale; the Coach's own playbook says what "enough" means for it and is itself scored: do its revisions improve the role's subsequent scores?).
4. Add or update eval cases derived from real failures; run them; a playbook revision that fails its evals is not published.
5. Request skill or calculator changes from the Skill Engineer.
6. Recommend model/effort changes or role retraining to the CIO.
7. Write the coaching report to desk memory and the digest.

The Coach is scored too: revision → next-period score delta, tracked in its calibration record.

## 4. Research Lab (firm loop)

### 4.1 Backlog
`research/backlog.yaml`: `id, statement, source (reviewer|analyst|cio|principal|researcher), source_refs, universe, horizon, cost_model, status (open|registered|falsified|proposed|adopted|parked), disposition`. Anyone may add; the Researcher decides what to run.

Seed items (evidence in `docs/research/2026-09-07-path-to-edge.md`): cross-sectional mid/small-cap momentum (positional); stocks-in-play opening-range breakouts with wide stops; afternoon range breaks with daily-ATR stops; intraday-to-overnight carry; multi-day holds of intraday setups; NIFTY futures last-30-minute momentum; trend overlay; catalyst-driven event desk; PEAD in small caps; low-vol/quality core. Parked by evidence: sub-15-minute holds; VWAP reversion; gap fades; option selling.

### 4.2 Pre-registration (playbook, enforced only as ledger hygiene)
The Researcher's playbook requires committing `research/experiments/<id>/preregistration.md` (hypothesis, universe, data, splits, parameter grid and its size, aggregation plan, cost model, metrics, kill criteria, masking) before running. The ledger tool requires `experiment_id` and `hypothesis` and records the registration SHA if present; the Validation Reviewer treats a missing or post-dated registration as a failing check. The decision to proceed anyway belongs to the CIO, on record.

### 4.3 Trial ledger and statistics
`research_trials` as before (params, hash, holdout flag, n, expR, t, Sharpe, skew, kurtosis, PSR, DSR at N, SR*, MTRL, max DD, cost_R, N, k, zero-alpha reference, code SHA, data snapshot). Formulas (Bailey & López de Prado) live in `calc:stats` and are pinned by tests. A zero-alpha calibration tool reruns any pipeline on shuffled/synthetic data and reports the percentile of the headline.

### 4.4 Two research modes
- **Rule studies** (large samples): playbook rules expressed as code by the Skill Engineer, run over years of bars.
- **Agentic replays** (cost-bounded): the desk's roles replayed over sampled historical days with masked identifiers and time-aware memory, to evaluate the agentic playbook itself and each role's calibration before a desk goes to paper or live.

### 4.5 Desk proposals
The Desk Designer composes `desks/<proposed_id>/PROPOSAL.md`: charter draft, team, playbook v1, evidence (trials with N/k, agentic replay scores), paper capital request, and the success criteria the desk proposes to be judged by (expectancy, cost_R, DSR/MTRL targets, drawdown tolerance, calibration targets). The Validation Reviewer attaches a checklist verdict (leakage, survivorship, costs, multiple testing, regime coverage, masking, attribution, stability). The investment committee decides; minutes record every member's position.

## 5. Promotion and retirement are committee decisions

There is no threshold table that promotes or retires. The committee sees the desk's own proposed criteria, its statistics with n and CIs, DSR and MTRL progress, the counterfactual record, the Risk Office's view and the Validation Reviewer's verdict, and the CIO decides. Every decision records the evidence it rested on, so the Coach can later score the CIO's decisions (did promoted desks perform as expected?). The IPS caps (max desks live, capital per desk) are the only rails.

## 6. Skills and calculators evolve

A role or the Coach files a `SkillChangeRequest` (what, why, evidence). The Skill Engineer implements it in a scratch clone with evals and tests; a second agent reviews; CI merges; the runtime loads the new version at the next session; the Principal reads it in the digest. Trading-impact changes carry the Validation Reviewer's verdict. Rails cannot be changed this way.

## 7. Masking and leakage discipline

Any LLM-touched historical study masks tickers and shifts dates; all dated data is point-in-time (announcements by `published_at`, fundamentals as filed, universe as of date); the Validation Reviewer's checklist includes a forward-shifted rerun to detect look-ahead; the memory embargo applies in replays.

## 5a. Watch-mode evaluation (ADR-008)

Both watch modes run on every dossier, one governing and one shadow (`spec.md` DH2-EXEC-002). Code computes, per desk and per strategy family, with n and CIs:

| Metric | Definition |
|---|---|
| Fidelity | Share of book-specified actions taken correctly (right strategy, right time window, right parameters) |
| Latency | Seconds from condition satisfied (feature timestamp) to order sent |
| Slippage | Fill vs reference at condition time, per mode |
| Cost | LLM cost per stock-day per mode |
| Escalation quality | Escalations raised vs situations the Trade Reviewer judges should have been escalated (precision/recall) |
| Judgment coverage | Judgment-condition strategies evaluated (Agent Watch only) and their outcomes |
| Outcome delta | Realised R (governing) minus simulated R (shadow), and vice versa when governance flips |

The Recalibration Agent reads the report weekly; the Validation Reviewer red-teams it; the investment committee decides governance per desk (Rule Watch, Agent Watch, or a split by `condition_kind`). Governance may be alternated by session in a desk's early weeks so both modes accumulate governing evidence. Every governance decision records the evidence it rested on and is itself scored later.

## 8. Acceptance scenarios

- **L1** A closed dossier gets counterfactuals and per-role scores within the same evening; each role's `calibration.md` updates.
- **L2** The Coach's weekly session produces a versioned playbook revision with rationale and evidence, an eval case, and a passing eval run before publication.
- **L3** A ledger run without `experiment_id` is refused by the tool; a run with one but no registration is recorded and flagged for the Validation Reviewer.
- **L4** A desk proposal reaches the investment committee with a Validation Reviewer verdict attached; minutes record positions; the CIO's decision is applied by tool within IPS caps.
- **L5** A `SkillChangeRequest` becomes a PR with evals; the reviewing agent's approval and CI results are recorded; the new skill version appears in the next session's evidence.
