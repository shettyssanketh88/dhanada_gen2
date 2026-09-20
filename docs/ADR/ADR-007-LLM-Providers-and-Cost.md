# ADR-007 — LLM providers and cost governance

## Status
Proposed (2026-09-20).

## Context
v1 (2026-06-12) made OpenAI primary and Claude the fallback for cost reasons, then found gpt-4o-mini could not do the planning task and modern OpenAI models needed parameter changes. v2's runtime is the Claude Agent SDK (ADR-001), which requires Claude models for agent sessions.

## Decision
- Agent sessions run on Claude: `claude-opus-5` for reasoning roles (Researcher, Reviewer, Portfolio Manager, Risk Officer, Compliance), `claude-sonnet-5` for Trade Manager vetting, Desk Head, Ops and per-trade review, `claude-haiku-4-5` for bulk classification and consolidation summaries. Adaptive thinking; effort per role.
- Pure classification batch jobs (catalyst tagging on history) go through a thin provider gateway and may use any provider chosen by measured accuracy and cost, with the prompt version and provider recorded per tag.
- Budgets: per-shift `max_budget_usd`, daily desk cap, per-candidate vetting cap; `total_cost_usd` recorded per invocation; cost per trade and per trial reported weekly.
- Prompt caching via stable per-role system prefixes.

## Consequences
- Estimated steady-state spend: USD 15–30 per trading day at the budgets in operations.md; research dominates.
- Model upgrades are a versioned change to a role definition with eval re-runs, not a config flip.
