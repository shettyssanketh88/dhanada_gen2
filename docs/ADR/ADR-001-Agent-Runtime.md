# ADR-001 — Agent runtime: Claude Agent SDK, self-hosted on the VM

## Status
Proposed (2026-09-20), pending Principal approval.

## Context
v2 is skill-based and role-based. Three runtimes were evaluated (docs/research/2026-09-20-agent-engineering-state-of-the-art.md §2; claude-api skill docs on Managed Agents):

| Option | Pros | Cons |
|---|---|---|
| Claude Agent SDK (Python) on the VM | Skills from `skills/`, subagents as `AgentDefinition`, hooks (enforced deny), sandbox, `max_budget_usd`, structured `output_format`, data locality (Postgres/Parquet on the box), no schedule jitter | We host the loop; sessions are not resumable across hosts (we do not need that) |
| Managed Agents (cloud harness, self-hosted sandbox) | Versioned agent objects, memory stores with versions, scheduled deployments, per-run budgets, outcomes/rubrics, no loop code | Beta; tool I/O transits Anthropic; cron jitter up to 9 min; not ZDR; another trust boundary next to the broker; memory store sync semantics on self-hosted |
| CrewAI (v1) | Familiar | v1 lesson: framework glue without enforcement; no skills/hooks; agents never ran in the live path |

## Decision
Use the **Claude Agent SDK** as the single agent runtime, self-hosted on the Mumbai VM. Roles are `AgentDefinition`s generated from `agents/<role>/ROLE.md`; skills follow the open Agent Skills spec; enforcement is by `PreToolUse` hooks, tool allowlists and the sandbox; budgets by `max_budget_usd`/`max_turns`; outputs by JSON-schema `output_format` validated with Pydantic.

## Consequences
- One trust boundary (the VM) holds data, engine and agents; agents still never hold broker write credentials (ADR-002).
- Scheduling is engine-owned (ADR-006).
- Revisit for research shifts only (Phase 5.3) if VM compute or isolation becomes limiting; trading roles stay on the VM.
