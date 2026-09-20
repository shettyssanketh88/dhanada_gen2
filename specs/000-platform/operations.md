# Operations — shifts, schedules, monitoring, human touchpoints

*Companion to `spec.md` (DH2-OPS-*, DH2-OBS-*, DH2-COST-*). Times are IST. The scheduler is the engine's durable shift runner (`plan.md` §5); agent sessions are launched per shift with a budget.*

## 1. Daily schedule (trading day)

| Time | Shift | Actor | Budget | What happens |
|---|---|---|---|---|
| 07:30 | `ops.morning` | Engine checks → Operations Engineer on failure | USD 1 | Instrument master, rule tables valid for today, DB/disk, feed pre-checks, egress IP, token presence. If no token: one Principal reminder with login link; desk state `awaiting_login`; re-check every 10 min until 09:10. |
| 08:30 | `data.prep` | Engine | — | Announcements, results calendar, corporate actions ingested; point-in-time universe for today; features rebuilt; degeneracy tests. |
| 08:45 | `intel.premarket` | Market Intelligence Analyst | USD 1.5 | Catalyst tagging batch; `MarketBrief`. |
| 09:00 | `desk.open` | Desk Head | USD 1 | Sleeve statuses, governor outputs, allocation tiers, health summary; confirms `armed` or records why not (no token, kill engaged, degenerate feature). |
| 09:15–15:30 | `market.session` | Engine | — | Ticks, bars, signal engines, candidates, OMS, brackets, reconciliation every 60 s. |
| event | `trade.vet` | Trade Manager | USD 0.15 per candidate, cap per sleeve per day | On `candidate_created`; must return within 90 s or the candidate expires (`expired`, never a default take). |
| event | `trade.hold_event` | Trade Manager | USD 0.3 per event | On enumerated invalidation events for open dossiers. |
| every 30 min | `risk.sweep` | Risk Officer | USD 0.5 | Policy outcomes, exposure, reconciliation state, cost ratios; acts only within enumerated authority. |
| 12:30 | `intel.midday` | Market Intelligence Analyst | USD 0.75 | Refresh catalyst tags; brief addendum. |
| 15:00 | `trade.carry_window` | Engine rule (+ Trade Manager note) | — | Gated carry rule evaluates; product conversions executed; dossier notes appended. |
| 15:15 | `oms.squareoff` | Engine | — | MIS flatten; verify 15:20, 15:23; escalate. |
| 15:35 | `oms.eod_reconcile` | Engine | — | Final order/position/holdings reconciliation; mismatches → incident. |
| 16:00 | `accounting.close` | Engine | — | Fills applied, costs, R, daily sleeve rollup. |
| 16:10 | `governor.run` | Engine | — | Sleeve and desk governor; actions audited; alerts. |
| 16:30 | `review.trades` | Post-Trade Reviewer | USD 2 | Per-dossier rubric for the day's closes. |
| 17:00 | `desk.journal` | Desk Head | USD 1 | Daily journal to Principal (email/Telegram + dashboard). |
| 20:00 | `research.nightly` | Quant Researcher (+ Reviewer on proposals) | USD 10 | Trial queue from backlog; reports; proposals. |
| 22:30 | `memory.consolidate` | Engine (+ small model for summaries) | USD 0.5 | Index rebuild, lesson expiry, archival, memory health. |
| 23:00 | `data.nightly` | Engine | — | Bhavcopy, backfills, Parquet compaction, backups (`age`-encrypted, off-box). |

Non-trading days run `data.nightly`, `research.nightly` (extended budget USD 20 on Saturday) and the weekly shifts below.

## 2. Weekly and monthly

| When | Shift | Actor | Output |
|---|---|---|---|
| Sat 09:00 | `review.week` | Post-Trade Reviewer | Weekly review; hypotheses to backlog; lesson proposals |
| Sat 10:00 | `risk.week` | Risk Officer | Cost calibration; veto-arm A/B; edge-to-cost; correlation |
| Sat 11:00 | `compliance.week` | Compliance Auditor | Compliance report; rule PRs if circulars changed |
| Sat 12:00 | `research.committee` | Researcher → Reviewer → PM | Promotion proposals reviewed; gate evaluations recorded |
| Sat 14:00 | `desk.digest` | Desk Head | Weekly digest to Principal with pending approvals |
| 1st trading day 08:00 | `portfolio.monthly` | Portfolio Manager | Allocation tiers for the month |
| 1st trading day 09:20 | `sleeve.rebalance` | Engine (positional sleeves) | Rebalance orders per sleeve config |
| Emergency (desk vol > 2× target or index |move| > 3 %) | `portfolio.emergency` | Portfolio Manager + Risk Officer | Emergency review; tiers may only go down |
| Each release | `release.drill` | CI + Risk Officer | Three-level kill drill evidence |

## 3. Human touchpoints (the Principal)

| Touchpoint | Frequency | Channel |
|---|---|---|
| Broker login (TOTP) | Every trading morning before 09:10 | Reminder with link; confirmation shown on dashboard |
| Daily journal | Daily 17:00 | Email/Telegram + dashboard |
| Weekly digest with approvals queue | Saturday | Email + dashboard |
| Approvals: G5 capital, constitution, trading-impact skill/role changes, threshold PRs | As they arise | PR review + signed approval file |
| Kill switch | Any time | Dashboard button + signed CLI |
| Clearing a governor pause/halt | As they arise | Dashboard action with reason |

Nothing else requires the Principal. If the login is missing, the desk simply does not trade that day and says so.

## 4. Monitoring

Deterministic health checks (every 60 s in market hours, every 5 min otherwise) with thresholds in `rules/health.yaml`:

| Check | Threshold | Remediation (deterministic first) |
|---|---|---|
| Tick freshness | > 60 s stale → REST fallback; > 5 min → `feed_stall` incident + alert | Reconnect ticker; switch quote source |
| Token validity | any `TokenException` | Halt entries; alert Principal |
| Egress IP | mismatch | Halt entries; alert |
| Reconciliation | any mismatch | Re-run; if persists → incident, Risk Officer |
| OPS usage | > 80 % of bucket sustained 10 s | Throttle; alert if > 95 % |
| Bracket presence | missing > 30 s | Re-place; incident |
| Feature degeneracy | any failed test | Withhold feature from prompts; alert |
| LLM budget | > 80 % of daily | Warn; at 100 % stop non-essential shifts (research, midday intel) first |
| DB / disk | latency, free space | Alert |
| Backup | missing nightly backup | Alert |

The Operations Engineer is invoked only after deterministic remediation fails or for diagnosis (DH2-OPS-004).

## 5. Incidents

Severity enum: `S1` (money at risk: unflattened MIS, reconciliation mismatch on an open position, kill drill failure), `S2` (desk not trading: token, feed, IP), `S3` (degraded: research shift failed, budget exhausted), `S4` (cosmetic). S1 pages immediately; S2 alerts within 5 minutes; S3/S4 go to the journal. Every S1/S2 gets an incident file in ops memory within 24 h and a follow-up item (PR or backlog).

## 6. Deployment and release

- Images built by CI on tags; deployed with Docker Compose on the single Mumbai VM; native PostgreSQL; Parquet on local disk with nightly encrypted backup to off-box storage (v1 ADR-005 retained).
- Release checklist (skill `releasing`): CI green (lint, types, unit, integration, skill evals), migration dry-run on a DB snapshot, kill drill in paper, deploy after 15:35 IST only, `verifying-deploys` run, Principal re-login expected after container recreate (documented, not surprising).
- Two environments on the VM: `paper` and `live`, separate accounts and databases, same images.
- Configuration only via the declared environment file; the deploy script refuses if any secret appears in a non-secret path.

## 7. Cost governance

| Item | Default | Enforcement |
|---|---|---|
| Daily desk LLM budget | USD 25 `[NC-3]` | Scheduler sums `total_cost_usd` per shift; stops non-essential shifts at the cap |
| Per-shift budgets | as in §1 | `max_budget_usd` on each session |
| Per-candidate vetting | USD 0.15, daily cap per sleeve = 40 candidates | Scheduler; beyond the cap candidates run on the shadow arm only |
| Model routing | per role in `roles.md` | Role definition; hooks deny other models |
| Prompt caching | Stable system prefix per role; volatile context last | Prompt assembly scripts |

Cost per trade and per trial are reported weekly (DH2-COST-003).

## 8. Dashboard (minimal, v2.0)

One page per audience, read-only except the Principal actions:

- **Desk**: armed state, broker state, kill state, sleeves (status, tier, expectancy R, cost_R, drawdown vs limits, DSR/MTRL progress), open dossiers, today's shifts and costs.
- **Research**: backlog, experiments, ledger with DSR/N/k, proposals awaiting review or approval.
- **Ops**: health checks, incidents, deploy state, backups.
- **Principal actions**: login status, approvals queue, kill buttons, clear pause/halt.

Win rate is not displayed anywhere (constitution II.3).

## 9. Acceptance scenarios

- **O1** Given a crash at 10:42 during `market.session`, When the engine restarts, Then open dossiers, brackets and the token state are recovered from the database, reconciliation runs first, and the shift log shows a resumed run rather than a new day.
- **O2** Given the LLM daily budget reaches 100 % at 14:00, When a candidate is created, Then it runs on the shadow arm only and the journal records the budget stop.
- **O3** Given no token at 08:30, When the checklist runs, Then exactly one reminder is sent, the dashboard shows `awaiting_login`, and after login the desk arms without further action.
- **O4** Given a release tag, When CI runs the kill drill and it fails, Then no image is published and the failure is an S1 incident.
