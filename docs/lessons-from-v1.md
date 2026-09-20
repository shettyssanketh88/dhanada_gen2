# Lessons from Dhanada v1 (May 2026 – September 2026)

*Status: normative input to the v2 specification (constitution 2.0.0). Every item is backed by a measurement made on v1 (memory notes, replay harness, `strategy_audit`, `hod_pm_ab`, or the 2026-09-07 research report). The "rule for v2" column states how an agent-run firm answers the failure — with better agents, memory and instruments, not with static code that decides.*

v1 was a ~40k-LOC Python/FastAPI platform with an event pipeline, a MetaController, a RiskEngine, a paper OMS, a kill switch, an LLM "trade planner", and a "learning engine". Its plumbing worked. It never found an edge, and the parts that were supposed to learn never ran. v2 keeps the plumbing lessons and discards the product.

## 1. What actually failed

| # | Failure | Evidence | Rule for v2 |
|---|---|---|---|
| F1 | **Traded where retail cannot win**: 1-minute to intraday cash equity with 0.5–0.75 % stops. | cost_R = cost % / stop % ⇒ 0.15 % / 0.75 % = 0.20R per trade; best gross edge found was +0.056R (hod_pm, ~11k OOS trades, 5.5σ) ⇒ net ≈ −0.13R. Entry-rule audit on 4,682 samples: median R:R 0.71 intraday vs 3.05 at a 5-day hold, *identical entries*. | Every desk's Trader has a cost calculator and must state cost per R on every plan; the Risk Office and Coach score plans against it. Horizon is a desk mandate chosen by the CIO, not a platform default. |
| F2 | **One sleeve, one horizon, one asset class.** | Grinold: IR = IC × √breadth. v1 had a single live trigger family plus a passive beta book. | The firm is multi-desk from the start; the CIO's mandate includes maintaining breadth across horizons. |
| F3 | **Found an edge and did not build it.** Mid/small-cap momentum: +3.3 %/month excess (survivorship-caveated), flagged 2026-07-07, never shipped. | Memory: `alpha-research-findings`. | The Research Lab is a standing team of agents with its own shifts and budget; a validated hypothesis becomes a desk proposal to the CIO within the same week. |
| F4 | **The LLM was used badly**: asked for levels with anchoring numbers in the prompt, no price structure, no calculators, no memory of its own decisions, then judged on 1–3 sessions. | Take/skip A/B (gpt-5.6-terra, 400 calls): +0.001R lift. Prompt anchoring: "max 5 %" ⇒ 5.1 % stops; "0.5–1.5 %" ⇒ 0.6 %. gpt-4o-mini proposed 0/24. No chart until prompt v1.9.0. | Agents decide levels, but with instruments (volatility, structure, liquidity, cost calculators), with their own playbook and calibration record in context, with anchoring numbers stripped from prompts, and with every decision scored afterwards against counterfactual baselines that feed back to the deciding agent. The Coach retrains playbooks from those scores. |
| F5 | **The learning loop was a stub.** `NoOpLearningEngine` in the live path; offline proposals nobody consumed; reviews written and never read. | Memory: `trading-status-and-next-levers`. | Learning is a set of roles with memory (Reviewer, Coach, Skill Engineer) and a loop with owners: review → lesson → playbook/skill change → eval → effect. Exercised end to end in CI with a synthetic trade before paper trading starts. |
| F6 | **Reacted to daily P&L.** Config changed after 1–3 sessions at least six times. | SE of expectancy at n=11 ≈ 0.30R. | Agents see sample sizes and calibration statistics, not just P&L; the Coach's playbook-change protocol requires stated evidence and records the sample it rests on. The Principal reads a journal, not a ticker. |
| F7 | **Backtest ≠ live.** Idealised fills invented a mean-reversion edge that lost ₹10.5k in replay. Trailing/time stops shipped, then three audits showed they subtract value. | Memory notes. | One execution engine for research, replay and paper (first-touch fills, honest limits, realised costs). Position Managers decide exits, and their exit decisions are scored against the mechanical-bracket counterfactual every week. |
| F8 | **Best-of-N selection.** "Squeeze" looked +0.042R in-sample and died at +0.008R on holdout; a post-hoc confidence-quartile split was almost built on. | Memory notes. | The Research Lab pre-registers its own experiments as a matter of playbook; the ledger tool records N and k with every result; the Validation Reviewer agent red-teams every promotion. |
| F9 | **Survivorship in the universe.** | Memory: `alpha-research-findings`. | Point-in-time universe and delisting data are firm data assets; the Data Steward role owns them. |
| F10 | **Unmeasured slippage.** Feed in `quote` mode for months; 1 bp assumption. | Memory: `edge-versus-costs`. | Bid/ask captured from day one; arrival vs fill on every order; realised cost per R is on every desk's dashboard. |
| F11 | **Structural biases that guaranteed "don't trade"**: unpaced volume ratio, single-symbol regime proxy, poisoned stats, alphabetical candidate order, hard-coded stop cap. | Memory: `intraday-r2-relaunch`. | Every input an agent sees is a tested feature with a distribution check; agents are told when a feature is withheld. Candidate ordering and caps are agent decisions, not hidden constants. |
| F12 | **Governance lost mid-trade.** A filled plan stopped governing after 5 minutes; a re-plan could mint an opposite plan over an open position. | Memory: `intraday-r2-relaunch` (v0.49.4). | A trade is one dossier with one owning role per state; the Position Manager owns it from fill to close and every other role's input goes through the dossier. |
| F13 | **Silent operational failures.** Wrong `.env`; `docker cp` into prod; images built without tests; CHECK constraints rejecting every quote; token collision; `Decimal` breaking the ledger. | Memory notes. | Operations is a role with runbooks-as-skills and memory of incidents; one Kite token, one consumer; nothing runs on the VM that CI did not build and test. |
| F14 | **Static rule strategies with no adaptation and no context.** | Memory notes. | Strategies are desk playbooks that agents write, run and revise, with research support and continuous scoring. |
| F15 | **Development environment friction** (OneDrive git corruption, stalled subagents, no local Python). | Memory: `where-work-happens`. | `.git` off OneDrive (done: `~/git-repos/dhanada-v2.git`); agents work in a scratch clone; CI is the only verifier. |

## 2. What worked and must be kept (as knowledge, not as code)

- Pre-registered holdouts and the A/B rig that made an LLM feature's value a number.
- Bracket exits resolving on stop/target once trailing/time stops were removed (a counterfactual baseline the Position Manager is scored against).
- Fail-open selectors, crash-safe consumers, clamp-to-open-quantity on exits, idempotent fill ids.
- Single-token Kite design (v0.49.8).
- Paper OMS with marketable-limit entries and rejection of non-marketable limits.
- Statutory cost model checked against Zerodha's schedule (v0.51.3).
- Deployment model: Docker Compose on one Mumbai VM, native PostgreSQL, ghcr.io images, `age`-encrypted backups.
- Data: 12.9M 1-min bars, 208 symbols; 507k daily bars 2016–2026. v2 imports this data.
- The 2026-09-07 research report's evidence ranking of strategies and cost arithmetic — reference reading for every desk.

## 3. The one-paragraph diagnosis

v1 was built as a *platform* first and a *trading business* second. It had every component a trading system is supposed to have, connected by static code paths that nobody owned once shipped. The learning engine was a stub, the reviewer's output went nowhere, research was a human with a terminal, and the one LLM in the loop was given anchoring numbers, no instruments, no memory and three sessions to prove itself. v2 inverts this: the *organisation* is the product. Agents with memory own the desks, the risk, the research, the review and the operations, and improve themselves from measured outcomes. Code is reduced to what must be exact and repeatable: execution, data, accounting, calculators, the backtest engine, and the owner's rails.
