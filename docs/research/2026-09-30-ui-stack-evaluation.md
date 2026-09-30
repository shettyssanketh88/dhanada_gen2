# UI stack evaluation — owner console for the agent-run firm

*Research date 2026-09-30. Versions read live from npm/PyPI registries unless a URL says otherwise. Feeds `specs/000-platform/ui.md`.*

## 1. Decision table (1 = poor, 5 = excellent)

| Criterion (weight) | (a) Vite+React+TS+shadcn | (b) Python-native (NiceGUI/Reflex/Streamlit) | (c) HTMX 4 + Jinja + SSE | (d) SvelteKit 2 / Solid |
|---|---|---|---|---|
| Fit for the screen list (charts, diff, chat, tables) (×3) | 5 | 3 | 3 | 4 |
| Agents write it well / training-data depth (×3) | 5 | 3 | 4 | 3 |
| Type safety end-to-end (×2) | 5 (TS + OpenAPI codegen) | 3 | 2 | 4 |
| Playwright testability (×2) | 5 | 3 | 5 | 5 |
| CI simplicity, lockfile discipline (×2) | 4 (pnpm frozen lockfile) | 4 | 5 | 4 |
| Real-time 1-min cadence (×2) | 5 (SSE + Query invalidation) | 4 | 5 | 5 |
| Mobile + dark mode + a11y (×2) | 5 (Radix via shadcn) | 3 | 4 | 4 |
| Finance charts (lightweight-charts) (×2) | 5 native | 2 | 3 | 4 |
| LLM chat with tool-call UI (×1) | 5 | 2 | 2 | 3 |
| Hosting on same VM behind Caddy (×1) | 5 (static dist/) | 4 | 5 | 5 |
| **Weighted total /100** | **97** | **63** | **73** | **80** |

(a) wins on the screens that matter (candles + overlays, YAML diff, tool-call chat, dense tables). (c) is the runner-up if a zero-JS toolchain is wanted, but three screens would become hand-rolled JS islands anyway. (b) is disqualified by the candlestick + diff + chat trio: NiceGUI 3.17.1 and Reflex 0.9.12 are fast-moving 0.x/1.x, Streamlit 1.64 has no server push ([comparison](https://www.bitdoze.com/best-python-web-frameworks/), [Reflex vs Streamlit](https://reflex.dev/blog/streamlit-vs-dash-python-dashboards/)). (d) Svelte 5 reads well and AI SDK 5+ has Svelte parity ([Vercel](https://vercel.com/blog/ai-sdk-5)), but the React ecosystem is ~30× larger and the key libraries are React-first.

## 2. Recommended stack (exact pins)

**Frontend (`ui/`)** — Vite SPA, no Next.js (no SSR need; one owner; static files behind Caddy):
- `pnpm@12.8.1` (pin via `packageManager` + corepack), `pnpm-lock.yaml` committed, CI `pnpm install --frozen-lockfile`.
- `vite@8.3.1` (Rolldown, stable since 2026-03: https://vite.dev/blog/announcing-vite8), `react@19.3.0`, `typescript@7.0.2` (pin `~7.0`; fall back to `typescript@5.9` if a plugin needs it), `react-router@8.4.0`.
- `tailwindcss@4.3.3` + `@tailwindcss/vite`, `shadcn@4.21.0` CLI (Radix-based, dark mode via `class`) — https://www.shadcn.io/ui/installation/vite.
- `@tanstack/react-query@5.104.0`, `@tanstack/react-table@9.2.4` (v9 stable 2026-08-04: https://tanstack.com/blog/announcing-tanstack-table-v9).
- `lightweight-charts@5.2.1` + `@tradingview/lwc-toolkit` (official plugins, 2026-09-16: https://github.com/tradingview/lightweight-charts/releases).
- `recharts@3.10.1` for calibration/drawdown/score charts; escalate to `echarts@6.1.0` only for 100k-point scatter.
- `react-diff-viewer-continued@4.4.0` (`DiffMethod.YAML`) for book diffs; skip Monaco (2–3 MB for a read-only diff).
- `ai@7.0.123` (`useChat` + `DefaultChatTransport` to FastAPI) + `@assistant-ui/react@0.15.22` for message-parts/tool-call rendering (https://www.assistant-ui.com/docs/integrations/frameworks/ai-sdk).
- `zod@4.6.5` + `openapi-typescript`/`openapi-fetch` generated from FastAPI's `/openapi.json`.
- `@playwright/test@1.63.0`.

**Backend additions (Python 3.12)**: `fastapi==0.142.2`, `starlette==1.7.0`, `uvicorn==0.54.0`, `sse-starlette==3.5.0` (2026-09-28: https://pypi.org/project/sse-starlette/), `webauthn==3.0.1` (https://github.com/duo-labs/py_webauthn), `pyotp==2.10.0`, `itsdangerous==2.2.0`, `anthropic==1.9.0`, `aiogram==3.31.0`, `textual==8.2.8` + `textual-plotext==1.0.1` (optional).

## 3. Real-time design

SSE, not WebSocket: 1-minute cadence, server→client only, rides HTTP/2 through Caddy with auto-reconnect and `Last-Event-ID`.
- One `GET /api/events` `EventSourceResponse` multiplexing the firm event bus. Event types map 1:1 to Query keys: `dossier.transition` → `['dossier', id]`, `['dossiers']`; `book.version` → `['book', desk, symbol]`; `rail.event` / `firm.state` → `['firm']`, `['risk']`; `order|position|pnl` → `['positions']`; `approval.pending` → `['approvals']` + toast; `alert.compliance` → `['compliance']`.
- A `useFirmEvents()` hook holds one `EventSource` and calls `invalidateQueries`; components are pure `useQuery` consumers. Fallback `refetchInterval: 60_000` while disconnected.
- Server: one in-process `asyncio.Queue` fan-out fed by Postgres `LISTEN/NOTIFY` (or the events table); `: ping` every 15 s for Caddy idle timeouts.

## 4. Charts and diffs

- Candles + levels + strategy-book overlays: lightweight-charts `CandlestickSeries` + `createPriceLine` for stop/target/rails, official plugins for zones and session highlighting; thin `useEffect` wrapper, no third-party React wrappers.
- Calibration (reliability diagram), drawdown vs limit, score histograms: Recharts with `ReferenceLine` for limits; shadcn CSS variables for colours so dark mode is automatic.
- Book version diff: `react-diff-viewer-continued` split view plus a **semantic** tab from a server-side `deepdiff` ("stop 2925 → 2940") — what the owner reads on a phone.

## 5. "Ask the firm" chat

- FastAPI `POST /api/chat` streams AI SDK UI Message Stream frames over SSE so `useChat` works unmodified (https://ai-sdk.dev/docs/ai-sdk-ui/transport); backend loop `anthropic.AsyncAnthropic().messages.stream(...)`.
- Tools read-only by construction: `search_dossiers`, `get_dossier_section`, `get_book_version`, `get_positions`, `query_ledger`; each returns `{content, citation}`; the server emits `source-document` parts and assistant-ui renders citation chips linking to `/dossiers/:id#section`. Enforced three ways: read-only DB role, `chat:read` session scope, static test that the tool registry imports nothing from execution/approval modules.

## 6. Telegram companion

- `aiogram 3.31.0` over python-telegram-bot: async-only, typed routers, better fit for one handler per firm event (https://apitube.io/blog/post/telegram-news-bot-python).
- Webhooks behind Caddy at `/tg/<secret_path>` with `secret_token` and Telegram IP allowlist; polling for local dev.
- Approvals: inline `[Approve] [Deny]`; `callback_data` ≤ 64 bytes → opaque `itsdangerous` token id; `answerCallbackQuery` within 10 s. Kill/approve need a second factor: `ForceReply` for the current TOTP, or a one-time 6-digit code valid 60 s; one code = one action, recorded in `signed_actions`.
- Rate limits 1 msg/s/chat, 30/s global → batch alerts into 1-minute digests in market hours.

## 7. TUI (Textual)

Textual 8.2.8 + textual-plotext is mature for an ops console (tables, sparklines, SSH-friendly). Build only as a ~300-line "firm status + kill + tail events" client on the same API after the web UI ships: the thing that works when the browser/passkey path is broken at 09:10.

## 8. Auth and security (single owner, public VM)

- Primary access via **Tailscale** (laptop + phone on the tailnet; UI bound to the tailnet IP); public Caddy vhost only for `/tg/*` and optionally `/api/health` (https://needtoknowit.com.au/blog/tailscale-vs-cloudflare-tunnels-for-remote-access/).
- Login with **passkeys** (`webauthn==3.0.1`) and TOTP fallback; `itsdangerous`-signed `HttpOnly; Secure; SameSite=Lax` cookie, 12 h idle; CSRF via SameSite=Lax + `Origin` check.
- Dangerous actions (`POST /api/actions/kill`, `/approvals/{id}/decide`): fresh WebAuthn assertion with `userVerification: required` or a TOTP code, plus `Idempotency-Key`; recorded in `signed_actions` (shared with the Telegram path).

## 9. Observability

Do not embed Grafana in the trading UI (iframe needs `allow_embedding` + anonymous auth). Run Grafana 13.2 + Prometheus + Loki + Alloy as a separate Compose profile on the tailnet (~1.5–2 GB RAM). The trading UI shows business health natively (feed lag, last agent tick, event-bus lag) and deep-links to Grafana for infra.

## 10. Repo layout and endpoints

```
ui/
  package.json  pnpm-lock.yaml  .npmrc(engine-strict)  vite.config.ts  tsconfig.json
  playwright.config.ts  components.json (shadcn)
  src/
    api/        client.ts (openapi-fetch), schema.d.ts (generated), events.ts (SSE hook)
    app/        router.tsx, layout/ (Shell, Nav, ThemeToggle)
    features/   firm/ desks/ books/ dossiers/ positions/ risk/ scores/ compliance/
                research/ journal/ approvals/ chat/ auth/
    components/ui/ (shadcn), charts/ (Candles.tsx, Reliability.tsx, Drawdown.tsx), diff/
  e2e/          firm.spec.ts approvals.spec.ts chat.spec.ts ...
```
FastAPI under `/api`: `GET firm`, `POST actions/kill` (2FA), `GET desks`, `GET desks/{d}/books`, `GET books/{d}/{sym}/versions[/{v}]`, `GET books/{d}/{sym}/diff?from=&to=`, `GET dossiers?state=`, `GET dossiers/{id}`, `GET positions`, `GET orders`, `GET pnl?window=`, `GET risk`, `GET scores`, `GET calibration?agent=`, `GET compliance/alerts`, `POST compliance/alerts/{id}/clear` (2FA), `GET research/trials`, `GET journal?date=`, `GET approvals`, `POST approvals/{id}/decide` (2FA), `POST chat` (AI SDK stream), `GET events` (SSE), `POST auth/webauthn/...`, `POST auth/totp/verify`, `GET auth/session`, `POST auth/logout`, `GET market/{sym}/candles?tf=`.

## 11. CI recipe

```yaml
ui:
  runs-on: ubuntu-latest
  defaults: { run: { working-directory: ui } }
  steps:
    - uses: actions/checkout@v4
    - uses: pnpm/action-setup@v4
    - uses: actions/setup-node@v4
      with: { node-version: 24, cache: pnpm, cache-dependency-path: ui/pnpm-lock.yaml }
    - run: pnpm install --frozen-lockfile
    - run: pnpm openapi:gen && git diff --exit-code src/api/schema.d.ts
    - run: pnpm tsc --noEmit && pnpm eslint . && pnpm build
    - run: pnpm exec playwright install --with-deps chromium
    - run: pnpm exec playwright test
    - uses: actions/upload-artifact@v4
      if: failure()
      with: { name: playwright-report, path: ui/playwright-report }
```
`engine-strict=true` in `.npmrc`; Dependabot for `pnpm-lock.yaml`; Dockerfile stage `FROM node:24-alpine AS ui` → `COPY --from=ui /app/ui/dist /srv/ui`; Caddy `file_server` with `try_files {path} /index.html`, `reverse_proxy /api/* app:8000` with `flush_interval -1` for SSE.

## 12. Effort estimate for v0 (agent-written, owner-reviewed)

| Slice | Agent-days |
|---|---|
| Scaffold, auth (passkey+TOTP), shell/nav, dark mode, Tailscale/Caddy | 3 |
| Firm state, desks, positions/orders/P&L (R), drawdown, approvals + kill (2FA) | 4 |
| Books + version diff, dossiers (sections + timeline) | 3 |
| Scores/calibration, compliance, research ledger, journal/digest | 3 |
| SSE bus + Query invalidation, candles with overlays | 2 |
| Ask-the-firm chat (tool loop + assistant-ui + citations) | 3 |
| Telegram bot (alerts, approve/deny, signed codes) | 2 |
| Playwright suite, CI, OpenAPI codegen, Grafana profile | 3 |
| **Total** | **~23 agent-days** |

Optional Textual console: +2 days after v0.
