# Operations — firm hours, cadence, monitoring, human touchpoints

*Companion to `spec.md` v2.0 (DH2-OPS-*, DH2-OBS-*, DH2-COST-*). The scheduler provides firm hours and triggers; desks set their own cadence within them (charter); leadership roles set theirs. Times are IST.*

## 1. Firm-level schedule (trading day)

| Time | Shift | Actor | What |
|---|---|---|---|
| 07:30 | `ops.morning` | Code checks → Operations Engineer on failure | Token, egress IP, instrument master, rule tables, feeds, DB/disk. No token → one Principal reminder; firm `awaiting_login`; recheck every 10 min to 09:10. |
| 08:30 | `data.prep` | Code | Announcements, calendars, corporate actions, features, feature health, universe as-of. |
| 07:45 | `desks.scan` | Stock Scanners | Watchlists with reasons and priority; dossiers opened. |
| 08:00 | `desks.ingest` | Data Ingestors | Data packs per stock; quality flags. |
| 08:30 | `desks.books` | Senior Analysts → Risk Officer | Strategy books drafted and reviewed (intraday desks daily; swing/positional desks weekly on Monday with daily check-ins). |
| 08:45 | `desks.open` | Each desk (Senior Analyst chairs) | Desk meeting per charter: emphasis, escalation policy, template notes. |
| 09:00 | `firm.open` | CIO shift (short) | Confirms desks armed, allocations and budgets applied, rails status; journal opening note. |
| 09:15–15:30 | `market.session` | Code + roles on events | Feature service every minute; Rule Watch per tick; Agent Watch sessions per CIO cap; Execution Agents on events; Analysts on escalations (90 s) and revision requests; Scanners' intraday re-scans per charter; Risk Officer reviews (120 s) and sweeps every 30 min. |
| per charter (default every 60–90 min) | `desks.recalibrate` | Recalibration Agents | Intraday pass: family stats, regime, revision requests. |
| 15:00 | `carry.window` | Execution Agents per book rules; Analysts on escalation | Carries only as the book specifies; uncovered cases escalate. |
| 15:15 | `squareoff` | Code | MIS flatten for anything not converted/exited; verification 15:20/15:23. |
| 15:35 | `eod.reconcile` | Code | Final reconciliation; mismatches → Risk Office + Ops. |
| 16:00 | `accounting.close` | Code | Fills, costs, R, counterfactuals, desk and firm rollups, decision scores. |
| 16:30 | `desks.review` | Trade Reviewers | Per-agent reviews for the day's closes, with counterfactuals per version and mode. |
| 17:00 | `firm.journal` | CIO shift | Daily journal to the Principal. |
| 17:30 | `coach.daily` | Coach | Scores read; `REVIEW` sentinels handled; notes. |
| 19:00 | `desks.recalibrate.nightly` | Recalibration Agents | Family stats across days and stocks; template recommendations to the Coach; watch-mode report read. |
| 20:00 | `lab.nightly` | Research Lab | Trials from the backlog; reports; proposals in progress. |
| 22:30 | `memory.consolidate` | Each role (short) + Coach + code | Curation diffs; adoption decisions; index rebuild; health report. |
| 23:00 | `data.nightly` | Code | Bhavcopy, backfills, Parquet compaction, encrypted backups. |

Event-driven invocations during the session have deadlines: book review 120 s; Execution Agent event 30 s; Analyst escalation 90 s; Agent Watch digest handling 20 s. A missed deadline is logged and scored (timeliness), and the last standing instructions remain in force.

## 2. Weekly and monthly

| When | Shift | Actor | Output |
|---|---|---|---|
| Sat 09:00 | `desks.week` | Desk Reviewers + desk teams | Weekly desk reviews; meeting items |
| Sat 10:00 | `coach.week` | Coach (per desk) | Coaching reports; playbook revisions; lesson decisions; change requests |
| Sat 11:00 | `risk.week` | Risk Office | Cost calibration; guidance updates; risk section of the digest |
| Sat 11:30 | `compliance.week` | Compliance Auditor | Compliance report; rule PRs |
| Sat 12:00 | `lab.week` | Research Lab + Validation Reviewer | Ledger audit; proposals readied |
| Sat 14:00 | `firm.digest` | CIO | Weekly digest to the Principal |
| 1st trading day 08:00 | `investment.committee` | CIO chairs | Allocations, charters, promotions, retirements; minutes |
| Emergency | `risk.conference` / `committee.emergency` | Risk Office / CIO | On IPS proximity (≥ 50 % of daily loss or drawdown limit), index |move| > 3 %, or a desk's request |
| Each release | `release.drill` | CI + Risk Office | Kill drill evidence |

## 3. The Principal's touchpoints

| Touchpoint | Frequency | Channel |
|---|---|---|
| Broker login | Every trading morning before 09:10 | Reminder with link; dashboard confirms |
| Daily journal | 17:00 | Email/Telegram + dashboard |
| Weekly digest (organisational decisions, skill changes, incidents, spend) | Saturday | Email + dashboard |
| IPS and rails changes; constitution | As the Principal chooses | PR + signed approval file |
| Kill L3; clearing an L2 halt | As needed | Dashboard action / signed CLI |

Everything else is decided by agents and reported.

## 4. Monitoring (deterministic first, agent second)

| Check | Threshold | Deterministic remediation | Then |
|---|---|---|---|
| Tick freshness | > 60 s stale → REST fallback; > 5 min → incident | Reconnect; switch source | Ops diagnosis |
| Token | any auth failure | Halt new orders; keep protective orders | Principal + Risk Office |
| Egress IP | mismatch | Halt new orders | Ops + Principal |
| Reconciliation | mismatch | Re-run | Risk Office + Ops incident |
| Order-rate usage | > 80 % sustained 10 s | Queue/pace | Alert at > 95 % |
| Protective orders | missing > 30 s | Re-place | Incident |
| Feature health | failed test | Withhold and inform agents | Data Steward |
| IPS proximity | ≥ 80 % of any limit | — | Risk Office notice + Principal alert |
| LLM spend | ≥ 80 % of IPS daily budget | Warn CIO | At 100 %: stop non-essential sessions (research, consolidation) first; desks continue on reserved budget |
| DB/disk/backup | thresholds | — | Ops |

## 5. Incidents

Severity `S1` (money at risk: unflattened MIS, open-position reconciliation mismatch, drill failure), `S2` (firm not trading: token, feed, IP), `S3` (degraded: a shift failed, budget exhausted), `S4` (cosmetic). S1 pages immediately; S2 within 5 minutes; S3/S4 in the journal. Every S1/S2 gets an incident file within 24 h and a follow-up (PR or backlog item).

## 6. Deployment and release

Docker Compose on the Mumbai VM; native PostgreSQL; ghcr.io images from CI; two environments (paper, live) with separate databases and accounts; release checklist by the Skill Engineer's `releasing` skill (CI green incl. skill evals, migration dry-run, kill drill, deploy after 15:35 only, `verifying-deploys` by Ops, Principal re-login expected after container recreate). Configuration only via the declared environment file.

## 7. Cost governance

| Item | Default | Enforcement |
|---|---|---|
| Firm daily budget | IPS `llm_budget_usd_per_day` `[NC-2: proposed USD 40]` | Rail |
| Desk daily budgets | Allocated by the CIO monthly | Scheduler |
| Session budgets | Per role definition (`max_budget_usd`, `max_turns`) | Runtime |
| Model routing | Per role definition | Runtime |
| Reporting | Cost per decision, per trade, per trial, per desk | Weekly digest |

## 8. Dashboard (v2.0, minimal)

- **Firm**: state (armed/awaiting_login/halted), desks with allocation, expectancy R, cost_R, drawdown vs IPS, DSR/MTRL progress, calibration summary per role, open dossiers, spend.
- **Desk**: watchlist, dossiers by state with the owning role, meeting minutes, playbook version.
- **Learning**: scores by role, lesson pipeline, playbook revisions, evals.
- **Research**: backlog, experiments, ledger with N/k, proposals.
- **Ops/Compliance**: health, incidents, audits, deploys.
- **Principal**: login status, IPS, rails, kill controls, digest archive.

Win rate is not a headline anywhere.

## 9. Acceptance scenarios

- **O1** Crash mid-session → restart recovers dossiers, protective orders, token state; reconciliation runs first; shift resumes.
- **O2** Budget at 100 % at 14:00 → research and consolidation stop; desks continue on reserved budget; journal records it.
- **O3** No token at 08:30 → one reminder; `awaiting_login`; arms after login without further action.
- **O4** Release with a failing drill → no image published; S1 incident.
- **O5** A Position Manager misses a 60 s deadline → timeliness scored; last instructions stand; the event is retried once.
