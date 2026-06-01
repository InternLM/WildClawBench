# BigCommerce API Mock — Test Results

Base URL: `http://localhost:8084` (in docker-compose: `http://bigcommerce-api:8084`)

## Endpoints covered

| Method | Path                            | Status  |
|--------|---------------------------------|---------|
| GET    | /health                         | 200     |
| GET    | /v3/catalog/products            | 200     |
| GET    | /v3/catalog/products/{id}       | 200/404 |
| GET    | /v2/orders                      | 200     |
| GET    | /v2/orders/{id}                 | 200/404 |
| POST   | /v2/orders                      | 200     |
| GET    | /v3/customers                   | 200     |

## Seed data summary

- Products: 8 catalog products (physical + digital) with price, sale_price,
  inventory, brand_id and categories.
- Customers: 5 customers with company, phone and customer_group_id.
- Orders: 6 orders across various statuses with billing address fields.

## Notes

- v3 endpoints (`/v3/catalog/products`, `/v3/customers`) wrap results in
  `{"data": [...], "meta": {"pagination": {...}}}`. v2 order list endpoints
  return a bare array, matching BigCommerce conventions.
- `/v3/catalog/products` filters by `name` (substring), `sku` (exact) and
  `is_visible`; both v3 list endpoints support `page`/`limit` pagination.
- `/v2/orders` filters by `customer_id` and `status_id`.
- `POST /v2/orders` creates an in-memory order: it sums line totals from the
  referenced products and assigns a new id.
- Unknown product/order ids return HTTP 404.
- Mutations are held in process memory and reset on container restart.
