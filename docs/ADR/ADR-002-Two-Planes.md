# ADR-002 — Two planes with a hard boundary

## Status
Proposed (2026-09-20).

## Context
v1 put the LLM in the entry path and measured zero lift (docs/lessons-from-v1.md F4). Evidence across TradeTrap, NOFX, DXRG and the 2026 surveys says the deterministic ledger and risk engine must sit outside the model with clamps it cannot override.

## Decision
- **Engine plane** (deterministic): data, features, signal engines, policy gate, OMS, accounting, simulation, ledger/stats, governor, kill switch, dossier store, scheduler. No LLM client may be imported (structural CI test).
- **Agent plane**: roles, skills, memory. Agents reach the engine only through typed MCP tools scoped per role; write tools take reason enums and never numbers.
- Broker credentials exist only in the engine's secret store. Hooks deny agent access to secrets, environment files, broker endpoints and the live database.
- Any LLM feature on the trading path is deployed as an A/B arm against the mechanical baseline (spec DH2-TRD-005, G4).

## Consequences
- "Fully agentic" means the organisation is agentic; numbers are code. This is a deliberate narrowing of the request "only order execution is static" — signal levels, sizing, risk policy and simulation are also static because the evidence shows LLM-produced numbers anchor and lose.
- The Trade Manager's value is measured, not assumed.
