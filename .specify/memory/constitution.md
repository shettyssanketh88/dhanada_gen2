# Dhanada v2 Constitution

*Version 1.0.0 — ratified 2026-09-20. This document is the highest authority in the repository. Every spec, plan, task, skill, agent definition and pull request is checked against it. Amending it requires a version bump, a dated rationale in §9, and the Principal's written approval.*

## Preamble

Dhanada v2 is an autonomous trading organisation, not a trading program. Its product is a governed portfolio of small, real, measured edges in Indian markets, run by AI agents in named roles who research, decide, review and operate, and by deterministic code that executes, accounts, simulates and enforces. The organisation exists to be net positive after realised costs in roughly 95 % of years, with drawdowns it has pre-declared it can survive. It does not exist to win a high percentage of trades, to trade every day, or to demonstrate that language models can predict prices.

## Article I — Agents decide categories, code decides numbers

1. No language model output may be used as a price, stop, target, quantity, weight, threshold, or any other number that affects an order or a risk limit. Numbers are computed by versioned, unit-tested code from declared inputs.
2. Language models produce: hypotheses, classifications (enums), rankings among pre-computed options, explanations, reviews, plans, and code. Every such output is a typed structured object validated by schema before use.
3. Prompts that feed a decision contain no anchoring numbers. Where a number is needed for context, it is expressed in relative, categorical, or z-scored form produced by code.
4. Any agent feature that touches trading is deployed only as an A/B arm against the mechanical baseline, and stays only if its measured lift passes a pre-registered gate.

## Article II — Nothing trades without a pre-registered gate

1. Every strategy, parameter change, feature, or allocation rule enters production through a gate whose criteria were written before the data were seen. Gates have ids, owners, minimum sample sizes, holdout windows and kill criteria.
2. Every backtest, replay, or audit is a row in the trial ledger before its result is known. Deflated Sharpe with the ledger's trial count, and the Minimum Track Record Length, are reported beside every Sharpe or expectancy.
3. A result without a ledger row is not evidence. A result on data used to choose its parameters is not evidence. Win rate is never a promotion metric.
4. Nobody, human or agent, changes a trading parameter in response to fewer trades than the sleeve's declared MTRL. Daily P&L is an operational signal, never a research signal.

## Article III — The cost equation governs every strategy

1. Every strategy carries its cost equation: `cost_R = round-trip cost % of notional ÷ stop distance % of price`, computed from realised fills, not assumptions.
2. A strategy is eligible for capital only if its gross expectancy after holdout is at least twice its realised `cost_R`.
3. Sub-15-minute holding periods and stops inside one daily ATR are presumptively cost-dominated and require the Principal's written exception to be researched at all.
4. Slippage is measured (bid/ask captured, arrival vs fill logged on every order) and recalibrated weekly. An unmeasured cost is assumed to be worse than modelled.

## Article IV — One trade, one owner, one state machine

1. A trade is a single durable entity (the *dossier*) from idea to archive. It has exactly one owning role at every state, and only that role's actions, plus the Risk Officer's veto and the kill switch, may change it.
2. Every role that touches a trade writes to that trade's dossier in its own section, and reads the dossier before acting. Memory is per trade per role, and it persists across agent invocations, restarts and deploys.
3. Exits are defined at entry (bracket) and changed only by rules that passed a gate. Discretionary exit management by an agent is forbidden unless the gate that admits it names the categorical conditions it may act on.

## Article V — Breadth before signal quality

1. The desk is a portfolio of independently accounted sleeves. Real capital requires at least three sleeves with positive net paper expectancy across at least two horizons, a measured correlation matrix, and a portfolio-level Deflated Sharpe above zero.
2. Sizing is in R from a fractional-Kelly risk budget per sleeve under portfolio volatility targeting. Drawdown governance is automatic and pre-declared per sleeve and per desk; overrides require the Principal in writing and are logged.
3. No naked short-tail exposure. Any option position is defined-risk and sized so that a three-sigma day costs at most one R.

## Article VI — Deterministic where it must be, agentic where it may be

1. Execution (order placement, modification, cancellation, bracket management, reconciliation), accounting (positions, cash, costs, P&L, R), risk policy enforcement, simulation, and market-data ingestion are static, versioned, tested code. They expose typed tools. They never call a language model.
2. Research, analysis, classification of text, planning, review, allocation within bounds, operations diagnosis, and documentation are performed by agents through skills. Skills bundle instructions with the deterministic scripts they rely on.
3. An agent may propose a change to code or to a skill. The change becomes effective only through the repository's pull-request, CI, gate and release process. Agents do not hot-patch running systems.

## Article VII — Evidence, provenance and replay

1. Every agent invocation that influences a trade or a promotion records its inputs (versioned), prompt version, model, outputs, cost, and the dossier or trial it belongs to. Any decision can be replayed from stored inputs.
2. Every feature an agent sees has a distribution test; a degenerate feature (constant, stale, or structurally biased) fails the build.
3. Research and paper trading share one simulation kernel with first-touch fills and conservative tie-breaking. Paper fills are honest: non-marketable limits do not fill.

## Article VIII — Safety, compliance and the Principal

1. Three kill levels exist and are drilled every release: sleeve pause, desk flat-and-halt, gateway cancel-all-and-disconnect. A failed drill blocks the release.
2. SEBI's framework for individual algorithmic trading is a design constraint: static IP, OAuth with 2FA, a hard order-rate governor below the exchange threshold, five-year audit retention, algo identification readiness, and market-hour and product rules encoded as policy.
3. The Principal (the human owner) alone may: approve a capital gate, change this constitution, approve a skill or agent change that alters trading behaviour, and provide broker credentials. The daily broker login is a Principal action until the broker permits otherwise.
4. Agents never hold broker credentials in their context. Credentials live in the execution layer's secret store.

## Article IX — Simplicity, surgical change, honesty

1. Build the minimum that satisfies the spec; no speculative abstraction, no configurability that no gate asked for.
2. Change only what the task requires; do not refactor adjacent code.
3. Report outcomes faithfully. A failed test is reported with its output. A skipped gate is reported as skipped. "The image built" is not "CI passed". An agent that cannot verify a claim says so.

## Article X — Development discipline (Spec-Driven Development)

1. Specifications precede code. Each feature has a `spec.md` (what and why, with EARS-style requirements and acceptance scenarios), a `plan.md` (how, with contracts and data model), and `tasks.md` (ordered, verifiable steps). Code that has no spec is not merged.
2. Requirements carry stable ids (`DH2-<AREA>-<nnn>`); tests and PRs cite them.
3. CI is the only verifier. Source never lives on the production VM; the VM runs released images only. The Git object database never lives on a cloud-synced filesystem.
4. Python 3.12+, type hints and docstrings everywhere, `ruff` and `mypy --strict` clean, unit coverage ≥ 85 % for new modules and ≥ 90 % for execution, accounting and risk-policy code.

## §9 Amendment log

| Version | Date | Change | Approved by |
|---|---|---|---|
| 1.0.0 | 2026-09-20 | Initial ratification from v1 lessons (docs/lessons-from-v1.md) and the 2026-09-07 research report. | pending Principal |
