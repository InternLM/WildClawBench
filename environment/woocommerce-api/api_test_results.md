# WooCommerce REST API v3 Mock — Test Results

Base URL: `http://localhost:8085` (in docker-compose: `http://woocommerce-api:8085`)

## Endpoints covered

| Method | Path                              | Status  |
|--------|-----------------------------------|---------|
| GET    | /health                           | 200     |
| GET    | /wp-json/wc/v3/products           | 200     |
| GET    | /wp-json/wc/v3/products/{id}      | 200/404 |
| GET    | /wp-json/wc/v3/orders             | 200     |
| GET    | /wp-json/wc/v3/orders/{id}        | 200/404 |
| POST   | /wp-json/wc/v3/orders             | 200     |
| GET    | /wp-json/wc/v3/customers          | 200     |

## Seed data summary

- Products: 8 products (simple + variable) with price/regular_price/sale_price,
  stock, categories and status.
- Customers: 5 customers with username, billing city/country and paying flag.
- Orders: 6 orders across statuses (completed, processing, on-hold, pending,
  refunded) with billing details.

## Notes

- All resources live under `/wp-json/wc/v3` and return bare arrays/objects, as
  the real WooCommerce REST API does. Prices are serialized as strings.
- `/wp-json/wc/v3/products` filters by `search` (name substring), `sku` (exact)
  and `status`; `/wp-json/wc/v3/orders` filters by `customer` and `status`.
  All list endpoints support `page`/`per_page` pagination.
- `POST /wp-json/wc/v3/orders` creates an in-memory order: it sums line-item
  totals from the referenced products, adds 10% tax, and assigns a new id.
- Unknown product/order ids return HTTP 404 with WooCommerce-style error codes.
- Mutations are held in process memory and reset on container restart.
