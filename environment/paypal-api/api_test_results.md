# PayPal Mock API — Test Results

Base URL: `http://localhost:8042` (in docker-compose: `http://paypal-api:8042`)

## Endpoints covered

| Method | Path                                          | Status  |
|--------|-----------------------------------------------|---------|
| GET    | /health                                       | 200     |
| POST   | /v2/checkout/orders                           | 201     |
| GET    | /v2/checkout/orders/{order_id}                | 200/404 |
| POST   | /v2/checkout/orders/{order_id}/capture        | 201/404/422 |
| POST   | /v2/payments/refunds                          | 201/404 |
| GET    | /v2/payments/refunds/{refund_id}              | 200/404 |
| GET    | /v2/invoicing/invoices                        | 200     |
| POST   | /v2/invoicing/invoices                        | 201     |
| POST   | /v1/payments/payouts                          | 201     |

## Seed data summary

- Orders: 6 in mixed statuses (CREATED, APPROVED, COMPLETED, VOIDED)
- Captures: 2 (for the two COMPLETED orders)
- Refunds: 1 (partial refund against a capture)
- Invoices: 5 (DRAFT / SENT / PAID)
- Payouts: 2 (SUCCESS / PENDING)

## Notes

- Amounts are Money objects with string decimal values:
  `{"currency_code": "USD", "value": "49.99"}`.
- Mutations are held in process memory and reset on container restart.
- Newly created orders start as `CREATED`; capturing them transitions to
  `COMPLETED` and produces a capture record.
- Capturing an already-COMPLETED order returns 422; capturing a VOIDED order
  returns 422; an unknown order returns 404.
- `POST /v2/payments/refunds` requires a known `capture_id` (else 404); omitting
  `amount` refunds the full capture amount.
