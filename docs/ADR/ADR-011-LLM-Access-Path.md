# ADR-011 — LLM access path: direct vendor APIs, not an aggregator

## Status
Proposed (2026-10-02), on the Principal's question "OpenRouter or direct vendors?"; the Principal is aligned.

## Context
The firm's agent runtime is the Claude Agent SDK (ADR-001) and its cost model (ADR-007, `docs/decisions/2026-09-21-open-items.md`) depends on prompt caching, structured outputs, adaptive thinking, context editing/compaction for long Agent Watch sessions, task budgets, server-side fallbacks and the Batch API. Every invocation is recorded with its model for replay and compliance. Aggregators (OpenRouter and similar) normalise to a common API, route one model name across several upstream providers, add their own logging and retention layer, charge a markup on credits, and offer no batch discount.

## Decision
1. **Production paths (agent runtime, watch modes, classification gateway, Ask the firm) call vendors directly** through their official SDKs: Anthropic first; OpenAI or Google only where ADR-007's measured-accuracy rule selects them for a classification seat; Jev as a direct integration under its own evaluation (`docs/decisions/2026-10-02-jev-evaluation.md`).
2. Every call records provider, model id, request id and prompt/skill versions in `invocations`; prompt-cache hit rate is a reported metric.
3. **OpenRouter may be used only by the Research Lab for throwaway model comparisons**, behind a separate key, never on a path that writes to a dossier, book, memory or ledger. A structural test asserts no production module imports the aggregator client.
4. Resilience comes from the SDK's retries, Anthropic's server-side model fallbacks, and the firm's fail-open design (last instructions stand; rails hold), not from multi-provider routing of the same request.

## Consequences
- One primary SDK to keep correct (v1 broke on an OpenAI parameter change); Batch API and cache discounts retained.
- Adding a second production vendor is a deliberate, logged integration, not a routing flag.
