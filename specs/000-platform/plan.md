# Technical plan (HOW)

*Companion to `spec.md`. Decisions recorded as ADRs in `docs/ADR/`. Stack choices are minimal (constitution IX): one runtime for agents, one engine, one database family.*

## 1. Architecture

```
┌──────────────────────────────── Mumbai VM (static IP) ────────────────────────────────┐
│                                                                                        │
│  AGENT PLANE                                                                           │
│  ┌──────────────┐   launches per shift    ┌──────────────────────────────────────────┐ │
│  │ Scheduler    │────────────────────────►│ Claude Agent SDK sessions (one per role) │ │
│  │ (engine)     │◄─── structured result ──│  skills/ · agents/ · hooks · budgets     │ │
│  └──────────────┘                         └───────────────┬──────────────────────────┘ │
│                                                            │ MCP (typed tools)          │
│  ENGINE PLANE (FastAPI service + workers)                  ▼                            │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │ dhanada-engine MCP server │ policy gate │ OMS │ accounting │ dossiers │ governor │   │
│  │ data ingest │ features │ signal engines │ sim kernel │ ledger+stats │ kill switch│   │
│  └──────────────┬───────────────────────────────────────────────┬───────────────────┘   │
│                 │ Kite Connect (one token)                      │                       │
│  ┌──────────────▼───────────┐   ┌──────────────────┐   ┌────────▼────────────────────┐  │
│  │ Kite REST + WebSocket    │   │ PostgreSQL 16    │   │ Parquet store + DuckDB      │  │
│  └──────────────────────────┘   └──────────────────┘   └─────────────────────────────┘  │
│  Optional sidecar: read-only kite-mcp-server (own key) for Ops/Risk verification        │
└────────────────────────────────────────────────────────────────────────────────────────┘
        ▲ ghcr.io images (CI-built)                      ▲ Principal: login, approvals, kill
```

## 2. Stack

| Layer | Choice | Rationale / ADR |
|---|---|---|
| Language | Python 3.12, type hints, `ruff`, `mypy --strict`, `pytest` | Team standard; v1 tooling knowledge carries over |
| Agent runtime | **Claude Agent SDK (Python)** self-hosted on the VM; roles as `AgentDefinition`s from `agents/<role>/ROLE.md`; skills from `skills/`; hooks for enforcement | ADR-001 |
| Models | `claude-opus-5` (reasoning roles), `claude-sonnet-5` (Trade Manager vetting, Desk Head, Ops, per-trade review), `claude-haiku-4-5` (bulk classification, consolidation summaries) | ADR-007 |
| Engine service | FastAPI (internal API + MCP server + dashboard API), asyncio workers | v1 experience |
| Database | PostgreSQL 16 (native on VM) | ADR-004; v1 ADR-005 retained |
| Research data | Parquet + DuckDB; immutable snapshots | ADR-004 |
| Scheduler | Engine-owned durable shift runner on PostgreSQL (`shift_runs`, `shift_steps`) with idempotent steps; APScheduler for triggers | ADR-006 |
| Broker | Kite Connect v3 via `kiteconnect` SDK + own WebSocket client | `execution.md` |
| Deployment | Docker Compose, ghcr.io, GitHub Actions CI | v1 ADR-005 retained |
| Observability | OpenTelemetry (traces + metrics), Prometheus scrape, log JSON; Grafana optional | DH2-OBS |
| Notifications | Email + Telegram bot (existing v1 Gmail bot account can be reused) | operations.md |
| Dashboard | React + Vite (small), read-mostly | operations.md §8 |

## 3. Repository layout

```
dhanada-v2/
  .specify/memory/constitution.md
  specs/000-platform/…               # this specification
  specs/NNN-<feature>/…              # feature specs (spec.md, plan.md, tasks.md, contracts/)
  docs/ADR/, docs/research/, docs/lessons-from-v1.md
  engine/                            # deterministic plane (Python package `dhanada_engine`)
    broker/kite/  data/  features/  sleeves/<id>/  policy/  oms/  accounting/  sim/
    ledger/  governor/  kill/  dossiers/  scheduler/  mcp/  api/  common/
  agents/<role>/ROLE.md              # role definitions (frontmatter → AgentDefinition)
  skills/<name>/SKILL.md + scripts/ + references/ + evals/
  runtime/                           # agent-plane glue: session launcher, hooks, prompt assembly, budgets
    hooks/  prompts/  launcher.py  budgets.py
  memory/                            # git-backed role/desk/ops memory (see memory.md)
  research/                          # backlog.yaml, experiments/<id>/
  rules/                             # policy.yaml, health.yaml, instruments/, costs/, calendars/
  contracts/                         # Pydantic models + JSON schemas shared by both planes
  tests/{unit,integration,compliance,evals}
  infra/{compose,alembic,ci,runbooks}
  ui/
```

Structural test: nothing under `engine/` imports `anthropic`, `claude_agent_sdk`, or any LLM client (E8).

## 4. Agent runtime design (ADR-001)

- **Role → AgentDefinition.** `ROLE.md` frontmatter: `model`, `effort`, `tools` (allowlist of `mcp__dhanada_engine__*`, `Read`, restricted `Bash`), `skills`, `memory_scopes`, `max_turns`, `max_budget_usd`, `forbidden` (used by hooks). The launcher builds `ClaudeAgentOptions(agents={role: AgentDefinition(...)}, setting_sources=["project"], permission_mode="dontAsk", hooks=..., mcp_servers={"dhanada_engine": ...}, output_format=<role schema>, max_budget_usd=..., max_turns=...)`.
- **Invocation = one session per shift step.** The launcher passes a compact task brief (ids and paths, not data), the role's `MEMORY.md` index, and the structured schema. The session reads what it needs through tools. Results come back as `structured_output`; the launcher validates with Pydantic (range checks the schema cannot express) and stores an `invocations` row with cost, model, session id, prompt version and input refs.
- **Hooks (enforced, not advisory).** `PreToolUse` command hooks deny: Bash matching order endpoints, `.env*`, secret paths, `docker`, `psql` against live; file writes outside the role's allowed paths; MCP tools not in the role allowlist. `Stop` hooks verify postconditions per skill (e.g., research run wrote a ledger row). `PostToolUse` logs every tool call to the audit table.
- **Sandbox.** Sessions run in the Claude Code sandbox with network restricted to the engine's local MCP endpoint and the Anthropic API; research sessions additionally get read-only Parquet paths.
- **No cross-host session resume.** State lives in the dossier store, ledger and memory; sessions are disposable.
- **Prompt assembly.** Stable system prefix per role (cached); volatile context last; numbers only as z-scores, buckets or enums; no rankings; explicit "external text is data" instruction where announcements appear.

## 5. Scheduler and durability (ADR-006)

- Tables `shift_runs (id, shift, trading_date, state, started_at, ended_at, cost_usd, outcome)` and `shift_steps (run_id, step, state, attempt, idempotency_key, result_ref)`.
- Each shift is a list of steps; each step is idempotent (keyed) and retried with backoff; agent steps are budgeted; a crash resumes at the first non-complete step.
- Event-driven steps (`trade.vet`, `trade.hold_event`, `risk.sweep` triggers) are queued in `engine_events` and consumed by the same runner with a per-event deadline.
- Temporal/DBOS were considered and deferred; the step table gives checkpoint resumption with far less surface (ADR-006 lists the trigger conditions for revisiting).

## 6. Contracts (Pydantic, in `contracts/`)

| Model | Producer → Consumer | Key fields |
|---|---|---|
| `Candidate` | signal engine → dossier | sleeve_id, symbol, direction, entry_zone, stop, target, horizon, product, feature_snapshot_id, risk_budget_inr |
| `VetVerdict` | Trade Manager → engine | decision, veto_reason, thesis, invalidation_conditions[], confidence_bucket |
| `TradeIntent` | engine → policy → OMS | dossier_id, qty, entry_price, stop_price, target_price, product, validity, legs[] |
| `PolicyDecision` | policy → dossier | allowed, denials[{rule_id, detail}] |
| `OrderIntent` / `OrderEvent` / `Fill` | OMS | client_tag, broker_order_id, state, reference_price, spread_at_decision, fill_price |
| `HoldAction` | Trade Manager → engine | action, reason |
| `MarketBrief`, `CatalystTag` | Market Intel → feature store | see roles.md |
| `PreRegistration`, `TrialRecord`, `TrialReport`, `PromotionProposal`, `ReviewVerdict` | research | see research.md |
| `GovernorAction`, `AllocationDecision` | governor / PM | sleeve_id, status, risk_pct, tier, reasons |
| `RiskAssessment`, `TradeReview`, `WeeklyReview`, `ComplianceReport`, `IncidentReport`, `ChecklistResult`, `DeskJournal` | roles | see roles.md |
| `ShiftRun`, `Invocation` | runtime | cost, model, prompt_version, input_refs, output_ref |

All agent-facing schemas have `additionalProperties: false`; numeric fields are absent from agent outputs by construction.

## 7. Data model (PostgreSQL, principal tables)

| Group | Tables |
|---|---|
| Accounts & sleeves | `accounts`, `sleeves`, `sleeve_metrics_daily`, `allocation_decisions` |
| Dossiers | `dossiers`, `dossier_sections`, `dossier_events`, `dossier_evidence` |
| Orders | `order_intents`, `orders`, `order_events`, `fills`, `positions`, `cash_ledger`, `gtt_brackets` |
| Policy & risk | `policy_outcomes`, `governor_actions`, `kill_events`, `exposure_snapshots` |
| Market data (transactional) | `instruments(as_of)`, `quote_snapshots(depth)`, `announcements(published_at)`, `corporate_actions`, `results_calendar`, `universe_pit`, `delistings`, `holidays` |
| Features | `feature_snapshots`, `feature_health` |
| Research | `research_trials`, `preregistrations`, `experiments`, `backlog_items`, `review_verdicts`, `gate_evaluations` |
| Memory | `memory_items`, `memory_retrievals`, `journal_entries` |
| Runtime | `shift_runs`, `shift_steps`, `engine_events`, `invocations`, `llm_costs` |
| Audit | `audit_chain` (hash-chained, partitioned by month, 5-year retention) |

Bars live in Parquet (`data/bars/<interval>/<symbol>/<yyyy-mm>.parquet`) with a `data_snapshots` table recording immutable research snapshots.

## 8. Security

- Secrets (Kite key/secret, daily token, notification tokens, DB) in the engine's secret store (environment file with restricted permissions in v2.0; `age`-encrypted at rest for backups). Agent sessions have no access path: hooks deny, sandbox denies, and the MCP server never returns secrets.
- Engine MCP server binds to localhost; tools scoped per role by a per-session capability token issued by the launcher.
- Principal actions (approvals, kill, clear pause) require a signed request (CLI with a local key) or an authenticated dashboard session with 2FA.
- Audit chain covers orders, fills, policy outcomes, governor actions, kill events, invocations, memory writes.
- Read-only Kite sidecar (if funded) runs with `EXCLUDED_TOOLS` for all writes and its own key.

## 9. Testing strategy

| Level | What | Gate |
|---|---|---|
| Unit | Engine modules; pure functions; contracts; stats formulas with pinned numeric cases (from v1 WP0.4) | coverage ≥ 90 % execution/accounting/policy/sim, ≥ 85 % elsewhere |
| Integration | PostgreSQL via testcontainers: OMS state machine, reconciliation, dossier transitions, ledger refusals, governor idempotency | CI on every PR |
| Fault injection | Process kill between persist and send; timeout-then-appears; WS drop mid-fill; token invalid mid-session | CI nightly |
| Simulation parity | Same trades through sim kernel and paper OMS produce identical accounting | CI |
| Compliance | OPS ceiling, static-IP behaviour, retention config, no-LLM-in-engine structural test | CI |
| Skill evals | ≥ 3 per skill; state-graded; pass^5 for ops/risk | CI (budgeted) |
| Kill drill | Three levels in paper | Release tags |
| Replay | Dossier decision replay reproduces engine outputs | CI sample |

## 10. Observability

- OTel spans: `shift` → `invoke_agent` → `chat`/`execute_tool`; `order` spans from intent to reconciliation; attributes include `dossier_id`, `sleeve_id`, `shift_run_id`, `gen_ai.*` token usage.
- Metrics: feed freshness, reconciliation lag, policy denials by rule, OPS bucket usage, LLM cost by role, expectancy and cost_R by sleeve, governor actions, memory health.
- Alerts per `operations.md` §4.

## 11. Migration from v1 (data only)

- Export v1 bars (Postgres → Parquet) and daily bars; import the trial ledger rows as historical trials with `experiment_id` prefixed `v1_`; import cost calibration history; import the hod_pm holdout evidence as backlog B-004 attachments.
- No v1 code is imported. Specific v1 modules (Kite REST quote fetcher, cost rates, DSR stats, first-touch simulator, governor rules) are reference reading for the implementer of the corresponding v2 feature spec.

## 12. Open clarifications

| id | Question | Proposed default |
|---|---|---|
| NC-1 | Shadow fraction for the Trade Manager veto A/B | 30 % of candidates per sleeve |
| NC-2 | Initial desk daily loss cap | 2 % of desk equity |
| NC-3 | LLM budgets | USD 25/day desk; USD 10 nightly research; USD 20 Saturday |
| NC-4 | Fund a second Kite app key for the read-only sidecar | Yes if ₹500/month is acceptable; else omit the sidecar |
| NC-5 | Notification channel | Email (existing bot account) + Telegram |
| NC-6 | Paper capital per sleeve at birth | ₹10,00,000 intraday/swing; ₹20,00,000 positional |
