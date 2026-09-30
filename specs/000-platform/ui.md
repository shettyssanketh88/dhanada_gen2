# Owner interface — console, Telegram companion, and "Ask the firm"

*Companion to `spec.md` v2.2 (adds DH2-UI-*). Sources: `docs/research/2026-09-30-ui-ux-patterns.md`, `docs/research/2026-09-30-ui-stack-evaluation.md`. Replaces the "Dashboard (v2.0, minimal)" sketch in `operations.md` §8.*

## 1. Decision

**A responsive web console (installable PWA) as the system of record, plus a Telegram bot that carries only interrupts and digests, both driven by one approval state machine. No terminal UI.** An "Ask the firm" chat over the dossiers lives inside the console and as a Telegram command.

Why this shape: every 2025–26 supervisor-of-many-agents product (Codex app, Devin coordinator, Claude Code remote control, Managed Agents console) and both mature trading-bot ecosystems (Hummingbot Condor, Freqtrade FreqUI + Telegram) converged on it independently. A TUI would be a second front end that cannot render diffs or charts and is unusable on a phone; Freqtrade's own TUI is a stalled monitor-only alpha. Chat alone cannot carry a 2,000-word journal or a book diff.

Two India-specific facts shape the design: the daily broker login is a regulatory ritual (SEBI April-2026 framework), so the console surfaces it rather than hiding it; and the kill switch is a compliance object that must work from a phone.

## 2. Principles

1. **The Principal's levers are approve, edit, pause, kill, ask.** No manual order entry anywhere, in paper or live (constitution I; anti-pattern: override buttons train intervention and invalidate the two-scale paper comparison).
2. **The Inbox is the unifying object.** Every human touchpoint is an interrupt card with the verbs Accept / Edit / Respond / Ignore, an expiry, and an actor record. Approval is a state machine (`draft → requested → approved | rejected | expired`), idempotent, attributed.
3. **Reading layouts for thinking, dense layouts for the desk.** Bloomberg density only on the Desk screen; Journal, Dossier and Governance screens are prose-first.
4. **Measure in R; show distributions, not headlines.** No win-rate headline; no rupee P&L above the fold on the home screen (myopic loss aversion). Rupee P&L lives on the Desk and in the weekly digest.
5. **Progressive disclosure of reasoning.** Each role's section shows a one-paragraph verdict; expand for full reasoning, cited data and instruments used.
6. **Versioned artefacts are reviewed as diffs.** Book v2 → v4, IPS, rails, constitution, playbooks: side-by-side plus a semantic change list; approval is on the diff.
7. **Notifications are budgeted.** Per-event levels on / silent / off; push only for login due, Inbox item, pause/kill, rail breach, broker disconnect, reconciliation break. Everything else is silent or in the digest.
8. **Read-only by construction.** The console's data endpoints and the chat's tools run on a read-only database role; the few write endpoints require a second factor and are recorded in `signed_actions`.
9. **Opinionated screens.** Fixed layouts; configurable only notification levels and column visibility.

## 3. Information architecture

| # | Screen | Purpose | What it shows | Phone |
|---|---|---|---|---|
| 1 | **Today** (home) | The day at a glance | Strip: firm mode (`PAPER-FIRM` / `PAPER-MIRROR` / `LIVE`), broker session (with **Log in now** before 09:15), IPS and constitution versions, kill state. Then Inbox count, drawdown vs limit gauge (limits drawn), regime label, 3-line CIO summary, link to today's Journal. **No P&L figure.** | Landing page |
| 2 | **Inbox** | Everything that needs the Principal | Cards: role, title, arguments, markdown rationale, expiry, enabled verbs (Accept / Edit / Respond / Ignore); filters Governance / Promotion / Coach / Ops; History tab (who decided, when, how) | Full |
| 3 | **Desk** | Dense operating view | Positions grouped by book: qty, entry, stop, current R, MAE/MFE, watch status light; order blotter with strategy id, book version, rejection reasons; exposure vs rails as bars; agent roster chips (idle / running / needs-you / errored, last heartbeat, cost today); keyboard `/` symbol jump, `d` open dossier | Read-only, one column |
| 4 | **Dossiers** | Why each trade happened | List with outcome in R, book version, score. Detail: timeline of role sections (Scanner → Ingestor → Analyst → Risk → Compliance → Execution → Recalibration → Reviewer) collapsed to verdict lines; candle chart with entry/stop/targets/exit and book zones drawn; Replay stepping through the event log; counterfactual panel (per book version, per watch mode); reviewer scores | Full |
| 5 | **Books** | Strategy books | Per stock: current version, changelog, diff between any two versions (side-by-side YAML + semantic change list), which dossiers used which version and their aggregate R, pending recalibration requests and clearances | Semantic diff |
| 6 | **Agents** | Scorecards | Per role: decisions per week, calibration (reliability curve), counterfactual delta, override rate by Risk/Compliance, execution fidelity, LLM cost, error/REVIEW rate; activity log; "message this role" (routed to the Coach) | Read-only |
| 7 | **Journal & Digest** | Reading | Daily journal; weekly digest with DSR and N beside any Sharpe; open questions | Full |
| 8 | **Governance** | The Principal's documents | IPS, rails, constitution, broker confirmation as versioned documents; proposal → diff → approve with re-auth; kill switch (two-step, hold-to-confirm, reason); audit export | Kill and approve |
| 9 | **Ask** | "Why did we…?" | Chat over dossiers, books, ledger and journal with citations; answers render catalogue widgets (dossier card, rule card, diff, R chart) | Full |
| 10 | **Research Lab** | Evidence | Backlog, experiments, trials with N/k/DSR, desk proposals and verdicts, watch-mode reports | Read-only |
| 11 | **Compliance** | Rules | Clearances per book version, alerts and dispositions, holds, EOD reports, catalogue versions with effective dates, self-audit bundles | Read-only |

### 3.1 Today (phone width)

```
┌─────────────────────────────────┐
│ DHANADA · PAPER-FIRM · IPS v0.2 │
│ Broker: no token  [Log in now]  │
│ Kill: OFF        Regime: trend↑ │
├─────────────────────────────────┤
│ Inbox  ●3   Drawdown ▮▮▮▯▯ −2.1%│
│                     limit −5% ½ │
├─────────────────────────────────┤
│ CIO: Two desks armed; RELIANCE  │
│ book v4 after 12:30 recal; one  │
│ compliance hold on SAIL (ASM).  │
│ → Journal                       │
└─────────────────────────────────┘
```

### 3.2 Dossier detail (laptop)

```
RELIANCE · Intraday Breakout · 2026-09-22 · book v2→v4 · closed +1.45R · score 4.2/5
┌ chart: candles 15m, S1 zone, stop 2,925→2,940, T1 3,025, exit 3,018 ┐
├ timeline ────────────────────────────────────────────────────────────┤
│ 07:45 Scanner      ▸ picked: 15m trend up, coiling under 2,960, RVOL 1.4×   │
│ 08:00 Ingestor     ▸ pack ok; 09-12 bar gap excluded                          │
│ 08:35 Analyst v1   ▸ S1 breakout, S2 fade, S3 pullback; instruments: ATR…     │
│ 08:50 Risk         ▸ modify S2 stop (cost/R 0.10); approved v2                 │
│ 08:52 Compliance   ▸ clear S1,S3; S2 clear w/ condition "no orders >15:05"   │
│ 10:42 Execution    ▸ S1 match → 162 @ 2,964; stop/T1 working                   │
│ 11:20 Execution    ▸ escalate: invalidation with open position                 │
│ 11:23 Analyst v3   ▸ hold S1, stop → 2,940, cancel S3                           │
│ 12:30 Recalibration▸ retire S3 family today; T1 → 3,025  (v4)                  │
│ 13:55 Execution    ▸ T1 hit ½; stop → entry per book                           │
│ 15:00 Execution    ▸ square-off ½ @ 3,018 (CAS stock)                           │
│ 16:30 Reviewer     ▸ scores; lesson: invalidation rules need open-pos clause  │
├ counterfactuals: v2 as filed +1.05R · v4 +1.45R · shadow Agent Watch +1.38R ┤
└ [Replay] [Ask why] [Open book v4 diff] ──────────────────────────────────────┘
```

## 4. Telegram companion

Owner-only allowlist (single Telegram user id). Eight verbs, nothing else:

| Verb | Effect |
|---|---|
| `/login` | Deep link to the broker OAuth flow; sent automatically at 08:30 if no token |
| `/inbox` | Pending cards with inline **Accept** / **Edit** (opens console) / **Ignore**; Accept on a governance item requires the TOTP reply |
| `/desk` | Compact positions table in R and exposure vs rails |
| `/journal` | Today's summary + link |
| `/why <id or symbol>` | Ask-the-firm answer with citations and a console deep link |
| `/pause <desk>` | Level-1 pause, confirmation required |
| `/kill` | Level-2 halt; requires the current TOTP code within 60 s; one code, one action |
| `/status` | Firm mode, broker, kill state, spend today |

Push notifications (only these): login due, new Inbox item, pause/kill events, rail breach, broker disconnect or token failure, reconciliation break, budget exhaustion. Everything else is silent or batched into the daily digest at close and the weekly digest on Saturday. Alerts in market hours are batched per minute to respect Telegram rate limits.

## 5. Ask the firm

- Chat over dossiers, books, ledger, journal, compliance records. Tools are **read-only by construction**: `search_dossiers`, `get_dossier_section`, `get_book_version`, `diff_book_versions`, `get_positions`, `query_ledger`, `get_journal`, `get_compliance_record`. Each returns content plus a citation (`dossier_id`, section, version, url); the UI renders citation chips that deep-link.
- Answers use a fixed widget catalogue (dossier card, rule card, book diff, R chart, calibration chart, table) chosen by the model; no free-form HTML.
- Enforcement: read-only DB role; `chat:read` session scope; a structural test that the chat tool registry imports nothing from execution, approvals or memory-write modules.
- Time-aware: the chat reads with `as_of = now` and shows `known_at` for anything it cites.

## 6. Stack (from the evaluation, ADR-010)

| Layer | Choice |
|---|---|
| Front end | Vite 8 SPA, React 19, TypeScript ~7.0 (fallback 5.9), react-router 8, Tailwind 4 + shadcn (Radix), TanStack Query 5 + Table 9, lightweight-charts 5.2 + official toolkit for candles/zones, Recharts 3 for calibration/drawdown/scores, react-diff-viewer-continued for YAML diffs plus a server-side semantic diff, AI SDK 7 `useChat` + assistant-ui for the chat, zod + `openapi-typescript`/`openapi-fetch` generated from FastAPI's OpenAPI |
| Package management | pnpm 12 pinned via `packageManager`, `pnpm-lock.yaml` committed, `--frozen-lockfile` in CI, `engine-strict` (v1's "no lockfile" pain does not recur) |
| Real-time | One `GET /api/events` SSE stream (sse-starlette) multiplexing the firm event bus → TanStack Query invalidation; `Last-Event-ID` resume; 15 s pings; `refetchInterval` fallback |
| Backend | FastAPI `/api/*` JSON envelope; Postgres LISTEN/NOTIFY fan-out; `POST /api/chat` streaming AI SDK message frames from the Anthropic SDK |
| Telegram | aiogram 3 via webhook at `/tg/<secret>` behind Caddy with `secret_token`; inline keyboards; `itsdangerous` one-time tokens; `signed_actions` shared with the console |
| Auth | Access over **Tailscale** (confirmed by the Principal 2026-09-30; laptop + phone join the tailnet, console bound to the VM's tailnet address); passkeys (py_webauthn 3) with TOTP fallback; signed `HttpOnly; Secure; SameSite=Lax` cookie, 12 h idle; dangerous actions need a fresh WebAuthn assertion (`userVerification: required`) or TOTP plus an `Idempotency-Key` |
| Hosting | `ui/dist` served by Caddy (`try_files → index.html`), `reverse_proxy /api/* app:8000` with `flush_interval -1`; public vhost only for `/tg/*` and `/api/health` |
| Observability | Business health natively in the console (feed lag, last agent tick, event-bus lag, spend); Grafana + Prometheus + Loki + Alloy as a separate Compose profile on the tailnet; no Grafana iframes |
| Testing | Playwright (Chromium) against a seeded API fixture; `tsc --noEmit`; eslint; OpenAPI type drift check (`git diff --exit-code` on the generated schema) |

## 7. Requirements (UI)

- **DH2-UI-001** THE SYSTEM SHALL provide a responsive web console with the eleven screens in §3, usable at phone width for Today, Inbox, Dossiers, Journal, Governance (approve, kill) and Ask.
- **DH2-UI-002** THE SYSTEM SHALL expose no manual order entry, modification or cancellation in any interface; the Principal's actions are approve, edit (of a proposal), respond, ignore, pause, kill and ask.
- **DH2-UI-003** THE SYSTEM SHALL implement approvals as a state machine (`draft → requested → approved | rejected | expired`) with expiry, idempotent decisions, actor and method recorded in `signed_actions`, shared by console and Telegram.
- **DH2-UI-004** THE SYSTEM SHALL require a second factor (fresh passkey assertion or TOTP) for kill, pause, approvals of governance items, compliance-alert clearance and go-live, and SHALL record each in `signed_actions`.
- **DH2-UI-005** THE SYSTEM SHALL show no win-rate headline and no rupee P&L above the fold on Today; expectancy in R, drawdown vs limits, DSR with N, and calibration are the headline metrics.
- **DH2-UI-006** THE SYSTEM SHALL render every versioned artefact (book, IPS, rails, constitution, playbook) as a side-by-side diff with a semantic change list and the author's rationale, and SHALL take approvals on the diff.
- **DH2-UI-007** THE SYSTEM SHALL update the console from the firm event bus over SSE with Query invalidation within 5 s of an event, falling back to 60 s polling when disconnected.
- **DH2-UI-008** THE SYSTEM SHALL provide a Telegram bot bound to one owner id with exactly the eight verbs in §4, per-event notification levels (on / silent / off), and market-hour batching.
- **DH2-UI-009** THE SYSTEM SHALL provide the Ask chat with read-only tools, citations to dossiers/books/ledger, catalogue widgets, and `known_at` on cited facts; a structural test SHALL prove the tool registry cannot reach write modules.
- **DH2-UI-010** THE SYSTEM SHALL serve the console only over the tailnet (plus the Telegram webhook path publicly), authenticate with passkeys or TOTP, and log every session and dangerous action to the audit chain.
- **DH2-UI-011** THE SYSTEM SHALL pin the front-end toolchain (pnpm `packageManager`, committed lockfile, frozen install, engine-strict) and fail CI on OpenAPI type drift, type errors, lint errors or Playwright failures.
- **DH2-UI-012** THE SYSTEM SHALL surface the daily broker login on Today and via Telegram before 09:15 IST with a one-tap deep link, and SHALL show `awaiting_login` until the token exists.

## 8. Acceptance scenarios

- **U1** At 08:30 with no token, the phone receives one Telegram reminder with a deep link; Today shows `awaiting_login` and **Log in now**; after login the strip turns green without any other action.
- **U2** A Coach playbook revision arrives as an Inbox card with a semantic diff; the Principal taps **Edit**, changes one value in the console, re-authenticates with a passkey, and the decision is recorded with actor, method and time; the card expires automatically after its window if untouched.
- **U3** `/kill` in Telegram asks for the TOTP code; a wrong or late code does nothing; a correct code engages level 2, the console shows the kill state within 5 s, and `signed_actions` has one row.
- **U4** Opening a closed dossier shows the timeline with verdict lines, the candle chart with entry/stop/targets/exit and book zones, and counterfactuals per book version and per watch mode; Replay steps through the events.
- **U5** Asking "why did we exit RELIANCE at 15:00?" returns the dossier card, the book rule that fired, the R chart, and citations that deep-link; the tool registry test proves no write path exists.
- **U6** The Today screen contains no rupee P&L and no win rate (Playwright assertion).
- **U7** A `book.version` event on the SSE stream refreshes the Books screen within 5 s; with the stream disconnected the screen refreshes within 60 s.
- **U8** CI fails when `pnpm-lock.yaml` is out of date, when generated OpenAPI types differ from the server schema, or when any Playwright scenario fails.
