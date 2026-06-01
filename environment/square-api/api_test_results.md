# Square Mock API — Test Results

Base URL: `http://localhost:8041` (in docker-compose: `http://square-api:8041`)

## Endpoints covered

| Method | Path                                  | Status  |
|--------|---------------------------------------|---------|
| GET    | /health                               | 200     |
| GET    | /v2/merchants/me                      | 200     |
| GET    | /v2/payments                          | 200     |
| GET    | /v2/payments/{payment_id}             | 200/404 |
| POST   | /v2/payments                          | 201/400/404 |
| POST   | /v2/refunds                           | 201/400/404 |
| GET    | /v2/customers                         | 200     |
| GET    | /v2/customers/{customer_id}           | 200/404 |
| POST   | /v2/customers                         | 201     |
| GET    | /v2/catalog/list                      | 200     |
| POST   | /v2/orders                            | 201     |
| GET    | /v2/orders/{order_id}                 | 200/404 |
| GET    | /v2/inventory/{catalog_object_id}     | 200/404 |

## Seed data summary

- Merchant: `MERCH_RIVERSIDE` (Riverside Coffee Co.), location `LOC_MAIN`
- Customers: 7
- Catalog items: 7 (drinks, bakery, merch), each with one variation
- Inventory counts: 7 (one per variation)
- Payments: 7 (mix of COMPLETED / APPROVED / FAILED)
- Orders: 7 (mix of COMPLETED / OPEN)

## Notes

- Amounts are integer cents inside Money objects: `{"amount": 825, "currency": "USD"}`.
- Mutations are held in process memory and reset on container restart.
- `POST /v2/payments` rejects non-positive amounts (400) and unknown `customer_id` (404).
- `POST /v2/refunds` rejects refunds exceeding the original payment amount (400) and
  unknown `payment_id` (404).
- `POST /v2/orders` computes `total_money` from catalog variation prices times quantity.
- `GET /v2/catalog/list` accepts a comma-separated `types` filter (e.g. `ITEM`).
