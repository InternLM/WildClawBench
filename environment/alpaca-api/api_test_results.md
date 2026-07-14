# Alpaca Trading Mock API — Test Results

Base URL: `http://localhost:8043` (in docker-compose: `http://alpaca-api:8043`)

## Endpoints covered

| Method | Path                                      | Status  |
|--------|-------------------------------------------|---------|
| GET    | /health                                   | 200     |
| GET    | /v2/account                               | 200     |
| GET    | /v2/positions                             | 200     |
| GET    | /v2/positions/{symbol}                    | 200/404 |
| GET    | /v2/orders                                | 200     |
| GET    | /v2/orders/{order_id}                     | 200/404 |
| POST   | /v2/orders                                | 201/403/404/422 |
| DELETE | /v2/orders/{order_id}                     | 200/404/422 |
| GET    | /v2/assets                                | 200     |
| GET    | /v2/stocks/{symbol}/quotes/latest         | 200/404 |

## Seed data summary

- Account: `ACCT-9f8a...` (ACTIVE), buying_power 50681.50, portfolio_value 98765.40
- Positions: 5 (AAPL, MSFT, TSLA, NVDA, AMZN)
- Orders: 6 (mix of filled and open/new, buy and sell)
- Assets: 7 (5 held + GOOGL + SPY)
- Latest quotes: 7 (one per asset symbol)

## Notes

- Numeric fields are returned as strings (Alpaca convention), e.g. `qty: "40"`,
  `buying_power: "50681.50"`.
- Mutations are held in process memory and reset on container restart.
- A **buy** order is rejected (403) when `price * qty` exceeds account
  `buying_power`; price is the limit price if given, else the latest ask.
- A **sell** order is rejected (403) when `qty` exceeds the held position.
- Unknown symbols on order create return 404; unknown order ids return 404.
- `DELETE /v2/orders/{id}` cancels an open order; already-filled/canceled orders
  return 422.
- `GET /v2/orders` supports `status=open|closed|all` plus exact-status filters.
