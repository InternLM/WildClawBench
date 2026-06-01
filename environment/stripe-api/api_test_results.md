# Stripe Mock API — Test Results

Base URL: `http://localhost:8021` (in docker-compose: `http://stripe-api:8021`)

## Endpoints covered

| Method | Path                              | Status   |
|--------|-----------------------------------|----------|
| GET    | /health                           | 200      |
| GET    | /v1/customers                     | 200      |
| GET    | /v1/customers/{id}                | 200/404  |
| POST   | /v1/customers                     | 201      |
| GET    | /v1/products                      | 200      |
| GET    | /v1/prices                        | 200      |
| POST   | /v1/payment_intents               | 201/400  |
| GET    | /v1/payment_intents/{id}          | 200/404  |
| GET    | /v1/charges                       | 200      |
| GET    | /v1/charges/{id}                  | 200/404  |
| POST   | /v1/charges                       | 201/400  |
| POST   | /v1/refunds                       | 201/400/404 |
| GET    | /v1/invoices                      | 200      |
| GET    | /v1/invoices/{id}                 | 200/404  |
| POST   | /v1/invoices                      | 201/404  |
| GET    | /v1/subscriptions                 | 200      |
| GET    | /v1/subscriptions/{id}            | 200/404  |
| POST   | /v1/subscriptions                 | 201/400  |
| GET    | /v1/balance                       | 200      |

## Seed data summary

- Customers: 6 (`cus_*`), one delinquent (Pelagic Freight)
- Products: 4 (Starter, Pro, Enterprise, POS Hardware)
- Prices: 5 (monthly/annual recurring + a one-time POS bundle)
- Charges: 7 (`ch_*`) in mixed status (succeeded/failed/pending), some refunded
- Invoices: 7 (`in_*`) in paid/open/draft status
- Subscriptions: 6 (`sub_*`) in active/past_due/canceled status
- Balance: singleton from `balance.json` (available 184200, pending 4900 cents)

## Notes

- All amounts are integer cents (e.g. `4900` = $49.00).
- List endpoints return Stripe `{"object": "list", "data": [...], "has_more": false}` envelopes.
- `POST /v1/payment_intents` with `confirm: true` also records a succeeded charge and sets `latest_charge`.
- `POST /v1/refunds` validates the refund amount against the charge's remaining
  refundable balance; over-refunding returns 400, unknown charge returns 404.
- Mutations (payment_intents, charges, refunds, created customers/invoices/subscriptions)
  are held in process memory and reset on container restart.
