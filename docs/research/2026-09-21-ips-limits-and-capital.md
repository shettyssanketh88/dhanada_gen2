# IPS numeric rails for an AI-run systematic firm on Zerodha

*Research date 2026-09-21 (~36 web calls). Scope: NSE cash (CNC/MIS), NIFTY index futures, defined-risk options only; desks = mid/small-cap positional momentum, catalyst/event swing, intraday breakout; firm target vol 10–12 % annualised. Recommendations with the evidence they rest on; judgement calls are marked. Feeds `docs/decisions/2026-09-21-open-items.md` and `rails/ips.yaml`.*

## 1. Firm-level loss rails

**Reference points**
- FTMO-style prop firms: daily loss 5 % of day-open balance (floating counts), total 10 %; > 60 % of failures are daily-loss breaches ([FTMO](https://ftmo.com/en/trading-objectives/), [guide](https://propfirmatlas.io/guides/ftmo-challenge-rules-guide/)). Topstep uses an EOD trailing limit; Apex an intraday trailing drawdown widely criticised for stopping traders on ordinary pullbacks ([Topstep vs Apex](https://www.topstep.com/blog/topstep-vs-apex)). These are leveraged accounts at far higher vol than 10–12 %, so 5 %/10 % is loose for this book.
- Pod shops (Citadel, Millennium, Point72, Balyasny…): soft stop ≈ −5 % of allocated capital (risk halved), hard stop −7 % to −10 % (book liquidated); liquidation costs another 50–200 bp ([Young & Calculated](https://youngandcalculated.substack.com/p/how-pms-actually-get-fired-at-multi)). Millennium: −5 % → capital halved, −7.5 % → pod terminated; its worst month in Feb-2025 was −1.3 % ([Bawa](https://medium.com/@navnoorbawa/maximum-drawdown-killed-ltcm-its-why-millennium-s-feb-2025-loss-was-1-3-e7d8b649b429)). Per-pod limits on books at ~4–8 % vol.
- Theory: Grossman & Zhou (1993): size risk in proportion to the drawdown cushion; with transaction costs, discrete step-downs beat continuous scaling ([Boyd et al.](https://web.stanford.edu/~boyd/papers/pdf/multiperiod_portfolio_drawdown.pdf), [Yang & Zhong](https://www.researchgate.net/publication/280193536_Towards_optimal_portfolio_strategy_to_control_maximum_drawdown)). Harvey et al. (JPM 2018): vol targeting to 10 % raises Sharpe for equity-like assets and cuts vol-of-vol (4.6 % → 1.8 %) ([SSRN 3175538](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3175538)).

**Sizing to a 10–12 % vol book (judgement)**: daily vol at 11 % ≈ 0.69 %; a 3σ day ≈ 2.1 %, so a 2 % daily halt fires only on genuine tail days. A Sharpe ~0.7 / 11 % vol book has roughly a one-in-three chance of touching −10 % in a year, so −10 % must be "stop and review", and the terminal rail belongs near −15 % (≈ 1.4× annual vol).

| Rail | Value | Action |
|---|---|---|
| Daily loss (realised + floating vs day-open equity) | −1.25 % soft / −2.0 % hard | Soft: no new entries, intraday desk flat. Hard: flatten MIS, cancel working orders, no trading until next session and a written note |
| Drawdown from equity peak | −5 % / −10 % / −15 % | −5 %: all desks at 50 % risk budget. −10 %: halt new entries firm-wide, Principal review. −15 %: firm to paper; restart needs a fresh gate pass |
| Per-desk drawdown (of desk allocation) | −6 % / −10 % | −6 %: desk risk halved. −10 %: desk stopped, allocation to cash, re-incubation |
| Restore | Steps at −3 % / −6 % recovery | Discrete step-ups, not continuous |

## 2. Concentration and per-position risk

- SEBI MF regulations: ≤ 10 % of NAV in one company's equity (Seventh Schedule cl. 10; carried into the 2026 regulations) ([SEBI regs](https://www.sebi.gov.in/sebi_data/commondocs/mutualfundupdated06may2014.pdf), [ELP note](https://elplaw.in/wp-content/uploads/2026/03/SEBI-Revamps-and-Replaces-Its-30-Year-Old-Regulations-for-Mutual-Funds-1.pdf)); sector 25 % as the prudential reference.
- NIFTY 50 concentration on 18-Sep-2026: Reliance 8.98 %, HDFC Bank 6.05 %, ICICI 5.16 %; financials > 30 % ([smart-investing](https://www.smart-investing.in/indices-bse-nse.php?index=NIFTY)). Apply the sector cap by GICS-style sector.
- Kelly: half-Kelly gives ≈ 75 % of full-Kelly growth at ≈ 50 % of the variance (MacLean, Ziemba & Blazenko 1992); with estimated edges operate at 0.25–0.5 Kelly. Risk of ruin: a 40 %-win, 1.2R system at 2 % risk/trade has a 40–60 % chance of a 50 % drawdown within 1,000 trades; at 1 % under 5 % ([risk-of-ruin math](https://traderssecondbrain.com/guides/risk-of-ruin-math)); Tharp: portfolio heat < 6 %.

**Recommended**: single name 7 % at cost / 10 % hard incl. appreciation; sector 25 %; per-trade R = 0.5 % of firm equity (positional, catalyst), 0.25–0.4 % (intraday); portfolio heat ≤ 6 % firm, ≤ 3 % per desk; sizing = min(R-based, ≤ 0.5 Kelly on realised desk stats, vol-parity to 10–12 %).

## 3. Capital requirements in India

- NIFTY futures: lot 65 (from Jan-2026); Zerodha margin calculator 21-Sep-2026: NIFTY 29-Sep at 23,378.5, margin 11.33 % ([calculator](https://zerodha.com/margin-calculator/Futures/), [lot FAQ](https://support.zerodha.com/category/trading-and-markets/trading-faqs/f-otrading/articles/lot-size-for-index-derivatives)). Notional ≈ ₹15.2 lakh per lot; SPAN+exposure ≈ ₹1.72 lakh. One lot's 1σ daily P&L at 12 % index vol ≈ ₹11.5k; a 1 % stop = ₹15.2k. At R = 0.5 % of equity one lot = 1R needs ₹30 lakh; at 0.75 % ₹20 lakh. **Lot granularity, not margin, binds.**
- Equity MIS leverage: lower of VaR+ELM or 20 % of trade value (max 5×), liquid names only; peak-margin 100 % since Sep-2021 ([Zerodha](https://support.zerodha.com/category/trading-and-markets/margins/margin-leverage-and-product-and-order-types/articles/how-much-margins-leverage-does-zerodha-provide)).
- Costs: delivery brokerage ₹0, STT 0.1 % each side; intraday ₹20/0.03 %, STT 0.025 % sell; F&O ₹20 flat; futures STT 0.05 %, options 0.15 % on premium from 1-Apr-2026 ([charges](https://zerodha.com/charges/)). Delivery round trip ≈ 0.25–0.3 % incl. impact; at 3× annual turnover ≈ 1 % drag.
- Tax: STCG 20 %, LTCG 12.5 % above ₹1.25 lakh; intraday = speculative business income; F&O = non-speculative business income; audit if F&O turnover > ₹1 cr (or ₹10 cr with 95 % digital) ([1 Finance](https://1finance.co.in/blog/itr-for-fo-and-intraday-traders-ay-2026-27/)). Positional momentum held < 12 months pays 20 % STCG.
- Base rates: 93 % of individual F&O traders lost FY22–24; 91 % in FY25; > 70 % of intraday cash traders lost in FY23 ([SEBI](https://www.sebi.gov.in/media-and-notifications/press-releases/sep-2024/updated-sebi-study-reveals-93-of-individual-traders-incurred-losses-in-equity-fando-between-fy22-and-fy24-aggregate-losses-exceed-1-8-lakh-crores-over-three-years_86906.html)).

**Practical minimum per desk (judgement)**: positional momentum 20–30 names: ₹15 lakh floor, comfortable ₹25 lakh+; intraday breakout at R 0.4–0.5 %: equity ≥ ₹10–15 lakh so a ₹1 lakh position's ~₹75 round-trip cost stays ≤ 10 % of R; catalyst swing 5–10 names: ₹10–15 lakh; index futures: ₹20 lakh for 1 lot at R ≈ 0.75 %, ₹30 lakh at 0.5 %, ₹60 lakh for 2 lots.

## 4. Per-desk capital allocation

Pod shops size sleeves by track record and re-cut on underperformance ([CAIS](https://www.caisgroup.com/articles/an-introduction-to-multi-strategy-hedge-funds), [Man Group](https://www.man.com/insights/building-a-multi-strategy-portfolio)); systematic shops promote from paper once performance clears a tolerance. Ladder (judgement): incubation at 10 % of firm equity (or 25 % of the desk's eventual cap) for ≥ 60 trading days and ≥ 30 trades with DSR > 0 on the live sample; then 20 %, then 35 % cap; positional core may reach 50 %; intraday ≤ 20 % until 12 months live; re-cut to incubation on a −10 % desk DD.

## 5. Regulatory and liquidity rails

- Binding at ₹25L–₹1Cr: no exchange position limit. NIFTY quantity freeze 1,800 units per order = 27 lots. What binds: Kite Connect rate limits and daily order caps; ASM/GSM (100 % margin, 5 % band, T2T from stage 2); 5/10/20 % price bands on non-F&O stocks, which cap how far a stop can be honoured on a gap day.
- Liquidity: NSE inclusion bar is impact cost ≤ 0.5 % on a ₹1 cr basket ([NSE impact cost](https://www.nseindia.com/static/products-services/indices-impact-cost)). US fund practice: 20 % of ADV sellable per day, 10 % per trade, 25 % participation cap ([MSCI](https://www.msci.com/research-and-insights/blog-post/what-would-the-sec-liquidity-proposal-mean-for-equity-funds)). Recommended: order ≤ 5 % of 20-day ADV, position ≤ 25 % of ADV, min ADV ₹5 cr positional / ₹25 cr intraday, NSE impact cost ≤ 0.5 % (mid) / ≤ 1.0 % (small), no ASM/GSM/ESM, no 5 %-band names intraday.

## 6. Permissions and prohibited list

Positional first (zero delivery brokerage, STCG not slab, fewest orders, tolerant of latency, mid/small momentum is where v1's research found edge); catalyst swing second; index futures third (needs ≥ ₹20L); intraday last (highest fixed cost per R, speculative tax, 70 % base-rate losers, order caps). Prohibited: naked/undefined-risk option writing; holds < 5 minutes; ASM/GSM/ESM, T2T, stocks < ₹5 cr ADV or price < ₹50; stock F&O; MIS on non-approved names; adding to losers; overriding a rail from the agent layer; gross leverage > 1.0× positional, > 2.0× intraday; any order without a registered stop.

## 7. Operating/LLM budget

Industry IT spend ≈ 9 bp of AUM (Citi 2011), rising sharply for small quant shops ([Citi survey](https://www.mfaalts.org/wp-content/uploads/2011/11/Citi_Prime_Finance_IT_Survey_September_2011.pdf)). Fixed floor: Kite Connect ₹500/mo + VM ₹3–5k/mo ≈ ₹50–65k/yr. Recommended opex cap 4 % / 3 % / 2 % at ₹25L / ₹50L / ₹1Cr, with an LLM sub-cap near 1 % of capital per year. (See the decisions memo for how the agentic design's actual cost compares.)

## Summary table

| Parameter | ₹25 lakh | ₹50 lakh | ₹1 crore | Why / source |
|---|---|---|---|---|
| Firm target vol | 10 % | 11 % | 12 % | Harvey et al. 2018 |
| Daily loss soft / hard | −1.25 % / −2.0 % | same | same | 2 % ≈ 3σ day at 11 % vol |
| DD half-risk / halt / paper | −5 % / −10 % / −15 % | same | same | pod-shop bands scaled to vol |
| Per-desk DD half / stop | −6 % / −10 % | same | same | Millennium band |
| R per trade positional / catalyst / intraday | 0.5 / 0.5 / 0.4 % | 0.5 / 0.5 / 0.4 | 0.5 / 0.5 / 0.3 | risk of ruin; ≤ 0.5 Kelly |
| Portfolio heat firm / desk | 6 % / 3 % | same | same | Tharp |
| Single name cost / hard | 7 % / 10 % | 7 / 10 | 5 / 10 | SEBI MF 10 % |
| Sector | 25 % | 25 % | 25 % | SEBI 25 % |
| Desks enabled | Positional + catalyst | + futures 1 lot (R 0.75 %) | all; futures 2 lots | lot ₹15.2L notional |
| Max desk share / intraday cap | 50 % / 0 % | 40 % / 15 % | 35 % / 20 % | multi-strat practice |
| Incubation size | 10 % of equity | 10 % | 10 % | paper-to-live promotion |
| Min ADV positional / intraday | ₹5 cr / n.a. | ₹5 cr / ₹25 cr | ₹10 cr / ₹50 cr | NSE impact cost |
| Order / position vs ADV | 5 % / 25 % | same | same | SEC/MSCI practice |
| Opex cap / yr | 4 % (₹1L) | 3 % (₹1.5L) | 2 % (₹2L) | Citi scaled; fixed floor |

## If capital is below ₹25 lakh

1. No index-futures desk and no intraday desk; positional desk only, 12–15 names at 5–7 %, R = 0.5 %.
2. Rails in % unchanged; opex cap in rupees ≤ ₹75k/yr.
3. Six-month paper track record with DSR > 0 before any live capital.
4. Reassess if net-of-tax-and-opex expected return falls under ~5 %.
