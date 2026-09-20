# Broker confirmation — Zerodha Kite Connect automated trading

*Recorded by the Principal on 2026-09-21. This confirmation resolves NC-7 and supersedes the older Kite Connect terms-of-use wording ("not meant for placing fully automated trades"). The four constraints below are rails (`rails/RAILS.md`, ids `broker.static_ip`, `broker.market_protection`, `sebi.order_rate`, `broker.daily_auth`). Any change to this file requires the Principal.*

## Confirmation text (verbatim, from Zerodha support)

> We would like to inform you that you can absolutely automate your trades using the Kite Connect API. The API is specifically designed for programmatic order placement — you can place, modify, and cancel orders directly via the API without using the Zerodha Kite web or mobile app, but it requires a static IP for order placement endpoints.
>
> Regarding Approval:
> SEBI does not require any separate approval for individual retail traders to use API-based trading, as long as you operate within the following guidelines, effective from April 1, 2026:
>
> Static IP — You must have a whitelisted static IP in your Kite Connect developer account for order placement endpoints.
> Market Protection — All MARKET and SL-M orders must include the market_protection parameter.
> Rate Limits — Your order frequency must remain within 10 orders per second (OPS). If you stay below this threshold, no algorithm registration is required.
> Daily Authentication — You must complete the OAuth login with 2FA/TOTP daily to generate a valid access token.
>
> For personal automated trading within these limits, you are free to build and run your own strategies without any additional approval.

## Binding operating constraints (rails)

| Rail id | Constraint | Enforcement |
|---|---|---|
| `broker.static_ip` | Every order-placement, modification and cancellation request egresses from the whitelisted static IP registered in the Kite Connect developer account. Observed egress IP checked at start and hourly; mismatch → no new orders, protective orders continue, Principal alerted. | Execution service, synchronous |
| `broker.market_protection` | Every MARKET and SL-M order carries `market_protection` (never 0; default `-1`). An order constructed without it is rejected before the broker call. | Order construction |
| `sebi.order_rate` | Order actions (place, modify, cancel; rejections count) stay below 10 per second per exchange segment: token bucket 8/s sustained, burst 8, hard ceiling 9; secondary caps 400/min and the broker's daily limits. No strategy registration is required while this holds; exceeding it is a rail breach and a compliance incident. | Execution service |
| `broker.daily_auth` | The access token is generated each trading day by the Principal's manual OAuth login with 2FA/TOTP. No automated login. Without a valid token the firm is `awaiting_login`; new orders are blocked; protective orders continue from cached state. | Execution service, morning checklist |

`broker.terms_confirmed = true` as of 2026-09-21 (this file). The Broker Compliance Officer re-confirms annually or on any change to Kite Connect terms, and files the evidence here.
