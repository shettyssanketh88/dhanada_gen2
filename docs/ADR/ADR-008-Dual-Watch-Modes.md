# ADR-008 — Dual watch modes for the Execution Agent, evaluated against each other

## Status
Proposed (2026-09-20), on the Principal's direction to have both and evaluate them.

## Context
The Execution Agent applies the Senior Analyst's strategy book to the tape. Two mechanisms exist: a deterministic evaluator of crisp conditions that invokes the agent on events (Rule Watch), and a continuous agent session that reads 1-minute digests and tick events and evaluates crisp and judgment conditions itself (Agent Watch). Rule Watch is cheap and low-latency but cannot evaluate judgment conditions; Agent Watch can, at higher cost and latency, and may drift from the book.

## Decision
- Implement both. Every dossier runs one mode as governing and the other as shadow (paper-only, would-be actions and simulated fills recorded).
- Code computes a weekly watch-mode report per desk and strategy family (fidelity, latency, slippage, LLM cost per stock-day, escalation precision/recall, judgment coverage, outcome deltas, n and CIs).
- The investment committee decides governance per desk (Rule Watch, Agent Watch, or split by `condition_kind`), may alternate governance by session early on, and records the evidence for each decision; the Coach scores those decisions later.
- Strategies with `condition_kind: judgment` are evaluated only by Agent Watch; under Rule Watch governance they are handed to Agent Watch or escalated.
- Agent Watch concurrency is capped per desk by the CIO within the IPS budget.

## Consequences
- Double execution logs per dossier; the shadow path must be structurally unable to place broker orders (test T13).
- Costs are visible per mode; governance is an evidence-based agent decision, not a fixed architecture choice.
