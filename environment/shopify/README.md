# shopify (flat-file)

Flat-file environment — no server, no Docker. The agent reads these files
directly to answer Shopify-style questions about orders, products, customers,
inventory, and discount codes.

## Files

| File                 | Description                                              |
|----------------------|----------------------------------------------------------|
| `shop.json`          | Shop profile (name, domain, currency, plan)              |
| `products.csv`       | Product catalog (one row per variant)                    |
| `inventory.csv`      | Stock levels per variant per location                    |
| `locations.csv`      | Fulfillment locations                                    |
| `customers.csv`      | Customer roster (lifetime spend, order count, tags)      |
| `orders.csv`         | Order header info                                        |
| `order_items.csv`    | Line items per order                                     |
| `discount_codes.csv` | Active and expired discount codes                        |

All amounts are in the shop's currency (`USD`, see `shop.json`).
