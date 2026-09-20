# ADR-009 — Compliance architecture: two officers, one catalogue, rails at the order

## Status
Proposed (2026-09-20), on the Principal's instruction that no SEBI or broker rule may be broken.

## Context
Regulated firms split compliance into pre-trade, surveillance and audit functions under an accountable principal officer (docs/research/2026-09-20-firm-roles-gap-analysis.md). The applicable rules for an individual Kite Connect algo trader are catalogued in docs/research/2026-09-20-sebi-zerodha-rule-catalogue.md (A1–A19, B1–B10) with check timings and data feeds. The constitution makes regulator and broker mechanics rails enforced by code (Article II.2) while keeping decisions agentic (Article I).

## Decision
1. Two agent roles own the rules: a **Regulatory Compliance Officer** (SEBI, NSE/BSE, NSE Clearing, tax) and a **Broker Compliance Officer** (Zerodha/Kite Connect). They maintain the catalogue as dated data in `rails/market_rules/` via PRs, decide grey cases, pre-clear every strategy in every book version (`clear | clear_with_conditions | block`), dispose surveillance alerts, run the EOD close and the weekly/half-yearly self-audits. The CIO is the principal officer.
2. The **pre-order rail** evaluates the crisp catalogue checks synchronously on every order using the officers' data and clearance conditions; it rejects with rule ids and never modifies an order. Officers' holds are rails.
3. **Independence**: officers never author books or place orders; the Execution Agent cannot bypass rails; three approvals (Risk Officer economics, two compliance clearances) precede a governing book version.
4. Three control roles are added for money and truth: **Treasury & Settlement Manager** (margin, cash, collateral, settlement), **Books & Records Agent** (daily reconciliation against the broker, P&L attribution, tax ledger; an unresolved break halts new books), **Execution Quality Analyst** (implementation shortfall, cost-model calibration).
5. Live trading is blocked by rail until Zerodha's written confirmation of the operating model is recorded (NC-7); retention is 8 years (NC-9).

## Consequences
- Every book version costs three review sessions; auto-clearance rules within the catalogue keep intraday revisions fast.
- The catalogue's `[verify]` items must be resolved from primary text before Phase 3 (NC-8).
- Compliance evidence (clearances, alerts, dispositions, audits) is first-class data for the Coach and the Principal.
