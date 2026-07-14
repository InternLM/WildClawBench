# Shippo API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$SHIPPO_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `SHIPPO_API_URL` | Base URL for all requests |

## Addresses

```bash
curl -s -X POST "$SHIPPO_API_URL/addresses" -H 'Content-Type: application/json' -d '{}'
curl -s "$SHIPPO_API_URL/addresses/<object_id>"
```

## Shipments

```bash
curl -s -X POST "$SHIPPO_API_URL/shipments" -H 'Content-Type: application/json' -d '{}'
curl -s "$SHIPPO_API_URL/shipments/<object_id>"
curl -s "$SHIPPO_API_URL/shipments/<object_id>/rates"
```

## Tracks

```bash
curl -s "$SHIPPO_API_URL/tracks/<carrier>/<tracking_number>"
```

## Transactions

```bash
curl -s -X POST "$SHIPPO_API_URL/transactions" -H 'Content-Type: application/json' -d '{}'
curl -s "$SHIPPO_API_URL/transactions/<object_id>"
```

The audit log of every call is available at `$SHIPPO_API_URL/audit/requests` (used for grading).
