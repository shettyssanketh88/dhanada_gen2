# Regulatory verification of the flagged catalogue items — 2026-09-21

*Method: sebi.gov.in HTML pages return only headers to fetchers and NSE archive PDFs time out; primary PDFs were pulled via mirrors (CSE, ricago, broker mirrors) and NSE archives by curl and read locally. "Primary" = circular text read; "secondary" = broker/press summaries only. Resolves NC-8 and updates `docs/research/2026-09-20-sebi-zerodha-rule-catalogue.md`.*

## 1. SEBI retail-algo circular (4 Feb 2025) and NSE implementation standards

Sources: SEBI circular text (mirror https://www.cse-india.com/upload/upload/Feb_042025.pdf; SEBI page https://www.sebi.gov.in/legal/circulars/feb-2025/safer-participation-of-retail-investors-in-algorithmic-trading_91614.html); NSE Implementation Standards NSE/INVG/67858, Circ. 471/2025, 5 May 2025 (https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf); NSE FAQ 3 Nov 2025 (https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Retail%20Algo_03112025_NSE.pdf); SEBI extension circular …/2025/132 of 30 Sep 2025 (annexed in NSE/INVG/70541).

| Item | Value | Quoted text | Effective | Conf. |
|---|---|---|---|---|
| OPS threshold | **SEBI sets no number**; NSE sets **10 OPS per exchange/segment**, counted on the broker server's calendar-clock second | NSE B.2: "The Threshold Order Per Second (TOPS) is initially set at not exceeding 10 orders per second… applied basis the calendar clock second of the broker server." | 1 Apr 2026 all brokers | Primary |
| Sub-threshold algos | Tagged with a generic algo ID; no registration | NSE B.3; FAQ Q8: "all orders received via API from clients are considered Algo orders and require appropriate tagging" | — | Primary |
| > 10 OPS | Register with each exchange; broker rejects excess | NSE C.1, B.5 | — | Primary |
| Modifications/cancels counted? | Not stated by SEBI or NSE; Zerodha counts placements (429) | — | — | Secondary |
| Static IP | Mandatory for client-generated API algos; primary + optional secondary; unregistered algos via one API key; change ≤ once per calendar week; sharing only within family; daily forced logout | SEBI I(d); NSE A.2, A.4, A.6, A.7, A.8; FAQ Q6 | — | Primary |
| White vs black box | SEBI para V fn.5/6: white box = "logic, decision making processes and underlying rules are accessible and understandable to users"; black box = "internal workings and rationale… not known… not replicable"; black-box provider must register as a Research Analyst | — | — | Primary |
| Log retention | SEBI: none stated. NSE I(a): audit trail "available for at least 5 years" | — | — | Primary |
| Self-developed / family | Register only if over threshold; usable for family (self, spouse, dependent children, dependent parents) only; tech-savvy client hosts the algo at their own static IP | SEBI I(c); FAQ Q5 | — | Primary |
| Empanelment | Algo providers empanel with each exchange; broker due diligence | SEBI III(a); NSE E.1–E.4; NSE/INVG/70309 (19 Sep 2025) | — | Primary |
| Timeline | 1 Aug 2025 → 1 Oct 2025 → milestones to Jan 2026 → **all brokers 1 Apr 2026** | SEBI …/2025/132 | — | Primary |
| 2026 updates | No amending circular found; brokers enforce static-IP-only order acceptance from 1 Apr 2026 | — | — | Secondary |

## 2. NSE index quantity-freeze limits and lot sizes

| Item | Value | Source | Effective | Conf. |
|---|---|---|---|---|
| Freeze limits (units) | BANKNIFTY 600; NIFTY 1,800; FINNIFTY 1,800; MIDCPNIFTY 2,800; NIFTYNXT50 600 | NSE/FAOP/74942, Circ. 94/2026, 30 Jun 2026 | 1 Jul 2026 | Primary |
| Later revision | Same values plus NIFTYFPI 8,500 (circular 31 Aug 2026) | choiceindia / 5paisa summaries | 1 Sep 2026 | Secondary |
| Lot sizes | NIFTY 65; BANKNIFTY 30; FINNIFTY 60; MIDCPNIFTY 120; NIFTYNXT50 25 | NSE/FAOP/70616, Circ. 176/2025, 3 Oct 2025 (https://nsearchives.nseindia.com/content/circulars/FAOP70616.pdf) | Jan 2026 series (weekly from 6 Jan, monthly from 27 Jan 2026) | Primary |
| Max lots per order | NIFTY 27; BANKNIFTY 20; FINNIFTY 30; MIDCPNIFTY 23; NIFTYNXT50 24 | derived | — | — |

## 3. SEBI index-derivative position limits

Sources: SEBI/HO/MRD/TPD-1/P/CIR/2025/79 (29 May 2025); SEBI/HO/MRD/TPD/CIR/P/2025/122 (1 Sep 2025), both read via CSE mirrors.

| Item | Value | Quote | Effective | Conf. |
|---|---|---|---|---|
| Index options EOD | Net FutEq ₹1,500 cr; gross ₹10,000 cr each side, **at PAN level** | 5.5.1.1 | Normal from 6 Dec 2025 | Primary |
| Index options intraday | Net ₹5,000 cr; gross ₹10,000 cr each side per entity; ≥ 4 random snapshots incl. one 14:45–15:30; expiry-day breach penalised; **options only** | Circ. 122 paras 4.1–4.10 | 1 Oct 2025 | Primary |
| Index futures EOD | No market-wide limit; per client: higher of 15 % of index-futures OI or ₹500 cr gross notional, net at client level; TM combined 15 % or ₹7,500 cr | 5.5.2.x, Annex 1.3.2 | 1 Jul 2025 | Primary |
| Index futures intraday | No separate cap; EOD limits monitored via ≥ 4 snapshots, no penalty | Annex 1.3.4 | 1 Apr 2025 | Primary |

## 4. NSE market timings 2026

| Item | Value | Source | Effective | Conf. |
|---|---|---|---|---|
| F&O close 15:40 | Circular exists: NSE/FAOP/74467 (29 May 2026); go-live confirmed by NSE/FAOP/75472 (30 Jul 2026): "effective in LIVE from August 03, 2026". Normal close 15:30 → 15:40; F&O close-price VWAP window 15:10–15:40 | https://nsearchives.nseindia.com/content/circulars/FAOP75472.pdf; broker summaries | 3 Aug 2026 | Primary (existence/date) / Secondary (content) |
| Cash closing auction session (CAS) | 15:15–15:35 call auction for F&O-segment stocks; 15:15–15:20 no new orders, 15:20–15:25 market+limit, 15:25–15:30 limit only (random close 15:28–15:30), 15:30–15:35 matching; non-F&O stocks continue to 15:30 | NSE/CMTR/73362 (18 Mar 2026); Zerodha CAS FAQ | 3 Aug 2026 | Primary/Secondary |
| Derivatives pre-open restructure | 09:00–09:05 market+limit; 09:05–09:10 limit only; matching from 09:10 | Kotak Neo summary; circular not retrieved | 7 Sep 2026 | Secondary |

## 5. Zerodha MIS auto square-off (primary)

Equity **CAS stocks (F&O-segment stocks) 15:12**; non-CAS stocks 15:25; F&O 15:26; ₹50 + 18 % GST per squared-off order. Source: https://support.zerodha.com/category/trading-and-markets/trading-faqs/market-sessions/articles/intraday-auto-square-off-timings.

## 6. STT from 1 Apr 2026 (secondary; Act text not fetched)

Futures sell 0.05 % (from 0.02 %); options premium sell 0.15 % (from 0.10 %); options exercised 0.15 % of intrinsic (from 0.125 %); equity delivery 0.1 % both sides; intraday 0.025 % sell. Sources: taxguru, Arihant bulletin (assent 30 Mar 2026).

## Corrections to the catalogue's premise

- The 10 OPS number, the once-a-week IP change rule and the 5-year retention are **NSE standards**, not SEBI clauses; SEBI delegates the threshold and is silent on retention.
- Options EOD limits are at PAN level; futures limits are per client (net) with a TM-combined limit; there is no intraday futures cap.
- The reported freeze limits have been live since 1 Jul 2026.
- **Operational consequence:** for F&O-segment stocks the MIS auto square-off is now 15:12 and the cash market enters a closing auction at 15:15. The firm's own MIS flatten for those stocks must complete by ~15:05, and the intraday carry window moves to 14:45.
