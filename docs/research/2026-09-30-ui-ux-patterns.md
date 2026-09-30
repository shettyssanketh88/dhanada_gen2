# Owner-facing interface for an agent-run investment firm — UX research

*Research date 2026-09-30 (~35 web calls). Feeds `specs/000-platform/ui.md`.*

## Bottom line

Every serious "many agents, one supervisor" product shipped in 2025–26 converged on the same shape: **a web console as the system of record plus a phone/chat channel that carries only interrupts and digests**. OpenAI's Codex app: a threads sidebar with per-thread state and "visible child-thread approval prompts" ([changelog](https://developers.openai.com/codex/changelog)); Cognition's Devin coordinator: per-child session link, cost meter, "message any managed Devin mid-task", sleep/terminate ([Cognition](https://cognition.com/blog/devin-can-now-manage-devins)); Claude Code added phone push "when actions required" so approvals land on the phone while the deep view stays on the laptop ([Remote Control](https://code.claude.com/docs/en/remote-control)); Managed Agents put tracing in the Console ([claude.com](https://claude.com/blog/claude-managed-agents)). The trading-bot world did the same: Hummingbot deprecated its Streamlit dashboard for **Condor**, "Telegram bot, web dashboard, and CLI access with session continuity" ([hummingbot.org/condor](https://hummingbot.org/condor/)); Freqtrade ships FreqUI (web) + a Telegram bot + an alpha TUI (ftui) that is deliberately monitor-only ([ftui](https://github.com/freqtrade/ftui)).

**Recommendation: a responsive web console (installable PWA) plus a Telegram bot for interrupts and digests, on the same approval state machine. No TUI.** An "ask the firm why" chat over dossiers belongs inside the console (and as a Telegram command), not as the primary surface.

India-specific: SEBI's April-2026 framework makes the API session close every trading day with 2FA/OAuth, static IP, tagging and a kill switch, so the daily login is a regulatory ritual to surface, not hide, and the kill switch must be reachable from a phone.

## (a) Comparison

| Dimension | Web console (PWA) | TUI | Chat-first | **Hybrid: console + chat interrupts** |
|---|---|---|---|---|
| Daily owner tasks (login, journal, approve, kill) | All possible; approvals need a tab | OAuth redirect awkward; kill fine over SSH | Login reminder, approve, kill, digest excellent; long reads and diffs poor | Chat for the four daily touches; console for anything longer than a screen |
| Explainability (dossiers, diffs, calibration, replay) | Best | Text diffs OK; charts weak; no shareable links | Worst: linear text | Console owns it; chat deep-links |
| Mobile | Good if mobile-first; iOS PWA push flaky | None ([Textual on mobile](https://johal.in/textual-web-tui-python-browser-based-terminal-uis-2025-2/)) | Best: native push, buttons | Best of both |
| Build cost | Medium-high | Low-medium but a second UI | Low | Medium: console + thin bot |
| Maintenance | One front end | Second front end; terminal bugs (ftui: "sleep mode crashes", Linux-only) | Bot grows into an unstructured CLI (Freqtrade ~30 commands) | Bot ≤ 8 verbs |
| Security | Web auth, TOTP, audit log | SSH strongest, no second approver | Group chats leak control ([Freqtrade docs](https://www.freqtrade.io/en/stable/telegram-usage/)) | Chat may only approve/kill/ask; rails/books changes need console re-auth |

## (b) UX patterns to adopt

1. **The Inbox as the unifying object** — LangChain Agent Inbox: every human touchpoint is an interrupt with **Accept / Edit / Respond / Ignore**, showing title, arguments, markdown description ([agent-inbox](https://github.com/langchain-ai/agent-inbox)). "Edit" lets the Principal change a proposed rail value, not just reject.
2. **Approval as a state machine** — DRAFT → REQUEST_APPROVAL → APPROVED / REJECTED / **EXPIRED**, idempotent callbacks, actor captured ([HITL guide](https://www.nnode.ai/blog/2026-02-05-human-in-the-loop-approval-gates)).
3. **Threads with state chips** — Codex sidebar: running / paused / done, "needs you" bubbled to the top.
4. **Per-agent cost meter and "message it mid-task"** — Devin coordinator; AgentOps agent-level cost attribution ([aimultiple](https://aimultiple.com/agentic-monitoring)).
5. **Tracing inside the console** — the dossier *is* the trace: one timeline per trade, each role's section a collapsible step.
6. **Progressive disclosure of reasoning, capped** — Claude Code collapses thinking to ≤ 10 lines with a toggle; "3 of 7 steps" summaries ([zylos](https://zylos.ai/research/2026-05-28-agentic-ux-frontend-design-patterns-ai-agents/)). One-paragraph verdict per role, expand for full reasoning.
7. **Per-event notification levels on / silent / off** — Freqtrade's ~13 event types ([telegram-usage](https://www.freqtrade.io/en/stable/telegram-usage/)). Default almost everything to silent in paper mode.
8. **Custom keyboard of ≤ 8 verbs** — Freqtrade keyboard rows; OpenClaw approvals as reactions/numbered options ([OpenClaw](https://docs.openclaw.ai/channels/whatsapp)).
9. **Read-only by default; state-changing actions explicitly enabled** — k9s/lazygit style; ftui monitor-only. Paper console: no order buttons at all; live: pause/kill only, never manual order entry.
10. **Bloomberg density with stable colour semantics, on the desk view only** ([UX Magazine](https://uxmag.com/articles/the-impossible-bloomberg-makeover), [UI density](https://mattstromawn.com/writing/ui-density/)). Journal and dossier screens are reading layouts.
11. **Positions grouped by underlying with "Analyze" and a macro strip** — Sensibull ([Strike review](https://www.strike.money/reviews/sensibull)). Ours: grouped by book with "Open dossier"; top strip of regime, drawdown vs limit, firm mode, constitution version.
12. **Measure in R, show distributions, not headlines** — Edgewonk: "average R tells you more than your win rate" ([review](https://tradertrac.com/blog/edgewonk-review-2026-is-the-one-time-fee-still/)); Tradervue marks entries/exits on the chart.
13. **Calibration (reliability) diagrams for scored decisions** — Brier decomposition into calibration + resolution ([arXiv 2311.18258](https://arxiv.org/pdf/2311.18258)).
14. **Versioned artefacts with diff review** — Codex/Devin review output as diffs you accept/reject. Book v2 → v4 and constitution changes render as side-by-side diffs with the rationale attached; approval is on the diff.
15. **Generative UI from a fixed widget catalogue for "ask why"** — Google A2UI, Vercel json-render ([A2UI](https://developers.googleblog.com/a2ui-v0-9-generative-ui/), [json-render](https://thenewstack.io/vercels-json-render-a-step-toward-generative-ui/)). "Why did we exit RELIANCE early?" returns the dossier card + the rule that fired + the R chart with citations, not prose alone.

## (c) Recommended information architecture

Console (responsive PWA; laptop-first; every screen collapses to one column):

1. **Today** (home; phone landing). Strip: firm mode (PAPER-S / PAPER-L / LIVE), broker session with "Log in now" before 09:15, constitution/IPS version, kill state. Then Inbox count, drawdown vs limit gauge, 3-line CIO summary, link to Journal. **No P&L above the fold.**
2. **Inbox.** One list, urgent first; each card: who, what (title + args), why (markdown), expiry, verbs enabled. Filters; history tab with who decided and when.
3. **Desk** (dense). Positions grouped by book: qty, entry, stop, current R, MAE/MFE, watch status light; order blotter with strategy id and rejection reasons; exposure vs rails as bars; Agent panel with role chips (idle / running / needs-you / errored, last heartbeat). Keyboard `/` jump to symbol, `d` open dossier.
4. **Dossiers.** List with outcome in R, book version, score. Detail: timeline of role sections collapsed to verdict lines; chart with entry/stop/exit marked; Replay; counterfactual panel; reviewer score.
5. **Books.** Per stock: current version, changelog, diff between any two versions, which dossiers used which version and aggregate R; recalibration proposals.
6. **Agents.** Roster with scorecards (decisions/week, avg R, calibration curve, override rate, LLM cost, error rate), activity log, "message this agent".
7. **Journal & Digest.** Reading layout; DSR and N beside any Sharpe; open questions for the Principal.
8. **Governance.** IPS, rails, constitution as versioned documents; proposal → diff → approve (re-auth); kill switch (two-step, hold-to-confirm, reason); audit export in Console-style formats ([Zerodha Console](https://support.zerodha.com/category/console/reports)).
9. **Ask.** Chat over dossiers with citations; answers render catalogue widgets.
10. **Research Lab.** Trials ledger (N, DSR), proposals.

Telegram bot (owner-only): morning login reminder with deep link; Inbox items with inline Accept / Edit (opens console) / Ignore; `/desk`, `/journal`, `/why`, `/pause`, `/kill` (confirm), `/status`; daily digest at close; weekly digest. Notification matrix per event.

No TUI.

## (d) Anti-patterns

- **P&L ticker on home.** Myopic loss aversion: infrequent checkers held ~33 % more risk and earned ~53 % more; a daily checker sees a loss on ~47 % of days ([Behavioral Policy](https://behavioralpolicy.org/myopic-loss-aversion-a-behavioral-answer-to-the-equity-premium-puzzle/)). Rupee P&L on Desk and weekly digest only.
- **Win-rate headlines** (FreqUI leads with it). Headline expectancy in R, DSR, calibration.
- **Alert floods.** 2–3 actionable pages per shift; delete alerts not acted on in 90 days ([incident.io](https://incident.io/blog/sre-alerting-best-practices)). Push only: login due, Inbox item, kill/pause, rail breach, broker disconnect.
- **Bot-as-CLI sprawl**; never order entry in chat.
- **Fully customisable dashboards** — opinionated screens; only notification levels and column visibility configurable ([Linear](https://prototypr.io/news/linear-opiniated-software)).
- **Raw reasoning dumps**; **approval without expiry or identity**; **manual override buttons in paper mode** (they train intervention and break the two-scale paper comparison); **building a TUI**; **group-chat control**.
