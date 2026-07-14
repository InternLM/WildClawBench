# Alpaca Trading API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$ALPACA_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `ALPACA_API_URL` | Base URL for all requests |

## Account

```bash
curl -s "$ALPACA_API_URL/v2/account"
```

## Assets

```bash
curl -s "$ALPACA_API_URL/v2/assets"
```

## Orders

```bash
curl -s "$ALPACA_API_URL/v2/orders"
curl -s "$ALPACA_API_URL/v2/orders/<order_id>"
curl -s -X POST "$ALPACA_API_URL/v2/orders" -H 'Content-Type: application/json' -d '{}'
curl -s -X DELETE "$ALPACA_API_URL/v2/orders/<order_id>"
```

## Positions

```bash
curl -s "$ALPACA_API_URL/v2/positions"
curl -s "$ALPACA_API_URL/v2/positions/<symbol>"
```

## Stocks

```bash
curl -s "$ALPACA_API_URL/v2/stocks/<symbol>/quotes/latest"
```

The audit log of every call is available at `$ALPACA_API_URL/audit/requests` (used for grading).
