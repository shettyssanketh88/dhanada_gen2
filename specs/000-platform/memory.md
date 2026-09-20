# Memory architecture

*Companion to `spec.md` (DH2-MEM-*). Implements constitution Article IV.2 (per-trade, per-role memory) and Article VII (evidence and replay). Evidence base: CoALA taxonomy; TradingAgents/FinMem/FinAgent/FinCon memory designs and their failures; the "Outcome Embargo" and "hierarchy of truth" proposals in arXiv 2605.19337; verbatim-over-extracted result (arXiv 2601.00821); Managed Agents memory-store warning on read-write poisoning.*

## 1. Principles

1. **Memory is per entity and per role.** A trade has a dossier; each role has its own section in it. A role also has its own long-term memory. There is no single shared blob.
2. **Evidence first, lessons second.** Every lesson links to the verbatim inputs and outputs it came from. Retrieval returns evidence and lesson together; a lesson without evidence is invalid.
3. **Outcome embargo.** Every memory item carries `known_at`. Retrieval for a decision at time T filters to `known_at ≤ T`. Outcomes (P&L, R, exit reason) are `known_at = closed_at`, never earlier.
4. **Lessons have a status.** `hypothesis` → `validated` (tied to a passed gate id) → `retired` (failed G6, expired, or superseded). Only `validated` lessons enter a trading-path prompt.
5. **Hierarchy of truth.** The engine's ledger (positions, fills, costs) is authoritative over anything in an agent's memory or context. Agents may not "remember" a position; they read it.
6. **Reference is read-only.** Desk knowledge is changed only through PRs. Agent scratch memory is read-write but never auto-promoted.
7. **Versioned and replayable.** Every write records actor, time, prior hash. Point-in-time reads are supported.
8. **Decay and pruning are governed.** Lessons expire on a validity window unless re-validated; evidence is never deleted, only archived.

## 2. Memory scopes (CoALA mapping)

| Scope | CoALA type | Owner | Read by | Write by | Storage |
|---|---|---|---|---|---|
| **Working memory** | working | the running session | itself | itself | session context; recited plan file per shift |
| **Trade dossier** | episodic (per entity) | Engine (state) + roles (sections) | Trade Manager, Risk Officer, Post-Trade Reviewer, Desk Head, Quant Researcher (embargo-safe) | Engine (engine section, transitions), each role (own section only) | PostgreSQL (`dossiers`, `dossier_sections`, `dossier_events`) + filesystem projection for agent file tools |
| **Role memory** | semantic + procedural (per role) | each role | that role; Validation Reviewer (audit) | that role (proposals), Validation Reviewer (status changes), consolidation job | Git-backed markdown under `memory/roles/<role>/` with `MEMORY.md` index + topic files; mirrored to PostgreSQL for search |
| **Desk knowledge** | semantic (shared) | Principal via PRs | all roles | PR only | `memory/desk/` markdown + rule data tables |
| **Research memory** | episodic + semantic | Quant Researcher | Researcher, Reviewer, PM | Researcher (experiments), Reviewer (verdicts) | Trial ledger (PostgreSQL) + `research/experiments/<id>/` files in git |
| **Ops memory** | episodic + procedural | Operations Engineer | Ops, Desk Head, Compliance | Ops | `memory/ops/` incidents + runbooks-as-skills |
| **Desk journal** | episodic (desk-level) | Desk Head | Principal, all roles | Desk Head | `journal/YYYY-MM-DD.md` + structured summary row |

Role memory is where a role "continues work" across invocations. Dossier sections are where a role continues work on a specific trade across invocations, restarts and deploys (constitution IV.2).

## 3. The trade dossier

### 3.1 Structure

```
dossier/<dossier_id>/
  dossier.json            # engine-owned: state, sleeve, symbol, levels, qty, product, timestamps, refs
  transitions.jsonl       # engine-owned: every state change {from, to, actor, at, reason, correlation_id}
  engine/
    candidate.json        # signal engine output + feature snapshot ids at creation
    intent.json           # sizing, prices, policy decision (rule ids), margin check
    orders.jsonl          # order/fill events with reference prices, spreads, ack states
    accounting.json       # gross, costs, slippage, risk_inr, r_multiple (known_at = closed_at)
  sections/
    trade_manager.md      # thesis, invalidation conditions, hold notes, each entry timestamped
    risk_officer.md       # any findings touching this trade
    market_intel.md       # brief + catalyst tags relevant at vet time (copied, embargo-safe)
    post_trade_review.md  # rubric + reflection (known_at = review time)
  evidence/
    <invocation_id>.json  # prompt version, model, inputs refs, structured output, cost
```

The filesystem projection is generated from PostgreSQL for agent file tools (read) and parsed back (write to own section only, enforced by the tool). The database is the source of truth.

### 3.2 Section write rules

- A role writes only to `sections/<own_role>.md` through `dossiers:write_section`, which appends a timestamped block; it cannot edit or delete prior blocks.
- The engine writes `dossier.json`, `transitions.jsonl`, `engine/*`.
- `evidence/` is written by the runtime for every invocation that reads the dossier.
- After `archived`, the dossier is immutable.

### 3.3 Retrieval for a role ("recall similar trades")

`memory:recall_similar_trades(symbol, sleeve_id, setup_tags[], as_of, k)`:

1. Candidate set: dossiers with the same sleeve, or same symbol, or overlapping setup tags, with `created_at < as_of`.
2. Embargo: strip any field with `known_at > as_of` (outcomes, reviews written after `as_of`).
3. Rank: BM25 on the concatenated sections plus a recency decay with a per-sleeve half-life (default 90 days) — the age decay exists because old lessons anchor across regimes.
4. Return at most `k` (default 5) dossiers as structured summaries ≤ 300 tokens each, with links to full sections.
5. Log the retrieval (ids returned, embargo applied) in the invocation evidence.

No embeddings in v2.0; PostgreSQL full-text search is sufficient at this scale and is deterministic. pgvector is an optional later ADR.

## 4. Role memory

### 4.1 Layout

```
memory/roles/<role>/
  MEMORY.md               # index, ≤ 200 lines, one line per topic file, loaded every invocation
  lessons/<slug>.md       # one lesson per file (see 4.2)
  notes/<slug>.md         # working notes, scratch, never injected into trading-path prompts
  profile.md              # what this role has learned about how to do its job (procedural), reviewed quarterly
```

### 4.2 Lesson file

```markdown
---
name: results-window-veto-reduces-stopouts
role: trade_manager
status: hypothesis | validated | retired
gate_id: G6-2026-11-03-a          # required when validated
known_at: 2026-10-04T11:20:00+05:30
valid_until: 2027-04-04            # re-validation due; consolidation retires after this
scope: {sleeves: [sip_orb], regimes: [any]}
evidence:
  - dossier: 7f2c…                 # verbatim sources
  - dossier: 91aa…
  - trial: exp_sip_orb_results_veto_v1
---
Statement (one falsifiable sentence).
Rationale (≤ 10 lines).
How to apply (categorical instruction only; no numbers).
```

### 4.3 Injection policy

| Prompt type | May include |
|---|---|
| Trading-path (vetting, hold actions) | `validated` lessons in scope, ≤ 5, plus embargo-safe similar trades |
| Research | `validated` + `hypothesis` lessons (labelled), full trial history |
| Review | everything embargo-safe, including `retired` (labelled) |
| Ops | ops memory, incidents, runbooks |

### 4.4 Lesson lifecycle

1. Post-Trade Reviewer proposes a lesson (`hypothesis`) with evidence links.
2. Quant Researcher may convert it into a pre-registered trial (the lesson's implied rule as an A/B on holdout).
3. Validation Reviewer sets `validated` on a passed G6 (recording `gate_id`) or `retired` on failure.
4. Consolidation job retires lessons past `valid_until` and files a re-validation item in the backlog.

## 5. Desk knowledge (reference, read-only)

```
memory/desk/
  cost-model.md            # rates by segment, effective dates, calibration history (numbers live in rule tables; this explains them)
  universe.md              # how the point-in-time universe is built
  instruments.md           # lot sizes, freeze limits, expiries — pointer to rule tables
  regulation.md            # SEBI/NSE/Zerodha rules that bind the desk, with circular references
  gates.md                 # gate register, mirrors spec.md §9
  sleeves/<sleeve_id>.md   # each sleeve's thesis, evidence, parameters (numbers as references to config), status history
  glossary.md
```

Changed only by PR. The Compliance Auditor and Quant Researcher propose changes; the Principal merges those that alter trading behaviour.

## 6. Research memory

- **Trial ledger** (PostgreSQL, `research_trials` — schema in `research.md`): the authoritative record of every backtest.
- **Experiments** (`research/experiments/<experiment_id>/`): `preregistration.md` (committed before the run), `report.md`, `artefacts/` (paths to Parquet outputs), `verdict.md` (reviewer). Git history is the audit trail.
- **Idea forest** (`memory/roles/quant_researcher/notes/idea-forest.md`): a tree of hypotheses tried, with links to experiments and dispositions, so the Researcher does not re-run what was already falsified (RD-Agent(Q) "history-aware synthesis").

## 7. Ops memory

- `memory/ops/incidents/YYYY-MM-DD-<slug>.md`: symptom, timeline, cause, fix, follow-ups (the v1 memory notes are the model: `sidecar-token-collision`, etc.).
- `memory/ops/baselines.md`: normal ranges for health metrics, used by the checklist skill.
- Runbooks are skills (`skills.md` §6), not memory, so they are versioned with tests.

## 8. Consolidation ("sleep-time") job

Runs nightly at 22:30 IST after the research shift, as an engine job that may invoke a small agent session (`claude-haiku-4-5`) for summarisation only:

1. Re-index role `MEMORY.md` files (deterministic script) and fail if any index exceeds 200 lines.
2. Retire lessons past `valid_until`; file re-validation backlog items.
3. Archive dossiers past retention into cold storage (evidence preserved, sections frozen).
4. Produce a one-page memory health report (counts by status, retrievals per day, embargo violations detected = must be zero) into the desk journal.
5. Never merges or rewrites lessons automatically; proposed merges go to the Validation Reviewer.

## 9. Security of memory

- Agents write only through tools that enforce scope; direct filesystem writes outside the allowed paths are blocked by hooks.
- Read-write scratch (`notes/`) is never injected into trading-path prompts, which bounds prompt-injection reach (a poisoned note cannot become a validated lesson without the Reviewer and a gate).
- Announcements and other external text enter memory only as tagged features with `source_ref`, never as raw instructions; the tagging prompt treats the text as data.
- No credentials, tokens or account identifiers are ever stored in memory (constitution VIII.4); a linter runs on every memory write.

## 10. Data model (summary; full DDL in `plan.md` §7)

| Table | Purpose |
|---|---|
| `dossiers` | one row per trade; state, sleeve, symbol, engine fields, timestamps, hash chain |
| `dossier_sections` | role, dossier_id, seq, content, written_at, known_at, invocation_id |
| `dossier_events` | transitions and engine events |
| `memory_items` | mirrored role memory (role, path, content, status, known_at, valid_until, version, prior_hash) |
| `memory_retrievals` | audit of what was returned to whom, with embargo cut-off |
| `invocations` | every agent invocation with cost, model, prompt version, input/output refs |
| `journal_entries` | desk journal structured rows |

## 11. Acceptance scenarios

- **M1 Embargo.** Given dossier A closed on day D with a review on D+1, When recall runs for `as_of = D 10:00`, Then A is returned without accounting or review fields and the retrieval log records the cut-off.
- **M2 Own section only.** Given the Trade Manager attempts to write to `sections/risk_officer.md`, When the tool is called, Then it is denied and logged.
- **M3 Validated only.** Given a `hypothesis` lesson in scope, When a vetting prompt is assembled, Then the lesson is absent; after `validated` with a gate id, it is present.
- **M4 Index bound.** Given a role index exceeding 200 lines, When consolidation runs, Then the job fails the memory health check and alerts.
- **M5 Replay.** Given an invocation id, When replay is requested, Then the same inputs (by reference hash) are reassembled and the stored output is shown alongside a fresh run's output for diff.
