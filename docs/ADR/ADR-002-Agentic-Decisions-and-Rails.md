# ADR-002 — Agentic decisions, owner-set rails

## Status
Proposed (2026-09-20). Supersedes the same-day ADR-002 "Two planes: agents decide categories, code decides numbers", withdrawn on the Principal's direction that all decisions be agent-driven.

## Context
v1 put one LLM planner in the entry path without instruments, memory or feedback and measured zero lift (docs/lessons-from-v1.md F4). The Principal's reading is that the LLM was used badly, not that agents cannot decide. The evidence on anchoring, overtrading and look-ahead (docs/research/2026-09-20-multi-agent-llm-trading-systems.md) is real and must be answered by design, not by removing agents from decisions.

## Decision
1. Every trading and organisational decision is made by a named agent role (constitution I). Code computes, executes, remembers, scores and enforces rails; it never decides.
2. Rails are only: the Principal's IPS limits, regulator and broker mechanics, and the kill switch (`rails/RAILS.md`). They reject and explain; they never silently alter a decision.
3. Anchoring, overconfidence and drift are countered by: calculators the agent must call and cite; prompts free of system-injected numbers and rankings; per-role calibration records in context; decision scoring against counterfactual baselines; a Coach that revises playbooks with evidence; the Validation Reviewer's adversarial verdict on anything with trading impact.
4. The Principal is informed of organisational decisions and approves only IPS, rails and constitution changes.

## Consequences
- The firm's quality depends on the learning loop working; Phase 2 (Coach, Lab, Skill Engineer) is not optional.
- LLM spend is higher than in the withdrawn design (decisions per trade rather than per feature); budgets are rails.
- The withdrawn design's measurement instruments (counterfactuals, DSR with N and k, calibration) are retained as instruments the agents and the Coach use, not as gates that decide.
