# Memory architecture

*Companion to `spec.md` v2.0 (DH2-MEM-*). Every role remembers; every trade is a dossier every role writes into; the Coach curates what the firm believes. Evidence base: CoALA taxonomy; FinMem layered memory; FinAgent low/high-level reflection; FinCon belief propagation; TradingAgents per-role reflection and its embargo bug; verbatim-over-extracted result (arXiv 2601.00821); Anthropic memory tool and auto-memory conventions.*

## 1. Principles

1. **Per role, per entity.** A role's memory is its own. A trade's memory (dossier) has a section per role. Desk and firm memories are shared with explicit write rights.
2. **Time-aware.** Every item carries `known_at`; a decision at T retrieves only `known_at ≤ T` (replay-safe).
3. **Evidence with every lesson.** Lessons link to the verbatim dossiers, trials and scores they came from; retrieval returns both.
4. **Agents curate their own memory; the Coach decides what the firm adopts.** Lesson status (`proposed | adopted | retired`) is the Coach's decision, with the Validation Reviewer for trading-impact lessons.
5. **Ledger over memory.** Positions, fills, cash and costs are read from the execution service, never remembered.
6. **Versioned.** Every write records actor, time, prior hash; point-in-time reads exist.

## 2. Scopes (CoALA mapping)

| Scope | Type | Owner | Readers | Writers | Storage |
|---|---|---|---|---|---|
| Working memory | working | the session | itself | itself | context + recited plan file |
| Trade dossier | episodic per entity | Execution service (facts) + owning roles | desk team, Risk Office, Coach, Reviewers, Research Lab (time-aware) | execution service (facts), each role (own section) | PostgreSQL + file projection |
| Role memory | semantic + procedural | the role | the role, Coach, Validation Reviewer | the role; Coach (lesson status, playbook revisions) | git-backed markdown `memory/roles/<role>/` + PostgreSQL mirror |
| Desk memory | semantic + episodic | the desk | desk team, CIO, Coach | desk roles per charter; Strategist curates | `memory/desks/<desk_id>/` |
| Firm memory | semantic | CIO | all | CIO, Risk Office (risk section), Coach (lessons index), Compliance (rules pointers) | `memory/firm/` |
| Research memory | episodic + semantic | Research Lab | Lab, CIO, Coach | Researcher, Reviewer, Data Steward | trial ledger + `research/experiments/` |
| Ops memory | episodic + procedural | Operations | Ops, Compliance, Coach | Ops | `memory/ops/` |
| Journal | episodic firm-level | Desk Head function (CIO's shift) | Principal, all | CIO shift | `journal/` |

## 3. Trade dossier

```
dossier/<id>/
  dossier.json          # facts: state, desk, symbol, product, qty, fills, costs, R, timestamps, playbook_version, hash chain
  transitions.jsonl     # {from, to, actor_role, at, reason, invocation_id}
  facts/
    orders.jsonl        # order intents, acks, fills, reference prices, spreads
    accounting.json     # known_at = closed_at
    counterfactuals.json# no_trade, per_book_version, per_watch_mode(shadow), unmodified_by_risk (written at close)
  sections/
    scanner.md          # why picked, priority, features used
    data_ingestor.md    # data pack refs, quality flags, excluded windows
    analyst.md          # each book version: strategies, instruments used, reasoning; escalation resolutions
    risk_officer.md     # per-version reviews, modifications, notices
    execution.md        # matches, orders, fills, escalations, mode (governing/shadow), book_version per action
    recalibration.md    # revision requests with evidence; regime assessment
    trade_reviewer.md   # per-agent scores, findings, lesson proposals
    coach.md            # coaching notes
  books/v<n>.yaml       # every strategy book version that governed, immutable
  evidence/<invocation_id>.json  # prompt/skill versions, model, input refs, output, cost
```

- A role writes only its own section (append-only blocks), through `dossiers:write_section`.
- `facts/` is written by the execution service; agents cannot write it.
- Every section block carries `known_at`; the decision it records is scored later against `facts/` and `counterfactuals.json`.

### Continuing work on a trade

When a role is re-invoked for a dossier (new event, next day, after a restart), the launcher assembles: the role's playbook, its calibration summary, adopted lessons in scope, the dossier facts as of now, and **all sections** (own and others') up to now. The role therefore resumes with its own prior reasoning intact and everyone else's, which is what "memory per trade per agent type" means in practice.

## 4. Role memory

```
memory/roles/<role>/
  MEMORY.md             # index ≤ 200 lines, loaded every session
  playbook.md           # how this role does its job; versioned; revised by the role or the Coach
  calibration.md        # generated: stated p vs outcome, expected R vs realised, counterfactual deltas, by desk and regime, with n and CIs
  lessons/<slug>.md     # status proposed|adopted|retired; evidence refs; scope; valid_until
  notes/<slug>.md       # scratch; never injected automatically
```

Lesson file frontmatter: `name, role, status, decided_by (coach), decided_at, known_at, valid_until, scope {desks, regimes, horizons}, evidence [dossier/trial/score refs]`, then statement, rationale, how-to-apply.

Injection: adopted lessons in scope are included in the role's context (bounded by a per-role count the Coach sets in the playbook); proposed lessons are visible to the role as "under review"; retired lessons are visible only to reviews.

## 5. Desk memory

```
memory/desks/<desk_id>/
  CHARTER.md            # CIO-owned
  playbook.md           # desk procedure; Strategist curates; Coach revises with evidence
  MEMORY.md             # index
  watchlist.md          # current, with reasons and dates
  regimes.md            # the desk's own regime notes
  lessons/              # desk-level lessons (adopted by Coach)
  meetings/YYYY-MM-DD.md# minutes with positions and decisions
```

## 6. Firm memory

```
memory/firm/
  MEMORY.md
  strategy.md           # CIO's firm strategy and allocation rationale history
  risk-guidance.md      # Risk Office's standing guidance per desk
  lessons-index.md      # adopted lessons across roles (Coach)
  market-knowledge/     # cost arithmetic, microstructure notes, regulation pointers — proposed by any role, adopted by Coach/Compliance
  glossary.md
```

## 7. Retrieval

`memory:recall(query, scope[], as_of, k)`:

1. Candidate items from the requested scopes with `known_at < as_of`.
2. Strip outcome fields whose `known_at > as_of`.
3. Rank: PostgreSQL full-text (BM25-like) + recency decay with a half-life the requesting role's playbook sets (default 90 days).
4. Return ≤ k structured summaries (≤ 300 tokens each) with references; log the retrieval (ids, cut-off) in the invocation evidence.

`memory:recall_similar_trades(desk_id?, symbol?, tags[], as_of, k)` is the dossier-specialised form.

No embeddings in v2.0 (ADR-003); pgvector is a later ADR if recall proves insufficient.

## 8. Consolidation (nightly, 22:30 IST)

Each role runs a short curation session on its own memory (index, merge duplicates, mark `notes/` for archive, propose `valid_until` extensions), producing a diff. The Coach reviews the diffs (adopt/retire decisions, playbook impacts). A deterministic script then rebuilds indexes, archives, and writes the memory health report (counts by status, retrievals per day, embargo violations detected — must be zero). Evidence is never deleted.

## 9. Security

- Writes only through scoped tools; hooks block direct writes outside a role's paths.
- External text (announcements, circulars) enters memory only as tagged items with `source_ref`; prompts state it is data.
- No credentials or account identifiers in memory; a linter runs on every write.
- Poisoning containment: `notes/` never auto-injects; a lesson reaches trading context only after the Coach adopts it.

## 10. Data model (summary)

| Table | Purpose |
|---|---|
| `dossiers`, `dossier_sections`, `dossier_events`, `dossier_evidence`, `dossier_counterfactuals` | trade memory |
| `memory_items` (scope, path, content, status, known_at, valid_until, version, prior_hash, actor) | mirrored markdown memory |
| `memory_retrievals` | audit of what was returned, to whom, with cut-off |
| `decision_scores` (invocation_id, role, desk, type, stated_p, outcome, expected_r, realised_r, counterfactual_deltas, process_flags) | calibration inputs |
| `playbook_versions` | role and desk playbooks with diffs and rationale |
| `invocations` | every session with cost, model, prompt/skill versions, refs |

## 11. Acceptance scenarios

- **M1** Time-aware recall strips outcomes and later reviews (as in spec S5).
- **M2** A role cannot write another role's section (denied, logged).
- **M3** A `proposed` lesson is absent from a Trader's context; once `adopted` it is present; once `retired` it is absent.
- **M4** Re-invoking a Position Manager after a restart shows its own prior actions and the Trader's plan in context.
- **M5** Replay of an invocation reassembles the same references and shows stored vs fresh output.
- **M6** Consolidation fails the health check if any index exceeds 200 lines or any embargo violation is detected.
