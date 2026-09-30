# ADR-010 — Owner interface: web console + Telegram interrupts, no TUI

## Status
Proposed (2026-09-30), on the Principal's request for a fresh UI.

## Context
The Principal needs to log in daily, read a journal and digest, approve governance items, pause or kill, and understand why the firm did what it did, from a laptop and a phone. Research (`docs/research/2026-09-30-ui-ux-patterns.md`, `docs/research/2026-09-30-ui-stack-evaluation.md`) shows every 2025–26 supervisor-of-agents product and both mature trading-bot ecosystems converged on a web console as system of record plus a chat channel for interrupts and digests; TUIs are monitor-only, phone-unusable and a second front end.

## Decision
1. **Web console** as an installable PWA: Vite 8 + React 19 + TypeScript, Tailwind 4 + shadcn, TanStack Query/Table, lightweight-charts for candles and book zones, Recharts for calibration/drawdown, YAML diff with semantic change list, AI SDK + assistant-ui for "Ask the firm". pnpm with a committed lockfile and frozen installs (v1 lesson).
2. **Telegram bot** (aiogram, webhook) bound to one owner id with eight verbs; interrupts and digests only; kill/approve require TOTP; shared `signed_actions` with the console.
3. **No terminal UI.** The CLI covers SSH operations.
4. **Real-time via SSE** from the firm event bus into Query invalidation; 1-minute cadence is sufficient.
5. **Access over Tailscale**, passkeys with TOTP fallback, second factor on dangerous actions; the public vhost serves only the Telegram webhook and health.
6. **Principal levers are approve, edit, respond, ignore, pause, kill, ask.** No manual order entry in any mode. No rupee P&L above the fold; no win-rate headline.
7. Grafana stack separate on the tailnet; business health native in the console.

## Consequences
- ~23 agent-days for v0 (estimate in the stack evaluation); Telegram bot ~2 days of that.
- One front-end codebase; OpenAPI type generation keeps agents from drifting the wire types.
- The Ask chat's read-only tool registry is enforced by a structural test.
