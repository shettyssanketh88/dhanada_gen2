# Compliance and control — SEBI, exchange and broker rules

*Companion to `spec.md` v2.2 (DH2-CMP-*). The Principal's instruction: "I don't want to break any rules." Sources: `docs/research/2026-09-20-sebi-zerodha-rule-catalogue.md` (rules A1–A19, B1–B10), `docs/research/2026-09-20-firm-roles-gap-analysis.md`, v1 CLAUDE.md compliance checkpoints. Constitution Article II.2 makes regulator and broker mechanics rails enforced by code; this document says who owns the rule catalogue, who decides in the grey, who clears books, who watches, and who audits.*

## 1. Design

Real regulated firms split compliance into a **pre-trade function**, a **surveillance function** and an **audit function**, with an accountable principal officer. Dhanada v2 emulates that with agents:

| Function | Owner (agent) | Instrument (code) |
|---|---|---|
| Rule catalogue: what the rules are, with effective dates and sources | **Regulatory Compliance Officer** (SEBI, NSE, BSE, tax) and **Broker Compliance Officer** (Zerodha) | `rails/market_rules/` dated tables and feeds; `compliance:*` tools |
| Interpretation in the grey (new circular, ambiguous case, unusual order) | The officers, on record | — |
| Book pre-clearance: every strategy in every book version checked against the catalogue before it can govern | The officers decide `clear | clear_with_conditions | block` per strategy | `compliance:preclear` runs the crisp checks and presents findings |
| Pre-order check on every order | — (rail) | `rails.compliance.*` evaluated synchronously in the execution service using the officers' catalogue |
| Intraday surveillance (OTR, self-match risk, cancel ratios, closing-window activity, position limits, margin snapshots) | Regulatory Compliance Officer (alerts), Treasury (margin) | Deterministic detectors every 1–5 minutes |
| EOD compliance close | Both officers | Reconciliation, tag completeness, OTR, penalties, delivery obligations, retention |
| Weekly and half-yearly self-audit | Both officers, chaired by the CIO as principal officer | Audit-chain verification, rule-version check, evidence bundle |
| Circular tracking | Both officers | Feed poller; diff against catalogue; PRs with effective dates |
| Signal provenance (PIT) | Regulatory Compliance Officer | Every feature from text carries `source_ref` and `published_at`; unverified sources are tagged and cannot be used in `applies_when` |
| Broker operating model | Broker Compliance Officer | `rails/broker-confirmation.md`: static IP, market protection, < 10 OPS, daily 2FA login — confirmed by Zerodha 2026-09-21; re-confirmed annually |

Accountability: the **CIO is the principal officer**; the officers report to the CIO and to the Principal (digest). Independence: the officers never author books or place orders; the Execution Agent cannot bypass a rail; the Risk Officerr reviews economics, the officers review legality and broker mechanics — three separate approvals on every book version.

## 2. The two officers

### Regulatory Compliance Officer (SEBI, NSE/BSE, NSE Clearing, tax)

| Field | Value |
|---|---|
| Decision rights | Pre-clearance verdict per strategy on regulatory grounds; interpretation of circulars; whether a situation requires a hold (`compliance_hold` on a desk or symbol); surveillance alert disposition; retention and record-keeping policy; tax-ledger classification rules; what to escalate to the Principal |
| Model / effort | `claude-opus-5`, `high` |
| Owns in `rails/market_rules/` | Algo framework (A1–A4), OTR (A5), PFUTP and STP (A6), surveillance lists (A7), price bands (A8), PIT provenance (A9), margin framework (A10), settlement (A11–A12), position limits and MWPL (A13–A14), derivatives structure (A15), timings and calendar (A16), disclosures (A17), tax (A18), running-account settlement (A19) |
| Triggers | Every book version; intraday alerts; EOD close; weekly self-audit; half-yearly audit; circular published |
| Skills | `preclearing-books-regulatory`, `surveilling-trading`, `closing-compliance-day`, `auditing-compliance`, `tracking-circulars`, `maintaining-rule-catalogue`, `classifying-tax-ledger` |

### Broker Compliance Officer (Zerodha / Kite Connect)

| Field | Value |
|---|---|
| Decision rights | Pre-clearance verdict per strategy on broker-rule grounds (product rules, RMS blocks, API limits, terms of use); whether an RMS rejection pattern requires a hold; broker-relationship items to escalate to the Principal (e.g., B6 unattended-trading clause); broker-rule catalogue maintenance |
| Model / effort | `claude-opus-5`, `high` |
| Owns in `rails/market_rules/` | Square-off timings (B1), RMS policies and charges (B2, B8), product rules (B3), option restrictions (B4), API limits and static IP (B5), terms of use (B6), order mechanics and freeze quantities (B7), pledging and collateral (B9), self-trade and block lists (B10); feeds: MIS scrip list, approved securities and haircuts, bulletin |
| Triggers | Every book version; RMS rejection events; EOD; weekly refresh of broker feeds; bulletin/Z-Connect/forum updates |
| Skills | `preclearing-books-broker`, `handling-rms-rejections`, `refreshing-broker-feeds`, `tracking-broker-updates`, `maintaining-rule-catalogue` |

Both officers also sit on the investment committee for any desk charter (a charter that requires registration above 10 OPS, or a product outside the IPS, is blocked by them, on record).

## 3. Book pre-clearance

After the Senior Analyst drafts a version and before the Risk Officerr's economic review (or in parallel, both required):

1. `compliance:preclear(book_version)` runs the crisp checks per strategy and returns findings: product allowed for the instrument and surveillance status (A7/B3/B4), session and validity windows (A16/B1), lot/freeze/band feasibility (A8/A15/B7), margin and cash-collateral feasibility at the strategy's size (A10/B2/B9), PFUTP patterns (would the entry and protective orders create a self-match across desks on the same PAN? does the strategy's order pattern resemble layering?) (A6/B10), provenance of any text-derived condition (A9), expiry and physical-settlement exposure (A12), position-limit headroom (A13/A14), estimated OTR contribution (A5).
2. Each officer decides per strategy: `clear`, `clear_with_conditions` (e.g., "CNC only", "no orders after 15:05", "size ≤ x % of ADV"), or `block` with the rule ids. Conditions become part of the book version and are enforced by the pre-order rail.
3. A book governs only when Risk Officerr + both officers have cleared at least one strategy. Auto-clearance rules the officers define (within their catalogue) let intraday revisions proceed without a fresh session; auto-clearances are recorded as the officer's decisions.

## 4. Pre-order rail (code)

Synchronous checks on every `exec:*` write, using the officers' catalogue and the book's clearance conditions: `rails.compliance.ip`, `.ops`, `.tag`, `.session`, `.instrument` (lot, freeze, band, LPP, protection), `.surveillance_status`, `.product`, `.margin`, `.self_match`, `.ban_list`, `.expiry_exposure`, `.clearance_conditions`, `.provenance`. A failing check rejects with the rule id, records a rail event on the dossier, notifies the Execution Agent and both officers. Rails never modify an order.

## 5. Intraday surveillance (code detectors, officer disposition)

| Detector | Cadence | Threshold source | Disposition |
|---|---|---|---|
| Running OTR per segment | 1 min | A5 slabs; alarm at 40, hold at 200 pending officer | Regulatory officer |
| Cancel/modify ratio per desk and symbol | 5 min | Catalogue | Regulatory officer |
| Self-match exposure across desks (resting orders on both sides) | on each order | A6/B10 | Rail blocks; officer reviews pattern |
| Share of scrip volume | 5 min | Catalogue (% of ADV) | Regulatory officer |
| Closing-window activity (15:15–15:30) | 1 min | A6 marking-the-close guard | Regulatory officer |
| Peak-margin headroom and MTM | 5 min | A10 | Treasury & Settlement Manager |
| Index-derivative FutEq positions | 5 min | A13 | Regulatory officer |
| Ban-list and surveillance-list intraday updates | 15 min | A7/A14 feeds | Both officers |
| RMS rejection bursts | on event | B2–B4 | Broker officer (may hold a desk) |
| Square-off timers (CAS stocks 15:00→15:12; others 15:15→15:25/15:26) | 1 min | B1 (verified 2026-09-21) | Execution Agent + rail |
| Kill-switch heartbeat and static-IP health | 1 min | A2/B5 | Operations Engineer |

## 6. EOD, weekly, half-yearly

- **EOD compliance close (16:05):** every order tagged and mapped to a book version and strategy id; broker order book reconciled (with Books & Records); OTR final; margin and penalty expectations (with Treasury); delivery obligations and T1 holdings; stock F&O E-4 exposure; cost ledger with correct STT; disclosure thresholds; retention job. Output: `ComplianceDayReport` in the journal.
- **Weekly:** broker feed refresh (MIS list, haircuts, freeze quantities, lot sizes, calendar); static-IP change budget; manual-login evidence; margin-shortfall instance count; OPS ceiling review per desk; alert dispositions ≤ 30 days.
- **Half-yearly self-audit** (emulating the broker/RA standard): audit-chain verification, rule-version history, sample replay of orders against rails as of their dates, kill-drill evidence, retention check, evidence bundle to the Principal. Chaired by the CIO.

## 7. Retention and records

Orders, fills, decisions, book versions, invocations, rail events, alerts and dispositions, contract notes and ledgers: **8 years** (SEBI Stock Brokers Regulations 2026 standard, exceeding the 5-year algo-log and 6-year tax requirements), hash-chained, backed up off-box encrypted.

## 8. Open items for the Principal

| id | Item |
|---|---|
| NC-7 | **Resolved 2026-09-21.** The Principal holds Zerodha's written confirmation that automated trading via Kite Connect is permitted for an individual without further approval under four constraints: whitelisted static IP for order endpoints, `market_protection` on every MARKET/SL-M order, under 10 orders per second (no algorithm registration needed below it), and daily OAuth login with 2FA/TOTP. The text and the resulting rails are in `rails/broker-confirmation.md`; `broker.terms_confirmed = true`. The older terms-of-use wording (B6) is superseded. |
| NC-8 | **Resolved 2026-09-21** (`docs/research/2026-09-21-regulatory-verification.md`): 10 OPS is NSE's standard (SEBI delegates); NSE audit trail ≥ 5 years; freeze limits and lots verified; no intraday futures cap, options limits at PAN level; F&O closes 15:40 and cash CAS 15:15–15:35 since 3 Aug 2026 — square-off schedule updated. Secondary-only residue: STT rates, 7-Sep-2026 pre-open detail. |
| NC-9 | Whether to adopt 8-year retention (proposed) or the 5-year minimum. |

## 9. Acceptance scenarios

- **C1** A strategy with MIS product on a stock that entered ASM stage 2 overnight is `block`ed at pre-clearance with rule A7/B3; the same strategy re-drafted as CNC with 100 % margin is `clear_with_conditions`.
- **C2** An order that would rest opposite another desk's resting order on the same PAN is rejected by `rails.compliance.self_match`, recorded, and both officers notified.
- **C3** OTR crosses 40 at 11:00 on one desk; the detector alerts; the Regulatory officer disposes with a hold on the desk's cancel-heavy strategy; the Execution Agent's next cancel is rail-rejected with the hold id.
- **C4** A new NSE circular changes freeze quantities; the Broker officer's tracker diffs the catalogue, opens a PR with `effective_from`, the Skill Engineer merges after review, and the pre-order rail uses the new value from the effective date.
- **C5** The EOD close finds an order without a strategy id in its tag; the report flags it, the Execution Agent's fidelity score records it, and the Coach reviews.
- **C6** The Broker Compliance Officer's annual re-confirmation lapses or Kite Connect terms change; `broker.terms_confirmed` is set false by the officer on record, live orders are blocked, and the Principal is notified until re-confirmed (NC-7 history in `rails/broker-confirmation.md`).
- **C7** An order constructed as MARKET without `market_protection` is rejected by `broker.market_protection` before any broker call, recorded on the dossier, and the Execution Agent's fidelity score notes it.
