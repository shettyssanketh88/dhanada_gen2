# Technical plan (HOW)

*Companion to `spec.md` v2.0. Decisions recorded in `docs/ADR/`. The plan serves the agents: the runtime that runs roles and meetings, the memory they rely on, the tools they act through, and the rails the owner set.*

## 1. Architecture

```
┌──────────────────────────────── Mumbai VM (static IP) ───────────────────────────────────┐
│  AGENT PLANE (Claude Agent SDK)                                                            │
│  ┌────────────┐  triggers/events  ┌──────────────────────────────────────────────────────┐ │
│  │ Scheduler  │──────────────────►│ Role sessions (one per invocation) and meetings      │ │
│  │ (code)     │◄── decisions ─────│  agents/<role>/ROLE.md · skills/ · memory/ · hooks   │ │
│  └────────────┘                   └───────────────────────────┬──────────────────────────┘ │
│                                                               │ MCP typed tools            │
│  INSTRUMENTS & EXECUTION SERVICE (code, decides nothing)      ▼                            │
│  ┌──────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ firm-tools MCP │ calculators │ exec (orders, protective orders, reconciliation) │ rails│  │
│  │ data ingest │ features │ sim/replay engine │ accounting + counterfactuals │ ledger     │  │
│  │ dossier & memory stores │ decision scoring │ audit chain │ subscriptions │ notify      │  │
│  └──────────────┬───────────────────────────────────────────────┬───────────────────────┘  │
│                 │ Kite Connect (one token, static IP)            │                          │
│  ┌──────────────▼───────────┐   ┌──────────────────┐   ┌────────▼────────────────────┐     │
│  │ Kite REST + WebSocket    │   │ PostgreSQL 16    │   │ Parquet + DuckDB            │     │
│  └──────────────────────────┘   └──────────────────┘   └─────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────────────────────────────┘
        ▲ ghcr.io images (CI-built)                ▲ Principal: IPS, login, kill L3, digest
```

## 2. Stack

| Layer | Choice | ADR |
|---|---|---|
| Language | Python 3.12, `ruff`, `mypy --strict`, `pytest` | — |
| Agent runtime | Claude Agent SDK (Python), self-hosted; roles as `AgentDefinition`s; meetings as orchestrated multi-session runs; skills from `skills/`; hooks for rails and scope | ADR-001 |
| Models | `claude-opus-5` for deciding roles (CIO, Risk Office, Coach, Strategist, Trader, Position Manager, Researcher, Reviewer, Designer, Compliance, Skill Engineer); `claude-sonnet-5` for Analysts, Desk Reviewer per-trade, Ops, Data Steward; `claude-haiku-4-5` for batch tagging and summaries | ADR-007 |
| Execution service | FastAPI (internal API, MCP server, dashboard API), asyncio workers | — |
| Storage | PostgreSQL 16 native; Parquet + DuckDB for research | ADR-004 |
| Memory | PostgreSQL truth + git-backed markdown projection; FTS retrieval | ADR-003 |
| Scheduler | Engine-owned durable runner (`shift_runs`, `shift_steps`, `events`) | ADR-006 |
| Broker | Kite Connect v3 | tools-and-rails.md |
| Deployment | Docker Compose, ghcr.io, GitHub Actions | ADR-005 |
| Observability | OpenTelemetry, Prometheus, JSON logs | — |
| Notifications | Email + Telegram | — |
| Dashboard | React + Vite, read-mostly | — |

## 3. Repository layout

```
dhanada-v2/
  .specify/memory/constitution.md
  specs/000-platform/…  specs/NNN-<feature>/…
  docs/ADR/  docs/research/  docs/lessons-from-v1.md
  rails/            # RAILS.md, ips.yaml, market_rules/ (dated), health.yaml   ← Principal-owned
  agents/<role>/ROLE.md
  desks/<desk_id>/CHARTER.md, PROPOSAL.md, playbook.md (CIO/Designer/Strategist-owned)
  skills/<name>/…
  memory/roles/  memory/desks/  memory/firm/  memory/ops/   (git-backed projection)
  research/backlog.yaml  research/experiments/<id>/
  journal/
  engine/           # code plane: exec/ calc/ data/ features/ sim/ accounting/ ledger/ scoring/ dossiers/ memory/ scheduler/ rails/ mcp/ api/ common/
  runtime/          # agent plane glue: launcher, meetings, hooks, prompt assembly, budgets, evals runner
  contracts/        # Pydantic models + JSON schemas (decision objects)
  tests/{unit,integration,compliance,evals}
  infra/{compose,alembic,ci,runbooks}
  ui/
```

Structural test: nothing under `engine/` imports an LLM client.

## 4. Agent runtime design

- **Role → AgentDefinition.** Frontmatter: `model`, `effort`, `decision_rights`, `tools` (allowlist), `skills`, `memory_scopes`, `max_turns`, `max_budget_usd`, `meeting_roles`. The launcher builds `ClaudeAgentOptions(agents={...}, setting_sources=["project"], permission_mode="dontAsk", hooks=..., mcp_servers={"firm": ...}, output_format=<decision schema>, max_budget_usd, max_turns)`.
- **Invocation.** One session per decision or event. The launcher assembles: the role's `MEMORY.md`, playbook, calibration summary, adopted lessons in scope, the dossier (facts + all sections) or meeting agenda, and a task brief with ids and paths. Numbers reach the prompt only through the agent's own calculator calls. The decision object comes back as `structured_output`, validated (type, rails, consistency) with two correction rounds before `REVIEW`.
- **Meetings.** An orchestrated run: the chair role's session opens the agenda; member roles are invoked in rounds with the minutes so far; the chair closes with a decision; all positions stored. Round caps from the chair's role definition.
- **Hooks (enforcement).** `PreToolUse` denies: Bash touching broker endpoints, `.env*`, secrets, `docker`, live DB; writes outside the role's memory paths; MCP tools outside the allowlist. `PostToolUse` logs to the audit chain. `Stop` hooks verify skill postconditions (decision written, forecast present).
- **Sandbox.** Sessions run in the Claude Code sandbox with network limited to the local MCP endpoint and the Anthropic API; research sessions get read-only Parquet paths.
- **Continuity.** State lives in dossiers, memory and the ledger; sessions are disposable; no cross-host resume.
- **Prompt hygiene.** Stable per-role system prefix (cached); volatile context last; external text labelled as data; no rankings/leaderboards injected by the system.

## 5. Scheduler and durability

`shift_runs`, `shift_steps` (idempotent, retried), `events` (subscriptions, fills, notices, rail events) with deadlines and owning role; crash → resume at the first incomplete step; per-desk cadence read from charters. Temporal/DBOS deferred (ADR-006).

## 6. Contracts (Pydantic, `contracts/`)

| Model | Producer | Key fields |
|---|---|---|
| `Idea` | Analyst | symbol, direction_view, horizon, evidence[], confidence, invalidation_hint |
| `Thesis` | Strategist | idea_refs, direction, horizon, catalyst, invalidation[], conviction_prob, expected_move_frame |
| `Plan` | Trader | instrument, product, entry{type, price/zone}, stop, target[], qty, timing, order_type, validity, instruments_used[], expected_r, p_success, cost_r, rationale |
| `RiskReview` | Risk Office | decision, changes?, reasons, expected_effect |
| `OrderAction` | Trader | place/modify/cancel with parameters |
| `PositionAction` | Position Manager | action, params, reasoning, expected_effect, subscriptions[] |
| `TradeReview` | Desk Reviewer | per_role_scores, findings, lesson_proposals[], meeting_items[] |
| `CoachingReport`, `PlaybookRevision`, `LessonDecision` | Coach | diffs, rationale, evidence, n |
| `AllocationDecision`, `CharterDecision` | CIO | per-desk capital and budget, environment, rationale, evidence |
| `PreRegistration`, `TrialRecord`, `TrialReport`, `DeskProposal`, `ReviewVerdict` | Research Lab | see learning.md |
| `SkillChangeRequest` | any | what, why, evidence |
| `RiskNotice`, `DeskGuidance`, `IncidentReport`, `ComplianceReport`, `ChecklistResult`, `Journal`, `Minutes` | as named | — |
| `Invocation`, `DecisionScore`, `ShiftRun`, `RailEvent` | runtime/code | cost, model, versions, refs; scores; runs; rail id |

Decision objects carry the agent's numbers; validation checks type, rails and consistency only.

## 7. Data model (principal tables)

| Group | Tables |
|---|---|
| Firm | `desks`, `charters`, `allocations`, `accounts`, `desk_metrics_daily`, `firm_metrics_daily` |
| Dossiers | `dossiers`, `dossier_sections`, `dossier_events`, `dossier_evidence`, `dossier_counterfactuals`, `subscriptions` |
| Orders | `order_intents`, `orders`, `order_events`, `fills`, `positions`, `cash_ledger`, `protective_orders`, `gtt_brackets` |
| Rails & risk | `rail_events`, `kill_events`, `risk_reviews`, `risk_notices`, `desk_guidance` |
| Market data | `instruments(as_of)`, `quote_snapshots`, `announcements`, `corporate_actions`, `results_calendar`, `universe_pit`, `delistings`, `holidays`, `market_rules(effective_from)` |
| Features | `feature_snapshots`, `feature_health` |
| Learning | `decision_scores`, `playbook_versions`, `lessons`, `evals`, `eval_runs`, `skill_change_requests` |
| Research | `research_trials`, `preregistrations`, `experiments`, `backlog_items`, `review_verdicts`, `desk_proposals`, `committee_minutes` |
| Memory | `memory_items`, `memory_retrievals`, `journal_entries` |
| Runtime | `shift_runs`, `shift_steps`, `events`, `invocations`, `llm_costs` |
| Audit | `audit_chain` (hash-chained, monthly partitions, 5-year retention) |

Bars in Parquet (`data/bars/<interval>/<symbol>/<yyyy-mm>.parquet`); `data_snapshots` for immutable research inputs.

## 8. Security

Secrets in the execution service's store (restricted env file in v2.0; `age`-encrypted backups); MCP server on localhost with per-session capability tokens; hooks and sandbox deny agent access; Principal actions signed (CLI key) or 2FA dashboard; audit chain over orders, fills, decisions, invocations, memory writes, rail events; optional read-only Kite sidecar with its own key `[NC-3]`.

## 9. Testing

| Level | What | Gate |
|---|---|---|
| Unit | Engine, calculators (pinned numerics), contracts, rails, stats | ≥ 90 % exec/accounting/rails; ≥ 85 % elsewhere |
| Integration | PostgreSQL testcontainers: order state machine, reconciliation, dossier transitions, memory embargo, scoring, scheduler resume | every PR |
| Fault injection | kill between persist and send; timeout-then-appears; WS drop; token invalid | nightly |
| Parity | sim engine vs paper accounting identical | CI |
| Compliance | order-rate ceiling, static IP behaviour, retention, no-LLM-in-engine | CI |
| Skill evals | ≥ 3 per skill, state-graded; pass^5 for ops/risk/exec-adjacent | CI (budgeted) |
| Agentic replay | a desk's roles over sampled history days (masked) produce calibration and counterfactual reports | before paper |
| Kill drill | three levels in paper | release tags |
| Replay | any invocation reassembles inputs; stored vs fresh output diff | CI sample |

## 10. Observability

OTel spans `shift → session → tool/order` with `dossier_id`, `desk_id`, `role`, `gen_ai.*`; metrics per `operations.md` §4; alerts per spec DH2-OBS-002.

## 11. Migration from v1 (data only)

Export bars and daily bars to Parquet; import v1 trials as `v1_*` experiments; import cost calibration history; no v1 code imported (reference reading only).

## 12. Open clarifications

| id | Question | Proposed default |
|---|---|---|
| NC-1 | Initial IPS values (capital, loss limits, exposure caps, permitted products/horizons, prohibited list, max desks, capital per desk) | Paper ₹50L across desks; live first allocation ≤ ₹1L; max daily loss 2 %, max drawdown 15 %; single name 15 %, sector 30 %; products equity CNC/MIS + index futures; options defined-risk only; prohibited: naked option selling, automated login |
| NC-2 | Firm daily LLM budget | USD 40/day (desks ~USD 20, leadership ~USD 8, lab ~USD 10, rest ~USD 2) |
| NC-3 | Second Kite app key for a read-only sidecar | Yes if ₹500/month acceptable |
| NC-4 | Notification channel | Email (existing bot) + Telegram |
| NC-5 | Initial desks to charter for paper | Positional Momentum Desk, Event/Catalyst Desk, Intraday Breakout Desk (from the seed backlog) |
