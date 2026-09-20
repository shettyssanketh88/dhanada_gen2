# ADR-006 — Scheduler and durability: engine-owned shift runner on PostgreSQL

## Status
Proposed (2026-09-20).

## Context
Always-on operation needs crash-resumable shifts, budgets and an event queue. Options: Temporal/DBOS/Restate; Managed Agents scheduled deployments; cron + scripts; an engine-owned runner.

## Decision
An **engine-owned durable shift runner**: `shift_runs` and `shift_steps` tables, idempotent steps with keys and retries, an `engine_events` queue for event-driven steps, APScheduler for time triggers, per-shift budgets. A crash resumes at the first incomplete step.

## Revisit triggers
Adopt Temporal (or DBOS) if any of: more than one VM, human-approval waits longer than a day inside a workflow, or step graphs exceed what a table-driven runner can express clearly. Managed Agents scheduled deployments are acceptable for research-only shifts (jitter tolerant).
