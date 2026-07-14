# Coinbase API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$COINBASE_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `COINBASE_API_URL` | Base URL for all requests |

## Accounts

```bash
curl -s "$COINBASE_API_URL/v2/accounts"
curl -s "$COINBASE_API_URL/v2/accounts/<account_id>"
curl -s -X POST "$COINBASE_API_URL/v2/accounts/<account_id>/buys" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$COINBASE_API_URL/v2/accounts/<account_id>/sells" -H 'Content-Type: application/json' -d '{}'
curl -s "$COINBASE_API_URL/v2/accounts/<account_id>/transactions"
```

## Prices

```bash
curl -s "$COINBASE_API_URL/v2/prices/<pair>/spot"
```

## User

```bash
curl -s "$COINBASE_API_URL/v2/user"
```

The audit log of every call is available at `$COINBASE_API_URL/audit/requests` (used for grading).
