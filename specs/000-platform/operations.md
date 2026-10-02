# Operations — firm hours, cadence, monitoring, human touchpoints

*Companion to `spec.md` v2.0 (DH2-OPS-*, DH2-OBS-*, DH2-COST-*). The scheduler provides firm hours and triggers; desks set their own cadence within them (charter); leadership roles set theirs. Times are IST.*

## 1. Firm-level schedule (trading day)

| Time | Shift | Actor | What |
|---|---|---|---|
| 07:30 | `ops.morning` | Code checks → Operations Engineer on failure | Token, egress IP, instrument master, rule tables, feeds, DB/disk. No token → one Principal reminder; firm `awaiting_login`; recheck every 10 min to 09:10. |
| 08:30 | `data.prep` | Code | Announcements, calendars, corporate actions, features, feature health, universe as-of. |
| 07:40 | `books.sod` | Books & Records Agent | Start-of-day clean book: ledger vs broker positions/holdings/funds/orders; a break holds new book approvals. |
| 07:45 | `desks.scan` | Stock Scanners | Watchlists with reasons and priority; dossiers opened. |
| 08:10 | `compliance.feeds` | Code + Broker Compliance Officer on change | Surveillance lists, ban list, price bands, MIS list, freeze quantities, calendar refreshed; catalogue diff. |
| 08:15 | `treasury.plan` | Treasury & Settlement Manager | Margin and cash plan per desk; settlement obligations; funds actions to the Principal. |
| 08:00 | `desks.ingest` | Data Ingestors | Data packs per stock; quality flags. |
| 08:30 | `desks.books` | Senior Analysts → Risk Officer + both Compliance Officers | Strategy books drafted, economically reviewed and pre-cleared (intraday desks daily; swing/positional desks weekly on Monday with daily check-ins). |
| 08:45 | `desks.open` | Each desk (Senior Analyst chairs) | Desk meeting per charter: emphasis, escalation policy, template notes. |
| 09:00 | `firm.open` | CIO shift (short) | Confirms desks armed, allocations and budgets applied, rails status; journal opening note. |
| 09:15–15:30 | `market.session` | Code + roles on events | Feature service every minute; Rule Watch per tick; Agent Watch sessions per CIO cap; Execution Agents on events; Analysts on escalations (90 s) and revision requests; Scanners' intraday re-scans per charter; Risk Officer reviews (120 s) and sweeps every 30 min. |
| per charter (default every 60–90 min) | `desks.recalibrate` | Recalibration Agents | Intraday pass: family stats, regime, revision requests. |
| every 1–5 min | `compliance.surveil` | Detectors → Compliance Officers on alert | OTR, cancel ratios, self-match, volume share, closing window, position limits, RMS bursts; holds. |
| every 5 min | `treasury.peak` | Detector → Treasury on breach | Peak-margin headroom incl. MTM; reduce requests. |
| 14:45 | `carry.window` | Execution Agents per book rules; Analysts on escalation | Carries only as the book specifies; uncovered cases escalate (moved from 15:00: CAS stocks auto-square at 15:12 and enter the closing auction at 15:15). |
| 15:00 | `squareoff.cas` | Code | MIS flatten for F&O-segment (CAS) stocks not converted/exited; verification 15:05/15:08 (Zerodha auto-squares at 15:12; cash CAS opens 15:15 with no new orders until 15:20). |
| 15:15 | `squareoff.rest` | Code | MIS flatten for non-CAS stocks and index futures; verification 15:20/15:23 (broker backstops 15:25/15:26). |
| 15:35 | `eod.reconcile` | Code + Books & Records | Final reconciliation; breaks → Books & Records disposition, Risk Officer, Ops. |
| 16:00 | `accounting.close` | Code | Fills, costs, R, counterfactuals, desk and firm rollups, decision scores. |
| 16:05 | `compliance.close` | Both Compliance Officers + Books & Records | EOD compliance close; P&L attribution; tax ledger; expected penalties (with Treasury). |
| 16:20 | `tca.daily` | Execution Quality Analyst | Implementation shortfall per fill; recommendations. |
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
| Sat 09:00 | `desks.week` | Trade Reviewers + desk teams | Weekly desk reviews; meeting items |
| Sat 10:00 | `coach.week` | Coach (per desk) | Coaching reports; playbook revisions; lesson decisions; change requests |
| Sat 11:00 | `risk.week` | Risk Officer | Cost calibration; guidance updates; risk section of the digest |
| Sat 11:30 | `compliance.week` | Both Compliance Officers | Weekly self-audit; feed refresh; alert dispositions ≤ 30 days; rule PRs |
| Sat 11:45 | `tca.week` | Execution Quality Analyst | Cost-model calibration proposal |
| Half-yearly | `compliance.audit` | CIO chairs; officers, Books & Records, Ops | Evidence bundle to the Principal |
| Quarterly | `treasury.settlement` | Treasury | Running-account settlement pre-funding |
| Quarterly | `lab.revalidate` | Validation Reviewer | Re-validation of every live desk |
| Sat 12:00 | `lab.week` | Research Lab + Validation Reviewer | Ledger audit; proposals readied |
| Sat 14:00 | `firm.digest` | CIO | Weekly digest to the Principal |
| 1st trading day 08:00 | `investment.committee` | CIO chairs | Allocations, charters, promotions, retirements; minutes |
| Emergency | `risk.conference` / `committee.emergency` | Risk Officer / CIO | On IPS proximity (≥ 50 % of daily loss or drawdown limit), index |move| > 3 %, or a desk's request |
| Each release | `release.drill` | CI + Risk Officer | Kill drill evidence |

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
| Token | any auth failure | Halt new orders; keep protective orders | Principal + Risk Officer |
| Egress IP | mismatch | Halt new orders | Ops + Principal |
| Reconciliation | mismatch | Re-run | Risk Officer + Ops incident |
| Order-rate usage | > 80 % sustained 10 s | Queue/pace | Alert at > 95 % |
| Protective orders | missing > 30 s | Re-place | Incident |
| Feature health | failed test | Withhold and inform agents | Data Ingestor |
| IPS proximity | ≥ 80 % of any limit | — | Risk Officer notice + Principal alert |
| Reconciliation break | any | Hold new book approvals | Books & Records + Principal (S13) |
| OTR | ≥ 40 per segment | Alert | Regulatory Compliance Officer; hold at 200 |
| Peak-margin headroom | < 20 % | — | Treasury reduce request; Principal if funds needed |
| RMS rejection burst | ≥ 3 in 5 min on a desk | Pause the strategy's orders | Broker Compliance Officer |
| LLM spend | ≥ 80 % of IPS daily budget | Warn CIO | At 100 %: stop non-essential sessions (research, consolidation) first; desks continue on reserved budget |
| DB/disk/backup | thresholds | — | Ops |

## 5. Incidents

Severity `S1` (money at risk: unflattened MIS, open-position reconciliation mismatch, drill failure), `S2` (firm not trading: token, feed, IP), `S3` (degraded: a shift failed, budget exhausted), `S4` (cosmetic). S1 pages immediately; S2 within 5 minutes; S3/S4 in the journal. Every S1/S2 gets an incident file within 24 h and a follow-up (PR or backlog item).

## 6. Deployment and release

Docker Compose on the Mumbai VM; native PostgreSQL; ghcr.io images from CI; two environments (paper, live) with separate databases and accounts; release checklist by the Skill Engineer's `releasing` skill (CI green incl. skill evals, migration dry-run, kill drill, deploy after 15:35 only, `verifying-deploys` by Ops, Principal re-login expected after container recreate). Configuration only via the declared environment file.

## 7. Cost governance

| Item | Default | Enforcement |
|---|---|---|
| Firm daily budget | IPS `llm_budget_usd_per_day` (NC-2 decided: USD 15/day paper phase, `rails/ips.yaml`) | Rail |
| Desk daily budgets | Allocated by the CIO monthly | Scheduler |
| Session budgets | Per role definition (`max_budget_usd`, `max_turns`) | Runtime |
| Model routing | Per role definition | Runtime |
| Reporting | Cost per decision, per trade, per trial, per desk | Weekly digest |

## 8. Owner interface

Specified in `ui.md` (ADR-010): a responsive web console as the system of record (Today, Inbox, Desk, Dossiers, Books, Agents, Journal & Digest, Governance, Ask, Research Lab, Compliance) plus a Telegram companion with eight verbs for interrupts and digests. The Principal's levers are approve, edit, respond, ignore, pause, kill and ask; there is no manual order entry. Win rate is not a headline anywhere and no rupee P&L appears above the fold on the home screen.

## 9. Acceptance scenarios

- **O1** Crash mid-session → restart recovers dossiers, protective orders, token state; reconciliation runs first; shift resumes.
- **O2** Budget at 100 % at 14:00 → research and consolidation stop; desks continue on reserved budget; journal records it.
- **O3** No token at 08:30 → one reminder; `awaiting_login`; arms after login without further action.
- **O4** Release with a failing drill → no image published; S1 incident.
- **O5** An Execution Agent misses a 60 s deadline → timeliness scored; last instructions stand; the event is retried once.
