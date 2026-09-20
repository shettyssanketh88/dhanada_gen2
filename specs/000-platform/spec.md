# Dhanada v2 — Platform Specification (WHAT and WHY)

| Field | Value |
|---|---|
| Spec id | `000-platform` |
| Status | Draft v2.1 for Principal review (v2.0 + the strategy-book pipeline from `scenario-walkthrough.md`) |
| Date | 2026-09-20 |
| Governed by | `.specify/memory/constitution.md` v2.0.0 |
| Inputs | `docs/lessons-from-v1.md`, `docs/research/*`, the Principal's directions of 2026-09-20 (all decisions agent-driven; the scanner → ingestor → analyst → execution → recalibration pipeline; both watch modes evaluated; books per stock per session/week) |
| Companion documents | `plan.md`, `roles.md`, `memory.md`, `skills.md`, `tools-and-rails.md`, `learning.md`, `operations.md`, `scenario-walkthrough.md`, `tasks.md` |

Requirement ids are `DH2-<AREA>-<nnn>`. Areas: FIRM, PIPE (pipeline and books), EXEC (execution agent and watch), MEM, LRN, RAIL, TOOL, DAT, OPS, CMP, OBS, COST, DEV. EARS phrasing. `[NC]` marks a clarification for the Principal.

---

## 1. Vision

Dhanada v2 is an **AI-run investment firm** for Indian markets, trading through Zerodha Kite. Agents hold every role that decides. Each desk runs a pipeline: a **Stock Scanner** picks the stocks, a **Data Ingestor** assembles everything known about them, a **Senior Analyst** writes a **strategy book** per stock (several strategies, each with the conditions under which it applies and its buy, stop and sell prices), a **Risk Officer** approves it, an **Execution Agent** watches the tape and applies whichever strategy's conditions are met, and a **Recalibration Agent** revises the strategies as the data comes in. A **Trade Reviewer** scores every agent's contribution after each trade; a **Coach** turns those scores into better playbooks and templates; a **CIO** allocates capital among desks; a **Research Lab** proposes new desks. Code provides instruments, executes orders, keeps memory, scores decisions and enforces the owner's rails.

Every stock a desk works on has a **dossier** that each agent writes into and reads from, so every agent continues its own work on that stock across the day, across days and across restarts.

## 2. Goals

| # | Goal | Measure |
|---|---|---|
| G1 | The firm makes money after realised costs | Firm net expectancy > 0 and Deflated Sharpe > 0 on paper across ≥ 3 desks before real capital; then live |
| G2 | Agentic end to end | Every trading, book, allocation and promotion decision attributable to a role with reasoning; execution fidelity to books ≥ 99 % |
| G3 | The firm learns | Every closed trade reviewed; every strategy family calibrated; templates revised with evidence; decision scores improve quarter over quarter |
| G4 | Breadth | ≥ 3 desks across ≥ 2 horizons on paper within 3 months; ≥ 5 within 12 months of first capital |
| G5 | Operational autonomy | Only the daily broker login, the IPS and rail changes involve the Principal |
| G6 | Honest measurement | Calibration, counterfactuals per book version and per watch mode, trial counts on every claim |
| G7 | Bounded LLM spend | Firm budget as a rail; allocated by the CIO; both watch modes costed |

## 3. Non-goals (v2.0)

Multi-tenant SaaS; mobile; public API; automated broker login; Kubernetes; any decision rule hard-coded outside the IPS rails.

## 4. The IPS and rails

The Principal writes `rails/ips.yaml` (`[NC-1]`): total and paper capital; max daily loss and drawdown; single-name and sector caps; permitted products, segments and horizons; prohibited activities; max desks live and capital per desk; LLM daily budget. Rails (`tools-and-rails.md` §9) = IPS + regulator/broker mechanics + kill switch. Everything else is an agent decision.

## 5. The firm

```
                                   Principal (IPS, login, kill L3)
                                                │
   ┌────────────────────────────────────────────┴───────────────────────────────────────────┐
   │ LEADERSHIP:  CIO (capital, charters, watch-mode governance) · Risk Officer · Coach       │
   └───────┬───────────────────────────────────┬────────────────────────────────┬───────────┘
           │                                   │                                │
   ┌───────▼─────────────────────────┐ ┌───────▼──────────────┐ ┌───────────────▼──────────┐
   │ DESK (pipeline instance) × N    │ │ RESEARCH LAB         │ │ OPERATIONS               │
   │  Stock Scanner                  │ │  Quant Researcher    │ │  Operations Engineer     │
   │  Data Ingestor                  │ │  Validation Reviewer │ │  Compliance Auditor      │
   │  Senior Analyst ──► Risk Officer│ │  Desk Designer       │ │  Skill Engineer          │
   │  Execution Agent (Rule Watch /  │ └──────────────────────┘ └──────────────────────────┘
   │    Agent Watch)                 │
   │  Recalibration Agent            │
   │  Trade Reviewer                 │
   └─────────────────────────────────┘
   ══════════════════ typed tools (MCP) ══════════════════════════════════════════════════════
   INSTRUMENTS & EXECUTION SERVICE (code): feature service · rule watch · exec · accounting ·
   calculators · sim engine · ledger · dossiers & memory · scoring · scheduler · rails
```

## 6. The dossier state machine (one per stock per desk per book period)

| State | Owner | Meaning |
|---|---|---|
| `scanned` | Stock Scanner | On the watchlist with reasons and priority |
| `data_ready` | Data Ingestor | Data pack attached; quality flags set |
| `book_drafted` | Senior Analyst | Strategy book version written |
| `book_approved` | Risk Officer | Per-strategy approvals; book version governs |
| `watching` | Execution Agent | Watch armed on the governing version; no position |
| `working` | Execution Agent | An entry order is live |
| `open` | Execution Agent | Position held; protective orders per the book |
| `escalated` (transient) | Senior Analyst | The book did not cover the situation; the Analyst decides and issues a new version; the Execution Agent keeps protective orders working meanwhile |
| `closed` | Execution service (facts) → Trade Reviewer | Both legs reconciled; accounting and counterfactuals written |
| `reviewed` | Trade Reviewer + Coach | Scores and lessons |
| `archived` | — | Immutable |

Side exits: `dropped` (Scanner or Analyst, with reason), `rejected` (Risk Officer rejects every strategy), `expired` (book period ended without a trade), `killed` (rail). A new book version does not reset the state; it is recorded on the dossier with the time it took effect.

## 7. Requirements

### 7.1 Firm (FIRM)

- **DH2-FIRM-001** THE SYSTEM SHALL define every role as a versioned role definition and run each role as its own agent session with its own memory.
- **DH2-FIRM-002** THE SYSTEM SHALL represent desks as chartered pipeline instances (`desks/<desk_id>/CHARTER.md`: mandate, universe, horizon, book period, capital, LLM budget, cadences, watch-mode governance, template set) manageable by the CIO through tools.
- **DH2-FIRM-003** THE SYSTEM SHALL record every decision with role, version, reasoning, instruments used, expected outcome and correlation ids for replay and scoring.
- **DH2-FIRM-004** WHEN a role's structured output fails validation, THE SYSTEM SHALL return the errors for correction up to twice, then record `REVIEW` and notify the Coach; never a default decision.
- **DH2-FIRM-005** THE SYSTEM SHALL support meetings (desk meeting, risk conference, investment committee, coaching session) as chaired multi-agent sessions with minutes and recorded positions.
- **DH2-FIRM-006** THE SYSTEM SHALL inform the Principal of every organisational decision via journal and digest and require approval only for IPS, rails and constitution changes.

### 7.2 Pipeline and strategy books (PIPE)

- **DH2-PIPE-001** THE SYSTEM SHALL let the Stock Scanner set and revise the desk watchlist with reasons, features used, horizon hint and priority, and SHALL open a dossier per watchlist entry per book period.
- **DH2-PIPE-002** THE SYSTEM SHALL let the Data Ingestor assemble a data pack per stock from the sources it selects, record quality flags and excluded windows, and commission new sources through PRs.
- **DH2-PIPE-003** THE SYSTEM SHALL represent a strategy book as a versioned artefact per stock per book period (session for intraday desks; week for swing and positional desks) containing global rules (invalidation, event rules, exclusivity, product and carry rules) and strategies, each with: `applies_when` (with `condition_kind: crisp | judgment`), direction, entry (type, price or zone), stop, targets with fractions, post-target rules, size, validity, priority, expected R, probability, instruments used, thesis, status.
- **DH2-PIPE-004** THE SYSTEM SHALL validate a book only for type, rails, and internal consistency (stop on the correct side, zones ordered, fractions sum to one, validity inside session, size within desk capital); every number is the Senior Analyst's.
- **DH2-PIPE-005** THE SYSTEM SHALL provide a feature expression language for crisp conditions over named features the feature service computes each minute (trend labels by timeframe, volume ratios paced by session time, levels, ranges, VWAP distance, breadth, time windows, event flags), extensible by the Skill Engineer on request.
- **DH2-PIPE-006** WHEN the Risk Officer reviews a book version, THE SYSTEM SHALL record per-strategy `approve | modify | reject` with reasons; a modified strategy takes effect only after the Analyst accepts or a chaired resolution; a book with no approved strategy leaves the dossier in `book_drafted`.
- **DH2-PIPE-007** THE SYSTEM SHALL let the Risk Officer define auto-approval rules for revisions within standing guidance so that intraday revisions are not blocked; auto-approvals are recorded as the Risk Officer's decisions.
- **DH2-PIPE-008** THE SYSTEM SHALL let the Recalibration Agent request revisions (retire, adjust, add) with evidence, and let the Senior Analyst accept, amend or decline each request with reasons; every revision is a new book version.
- **DH2-PIPE-009** THE SYSTEM SHALL compute, for every closed trade, counterfactual outcomes under each book version that governed during the trade (what v2 would have done versus v4) and under each watch mode, and attach them to the dossier.
- **DH2-PIPE-010** THE SYSTEM SHALL maintain strategy-family statistics (expectancy, calibration, cost per R, by regime and desk) with sample sizes for the Recalibration Agent and the Coach.

### 7.3 Execution agent and watch (EXEC)

- **DH2-EXEC-001** THE SYSTEM SHALL implement two watch modes: **Rule Watch** (deterministic evaluator of crisp conditions on every tick, invoking the Execution Agent on match, order event, escalation condition or milestone) and **Agent Watch** (a continuous Execution Agent session per stock or group receiving 1-minute digests and notable tick events, evaluating crisp and judgment conditions, acting through tools).
- **DH2-EXEC-002** THE SYSTEM SHALL run both modes on every dossier — one governing (places orders) and one in shadow (paper-only, records what it would have done and when) — as configured per desk by the CIO, so that fidelity, latency, slippage, cost and outcome can be compared.
- **DH2-EXEC-003** THE SYSTEM SHALL let the Execution Agent execute only what the governing book specifies (entries, protective orders, post-target rules, exits, carries) and SHALL escalate to the Senior Analyst any situation the book does not cover; the Execution Agent SHALL NOT invent a level, size or exit.
- **DH2-EXEC-004** WHILE a dossier is `escalated`, THE SYSTEM SHALL keep the last protective orders working and SHALL apply the Analyst's resolution (a new version) as soon as it is approved or auto-approved.
- **DH2-EXEC-005** WHEN several strategies' conditions are met, THE SYSTEM SHALL apply the book's priority and exclusivity rules; if they do not resolve the conflict, the Execution Agent escalates.
- **DH2-EXEC-006** THE SYSTEM SHALL reload a new book version into the watch within 5 seconds of approval and record the version change on the dossier with any protective-order modifications it implies.
- **DH2-EXEC-007** THE SYSTEM SHALL measure execution fidelity (actions taken versus actions the book specified, with timestamps) and report it per mode, per desk, weekly.

### 7.4 Memory (MEM)

- **DH2-MEM-001** Per-role long-term memory (playbook, templates for the Analyst, lessons, calibration, notes) and per-dossier sections per pipeline role; read before deciding, write after.
- **DH2-MEM-002** Time-aware retrieval (`known_at ≤ T`).
- **DH2-MEM-003** Lessons with evidence and status decided by the Coach; adopted lessons in the owning role's context.
- **DH2-MEM-004** Desk memory (shared by the pipeline team) and firm memory with write rights per role.
- **DH2-MEM-005** Versioned writes; point-in-time reads; replay.
- **DH2-MEM-006** Nightly consolidation by each role, reviewed by the Coach.

### 7.5 Learning and research (LRN)

- **DH2-LRN-001** Decision scoring after the fact: calibration (stated p and expected R vs realised), process adherence, counterfactual deltas per book version and watch mode, execution fidelity, timeliness; written to the deciding role's calibration record.
- **DH2-LRN-002** The Recalibration Agent receives strategy-family statistics intraday and nightly; the Coach receives role statistics weekly; both revise (books, templates, playbooks) through versioned changes with evals.
- **DH2-LRN-003** Research Lab backtests, replays and factor studies through a sandboxed engine with a trial ledger requiring an experiment id and hypothesis, recording N and k.
- **DH2-LRN-004** Desk proposals from the Desk Designer with the Validation Reviewer's adversarial verdict before the investment committee.
- **DH2-LRN-005** Skills, calculators and features evolve through Skill Engineer PRs with evals and agent review; the Principal is informed.
- **DH2-LRN-006** Point-in-time data, delisting-inclusive histories and masked identifiers for LLM-touched historical studies.
- **DH2-LRN-007** THE SYSTEM SHALL produce a watch-mode evaluation report per desk (fidelity, latency from condition to order, slippage, cost per stock-day, escalation quality, outcome deltas, with n and CIs) for the investment committee's governance decision.

### 7.6 Rails (RAIL), tools (TOOL), data (DAT), operations (OPS), compliance (CMP), observability (OBS), cost (COST), development (DEV)

Unchanged from v2.0 except:

- **DH2-TOOL-007** THE SYSTEM SHALL provide a **feature service** computing the named features of the expression language every minute for all watched stocks, with health tests, and SHALL expose them to both watch modes and to the Analyst's calculators.
- **DH2-TOOL-008** THE SYSTEM SHALL provide `books:*` tools (draft, revise, review, load, retire, request_revision) and `watch:*` tools (arm, reload, status, shadow_report).
- **DH2-COST-003** THE SYSTEM SHALL cost Agent Watch per stock-day and enforce a per-desk cap on concurrent Agent Watch sessions set by the CIO within the IPS budget.

## 8. Acceptance scenarios

**S1 — Pipeline end to end (RELIANCE day, `scenario-walkthrough.md` §3).** Scanner → data pack → book v1 → Risk `modify` → v2 approved → watch armed → S1 match at 10:42 → fill and protective orders → invalidation escalation at 11:20 → v3 → recalibration at 12:30 → v4 → T1 → square-off → accounting with counterfactuals per version → review with per-agent scores → nightly template revision. Every step attributable, every section written.

**S2 — Both watch modes.** Given a desk where Rule Watch governs and Agent Watch shadows, When S1's crisp condition is met, Then Rule Watch invokes the Execution Agent and an order is placed; Agent Watch records its own would-be action and timestamp; the weekly report shows fidelity, latency and outcome deltas for both.

**S3 — Judgment condition.** Given a strategy whose `applies_when` is a judgment condition, When the desk runs Rule Watch as governing, Then that strategy is evaluated by Agent Watch only (Rule Watch marks it `judgment_only`), and the Execution Agent's action is recorded with its reasoning.

**S4 — Escalation keeps protection.** Given an open position and an uncovered situation, When the Execution Agent escalates, Then protective orders stay working, the Analyst resolves within its deadline or the last book version continues, and the resolution becomes a new version.

**S5 — Recalibration is scored.** Given v2 and v4 governed a trade, When it closes, Then the dossier carries outcomes under each version and the Recalibration Agent's calibration record is updated with the delta.

**S6 — Rail rejection explained.** As v2.0 S4.

**S7 — Time-aware memory.** As v2.0 S5.

**S8 — CIO reallocates and sets watch governance.** Minutes record the decision and evidence; tools apply within IPS.

**S9 — Coach revises a template.** An over-optimistic pullback family over ≥ 50 trades → template v(n+1) with an eval case; next day's books use it.

**S10 — Broker timeout does not duplicate; S11 — the Principal's only daily job.** As v2.0.

## 9. Glossary

| Term | Meaning |
|---|---|
| Strategy book | The Senior Analyst's versioned set of strategies for one stock and one book period |
| Book period | Session (intraday desks) or week (swing/positional desks) |
| Crisp / judgment condition | Machine-checkable expression / prose condition needing agent judgment |
| Rule Watch / Agent Watch | Deterministic evaluator with event invocations / continuous agent session |
| Governing / shadow | The mode placing orders / the mode recording would-be actions |
| Feature service | Code computing the named features each minute |
| Escalation | The Execution Agent handing an uncovered situation back to the Analyst |
| Recalibration | The Recalibration Agent's intraday and nightly revision of strategies and templates |
| IPS, rail, desk, dossier, playbook, calibration record, counterfactual | As v2.0 |
